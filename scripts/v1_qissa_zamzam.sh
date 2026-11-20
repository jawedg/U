#!/usr/bin/env bash
# QISSAH Folge 2: wartet auf den Blender-Render (render_qissa_zamzam.sh), markiert die Einstellungen als gerendert,
# mischt den Ton neu und baut das fertige Video (Remotion + HEVC-Kleinversion). Fortsetzbar.
set -u
cd "$(dirname "$0")/.."
while pgrep -f render_qissa_zamzam.sh > /dev/null; do sleep 60; done
python3 scripts/build_qissa_zamzam.py > /dev/null
SH=$(python3 -c "import json; print(' '.join(s['id'] for s in json.load(open('src/qissa_zamzam/timeline.json'))['segments'] if s['kind']=='shot'))")
for s in $SH; do [ -s "public/qissa_zamzam/shots/$s.mp4" ] || { echo "❌ fehlt: $s"; exit 1; }; done
python3 scripts/build_qissa_zamzam.py --mark-rendered $SH | tail -3
python3 scripts/sfx_qissa_zamzam.py
./scripts/finish_qissa_zamzam.sh
