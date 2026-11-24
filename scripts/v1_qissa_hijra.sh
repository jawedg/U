#!/usr/bin/env bash
# QISSAH Folge 5 „Die Hidschra – der Jäger in der Wüste“ – alles bis zum fertigen Video, fortsetzbar (Neustart des Rechners: einfach neu starten):
#   setsid nohup ./scripts/v1_qissa_hijra.sh >> out/hj_v1.log 2>&1 < /dev/null &
# Rendert fehlende Einstellungen (Platzhalter abgebrochener Läufe werden gelöscht), dann Ton + Remotion + HEVC.
set -u
cd "$(dirname "$0")/.."
ALL=$(python3 -c "import json; print(' '.join(s['id'] for s in json.load(open('src/qissa_hijra/timeline.json'))['segments'] if s['kind']=='shot'))")
while true; do
  missing=""
  for s in $ALL; do [ -s "public/qissa_hijra/shots/$s.mp4" ] || missing="$missing $s"; done
  [ -z "$missing" ] && break
  if ! pgrep -f render_qissa_hijra.sh > /dev/null; then
    find out/hj_frames -name '*.png' -size -1k -delete 2>/dev/null
    echo "▶ rendern:$missing $(date -u +%T)"
    JOBS=${JOBS:-2} SAMPLES=2 MID_SHOTS="jagd ritt nah versinken pferd rueckweg" ./scripts/render_qissa_hijra.sh $missing >> out/hj_render.log 2>&1
  fi
  sleep 30
done
echo "✅ alle Einstellungen $(date -u +%T)"
python3 scripts/sfx_qissa_hijra.py
./scripts/finish_qissa_hijra.sh || echo "❌ finish"
