#!/usr/bin/env python3
"""Zeitplan für das POV-Erinnerungsvideo „Was, wenn das dein letzter Flug ist?“ (src/flug/).

Wie scripts/build_qissa_hijra.py, aber zusätzlich echte Koran-Rezitationen (Schritt ("r", id): Datei aus script.json
"recitations", arabische Wörter mit Zeiten aus der Spracherkennung) und Tafeln mit Schritten (schwarze Tafel mit Rezitation).

  python3 scripts/build_flug.py          # Zeitplan bauen + Übersicht -> src/flug/timeline.json
"""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "src" / "flug"
FPS = 60
RFPS = int(os.environ.get("FLUG_RFPS", "30"))
XF = 0.4          # Überblendung zwischen Einstellungen (jede Einstellung wird so viel länger gerendert)
REC_TAIL = 1.8    # Rezitationen haben ~2,4 s Nachhall – der nächste Satz darf schon im Nachhall beginnen

# Schritte: ("p", s) Pause · ("l", id) Satz · ("q", id) Zitat (Hall + goldene Schrift) · ("r", id) Koran-Rezitation
#   ("clip", id, quelle, at, schritte)  Ausschnitt einer anderen Einstellung ab Sekunde `at` (Einstieg)
#   ("shot", id, ort_zeile, schritte)   Blender-Einstellung · ("card", id, None, schritte) schwarze Tafel
PLAN = [
    ("clip", "hook_a", "absturz", 2.6, [("p", 0.35), ("l", "h1"), ("p", 0.15)]),
    ("clip", "hook_b", "beten", 2.0, [("p", 0.05), ("l", "h2"), ("p", 0.35)]),
    ("shot", "kabine", "FLUG 417 · 11.000 METER · 21:40 UHR", [("p", 0.35), ("l", "k1"), ("p", 0.15)]),
    ("shot", "handy", None, [("p", 0.1), ("l", "k2"), ("p", 0.25), ("l", "k3"), ("p", 0.5)]),
    ("shot", "gong", None, [("p", 0.8), ("l", "t1"), ("p", 0.35), ("l", "t2"), ("p", 1.6)]),
    ("shot", "absturz", None, [("p", 0.3), ("l", "a1"), ("p", 0.2), ("l", "a2"), ("p", 0.2), ("l", "a3"), ("p", 0.3)]),
    ("shot", "beten", None, [("p", 0.1), ("l", "a4"), ("p", 0.3), ("l", "a5"), ("p", 0.3), ("l", "a6"), ("p", 0.8)]),
    ("shot", "stille", None, [("p", 1.2), ("l", "s1"), ("p", 0.5)]),
    ("shot", "landung", None, [("p", 2.1), ("l", "l1"), ("p", 0.2), ("l", "l2"), ("p", 0.4)]),
    ("shot", "vergessen", None, [("p", 0.3), ("l", "l3"), ("p", 0.35), ("l", "q0"), ("p", 0.3)]),
    ("card", "koran", None, [("p", 0.2), ("r", "r1"), ("p", 0.3)]),
    ("shot", "terminal", None, [("p", 0.3), ("l", "e1"), ("p", 0.3), ("r", "r2"), ("p", 0.3), ("l", "e2"), ("p", 0.4)]),
    ("shot", "gebetsraum", None, [("p", 0.3), ("l", "e3"), ("p", 0.1), ("q", "qh"), ("p", 0.3), ("l", "e4"), ("p", 0.3),
                                  ("l", "e5"), ("p", 0.8)]),
    ("card", "ende", None, [("p", 0.35), ("r", "r3"), ("p", 0.2)]),
]


def est_seconds(text: str) -> float:
    t = text.replace("*", "")
    return round(0.76 * (len(t.split()) / 2.35 + 0.28 * len(re.findall(r"[.!?]", t)) + 0.12 * len(re.findall(r"[,:;]", t)) + 0.15), 2)


def word_times(text: str, dur: float) -> list:
    words = text.split()
    weights = [len(re.sub(r"[^\wäöüÄÖÜß]", "", w)) + 2 + (5 if re.search(r"[,.:!?]$", w) else 0) for w in words]
    usable = max(0.1, dur - 0.25)
    t, out = 0.1, []
    for w, wt in zip(words, weights):
        out.append({"word": w, "start": round(t, 3)})
        t += usable * wt / sum(weights)
    return out


def norm(w: str) -> str:
    return re.sub(r"[^\wäöüÄÖÜß]", "", w.replace("*", "")).lower()


def duration(p: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout)


def arabic_times(path: Path, ar: str) -> list:
    """Zeiten der arabischen Wörter (für die goldene Schrift Wort für Wort): ElevenLabs-Spracherkennung (Arabisch),
    zwischengespeichert; Wörter der Reihe nach zugeordnet (Pausenzeichen ۖ ۚ zählen nicht)."""
    words = [w for w in ar.split() if not re.fullmatch(r"[ۖ-ۜ]+", w)]
    sig = hashlib.sha1(path.read_bytes()).hexdigest()[:16]
    cp = ROOT / "out" / "stimmproben" / f"stt-ar-{sig}.json"
    if not cp.exists():
        r = subprocess.run(["curl", "-s", "-m", "180", "-H", "xi-api-key: proxy-injected", "-F", "model_id=scribe_v1",
                            "-F", "language_code=ar", "-F", "timestamps_granularity=word", "-F", f"file=@{path}",
                            "https://api.elevenlabs.io/v1/speech-to-text"], capture_output=True, text=True)
        d = json.loads(r.stdout)
        cp.write_text(json.dumps([{"w": w["text"], "s": w["start"], "e": w["end"]} for w in d["words"] if w.get("type") == "word"],
                                 ensure_ascii=False))
    rec = json.loads(cp.read_text())
    if len(rec) >= len(words):
        rec = rec[len(rec) - len(words):] if len(rec) > len(words) else rec
        return [{"word": w, "start": round(r_["s"], 3)} for w, r_ in zip(words, rec)]
    dur = duration(path) - 2.4
    return [{"word": w, "start": round(0.2 + dur * i / len(words), 3)} for i, w in enumerate(words)]


def main() -> None:
    script = json.loads((D / "script.json").read_text(encoding="utf-8"))
    sents = {s["id"]: s for s in script["sentences"]}
    order = [s["id"] for s in script["sentences"]]
    recs = {r["id"]: r for r in script.get("recitations", [])}
    tp = D / "timing.json"
    timing = json.loads(tp.read_text(encoding="utf-8"))["lines"] if tp.exists() else None
    voiced = timing is not None and len(timing) == len(order)

    def line_info(i: str) -> dict:
        s = sents[i]
        if voiced:
            ln = timing[order.index(i)]
            return {"file": ln["file"], "dur": round(ln["seconds"] - 0.3, 3), "words": ln["words"], "tail": ln.get("tail", 0)}
        dur = est_seconds(s["text"])
        return {"file": "", "dur": dur, "words": word_times(s["text"], dur), "tail": 0}

    t = 0.0
    segs, lines, qs, rs, ev = [], [], [], [], {}

    def add_line(i: str, sid: str, at: float) -> float:
        li = line_info(i)
        s = sents[i]
        ln = {"id": i, "shot": sid, "start": round(at, 3), "dur": li["dur"], "file": li["file"], "text": s["text"],
              "speaker": s.get("speaker", ""), "words": li["words"], "tail": li["tail"]}
        if s.get("dialog"):
            ln["dialog"] = True
        if s.get("quote"):
            ln["quote"] = True
            ln["by"] = s.get("by", "")
            qs.append({"id": i, "shot": sid, "start": round(at, 3), "dur": li["dur"], "text": s["text"], "by": s.get("by", ""),
                       "words": li["words"]})
        lines.append(ln)
        for w in li["words"]:
            k = norm(w["word"])
            if k and f"{k}_{i}" not in ev:
                ev[f"{k}_{i}"] = round(at + w["start"], 3)
        return li["dur"]

    def add_rec(i: str, sid: str, at: float, last: bool) -> float:
        r = recs[i]
        p = ROOT / "public" / r["file"]
        full = duration(p)
        dur = full if last else full - REC_TAIL
        rs.append({"id": i, "shot": sid, "start": round(at, 3), "dur": round(dur, 3), "full": round(full, 3), "file": r["file"],
                   "ar": r["ar"], "de": r["de"], "ref": r["ref"], "words": arabic_times(p, r["ar"])})
        ev[f"rez_{i}"] = round(at, 3)
        return dur

    # Fluss-Modus: zwischen Sätzen, die in der Aufnahme direkt aufeinander folgen, keine eigene Pause
    flow = {}
    if voiced:
        for i, ln_ in zip(order, timing):
            if "flow" in ln_:
                flow[i] = ln_["flow"]
    flow_next = {}
    for part_ in set(flow.values()):
        ids_ = [i for i in order if flow.get(i) == part_]
        flow_next.update({a_: b_ for a_, b_ in zip(ids_, ids_[1:])})

    def steps_of(item):
        return item[4] if item[0] == "clip" else item[3]
    seq = [(pi, si, st) for pi, item in enumerate(PLAN) for si, st in enumerate(steps_of(item))]

    def flowing(pi, si):
        k = next(n for n, x in enumerate(seq) if x[0] == pi and x[1] == si)

        def key(st):
            return st[1] if st[0] in ("l", "q") else "#" + st[0]
        marks = ("l", "q", "r")
        prev = next((key(x[2]) for x in reversed(seq[:k]) if x[2][0] in marks), None)
        nxt = next((key(x[2]) for x in seq[k + 1:] if x[2][0] in marks), None)
        return prev is not None and nxt is not None and flow_next.get(prev) == nxt

    for pi, item in enumerate(PLAN):
        sid = item[1]
        t0 = t
        steps = steps_of(item)
        for si, st in enumerate(steps):
            if st[0] == "p":
                t += 0.0 if flowing(pi, si) else st[1]
            elif st[0] in ("l", "q"):
                t += add_line(st[1], sid, t)
            elif st[0] == "r":
                t += add_rec(st[1], sid, t, last=(pi == len(PLAN) - 1))
        if item[0] == "clip":
            segs.append({"id": sid, "kind": "clip", "src": item[2], "at": item[3], "start": round(t0, 3), "dur": round(t - t0, 3)})
        elif item[0] == "card":
            segs.append({"id": sid, "kind": "card", "start": round(t0, 3), "dur": round(t - t0, 3)})
        else:
            segs.append({"id": sid, "kind": "shot", "label": item[2], "start": round(t0, 3), "dur": round(t - t0, 3),
                         "frames": int(round((t - t0 + XF) * RFPS))})
    total = round(t, 3)
    out = {"fps": FPS, "render_fps": RFPS, "xfade": XF, "voiced": voiced, "total": total, "frames": int(round(total * FPS)),
           "segments": segs, "lines": lines, "quotes": qs, "recites": rs, "events": ev}
    (D / "timeline.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{'vertont' if voiced else 'GESCHÄTZT'} · Gesamtlänge {int(total // 60)}:{total % 60:04.1f} min · {out['frames']} Bilder")
    for s in segs:
        extra = f"  ← {s['src']} ab {s['at']:.1f}s" if s["kind"] == "clip" else ""
        print(f"  {s['start']:6.1f}s  {s['dur']:5.1f}s  {s['kind']:5s} {s['id']:12s}{extra}")
    print("Bilder zu rendern:", sum(s["frames"] for s in segs if s["kind"] == "shot"))


if __name__ == "__main__":
    main()
