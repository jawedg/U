#!/usr/bin/env bash
# QISSA „Der erste Adhan“ fertigstellen:
#   Stimme (Gemini, Charon + Orus + Iapetus) → Zeitplan → nur Einstellungen neu rendern, deren Länge sich stark geändert hat
#   → Ton-Spur → Video → kleine Version (≤ 60 MB, lässt sich in der App speichern).
#   ./scripts/run_qissa_adhan.sh            (alles)
#   NOVOICE=1 ./scripts/run_qissa_adhan.sh  (Entwurf ohne Stimme, geschätzte Zeiten)
set -euo pipefail
cd "$(dirname "$0")/.."
BR=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
[ -d node_modules ] || npm install --no-audit --no-fund

if [ -z "${NOVOICE:-}" ]; then
  # Schlüssel als Umgebungsvariable ODER als Network Secret (dann ersetzt der Proxy diesen Platzhalter)
  export GEMINI_API_KEY="${GEMINI_API_KEY:-proxy-injected}"
  python3 scripts/voice_gemini.py --project qissa_adhan
fi
python3 scripts/build_qissa_adhan.py

# Einstellungen mit > 10 % Längenänderung neu rendern, die anderen per playbackRate anpassen
CHANGED=$(python3 - <<'EOF'
import json
tl = json.load(open("src/qissa_adhan/timeline.json"))
r = json.load(open("src/qissa_adhan/rendered.json"))
out = [s["id"] for s in tl["segments"] if s["kind"] == "shot" and not (0.9 <= r.get(s["id"], 0) / s["frames"] <= 1.1)]
print(" ".join(out))
EOF
)
if [ -n "$CHANGED" ]; then
  echo "🔁 neu rendern: $CHANGED"
  for s in $CHANGED; do rm -rf "out/qissa_frames/${s:?}"; done
  # shellcheck disable=SC2086
  ./scripts/render_qissa_adhan.sh $CHANGED
  python3 - "$CHANGED" <<'EOF'
import json, sys
tl = json.load(open("src/qissa_adhan/timeline.json"))
r = json.load(open("src/qissa_adhan/rendered.json"))
for s in tl["segments"]:
    if s["kind"] == "shot" and s["id"] in sys.argv[1].split():
        r[s["id"]] = s["frames"]
json.dump(r, open("src/qissa_adhan/rendered.json", "w"), indent=1)
EOF
fi

python3 scripts/sfx_qissa_adhan.py
NAME=${NAME:-qissa-erster-adhan}
npx remotion render QissaAdhan "out/$NAME.mp4" --concurrency=4 --browser-executable="$BR" --log=error
# kleine Version: 2 Durchgänge, Bitrate so, dass ≤ 58 MB herauskommen
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "out/$NAME.mp4")
VB=$(python3 -c "print(int(58*8*1024/float('$DUR') - 128))")
ffmpeg -loglevel error -y -i "out/$NAME.mp4" -c:v libx264 -b:v "${VB}k" -pass 1 -an -f mp4 /dev/null
ffmpeg -loglevel error -y -i "out/$NAME.mp4" -c:v libx264 -b:v "${VB}k" -pass 2 -c:a aac -b:a 128k "out/$NAME-klein.mp4"
rm -f ffmpeg2pass-0.log ffmpeg2pass-0.log.mbtree
ls -la "out/$NAME.mp4" "out/$NAME-klein.mp4"
echo "✅ fertig: out/$NAME-klein.mp4"
