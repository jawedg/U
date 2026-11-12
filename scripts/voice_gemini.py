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
PAUSE = 0.3  # Sekunden Pause nach jeder Szene
ALIGN = False  # Schnittpunkte per Gemini-Transkription bestimmen (genauer bei langen Blöcken)


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
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.load(r)
            part = data["candidates"][0]["content"]["parts"][0]["inlineData"]
            return base64.b64decode(part["data"])
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")
            if "per day" in msg or "PerDay" in msg:
                sys.exit(f"❌ Tageslimit für {MODEL} erreicht. Morgen wieder oder anderes Modell "
                         "(GEMINI_TTS_MODEL=gemini-3.1-flash-tts-preview).")
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


def clean(path: Path) -> float:
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
    return duration(path)


def spoken(s: dict) -> str:
    return s.get("say", s["text"]).replace("*", "")


def split(full: Path, texts: list[str], out_dir: Path, prefix: str = "") -> list[Path]:
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="train", help="Ordner unter src/ (z. B. train, athan)")
    ap.add_argument("--voice", default="Charon")  # Lieblingsstimme des Nutzers
    ap.add_argument("--samples", nargs="*")
    ap.add_argument("--neu", action="store_true", help="Erzählung neu erzeugen")
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

    def full_path(v: str, part: int = 0) -> Path:
        if a.project == "train":
            return samples_dir / f"{v}.wav"
        return samples_dir / (f"{a.project}-{v}-p{part}.wav" if multi else f"{a.project}-{v}.wav")

    def narrate(v: str, part: int = 0) -> Path:
        f = full_path(v, part)
        if a.neu or not f.exists():
            block = [s for s in voiced if s.get("part", 0) == part]
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
    for part in parts:
        idxs = [i for i, s in enumerate(scenes) if s.get("text") and s.get("part", 0) == part]
        block = [scenes[i] for i in idxs]
        v = block[0].get("voice", a.voice)
        fs = split(narrate(v, part), [spoken(s) for s in block], out_dir, f"{part}-" if multi else "")
        fmap.update(zip(idxs, fs))
    lines = []
    for i, s in enumerate(scenes):
        if not s.get("text"):
            lines.append({"file": "", "seconds": float(script.get("athanSeconds", 10)), "words": []})
            continue
        f = fmap[i]
        dur = clean(f)
        lines.append({"file": f"{a.project}/{f.name}", "seconds": round(dur + PAUSE, 3),
                      "words": word_times(s["text"], dur)})
        print(f"   {i + 1:2d}. ({dur:4.1f}s) {spoken(s)}")
    timing_path.write_text(json.dumps({"lines": lines}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    total = sum(l["seconds"] for l in lines)
    print(f"✅ Stimme '{a.voice}' fertig – Gesamtlänge ca. {int(total // 60)}:{int(total % 60):02d} min")


if __name__ == "__main__":
    main()
