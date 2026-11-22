#!/usr/bin/env bash
# QISSAH Folge 3 v2 (Nutzer-Korrekturen): nur betroffene Stellen neu rendern, fortsetzbar.
#  - ohne Kinder vor der Tür: ankunft (ganz), tuer1 1–360, abend1 1–360, abend2 (ganz), besuch2 210–340  → alter Zeitplan (timeline_v1)
#  - neu mit Tablett statt Händen + längeren Pausen: tuer2, segen (+ echte Zwischenbilder)                  → neuer Zeitplan
#  - Ismail geht um die Mauer herum: bau (ganz)
# Danach: Einstellungen kodieren (Teilstücke in die alten Videos einsetzen), Ton, Remotion, HEVC.
set -u
cd "$(dirname "$0")/.."
V1=src/qissa_kaaba/timeline_v1.json
O=out/kb_frames2
mkdir -p $O
find $O -name '*.png' -size -1k -delete 2>/dev/null
fr() { python3 -c "import json; print({x['id']: x for x in json.load(open('${2:-src/qissa_kaaba/timeline.json}'))['segments']}['$1']['frames'])"; }
job() {  # shot a b tl mid
  local s=$1 a=$2 b=$3 tl=$4 mid=${5:-0} d=$O/$1
  [ "$mid" = 1 ] && d=$O/${1}_mid
  mkdir -p $d
  local hi=$b; [ "$mid" = 1 ] && hi=$((b - 1))   # Zwischenbilder: Blender rendert a … b-1
  local have; have=$(python3 -c "import os; print(sum(1 for k in range($a, $hi + 1) if os.path.exists('$d/%04d.png' % k) and os.path.getsize('$d/%04d.png' % k) > 1000))")
  [ "$have" -ge $((hi - a + 1)) ] && return 0
  echo "▶ $s $a–$b $( [ $mid = 1 ] && echo Zwischenbilder) $(date -u +%T)"
  if [ "$mid" = 1 ]; then
    MID=1 FRAMES=$a-$b TL_FILE=$tl blender -b --factory-startup --python blender/qissa/kaaba.py -- $s $d 100 2 > $O/$s.mid.$a.log 2>&1
  else
    FRAMES=$a-$b TL_FILE=$tl blender -b --factory-startup --python blender/qissa/kaaba.py -- $s $d 100 2 > $O/$s.$a.log 2>&1
  fi
}
NEW=src/qissa_kaaba/timeline.json
python3 scripts/build_qissa_kaaba.py > /dev/null
NT2=$(fr tuer2); NSG=$(fr segen); NBAU=$(fr bau)
H2=$((NSG / 2))
workerA() {
  job tuer1 1 360 $V1; job ankunft 1 $(fr ankunft $V1) $V1; job besuch2 210 340 $V1; job bau 1 $NBAU $NEW
  job segen 1 $H2 $NEW; job segen 1 $((H2 + 1)) $NEW 1
}
workerB() {
  job abend1 1 360 $V1; job abend2 1 $(fr abend2 $V1) $V1; job tuer2 1 $NT2 $NEW
  job segen $((H2 + 1)) $NSG $NEW; job segen $((H2 + 1)) $NSG $NEW 1
}
for attempt in 1 2 3; do
  workerA & sleep 25; workerB & wait
  find $O -name '*.png' -size -1k -delete
done
echo "🖼  Bilder fertig $(date -u +%T)"
python3 scripts/v2_kaaba_splice.py && echo "✅ Einstellungen eingesetzt" || { echo "❌ Einsetzen fehlgeschlagen"; exit 1; }
python3 scripts/build_qissa_kaaba.py --mark-rendered tuer2 segen | tail -1
python3 scripts/sfx_qissa_kaaba.py
rm -f out/kb_parts/*.ok
./scripts/finish_qissa_kaaba.sh
