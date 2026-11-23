#!/usr/bin/env bash
# Rendert die Blender-Einstellungen von QISSAH Folge 4 „Die Schlacht von Badr“ als flüssige 60-fps-MP4s für Remotion.
#   ./scripts/render_qissa_badr.sh                 # alle Einstellungen
#   ./scripts/render_qissa_badr.sh traum umar      # nur diese
# Vorher: python3 scripts/build_qissa_badr.py (Zeitplan). Fertige Bilder werden übersprungen (Fortsetzen möglich).
# Durchgang 1: Blender rendert render_fps (30) Bilder/s in voller Auflösung -> out/bd_frames/<einstellung>/
# Durchgang 2: Blender rendert die ECHTEN Zwischenbilder (Bild k + 0,5)       -> out/bd_frames/<einstellung>_mid/
#   (keine Interpolation = keine Klötzchen/Doppelbilder; MID60=0 überspringt das, dann ffmpeg-minterpolate als Notlösung)
# JOBS Blender-Prozesse arbeiten wie eine Warteschlange: jeder nimmt sich die Einstellung mit den meisten offenen Bildern
# (Platzhalter-Dateien verhindern doppelte Arbeit). Lange Läufe: setsid nohup ./scripts/render_qissa_badr.sh > out/bd_render.log 2>&1 &
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
TLF=src/qissa_badr/timeline.json
RFPS=$(python3 -c "import json; print(json.load(open('$TLF')).get('render_fps', 24))")
SHOTS=("$@")
if [ ${#SHOTS[@]} -eq 0 ]; then
  SHOTS=($(python3 -c "
import json; d=json.load(open('$TLF'))
print(' '.join(s['id'] for s in sorted([s for s in d['segments'] if s['kind']=='shot'], key=lambda s: -s['frames'])))"))
fi
mkdir -p out/bd_frames public/qissa_badr/shots
frames() { python3 -c "import json; print({x['id']: x for x in json.load(open('$TLF'))['segments']}['$1']['frames'])"; }
dir_of() { if [ "$2" = mid ]; then echo "out/bd_frames/$1_mid"; else echo "out/bd_frames/$1"; fi; }
needs_mid() { [ "$MID60" = 1 ] && { [ -z "$MID_SHOTS" ] || [[ " $MID_SHOTS " == *" $1 "* ]]; }; }
open_frames() {  # offene Bilder einer Einstellung im Durchgang $2 (fertiges Video = nichts mehr offen)
  [ -s "public/qissa_badr/shots/$1.mp4" ] && { echo 0; return; }
  local n d; n=$(frames "$1"); [ "$2" = mid ] && n=$((n - 1)); d=$(dir_of "$1" "$2"); mkdir -p "$d"
  echo $((n - $(ls "$d"/*.png 2>/dev/null | wc -l)))
}
pick() {
  local best="" bf=0 f
  for s in "${SHOTS[@]}"; do
    if [ "$1" = mid ] && ! needs_mid "$s"; then continue; fi
    f=$(open_frames "$s" "$1"); if [ "$f" -gt "$bf" ]; then best=$s; bf=$f; fi
  done
  echo "$best"
}
enc() {
  local s=$1 n have mid
  n=$(frames "$s")
  have=$(find "out/bd_frames/$s" -name '*.png' -size +1k 2>/dev/null | wc -l)
  if [ "$have" -lt "$n" ]; then echo "❌ $s: nur $have/$n Bilder (siehe out/bd_frames/$s.*.log)"; return 1; fi
  mid=$(find "out/bd_frames/${s}_mid" -name '*.png' -size +1k 2>/dev/null | wc -l)
  if [ "$mid" -ge $((n - 1)) ]; then
    # echte 60 fps: Bild k, Zwischenbild k, Bild k+1, … (letztes Bild doppelt)
    rm -rf "out/bd_frames/${s}_60"; mkdir -p "out/bd_frames/${s}_60"
    python3 - "$s" "$n" <<'PY'
import os, sys
s, n = sys.argv[1], int(sys.argv[2])
d = f"out/bd_frames/{s}_60"
j = 1
for k in range(1, n + 1):
    for src in ([f"out/bd_frames/{s}/{k:04d}.png"] + ([f"out/bd_frames/{s}_mid/{k:04d}.png"] if k < n else [f"out/bd_frames/{s}/{k:04d}.png"])):
        os.symlink(os.path.abspath(src), f"{d}/{j:05d}.png")
        j += 1
PY
    ffmpeg -loglevel error -y -framerate 60 -i "out/bd_frames/${s}_60/%05d.png" -c:v libx264 -preset slow -crf 15 -pix_fmt yuv420p \
      "public/qissa_badr/shots/$s.tmp.mp4" && mv "public/qissa_badr/shots/$s.tmp.mp4" "public/qissa_badr/shots/$s.mp4" \
      && echo "✅ $s (echte 60 fps) $(date +%H:%M:%S)"
  else
    ffmpeg -loglevel error -y -framerate "$RFPS" -i "out/bd_frames/$s/%04d.png" \
      -vf "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" \
      -c:v libx264 -preset slow -crf 15 -pix_fmt yuv420p "public/qissa_badr/shots/$s.tmp.mp4" \
      && mv "public/qissa_badr/shots/$s.tmp.mp4" "public/qissa_badr/shots/$s.mp4" && echo "✅ $s (60 fps interpoliert) $(date +%H:%M:%S)"
  fi
}
try_enc() {  # komplette Einstellung sofort zu MP4, dann Einzelbilder löschen (Plattenplatz reicht nicht für alle PNGs)
  local s=$1 n have mid
  [ -s "public/qissa_badr/shots/$s.mp4" ] && return 0
  n=$(frames "$s")
  have=$(find "out/bd_frames/$s" -name '*.png' -size +1k 2>/dev/null | wc -l)
  [ "$have" -lt "$n" ] && return 0
  if needs_mid "$s"; then
    mid=$(find "out/bd_frames/${s}_mid" -name '*.png' -size +1k 2>/dev/null | wc -l)
    [ "$mid" -lt $((n - 1)) ] && return 0
  fi
  mkdir "out/bd_frames/$s.enclock" 2>/dev/null || return 0
  if enc "$s"; then rm -rf "out/bd_frames/$s" "out/bd_frames/${s}_mid" "out/bd_frames/${s}_60"; echo "🧹 $s: Einzelbilder gelöscht"; fi
  rmdir "out/bd_frames/$s.enclock" 2>/dev/null
}
worker() {
  local k=$1 pass=$2 s
  while true; do
    s=$(pick "$pass")
    [ -z "$s" ] && break
    echo "▶ [$pass] Prozess $k: $s ($(open_frames "$s" "$pass") offen) $(date +%H:%M:%S)"
    if [ "$pass" = mid ]; then
      MID=1 blender -b --factory-startup --python blender/qissa/badr.py -- "$s" "$(dir_of "$s" mid)" "$PCT" "$SAMPLES" \
        > "out/bd_frames/$s.mid$k.log" 2>&1
    else
      blender -b --factory-startup --python blender/qissa/badr.py -- "$s" "$(dir_of "$s" main)" "$PCT" "$SAMPLES" \
        > "out/bd_frames/$s.$k.log" 2>&1
    fi
    sleep 2
    try_enc "$s"
  done
}
echo "🎬 ${SHOTS[*]} · ${PCT}% · ${SAMPLES} Samples · ${RFPS} Bilder/s + Zwischenbilder → 60 fps · $(date +%H:%M:%S)"
for pass in $PASSES; do
  [ "$pass" = mid ] && [ "$MID60" != 1 ] && continue
  for k in $(seq 1 "$JOBS"); do
    worker "$k" "$pass" &
    sleep 20   # versetzt starten: die Platzhalter des vorigen Prozesses sind dann schon da
  done
  wait
  echo "🖼  Durchgang $pass fertig $(date +%H:%M:%S)"
done
for s in "${SHOTS[@]}"; do [ -s "public/qissa_badr/shots/$s.mp4" ] || try_enc "$s"; done
for s in "${SHOTS[@]}"; do [ -s "public/qissa_badr/shots/$s.mp4" ] || enc "$s"; done
echo "🏁 alle Einstellungen fertig $(date +%H:%M:%S)"
