#!/usr/bin/env python3
"""Ton-Spur (Atmo + Effekte, keine Musik) für „Der erste Adhan“ (QISSA, POV) passend zum Zeitplan.

Nutzt die synthetischen Klänge aus scripts/sfx.py und mischt sie an den Zeitpunkten aus
src/qissa_adhan/timeline.json zu EINER Datei: public/qissa_adhan/sfx.wav
(Stimmen und Adhan legt Remotion separat darüber.)
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sfx as S  # noqa: E402

SR = S.SR
CAP = {}
S.save = lambda name, x, peak=0.8: CAP.__setitem__(name, (x / (np.max(np.abs(x)) or 1)) * peak)
rng = np.random.default_rng(11)


def get(fn, name, *a, **k):
    fn(*a, **k)
    x = CAP[name]
    return x if x.ndim == 2 else np.stack([x, x], axis=1)


TL = json.loads((ROOT / "src" / "qissa_adhan" / "timeline.json").read_text(encoding="utf-8"))
SEG = {s["id"]: s for s in TL["segments"]}
EV = TL["events"]
LINES = {l["id"]: l for l in TL["lines"]}
QUOTES = {q["id"]: q for q in TL["quotes"]}
TOTAL = TL["total"] + 0.5
buf = np.zeros((int(TOTAL * SR), 2))


def add(t0, x, g=1.0, pan=0.0, fade_in=0.0, fade_out=0.0, dur=None):
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    if dur is not None:
        n = int(dur * SR)
        if len(x) < n:  # Schleife
            reps = n // len(x) + 1
            x = np.concatenate([x] * reps)[:n]
        x = x[:n]
    x = x.copy()
    if fade_in:
        k = min(len(x), int(fade_in * SR))
        x[:k] *= np.linspace(0, 1, k)[:, None]
    if fade_out:
        k = min(len(x), int(fade_out * SR))
        x[-k:] *= np.linspace(1, 0, k)[:, None]
    x[:, 0] *= g * (1 - max(0, pan))
    x[:, 1] *= g * (1 + min(0, pan))
    i = int(max(0, t0) * SR)
    j = min(len(buf), i + len(x))
    if j > i:
        buf[i:j] += x[: j - i]


def seg(i):
    return SEG[i]["start"], SEG[i]["start"] + SEG[i]["dur"]


def steps(t0, t1, gap=0.5, g=0.35, run=False):
    t = t0
    k = 0
    while t < t1:
        n = int(0.12 * SR)
        s_ = S.band(S.noise(0.12), 60, 900 if not run else 1200) * S.env(n, 0.003, 0.035 if not run else 0.025)
        s_ += S.band(S.noise(0.12), 1800, 6000) * S.env(n, 0.004, 0.02) * 0.35  # Sand knirscht
        add(t, s_, g * rng.uniform(0.8, 1.1), pan=0.15 if k % 2 else -0.15)
        t += gap * rng.uniform(0.93, 1.07)
        k += 1


def murmur(sec):
    """leises Stimmengewirr ohne Worte"""
    x = np.zeros(int(sec * SR))
    for _ in range(int(sec * 2.5)):
        d = rng.uniform(0.3, 1.0)
        n = int(d * SR)
        f = rng.uniform(110, 220)
        tt = np.arange(n) / SR
        v = np.sin(2 * np.pi * f * tt + 2 * np.sin(2 * np.pi * 5 * tt)) * np.sin(np.pi * tt / d) ** 2
        v = S.band(v + 0.3 * S.band(S.noise(d), 300, 1500), 120, 1600)
        S.place_mono(x, v, rng.uniform(0, sec - d), rng.uniform(0.2, 0.6))
    return S.band(x, 100, 1400)


def shimmer(sec, g=1.0):
    x = S.band(S.noise(sec), 4000, 11000) * S.slow_lfo(sec, 0.3, 0.6) * 0.25
    tt = np.arange(int(sec * SR)) / SR
    x += sum(np.sin(2 * np.pi * f * tt) * 0.02 * (0.5 + 0.5 * np.sin(2 * np.pi * r * tt))
             for f, r in ((1318, 0.11), (1975, 0.07), (2637, 0.13)))
    return x * g


def whoosh(sec=0.8, g=1.0):
    n = int(sec * SR)
    tt = np.linspace(0, 1, n)
    x = S.noise(sec)
    lo = S.band(x, 200, 1200) * np.sin(np.pi * tt) ** 2
    hi = S.band(x, 2000, 6000) * np.sin(np.pi * tt) ** 3 * 0.4
    return (lo + hi) * g


def boom(sec=2.5):
    tt = np.arange(int(sec * SR)) / SR
    return (np.sin(2 * np.pi * 48 * tt) * np.exp(-tt / 0.8) + S.band(S.noise(sec), 30, 200) * np.exp(-tt / 0.3) * 0.5)


def ping():
    tt = np.arange(int(0.6 * SR)) / SR
    return (np.sin(2 * np.pi * 1320 * tt) + 0.4 * np.sin(2 * np.pi * 1980 * tt)) * np.exp(-tt / 0.15) * 0.5


def door_bang():
    tt = np.arange(int(1.2 * SR)) / SR
    knock = S.band(S.noise(1.2), 60, 700) * np.exp(-tt / 0.08)
    creak_f = 300 + 180 * np.sin(2 * np.pi * 2.5 * tt)
    creak = np.sin(2 * np.pi * np.cumsum(creak_f) / SR) * np.exp(-tt / 0.25) * 0.25
    wood = S.band(S.noise(1.2), 900, 3500) * np.exp(-tt / 0.05) * 0.4
    return knock + creak + wood


def cloth(sec):
    tt = np.arange(int(sec * SR)) / SR
    return S.band(S.noise(sec), 250, 1800) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 3.2 * tt))) * 0.5


def main():
    night = get(S.amb_night, "amb_night", 60)
    dawn = get(S.amb_dawn, "amb_dawn", 60)
    dream = get(S.amb_dream, "amb_dream", 40)
    bell = get(S.bell, "bell")
    horn = get(S.horn, "horn")
    fire = get(S.fire, "fire")

    # --- Nacht: Gasse, Moschee, Beratung
    a, b = seg("gasse")
    add(a, night, 0.9, dur=b - a + 0.3, fade_in=0.4)
    add(a, whoosh(0.9, 0.5), 1.0)
    steps(a + 0.25, b - 1.0, gap=0.46, g=0.35)
    a, b = seg("moschee")
    add(a, night, 0.8, dur=b - a + 0.3)
    add(a + 2.0, murmur(b - a - 2.0), 0.18, fade_in=1.0, fade_out=1.0)
    steps(a, a + 4.0, gap=0.46, g=0.3)
    a, b = seg("beratung")
    add(a, night, 0.45, dur=b - a + 0.3)
    add(a, shimmer(b - a), 0.6, fade_in=1.0, fade_out=1.0)
    add(EV["glocke_d4"] - 0.05, bell, 0.45)
    add(EV["horn_d4"] - 0.05, horn, 0.3)
    add(EV["feuer_d4"] - 0.1, fire[: int(2.2 * SR)], 0.6, fade_out=0.6)
    # --- Tafel „In dieser Nacht“
    a, b = seg("nacht")
    add(a - 0.2, whoosh(1.0, 0.6), 1.0)
    add(a, night, 0.45, dur=b - a + 0.6, fade_out=1.2)
    # --- Traum (Traum-Atmo blendet schon auf der Tafel ein und klingt auf der nächsten aus → nie Stille)
    a, b = seg("traum")
    a0 = SEG["nacht"]["start"] + 0.3
    add(a0, dream, 0.9, dur=b - a0 + 1.0, fade_in=1.2, fade_out=1.6)
    add(a, shimmer(b - a), 0.7, fade_in=1.5, fade_out=1.0)
    add(LINES["d7"]["start"] + 1.0, bell, 0.25)
    add(QUOTES["q1"]["start"] + 0.2, bell, 0.18)
    add(LINES["d8"]["start"], shimmer(4.5, 2.0), 1.0, fade_in=0.8, fade_out=1.5)
    # --- Tafel „Am Morgen“ + Morgen + Adhan-Szenen + Umar
    a, b = seg("morgen_karte")
    add(a - 0.2, whoosh(1.0, 0.6), 1.0)
    a = SEG["morgen"]["start"]
    b = SEG["umar"]["start"] + SEG["umar"]["dur"]
    a0 = SEG["morgen_karte"]["start"] + 0.3
    add(a0, dawn, 0.85, dur=b - a0, fade_in=1.2)
    add(a, shimmer(SEG["morgen"]["dur"]), 0.45, fade_in=1.0, fade_out=1.0)
    steps(a + 0.2, a + 4.8, gap=0.5, g=0.22)
    add(SEG["dach_a"]["start"] + 0.5, murmur(EV["athan"] - SEG["dach_a"]["start"]), 0.12, fade_out=0.8)
    td = EV["door_umar"]
    add(td, door_bang(), 0.8)
    steps(td + 0.1, td + 4.0, gap=0.24, g=0.4, run=True)
    add(td + 0.1, cloth(3.5), 0.35, fade_out=1.0)
    a2, b2 = seg("umar")
    steps(td + 2.1, b2 - 0.3, gap=0.47, g=0.25)
    # --- Ende: Morgen, Vögel, Auswahltafel, Logo
    a, b = seg("ende")
    add(a, dawn, 0.95, dur=b - a + 2.6, fade_out=2.0)
    ch = TL["choice"]
    add(ch["start"], ping(), 0.6)
    add(ch["start"] + 0.5, ping(), 0.45)
    a, b = seg("logo")
    add(a, boom(), 0.6)
    add(a - 0.3, whoosh(0.8, 0.4), 1.0)

    m = np.max(np.abs(buf)) or 1
    out = (buf / m * 0.9 * 32767).astype(np.int16)
    p = ROOT / "public" / "qissa_adhan" / "sfx.wav"
    with wave.open(str(p), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(out.tobytes())
    print("🔊", p.relative_to(ROOT), f"{len(buf) / SR:.1f}s")


if __name__ == "__main__":
    main()
