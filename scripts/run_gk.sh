#!/usr/bin/env bash
# Gemeinschaftskunde-Lernvideo: Stimme (Gemini 3.8, Charon, 7 Anfragen), prüfen, rendern, komprimieren.
cd "$(dirname "$0")/.."
./scripts/setup_cloud.sh >/dev/null
export GEMINI_API_KEY="${GEMINI_API_KEY:-$(cat /tmp/gem/key 2>/dev/null)}"
B=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
python3 scripts/build_gk_script.py
GEMINI_TTS_MODEL=gemini-3.8-flash-tts python3 -I scripts/voice_gemini.py --project lern_gk 2>&1 | grep -E "Erzeuge|✓|⚠️|✅|❌|Error"
python3 -I scripts/check_voice_split.py lern_gk | tail -6
# Variante 2 (Legetechnik) und Variante 1 (dunkel, mit Bewegung)
for C in LernGK2:lern-gk-lege LernGK:lern-gk-dunkel; do
  ID=${C%%:*}; N=${C##*:}
  npx remotion render $ID out/$N.mp4 --concurrency=3 --browser-executable=$B 2>&1 | grep -E "out/|rror" | tail -2
  ffmpeg -loglevel error -y -i out/$N.mp4 -c:v libx264 -preset medium -crf 26 -c:a aac -b:a 128k -movflags +faststart out/$N-klein.mp4
  ls -la out/$N-klein.mp4
done
