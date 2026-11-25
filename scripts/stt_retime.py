#!/usr/bin/env python3
"""Untertitel-Wortzeiten aus einer Spracherkennung (ElevenLabs Speech-to-Text, Modell scribe_v1) statt aus den
Buchstaben-Zeiten der Sprachausgabe (Nutzer, Folge 5: Untertitel passten an einigen Stellen nicht zur Stimme; nach
Regie-Tags und bei arabischen Namen lagen die Zeiten bis zu 0,6 s daneben).

Ablauf: nach voice_gemini.py, vor build_qissa_*.py:
    python3 scripts/stt_retime.py --project qissa_hijra
Je Satz-Datei eine Erkennung (Ergebnis zwischengespeichert in out/stimmproben/stt-<hash>.json -> kein zweites Mal),
Wörter per Folgen-Abgleich den Untertitel-Wörtern zugeordnet; nicht erkannte Wörter (z. B. arabische Namen) werden
zwischen den Nachbarn verteilt. Schlüssel: Network Secret für api.elevenlabs.io (Header xi-api-key, "proxy-injected").
"""
import argparse
import difflib
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "out" / "stimmproben"
PAUSE = 0.3   # wie in voice_gemini.py (seconds = Dauer + PAUSE)


def norm(w: str) -> str:
    w = re.sub(r"^a[lsdnrtz]-", "", w.replace("*", ""), flags=re.I)
    return re.sub(r"[^\wäöüß]", "", w.lower())


def stt(path: Path) -> list:
    sig = hashlib.sha1(path.read_bytes()).hexdigest()[:16]
    cp = CACHE / f"stt-{sig}.json"
    if cp.exists():
        return json.loads(cp.read_text())
    for attempt in range(3):
        r = subprocess.run(["curl", "-s", "-m", "180", "-H", "xi-api-key: proxy-injected", "-F", "model_id=scribe_v1",
                            "-F", "language_code=de", "-F", "timestamps_granularity=word", "-F", f"file=@{path}",
                            "https://api.elevenlabs.io/v1/speech-to-text"], capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
            words = [{"w": w["text"], "s": round(w["start"], 3), "e": round(w["end"], 3)} for w in d["words"] if w.get("type") == "word"]
            cp.write_text(json.dumps(words, ensure_ascii=False))
            return words
        except (json.JSONDecodeError, KeyError):
            print("   … Erkennung fehlgeschlagen, nochmal:", r.stdout[:200])
    sys.exit(f"❌ Spracherkennung für {path.name} fehlgeschlagen")


def retime(disp: list, old: list, rec: list) -> tuple[list, int]:
    a = [norm(w) for w in disp]
    b = [norm(w["w"]) for w in rec]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    t = [None] * len(disp)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1):
                t[i1 + k] = rec[j1 + k]["s"]
        elif op == "replace" and i2 - i1 == j2 - j1:   # gleich viele Wörter, nur anders geschrieben (Soraka/Suraqa)
            for k in range(i2 - i1):
                t[i1 + k] = rec[j1 + k]["s"]
        elif op == "replace" and j2 > j1:   # z. B. „Abu Bakr“ -> „Abubakr“: erstes Wort bekommt den Beginn
            t[i1] = rec[j1]["s"]
    hit = sum(x is not None for x in t)
    # Lücken zwischen bekannten Nachbarn gleichmäßig füllen
    n = len(t)
    for i in range(n):
        if t[i] is None:
            lo = next((j for j in range(i - 1, -1, -1) if t[j] is not None), None)
            hi = next((j for j in range(i + 1, n) if t[j] is not None), None)
            if lo is not None and hi is not None:
                t[i] = t[lo] + (t[hi] - t[lo]) * (i - lo) / (hi - lo)
            elif lo is not None:
                t[i] = t[lo] + 0.3 * (i - lo)
            elif hi is not None:
                t[i] = max(0.0, t[hi] - 0.3 * (hi - i))
            else:
                t[i] = old[i]["start"] if i < len(old) else 0.0
    for i in range(1, n):   # streng steigend
        t[i] = max(t[i], t[i - 1] + 0.02)
    return [{"word": w, "start": round(x, 3)} for w, x in zip(disp, t)], hit


def dur(p: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout)


def move_audio(src: Path, dst: Path, t: float, to_front: bool) -> None:
    """Hängt den Teil von src ab t (to_front: an den Anfang von dst) bzw. bis t (sonst: ans Ende von dst) um."""
    tmp = src.with_suffix(".mv.wav")
    a, b = src.with_suffix(".a.wav"), src.with_suffix(".b.wav")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-t", f"{t:.3f}", "-af",
                    "areverse,afade=t=in:d=0.02,areverse", str(a)], check=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", str(src), "-af", "afade=t=in:d=0.02", str(b)], check=True)
    keep, move = (a, b) if to_front else (b, a)
    parts = [move, dst] if to_front else [dst, move]
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(parts[0]), "-i", str(parts[1]), "-filter_complex",
                    "[0][1]concat=n=2:v=0:a=1", str(tmp)], check=True)
    tmp.replace(dst)
    keep.replace(src)
    move.unlink(missing_ok=True)


def fix_boundaries(sents: list, lines: list) -> set:
    """Wort am falschen Satz (z. B. „Er kommt“ am Ende von „Er galoppiert los.“): an der Spracherkennung erkennen und den
    Ton in den richtigen Satz verschieben (nur innerhalb einer Erzähler-Aufnahme, d. h. gleicher Fluss-Block)."""
    fixes = set()
    idx = [i for i, ln in enumerate(lines) if ln.get("file")]
    for i, j in zip(idx, idx[1:]):
        A, B = lines[i], lines[j]
        if A.get("flow") is None or A.get("flow") != B.get("flow") or A.get("tail") or B.get("tail"):
            continue
        fa, fb = ROOT / "public" / A["file"], ROOT / "public" / B["file"]
        ra, rb = stt(fa), stt(fb)
        da, db = [norm(w) for w in sents[i]["text"].split()], [norm(w) for w in sents[j]["text"].split()]
        na, nb = [norm(w["w"]) for w in ra], [norm(w["w"]) for w in rb]
        # Ende von A enthält den Anfang von B?
        for k in range(min(4, len(db)), 0, -1):
            if len(na) > k and na[-k:] == db[:k] and na[:-k][-1:] == da[-1:]:
                move_audio(fa, fb, max(0.0, ra[-k]["s"] - 0.05), to_front=True)
                print(f"   ✂️  {sents[i]['id']} -> {sents[j]['id']}: „{' '.join(w['w'] for w in ra[-k:])}“ verschoben")
                fixes |= {i, j}
                break
        else:
            # Anfang von B enthält das Ende von A?
            for k in range(min(4, len(da)), 0, -1):
                if len(nb) > k and nb[:k] == da[-k:] and nb[k:k + 1] == db[:1]:
                    move_audio(fb, fa, rb[k]["s"] - 0.05, to_front=False)
                    print(f"   ✂️  {sents[j]['id']} -> {sents[i]['id']}: „{' '.join(w['w'] for w in rb[:k])}“ verschoben")
                    fixes |= {i, j}
                    break
    return fixes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    a = ap.parse_args()
    D = ROOT / "src" / a.project
    script = json.loads((D / "script.json").read_text(encoding="utf-8"))
    tp = D / "timing.json"
    timing = json.loads(tp.read_text(encoding="utf-8"))
    sents = [s for s in script["sentences"]]
    for i in sorted(fix_boundaries(sents, timing["lines"])):   # Längen der geänderten Dateien neu
        ln = timing["lines"][i]
        ln["seconds"] = round(dur(ROOT / "public" / ln["file"]) + PAUSE, 3)
    total_shift = []
    for s, ln in zip(sents, timing["lines"]):
        if not ln.get("file"):
            continue
        f = ROOT / "public" / ln["file"]
        rec = stt(f)
        disp = s["text"].split()
        new, hit = retime(disp, ln["words"], rec)
        sh = [abs(x["start"] - y["start"]) for x, y in zip(new, ln["words"])]
        total_shift += sh
        print(f"   {s['id']:4s} {hit}/{len(disp)} erkannt · max. Verschiebung {max(sh) if sh else 0:.2f}s · {' '.join(w['w'] for w in rec)[:70]}")
        ln["words"] = new
        ln["stt"] = True
    tp.write_text(json.dumps(timing, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"✅ Wortzeiten aus Spracherkennung · mittlere Verschiebung {sum(total_shift) / max(1, len(total_shift)):.2f}s")


if __name__ == "__main__":
    main()
