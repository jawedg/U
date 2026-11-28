"""Flug v2: neue Stimm-Kandidaten (Sitznachbar ohne Clown-Stimme, ernste Frau für „Ya Allah“ + „Ya Rabbi … meine Kinder“).
Erzeugt je Kandidat und Zeile eine ElevenLabs-Aufnahme (Cache in out/stimmproben), misst die Tonhöhe, prüft per Spracherkennung
und legt Hörproben (alle Zeilen einer Figur nacheinander) nach out/stimmproben/flug/figuren_v2/<name>.m4a."""
import json, subprocess, sys, wave
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/user/U/scripts")
import voice_gemini as VG

ROOT = Path("/home/user/U")
CACHE = ROOT / "out/stimmproben"
OUT = ROOT / "out/stimmproben/flug/figuren_v2"
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / "tmp"
TMP.mkdir(exist_ok=True)

FIG = json.loads(Path(sys.argv[1]).read_text())   # {"name": {"voice": id, "lines": [el, ...]}}


def f0(path):
    w = wave.open(str(path)); sr = w.getframerate(); n = w.getnframes(); ch = w.getnchannels()
    y = np.frombuffer(w.readframes(n), dtype=np.int16).astype(float).reshape(-1, ch).mean(1) / 32768
    fr, hop, vals = int(0.04 * sr), int(0.01 * sr), []
    for i in range(0, len(y) - fr, hop):
        x = y[i:i + fr]
        if np.sqrt((x ** 2).mean()) < 0.02:
            continue
        x = x - x.mean(); c = np.correlate(x, x, "full")[fr - 1:]
        lo, hi = int(sr / 600), int(sr / 70)
        k = lo + np.argmax(c[lo:hi])
        if c[k] > 0.4 * c[0]:
            vals.append(sr / k)
    return round(float(np.median(vals))) if vals else 0


def stt(path):
    r = subprocess.run(["curl", "-s", "-m", "180", "-H", "xi-api-key: proxy-injected", "-F", "model_id=scribe_v1",
                        "-F", "language_code=de", "-F", f"file=@{path}", "https://api.elevenlabs.io/v1/speech-to-text"],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout).get("text", "")
    except json.JSONDecodeError:
        return "?" + r.stdout[:100]


for name, spec in FIG.items():
    parts = []
    for k, el in enumerate(spec["lines"]):
        mp3, _ = VG.eleven_tts(el, spec["voice"], "eleven_v3", spec.get("settings"), CACHE)
        wav = TMP / f"{name}-{k}.wav"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100", str(wav)], check=True)
        print(f"{name} [{k}] Tonhöhe {f0(wav)} Hz | erkannt: {stt(wav)!r}")
        parts.append(wav)
    lst = TMP / f"{name}.txt"
    sil = TMP / "sil.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.8", str(sil)], check=True)
    lst.write_text("".join(f"file '{p}'\nfile '{sil}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-af", "loudnorm=I=-16:TP=-1.5", "-c:a", "aac", "-b:a", "160k", str(OUT / f"{name}.m4a")], check=True)
