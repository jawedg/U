#!/usr/bin/env python3
"""Ton für „Futaba, 11. März 2011“ (blender/futaba): Kleinstadt-Atmo (Wind, Vögel, Auto), Schritte,
Handy-Nachricht, Erdbeben-Frühwarnung auf vielen Handys, Beben (Grollen, Klirren, Leitungen, Töpfe, Ziegel),
Autoalarm. Synthetisch -> public/futaba/sfx.mp3 (Zeiten aus src/futaba/events.json)."""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
EV = json.load(open(ROOT / "src/futaba/events.json"))
SR = 44100
TOTAL = EV["end"] + 1.0
N = int(TOTAL * SR)
rng = np.random.default_rng(2011)
mix = np.zeros((N, 2))
t_all = np.arange(N) / SR
Q = EV["quake"]


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
    if i >= N:
        return
    x = x[: max(0, N - i)]
    mix[i:i + len(x), 0] += x * g * np.sqrt(0.5 * (1 - pan))
    mix[i:i + len(x), 1] += x * g * np.sqrt(0.5 * (1 + pan))


def qamp(t):
    return np.clip((t - Q) / 0.8, 0, 1) * (0.85 + 0.15 * np.sin(t * 1.3))


# Atmo: Wind + fernes Rauschen, Vögel (verstummen beim Beben)
wind = norm(band(noise(TOTAL), 90, 1400)) * 0.05
mix[:, 0] += wind
mix[:, 1] += np.roll(wind, 5000)
t = 0.4
while t < Q - 0.3:
    for _ in range(rng.integers(2, 5)):
        d = 0.06 + rng.random() * 0.08
        tt = np.arange(int(d * SR)) / SR
        f0 = 2600 + rng.random() * 2200
        ch = np.sin(2 * np.pi * (f0 + 1800 * tt / d * rng.choice([-1, 1])) * tt) * np.sin(np.pi * tt / d)
        add(t, ch, 0.05, rng.random() * 2 - 1)
        t += d + 0.04
    t += 0.9 + rng.random() * 1.4
# Auto fährt in der Ferne vorbei
d = 5.0
tt = np.arange(int(d * SR)) / SR
car = norm(band(noise(d), 60, 900)) * np.sin(np.pi * tt / d) ** 2
add(1.0, car, 0.18, -0.6)
# Schritte (ich + Sota)
for start, pan, g in ((0.25, 0.1, 0.22), (0.55, -0.6, 0.16)):
    t = start
    while t < EV["stop"]:
        d = 0.09
        s = band(noise(d), 150, 4000) * env(int(d * SR), 0.002, 0.025) + np.sin(2 * np.pi * 70 * np.arange(int(d * SR)) / SR) * env(int(d * SR), 0.002, 0.03) * 0.6
        add(t + rng.random() * 0.02, norm(s), g * (0.8 + 0.3 * rng.random()), pan)
        t += 0.63
# Handy: Vibration + Nachricht
P = EV["ping"]
for k in range(2):
    tt = np.arange(int(0.25 * SR)) / SR
    add(P + k * 0.32, np.sign(np.sin(2 * np.pi * 160 * tt)) * band(np.ones(len(tt)), 60, 600) * 0 + np.sin(2 * np.pi * 160 * tt) * np.sin(np.pi * tt / 0.25), 0.18, 0.15)
for k, f in enumerate((1318.5, 1760.0)):
    tt = np.arange(int(0.35 * SR)) / SR
    add(P + 0.1 + k * 0.12, np.sin(2 * np.pi * f * tt) * env(len(tt), 0.003, 0.12), 0.22, 0.15)
# Erdbeben-Frühwarnung: schrilles Signal aus vielen Handys
A = EV["alarm"]


def eew(dur):
    tt = np.arange(int(dur * SR)) / SR
    f = np.where((tt * 4).astype(int) % 2 == 0, 1046.5, 1396.9)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    tone += 0.35 * np.sin(2 * 2 * np.pi * np.cumsum(f) / SR)
    gate = ((tt * 8).astype(int) % 2 == 0) * 0.6 + 0.4
    return tone * gate * np.minimum(1, tt / 0.02)


add(A, eew(Q + 2.2 - A), 0.22, 0.1)
for k, (dt, pan) in enumerate(((0.12, -0.7), (0.25, 0.6), (0.33, -0.3), (0.47, 0.8), (0.6, 0.3))):
    x = eew(Q + 1.8 - A - dt)
    add(A + dt, band(x, 500, 4500) * np.linspace(1, 0.5, len(x)), 0.1, pan)
# Beben: tiefes Grollen + Klirren + Knarzen + Leitungen
qa = qamp(t_all)
rumble = norm(band(noise(TOTAL), 16, 120)) * qa
mix[:, 0] += rumble * 0.75
mix[:, 1] += np.roll(rumble, 400) * 0.75
roar = norm(band(noise(TOTAL), 80, 900)) * qa * 0.25
mix[:, 0] += roar
mix[:, 1] += np.roll(roar, 900)
for _ in range(420):
    t0 = rng.uniform(Q + 0.3, TOTAL - 0.3)
    d = 0.02 + rng.random() * 0.04
    add(t0, norm(band(noise(d), 1500, 9000)) * env(int(d * SR), 0.001, 0.01), 0.07 * rng.random(), rng.random() * 2 - 1)
for _ in range(10):
    d = 0.7 + rng.random()
    tt = np.arange(int(d * SR)) / SR
    cr = np.sin(2 * np.pi * np.cumsum(70 + 50 * np.sin(tt * 6)) / SR) * band(noise(d), 60, 900)
    add(rng.uniform(Q + 0.5, TOTAL - 1.0), norm(cr) * np.sin(np.pi * tt / d), 0.14, rng.random() - 0.5)
for _ in range(14):  # Leitungen schlagen
    d = 0.4
    tt = np.arange(int(d * SR)) / SR
    add(rng.uniform(Q + 0.8, TOTAL - 0.5), norm(band(noise(d), 40, 400)) * np.sin(np.pi * tt / d) ** 2, 0.18, rng.random() * 2 - 1)
# Töpfe zerbrechen, Ziegel krachen
for t0 in EV.get("pot", []):
    d = 0.5
    x = norm(band(noise(d), 700, 9000)) * env(int(d * SR), 0.001, 0.08) + 0.5 * norm(band(noise(d), 150, 1200)) * env(int(d * SR), 0.001, 0.04)
    add(t0, x, 0.35, -0.7)
for t0 in EV.get("tile", []):
    d = 0.4
    x = norm(band(noise(d), 400, 7000)) * env(int(d * SR), 0.001, 0.05)
    add(t0, x, 0.4, 0.6)
# Autoalarm
ca = 12.2
tt = np.arange(int((TOTAL - ca) * SR)) / SR
f = 900 + 500 * np.sign(np.sin(2 * np.pi * 1.6 * tt))
alarm = band(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 300, 3000) * np.minimum(1, tt / 0.3)
add(ca, alarm, 0.06, 0.8)

mix = np.tanh(mix * 1.4)
mix = mix / np.max(np.abs(mix)) * 0.85
out = ROOT / "public/futaba"
out.mkdir(parents=True, exist_ok=True)
with wave.open(str(out / "sfx.wav"), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(out / "sfx.wav"), "-b:a", "160k", str(out / "sfx.mp3")], check=True)
(out / "sfx.wav").unlink()
print("🔊 sfx.mp3", TOTAL, "s")
