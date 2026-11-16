#!/usr/bin/env python3
"""Zeitplan für „Der erste Adhan“ (QISSA, POV): welche Einstellung wann, wann welcher Satz, Zitat, Effekt.

Liest src/qissa_adhan/script.json und – falls schon vertont – src/qissa_adhan/timing.json (voice_gemini.py).
Ohne Vertonung werden die Satzlängen geschätzt. Schreibt src/qissa_adhan/timeline.json, die von Blender
(blender/qissa/adhan.py: Länge jeder Einstellung + Ereignisse) und Remotion (QissaAdhan) gelesen wird.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "src" / "qissa_adhan"
FPS = 24
ATHAN_IN = 0.0       # Startpunkt in der Aufnahme
ATHAN_TAKBIR = [2.3, 6.5, 10.0, 14.0]  # „Allahu akbar“ in der Aufnahme (Sekunden)

# Ablauf: Einstellungen (Blender) und Tafeln (Remotion). Schritte je Einstellung:
#   ("p", s) Pause · ("l", id) Satz · ("q", id, s) Zitat (nur Schrift) · ("athan",) Adhan beginnt · ("choice", s) Auswahltafel
PLAN = [
    ("shot", "gasse", "MEDINA · 622 · NACHT", [("p", 3.9), ("l", "d1"), ("p", 0.7)]),
    ("shot", "moschee", None, [("p", 0.5), ("l", "m1"), ("p", 0.25), ("l", "m2"), ("p", 0.45), ("l", "d2"), ("p", 0.6)]),
    ("shot", "beratung", None, [("p", 0.6), ("l", "d3"), ("p", 0.45), ("l", "d4"), ("p", 0.4), ("l", "d5"), ("p", 0.7)]),
    ("card", "nacht", "IN DIESER NACHT", 1.7),
    ("shot", "traum", None, [("p", 0.5), ("l", "d6"), ("p", 0.3), ("l", "d7"), ("p", 0.35), ("q", "q1", 4.2), ("p", 0.15),
                             ("q", "q2", 3.3), ("p", 0.2), ("l", "d8"), ("p", 0.9)]),
    ("card", "morgen_karte", "AM MORGEN", 1.6),
    ("shot", "morgen", "MEDINA · MORGENDÄMMERUNG", [("p", 0.5), ("l", "d9"), ("p", 0.35), ("q", "q3", 6.2), ("p", 0.3), ("l", "d10"),
                                                  ("p", 0.6)]),
    ("shot", "dach_a", None, [("p", 0.4), ("l", "d11"), ("p", 0.3), ("athan",), ("p", 4.4)]),
    ("shot", "dach_b", None, [("p", 4.2)]),
    ("shot", "dach_c", None, [("p", 4.0)]),
    ("shot", "dach_d", None, [("p", 4.4)]),
    ("shot", "umar", None, [("p", 0.6), ("l", "d12"), ("p", 0.3), ("q", "q4", 4.8), ("p", 0.2), ("l", "d13"), ("p", 0.8)]),
    ("shot", "ende", None, [("p", 0.4), ("l", "d14"), ("p", 0.5), ("choice", 4.4)]),
    ("card", "logo", "QISSA", 2.4),
]


def est_seconds(text: str) -> float:
    t = text.replace("*", "")
    words = len(t.split())
    stops = len(re.findall(r"[.!?]", t))
    commas = len(re.findall(r"[,:;]", t))
    return round(words / 2.35 + 0.28 * stops + 0.12 * commas + 0.15, 2)


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


def main() -> None:
    script = json.loads((D / "script.json").read_text(encoding="utf-8"))
    sents = {s["id"]: s for s in script["sentences"]}
    order = [s["id"] for s in script["sentences"]]
    quotes = {q["id"]: q for q in script["quotes"]}
    timing = None
    tp = D / "timing.json"
    if tp.exists():
        timing = json.loads(tp.read_text(encoding="utf-8"))["lines"]
    voiced = timing is not None

    def line_info(i: str) -> dict:
        s = sents[i]
        if voiced:
            ln = timing[order.index(i)]
            return {"file": ln["file"], "dur": round(ln["seconds"] - 0.3, 3), "words": ln["words"]}
        dur = est_seconds(s["text"])
        return {"file": "", "dur": dur, "words": word_times(s["text"], dur)}

    t = 0.0
    segs, lines, qs, ev = [], [], [], {}
    athan_at = None
    choice = None
    for item in PLAN:
        if item[0] == "card":
            segs.append({"id": item[1], "kind": "card", "text": item[2], "start": round(t, 3), "dur": item[3]})
            t += item[3]
            continue
        _, sid, label, steps = item
        t0 = t
        for st in steps:
            if st[0] == "p":
                t += st[1]
            elif st[0] == "l":
                li = line_info(st[1])
                s = sents[st[1]]
                lines.append({"id": st[1], "shot": sid, "start": round(t, 3), "dur": li["dur"], "file": li["file"],
                              "text": s["text"], "voice": s.get("voice", "Charon"), "words": li["words"]})
                # Ereignisse an Schlüsselwörtern (für Kopfdrehungen / Geräusche)
                for w in li["words"]:
                    k = re.sub(r"[^\wäöüÄÖÜß]", "", w["word"].replace("*", "")).lower()
                    if k in ("glocke", "horn", "feuer", "bilal", "umar") and f"{k}_{st[1]}" not in ev:
                        ev[f"{k}_{st[1]}"] = round(t + w["start"], 3)
                t += li["dur"]
            elif st[0] == "q":
                q = quotes[st[1]]
                qs.append({"id": st[1], "shot": sid, "start": round(t, 3), "dur": st[2], "text": q["text"], "by": q["by"]})
                t += st[2]
            elif st[0] == "athan":
                athan_at = round(t, 3)
            elif st[0] == "choice":
                choice = {"start": round(t, 3), "dur": st[1], **script["choice"]}
                t += st[1]
        segs.append({"id": sid, "kind": "shot", "label": label, "start": round(t0, 3), "dur": round(t - t0, 3),
                     "frames": int(round((t - t0) * FPS))})
    total = round(t, 3)
    seg = {s["id"]: s for s in segs}
    # Adhan läuft vom Dach bis in Umars Szene (er hört ihn im Haus und stürzt hinaus), dort leiser, dann ausblenden
    umar = seg["umar"]
    ev["athan"] = athan_at
    ev["athan_end"] = round(umar["start"] + umar["dur"], 3)
    ev["takbir"] = [round(athan_at + x - ATHAN_IN, 3) for x in ATHAN_TAKBIR]
    ev["door_umar"] = round(umar["start"] + 0.35, 3)
    out = {"fps": FPS, "voiced": voiced, "total": total, "frames": int(round(total * FPS)), "segments": segs, "lines": lines,
           "quotes": qs, "choice": choice, "events": ev, "athan": {"file": script["athanFile"], "in": ATHAN_IN}}
    (D / "timeline.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{'vertont' if voiced else 'GESCHÄTZT'} · Gesamtlänge {int(total // 60)}:{total % 60:04.1f} min · {out['frames']} Bilder")
    for s in segs:
        print(f"  {s['start']:6.1f}s  {s['dur']:5.1f}s  {s['kind']:5s} {s['id']}")


if __name__ == "__main__":
    main()
