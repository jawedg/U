#!/usr/bin/env bash
# QISSAH Folge 2 komplett: Blender-Render (2 Prozesse – 4 CPU / 15 GB: mit 4 Prozessen kam der Speicher-Killer), fehlende Bilder
# werden bei Neustart nachgerendert (0-Byte-Platzhalter vorher löschen), dann Ton + Remotion + HEVC. Fortsetzbar:
#   setsid nohup ./scripts/v1_qissa_zamzam.sh > out/zz_v1.log 2>&1 &
set -u
cd "$(dirname "$0")/.."
python3 scripts/build_qissa_zamzam.py > /dev/null
SH=$(python3 -c "import json; print(' '.join(s['id'] for s in json.load(open('src/qissa_zamzam/timeline.json'))['segments'] if s['kind']=='shot'))")
for attempt in 1 2 3; do
  missing=""
  for s in $SH; do [ -s "public/qissa_zamzam/shots/$s.mp4" ] || missing="$missing $s"; done
  [ -z "$missing" ] && break
  echo "🎬 Durchgang $attempt:$missing $(date -u +%T)"
  find out/zz_frames -name '*.png' -size -1k -delete 2>/dev/null
  JOBS=2 SAMPLES=2 MID_SHOTS="quelle" ./scripts/render_qissa_zamzam.sh $missing
done
for s in $SH; do [ -s "public/qissa_zamzam/shots/$s.mp4" ] || { echo "❌ fehlt: $s"; exit 1; }; done
python3 scripts/build_qissa_zamzam.py --mark-rendered $SH | tail -2
python3 scripts/sfx_qissa_zamzam.py
./scripts/finish_qissa_zamzam.sh
