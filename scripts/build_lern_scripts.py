#!/usr/bin/env python3
"""Baut die 4 ausführlichen Lernvideos (KB I–IV) nach dem Lernzettel des Nutzers
(WiSo_Lernzettel_Wirtschaft_KB_I-IV.pdf). Ausgabe: src/lern_kb1..4/script.json

Jede Szene: topic (Themen-Nr., 0 = KB-Einstieg/Abschluss), tname (Themenname), text (gesprochen, *Wort* = betont),
v (Bild). Items erscheinen, wenn ihr cue-Wort gesprochen wird. part (Sprach-Block) wird automatisch vergeben.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = {}
cur = None
topic_no = 0
topic_name = ""


def kb(n, title, topics):
    global cur, topic_no, topic_name
    cur = {"kb": n, "title": title, "topics": topics, "sentences": []}
    KB[n] = cur
    topic_no, topic_name = 0, "Überblick"


def thema(name):
    global topic_no, topic_name
    topic_no += 1
    topic_name = name


def sc(text, v):
    cur["sentences"].append({"topic": topic_no, "tname": topic_name, "text": " ".join(text.split()), "v": v})


def it(text, cue, **kw):
    return {"text": text, "cue": cue, **kw}


def T(text):  # Themen-Startbild
    sc(text, {"type": "topic"})


def P(text, title, items, label=None, note=None):
    sc(text, {"type": "points", "title": title, "label": label, "items": items, "note": note})


def D(text, term, definition, cue=None):
    sc(text, {"type": "def", "term": term, "text": definition, "cue": cue or ""})


def C(text, lt, li, rt, ri, cue_right, note=None):
    sc(text, {"type": "compare", "left": {"title": lt, "items": li}, "right": {"title": rt, "items": ri}, "cueRight": cue_right, "note": note})


def TB(text, title, head, rows, note=None):
    sc(text, {"type": "table", "title": title, "head": head, "rows": [{"cells": r[0], "cue": r[1], "hl": (len(r) > 2 and r[2])} for r in rows], "note": note})


def X(text, steps, title="Was passiert?"):
    sc(text, {"type": "case", "title": title, "items": steps})


def M(text, merke):
    sc(text, {"type": "merke", "text": merke})


def BIG(text, big, sub=None, items=None):
    sc(text, {"type": "big", "big": big, "sub": sub, "items": items or []})


def F(text, parts, note=None):
    sc(text, {"type": "formula", "parts": parts, "note": note})


def RAW(text, v):
    sc(text, v)


def Q(text, question, answer, cue_answer):  # Quizfrage an den Zuschauer
    sc(text, {"type": "quiz", "q": question, "a": answer, "cueA": cue_answer})


# =====================================================================================
# KB I – im Lehrer-Erklärstil
# =====================================================================================
kb(1, "Die Rolle des Mitarbeiters in der Arbeitswelt",
   ["Duale Ausbildung", "Ausbildungsvertrag", "Schutzgesetze", "Arbeitsvertrag", "Kündigung und Kündigungsschutz", "Arbeitszeugnis",
    "Betriebsrat", "Tarifvertrag und Arbeitskampf", "Sozialversicherung", "Lohnabrechnung", "Steuererklärung"])
sc("""Hallo und willkommen! Heute geht es um Kompetenzbereich eins, also um *dich* als Mitarbeiter: von der Ausbildung über deinen Arbeitsvertrag
bis zu deiner Lohnabrechnung. Das Gute an diesem Bereich: Du *erlebst* das alles gerade selbst. Deshalb erkläre ich dir jedes Thema so,
dass du es mit deinem eigenen Alltag verbinden kannst. Wir gehen die *elf Themen* in der Reihenfolge deines Lernzettels durch.
Zwischendurch stelle ich dir kurze Fragen, also mach ruhig kurz Pause, wenn du überlegen willst.""",
   {"type": "kb"})

# ---------------------------------------------------------------- 1
thema("Duale Ausbildung")
T("""Fangen wir an mit Thema eins: der *dualen Ausbildung*.""")
C("""Überleg mal kurz, wie deine Woche aussieht. Ein paar Tage bist du im Betrieb, stehst an der Anlage, verdrahtest Schaltschränke. Und dann sitzt du wieder in der Berufsschule.
Genau das meint *dual*: Das Wort heißt einfach *zwei*. Du lernst an zwei *Lernorten*. Im *Betrieb* lernst du die *Praxis*, also wie man es *macht*.
In der *Berufsschule* lernst du die *Theorie*, also *warum* man es so macht. Und damit beide wissen, was sie dir beibringen sollen, hat jeder seinen eigenen Plan:
Der Betrieb hält sich an die *Ausbildungsordnung*. Die kommt vom *Bund*, gilt also in ganz Deutschland gleich, und darin steckt der *Ausbildungsrahmenplan*.
Die Berufsschule hält sich an den *Rahmenlehrplan*, und der kommt vom *Land*, bei dir also von Baden-Württemberg. Bildung ist nämlich Ländersache.""",
  "Betrieb", ["Praxis – wie man es macht", "Ausbildungsordnung (Bund)", "darin: Ausbildungsrahmenplan"],
  "Berufsschule", ["Theorie – warum man es so macht", "Rahmenlehrplan (Land)"], "Berufsschule")
P("""Jetzt kommt eine typische Prüfungsfrage: Wer ist eigentlich alles an deiner Ausbildung *beteiligt*? Es sind *sechs*.
Da bist natürlich *du*, der *Auszubildende*. Deine Aufgabe ist zu lernen. Dann der *Ausbildende*. Und jetzt aufpassen, das klingt fast gleich, ist aber was anderes:
Der Ausbildende ist die *Firma*. Die schließt den Vertrag mit dir und zahlt dir die Vergütung. Der *Ausbilder* dagegen ist eine *Person*, also der Meister oder Geselle,
der dir wirklich zeigt, wie es geht. Und der muss *persönlich und fachlich geeignet* sein. Nicht jeder darf also ausbilden.
Dann haben wir die *Berufsschule*, die *Kammer*, also IHK oder Handwerkskammer, die deine Ausbildung *überwacht*, dich bei Problemen *berät* und am Ende die *Prüfung* abnimmt.
Und zuletzt die *Eltern*: Bist du noch nicht achtzehn, unterschreiben die deinen Vertrag mit.""",
  "Die 6 Beteiligten", [it("Auszubildender – lernt", "Auszubildende"), it("Ausbildender = Firma – Vertrag, Vergütung", "Ausbildende"),
                         it("Ausbilder = Person – persönlich & fachlich geeignet", "Ausbilder"), it("Berufsschule – Theorie", "Berufsschule"),
                         it("Kammer (IHK/HWK) – überwacht, berät, prüft", "Kammer"), it("Eltern – unterschreiben unter 18", "Eltern")])
C("""Warum macht man das überhaupt so kompliziert mit zwei Lernorten? Weil es echte *Vorteile* hat. Du lernst *Praxis und Theorie* zusammen, also nicht nur Bücherwissen.
Du verdienst schon *Geld*, und viele Betriebe *übernehmen* ihre Azubis danach, weil sie sie ja schon kennen. Es gibt aber auch einen *Nachteil*:
Die *Qualität* hängt stark vom Betrieb ab. Ein guter Betrieb nimmt sich Zeit für dich. Ein schlechter lässt dich vielleicht nur Kabel schleppen.""",
  "Vorteile", ["Praxis + Theorie", "schon Geld verdienen", "Übernahmechance"], "Nachteil", ["Qualität hängt vom Betrieb ab"], "Nachteil")
Q("""Kurze Frage an dich: Wer ist der *Ausbildende*, und wer ist der *Ausbilder*? Überleg kurz … Genau: Der *Ausbildende* ist die *Firma*, die den Vertrag macht und zahlt.
Der *Ausbilder* ist die *Person*, die dich ausbildet. Und das ist auch schon das Merke zu diesem Thema.""",
  "Wer ist der Ausbildende – und wer der Ausbilder?", "Ausbildender = Firma (Vertrag, Geld) · Ausbilder = Person (bildet aus)", "Genau")

# ---------------------------------------------------------------- 2
thema("Ausbildungsvertrag")
T("""Thema zwei: der *Ausbildungsvertrag*, also das Papier, das deine ganze Ausbildung regelt.""")
P("""Wie kommt so ein Vertrag zustande? Er wird *schriftlich* gemacht, und zwar *vor Beginn* der Ausbildung. Beide *unterschreiben*, und dann wird er bei der *Kammer eingetragen*.
Warum bei der Kammer? Weil die ja deine Ausbildung überwachen soll, also muss sie wissen, dass es dich gibt. Bist du *unter achtzehn*, kommen zwei Dinge dazu:
Deine *Eltern* unterschreiben mit, und du brauchst eine *ärztliche Erstuntersuchung*. Damit soll sichergestellt werden, dass dir die Arbeit gesundheitlich nicht schadet.""",
  "So entsteht der Vertrag", [it("schriftlich, vor Beginn", "schriftlich"), it("unterschrieben", "unterschreiben"), it("bei der Kammer eingetragen", "Kammer"),
                              it("unter 18: Eltern + ärztliche Erstuntersuchung", "Eltern")])
P("""Was steht drin? Im Grunde alles, worüber es später Streit geben könnte. Der *Beruf*, *Beginn und Dauer*, die tägliche *Ausbildungszeit*,
die *Probezeit*, die dauert *ein bis vier Monate*, die *Vergütung*, die übrigens jedes Lehrjahr *steigt*, der *Urlaub* und die Regeln zur *Kündigung*.""",
  "Inhalt", [it("Beruf · Beginn und Dauer · Ausbildungszeit", "Beruf"), it("Probezeit 1–4 Monate", "Probezeit"), it("Vergütung (steigt jährlich)", "Vergütung"),
             it("Urlaub, Kündigung", "Urlaub")])
C("""Aus dem Vertrag folgen *Pflichten*, und zwar für beide Seiten. Das kannst du dir wie zwei Seiten einer Münze vorstellen: Was für dich eine Pflicht ist, ist für den anderen meistens ein Recht.
Du musst *lernen*, in die *Berufsschule* gehen, dein *Berichtsheft* führen, *Weisungen* befolgen, *sorgfältig* arbeiten und über Betriebsgeheimnisse *schweigen*.
Der Betrieb muss dich wirklich *ausbilden*, dir *Werkzeug kostenlos* geben, dich für Berufsschule und Prüfung *freistellen*, dich *bezahlen* und dir am Ende ein *Zeugnis* ausstellen.
Und ganz wichtig: Er darf dir keine *ausbildungsfremden* Arbeiten geben. Also: Arbeitsplatz aufräumen, das gehört dazu, das musst du auch als Elektriker können.
Aber jeden Tag nur Kaffee holen oder das Auto vom Chef waschen? Das hat mit deinem Beruf nichts zu tun, das darf er nicht verlangen.""",
  "Pflichten Azubi", ["lernen", "Berufsschule", "Berichtsheft", "Weisungen befolgen", "sorgfältig, schweigen"],
  "Pflichten Betrieb", ["ausbilden", "Werkzeug kostenlos", "freistellen", "zahlen, Zeugnis", "keine ausbildungsfremden Arbeiten"], "Betrieb",
  note="Arbeitsplatz aufräumen ✅ · jeden Tag Kaffee holen ❌")
X("""Und wenn es doch mal kracht? Dann gehst du nicht gleich vor Gericht, sondern Schritt für Schritt. Erst das *Gespräch* mit deinem Ausbilder, oft klärt sich da schon viel.
Hilft das nicht, gehst du zum *Betriebsrat* oder zur *JAV*, das ist die Jugend- und Auszubildendenvertretung, quasi die Interessenvertretung für junge Leute im Betrieb.
Danach die *Kammer*, die hat extra Ausbildungsberater. Und erst ganz am Ende das *Arbeitsgericht*. Übrigens: Bevor ein Betrieb einem Azubi kündigt, gibt es meistens vorher eine *Abmahnung*,
also eine Art gelbe Karte.""",
  [it("Gespräch", "Gespräch"), it("Betriebsrat / JAV", "Betriebsrat"), it("Kammer", "Kammer"), it("Arbeitsgericht", "Arbeitsgericht")], title="Konflikte lösen – Schritt für Schritt")
TB("""Jetzt das Thema, das in Prüfungen gern drankommt: die *Kündigung* der Ausbildung. Grundsätzlich gilt: immer *schriftlich*.
In der *Probezeit* ist es ganz einfach: *Beide* dürfen jederzeit kündigen, ohne Grund und ohne Frist. Das ist ja der Sinn der Probezeit, man testet, ob es passt.
*Nach* der Probezeit wird es streng. Der *Betrieb* darf nur noch *fristlos* aus einem *wichtigen Grund* kündigen, zum Beispiel wenn du klaust.
Und du als *Azubi*? Du darfst auch fristlos aus wichtigem Grund kündigen, oder mit *vier Wochen* Frist, wenn du den *Beruf wechselst* oder die Ausbildung ganz aufgibst.
Warum darf der Azubi das und der Betrieb nicht? Weil das Gesetz dich als den Schwächeren schützen will.""",
   "Kündigung (immer schriftlich)", ["Wann?", "Wer?", "Wie?"],
   [(["Probezeit", "beide", "jederzeit, ohne Grund"], "Probezeit"),
    (["danach", "Betrieb", "nur fristlos aus wichtigem Grund"], "Betrieb"),
    (["danach", "Azubi", "fristlos ODER 4 Wochen bei Berufswechsel"], "vier")])
P("""Und wann *endet* die Ausbildung? Ganz normal mit *Ablauf* der Zeit, oder schon früher, nämlich mit der *bestandenen Prüfung*. Fällst du durch, kannst du *verlängern*,
bis zur Wiederholungsprüfung, höchstens *ein Jahr*. Und noch eine Falle: Arbeitest du nach dem Ende einfach weiter und keiner sagt etwas, dann bist du automatisch *unbefristet* angestellt.""",
  "Ende der Ausbildung", [it("Ablauf der Zeit oder bestandene Prüfung", "Ablauf"), it("nicht bestanden ➜ Verlängerung bis 1 Jahr", "verlängern"),
                          it("einfach weiterarbeiten ➜ unbefristet!", "unbefristet")])
Q("""Testfrage: Lukas ist im *zweiten* Lehrjahr und will Mechatroniker werden statt Elektroniker. Wie kann er kündigen? … Er ist nach der Probezeit, und er *wechselt den Beruf*.
Also darf er mit *vier Wochen* Frist kündigen, schriftlich.""",
  "Lukas (2. Lehrjahr) will den Beruf wechseln. Wie kann er kündigen?", "Nach der Probezeit + Berufswechsel ➜ mit 4 Wochen Frist, schriftlich", "Also")

# ---------------------------------------------------------------- 3
thema("Schutzgesetze")
T("""Thema drei: die *Schutzgesetze*, auch *sozialer Arbeitsschutz* genannt. Hier geht es darum, dass Arbeit dich nicht kaputtmacht.""")
BIG("""Für *Jugendliche* unter achtzehn gibt es das Jugendarbeitsschutzgesetz, weil Jugendliche noch im Wachstum sind und mehr Schutz brauchen.
Merk dir dafür die Zahlenreihe *acht, vierzig, fünf, zwölf*. Höchstens *acht Stunden* am Tag, *vierzig* in der Woche, an *fünf* Tagen, und dazwischen mindestens *zwölf Stunden* Freizeit.
Dazu kommt: keine Arbeit zwischen *zwanzig und sechs Uhr*. Ein *Berufsschultag* mit mehr als fünf Stunden zählt als voller Arbeitstag, du musst danach also nicht noch in den Betrieb.
Jugendliche bekommen *mehr Urlaub*, müssen vor Beginn zum *Arzt*, und *gefährliche Arbeiten* und *Akkord*, also Arbeiten unter Zeitdruck nach Stückzahl, sind verboten.""",
    "8 – 40 – 5 – 12", "Jugendarbeitsschutz (unter 18)",
    [it("8 Std./Tag · 40 Std./Woche · 5 Tage · 12 Std. Freizeit", "acht"), it("keine Arbeit 20–6 Uhr", "zwanzig"),
     it("Berufsschultag > 5 Std. = voller Arbeitstag", "Berufsschultag"), it("mehr Urlaub, Arzt vor Beginn", "Urlaub"), it("verboten: gefährliche Arbeit, Akkord", "gefährliche")])
TB("""Bei den *Pausen* passen viele nicht auf. Jugendliche bekommen bei mehr als *viereinhalb* Stunden *dreißig Minuten* Pause, bei mehr als *sechs* Stunden insgesamt *sechzig Minuten*.
Und eine Pause zählt erst ab *fünfzehn Minuten*. Zweimal fünf Minuten Kaffee sind also rechtlich gar keine Pause.
Für *Erwachsene* gilt: *acht* Stunden am Tag, kurzzeitig auch *zehn*, wenn es später wieder ausgeglichen wird, und *elf Stunden* Ruhe zwischen zwei Arbeitstagen.""",
   "Pausen & Arbeitszeit", ["", "Jugendliche", "Erwachsene"],
   [(["Arbeitszeit", "8 Std.", "8 Std., kurz 10"], "Pausen"),
    (["Pause", "> 4,5 Std. ➜ 30 Min. · > 6 Std. ➜ 60 Min.", "30 / 45 Min."], "viereinhalb"),
    (["Pause zählt ab", "15 Minuten", "15 Minuten"], "fünfzehn"),
    (["Ruhe zwischen Arbeitstagen", "12 Std.", "11 Std."], "elf")])
F("""Beim *Urlaub* gibt es einen kleinen Rechentrick. Im Gesetz stehen *vierundzwanzig Werktage*. Werktage sind aber Montag *bis Samstag*, also sechs Tage pro Woche.
Du arbeitest aber nur fünf Tage. Deshalb rechnest du vierundzwanzig *geteilt durch sechs*, das sind vier Wochen, *mal fünf* Arbeitstage, macht *zwanzig Arbeitstage*.
Das ist das Minimum, mehr darf der Chef dir immer geben, weniger nie.""",
  [["24 Werktage", "#2563eb", "vierundzwanzig"], ["÷ 6 × 5", "#1f2937", "geteilt"], ["=", "#1f2937", "zwanzig"], ["20 Arbeitstage", "#16a34a", "zwanzig"]],
  note="Mehr Urlaub erlaubt, weniger nicht")
P("""Und dann gibt es noch Schutz rund um *Familie*. Beim *Mutterschutz* darf eine Frau *sechs Wochen vor* und *acht Wochen nach* der Geburt nicht arbeiten. Und sie ist geschützt:
Kündigungsschutz *ab der Schwangerschaft* bis *vier Monate* nach der Geburt. *Elternzeit* können *beide Eltern* nehmen, Mama und Papa, bis zum *dritten Geburtstag* des Kindes.
Auch da gilt Kündigungsschutz, und das *Elterngeld* zahlt nicht der Chef, sondern der *Staat*. Und wer passt auf, dass das alles eingehalten wird?
Das *Gewerbeaufsichtsamt*, die *Berufsgenossenschaft* und im Betrieb der *Betriebsrat*.""",
  "Mutterschutz & Elternzeit", [it("Mutterschutz: 6 Wochen vor, 8 nach der Geburt", "Mutterschutz"), it("Kündigungsschutz ab Schwangerschaft bis 4 Monate danach", "Kündigungsschutz"),
                                it("Elternzeit: beide Eltern, bis zum 3. Geburtstag", "Elternzeit"), it("Elterngeld zahlt der Staat", "Elterngeld"),
                                it("Überwachung: Gewerbeaufsicht, Berufsgenossenschaft, Betriebsrat", "Gewerbeaufsichtsamt")])
M("""Und jetzt drei Begriffe, die in der Prüfung gern verwechselt werden. Die *Ruhepause* ist *in* der Arbeit, also mitten am Tag. Die *Freizeit* ist *zwischen* zwei Arbeitstagen, zwölf Stunden.
Und die *Nachtruhe* ist eine *Uhrzeit*, nämlich zwanzig bis sechs Uhr.""",
  "Ruhepause = IN der Arbeit · Freizeit = ZWISCHEN zwei Tagen (12 Std.) · Nachtruhe = UHRZEIT (20–6 Uhr)")

# ---------------------------------------------------------------- 4
thema("Arbeitsvertrag")
T("""Thema vier: der *Arbeitsvertrag*. Den unterschreibst du nach der Ausbildung, und im Kern ist er ganz simpel: Du *arbeitest*, der Chef *zahlt*.""")
C("""Spannend wird es schon vorher, beim *Vorstellungsgespräch*. Der Chef darf nicht alles fragen. *Zulässig* ist alles, was mit dem *Job* zu tun hat: deine *Ausbildung*, deine *Erfahrung*,
deine *Kenntnisse*. *Unzulässig* sind Fragen, die ihn nichts angehen und dich benachteiligen könnten: *Schwangerschaft*, *Religion*, *Partei*, deine *Finanzen*.
Und jetzt kommt etwas, das viele überrascht: Auf eine unzulässige Frage darfst du *lügen*. Das nennt man das *Recht zur Lüge*. Fragt der Chef eine Bewerberin, ob sie schwanger ist,
darf sie Nein sagen, auch wenn es stimmt, und das hat später keine Folgen für sie.""",
  "Zulässig ✅", ["Ausbildung", "Erfahrung", "Kenntnisse"], "Unzulässig ❌", ["Schwangerschaft", "Religion, Partei", "Finanzen", "➜ Recht zur Lüge"], "Unzulässig")
P("""Muss der Arbeitsvertrag schriftlich sein? Überraschung: nein. Er ist *formfrei*, sogar ein *Handschlag* reicht. Aber damit du später etwas in der Hand hast,
muss dir der Chef die wichtigsten *Bedingungen schriftlich* geben, so verlangt es das *Nachweisgesetz*. Und eine wichtige Ausnahme gibt es: die *Befristung*.
Wird die *nicht schriftlich* vereinbart, dann gilt dein Vertrag einfach als *unbefristet*. Das ist ein Schutz für dich.""",
  "Form", [it("formfrei – Handschlag reicht", "formfrei"), it("Bedingungen schriftlich aushändigen (Nachweisgesetz)", "Bedingungen"),
           it("Befristung ohne Schriftform ➜ unbefristet!", "Befristung")])
C("""Und die Pflichten im Arbeitsverhältnis? Du als *Arbeitnehmer* musst *arbeiten*, *Weisungen* befolgen, Betriebsgeheimnisse für dich behalten und dich *krank melden*, wenn du ausfällst.
Dein *Arbeitgeber* muss *zahlen*, auch wenn du krank bist, und zwar bis zu *sechs Wochen*. Danach springt die Krankenkasse ein. Er hat außerdem eine *Fürsorgepflicht*,
er muss also für deine Sicherheit sorgen, gerade als Elektriker wichtig. Und er muss *Urlaub* geben und dir am Ende ein *Zeugnis* ausstellen.""",
  "Arbeitnehmer", ["arbeiten", "Weisungen befolgen", "schweigen", "krank melden"], "Arbeitgeber", ["zahlen (krank bis 6 Wochen)", "Fürsorge", "Urlaub", "Zeugnis"], "Arbeitgeber")
Q("""Frage: Lukas und sein Chef machen per Handschlag aus, dass er ein Jahr befristet arbeitet. Nichts Schriftliches. Was gilt? … Die Befristung ist *nicht schriftlich*,
also gilt der Vertrag als *unbefristet*. Gut für Lukas!""",
  "Befristung per Handschlag, nichts Schriftliches – was gilt?", "Befristung ohne Schriftform ➜ Vertrag gilt als unbefristet", "Befristung")

# ---------------------------------------------------------------- 5
thema("Kündigung und Kündigungsschutz")
T("""Thema fünf: *Kündigung und Kündigungsschutz*. Ein Thema, das dir hoffentlich nie passiert, aber in der Prüfung fast immer.""")
P("""Erst mal: Wie kann ein Arbeitsverhältnis überhaupt *enden*? Durch eine *Kündigung*, durch einen *Aufhebungsvertrag*, da einigen sich beide einfach, wenn eine *Befristung* abläuft,
oder mit der *Rente*. Kurz zur Befristung: Sie hat ein festes Enddatum, muss *schriftlich* sein, und *ohne Grund* darf man höchstens *zwei Jahre* befristen.
Mit einem Grund, zum Beispiel als Vertretung für jemanden in Elternzeit, auch länger.""",
  "So endet ein Arbeitsverhältnis", [it("Kündigung", "Kündigung"), it("Aufhebungsvertrag – beide einigen sich", "Aufhebungsvertrag"), it("Befristung läuft ab", "Befristung"),
                                     it("Rente", "Rente"), it("Befristung: schriftlich, ohne Grund max. 2 Jahre", "zwei")])
D("""Was *ist* eine Kündigung juristisch? Eine *empfangsbedürftige einseitige Willenserklärung*. Klingt kompliziert, ist aber logisch. *Einseitig*: Der andere muss nicht zustimmen,
du kannst ja auch kündigen, wenn der Chef das doof findet. *Empfangsbedürftig*: Sie wirkt erst, wenn sie beim anderen *ankommt*. Und sie muss immer *schriftlich* sein,
mit Unterschrift. Eine WhatsApp oder E-Mail reicht nicht.""",
  "Kündigung", "empfangsbedürftige, einseitige Willenserklärung – immer schriftlich", "empfangsbedürftige")
C("""Es gibt zwei Arten. Die *ordentliche* Kündigung ist die normale, mit Frist: *vier Wochen*, also genau *achtundzwanzig Tage*, und dann zum *Fünfzehnten* oder zum *Monatsende*.
In der Probezeit nur *zwei Wochen*. Kündigt der *Chef*, wird die Frist *länger*, je länger du im Betrieb bist, die genauen Werte stehen in der Prüfung in der Anlage.
Die *außerordentliche* Kündigung ist die Notbremse: *fristlos*, also sofort, aber nur mit einem *wichtigen Grund*, zum Beispiel Diebstahl.""",
  "ordentlich 🚶", ["4 Wochen (28 Tage) zum 15. / Monatsende", "Probezeit: 2 Wochen", "Chef kündigt ➜ länger (Anlage)"],
  "außerordentlich 🚨", ["fristlos", "nur mit wichtigem Grund", "z. B. Diebstahl"], "außerordentliche")
X("""Rechnen wir das mal zusammen. Lukas' Kündigung kommt am *zehnten März* an. Jetzt zählst du *achtundzwanzig Tage* dazu, dann bist du beim *siebten April*.
Aber da darf es noch nicht enden, es muss ja zum Fünfzehnten oder zum Monatsende sein. Welcher Termin kommt als *nächstes*? Der *fünfzehnte April*. Da ist dann Schluss.""",
  [it("Kündigung kommt an: 10. März", "zehnten"), it("+ 28 Tage = 7. April", "achtundzwanzig"), it("nächster Termin (15. / Monatsende)", "nächstes"), it("Ende: 15. April", "fünfzehnte")],
  title="Rechenbeispiel")
P("""Jetzt der *allgemeine Kündigungsschutz*. Der soll verhindern, dass dich der Chef einfach so loswird. Er gilt, wenn du *länger als sechs Monate* da bist *und* der Betrieb
*mehr als zehn* Mitarbeiter hat. Dann braucht der Chef einen *Grund*, und es gibt nur drei. Ein Trick zum Merken: kann nicht, will nicht, geht nicht.
*Person*: Du *kannst* nicht mehr, zum Beispiel wegen sehr langer Krankheit. *Verhalten*: Du *willst* nicht, kommst zum Beispiel ständig zu spät. *Betrieb*: Es *geht* nicht mehr,
weil Aufträge wegfallen. Dann gibt es eine *Sozialauswahl*: Wer es am leichtesten verkraftet, zum Beispiel jung, ohne Kinder, kurz im Betrieb, geht zuerst.
Wichtig: Gibt es einen Betriebsrat, muss er vorher *angehört* werden, sonst ist die Kündigung *unwirksam*. Und wehren kannst du dich mit einer *Klage* innerhalb von *drei Wochen*.""",
  "Allgemeiner Kündigungsschutz", [it("> 6 Monate UND > 10 Mitarbeiter", "sechs"), it("Person – kann nicht (lange Krankheit)", "Person"),
                                    it("Verhalten – will nicht (ständig zu spät)", "Verhalten"), it("Betrieb – geht nicht (Aufträge weg) ➜ Sozialauswahl", "Betrieb"),
                                    it("Betriebsrat anhören, sonst unwirksam", "angehört"), it("Klage innerhalb 3 Wochen", "Klage")])
BIG("""Und dann gibt es Menschen, die *besonders* geschützt sind, egal wie groß der Betrieb ist. Merk dir *S E S B A*: *Schwangere*, Leute in *Elternzeit*,
*Schwerbehinderte*, Mitglieder des *Betriebsrats*, damit die sich trauen, dem Chef zu widersprechen, und *Azubis* nach der Probezeit.""",
    "S – E – S – B – A", "Besonderer Kündigungsschutz (gilt immer)",
    [it("Schwangere", "Schwangere"), it("Elternzeit", "Elternzeit"), it("Schwerbehinderte", "Schwerbehinderte"), it("Betriebsrat", "Betriebsrats"), it("Azubis nach Probezeit", "Azubis")])
Q("""Testfrage: Ein Betrieb mit *acht* Mitarbeitern kündigt einem Gesellen nach drei Jahren ohne Grund. Geht das? … Ja, leider. Der *allgemeine* Kündigungsschutz gilt erst
ab *mehr als zehn* Mitarbeitern. Die Frist muss der Chef aber trotzdem einhalten.""",
  "Betrieb mit 8 Mitarbeitern kündigt ohne Grund – geht das?", "Ja – allg. Kündigungsschutz erst ab > 10 Mitarbeitern (Frist muss aber eingehalten werden)", "Ja")

# ---------------------------------------------------------------- 6
thema("Arbeitszeugnis")
T("""Thema sechs: das *Arbeitszeugnis*. Das ist quasi deine Visitenkarte für die nächste Bewerbung.""")
C("""Es gibt zwei Arten. Das *einfache* Zeugnis ist eher langweilig: *Name*, *Tätigkeit* und *Dauer*, mehr nicht. Das *qualifizierte* Zeugnis bewertet zusätzlich
deine *Leistung* und deine *Führung*, also dein Verhalten. Das ist das, was neue Chefs lesen wollen. Aber Achtung: Das qualifizierte bekommst du nur auf *Verlangen*. Du musst es also ansprechen.""",
  "einfach", ["Name", "Tätigkeit", "Dauer"], "qualifiziert", ["+ Leistung", "+ Führung (Verhalten)", "nur auf Verlangen"], "qualifizierte")
TB("""Jetzt wird es interessant. Ein Zeugnis muss *wahr* sein, aber auch *wohlwollend*. Der Chef darf dir also nicht die Zukunft verbauen. Deshalb schreibt er nie „er war schlecht“,
sondern verpackt das in eine Geheimsprache, die *Zeugnissprache*. Für die *Leistung*: „*stets* zu unserer *vollsten* Zufriedenheit“ ist eine *Eins*. Fehlt das „stets“ oder das „vollsten“,
geht es runter: „stets zur vollen“ ist eine *Zwei*, „zur vollen“ eine *Drei*, „zu unserer Zufriedenheit“ eine *Vier*, „im Großen und Ganzen“ eine *Fünf*.
Und wenn da steht „er war *bemüht*“, klingt das nett, ist aber eine *Sechs*. Er hat es versucht, aber nicht geschafft.""",
   "Zeugnissprache – Leistung", ["Formulierung", "Note"],
   [(["stets zu unserer vollsten Zufriedenheit", "1"], "Eins"), (["stets zur vollen Zufriedenheit", "2"], "Zwei"), (["zur vollen Zufriedenheit", "3"], "Drei"),
    (["zu unserer Zufriedenheit", "4"], "Vier"), (["im Großen und Ganzen", "5"], "Fünf"), (["bemüht", "6"], "Sechs")])
TB("""Für die *Führung* ist es ähnlich: „*stets vorbildlich*“ ist eine Eins, „*vorbildlich*“ eine Zwei, „*stets einwandfrei*“ eine Drei, „*einwandfrei*“ eine Vier.
Und lies auch zwischen den Zeilen: Stehen da nur die Kollegen und *nicht die Vorgesetzten*, gab es Ärger mit dem Chef. „*Erfrischende Offenheit*“ heißt eigentlich: Der war *vorlaut*.
Ein gutes Zeugnis endet mit einer Schlussformel aus *Bedauern*, *Dank* und guten *Wünschen*. Und „*auf eigenen Wunsch*“ heißt: Du hast selbst gekündigt, das ist positiv.""",
   "Zeugnissprache – Führung", ["Formulierung", "Bedeutung"],
   [(["stets vorbildlich", "1"], "Führung"), (["vorbildlich", "2"], "Zwei"), (["stets einwandfrei", "3"], "Drei"), (["einwandfrei", "4"], "Vier"),
    (["Vorgesetzte fehlen", "Ärger mit dem Chef"], "Vorgesetzten"), (["„erfrischende Offenheit“", "vorlaut"], "Erfrischende"),
    (["Schlussformel: Bedauern, Dank, Wünsche", "gut"], "Schlussformel")])
Q("""Frage: In Lukas' Zeugnis steht „Er erledigte seine Aufgaben *stets zu unserer vollen Zufriedenheit*“. Welche Note ist das? … Das „stets“ ist da, aber nicht „vollsten“, also eine *Zwei*.""",
  "„stets zu unserer vollen Zufriedenheit“ – welche Note?", "Note 2 (für die 1 bräuchte es „vollsten“)", "Zwei")

# ---------------------------------------------------------------- 7
thema("Betriebsrat")
T("""Thema sieben: der *Betriebsrat*.""")
P("""Stell dir vor, du hast ein Problem mit dem Chef. Allein traust du dich vielleicht nicht, etwas zu sagen. Genau dafür gibt es den Betriebsrat: die *gewählte Vertretung* der Mitarbeiter,
geregelt im *Betriebsverfassungsgesetz*. Gewählt werden kann er ab *fünf* Arbeitnehmern, alle *vier Jahre*. *Wählen* darfst du schon ab *sechzehn*, *gewählt werden* ab *achtzehn*,
wenn du *sechs Monate* im Betrieb bist. Was macht er? Er *überwacht*, ob Gesetze eingehalten werden, *vertritt* die Interessen aller, nimmt *Beschwerden* an, setzt sich für *Schwächere* ein
und macht mit dem Chef *Betriebsvereinbarungen*, also Regeln für den ganzen Betrieb. Sein Prinzip: *Allein* bist du *schwach*, *zusammen* seid ihr *stark*.""",
  "Betriebsrat (BetrVG)", [it("ab 5 Arbeitnehmern · Wahl alle 4 Jahre", "fünf"), it("wählen ab 16 · gewählt werden ab 18 + 6 Monate", "Wählen"),
                           it("überwacht, vertritt Interessen, Beschwerden", "überwacht"), it("für Schwächere, Betriebsvereinbarungen", "Schwächere"),
                           it("allein schwach, zusammen stark", "Allein")])
RAW("""Jetzt das Wichtigste für die Prüfung: Wie viel darf der Betriebsrat mitreden? Das geht in *drei Stufen*, vom wenigsten zum meisten.
Stufe eins, *Information*: Der Chef muss nur *Bescheid sagen*, zum Beispiel wenn *neue Technik* oder eine *Automatisierung* kommt.
Stufe zwei, *Mitwirkung*: Der Betriebsrat wird *angehört* und darf seine Meinung sagen, aber am Ende *entscheidet der Chef*. Zum Beispiel bei einer *Kündigung*, *Einstellung* oder *Versetzung*.
Stufe drei, *Mitbestimmung*: Hier geht *ohne Zustimmung* gar nichts. Zum Beispiel bei der *Arbeitszeit*, den *Pausen*, *Überstunden* oder dem *Urlaubsplan*.
Also alles, was den Alltag von allen betrifft.""",
    {"type": "stairs", "title": "Die 3 Stufen", "items": [
        it("Information = Bescheid sagen", "Information", sub="neue Technik, Automatisierung"),
        it("Mitwirkung = anhören, Chef entscheidet", "Mitwirkung", sub="Kündigung, Einstellung, Versetzung"),
        it("Mitbestimmung = Chef braucht Zustimmung", "Mitbestimmung", sub="Arbeitszeit, Pausen, Überstunden, Urlaubsplan")]})
Q("""Frage: Der Chef will, dass alle ab nächster Woche jeden Samstag Überstunden machen. Welche Stufe ist das? … *Überstunden* sind *Mitbestimmung*.
Ohne Zustimmung des Betriebsrats geht das nicht.""",
  "Chef will Samstags-Überstunden für alle – welche Stufe?", "Mitbestimmung – ohne Zustimmung des Betriebsrats geht es nicht", "Überstunden")

# ---------------------------------------------------------------- 8
thema("Tarifvertrag und Arbeitskampf")
T("""Thema acht: *Tarifvertrag und Arbeitskampf*. Hier geht es um die großen Verhandlungen über Löhne, die du aus den Nachrichten kennst, wenn mal wieder gestreikt wird.""")
P("""Ein Tarifvertrag wird nicht zwischen dir und deinem Chef gemacht, sondern eine Ebene höher: zwischen der *Gewerkschaft*, zum Beispiel der IG Metall, und dem *Arbeitgeberverband*.
Die beiden nennt man *Sozialpartner*. Und der Staat hält sich raus, die verhandeln das selbst. Das heißt *Tarifautonomie*.""",
  "Tarifvertrag", [it("Gewerkschaft + Arbeitgeberverband = Sozialpartner", "Gewerkschaft"), it("Tarifautonomie = ohne Staat", "Tarifautonomie")])
TB("""Es gibt *drei Arten*, und der Unterschied liegt in dem, was geregelt wird, und wie lange es gilt. Der *Entgelttarifvertrag* regelt die *Lohnhöhe*. Weil sich Preise schnell ändern,
läuft er kurz, etwa *ein Jahr*. Der *Rahmenentgelttarifvertrag* regelt die *Lohngruppen*, also wer mit welcher Ausbildung wie eingestuft wird, der läuft *mehrere Jahre*.
Und der *Manteltarifvertrag* regelt die allgemeinen Bedingungen wie *Arbeitszeit* und *Urlaub*. Die ändern sich selten, darum läuft er am längsten, *drei bis fünf Jahre*.""",
   "Tarifvertragsarten", ["Art", "regelt", "Laufzeit"],
   [(["Entgelt", "Lohnhöhe", "ca. 1 Jahr"], "Entgelttarifvertrag"), (["Rahmenentgelt", "Lohngruppen", "mehrere Jahre"], "Rahmenentgelttarifvertrag"),
    (["Mantel", "Arbeitszeit, Urlaub", "3–5 Jahre"], "Manteltarifvertrag")])
P("""Für wen gilt so ein Tarifvertrag? Rechtlich erst mal nur für *Gewerkschaftsmitglieder*, das nennt man *Tarifbindung*. Er gilt aber auch, wenn du *beitrittst*, wenn dein *Arbeitsvertrag*
darauf verweist, oder wenn der Staat ihn für *allgemeinverbindlich* erklärt. Zwei Regeln noch: Das *Günstigkeitsprinzip*, es gilt immer das *Günstigere* für dich. Zahlt dein Chef mehr
als der Tarif, ist das erlaubt, weniger nicht. Und die *Friedenspflicht*: Solange der Vertrag *läuft*, darf *nicht gestreikt* werden.""",
  "Regeln", [it("Tarifbindung: Gewerkschaftsmitglieder", "Gewerkschaftsmitglieder"), it("sonst: beitreten, Arbeitsvertrag, allgemeinverbindlich", "beitrittst"),
             it("Günstigkeitsprinzip: das Günstigere gilt", "Günstigkeitsprinzip"), it("Friedenspflicht: kein Streik während der Laufzeit", "Friedenspflicht")])
X("""Und so läuft eine *Tarifrunde* ab. Die Gewerkschaft stellt eine *Forderung*, zum Beispiel acht Prozent mehr Lohn. Dann wird *verhandelt*, und damit Druck entsteht, gibt es oft
kurze *Warnstreiks*. Kommen sie nicht zusammen, holt man einen neutralen *Schlichter*. Klappt auch das nicht, kommt die *Urabstimmung*: Mindestens *fünfundsiebzig Prozent* der Mitglieder
müssen für einen echten *Streik* sein. Wer streikt, bekommt keinen Lohn, aber *Streikgeld* von der Gewerkschaft. Der Arbeitgeber kann mit *Aussperrung* antworten, dann bekommen auch
Arbeitswillige keinen Lohn. Irgendwann gibt es eine *Einigung*, und dann wird nochmal abgestimmt: Hier reichen *fünfundzwanzig Prozent* für das Ergebnis, und es gibt einen *neuen Tarifvertrag*.""",
  [it("Forderung", "Forderung"), it("Verhandlung (Warnstreik)", "verhandelt"), it("Schlichtung", "Schlichter"), it("Urabstimmung 75 %", "Urabstimmung"),
   it("Streik ↔ Aussperrung", "Streik"), it("Einigung", "Einigung"), it("Urabstimmung 25 % ➜ neuer TV", "fünfundzwanzig")], title="Ablauf einer Tarifrunde")
M("""Merk dir: *fünfundsiebzig Prozent*, um *in* den Streik zu gehen, und nur *fünfundzwanzig Prozent*, um wieder *raus* zu kommen. Es ist also schwer anzufangen und leicht aufzuhören.""",
  "Tarifautonomie = ohne Staat · Streik: 75 % rein · 25 % raus")

# ---------------------------------------------------------------- 9
thema("Sozialversicherung")
T("""Thema neun: die *Sozialversicherung*. Schau mal auf deine Lohnabrechnung, da geht jeden Monat ein dicker Batzen dafür ab. Jetzt erfährst du, wofür.""")
P("""Die Sozialversicherung schützt dich vor den fünf großen Risiken im Leben: *Krankheit*, *Pflege*, *Alter*, *Arbeitslosigkeit* und *Unfall*. Dahinter steckt das *Solidaritätsprinzip*:
Jeder zahlt nach seinem *Einkommen*, und jeder bekommt Hilfe nach seinem *Bedarf*. Wer viel verdient, zahlt mehr, bekommt beim Arzt aber nicht mehr Behandlung. Die Starken tragen die Schwachen.
Als Arbeitnehmer und als Azubi bist du *pflichtversichert*. Die Beiträge werden von deinem *Brutto* berechnet und *fünfzig zu fünfzig* geteilt, die Hälfte zahlst du, die Hälfte der Chef.
Nur die *Unfallversicherung* zahlt der *Arbeitgeber allein*. Logisch eigentlich, Arbeitsunfälle passieren ja in seinem Betrieb.""",
  "Sozialversicherung", [it("schützt vor Krankheit, Pflege, Alter, Arbeitslosigkeit, Unfall", "Krankheit"), it("Solidaritätsprinzip: zahlen nach Einkommen, Hilfe nach Bedarf", "Solidaritätsprinzip"),
                         it("Arbeitnehmer & Azubis pflichtversichert", "pflichtversichert"), it("vom Brutto, 50 / 50", "fünfzig"), it("Unfall: Arbeitgeber allein", "Arbeitgeber")])
TB("""Gehen wir die fünf Zweige durch. Die *Krankenversicherung*, Träger ist deine Krankenkasse. Sie zahlt Arzt und Medikamente, und ab der siebten Woche *Krankengeld*,
weil die ersten sechs Wochen ja der Chef zahlt. Die *Pflegeversicherung* bei der Pflegekasse zahlt Pflegegeld. Wer *keine Kinder* hat und älter als dreiundzwanzig ist, zahlt hier etwas mehr.
Die *Rentenversicherung*, Träger ist die Deutsche Rentenversicherung: Altersrente, Rente bei Erwerbsminderung, Hinterbliebenenrente und Reha. Sie funktioniert als *Generationenvertrag*:
Was du heute einzahlst, bekommen die heutigen Rentner. Deine Rente zahlen später die dann Jungen. Die *Arbeitslosenversicherung* bei der Bundesagentur für Arbeit zahlt
*Arbeitslosengeld eins*, sechzig Prozent, mit Kind siebenundsechzig, und hilft bei Vermittlung und Weiterbildung. Und die *Unfallversicherung* bei der Berufsgenossenschaft zahlt bei
*Arbeitsunfällen*, beim *direkten Weg* zur Arbeit oder Berufsschule und bei *Berufskrankheiten*. Aber *nicht* in der Freizeit, also nicht beim Fußball am Wochenende.""",
   "Die 5 Zweige", ["Zweig", "Träger", "Leistungen"],
   [(["Kranken", "Krankenkasse", "Arzt, Medikamente, Krankengeld ab 7. Woche"], "Krankenversicherung"),
    (["Pflege", "Pflegekasse", "Pflegegeld · Kinderlose ab 23 zahlen mehr"], "Pflegeversicherung"),
    (["Rente", "Dt. Rentenversicherung", "Alters-, Erwerbsminderungs-, Hinterbliebenenrente, Reha"], "Rentenversicherung"),
    (["Arbeitslosen", "Bundesagentur für Arbeit", "ALG I 60 / 67 %, Vermittlung, Weiterbildung"], "Arbeitslosenversicherung"),
    (["Unfall", "Berufsgenossenschaft", "Arbeitsunfall, direkter Weg, Berufskrankheit – nicht Freizeit"], "Unfallversicherung")])
C("""Klingt nach Rundum-Schutz, hat aber *Grenzen*. Die gesetzliche Rente wird später nicht reichen, das ist die *Rentenlücke*. Kannst du deinen Beruf nicht mehr ausüben, gibt es keine
richtige *Berufsunfähigkeitsrente*. Machst du bei jemand anderem etwas kaputt, zahlt keiner. Und *Freizeitunfälle* sind nicht abgedeckt. Deshalb gibt es *Zusatzversicherungen*:
die *Berufsunfähigkeitsversicherung*, gerade für Handwerker wichtig, die zahlt, egal ob durch Krankheit oder Unfall. Die *private Altersvorsorge* gegen die Rentenlücke.
Und die *Haftpflicht*. Das ist die *wichtigste* von allen, denn wenn du jemandem einen großen Schaden zufügst, haftest du unbegrenzt, im schlimmsten Fall dein Leben lang.""",
  "Grenzen", ["Rentenlücke", "keine BU-Rente", "Schäden an anderen", "Freizeitunfälle"],
  "Zusatzversicherungen", ["Berufsunfähigkeit (BU)", "private Altersvorsorge", "Haftpflicht – die wichtigste!"], "Zusatzversicherungen")
Q("""Frage: Lukas fällt auf dem *direkten Weg zur Berufsschule* vom Fahrrad. Welche Versicherung zahlt? … Die *Unfallversicherung*. Der direkte Weg zur Berufsschule ist genauso geschützt
wie der Weg zur Arbeit. Hätte er einen Umweg zum Bäcker gemacht, wäre das schon schwieriger.""",
  "Unfall auf dem direkten Weg zur Berufsschule – wer zahlt?", "Die Unfallversicherung (Berufsgenossenschaft) – direkter Weg ist geschützt", "Unfallversicherung")

# ---------------------------------------------------------------- 10
thema("Lohnabrechnung")
T("""Thema zehn: die *Lohnabrechnung*. Endlich mal rechnen!""")
F("""Bevor wir rechnen, das Grundschema, das musst du im Schlaf können. Du startest mit dem *Brutto*, also dem, was du eigentlich verdienst. Davon gehen die *Steuern* ab und die *Sozialversicherung*.
Was übrig bleibt, ist dein *Netto*. Und davon gehen eventuell noch eine *Sparrate* oder ein *Vorschuss* ab, und dann hast du die *Auszahlung*, also das, was wirklich auf dem Konto landet.""",
  [["Brutto", "#2563eb", "Brutto"], ["− Steuern", "#dc2626", "Steuern"], ["− SV", "#dc2626", "Sozialversicherung"], ["= Netto", "#16a34a", "Netto"]],
  note="Netto − Sparrate / Vorschuss = Auszahlung")
P("""Jetzt die Fallen, auf die du achten musst. Das *Brutto* ist Stundenlohn *mal Stunden*, plus eventuell ein *Überstundenzuschlag*. Bei einer *Lohnerhöhung* rechnest du den alten Lohn
mal eins Komma null x, also bei drei Prozent mal eins Komma null drei. Die *Kirchensteuer* sind *acht Prozent*, aber Achtung, *von der Lohnsteuer*, nicht vom Brutto!
Die *Sozialversicherung* berechnest du vom Brutto mit dem *halben Satz*, weil der Chef die andere Hälfte zahlt. Und die größte Falle ist der *Kinderlosenzuschlag*.
Den zahlst du *allein*, also halbierst du ihn *nicht*. Erst halbierst du den Pflegesatz, *dann* kommen null Komma sechs Prozent obendrauf. Ein *Vorschuss* wird ganz am Ende *abgezogen*.""",
  "Die Fallen", [it("Brutto = Stundenlohn × Stunden (+ Überstundenzuschlag)", "Brutto"), it("Lohnerhöhung: alter Lohn × 1,0x", "Lohnerhöhung"),
                 it("Kirchensteuer = 8 % der LOHNSTEUER", "Kirchensteuer"), it("SV vom Brutto, halber Satz", "halben"),
                 it("Kinderlosenzuschlag NICHT halbieren", "Kinderlosenzuschlag"), it("Vorschuss am Ende abziehen", "Vorschuss")])
RAW("""Und jetzt rechnen wir ein Beispiel durch. Lukas ist dreiundzwanzig, hat keine Kinder, verdient fünfzehn Euro die Stunde und hat hundertsechzig Stunden gearbeitet,
plus zehn *Überstunden* mit fünfundzwanzig Prozent Zuschlag. Das ergibt ein *Brutto* von zweitausendfünfhundertsiebenundachtzig Euro fünfzig. Die *Lohnsteuer* nehmen wir aus der Tabelle:
zweihundertfünfzig Euro. Die *Kirchensteuer* sind acht Prozent davon, also zwanzig Euro. Die *Sozialversicherung*, mit Beispielsätzen und dem Kinderlosenzuschlag:
fünfhundertzweiundsechzig Euro achtundsiebzig. Damit bleibt ein *Netto* von tausendsiebenhundertvierundfünfzig Euro zweiundsiebzig. Lukas hatte sich aber hundert Euro *Vorschuss* geholt,
also bekommt er *tausendsechshundertvierundfünfzig Euro zweiundsiebzig* ausgezahlt.""",
    {"type": "ledger", "title": "Lohnabrechnung Lukas (Beispielwerte)", "rows": [
        {"label": "160 Std. × 15 € + 10 Überstunden × 15 € × 1,25", "amount": 2587.5, "cue": "Überstunden"},
        {"label": "− Lohnsteuer (laut Tabelle)", "amount": -250, "cue": "Lohnsteuer"},
        {"label": "− Kirchensteuer (8 % von 250 €)", "amount": -20, "cue": "Kirchensteuer"},
        {"label": "− Sozialversicherung (AN-Anteil inkl. Kinderlosenzuschlag)", "amount": -562.78, "cue": "Sozialversicherung"},
        {"label": "= Netto", "amount": None, "cue": "Netto", "total": True},
        {"label": "− Vorschuss", "amount": -100, "cue": "Vorschuss"},
        {"label": "= Auszahlung", "amount": None, "cue": "ausgezahlt", "total": True}],
     "note": "Steuer- und SV-Sätze stehen in der Prüfung in der Anlage", "cueNote": "Netto"})
Q("""Frage: Die Lohnsteuer ist zweihundert Euro. Wie hoch ist die Kirchensteuer? … *Acht Prozent von zweihundert*, also *sechzehn Euro*. Nicht acht Prozent vom Brutto!""",
  "Lohnsteuer = 200 €. Wie hoch ist die Kirchensteuer?", "8 % von 200 € = 16 € (nicht vom Brutto!)", "Acht")

# ---------------------------------------------------------------- 11
thema("Steuererklärung")
T("""Thema elf, das letzte: die *Steuererklärung*. Und das lohnt sich für dich ganz direkt, denn oft gibt es Geld zurück.""")
P("""Warum gibt es Geld zurück? Dein Chef zieht jeden Monat Lohnsteuer ab, aber er weiß nicht, was *du* für deinen Beruf ausgegeben hast. Bei der Steuererklärung *rechnet* das Finanzamt
*nach* und berücksichtigt das. Was kannst du abziehen? Erstens die *Werbungskosten*, also alles, was du für deinen *Beruf* ausgibst: die Fahrt zur Arbeit, ein *Fachbuch*,
*Arbeitskleidung*, deinen *Gewerkschaftsbeitrag*. Hast du wenig davon, zieht das Finanzamt automatisch den *Pauschbetrag* von *zwölfhundertdreißig Euro* ab.
Zweitens die *Sonderausgaben*: *Kirchensteuer*, *Spenden* und *Vorsorge*, also deine Beiträge für Rente, Krankenkasse, Berufsunfähigkeit und Haftpflicht.
Was *nicht* geht: alles für die *Freizeit*, also dein Hobby oder der *Sportverein*.""",
  "Was kann ich abziehen?", [it("Werbungskosten = für den Beruf: Fahrt, Fachbuch, Arbeitskleidung, Gewerkschaft", "Werbungskosten"),
                             it("Pauschbetrag 1.230 €", "Pauschbetrag"), it("Sonderausgaben = Kirche, Spenden, Vorsorge", "Sonderausgaben"),
                             it("NICHT: Freizeit, Hobby, Sportverein", "Freizeit")])
F("""Die *Fahrtkosten* sind oft der größte Posten. Die Formel: *einfache Strecke* mal *Kilometerpauschale* laut Anlage mal *Arbeitstage*. Nur die einfache Strecke, nicht hin und zurück!
Lukas fährt zwanzig Kilometer, die Pauschale ist zum Beispiel achtunddreißig Cent, und er arbeitet zweihundertzwanzig Tage. Das sind *tausendsechshundertzweiundsiebzig Euro*.
Das ist mehr als der Pauschbetrag, also lohnt sich die Steuererklärung für ihn.""",
  [["20 km", "#2563eb", "einfache"], ["× 0,38 €", "#1f2937", "Kilometerpauschale"], ["× 220 Tage", "#1f2937", "Arbeitstage"], ["= 1.672 €", "#16a34a", "tausendsechshundertzweiundsiebzig"]],
  note="einfache Strecke × Pauschale (laut Anlage) × Arbeitstage")
P("""Und noch ein Denkfehler, den viele machen. Viele glauben: tausend Euro Werbungskosten heißt tausend Euro zurück. Leider nein. Werbungskosten senken das *zu versteuernde Einkommen*,
*nicht eins zu eins* die Steuer. Zahlst du ungefähr zwanzig Prozent Steuern, bekommst du von tausend Euro Werbungskosten etwa *zweihundert Euro* zurück.""",
  "Achtung Denkfehler", [it("Werbungskosten senken das zu versteuernde Einkommen", "versteuernde"), it("nicht 1 : 1 die Steuer", "eins"),
                         it("1.000 € Werbungskosten × 20 % ≈ 200 € zurück", "zweihundert")])
Q("""Letzte Frage: Lukas zahlt achtzig Euro im Jahr für seinen Fußballverein. Kann er das absetzen? … Nein. Das ist *Freizeit*. Der Gewerkschaftsbeitrag dagegen schon, der hat mit dem Beruf zu tun.""",
  "Fußballverein 80 € im Jahr – absetzbar?", "Nein – Freizeit. (Gewerkschaftsbeitrag dagegen schon: Werbungskosten)", "Nein")
sc("""Und das war Kompetenzbereich eins! Elf Themen, und die meisten davon betreffen dich jeden Tag. Wenn du bei einem Thema unsicher bist, spring einfach zurück,
oben siehst du immer, wo du gerade bist. Und mein Tipp: Rechne die Lohnabrechnung und die Kündigungsfrist einmal selbst mit eigenen Zahlen durch, dann sitzt es.
Weiter geht's mit Kompetenzbereich zwei.""",
   {"type": "kb", "outro": True})

# =====================================================================================
# KB II – im Lehrer-Erklärstil
# =====================================================================================
kb(2, "Als Verbraucher Rechte anwenden",
   ["Rechtsfähigkeit", "Geschäftsfähigkeit", "Willenserklärung und Rechtsgeschäfte", "Formvorschriften", "Nichtig und anfechtbar", "Kaufvertrag",
    "Besitz und Eigentum", "Mangelhafte Lieferung", "Zahlungsverzug", "Regelmäßige Verjährung", "Verbraucherberatung", "Fernabsatz", "AGB",
    "Girokonto und Zahlungsverkehr", "Geldanlage", "Verbraucherdarlehen", "Überschuldung"])
sc("""Willkommen zu Kompetenzbereich zwei! Hier geht es um dich als *Verbraucher*, also als Kunde. Jedes Mal, wenn du beim Bäcker ein Brötchen kaufst, einen Handyvertrag abschließt
oder online etwas bestellst, passiert rechtlich eine ganze Menge, ohne dass du es merkst. Genau das schauen wir uns an. Es sind *siebzehn Themen*, aber keine Sorge,
viele sind kurz, und sie bauen aufeinander auf.""", {"type": "kb"})

thema("Rechtsfähigkeit")
T("""Thema eins: die *Rechtsfähigkeit*.""")
D("""Die Frage ist ganz einfach: Wer kann überhaupt *Rechte und Pflichten haben*? Zum Beispiel das Recht, etwas zu besitzen, oder die Pflicht, Steuern zu zahlen. Wer das kann, ist rechtsfähig.""",
  "Rechtsfähigkeit", "Man kann Rechte und Pflichten haben.")
C("""Bei *Menschen* ist das klar: von der *Geburt* bis zum *Tod*. Sogar ein Baby ist rechtsfähig, es kann zum Beispiel schon ein Haus *erben*. Selbst kaufen kann es natürlich noch nichts,
aber dazu gleich mehr. Und *Firmen*, also zum Beispiel eine *GmbH* oder ein *Verein*, sind rechtsfähig ab ihrer *Eintragung* ins Register. Die nennt man juristische Personen.""",
  "Menschen", ["von Geburt bis Tod", "auch ein Baby kann erben"], "Firmen (GmbH, Verein)", ["ab Eintragung ins Register"], "Firmen")
M("""Merk dir: Rechtsfähig heißt, Rechte *haben*. Das ist noch nicht dasselbe wie selbst Verträge machen, das ist das nächste Thema.""", "Rechtsfähig = Rechte HABEN")

thema("Geschäftsfähigkeit")
T("""Thema zwei: die *Geschäftsfähigkeit*. Und hier geht es genau darum: Ab wann darf ich selbst einkaufen und Verträge machen?""")
D("""Geschäftsfähig ist, wer *selbst gültige Verträge* abschließen kann. Und das hängt vom *Alter* ab, weil man Kinder vor schlechten Geschäften schützen will.""",
  "Geschäftsfähigkeit", "Man kann selbst gültige Verträge abschließen.")
RAW("""Es gibt *drei Stufen*. *Unter sieben* Jahren ist man *geschäftsunfähig*. Kauft ein Sechsjähriger etwas, ist der Vertrag *nichtig*, also gar nicht vorhanden.
Von *sieben bis siebzehn* ist man *beschränkt geschäftsfähig*. Der Vertrag ist dann *schwebend unwirksam*. Stell dir vor, er hängt in der Luft: Er wird erst gültig,
wenn die *Eltern zustimmen*. Sagen sie Nein, fällt er runter. Und ab *achtzehn* bist du *voll geschäftsfähig*, dann gilt alles, was du unterschreibst.""",
    {"type": "stairs", "title": "Die 3 Stufen", "items": [
        it("unter 7: geschäftsunfähig", "sieben", sub="Vertrag nichtig"),
        it("7 bis 17: beschränkt geschäftsfähig", "beschränkt", sub="schwebend unwirksam ➜ gültig, wenn Eltern zustimmen"),
        it("ab 18: voll geschäftsfähig", "achtzehn", sub="Vertrag gültig")]})
P("""Jetzt denkst du vielleicht: Moment, ich habe mit fünfzehn doch auch Döner gekauft, ohne meine Eltern zu fragen! Stimmt, dafür gibt es *Ausnahmen*. Erstens den *Taschengeldparagrafen*:
Wenn du *sofort und komplett* mit deinem Taschengeld bezahlst, ist das gültig. Zweitens, wenn du *nur einen rechtlichen Vorteil* hast, zum Beispiel ein *Geschenk*.
Und drittens Geschäfte rund um ein *Arbeits- oder Ausbildungsverhältnis*, das die Eltern erlaubt haben, zum Beispiel ein Konto für deine Ausbildungsvergütung.""",
  "Ausnahmen (gültig ohne Eltern)", [it("Taschengeldparagraf: sofort & komplett bezahlt", "Taschengeldparagrafen"), it("nur rechtlicher Vorteil (Geschenk)", "Vorteil"),
                                     it("Arbeits- / Ausbildungsverhältnis, von Eltern erlaubt", "Arbeits")])
Q("""Jetzt du: Ein *Sechzehnjähriger* kauft ein Handy auf *Raten*, mit seinem Taschengeld. Ist der Vertrag gültig? … Nein, noch nicht. Der Taschengeldparagraf gilt nur,
wenn *sofort und komplett* bezahlt wird, und bei Raten ist das nicht so. Also ist der Vertrag *schwebend unwirksam*. Sagen die Eltern Nein, ist er *ungültig*.""",
  "16-Jähriger kauft ein Handy auf Raten. Gültig?", "Nein – Raten ≠ sofort & komplett ➜ schwebend unwirksam ➜ Eltern sagen Nein ➜ ungültig", "Nein")

thema("Willenserklärung und Rechtsgeschäfte")
T("""Thema drei: *Willenserklärung und Rechtsgeschäfte*.""")
D("""Eine *Willenserklärung* ist einfach gesagt: Du zeigst, dass du etwas *rechtlich* willst. Das kann *mündlich* sein, *schriftlich*, oder sogar nur durch *Handeln*.
Wenn du im Supermarkt wortlos die Milch aufs Band legst, ist das auch eine Willenserklärung. Jeder weiß: Du willst die kaufen.""",
  "Willenserklärung", "Äußerung, um eine rechtliche Folge zu erreichen – mündlich, schriftlich oder durch Handeln.")
C("""Aus Willenserklärungen werden *Rechtsgeschäfte*. Manchmal reicht *eine* einzige, das nennt man *einseitig*. Beispiel: Du *kündigst* deinen Handyvertrag. Da muss niemand zustimmen.
Oder ein *Testament*. Meistens braucht man aber *zwei*, die zusammenpassen, das ist *zweiseitig*, also ein *Vertrag*. Beim Kaufvertrag sagst du: Ich will kaufen, und der Verkäufer sagt: Ich will verkaufen.""",
  "einseitig", ["eine Willenserklärung reicht", "Kündigung", "Testament"], "zweiseitig = Vertrag", ["zwei übereinstimmende Willenserklärungen", "Kauf, Miete, Arbeit"], "zweiseitig")
M("""Merke: Reicht *einer*, ist es *einseitig*. Braucht man *zwei*, ist es ein *Vertrag*.""", "Einer reicht = einseitig · Zwei nötig = Vertrag")

thema("Formvorschriften")
T("""Thema vier: *Formvorschriften*. Also: Muss das eigentlich schriftlich sein?""")
D("""Formvorschriften sagen, *in welcher Form* ein Rechtsgeschäft gemacht werden muss. Und jetzt die gute Nachricht: Der *Grundsatz* ist *formfrei*. Fast alles kannst du mündlich abschließen,
dein Brötchen kaufst du ja auch nicht schriftlich.""",
  "Formvorschriften", "Regeln, in welcher Form ein Rechtsgeschäft geschlossen werden muss. Grundsatz: formfrei.")
TB("""Bei *wichtigen* Dingen gibt es aber Ausnahmen, und die steigen wie eine Treppe. Die *Schriftform*: Du musst *eigenhändig unterschreiben*. Zum Beispiel bei der *Kündigung* eines Arbeitsvertrags,
bei einer *Bürgschaft*, einem *Verbraucherdarlehen* und beim *Mietvertrag über ein Jahr*. Eine Stufe höher die *öffentliche Beglaubigung*: Ein Notar bestätigt, dass die *Unterschrift* wirklich von dir ist,
zum Beispiel für das Handelsregister. Und ganz oben die *notarielle Beurkundung*: Der Notar schreibt den *ganzen Vertrag*, liest ihn vor und *berät* dich. Das braucht man beim *Grundstückskauf*.""",
   "Die Formen", ["Form", "Was?", "Beispiele"],
   [(["Schriftform", "eigenhändige Unterschrift", "Kündigung, Bürgschaft, Darlehen, Miete > 1 Jahr"], "Schriftform"),
    (["öffentliche Beglaubigung", "Notar bestätigt die Unterschrift", "Handelsregister"], "Beglaubigung"),
    (["notarielle Beurkundung", "Notar beurkundet den ganzen Vertrag", "Grundstückskauf, GmbH-Gründung"], "Beurkundung")])
P("""Warum macht man das? Erstens als *Beweis*, später kann keiner sagen: Das habe ich nie gesagt. Zweitens als Schutz vor *übereilten Entscheidungen*, ein Haus kauft man nicht spontan.
Und drittens, damit man *beraten* wird. Und was passiert, wenn die Form fehlt? Dann ist der Vertrag *nichtig*. Ein Grundstück per Handschlag kaufen geht also nicht.""",
  "Warum?", [it("Beweis", "Beweis"), it("Schutz vor übereilten Entscheidungen", "übereilten"), it("Beratung", "beraten"), it("Form fehlt ➜ Vertrag nichtig", "nichtig")])
M("""Merke: *Normal* ist *formfrei*. Bei *wichtigen* Sachen *Schrift* oder *Notar*.""", "normal formfrei · wichtig = Schrift oder Notar · Form fehlt ➜ nichtig")

thema("Nichtig und anfechtbar")
T("""Thema fünf: *nichtig und anfechtbar*. Zwei Wörter, die in der Prüfung oft verwechselt werden.""")
C("""Der Unterschied ist eigentlich schön zu merken. *Nichtig* heißt: Der Vertrag war *von Anfang an* ungültig. Er hat nie existiert. *Anfechtbar* heißt: Der Vertrag ist erst einmal ganz normal *gültig*.
Aber einer darf ihn *anfechten*, und dann wird er *rückwirkend* ungültig, also so, als hätte es ihn nie gegeben.""",
  "nichtig", ["von Anfang an ungültig"], "anfechtbar", ["erst gültig", "durch Anfechtung rückwirkend ungültig"], "Anfechtbar")
C("""Wann ist ein Vertrag *nichtig*? Bei *Geschäftsunfähigen*, also unter sieben. Bei einem *Formfehler*. Wenn er gegen ein *Gesetz* verstößt, zum Beispiel ein Drogenverkauf,
oder gegen die *guten Sitten*, zum Beispiel *Wucher*, also ein völlig überzogener Preis, weil jemand in einer Notlage ist. Und bei *Scherz- und Scheingeschäften*.
Wann ist er *anfechtbar*? Bei einem *Irrtum*: Du hast dich *verschrieben*, zum Beispiel hundert statt zehn Euro. Dann musst du *sofort* anfechten.
Bei *arglistiger Täuschung*, also wenn dich jemand absichtlich anlügt, und bei *widerrechtlicher Drohung* hast du *ein Jahr* Zeit.""",
  "nichtig bei …", ["Geschäftsunfähigen", "Formfehler", "Verstoß gegen Gesetz / gute Sitten (Wucher)", "Scherz- & Scheingeschäft"],
  "anfechtbar bei …", ["Irrtum ➜ sofort anfechten", "arglistige Täuschung ➜ 1 Jahr", "widerrechtliche Drohung ➜ 1 Jahr"], "anfechtbar")
Q("""Ein Fall für dich: Ein Händler verkauft Lukas einen Gebrauchtwagen und *verschweigt* absichtlich einen *Unfallschaden*. Nichtig oder anfechtbar? … *Anfechtbar*, wegen arglistiger *Täuschung*.
Lukas ficht an, der Vertrag wird ungültig, und beide bekommen zurück, was sie gegeben haben: Auto und Geld.""",
  "Unfallschaden absichtlich verschwiegen – nichtig oder anfechtbar?", "Anfechtbar (arglistige Täuschung, 1 Jahr) ➜ Auto & Geld zurück", "Anfechtbar")
M("""Und das Merke als Bild: *Nichtig* ist *sofort tot*. *Anfechtbar* *lebt*, bis jemand anficht.""", "Nichtig = sofort tot · Anfechtbar = lebt, bis jemand anficht")

thema("Kaufvertrag")
T("""Thema sechs: der *Kaufvertrag*, der Vertrag, den du am häufigsten abschließt.""")
D("""Ein Kaufvertrag entsteht durch *Antrag* und *Annahme*. Einer macht ein Angebot, der andere sagt Ja. Zwei Willenserklärungen, die zusammenpassen.""",
  "Kaufvertrag", "Antrag + Annahme (zwei übereinstimmende Willenserklärungen)")
P("""Und jetzt eine beliebte Prüfungsfalle: Ist das Preisschild im *Schaufenster* ein Antrag? Nein! *Werbung*, *Schaufenster*, *Prospekt* und auch der *Online-Shop* sind nur eine *Aufforderung*,
ein Angebot zu machen. Warum? Stell dir vor, tausend Leute bestellen einen Fernseher, und es gibt nur zehn. Dann müsste der Shop tausend Verträge erfüllen. Deshalb ist erst deine *Bestellung* der Antrag.
Wer einen Antrag macht, ist daran *gebunden*: unter Anwesenden oder am *Telefon* nur *sofort*. Per Brief oder *E-Mail* so lange, wie man *normalerweise* eine Antwort erwartet.
Mit „*freibleibend*“ oder „solange Vorrat reicht“ bindet man sich nicht oder nur eingeschränkt. Und kommt die Annahme *zu spät* oder *geändert*, ist das wieder ein *neuer Antrag*.""",
  "Antrag & Bindung", [it("Werbung, Schaufenster, Prospekt, Online-Shop = KEIN Antrag", "Werbung"), it("erst die Bestellung = Antrag", "Bestellung"),
                       it("Bindung: Telefon / anwesend ➜ sofort", "Telefon"), it("Brief / E-Mail ➜ so lange wie normal", "E-Mail"),
                       it("„freibleibend“, „solange Vorrat reicht“ ➜ eingeschränkt", "freibleibend"), it("zu spät / geändert ➜ neuer Antrag", "spät")])
C("""Und welche *Pflichten* hat jeder? Der *Verkäufer* muss die Ware *übergeben*, dir das *Eigentum* verschaffen, sie gehört dann also dir, und sie *mangelfrei* liefern.
Der *Käufer* muss *zahlen* und die Ware *abnehmen*, er darf sie also nicht einfach im Laden stehen lassen.""",
  "Verkäufer", ["übergeben", "Eigentum verschaffen", "mangelfrei liefern"], "Käufer", ["zahlen", "abnehmen"], "Käufer")
M("""Merke: *Werbung* ist *kein Antrag*. Erst *Antrag plus Annahme* gibt einen Vertrag.""", "Werbung ≠ Antrag · Antrag + Annahme = Vertrag")

thema("Besitz und Eigentum")
T("""Thema sieben: *Besitz und Eigentum*. Im Alltag sagen wir oft beides gleich, juristisch ist das ein großer Unterschied.""")
C("""*Besitz* ist die *tatsächliche* Herrschaft. Also: Wer *hat* die Sache gerade in der Hand? *Eigentum* ist die *rechtliche* Herrschaft: Wem *gehört* sie?
Beispiel: Lukas leiht sich die Bohrmaschine vom Kollegen. Lukas ist jetzt *Besitzer*, er hat sie ja. Aber der Kollege bleibt *Eigentümer*, sie gehört ihm.""",
  "Besitz", ["tatsächliche Herrschaft", "➜ haben"], "Eigentum", ["rechtliche Herrschaft", "➜ gehören"], "Eigentum")
P("""Wie wird man Eigentümer? Durch *Einigung* und *Übergabe*. Man ist sich einig, dass es jetzt dir gehören soll, und du bekommst die Sache. Es gibt aber einen Sonderfall,
den *Eigentumsvorbehalt*. Da bleibt die Ware *Eigentum des Verkäufers*, bis sie *komplett bezahlt* ist. Das ist typisch beim Ratenkauf, und es muss *vereinbart* werden.""",
  "Eigentumsübertragung", [it("Einigung + Übergabe", "Einigung"), it("Eigentumsvorbehalt: gehört dem Verkäufer bis komplett bezahlt", "Eigentumsvorbehalt"),
                           it("muss vereinbart werden", "vereinbart")])
Q("""Frage: Jemand klaut Lukas' Fahrrad. Wer ist jetzt Besitzer, und wer Eigentümer? … Der *Dieb* ist *Besitzer*, er hat das Fahrrad ja. Aber *Eigentümer* bleibt Lukas.
Ein Dieb wird *nie* Eigentümer.""",
  "Dieb klaut Lukas' Fahrrad – wer ist Besitzer, wer Eigentümer?", "Dieb = Besitzer · Lukas bleibt Eigentümer (Dieb wird nie Eigentümer)", "Dieb")

thema("Mangelhafte Lieferung")
T("""Thema acht: die *mangelhafte Lieferung*. Das passiert jedem mal: Du bestellst etwas, und es ist kaputt.""")
D("""Ein *Mangel* liegt vor, wenn die Ware bei der *Übergabe* nicht so ist wie *vereinbart* oder wie es *üblich* ist. Ein neues Handy mit Kratzer ist also mangelhaft.""",
  "Mangel", "Ware ist bei Übergabe nicht wie vereinbart oder üblich.")
P("""Welche Mängel gibt es? Den *Qualitätsmangel*, die Ware ist kaputt. Die *Falschlieferung*, du bekommst was anderes. Den *Mengenmangel*, es fehlt was. Den *Montagemangel*,
der Verkäufer baut es falsch ein, und die *fehlerhafte Montageanleitung*, du baust es wegen einer falschen Anleitung falsch auf. Und die *falsche Werbeaussage*.
Außerdem unterscheidet man, wie man sie *erkennt*: *offene* Mängel siehst du sofort, *versteckte* erst später, und *arglistig verschwiegene* hat der Verkäufer absichtlich verheimlicht.""",
  "Mängelarten", [it("Qualitätsmangel", "Qualitätsmangel"), it("Falschlieferung", "Falschlieferung"), it("Mengenmangel", "Mengenmangel"),
                  it("Montagemangel, fehlerhafte Montageanleitung", "Montagemangel"), it("falsche Werbeaussage", "Werbeaussage"),
                  it("offen · versteckt · arglistig verschwiegen", "erkennt")])
RAW("""Und was darfst du dann? Hier ist die *Reihenfolge* entscheidend, und genau die wird in der Prüfung abgefragt. Zuerst kommt *immer* die *Nacherfüllung*. Du darfst *wählen*:
*Nachbesserung*, also reparieren, oder *Ersatzlieferung*, also ein neues. Der Verkäufer bekommt also erst mal eine zweite Chance. Erst *danach*, wenn das *fehlgeschlagen* ist,
meistens nach *zwei Versuchen*, darfst du mehr: vom Vertrag *zurücktreten*, also Geld zurück, das aber nicht bei einem ganz kleinen Mangel. Oder *Minderung*, du zahlst weniger.
Und *Schadensersatz* gibt es zusätzlich, aber nur, wenn der Verkäufer *schuld* ist.""",
    {"type": "stairs", "title": "Rechte des Käufers – in dieser Reihenfolge!", "items": [
        it("1. Nacherfüllung: Reparatur oder Ersatz", "Nacherfüllung", sub="Käufer wählt – Verkäufer bekommt 2. Chance"),
        it("2. danach (meist nach 2 Versuchen): Rücktritt", "zurücktreten", sub="nicht bei kleinem Mangel"),
        it("… oder Minderung", "Minderung", sub="weniger zahlen"),
        it("… zusätzlich Schadensersatz", "Schadensersatz", sub="nur wenn Verkäufer schuld ist")]})
P("""Und wie lange hast du Zeit? Die *Gewährleistung* beträgt *zwei Jahre* ab Übergabe. Bei *gebrauchter* Ware darf der Händler sie gegenüber Verbrauchern auf *ein Jahr* verkürzen.
Und dann gibt es die *Beweislastumkehr*: Zeigt sich der Mangel im *ersten Jahr*, muss der *Verkäufer* beweisen, dass die Ware in Ordnung war. Das ist gut für dich.
Danach musst *du* beweisen, dass der Fehler schon beim Kauf da war.""",
  "Fristen", [it("Gewährleistung: 2 Jahre ab Übergabe", "Gewährleistung"), it("gebraucht an Verbraucher: auf 1 Jahr verkürzbar", "gebrauchter"),
              it("Beweislastumkehr: im 1. Jahr muss der Verkäufer beweisen", "Beweislastumkehr"), it("danach der Käufer", "Danach")])
Q("""Frage: Lukas' neue Kaffeemaschine ist nach einer Woche kaputt. Er will sofort sein Geld zurück. Darf er das? … *Nein*, noch nicht. Zuerst kommt die *Nacherfüllung*:
Er muss dem Verkäufer die Chance geben, sie zu reparieren oder eine neue zu liefern. Erst wenn das scheitert, darf er zurücktreten.""",
  "Kaffeemaschine nach 1 Woche kaputt – sofort Geld zurück?", "Nein – erst Nacherfüllung (Reparatur oder neu), erst dann Rücktritt", "Nein")

thema("Zahlungsverzug")
T("""Thema neun: der *Zahlungsverzug*. Jetzt drehen wir es um: Was passiert, wenn der Käufer nicht zahlt?""")
D("""Zahlungsverzug heißt: Der Käufer zahlt *nicht rechtzeitig*, obwohl die Zahlung *fällig* ist.""", "Zahlungsverzug", "Der Käufer zahlt nicht rechtzeitig, obwohl die Zahlung fällig ist.")
P("""Aber ab wann genau ist man im *Verzug*? Es gibt drei Wege. Erstens: eine *Mahnung* nach der Fälligkeit. Eine einzige reicht schon. Zweitens: ein *festes Kalenderdatum*.
Steht auf der Rechnung „zahlbar bis fünfzehnten Mai“, bist du am sechzehnten automatisch im Verzug, ganz ohne Mahnung, denn das Datum mahnt ja quasi für den Verkäufer.
Drittens: *dreißig Tage* nach der Rechnung. Bei Verbrauchern aber nur, wenn darauf auf der Rechnung *hingewiesen* wurde.""",
  "Verzug tritt ein durch …", [it("Mahnung nach Fälligkeit (eine reicht)", "Mahnung"), it("festes Kalenderdatum ➜ ohne Mahnung", "Kalenderdatum"),
                               it("30 Tage nach Rechnung (Verbraucher: nur mit Hinweis)", "dreißig")])
P("""Und was darf der *Verkäufer* dann? Er bekommt natürlich seine *Zahlung*, und dazu *Verzugszinsen*. Bei Verbrauchern sind das *Basiszinssatz plus fünf Prozentpunkte*.
Er darf *Schadensersatz* verlangen, zum Beispiel für die *Mahnkosten*. Und wenn du nach einer *Nachfrist* immer noch nicht zahlst, darf er vom Vertrag *zurücktreten* und seine Ware zurückholen.""",
  "Rechte des Verkäufers", [it("Zahlung + Verzugszinsen (Basiszins + 5 Prozentpunkte)", "Verzugszinsen"), it("Schadensersatz (Mahnkosten)", "Schadensersatz"),
                            it("nach Nachfrist: Rücktritt", "Nachfrist")])
M("""Merke: *Fällig* plus *Mahnung*, oder ein festes *Datum*, oder *dreißig Tage* mit Hinweis, das ergibt *Verzug*, und dann kosten Zinsen.""",
  "fällig + Mahnung (oder Datum / 30 Tage mit Hinweis) = Verzug ➜ Zinsen")

thema("Regelmäßige Verjährung")
T("""Thema zehn: die *regelmäßige Verjährung*. Also: Wie lange kann man Geld von dir verlangen?""")
D("""Verjährung heißt: Nach Ablauf einer Frist kann man eine Forderung *nicht mehr vor Gericht durchsetzen*. Die Schuld ist nicht weg, aber der Schuldner darf die Zahlung *verweigern*.""",
  "Verjährung", "Nach Ablauf der Frist kann man eine Forderung nicht mehr vor Gericht durchsetzen.")
RAW("""Die regelmäßige Frist sind *drei Jahre*. Aber, und das ist der Trick, sie *beginnt* nicht am Tag der Rechnung, sondern immer am *einunddreißigsten Zwölften* des Jahres,
in dem die Forderung entstanden ist. Ein *Beispiel*: Eine Rechnung vom *fünfzehnten März zweitausendsechsundzwanzig*. Die Frist startet erst am Jahresende, also am einunddreißigsten Dezember
zweitausendsechsundzwanzig, und endet drei Jahre später, am *einunddreißigsten Dezember zweitausendneunundzwanzig*. Warum so? Damit Firmen nicht für jede Rechnung ein eigenes Datum
im Kopf haben müssen, alle laufen einfach zum Jahresende ab. Und noch was: Wer eine *verjährte Schuld* trotzdem bezahlt, bekommt das Geld *nicht zurück*.""",
    {"type": "timeline", "title": "Regelmäßige Verjährung: 3 Jahre ab Jahresende", "cue": "Beispiel",
     "points": ["15.03.2026 Rechnung", "31.12.2026 Start", "31.12.2029 Ende"]})
C("""Und dann gibt es zwei Begriffe, die gut zu wissen sind. Der *Neubeginn*: Die Uhr wird auf *null* gestellt, die drei Jahre starten *komplett neu*. Das passiert, wenn der Schuldner
die Schuld *anerkennt*, zum Beispiel durch eine *Teilzahlung*, oder bei einer *Vollstreckung*. Und die neuen drei Jahre starten am *Tag danach*, nicht am Jahresende.
Die *Hemmung*: Die Uhr wird *angehalten*, zum Beispiel während *Verhandlungen*, nach einem *Mahnbescheid* oder einer *Klage*. Danach läuft sie weiter, die Zeit wird *hinten angehängt*.""",
  "Neubeginn ⏮", ["Uhr auf null – startet komplett neu", "Anerkennung (Teilzahlung …), Vollstreckung", "ab dem Tag danach"],
  "Hemmung ⏸", ["Uhr angehalten", "Verhandlungen, Mahnbescheid, Klage", "Zeit wird hinten angehängt"], "Hemmung")
M("""Merke: *Drei Jahre*, Start *immer am Jahresende*. *Neubeginn* heißt Uhr auf *null*. *Hemmung* heißt Uhr *angehalten*.""",
  "3 Jahre, Start am Jahresende · Neubeginn = Uhr auf null · Hemmung = Uhr angehalten")

thema("Verbraucherberatung")
T("""Thema elf: die *Verbraucherberatung*. Wo bekommst du Hilfe, wenn du Ärger mit einem Vertrag hast?""")
P("""Verbraucherberatung hilft dir, dich zu *informieren* und deine *Rechte durchzusetzen*. Die erste Adresse sind die *Verbraucherzentralen*, da bekommst du *persönliche Beratung*,
zum Beispiel wenn dich ein Handyanbieter abzocken will. Dann die *Stiftung Warentest*. Die testet Produkte und Finanzangebote und veröffentlicht die Ergebnisse in den Heften *test* und *Finanztest*.
Und dann gibt es *Publikationen*, also Ratgeber, Broschüren und Infos im Internet.""",
  "Wo gibt's Hilfe?", [it("Verbraucherzentralen ➜ persönliche Beratung", "Verbraucherzentralen"), it("Stiftung Warentest ➜ Hefte „test“ & „Finanztest“", "Warentest"),
                       it("Publikationen ➜ Ratgeber, Broschüren, Internet", "Publikationen")])
M("""Merke: Für *Beratung* gehst du zur *Verbraucherzentrale*. *Tests* macht die *Stiftung Warentest*.""", "Beratung = Verbraucherzentrale · Tests = Stiftung Warentest")

thema("Fernabsatz")
T("""Thema zwölf: der *Fernabsatz*. Klingt kompliziert, heißt aber einfach Online-Shopping.""")
D("""Fernabsatz ist ein Vertrag *ohne persönlichen Kontakt*, also im *Internet*, am *Telefon* oder per *Katalog*. Du kannst die Ware vorher nicht anfassen,
und genau deshalb bekommst du einen besonderen Schutz.""", "Fernabsatz", "Vertrag ohne persönlichen Kontakt (Internet, Telefon, Katalog)")
P("""Du hast ein *Widerrufsrecht* von *vierzehn Tagen*, und zwar *ohne Grund*. Die Frist beginnt, wenn du die *Ware erhalten* hast und *belehrt* wurdest, also über dein Widerrufsrecht informiert.
Hat der Händler das vergessen, verlängert sich die Frist auf bis zu *zwölf Monate plus vierzehn Tage*. Wichtig: Den Widerruf musst du *eindeutig erklären*, zum Beispiel per E-Mail.
Nur das Paket zurückschicken reicht nicht. Die *Rücksendekosten* zahlst *du*, wenn das vorher gesagt wurde. Und es gibt *Ausnahmen*: Kein Widerruf bei *individuell angefertigter* Ware,
zum Beispiel ein T-Shirt mit deinem Namen, bei *verderblichen* Lebensmitteln und bei *entsiegelter* Hygieneware, Software oder CDs.""",
  "Widerrufsrecht", [it("14 Tage, ohne Grund", "vierzehn"), it("Beginn: Erhalt der Ware + Belehrung", "erhalten"), it("ohne Belehrung: max. 12 Monate + 14 Tage", "zwölf"),
                     it("Widerruf eindeutig erklären", "eindeutig"), it("Rücksendekosten: Kunde (wenn informiert)", "Rücksendekosten"),
                     it("kein Widerruf: individuell, verderblich, entsiegelt", "individuell")])
Q("""Frage: Lukas kauft im *Laden* eine Jacke, zu Hause gefällt sie ihm nicht mehr. Hat er vierzehn Tage Widerrufsrecht? … *Nein!* Das Widerrufsrecht gibt es nur beim *Fernabsatz*.
Wenn der Laden die Jacke trotzdem zurücknimmt, ist das reine *Kulanz*, also freiwillig.""",
  "Jacke im Laden gekauft – 14 Tage Widerrufsrecht?", "Nein – nur beim Fernabsatz. Im Laden: höchstens Kulanz (freiwillig)", "Nein")

thema("AGB")
T("""Thema dreizehn: die *AGB*, die *Allgemeinen Geschäftsbedingungen*, also das Kleingedruckte, das du nie liest.""")
D("""AGB sind *vorformulierte* Vertragsbedingungen für *viele Verträge*. Die Firma schreibt sie einmal und nutzt sie für alle Kunden.""", "AGB", "Vorformulierte Vertragsbedingungen für viele Verträge.")
P("""Warum gibt es die? Die Firma *spart Zeit und Kosten*, sie muss nicht mit jedem Kunden einzeln verhandeln. Das Problem: Du als Kunde *kannst nicht mitverhandeln*,
und die Firma könnte dich *benachteiligen*. Deshalb schützt dich das *Gesetz*. AGB gelten überhaupt nur, wenn es einen *deutlichen Hinweis* gab, du sie *zumutbar lesen* konntest
und *einverstanden* warst. Und dann gibt es Regeln: *Überraschende Klauseln*, mit denen niemand rechnet, zum Beispiel ein verstecktes Abo beim Kauf eines Kabels, sind *unwirksam*.
Die *Gewährleistung* darf gegenüber Verbrauchern *nicht verkürzt* werden. Und ist eine Klausel unwirksam, gilt dafür einfach das *Gesetz*, der *Rest des Vertrags* bleibt gültig.""",
  "AGB-Regeln", [it("Firma spart Zeit & Kosten – Kunde kann nicht mitverhandeln", "spart"), it("gelten nur: Hinweis, lesen können, einverstanden", "Hinweis"),
                 it("überraschende Klauseln ➜ unwirksam", "Überraschende"), it("Gewährleistung bei Verbrauchern nicht verkürzbar", "Gewährleistung"),
                 it("unwirksame Klausel ➜ Gesetz gilt, Rest bleibt gültig", "Rest")])
M("""Merke: AGB dürfen *nicht überraschen* und dir *keine gesetzlichen Rechte* wegnehmen.""", "AGB dürfen nicht überraschen und keine gesetzlichen Rechte wegnehmen")

thema("Girokonto und Zahlungsverkehr")
T("""Thema vierzehn: *Girokonto und Zahlungsverkehr*. Wie bezahlst du eigentlich, und was ist wann sinnvoll?""")
P("""Das *Girokonto* ist dein Konto für den *täglichen Zahlungsverkehr*, da kommt dein Lohn drauf, und davon gehen Miete und Handy ab. Banken unterscheiden sich stark, deshalb lohnt es sich,
die *Konditionen* zu vergleichen: *Kontoführungsgebühr*, *Kartenkosten*, die *Dispozinsen*, falls du mal ins Minus rutschst, wo es kostenlose Geldautomaten gibt, *Online-Banking* und ob es eine Filiale gibt.""",
  "Girokonto – vergleiche", [it("Kontoführungsgebühr", "Kontoführungsgebühr"), it("Kartenkosten", "Kartenkosten"), it("Dispozinsen", "Dispozinsen"),
                             it("Geldautomaten, Online-Banking, Filiale", "Online")])
TB("""Und wie bezahlst du? Jede Form hat ihre Stärke. *Bar*: sofort, anonym, und du behältst gut den Überblick, weil du siehst, wie das Geld weniger wird. Nachteil: Es kann geklaut werden.
Die *Überweisung*, und als *Dauerauftrag* perfekt für immer gleiche Beträge wie die Miete. Die *Lastschrift*, da holt sich der Empfänger das Geld selbst, praktisch bei wechselnden Beträgen wie Strom.
Die *Girocard*: Das Geld geht *sofort* vom Konto. Die *Kreditkarte*: Es wird erst *später* abgebucht. Sie funktioniert weltweit, aber man verliert schnell den Überblick und rutscht in Schulden.
Und *elektronisch*, also PayPal oder Apple Pay: schnell beim Online-Shopping und oft mit *Käuferschutz*.""",
   "Zahlungsformen", ["Form", "Stärke / Schwäche"],
   [(["Bar", "sofort, anonym, Überblick / kann geklaut werden"], "Bar"), (["Dauerauftrag", "gleicher Betrag (Miete)"], "Dauerauftrag"),
    (["Lastschrift", "Empfänger holt ab – wechselnde Beträge (Strom)"], "Lastschrift"), (["Girocard", "Geld geht sofort ab"], "Girocard"),
    (["Kreditkarte", "später abgebucht, weltweit / Überblick, Schulden"], "Kreditkarte"), (["PayPal, Apple Pay", "schnell online, Käuferschutz"], "elektronisch")])
M("""Merke: Es gibt keine beste Zahlungsform. In der Prüfung musst du sie immer *nach der Situation* begründen.""", "Zahlungsform immer nach Situation begründen")

thema("Geldanlage")
T("""Thema fünfzehn: die *Geldanlage*. Du hast was gespart, und jetzt soll es mehr werden.""")
RAW("""Jede Geldanlage bewertest du mit dem *magischen Dreieck*. Drei Fragen: *Liquidität*: Wie *schnell* komme ich an mein Geld? *Rentabilität*: Wie viel *Ertrag* bringt es?
*Sicherheit*: Wie *sicher* ist es? Und warum heißt es *magisch*? Weil du nie alle drei gleichzeitig maximal bekommst, das wäre Zauberei. Das ist der *Zielkonflikt*: mehr Rendite heißt mehr Risiko.
Schauen wir zwei Beispiele an. Das *Termingeld*: Du legst Geld für eine feste Zeit zu einem festen Zins an. Sicherheit *hoch*, Liquidität *niedrig*, weil du vor Ende nicht rankommst, Rentabilität *mittel*.
Der *Aktienfonds*: Viele Aktien in einem Topf, so ist das Risiko verteilt. Rentabilität *hoch*, Sicherheit *niedriger*, weil Kurse schwanken, Liquidität *hoch*, du kannst jederzeit verkaufen.""",
    {"type": "triangle", "corners": [["Sicherheit", "🛡️", "Sicherheit"], ["Liquidität", "💧", "Liquidität"], ["Rentabilität", "📈", "Rentabilität"]],
     "compare": [{"name": "Termingeld", "vals": ["hoch", "niedrig", "mittel"], "cue": "Termingeld"}, {"name": "Aktienfonds", "vals": ["niedriger", "hoch", "hoch"], "cue": "Aktienfonds"}]})
Q("""Frage: Lukas will in einem Jahr ein Auto kaufen und darf auf keinen Fall Geld verlieren. Termingeld oder Aktienfonds? … *Termingeld*. Kurze Zeit und Sicherheit sind ihm wichtig.
Ein Aktienfonds lohnt sich eher langfristig, wenn man Schwankungen aushalten kann.""",
  "Auto in 1 Jahr, kein Verlust erlaubt – Termingeld oder Aktienfonds?", "Termingeld (sicher, kurzfristig) – Aktienfonds eher langfristig mit Chance & Risiko", "Termingeld")

thema("Verbraucherdarlehen")
T("""Thema sechzehn: das *Verbraucherdarlehen*, also ein Kredit für dich als Privatperson.""")
P("""Ein Verbraucherdarlehen ist ein *Kredit* von einem Unternehmen, meist einer Bank, an einen *Verbraucher*. Bevor die Bank dir Geld gibt, prüft sie deine *Kreditwürdigkeit*.
Sie will wissen: Kann der das zurückzahlen? Dafür schaut sie auf dein Einkommen, deinen *Arbeitsvertrag*, die *SCHUFA*, also deine bisherige Zahlungsmoral, dein Vermögen und andere Schulden.
Der Vertrag muss *schriftlich* sein und alles Wichtige nennen. Am wichtigsten für dich ist der *effektive Jahreszins*, denn der enthält alle Kosten, damit kannst du Angebote fair vergleichen.
Und du hast vierzehn Tage *Widerrufsrecht*.""",
  "Verbraucherdarlehen", [it("Kreditwürdigkeit: Einkommen, Arbeitsvertrag, SCHUFA, Vermögen", "Kreditwürdigkeit"), it("Form: schriftlich", "schriftlich"),
                          it("effektiver Jahreszins = alle Kosten ➜ zum Vergleichen", "effektive"), it("Widerrufsrecht 14 Tage", "Widerrufsrecht")])
TB("""Und weil die Bank auf Nummer sicher gehen will, verlangt sie *Sicherheiten*. Drei musst du kennen. Die *Sicherungsübereignung*: Die Bank wird *Eigentümer*, du bleibst *Besitzer*.
Beim Autokredit hat die Bank zum Beispiel den Fahrzeugbrief, aber du fährst das Auto. Erinnerst du dich an Besitz und Eigentum? Genau das ist es. Die *Bürgschaft*: Eine *andere Person*,
zum Beispiel deine Eltern, haftet für dich, wenn du nicht zahlst. Das muss schriftlich sein. Und die *Lohnabtretung*: Zahlst du nicht, holt sich die Bank einen Teil deines *Lohns* direkt beim *Arbeitgeber*.""",
   "Kreditsicherheiten", ["Sicherheit", "So funktioniert's"],
   [(["Sicherungsübereignung", "Bank = Eigentümer, du = Besitzer (Fahrzeugbrief)"], "Sicherungsübereignung"),
    (["Bürgschaft", "andere Person haftet, schriftlich"], "Bürgschaft"), (["Lohnabtretung", "Bank holt Teil vom Lohn beim Arbeitgeber"], "Lohnabtretung")])
M("""Merke: *Sicherungsübereignung*, die Bank ist *Eigentümer*. *Bürgschaft*, ein *anderer* zahlt. *Lohnabtretung*, es geht *vom Lohn*.""",
  "Sicherungsübereignung = Bank Eigentümer · Bürgschaft = anderer zahlt · Lohnabtretung = vom Lohn")

thema("Überschuldung")
T("""Thema siebzehn, das letzte: die *Überschuldung*. Kein schönes Thema, aber wichtig, weil es schneller passieren kann, als man denkt.""")
D("""Überschuldet ist, wer seine Schulden mit Einkommen und Vermögen *auf Dauer nicht mehr bezahlen* kann. Nicht nur einen Monat knapp, sondern dauerhaft.""",
  "Überschuldung", "Schulden können mit Einkommen und Vermögen auf Dauer nicht mehr bezahlt werden.")
P("""Wie kommt man da rein? Oft durch Schicksalsschläge wie *Arbeitslosigkeit*, *Trennung* oder *Krankheit*. Aber auch durch eigene Fehler: zu viel *Konsum auf Raten*, ein dauernd genutzter *Dispo*
oder mehrere teure *Handyverträge*. Jede Rate wirkt klein, aber zusammen fressen sie das ganze Gehalt auf.""",
  "Ursachen", [it("Arbeitslosigkeit, Trennung, Krankheit", "Arbeitslosigkeit"), it("Konsum auf Raten", "Konsum"), it("Dispo", "Dispo"), it("Handyverträge", "Handyverträge")])
X("""Und wie kommt man wieder raus? In drei Stufen. Erstens ein *Haushaltsplan*: Alle Einnahmen und Ausgaben aufschreiben. Das hilft übrigens auch, damit es gar nicht erst so weit kommt.
Zweitens die *Schuldnerberatung*. Die ist *kostenlos*, zum Beispiel bei der Caritas oder der Verbraucherzentrale, und verhandelt für dich mit den Gläubigern.
Und drittens, wenn gar nichts mehr geht, die *Verbraucherinsolvenz*. Die läuft so: Erst ein *außergerichtlicher Einigungsversuch* mit den Gläubigern. Klappt das nicht, der *Antrag* beim Insolvenzgericht.
Dann kommt die *Wohlverhaltensphase*, *drei Jahre* lang. Da gibst du alles ab, was über dem pfändbaren Freibetrag liegt, arbeitest oder suchst Arbeit und machst keine neuen Schulden.
Und wenn du das durchhältst, kommt die *Restschuldbefreiung*: Die übrigen Schulden sind weg, und du kannst neu anfangen.""",
  [it("Haushaltsplan", "Haushaltsplan"), it("Schuldnerberatung (kostenlos)", "Schuldnerberatung"), it("Einigungsversuch", "außergerichtlicher"), it("Antrag Insolvenzgericht", "Antrag"),
   it("Wohlverhaltensphase 3 Jahre", "Wohlverhaltensphase"), it("Restschuldbefreiung ➜ Neustart", "Restschuldbefreiung")], title="Wege aus der Überschuldung")
M("""Merke den Weg: *Haushaltsplan*, *Schuldnerberatung*, *Insolvenz*, und nach *drei Jahren* ein *Neustart*.""", "Haushaltsplan ➜ Schuldnerberatung ➜ Insolvenz ➜ nach 3 Jahren Neustart")
sc("""Und das war Kompetenzbereich zwei mit allen siebzehn Themen! Wenn du dir eins merken willst: Fast alles hier dreht sich um Verträge, wann sie gelten, was man bei Problemen darf,
und wie man sich schützt. Schau dir die Quizfragen ruhig nochmal an, die sind genau so wie in der Prüfung. Weiter geht's mit Kompetenzbereich drei.""",
   {"type": "kb", "outro": True})

# =====================================================================================
# KB III
# =====================================================================================
kb(3, "Wirtschaften in der Sozialen Marktwirtschaft",
   ["Preisbildung", "Marktformen", "Vollkommener Markt", "Höchst- und Mindestpreis", "Soziale Marktwirtschaft", "Preisindex (VPI)", "Inflation", "Deflation",
    "BIP (Bruttoinlandsprodukt)", "Konjunktur"])
sc("""Willkommen zum Kompetenzbereich drei: Wirtschaften in der *Sozialen Marktwirtschaft*. Hier schauen wir auf die Wirtschaft als Ganzes:
Wie entstehen Preise, was macht der Staat, und wie misst man, ob es der Wirtschaft gut geht. *Zehn Themen*, genau wie auf deinem Lernzettel.""", {"type": "kb"})

thema("Preisbildung")
T("""Thema eins: die *Preisbildung*.""")
P("""Worum geht es? Auf einem *Markt* treffen *Anbieter*, also Verkäufer, und *Nachfrager*, also Käufer, aufeinander. Dabei bildet sich der *Preis*.
Das *Angebot*: Je *höher* der Preis, desto *mehr* wollen die Verkäufer verkaufen. Logisch, es lohnt sich mehr. Die *Nachfrage*: Je *höher* der Preis,
desto *weniger* wollen die Käufer kaufen.""",
  "Angebot & Nachfrage", [it("Markt: Anbieter + Nachfrager ➜ Preis", "Markt"), it("Angebot: Preis höher ➜ mehr verkaufen", "Angebot"),
                          it("Nachfrage: Preis höher ➜ weniger kaufen", "Nachfrage")])
RAW("""Der *Gleichgewichtspreis* ist der Preis, bei dem die *Angebotsmenge* gleich der *Nachfragemenge* ist. Hier wird *am meisten verkauft*, und die Menge heißt *Gleichgewichtsmenge*.
*Grafisch*: Auf der x-Achse ist die *Menge*, auf der y-Achse der *Preis*. Die *Angebotskurve steigt*, die *Nachfragekurve fällt*. Der *Schnittpunkt* ist der Gleichgewichtspreis.""",
    {"type": "chart", "mode": "basic", "cueEq": "Schnittpunkt", "cueOver": "zzz", "cueUnder": "zzz"})
TB("""*Tabellarisch* sieht das so aus. Bei *einem Euro* wollen die Verkäufer nur hundert Kilo anbieten, aber die Käufer wollen fünfhundert. Bei *fünf Euro* ist es umgekehrt.
Bei *drei Euro* ist beides gleich: dreihundert Kilo. Also liegt das *Gleichgewicht bei drei Euro und dreihundert Kilo*.""",
   "Gleichgewicht aus der Tabelle", ["Preis", "Angebot", "Nachfrage"],
   [(["1 €", "100 kg", "500 kg"], "einem"), (["3 €", "300 kg", "300 kg"], "drei", True), (["5 €", "500 kg", "100 kg"], "fünf")],
   note="Gleichgewicht: 3 € und 300 kg")
C("""Was, wenn der Preis nicht stimmt? Ist der *Preis zu hoch*, gibt es einen *Angebotsüberhang*: mehr Angebot als Nachfrage, die Ware bleibt liegen, und der Preis *sinkt*.
Bei fünf Euro: fünfhundert minus hundert gleich *vierhundert Kilo* Angebotsüberhang. Ist der *Preis zu niedrig*, gibt es einen *Nachfrageüberhang*: Die Ware ist knapp,
und der Preis *steigt*. Bei einem Euro: fünfhundert minus hundert gleich vierhundert Kilo Nachfrageüberhang.""",
  "Preis zu hoch", ["Angebotsüberhang", "Ware bleibt liegen ➜ Preis sinkt", "5 €: 500 − 100 = 400 kg"],
  "Preis zu niedrig", ["Nachfrageüberhang", "Ware knapp ➜ Preis steigt", "1 €: 500 − 100 = 400 kg"], "niedrig",
  note="Überhang = größere Menge − kleinere Menge")
TB("""Und wenn sich Angebot oder Nachfrage *ändern*? *Nachfrage steigt*, zum Beispiel *Hitzewelle*, alle wollen *Ventilatoren*: Die Kurve geht nach *rechts*, *Preis und Menge steigen*.
*Nachfrage sinkt*, zum Beispiel *Eis im Winter*: nach *links*, Preis und Menge *sinken*. *Angebot steigt*, zum Beispiel viele *neue E-Bike-Firmen*: nach rechts, der Preis *sinkt*,
die Menge *steigt*. *Angebot sinkt*, zum Beispiel *Missernte* beim Kaffee: nach links, der Preis *steigt*, die Menge *sinkt*.""",
   "Änderungen", ["Was passiert?", "Kurve", "Preis", "Menge"],
   [(["Nachfrage ↑ (Hitzewelle ➜ Ventilatoren)", "rechts", "⬆", "⬆"], "Hitzewelle"), (["Nachfrage ↓ (Winter ➜ Eis)", "links", "⬇", "⬇"], "Winter"),
    (["Angebot ↑ (neue E-Bike-Firmen)", "rechts", "⬇", "⬆"], "E-Bike"), (["Angebot ↓ (Missernte Kaffee)", "links", "⬆", "⬇"], "Missernte")])
M("""Merke: Überhang gleich größere Menge minus kleinere Menge. Und bei Änderungen erst überlegen: Was verschiebt sich, Angebot oder Nachfrage, und in welche Richtung?""",
  "Überhang = größere − kleinere Menge · erst fragen: Angebot oder Nachfrage? Rechts oder links?")

thema("Marktformen")
T("""Thema zwei: die *Marktformen*.""")
P("""Märkte werden nach der *Anzahl der Anbieter* unterschieden, denn je nach Anzahl verhalten sich die Anbieter anders. Das *Polypol*: *viele* Anbieter, viele Nachfrager,
zum Beispiel *Klamottenläden* oder *Friseure*. Erhöht einer stark die Preise, gehen die Kunden einfach zur Konkurrenz. Darum hat einer *kaum Einfluss* auf den Preis.
Der Fachbegriff: *Mengenanpasser*.""",
  "Polypol", [it("viele Anbieter, viele Nachfrager", "viele"), it("z. B. Klamottenläden, Friseure", "Klamottenläden"), it("kaum Einfluss auf den Preis", "Einfluss"),
              it("Fachbegriff: Mengenanpasser", "Mengenanpasser")])
P("""Das *Angebotsoligopol*: *wenige* Anbieter, viele Nachfrager, zum Beispiel *Tankstellen*. Sie *beobachten sich genau*. Senkt einer den Preis, ziehen die anderen nach,
das ist ein *Preiskampf*. Die Gefahr: heimliche *Preisabsprachen*, das nennt man *Kartell*, und das ist *verboten*. Das *Bundeskartellamt* kontrolliert das.
Das *Angebotsmonopol*: *ein* Anbieter, zum Beispiel die Deutsche Bahn beim *Schienennetz* oder der *Wasserversorger*. Er legt den Preis selbst fest, Fachbegriff *Preisfestsetzer*.
Aber nicht beliebig hoch: Bei zu hohen Preisen kaufen die Leute weniger oder weichen aus, zum Beispiel aufs *Auto* statt Bahn.""",
  "Oligopol & Monopol", [it("Oligopol: wenige (Tankstellen) – beobachten sich, Preiskampf", "Angebotsoligopol"), it("Gefahr: Kartell ➜ verboten (Bundeskartellamt)", "Kartell"),
                         it("Monopol: einer (Schienennetz, Wasser) – Preisfestsetzer", "Angebotsmonopol"), it("nicht beliebig hoch: Leute weichen aus", "beliebig")])
TB("""Der *Überblick*: Polypol, viele, *Mengenanpasser*. Oligopol, wenige, *Preiskampf* und Gefahr *Kartell*. Monopol, einer, *Preisfestsetzer*.""",
   "Überblick", ["Marktform", "Anbieter", "Verhalten"],
   [(["Polypol", "viele", "Mengenanpasser"], "Mengenanpasser"), (["Oligopol", "wenige", "Preiskampf, Gefahr Kartell"], "Preiskampf"), (["Monopol", "einer", "Preisfestsetzer"], "Preisfestsetzer")])

thema("Vollkommener Markt")
T("""Thema drei: der *vollkommene Markt*.""")
P("""Der vollkommene Markt ist ein *Modell*, also eine Idee zum Erklären. In echt gibt es ihn *nicht*. Fünf *Bedingungen*: Erstens *homogene Güter*, alle Produkte sind völlig gleich.
Zweitens *vollständige Markttransparenz*, alle kennen alle Preise und Angebote. Drittens *keine Präferenzen*, also keine Vorlieben: keine *persönlichen*, wie ein netter Verkäufer,
keine *räumlichen*, wie ein näherer Laden, keine *zeitlichen*, wie eine schnellere Lieferung. Viertens *sofortige Reaktion* aller auf Preisänderungen. Und fünftens ein *Polypol*.""",
  "Bedingungen", [it("homogene Güter", "homogene"), it("vollständige Markttransparenz", "Markttransparenz"), it("keine Präferenzen (persönlich, räumlich, zeitlich)", "Präferenzen"),
                  it("sofortige Reaktion", "sofortige"), it("Polypol", "Polypol")])
X("""Ein Beispiel: Du kaufst beim *Bäcker um die Ecke*, obwohl es zweihundert Meter weiter *billiger* ist, weil er *näher* ist und die Verkäuferin *nett* ist.
Das sind eine *räumliche* und eine *persönliche* Präferenz, also *kein* vollkommener Markt.""",
  [it("Bäcker um die Ecke", "Bäcker"), it("200 m weiter billiger", "billiger"), it("näher + nette Verkäuferin", "näher"), it("räumliche & persönliche Präferenz", "räumliche"),
   it("➜ kein vollkommener Markt", "kein")], title="Beispiel")
M("""Merke: Gleiche Ware, alle wissen alles, keine Vorlieben, sofortige Reaktion.""", "gleiche Ware · alle wissen alles · keine Vorlieben · sofortige Reaktion")

thema("Höchst- und Mindestpreis")
T("""Thema vier: *Höchst- und Mindestpreis*.""")
P("""Normalerweise bestimmt der Markt den Preis. Das hat aber *Nachteile*: Manche Preise sind für Käufer *zu teuer*, zum Beispiel *Mieten in Stuttgart*. Andere sind für Verkäufer
*zu billig*, zum Beispiel der *Milchpreis* für Bauern. Dann *legt der Staat* für eine Ware einen *Preis fest*.""",
  "Warum greift der Staat ein?", [it("zu teuer für Käufer (Mieten in Stuttgart)", "teuer"), it("zu billig für Verkäufer (Milchpreis)", "billig"), it("Staat legt Preis fest", "legt")])
C("""Der *Höchstpreis* ist eine *Decke*. Beispiel: Die Miete darf nicht über einen bestimmten Betrag steigen. Es darf also *nicht teurer* sein als, er schützt die *Käufer*,
und er liegt *unter* dem Gleichgewichtspreis. Was passiert? Die Miete bleibt billig, viele wollen eine Wohnung, aber Vermieter bauen keine neuen: ein *Nachfrageüberhang*.
Vorteil: Dinge bleiben bezahlbar. Probleme: *Knappheit*, also lange Wohnungssuche, *Schwarzmarkt*, weniger Produktion und schlechtere Qualität.
Der *Mindestpreis* ist ein *Boden*. Beispiel: Milch darf nicht billiger sein als ein bestimmter Betrag. Er schützt die *Verkäufer* und liegt *über* dem Gleichgewichtspreis.
Was passiert? Milch ist teurer, die Leute kaufen weniger, die Bauern produzieren mehr: ein *Angebotsüberhang*. Vorteil: sichere Einnahmen für die Bauern.
Probleme: Verbraucher zahlen mehr, und der Staat kauft die übrige Milch mit Steuergeld auf, das ist Verschwendung.""",
  "Höchstpreis = DECKE ⬇", ["nicht teurer als … (Miete)", "schützt Käufer", "liegt UNTER dem GG-Preis", "➜ Nachfrageüberhang, Knappheit, Schwarzmarkt"],
  "Mindestpreis = BODEN ⬆", ["nicht billiger als … (Milch)", "schützt Verkäufer", "liegt ÜBER dem GG-Preis", "➜ Angebotsüberhang, Staat kauft auf"], "Mindestpreis")
TB("""Wann wirkt so ein Preis überhaupt? Sagen wir, der Marktpreis ist *zehn Euro*. Ein Höchstpreis von *acht Euro* wirkt, denn er drückt den Preis runter.
Ein Höchstpreis von *zwölf Euro* wirkt nicht, der Preis liegt ja eh darunter. Beim Mindestpreis genau umgekehrt: *zwölf Euro* wirkt, acht Euro nicht.""",
   "Wann wirkt es? (Marktpreis 10 €)", ["", "wirkt ✅", "keine Wirkung ❌"],
   [(["Höchstpreis", "8 €", "12 €"], "Höchstpreis"), (["Mindestpreis", "12 €", "8 €"], "Mindestpreis")])
M("""Merke: Die Decke muss runterdrücken, also unter dem Marktpreis liegen. Der Boden muss hochdrücken, also über dem Marktpreis liegen.""",
  "Decke muss runterdrücken ➜ UNTER dem Marktpreis · Boden muss hochdrücken ➜ ÜBER dem Marktpreis")

thema("Soziale Marktwirtschaft")
T("""Thema fünf: die *Soziale Marktwirtschaft*.""")
P("""Die Grundidee: Der Markt ist *frei*, Firmen entscheiden selbst, was sie herstellen und zu welchem Preis. Aber der *Staat greift ein*, um für *sozialen Ausgleich*
zu sorgen und die Schwächeren zu schützen. Der Merksatz: *So viel Markt wie möglich, so viel Staat wie nötig.* Das Wesen besteht aus *zwei Säulen*:
*Freiheit*, also freie Preisbildung, Wettbewerb, Privateigentum, Vertragsfreiheit und Gewerbefreiheit. Und *sozialer Ausgleich*: soziale Sicherheit,
soziale Gerechtigkeit, Schutz des Wettbewerbs und Schutz der Umwelt.""",
  "Grundidee & 2 Säulen", [it("„So viel Markt wie möglich, so viel Staat wie nötig.“", "Markt"), it("Säule 1: Freiheit – Preisbildung, Wettbewerb, Eigentum, Vertrags- & Gewerbefreiheit", "Freiheit"),
                           it("Säule 2: sozialer Ausgleich – Sicherheit, Gerechtigkeit, Wettbewerbs- & Umweltschutz", "sozialer")])
C("""Der Unterschied zur *freien* Marktwirtschaft: Dort greift der Staat *kaum* ein. In der *Sozialen* Marktwirtschaft setzt er *Regeln und Grenzen*, zum Beispiel beim Arbeitsschutz.
So ist es in *Deutschland*.""",
  "Freie Marktwirtschaft", ["Staat greift kaum ein"], "Soziale Marktwirtschaft", ["Staat setzt Regeln & Grenzen", "z. B. Arbeitsschutz", "so in Deutschland"], "Sozialen")
TB("""Es gibt *vier Instrumente*. Die *Sozialpolitik*: Schwache schützen, mit Sozialversicherung, Kindergeld und Bürgergeld. Die *Einkommenspolitik*: gerechtere Einkommen,
mit *Mindestlohn* und *Steuerprogression*. Die *Wettbewerbspolitik*: Konkurrenz sichern, mit *Bundeskartellamt* und Kartellverbot. Und die *Umweltpolitik*: Umwelt schützen,
mit *CO-zwei-Preis*, Grenzwerten und der Förderung von Wärmepumpen.""",
   "Die 4 Instrumente", ["Instrument", "Ziel", "Beispiele"],
   [(["Sozialpolitik", "Schwache schützen", "Sozialversicherung, Kindergeld, Bürgergeld"], "Sozialpolitik"),
    (["Einkommenspolitik", "gerechtere Einkommen", "Mindestlohn, Steuerprogression"], "Einkommenspolitik"),
    (["Wettbewerbspolitik", "Konkurrenz sichern", "Bundeskartellamt, Kartellverbot"], "Wettbewerbspolitik"),
    (["Umweltpolitik", "Umwelt schützen", "CO₂-Preis, Grenzwerte, Wärmepumpen"], "Umweltpolitik")])
C("""Zwei Begriffe werden oft verwechselt. Das *Solidaritätsprinzip*: Jeder zahlt *Beiträge nach seinem Einkommen*, jeder bekommt Hilfe *nach seinem Bedarf*, das gehört zur Sozialpolitik.
Die *Steuerprogression*: Wer mehr verdient, zahlt *prozentual mehr Steuern*, das gehört zur Einkommenspolitik.""",
  "Solidaritätsprinzip", ["Beiträge nach Einkommen", "Hilfe nach Bedarf", "➜ Sozialpolitik"], "Steuerprogression", ["mehr verdienen ➜ prozentual mehr Steuern", "➜ Einkommenspolitik"], "Steuerprogression")
C("""Und die *Wirkung* zweier Instrumente. Der *Mindestlohn*: Eine Stunde Arbeit darf nicht schlechter bezahlt werden als ein festgelegter Betrag. Vorteile: Geringverdiener haben mehr Geld,
weniger Menschen brauchen Hilfe vom Staat, Schutz vor Lohndumping. Nachteile, merk dir *P S P*: *Preise* steigen, *Stellenabbau*, *Pleite* kleiner Betriebe.
Und wichtig: Den Mindestlohn zahlt der *Arbeitgeber*, nicht der Staat. Der *CO-zwei-Preis*: Vorteil, die Leute steigen auf Umweltfreundliches um, Fahrrad, Bus, Wärmepumpe.
Nachteil: *Geringverdiener*, die aufs Auto angewiesen sind, werden hart getroffen.""",
  "Mindestlohn", ["➕ mehr Geld, weniger Staatshilfe, kein Lohndumping", "➖ P–S–P: Preise, Stellenabbau, Pleite", "zahlt der Arbeitgeber!"],
  "CO₂-Preis", ["➕ Umstieg: Fahrrad, Bus, Wärmepumpe", "➖ trifft Geringverdiener mit Auto"], "CO")

thema("Preisindex (VPI)")
T("""Thema sechs: der *Preisindex*, genauer der *Verbraucherpreisindex*.""")
X("""Der Staat will wissen: Wie viel *teurer* wird das Leben? Dafür gibt es den Verbraucherpreisindex, ermittelt vom *Statistischen Bundesamt* in *vier Schritten*.
Erstens den *Warenkorb festlegen*: alles, was ein normaler Haushalt kauft, Lebensmittel, Miete, Strom, Kleidung, Handy, Friseur, etwa *sechshundertfünfzig* Sachen.
Zweitens *gewichten*: Was viel Geld kostet, zählt mehr. Die *Miete* zählt viel mehr als Brötchen. Drittens *Preise prüfen*: Jeden Monat werden in ganz Deutschland die Preise erfasst.
Viertens *vergleichen*: mit einem *Basisjahr*, das auf *hundert* gesetzt wird.""",
  [it("Warenkorb festlegen (ca. 650 Sachen)", "Warenkorb"), it("gewichten (Miete > Brötchen)", "gewichten"), it("Preise prüfen (jeden Monat)", "prüfen"),
   it("vergleichen mit Basisjahr = 100", "vergleichen")], title="So wird der VPI ermittelt")
F("""Ein Beispiel: Der Warenkorb kostet im Basisjahr *tausend Euro*, das ist Index hundert. Heute kostet er *zwölfhundert Euro*, das ist Index *hundertzwanzig*.
Das heißt: Das Leben ist *zwanzig Prozent teurer* als im Basisjahr.""",
  [["Basisjahr 1.000 € = 100", "#2563eb", "tausend"], ["➜", "#1f2937", "zwölfhundert"], ["heute 1.200 € = 120", "#dc2626", "zwölfhundert"], ["= + 20 %", "#16a34a", "zwanzig"]])
M("""Merke: Warenkorb, gewichten, Preise prüfen, mit Basisjahr vergleichen.""", "Warenkorb ➜ gewichten ➜ Preise prüfen ➜ mit Basisjahr vergleichen")

thema("Inflation")
T("""Thema sieben: die *Inflation*.""")
P("""Inflation heißt: Die Preise steigen *allgemein* und *über längere Zeit*. Nicht nur ein einzelnes Produkt, sondern fast alles. Bei Inflation verliert das *Geld an Wert*.
Die *Inflationsrate* sagt, um wie viel Prozent die Preise im Vergleich zum *Vorjahr* gestiegen sind. Bei *drei Prozent* kostet, was letztes Jahr hundert Euro gekostet hat,
jetzt hundertdrei Euro.""",
  "Inflation", [it("Preise steigen allgemein & über längere Zeit", "allgemein"), it("Geld verliert an Wert", "Wert"), it("Inflationsrate: % zum Vorjahr", "Inflationsrate"),
                it("3 %: 100 € ➜ 103 €", "drei")])
TB("""Die *Ursachen*, merk dir *N K I*. *N* wie *Nachfrageinflation*: Die Leute wollen mehr kaufen, als es gibt, die Ware wird knapp, die Preise steigen. Nach Corona wollten alle reisen,
Flüge und Hotels wurden teurer. *K* wie *Kosteninflation*: Die Herstellung wird teurer, Löhne, Rohstoffe, Energie, und die Firmen geben das weiter. Gas wird teurer,
der Bäcker zahlt mehr für den Ofen, das Brot wird teurer. *I* wie *importierte Inflation*: Waren aus dem Ausland werden teurer. Zweitausendzweiundzwanzig wurden Öl und Gas teurer,
also wurden Tanken und Heizen teurer.""",
   "Ursachen: N – K – I", ["Ursache", "Erklärung", "Beispiel"],
   [(["N – Nachfrageinflation", "mehr Nachfrage als Ware", "nach Corona: Flüge, Hotels"], "Nachfrageinflation"),
    (["K – Kosteninflation", "Löhne, Rohstoffe, Energie teurer", "Gas ➜ Bäcker ➜ Brot"], "Kosteninflation"),
    (["I – importierte Inflation", "Waren aus dem Ausland teurer", "2022: Öl, Gas ➜ Tanken, Heizen"], "importierte")])
P("""Folge eins: Die *Kaufkraft sinkt*. Kaufkraft heißt: Wie viel kannst du dir für dein Geld kaufen? Ein *Döner* kostet *fünf Euro*, mit zwanzig Euro bekommst du *vier* Döner.
Kostet er *zehn Euro*, nur noch *zwei*. Folge zwei: Der *Reallohn* kann sinken. Der *Nominallohn* ist die Zahl auf deiner Lohnabrechnung, der *Reallohn* ist, was du dir davon
*wirklich kaufen* kannst. Faustregel: Reallohn gleich Lohnerhöhung minus Inflationsrate. Lohn plus *drei* Prozent, Inflation *fünf* Prozent, Reallohn *minus zwei* Prozent, er *sinkt*.
Lohn plus *sechs*, Inflation *zwei*, Reallohn plus *vier*, er *steigt*.""",
  "Folgen: Kaufkraft & Reallohn", [it("Kaufkraft sinkt: Döner 5 € ➜ 4 Stück, 10 € ➜ 2 Stück", "Döner"), it("Nominallohn = Zahl auf der Abrechnung", "Nominallohn"),
                                   it("Reallohn = was du wirklich kaufen kannst", "Reallohn"), it("Lohn + 3 %, Inflation 5 % ➜ Reallohn − 2 %", "drei"),
                                   it("Lohn + 6 %, Inflation 2 % ➜ Reallohn + 4 %", "sechs")])
C("""Folge drei: *Verlierer und Gewinner*. Verlierer sind die *Sparer*, das Geld auf dem Konto ist weniger wert. Die *Arbeitnehmer*, wenn der Lohn nicht mitsteigt.
Und *Geringverdiener und Rentner*, die fast alles für Miete, Essen und Energie brauchen. Gewinner sind die *Schuldner*: Die Schulden bleiben gleich, aber das Geld ist weniger wert,
die Schulden werden „leichter“. Und Besitzer von *Sachwerten* wie Haus oder Gold. Und die Gefahr: die *Lohn-Preis-Spirale*. Preise steigen, Arbeitnehmer wollen mehr Lohn,
Firmen haben höhere Kosten und erhöhen die Preise, Arbeitnehmer wollen wieder mehr Lohn, und so weiter.""",
  "Verlierer 😟", ["Sparer", "Arbeitnehmer (ohne Lohnplus)", "Geringverdiener & Rentner"], "Gewinner 😊", ["Schuldner", "Sachwert-Besitzer (Haus, Gold)"], "Gewinner",
  note="Gefahr: Lohn-Preis-Spirale 🌀")
M("""Merke: Inflation steigt, Kaufkraft sinkt. Und Reallohn gleich Lohnerhöhung minus Inflationsrate.""", "Inflation ⬆ ➜ Kaufkraft ⬇ · Reallohn = Lohnerhöhung − Inflationsrate")

thema("Deflation")
T("""Thema acht: die *Deflation*.""")
P("""Deflation ist das *Gegenteil* von Inflation: Die Preise *sinken* allgemein und dauerhaft. Klingt gut, ist aber *gefährlich*. Bei Deflation *gewinnt* das Geld an Wert.
Die *Ursachen*: Die *Nachfrage sinkt*. In einer *Krise* haben die Leute Angst um ihren Job und *sparen*, die Firmen bleiben auf der Ware sitzen und senken die Preise.
Oder *zu viel Angebot*: Firmen stellen mehr her, als gekauft wird. Achtung: Die *Ursache* ist Angst und Sparen. Dass die Leute auf billigere Preise *warten*, ist schon die *Folge*.""",
  "Deflation", [it("Preise sinken allgemein & dauerhaft", "sinken"), it("Geld gewinnt an Wert", "gewinnt"), it("Ursache: Nachfrage sinkt (Krise, Angst, Sparen)", "Krise"),
                it("Ursache: zu viel Angebot", "Angebot"), it("Warten auf billigere Preise = schon die Folge!", "Folge")])
X("""Die Folgen: Die *Kaufkraft steigt*, Gewinner sind die *Sparer*. Verlierer sind die *Schuldner*, ihre Schulden werden „schwerer“, die *Unternehmen* und die *Arbeitnehmer*.
Und die Gefahr ist die *Deflationsspirale*: Die Leute *warten* mit dem Kaufen, „das Handy wird noch billiger“. Die Firmen machen *weniger Umsatz*. Sie *entlassen* Mitarbeiter.
Die Arbeitslosen *kaufen noch weniger*. Und die Preise *sinken weiter*, und alles geht von vorne los, bis zur *Krise*.""",
  [it("Leute warten mit dem Kaufen", "warten"), it("weniger Umsatz", "Umsatz"), it("Entlassungen", "entlassen"), it("Arbeitslose kaufen noch weniger", "Arbeitslosen"),
   it("Preise sinken weiter ➜ Krise", "weiter")], title="Deflationsspirale 🌀")
TB("""Der Überblick: Bei *Inflation* steigen die Preise, die Kaufkraft sinkt, Sparer verlieren, Schuldner gewinnen. Bei *Deflation* ist alles genau *umgekehrt*.""",
   "Inflation vs. Deflation", ["", "Inflation 🔥", "Deflation ❄️"],
   [(["Preise", "steigen", "sinken"], "Inflation"), (["Kaufkraft", "sinkt", "steigt"], "Kaufkraft"), (["Sparer", "verlieren", "gewinnen"], "Sparer"),
    (["Schuldner", "gewinnen", "verlieren"], "Schuldner")])

thema("BIP (Bruttoinlandsprodukt)")
T("""Thema neun: das *BIP*, das *Bruttoinlandsprodukt*.""")
P("""Der Staat will wissen: *Wie stark* ist unsere Wirtschaft? Dafür gibt es das BIP, sozusagen das *Zeugnis der Wirtschaft*. Das BIP ist der *Wert aller Waren und Dienstleistungen*,
die *in einem Jahr* im *Inland*, also in Deutschland, hergestellt werden. Zum Beispiel ein *Auto aus Stuttgart*, ein *Haarschnitt* oder deine *Arbeit beim Kunden* an einer Anlage.
Baut eine deutsche Firma in *China* ein Auto, zählt das *nicht*. Der Fachbegriff: *gesamtwirtschaftliche Messgröße*.""",
  "Was ist das BIP?", [it("Wert aller Waren & Dienstleistungen", "Wert"), it("in einem Jahr im Inland", "Inland"), it("Auto aus Stuttgart, Haarschnitt, deine Arbeit beim Kunden", "Stuttgart"),
                       it("deutsche Firma baut in China ➜ zählt NICHT", "China"), it("gesamtwirtschaftliche Messgröße", "gesamtwirtschaftliche")])
C("""Es gibt das *nominale* und das *reale* BIP, das funktioniert genauso wie Nominallohn und Reallohn. Das *nominale* BIP rechnet mit *heutigen Preisen*, die Inflation steckt drin.
Beim *realen* BIP ist die *Inflation herausgerechnet*, es zeigt, ob *wirklich mehr* hergestellt wurde. Beispiel: nominal plus fünf Prozent, Inflation drei Prozent, real plus zwei Prozent.
Das reale BIP ist also *aussagekräftiger*.""",
  "nominales BIP", ["heutige Preise", "Inflation steckt drin"], "reales BIP", ["Inflation herausgerechnet", "zeigt echtes Wachstum", "nominal + 5 %, Inflation 3 % ➜ real + 2 %"], "realen",
  note="Das reale BIP ist aussagekräftiger")
C("""Ist das BIP ein guter *Wohlstandsindikator*? Das musst du kritisch beurteilen können. Vorteile: *einfach zu messen*, und Jahre und Länder sind *vergleichbar*.
Kritik: Erstens fehlt *unbezahlte Arbeit*, also Hausarbeit, Kindererziehung, Pflege, Ehrenamt. Zweitens fehlt *Schwarzarbeit*. Drittens werden *Umweltschäden* nicht abgezogen,
nach einer Katastrophe *steigt* das BIP durch die Reparaturen sogar. Viertens fehlt die *Verteilung*: Landet das Geld nur bei wenigen Reichen? Und fünftens fehlt die *Lebensqualität*,
also Gesundheit, Freizeit und Zufriedenheit.""",
  "➕ Vorteile", ["einfach zu messen", "Jahre & Länder vergleichbar"],
  "➖ Kritik", ["unbezahlte Arbeit fehlt", "Schwarzarbeit fehlt", "Umweltschäden nicht abgezogen", "Verteilung fehlt", "Lebensqualität fehlt"], "Kritik")
M("""Der Merksatz: Ein hohes BIP heißt *nicht automatisch*, dass es den Menschen gut geht.""", "Ein hohes BIP heißt nicht automatisch, dass es den Menschen gut geht.")

thema("Konjunktur")
T("""Thema zehn, das letzte: die *Konjunktur*.""")
RAW("""Die Wirtschaft läuft nicht immer gleich gut. Mal geht es *bergauf*, mal *bergab*, wie *Wellen*. Dieses Auf und Ab heißt Konjunktur. Es gibt *vier Phasen*.
Der *Aufschwung*: mehr Kauf, mehr Aufträge, Firmen stellen ein, die Arbeitslosigkeit sinkt. Die *Hochkonjunktur*, der Boom: Die Wirtschaft läuft auf Hochtouren, fast alle haben Arbeit,
die Preise steigen stark. Der *Abschwung*, die Rezession: weniger Kauf, weniger Aufträge, Entlassungen, die Arbeitslosigkeit steigt. Und der *Tiefstand*, die Depression: ganz unten,
hohe Arbeitslosigkeit, wenig Nachfrage. Im Schulbuch sind die Wellen gleichmäßig, in echt sind die Phasen *unterschiedlich lang und stark*. Manchmal kommt ein plötzlicher Absturz,
wie *Corona zweitausendzwanzig*.""",
    {"type": "cycle", "cues": ["Aufschwung", "Hochkonjunktur", "Abschwung", "Tiefstand"],
     "ind": [it("idealtypisch: gleichmäßige Wellen", "Schulbuch"), it("real: unterschiedlich lang & stark (Corona 2020)", "Corona")]})
TB("""Woran erkennt man die Phase? An den *Konjunkturindikatoren*. Die *Auftragseingänge* sind der *Frühindikator*, sie zeigen die *Zukunft*. Das *BIP* ist der *Präsenzindikator*,
es zeigt die *Gegenwart*. Und die *Arbeitslosenquote* ist der *Spätindikator*, denn Firmen stellen erst ein, wenn sie *sicher* sind. Im Aufschwung also: Aufträge steigen,
dann steigt das BIP, und erst dann sinkt die Arbeitslosigkeit.""",
   "Konjunkturindikatoren", ["Indikator", "Art", "zeigt"],
   [(["Auftragseingänge", "Frühindikator", "Zukunft"], "Auftragseingänge"), (["BIP", "Präsenzindikator", "Gegenwart"], "Präsenzindikator"),
    (["Arbeitslosenquote", "Spätindikator", "Firmen stellen erst ein, wenn sicher"], "Arbeitslosenquote")],
   note="Aufschwung: Aufträge ⬆ ➜ BIP ⬆ ➜ Arbeitslosigkeit ⬇")
TB("""Was kann der *Staat* tun? Immer das *Gegenteil*: im *Abschwung Gas geben*, im *Boom bremsen*. Mit der *Staatsnachfrage*: Im Abschwung *gibt er mehr aus*,
für Schulen und Straßen, Firmen bekommen Aufträge und stellen Leute ein. Im Boom gibt er weniger aus. Mit der *Einkommensteuer*: Im Abschwung *senken*, dann haben die Leute mehr Netto,
kaufen mehr, und die Firmen verkaufen mehr. Im Boom *erhöhen*, dann gibt es weniger Nachfrage, und die Preise steigen nicht so stark.""",
   "Was kann der Staat tun?", ["", "Abschwung (Gas geben)", "Boom (bremsen)"],
   [(["Staatsnachfrage", "erhöhen (Schulen, Straßen)", "senken"], "Staatsnachfrage"), (["Einkommensteuer", "senken ➜ mehr Netto", "erhöhen"], "Einkommensteuer")])
C("""Aber es gibt *Probleme*, merk dir *S Z S*: *Schulden*, der Staat muss oft Kredite aufnehmen. *Zu spät*, bis eine Schule gebaut ist, dauert es lange.
Und *Sparen*: Die Leute legen die Steuerersparnis zur Seite, dann wirkt es nicht. Und was hat das mit *dir* zu tun? Im *Abschwung* gibt es weniger Aufträge,
die Übernahme nach der Ausbildung wird unsicherer. Gibt der Staat mehr aus und saniert *Schulen*, braucht es neue *Gebäudetechnik*, das sind Aufträge für deinen Betrieb.
Und eine *Steuersenkung* heißt *mehr Netto* für dich.""",
  "Probleme: S – Z – S", ["Schulden", "zu spät", "Sparen statt Kaufen"], "Was hat das mit dir zu tun?", ["Abschwung: Übernahme unsicherer", "Schulen saniert ➜ Aufträge Gebäudetechnik", "Steuersenkung ➜ mehr Netto"], "dir")
sc("""Das war Kompetenzbereich drei mit allen *zehn Themen*. Hier noch einmal der Überblick. Weiter geht's mit dem letzten Bereich, der Selbstständigkeit.""",
   {"type": "kb", "outro": True})

# =====================================================================================
# KB IV – im Lehrer-Erklärstil
# =====================================================================================
kb(4, "Entscheidungen bei einer Selbstständigkeit", ["Selbstständigkeit", "Geschäftsplan und Standort", "Rechtsformen", "Kapitalbedarfsplan"])
sc("""Willkommen zu Kompetenzbereich vier, dem letzten! Hier geht es um eine Frage, die du dir als Elektroniker vielleicht irgendwann wirklich stellst:
Soll ich mich *selbstständig* machen? Wir begleiten dabei Lukas, der genau das vorhat, und gehen die *vier Themen* deines Lernzettels Schritt für Schritt durch.
Du wirst sehen: Die vier Themen sind eigentlich vier Entscheidungen, die man bei einer Gründung nacheinander trifft.""", {"type": "kb"})

thema("Selbstständigkeit")
T("""Thema eins: die *Selbstständigkeit*. Die erste Entscheidung ist also: Passt das überhaupt zu mir?""")
D("""Stell dir vor, du bist morgen dein eigener Chef. Klingt erstmal super, oder? Keiner sagt dir mehr, was du tun sollst. Aber: Es zahlt dir auch keiner mehr jeden Monat ein festes Gehalt.
Genau das ist die Definition: Selbstständig ist, wer sein *eigenes Unternehmen* führt. Du hast *keinen Chef*, aber du trägst das *ganze Risiko*.""",
  "Selbstständigkeit", "Wer sein eigenes Unternehmen führt. Kein Chef, aber das ganze Risiko.")
P("""Warum machen Leute das trotzdem? Das sind die *Motive*. Lukas zum Beispiel will sein *eigener Chef* sein und nicht mehr gesagt bekommen, wie er eine Anlage zu verdrahten hat.
Er hat *eigene Ideen*, er will sich auf Photovoltaik spezialisieren. Er hofft, *mehr zu verdienen*, denn der Gewinn gehört ihm. Er will sich *selbst verwirklichen*, also etwas Eigenes aufbauen.
Und manche gründen auch, weil *kein passender Job* in Aussicht ist. Das ist dann eher ein Motiv aus der Not.""",
  "Motive – warum gründen?", [it("eigener Chef sein", "eigener"), it("eigene Ideen umsetzen", "Ideen"), it("mehr verdienen", "verdienen"),
                              it("Selbstverwirklichung", "verwirklichen"), it("kein passender Job in Aussicht", "Job")])
TB("""Aber nicht jeder ist ein guter Unternehmer. Dafür braucht man bestimmte *Eigenschaften*. Und jetzt der wichtigste Prüfungstipp in diesem Thema: Nenn eine Eigenschaft *nie allein*,
sondern immer *mit Begründung*. Also nicht nur „Belastbarkeit“, sondern: *Belastbarkeit*, *weil* man als Selbstständiger viel Arbeit und Stress hat.
*Kommunikationsfähigkeit*, weil man ständig mit Kunden, Mitarbeitern und der Bank reden muss. *Fachwissen*, weil man das Handwerk beherrschen muss, sonst kommen keine Kunden wieder.
*Kaufmännisches Wissen*, weil man rechnen und planen muss. *Entscheidungsfreude*, weil kein Chef mehr entscheidet. Und *Risikobereitschaft*, weil das eigene Geld verloren gehen kann.""",
   "Eigenschaften – immer mit „weil“!", ["Eigenschaft", "weil …"],
   [(["Belastbarkeit", "viel Arbeit und Stress"], "Belastbarkeit"), (["Kommunikationsfähigkeit", "mit Kunden, Mitarbeitern, Bank reden"], "Kommunikationsfähigkeit"),
    (["Fachwissen", "das Handwerk beherrschen"], "Fachwissen"), (["Kaufmännisches Wissen", "rechnen und planen"], "Kaufmännisches"),
    (["Entscheidungsfreude", "allein entscheiden"], "Entscheidungsfreude"), (["Risikobereitschaft", "eigenes Geld kann verloren gehen"], "Risikobereitschaft")])
TB("""Und jetzt das Herzstück: *Chancen und Risiken*. Das ist wie eine Waage, und zu jedem Bereich gibt es eine gute und eine schlechte Seite.
*Einkommen*: Die Chance ist, *mehr* zu verdienen, der Gewinn gehört dir. Das Risiko: Es gibt *kein festes Gehalt*. In einem schlechten Monat kommt vielleicht fast nichts rein,
im schlimmsten Fall verlierst du dein Geld, bis zur *Insolvenz*, also Zahlungsunfähigkeit. *Arbeitszeit*: Du kannst dir die Zeit *selbst einteilen*, aber am Anfang arbeitest du viel mehr,
oft auch am Wochenende. *Verantwortung*: Du *entscheidest selbst*, bist aber auch für *alles* verantwortlich, sogar für die Jobs deiner Mitarbeiter.
Und *Absicherung*: Du kannst Versicherungen *frei wählen*, musst aber alles *selbst zahlen*. Bist du krank, zahlt keiner deinen Lohn weiter, und bezahlten Urlaub gibt es auch nicht.""",
   "Chancen ⚖ Risiken", ["Bereich", "Chance ➕", "Risiko ➖"],
   [(["Einkommen", "mehr verdienen, Gewinn gehört mir", "kein festes Gehalt, bis Insolvenz"], "Einkommen"),
    (["Arbeitszeit", "Zeit selbst einteilen", "viel Arbeit, Wochenende, wenig Urlaub"], "Arbeitszeit"),
    (["Verantwortung", "selbst entscheiden", "für alles verantwortlich, auch Mitarbeiter"], "Verantwortung"),
    (["Absicherung", "Versicherungen frei wählen", "alles selbst zahlen, keine Lohnfortzahlung"], "Absicherung")])
M("""Damit du die vier Bereiche nie vergisst, hier der Trick: *Geld*, *Zeit*, *Verantwortung*, *Absicherung*. Sag es dir ein paar Mal vor, das sitzt dann.""",
  "Trick: Geld – Zeit – Verantwortung – Absicherung")
Q("""Prüfungsfrage: Nenne eine Unternehmereigenschaft. … Und? Hast du nur das Wort gesagt? Dann gibt es nur halbe Punkte! Richtig wäre zum Beispiel:
*Risikobereitschaft*, *weil* man sein eigenes Geld verlieren kann. Immer mit *weil*.""",
  "Nenne eine Unternehmereigenschaft.", "z. B. Risikobereitschaft, WEIL man eigenes Geld verlieren kann – immer mit Begründung!", "Risikobereitschaft")

thema("Geschäftsplan und Standort")
T("""Thema zwei: *Geschäftsplan und Standort*. Lukas hat sich entschieden, er will es wagen. Aber einfach loslegen wäre leichtsinnig.""")
D("""Stell dir vor, du baust eine große Schaltanlage ohne Schaltplan. Das geht schief, oder? Genauso ist es bei einer Gründung. Der Schaltplan einer Gründung ist der *Geschäftsplan*:
ein *schriftliches Konzept*, das zwei Fragen beantwortet. *Was* will ich machen? Und *wie* verdiene ich damit Geld?""",
  "Geschäftsplan", "Schriftliches Konzept für die Gründung: Was will ich machen, und wie verdiene ich damit Geld?")
P("""Was steht drin? Die *Geschäftsidee*, bei Lukas ein Elektrobetrieb für Photovoltaik. Die *Gründerperson*, also seine Ausbildung und Erfahrung. *Kunden und Markt*: Wer braucht das?
Die *Konkurrenz*: Wer macht das schon, und was macht Lukas besser? Das *Marketing*: Wie erfahren die Kunden von ihm? Dann *Standort*, *Rechtsform*, *Personal* und ganz wichtig die *Finanzen*,
also der Kapitalbedarfsplan. Und wozu das Ganze? Das ist die *Funktion*: Lukas muss alles *durchdenken*, viele Fehler fallen schon auf dem Papier auf. Das senkt das Risiko.
Und ohne Geschäftsplan bekommt er keinen *Kredit*. Damit sind wir bei den *Adressaten*, also wer ihn liest: vor allem die *Bank*, dann der *Gründer selbst* und *Förderstellen*,
zum Beispiel die Agentur für Arbeit.""",
  "Geschäftsplan", [it("Inhalt: Idee, Gründerperson, Kunden & Markt, Konkurrenz", "Geschäftsidee"), it("… Marketing, Standort, Rechtsform, Personal, Finanzen", "Marketing"),
                    it("Funktion: durchdenken ➜ weniger Risiko + Kredit", "Funktion"), it("Adressaten: Bank, Gründer selbst, Förderstellen", "Adressaten")])
P("""Ein Punkt im Geschäftsplan ist besonders wichtig: der *Standort*, also der *Ort*, an dem das Unternehmen sitzt. Der entscheidet oft über *Erfolg oder Misserfolg*.
Worauf achtet man? Auf die *Standortfaktoren*: Gibt es *Kunden* in der Nähe? Wie viel *Konkurrenz* sitzt nebenan? Was *kostet* die Miete oder Pacht? Wie ist die *Erreichbarkeit*,
also Parkplätze, Bus und Bahn? Und passen *Größe und Ausstattung*, gibt es Platz und kann man später erweitern?""",
  "Standortfaktoren", [it("Kunden in der Nähe", "Kunden"), it("Konkurrenz in der Nähe", "Konkurrenz"), it("Kosten (Miete, Pacht)", "kostet"),
                       it("Erreichbarkeit (Parkplätze, Bus, Bahn)", "Erreichbarkeit"), it("Größe & Ausstattung (Platz, Erweiterung)", "Größe")])
X("""In der Prüfung bekommst du dafür meist eine *Bewertungstabelle* mit zwei oder drei Standorten. So gehst du vor: Erstens vergibst du für jeden Faktor und jeden Standort *Punkte*,
und zwar passend zu den Infos in der *Anlage*. Zweitens *addierst* du die Punkte. Und drittens empfiehlst du den Standort mit den *meisten Punkten*, und, wie immer, *mit Begründung*.
Zum Beispiel: Der Standort im Gewerbegebiet hat die meisten Punkte, weil die Miete günstig ist und genug Platz für ein Lager da ist.""",
  [it("Punkte pro Faktor & Standort (passend zur Anlage)", "Punkte"), it("Punkte addieren", "addierst"), it("meiste Punkte ➜ empfehlen + begründen", "meisten")], title="Bewertungstabelle")

thema("Rechtsformen")
T("""Thema drei: die *Rechtsformen*. Jetzt muss Lukas entscheiden, in welcher Form er sein Unternehmen führt.""")
D("""Die Rechtsform klingt trocken, beantwortet aber die wichtigste Frage überhaupt: Wenn es schiefgeht, *wer haftet*, und mit *welchem Geld*? Und *wie viel Geld* brauche ich zum Gründen?
Verglichen wird immer nach *drei Merkmalen*: *Mindestkapital*, *Haftung* und *Geschäftsführung*.""",
  "Rechtsform", "Regelt vor allem, wer haftet und wie viel Geld man zum Gründen braucht. Merkmale: Mindestkapital, Haftung, Geschäftsführung.")
P("""Bevor wir die Formen anschauen, ein Bild zur *Haftung*. Stell dir zwei Töpfe vor. Im einen liegt das *Geschäftsvermögen*: Werkzeug, Transporter, Firmenkonto. Im anderen dein *Privatvermögen*:
dein Auto, dein Erspartes. *Unbeschränkte Haftung* heißt: Wenn das Geschäft Schulden hat, dürfen die Gläubiger an *beide Töpfe*. *Beschränkte Haftung* heißt: nur an den Geschäftstopf,
dein *privates Geld ist geschützt*.""",
  "Das Bild mit den zwei Töpfen", [it("Topf 1: Geschäftsvermögen (Werkzeug, Transporter, Firmenkonto)", "Geschäftsvermögen"), it("Topf 2: Privatvermögen (Auto, Erspartes)", "Privatvermögen"),
                                   it("unbeschränkt ➜ Gläubiger an beide Töpfe", "Unbeschränkte"), it("beschränkt ➜ nur Geschäftstopf, privat geschützt", "Beschränkte")])
TB("""Jetzt die vier Rechtsformen. Das *Einzelunternehmen*: *eine Person*, *kein* Mindestkapital, man kann also sofort loslegen. Aber die Haftung ist *unbeschränkt*, also auch mit dem *Privatvermögen*.
Die Geschäftsführung macht der *Inhaber allein*. Die *GbR* entsteht, wenn sich *mindestens zwei* zusammentun. Auch *kein* Mindestkapital, und *alle* haften *unbeschränkt*, und zwar *jeder für alles*.
Macht dein Partner Schulden, kann der Gläubiger sich das Geld komplett von dir holen. Die Geschäftsführung machen *alle gemeinsam*.""",
   "Einzelunternehmen & GbR", ["", "Einzelunternehmen", "GbR"],
   [(["Personen", "1", "mind. 2"], "Einzelunternehmen"), (["Mindestkapital", "keins", "keins"], "Mindestkapital"),
    (["Haftung", "unbeschränkt, auch privat", "alle unbeschränkt, jeder für alles"], "unbeschränkt"), (["Geschäftsführung", "Inhaber allein", "alle gemeinsam"], "Inhaber")])
TB("""Die *GmbH*, die Gesellschaft mit beschränkter Haftung, der Name verrät es schon: ab *einer Person*, Mindestkapital *fünfundzwanzigtausend Euro*, die Haftung ist *beschränkt*,
das *Privatvermögen geschützt*, und es gibt einen *Geschäftsführer*. Und für alle, die keine fünfundzwanzigtausend Euro haben, gibt es die *UG haftungsbeschränkt*, die *Mini-GmbH*:
ab einer Person, Mindestkapital *ab einem Euro*, ebenfalls beschränkte Haftung und ein Geschäftsführer. Der Haken: Sie muss *fünfundzwanzig Prozent* ihres Gewinns zurücklegen,
bis die fünfundzwanzigtausend Euro zusammen sind. Dann kann sie zur richtigen GmbH werden.""",
   "GmbH & UG", ["", "GmbH", "UG (haftungsbeschränkt)"],
   [(["Personen", "ab 1", "ab 1"], "GmbH"), (["Mindestkapital", "25.000 €", "ab 1 €"], "fünfundzwanzigtausend"),
    (["Haftung", "beschränkt, privat geschützt", "beschränkt, privat geschützt"], "beschränkt"), (["Geschäftsführung", "Geschäftsführer", "Geschäftsführer"], "Geschäftsführer"),
    (["Besonderheit", "–", "25 % vom Gewinn zurücklegen bis 25.000 €"], "Prozent")])
X("""Und wie wählst du in der Prüfung die *passende* Rechtsform? Stell dir einfach drei Fragen. Erstens: *Wie viele* gründen, allein oder mehrere? Zweitens: *Wie viel Geld* ist da?
Wer keine fünfundzwanzigtausend Euro hat, kann keine GmbH gründen. Drittens: Soll das *Privatvermögen geschützt* sein? Dann GmbH oder UG.""",
  [it("Wie viele gründen?", "viele"), it("Wie viel Geld? Wenig ➜ keine GmbH", "Geld"), it("Privatvermögen schützen? ➜ GmbH / UG", "Privatvermögen")], title="So wählst du die Rechtsform")
Q("""Ein Fall: Lukas gründet *allein*, hat *zehntausend Euro* und will auf keinen Fall sein Privatvermögen riskieren. Welche Rechtsform? … *Allein*, also kein GbR. Zu wenig Geld für eine GmbH.
Aber er will sein Privatvermögen schützen. Also die *UG*.""",
  "Allein, 10.000 €, Privatvermögen schützen – welche Rechtsform?", "UG (haftungsbeschränkt) – allein, zu wenig für GmbH, Privatvermögen geschützt", "Allein")

thema("Kapitalbedarfsplan")
T("""Thema vier, das letzte: der *Kapitalbedarfsplan*. Jetzt geht es ums Geld: Wie viel braucht Lukas eigentlich?""")
D("""Viele Gründer denken nur an Werkzeug und Transporter und vergessen, dass in den ersten Monaten kaum Geld reinkommt, sie aber trotzdem Miete und Essen zahlen müssen. Davor schützt der
*Kapitalbedarfsplan*. Er zeigt, *wie viel Geld* man *insgesamt* für die Gründung braucht, und daraus ergibt sich, wie viel man *von der Bank* leihen muss.""",
  "Kapitalbedarfsplan", "Zeigt, wie viel Geld man insgesamt für die Gründung braucht und wie viel davon von der Bank geliehen werden muss.")
P("""Was gehört rein? Sechs Bausteine, a bis f. a: die *Investitionen*, also einmalige Anschaffungen wie Einrichtung, Maschinen, Werkzeug, Fahrzeug und Computer. b: die *ersten Waren*,
beim Fahrradladen zum Beispiel die ersten Fahrräder. c: die *Gründungskosten* wie Notar und Gewerbeanmeldung. d: die *laufenden Kosten* für die ersten Monate, also Miete, Löhne, Werbung.
e, und das vergessen viele: die *Lebenshaltungskosten* des Gründers. Lukas muss ja selbst auch von etwas leben. Und f: eine *Reserve* für Unvorhergesehenes, falls der Transporter kaputtgeht.""",
  "Die 6 Bausteine", [it("a) Investitionen (Einrichtung, Maschinen, Fahrzeug …)", "Investitionen"), it("b) erste Waren", "Waren"), it("c) Gründungskosten (Notar, Gewerbeanmeldung)", "Gründungskosten"),
                      it("d) laufende Kosten für die ersten Monate", "laufenden"), it("e) Lebenshaltungskosten des Gründers", "Lebenshaltungskosten"), it("f) Reserve", "Reserve")])
F("""Jetzt zwei Dinge, die du für die Rechnung brauchst. Erstens: Bei *monatlichen* Kosten rechnest du immer *mal die Monate*. Pacht zwölfhundert Euro im Monat, für zwölf Monate eingeplant,
sind vierzehntausendvierhundert Euro. Das ist der häufigste Fehler in der Prüfung. Und zweitens die Formel: *Kapitalbedarf minus Eigenkapital gleich Kredit*, also *Fremdkapital*.
Eigenkapital ist das, was du selbst mitbringst, Fremdkapital ist das, was du dir leihst.""",
  [["Kapitalbedarf", "#ea580c", "Kapitalbedarf"], ["− Eigenkapital", "#16a34a", "Eigenkapital"], ["= Kredit (Fremdkapital)", "#dc2626", "Kredit"]],
  note="monatliche Kosten × Monate (z. B. Pacht 1.200 € × 12 = 14.400 €)")
RAW("""Rechnen wir das Beispiel aus deinem Lernzettel zusammen durch. Stefan gründet einen *Fahrradladen* und hat fünfundzwanzigtausend Euro Eigenkapital. Die *Einrichtung* kostet fünfzehntausend,
das *Werkzeug* fünftausend, der *Lieferwagen* zwölftausend, die *ersten Fahrräder* zwanzigtausend, die *Gründungskosten* tausendfünfhundert. Die *Pacht*: zwölfhundert mal zwölf,
also vierzehntausendvierhundert. Seine *Lebenshaltung*: fünfzehnhundert mal zwölf, also achtzehntausend. Und eine *Reserve* von fünftausend. Zusammen ergibt das einen *Kapitalbedarf*
von neunzigtausendneunhundert Euro. Davon ziehen wir die fünfundzwanzigtausend Eigenkapital ab, und Stefan braucht *fünfundsechzigtausendneunhundert Euro Kredit*.""",
    {"type": "ledger", "title": "Kapitalbedarf Stefan (Fahrradladen)", "rows": [
        {"label": "Einrichtung", "amount": 15000, "cue": "Einrichtung"}, {"label": "Werkzeug", "amount": 5000, "cue": "Werkzeug"},
        {"label": "Lieferwagen", "amount": 12000, "cue": "Lieferwagen"}, {"label": "Erste Fahrräder", "amount": 20000, "cue": "ersten"},
        {"label": "Gründungskosten", "amount": 1500, "cue": "Gründungskosten"}, {"label": "Pacht 1.200 € × 12", "amount": 14400, "cue": "Pacht"},
        {"label": "Lebenshaltung 1.500 € × 12", "amount": 18000, "cue": "Lebenshaltung"}, {"label": "Reserve", "amount": 5000, "cue": "Reserve"},
        {"label": "= Kapitalbedarf", "amount": None, "cue": "Kapitalbedarf", "total": True}],
     "note": "90.900 € − 25.000 € Eigenkapital = 65.900 € Kredit", "cueNote": "fünfundsechzigtausendneunhundert"})
P("""Und zum Abschluss das *Merke alles* für Kompetenzbereich vier, also vier Entscheidungen in einem Satz pro Thema. Eins: Passt die Selbstständigkeit zu mir? Motive, Eigenschaften *mit Begründung*,
und Chancen und Risiken mit *Geld, Zeit, Verantwortung, Absicherung*. Zwei: Der *Geschäftsplan* ist das Konzept für die *Bank*, und den Standort wählst du per *Punktetabelle* mit Begründung.
Drei: *Einzelunternehmen* und GbR haften privat und brauchen kein Kapital, GmbH und UG schützen das Privatvermögen. Vier: *Kapitalbedarf* minus Eigenkapital gleich Kredit, und monatliche Kosten mal Monate.
Damit bist du für Kompetenzbereich vier bestens vorbereitet. Viel Erfolg in deiner Prüfung, du schaffst das!""",
  "Merke alles 🧠", [it("1: Motive, Eigenschaften + Begründung, Geld – Zeit – Verantwortung – Absicherung", "Motive"), it("2: Geschäftsplan = Konzept für die Bank · Standort per Punktetabelle", "Geschäftsplan"),
                    it("3: Einzel/GbR privat haften · GmbH (25.000 €) / UG (1 €) geschützt", "Einzelunternehmen"), it("4: Kapitalbedarf − Eigenkapital = Kredit · monatlich × Monate", "Kapitalbedarf")])

# ---------------------------------------------------------------------------------- Ausgabe
MAX_WORDS = {1: 800, 2: 800, 3: 800, 4: 800}  # gemini-3.8 schafft ~800 Wörter pro Anfrage
for n, d in KB.items():
    part, words = 0, 0
    for s in d["sentences"]:
        w = len(s["text"].split())
        if words and words + w > MAX_WORDS[n]:
            part, words = part + 1, 0
        s["part"] = part
        words += w
    p = ROOT / "src" / f"lern_kb{n}" / "script.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tl = ROOT / "src" / f"lern_kb{n}" / "timing.json"
    if not tl.exists():
        tl.write_text('{ "lines": [] }\n')
    total = sum(len(s["text"].split()) for s in d["sentences"])
    print(f"KB {n}: {len(d['sentences'])} Szenen, {total} Wörter (~{total / 165:.0f} min), {part + 1} Blöcke")
