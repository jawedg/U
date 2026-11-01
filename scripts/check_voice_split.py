#!/usr/bin/env python3
"""Prüft lokal (Whisper), ob jedes Sprachstück mit dem richtigen Satz beginnt und endet.
Aufruf: python3 scripts/check_voice_split.py wiso"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import voice_gemini as vg  # noqa: E402

proj = sys.argv[1] if len(sys.argv) > 1 else "wiso"
S = json.loads((vg.ROOT / "src" / proj / "script.json").read_text())["sentences"]
L = json.loads((vg.ROOT / "src" / proj / "timing.json").read_text())["lines"]
bad = 0
for i, (s, l) in enumerate(zip(S, L)):
    if not l["file"]:
        continue
    got = vg._norm(vg.transcribe(vg.ROOT / "public" / l["file"]))
    want = vg._norm(s["text"])
    ok1 = any(w in got[:3] for w in want[:2]) or any(w in want[:3] for w in got[:2])
    ok2 = any(w in got[-3:] for w in want[-2:]) or any(w in want[-3:] for w in got[-2:])
    if not (ok1 and ok2):
        bad += 1
        print(f"{i}: SOLL «{' '.join(want[:4])} … {' '.join(want[-4:])}»  IST «{' '.join(got[:4])} … {' '.join(got[-4:])}»")
print("Fehlerhafte Stücke:", bad, "von", len(S))
