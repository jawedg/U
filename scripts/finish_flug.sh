#!/usr/bin/env bash
# Letzter Schritt Flug-Video „Was, wenn das dein letzter Flug ist?“: Remotion in Teilstücken (ohne Ton) → zusammenfügen + fertige Tonspur (master.wav)
# → out/flug-letzter-flug.mp4 (H.264, hohe Qualität) + out/flug-letzter-flug-klein.mp4 (HEVC, ≤ 58 MB).
# Teilstücke überleben einen Neustart des Rechners (fertige werden übersprungen). Vorher: Einstellungen gerendert, master.wav da.
set -euo pipefail
cd "$(dirname "$0")/.."
BR=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
NAME=${NAME:-flug-letzter-flug}
CH=${CH:-2000}
N=$(python3 -c "import json; print(json.load(open('src/flug/timeline.json'))['frames'])")
mkdir -p out/fl_parts
: > out/fl_parts/list.txt
k=0
for ((a = 0; a < N; a += CH)); do
  b=$((a + CH - 1)); [ $b -ge $N ] && b=$((N - 1))
  f="out/fl_parts/p$k.mp4"
  if [ ! -s "$f.ok" ]; then
    echo "▶ Teil $k: Bilder $a–$b $(date -u +%T)"
    npx remotion render Flug "$f" --frames="$a-$b" --muted --crf=15 --concurrency=4 --browser-executable="$BR" --log=error
    echo ok > "$f.ok"
  fi
  echo "file '$(basename "$f")'" >> out/fl_parts/list.txt
  k=$((k + 1))
done
echo "🎞  zusammenfügen $(date -u +%T)"
ffmpeg -loglevel error -y -f concat -safe 0 -i out/fl_parts/list.txt -i public/flug/master.wav \
  -map 0:v -map 1:a -c:v copy -af "afade=t=in:d=0.02" -c:a aac -b:a 192k -shortest -movflags +faststart "out/$NAME.mp4"
# (20-ms-Einblendung: der Einstieg beginnt sofort laut -> AAC überschwang sonst im ersten Block auf +2,8 dBFS = Knacken)
# kleine Version: HEVC (H.265, ~halbe Datenmenge bei gleicher Qualität -> keine Klötzchen), 2 Durchgänge, ≤ 58 MB
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "out/$NAME.mp4")
VB=$(python3 -c "print(int(58*8*1024/float('$DUR') - 170))")
X265="aq-mode=3:psy-rd=1.5:deblock=-1,-1:log-level=error"
echo "📦 HEVC ${VB}k $(date -u +%T)"
ffmpeg -loglevel error -y -i "out/$NAME.mp4" -c:v libx265 -preset slow -b:v "${VB}k" -x265-params "pass=1:$X265" -an -f mp4 /dev/null
ffmpeg -loglevel error -y -i "out/$NAME.mp4" -i public/flug/master.wav -map 0:v -map 1:a -c:v libx265 -preset slow -b:v "${VB}k" \
  -x265-params "pass=2:$X265" -tag:v hvc1 -pix_fmt yuv420p -af "afade=t=in:d=0.02" -c:a aac -b:a 160k -shortest \
  -movflags +faststart "out/$NAME-klein.mp4"
rm -f x265_2pass.log x265_2pass.log.cutree
ls -la "out/$NAME.mp4" "out/$NAME-klein.mp4"
echo "✅ fertig: out/$NAME-klein.mp4 $(date -u +%T)"
