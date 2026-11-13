#!/usr/bin/env python3
"""Ton für die 3D-POV-Probe „Plan Rot“ (blender/pov): Raumklang, Stift, Gong, Lautsprecher-Knacken,
Stühle, Schritte, Schlüssel, Jalousien, Lichtschalter + Brummen, Herzschlag, Handy-Vibration,
Türklinke, Rütteln, Schlussschlag. Synthetisch.  ->  public/pov3d/sfx.mp3
"""
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
TOTAL = 20.5
N = int(TOTAL * SR)
rng = np.random.default_rng(21)
mix = np.zeros((N, 2))
t_all = np.arange(N) / SR


def band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4), len(x))


def noise(s):
    return rng.standard_normal(int(s * SR))


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4))


def norm(x):
    return x / (np.max(np.abs(x)) or 1)


def add(t0, x, g=1.0, pan=0.0):
    i = int(t0 * SR)
    x = x[: max(0, N - i)]
    mix[i:i + len(x), 0] += x * g * np.sqrt(0.5 * (1 - pan))
    mix[i:i + len(x), 1] += x * g * np.sqrt(0.5 * (1 + pan))


# Raumklang + Neonröhren-Brummen bis Licht aus (10,0 s)
room = norm(band(noise(TOTAL), 60, 900)) * 0.05
hum = (np.sin(2 * np.pi * 100 * t_all) * 0.6 + np.sin(2 * np.pi * 200 * t_all) * 0.3) * 0.025 * (t_all < 10.0)
mix[:, 0] += room + hum
mix[:, 1] += np.roll(room, 1000) + hum
# Stift kratzt (0–1,5 s)
for k in range(9):
    d = 0.08 + rng.random() * 0.12
    add(0.1 + k * 0.16, norm(band(noise(d), 2500, 9000)) * env(int(d * SR), 0.01, d / 2), 0.08, 0.3)
# Gong (1,0 s): zwei Töne
for i, (f0, t0) in enumerate(((659, 1.0), (523, 1.45))):
    t = np.arange(int(2.2 * SR)) / SR
    g = sum(np.sin(2 * np.pi * f0 * h * t) / (h * h) for h in (1, 2, 3)) * np.exp(-t * 1.8)
    add(t0, norm(band(g, 300, 3500)), 0.22, 0.4)
# Lautsprecher-Knacken vor/nach Durchsage
for t0 in (1.75, 9.45):
    add(t0, norm(band(noise(0.25), 500, 5000)) * env(int(0.25 * SR), 0.002, 0.05), 0.18, 0.5)
# Stühle rücken (3,4–4,6 s)
for k in range(5):
    d = 0.3 + rng.random() * 0.4
    t = np.arange(int(d * SR)) / SR
    x = np.sin(2 * np.pi * np.cumsum(180 + 120 * np.sin(t * 30) + rng.random() * 60) / SR) * band(noise(d), 100, 2000)
    add(3.4 + rng.random() * 1.2, norm(x) * np.sin(np.pi * t / d), 0.1, rng.random() * 1.2 - 0.6)
# Schritte der Lehrerin (4,6–6,8 s), danach 9,0–9,6 s
for t0 in list(np.arange(4.6, 6.8, 0.38)) + list(np.arange(8.9, 9.7, 0.36)):
    add(t0, norm(band(noise(0.12), 200, 4000)) * env(int(0.12 * SR), 0.001, 0.03), 0.18, 0.5)
# Schlüssel (7,3 / 7,55 s)
for t0, g in ((7.25, 0.35), (7.55, 0.5)):
    add(t0, norm(band(noise(0.06), 1500, 9000)) * env(int(0.06 * SR), 0.0005, 0.012), g, 0.6)
# Jalousien (9,4–10,8 s)
d = 1.4
x = band(noise(d), 1500, 7000) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 14 * np.arange(int(d * SR)) / SR)))
add(9.4, norm(x) * np.sin(np.pi * np.arange(int(d * SR)) / SR / d), 0.12, -0.7)
# Lichtschalter (10,0 s) + kurzes Flackern
add(9.98, norm(band(noise(0.04), 1000, 8000)) * env(int(0.04 * SR), 0.0005, 0.008), 0.6, 0.6)
# Ducken / Rascheln (10,4–11,6 s)
add(10.4, norm(band(noise(1.2), 300, 5000)) * np.sin(np.pi * np.arange(int(1.2 * SR)) / SR / 1.2) ** 2, 0.15)
# Dunkler Brumm-Ton + Herzschlag ab 10,5 s
drone = (np.sin(2 * np.pi * 46 * t_all) + 0.5 * np.sin(2 * np.pi * 69.3 * t_all)) * np.clip((t_all - 10.3) / 3, 0, 1) * (t_all < 17.6)
mix[:, 0] += drone * 0.06
mix[:, 1] += drone * 0.06


def thump(f=55, d=0.14):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * t * (1 - t * 2)) * env(len(t), 0.004, 0.04)


t, bpm = 11.0, 90
while t < 17.5:
    add(t, thump(), 0.45)
    add(t + 0.14, thump(47), 0.3)
    bpm = min(140, bpm + 4)
    t += 60 / bpm
# Handy vibriert (13,6 s)
d = 0.5
tt = np.arange(int(d * SR)) / SR
bz = np.sign(np.sin(2 * np.pi * 170 * tt)) * ((tt % 0.25) < 0.18)
add(13.6, norm(band(bz, 100, 2000)), 0.3)
# Türklinke quietscht langsam (15,8–16,8 s), Rütteln (17,0 s)
d = 1.0
tt = np.arange(int(d * SR)) / SR
sq = np.sin(2 * np.pi * np.cumsum(900 + 300 * tt + 40 * np.sin(tt * 25)) / SR) * band(noise(d), 600, 3000) * 3
add(15.8, norm(sq) * np.sin(np.pi * tt / d), 0.12, 0.7)
for t0 in (16.97, 17.07, 17.17):
    add(t0, norm(band(noise(0.1), 80, 2500)) * env(int(0.1 * SR), 0.001, 0.03), 0.45, 0.7)
# Schlussschlag (17,5 s)
d = 2.0
tt = np.arange(int(d * SR)) / SR
boom = np.sin(2 * np.pi * (40 + 50 * np.exp(-tt * 10)) * tt) * env(len(tt), 0.002, 0.5)
add(17.5, norm(boom), 0.7)

mix = np.tanh(mix * 1.3)
mix = mix / np.max(np.abs(mix)) * 0.85
out = ROOT / "public/pov3d"
with wave.open(str(out / "sfx.wav"), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(out / "sfx.wav"), "-b:a", "160k", str(out / "sfx.mp3")], check=True)
(out / "sfx.wav").unlink()
print("🔊 sfx.mp3", TOTAL, "s")
