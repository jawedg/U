#!/usr/bin/env bash
# v5: Algieba-Erzählung (fließend), Fixes (Beratung ruhiger, Bilal vor der Säule, Mutter aus echter Tür), neues Ende.
# Neu gerendert: Einstellungen mit Fix oder deutlich längerer Dauer. Leicht längere (Tempo >= 0,95) werden per
# Bewegungs-Interpolation minimal gestreckt (60-fps-Vorlage -> kaum Artefakte), dann alles im Originaltempo. Fortsetzbar.
cd "$(dirname "$0")/.."
RENDER="beratung traum morgen dach_b ende"
STRETCH="gasse dach_a umar"
find out/qissa_frames -name '*.png' -size -1k -delete
SAMPLES=2 MID_SHOTS="traum" ./scripts/render_qissa_adhan.sh $RENDER || exit 1
python3 scripts/build_qissa_adhan.py --mark-rendered $RENDER | tail -1
for s in $STRETCH; do
  python3 - "$s" <<'PY' || exit 1
import json, subprocess, sys, shutil
from pathlib import Path
s = sys.argv[1]
tl = json.load(open("src/qissa_adhan/timeline.json"))
seg = next(x for x in tl["segments"] if x["id"] == s)
old = seg["src_dur"]; new = seg["dur"]
f = Path(f"public/qissa_adhan/shots/{s}.mp4")
bak = f.with_suffix(".orig.mp4")
if not bak.exists():
    shutil.copy(f, bak)
if new > old + 0.02:
    k = new / old
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(bak), "-vf",
                    f"setpts=PTS*{k:.5f},minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", str(f)], check=True)
    print(f"↔ {s}: {old:.2f}s -> {new:.2f}s (x{k:.3f})", flush=True)
PY
done
python3 scripts/build_qissa_adhan.py --mark-rendered $STRETCH | tail -3
python3 scripts/sfx_qissa_adhan.py
rm -f out/qissa_parts/*.ok
./scripts/finish_qissa_adhan.sh
