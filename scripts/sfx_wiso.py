#!/usr/bin/env python3
"""Dezente UI-Sounds fürs Lernvideo: pop (Begriff erscheint), ding (Prüfungswissen), whoosh (Themenwechsel)."""
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 44100
OUT = Path(__file__).resolve().parent.parent / "public" / "wiso" / "sfx"
rng = np.random.default_rng(3)


def save(name, x, peak=0.7):
    x = x / (np.max(np.abs(x)) or 1) * peak
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / f"{name}.wav"
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(tmp), "-b:a", "128k", str(OUT / f"{name}.mp3")], check=True)
    tmp.unlink()


def t_(s):
    return np.arange(int(s * SR)) / SR


def band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4), len(x))


# weiches „Pop“: kurzer Sinus mit fallender Tonhöhe
t = t_(0.12)
f = 900 * np.exp(-t * 18) + 380
pop = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.035) * np.minimum(1, t / 0.002)
save("pop", pop, 0.5)

# „Ding“: zwei helle, kurze Glockentöne
t = t_(1.2)
ding = sum(a * np.sin(2 * np.pi * fr * t) * np.exp(-t / d) for fr, a, d in [(1320, 1, 0.5), (1980, 0.4, 0.3), (2640, 0.2, 0.2)])
ding2 = np.zeros_like(ding)
k = int(0.11 * SR)
ding2[k:] = ding[: len(ding) - k] * 0.8
save("ding", ding * 0.6 + ding2, 0.5)

# Whoosh: Rauschen, das hell wird und wieder abklingt
t = t_(0.6)
n = rng.standard_normal(len(t))
w = np.zeros_like(n)
for i, (lo, hi) in enumerate([(200, 700), (500, 1500), (1000, 3000), (2000, 6000)]):
    w += band(n, lo, hi) * np.exp(-((t / 0.6 - (i + 0.5) / 4) ** 2) / 0.02)
save("whoosh", w * np.sin(np.pi * t / 0.6), 0.45)

# Marker-Strich (für Unterstreichungen/Tabellen)
t = t_(0.35)
m = band(rng.standard_normal(len(t)), 1500, 7000) * (0.6 + 0.4 * np.sin(2 * np.pi * 22 * t)) * np.sin(np.pi * t / 0.35)
save("marker", m, 0.3)
print("ok")
