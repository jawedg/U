#!/usr/bin/env bash
# Rendert die Blender-Einstellungen von „Der erste Adhan“ (QISSA) als flüssige 60-fps-MP4s für Remotion.
#   ./scripts/render_qissa_adhan.sh                 # alle Einstellungen
#   ./scripts/render_qissa_adhan.sh traum umar      # nur diese
# Vorher: python3 scripts/build_qissa_adhan.py (Zeitplan). Fertige Bilder werden übersprungen (Fortsetzen möglich).
# Durchgang 1: Blender rendert render_fps (30) Bilder/s in voller Auflösung -> out/qissa_frames/<einstellung>/
# Durchgang 2: Blender rendert die ECHTEN Zwischenbilder (Bild k + 0,5)       -> out/qissa_frames/<einstellung>_mid/
#   (keine Interpolation = keine Klötzchen/Doppelbilder; MID60=0 überspringt das, dann ffmpeg-minterpolate als Notlösung)
# JOBS Blender-Prozesse arbeiten wie eine Warteschlange: jeder nimmt sich die Einstellung mit den meisten offenen Bildern
# (Platzhalter-Dateien verhindern doppelte Arbeit). Lange Läufe: setsid nohup ./scripts/render_qissa_adhan.sh > out/qissa_render.log 2>&1 &
# MID_SHOTS="traum umar": echte Zwischenbilder nur dort (viel Bewegung/Lichtpunkte), sonst minterpolate (ruhige Szenen sind sauber).
# ACHTUNG: diese Datei nie bearbeiten, während sie läuft (bash liest nach) – neue Fassung daneben schreiben und per mv ersetzen.
set -u
cd "$(dirname "$0")/.."
PCT=${PCT:-100}
SAMPLES=${SAMPLES:-3}
JOBS=${JOBS:-4}
MID60=${MID60:-1}
PASSES=${PASSES:-"main mid"}
MID_SHOTS=${MID_SHOTS:-}   # nur diese Einstellungen bekommen echte Zwischenbilder (leer = alle)
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
dir_of() { if [ "$2" = mid ]; then echo "out/qissa_frames/$1_mid"; else echo "out/qissa_frames/$1"; fi; }
open_frames() {  # offene Bilder einer Einstellung im Durchgang $2
  local n d; n=$(frames "$1"); [ "$2" = mid ] && n=$((n - 1)); d=$(dir_of "$1" "$2"); mkdir -p "$d"
  echo $((n - $(ls "$d"/*.png 2>/dev/null | wc -l)))
}
pick() {
  local best="" bf=0 f
  for s in "${SHOTS[@]}"; do
    if [ "$1" = mid ] && [ -n "$MID_SHOTS" ] && [[ " $MID_SHOTS " != *" $s "* ]]; then continue; fi
    f=$(open_frames "$s" "$1"); if [ "$f" -gt "$bf" ]; then best=$s; bf=$f; fi
  done
  echo "$best"
}
worker() {
  local k=$1 pass=$2 s
  while true; do
    s=$(pick "$pass")
    [ -z "$s" ] && break
    echo "▶ [$pass] Prozess $k: $s ($(open_frames "$s" "$pass") offen) $(date +%H:%M:%S)"
    if [ "$pass" = mid ]; then
      MID=1 blender -b --factory-startup --python blender/qissa/adhan.py -- "$s" "$(dir_of "$s" mid)" "$PCT" "$SAMPLES" \
        > "out/qissa_frames/$s.mid$k.log" 2>&1
    else
      blender -b --factory-startup --python blender/qissa/adhan.py -- "$s" "$(dir_of "$s" main)" "$PCT" "$SAMPLES" \
        > "out/qissa_frames/$s.$k.log" 2>&1
    fi
    sleep 2
  done
}
echo "🎬 ${SHOTS[*]} · ${PCT}% · ${SAMPLES} Samples · ${RFPS} Bilder/s + Zwischenbilder → 60 fps · $(date +%H:%M:%S)"
for pass in $PASSES; do
  [ "$pass" = mid ] && [ "$MID60" != 1 ] && continue
  for k in $(seq 1 "$JOBS"); do
    worker "$k" "$pass" &
    sleep 40   # versetzt starten: die Platzhalter des vorigen Prozesses sind dann schon da
  done
  wait
  echo "🖼  Durchgang $pass fertig $(date +%H:%M:%S)"
done
enc() {
  s=$1
  n=$(frames "$s")
  have=$(find "out/qissa_frames/$s" -name '*.png' -size +1k | wc -l)
  if [ "$have" -lt "$n" ]; then echo "❌ $s: nur $have/$n Bilder (siehe out/qissa_frames/$s.*.log)"; return 1; fi
  mid=$(find "out/qissa_frames/${s}_mid" -name '*.png' -size +1k 2>/dev/null | wc -l)
  if [ "$mid" -ge $((n - 1)) ]; then
    # echte 60 fps: Bild k, Zwischenbild k, Bild k+1, … (letztes Bild doppelt)
    rm -rf "out/qissa_frames/${s}_60"; mkdir -p "out/qissa_frames/${s}_60"
    python3 - "$s" "$n" <<'PY'
import os, sys
s, n = sys.argv[1], int(sys.argv[2])
d = f"out/qissa_frames/{s}_60"
j = 1
for k in range(1, n + 1):
    for src in ([f"out/qissa_frames/{s}/{k:04d}.png"] + ([f"out/qissa_frames/{s}_mid/{k:04d}.png"] if k < n else [f"out/qissa_frames/{s}/{k:04d}.png"])):
        os.symlink(os.path.abspath(src), f"{d}/{j:05d}.png")
        j += 1
PY
    ffmpeg -loglevel error -y -framerate 60 -i "out/qissa_frames/${s}_60/%05d.png" -c:v libx264 -preset slow -crf 15 -pix_fmt yuv420p \
      "public/qissa_adhan/shots/$s.mp4" && echo "✅ $s (echte 60 fps) $(date +%H:%M:%S)"
  else
    ffmpeg -loglevel error -y -framerate "$RFPS" -i "out/qissa_frames/$s/%04d.png" \
      -vf "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" \
      -c:v libx264 -preset slow -crf 15 -pix_fmt yuv420p "public/qissa_adhan/shots/$s.mp4" && echo "✅ $s (60 fps interpoliert) $(date +%H:%M:%S)"
  fi
}
export -f enc frames
export TLF RFPS
printf "%s\n" "${SHOTS[@]}" | xargs -P "$JOBS" -I{} bash -c 'enc {}'
echo "🏁 alle Einstellungen fertig $(date +%H:%M:%S)"
