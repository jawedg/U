#!/usr/bin/env python3
"""Prüfungs-Simulation AP Teil 2 Elektroniker/-in für Betriebstechnik (Winter 2026/27, Blechbearbeitungsmaschine).
Ablauf aus Sicht des Prüflings („Ich“, Stimme Charon) mit Prüfer (Stimme Orus):
Fertigmeldung → Fachgespräch → Besichtigen → Messen ohne Spannung → Messen mit Spannung → Erprobung/Übergabe.
Grundlage: IHK-Unterlagen W26 3090 B1/B2 (Anlage, Prüfprotokoll-Auszug DIN VDE 0100-600). Die Änderung ist ausgedacht,
Messwerte sind Beispielwerte. Ausgabe: src/pruef/script.json (kb = 7).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHASES = ["Fertigmeldung", "Fachgespräch", "Besichtigen", "Messen ohne Spannung", "Messen mit Spannung", "Erprobung & Übergabe"]
S = []
ph, phname = 0, "Start"
ICH, PRUEFER = "Charon", "Orus"


def phase(name):
    global ph, phname
    ph += 1
    phname = name


def sc(text, v, who="ich"):
    S.append({"topic": ph, "tname": phname, "text": " ".join(text.split()), "who": who, "voice": PRUEFER if who == "pruefer" else ICH, "v": v})


def it(text, cue):
    return {"text": text, "cue": cue}


def ich(text, v=None):
    sc(text, v or {"type": "talk"}, "ich")


def pr(text, v=None):
    sc(text, v or {"type": "talk"}, "pruefer")


# =====================================================================================
sc("""Stell dir vor: Es ist Prüfungstag, Abschlussprüfung Teil 2. Meine Anlage, die *Blechbearbeitungsmaschine*, steht fertig auf dem Gestell,
und meine *Änderung* ist eingebaut. In diesem Video bin ich du. Ich zeige dir, wie es jetzt weitergeht: die *Fertigmeldung*, das *Fachgespräch*,
die *Prüfung nach VDE 0100-600* mit allen Messungen und am Ende die *Übergabe*. Eins vorweg: Die Änderung in diesem Video habe ich mir ausgedacht.
Deine echte Änderung erfährst du erst am Prüfungstag. Die Messwerte sind Beispielwerte.""",
   {"type": "title"})

# ---------------------------------------------------------------- 1
phase("Fertigmeldung")
sc("""Phase eins: die *Fertigmeldung*.""", {"type": "phase"})
sc("""Das ist mein Gestell. Unten kommt die Einspeisung über den *CEE-Stecker* an die Klemmleiste *X1*. Oben links sitzt der *FI/LS* F3 für die Steckdose,
daneben die Sicherungen F1 und F2 und das *24-Volt-Netzteil*. Rechts davon der *Motorschutzschalter* F4 und die *Wendeschütze* Q1 und Q2 für den Haspelmotor.
In der Mitte meine *S7*, daneben die *Simulationsplatine*, und rechts die *Bedieneinheit* mit S1 bis S4 und den Meldeleuchten.""",
   {"type": "board", "hl": [["CEE-Stecker", "CEE", "X1"], ["FI/LS", "F3", "X5"], ["24-Volt-Netzteil", "F1", "F2", "T1"], ["Motorschutzschalter", "F4"],
                            ["Wendeschütze", "Q1", "Q2"], ["S7", "SPS"], ["Simulationsplatine", "X10"], ["Bedieneinheit", "BED"]]})
sc("""Meine Änderung war: Nach *3 Entleerungen* ist der Container voll. Dann soll die Meldeleuchte P2 *blinken*, ein neuer Vorgang mit S4 ist *gesperrt*,
und mit dem Taster S2 setze ich den Zähler wieder *zurück*. Dafür habe ich im Programm einen *Zähler* und einen Taktmerker ergänzt und die Pläne und die
Zuordnungsliste *handschriftlich* nachgetragen.""",
   {"type": "change", "items": [it("Nach 3 Entleerungen: Container voll", "Entleerungen"), it("P2 blinkt (1 Hz)", "blinken"), it("Start mit S4 gesperrt", "gesperrt"),
                                it("S2 setzt den Zähler zurück", "zurück"), it("Programm: Zähler CTU + Taktmerker", "Zähler"), it("Pläne + Zuordnungsliste nachgetragen", "handschriftlich")]})
ich("""Entschuldigung, ich bin fertig. Die Änderung ist eingebaut, getestet und in den Unterlagen nachgetragen.""")
pr("""Gut. Dann legen Sie mir bitte Ihre Unterlagen hin: die geänderten Pläne, die Zuordnungsliste, den Programmausdruck und Ihr Prüfprotokoll.
Ich schaue mir das und die Anlage kurz an.""")
sc("""Jetzt bereitet sich der Prüfer vor. Er vergleicht meine *Pläne* mit der Anlage, schaut auf die *Verdrahtung*, die *Aderfarben* und die *Beschriftung*
und prüft, ob die Änderung im *Programm* und in der *Zuordnungsliste* auftaucht. Mein Tipp: Melde dich erst fertig, wenn deine Unterlagen wirklich zur Änderung passen.""",
   {"type": "docs", "items": [it("Pläne ↔ Anlage", "Pläne"), it("Verdrahtung", "Verdrahtung"), it("Aderfarben", "Aderfarben"), it("Beschriftung", "Beschriftung"),
                              it("Änderung im Programm", "Programm"), it("Zuordnungsliste ergänzt", "Zuordnungsliste")]})

# ---------------------------------------------------------------- 2
phase("Fachgespräch")
sc("""Phase zwei: das *Fachgespräch*. Es dauert höchstens 20 Minuten. Der Prüfer will sehen, dass ich verstehe, was ich gebaut habe.""", {"type": "phase"})
pr("""Erklären Sie mir bitte kurz, was Sie geändert haben und wie Sie das im Programm umgesetzt haben.""")
ich("""Ich habe einen *Vorwärtszähler* eingefügt. Immer wenn die Klappe nach dem Entleeren wieder schließt, also wenn *B10* kommt, zählt er um eins hoch.
Bei *3* wird der Ausgang des Zählers gesetzt. Damit sperre ich den Start mit *S4*, und P2 blinkt über den *Taktmerker*. Mit *S2* setze ich den Zähler zurück.""",
    {"type": "talk", "focus": [["Vorwärtszähler", "SPS"], ["B10", "X10"], ["S4", "BED"]]})
pr("""Der Sensor B10 meldet ja die ganze Zeit, solange die Klappe zu ist. Warum zählt Ihr Zähler dann nicht ständig weiter?""")
ich("""Weil der Zählereingang auf die *positive Flanke* reagiert. Er zählt nur in dem Moment, in dem das Signal von 0 auf 1 wechselt, also einmal pro Schließvorgang.
Danach kann das Signal anstehen, so lange es will.""", {"type": "talk", "diagram": "flanke"})
pr("""Wie haben Sie verhindert, dass die Schütze Q1 und Q2 gleichzeitig anziehen?""")
ich("""*Doppelt*. Im Programm sind Rechts- und Linkslauf gegenseitig verriegelt. Und zusätzlich in der *Hardware*: Der Öffner von Q2 liegt vor der Spule von Q1,
und der Öffner von Q1 vor der Spule von Q2. Würden beide gleichzeitig anziehen, gäbe es einen *Kurzschluss* zwischen zwei Außenleitern.""",
    {"type": "talk", "diagram": "verriegelung", "focus": [["Doppelt", "Q1", "Q2"]]})
pr("""Auf welchen Wert haben Sie den Motorschutzschalter eingestellt, und warum?""")
ich("""Auf *3,25 Ampere*. Das ist der Bemessungsstrom vom *Leistungsschild*, 400 Volt im Dreieck. Höher eingestellt würde der Motor bei Überlast nicht geschützt,
niedriger würde der Schalter schon im normalen Betrieb auslösen.""", {"type": "talk", "focus": [["Ampere", "F4"]], "diagram": "typenschild"})
pr("""Warum hat die Steckdose einen FI/LS-Schalter mit 10 Milliampere?""")
ich("""Steckdosen bis 32 Ampere, die auch von Laien benutzt werden können, brauchen einen *zusätzlichen Schutz* durch eine Fehlerstrom-Schutzeinrichtung mit höchstens
*30 Milliampere*. Hier sind laut Vorgabe sogar 10 Milliampere vorgesehen. Der *FI-Teil* schützt Personen bei einem Fehlerstrom, und der *LS-Teil* mit B16 schützt die
Leitung bei Überlast und Kurzschluss.""", {"type": "talk", "focus": [["zusätzlichen", "F3", "X5"]]})
pr("""Was passiert, wenn bei Ihnen die Ader zum Schalter S1 abfällt?""")
ich("""S1 ist ein *Schließer*. Fällt die Ader ab, kommt kein Signal an der S7 an, die Anlage geht aus und lässt sich nicht einschalten. Das ist der *sichere Zustand*.
Gefährlich wäre ein AUS-Befehl mit Schließer. Deshalb nimmt man für AUS und Not-Halt immer *Öffner*, die sind drahtbruchsicher.""", {"type": "talk", "focus": [["Schließer", "BED"]]})
pr("""Gut. Bevor Sie die Anlage einschalten: Was prüfen Sie, und in welcher Reihenfolge?""")
ich("""Zuerst *besichtigen*. Dann die Messungen *ohne Spannung*: Durchgängigkeit des Schutzleiters und Isolationswiderstand. Erst wenn das in Ordnung ist,
schalte ich mit Ihrer Erlaubnis ein und messe *mit Spannung*: Fehlerstrom-Schutzeinrichtung und Drehfeld. Zum Schluss kommt die *Erprobung*, also der Funktionstest.""",
    {"type": "talk", "steps": [it("Besichtigen", "besichtigen"), it("Messen ohne Spannung", "ohne"), it("Messen mit Spannung", "mit"), it("Erprobung", "Erprobung")]})
pr("""Gut, dann zeigen Sie mir das bitte.""")

# ---------------------------------------------------------------- 3
phase("Besichtigen")
sc("""Phase drei: *Besichtigen*. Ich gehe das Protokoll Punkt für Punkt durch und sage dabei laut, was ich prüfe.""", {"type": "phase"})
sc("""*Schaltungsunterlagen*: komplett und mit der Änderung ergänzt. *Betriebsmittel*: richtig ausgewählt, nicht beschädigt und gekennzeichnet.
*Leitungsanschlüsse*: alles fest, sauber abisoliert, mit Aderendhülsen. *Leitungswahl*: schwarz 1,5 Quadratmillimeter im Hauptstromkreis, dunkelblau 0,75 für die
24 Volt, *grün-gelb* für den Schutzleiter und hellblau für den Neutralleiter. *Schutz* gegen direktes Berühren: alle Abdeckungen drauf, alles fingersicher.
Und die *Überstromschutzeinrichtungen*: F1 mit 6 Ampere, F3 B16, und F4 auf 3,25 Ampere eingestellt.""",
   {"type": "check", "title": "Besichtigung", "items": [it("Schaltungsunterlagen komplett + ergänzt", "Schaltungsunterlagen"), it("Betriebsmittel: Auswahl, keine Schäden, gekennzeichnet", "Betriebsmittel"),
                                                       it("Leitungsanschlüsse: fest, abisoliert, Aderendhülsen", "Leitungsanschlüsse"), it("Leitungswahl: 1,5 mm² sw · 0,75 mm² dbl (24 V)", "Leitungswahl"),
                                                       it("PE grün-gelb · N hellblau", "grün-gelb"), it("Schutz gegen direktes Berühren: fingersicher", "Schutz"),
                                                       it("Überstromschutz: F1 6 A · F3 B16 · F4 3,25 A", "Überstromschutzeinrichtungen")]})
sc("""Alles in *Ordnung*, also mache ich im Protokoll bei der Besichtigung überall mein Kreuz bei OK.""",
   {"type": "protocol", "fill": [["Ordnung", "bes", "all"]]})

# ---------------------------------------------------------------- 4
phase("Messen ohne Spannung")
sc("""Phase vier: *Messen ohne Spannung*. Bevor ich messe, sorge ich dafür, dass die Anlage wirklich spannungsfrei ist.""", {"type": "phase"})
sc("""Ich ziehe den *CEE-Stecker*. Damit ist *freigeschaltet*. Den Stecker lege ich so hin, dass ihn niemand wieder einstecken kann, das ist gegen *Wiedereinschalten* gesichert.
Und dann stelle ich mit dem zweipoligen Spannungsprüfer die *Spannungsfreiheit* fest. Vorher teste ich den Spannungsprüfer an einer bekannten Spannung.""",
   {"type": "tip", "title": "Sicherheitsregeln", "items": [it("Freischalten: CEE-Stecker ziehen", "freigeschaltet"), it("Gegen Wiedereinschalten sichern", "Wiedereinschalten"),
                                                         it("Spannungsfreiheit feststellen (2-polig)", "Spannungsfreiheit"), it("Spannungsprüfer vorher testen", "Vorher")]})
sc("""Erste Messung: *Durchgängigkeit des Schutzleiters*. Am Messgerät stelle ich *R-Low* ein. Zuerst mache ich den *Nullabgleich*, damit der Widerstand der Messleitungen
nicht mitgemessen wird. Dann messe ich vom *PE-Kontakt* des CEE-Steckers zu allen Punkten, die mit dem Schutzleiter verbunden sein müssen.""",
   {"type": "measure", "mode": "R LOW", "cam": [330, 520, 1.6], "vals": [["Nullabgleich", "0,00 Ω"]], "probes": [["Nullabgleich", "NULL", "NULL"], ["PE-Kontakt", "CEEPE", "PLATTE"]]})
sc("""Zur *Montageplatte*: 0,08 Ohm. Zum Schutzkontakt der *Steckdose*: 0,14 Ohm. Zum *Motor* über X1: 0,21 Ohm. Und zur *Bedieneinheit*: 0,11 Ohm.
Einen festen Grenzwert gibt es in der Norm dafür nicht. Der Wert muss *niedrig* sein und zur Leitungslänge passen, und das tut er. Ins Protokoll schreibe ich den größten Wert.""",
   {"type": "measure", "mode": "R LOW", "cam": [420, 390, 1.0],
    "probes": [["Montageplatte", "CEEPE", "PLATTE"], ["Steckdose", "CEEPE", "X5PE"], ["Motor", "CEEPE", "M1PE"], ["Bedieneinheit", "CEEPE", "BEDPE"]],
    "vals": [["Montageplatte", "0,08 Ω"], ["Steckdose", "0,14 Ω"], ["Motor", "0,21 Ω"], ["Bedieneinheit", "0,11 Ω"]], "limit": "niedrig + plausibel", "ok": "niedrig"})
sc("""In das Protokoll kommt: Durchgängigkeit des Schutzleiters, *gemessener* Wert 0,21 Ohm, OK.""", {"type": "protocol", "fill": [["gemessener", "pe", "0,21 Ω"]]})
sc("""Zweite Messung: der *Isolationswiderstand*. Vorher muss ich die Anlage vorbereiten. Ich *klemme* das Netzteil T1 ab, denn Elektronik kann die 500 Volt Messspannung nicht ab
und würde das Ergebnis verfälschen. Dann schalte ich F1, F3 und den Motorschutzschalter F4 *ein*, damit auch die Leitungen hinter den Schutzeinrichtungen mitgemessen werden.""",
   {"type": "tip", "title": "Vorbereitung Isolationsmessung", "items": [it("Netzteil T1 abklemmen (Elektronik!)", "klemme"), it("F1, F3, F4 einschalten", "ein"),
                                                                       it("Messspannung 500 V DC", "Messspannung"), it("Grenzwert: mindestens 1 MΩ", "Netzteil")]})
pr("""Warum schalten Sie die Sicherungen und den Motorschutzschalter vor der Isolationsmessung ein?""")
ich("""Damit die Leitungen *hinter* den Schutzeinrichtungen auch geprüft werden. Wären sie aus, würde ich nur bis zur Sicherung messen und einen Fehler dahinter nicht finden.""")
sc("""Jetzt messe ich mit *500 Volt* Gleichspannung an der Klemmleiste X1, genau die Kombinationen aus dem Protokoll. X1 Klemme 1 ist L1, 3 ist L2, 5 ist L3,
7 ist der Neutralleiter und 9 ist PE. Also zuerst *L1 gegen L2*, dann L1 gegen L3, danach L1 gegen N, anschließend L1 gegen PE, und so weiter, bis zuletzt *N gegen PE*.
Überall zeigt das Gerät *größer 500 Megaohm*. Der Grenzwert ist mindestens 1 Megaohm. Alles in Ordnung.""",
   {"type": "measure", "mode": "R ISO 500 V", "cam": [200, 520, 1.8],
    "probes": [["zuerst", "X1:1", "X1:3"], ["dann", "X1:1", "X1:5"], ["danach", "X1:1", "X1:7"], ["anschließend", "X1:1", "X1:9"], ["weiter", "X1:3", "X1:5"], ["zuletzt", "X1:7", "X1:9"]],
    "vals": [["zeigt", "> 500 MΩ"]], "limit": "≥ 1 MΩ", "ok": "Grenzwert"})
sc("""Für den *24-Volt-Kreis* gilt übrigens: Messspannung 250 Volt, Grenzwert 0,5 Megaohm. Die Werte trage ich in die *Tabelle* im Protokoll ein.""",
   {"type": "protocol", "fill": [["Tabelle", "iso", "> 500 MΩ"]]})

# ---------------------------------------------------------------- 5
phase("Messen mit Spannung")
sc("""Phase fünf: *Messen mit Spannung*. Ich klemme das Netzteil wieder an und kontrolliere den Anschluss.""", {"type": "phase"})
ich("""Die Messungen ohne Spannung sind in Ordnung. Darf ich die Anlage jetzt einschalten?""")
pr("""Ja, schalten Sie ein.""")
sc("""Ich stecke den CEE-Stecker ein und messe zuerst das *Drehfeld* an L1, L2 und L3. Das Gerät zeigt *Rechtsdrehfeld*. Damit dreht der Motor mit Q1 auch wirklich rechts herum.""",
   {"type": "measure", "mode": "DREHFELD", "cam": [200, 520, 1.8], "probes": [["Drehfeld", "X1:1", "X1:3"]], "vals": [["Rechtsdrehfeld", "rechts ↻"]], "limit": "Rechtsdrehfeld", "ok": "Rechtsdrehfeld"})
sc("""Jetzt die *Fehlerstrom-Schutzeinrichtung*, also der FI/LS F3 an der Steckdose. Am Gerät stelle ich *10 Milliampere* ein, Typ A, und stecke den Prüfadapter in die Steckdose.
Zuerst misst das Gerät die *Berührungsspannung*: 0,3 Volt. Erlaubt sind höchstens *50 Volt*.""",
   {"type": "measure", "mode": "RCD 10 mA", "cam": [520, 160, 1.9], "probes": [["Steckdose", "X5", "X5"]], "vals": [["Berührungsspannung", "U_B 0,3 V"]], "limit": "U_B ≤ 50 V", "ok": "Volt"})
sc("""Dann die *Auslösezeit* mit dem vollen Bemessungsfehlerstrom: Der FI/LS löst nach *18 Millisekunden* aus. Erlaubt sind höchstens 300 Millisekunden. Auch das passt.""",
   {"type": "measure", "mode": "RCD 10 mA", "cam": [520, 160, 1.9], "probes": [["Auslösezeit", "X5", "X5"]], "vals": [["Millisekunden", "t_A 18 ms"]], "limit": "t_A ≤ 300 ms", "ok": "passt", "trip": "Millisekunden"})
sc("""Ins Protokoll: *Berührungsspannung* OK, Auslösezeit *18* Millisekunden OK, *Drehfeld* rechts OK.""",
   {"type": "protocol", "fill": [["Berührungsspannung", "rcd", "ok"], ["18", "ta", "18 ms"], ["Drehfeld", "dreh", "ok"]]})

# ---------------------------------------------------------------- 6
phase("Erprobung & Übergabe")
sc("""Phase sechs: die *Erprobung*. Zuerst drücke ich am FI/LS die *Prüftaste*: Er löst aus. Ich schalte ihn wieder ein.""",
   {"type": "board", "cam": [140, 150, 2.2], "hl": [["Prüftaste", "F3"]], "states": [[0, {}], ["löst", {"F3trip": 1}], ["wieder", {}]]})
sc("""Dann teste ich die *Funktion*, so wie in der Beschreibung. S1 an: P1 leuchtet. Mit *S3* tippe ich den Motor im Rechtslauf, die Haspel wickelt auf, und *B13* meldet Material.
Ich drücke *S4*: Die Klappe geht auf, und sobald *B11* meldet, läuft der Motor links. Ist kein Material mehr da, geht alles *aus*, und die Klappe schließt.""",
   {"type": "board", "cam": [610, 330, 1.25], "hl": [["Funktion", "BED", "X10"]],
    "states": [[0, {}], ["an", {"P1": 1}], ["S3", {"P1": 1, "P11": 1, "Q1": 1}], ["B13", {"P1": 1, "P11": 1, "Q1": 1, "B13": 1}], ["S4", {"P1": 1, "B13": 1, "P12": 1}],
               ["B11", {"P1": 1, "B13": 1, "P12": 1, "B11": 1, "P10": 1, "Q2": 1}], ["aus", {"P1": 1, "B10": 1}]]})
sc("""Jetzt meine *Änderung*: Nach der dritten Entleerung *blinkt* P2, und S4 bewirkt nichts mehr. Mit *S2* setze ich zurück, P2 geht aus. Und zum Schluss löse ich noch den
Motorschutzschalter mit der *Prüftaste* aus: Motor und Ventil sind aus, P2 leuchtet. Wieder einschalten, mit S2 *quittieren*, fertig.""",
   {"type": "board", "cam": [610, 330, 1.25], "hl": [["Änderung", "BED"]],
    "states": [[0, {"P1": 1}], ["blinkt", {"P1": 1, "P2": "blink"}], ["S2", {"P1": 1}], ["Prüftaste", {"P1": 1, "P2": 1, "F4trip": 1}], ["quittieren", {"P1": 1}]]})
sc("""Alles funktioniert. Im Protokoll kreuze ich bei der Erprobung *Funktion* der Anlage und Funktion *RCD* an, setze das Kreuz bei
*mängelfrei* und unterschreibe.""", {"type": "protocol", "fill": [["Funktion", "funk", "ok"], ["RCD", "rcdt", "ok"], ["mängelfrei", "frei", "ok"]]})
ich("""Die Anlage ist geprüft und funktioniert. Hier ist mein ausgefülltes Prüfprotokoll mit den Unterlagen.""")
pr("""Danke. Dann schalten Sie die Anlage bitte aus und räumen Ihren Arbeitsplatz auf.""")
sc("""Und das war's. Zum Merken die *Reihenfolge*: Erst besichtigen. Dann *ohne Spannung* messen, Schutzleiter und Isolation. Dann mit *Erlaubnis* einschalten
und mit Spannung messen, Drehfeld und RCD. Dann die *Erprobung*. Und alles sauber ins *Protokoll*. Sag beim Messen immer laut, was du gerade machst und warum.
Dann sieht der Prüfer, dass du weißt, was du tust. Viel Erfolg bei deiner Prüfung!""",
   {"type": "tip", "title": "Reihenfolge merken", "items": [it("1. Besichtigen", "Reihenfolge"), it("2. Ohne Spannung: R-PE, R-ISO", "ohne"), it("3. Mit Erlaubnis einschalten", "Erlaubnis"),
                                                          it("4. Mit Spannung: Drehfeld, RCD", "Drehfeld"), it("5. Erprobung", "Erprobung"), it("6. Protokoll + laut erklären", "Protokoll")]})

# =====================================================================================
# Blöcke: alle Prüfer-Sätze in einen Block (eigene Stimme), Ich-Sätze in Blöcke bis ~800 Wörter
MAXW = 800
pr_idx = [i for i, s in enumerate(S) if s["who"] == "pruefer"]
part, words = 1, 0
for s in S:
    if s["who"] == "pruefer":
        s["part"] = 0
        continue
    w = len(s["text"].split())
    if words and words + w > MAXW:
        part, words = part + 1, 0
    s["part"] = part
    words += w
d = {"kb": 7, "label": "AP2", "title": "Prüfungssimulation", "topics": PHASES, "sentences": S}
out = ROOT / "src" / "pruef" / "script.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
tf = ROOT / "src" / "pruef" / "timing.json"
if not tf.exists():
    tf.write_text('{"lines": []}\n')
tot = sum(len(s["text"].split()) for s in S)
prw = sum(len(S[i]["text"].split()) for i in pr_idx)
print(f"Prüfung: {len(S)} Szenen, {tot} Wörter (~{tot / 150:.0f} min), Prüfer {prw} Wörter, Blöcke: {part + 1}")
