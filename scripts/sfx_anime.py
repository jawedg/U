#!/usr/bin/env python3
"""Ton-Spur für die Anime-Folge (src/anime): Regen, Donner, dunkler Brumm-Ton, Schnitt-Schläge,
Handy-Vibration, Glitch, Herzschlag, Anstieg zum Ende. Alles synthetisch, eine Datei.

Starten (nach voice_gemini.py --project anime):  python3 scripts/sfx_anime.py  -> public/anime/sfx.mp3
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
rng = np.random.default_rng(11)
script = json.loads((ROOT / "src/anime/script.json").read_text())
timing = json.loads((ROOT / "src/anime/timing.json").read_text())
FPS = script.get("fps", 30)
shots, acc = [], 0
for s, l in zip(script["sentences"], timing["lines"]):
    dur = round((s["delay"] + l["seconds"] + s["pad"]) * FPS)
    shots.append({**s, "start": acc / FPS, "dur": dur / FPS, "words": l["words"]})
    acc += dur
TOTAL = acc / FPS
N = int(TOTAL * SR) + SR
mix = np.zeros((N, 2))
S = {s["shot"]: s for s in shots}
t_all = np.arange(N) / SR


def band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4), len(x))


def noise(sec):
    return rng.standard_normal(int(sec * SR))


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4))


def norm(x):
    return x / (np.max(np.abs(x)) or 1)


def add(t0, x, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    x = x[: N - i]
    mix[i:i + len(x), 0] += x * g * np.sqrt(0.5 * (1 - pan))
    mix[i:i + len(x), 1] += x * g * np.sqrt(0.5 * (1 + pan))


def word_time(sh, needle):
    ws = sh["text"].split()
    i = next(k for k, w in enumerate(ws) if needle in w)
    return sh["start"] + sh["delay"] + sh["words"][i]["start"]


def curve(points):
    """stückweise lineare Lautstärke über die ganze Länge"""
    xs, ys = zip(*points)
    return np.interp(t_all, xs, ys)


# Regen: draußen laut (1. Szene), drinnen gedämpft
rain_l = norm(band(noise(N / SR), 400, 9000))
rain_r = norm(band(noise(N / SR), 400, 9000))
drops = np.zeros(N)
for _ in range(int(TOTAL * 40)):
    p = int(rng.random() * (N - 400))
    drops[p:p + 300] += rng.standard_normal(300) * np.exp(-np.arange(300) / 40) * rng.random()
drops = band(drops, 1500, 9000)
inside = S["face"]["start"]
rv = curve([(0, 0.0), (0.5, 0.5), (inside - 0.2, 0.5), (inside + 0.3, 0.16), (TOTAL - 3, 0.16), (TOTAL, 0.05)])
low = norm(band(noise(N / SR), 80, 700))
mix[:, 0] += (rain_l * 0.25 + norm(drops) * 0.3) * rv * np.where(t_all < inside, 1, 0.45) + low * rv * 0.25
mix[:, 1] += (rain_r * 0.25 + np.roll(norm(drops), 777) * 0.3) * rv * np.where(t_all < inside, 1, 0.45) + low * rv * 0.25

# Donner zum Blitz
th = band(noise(4.0), 25, 400) * env(int(4.0 * SR), 0.05, 1.1)
th += band(noise(4.0), 300, 3000) * env(int(4.0 * SR), 0.005, 0.15) * 0.5
add(0.28, norm(th), 0.9)

# Dunkler Brumm-Ton, wird mit der Spannung lauter
f0 = 41.2
drone = (np.sin(2 * np.pi * f0 * t_all) + 0.6 * np.sin(2 * np.pi * f0 * 1.5 * t_all + 1) + 0.4 * np.sin(2 * np.pi * (f0 * 2 + 0.7) * t_all)) / 2
drone += norm(band(noise(N / SR), 40, 200)) * 0.5
p1, sd, f2, en = S["phone1"]["start"], S["side"]["start"], S["face2"]["start"], S["end"]["start"]
dv = curve([(0, 0), (2, 0.2), (p1, 0.25), (p1 + 1, 0.45), (sd, 0.6), (f2 + 2, 0.9), (en, 0.2), (TOTAL, 0)])
mix[:, 0] += drone * dv * 0.3
mix[:, 1] += drone * dv * 0.3


def hit(big=False):
    d = 2.5 if big else 1.4
    n = int(d * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (38 + 60 * np.exp(-t * 12)) * t) * env(n, 0.002, 0.5 if big else 0.3)
    crack = band(rng.standard_normal(n), 800, 8000) * env(n, 0.001, 0.03)
    return norm(boom + crack * (0.5 if big else 0.25))


def whoosh(d=0.6):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = band(rng.standard_normal(n), 300, 4000) * np.sin(np.pi * t / d) ** 2
    return norm(x)


for name, big in (("face", False), ("sit", False), ("side", True), ("face2", True)):
    t0 = S[name]["start"]
    add(t0 - 0.45, whoosh(0.5), 0.35)
    add(t0, hit(big), 0.75 if big else 0.5)


def glitch(d=0.35):
    n = int(d * SR)
    x = np.zeros(n)
    k = 0
    while k < n:
        L = int(SR * (0.01 + rng.random() * 0.04))
        f = 200 + rng.random() * 3000
        seg = np.sign(np.sin(2 * np.pi * f * np.arange(L) / SR)) * 0.5 + rng.standard_normal(L) * 0.5 * (rng.random() > 0.5)
        x[k:k + L] += seg[: n - k]
        k += L + int(SR * rng.random() * 0.02)
    return norm(band(x, 150, 9000))


add(sd, glitch(0.4), 0.45)
add(f2, glitch(0.3), 0.4)
add(en, glitch(0.3), 0.4)


def buzz(d=0.55):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * 172 * t)) * (np.sin(2 * np.pi * 172 * t) ** 2) + 0.4 * np.sin(2 * np.pi * 344 * t)
    gate = ((t % 0.28) < 0.2).astype(float)
    return norm(band(x, 100, 2500)) * gate * env(n, 0.005, 0.6)


add(word_time(S["phone1"], "Nachricht") - 0.13, buzz(), 0.5)
add(word_time(S["phone2"], "Foto") - 0.13, buzz(0.35), 0.45)

# Kamera-Auslöser beim Foto
cl = band(noise(0.08), 1500, 9000) * env(int(0.08 * SR), 0.0005, 0.01)
add(sd + 0.05, norm(cl), 0.5)
add(sd + 0.13, norm(cl), 0.35)


def thump(f=56, d=0.14):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * t * (1 - t * 2)) * env(len(t), 0.004, 0.04)


t = f2 + 0.2
bpm = 80
while t < en - 0.1:
    add(t, thump(), 0.7)
    add(t + 0.14, thump(48), 0.5)
    bpm = min(135, bpm + 7)
    t += 60 / bpm

# Anstieg in den Schluss + Schlag
n = int(1.6 * SR)
tt = np.arange(n) / SR
riser = band(rng.standard_normal(n), 500, 7000) * (tt / 1.6) ** 2
riser += np.sin(2 * np.pi * np.cumsum(200 + 900 * (tt / 1.6) ** 2) / SR) * (tt / 1.6) ** 2 * 0.3
add(en - 1.6, norm(riser), 0.35)
add(en, hit(True), 0.9)

mix = np.tanh(mix * 1.2) * 0.9
mix /= np.max(np.abs(mix))
mix *= 0.85
out = ROOT / "public/anime"
with wave.open(str(out / "sfx.wav"), "wb") as wv:
    wv.setnchannels(2)
    wv.setsampwidth(2)
    wv.setframerate(SR)
    wv.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(out / "sfx.wav"), "-b:a", "160k", str(out / "sfx.mp3")], check=True)
(out / "sfx.wav").unlink()
print(f"🔊 sfx.mp3 {TOTAL:.1f}s")
