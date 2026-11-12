#!/usr/bin/env python3
"""POV-Video (3D): VDE-0100-600-Messungen am Prüfungsgestell mit dem Fluke 1664 FC – genau mit Einstellungen.
Bedienung laut Fluke 1662/1663/1664 FC Users Manual:
  RLO:  F1 Messleitungspaar, F2 ZERO (2–6 s halten), F3 Polarität (+ / − / ±), F4 Prüfstrom 10 mA / 250 mA, TEST halten.
  RISO: F1 Messleitungspaar, F3 Safety Pretest, F4 Prüfspannung 50/100/250/500/1000 V, TEST halten bis Piep (unten: echte Prüfspannung).
  Drehfeld: rot (L) an L1, grün (PE) an L2, blau (N) an L3 → „123“ rechts, „321“ links.
  ΔT (RCD-Auslösezeit): F1 0°/180°, F2 Faktor x½/x1/x5/Auto, F3 RCD-Typ/Kurvenform, F4 IΔN; TEST drücken+loslassen;
        oben Auslösezeit, unten U_F (Berührungsspannung).
Messwerte sind Beispielwerte. Ausgabe: src/mess/script.json (kb = 8).
Cues: Wort aus dem Sprechtext (ohne Satzzeichen) oder "@0.4" = Anteil der Szenendauer.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHASES = ["Messgerät", "Schutzleiter", "Isolation", "Drehfeld", "FI/LS (RCD)", "Erprobung"]
S = []
ph, phname = 0, "Start"


def phase(n):
    global ph, phname
    ph += 1
    phname = n


def sc(text, v):
    S.append({"topic": ph, "tname": phname, "text": " ".join(text.split()), "v": v})


LOOK = "look"
HOLD = "hold"

# ------------------------------------------------------------------ Intro
sc("""POV: Ich bin du, am Prüfungstag. Die Anlage ist fertig, und der Prüfer sagt: Zeigen Sie mir bitte die Prüfung nach VDE 0100-600.
Ich messe mit dem *Fluke 1664 FC*. Ich zeige dir genau, wo der *Drehschalter* steht, welche *Taste* ich drücke und wo die *Messspitzen* hinkommen.
Die Messwerte sind Beispielwerte.""",
   {"type": "title", "cam": [[0, "ALL", 1.45, -12, 6], ["@0.5", "ALL", 1.25, 8, 4]], "fl": [[0, {"pose": HOLD, "dial": "V"}]]})

# ------------------------------------------------------------------ 1 Gerät
phase("Messgerät")
sc("""Kurz zum Gerät. Unten ist der *Drehschalter*. Für uns wichtig sind *RLO* für den Schutzleiter, *RISO* für die Isolation,
das *Drehfeld*-Symbol und *Delta* T für die Auslösezeit vom FI. Rechts neben dem Display liegen die vier Tasten *F1* bis F4.
Was sie tun, hängt von der Messart ab. Links ist die große *TEST*-Taste mit dem *Touchpad*. Das berühre ich immer, bevor ich TEST drücke.
Leuchtet darüber das *Warndreieck*, liegt am Schutzleiter eine gefährliche Spannung, und ich höre sofort auf.""",
   {"type": "pov", "cam": [[0, "ALL", 1.2, 0, 4]],
    "fl": [[0, {"pose": LOOK, "hl": "dial"}], ["RLO", {"dial": "RLO"}], ["RISO", {"dial": "RISO"}], ["Drehfeld", {"dial": "PHASE"}],
           ["Delta", {"dial": "DT"}], ["F1", {"hl": "fkeys"}], ["TEST", {"hl": "test"}], ["Warndreieck", {"hl": "warn"}]]})
sc("""Die Messleitungen: *rot* ist L, *grün* ist PE und *blau* ist N. Dazu kommen das *Netzkabel* mit Schukostecker und der *Zero*-Adapter
für den Nullabgleich.""",
   {"type": "pov", "fl": [[0, {"pose": LOOK, "hl": "leads"}]],
    "cards": [["rot", "rot = L"], ["grün", "grün = PE"], ["blau", "blau = N"], ["Netzkabel", "Netzkabel (Schuko)"], ["Zero", "Zero-Adapter"]]})

# ------------------------------------------------------------------ 2 RLO
phase("Schutzleiter")
sc("""Die Anlage ist *freigeschaltet*: Der CEE-Stecker ist gezogen und liegt bei mir, die Spannungsfreiheit habe ich festgestellt.
Ich stelle den *Drehschalter* auf RLO.""",
   {"type": "pov", "cam": [[0, "CEE", 0.55, 15, 18]], "fl": [[0, {"pose": HOLD, "hl": ""}], ["Drehschalter", {"dial": "RLO", "fn": "RLO", "prim": "- - -", "unit": "Ω"}]]})
sc("""Jetzt die Einstellungen. Mit *F1* wähle ich das Messleitungspaar L-PE, also rot und grün. Mit *F4* stelle ich den Prüfstrom auf
*250* Milliampere, denn die Norm verlangt mindestens 200. Mit *F3* wähle ich die Polarität *plus-minus*: Das Gerät misst in beide Richtungen
und zeigt den Mittelwert.""",
   {"type": "pov", "fl": [[0, {"pose": LOOK, "hl": ""}], ["F1", {"press": "F1", "F1": "L-PE", "note": "F1 → L-PE (rot + grün)"}],
                          ["F4", {"press": "F4", "F4": "250 mA", "note": "F4 → 250 mA"}], ["F3", {"press": "F3", "F3": "±", "note": "F3 → ± (beide Polaritäten)"}]]})
sc("""Dann der *Nullabgleich*. Ich stecke rot und grün in den Zero-Adapter und halte *F2* zwei bis sechs Sekunden gedrückt, bis das
*Zero*-Symbol erscheint und das Gerät *piept*. Jetzt wird der Widerstand der Messleitungen abgezogen.""",
   {"type": "pov", "fl": [[0, {"pose": LOOK}], ["F2", {"press": "F2", "hold": 1, "note": "F2 halten (2–6 s)"}], ["Zero", {"zero": 1, "prim": "0.00", "note": "ZERO gespeichert"}],
                          ["piept", {"hold": 0}]]})
sc("""Die *grüne* Leitung klemme ich mit der Krokodilklemme an den PE-Kontakt vom CEE-Stecker. Mit der *roten* Spitze gehe ich an den
PE-Bolzen der *Montageplatte*. Touchpad berühren, *TEST* gedrückt halten, bis der Wert steht: 0,08 *Ohm*.""",
   {"type": "pov", "cam": [[0, "CEE", 0.6, 10, 15], ["roten", "LOW", 0.95, -6, 8]],
    "pr": [["grüne", None, "CEEPE", None], ["roten", "PLATTE", "CEEPE", None]],
    "fl": [[0, {"pose": HOLD, "note": ""}], ["TEST", {"press": "TEST", "prim": "…"}], ["Ohm", {"prim": "0.08", "note": "0,08 Ω"}]]})
sc("""Dann die rote Spitze an den *Schutzkontakt* der Steckdose: 0,14 Ohm. An *X1* Klemme 16, den PE vom *Motor*: 0,21 Ohm. *Und* an den PE der
*Bedieneinheit*: 0,11 Ohm. Alle Werte sind *niedrig* und passen zur Leitungslänge.""",
   {"type": "pov", "cam": [[0, "X5", 0.6, -10, 6], ["X1", "X1:16", 0.55, 10, 8], ["Und", "BEDPE", 0.6, -18, 5], ["niedrig", "ALL", 1.15, 0, 4]],
    "pr": [["Schutzkontakt", "X5PE", "CEEPE", None], ["X1", "M1PE", "CEEPE", None], ["Und", "BEDPE", "CEEPE", None]],
    "fl": [[0, {"pose": HOLD}], ["Steckdose", {"press": "TEST", "prim": "0.14", "note": "0,14 Ω"}], ["Motor", {"press": "TEST", "prim": "0.21", "note": "0,21 Ω"}],
           ["Bedieneinheit", {"press": "TEST", "prim": "0.11", "note": "0,11 Ω"}], ["niedrig", {"note": ""}]]})
sc("""Ins Protokoll schreibe ich den *größten* Wert: 0,21 Ohm, OK.""", {"type": "protocol", "fill": [["größten", "pe", "0,21 Ω"]], "pr": [[0, "-", "-", None]]})

# ------------------------------------------------------------------ 3 RISO
phase("Isolation")
sc("""Vor der Isolationsmessung *klemme* ich das Netzteil T1 ab, damit die 500 Volt die Elektronik nicht beschädigen. F1, F3 und den
Motorschutzschalter F4 schalte ich *ein*, damit die Leitungen dahinter mitgemessen werden.""",
   {"type": "pov", "cam": [[0, "T1", 0.55, 0, 6], ["ein", "F3", 0.6, 10, 6]], "st": [["klemme", {"T1off": 1}]], "fl": [[0, {"pose": HOLD, "note": ""}]]})
sc("""Drehschalter auf *RISO*. Mit *F1* wieder das Paar rot und grün. Mit *F4* stelle ich die Prüfspannung auf *500* Volt. Den *Pretest* mit
F3 lasse ich aus, weil ich einzelne Klemmen gegeneinander messe.""",
   {"type": "pov", "fl": [[0, {"pose": LOOK}], ["RISO", {"dial": "RISO", "fn": "RISO", "prim": "- - -", "unit": "MΩ", "sec": "", "zero": 0, "F1": "L-PE", "F3": "Pretest aus", "F4": "", "F2": ""}],
                          ["F1", {"press": "F1", "note": "F1 → L-PE (rot + grün)"}], ["F4", {"press": "F4", "F4": "500 V", "note": "F4 → 500 V"}],
                          ["Pretest", {"press": "", "note": "F3: Pretest aus"}]]})
sc("""Jetzt messe ich an X1, genau die Paare aus dem Protokoll. Rot an *L1*, grün an *L2*. Touchpad, *TEST* gedrückt halten, bis es piept.
Oben steht der Widerstand: 620 *Megaohm*. Unten die echte *Prüfspannung*: 527 Volt. Die muss mindestens 500 Volt sein.""",
   {"type": "pov", "cam": [[0, "X1:3", 0.48, 0, 10]], "pr": [["L1", "X1:1", None, None], ["L2", "X1:1", "X1:3", None]],
    "fl": [[0, {"pose": HOLD, "note": ""}], ["TEST", {"press": "TEST", "prim": "…"}], ["Megaohm", {"prim": "620", "note": "L1–L2: 620 MΩ"}],
           ["Prüfspannung", {"sec": "527 V", "note": "U = 527 V ≥ 500 V ✓"}]]})
PAIRS = [("X1:1", "X1:5", "710"), ("X1:1", "X1:7", "655"), ("X1:1", "X1:9", "580"), ("X1:3", "X1:5", "690"), ("X1:3", "X1:7", "742"),
         ("X1:3", "X1:9", "605"), ("X1:5", "X1:7", "630"), ("X1:5", "X1:9", "668"), ("X1:7", "X1:9", "590")]
NAMES = {"X1:1": "L1", "X1:3": "L2", "X1:5": "L3", "X1:7": "N", "X1:9": "PE"}
sc("""So mache ich *weiter*: L1 gegen L3, L1 gegen N, L1 gegen PE, dann L2 gegen L3, L2 gegen N, L2 gegen PE, L3 gegen N, L3 gegen PE und zum
*Schluss* N gegen PE. Alle Werte liegen weit über dem *Grenzwert* von 1 Megaohm.""",
   {"type": "pov", "cam": [[0, "X1:5", 0.5, 0, 10]],
    "pr": [[f"@{0.08 + i * 0.075:.3f}", a, b, None] for i, (a, b, _) in enumerate(PAIRS)],
    "fl": [[0, {"pose": HOLD}]] + [[f"@{0.12 + i * 0.075:.3f}", {"press": "TEST", "prim": v, "sec": "52%d V" % (4 + i % 5), "note": f"{NAMES[a]}–{NAMES[b]}: {v} MΩ"}]
                                   for i, (a, b, v) in enumerate(PAIRS)] + [["Grenzwert", {"note": "Grenzwert ≥ 1 MΩ ✓"}]]})
sc("""Alle Werte trage ich in die *Tabelle* ein. Dann klemme ich das Netzteil *wieder* an.""",
   {"type": "protocol", "fill": [["Tabelle", "iso", "*"]], "st": [["wieder", {"T1off": 0}]], "pr": [[0, "-", "-", None]]})

# ------------------------------------------------------------------ 4 Drehfeld
phase("Drehfeld")
sc("""Die Messungen ohne Spannung sind in Ordnung. Ich frage den Prüfer, ob ich einschalten darf, und erst nach seinem *Ja* stecke ich den
CEE-Stecker ein.""", {"type": "pov", "cam": [[0, "CEE", 0.6, -8, 15]], "fl": [[0, {"pose": HOLD, "note": ""}], ["Ja", {"note": "Erst nach dem OK vom Prüfer einschalten!"}]]})
sc("""Drehschalter auf das *Drehfeld*-Symbol. Jetzt brauche ich alle drei Leitungen: *rot* an L1, *grün* an L2 und *blau* an L3, also X1
Klemme 1, 3 und 5. Das Display zeigt *123*. Das heißt *Rechtsdrehfeld*. Würde 321 stehen, wäre es ein Linksdrehfeld.""",
   {"type": "pov", "cam": [[0, "X1:3", 0.5, 0, 10]], "pr": [["rot", "X1:1", None, None], ["grün", "X1:1", "X1:3", None], ["blau", "X1:1", "X1:3", "X1:5"]],
    "fl": [[0, {"pose": LOOK, "note": ""}], ["Drehfeld", {"dial": "PHASE", "fn": "PHASE", "prim": "- - -", "unit": "", "sec": "", "F1": "", "F2": "", "F3": "", "F4": ""}],
           ["rot", {"pose": HOLD}], ["123", {"prim": "123", "note": "123 = Rechtsdrehfeld ✓"}]]})
sc("""Im Protokoll: *Drehfeld* rechts, OK.""", {"type": "protocol", "fill": [["Drehfeld", "dreh", "ok"]], "pr": [[0, "-", "-", "-"]]})

# ------------------------------------------------------------------ 5 RCD
phase("FI/LS (RCD)")
sc("""Jetzt die *Auslösezeit* vom FI/LS F3. Drehschalter auf *Delta* T. Mit *F4* den Bemessungsfehlerstrom: *10* Milliampere. Mit *F2* den Faktor
*mal* 1. Mit *F3* die Kurvenform passend zum FI-Typ, der auf dem Gerät aufgedruckt ist. Und mit *F1* die Phasenlage *0* Grad.""",
   {"type": "pov", "fl": [[0, {"pose": LOOK}], ["Delta", {"dial": "DT", "fn": "DT", "prim": "- - -", "unit": "ms", "sec": "", "F1": "", "F2": "", "F3": "", "F4": ""}],
                          ["F4", {"press": "F4", "F4": "10 mA", "note": "F4 → IΔN 10 mA"}], ["F2", {"press": "F2", "F2": "x1", "note": "F2 → x1"}],
                          ["F3", {"press": "F3", "F3": "Typ ~", "note": "F3 → Kurvenform wie FI-Typ"}], ["F1", {"press": "F1", "F1": "0°", "note": "F1 → 0°"}]]})
sc("""Ich stecke den Schukostecker vom *Netzkabel* des Fluke in die Steckdose X5. Touchpad berühren, *TEST* drücken und loslassen. Der FI/LS
*löst* aus. Oben steht die Auslösezeit: 18 *Millisekunden*. Unten steht U F, die *Berührungsspannung*: 0,3 Volt.""",
   {"type": "pov", "cam": [[0, "X5", 0.6, -6, 5], ["löst", "F3", 0.75, -14, 6]], "st": [["Netzkabel", {"plug": 1}], ["löst", {"F3trip": 1}]],
    "fl": [[0, {"pose": HOLD, "note": ""}], ["TEST", {"press": "TEST", "prim": "…"}], ["Millisekunden", {"prim": "18", "note": "t = 18 ms"}],
           ["Berührungsspannung", {"sec": "U_F 0.3 V", "note": "U_F = 0,3 V"}]]})
sc("""Ich schalte den FI/LS *wieder* ein, stelle mit F1 auf *180* Grad und *messe* noch einmal: 21 Millisekunden. Grenzwert für die *Auslösezeit*
sind 300 Millisekunden, für die *Berührungsspannung* 50 Volt. Beides passt, das Gerät zeigt zusätzlich ein *Häkchen* am RCD-Symbol.""",
   {"type": "pov", "cam": [[0, "F3", 0.7, -14, 6], ["messe", "X5", 0.7, -8, 5]], "st": [["wieder", {"F3trip": 0}], ["messe", {"F3trip": 1}]],
    "fl": [[0, {"pose": HOLD}], ["180", {"press": "F1", "F1": "180°", "note": "F1 → 180°"}], ["messe", {"press": "TEST", "prim": "21", "sec": "U_F 0.3 V", "note": "t = 21 ms"}],
           ["Auslösezeit", {"note": "t ≤ 300 ms ✓"}], ["Berührungsspannung", {"note": "U_F ≤ 50 V ✓"}], ["Häkchen", {"rcdok": 1}]]})
sc("""Ins Protokoll: *Berührungsspannung* OK und die längere Auslösezeit, *21* Millisekunden.""",
   {"type": "protocol", "fill": [["Berührungsspannung", "rcd", "ok"], ["21", "ta", "21 ms"]], "st": [[0, {"plug": 0, "F3trip": 0}]]})

# ------------------------------------------------------------------ 6 Erprobung
phase("Erprobung")
sc("""Zum Schluss drücke ich die *Prüftaste* am FI/LS: Er *löst* aus. Dann schalte ich ihn *wieder* ein.""",
   {"type": "pov", "cam": [[0, "F3", 0.45, -6, 6]], "st": [["löst", {"F3trip": 1}], ["wieder", {"F3trip": 0}]], "fl": [[0, {"pose": HOLD, "note": ""}]],
    "cards": [["Prüftaste", "Prüftaste T am FI/LS"]]})
sc("""Funktion der Anlage testen, im Protokoll alles *ankreuzen*, *mängelfrei*, unterschreiben. Fertig.""",
   {"type": "protocol", "fill": [["ankreuzen", "funk", "ok"], ["ankreuzen", "rcdt", "ok"], ["mängelfrei", "frei", "ok"]]})
sc("""Hier noch mal alle *Einstellungen* auf einen Blick. *RLO*: F1 rot-grün, F4 250 Milliampere, F3 plus-minus, F2 Nullabgleich.
*RISO*: F4 500 Volt, TEST halten bis zum Piep. *Drehfeld*: rot L1, grün L2, blau L3, 123 heißt rechts. *Delta* T: F4 10 Milliampere, F2 mal 1,
F3 FI-Typ, F1 0 und 180 Grad. Mach dir einen *Screenshot* davon. Viel Erfolg!""",
   {"type": "card", "rows": [["RLO", "RLO", ["F1: L-PE (rot + grün)", "F4: 250 mA", "F3: ±", "F2: ZERO (2–6 s halten)", "TEST halten"]],
                             ["RISO", "RISO", ["F1: L-PE", "F4: 500 V", "F3: Pretest aus", "TEST halten bis Piep", "unten: U ≥ 500 V"]],
                             ["Drehfeld", "Drehfeld", ["rot → L1", "grün → L2", "blau → L3", "123 = rechts"]],
                             ["Delta", "ΔT (RCD)", ["F4: 10 mA", "F2: x1", "F3: FI-Typ", "F1: 0° und 180°", "TEST drücken"]]]})

# =====================================================================================
MAXW = 800
part, words = 0, 0
for s in S:
    w = len(s["text"].split())
    if words and words + w > MAXW:
        part, words = part + 1, 0
    s["part"] = part
    words += w
d = {"kb": 8, "label": "POV", "title": "Messen mit dem Fluke 1664 FC", "topics": PHASES, "sentences": S}
out = ROOT / "src" / "mess" / "script.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
tf = ROOT / "src" / "mess" / "timing.json"
if not tf.exists():
    tf.write_text('{"lines": []}\n')
tot = sum(len(s["text"].split()) for s in S)
print(f"Messen: {len(S)} Szenen, {tot} Wörter (~{tot / 150:.1f} min), {part + 1} Blöcke")
