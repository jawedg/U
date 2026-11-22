#!/usr/bin/env python3
"""Fertige Tonspur für QISSAH Folge 3 „Die Erbauer der Kaaba“: Stimmen + Atmo + Effekte (keine Musik).

Wie scripts/sfx_qissa_adhan.py (Folge 1): echte Aufnahmen aus assets/sfx/*.flac (Nachweise assets/sfx/CREDITS.md), sonst
synthetische Klänge (Wasser-Sprudeln, Atmen, Sand-Schieben, Kamel-Schritte …). Atmo wird unter der Stimme leiser (Ducking),
Lautheit -14 LUFS, True Peak -1,5 dB, Begrenzer. Ausgabe: public/qissa_kaaba/master.wav
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sfx as S  # noqa: E402

SR = S.SR = 48000
REAL = ROOT / "assets" / "sfx"
TL = json.loads((ROOT / "src" / "qissa_kaaba" / "timeline.json").read_text(encoding="utf-8"))
SEG = {s["id"]: s for s in TL["segments"]}
EV = TL["events"]
LINES = {l["id"]: l for l in TL["lines"]}
QUOTES = {q["id"]: q for q in TL["quotes"]}
TOTAL = TL["total"] + 0.5
buf = np.zeros((int(TOTAL * SR), 2))   # Atmo (wird unter der Stimme leiser)
fxb = np.zeros((int(TOTAL * SR), 2))   # Effekte
bedb = np.zeros((int(TOTAL * SR), 2))  # Hintergrund-Stimmen (Talbiya): leise, unter der Erzählung stark abgesenkt
rng = np.random.default_rng(21)


def load(path, t0=0.0, dur=None):
    cmd = ["ffmpeg", "-loglevel", "error", "-ss", f"{t0:.3f}"] + (["-t", f"{dur:.3f}"] if dur else []) + [
        "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def real(key, t0=0.0, dur=None, peak=0.8):
    p = REAL / f"{key}.flac"
    if not p.exists():
        return None
    x = load(p, t0, dur)
    return x / (np.max(np.abs(x)) or 1) * peak


def st(x):
    return x if x.ndim == 2 else np.stack([x, x], axis=1)


def add(t0, x, g=1.0, pan=0.0, fade_in=0.0, fade_out=0.0, dur=None, fx=False, bed=False):
    if x is None:
        return
    x = st(x)
    if dur is not None:
        n = int(dur * SR)
        if len(x) < n:  # Schleife mit weicher Überblendung
            xf = min(int(0.8 * SR), len(x) // 4)
            r = np.linspace(0, 1, xf)[:, None]
            y = x.copy()
            while len(y) < n:
                y = np.concatenate([y[:-xf], y[-xf:] * (1 - r) + x[:xf] * r, x[xf:]])
            x = y
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
        (bedb if bed else fxb if fx else buf)[i:j] += x[: j - i]


def seg(i):
    return SEG[i]["start"], SEG[i]["start"] + SEG[i]["dur"]


def speed(x, f):
    x = st(x)
    n = int(len(x) / f)
    src = np.linspace(0, len(x) - 1, n)
    return np.stack([np.interp(src, np.arange(len(x)), x[:, c]) for c in range(2)], axis=1)


def far(x, lo=250, hi=3500):
    x = st(x)
    return np.stack([S.band(x[:, c], lo, hi) for c in range(2)], axis=1)


def reverb(x, sec=1.6, wet=0.35):
    """großer Raum (Mas'a-Halle): Faltung mit abklingendem Rauschen"""
    x = st(x)
    n = int(sec * SR)
    tt = np.arange(n) / SR
    out = []
    for c in range(2):
        ir = rng.standard_normal(n) * np.exp(-tt / (sec / 6.9))
        ir /= np.sqrt(np.sum(ir ** 2))
        L = len(x) + n
        y = np.fft.irfft(np.fft.rfft(x[:, c], L) * np.fft.rfft(ir, L), L)[: len(x)]
        out.append(x[:, c] * (1 - wet) + y * wet * 2.0)
    return np.stack(out, axis=1)


# ---------------------------------------------------------------- synthetische Klänge
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
    return (S.band(x, 200, 1200) * np.sin(np.pi * tt) ** 2 + S.band(x, 2000, 6000) * np.sin(np.pi * tt) ** 3 * 0.4) * g


def boom(sec=2.5):
    tt = np.arange(int(sec * SR)) / SR
    return np.sin(2 * np.pi * 48 * tt) * np.exp(-tt / 0.8) + S.band(S.noise(sec), 30, 200) * np.exp(-tt / 0.3) * 0.5


def riser(sec=2.2):
    n = int(sec * SR)
    tt = np.linspace(0, 1, n)
    x = S.band(S.noise(sec), 300, 5000) * tt ** 2.2 + S.band(S.noise(sec), 60, 250) * tt ** 1.5 * 0.6
    return x * (1 - np.clip((tt - 0.96) / 0.04, 0, 1))


def el(key, t0=0.0, dur=None, peak=0.8):
    """von ElevenLabs erzeugte Geräusche (assets/sfx/el_*.flac, auf gleiche Lautheit gebracht)"""
    return real(f"el_{key}", t0, dur, peak)


def water(sec, g=1.0):
    """Sprudeln: echte (ElevenLabs) Aufnahme als Schleife, sonst synthetisch"""
    x = el("spring_bubble")
    if x is None:
        return bubbles(sec, g=g)
    n = int(sec * SR)
    y = x.copy()
    xf = int(0.8 * SR)
    r = np.linspace(0, 1, xf)[:, None]
    while len(y) < n:
        y = np.concatenate([y[:-xf], y[-xf:] * (1 - r) + x[:xf] * r, x[xf:]])
    return y[:n] * g


def bubbles(sec, rate=9.0, lo=380, hi=1100, g=1.0):
    """Sprudeln: viele kleine „Blubb“ (Sinus mit steigender Tonhöhe, schnell abklingend) + leises Rieseln"""
    n = int(sec * SR)
    x = np.zeros(n)
    k = int(sec * rate)
    for _ in range(k):
        d = rng.uniform(0.03, 0.09)
        m = int(d * SR)
        tt = np.arange(m) / SR
        f0 = rng.uniform(lo, hi)
        ph = 2 * np.pi * np.cumsum(f0 * (1 + 1.8 * tt / d)) / SR
        b = np.sin(ph) * np.exp(-tt / (d * 0.35)) * (1 - np.exp(-tt / 0.002))
        i = rng.integers(0, max(1, n - m))
        x[i:i + m] += b * rng.uniform(0.2, 1.0)
    x += S.band(S.noise(sec), 1500, 7000) * 0.12 * (0.7 + 0.3 * S.slow_lfo(sec, 0.4, 1.0))
    x += S.band(S.noise(sec), 120, 500) * 0.15
    return x * g


def gush(sec=2.5):
    """Wasser bricht hervor: Rauschen schwillt an, Spritzen, dann Plätschern"""
    tt = np.arange(int(sec * SR)) / SR
    env_ = np.clip(tt / 0.08, 0, 1) * (0.35 + 0.65 * np.exp(-tt / 0.7))
    x = (S.band(S.noise(sec), 200, 2500) * 0.9 + S.band(S.noise(sec), 2500, 9000) * 0.5) * env_
    return x + bubbles(sec, rate=30, g=0.6)


def breath(sec, run=True):
    x = el("breath_run" if run else "breath_tired")
    return x if x is not None else breathing(sec, 2.5 if run else 0.9)


def breathing(sec, rate=2.1, g=1.0, voice=True):
    """hastiges Atmen (Laufen) bzw. langsam erschöpft: ein-/ausatmen als gefiltertes Rauschen mit Hüllkurven"""
    n = int(sec * SR)
    x = np.zeros(n)
    per = 1.0 / rate
    t = 0.0
    while t < sec - per:
        for k, (lo, hi, amp, frac) in enumerate(((700, 3200, 0.55, 0.42), (400, 2400, 0.85, 0.5))):  # ein, aus
            d = per * frac
            m = int(d * SR)
            tt = np.linspace(0, 1, m)
            e = np.sin(np.pi * tt) ** (1.5 if k == 0 else 1.0) * (1 - 0.4 * tt if k else 1)
            b = S.band(S.noise(d), lo, hi) * e * amp
            if voice and k == 1:
                ph = 2 * np.pi * np.cumsum(np.full(m, rng.uniform(170, 210))) / SR
                b += np.sin(ph) * e * 0.04
            i = int((t + (0 if k == 0 else per * 0.45)) * SR)
            x[i:i + m] += b[: max(0, n - i)]
        t += per * rng.uniform(0.92, 1.08)
    return x * g


def sand_scrape(sec=0.35):
    tt = np.linspace(0, 1, int(sec * SR))
    return S.band(S.noise(sec), 300, 4000) * np.sin(np.pi * tt) ** 1.5 * (0.8 + 0.2 * np.sin(tt * 40))


def thud(sec=0.25, f=70):
    tt = np.arange(int(sec * SR)) / SR
    return np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.05) + S.band(S.noise(sec), 60, 400) * np.exp(-tt / 0.03) * 0.5


def camel_steps(t0, t1, gap=0.62, g=0.25):
    t = t0
    k = 0
    while t < t1:
        add(t, thud(0.3, rng.uniform(55, 80)), g * rng.uniform(0.7, 1.0), pan=0.2 if k % 2 else -0.2, fx=True)
        add(t + 0.02, S.band(S.noise(0.15), 1500, 5000) * np.exp(-np.arange(int(0.15 * SR)) / SR / 0.04) * 0.3, g, fx=True)
        t += gap * rng.uniform(0.95, 1.05)
        k += 1


def tinkle(t0, t1, every=1.24, g=0.12):
    """kleine Kamelglocke im Gehrhythmus"""
    t = t0
    while t < t1:
        tt = np.arange(int(0.7 * SR)) / SR
        f = rng.uniform(1650, 1800)
        x = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 2.76 * tt)) * np.exp(-tt / 0.18)
        add(t, x * 0.4, g, pan=0.3, fx=True)
        t += every * rng.uniform(0.9, 1.1)


def steps(t0, t1, gap=0.5, g=0.35, run=False):
    t = t0
    k = 0
    while t < t1:
        n = int(0.12 * SR)
        s_ = S.band(S.noise(0.12), 60, 900 if not run else 1200) * S.env(n, 0.003, 0.035 if not run else 0.025)
        s_ += S.band(S.noise(0.12), 1800, 6000) * S.env(n, 0.004, 0.02) * 0.4  # Kies knirscht
        add(t, s_, g * rng.uniform(0.8, 1.1), pan=0.15 if k % 2 else -0.15, fx=True)
        t += gap * rng.uniform(0.93, 1.07)
        k += 1


def walk_steps(t0, t1, g=0.3, run=False):
    if run and el("steps_run") is not None:
        add(t0, el("steps_run"), g * 1.1, fade_in=0.08, fade_out=0.25, dur=t1 - t0, fx=True)
        return
    x = real("steps_sand")
    if x is None or t1 - t0 < 0.4:
        steps(t0, t1, gap=0.27 if run else 0.5, g=g * 0.9, run=run)
        return
    if run:
        x = speed(x, 1.65)
    add(t0, x, g * (1.2 if run else 1.0), fade_in=0.12, fade_out=0.25, dur=t1 - t0, fx=True)


def desert(t0, t1, g=1.0, fade_in=0.0, fade_out=0.0, hot=False):
    """Wüstenwind; mittags heller/heißer (Hitze-Flimmern als feines Rauschen)"""
    add(t0, real("wind", 1.0), 0.55 * g, dur=t1 - t0, fade_in=fade_in, fade_out=fade_out)
    add(t0, S.band(S.noise(t1 - t0 + 0.1), 90, 600) * S.slow_lfo(t1 - t0 + 0.1, 0.12, 0.5) * 0.25, g, fade_in=fade_in, fade_out=fade_out)
    if hot:
        add(t0, S.band(S.noise(t1 - t0 + 0.1), 5000, 12000) * 0.05, g, fade_in=fade_in, fade_out=fade_out)
        add(t0, el("wind_hot"), 0.5 * g, dur=t1 - t0, fade_in=fade_in, fade_out=fade_out)


def baby(t, dur, g=0.25):
    """weinendes Baby (echte Aufnahme, falls vorhanden), sonst leises synthetisches Wimmern"""
    x = el("baby_cry") if el("baby_cry") is not None else real("baby_cry")
    if x is None:
        tt = np.arange(int(dur * SR)) / SR
        f = 420 + 60 * np.sin(2 * np.pi * 0.9 * tt) + 40 * np.sin(2 * np.pi * 5.5 * tt)
        ph = 2 * np.pi * np.cumsum(f) / SR
        e = np.clip(np.sin(2 * np.pi * 0.42 * tt), 0, 1) ** 1.5
        x = sum(np.sin(k * ph) / k ** 1.4 for k in range(1, 7)) * e
        x = S.band(x, 300, 3500) * 0.5
        g *= 0.6
    add(t, far(x, 300, 5000), g, dur=dur, fade_in=0.2, fade_out=0.5, fx=True)


def R(key, t0=0.0, dur=None, peak=0.8, alt=None):
    x = real(key, t0, dur, peak)
    return x if x is not None else (alt() if alt else None)


def main():
    W = lambda: R("whoosh_slow", alt=lambda: whoosh(0.9, 0.6))       # noqa: E731
    Wr = lambda: R("whoosh_rev", alt=lambda: whoosh(0.7, 0.5))       # noqa: E731
    B = lambda: R("boom_big", alt=boom)                              # noqa: E731
    Bs = lambda: R("impact", alt=boom)                               # noqa: E731
    sparkle = real("sparkle")
    shim = real("shimmer")
    tawaf = el("tawaf")
    # echte Aufnahme vom Nutzer: Pilgermenge ruft die Talbiya (14,5 s, keine Musik) – einmal ganz bei „HEUTE“, Anfang im Einstieg
    talb = real("talbiya_user")
    hall = el("hall_crowd")
    camp = el("camp")
    goats = el("goats")
    kids = el("children")
    eve = el("camp_evening")
    cook = el("cooking")
    fire = real("fire")
    crick = real("crickets")
    wind = lambda t0, t1, g=1.0, fi=0.3, fo=0.3: desert(t0, t1, g, fade_in=fi, fade_out=fo)  # noqa: E731

    def card(i):
        a, b = seg(i)
        add(a - 0.45, W(), 0.8, fx=True)
        add(a + 0.02, B(), 0.55, fx=True)

    def cut(i, g=0.7):
        a, b = seg(i)
        add(a - 0.4, Wr(), g, fx=True)
        add(a + 0.02, Bs(), g * 0.6, fx=True)

    def inside(a, b, g=1.0):
        """im Haus: Wind + Lager gedämpft (Tiefpass)"""
        add(a, far(real("wind", 2.0), 80, 900), 0.5 * g, dur=b - a, fade_in=0.2, fade_out=0.3)
        add(a, far(camp, 100, 1400) if camp is not None else None, 0.35 * g, dur=b - a, fade_in=0.3, fade_out=0.3)
        add(a + 1.0, far(goats, 200, 2500) if goats is not None else None, 0.25 * g, dur=min(9.0, b - a - 1.0), fade_in=0.5, fade_out=0.8, pan=0.3)

    # --- Einstieg: Kaaba heute (Menge) – Engel (Folge 2) – Bau
    a, b = seg("hook_a")
    add(a, tawaf, 1.0, dur=b - a + 0.3, fade_in=0.2, fade_out=0.3)
    add(a, hall, 0.35, dur=b - a + 0.3, fade_in=0.2, fade_out=0.3)
    if talb is not None:  # erste zwei Zeilen (0–7,25 s, endet an einer natürlichen Atempause), sanft ein- und ausgeblendet
        add(a, talb[: int(7.25 * SR)], 1.0, fade_in=0.6, fade_out=1.2, bed=True)
    a, b = seg("hook_b")
    add(a - 0.45, Wr(), 0.8, fx=True)
    add(a, B(), 0.5, fx=True)
    add(a, shimmer(b - a + 0.3), 1.0, fade_in=0.2, fade_out=0.3)
    add(a + 0.2, shim, 0.6, fx=True)
    add(a + 0.3, sparkle, 0.4, fx=True)
    add(a, water(b - a + 0.3), 0.5, fade_in=0.2, fade_out=0.3)
    a, b = seg("hook_c")
    add(a - 0.45, W(), 0.8, fx=True)
    add(a, Bs(), 0.5, fx=True)
    wind(a, b + 0.3, 0.9, fi=0.1)
    add(a, el("stone_place"), 0.9, dur=b - a, fade_out=0.3, fx=True)

    # --- Zelte (Morgen): Lager, Ziegen, Kinder, Schritte, am Ende der Brunnen
    a, b = seg("zelte")
    cut("zelte", 0.8)
    wind(a, b + 0.2, 0.8)
    add(a, camp, 0.9, dur=b - a + 0.2, fade_in=0.6, fade_out=0.2)
    add(a + 1.0, goats, 0.6, dur=b - a - 1.0, fade_in=0.6, fade_out=0.4, pan=-0.3)
    add(a + 3.5, kids, 0.35, dur=min(7.0, b - a - 3.5), fade_in=0.5, fade_out=0.6, pan=0.3)
    walk_steps(a + 0.1, b - 0.2, 0.25)
    add(EV["zamzam_e2"] - 1.5, el("well"), 0.8, fade_in=0.2, fade_out=0.6, fx=True)
    add(EV["zamzam_e2"] - 0.2, shim, 0.35, fx=True)
    # --- Ismail am Feuer (goldene Stunde)
    a, b = seg("ismail")
    wind(a, b, 0.6)
    add(a, fire, 0.7, dur=b - a, fade_in=0.3, fade_out=0.3)
    add(a, eve if eve is not None else camp, 0.6, dur=b - a, fade_in=0.4, fade_out=0.4)
    add(a + 0.5, shimmer(b - a - 0.5), 0.4, fade_in=1.0, fade_out=1.0)
    add(EV["ismail_e3"] - 0.2, sparkle, 0.3, fx=True)
    walk_steps(LINES["e4"]["start"] + 3.6, b, 0.15)
    # --- Grab (Dämmerung)
    a, b = seg("grab")
    add(a, crick, 0.4, dur=b - a + 0.4, fade_in=0.3, fade_out=0.6)
    wind(a, b + 0.3, 0.5)
    add(a, shimmer(b - a), 0.45, fade_in=0.5, fade_out=0.8)

    # --- Der erste Besuch
    card("k1")
    a, b = seg("ankunft")
    inside(a, SEG["tuer1"]["start"] + SEG["tuer1"]["dur"])
    add(EV["ibrahim_e6"] - 1.6, R("riser", alt=lambda: riser(1.6)), 0.25, fx=True, fade_out=0.2)
    add(EV["ibrahim_e6"] - 0.1, shim, 0.5, fx=True)
    add(a + 4.0, shimmer(SEG["tuer1"]["start"] + SEG["tuer1"]["dur"] - a - 4.0), 0.5, fade_in=1.5, fade_out=1.0)
    a, b = seg("tuer1")
    add(EV["schwelle_q1"] - 0.05, Bs(), 0.35, fx=True)
    add(EV["schwelle_q1"], thud(0.35, 55), 0.4, fx=True)
    a, b = seg("abend1")
    add(a - 0.3, Wr(), 0.6, fx=True)
    add(a, crick, 0.5, dur=b - a, fade_in=0.4, fade_out=0.3)
    add(a, eve, 0.45, dur=b - a, fade_in=0.4, fade_out=0.3)
    add(a, real("fire2"), 0.18, dur=b - a, fade_in=0.4, fade_out=0.3)
    walk_steps(EV["ismail_e8"] - 0.4, EV["ismail_e8"] + 2.0, 0.22)
    add(EV["jemand_e8"] - 0.2, R("riser", alt=lambda: riser(1.2)), 0.15, fx=True)
    add(EV["trennen_q2"] - 0.05, Bs(), 0.3, fx=True)
    walk_steps(EV["trennen_q2"] + 1.6, b, 0.3)
    add(EV["familie_q2"] + 0.5, thud(0.3, 65), 0.35, fx=True)

    # --- Der zweite Besuch
    card("k2")
    a, b = seg("besuch2")
    wind(a, SEG["segen"]["start"] + SEG["segen"]["dur"], 0.6)
    add(a, cook, 0.9, dur=SEG["segen"]["start"] + SEG["segen"]["dur"] - a, fade_in=0.4, fade_out=0.4)
    add(a, camp, 0.5, dur=SEG["segen"]["start"] + SEG["segen"]["dur"] - a, fade_in=0.4, fade_out=0.4)
    add(a + 1.5, goats, 0.55, dur=9.0, fade_in=0.5, fade_out=0.6, pan=0.4)
    add(a + 4.0, kids, 0.25, dur=6.0, fade_in=0.5, fade_out=0.6, pan=-0.4)
    add(EV["ibrahim_e9"] - 1.6, R("riser", alt=lambda: riser(1.6)), 0.25, fx=True, fade_out=0.2)
    add(EV["ibrahim_e9"] - 0.1, shim, 0.5, fx=True)
    a, b = seg("tuer2")
    add(EV["fleisch_f4"] - 0.3, thud(0.2, 120), 0.15, fx=True)
    add(EV["segne_q5"] - 0.1, shim, 0.7, fx=True)
    add(EV["segne_q5"], sparkle, 0.5, fx=True)
    add(EV["segne_q5"], shimmer(b - EV["segne_q5"] + SEG["segen"]["dur"]), 0.8, fade_in=0.6, fade_out=1.5)
    a, b = seg("segen")
    add(a + 0.3, sparkle, 0.3, fx=True)
    add(EV["schwelle_q7"] - 0.05, Bs(), 0.3, fx=True)
    add(EV["schwelle_q7"], thud(0.35, 55), 0.35, fx=True)
    a, b = seg("abend2")
    add(a - 0.3, Wr(), 0.6, fx=True)
    add(a, crick, 0.5, dur=b - a, fade_in=0.4, fade_out=0.3)
    add(a, eve, 0.45, dur=b - a, fade_in=0.4, fade_out=0.3)
    add(a, real("fire2"), 0.18, dur=b - a, fade_in=0.4, fade_out=0.3)
    walk_steps(a + 0.1, a + 2.2, 0.22)
    add(EV["dich_q8"] - 0.4, shim, 0.6, fx=True)
    add(EV["dich_q8"] - 0.3, sparkle, 0.35, fx=True)

    # --- Der dritte Besuch: Baum, Befehl, Hügel, Bau, Gebet
    card("k3")
    a, b = seg("baum")
    wind(a, SEG["huegel"]["start"] + SEG["huegel"]["dur"], 0.7)
    add(a, camp, 0.35, dur=SEG["huegel"]["start"] + SEG["huegel"]["dur"] - a, fade_in=0.4, fade_out=0.4)
    add(a + 0.5, el("carving"), 0.75, dur=EV["steht_e13"] - a - 0.5, fade_in=0.3, fade_out=0.4, fx=True)
    add(a + 2.0, far(el("hawk"), 600, 6000) if el("hawk") is not None else None, 0.2, pan=-0.3, fx=True)
    add(EV["vater_e13"] - 1.4, R("riser", alt=lambda: riser(1.6)), 0.25, fx=True, fade_out=0.2)
    add(EV["vater_e13"] - 0.1, shim, 0.45, fx=True)
    add(EV["begrüßen_e13"] - 0.1, B(), 0.35, fx=True)
    add(EV["begrüßen_e13"], sparkle, 0.45, fx=True)
    add(EV["begrüßen_e13"], shimmer(b - EV["begrüßen_e13"] + 0.5), 0.9, fade_in=0.4, fade_out=0.6)
    a, b = seg("befehl")
    add(EV["haus_q13"] - 1.6, R("riser", alt=lambda: riser(1.6)), 0.3, fx=True, fade_out=0.15)
    add(EV["haus_q13"] - 0.05, B(), 0.4, fx=True)
    a, b = seg("huegel")
    add(EV["engel_e14"] - 0.1, shim, 0.7, fx=True)
    add(EV["engel_e14"], sparkle, 0.5, fx=True)
    add(EV["engel_e14"], shimmer(b - EV["engel_e14"] + 0.4), 1.0, fade_in=0.3, fade_out=0.4)
    a, b = seg("bau")
    cut("bau", 0.6)
    wind(a, b + SEG["gebet"]["dur"], 0.7)
    sp_ = el("stone_place")
    # erste Lage: jeder Stein ein Aufsetzen (wie im Bild: alle 0,42 s)
    for k in range(12):
        t = a + 0.4 + k * 0.42
        add(t, thud(0.3, rng.uniform(70, 95)), 0.4, pan=rng.uniform(-0.3, 0.3), fx=True)
        add(t + 0.01, sand_scrape(0.2), 0.15, fx=True)
    # Zeitraffer: schnelleres Steine-Klacken
    tm, ts, td = EV["mauern_e16"], EV["stein_e16"], EV["darauf_e16"]
    add(tm, speed(sp_, 1.6) if sp_ is not None else None, 0.8, dur=ts - 1.6 - tm, fade_in=0.2, fade_out=0.3, fx=True)
    add(tm - 0.4, W(), 0.5, fx=True)
    add(ts + 0.1, thud(0.5, 48), 0.6, fx=True)
    add(ts + 0.1, Bs(), 0.4, fx=True)
    add(td - 0.1, shim, 0.5, fx=True)
    add(td + 0.7, speed(sp_, 1.6) if sp_ is not None else None, 0.7, dur=b - td - 0.7, fade_in=0.2, fade_out=0.3, fx=True)
    a, b = seg("gebet")
    add(a, real("wind", 4.0), 0.25, dur=b - a, fade_in=0.3, fade_out=0.6)
    add(a, shimmer(b - a + 0.5), 1.0, fade_in=0.6, fade_out=0.8)
    add(LINES["q15"]["start"] + LINES["q15"]["dur"], B(), 0.35, fx=True)

    # --- Heute
    card("heute_karte")
    a, b = seg("heute")
    t_end = SEG["ende"]["start"] + SEG["ende"]["dur"]
    add(a - 0.2, tawaf, 1.0, dur=t_end - a + 2.8, fade_in=0.4, fade_out=2.5)
    add(a - 0.2, hall, 0.3, dur=t_end - a + 2.8, fade_in=0.4, fade_out=2.5)
    if talb is not None:  # ganze Talbiya im Hintergrund, beginnt mit der Tafel „HEUTE“, am Ende lang ausgeblendet
        add(SEG["heute_karte"]["start"] - 0.4, talb, 1.0, fade_in=0.5, fade_out=1.8, bed=True)
    a, b = seg("maqam")
    walk_steps(a, LINES["e20"]["start"] + 3.0, 0.18)
    add(EV["maqam_e19"] - 0.1, shim, 0.45, fx=True)
    add(EV["füßen_e20"] - 0.1, sparkle, 0.4, fx=True)
    add(EV["füßen_e20"] - 0.2, shimmer(4.0, 1.2), 0.8, fade_in=0.3, fade_out=1.2)
    a, b = seg("ende")
    add(LINES["e21"]["start"] + 3.0, shimmer(b - LINES["e21"]["start"] - 3.0 + 1.5), 0.9, fade_in=0.8, fade_out=1.5)
    a, b = seg("logo")
    add(a, B(), 0.5, fx=True)
    add(a - 0.5, W(), 0.6, fx=True)

    # Zitate (Ibrahim, Ismail, der Prophet ﷺ): leiser Schimmer darunter
    for q in QUOTES.values():
        add(q["start"] - 0.3, shimmer(q["dur"] + 1.6, 1.0), 0.6, fade_in=0.5, fade_out=1.2)

    # ================= Stimmen, Mischung, Lautheit
    n = len(buf)
    voice = np.zeros((n, 2))
    for l in TL["lines"]:
        if l.get("file"):
            x = load(ROOT / "public" / l["file"])
            i = int(l["start"] * SR)
            j = min(n, i + len(x))
            voice[i:j] += x[: j - i]

    def rms(x):
        return float(np.sqrt(np.mean(x ** 2)) + 1e-9)

    def active_rms(x, thr=1e-3):
        m = np.abs(x).max(axis=1) > thr
        return rms(x[m]) if m.any() else 1e-9

    v_ref = active_rms(voice)
    atmo = buf * (0.16 * v_ref / active_rms(buf))
    fx = fxb * (0.55 * v_ref / active_rms(fxb, 3e-3))

    def follower(x, att=0.03, rel=0.4):
        e = np.abs(x).max(axis=1)
        hop = int(0.01 * SR)
        e = np.array([e[k:k + hop].max() for k in range(0, len(e), hop)])
        out = np.zeros_like(e)
        a_, r_ = np.exp(-0.01 / att), np.exp(-0.01 / rel)
        cur = 0.0
        for k, v in enumerate(e):
            cur = a_ * cur + (1 - a_) * v if v > cur else r_ * cur + (1 - r_) * v
            out[k] = cur
        return np.repeat(out, hop)[: len(x)]
    dv = np.clip(follower(voice) / (2.5 * v_ref), 0, 1)
    mix = voice + atmo * (1 - 0.55 * dv)[:, None] + fx * (1 - 0.25 * dv)[:, None]
    if np.abs(bedb).max() > 0:  # Talbiya: Hintergrund (~ -14 dB unter der Stimme), unter der Erzählung noch einmal deutlich leiser
        bed = bedb * (0.2 * v_ref / active_rms(bedb))
        mix += bed * (1 - 0.7 * dv)[:, None]

    tmp = ROOT / "out" / "kb_mix_tmp.wav"
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        pk = np.max(np.abs(mix)) or 1
        w.writeframes((mix / pk * 0.5 * 32767).astype(np.int16).tobytes())
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    mj = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    out = ROOT / "public" / "qissa_kaaba" / "master.wav"
    af_ = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={mj['input_i']}:measured_TP={mj['input_tp']}:"
           f"measured_LRA={mj['input_lra']}:measured_thresh={mj['input_thresh']}:offset={mj['target_offset']}:linear=true,"
           "alimiter=limit=0.84:attack=3:release=60:level=disabled")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(tmp), "-af", af_, "-ar", str(SR), "-c:a", "pcm_s16le", str(out)],
                   check=True)
    tmp.unlink()
    chk = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(out), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    cj = json.loads(chk[chk.rindex("{"):chk.rindex("}") + 1])
    print("🔊", out.relative_to(ROOT), f"{n / SR:.1f}s  Lautheit {cj['input_i']} LUFS  Spitze {cj['input_tp']} dBTP")


if __name__ == "__main__":
    main()
