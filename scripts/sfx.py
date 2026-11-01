#!/usr/bin/env python3
"""Erzeugt alle Atmo- und Effekt-Sounds synthetisch (keine Musik, keine Lizenzprobleme).

Starten: python3 scripts/sfx.py   -> public/athan2d/sfx/*.wav
"""
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 44100
OUT = Path(__file__).resolve().parent.parent / "public" / "athan2d" / "sfx"
rng = np.random.default_rng(7)


def save(name: str, x: np.ndarray, peak: float = 0.8) -> None:
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    m = np.max(np.abs(x)) or 1
    x = x / m * peak
    OUT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(OUT / f"{name}.wav"),
                    "-b:a", "160k", str(OUT / f"{name}.mp3")], check=True)
    (OUT / f"{name}.wav").unlink()
    print("🔊", name, f"{len(x) / SR:.1f}s")


def t_(sec: float) -> np.ndarray:
    return np.arange(int(sec * SR)) / SR


def band(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """Bandpass über FFT (weiche Flanken)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    mask = 1 / (1 + (lo / np.maximum(f, 1)) ** 4) * 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * mask, len(x))


def noise(sec: float) -> np.ndarray:
    return rng.standard_normal(int(sec * SR))


def brown(sec: float) -> np.ndarray:
    b = np.cumsum(noise(sec))
    b -= np.convolve(b, np.ones(4000) / 4000, mode="same")
    return b / np.max(np.abs(b))


def env(n: int, a: float, d: float) -> np.ndarray:
    """Attack/Decay-Hüllkurve (Sekunden)."""
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4))


def slow_lfo(sec: float, rate: float, depth: float) -> np.ndarray:
    """zufällige, langsame Schwankung 1±depth"""
    pts = rng.uniform(-1, 1, int(sec * rate) + 3)
    x = np.interp(t_(sec) * rate, np.arange(len(pts)), pts)
    return 1 + depth * x


def place(buf: np.ndarray, x: np.ndarray, at: float, gain: float = 1, pan: float = 0) -> None:
    i = int(at * SR)
    j = min(len(buf), i + len(x))
    if j <= i:
        return
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:j, 0] += x[: j - i] * gain * l
    buf[i:j, 1] += x[: j - i] * gain * r


def stereo(sec: float) -> np.ndarray:
    return np.zeros((int(sec * SR), 2))


def wind(sec: float, lo=80, hi=500) -> np.ndarray:
    return band(noise(sec), lo, hi) * slow_lfo(sec, 0.25, 0.6)


# ---------------- Atmos (Loops) ----------------
def cricket_chirp() -> np.ndarray:
    f = rng.uniform(3900, 4700)
    out = np.zeros(int(0.25 * SR))
    for k in range(3):
        n = int(0.018 * SR)
        tt = np.arange(n) / SR
        p = np.sin(2 * np.pi * f * tt) * np.sin(np.pi * tt / tt[-1])
        place_mono(out, p, k * 0.035)
    return out


def place_mono(buf, x, at, gain=1):
    i = max(0, int(at * SR))
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i] * gain


def amb_night(sec=40):
    b = stereo(sec)
    w = band(noise(sec), 150, 700) * slow_lfo(sec, 0.2, 0.7)
    b[:, 0] += w * 0.25
    b[:, 1] += np.roll(w, 3000) * 0.25
    for c in range(3):
        pan = [-0.6, 0.5, 0.1][c]
        g = [0.12, 0.08, 0.05][c]
        period = rng.uniform(0.7, 1.0)
        t = rng.uniform(0, 1)
        while t < sec - 0.5:
            if rng.random() < 0.85:
                place(b, cricket_chirp(), t, g, pan)
            t += period
    save("amb_night", b, 0.45)

def amb_city(sec=40):
    """ruhiger Abend in der Stadt: leichter Wind, ein paar Grillen, ferne Schritte"""
    b = stereo(sec)
    w = band(noise(sec), 150, 900) * slow_lfo(sec, 0.25, 0.7)
    b[:, 0] += w * 0.3
    b[:, 1] += np.roll(w, 5000) * 0.3
    t = 1.0
    while t < sec - 1:
        place(b, cricket_chirp(), t, 0.04, 0.6)
        t += 1.1
    t = 3.0
    while t < sec - 3:
        for k in range(4):
            s_ = band(noise(0.1), 80, 900) * env(int(0.1 * SR), 0.004, 0.03)
            place(b, s_, t + k * 0.5, 0.06, rng.uniform(-0.8, 0.8))
        t += rng.uniform(6, 10)
    save("amb_city", b, 0.4)

def amb_desert(sec=40):
    b = stereo(sec)
    for ch in range(2):
        b[:, ch] += band(noise(sec), 300, 2500) * slow_lfo(sec, 0.35, 0.8) * 0.4
        b[:, ch] += wind(sec, 40, 200) * 0.6
    save("amb_desert", b, 0.55)


def amb_dream(sec=40):
    b = stereo(sec)
    for ch in range(2):
        b[:, ch] += band(noise(sec), 3000, 9000) * slow_lfo(sec, 0.15, 0.7) * 0.15
        b[:, ch] += band(noise(sec), 80, 300) * slow_lfo(sec, 0.1, 0.5) * 0.5
    save("amb_dream", b, 0.4)


def bird_chirp() -> np.ndarray:
    n = int(rng.uniform(0.05, 0.12) * SR)
    tt = np.arange(n) / SR
    f0, f1 = rng.uniform(2500, 4000), rng.uniform(4000, 6500)
    if rng.random() < 0.5:
        f0, f1 = f1, f0
    ph = 2 * np.pi * np.cumsum(np.linspace(f0, f1, n)) / SR
    return np.sin(ph) * np.sin(np.pi * tt / tt[-1]) ** 2


def amb_dawn(sec=40):
    b = stereo(sec)
    w = wind(sec, 60, 400)
    b[:, 0] += w * 0.4
    b[:, 1] += np.roll(w, 4000) * 0.4
    for bird in range(4):
        pan = rng.uniform(-0.8, 0.8)
        t = rng.uniform(0, 3)
        while t < sec - 1:
            for k in range(rng.integers(2, 6)):
                place(b, bird_chirp(), t + k * 0.13, rng.uniform(0.05, 0.12), pan)
            t += rng.uniform(1.5, 4)
    save("amb_dawn", b, 0.5)


# ---------------- Effekte ----------------
def bell():
    """Handglocke: lange Ausklingzeit, inharmonische Teiltöne"""
    sec = 5
    t = t_(sec)
    f0 = 740
    parts = [(1, 1, 2.8), (2.32, 0.6, 1.6), (2.76, 0.45, 1.3), (4.07, 0.3, 0.9), (5.4, 0.18, 0.6), (6.8, 0.1, 0.4)]
    x = sum(a * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t / d) for r, a, d in parts)
    x *= np.minimum(1, t / 0.004)
    n = int(0.01 * SR)
    x[:n] += band(noise(0.01), 2000, 9000) * np.linspace(1, 0, n) * 0.4
    save("bell", x)

def horn():
    sec = 2.2
    t = t_(sec)
    f = np.interp(t, [0, 0.25, 1.3, 1.5, 2.2], [180, 235, 235, 330, 320]) * (1 + 0.012 * np.sin(2 * np.pi * 5.5 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) / k ** 0.9 for k in range(1, 14))
    x = band(x, 150, 2600) * np.minimum(1, t / 0.08) * np.minimum(1, (sec - t) / 0.3)
    x += band(noise(sec), 500, 3000) * 0.05
    save("horn", x, 0.7)


def fire():
    sec = 4
    x = band(noise(sec), 100, 900) * slow_lfo(sec, 3, 0.5) * 0.5
    for _ in range(90):
        c = band(noise(0.02), 1500, 7000) * env(int(0.02 * SR), 0.0005, 0.004)
        place_mono(x, c, rng.uniform(0, sec - 0.05), rng.uniform(0.5, 2))
    save("fire", x, 0.7)


def footsteps(n=6, gap=0.42, name="footsteps"):
    sec = n * gap + 0.5
    x = np.zeros(int(sec * SR))
    for k in range(n):
        s = band(noise(0.12), 60, 900) * env(int(0.12 * SR), 0.004, 0.035)
        s += band(noise(0.12), 1500, 5000) * env(int(0.12 * SR), 0.01, 0.03) * 0.25  # Sand knirscht
        place_mono(x, s, k * gap + rng.uniform(-0.02, 0.02), rng.uniform(0.7, 1))
    save(name, x, 0.7)


def door():
    """Holztür: Riegel klickt, Tür schwingt, dumpfer Holzschlag"""
    sec = 1.6
    x = np.zeros(int(sec * SR))
    tt = t_(0.05)
    click = np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt / 0.006) + band(noise(0.05), 1500, 6000) * np.exp(-tt / 0.004)
    place_mono(x, click, 0.05, 0.6)
    swing = band(noise(0.9), 200, 1200) * np.sin(np.pi * t_(0.9) / 0.9) * 0.15
    place_mono(x, swing, 0.15)
    tt = t_(0.6)
    wood = (np.sin(2 * np.pi * 140 * tt) + 0.6 * np.sin(2 * np.pi * 310 * tt) + 0.3 * np.sin(2 * np.pi * 520 * tt)) * np.exp(-tt / 0.07)
    wood += band(noise(0.6), 100, 2000) * np.exp(-tt / 0.02) * 0.8
    place_mono(x, wood, 0.95, 1.2)
    save("door", x, 0.7)

def chains():
    sec = 1.6
    x = np.zeros(int(sec * SR))
    for _ in range(14):
        tt = t_(0.15)
        f = rng.uniform(2500, 6000)
        c = sum(np.sin(2 * np.pi * f * r * tt) for r in (1, 1.43, 2.1)) * np.exp(-tt / 0.03)
        place_mono(x, c, rng.uniform(0, 1.3), rng.uniform(0.3, 1))
    place_mono(x, band(noise(0.4), 50, 400) * env(int(0.4 * SR), 0.002, 0.08), 1.0, 2)  # fällt zu Boden
    save("chains", x, 0.7)


def coins():
    sec = 1.2
    x = np.zeros(int(sec * SR))
    for k in range(7):
        tt = t_(0.4)
        f = rng.uniform(3000, 5000)
        c = (np.sin(2 * np.pi * f * tt) + 0.6 * np.sin(2 * np.pi * f * 2.76 * tt)) * np.exp(-tt / 0.08)
        place_mono(x, c, 0.08 * k + rng.uniform(0, 0.05), rng.uniform(0.4, 1))
    save("coins", x, 0.6)


def whoosh(sec=0.7, name="whoosh"):
    t = t_(sec)
    n = noise(sec)
    # Sweep: mehrere Bänder nacheinander einblenden
    x = np.zeros_like(n)
    for k, (lo, hi) in enumerate([(200, 600), (400, 1200), (800, 2500), (1500, 4500)]):
        center = (k + 0.5) / 4
        w = np.exp(-((t / sec - center) ** 2) / 0.03)
        x += band(n, lo, hi) * w
    x *= np.sin(np.pi * t / sec)
    save(name, x, 0.6)


def thud():
    x = band(noise(0.8), 30, 220) * env(int(0.8 * SR), 0.003, 0.15)
    x += band(noise(0.8), 200, 1200) * env(int(0.8 * SR), 0.001, 0.03) * 0.4
    save("thud", x, 0.8)


def shimmer():
    sec = 3
    t = t_(sec)
    x = band(noise(sec), 3000, 10000) * np.sin(np.pi * t / sec) ** 2 * 0.6
    x += band(noise(sec), 300, 1200) * np.sin(np.pi * t / sec) ** 2 * 0.3
    for k in range(8):
        tt = t_(1.5)
        c = np.sin(2 * np.pi * rng.uniform(1200, 2600) * tt) * np.exp(-tt / 0.5) * np.minimum(1, tt / 0.05)
        place_mono(x, c, 0.2 + k * 0.25, 0.08)
    save("shimmer", x, 0.45)

def heat():
    sec = 4
    x = band(noise(sec), 2000, 8000) * slow_lfo(sec, 2, 0.6) * 0.2 + wind(sec, 30, 150)
    save("heat", x, 0.6)


def rush():
    """Schnelle Schritte + flatternder Umhang (Umar)"""
    sec = 2.2
    x = np.zeros(int(sec * SR))
    for k in range(8):
        s_ = band(noise(0.1), 60, 900) * env(int(0.1 * SR), 0.003, 0.03)
        s_ += band(noise(0.1), 1500, 5000) * env(int(0.1 * SR), 0.005, 0.02) * 0.2
        place_mono(x, s_, 0.2 + k * 0.22, 1)
    cloth = band(noise(sec), 300, 1500) * np.abs(np.sin(2 * np.pi * 3 * t_(sec))) * np.sin(np.pi * t_(sec) / sec) * 0.08
    save("rush", x + cloth, 0.7)

if __name__ == "__main__":
    amb_night()
    amb_city()
    amb_desert()
    amb_dream()
    amb_dawn()
    bell()
    horn()
    fire()
    footsteps()
    door()
    chains()
    coins()
    whoosh()
    thud()
    shimmer()
    heat()
    rush()
