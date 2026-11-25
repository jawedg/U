#!/usr/bin/env bash
# QISSAH Folge 5 v2 (Nutzer-Feedback 25.11.2026: weicher Ritt, Zügel, Pferd lebendig, Lospfeile, Sturz/Sand/Staub, Netz in der Öffnung,
# Verfolger sichtbar, Türnische, Überblendungen, neue Stimmen) – ALLE Einstellungen neu (mit Handle für die Überblendung), fortsetzbar:
#   setsid nohup ./scripts/v2_qissa_hijra.sh >> out/hj_v2.log 2>&1 < /dev/null &
# Vorher (schon erledigt): voice_gemini.py --project qissa_hijra -> stt_retime.py --project qissa_hijra -> build_qissa_hijra.py
set -u
cd "$(dirname "$0")/.."
if [ ! -f out/hj_v2.started ]; then   # einmalig: alte Einstellungen/Teilstücke weg (alle Längen haben sich geändert)
  rm -f public/qissa_hijra/shots/*.mp4 out/hj_parts/*.ok
  rm -rf out/hj_frames/*
  touch out/hj_v2.started
fi
ALL=$(python3 -c "import json; print(' '.join(s['id'] for s in json.load(open('src/qissa_hijra/timeline.json'))['segments'] if s['kind']=='shot'))")
while true; do
  missing=""
  for s in $ALL; do [ -s "public/qissa_hijra/shots/$s.mp4" ] || missing="$missing $s"; done
  [ -z "$missing" ] && break
  if ! pgrep -f render_qissa_hijra.sh > /dev/null; then
    find out/hj_frames -name '*.png' -size -1k -delete 2>/dev/null
    echo "▶ rendern:$missing $(date -u +%T)"
    JOBS=${JOBS:-2} SAMPLES=2 MID_SHOTS="jagd ritt nah versinken pferd rueckweg lose" ./scripts/render_qissa_hijra.sh $missing >> out/hj_render.log 2>&1
  fi
  sleep 30
done
echo "✅ alle Einstellungen $(date -u +%T)"
python3 scripts/sfx_qissa_hijra.py
./scripts/finish_qissa_hijra.sh || echo "❌ finish"
