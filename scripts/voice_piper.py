#!/usr/bin/env python3
"""Kostenlose, OFFLINE KI-Stimme (Piper "Thorsten", deutsch) für das 3D-Video.

Einmalig:
  pip install sherpa-onnx soundfile
  Stimme laden (~115 MB) und entpacken nach models/:
  https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-de_DE-thorsten-high.tar.bz2

Starten:  npm run voice:3d
Erzeugt public/train/line-N.wav + src/train/timing.json (Wort-Zeiten für die Untertitel).
"""
import json
import re
import sys
from pathlib import Path

import sherpa_onnx
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "models" / "vits-piper-de_DE-thorsten-high"
SCRIPT = ROOT / "src" / "train" / "script.json"
OUT = ROOT / "public" / "train"
TIMING = ROOT / "src" / "train" / "timing.json"
SPEED = 1.12  # >1 = schneller (TikTok-Tempo)
PAUSE = 0.25  # Sekunden Pause nach jedem Satz


def main() -> None:
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=str(MODEL_DIR / "de_DE-thorsten-high.onnx"),
                tokens=str(MODEL_DIR / "tokens.txt"),
                data_dir=str(MODEL_DIR / "espeak-ng-data"),
            ),
            num_threads=4,
        ),
    )
    tts = sherpa_onnx.OfflineTts(cfg)
    OUT.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, s in enumerate(json.loads(SCRIPT.read_text(encoding="utf-8"))["sentences"]):
        spoken = s["text"].replace("*", "")
        audio = tts.generate(spoken, sid=0, speed=SPEED)
        f = OUT / f"line-{i}.wav"
        sf.write(f, audio.samples, audio.sample_rate)
        dur = len(audio.samples) / audio.sample_rate
        # Wort-Zeiten grob nach Silben/Buchstaben verteilen (Piper liefert keine Wortgrenzen)
        words = s["text"].split()
        weights = [len(re.sub(r"[^\wäöüÄÖÜß]", "", w)) + 2 + (4 if re.search(r"[,.:!?]$", w) else 0) for w in words]
        lead, tail = 0.12, 0.15
        usable = max(0.1, dur - lead - tail)
        t, timed = lead, []
        for w, wt in zip(words, weights):
            timed.append({"word": w, "start": round(t, 3)})
            t += usable * wt / sum(weights)
        lines.append({"file": f"train/line-{i}.wav", "seconds": round(dur + PAUSE, 3), "words": timed})
        print(f"🎙️  {i + 1}: {spoken} ({dur:.1f}s)")
    TIMING.write_text(json.dumps({"lines": lines}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("✅ fertig -> npm run render:3d")


if __name__ == "__main__":
    main()
