#!/usr/bin/env python3
"""Zeitplan für QISSAH Folge 4 „Die Schlacht von Badr“ (POV): welche Einstellung wann, wann welcher Satz/Zitat, Ereignisse.

Wie scripts/build_qissa_kaaba.py (Folge 3): liest src/qissa_badr/script.json + timing.json (voice_gemini.py),
schreibt src/qissa_badr/timeline.json für Blender (blender/qissa/badr.py) und Remotion (QissaBadr).

  python3 scripts/build_qissa_badr.py                       # Zeitplan bauen + Übersicht
  python3 scripts/build_qissa_badr.py --mark-rendered a b   # Einstellungen a, b wurden mit diesem Plan gerendert
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "src" / "qissa_badr"
FPS = 60
RFPS = int(os.environ.get("QISSA_RFPS", "30"))
RATE_MIN, RATE_MAX = 0.75, 1.33

# Ablauf. Schritte: ("p", s) Pause · ("l", id) Satz · ("q", id) Zitat (Hall + goldene Schrift)
#   ("clip", id, quelle, at, schritte)   Ausschnitt einer anderen Einstellung ab Sekunde `at`
#   ("montage", id, schritte, [(quelle, at), …])   schnelle Schnitte, je Wort des Satzes ein Ausschnitt
#   ("extra", id, sekunden)   Einstellung nur als Quelle für Ausschnitte (wird gerendert, aber nicht selbst gezeigt)
PLAN = [
    ("clip", "hook_0", "kampf", 2.0, [("p", 0.6)]),
    ("clip", "hook_a", "kolonne", 0.2, [("l", "h1"), ("p", 0.1)]),
    ("clip", "hook_b", "sturm", 0.2, [("p", 0.05), ("l", "h2"), ("p", 0.05)]),
    ("clip", "hook_c", "kampf", 4.2, [("p", 0.05), ("l", "h3"), ("p", 0.25)]),
    ("shot", "medina", "MEDINA · RAMADAN, 2 N. H.", [("p", 0.2), ("l", "e1"), ("p", 0.15)]),
    ("shot", "auszug", None, [("p", 0.1), ("l", "e3"), ("p", 0.1)]),
    ("shot", "heer", None, [("p", 0.05), ("l", "e4"), ("p", 0.15)]),
    ("shot", "rat", "BADR", [("p", 0.15), ("l", "e5"), ("p", 0.35), ("q", "q1"), ("p", 0.35)]),
    ("shot", "regen", None, [("p", 0.2), ("l", "e6"), ("p", 0.2)]),
    ("shot", "baum", None, [("p", 0.1), ("l", "e7"), ("p", 0.25)]),
    ("shot", "reihen", "BADR · MORGEN", [("p", 0.2), ("l", "e8"), ("p", 0.25)]),
    ("shot", "gebet", None, [("p", 0.1), ("q", "q2"), ("p", 0.45), ("l", "e9"), ("p", 0.4), ("q", "q3"), ("p", 0.35)]),
    ("shot", "engel", None, [("p", 0.1), ("l", "e10"), ("p", 0.25)]),
    ("shot", "duell", None, [("p", 0.2), ("l", "d1"), ("p", 0.3), ("l", "d2"), ("p", 0.2), ("l", "d3"), ("p", 0.7)]),
    ("shot", "sturm", None, [("p", 0.05), ("l", "e11"), ("p", 0.05)]),
    ("montage", "schlacht", [("p", 0.0), ("l", "e12"), ("p", 0.2)], [("kampf", 8.6), ("kampf", 9.7), ("kampf", 10.8)]),
    ("shot", "jagd", None, [("p", 0.15), ("l", "e13"), ("p", 0.25), ("l", "e14"), ("p", 0.2)]),
    ("clip", "himmel", "engel", 2.3, [("p", 0.05), ("q", "q4"), ("p", 0.4)]),
    ("shot", "abujahl", None, [("p", 0.2), ("l", "a1"), ("p", 0.25), ("l", "a2"), ("p", 0.2), ("l", "a3"), ("p", 0.35)]),
    ("shot", "ende", None, [("p", 0.2), ("l", "e15"), ("p", 0.2)]),
    ("shot", "abend", None, [("p", 0.2), ("l", "e16"), ("p", 0.3), ("l", "e17"), ("p", 0.9)]),
    ("card", "logo", "QISSAH", 2.8),
    ("extra", "kampf", 12.0),
    ("extra", "kolonne", 7.0),
]
# Wörter, an denen in Blender etwas passiert (Ereignis „wort_satz“, z. B. regen_e6)
KEYS = {"medina", "ramadan", "häuser", "besitz", "karawane", "prophet", "abfangen", "krieg", "entkommt", "mekka", "heer", "tausend",
        "gefährten", "miqdad", "musa", "kämpfen", "rechts", "links", "nacht", "regen", "sand", "ruhe", "schlafen", "wach", "baum",
        "weint", "morgen", "heere", "qibla", "hände", "schar", "untergeht", "umhang", "zurück", "genug", "versprochen", "engeln",
        "anderen", "aufeinander", "staub", "schreie", "schwerter", "muslim", "gegner", "peitschenknall", "stimme", "haizum",
        "stürzt", "erzählt", "sagt", "himmel", "fliehen", "siebzig", "gefangen", "dreihundert", "geholfen", "schwach", "koran",
        "furqan", "unterscheidung", "krieger", "rufen", "uns", "hamza", "ali", "ubaida", "hiebe",
        "herausforderer", "fallen", "los", "gedränge", "jungen", "jahl", "zeigt", "stürzen", "falken", "fällt", "umkehren", "steht", "schläft", "später"}
ANCHORS = {}
NUM = {"zwei": 2, "drei": 3, "vier": 4, "fünf": 5, "sechs": 6}


def est_seconds(text: str) -> float:
    t = text.replace("*", "")
    words = len(t.split())
    return round(0.76 * (words / 2.35 + 0.28 * len(re.findall(r"[.!?]", t)) + 0.12 * len(re.findall(r"[,:;]", t)) + 0.15), 2)


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
    w = re.sub(r"^a[lsdnrtz]-", "", w.replace("*", ""), flags=re.I)  # arabischer Artikel: „al-Marwa“ -> marwa (Ereignis-Schlüssel)
    return re.sub(r"[^\wäöüÄÖÜß]", "", w).lower()


def shot_times(tl: dict, sid: str) -> dict:
    s = next(x for x in tl["segments"] if x["id"] == sid)
    t0, t1 = s["start"], s["start"] + s["dur"]
    t = {}
    for l in tl["lines"]:
        if l["shot"] == sid:
            t["l:" + l["id"]] = round(l["start"] - t0, 3)
    for q in tl["quotes"]:
        if q["shot"] == sid:
            t["q:" + q["id"]] = round(q["start"] - t0, 3)
    for k, v in tl["events"].items():
        if isinstance(v, (int, float)) and t0 <= v <= t1:
            t["e:" + k] = round(v - t0, 3)
    return t


def time_map(sid: str, new_dur: float, new_t: dict, ref: dict) -> tuple[list, bool]:
    r = ref.get(sid)
    if not r:
        return [[0.0, 0.0], [new_dur, new_dur]], True
    pts = [(new_t[k], r["t"][k]) for k in ANCHORS.get(sid, []) if k in new_t and k in r["t"]]
    pts = sorted(set([(0.0, 0.0)] + pts + [(round(new_dur, 3), r["dur"])]))

    def bad(p):
        return [i for i in range(len(p) - 1) if p[i + 1][0] - p[i][0] <= 0.05
                or not RATE_MIN <= (p[i + 1][1] - p[i][1]) / (p[i + 1][0] - p[i][0]) <= RATE_MAX]
    want = list(pts)
    while bad(pts) and len(pts) > 2:
        i = bad(pts)[0]
        k = i + 1 if i + 1 < len(pts) - 1 else i
        if k == 0:
            break
        pts.pop(k)

    def f(x):
        for (a0, b0), (a1, b1) in zip(pts, pts[1:]):
            if x <= a1:
                return b0 + (x - a0) * (b1 - b0) / max(1e-6, a1 - a0)
        return pts[-1][1]
    err = max(abs(f(a) - b) for a, b in want)
    glob = r["dur"] / new_dur
    return [[round(a, 3), round(b, 3)] for a, b in pts], bool(bad(pts)) or err > 1.0 or not 0.8 <= glob <= 1.25


def main() -> None:
    script = json.loads((D / "script.json").read_text(encoding="utf-8"))
    sents = {s["id"]: s for s in script["sentences"]}
    order = [s["id"] for s in script["sentences"]]
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
    segs, lines, qs, ev = [], [], [], {}
    counts = []

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
            if k in KEYS and f"{k}_{i}" not in ev:
                ev[f"{k}_{i}"] = round(at + w["start"], 3)
        return li["dur"]

    # Fluss-Modus: zwischen Erzähler-Sätzen, die in der Aufnahme direkt aufeinander folgen, keine eigene Pause
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
        return item[2] if item[0] == "montage" else (item[4] if item[0] == "clip" else item[3])
    seq = []
    for pi, item in enumerate(PLAN):
        if item[0] == "card":
            seq.append((pi, -1, ("card",)))
        elif item[0] == "extra":
            continue
        else:
            seq.extend((pi, si, st) for si, st in enumerate(steps_of(item)))

    def flowing(pi, si):
        k = next(n for n, x in enumerate(seq) if x[0] == pi and x[1] == si)

        def key(st):
            return st[1] if st[0] in ("l", "q") else "#" + st[0]
        marks = ("l", "q", "card")
        prev = next((key(x[2]) for x in reversed(seq[:k]) if x[2][0] in marks), None)
        nxt = next((key(x[2]) for x in seq[k + 1:] if x[2][0] in marks), None)
        return prev is not None and nxt is not None and flow_next.get(prev) == nxt

    for pi, item in enumerate(PLAN):
        if item[0] == "card":
            segs.append({"id": item[1], "kind": "card", "text": item[2], "start": round(t, 3), "dur": item[3]})
            t += item[3]
            continue
        if item[0] == "extra":
            continue
        sid = item[1]
        t0 = t
        for si, st in enumerate(steps_of(item)):
            if st[0] == "p":
                t += 0.0 if flowing(pi, si) else st[1]
            elif st[0] in ("l", "q"):
                t += add_line(st[1], sid, t)
        if item[0] == "clip":
            segs.append({"id": sid, "kind": "clip", "src": item[2], "at": item[3], "start": round(t0, 3), "dur": round(t - t0, 3)})
            continue
        if item[0] == "montage":
            ln = next(l for l in lines if l["shot"] == sid)
            cuts = [t0] + [ln["start"] + w["start"] - 0.06 for w in ln["words"][1:]] + [t]
            for k, ((src, at), a, b) in enumerate(zip(item[3], cuts, cuts[1:])):
                segs.append({"id": f"{sid}{k}", "kind": "clip", "src": src, "at": at, "start": round(a, 3), "dur": round(b - a, 3)})
            for w in ln["words"]:
                n = NUM.get(norm(w["word"]))
                if n:
                    counts.append([round(ln["start"] + w["start"], 3), n])
            continue
        label = item[2]
        segs.append({"id": sid, "kind": "shot", "label": label, "start": round(t0, 3), "dur": round(t - t0, 3),
                     "frames": int(round((t - t0) * RFPS))})
    total = round(t, 3)
    seg = {s["id"]: s for s in segs}
    ev["count"] = counts
    for item in PLAN:  # nur als Quelle für Ausschnitte: wird gerendert, liegt hinter dem Ende (nie sichtbar)
        if item[0] == "extra":
            segs.append({"id": item[1], "kind": "shot", "hidden": True, "label": None, "start": total, "dur": item[2],
                         "frames": int(round(item[2] * RFPS))})
    seg = {s["id"]: s for s in segs}
    out = {"fps": FPS, "render_fps": RFPS, "voiced": voiced, "total": total, "frames": int(round(total * FPS)), "segments": segs,
           "lines": lines, "quotes": qs, "choice": None, "events": ev}

    refp = D / "rendered_ref.json"
    ref = json.loads(refp.read_text(encoding="utf-8")) if refp.exists() else {}
    if "--mark-rendered" in sys.argv:
        for sid in sys.argv[sys.argv.index("--mark-rendered") + 1:]:
            ref[sid] = {"dur": seg[sid]["dur"], "frames": seg[sid]["frames"], "t": shot_times(out, sid)}
            print(f"   ✓ {sid} gilt als gerendert mit diesem Zeitplan")
        refp.write_text(json.dumps(ref, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    rate1 = script.get("retime") == "rate1"
    for s in segs:
        if s["kind"] == "shot":
            s["map"], s["rerender"] = time_map(s["id"], s["dur"], shot_times(out, s["id"]), ref)
            if rate1 and s["id"] in ref and not s["rerender"]:
                s["map"] = [[0.0, 0.0], [s["dur"], round(min(s["dur"], ref[s["id"]]["dur"]), 3)]]
            s["src_frames"] = ref.get(s["id"], {}).get("frames", s["frames"])
            s["src_dur"] = ref.get(s["id"], {}).get("dur", s["dur"])
    (D / "timeline.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{'vertont' if voiced else 'GESCHÄTZT'} · Gesamtlänge {int(total // 60)}:{total % 60:04.1f} min · {out['frames']} Bilder")
    for s in segs:
        extra = ""
        if s["kind"] == "shot":
            m = s["map"]
            rates = [(m[i + 1][1] - m[i][1]) / max(1e-6, m[i + 1][0] - m[i][0]) for i in range(len(m) - 1)]
            extra = f"  Bildtempo {' '.join(f'{r:.2f}' for r in rates)}" + ("  → NEU RENDERN" if s["rerender"] else "")
        elif s["kind"] == "clip":
            extra = f"  ← {s['src']} ab {s['at']:.1f}s"
        print(f"  {s['start']:6.1f}s  {s['dur']:5.1f}s  {s['kind']:5s} {s['id']:12s}{extra}")
    print("Bilder zu rendern:", sum(s["frames"] for s in segs if s["kind"] == "shot"))


if __name__ == "__main__":
    main()
