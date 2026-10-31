#!/usr/bin/env python3
"""Natürliche KI-Erzählstimme mit Google Gemini TTS (kostenloser API-Schlüssel).

Schlüssel holen: https://aistudio.google.com/apikey
Dann:  export GEMINI_API_KEY=...      (NIE ins Repo schreiben!)

Video-Stimme erzeugen:   python3 scripts/voice_gemini.py
Andere Stimme:           python3 scripts/voice_gemini.py --voice Algenib
Hörproben mehrerer Stimmen:
                         python3 scripts/voice_gemini.py --samples Charon Algenib Orus Sadaltager
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "src" / "train" / "script.json"
OUT = ROOT / "public" / "train"
TIMING = ROOT / "src" / "train" / "timing.json"
MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
# Free Tier: ca. 10 Anfragen/Tag pro Modell. Ausweichen z. B. mit
#   GEMINI_TTS_MODEL=gemini-3.1-flash-tts-preview
PAUSE = 0.25

# Hinweis: Dieses Modell liest Stil-Anweisungen im Text mit vor, darum KEINE Anweisung,
# die Tiefe/Stimmung kommt allein von der gewählten Stimme.


def tts(text: str, voice: str) -> bytes:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("❌ GEMINI_API_KEY fehlt (https://aistudio.google.com/apikey)")
    body = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
        },
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.load(r)
            part = data["candidates"][0]["content"]["parts"][0]["inlineData"]
            return base64.b64decode(part["data"])  # WAV (oder rohes PCM 16 bit, 24 kHz)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")[:300]
            if e.code in (429, 500, 503) and attempt < 4:
                wait = 20 * (attempt + 1)
                print(f"   … Limit/Fehler {e.code}, warte {wait}s")
                time.sleep(wait)
                continue
            sys.exit(f"❌ Gemini-Fehler {e.code}: {msg}")
    raise RuntimeError("unreachable")


def write_wav(path: Path, pcm: bytes, rate: int = 24000) -> float:
    if pcm[:4] == b"RIFF":
        path.write_bytes(pcm)
        return 0.0
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return len(pcm) / 2 / rate


def trim(path: Path) -> float:
    """Stille am Anfang/Ende abschneiden, Lautstärke angleichen."""
    tmp = path.with_suffix(".tmp.wav")
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-i", str(path), "-af",
         "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
         "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
         "adelay=80,apad=pad_dur=0.08,loudnorm=I=-16:TP=-1.5", "-ar", "48000", str(tmp)],
        check=True,
    )
    tmp.replace(path)
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(out)


def sentences():
    return json.loads(SCRIPT.read_text(encoding="utf-8"))["sentences"]


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(out)


def narrate(voice: str, target: Path) -> None:
    """Ganzer Text in EINER Anfrage (spart Kontingent, klingt zusammenhängender)."""
    text = "\n\n".join(s["text"].replace("*", "") for s in sentences())
    write_wav(target, tts(text, voice))


def split(full: Path, n: int) -> list[Path]:
    """An den n-1 längsten Pausen in Sätze schneiden."""
    log = subprocess.run(
        ["ffmpeg", "-i", str(full), "-af", "silencedetect=n=-40dB:d=0.2", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    total = duration(full)
    gaps = [(e - s, (s + e) / 2) for s, e in zip(starts, ends) if s > 0.05 and e < total - 0.05]
    if len(gaps) < n - 1:
        sys.exit(f"❌ Nur {len(gaps)} Pausen gefunden, brauche {n - 1}")
    cuts = sorted(m for _, m in sorted(gaps, reverse=True)[: n - 1])
    bounds = [0.0] + cuts + [total]
    OUT.mkdir(parents=True, exist_ok=True)
    files = []
    for i in range(n):
        f = OUT / f"line-{i}.wav"
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-i", str(full), "-ss", f"{bounds[i]:.3f}",
             "-to", f"{bounds[i + 1]:.3f}", str(f)],
            check=True,
        )
        files.append(f)
    return files


def sample_path(voice: str) -> Path:
    return ROOT / "out" / "stimmproben" / f"{voice}.wav"


def samples(voices: list[str]) -> None:
    for v in voices:
        f = sample_path(v)
        f.parent.mkdir(parents=True, exist_ok=True)
        narrate(v, f)
        print(f"🎧 {f.relative_to(ROOT)} ({duration(f):.1f}s)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="Charon")
    ap.add_argument("--samples", nargs="*")
    a = ap.parse_args()
    if a.samples:
        return samples(a.samples)
    full = sample_path(a.voice)
    if not full.exists():  # Hörprobe wiederverwenden, sonst neu erzeugen
        full.parent.mkdir(parents=True, exist_ok=True)
        narrate(a.voice, full)
    sents = sentences()
    lines = []
    for i, (s, f) in enumerate(zip(sents, split(full, len(sents)))):
        dur = trim(f)
        words = s["text"].split()
        weights = [len(re.sub(r"[^\wäöüÄÖÜß]", "", w)) + 2 + (4 if re.search(r"[,.:!?]$", w) else 0) for w in words]
        lead, tail = 0.1, 0.12
        usable = max(0.1, dur - lead - tail)
        t, timed = lead, []
        for w, wt in zip(words, weights):
            timed.append({"word": w, "start": round(t, 3)})
            t += usable * wt / sum(weights)
        lines.append({"file": f"train/line-{i}.wav", "seconds": round(dur + PAUSE, 3), "words": timed})
        print(f"🎙️  {i + 1}: {s['text'].replace('*', '')} ({dur:.1f}s)")
    TIMING.write_text(json.dumps({"lines": lines}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"✅ Stimme '{a.voice}' fertig -> npm run render:3d")


if __name__ == "__main__":
    main()
