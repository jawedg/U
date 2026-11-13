#!/usr/bin/env python3
"""Ton für „Blindflug im Reaktor“ (blender/fuku): Raumklang + 50-Hz-Brummen, Beben mit Klappern,
Alarm-Summer, Notstrom-Diesel, Monitor-Piepen, Wassertosen, Einschlag, KLACK + Stille,
Taschenlampen-Klicks, Herzschlag, Grollen, Schlussschlag. Synthetisch -> public/fuku/sfx.mp3
"""
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
TOTAL = 63.0
N = int(TOTAL * SR)
rng = np.random.default_rng(311)
mix = np.zeros((N, 2))
t_all = np.arange(N) / SR
QUAKE = (1.2, 9.6)
WARN, IMPACT, BLACK, K2LIGHT, MYLIGHT, END = 22.0, 30.2, 31.0, 35.2, 40.6, 59.4


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


def gate(a, b, fade=0.05):
    return np.clip((t_all - a) / fade, 0, 1) * np.clip((b - t_all) / fade, 0, 1)


power = gate(-1, BLACK, 0.01)
# Lüftung + 50-Hz-Brummen (Ostjapan) bis zum Blackout
room = norm(band(noise(TOTAL), 80, 1200)) * 0.05 * power
hum = (np.sin(2 * np.pi * 50 * t_all) * 0.6 + np.sin(2 * np.pi * 100 * t_all) * 0.35 + np.sin(2 * np.pi * 150 * t_all) * 0.15) * 0.03 * power
mix[:, 0] += room + hum
mix[:, 1] += np.roll(room, 777) + hum
# Beben: tiefes Rumpeln + Klappern + Knarzen
q = gate(QUAKE[0], QUAKE[1], 0.8)
rumble = norm(band(noise(TOTAL), 18, 140)) * q * (0.7 + 0.3 * np.sin(t_all * 3.1))
mix[:, 0] += rumble * 0.55
mix[:, 1] += np.roll(rumble, 300) * 0.55
for _ in range(220):
    t0 = rng.uniform(*QUAKE)
    d = 0.03 + rng.random() * 0.05
    add(t0, norm(band(noise(d), 800, 7000)) * env(int(d * SR), 0.001, 0.012), 0.12 * rng.random(), rng.random() * 2 - 1)
for _ in range(6):
    d = 0.6 + rng.random()
    tt = np.arange(int(d * SR)) / SR
    cr = np.sin(2 * np.pi * np.cumsum(90 + 40 * np.sin(tt * 7)) / SR) * band(noise(d), 60, 900)
    add(rng.uniform(2, 8), norm(cr) * np.sin(np.pi * tt / d), 0.12, rng.random() - 0.5)
add(3.75, norm(band(noise(0.3), 60, 2500)) * env(int(0.3 * SR), 0.001, 0.06), 0.45, -0.5)  # Ordner fällt
# Alarm-Summer (zweitönig) ab Beben, später leiser, bis Blackout
t = 1.7
while t < BLACK - 0.2:
    d = 0.35
    tt = np.arange(int(d * SR)) / SR
    tone = np.sign(np.sin(2 * np.pi * (880 if int(t * 2.5) % 2 else 660) * tt)) * env(len(tt), 0.005, 0.25)
    add(t, band(tone, 300, 4000), 0.06 if t < 10 else 0.035, 0.2)
    t += 0.45
# Notstrom-Diesel ab ~9,8 s (Fremdnetz weg) bis Blackout
dg = (np.sin(2 * np.pi * 25 * t_all) + 0.5 * np.sin(2 * np.pi * 50 * t_all + 1) + 0.3 * norm(band(noise(TOTAL), 30, 300))) * gate(9.8, BLACK, 1.0) * 0.05
mix[:, 0] += dg
mix[:, 1] += dg
# Monitor-Warnung piept
for k in range(8):
    tt = np.arange(int(0.18 * SR)) / SR
    add(WARN + k * 0.8, np.sin(2 * np.pi * 1760 * tt) * env(len(tt), 0.003, 0.12), 0.12, 0.4)
# Welle: Tosen schwillt an -> Einschlag
d = IMPACT - 27.8 + 3.0
tt = np.arange(int(d * SR)) / SR
roar = norm(band(noise(d), 40, 2500)) * np.clip(tt / (IMPACT - 27.8), 0, 1) ** 2 * np.exp(-np.clip(tt - (IMPACT - 27.8), 0, None) * 1.2)
add(27.8, roar, 0.6)
tt = np.arange(int(3 * SR)) / SR
boom = np.sin(2 * np.pi * (34 + 60 * np.exp(-tt * 9)) * tt) * env(len(tt), 0.003, 0.7) + band(noise(3), 200, 6000) * env(len(tt), 0.002, 0.25) * 0.6
add(IMPACT, norm(boom), 0.9)
# KLACK (Relais) + alles verstummt
add(BLACK, norm(band(noise(0.08), 400, 9000)) * env(int(0.08 * SR), 0.0005, 0.015), 0.9, 0.3)
tt = np.arange(int(0.6 * SR)) / SR
add(BLACK, np.sin(2 * np.pi * 50 * tt * (1 - tt * 0.8)) * np.exp(-tt * 5), 0.12)  # Brummen fällt ab
# Dunkelheit: fernes Wasserrauschen, Tropfen
far = norm(band(noise(TOTAL), 60, 700)) * gate(BLACK + 0.8, END, 2.0) * 0.06
mix[:, 0] += far
mix[:, 1] += np.roll(far, 2000)
for _ in range(14):
    tt = np.arange(int(0.06 * SR)) / SR
    add(rng.uniform(BLACK + 2, END - 1), np.sin(2 * np.pi * (1200 + rng.random() * 800) * tt * (1 - tt * 4)) * env(len(tt), 0.001, 0.02), 0.05, rng.random() - 0.5)
# Taschenlampen-Klicks
for t0, p in ((K2LIGHT, 0.5), (MYLIGHT, -0.2)):
    add(t0 - 0.02, norm(band(noise(0.03), 1500, 9000)) * env(int(0.03 * SR), 0.0003, 0.006), 0.5, p)
# Herzschlag (leise) im Dunkeln


def thump(f=52, d=0.14):
    tt = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * tt * (1 - tt * 2)) * env(len(tt), 0.004, 0.045)


t, bpm = 41.0, 84
while t < END - 0.3:
    add(t, thump(), 0.35)
    add(t + 0.15, thump(45), 0.22)
    bpm = min(118, bpm + 1.5)
    t += 60 / bpm
# Grollen durch den Boden (Tür-Szene)
add(50.8, norm(band(noise(3.0), 18, 120)) * np.sin(np.pi * np.arange(int(3 * SR)) / SR / 3.0), 0.5)
# Schnitt auf Schwarz
tt = np.arange(int(2.5 * SR)) / SR
add(END, norm(np.sin(2 * np.pi * (38 + 40 * np.exp(-tt * 8)) * tt) * env(len(tt), 0.003, 0.6)), 0.7)

mix = np.tanh(mix * 1.3)
mix = mix / np.max(np.abs(mix)) * 0.85
out = ROOT / "public/fuku"
out.mkdir(parents=True, exist_ok=True)
with wave.open(str(out / "sfx.wav"), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(out / "sfx.wav"), "-b:a", "160k", str(out / "sfx.mp3")], check=True)
(out / "sfx.wav").unlink()
print("🔊 sfx.mp3", TOTAL, "s")
