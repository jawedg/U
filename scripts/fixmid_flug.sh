#!/usr/bin/env bash
# Flug v2: echte Zwischenbilder NUR bei schnellen Schwenks der interpolierten Einstellungen (minterpolate machte dort
# Doppelbilder/Geister) und in deren MP4 einsetzen; danach Ton + Schnitt. Ersetzt den Schluss von v1_flug.sh (fortsetzbar):
#   setsid nohup ./scripts/fixmid_flug.sh >> out/fl_fix.log 2>&1 < /dev/null &
# Bereiche: out/fl_frames/mid_ranges.json {"einstellung": [[a, b], …]} = Hauptbilder k, deren Zwischenbild k+0,5 gerendert wird
# (gefunden über Bild-Unterschiede der Hauptbilder). minterpolate-MP4: Hauptbild k = Bild 2k-1, Zwischenbild k = Bild 2k (ab 1 gezählt).
set -u
cd "$(dirname "$0")/.."
R=out/fl_frames/mid_ranges.json
SHOTS=$(python3 -c "import json; print(' '.join(json.load(open('$R'))))")
ALL=$(python3 -c "import json; print(' '.join(s['id'] for s in json.load(open('src/flug/timeline.json'))['segments'] if s['kind']=='shot'))")
ml() { python3 -c "import json; print(','.join(f'{a}-{b}' for a, b in json.load(open('$R'))['$1']))"; }
need() { python3 -c "import json; print(sum(b - a + 1 for a, b in json.load(open('$R'))['$1']))"; }
have() { find "out/fl_frames/$1_fixmid" -name '*.png' -size +1k 2>/dev/null | wc -l; }
fixed() { [ -f "out/fl_frames/$1.fixed" ]; }
open_shots() { local s o=""; for s in $SHOTS; do fixed "$s" || [ "$(have "$s")" -ge "$(need "$s")" ] || o="$o $s"; done; echo $o; }
missing() { local s m=""; for s in $ALL; do [ -s "public/flug/shots/$s.mp4" ] || m="$m $s"; done; echo $m; }

worker() {
  local k=$1 s o
  while true; do
    o=$(open_shots); [ -z "$o" ] && break
    for s in $o; do
      echo "▶ Zwischenbilder $s (Prozess $k, $(have "$s")/$(need "$s")) $(date -u +%T)"
      MID=1 MIDLIST=$(ml "$s") blender -b --factory-startup --python blender/qissa/flug.py -- "$s" "out/fl_frames/${s}_fixmid" 100 2 \
        > "out/fl_frames/$s.fixmid$k.log" 2>&1
    done
    sleep 5
  done
}

splice() {
  local s=$1 D="out/fl_frames/$1_dec" n0 n1
  rm -rf "$D"; mkdir -p "$D"
  ffmpeg -loglevel error -y -i "public/flug/shots/$s.mp4" "$D/%05d.png" || return 1
  n0=$(ls "$D" | wc -l)
  python3 - "$s" "$D" "$n0" "$R" <<'PY' || return 1
import json, os, shutil, sys
s, D, n0, R = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
c = 0
for a, b in json.load(open(R))[s]:
    for k in range(a, b + 1):
        j = 2 * k
        if j > n0:
            continue
        shutil.copyfile(f"out/fl_frames/{s}_fixmid/{k:04d}.png", f"{D}/{j:05d}.png")
        c += 1
print(f"  {s}: {c} Zwischenbilder eingesetzt")
PY
  ffmpeg -loglevel error -y -framerate 60 -i "$D/%05d.png" -c:v libx264 -preset slow -crf 15 -pix_fmt yuv420p \
    "public/flug/shots/$s.fix.mp4" || return 1
  n1=$(ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -of csv=p=0 "public/flug/shots/$s.fix.mp4")
  [ "$n1" -eq "$n0" ] || { echo "❌ $s: $n1 statt $n0 Bilder"; rm -f "public/flug/shots/$s.fix.mp4"; return 1; }
  mkdir -p out/fl_frames/shots_interp
  cp "public/flug/shots/$s.mp4" "out/fl_frames/shots_interp/$s.mp4"
  mv "public/flug/shots/$s.fix.mp4" "public/flug/shots/$s.mp4"
  touch "out/fl_frames/$s.fixed"
  rm -rf "$D" "out/fl_frames/${s}_fixmid"
  echo "✅ $s: echte Zwischenbilder an schnellen Stellen ($n0 Bilder) $(date -u +%T)"
}

pgrep -f "blender -b" > /dev/null || find out/fl_frames -name '*.png' -size -1k -delete 2>/dev/null
echo "=== $(date -u +%T) Zwischenbilder für schnelle Schwenks: $SHOTS"
worker 1 &
w2=0
while true; do
  m=$(missing)
  if [ -n "$m" ] && ! pgrep -f render_flug.sh > /dev/null; then
    find out/fl_frames -name '*.png' -size -1k -delete 2>/dev/null
    echo "▶ rendern: $m $(date -u +%T)"
    JOBS=1 SAMPLES=2 MID_SHOTS="absturz beten" setsid ./scripts/render_flug.sh $m >> out/fl_render.log 2>&1 < /dev/null &
    sleep 60
  fi
  if [ "$w2" = 0 ] && [ -z "$m" ] && ! pgrep -f render_flug.sh > /dev/null && [ -n "$(open_shots)" ]; then
    worker 2 & w2=1
  fi
  for s in $SHOTS; do
    fixed "$s" && continue
    [ "$(have "$s")" -ge "$(need "$s")" ] || continue
    pgrep -f "flug.py -- $s out/fl_frames/${s}_fixmid" > /dev/null && continue
    splice "$s" || echo "❌ $s: Einsetzen fehlgeschlagen"
  done
  all=1; for s in $SHOTS; do fixed "$s" || all=0; done
  [ "$all" = 1 ] && [ -z "$(missing)" ] && ! pgrep -f render_flug.sh > /dev/null && break
  sleep 30
done
wait
echo "✅ alle Einstellungen + Zwischenbilder $(date -u +%T)"
python3 scripts/sfx_flug.py && ./scripts/finish_flug.sh || echo "❌ Ton/Schnitt"
