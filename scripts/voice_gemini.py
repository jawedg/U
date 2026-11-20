#!/usr/bin/env python3
"""Natürliche KI-Erzählstimme mit Google Gemini TTS (kostenloser API-Schlüssel).

Schlüssel holen: https://aistudio.google.com/apikey
Dann:  export GEMINI_API_KEY=...      (NIE ins Repo schreiben!)

Video-Stimme erzeugen:   python3 scripts/voice_gemini.py --project athan
Andere Stimme:           python3 scripts/voice_gemini.py --project athan --voice Algenib
Hörproben:               python3 scripts/voice_gemini.py --samples Charon Algenib Orus

Hinweise:
- Das Modell liest Stil-Anweisungen im Text MIT VOR -> nur reinen Text schicken.
- Free Tier: ca. 10 Anfragen/Tag pro Modell. Darum wird der GANZE Text in EINER Anfrage
  erzeugt und danach an den Pausen in Sätze/Szenen geschnitten.
  Anderes Modell: GEMINI_TTS_MODEL=gemini-3.1-flash-tts-preview
- Die Erzählung wird in out/stimmproben/<projekt>-<stimme>.wav gespeichert und wiederverwendet.
  Nach Textänderung: --neu angeben.
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
MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
# Ist das Tageslimit erreicht, wird automatisch das nächste Modell genommen (eigenes Limit, gleiche Stimme).
FALLBACKS = ["gemini-3.8-flash-tts", "gemini-3.1-flash-tts-preview"]
PAUSE = 0.3  # Sekunden Pause nach jeder Szene
ALIGN = False  # Schnittpunkte per Gemini-Transkription bestimmen (genauer bei langen Blöcken)


def tts(text: str, voice: str, cfg: dict | None = None) -> bytes:
    global MODEL
    if cfg:  # Block mit Regie-Anweisungen / mehreren Sprechern: festes Modell, kein Ausweichen (anderer Klang)
        try:
            return _tts(text, voice, cfg)
        except DayLimit:
            sys.exit(f"❌ Tageslimit für {cfg['model']} erreicht. Morgen wieder (oder anderes Modell in voiceParts).")
    while True:
        try:
            return _tts(text, voice)
        except DayLimit:
            rest = [m for m in FALLBACKS if m != MODEL and m not in _used]
            _used.add(MODEL)
            if not rest:
                sys.exit("❌ Tageslimit bei allen Gemini-Stimmenmodellen erreicht. Morgen wieder.")
            print(f"   ⚠️  Tageslimit für {MODEL} erreicht – wechsle auf {rest[0]}")
            MODEL = rest[0]


class DayLimit(Exception):
    pass


_used: set[str] = set()


def _tts(text: str, voice: str, cfg: dict | None = None) -> bytes:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("❌ GEMINI_API_KEY fehlt (https://aistudio.google.com/apikey)")
    speech = {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}
    if cfg and len(cfg["speakers"]) > 1:
        speech = {"multiSpeakerVoiceConfig": {"speakerVoiceConfigs": [
            {"speaker": k, "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": v}}} for k, v in cfg["speakers"].items()]}}
    body = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": speech},
    }
    model = cfg["model"] if cfg else MODEL
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.load(r)
            part = data["candidates"][0]["content"]["parts"][0]["inlineData"]
            return base64.b64decode(part["data"])
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")
            if "per day" in msg or "PerDay" in msg:
                raise DayLimit()
            if e.code in (429, 500, 503) and attempt < 4:
                wait = 20 * (attempt + 1)
                print(f"   … Limit/Fehler {e.code}, warte {wait}s")
                time.sleep(wait)
                continue
            sys.exit(f"❌ Gemini-Fehler {e.code}: {msg[:400]}")
    raise RuntimeError("unreachable")


def save_audio(path: Path, data: bytes, rate: int = 24000) -> None:
    if data[:4] == b"RIFF":  # Gemini liefert meist schon WAV
        path.write_bytes(data)
        return
    with wave.open(str(path), "wb") as w:  # sonst rohes PCM 16 bit mono
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data)


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(out)


def clean(path: Path, extra: str = "") -> float:
    """Stille am Anfang/Ende abschneiden, (optional Stimm-Filter), Lautstärke angleichen."""
    tmp = path.with_suffix(".tmp.wav")
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-i", str(path), "-af",
         "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
         "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
         f"adelay=80,apad=pad_dur=0.08,{extra + ',' if extra else ''}loudnorm=I=-16:TP=-1.5", "-ar", "48000", str(tmp)],
        check=True,
    )
    tmp.replace(path)
    return duration(path)


def spoken(s: dict) -> str:
    return s.get("say", s["text"]).replace("*", "")


def split(full: Path, texts: list[str], out_dir: Path, prefix: str = "", align: bool = False) -> list[Path]:
    """Schnittpunkte: erwartete Position (nach Textlänge) -> nächste echte Sprechpause."""
    n = len(texts)
    log = subprocess.run(
        ["ffmpeg", "-i", str(full), "-af", "silencedetect=n=-40dB:d=0.18", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    total = duration(full)
    gaps = [(s, e) for s, e in zip(starts, ends) if s > 0.05 and e < total - 0.05]
    speech_start = ends[0] if starts and starts[0] <= 0.05 else 0.0
    speech_end = starts[-1] if len(starts) > len(ends) or (starts and starts[-1] > ends[-1]) else total
    weights = [len(t) + 12 for t in texts]  # +12 ~ Pause zwischen Szenen
    import hashlib
    cache = full.with_suffix(".cuts.json")
    sig = hashlib.sha1(("\n".join(texts) + str(total)).encode()).hexdigest()
    cuts = None
    if cache.exists():
        c = json.loads(cache.read_text())
        if c.get("sig") == sig:
            cuts = c["cuts"]
            print("   ✓ Schnitte aus Cache")
    if cuts is None and align and n > 2:  # Transkript-Abgleich zuerst (Erzählung mit Dialogen: Pausen ungleichmäßig)
        cuts = beep_align(full, texts, gaps, total)
        if cuts:
            cache.write_text(json.dumps({"sig": sig, "cuts": cuts}))
            print("   ✓ Schnitte per Transkript-Abgleich")
    if cuts is None and n > 2:
        cuts = local_align(full, texts, gaps, total)
        if cuts:
            cache.write_text(json.dumps({"sig": sig, "cuts": cuts}))
            print("   ✓ Schnitte per lokaler Spracherkennung (Whisper)")
    if cuts is None and n > 2:
        cuts = dp_cuts(texts, gaps, speech_start, speech_end)
        if cuts:
            print("   ✓ Schnitte per Tempo-Optimierung")
    if cuts is None and ALIGN and n > 2:
        cuts = align_cuts(full, texts, gaps, total)
        if cuts:
            cache.write_text(json.dumps({"sig": sig, "cuts": cuts}))
            print("   ✓ Schnitte per Transkript-Abgleich")
    if cuts is None:
        if n > 2:
            print("   ⚠️  Abgleich fehlgeschlagen – schätze nach Textlänge")
        cuts, used, acc = [], set(), 0
        for i in range(n - 1):
            acc += weights[i]
            expected = speech_start + (speech_end - speech_start) * acc / sum(weights)
            best, best_score = None, 1e9
            for k, (s, e) in enumerate(gaps):
                if k in used or (cuts and (s + e) / 2 <= cuts[-1]):
                    continue
                score = abs((s + e) / 2 - expected) - 6 * (e - s)
                if score < best_score:
                    best, best_score = k, score
            if best is None:
                sys.exit("❌ Konnte die Erzählung nicht sauber in Szenen schneiden.")
            used.add(best)
            cuts.append(sum(gaps[best]) / 2)
    bounds = [0.0] + cuts + [total]
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for i in range(n):
        f = out_dir / f"line-{prefix}{i}.wav"
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-i", str(full), "-ss", f"{bounds[i]:.3f}",
             "-to", f"{bounds[i + 1]:.3f}", str(f)],
            check=True,
        )
        files.append(f)
    return files


TEXT_MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-flash-lite-latest"]


def dp_cuts(texts: list[str], gaps: list[tuple[float, float]], speech_start: float, speech_end: float) -> list[float] | None:
    """Optimale Schnitte: wählt aus allen Sprechpausen die Kombination, bei der die Länge jedes Stücks
    am besten zur Textlänge passt (gleichmäßiges Sprechtempo) – lange Pausen werden bevorzugt."""
    import math
    n = len(texts)
    chars = [len(t) for t in texts]
    rate = (speech_end - speech_start) / sum(chars)
    pts = [speech_start] + [(a + b) / 2 for a, b in gaps] + [speech_end]
    glen = [0.0] + [b - a for a, b in gaps] + [0.0]
    m = len(pts)
    INF = float("inf")
    # cost[k][j]: beste Kosten, wenn Stück k bei Punkt j endet
    best = [[INF] * m for _ in range(n + 1)]
    back = [[-1] * m for _ in range(n + 1)]
    best[0][0] = 0.0
    for k in range(1, n + 1):
        exp = chars[k - 1] * rate
        last = k == n
        for j in (range(m - 1, m) if last else range(1, m - 1)):
            for i in range(0, j):
                if best[k - 1][i] == INF:
                    continue
                d = pts[j] - pts[i] - 0.5 * (glen[i] + glen[j])
                if d <= 0.2:
                    continue
                c = best[k - 1][i] + math.log(d / exp) ** 2 * 10 - (0 if last else 2.0 * min(glen[j], 1.2))
                if c < best[k][j]:
                    best[k][j], back[k][j] = c, i
    if best[n][m - 1] == INF:
        return None
    cuts, j = [], m - 1
    for k in range(n, 0, -1):
        i = back[k][j]
        if k > 1:
            cuts.append(pts[i])
        j = i
    return sorted(cuts)


WHISPER_DIRS = [ROOT / "models" / "sherpa-onnx-whisper-base", Path("/tmp/models/sherpa-onnx-whisper-base")]
_REC = None


def whisper():
    """Lokale Spracherkennung (Whisper base über sherpa-onnx) – kostenlos, ohne Limit.
    Modell: https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-base.tar.bz2"""
    global _REC
    if _REC is None:
        d = next((x for x in WHISPER_DIRS if x.exists()), None)
        if d is None:
            return None
        import sherpa_onnx
        _REC = sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=str(d / "base-encoder.int8.onnx"), decoder=str(d / "base-decoder.int8.onnx"),
            tokens=str(d / "base-tokens.txt"), language="de", task="transcribe", num_threads=4)
    return _REC


def transcribe(path: Path, a: float = 0, b: float | None = None) -> str:
    import soundfile as sf
    rec = whisper()
    tmp = path.parent / "_asr.wav"
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", str(path), "-ss", f"{a:.3f}"]
    if b is not None:
        cmd += ["-to", f"{b:.3f}"]
    subprocess.run(cmd + ["-ar", "16000", "-ac", "1", str(tmp)], check=True)
    audio, sr = sf.read(str(tmp), dtype="float32")
    tmp.unlink()
    out = []
    for k in range(0, len(audio), sr * 28):  # Whisper: max. 30 s am Stück
        st = rec.create_stream()
        st.accept_waveform(sr, audio[k:k + sr * 28])
        rec.decode_stream(st)
        out.append(st.result.text)
    return " ".join(out)


_AUDIO: dict = {}


def quietest(path: Path, a: float, b: float) -> float:
    """Zeitpunkt mit der geringsten Lautstärke (20-ms-Fenster) zwischen a und b."""
    import numpy as np
    import soundfile as sf
    if str(path) not in _AUDIO:
        x, sr = sf.read(str(path), dtype="float32")
        if x.ndim > 1:
            x = x.mean(axis=1)
        _AUDIO[str(path)] = (x, sr)
    x, sr = _AUDIO[str(path)]
    win = int(0.02 * sr)
    i0, i1 = max(0, int(a * sr)), min(len(x) - win, int(b * sr))
    best, bt = 1e9, (a + b) / 2
    for i in range(i0, i1, win // 2):
        e = float(np.sqrt(np.mean(x[i:i + win] ** 2)))
        if e < best:
            best, bt = e, (i + win / 2) / sr
    return bt


def local_align(full: Path, texts: list[str], gaps: list[tuple[float, float]], total: float) -> list[float] | None:
    """Jede Phrase zwischen zwei Sprechpausen lokal transkribieren und Wort für Wort mit dem Skript abgleichen."""
    import difflib
    if whisper() is None:
        return None
    bounds = [0.0]
    for a_, b_ in gaps:
        mid = (a_ + b_) / 2
        if mid - bounds[-1] >= 0.4:  # sehr kurze Phrasen mit der nächsten zusammenlegen
            bounds.append(mid)
    bounds.append(total)
    t_words, t_chunk, t_first = [], [], []
    for i in range(len(bounds) - 1):
        ws = _norm(transcribe(full, bounds[i], bounds[i + 1]))
        for k, w in enumerate(ws):
            t_words.append(w)
            t_chunk.append(i)
            t_first.append(k == 0)
    s_words, scene_first = [], []
    for t in texts:
        scene_first.append(len(s_words))
        s_words += _norm(t)
    sm = difflib.SequenceMatcher(a=s_words, b=t_words, autojunk=False)
    m_of = {}
    for blk in sm.get_matching_blocks():
        for j in range(blk.size):
            m_of[blk.a + j] = blk.b + j
    cuts = []
    for k in range(1, len(texts)):
        idx = scene_first[k]
        cand = [(x - idx, m_of[x]) for x in range(idx, min(idx + 6, len(s_words))) if x in m_of]
        if not cand:
            return None
        off, tb = cand[0]
        # Transkript-Wort zurück auf den Szenenanfang schieben
        tb = max(0, tb - off)
        cut = bounds[t_chunk[tb]]
        if not t_first[tb]:
            # Szene beginnt mitten in einer Phrase: Position über den Wortanteil schätzen
            # und an der leisesten Stelle in der Nähe schneiden
            ci = t_chunk[tb]
            idxs = [x for x in range(len(t_chunk)) if t_chunk[x] == ci]
            pos = (tb - idxs[0]) / len(idxs)
            est = bounds[ci] + pos * (bounds[ci + 1] - bounds[ci])
            cut = quietest(full, est - 0.6, est + 0.6)
        if cuts and cut <= cuts[-1]:
            return None
        cuts.append(cut)
    return cuts


def _text_model(parts: list, timeout: int = 600) -> str | None:
    key = os.environ.get("GEMINI_API_KEY")
    body = json.dumps({"contents": [{"parts": parts}]}).encode()
    for model in TEXT_MODELS * 2:
        req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                     data=body, headers={"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:  # noqa: BLE001
            print(f"   … {model}: {e}")
            time.sleep(8)
    return None


def _norm(txt: str) -> list[str]:
    return re.sub(r"[^a-zäöüß0-9 ]", " ", txt.lower().replace("ß", "ss")).split()


def _beep_join(pieces: list[Path], out: Path) -> None:
    """Hängt Audiostücke aneinander, dazwischen je ein kurzer Piepton (Trennzeichen für die Transkription)."""
    import numpy as np
    sr = 16000
    t = np.arange(int(0.35 * sr)) / sr
    beep = np.concatenate([np.zeros(int(0.5 * sr)), 0.6 * np.sin(2 * np.pi * 1000 * t) * np.hanning(len(t)), np.zeros(int(0.5 * sr))])
    xs = []
    for k, f in enumerate(pieces):
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(f), "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                             capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.int16).astype(float) / 32768
        xs.append(x / max(1e-6, np.max(np.abs(x))) * 0.8)
        if k < len(pieces) - 1:
            xs.append(beep)
    y = np.concatenate(xs)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "s16le", "-ar", str(sr), "-ac", "1", "-i", "-", "-b:a", "48k", str(out)],
                   input=(y * 32767).astype(np.int16).tobytes(), check=True)


def beep_transcribe(pieces: list[Path]) -> list[str] | None:
    """Transkribiert viele Stücke in EINER Anfrage zuverlässig in der richtigen Reihenfolge:
    alle Stücke in einer Aufnahme, getrennt durch Pieptöne; das Modell schreibt '###' für jeden Piepton."""
    tmp = pieces[0].parent / "_beep.mp3"
    _beep_join(pieces, tmp)
    parts = [{"inlineData": {"mimeType": "audio/mp3", "data": base64.b64encode(tmp.read_bytes()).decode()}},
             {"text": f"Deutsche Sprachaufnahme. Sie enthält genau {len(pieces) - 1} kurze Pieptöne, die Abschnitte trennen. "
                      "Transkribiere wortwörtlich in EINER Zeile und setze '###' NUR dort, wo ein Piepton zu hören ist – "
                      "NICHT bei Satzenden, Pausen oder Sprecherwechseln. "
                      f"Die Antwort muss also genau {len(pieces) - 1}-mal '###' enthalten. Zahlen als Ziffern. Nur das Transkript."}]
    tmp.unlink()
    for _ in range(2):
        out = _text_model(parts)
        if not out:
            return None
        segs = [x.strip() for x in out.split("###")]
        if len(segs) == len(pieces):
            return segs
        print(f"   … Transkript hat {len(segs)} statt {len(pieces)} Abschnitte, nochmal")
    return None


def beep_align(full: Path, texts: list[str], gaps: list[tuple[float, float]], total: float) -> list[float] | None:
    """Schnitte an echten Sprechpausen: Aufnahme an allen Pausen zerlegen, Stücke per Piepton-Transkript
    erkennen, Wörter mit dem Skript abgleichen. Jede Satzgrenze muss auf eine Pause fallen."""
    import difflib
    bounds = [0.0] + [(a_ + b_) / 2 for a_, b_ in gaps] + [total]
    tmp = full.parent / "_chunks"
    tmp.mkdir(exist_ok=True)
    pieces = []
    for i in range(len(bounds) - 1):
        f = tmp / f"c{i:03d}.wav"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(full), "-ss", f"{bounds[i]:.3f}", "-to", f"{bounds[i + 1]:.3f}", str(f)],
                       check=True)
        pieces.append(f)
    segs = beep_transcribe(pieces)
    for f in pieces:
        f.unlink()
    tmp.rmdir()
    if not segs:
        return None
    t_words, t_chunk = [], []
    for i, seg in enumerate(segs):
        for w in _norm(seg):
            t_words.append(w)
            t_chunk.append(i)
    s_words, first = [], []
    for t in texts:
        first.append(len(s_words))
        s_words += _norm(t)
    sm = difflib.SequenceMatcher(a=s_words, b=t_words, autojunk=False)
    m_of = {}
    for blk in sm.get_matching_blocks():
        for j in range(blk.size):
            m_of[blk.a + j] = blk.b + j
    cuts = []
    for k in range(1, len(texts)):
        a0 = first[k]
        tb = next((m_of[x] - (x - a0) for x in range(a0, min(a0 + 5, len(s_words))) if x in m_of), None)
        prev = next((m_of[x] for x in range(a0 - 1, max(-1, a0 - 6), -1) if x in m_of), None)
        if tb is None or prev is None:
            return None
        ci = t_chunk[max(0, min(len(t_chunk) - 1, tb))]
        if t_chunk[prev] >= ci:  # Satzgrenze liegt nicht auf einer Pause
            print(f"   … Satz {k + 1} beginnt mitten in einem Stück")
            return None
        cuts.append(bounds[ci])
    return cuts


def align_cuts(full: Path, texts: list[str], gaps: list[tuple[float, float]], total: float) -> list[float] | None:
    """Schneidet an echten Sprechpausen: jede Phrase zwischen zwei Pausen wird von Gemini transkribiert,
    das Transkript wird Wort für Wort mit dem Skript abgeglichen."""
    import difflib
    bounds = [0.0] + [(s + e) / 2 for s, e in gaps] + [total]
    chunks = [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]
    tmp = full.parent / "_chunks"
    tmp.mkdir(exist_ok=True)
    parts = []
    for i, (a, b) in enumerate(chunks):
        f = tmp / f"c{i}.mp3"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(full), "-ss", f"{a:.3f}", "-to", f"{b:.3f}",
                        "-ac", "1", "-b:a", "40k", str(f)], check=True)
        parts += [{"text": f"Audio {i + 1}:"}, {"inlineData": {"mimeType": "audio/mp3", "data": base64.b64encode(f.read_bytes()).decode()}}]
        f.unlink()
    tmp.rmdir()
    parts.append({"text": f"Es sind {len(chunks)} kurze Audios einer deutschen Aufnahme. Transkribiere JEDES wortwörtlich. "
                          "Zahlen als Wörter. Format: eine Zeile pro Audio: 'N | Text'. Ist ein Audio still, schreibe 'N | -'."})
    out = _text_model(parts)
    if not out:
        return None
    trans: dict[int, list[str]] = {}
    for line in out.splitlines():
        m = re.match(r"\s*(\d+)\s*\|(.*)", line)
        if m:
            trans[int(m.group(1)) - 1] = _norm(m.group(2))
    t_words, t_chunk = [], []
    for i in range(len(chunks)):
        for w in trans.get(i, []):
            t_words.append(w)
            t_chunk.append(i)
    s_words, scene_first = [], []
    for k, t in enumerate(texts):
        scene_first.append(len(s_words))
        s_words += _norm(t)
    sm = difflib.SequenceMatcher(a=s_words, b=t_words, autojunk=False)
    m_of = {}
    for blk in sm.get_matching_blocks():
        for j in range(blk.size):
            m_of[blk.a + j] = blk.b + j
    cuts = []
    for k in range(1, len(texts)):
        idx = scene_first[k]
        # erstes zugeordnetes Wort ab Szenenanfang (max. 6 Wörter weiter suchen)
        tb = next((m_of[x] for x in range(idx, min(idx + 6, len(s_words))) if x in m_of), None)
        if tb is None:
            return None
        ci = t_chunk[tb]
        cut = bounds[ci]
        if cuts and cut <= cuts[-1]:
            return None
        cuts.append(cut)
    return cuts


def word_times(text: str, dur: float) -> list[dict]:
    words = text.split()
    weights = [len(re.sub(r"[^\wäöüÄÖÜß]", "", w)) + 2 + (5 if re.search(r"[,.:!?]$", w) else 0)
               for w in words]
    lead, tail = 0.1, 0.15
    usable = max(0.1, dur - lead - tail)
    t, timed = lead, []
    for w, wt in zip(words, weights):
        timed.append({"word": w, "start": round(t, 3)})
        t += usable * wt / sum(weights)
    return timed


def tighten(path: Path, max_pause: float = 0.38, tempo: float = 1.0, dots: bool = False) -> None:
    """Lange Sprechpausen im Stück kürzen (spannender, flotter) und optional leicht schneller (Tonhöhe bleibt).
    Bei '...' im Text darf die längste Pause etwas länger bleiben (dramatische Pause)."""
    import wave
    import numpy as np
    with wave.open(str(path)) as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch).astype(float)
    hop = int(0.01 * sr)
    n = len(x) // hop
    rms = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) for i in range(n)]) + 1e-9
    db = 20 * np.log10(rms / (rms.max()))
    quiet = db < -38
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if i > 0 and j < n:  # nur Pausen IM Stück (Rand macht clean())
                runs.append((i * hop, j * hop))
            i = j
        else:
            i += 1
    long_run = max(runs, key=lambda r: r[1] - r[0]) if runs else None
    keep, last, xf = [], 0, int(0.012 * sr)
    for a, b in runs:
        lim = int((0.62 if dots and (a, b) == long_run else max_pause) * sr)
        if b - a <= lim:
            continue
        h = lim // 2
        keep.append(x[last:a + h])
        last = b - h
    keep.append(x[last:])
    y = keep[0]
    for k in keep[1:]:  # kurze Überblendung gegen Knackser
        r = np.linspace(0, 1, xf)[:, None]
        y = np.concatenate([y[:-xf], y[-xf:] * (1 - r) + k[:xf] * r, k[xf:]])
    with wave.open(str(path), "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(sw)
        w.setframerate(sr)
        w.writeframes(np.clip(y, -32768, 32767).astype(np.int16).tobytes())
    if abs(tempo - 1.0) > 1e-3:
        tmp = path.with_suffix(".tempo.wav")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(path), "-af", f"atempo={tempo}", str(tmp)], check=True)
        tmp.replace(path)




def _speech_span(path: Path) -> tuple[float, float]:
    """(Beginn, Ende) der Sprache in einer Datei in Sekunden (alles über -45 dB unter dem Maximum)."""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float) / 32768
    hop = 160
    n = len(x) // hop
    if n < 3:
        return 0.0, len(x) / 16000
    rms = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) for i in range(n)]) + 1e-9
    on = np.where(20 * np.log10(rms / rms.max()) > -45)[0]
    if not len(on):
        return 0.0, len(x) / 16000
    return on[0] * 0.01, (on[-1] + 1) * 0.01

TAG = re.compile(r"\[[^\]]*\]")  # ElevenLabs-v3-Regie in eckigen Klammern, z. B. [whispers] – wird nicht gesprochen


def eleven_tts(text: str, voice: str, model: str, settings: dict | None, cache_dir: Path) -> tuple[Path, dict]:
    """ElevenLabs-Sprachausgabe MIT Zeit je Buchstabe (für exakte Schnitte + Untertitel). Ergebnis wird zwischengespeichert
    (gleicher Text/Stimme/Modell = keine neue Anfrage, keine Credits). Schlüssel: Network Secret für api.elevenlabs.io."""
    import hashlib
    sig = hashlib.sha1(json.dumps([text, voice, model, settings], ensure_ascii=False).encode()).hexdigest()[:16]
    mp3, js = cache_dir / f"eleven-{sig}.mp3", cache_dir / f"eleven-{sig}.json"
    if mp3.exists() and js.exists():
        return mp3, json.loads(js.read_text())
    body = {"text": text, "model_id": model}
    if settings:
        body["voice_settings"] = settings
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_192",
                                 data=json.dumps(body).encode(),
                                 headers={"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "proxy-injected"),
                                          "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.load(r)
            break
        except urllib.error.HTTPError as e:
            msg = e.read()[:300]
            if e.code in (429, 500, 502, 503) and attempt < 3:
                print(f"   … ElevenLabs {e.code}, warte …")
                time.sleep(20 * (attempt + 1))
                continue
            sys.exit(f"❌ ElevenLabs {e.code}: {msg}")
    mp3.write_bytes(base64.b64decode(d["audio_base64"]))
    js.write_text(json.dumps(d["alignment"]))
    return mp3, d["alignment"]


def eleven_block(block: list, pc: dict, out_dir: Path, part: int, cache_dir: Path, groups: list[list[int]]) -> tuple[list[Path], list]:
    """Erzähler per ElevenLabs (Nutzer: Gemini klang roboterhaft): je Szene EINE Anfrage (Feld "el" = Text mit Regie-Tags),
    exakte Satzgrenzen aus den Buchstaben-Zeiten, Ränder max. `edge` s Stille, Wortzeiten für die Untertitel.
    Rückgabe: Dateien (eine je Satz, in Reihenfolge von block) + Wortlisten."""
    files, words_all = [], []
    edge = float(pc.get("edge", 0.3))
    voice = next(iter(pc["speakers"].values()))
    for k, g in enumerate(groups):
        texts = [block[j].get("el") or spoken(block[j]) for j in g]
        joined, offs = "", []
        for t in texts:
            if joined:
                joined += " "
            offs.append((len(joined), len(joined) + len(t)))
            joined += t
        print(f"🎙️  ElevenLabs Block {part}, Szene {k + 1}/{len(groups)} ({len(joined)} Zeichen, {pc['model']}) …", flush=True)
        mp3, al = eleven_tts(joined, voice, pc["model"], pc.get("settings"), cache_dir)
        ch, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
        if len(ch) != len(joined):
            sys.exit(f"❌ Zeiten passen nicht zum Text ({len(ch)} statt {len(joined)} Zeichen)")
        spoken_mask = [True] * len(joined)
        for m in TAG.finditer(joined):
            for i in range(m.start(), m.end()):
                spoken_mask[i] = False
        wav = mp3.with_suffix(".proc.wav")
        flt = pc.get("filter", "highpass=f=60")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), "-af",
                        f"{flt + ',' if flt else ''}loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "1", str(wav)], check=True)
        total = duration(wav)
        spans = []  # (erster gesprochener Buchstabe Beginn, letzter Ende) je Satz
        for a, b in offs:
            idx = [i for i in range(a, b) if spoken_mask[i] and not ch[i].isspace()]
            spans.append((st[idx[0]], en[idx[-1]]))
        # Schnitte an ECHTE Pausen legen: nach einem Regie-Tag kommen die Buchstaben-Zeiten oft ~0,3 s zu spät
        # (sonst fehlt z. B. das „M“ von „Medina“). Je Satzgrenze die längste Stille im Bereich der Grenze nehmen.
        log = subprocess.run(["ffmpeg", "-i", str(wav), "-af", "silencedetect=n=-40dB:d=0.12", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
        sil = list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)],
                       [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]))
        lead = next((e for s_, e in sil if s_ <= 0.05), 0.0)  # Stille ganz am Anfang
        trail = next((s_ for s_, e in sil if e >= total - 0.05), total)  # Stille ganz am Ende
        cut_end, cut_start = {}, {}
        latest = pc.get("cutmode") == "latest"
        for n in range(len(spans) - 1):
            a_end, b_start = spans[n][1], spans[n + 1][0]
            cand = [(s_, e) for s_, e in sil if e > a_end - 0.6 and s_ < b_start + 0.6 and s_ > 0.05 and e < total - 0.05]
            if latest:
                # Folge 2: nach „… [whispers] niemand.“ lag die längste Stille VOR dem letzten Wort -> das Wort landete im
                # nächsten Stück. Daher: die LETZTE Stille vor dem Beginn des nächsten Satzes, die nach dem Beginn des
                # letzten Wortes dieses Satzes anfängt (Buchstaben-Zeiten nach Tags sind ~0,3 s zu spät -> Spielraum).
                a_, b_ = offs[n]
                lw_n = max((m.start() + a_ for m in re.finditer(r"\w+", joined[a_:b_]) if spoken_mask[m.start() + a_]), default=a_)
                c2 = [(s_, e) for s_, e in sil if s_ >= st[lw_n] - 0.25 and e <= b_start + 0.45 and s_ > 0.05 and e < total - 0.05]
                if c2:
                    cand = [max(c2, key=lambda x: x[1])]
            if cand:
                s_, e = max(cand, key=lambda x: x[1] - x[0])
                mid = (s_ + e) / 2
                cut_end[n], cut_start[n + 1] = min(s_ + edge, mid), max(e - edge, mid)
            else:
                mid = (a_end + b_start) / 2
                cut_end[n], cut_start[n + 1] = mid, mid
        # Szenen-Ende: ElevenLabs schneidet hart nach dem letzten Laut ab -> im Text endet die Szene mit " ..." (Ausklang);
        # geschnitten wird an der ersten echten Stille nach dem letzten Wort (kein Atmer/Klicken danach)
        la, lb = offs[-1]
        lw = max((m.start() + la for m in re.finditer(r"\w+", joined[la:lb]) if spoken_mask[m.start() + la]), default=la)
        after = [(s_, e) for s_, e in sil if s_ >= st[lw]]
        if after:
            trail = after[0][0]
        import numpy as np
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(wav), "-ac", "1", "-f", "s16le", "-"], capture_output=True,
                             check=True).stdout
        xs = np.frombuffer(raw, np.int16).astype(float) / 32768

        def loud(t0_, t1_):  # Pegel (dB) im Bereich – liegt ein Schnitt in einem Atmer, wird weicher ein-/ausgeblendet
            seg_ = xs[int(max(0, t0_) * 48000):int(max(0, t1_) * 48000)]
            return 20 * np.log10(np.sqrt(np.mean(seg_ ** 2)) + 1e-9) if len(seg_) else -120
        for n, (j, (a, b), (s0, s1)) in enumerate(zip(g, offs, spans)):
            c0 = cut_start.get(n, max(0.0, lead - edge))
            c1 = cut_end.get(n, min(total, trail + edge))
            f = out_dir / f"line-{part}-{len(files)}.wav"
            fi = 0.12 if loud(c0, c0 + 0.06) > -45 else 0.006
            fo = 0.15 if loud(c1 - 0.06, c1) > -45 else (0.05 if n == len(spans) - 1 else 0.012)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{c0:.4f}", "-t", f"{c1 - c0:.4f}", "-i", str(wav), "-af",
                            f"afade=t=in:d={fi},areverse,afade=t=in:d={fo},areverse", str(f)], check=True)
            files.append(f)
            # Wortzeiten: gesprochene Wörter (ohne Tags) aus den Buchstaben-Zeiten, dann auf die Untertitel-Wörter abbilden
            sp = []  # (Beginn, Text) je gesprochenem Wort
            i = a
            while i < b:
                if spoken_mask[i] and not ch[i].isspace():
                    w0 = i
                    while i < b and spoken_mask[i] and not ch[i].isspace():
                        i += 1
                    t_w = st[w0]
                    if pc.get("snap"):  # Wortbeginn kurz nach einer Pause -> auf das Ende der Pause (Zeiten nach Tags zu spät)
                        hit = [e for s_, e in sil if s_ - 0.05 < t_w < e + 0.45]
                        if hit:
                            t_w = min(t_w, hit[-1] + 0.02)
                    sp.append((min(t_w, c1 - 0.3) - c0, joined[w0:i]))
                else:
                    i += 1
            disp = block[j]["text"].split()
            if len(disp) == len(sp):
                ws = [{"word": w, "start": round(max(0.0, t), 3)} for w, (t, _) in zip(disp, sp)]
            else:  # andere Wortzahl (z. B. arabischer Name): nach Position im Satz abbilden
                tot_d = sum(len(w) + 1 for w in disp)
                ws, pos = [], 0
                for w in disp:
                    r = pos / tot_d
                    ws.append({"word": w, "start": round(max(0.0, sp[min(len(sp) - 1, int(r * len(sp)))][0]), 3)})
                    pos += len(w) + 1
            words_all.append(ws)
    return files, words_all


def word_times_audio(path: Path, text: str, dur: float) -> list[dict]:
    """Wortzeiten nach dem echten Ton (statt gleichmäßig verteilt – da liefen die Untertitel nach Pausen voraus):
    1) Sprechpausen im Stück finden, 2) Satzgrenzen (. ! ? : …) auf die passendsten Pausen legen,
    3) innerhalb eines Satzes läuft die Wort-Uhr nur, während gesprochen wird."""
    import numpy as np
    try:
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                             capture_output=True, check=True).stdout
    except subprocess.CalledProcessError:
        return word_times(text, dur)
    x = np.frombuffer(raw, np.int16).astype(float) / 32768
    hop = 160  # 10 ms
    n = len(x) // hop
    words = text.split()
    if n < 10 or not words:
        return word_times(text, dur)
    rms = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) for i in range(n)]) + 1e-9
    sp = 20 * np.log10(rms / rms.max()) > -34
    k = 0
    while k < n:  # kurze Lücken (< 120 ms, z. B. Verschlusslaute) zählen als Sprechen
        if not sp[k]:
            j = k
            while j < n and not sp[j]:
                j += 1
            if j - k < 12 and k > 0 and j < n:
                sp[k:j] = True
            k = j
        else:
            k += 1
    if sp.sum() < 20:
        return word_times(text, dur)
    first = int(np.argmax(sp))
    last = n - int(np.argmax(sp[::-1]))
    pauses, k = [], first
    while k < last:  # (Anfang, Ende) in s, nur innerhalb der Sprache
        if not sp[k]:
            j = k
            while j < last and not sp[j]:
                j += 1
            if j - k >= 15:
                pauses.append((k * 0.01, j * 0.01))
            k = j
        else:
            k += 1
    cum = np.cumsum(sp) * 0.01

    def at_speech(frac, lo, hi):  # Zeit in [lo, hi], bei der der Anteil frac der Sprechzeit erreicht ist
        c0, c1 = cum[min(n - 1, int(lo * 100))], cum[min(n - 1, max(0, int(hi * 100) - 1))]
        i = int(np.searchsorted(cum, c0 + frac * (c1 - c0) + 1e-6))
        return min(max(i * 0.01, lo), hi)
    # Gewicht ~ Sprechlänge; Zahlen werden lang gesprochen („622“ = sechshundertzweiundzwanzig)
    weights = [4 * len(re.sub(r"\D", "", w)) + 2 if re.search(r"\d", w) else len(re.sub(r"[^\wäöüÄÖÜß]", "", w)) + 2
               for w in words]
    ends = [i for i, w in enumerate(words[:-1]) if re.search(r"[.!?:…]\*?[“\"]?$", w)]  # Satzende nach Wort i
    t_start, t_end = first * 0.01, last * 0.01
    bounds, used = [], -1
    for i in ends:
        exp = at_speech(sum(weights[:i + 1]) / sum(weights), t_start, t_end)
        cand = [(abs((p0 + p1) / 2 - exp) - 1.0 * (p1 - p0), m) for m, (p0, p1) in enumerate(pauses)
                if m > used and abs((p0 + p1) / 2 - exp) < 2.0]
        if cand:
            m = min(cand)[1]
            used = m
            bounds.append((i, pauses[m][0], pauses[m][1]))
    out, w0, s0 = [], 0, t_start
    for i, p0, p1 in bounds + [(len(words) - 1, t_end, t_end)]:
        seg = list(range(w0, i + 1))
        tot = sum(weights[j] for j in seg) or 1
        acc = 0
        for j in seg:
            t = at_speech(acc / tot, s0, p0)
            out.append({"word": words[j], "start": round(max(0.0, t - 0.04), 3)})
            acc += weights[j]
        w0, s0 = i + 1, p1
    for q in range(1, len(out)):  # streng steigend
        if out[q]["start"] <= out[q - 1]["start"]:
            out[q]["start"] = round(out[q - 1]["start"] + 0.05, 3)
    return out

HALL_TAIL = 2.4  # Sekunden Nachhall nach dem Zitat


def hall(path: Path, sec: float = 2.8, wet: float = 0.55) -> None:
    """Zitat-Stimme mit großem Hall (Faltung mit künstlichem Raum, stereo); Datei wird um den Nachhall länger."""
    import numpy as np
    with wave.open(str(path)) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    rng = np.random.default_rng(1)
    n = int(sec * sr)
    t = np.arange(n) / sr
    pre = np.zeros(int(0.04 * sr))
    out = []
    for _ in range(2):
        ir = rng.standard_normal(n) * np.exp(-t / (sec / 6.9)) * (1 - np.exp(-t / 0.01))
        spec = np.fft.rfft(ir)
        f = np.fft.rfftfreq(n, 1 / sr)
        spec *= (f > 150) * (1 / (1 + (f / 5000) ** 4))  # Hall ohne Dröhnen/Zischen
        ir = np.concatenate([pre, np.fft.irfft(spec, n)])
        ir /= np.sqrt(np.sum(ir ** 2))
        L = len(x) + len(ir)
        out.append(np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L))
    w = np.stack(out, 1)
    keep = len(x) + int(HALL_TAIL * sr)
    w = w[:keep]
    dry = np.zeros_like(w)
    dry[: len(x)] = x[:, None]
    y = dry * (1 - wet * 0.4) + w * wet * 1.2
    y *= 0.89 / max(1e-9, np.max(np.abs(y)))
    fade = int(0.4 * sr)
    y[-fade:] *= np.linspace(1, 0, fade)[:, None]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((y * 32767).astype(np.int16).tobytes())


def check(files: list[Path], texts: list[str]) -> None:
    """Kontrolle: alle Stücke mit Gemini transkribieren (1 Anfrage) und mit dem Skript vergleichen."""
    import difflib
    segs = beep_transcribe(files)
    if not segs:
        print("   ⚠️  Kontrolle nicht möglich (Textmodell nicht erreichbar)")
        return
    got = dict(enumerate(segs))
    bad = 0
    for i, t in enumerate(texts):
        r = difflib.SequenceMatcher(a=_norm(t), b=_norm(got.get(i, ""))).ratio()
        if r < 0.8:
            bad += 1
            print(f"   ⚠️  Stück {i + 1} passt nicht ({r:.0%}): soll „{t}“ – ist „{got.get(i, '')}“")
    print("   ✓ Kontrolle: alle Stücke passen zum Text" if not bad else f"   ❌ Kontrolle: {bad} Stück(e) falsch geschnitten")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="train", help="Ordner unter src/ (z. B. train, athan)")
    ap.add_argument("--voice", default="Charon")  # Lieblingsstimme des Nutzers
    ap.add_argument("--samples", nargs="*")
    ap.add_argument("--neu", action="store_true", help="Erzählung neu erzeugen")
    ap.add_argument("--check", action="store_true", help="Schnitte per Gemini-Transkription kontrollieren")
    a = ap.parse_args()

    script_path = ROOT / "src" / a.project / "script.json"
    timing_path = ROOT / "src" / a.project / "timing.json"
    out_dir = ROOT / "public" / a.project
    script = json.loads(script_path.read_text(encoding="utf-8"))
    scenes = script["sentences"]
    voiced = [s for s in scenes if s.get("text")]
    samples_dir = ROOT / "out" / "stimmproben"
    samples_dir.mkdir(parents=True, exist_ok=True)

    # Lange Skripte: Szenen mit "part" werden blockweise aufgenommen (1 Anfrage pro Block)
    parts = sorted({s.get("part", 0) for s in voiced})
    multi = len(parts) > 1

    vparts = script.get("voiceParts", {})
    vfilter = script.get("voiceFilter", "")

    def chunk_groups(block: list, cfg: dict | None) -> list[list[int]]:
        """Stück-Modus: lange Erzählung in kurze Anfragen teilen (neues Stück ab den Satz-IDs in cfg["chunks"]).
        Nutzer: eine 1:35-min-Aufnahme am Stück klang roboterhaft, kurze Proben (~20 s) klangen natürlich."""
        starts = set((cfg or {}).get("chunks", []))
        groups: list[list[int]] = []
        for j, s in enumerate(block):
            if not groups or s.get("id") in starts:
                groups.append([])
            groups[-1].append(j)
        return groups

    def full_path(v: str, part: int = 0) -> Path:
        cfg = vparts.get(str(part))
        if cfg:
            k = ".k" if cfg.get("chunks") else ""
            return samples_dir / f"{a.project}-p{part}-{'+'.join(cfg['speakers'].values())}{k}.wav"
        if a.project == "train":
            return samples_dir / f"{v}.wav"
        return samples_dir / (f"{a.project}-{v}-p{part}.wav" if multi else f"{a.project}-{v}.wav")

    def narrate(v: str, part: int = 0) -> Path:
        f = full_path(v, part)
        cfg = vparts.get(str(part))
        if cfg and cfg.get("chunks"):  # Stück-Modus: jedes Stück eigene Anfrage (fertige Stücke werden wiederverwendet)
            block = [s for s in voiced if s.get("part", 0) == part]
            multi_spk = len(cfg["speakers"]) > 1
            cfiles = []
            for k, g in enumerate(chunk_groups(block, cfg)):
                cf = f.with_name(f"{f.stem}{k}.wav")
                if not cf.exists():
                    lines_ = [f"{block[j]['speaker']}: {spoken(block[j])}" if multi_spk else spoken(block[j]) for j in g]
                    text = cfg["notes"].strip() + "\n#### TRANSCRIPT\n" + ("\n" if multi_spk else "\n\n").join(lines_)
                    print(f"🎙️  Erzeuge Block {part}, Stück {k + 1} ({len(g)} Sätze, {cfg['model']}) …", flush=True)
                    save_audio(cf, tts(text, v, cfg))
                cfiles.append(cf)
            lst = f.with_suffix(".list")
            lst.write_text("".join(f"file '{c.resolve()}'\n" for c in cfiles))
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                            "-c", "copy", str(f)], check=True)
            lst.unlink()
            return f
        if a.neu or not f.exists():
            block = [s for s in voiced if s.get("part", 0) == part]
            if cfg:  # Regie-Anweisungen + Transkript („Sprecher: Text“ bei mehreren Sprechern)
                multi_spk = len(cfg["speakers"]) > 1
                lines_ = [f"{s['speaker']}: {spoken(s)}" if multi_spk else spoken(s) for s in block]
                text = cfg["notes"].strip() + "\n#### TRANSCRIPT\n" + ("\n" if multi_spk else "\n\n").join(lines_)
                if cfg.get("plain"):  # Modelle, die Anweisungen mitlesen: nur reiner Text
                    text = "\n\n".join(spoken(s) for s in block)
                print(f"🎙️  Erzeuge Block {part} mit {', '.join(f'{k}={x}' for k, x in cfg['speakers'].items())} "
                      f"({cfg['model']}, {len(block)} Sätze) …")
                save_audio(f, tts(text, v, cfg))
            else:
                print(f"🎙️  Erzeuge Erzählung mit {v} ({MODEL}), Block {part} ({len(block)} Szenen) …")
                save_audio(f, tts("\n\n".join(spoken(s) for s in block), v))
        return f

    if a.samples:
        for v in a.samples:
            print(f"🎧 {narrate(v).relative_to(ROOT)}")
        return

    # Blöcke dürfen über das Video verteilt sein (z. B. alle Sätze des Prüfers in einem Block) und eine eigene
    # Stimme haben ("voice" in der Szene). Die Stücke werden danach wieder der Szenen-Reihenfolge zugeordnet.
    fmap: dict[int, Path] = {}
    flow_files: set = set()
    el_words: dict = {}  # ElevenLabs: exakte Wortzeiten je Datei
    for part in parts:
        idxs = [i for i, s in enumerate(scenes) if s.get("text") and s.get("part", 0) == part]
        block = [scenes[i] for i in idxs]
        v = block[0].get("voice", a.voice)
        pc = vparts.get(str(part))
        if pc and len(pc["speakers"]) == 1:  # Block mit EINER Stimme: die Stimme aus voiceParts nehmen
            v = next(iter(pc["speakers"].values()))
        if pc and pc.get("engine") == "eleven":  # Erzähler per ElevenLabs (fertig geschnitten, exakte Wortzeiten)
            fs, wl = eleven_block(block, pc, out_dir, part, samples_dir, chunk_groups(block, pc))
            flow_files.update(fs)
            el_words.update(zip(fs, wl))
            fmap.update(zip(idxs, fs))
            continue
        full = narrate(v, part)
        if pc and pc.get("chunks"):  # jedes Stück einzeln schneiden (wenige Sätze -> sichere Schnitte), Stückgrenzen sind exakt
            fs = []
            for k, g in enumerate(chunk_groups(block, pc)):
                cf = full.with_name(f"{full.stem}{k}.wav")
                for p_ in split(cf, [spoken(block[j]) for j in g], out_dir, f"{part}-c{k}-", align=True):
                    dst = out_dir / f"line-{part}-{len(fs)}.wav"
                    p_.replace(dst)
                    fs.append(dst)
        else:
            fs = split(full, [spoken(s) for s in block], out_dir, f"{part}-" if multi else "", align=str(part) in vparts)
        if pc and pc.get("flow"):
            # Fluss-Modus (Nutzer: Erzähler klang „gehackt“): die Aufnahme bleibt wie gesprochen – Pausen, Atmer und
            # Lautstärke wie im Original. Ganze Aufnahme EINMAL filtern + angleichen, dann exakt an den Schnitten teilen.
            proc = full.with_suffix(".flow.wav")
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(full), "-af",
                            f"{vfilter + ',' if vfilter else ''}loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", str(proc)], check=True)
            t = 0.0
            edge = float(pc.get("edge", 0.3))  # höchstens so viel Stille vorn/hinten behalten (natürlich, aber nicht zu lang)
            for f in fs:
                d = duration(f)
                a0, a1 = _speech_span(f)
                s0 = t + max(0.0, a0 - edge)
                s1 = t + min(d, a1 + edge)
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{s0:.4f}", "-t", f"{s1 - s0:.4f}", "-i", str(proc), "-af",
                                "afade=t=in:d=0.006,areverse,afade=t=in:d=0.006,areverse", str(f.with_suffix(".tmp.wav"))], check=True)
                f.with_suffix(".tmp.wav").replace(f)
                flow_files.add(f)
                t += d
        fmap.update(zip(idxs, fs))
    lines = []
    for i, s in enumerate(scenes):
        if not s.get("text"):
            lines.append({"file": "", "seconds": float(script.get("athanSeconds", 10)), "words": []})
            continue
        f = fmap[i]
        if f in flow_files:  # schon fertig (Fluss-Modus): nicht kürzen, nicht einzeln angleichen
            dur = duration(f)
        else:
            tg = script.get("tighten")
            if tg and str(s.get("part", 0)) in tg.get("parts", {}):  # eigene Einstellung je Block (z. B. Dialoge)
                tg = tg["parts"][str(s.get("part", 0))]
            if tg and s.get("fx") != "hall":
                tighten(f, tg.get("maxPause", 0.38), tg.get("tempo", 1.0), dots="..." in s["text"])
            dur = clean(f, vfilter)
        ln = {"file": f"{a.project}/{f.name}", "seconds": round(dur + PAUSE, 3), "words": el_words.get(f) or word_times_audio(f, s["text"], dur)}
        if f in flow_files:
            ln["flow"] = s.get("part", 0)
        if s.get("fx") == "hall":
            hall(f)
            ln["tail"] = HALL_TAIL
        lines.append(ln)
        print(f"   {i + 1:2d}. ({dur:4.1f}s) {spoken(s)}")
    if vparts or a.check:  # Schnitte kontrollieren (1 Anfrage an ein Textmodell)
        idx = [i for i, s in enumerate(scenes) if s.get("text")]
        check([fmap[i] for i in idx], [spoken(scenes[i]) for i in idx])
    timing_path.write_text(json.dumps({"lines": lines}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    total = sum(l["seconds"] for l in lines)
    print(f"✅ Stimme '{a.voice}' fertig – Gesamtlänge ca. {int(total // 60)}:{int(total % 60):02d} min")


if __name__ == "__main__":
    main()
