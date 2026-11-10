#!/usr/bin/env python3
"""Lernvideo Berufstheorie: Füllstandsmessung mit Ultraschall (Analogwertverarbeitung).
Teil 1: Prüfungsaufgabe Winter 2024/25 (2.4.1 Schaubild, 2.4.2 Digitalwerte) Schritt für Schritt.
Teil 2: eigenes Beispiel im Prüfungsstil (Wassertank 100 cm, 2,5 V … 7,5 V).
Ausgabe: src/lern_fs/script.json (kb = 6, dunkles Design wie Gemeinschaftskunde).
Cue-Wörter: werden ohne Satzzeichen verglichen ("1,5" -> "15"), deshalb Wort-Cues statt Zahlen.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOPICS = ["Die Aufgabe verstehen", "Abstand und Füllhöhe", "Schaubild (2.4.1)", "Digitalwerte (2.4.2)", "Eigenes Beispiel", "Zusammenfassung"]
S = []
topic_no, topic_name = 0, "Überblick"


def thema(name):
    global topic_no, topic_name
    topic_no += 1
    topic_name = name


def sc(text, v):
    S.append({"topic": topic_no, "tname": topic_name, "text": " ".join(text.split()), "v": v})


def it(text, cue):
    return {"text": text, "cue": cue}


CHIPS = ["Prüfungsaufgabe lösen", "Eigenes Beispiel", "Schritt für Schritt"]

# =====================================================================================
sc("""Hallo! Heute rechnen wir zusammen eine typische Prüfungsaufgabe aus Berufstheorie: die *Füllstandsmessung* mit einem *Ultraschallsensor*.
Genau so eine Aufgabe kam in einer echten Abschlussprüfung dran. Wir machen das in zwei Durchgängen. Zuerst lösen wir die Prüfungsaufgabe *Schritt für Schritt*,
mit Bild, Schaubild und Rechnung. Danach rechnen wir ein *eigenes Beispiel*, das genauso aufgebaut ist. So siehst du, dass das Rezept immer gleich funktioniert.
Nimm dir ruhig Stift und Papier und rechne mit.""",
   {"type": "kb", "hero": "Füllstands­messung", "kicker": "Berufstheorie · Analogwerte", "chips": CHIPS})

# ---------------------------------------------------------------- 1
thema("Die Aufgabe verstehen")
T = lambda text: sc(text, {"type": "topic"})
T("""Schritt eins: *Die Aufgabe verstehen*.""")
TANK1 = {"type": "tank", "range": 20, "vTop": 1.5, "vBot": 8}
sc("""Schau dir das Bild an. *Oben* auf dem Behälter sitzt ein Ultraschallsensor. Der schickt einen Schallimpuls nach unten. Der Schall *prallt* an der Oberfläche
der Flüssigkeit ab und kommt als *Echo* zurück. Aus der Laufzeit weiß der Sensor, wie weit die Oberfläche weg ist. Ganz wichtig: Der Sensor *misst* also
den *Abstand* von oben, nicht die Füllhöhe von unten.""",
   {**TANK1, "levels": [[0, 0.45]], "show": {"abstand": "Abstand"}, "label": "So funktioniert der Sensor",
    "items": [it("Sensor sitzt oben", "Oben"), it("Schall prallt an der Oberfläche ab", "prallt"), it("Echo kommt zurück", "Echo"), it("Gemessen wird der Abstand von oben", "misst")]})
sc("""Direkt unter dem Sensor gibt es eine *Blindzone*. Das ist der Bereich, in dem der Sensor das Echo *nicht erkennen* kann. Deshalb fängt der *Messbereich* erst
unter der Blindzone an. In unserer Aufgabe ist der Messbereich 20 Zentimeter groß.""",
   {**TANK1, "levels": [[0, 0.45]], "show": {"abstand": 0, "blind": "Blindzone"}, "label": "Blindzone",
    "items": [it("Blindzone: Echo wird nicht erkannt", "Blindzone"), it("Messbereich beginnt unter der Blindzone", "Messbereich"), it("Messbereich hier: 20 cm", "Zentimeter")]})
sc("""Was ist gegeben? Der Sensor hängt an einer *Analogeingabe* von 0 bis 10 Volt. Am *Anfang* des Messbereichs, also bei 0 Zentimeter Abstand direkt unter der Blindzone,
liefert er 1,5 Volt. Am *Ende*, bei 20 Zentimeter Abstand, liefert er 8 Volt. *Außerdem* wissen wir: 0 Volt entspricht dem Digitalwert 0, und 10 Volt entspricht dem Digitalwert 27648.""",
   {"type": "points", "label": "Gegeben", "title": "Was wissen wir?",
    "items": [it("Analogeingabe 0 … 10 V", "Analogeingabe"), it("Abstand 0 cm  →  1,5 V", "Anfang"), it("Abstand 20 cm  →  8 V", "Ende"),
              it("0 V ≙ 0   ·   10 V ≙ 27648", "Außerdem")]})

# ---------------------------------------------------------------- 2
thema("Abstand und Füllhöhe")
T("""Schritt zwei: *Abstand* und *Füllhöhe* richtig zuordnen. Das ist die Stelle, an der die meisten Fehler passieren.""")
sc("""Überleg mal: Wann ist der Abstand klein? Wenn die Oberfläche nah am Sensor ist, also wenn der Behälter *voll* ist. Und wann ist der Abstand groß?
Wenn der Behälter *leer* ist und der Schall bis ganz nach unten muss. Abstand und Füllhöhe laufen also genau *entgegengesetzt*.""",
   {**TANK1, "levels": [[0, 0.45], ["voll", 1.0], ["leer", 0.0], ["entgegengesetzt", 0.5]], "show": {"abstand": 0, "fuell": 0, "blind": 0, "scale": 0},
    "label": "Abstand ↔ Füllhöhe",
    "items": [it("voll  →  kleiner Abstand  →  1,5 V", "voll"), it("leer  →  großer Abstand  →  8 V", "leer"), it("Abstand und Füllhöhe: entgegengesetzt", "entgegengesetzt")]})
sc("""Daraus machen wir eine kleine Tabelle. Behälter *voll*: Abstand 0 Zentimeter, Füllhöhe 20 Zentimeter, Spannung 1,5 Volt.
Behälter *leer*: Abstand 20 Zentimeter, Füllhöhe 0 Zentimeter, Spannung 8 Volt. *Merk* dir: Voller Behälter heißt hier kleine Spannung.""",
   {"type": "table", "title": "Zuordnung", "head": ["Behälter", "Abstand", "Füllhöhe", "Spannung"],
    "rows": [{"cells": ["voll", "0 cm", "20 cm", "1,5 V"], "cue": "voll"}, {"cells": ["leer", "20 cm", "0 cm", "8 V"], "cue": "leer"}],
    "note": "Voller Behälter = kleine Spannung!", "cueNote": "Merk"})
sc("""Kurze Frage an dich: Der Behälter ist halb voll, also 10 Zentimeter Füllhöhe. Ist die Spannung dann größer oder kleiner als 8 Volt? Überleg kurz …
*Richtig*: kleiner. Je voller der Behälter, desto kleiner die Spannung. Bei halb voll liegt sie genau in der Mitte zwischen 1,5 und 8 Volt, also bei 4,75 Volt.""",
   {"type": "quiz", "q": "Halb voll (10 cm Füllhöhe): Ist die Spannung größer oder kleiner als 8 V?", "a": "Kleiner – genau in der Mitte: 4,75 V", "cueA": "Richtig"})

# ---------------------------------------------------------------- 3
thema("Schaubild (2.4.1)")
T("""Schritt drei: das *Schaubild*. Das ist Aufgabe 2 Punkt 4 Punkt 1.""")
G1 = {"type": "graph", "title": "Aufgabe 2.4.1 · Schaubild", "xMax": 20, "xStep": 5, "yMax": 10, "xLabel": "Füllhöhe FH in cm", "yLabel": "U in V"}
P1 = [{"x": 0, "y": 8, "cue": "Erster", "label": "(0 cm | 8 V)"}, {"x": 20, "y": 1.5, "cue": "Zweiter", "label": "(20 cm | 1,5 V)"}]
sc("""Wir zeichnen ein Koordinatensystem. Nach rechts kommt die Füllhöhe in Zentimeter, von 0 bis 20. Nach oben kommt die Spannung in Volt, von 0 bis 10.
Jetzt setzen wir unsere zwei Punkte aus der Tabelle ein. *Erster* Punkt: Füllhöhe 0 Zentimeter, Spannung 8 Volt. *Zweiter* Punkt: Füllhöhe 20 Zentimeter,
Spannung 1,5 Volt. Und jetzt *verbinden* wir die beiden Punkte mit einer Geraden. Fertig ist das Schaubild: eine *fallende Gerade*.""",
   {**G1, "points": P1, "lineCue": "verbinden"})
sc("""Warum eine Gerade? Weil der Sensor *linear* arbeitet: Jeder Zentimeter verändert die Spannung um gleich viel. Wie viel genau? Die Spannung *fällt* um 8 minus 1,5,
also um 6,5 Volt, auf 20 Zentimeter. 6,5 geteilt durch 20 ergibt 0,325 Volt pro Zentimeter. Die Steigung ist also minus 0,325 Volt pro Zentimeter, minus, weil die Gerade fällt.
Damit können wir sogar eine *Formel* aufschreiben: U gleich 8 Volt minus 0,325 Volt pro Zentimeter mal Füllhöhe.""",
   {**G1, "points": [{**p, "cue": 0} for p in P1], "lineCue": 0, "slope": {"cue": "fällt", "dx": "ΔFH = 20 cm", "dy": "ΔU = −6,5 V"},
    "formula": {"text": "U = 8 V − 0,325 V/cm · FH", "cue": "Formel"}})
sc("""Machen wir die *Probe* mit 20 Zentimeter. 0,325 *mal* 20 sind 6,5. Und 8 minus 6,5 sind 1,5 Volt. *Passt* genau zu unserem zweiten Punkt.""",
   {"type": "calc", "title": "Probe", "lines": [{"t": "FH = 20 cm", "cue": "Probe"}, {"t": "U = 8 V − 0,325 V/cm · 20 cm", "cue": "mal"},
                                                 {"t": "U = 8 V − 6,5 V = 1,5 V  ✓", "cue": "Passt", "kind": "result"}]})

# ---------------------------------------------------------------- 4
thema("Digitalwerte (2.4.2)")
T("""Schritt vier: die *Digitalwerte*. Das ist Aufgabe 2 Punkt 4 Punkt 2.""")
sc("""Die Analogbaugruppe wandelt die Spannung in eine *Zahl* um. 0 Volt wird zur 0, und 10 Volt wird zu 27648. Dazwischen ist es wieder *linear*.
Stell dir zwei Lineale übereinander vor: oben Volt, unten Digitalwerte. Was oben bei 5 Volt steht, steht unten genau in der *Mitte*, bei 13824.""",
   {"type": "scales", "title": "Spannung ↔ Digitalwert", "markers": [{"v": 5, "cue": "Mitte", "top": "5 V", "bottom": "13824"}]})
sc("""Wir rechnen mit dem *Dreisatz*. 10 Volt entsprechen 27648. Für 1 Volt teilen wir *durch* 10. Das *ergibt* 2764,8 pro Volt. Diese Zahl brauchst du gleich für alles.""",
   {"type": "calc", "title": "Dreisatz", "head": "Erst auf 1 Volt", "lines": [{"t": "10 V  ≙  27648", "cue": "Dreisatz"}, {"t": " 1 V  ≙  27648 : 10", "cue": "durch"},
                                                                              {"t": " 1 V  ≙  2764,8", "cue": "ergibt", "kind": "result"}]})
sc("""Behälter *leer*: Da liegen 8 Volt an. 8 mal 2764,8 ergibt 22118,4. Ein Digitalwert ist immer eine ganze Zahl, also *runden* wir: 22118.
Behälter *voll*: Da liegen 1,5 Volt an. 1,5 mal 2764,8 ergibt 4147,2, *gerundet* 4147.""",
   {"type": "calc", "title": "Aufgabe 2.4.2 · Lösung", "lines": [{"t": "leer:  8 V · 2764,8 = 22118,4", "cue": "leer"}, {"t": "→  22118", "cue": "runden", "kind": "result"},
                                                               {"t": "voll:  1,5 V · 2764,8 = 4147,2", "cue": "voll"}, {"t": "→  4147", "cue": "gerundet", "kind": "result"}]})
sc("""Hier siehst du beides noch mal auf den Linealen. *Leer* liegt rechts bei 22118, *voll* liegt links bei 4147. Das ist die *Lösung* von Aufgabe 2 Punkt 4 Punkt 2.
Und auch hier gilt: Voll ist die kleinere Zahl, weil die Spannung kleiner ist.""",
   {"type": "scales", "title": "Ergebnis 2.4.2", "markers": [{"v": 8, "cue": "Leer", "top": "8 V · leer", "bottom": "22118"},
                                                            {"v": 1.5, "cue": "voll", "top": "1,5 V · voll", "bottom": "4147"}]})
sc("""Das Rezept für solche Aufgaben, in drei Schritten. Erstens: Klären, welche Spannung zu leer und welche zu voll gehört. Zweitens: den Digitalwert pro Volt ausrechnen.
Drittens: Spannung mal Digitalwert pro Volt, und am Ende auf eine ganze Zahl runden.""",
   {"type": "merke", "text": "1. Spannung für leer / voll zuordnen  ·  2. Digitalwert pro Volt: 27648 : 10 = 2764,8  ·  3. Spannung × 2764,8 – auf ganze Zahl runden"})

# ---------------------------------------------------------------- 5
thema("Eigenes Beispiel")
T("""Schritt fünf: ein *eigenes Beispiel*. Ich habe dir eine Aufgabe gebaut, die genauso aufgebaut ist wie in der Prüfung.""")
sc("""Die Aufgabe: Ein Wassertank hat einen Messbereich von 100 Zentimetern. Oben sitzt wieder ein Ultraschallsensor an einer *Analogeingabe* von 0 bis 10 Volt, also 0 bis 27648.
Direkt unter der *Blindzone*, also bei 0 Zentimeter Abstand, liefert er 2,5 Volt. Am *Ende* des Messbereichs, bei 100 Zentimeter Abstand, liefert er 7,5 Volt.
Gesucht sind drei Dinge. *Erstens*: die Digitalwerte für leer und voll. *Zweitens*: Spannung und Digitalwert bei 30 Zentimeter Füllhöhe.
Und *drittens*: die Füllhöhe, wenn die Steuerung den Digitalwert 13824 anzeigt.""",
   {"type": "points", "label": "Neue Aufgabe", "title": "Wassertank · Messbereich 100 cm",
    "items": [it("Analogeingabe 0 … 10 V  (0 … 27648)", "Analogeingabe"), it("Abstand 0 cm  →  2,5 V", "Blindzone"), it("Abstand 100 cm  →  7,5 V", "Ende"),
              it("a) Digitalwerte leer und voll", "Erstens"), it("b) Spannung + Digitalwert bei FH = 30 cm", "Zweitens"), it("c) Füllhöhe bei Digitalwert 13824", "drittens")]})
TANK2 = {"type": "tank", "range": 100, "vTop": 2.5, "vBot": 7.5}
sc("""Erster Schritt, wie vorhin: zuordnen. *Voll* heißt kleiner Abstand, also 2,5 Volt. *Leer* heißt großer Abstand, also 7,5 Volt. *Gleiches* Prinzip, nur andere Zahlen.""",
   {**TANK2, "levels": [[0, 0.5], ["Voll", 1.0], ["Leer", 0.0], ["Gleiches", 0.5]], "show": {"abstand": 0, "fuell": 0, "blind": 0, "scale": 0}, "label": "Zuordnen",
    "items": [it("voll  →  2,5 V", "Voll"), it("leer  →  7,5 V", "Leer")]})
sc("""Teil a. *Pro* Volt sind es wieder 2764,8, denn die Baugruppe ist dieselbe. *Leer*: 7,5 mal 2764,8 ergibt 20736. *Voll*: 2,5 mal 2764,8 ergibt 6912.
Diesmal sind es sogar glatte Zahlen.""",
   {"type": "calc", "title": "Teil a · Digitalwerte", "lines": [{"t": "pro Volt: 27648 : 10 = 2764,8", "cue": "Pro"}, {"t": "leer:  7,5 V · 2764,8 = 20736", "cue": "Leer", "kind": "result"},
                                                              {"t": "voll:  2,5 V · 2764,8 = 6912", "cue": "Voll", "kind": "result"}]})
G2 = {"type": "graph", "title": "Teil b · Schaubild", "xMax": 100, "xStep": 10, "yMax": 10, "xLabel": "Füllhöhe FH in cm", "yLabel": "U in V"}
sc("""Teil b. Dafür zeichnen wir wieder die Gerade durch unsere zwei *Punkte*: 0 Zentimeter bei 7,5 Volt und 100 Zentimeter bei 2,5 Volt. Die Spannung *fällt* um 5 Volt
auf 100 Zentimeter. Das sind 0,05 Volt pro Zentimeter. Jetzt *lesen* wir bei 30 Zentimeter ab.""",
   {**G2, "points": [{"x": 0, "y": 7.5, "cue": "Punkte", "label": "(0 cm | 7,5 V)"}, {"x": 100, "y": 2.5, "cue": "und", "label": "(100 cm | 2,5 V)"}], "lineCue": "fällt",
    "slope": {"cue": "fällt", "dx": "ΔFH = 100 cm", "dy": "ΔU = −5 V"}, "mark": {"x": 30, "cue": "lesen", "label": "6 V"}})
sc("""Bei 30 Zentimeter Füllhöhe ist die Spannung um 30 mal 0,05, also um 1,5 Volt *gefallen*. 7,5 *minus* 1,5 ergibt 6 Volt. Und der *Digitalwert*: 6 mal 2764,8 ergibt 16588,8,
*gerundet* 16589.""",
   {"type": "calc", "title": "Teil b · Rechnung", "lines": [{"t": "ΔU = 30 cm · 0,05 V/cm = 1,5 V", "cue": "gefallen"}, {"t": "U  = 7,5 V − 1,5 V = 6 V", "cue": "minus", "kind": "result"},
                                                          {"t": "D  = 6 V · 2764,8 = 16588,8", "cue": "Digitalwert"}, {"t": "→  16589", "cue": "gerundet", "kind": "result"}]})
sc("""Und jetzt Teil c. Versuch es erst selbst: Die Steuerung zeigt 13824. Welche Füllhöhe ist das? Überleg kurz … Die *Lösung*: 13824 ist genau die Hälfte von 27648,
also liegen 5 Volt an. Von 7,5 Volt runter auf 5 Volt sind es 2,5 Volt. 2,5 geteilt durch 0,05 ergibt 50 Zentimeter. Der Tank ist also halb voll.""",
   {"type": "quiz", "q": "Teil c: Die Steuerung zeigt 13824. Welche Füllhöhe ist das?", "a": "13824 ≙ 5 V  →  7,5 V − 5 V = 2,5 V  →  2,5 : 0,05 = 50 cm (halb voll)", "cueA": "Lösung"})
sc("""Im Bild siehst du es: Der Tank ist *halb* voll, der Sensor liefert 5 Volt, und die Steuerung zeigt 13824.""",
   {**TANK2, "levels": [[0, 0.3], ["halb", 0.5]], "show": {"abstand": 0, "fuell": 0, "blind": 0, "scale": 0}, "label": "Teil c · Ergebnis",
    "items": [it("13824  ≙  5 V", "halb"), it("Füllhöhe = 50 cm", "Steuerung")]})

# ---------------------------------------------------------------- 6
thema("Zusammenfassung")
T("""Zum Schluss die *Zusammenfassung*.""")
sc("""Fassen wir zusammen. *Erstens*: Ein Ultraschallsensor misst den Abstand von oben. Kleiner Abstand heißt voller Behälter. *Zweitens*: Im Schaubild entsteht eine Gerade
durch die zwei bekannten Punkte. *Drittens*: Bei 0 bis 10 Volt und 27648 sind es immer 2764,8 pro Volt. Und *viertens*: Spannung mal 2764,8, dann auf eine ganze Zahl runden.""",
   {"type": "points", "title": "Das musst du können",
    "items": [it("Ultraschall misst den Abstand von oben – kleiner Abstand = voll", "Erstens"), it("Schaubild: Gerade durch zwei bekannte Punkte", "Zweitens"),
              it("0 … 10 V ≙ 0 … 27648  →  2764,8 pro Volt", "Drittens"), it("Spannung × 2764,8, dann runden", "viertens")]})
sc("""Und ein Prüfungstipp: Schreib immer die Formel, die Rechnung und das Ergebnis mit Einheit hin. Auch wenn du dich mal verrechnest, gibt es für einen richtigen Rechenweg
meistens noch Teilpunkte.""",
   {"type": "merke", "text": "Prüfungstipp: Formel  →  Rechnung  →  Ergebnis mit Einheit. Der Rechenweg bringt Punkte!"})
topic_no, topic_name = 0, "Geschafft"
sc("""Das war's! Jetzt kannst du solche Füllstandsaufgaben Schritt für Schritt lösen. Viel Erfolg in der Prüfung!""",
   {"type": "kb", "outro": True, "chips": CHIPS})

# =====================================================================================
MAX_WORDS = 800
part, words = 0, 0
for s in S:
    w = len(s["text"].split())
    if words and words + w > MAX_WORDS:
        part, words = part + 1, 0
    s["part"] = part
    words += w
d = {"kb": 6, "label": "BT", "title": "Füllstandsmessung", "topics": TOPICS, "sentences": S}
out = ROOT / "src" / "lern_fs" / "script.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
tf = ROOT / "src" / "lern_fs" / "timing.json"
if not tf.exists():
    tf.write_text('{"lines": []}\n')
total = sum(len(s["text"].split()) for s in S)
print(f"Füllstand: {len(S)} Szenen, {total} Wörter (~{total / 150:.0f} min), {part + 1} Blöcke")
