#!/usr/bin/env bash
# QISSAH Folge 3 komplett: Blender-Render (2 Prozesse – 4 CPU / 15 GB), fehlende Bilder werden bei Neustart nachgerendert
# (0-Byte-Platzhalter vorher löschen), dann Ton + Remotion + HEVC. Fortsetzbar:
#   setsid nohup ./scripts/v1_qissa_kaaba.sh > out/kb_v1.log 2>&1 &
set -u
cd "$(dirname "$0")/.."
python3 scripts/build_qissa_kaaba.py > /dev/null
SH=${SHOTS:-$(python3 -c "import json; print(' '.join(s['id'] for s in json.load(open('src/qissa_kaaba/timeline.json'))['segments'] if s['kind']=='shot'))")}
for attempt in 1 2 3 4; do
  missing=""
  for s in $SH; do [ -s "public/qissa_kaaba/shots/$s.mp4" ] || missing="$missing $s"; done
  [ -z "$missing" ] && break
  echo "🎬 Durchgang $attempt:$missing $(date -u +%T)"
  find out/kb_frames -name '*.png' -size -1k -delete 2>/dev/null
  JOBS=2 SAMPLES=2 MID_SHOTS="segen" ./scripts/render_qissa_kaaba.sh $missing
done
for s in $SH; do [ -s "public/qissa_kaaba/shots/$s.mp4" ] || { echo "❌ fehlt: $s"; exit 1; }; done
python3 scripts/build_qissa_kaaba.py --mark-rendered $SH | tail -2
python3 scripts/sfx_qissa_kaaba.py
./scripts/finish_qissa_kaaba.sh
