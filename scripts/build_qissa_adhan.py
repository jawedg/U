#!/usr/bin/env python3
"""Zeitplan für „Der erste Adhan“ (QISSA, POV, Erzähl-Version): welche Einstellung wann, wann welcher Satz/Zitat, Effekt.

Liest src/qissa_adhan/script.json und – falls schon vertont – src/qissa_adhan/timing.json (voice_gemini.py).
Ohne Vertonung werden die Satzlängen geschätzt. Schreibt src/qissa_adhan/timeline.json, die von Blender
(blender/qissa/adhan.py: Länge jeder Einstellung + Ereignisse) und Remotion (QissaAdhan) gelesen wird.

Schon gerenderte Einstellungen (src/qissa_adhan/rendered_ref.json = mit welchem Zeitplan gerendert) werden über
Zeit-Anker angepasst: zwischen zwei Ankern (z. B. „Tür fliegt auf“, „Adhan beginnt“, Satzanfänge) läuft das Bild
mit konstanter Geschwindigkeit, an den Ankern stimmt es genau. Weicht das zu stark ab → „neu rendern“.

  python3 scripts/build_qissa_adhan.py                       # Zeitplan bauen + Übersicht
  python3 scripts/build_qissa_adhan.py --mark-rendered a b   # Einstellungen a, b wurden mit diesem Plan gerendert
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "src" / "qissa_adhan"
FPS = 60          # Video (flüssig; TikTok spielt max. 60 fps)
RFPS = int(__import__('os').environ.get('QISSA_RFPS', '30'))  # Blender-Bilder pro Sekunde (dazwischen wird interpoliert)
ATHAN_IN = 1.9       # Startpunkt in der Aufnahme (kurz vor dem ersten „Allahu akbar“)
ATHAN_TAKBIR = [2.3, 6.5, 10.0, 14.0]  # „Allahu akbar“ in der Aufnahme (Sekunden)
RATE_MIN, RATE_MAX = 0.75, 1.33        # erlaubte Bild-Geschwindigkeit zwischen zwei Ankern

# Ablauf: Einstellungen (Blender) und Tafeln (Remotion). Schritte je Einstellung:
#   ("p", s) Pause · ("l", id) Satz · ("q", id) Zitat (gesprochen mit Hall + goldene Schrift)
#   ("athan",) Adhan beginnt · ("duck",) Adhan wird leise (Reaktionen) · ("athan_end",) Adhan ist aus
#   ("choice", s, id) Auswahltafel, währenddessen Satz id
PLAN = [
    # Einstieg (Hook): Ausschnitte aus späteren Einstellungen – echtes „Allahu akbar“, dann die Frage
    ("clip", "hook_a", "dach_a", [("hook_takbir",), ("p", 2.1)]),
    ("clip", "hook_b", "ende", [("p", 0.1), ("l", "h1"), ("p", 0.1)]),
    ("clip", "hook_c", "traum", [("p", 0.05), ("l", "h2"), ("p", 0.25)]),
    ("shot", "gasse", "MEDINA · 622 · NACHT", [("p", 0.25), ("l", "e2"), ("p", 0.3), ("l", "d1"), ("p", 0.25), ("l", "n1"),
                                              ("p", 0.35)]),
    ("shot", "moschee", None, [("p", 0.2), ("l", "m1"), ("p", 0.15), ("l", "m2"), ("p", 0.25)]),
    ("shot", "beratung", None, [("p", 0.1), ("l", "d3"), ("p", 0.1), ("l", "d4"), ("p", 0.1), ("l", "d5"), ("p", 0.12)]),
    ("card", "nacht", "IN DIESER NACHT", 1.2),
    ("shot", "traum", None, [("p", 0.15), ("l", "d6"), ("p", 0.1), ("l", "d7"), ("p", 0.12), ("l", "e4"), ("p", 0.05), ("q", "q1"),
                             ("p", 0.12), ("l", "e5"), ("p", 0.05), ("q", "q2"), ("p", 0.15), ("l", "d8"), ("p", 0.2)]),
    ("card", "morgen_karte", "AM MORGEN", 1.2),
    ("shot", "morgen", "MEDINA · MORGENDÄMMERUNG", [("p", 0.3), ("l", "d9"), ("p", 0.05), ("q", "q3"), ("p", 0.2), ("l", "d10"),
                                                  ("p", 0.3)]),
    ("shot", "dach_a", None, [("p", 0.2), ("l", "d11"), ("p", 0.2), ("athan",), ("p", 4.4)]),
    ("shot", "dach_c", None, [("p", 4.0)]),
    ("shot", "dach_b", None, [("duck",), ("p", 0.3), ("l", "f1"), ("p", 0.25), ("l", "k1"), ("p", 0.4), ("athan_end",)]),
    ("shot", "dach_d", None, [("p", 0.15), ("l", "e6"), ("p", 0.25)]),
    ("shot", "umar", None, [("p", 0.25), ("l", "d12"), ("p", 0.05), ("q", "q4"), ("p", 0.3), ("l", "d13"), ("p", 0.35)]),
    ("shot", "ende", None, [("p", 0.2), ("l", "d14"), ("p", 0.35), ("l", "e7"), ("p", 1.4)]),  # Ende: Kreis zum Anfang („Aus einem Traum“)
    ("card", "logo", "QISSA", 2.0),
]
HOOK_IN = 2.2   # Startpunkt in der Aufnahme für das „Allahu akbar“ im Einstieg
# Anker je Einstellung: Zeitpunkte, an denen in Blender etwas passiert (Kopfdrehung, Tür, Adhan-Pose …)
ANCHORS = {
    "gasse": ["l:d1", "l:n1"],
    "moschee": ["l:m1", "l:m2"],
    "beratung": ["l:d3", "e:glocke_d4", "e:horn_d4", "e:feuer_d4", "l:d5"],
    "traum": ["q:q1", "q:q2", "l:d8"],
    "morgen": ["l:d9", "q:q3", "e:bilal_d10"],
    "dach_a": ["e:athan"],
    "umar": ["e:door_umar"],
}


def est_seconds(text: str) -> float:
    """Geschätzte Sprechdauer (geeicht an früheren Gemini-Charon-Aufnahmen: athan2d, fuku, futaba3 -> Faktor 0,76)."""
    t = text.replace("*", "")
    words = len(t.split())
    stops = len(re.findall(r"[.!?]", t))
    commas = len(re.findall(r"[,:;]", t))
    return round(0.76 * (words / 2.35 + 0.28 * stops + 0.12 * commas + 0.15), 2)


def word_times(text: str, dur: float) -> list:
    words = text.split()
    weights = [len(re.sub(r"[^\wäöüÄÖÜß]", "", w)) + 2 + (5 if re.search(r"[,.:!?]$", w) else 0) for w in words]
    lead, tail = 0.1, 0.15
    usable = max(0.1, dur - lead - tail)
    t, out = lead, []
    for w, wt in zip(words, weights):
        out.append({"word": w, "start": round(t, 3)})
        t += usable * wt / sum(weights)
    return out


def shot_times(tl: dict, sid: str) -> dict:
    """Zeitpunkte (relativ zum Einstellungsbeginn) aller Sätze, Zitate und Ereignisse einer Einstellung."""
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
        for j, x in enumerate(v if isinstance(v, list) else [v]):
            if t0 <= x <= t1:
                t["e:" + k + (f"{j}" if isinstance(v, list) else "")] = round(x - t0, 3)
    return t


def time_map(sid: str, new_dur: float, new_t: dict, ref: dict) -> tuple[list, bool]:
    """Stückweise lineare Zuordnung neue Zeit -> Zeit im gerenderten Bild. Rückgabe (Anker, neu_rendern?)."""
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
        k = i + 1 if i + 1 < len(pts) - 1 else i  # inneren Anker weglassen
        if k == 0:
            break
        pts.pop(k)

    def f(x):  # neue Zeit -> Bildzeit
        for (a0, b0), (a1, b1) in zip(pts, pts[1:]):
            if x <= a1:
                return b0 + (x - a0) * (b1 - b0) / max(1e-6, a1 - a0)
        return pts[-1][1]
    err = max(abs(f(a) - b) for a, b in want)  # wie weit verfehlt ein weggelassener Anker sein Bild?
    glob = r["dur"] / new_dur
    return [[round(a, 3), round(b, 3)] for a, b in pts], bool(bad(pts)) or err > 1.0 or not 0.8 <= glob <= 1.25


def main() -> None:
    script = json.loads((D / "script.json").read_text(encoding="utf-8"))
    sents = {s["id"]: s for s in script["sentences"]}
    order = [s["id"] for s in script["sentences"]]
    timing = None
    tp = D / "timing.json"
    if tp.exists():
        timing = json.loads(tp.read_text(encoding="utf-8"))["lines"]
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
    choice = None

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
        # Ereignisse an Schlüsselwörtern (für Kopfdrehungen / Geräusche)
        for w in li["words"]:
            k = re.sub(r"[^\wäöüÄÖÜß]", "", w["word"].replace("*", "")).lower()
            if k in ("glocke", "horn", "feuer", "bilal", "umar") and f"{k}_{i}" not in ev:
                ev[f"{k}_{i}"] = round(at + w["start"], 3)
        return li["dur"]

    for item in PLAN:
        if item[0] == "card":
            segs.append({"id": item[1], "kind": "card", "text": item[2], "start": round(t, 3), "dur": item[3]})
            t += item[3]
            continue
        if item[0] == "clip":
            _, sid, src, steps = item
            label = None
        else:
            _, sid, label, steps = item
        t0 = t
        for st in steps:
            if st[0] == "p":
                t += st[1]
            elif st[0] in ("l", "q"):
                t += add_line(st[1], sid, t)
            elif st[0] in ("athan", "duck", "athan_end", "hook_takbir"):
                ev[st[0]] = round(t, 3)
            elif st[0] == "choice":
                d = add_line(st[2], sid, t + 0.3)
                dur = max(st[1], d + 0.9)
                choice = {"start": round(t, 3), "dur": round(dur, 3), **script["choice"]}
                t += dur
        if item[0] == "clip":
            segs.append({"id": sid, "kind": "clip", "src": src, "start": round(t0, 3), "dur": round(t - t0, 3)})
            continue
        segs.append({"id": sid, "kind": "shot", "label": label, "start": round(t0, 3), "dur": round(t - t0, 3),
                     "frames": int(round((t - t0) * RFPS))})
    total = round(t, 3)
    seg = {s["id"]: s for s in segs}
    ev["takbir"] = [round(ev["athan"] + x - ATHAN_IN, 3) for x in ATHAN_TAKBIR if ev["athan"] + x - ATHAN_IN < ev["duck"] - 1.0]
    ev["takbir_hook"] = round(ev["hook_takbir"] + ATHAN_TAKBIR[0] - HOOK_IN, 3)
    ev["door_umar"] = round(seg["umar"]["start"] + 0.35, 3)
    # Einstieg: Ausschnitt-Startzeit in der Quell-Einstellung (Sekunden ab deren Beginn)
    src_at = {"hook_a": ev["athan"] - seg["dach_a"]["start"] - 0.15,
              "hook_b": 1.0,
              "hook_c": next(l["start"] for l in lines if l["id"] == "d7") - seg["traum"]["start"] + 0.5}
    for s_ in segs:
        if s_["kind"] == "clip":
            s_["at"] = round(src_at[s_["id"]], 3)
    out = {"fps": FPS, "render_fps": RFPS, "voiced": voiced, "total": total, "frames": int(round(total * FPS)), "segments": segs, "lines": lines,
           "quotes": qs, "choice": choice, "events": ev, "athan": {"file": script["athanFile"], "in": ATHAN_IN, "hook_in": HOOK_IN}}

    # Zeit-Anker für schon gerenderte Einstellungen
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
                # Originaltempo, nur hinten gekürzt (ist die neue Einstellung länger: minimal langsamer)
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
        print(f"  {s['start']:6.1f}s  {s['dur']:5.1f}s  {s['kind']:5s} {s['id']:12s}{extra}")
    rr = [s["id"] for s in segs if s.get("rerender")]
    print("neu zu rendern:", " ".join(rr) if rr else "nichts")


if __name__ == "__main__":
    main()
