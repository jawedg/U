#!/usr/bin/env python3
"""Fertige Tonspur für „Der erste Adhan“ (QISSA, POV): Stimmen + echter Adhan + Atmo + Effekte (keine Musik).

Echte Geräusch-Aufnahmen (frei lizenziert, Wikimedia Commons, Nachweis in assets/sfx/CREDITS.md) aus assets/sfx/*.flac,
sonst synthetische Klänge aus scripts/sfx.py. Mischung: Atmo wird unter der Stimme leiser (Ducking), am Ende
Lautheit auf -14 LUFS und Begrenzer (True Peak -1,5 dB) -> nichts übersteuert.
Ausgabe: public/qissa_adhan/master.wav (Remotion spielt nur diese eine Spur).
"""
import json
import sys
import wave
from pathlib import Path

import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sfx as S  # noqa: E402

SR = S.SR = 48000
REAL = ROOT / "assets" / "sfx"


def load(path, t0=0.0, dur=None, sr=SR):
    """Audiodatei (beliebiges Format) -> Stereo float, Abtastrate sr."""
    cmd = ["ffmpeg", "-loglevel", "error", "-ss", f"{t0:.3f}"] + (["-t", f"{dur:.3f}"] if dur else []) + [
        "-i", str(path), "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def real(key, t0=0.0, dur=None, peak=0.8):
    """echte Aufnahme assets/sfx/<key>.flac (auf Spitze normiert) oder None"""
    p = REAL / f"{key}.flac"
    if not p.exists():
        return None
    x = load(p, t0, dur)
    return x / (np.max(np.abs(x)) or 1) * peak
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
buf = np.zeros((int(TOTAL * SR), 2))   # Atmo (wird unter Stimme/Adhan leiser)
fxb = np.zeros((int(TOTAL * SR), 2))   # Effekte (bleiben)


def add(t0, x, g=1.0, pan=0.0, fade_in=0.0, fade_out=0.0, dur=None, fx=False):
    if x is None:
        return
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
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
    if x is None:
        return
    i = int(max(0, t0) * SR)
    j = min(len(buf), i + len(x))
    if j > i:
        (fxb if fx else buf)[i:j] += x[: j - i]


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


def riser(sec=2.2):
    """anschwellendes Rauschen (Spannung vor dem Adhan / vor Wendepunkten) – keine Musik"""
    n = int(sec * SR)
    tt = np.linspace(0, 1, n)
    x = S.band(S.noise(sec), 300, 5000) * tt ** 2.2
    x += S.band(S.noise(sec), 60, 250) * tt ** 1.5 * 0.6
    return x * (1 - np.clip((tt - 0.96) / 0.04, 0, 1))


def heartbeat(sec, bpm=62):
    """dumpfer Herzschlag (Traum)"""
    x = np.zeros(int(sec * SR))
    tt = np.arange(int(0.25 * SR)) / SR
    thump = np.sin(2 * np.pi * 55 * tt) * np.exp(-tt / 0.06)
    k = 0.0
    while k < sec - 0.5:
        for off, g in ((0.0, 1.0), (0.24, 0.7)):
            i = int((k + off) * SR)
            x[i:i + len(thump)] += thump[: len(x) - i] * g
        k += 60 / bpm
    return S.band(x, 30, 160)


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


def walk_steps(t0, t1, g=0.3, run=False):
    """Schritte: echte Kies-/Sandschritte (Aufnahme, geloopt) oder synthetisch"""
    x = real("gravel_run" if run else "gravel1") if run else real("gravel1")
    if x is None:
        x = real("gravel2")
    if x is None or t1 - t0 < 0.4:
        steps(t0, t1, gap=0.24 if run else 0.47, g=g * 0.9, run=run)
        return
    add(t0, x, g * (1.3 if run else 1.0), fade_in=0.15, fade_out=0.3, dur=t1 - t0, fx=True)


def night_bed(t0, t1, g=1.0, fade_in=0.0, fade_out=0.0):
    """Nacht: echte Grillen (Feldaufnahme) + leiser Wüstenwind"""
    c = real("crickets", 2.0)
    add(t0, c, 0.55 * g, dur=t1 - t0, fade_in=fade_in, fade_out=fade_out)
    add(t0, get(S.amb_night, "amb_night", 60), (0.35 if c is not None else 0.9) * g, dur=t1 - t0, fade_in=fade_in, fade_out=fade_out)


def dawn_bed(t0, t1, g=1.0, fade_in=0.0, fade_out=0.0):
    """Morgen: echte Vögel/Hunde/Grillen in der Dämmerung + leiser Wind"""
    d = real("dawn", 5.0)
    add(t0, d, 0.6 * g, dur=t1 - t0, fade_in=fade_in, fade_out=fade_out)
    add(t0, get(S.amb_dawn, "amb_dawn", 60), (0.3 if d is not None else 0.85) * g, dur=t1 - t0, fade_in=fade_in, fade_out=fade_out)


def main():
    dream = get(S.amb_dream, "amb_dream", 40)
    syn_bell = get(S.bell, "bell")
    syn_horn = get(S.horn, "horn")
    syn_fire = get(S.fire, "fire")
    church = real("bell1") if real("bell1") is not None else syn_bell
    hand = real("handbell", 0.0, 4.0)
    shofar = real("shofar", 0.0, 3.2)
    fire = real("fire", 1.0, 3.0)
    rooster = real("rooster1")
    rooster2 = real("rooster2")
    door_s = real("door_hinge")
    door_b = real("door_slam")

    # --- Einstieg (Hook): Morgen über Medina, „Allahu akbar“ (Adhan-Spur unten), Schnitt mit Schlag
    a, b = seg("hook_a")
    dawn_bed(a, b + 0.3, 0.55, fade_out=0.3)
    a, b = seg("hook_b")
    add(a - 0.15, whoosh(0.5, 0.6), 1.0, fx=True)
    add(a, boom(), 0.5, fx=True)
    dawn_bed(a, b + 0.3, 0.8, fade_out=0.3)
    a, b = seg("hook_c")
    add(a - 0.25, whoosh(0.7, 0.6), 1.0, fx=True)
    add(a, dream, 0.8, dur=b - a + 0.4, fade_in=0.15, fade_out=0.4)
    add(a, shimmer(b - a + 0.4, 1.6), 1.0, fade_in=0.3, fade_out=0.4)
    add(a + 0.1, hand, 0.25, fx=True, fade_out=1.0)

    # --- Nacht: Gasse, Moschee, Beratung
    a, b = seg("gasse")
    add(a - 0.3, whoosh(0.9, 0.5), 1.0, fx=True)
    add(a + 0.05, boom(), 0.6, fx=True)
    night_bed(a, b + 0.3, 1.0, fade_in=0.3)
    walk_steps(a + 0.2, b - 1.0, 0.32)
    a, b = seg("moschee")
    night_bed(a, b + 0.3, 0.9)
    add(a + 1.5, murmur(b - a - 1.5), 0.16, fade_in=1.0, fade_out=1.0)
    walk_steps(a, a + 2.5, 0.25)
    a, b = seg("beratung")
    night_bed(a, b + 0.3, 0.55)
    add(a, shimmer(b - a), 0.4, fade_in=1.0, fade_out=1.0)
    add(EV["glocke_d4"] - 0.05, church, 0.5, fx=True, fade_out=0.8, dur=2.4)
    add(EV["horn_d4"] - 0.05, shofar if shofar is not None else syn_horn, 0.45, fx=True, fade_out=0.5, dur=2.2)
    add(EV["feuer_d4"] - 0.1, fire if fire is not None else syn_fire[: int(2.2 * SR)], 0.6, fx=True, fade_in=0.05, fade_out=0.8, dur=2.4)
    # --- Tafel „In dieser Nacht“
    a, b = seg("nacht")
    add(a - 0.2, whoosh(1.0, 0.6), 1.0, fx=True)
    add(a + 0.05, boom(), 0.45, fx=True)
    night_bed(a, b + 0.6, 0.45, fade_out=1.2)
    # --- Traum (Traum-Atmo blendet schon auf der Tafel ein -> nie Stille)
    a, b = seg("traum")
    a0 = SEG["nacht"]["start"] + 0.3
    add(a0, dream, 0.9, dur=b - a0 + 1.0, fade_in=1.2, fade_out=1.6)
    add(a, shimmer(b - a), 0.7, fade_in=1.5, fade_out=1.0)
    add(EV.get("glocke_d7", LINES["d7"]["start"] + 1.0) - 0.05, hand if hand is not None else syn_bell, 0.35, fx=True, fade_out=1.0)
    add(a + 0.2, heartbeat(7.0), 0.5, fade_in=1.0, fade_out=2.0, fx=True)
    add(LINES["d8"]["start"], shimmer(4.5, 2.0), 1.0, fade_in=0.8, fade_out=1.5)
    for q in QUOTES.values():
        add(q["start"] - 0.3, shimmer(q["dur"] + 2.0, 1.4), 1.0, fade_in=0.6, fade_out=1.5)
    # --- Tafel „Am Morgen“ + Morgen + Adhan-Szenen + Umar
    a, b = seg("morgen_karte")
    add(a - 0.2, whoosh(1.0, 0.6), 1.0, fx=True)
    add(a + 0.05, boom(), 0.35, fx=True)
    a = SEG["morgen"]["start"]
    b = SEG["umar"]["start"] + SEG["umar"]["dur"]
    a0 = SEG["morgen_karte"]["start"] + 0.3
    dawn_bed(a0, b, 1.0, fade_in=1.2)
    add(a + 0.4, rooster, 0.22, fx=True, pan=-0.4)
    add(a, shimmer(SEG["morgen"]["dur"]), 0.35, fade_in=1.0, fade_out=1.0)
    walk_steps(a + 0.2, a + 4.8, 0.2)
    add(SEG["dach_a"]["start"] + 0.5, murmur(EV["athan"] - SEG["dach_a"]["start"]), 0.1, fade_out=0.8)
    add(EV["athan"] - 2.2, riser(2.2), 0.22, fx=True)
    td = EV["door_umar"]
    add(td - 0.25, door_s, 0.35, fx=True, dur=1.2, fade_out=0.4)
    add(td, door_b if door_b is not None else door_bang(), 0.6, fx=True)
    walk_steps(td + 0.1, td + 4.0, 0.42, run=True)
    add(td + 0.1, cloth(3.5), 0.35, fade_out=1.0, fx=True)
    a2, b2 = seg("umar")
    walk_steps(td + 2.1, b2 - 0.3, 0.22)
    # --- Ende: Morgen, Vögel, Auswahltafel, Logo
    a, b = seg("ende")
    dawn_bed(a, b + 2.6, 1.0, fade_out=2.0)
    add(a + 0.3, rooster2, 0.15, fx=True, pan=0.5)
    ch = TL["choice"]
    add(ch["start"], ping(), 0.5, fx=True)
    add(ch["start"] + 0.5, ping(), 0.4, fx=True)
    a, b = seg("logo")
    add(a, boom(), 0.5, fx=True)
    add(a - 0.3, whoosh(0.8, 0.4), 1.0, fx=True)

    # ================= Stimmen + Adhan, Mischung, Lautheit
    n = len(buf)
    voice = np.zeros((n, 2))
    for l in TL["lines"]:
        if l.get("file"):
            x = load(ROOT / "public" / l["file"])
            i = int(l["start"] * SR)
            j = min(n, i + len(x))
            voice[i:j] += x[: j - i]
    adh = np.zeros((n, 2))
    ath = TL["athan"]
    af = ROOT / "public" / ath["file"]
    if af.exists():
        t0, t1 = EV["athan"], EV["athan_end"]
        x = load(af, ath["in"], t1 - t0 + 0.1)
        tt = np.arange(len(x)) / SR + t0
        env_ = np.clip((tt - t0) / 0.4, 0, 1) * np.interp(tt, [EV["duck"] - 0.3, EV["duck"] + 0.4], [1, 0.3]) * \
            np.clip((t1 - tt) / 1.0, 0, 1)
        i = int(t0 * SR)
        adh[i:i + len(x)] += x[: n - i] * env_[: n - i, None]
        if "hook_takbir" in EV:
            th = EV["hook_takbir"]
            hd = SEG["hook_a"]["dur"] + 0.25
            x = load(af, ath.get("hook_in", 2.2), hd)
            tt = np.arange(len(x)) / SR
            x = x * (np.clip(tt / 0.05, 0, 1) * np.clip((hd - tt) / 0.45, 0, 1))[:, None]
            i = int(th * SR)
            adh[i:i + len(x)] += x
    else:
        print("⚠️  Adhan-Aufnahme fehlt:", af)

    def rms(x):
        return float(np.sqrt(np.mean(x ** 2)) + 1e-9)

    def active_rms(x, thr=1e-3):
        m = np.abs(x).max(axis=1) > thr
        return rms(x[m]) if m.any() else 1e-9

    v_ref = active_rms(voice)
    adh *= (0.95 * v_ref) / active_rms(adh, 3e-3) if adh.any() else 1.0
    atmo = buf * (0.16 * v_ref / active_rms(buf))
    fx = fxb * (0.55 * v_ref / active_rms(fxb, 3e-3))

    # Ducking: Atmo unter Stimme (-7 dB) und unter dem Adhan (-4 dB), weich
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
    da = np.clip(follower(adh) / (2.5 * v_ref), 0, 1)
    duck = (1 - 0.55 * dv) * (1 - 0.35 * da)
    mix = voice + adh + atmo * duck[:, None] + fx * (1 - 0.25 * dv)[:, None]

    tmp = ROOT / "out" / "qissa_mix_tmp.wav"
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        pk = np.max(np.abs(mix)) or 1
        w.writeframes((mix / pk * 0.5 * 32767).astype(np.int16).tobytes())  # Vorstufe mit viel Reserve
    # Lautheit -14 LUFS (TikTok), True Peak -1,5 dB: zuerst messen, dann linear angleichen + Begrenzer
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    mj = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    out = ROOT / "public" / "qissa_adhan" / "master.wav"
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
