#!/usr/bin/env python3
"""Ton für „Futaba, 11. März 2011 – Wohnzimmer“ (blender/inkpop/room_scene.py): Raumton, Konsolen-Piepser, Küchengeklapper,
Erdbeben-Frühwarnung (Fernseher + Handys), Beben (Grollen, Geschirr, Knarzen, fallende Dinge, Kessel), Stille + Autoalarm,
Tsunami-Signal, Schritte, Strom-Klack, Sirene draußen, Schluss-Drone. Synthetisch -> public/futaba3/sfx.mp3
Außerdem: Fernseh-Stimmen (TV-Lautsprecher) und Durchsage (Megafon, draußen) als bearbeitete wav."""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TL = json.load(open(ROOT / "src/futaba3/timeline.json"))
EV = json.load(open(ROOT / "src/futaba3/events.json"))
SR = 44100
TOTAL = TL.get("END2", TL["END"]) + 9.5
N = int(TOTAL * SR)
rng = np.random.default_rng(2011)
mix = np.zeros((N, 2))
t_all = np.arange(N) / SR
EEW, Q, QE, PWR, END = TL["EEW"], TL["QUAKE"], TL["QEND"], TL["POWER"], TL.get("END2", TL["END"])
T2 = TL.get("T2", TL["END"])


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


def tone(f, d, a=0.003, dec=0.1):
    tt = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * tt) * env(len(tt), a, dec)


# Raumton + leises Summen der Elektrik bis Stromausfall, Vögel draußen bis Beben
room = norm(band(noise(TOTAL), 60, 700)) * 0.035
mix[:, 0] += room
mix[:, 1] += np.roll(room, 3000)
hum = np.sin(2 * np.pi * 50 * t_all) * 0.012 * gate(-1, PWR, 0.01)
mix[:, 0] += hum
mix[:, 1] += hum
t = 0.5
while t < Q:
    for _ in range(rng.integers(2, 4)):
        d = 0.06 + rng.random() * 0.07
        tt = np.arange(int(d * SR)) / SR
        f0 = 2800 + rng.random() * 2000
        add(t, np.sin(2 * np.pi * (f0 + 1500 * tt / d) * tt) * np.sin(np.pi * tt / d), 0.025, -0.6)
        t += d + 0.05
    t += 1.2 + rng.random() * 1.5
# Konsole: kleine Piepser (Hana spielt)
t = 0.3
while t < 15.9:
    add(t, tone(rng.choice([880, 1046, 1318, 1568]), 0.08, 0.002, 0.04), 0.05, -0.4)
    t += rng.choice([0.15, 0.2, 0.3, 0.45])
# Küche: Geschirr
for t0 in (8.2, 8.9, 9.6, 10.2):
    add(t0, norm(band(noise(0.12), 1500, 8000)) * env(int(0.12 * SR), 0.001, 0.03), 0.06, 0.6)
# Erdbeben-Frühwarnung: Fernseh-Gong + Handys
for k, f in enumerate((987.8, 1318.5, 987.8, 1318.5)):
    add(EEW + k * 0.45, tone(f, 0.6, 0.005, 0.35), 0.18, 0.3)


def phone_alarm(d):
    tt = np.arange(int(d * SR)) / SR
    f = np.where((tt * 4).astype(int) % 2 == 0, 1046.5, 1396.9)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.35 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return x * (((tt * 8).astype(int) % 2 == 0) * 0.6 + 0.4) * np.minimum(1, tt / 0.02)


add(EEW + 0.2, phone_alarm(Q + 1.8 - EEW), 0.12, -0.5)
add(EEW + 0.4, band(phone_alarm(Q + 1.5 - EEW), 500, 4000), 0.08, 0.7)
# Beben
qa = np.clip((t_all - Q) / 1.2, 0, 1) * np.clip((QE + 1.5 - t_all) / 2.5, 0, 1)
rumble = norm(band(noise(TOTAL), 16, 120)) * qa
mix[:, 0] += rumble * 0.8
mix[:, 1] += np.roll(rumble, 400) * 0.8
roar = norm(band(noise(TOTAL), 80, 900)) * qa * 0.25
mix[:, 0] += roar
mix[:, 1] += np.roll(roar, 700)
for _ in range(700):  # Geschirr, Glas, Kleinkram
    t0 = rng.uniform(Q + 0.4, QE + 1.0)
    d = 0.02 + rng.random() * 0.05
    add(t0, norm(band(noise(d), 1500, 9500)) * env(int(d * SR), 0.001, 0.012), 0.07 * rng.random(), rng.random() * 2 - 1)
for _ in range(16):  # Holz knarzt
    d = 0.7 + rng.random()
    tt = np.arange(int(d * SR)) / SR
    cr = np.sin(2 * np.pi * np.cumsum(80 + 60 * np.sin(tt * 5)) / SR) * band(noise(d), 60, 900)
    add(rng.uniform(Q + 0.5, QE), norm(cr) * np.sin(np.pi * tt / d), 0.16, rng.random() - 0.5)
for t0 in EV["fall"]:
    d = 0.3
    x = norm(band(noise(d), 200, 4000)) * env(int(d * SR), 0.001, 0.05) + 0.6 * tone(90, d, 0.002, 0.06)
    add(t0, x, 0.3, rng.random() * 1.4 - 0.7)
k0 = EV["kettle"]
add(k0, norm(band(noise(0.8), 300, 7000)) * env(int(0.8 * SR), 0.001, 0.15), 0.4, 0.8)
for k in range(5):
    add(k0 + 0.05 + k * 0.07, tone(1800 + 300 * k, 0.3, 0.001, 0.12), 0.06, 0.8)
# Lampe schwingt: leises Quietschen
for k in range(10):
    t0 = Q + 1.5 + k * 1.6
    if t0 > QE + 4:
        break
    d = 0.5
    tt = np.arange(int(d * SR)) / SR
    add(t0, np.sin(2 * np.pi * (1300 + 300 * np.sin(tt * 9)) * tt) * np.sin(np.pi * tt / d) * 0.5, 0.025, 0.1)
# Danach: Autoalarm weit weg, Tsunami-Signal im Fernsehen
ca = QE + 1.0
tt = np.arange(int((TOTAL - ca) * SR)) / SR
f = 900 + 500 * np.sign(np.sin(2 * np.pi * 1.6 * tt))
add(ca, band(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 300, 2500) * np.minimum(1, tt / 0.5), 0.025, -0.8)
for k in range(6):
    add(34.6 + k * 0.32, tone(740 if k % 2 else 988, 0.28, 0.003, 0.2), 0.14, 0.3)
# Mama: schnelle Schritte
for k in range(8):
    add(37.0 + k * 0.28, norm(band(noise(0.06), 120, 2500)) * env(int(0.06 * SR), 0.001, 0.02), 0.15, 0.5 - k * 0.06)
# Stromausfall: Klack + Fernseher aus
add(PWR, norm(band(noise(0.06), 400, 9000)) * env(int(0.06 * SR), 0.0005, 0.012), 0.7, 0.2)
tt = np.arange(int(0.5 * SR)) / SR
add(PWR, np.sin(2 * np.pi * 50 * tt * (1 - tt * 0.8)) * np.exp(-tt * 6), 0.15)
# Sirene draußen (steigt/fällt), ab kurz vor der Durchsage bis zum Ende
s0 = PWR + 0.6
tt = np.arange(int((TOTAL - s0) * SR)) / SR  # Sirene läuft bis zum Ende
fs = 600 + 400 * (0.5 - 0.5 * np.cos(2 * np.pi * tt / 6.0))
siren = band(np.sin(2 * np.pi * np.cumsum(fs) / SR), 300, 2500) * np.minimum(1, tt / 2.0)
add(s0, siren, 0.05, -0.7)
# Zeitsprung-Karte (15:27): dumpfer Schlag
tt = np.arange(int(1.6 * SR)) / SR
add(T2 + 0.02, norm(np.sin(2 * np.pi * (42 + 40 * np.exp(-tt * 9)) * tt) * env(len(tt), 0.003, 0.45)), 0.55)
# Die Welle: fernes Tosen schwillt an, Knirschen von Holz, Wasser schlägt ans Haus
w0 = T2 + 0.8
wr = norm(band(noise(TOTAL), 40, 1800)) * np.clip((t_all - w0) / (END - w0), 0, 1) ** 1.3 * gate(w0, END + 0.3, 0.3)
mix[:, 0] += wr * 0.75
mix[:, 1] += np.roll(wr, 600) * 0.75
low = norm(band(noise(TOTAL), 20, 140)) * np.clip((t_all - w0) / (END - w0), 0, 1) * gate(w0, END + 0.3, 0.3)
mix[:, 0] += low * 0.5
mix[:, 1] += low * 0.5
for _ in range(14):
    d = 0.5 + rng.random()
    tt = np.arange(int(d * SR)) / SR
    cr = np.sin(2 * np.pi * np.cumsum(60 + 40 * np.sin(tt * 4)) / SR) * band(noise(d), 60, 700)
    add(rng.uniform(w0 + 2, END - 0.5), norm(cr) * np.sin(np.pi * tt / d), 0.12, rng.random() - 0.5)
# Mandarinen/Tasse: dumpfe Aufschläge
for t0 in (20.92, 21.72, 23.32, 24.52, 24.95):
    add(t0, tone(140, 0.12, 0.002, 0.04) + 0.4 * norm(band(noise(0.12), 300, 3000)) * env(int(0.12 * SR), 0.001, 0.02), 0.25, -0.2)
# Schluss: tiefer Schlag beim Übergang zur Texttafel + Drone
tt = np.arange(int(2.5 * SR)) / SR
add(END, norm(np.sin(2 * np.pi * (38 + 40 * np.exp(-tt * 8)) * tt) * env(len(tt), 0.003, 0.7)), 0.6)
drone = (np.sin(2 * np.pi * 55 * t_all) + 0.5 * np.sin(2 * np.pi * 82.4 * t_all)) * gate(END + 0.3, TOTAL, 1.5) * 0.04
mix[:, 0] += drone
mix[:, 1] += drone

mix = np.tanh(mix * 1.4)
mix = mix / np.max(np.abs(mix)) * 0.85
out = ROOT / "public/futaba3"
out.mkdir(parents=True, exist_ok=True)
with wave.open(str(out / "sfx.wav"), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(out / "sfx.wav"), "-b:a", "160k", str(out / "sfx.mp3")], check=True)
(out / "sfx.wav").unlink()
tim = json.load(open(ROOT / "src/futaba3/timing.json"))
scr = json.load(open(ROOT / "src/futaba3/script.json"))
files = {s["id"]: l["file"] for s, l in zip(scr["sentences"], tim["lines"])}
for sid in ("tv1", "tv2", "tv3"):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(ROOT / "public" / files[sid]), "-af",
                    "highpass=f=220,lowpass=f=5500,aecho=0.8:0.4:35:0.25,volume=0.9", str(out / f"{sid}_tv.wav")], check=True)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(ROOT / "public" / files["lsp"]), "-af",
                "highpass=f=450,lowpass=f=3000,acompressor=threshold=0.1:ratio=6,volume=2.0,aecho=0.8:0.7:260|520:0.4|0.25,lowpass=f=2400", str(out / "lsp_far.wav")], check=True)
print("🔊 sfx.mp3 + TV/Durchsage", TOTAL, "s")
