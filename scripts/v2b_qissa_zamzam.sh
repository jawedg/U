#!/usr/bin/env bash
# wartet auf die Korrektur-Bilder (v2), prüft die 4 Einstellungen, baut Ton + Video neu (alle Remotion-Teile neu).
set -u
cd "$(dirname "$0")/.."
while pgrep -f v2_qissa_zamzam.sh > /dev/null; do sleep 60; done
for s in abschied wall quelle heute; do
  n=$(find out/zz_frames/$s -name '*.png' -size +1k | wc -l)
  echo "$s: $n Bilder, Video $(stat -c %y public/qissa_zamzam/shots/$s.mp4 | cut -c1-16)"
done
python3 scripts/build_qissa_zamzam.py > /dev/null
python3 scripts/sfx_qissa_zamzam.py
rm -f out/zz_parts/*.ok
./scripts/finish_qissa_zamzam.sh
