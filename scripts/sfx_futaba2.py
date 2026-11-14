#!/usr/bin/env python3
"""Ton für „Futaba, 11. März 2011 – Teil 1“ (blender/inkpop/scene1.py).
Morgengrauen: Wind, Krähen, Lautsprecherwagen fährt vorbei; Schlag zur Zeitkarte;
Heimweg: Vögel, Schritte, Fegen, Handy-Nachricht; Erdbeben-Frühwarnung aus vielen Handys; Beben mit Grollen,
Klirren, Leitungen, umfallenden Fahrrädern, Töpfen, Ziegeln, Autoalarm. Synthetisch -> public/futaba2/sfx.mp3
Außerdem: Lautsprecher-Durchsage mit Megafon-Klang -> public/futaba2/lsp_radio.wav"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TL = json.load(open(ROOT / "src/futaba2/timeline.json"))
EV = json.load(open(ROOT / "src/futaba2/events.json"))
SR = 44100
TOTAL = TL["END"] + 1.5
N = int(TOTAL * SR)
rng = np.random.default_rng(311)
mix = np.zeros((N, 2))
t_all = np.arange(N) / SR
Q, A_END, B0, EEW, PING = TL["QUAKE"], TL["A_END"], TL["B0"], TL["EEW"], TL["PING"]


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
    if i >= N or i < 0:
        return
    x = x[: max(0, N - i)]
    mix[i:i + len(x), 0] += x * g * np.sqrt(0.5 * (1 - pan))
    mix[i:i + len(x), 1] += x * g * np.sqrt(0.5 * (1 + pan))


def gate(a, b, fade=0.05):
    return np.clip((t_all - a) / fade, 0, 1) * np.clip((b - t_all) / fade, 0, 1)


def chirp(t, g, pan):
    d = 0.06 + rng.random() * 0.08
    tt = np.arange(int(d * SR)) / SR
    f0 = 2600 + rng.random() * 2200
    add(t, np.sin(2 * np.pi * (f0 + 1800 * tt / d * rng.choice([-1, 1])) * tt) * np.sin(np.pi * tt / d), g, pan)
    return d


# --- Morgengrauen (0 .. A_END): Wind, ferne Krähen, Lautsprecherwagen ---
wind = norm(band(noise(TOTAL), 80, 900)) * 0.07 * gate(-1, A_END, 0.02)
mix[:, 0] += wind
mix[:, 1] += np.roll(wind, 3000)
for t0 in (1.2, 3.1):
    for k in range(2):
        d = 0.35
        tt = np.arange(int(d * SR)) / SR
        caw = band(np.sign(np.sin(2 * np.pi * (520 - 160 * tt / d) * tt)) * np.sin(np.pi * tt / d), 300, 2500)
        add(t0 + k * 0.45, caw, 0.05, -0.6)
d = A_END + 0.5
tt = np.arange(int(d * SR)) / SR
pass_t = 4.6
eng = norm(band(noise(d), 40, 600) + 0.5 * np.sin(2 * np.pi * 38 * tt)) * np.exp(-((tt - pass_t) / 2.6) ** 2)
add(0, eng, 0.32, -0.3)
# --- Zeitkarte: Schlag ---
tt = np.arange(int(2.0 * SR)) / SR
add(A_END + 0.05, norm(np.sin(2 * np.pi * (40 + 50 * np.exp(-tt * 9)) * tt) * env(len(tt), 0.003, 0.5)), 0.7)
# --- Tag: Wind, Vögel, Auto in der Ferne ---
day = norm(band(noise(TOTAL), 90, 1400)) * 0.05 * gate(B0, TOTAL + 1, 0.3)
mix[:, 0] += day
mix[:, 1] += np.roll(day, 5000)
t = B0 + 0.3
while t < Q - 0.3:
    for _ in range(rng.integers(2, 5)):
        t += chirp(t, 0.045, rng.random() * 2 - 1) + 0.04
    t += 0.8 + rng.random() * 1.3
d = 5.0
tt = np.arange(int(d * SR)) / SR
add(B0 + 1.5, norm(band(noise(d), 60, 900)) * np.sin(np.pi * tt / d) ** 2, 0.15, 0.6)
# Schritte (ich + Sota), Mädchen leiser
for start, pan, g in ((B0 + 0.2, 0.1, 0.22), (B0 + 0.5, -0.5, 0.17), (B0 + 0.35, -0.2, 0.06)):
    t = start
    while t < EEW:
        dd = 0.09
        n = int(dd * SR)
        s = band(noise(dd), 150, 4000) * env(n, 0.002, 0.025) + np.sin(2 * np.pi * 70 * np.arange(n) / SR) * env(n, 0.002, 0.03) * 0.6
        add(t + rng.random() * 0.02, norm(s), g * (0.8 + 0.3 * rng.random()), pan)
        t += 0.61
# Besen (Tanaka, rechts vorne, wird lauter)
t = B0
while t < EEW:
    dd = 0.5
    tt = np.arange(int(dd * SR)) / SR
    add(t, norm(band(noise(dd), 1500, 8000)) * np.sin(np.pi * tt / dd) ** 2, 0.03 + 0.07 * (t - B0) / (EEW - B0), 0.6)
    t += 0.9
# Handy: Vibration + Nachricht
for k in range(2):
    tt = np.arange(int(0.25 * SR)) / SR
    add(PING + k * 0.32, np.sin(2 * np.pi * 160 * tt) * np.sin(np.pi * tt / 0.25), 0.2, 0.15)
for k, f in enumerate((1318.5, 1760.0)):
    tt = np.arange(int(0.35 * SR)) / SR
    add(PING + 0.1 + k * 0.12, np.sin(2 * np.pi * f * tt) * env(len(tt), 0.003, 0.12), 0.22, 0.15)


# --- Erdbeben-Frühwarnung: schrilles Signal aus allen Handys ---
def eew(dur):
    tt = np.arange(int(dur * SR)) / SR
    f = np.where((tt * 4).astype(int) % 2 == 0, 1046.5, 1396.9)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.35 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return tone * (((tt * 8).astype(int) % 2 == 0) * 0.6 + 0.4) * np.minimum(1, tt / 0.02)


add(EEW, eew(Q + 2.4 - EEW), 0.22, 0.1)
for dt, pan in ((0.15, -0.7), (0.27, -0.4), (0.39, -0.8), (0.5, -0.5), (0.62, 0.7)):
    x = eew(Q + 2.0 - EEW - dt)
    add(EEW + dt, band(x, 500, 4500) * np.linspace(1, 0.5, len(x)), 0.1, pan)
# --- Beben ---
qa = np.clip((t_all - Q) / 0.7, 0, 1) * (0.85 + 0.15 * np.sin(t_all * 1.7))
rumble = norm(band(noise(TOTAL), 16, 120)) * qa
mix[:, 0] += rumble * 0.75
mix[:, 1] += np.roll(rumble, 400) * 0.75
roar = norm(band(noise(TOTAL), 80, 900)) * qa * 0.25
mix[:, 0] += roar
mix[:, 1] += np.roll(roar, 900)
for _ in range(500):
    t0 = rng.uniform(Q + 0.3, TOTAL - 0.5)
    dd = 0.02 + rng.random() * 0.04
    add(t0, norm(band(noise(dd), 1500, 9000)) * env(int(dd * SR), 0.001, 0.01), 0.07 * rng.random(), rng.random() * 2 - 1)
for _ in range(12):
    dd = 0.7 + rng.random()
    tt = np.arange(int(dd * SR)) / SR
    cr = np.sin(2 * np.pi * np.cumsum(70 + 50 * np.sin(tt * 6)) / SR) * band(noise(dd), 60, 900)
    add(rng.uniform(Q + 0.5, TOTAL - 1.0), norm(cr) * np.sin(np.pi * tt / dd), 0.14, rng.random() - 0.5)
for _ in range(16):
    dd = 0.4
    tt = np.arange(int(dd * SR)) / SR
    add(rng.uniform(Q + 0.8, TOTAL - 0.5), norm(band(noise(dd), 40, 400)) * np.sin(np.pi * tt / dd) ** 2, 0.18, rng.random() * 2 - 1)
for t0 in EV.get("bike", []):
    dd = 0.6
    x = norm(band(noise(dd), 300, 6000)) * env(int(dd * SR), 0.001, 0.09)
    for k in range(5):
        tt = np.arange(int(0.25 * SR)) / SR
        add(t0 + 0.05 + k * 0.03, np.sin(2 * np.pi * (2200 + 400 * k) * tt) * env(len(tt), 0.001, 0.08), 0.05)
    add(t0, x, 0.35, -0.5)
for t0 in EV.get("pot", []):
    dd = 0.5
    x = norm(band(noise(dd), 700, 9000)) * env(int(dd * SR), 0.001, 0.08) + 0.5 * norm(band(noise(dd), 150, 1200)) * env(int(dd * SR), 0.001, 0.04)
    add(t0, x, 0.35, -0.7)
for t0 in EV.get("tile", []):
    dd = 0.4
    add(t0, norm(band(noise(dd), 400, 7000)) * env(int(dd * SR), 0.001, 0.05), 0.42, -0.6)
ca = Q + 3.0
tt = np.arange(int((TOTAL - ca) * SR)) / SR
f = 900 + 500 * np.sign(np.sin(2 * np.pi * 1.6 * tt))
add(ca, band(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 300, 3000) * np.minimum(1, tt / 0.3), 0.06, -0.8)
# Schluss
tt = np.arange(int(1.5 * SR)) / SR
add(TL["END"] - 0.05, norm(np.sin(2 * np.pi * (38 + 40 * np.exp(-tt * 8)) * tt) * env(len(tt), 0.003, 0.5)), 0.6)
mix *= gate(-1, TL["END"] + 1.4, 0.4)[:, None]

mix = np.tanh(mix * 1.4)
mix = mix / np.max(np.abs(mix)) * 0.85
out = ROOT / "public/futaba2"
out.mkdir(parents=True, exist_ok=True)
with wave.open(str(out / "sfx.wav"), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(out / "sfx.wav"), "-b:a", "160k", str(out / "sfx.mp3")], check=True)
(out / "sfx.wav").unlink()
# Megafon-Durchsage
tim = json.load(open(ROOT / "src/futaba2/timing.json"))
scr = json.load(open(ROOT / "src/futaba2/script.json"))
src = [l["file"] for s, l in zip(scr["sentences"], tim["lines"]) if s["id"] == "lsp1"][0]
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(ROOT / "public" / src), "-af",
                "highpass=f=450,lowpass=f=3200,acompressor=threshold=0.1:ratio=6,volume=2.2,aecho=0.8:0.6:220|430:0.35|0.2", str(out / "lsp_radio.wav")], check=True)
print("🔊 sfx.mp3 + lsp_radio.wav", TOTAL, "s")
