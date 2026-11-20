#!/usr/bin/env bash
# Nachtrag v2: fehlendes heute-Bild (Blender-Prozess wurde wegen Speichermangel beendet) rendern, heute neu kodieren,
# dann nur die Remotion-Teile mit heute (p0 = Einstieg, p4/p5 = Mas'a-Halle) neu + zusammenfügen.
set -u
cd "$(dirname "$0")/.."
find out/zz_frames/heute -name '*.png' -size -1k -delete
JOBS=1 SAMPLES=2 PASSES=main ./scripts/render_qissa_zamzam.sh heute
n=$(find out/zz_frames/heute -name '*.png' -size +1k | wc -l)
[ "$n" -lt 442 ] && { echo "❌ heute nur $n/442"; exit 1; }
rm -f out/zz_parts/p0.mp4.ok out/zz_parts/p4.mp4.ok out/zz_parts/p5.mp4.ok
./scripts/finish_qissa_zamzam.sh
