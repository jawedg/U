#!/usr/bin/env python3
"""Fertige Tonspur für „Was, wenn das dein letzter Flug ist?“ (src/flug): Stimmen + echte Koran-Rezitation + Atmo + Effekte (keine Musik).

Nutzer: „immer Effekte, es soll nicht still klingen – wie in einem Film“. Geräusche per ElevenLabs (scripts/el_sfx.py,
assets/sfx/el_fl_*.flac): Kabine, Gong, Durchsage-Klick, Turbulenz, Absacken, Alarm, Masken, Sturm, Schreie, Donner, Baby,
Sturzflug, Beruhigung, Aufsetzen + Umkehrschub, Applaus, Gate, Terminal, Schritte, Tür, Gebetsraum, Teppich, Handy, Herzschlag.
Kapitän mit Bordlautsprecher-Klang. Atmo wird unter der Stimme leiser (Ducking); -14 LUFS, True Peak -1,5 dB, Begrenzer.
Ausgabe: public/flug/master.wav
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
TL = json.loads((ROOT / "src" / "flug" / "timeline.json").read_text(encoding="utf-8"))
SEG = {s["id"]: s for s in TL["segments"]}
EV = TL["events"]
LINES = {l["id"]: l for l in TL["lines"]}
REC = {r["id"]: r for r in TL.get("recites", [])}
TOTAL = TL["total"] + 0.5
N = int(TOTAL * SR)
buf = np.zeros((N, 2))    # Atmo (unter der Stimme leiser)
fxb = np.zeros((N, 2))    # Effekte
rng = np.random.default_rng(7)


def load(path, t0=0.0, dur=None):
    cmd = ["ffmpeg", "-loglevel", "error", "-ss", f"{t0:.3f}"] + (["-t", f"{dur:.3f}"] if dur else []) + [
        "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def el(key, t0=0.0, dur=None, peak=0.8):
    p = REAL / f"el_{key}.flac"
    if not p.exists():
        print("   ⚠️ fehlt", p.name)
        return None
    x = load(p, t0, dur)
    return x / (np.max(np.abs(x)) or 1) * peak


def st(x):
    return x if x.ndim == 2 else np.stack([x, x], axis=1)


def add(t0, x, g=1.0, pan=0.0, fade_in=0.0, fade_out=0.0, dur=None, fx=False):
    if x is None:
        return
    x = st(x)
    if dur is not None:
        n = int(dur * SR)
        if len(x) < n:   # Schleife mit weicher Überblendung
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
    j = min(N, i + len(x))
    if j > i:
        (fxb if fx else buf)[i:j] += x[: j - i]


def seg(i):
    return SEG[i]["start"], SEG[i]["start"] + SEG[i]["dur"]


def lowpass(x, hi=900):
    x = st(x)
    return np.stack([S.band(x[:, c], 30, hi) for c in range(2)], axis=1)


def pa(x):
    """Bordlautsprecher: schmalbandig, leicht verzerrt, kurzer Raumhall."""
    x = st(x)
    y = np.stack([S.band(x[:, c], 320, 3400) for c in range(2)], axis=1)
    y = np.tanh(y * 2.2) / 2.2
    n = int(0.35 * SR)
    tt = np.arange(n) / SR
    out = []
    for c in range(2):
        ir = rng.standard_normal(n) * np.exp(-tt / 0.07)
        ir /= np.sqrt(np.sum(ir ** 2))
        L = len(y) + n
        z = np.fft.irfft(np.fft.rfft(y[:, c], L) * np.fft.rfft(ir, L), L)[: len(y)]
        out.append(y[:, c] * 0.8 + z * 0.35)
    return np.stack(out, axis=1) * 1.6


def whoosh(sec=0.35, g=1.0):
    x = S.band(S.noise(sec), 1500, 7000)
    env = np.sin(np.linspace(0, np.pi, len(x))) ** 2
    return x * env * g


def main():
    # ------------------------------------------------------------------ Einstieg: mitten im Absturz (laut), dann gedämpft + Herzschlag
    a0, a1 = seg("hook_a")
    add(a0, el("fl_storm", 6.0), 1.0, dur=a1 - a0 + 0.4, fade_out=0.3)
    add(a0, el("fl_screams", 1.0), 0.75, dur=a1 - a0 + 0.3, fade_out=0.3, fx=True)
    add(a0, el("fl_alarm"), 0.35, dur=a1 - a0 + 0.2, fade_out=0.2, fx=True)
    add(a0, el("fl_impact"), 1.0, fx=True)
    add(a0 + 0.02, el("fl_thunder"), 0.8, dur=2.0, fade_out=0.6, fx=True)
    b0, b1 = seg("hook_b")
    add(b0, lowpass(el("fl_storm", 9.0), 700), 0.9, dur=b1 - b0 + 0.3, fade_in=0.15, fade_out=0.5)
    add(b0, el("fl_heart"), 0.9, dur=b1 - b0 + 0.2, fade_out=0.5, fx=True)
    # ------------------------------------------------------------------ Kabine (Nachtflug): Triebwerke, Klima, leises Murmeln
    k0, _ = seg("kabine")
    cab_end = seg("gong")[0] + 3.0
    add(k0 - 0.3, el("fl_cabin"), 1.0, dur=cab_end - k0 + 0.3, fade_in=0.6)
    add(k0, el("fl_chatter"), 0.25, dur=seg("gong")[0] + 8 - k0, fade_in=1.0, fade_out=2.0)
    add(k0, el("fl_wind"), 0.25, dur=seg("handy")[0] - k0 + 0.5, fade_in=0.5, fade_out=0.5)
    tv = EV.get("video_k1", k0 + 4.3)
    add(tv - 0.8, el("fl_vidlaugh"), 0.32, pan=-0.45, dur=2.6, fade_in=0.2, fade_out=0.5, fx=True)
    # ------------------------------------------------------------------ Handy: Brummen + Ding beim Hinweis, Wischen, Video leise
    h0, h1 = seg("handy")
    add(h0, el("fl_vidlaugh", 2.0), 0.12, dur=h1 - h0, fade_in=0.3, fade_out=0.4, fx=True)
    add(EV.get("leuchtet_k2", h0 + 1.2) - 0.15, el("fl_buzz"), 0.55, fx=True)
    add(EV.get("wischst_k2", h0 + 4.1) + 0.05, whoosh(0.3), 0.25, fx=True)
    add(EV.get("landung_k3", h0 + 6.1) + 0.25, whoosh(0.35), 0.18, fx=True)
    # ------------------------------------------------------------------ Gong, Durchsage, leichte Turbulenz, dann Absacken
    g0, g1 = seg("gong")
    add(g0 + 0.3, el("fl_chime"), 0.6, fx=True)
    add(LINES["t1"]["start"] - 0.35, el("fl_pa"), 0.45, fx=True)
    add(g0 + 1.8, el("fl_turb"), 0.55, dur=g1 - g0 - 1.8, fade_in=1.2)
    t_drop = g1 - 1.45
    add(t_drop - 0.05, el("fl_drop"), 1.0, fx=True)
    add(t_drop + 0.15, el("fl_bin"), 0.6, pan=0.35, fx=True)
    add(t_drop + 0.3, el("fl_screams"), 0.6, dur=2.2, fade_out=0.6, fx=True)
    add(t_drop + 0.25, el("fl_masks"), 0.7, fx=True)   # v2: Masken fallen schon beim Absacken
    add(t_drop, el("fl_storm"), 0.9, dur=g1 - t_drop + 0.5, fade_in=0.15)
    # ------------------------------------------------------------------ Absturz: Sturm, Masken, Alarm, Donner, Sturzflug, Schreie, Baby
    s0, s1 = seg("absturz")
    e0, e1 = seg("beten")
    add(s0, el("fl_storm", 2.0), 1.0, dur=e1 - s0 + 0.2, fade_out=0.6)
    add(s0 + 0.1, el("fl_masks"), 0.35, fx=True)
    add(s0 + 0.3, el("fl_alarm"), 0.32, dur=s1 - s0 - 0.3, fade_in=0.2, fade_out=0.5, fx=True)
    t_fall = EV.get("fällt_a2", s0 + 3.2)
    add(t_fall - 0.25, el("fl_dive"), 0.95, fade_out=1.0, fx=True)
    add(s0 + 0.2, el("fl_screams", 3.0), 0.45, dur=s1 - s0, fade_in=0.5, fade_out=0.8, fx=True)
    add(s0 + 4.0, el("fl_baby"), 0.35, pan=0.5, dur=8.0, fade_in=0.8, fade_out=1.0, fx=True)
    ta2, ta3 = LINES["a2"]["start"], LINES["a3"]["start"]
    egal = EV.get("egal_a2", ta2 + 5.4)
    for k, tl_ in enumerate((s0 + 0.6, t_fall + 0.1, egal - 0.4, ta3 + 0.5, s1 + 0.4 - 1.5)):
        add(tl_, el("fl_thunder", 0.0), 0.75 if k % 2 == 0 else 0.6, dur=3.5, fade_out=1.2, fx=True)
    # ------------------------------------------------------------------ Beten: Sturm etwas dumpfer, Herzschlag, Donner, Baby weint
    add(e0, el("fl_heart"), 0.55, dur=e1 - e0, fade_in=1.5, fade_out=1.0, fx=True)
    add(e0 + 0.2, el("fl_baby", 2.0), 0.4, pan=0.55, dur=e1 - e0 - 0.4, fade_in=0.5, fade_out=1.0, fx=True)
    ta5, ta6 = LINES["a5"]["start"], LINES["a6"]["start"]
    tdu = EV.get("du_a5", ta5 + 6.4)
    for k, tl_ in enumerate((e0 + 0.8, ta5 + 0.4, ta5 + 3.6, tdu + 0.3, ta6 + 2.6, e1 + 0.4 - 1.0)):
        add(tl_, el("fl_thunder", 0.0), 0.55, dur=3.0, fade_out=1.0, fx=True)
    # ------------------------------------------------------------------ Stille: Rütteln hört auf, Kabine beruhigt sich, Gong, Durchsage
    t0_, t1_ = seg("stille")
    add(t0_ - 0.1, el("fl_recover"), 0.9, dur=4.0, fade_out=1.5)
    add(t0_ + 0.8, el("fl_cabin", 3.0), 0.9, dur=t1_ - t0_ + 1.0, fade_in=1.2)
    add(t0_ + 1.0, el("fl_chime"), 0.5, fx=True)
    add(LINES["s1"]["start"] - 0.35, el("fl_pa"), 0.45, fx=True)
    add(t0_ + 0.2, el("fl_chatter", 4.0), 0.18, dur=t1_ - t0_, fade_in=2.0)
    # ------------------------------------------------------------------ Landung: Aufsetzen, Umkehrschub, Applaus
    l0, l1 = seg("landung")
    add(l0 - 0.2, el("fl_cabin", 8.0), 0.9, dur=l1 - l0 + 0.6, fade_in=0.3, fade_out=0.5)
    add(l0 + 1.4 - 0.3, el("fl_touchdown"), 1.0, fx=True)
    # v2 (Nutzer: „was war das für ein Geschrei“): altes Applaus-Geräusch hatte Jubelrufe -> reines Klatschen + erleichtertes Murmeln
    add(l0 + 2.0, el("fl_applause2"), 0.5, dur=l1 - l0 - 1.6, fade_in=0.4, fade_out=1.2, fx=True)
    # ------------------------------------------------------------------ Am Gate: Gurte, Fächer, Stimmen, Handys
    v0, v1 = seg("vergessen")
    add(v0 - 0.2, el("fl_gate"), 0.9, dur=v1 - v0 + 0.6, fade_in=0.4, fade_out=0.8)
    for k in range(3):
        add(v0 + 1.2 + k * 2.3, el("fl_buzz"), 0.18, pan=(-0.4, 0.3, 0.6)[k], fx=True)
    # ------------------------------------------------------------------ Koran-Tafel: leiser Raumton (nie ganz still)
    c0, c1 = seg("koran")
    add(c0 - 0.3, el("fl_room"), 0.5, dur=c1 - c0 + 0.8, fade_in=0.6, fade_out=0.8)
    # ------------------------------------------------------------------ Terminal (Morgen): Halle, Schritte, Tür am Ende
    m0, m1 = seg("terminal")
    add(m0 - 0.3, el("fl_terminal"), 1.0, dur=m1 - m0 + 0.6, fade_in=0.6, fade_out=0.6)
    add(m0, el("fl_steps"), 0.45, dur=m1 - m0 - 0.4, fade_out=0.4, fx=True)
    # ------------------------------------------------------------------ Gebetsraum: Tür, ruhiger Raum, Teppich
    p0, p1 = seg("gebetsraum")
    add(p0 - 0.2, el("fl_door"), 0.45, fx=True)
    add(p0, el("fl_room"), 0.8, dur=p1 - p0 + 0.6, fade_in=0.6)
    add(LINES["qh"]["start"] + 0.35, el("fl_rug"), 0.5, fx=True)
    add(EV.get("jetzt_e5", p0 + 15.0) - 0.1, whoosh(0.4), 0.12, fx=True)
    # ------------------------------------------------------------------ Ende: Raumton klingt mit der Rezitation aus
    z0, z1 = seg("ende")
    add(z0 - 0.3, el("fl_room", 5.0), 0.55, dur=z1 - z0 + 0.6, fade_out=2.0)

    # ------------------------------------------------------------------ Stimmen + Rezitation
    voice = np.zeros((N, 2))
    for l in TL["lines"]:
        if l.get("file"):
            x = load(ROOT / "public" / l["file"])
            if l.get("speaker") == "Kapitaen":
                x = pa(x)
            i = int(l["start"] * SR)
            j = min(N, i + len(x))
            voice[i:j] += x[: j - i]
    for r in TL.get("recites", []):
        x = load(ROOT / "public" / r["file"])
        x = x / (np.max(np.abs(x)) or 1) * 0.9
        i = int(r["start"] * SR)
        j = min(N, i + len(x))
        voice[i:j] += x[: j - i]

    def rms(x):
        return float(np.sqrt(np.mean(x ** 2)) + 1e-9)

    def active_rms(x, thr=1e-3):
        m = np.abs(x).max(axis=1) > thr
        return rms(x[m]) if m.any() else 1e-9

    v_ref = active_rms(voice)
    atmo = buf * (0.22 * v_ref / active_rms(buf))   # Film: Atmo präsenter als bei QISSAH (0.16)
    fx = fxb * (0.6 * v_ref / active_rms(fxb, 3e-3))

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
    mix = voice + atmo * (1 - 0.5 * dv)[:, None] + fx * (1 - 0.3 * dv)[:, None]

    tmp = ROOT / "out" / "fl_mix_tmp.wav"
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        pk = np.max(np.abs(mix)) or 1
        w.writeframes((mix / pk * 0.5 * 32767).astype(np.int16).tobytes())
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    mj = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    out = ROOT / "public" / "flug" / "master.wav"
    af_ = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={mj['input_i']}:measured_TP={mj['input_tp']}:"
           f"measured_LRA={mj['input_lra']}:measured_thresh={mj['input_thresh']}:offset={mj['target_offset']}:linear=true,"
           "alimiter=limit=0.84:attack=3:release=60:level=disabled")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(tmp), "-af", af_, "-ar", str(SR), "-c:a", "pcm_s16le", str(out)],
                   check=True)
    tmp.unlink()
    chk = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(out), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    cj = json.loads(chk[chk.rindex("{"):chk.rindex("}") + 1])
    print("🔊", out.relative_to(ROOT), f"{N / SR:.1f}s  Lautheit {cj['input_i']} LUFS  Spitze {cj['input_tp']} dBTP")


if __name__ == "__main__":
    main()
