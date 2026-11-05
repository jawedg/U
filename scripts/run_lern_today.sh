#!/usr/bin/env bash
# Erzeugt Stimme (Gemini 3.8, Charon), prüft, rendert und komprimiert die angegebenen Lernvideos.
# Aufruf: ./scripts/run_lern_today.sh 1 4
cd "$(dirname "$0")/.."
./scripts/setup_cloud.sh >/dev/null
export GEMINI_API_KEY="${GEMINI_API_KEY:-$(cat /tmp/gem/key 2>/dev/null)}"
B=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
for k in "$@"; do
  echo "===== KB $k ====="
  GEMINI_TTS_MODEL=gemini-3.8-flash-tts python3 -I scripts/voice_gemini.py --project lern_kb$k 2>&1 | grep -E "Erzeuge|✓|⚠️|✅|❌|Error"
  python3 -I scripts/check_voice_split.py lern_kb$k | tail -4
  npx remotion render LernKB$k out/lern-kb$k.mp4 --concurrency=3 --browser-executable=$B 2>&1 | grep -E "out/|rror" | tail -2
  ffmpeg -loglevel error -y -i out/lern-kb$k.mp4 -c:v libx264 -preset medium -crf 26 -tune stillimage -c:a aac -b:a 128k -movflags +faststart out/lern-kb$k-klein.mp4
  ls -la out/lern-kb$k-klein.mp4
done
