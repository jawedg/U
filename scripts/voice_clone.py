#!/usr/bin/env python3
"""Stimme des Nutzers: wandelt fertige Sprachaufnahmen (z. B. Gemini-Erzähler) per Seed-VC in die Stimmfarbe des Nutzers um.

Nur für die EIGENE Stimme des Nutzers (seine Erlaubnis). Die Vorlage liegt außerhalb des Repos (/home/user/voice_ref/,
nicht committen). Läuft mit der eigenen Umgebung /home/user/venv-vc (Seed-VC, PyTorch, CPU – ca. 18 s Rechenzeit je
Sekunde Sprache). Die Modelle werden EINMAL geladen, dann alle Dateien umgewandelt.

  /home/user/venv-vc/bin/python scripts/voice_clone.py --target /home/user/voice_ref/meine_stimme_25s.wav \
      --out <ordner> datei1.wav datei2.wav …
Ausgabe: <ordner>/<name>.wav (22,05 kHz mono), bereits umgewandelte werden übersprungen.
"""
import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")  # Xet-Speicher ist in der Cloud gesperrt -> normaler HTTP-Download

ap = argparse.ArgumentParser()
ap.add_argument("--target", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--steps", type=int, default=25)
ap.add_argument("--cfg", type=float, default=0.7)
ap.add_argument("files", nargs="+")
a = ap.parse_args()

import seed_vc.inference as I  # noqa: E402

args = argparse.Namespace(source=None, target=a.target, output=None, diffusion_steps=a.steps, length_adjust=1.0,
                          inference_cfg_rate=a.cfg, f0_condition=False, auto_f0_adjust=False, semi_tone_shift=0,
                          checkpoint=None, config=None, fp16=False)
models = I.load_models(args)
I.load_models = lambda _args: models  # einmal laden, für alle Dateien nutzen

out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
tmp = out / "_tmp"
for f in a.files:
    f = Path(f)
    dst = out / f"{f.stem}.wav"
    if dst.exists() and dst.stat().st_size > 1000:
        continue
    args.source, args.output = str(f), str(tmp)
    I.main(args)
    res = sorted(tmp.glob("vc_*.wav"), key=lambda p: p.stat().st_mtime)[-1]
    res.replace(dst)
    print("✓", dst, flush=True)
if tmp.exists():
    for p in tmp.glob("*"):
        p.unlink()
    tmp.rmdir()
