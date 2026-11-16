#!/usr/bin/env bash
# Rendert die Blender-Einstellungen von „Der erste Adhan“ (QISSA) und macht daraus flüssige 60-fps-MP4s für Remotion.
#   ./scripts/render_qissa_adhan.sh                 # alle Einstellungen
#   ./scripts/render_qissa_adhan.sh traum umar      # nur diese
# Vorher: python3 scripts/build_qissa_adhan.py (Zeitplan). Fertige Bilder werden übersprungen (Fortsetzen möglich).
# JOBS Blender-Prozesse arbeiten wie eine Warteschlange: jeder nimmt sich die Einstellung mit den meisten offenen
# Bildern (Platzhalter-Dateien verhindern doppelte Arbeit). Blender rendert render_fps (30) Bilder/s in voller
# Auflösung, ffmpeg rechnet per Bewegungs-Interpolation auf 60 fps hoch (TikTok-Maximum, sehr flüssig).
# Lange Läufe: setsid nohup ./scripts/render_qissa_adhan.sh > out/qissa_render.log 2>&1 &
set -u
cd "$(dirname "$0")/.."
PCT=${PCT:-100}
SAMPLES=${SAMPLES:-3}
JOBS=${JOBS:-4}
TLF=src/qissa_adhan/timeline.json
RFPS=$(python3 -c "import json; print(json.load(open('$TLF')).get('render_fps', 24))")
SHOTS=("$@")
if [ ${#SHOTS[@]} -eq 0 ]; then
  SHOTS=($(python3 -c "
import json; d=json.load(open('$TLF'))
print(' '.join(s['id'] for s in sorted([s for s in d['segments'] if s['kind']=='shot'], key=lambda s: -s['frames'])))"))
fi
mkdir -p out/qissa_frames public/qissa_adhan/shots
frames() { python3 -c "import json; print({x['id']: x for x in json.load(open('$TLF'))['segments']}['$1']['frames'])"; }
open_frames() { local n; n=$(frames "$1"); mkdir -p "out/qissa_frames/$1"; echo $((n - $(ls "out/qissa_frames/$1"/*.png 2>/dev/null | wc -l))); }
pick() {  # Einstellung mit den meisten offenen Bildern
  local best="" bf=0 f
  for s in "${SHOTS[@]}"; do f=$(open_frames "$s"); if [ "$f" -gt "$bf" ]; then best=$s; bf=$f; fi; done
  echo "$best"
}
worker() {
  local k=$1 s
  while true; do
    s=$(pick)
    [ -z "$s" ] && break
    echo "▶ Prozess $k: $s ($(open_frames "$s") offen) $(date +%H:%M:%S)"
    blender -b --factory-startup --python blender/qissa/adhan.py -- "$s" "out/qissa_frames/$s" "$PCT" "$SAMPLES" \
      > "out/qissa_frames/$s.$k.log" 2>&1
    sleep 2
  done
}
echo "🎬 ${SHOTS[*]} · ${PCT}% · ${SAMPLES} Samples · ${RFPS} Bilder/s → 60 fps · $(date +%H:%M:%S)"
for k in $(seq 1 "$JOBS"); do
  worker "$k" &
  sleep 40   # versetzt starten: die Platzhalter des vorigen Prozesses sind dann schon da
done
wait
echo "🖼  Blender fertig $(date +%H:%M:%S)"
enc() {
  s=$1
  n=$(frames "$s")
  have=$(find "out/qissa_frames/$s" -name '*.png' -size +1k | wc -l)
  if [ "$have" -lt "$n" ]; then echo "❌ $s: nur $have/$n Bilder (siehe out/qissa_frames/$s.*.log)"; return 1; fi
  ffmpeg -loglevel error -y -framerate "$RFPS" -i "out/qissa_frames/$s/%04d.png" \
    -vf "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1080:1920:flags=lanczos" \
    -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p "public/qissa_adhan/shots/$s.mp4" && echo "✅ $s (60 fps) $(date +%H:%M:%S)"
}
export -f enc frames
export TLF RFPS
printf "%s\n" "${SHOTS[@]}" | xargs -P "$JOBS" -I{} bash -c 'enc {}'
echo "🏁 alle Einstellungen fertig $(date +%H:%M:%S)"
