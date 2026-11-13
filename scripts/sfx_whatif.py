#!/usr/bin/env python3
"""Ton-Spur für „Was wäre, wenn …“ (src/whatif): Wind, Schritte im Schnee, Eis-Knacken, Einbruch,
Unterwasser, Wellen, Herzschlag im Takt der Anzeige. Alles synthetisch, eine Datei für das ganze Video.

Starten (nach voice_gemini.py --project whatif):  python3 scripts/sfx_whatif.py  -> public/whatif/sfx.mp3
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
rng = np.random.default_rng(3)

script = json.loads((ROOT / "src/whatif/script.json").read_text())
timing = json.loads((ROOT / "src/whatif/timing.json").read_text())
FPS = script.get("fps", 30)
shots, acc = [], 0
for s, l in zip(script["sentences"], timing["lines"]):
    dur = round((s["delay"] + l["seconds"] + s["pad"]) * FPS)
    shots.append({**s, "start": acc / FPS, "dur": dur / FPS})
    acc += dur
TOTAL = acc / FPS
N = int(TOTAL * SR) + SR
mix = np.zeros((N, 2))
S = {s["shot"]: s for s in shots}


def band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = 1 / (1 + (lo / np.maximum(f, 1)) ** 4) * 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))


def noise(sec):
    return rng.standard_normal(int(sec * SR))


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4))


def add(t0, x, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    x = x[: N - i]
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    mix[i:i + len(x), 0] += x * gain * l
    mix[i:i + len(x), 1] += x * gain * r


def norm(x):
    return x / (np.max(np.abs(x)) or 1)


t_all = np.arange(N) / SR
crack, under = S["crack"], S["under"]
uw_a = crack["start"] + 3.15
uw_b = under["start"] + under["dur"]
underwater = ((t_all > uw_a) & (t_all < uw_b)).astype(float)
uw = np.convolve(underwater, np.ones(2000) / 2000, mode="same")

# Wind (ganze Länge), unter Wasser fast weg
w = band(noise(N / SR), 120, 900)
w = norm(w) * (0.6 + 0.4 * np.sin(t_all * 0.37) * np.sin(t_all * 0.13 + 1))
w2 = norm(band(noise(N / SR), 1500, 5000)) * 0.15 * (0.5 + 0.5 * np.sin(t_all * 0.8))
wind = (w + w2) * (1 - 0.92 * uw)
mix[:, 0] += wind * 0.16
mix[:, 1] += np.roll(wind, 900) * 0.16

# Unterwasser-Rauschen
rumble = norm(band(noise(N / SR), 30, 260)) * uw
mix[:, 0] += rumble * 0.5
mix[:, 1] += rumble * 0.5

# Schritte im Schnee
walk = S["walk"]
k = 0
while True:
    t = 0.25 + k / 1.8
    if t > walk["dur"] * 0.82:
        break
    n = int(0.22 * SR)
    grains = np.zeros(n)
    for _ in range(40):
        p = int(rng.random() * n * 0.7)
        L = int(SR * (0.002 + rng.random() * 0.006))
        grains[p:p + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 3))
    x = band(grains, 900, 7000) * env(n, 0.01, 0.07) + band(noise(0.22), 80, 300) * env(n, 0.005, 0.03) * 0.6
    add(walk["start"] + t, norm(x), 0.32, -0.25 if k % 2 else 0.25)
    k += 1


def ping(f0=3800, f1=350, dur=0.35):
    """singendes Eis: absteigender Zirp-Ton"""
    t = np.arange(int(dur * SR)) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) + band(rng.standard_normal(len(t)), 2000, 9000) * np.exp(-t * 60) * 0.6


c0 = crack["start"]
# Ächzen
t = np.arange(int(1.6 * SR)) / SR
f = 70 + 25 * np.sin(t * 2.3) + 15 * t
groan = sum(np.sin(2 * np.pi * np.cumsum(f * h) / SR) / h for h in (1, 2, 3, 5)) * env(len(t), 0.25, 0.7)
groan *= 1 + 0.5 * band(rng.standard_normal(len(t)), 5, 40) / 3
add(c0 + 0.3, norm(groan), 0.5)
for tt, g, pan in [(0.55, 0.55, -0.3), (1.0, 0.6, 0.4), (1.45, 0.5, -0.1), (1.85, 0.65, 0.2), (2.3, 0.7, -0.4)]:
    add(c0 + tt, norm(ping(3000 + rng.random() * 1500, 250 + rng.random() * 200)), g, pan)
    crk = band(noise(0.08), 600, 9000) * env(int(0.08 * SR), 0.0005, 0.012)
    add(c0 + tt - 0.01, norm(crk), 0.8, pan)
# Bruch
br = band(noise(0.9), 200, 8000) * env(int(0.9 * SR), 0.002, 0.22)
for _ in range(25):
    add(c0 + 2.75 + rng.random() * 0.4, norm(band(noise(0.05), 800, 9000) * env(int(0.05 * SR), 0.0005, 0.01)), 0.5, rng.random() - 0.5)
add(c0 + 2.75, norm(br), 0.9)
add(c0 + 2.75, norm(band(noise(0.5), 30, 140) * env(int(0.5 * SR), 0.003, 0.15)), 0.9)
# Platsch + Eintauchen
sp = band(noise(1.4), 150, 6000) * env(int(1.4 * SR), 0.01, 0.35)
add(c0 + 3.18, norm(sp), 1.0)
add(c0 + 3.22, norm(band(noise(1.0), 40, 400) * env(int(1.0 * SR), 0.02, 0.4)), 0.8)


def bubble():
    d = 0.03 + rng.random() * 0.05
    t = np.arange(int(d * SR)) / SR
    f0 = 300 + rng.random() * 700
    f = f0 * (1 + t / d * 1.5)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d)


for i in range(140):
    tt = rng.random() ** 2 * 1.6 if i < 90 else rng.random() * under["dur"]
    add(under["start"] + tt, bubble(), 0.18 + rng.random() * 0.12, rng.random() * 1.4 - 0.7)

# Auftauchen
add(S["surface"]["start"], norm(band(noise(0.9), 200, 5000) * env(int(0.9 * SR), 0.02, 0.25)), 0.7)
# Wellen/Plätschern an der Oberfläche
for name in ("surface", "turn", "arms"):
    s = S[name]
    x = band(noise(s["dur"]), 250, 2200)
    tt = np.arange(len(x)) / SR
    x = norm(x) * (0.4 + 0.6 * np.abs(np.sin(tt * 2.1 + 0.5))) ** 2
    fade = np.minimum(1, np.minimum(tt / 0.2, (s["dur"] - tt) / 0.2))
    add(s["start"], x * fade, 0.22)
# Hände aufs Eis, dann Beinschläge
a0 = S["arms"]["start"]
for tt in (1.05, 1.23):
    add(a0 + tt, norm(band(noise(0.15), 150, 3000) * env(int(0.15 * SR), 0.001, 0.04)), 0.6)
tt = 1.35
while tt < S["arms"]["dur"] - 0.1:
    add(a0 + tt, norm(band(noise(0.35), 300, 5000) * env(int(0.35 * SR), 0.01, 0.09)), 0.35, rng.random() - 0.5)
    tt += 0.42
# Rollen über Eis
r0 = S["roll"]
x = band(noise(r0["dur"]), 400, 5000)
tt = np.arange(len(x)) / SR
x = norm(x) * np.sin(np.pi * np.clip(tt / (r0["dur"] - 0.2), 0, 1)) ** 2 * (0.6 + 0.4 * np.sin(tt * 7))
add(r0["start"], x, 0.3)
add(r0["start"] + r0["dur"] - 0.35, norm(band(noise(0.3), 60, 600) * env(int(0.3 * SR), 0.003, 0.08)), 0.5)

# Herzschlag im Takt der Anzeige
bpm_at = []
for i, s in enumerate(shots):
    prev = shots[max(0, i - 1)]["hud"][0] if i else s["hud"][0]
    bpm_at.append((s["start"], s["start"] + s["dur"], prev, s["hud"][0]))


def bpm(t):
    for a, b, p, c in bpm_at:
        if a <= t < b:
            return p + (c - p) * min(1, (t - a) / 1.4)
    return bpm_at[-1][3]


def thump(f=55, d=0.12):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * t * (1 - t * 2)) * env(len(t), 0.004, 0.035)


t = 1.6
end_start = S["end"]["start"]
while t < TOTAL - 1.0:
    g = 0.5 if t < end_start else 0.5 * max(0, 1 - (t - end_start) / 2.5)
    add(t, thump(58), g)
    add(t + 0.13, thump(50), g * 0.7)
    t += 60 / bpm(t)

mix = np.tanh(mix * 1.1) * 0.9
mix /= np.max(np.abs(mix))
mix *= 0.85
out = ROOT / "public/whatif"
out.mkdir(parents=True, exist_ok=True)
with wave.open(str(out / "sfx.wav"), "wb") as wv:
    wv.setnchannels(2)
    wv.setsampwidth(2)
    wv.setframerate(SR)
    wv.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(out / "sfx.wav"), "-b:a", "160k", str(out / "sfx.mp3")], check=True)
(out / "sfx.wav").unlink()
print(f"🔊 sfx.mp3 {TOTAL:.1f}s")
