#!/usr/bin/env bash
# Rendert alle Blender-Einstellungen von „Der erste Adhan“ (QISSA) parallel und macht daraus kurze MP4s für Remotion.
#   ./scripts/render_qissa_adhan.sh                 # alle Einstellungen
#   ./scripts/render_qissa_adhan.sh traum umar      # nur diese
# Vorher: python3 scripts/build_qissa_adhan.py (Zeitplan). Fertige Bilder werden übersprungen (Fortsetzen möglich).
# Lange Läufe: setsid nohup ./scripts/render_qissa_adhan.sh > out/qissa_render.log 2>&1 &
set -u
cd "$(dirname "$0")/.."
PCT=${PCT:-50}
SAMPLES=${SAMPLES:-8}
JOBS=${JOBS:-4}
SHOTS=("$@")
if [ ${#SHOTS[@]} -eq 0 ]; then
  # größte zuerst (gleichmäßige Auslastung)
  SHOTS=($(python3 -c "
import json; d=json.load(open('src/qissa_adhan/timeline.json'))
print(' '.join(s['id'] for s in sorted([s for s in d['segments'] if s['kind']=='shot'], key=lambda s: -s['frames'])))"))
fi
mkdir -p out/qissa_frames public/qissa_adhan/shots
one() {
  s="$1"
  n=$(python3 -c "import json; print({x['id']: x for x in json.load(open('src/qissa_adhan/timeline.json'))['segments']}['$s']['frames'])")
  echo "▶ $s ($n Bilder) $(date +%H:%M:%S)"
  blender -b --factory-startup --python blender/qissa/adhan.py -- "$s" "out/qissa_frames/$s" "$PCT" "$SAMPLES" \
    > "out/qissa_frames/$s.log" 2>&1
  have=$(ls "out/qissa_frames/$s"/*.png 2>/dev/null | wc -l)
  if [ "$have" -lt "$n" ]; then echo "❌ $s: nur $have/$n Bilder (siehe out/qissa_frames/$s.log)"; return 1; fi
  ffmpeg -loglevel error -y -framerate 24 -i "out/qissa_frames/$s/%04d.png" -c:v libx264 -preset slow -crf 16 \
    -pix_fmt yuv420p "public/qissa_adhan/shots/$s.mp4"
  echo "✅ $s fertig $(date +%H:%M:%S)"
}
export -f one
export PCT SAMPLES
printf "%s\n" "${SHOTS[@]}" | xargs -P "$JOBS" -I{} bash -c 'one {}'
echo "🏁 alle Einstellungen fertig $(date +%H:%M:%S)"
