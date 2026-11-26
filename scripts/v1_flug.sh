#!/usr/bin/env bash
# Flug-Video („Was, wenn das dein letzter Flug ist?“) – ganzer Ablauf, fortsetzbar (Cloud-Rechner startet neu -> einfach wieder starten):
#   setsid nohup ./scripts/v1_flug.sh >> out/fl_v1.log 2>&1 < /dev/null &
# Vorher: voice_gemini.py --project flug -> stt_retime.py --project flug -> build_flug.py
set -u
cd "$(dirname "$0")/.."
ALL=$(python3 -c "import json; print(' '.join(s['id'] for s in json.load(open('src/flug/timeline.json'))['segments'] if s['kind']=='shot'))")
while true; do
  missing=""
  for s in $ALL; do [ -s "public/flug/shots/$s.mp4" ] || missing="$missing $s"; done
  [ -z "$missing" ] && break
  if ! pgrep -f render_flug.sh > /dev/null; then
    find out/fl_frames -name '*.png' -size -1k -delete 2>/dev/null
    echo "▶ rendern:$missing $(date -u +%T)"
    JOBS=${JOBS:-2} SAMPLES=2 MID_SHOTS="absturz beten" ./scripts/render_flug.sh $missing >> out/fl_render.log 2>&1
  fi
  sleep 30
done
echo "✅ alle Einstellungen $(date -u +%T)"
python3 scripts/sfx_flug.py && ./scripts/finish_flug.sh || echo "❌ Ton/Schnitt"
