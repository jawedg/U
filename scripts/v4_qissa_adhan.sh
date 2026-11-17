#!/usr/bin/env bash
# v4: nur die Gasse neu rendern (Gespräch an der Tür), Rest läuft im Originaltempo weiter -> Ton -> Video (fortsetzbar)
cd "$(dirname "$0")/.."
find out/qissa_frames -name '*.png' -size -1k -delete
SAMPLES=2 MID_SHOTS="traum" ./scripts/render_qissa_adhan.sh gasse || exit 1
grep -q "❌" out/qissa_render.log && exit 1
python3 scripts/build_qissa_adhan.py --mark-rendered gasse | tail -2
python3 scripts/sfx_qissa_adhan.py
./scripts/finish_qissa_adhan.sh
