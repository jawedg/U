#!/usr/bin/env bash
# QISSAH Folge 4 v2 (spannender: Zweikampf, Abu Jahl, Kampf mit ganzem Körper) – alles bis zum fertigen Video, fortsetzbar (Neustart des Rechners: einfach neu starten):
#   setsid nohup ./scripts/v2_qissa_badr.sh > out/bd_v2.log 2>&1 &
# Rendert fehlende Einstellungen (Platzhalter abgebrochener Läufe werden gelöscht), dann Ton + Remotion + HEVC.
set -u
cd "$(dirname "$0")/.."
ALL="gebet abend rat medina auszug engel ende heer reihen sturm kolonne duell jagd abujahl regen kampf baum"
while true; do
  missing=""
  for s in $ALL; do [ -s "public/qissa_badr/shots/$s.mp4" ] || missing="$missing $s"; done
  [ -z "$missing" ] && break
  if ! pgrep -f render_qissa_badr.sh > /dev/null; then
    find out/bd_frames -name '*.png' -size -1k -delete 2>/dev/null
    echo "▶ rendern:$missing $(date -u +%T)"
    JOBS=${JOBS:-2} SAMPLES=2 MID_SHOTS="engel regen kampf sturm duell" ./scripts/render_qissa_badr.sh $missing >> out/bd_render_v2.log 2>&1
  fi
  sleep 30
done
echo "✅ alle Einstellungen $(date -u +%T)"
python3 scripts/sfx_qissa_badr.py
./scripts/finish_qissa_badr.sh || echo "❌ finish"
