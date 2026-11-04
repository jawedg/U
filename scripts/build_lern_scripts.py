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


# =====================================================================================
# KB I
# =====================================================================================
kb(1, "Die Rolle des Mitarbeiters in der Arbeitswelt",
   ["Duale Ausbildung", "Ausbildungsvertrag", "Schutzgesetze", "Arbeitsvertrag", "Kündigung und Kündigungsschutz", "Arbeitszeugnis",
    "Betriebsrat", "Tarifvertrag und Arbeitskampf", "Sozialversicherung", "Lohnabrechnung", "Steuererklärung"])
sc("""Willkommen zum Kompetenzbereich eins: Die Rolle des Mitarbeiters in der Arbeitswelt. Wir gehen *elf Themen* durch,
genau in der Reihenfolge deines Lernzettels. Bei jedem Thema erkläre ich dir zuerst, worum es geht, dann kommen Beispiele,
und am Ende gibt es immer ein *Merke*. Begleiten wird uns Lukas, er macht eine Ausbildung zum Elektroniker für Betriebstechnik.""",
   {"type": "kb"})

thema("Duale Ausbildung")
T("""Thema eins: die *duale Ausbildung*.""")
C("""Dual heißt einfach *zwei*. Du lernst an zwei *Lernorten*: im *Betrieb* die Praxis und in der *Berufsschule* die Theorie.
Und für beide gibt es einen eigenen Plan. Der Betrieb richtet sich nach der *Ausbildungsordnung*, die kommt vom *Bund*, und darin steckt der
*Ausbildungsrahmenplan*. Die Berufsschule richtet sich nach dem *Rahmenlehrplan*, und der kommt vom *Land*.""",
  "Betrieb", ["Praxis", "Ausbildungsordnung (Bund)", "darin: Ausbildungsrahmenplan"],
  "Berufsschule", ["Theorie", "Rahmenlehrplan (Land)"], "Berufsschule")
P("""Wer ist an deiner Ausbildung beteiligt? Es sind *sechs*. Erstens der *Auszubildende*, also du: Du lernst.
Zweitens der *Ausbildende*, das ist die *Firma*. Sie schließt den Vertrag mit dir und zahlt die Vergütung.
Drittens der *Ausbilder*, das ist eine *Person*, die dich wirklich ausbildet. Die muss *persönlich und fachlich geeignet* sein.
Viertens die *Berufsschule*. Fünftens die *Kammer*, also IHK oder Handwerkskammer: Sie überwacht, berät und nimmt die Prüfungen ab.
Und sechstens die *Eltern*: Die unterschreiben mit, wenn du noch unter achtzehn bist.""",
  "Die 6 Beteiligten", [it("Auszubildender – lernt", "Auszubildende"), it("Ausbildender = Firma – Vertrag, Vergütung", "Ausbildende"),
                         it("Ausbilder = Person – persönlich & fachlich geeignet", "Ausbilder"), it("Berufsschule – Theorie", "Viertens"),
                         it("Kammer (IHK/HWK) – überwacht, berät, prüft", "Kammer"), it("Eltern – unterschreiben unter 18", "Eltern")])
C("""Was bringt dir das duale System? Du lernst *Praxis und Theorie* zusammen, du verdienst schon *Geld*, und oft wirst du nach der Ausbildung *übernommen*.
Der Nachteil: Die *Qualität* hängt stark vom Betrieb ab. Ein guter Betrieb bringt dir viel bei, ein schlechter lässt dich nur Hilfsarbeiten machen.""",
  "Vorteile", ["Praxis + Theorie", "schon Geld verdienen", "Übernahmechance"], "Nachteil", ["Qualität hängt vom Betrieb ab"], "Nachteil")
M("""Und hier das Merke, da kommen viele durcheinander: Der *Ausbildende* ist die *Firma*, die den Vertrag macht und zahlt.
Der *Ausbilder* ist die *Person*, die dich ausbildet.""", "Ausbildender = Firma (Vertrag, Geld) · Ausbilder = Person (bildet aus)")

thema("Ausbildungsvertrag")
T("""Thema zwei: der *Ausbildungsvertrag*.""")
P("""Wie kommt er zustande? Der Vertrag wird *schriftlich* und *vor Beginn* der Ausbildung abgeschlossen, von beiden *unterschrieben*
und bei der *Kammer eingetragen*. Bist du unter achtzehn, müssen deine *Eltern* mitunterschreiben, und du brauchst eine *ärztliche Erstuntersuchung*.""",
  "Zustandekommen", [it("schriftlich", "schriftlich"), it("vor Beginn der Ausbildung", "Beginn"), it("unterschrieben", "unterschrieben"),
                     it("bei der Kammer eingetragen", "Kammer"), it("unter 18: Eltern + ärztliche Erstuntersuchung", "Eltern")])
P("""Was steht drin? Der *Beruf*, *Beginn und Dauer*, die tägliche *Ausbildungszeit*, die *Probezeit*, die ist *ein bis vier Monate* lang,
die *Vergütung*, die jedes Jahr steigt, der *Urlaub* und die Regeln zur *Kündigung*.""",
  "Inhalt", [it("Beruf", "Beruf"), it("Beginn und Dauer", "Dauer"), it("Ausbildungszeit", "Ausbildungszeit"), it("Probezeit 1–4 Monate", "Probezeit"),
             it("Vergütung (steigt jährlich)", "Vergütung"), it("Urlaub, Kündigung", "Urlaub")])
C("""Aus dem Vertrag folgen Pflichten. Du als *Azubi* musst *lernen*, die *Berufsschule* besuchen, dein *Berichtsheft* führen, *Weisungen* befolgen,
*sorgfältig* arbeiten und Betriebsgeheimnisse für dich behalten. Der *Betrieb* muss dich *ausbilden*, dir *Werkzeug kostenlos* stellen, dich für Schule
und Prüfung *freistellen*, dich *bezahlen* und dir am Ende ein *Zeugnis* geben. Und ganz wichtig: Er darf dir keine *ausbildungsfremden* Arbeiten geben.
Den Arbeitsplatz aufräumen gehört dazu. Aber jeden Tag nur Kaffee holen, das ist ausbildungsfremd.""",
  "Pflichten Azubi", ["lernen", "Berufsschule", "Berichtsheft", "Weisungen befolgen", "sorgfältig, schweigen"],
  "Pflichten Betrieb", ["ausbilden", "Werkzeug kostenlos", "freistellen", "zahlen, Zeugnis", "keine ausbildungsfremden Arbeiten"], "Betrieb",
  note="Arbeitsplatz aufräumen ✅ · ständig Kaffee holen ❌")
X("""Und wenn es Ärger gibt? Dann gehst du Schritt für Schritt vor: zuerst das *Gespräch* mit dem Ausbilder. Hilft das nicht, der *Betriebsrat* oder die
*JAV*, also die Jugend- und Auszubildendenvertretung. Dann die *Kammer*, und ganz am Ende das *Arbeitsgericht*. Und bevor ein Betrieb einem Azubi kündigt,
kommt meistens vorher eine *Abmahnung*.""",
  [it("Gespräch", "Gespräch"), it("Betriebsrat / JAV", "Betriebsrat"), it("Kammer", "Kammer"), it("Arbeitsgericht", "Arbeitsgericht")], title="Konflikte lösen")
TB("""Jetzt die *Kündigung*. Sie muss immer *schriftlich* sein. In der *Probezeit* dürfen *beide* jederzeit kündigen, ohne Grund und ohne Frist.
*Nach* der Probezeit darf der *Betrieb* nur noch *fristlos* kündigen, und zwar nur aus einem *wichtigen Grund*, zum Beispiel bei Diebstahl.
Der *Azubi* darf nach der Probezeit auch fristlos aus wichtigem Grund kündigen, oder mit *vier Wochen* Frist, wenn er den *Beruf wechselt*
oder die Ausbildung ganz aufgibt.""",
   "Kündigung (immer schriftlich)", ["Wann?", "Wer?", "Wie?"],
   [(["Probezeit", "beide", "jederzeit, ohne Grund"], "Probezeit"),
    (["danach", "Betrieb", "nur fristlos aus wichtigem Grund"], "Betrieb"),
    (["danach", "Azubi", "fristlos ODER 4 Wochen bei Berufswechsel"], "vier")])
P("""Wann *endet* die Ausbildung? Mit *Ablauf* der Ausbildungszeit oder schon mit der *bestandenen Prüfung*. Fällst du durch, kannst du
*verlängern*, bis zu *einem Jahr*. Und Achtung: Arbeitest du nach dem Ende einfach weiter, ohne dass etwas vereinbart wurde,
entsteht automatisch ein *unbefristetes* Arbeitsverhältnis.""",
  "Ende der Ausbildung", [it("Ablauf der Ausbildungszeit", "Ablauf"), it("oder bestandene Prüfung", "bestandenen"),
                          it("nicht bestanden ➜ Verlängerung bis 1 Jahr", "verlängern"), it("einfach weiterarbeiten ➜ unbefristet!", "unbefristetes")])
M("""Merke: In der *Probezeit* kann *jeder jederzeit* kündigen. Danach der *Betrieb* nur *fristlos*. Der *Azubi* zusätzlich mit *vier Wochen*,
wenn er den Beruf wechselt.""", "Probezeit: jeder jederzeit · danach Betrieb nur fristlos · Azubi auch 4 Wochen bei Berufswechsel")

thema("Schutzgesetze")
T("""Thema drei: die *Schutzgesetze*, auch *sozialer Arbeitsschutz* genannt.""")
BIG("""Für *Jugendliche* unter achtzehn gibt es das Jugendarbeitsschutzgesetz. Merk dir die Zahlenreihe *acht, vierzig, fünf, zwölf*:
höchstens *acht Stunden* am Tag, *vierzig Stunden* in der Woche, an *fünf Tagen*, und mindestens *zwölf Stunden* Freizeit zwischen zwei Arbeitstagen.
Außerdem: keine Arbeit zwischen *zwanzig und sechs Uhr*. Ein Berufsschultag mit *mehr als fünf* Stunden zählt als *voller Arbeitstag*.
Jugendliche bekommen *mehr Urlaub*, müssen vor Beginn zum *Arzt*, und *gefährliche Arbeiten* und *Akkordarbeit* sind verboten.""",
    "8 – 40 – 5 – 12", "Jugendarbeitsschutz (unter 18)",
    [it("8 Std./Tag · 40 Std./Woche · 5 Tage · 12 Std. Freizeit", "acht"), it("keine Arbeit 20–6 Uhr", "zwanzig"),
     it("Berufsschultag > 5 Std. = voller Arbeitstag", "Berufsschultag"), it("mehr Urlaub, Arzt vor Beginn", "Urlaub"),
     it("verboten: gefährliche Arbeit, Akkord", "gefährliche")])
TB("""Die *Ruhepausen* für Jugendliche: Wer mehr als *viereinhalb* Stunden arbeitet, bekommt *dreißig Minuten* Pause. Wer mehr als *sechs* Stunden arbeitet,
bekommt insgesamt *sechzig Minuten*. Und eine Pause zählt erst ab *fünfzehn Minuten*. Zwei Mal fünf Minuten Kaffee sind also keine Pause.
Für *Erwachsene* gilt: *acht* Stunden am Tag, kurzzeitig auch *zehn*, und *elf Stunden* Ruhe.""",
   "Pausen & Arbeitszeit", ["", "Jugendliche", "Erwachsene"],
   [(["Arbeitszeit", "8 Std.", "8 Std., kurz 10"], "Ruhepausen"),
    (["Pause", "> 4,5 Std. ➜ 30 Min. · > 6 Std. ➜ 60 Min.", "(30 / 45 Min.)"], "viereinhalb"),
    (["Pause zählt ab", "15 Minuten", "15 Minuten"], "fünfzehn"),
    (["Ruhe zwischen Arbeitstagen", "12 Std.", "11 Std."], "elf")])
F("""Der *Urlaub* für Erwachsene: mindestens *vierundzwanzig Werktage*. Werktage sind Montag bis Samstag, also sechs Tage pro Woche.
Du arbeitest aber nur fünf. Darum rechnest du: vierundzwanzig *geteilt durch sechs* mal *fünf*, das sind *zwanzig Arbeitstage*.
Mehr Urlaub ist erlaubt, weniger nicht.""",
  [["24 Werktage", "#2563eb", "vierundzwanzig"], ["÷ 6 × 5", "#1f2937", "geteilt"], ["=", "#1f2937", "zwanzig"], ["20 Arbeitstage", "#16a34a", "zwanzig"]],
  note="Mehr Urlaub erlaubt, weniger nicht")
P("""Beim *Mutterschutz* darf eine Frau *sechs Wochen vor* und *acht Wochen nach* der Geburt nicht arbeiten. Kündigungsschutz gilt *ab der Schwangerschaft*
bis *vier Monate* nach der Geburt. *Elternzeit* können *beide Eltern* nehmen, bis zum *dritten Geburtstag* des Kindes. Währenddessen gibt es Kündigungsschutz,
und *Elterngeld* zahlt der *Staat*. *Überwacht* wird das alles vom *Gewerbeaufsichtsamt*, der *Berufsgenossenschaft* und dem *Betriebsrat*.""",
  "Mutterschutz & Elternzeit", [it("Mutterschutz: 6 Wochen vor, 8 nach der Geburt", "Mutterschutz"), it("Kündigungsschutz ab Schwangerschaft bis 4 Monate danach", "Kündigungsschutz"),
                                it("Elternzeit: beide Eltern, bis zum 3. Geburtstag", "Elternzeit"), it("Elterngeld vom Staat", "Elterngeld"),
                                it("Überwachung: Gewerbeaufsichtsamt, Berufsgenossenschaft, Betriebsrat", "Überwacht")])
M("""Merke dir drei Begriffe, die oft verwechselt werden: Die *Ruhepause* ist *in* der Arbeit, also dreißig oder sechzig Minuten.
Die *Freizeit* ist *zwischen* zwei Arbeitstagen, zwölf Stunden. Und die *Nachtruhe* ist eine *Uhrzeit*: zwanzig bis sechs Uhr.""",
  "Ruhepause = IN der Arbeit · Freizeit = ZWISCHEN zwei Tagen (12 Std.) · Nachtruhe = UHRZEIT (20–6 Uhr)")

thema("Arbeitsvertrag")
T("""Thema vier: der *Arbeitsvertrag*. Ganz einfach gesagt: Der Arbeitnehmer *arbeitet*, der Arbeitgeber *zahlt*.""")
C("""Schon beim *Vorstellungsgespräch* gibt es Regeln. *Zulässig* sind Fragen, die mit der Arbeit zu tun haben: deine *Ausbildung*, deine *Erfahrung*,
deine *Kenntnisse*. *Unzulässig* sind Fragen nach *Schwangerschaft*, *Religion*, *Partei* oder deinen *Finanzen*. Auf eine unzulässige Frage darfst du
sogar *lügen*, das nennt man das *Recht zur Lüge*. Fragt der Chef eine Bewerberin, ob sie schwanger ist, darf sie Nein sagen, ohne Folgen.""",
  "Zulässig ✅", ["Ausbildung", "Erfahrung", "Kenntnisse"], "Unzulässig ❌", ["Schwangerschaft", "Religion, Partei", "Finanzen", "➜ Recht zur Lüge"], "Unzulässig")
P("""Muss der Vertrag schriftlich sein? Nein, er ist *formfrei*. Sogar ein *Handschlag* ist gültig. Aber der Arbeitgeber muss dir die wichtigsten
*Bedingungen schriftlich* aushändigen, so steht es im *Nachweisgesetz*. Eine Ausnahme ist die *Befristung*: Wird sie *nicht schriftlich* vereinbart,
dann gilt der Vertrag als *unbefristet*.""",
  "Form", [it("formfrei – Handschlag gültig", "formfrei"), it("Bedingungen schriftlich aushändigen (Nachweisgesetz)", "Bedingungen"),
           it("Befristung ohne Schriftform ➜ unbefristet!", "Befristung")])
C("""Die Pflichten: Der *Arbeitnehmer* muss *arbeiten*, *Weisungen* befolgen, Betriebsgeheimnisse für sich behalten und sich *krank melden*.
Der *Arbeitgeber* muss *zahlen*, auch bei Krankheit, und zwar bis zu *sechs Wochen*. Er hat eine *Fürsorgepflicht*, muss also für Sicherheit sorgen,
und er muss *Urlaub* gewähren und ein *Zeugnis* ausstellen.""",
  "Arbeitnehmer", ["arbeiten", "Weisungen befolgen", "schweigen", "krank melden"], "Arbeitgeber", ["zahlen (krank bis 6 Wochen)", "Fürsorge", "Urlaub", "Zeugnis"], "Arbeitgeber")
M("""Merke: Arbeitnehmer arbeitet, Arbeitgeber zahlt. Unzulässige Fragen darf man falsch beantworten. Und eine Befristung ohne Schriftform macht den Vertrag unbefristet.""",
  "AN arbeitet, AG zahlt · unzulässige Frage ➜ Recht zur Lüge · Befristung ohne Schriftform ➜ unbefristet")

thema("Kündigung und Kündigungsschutz")
T("""Thema fünf: *Kündigung und Kündigungsschutz*.""")
P("""Wie kann ein Arbeitsverhältnis *enden*? Durch *Kündigung*, durch einen *Aufhebungsvertrag*, wenn eine *Befristung* abläuft, oder mit der *Rente*.
Ein *befristeter* Vertrag hat ein Enddatum und muss *schriftlich* sein. *Ohne Grund* darf man höchstens *zwei Jahre* befristen, *mit Grund*, zum Beispiel
als Vertretung, auch länger.""",
  "Ende & Befristung", [it("Kündigung", "Kündigung"), it("Aufhebungsvertrag", "Aufhebungsvertrag"), it("Befristung läuft ab", "Befristung"), it("Rente", "Rente"),
                        it("befristet: Enddatum, schriftlich, ohne Grund max. 2 Jahre", "zwei")])
D("""Die Kündigung ist eine *empfangsbedürftige einseitige Willenserklärung*. Einseitig heißt: Der andere muss nicht zustimmen.
Empfangsbedürftig heißt: Sie wird erst wirksam, wenn sie beim anderen *ankommt*. Und sie muss immer *schriftlich* sein, eine WhatsApp reicht nicht.""",
  "Kündigung", "empfangsbedürftige, einseitige Willenserklärung – immer schriftlich", "empfangsbedürftige")
C("""Es gibt zwei Arten. Die *ordentliche* Kündigung hält eine Frist ein: *vier Wochen*, also *achtundzwanzig Tage*, zum *Fünfzehnten* oder zum *Monatsende*.
In der Probezeit sind es *zwei Wochen*. Kündigt der *Chef*, wird die Frist *länger*, je länger du im Betrieb bist, das steht dann in der Anlage.
Die *außerordentliche* Kündigung ist *fristlos* und nur mit einem *wichtigen Grund* möglich, zum Beispiel Diebstahl.""",
  "ordentlich 🚶", ["4 Wochen (28 Tage) zum 15. / Monatsende", "Probezeit: 2 Wochen", "Chef kündigt ➜ länger (Anlage)"],
  "außerordentlich 🚨", ["fristlos", "nur mit wichtigem Grund", "z. B. Diebstahl"], "außerordentliche")
X("""Ein Rechenbeispiel. Lukas' Kündigung kommt am *zehnten März* an. Plus *achtundzwanzig Tage*, das ist der *siebte April*.
Jetzt nimmst du den *nächsten* möglichen Termin, also den Fünfzehnten oder das Monatsende. Der nächste ist der *fünfzehnte April*. An dem Tag endet das Arbeitsverhältnis.""",
  [it("Kündigung kommt an: 10. März", "zehnten"), it("+ 28 Tage = 7. April", "achtundzwanzig"), it("nächster Termin (15. / Monatsende)", "nächsten"), it("Ende: 15. April", "fünfzehnte")],
  title="Rechenbeispiel ordentliche Kündigung")
P("""Dann der *allgemeine Kündigungsschutz*. Er gilt, wenn du *mehr als sechs Monate* im Betrieb bist *und* der Betrieb *mehr als zehn* Mitarbeiter hat.
Dann braucht der Chef einen *Grund*, und es gibt nur drei: Er liegt in der *Person*, du *kannst* nicht, zum Beispiel wegen langer Krankheit.
Im *Verhalten*, du *willst* nicht, zum Beispiel ständiges Zuspätkommen. Oder im *Betrieb*, zum Beispiel weil Aufträge wegfallen. Dann gibt es eine *Sozialauswahl*:
Wer am wenigsten schutzbedürftig ist, geht zuerst. Wichtig: Der *Betriebsrat* muss vorher *angehört* werden, sonst ist die Kündigung *unwirksam*.
Und wehren kannst du dich mit einer *Klage* innerhalb von *drei Wochen*.""",
  "Allgemeiner Kündigungsschutz", [it("> 6 Monate UND > 10 Mitarbeiter", "sechs"), it("Person – kann nicht (Krankheit)", "Person"),
                                    it("Verhalten – will nicht (Zuspätkommen)", "Verhalten"), it("Betrieb – Aufträge fehlen ➜ Sozialauswahl", "Betrieb"),
                                    it("Betriebsrat anhören, sonst unwirksam", "angehört"), it("Klage innerhalb 3 Wochen", "Klage")])
BIG("""Und der *besondere Kündigungsschutz* gilt *immer*, egal wie groß der Betrieb ist. Merk dir das Wort *S E S B A*:
*Schwangere*, Menschen in *Elternzeit*, *Schwerbehinderte*, Mitglieder des *Betriebsrats* und *Azubis* nach der Probezeit.""",
    "S – E – S – B – A", "Besonderer Kündigungsschutz (gilt immer)",
    [it("Schwangere", "Schwangere"), it("Elternzeit", "Elternzeit"), it("Schwerbehinderte", "Schwerbehinderte"), it("Betriebsrat", "Betriebsrats"), it("Azubis nach Probezeit", "Azubis")])
M("""Merke: Ordentlich vier Wochen zum Fünfzehnten oder Monatsende, außerordentlich fristlos mit wichtigem Grund. Allgemeiner Schutz ab sechs Monaten und mehr als zehn Mitarbeitern.
Besonderer Schutz: SESBA.""", "ordentlich 4 Wochen zum 15./Monatsende · außerordentlich fristlos · allg. Schutz: > 6 Monate + > 10 MA · SESBA")

thema("Arbeitszeugnis")
T("""Thema sechs: das *Arbeitszeugnis*.""")
C("""Es gibt zwei Arten. Das *einfache* Zeugnis enthält nur deinen *Namen*, deine *Tätigkeit* und die *Dauer*. Das *qualifizierte* Zeugnis bewertet zusätzlich
deine *Leistung* und deine *Führung*, also dein Verhalten. Das qualifizierte bekommst du aber nur auf *Verlangen*, du musst also danach fragen.""",
  "einfach", ["Name", "Tätigkeit", "Dauer"], "qualifiziert", ["+ Leistung", "+ Führung (Verhalten)", "nur auf Verlangen"], "qualifizierte")
TB("""Ein Zeugnis muss *wahr* und *wohlwollend* sein. Der Chef darf also nichts Schlechtes direkt reinschreiben. Darum gibt es die *Zeugnissprache*.
Für die *Leistung*: „*stets* zu unserer *vollsten* Zufriedenheit“ ist eine *Eins*. „Stets zur *vollen*“ eine *Zwei*. „Zur vollen“ eine *Drei*.
„Zu unserer *Zufriedenheit*“ eine *Vier*. „*Im Großen und Ganzen*“ eine *Fünf*. Und „er war *bemüht*“ ist eine *Sechs*.""",
   "Zeugnissprache – Leistung", ["Formulierung", "Note"],
   [(["stets zu unserer vollsten Zufriedenheit", "1"], "Eins"), (["stets zur vollen Zufriedenheit", "2"], "Zwei"), (["zur vollen Zufriedenheit", "3"], "Drei"),
    (["zu unserer Zufriedenheit", "4"], "Vier"), (["im Großen und Ganzen", "5"], "Fünf"), (["bemüht", "6"], "Sechs")])
TB("""Für die *Führung*: „*stets vorbildlich*“ ist eine Eins, „*vorbildlich*“ eine Zwei, „*stets einwandfrei*“ eine Drei und „*einwandfrei*“ eine Vier.
Achte auch auf das, was *fehlt*: Werden die *Vorgesetzten nicht erwähnt*, gab es Ärger mit dem Chef. Und „*erfrischende Offenheit*“ heißt: Er war *vorlaut*.
Eine gute *Schlussformel* enthält *Bedauern*, *Dank* und gute *Wünsche*. Und „*auf eigenen Wunsch*“ heißt, du hast selbst gekündigt, das ist positiv.""",
   "Zeugnissprache – Führung", ["Formulierung", "Bedeutung"],
   [(["stets vorbildlich", "1"], "Führung"), (["vorbildlich", "2"], "Zwei"), (["stets einwandfrei", "3"], "Drei"), (["einwandfrei", "4"], "Vier"),
    (["Vorgesetzte fehlen", "Ärger mit dem Chef"], "fehlt"), (["„erfrischende Offenheit“", "vorlaut"], "erfrischende"),
    (["Schlussformel: Bedauern, Dank, Wünsche", "gut"], "Schlussformel")])
M("""Merke: Einfach gleich Name, Tätigkeit, Dauer. Qualifiziert plus Leistung und Führung, nur auf Verlangen. Wahr und wohlwollend, darum Zeugnissprache.""",
  "einfach: Name, Tätigkeit, Dauer · qualifiziert: + Leistung & Führung (auf Verlangen) · wahr + wohlwollend")

thema("Betriebsrat")
T("""Thema sieben: der *Betriebsrat*.""")
P("""Der Betriebsrat ist die *gewählte Vertretung* der Mitarbeiter, geregelt im *Betriebsverfassungsgesetz*. Gewählt werden kann er ab *fünf* Arbeitnehmern,
und zwar alle *vier Jahre*. *Wählen* darfst du ab *sechzehn*, *gewählt werden* ab *achtzehn* und nach *sechs Monaten* im Betrieb.
Seine *Aufgaben*: Er *überwacht*, ob Gesetze eingehalten werden, *vertritt* die Interessen der Mitarbeiter, nimmt *Beschwerden* an, setzt sich für *Schwächere* ein
und schließt *Betriebsvereinbarungen* mit dem Chef. Seine Bedeutung: *Allein* ist ein Mitarbeiter *schwach*, *zusammen* sind alle *stark*.""",
  "Betriebsrat (BetrVG)", [it("ab 5 Arbeitnehmern · Wahl alle 4 Jahre", "fünf"), it("wählen ab 16 · gewählt werden ab 18 + 6 Monate", "Wählen"),
                           it("überwacht, vertritt Interessen, Beschwerden", "überwacht"), it("setzt sich für Schwächere ein, Betriebsvereinbarungen", "Schwächere"),
                           it("allein schwach, zusammen stark", "Allein")])
RAW("""Ganz wichtig für die Prüfung sind die *drei Stufen*. Stufe eins: *Information*. Der Chef muss *Bescheid sagen*, zum Beispiel bei *neuer Technik*
oder *Automatisierung*. Stufe zwei: *Mitwirkung*. Der Betriebsrat wird *angehört*, aber der *Chef entscheidet*, zum Beispiel bei einer *Kündigung*,
einer *Einstellung* oder einer *Versetzung*. Stufe drei: *Mitbestimmung*. Hier braucht der Chef die *Zustimmung*, zum Beispiel bei der *Arbeitszeit*,
den *Pausen*, bei *Überstunden* und beim *Urlaubsplan*.""",
    {"type": "stairs", "title": "Die 3 Stufen", "items": [
        it("Information = Bescheid sagen", "Information", sub="neue Technik, Automatisierung"),
        it("Mitwirkung = anhören, Chef entscheidet", "Mitwirkung", sub="Kündigung, Einstellung, Versetzung"),
        it("Mitbestimmung = Chef braucht Zustimmung", "Mitbestimmung", sub="Arbeitszeit, Pausen, Überstunden, Urlaubsplan")]})
M("""Merke die drei Stufen: Information heißt Bescheid sagen. Mitwirkung heißt anhören. Mitbestimmung heißt zustimmen.""",
  "Information = Bescheid sagen · Mitwirkung = anhören · Mitbestimmung = zustimmen")

thema("Tarifvertrag und Arbeitskampf")
T("""Thema acht: *Tarifvertrag und Arbeitskampf*.""")
P("""Ein Tarifvertrag ist ein Vertrag zwischen der *Gewerkschaft* und dem *Arbeitgeberverband*. Die beiden nennt man *Sozialpartner*.
Sie verhandeln *ohne den Staat*, das heißt *Tarifautonomie*.""",
  "Tarifvertrag", [it("Gewerkschaft + Arbeitgeberverband = Sozialpartner", "Gewerkschaft"), it("Tarifautonomie = ohne Staat", "Tarifautonomie")])
TB("""Es gibt drei Arten. Der *Entgelttarifvertrag* regelt die *Lohnhöhe* und läuft etwa *ein Jahr*. Der *Rahmenentgelttarifvertrag* regelt die *Lohngruppen*
und läuft *mehrere Jahre*. Und der *Manteltarifvertrag* regelt *Arbeitszeit* und *Urlaub* und läuft *drei bis fünf Jahre*.""",
   "Tarifvertragsarten", ["Art", "regelt", "Laufzeit"],
   [(["Entgelt", "Lohnhöhe", "ca. 1 Jahr"], "Entgelttarifvertrag"), (["Rahmenentgelt", "Lohngruppen", "mehrere Jahre"], "Rahmenentgelttarifvertrag"),
    (["Mantel", "Arbeitszeit, Urlaub", "3–5 Jahre"], "Manteltarifvertrag")])
P("""Für wen gilt der Tarifvertrag? Rechtlich nur für *Gewerkschaftsmitglieder*. Sonst gilt er, wenn du *beitrittst*, wenn dein *Arbeitsvertrag* darauf verweist,
oder wenn er für *allgemeinverbindlich* erklärt wurde. Das *Günstigkeitsprinzip* heißt: Es gilt immer das *Günstigere* für den Arbeitnehmer.
Und die *Friedenspflicht*: Während der *Laufzeit* darf *nicht gestreikt* werden.""",
  "Regeln", [it("Tarifbindung: Gewerkschaftsmitglieder", "Gewerkschaftsmitglieder"), it("sonst: beitreten, Arbeitsvertrag, allgemeinverbindlich", "beitrittst"),
             it("Günstigkeitsprinzip: das Günstigere gilt", "Günstigkeitsprinzip"), it("Friedenspflicht: kein Streik während der Laufzeit", "Friedenspflicht")])
X("""Wie läuft eine *Tarifrunde* ab? Erst stellt die Gewerkschaft eine *Forderung*. Dann wird *verhandelt*, oft mit *Warnstreiks*. Klappt das nicht, kommt die
*Schlichtung* mit einem neutralen Schlichter. Scheitert auch die, gibt es eine *Urabstimmung*: *fünfundsiebzig Prozent* der Mitglieder müssen für den
*Streik* stimmen. Streikende bekommen *Streikgeld* von der Gewerkschaft. Der Arbeitgeber kann mit *Aussperrung* antworten, dann gibt es keinen Lohn.
Kommt es zur *Einigung*, stimmen die Mitglieder noch einmal ab, dann reichen *fünfundzwanzig Prozent*, und es gibt einen *neuen Tarifvertrag*.""",
  [it("Forderung", "Forderung"), it("Verhandlung (Warnstreik)", "verhandelt"), it("Schlichtung", "Schlichtung"), it("Urabstimmung 75 %", "Urabstimmung"),
   it("Streik ↔ Aussperrung", "Streik"), it("Einigung", "Einigung"), it("Urabstimmung 25 % ➜ neuer TV", "fünfundzwanzig")], title="Ablauf einer Tarifrunde")
M("""Merke: Tarifautonomie heißt ohne Staat. Für den Streik braucht man fünfundsiebzig Prozent, für das Ende des Streiks nur fünfundzwanzig.""",
  "Tarifautonomie = ohne Staat · Streik: 75 % dafür · Ende: 25 % reichen")

thema("Sozialversicherung")
T("""Thema neun: die *Sozialversicherung*.""")
P("""Die Sozialversicherung schützt vor den großen Risiken im Leben: *Krankheit*, *Pflege*, *Alter*, *Arbeitslosigkeit* und *Unfall*.
Sie funktioniert nach dem *Solidaritätsprinzip*: Jeder zahlt nach seinem Einkommen, und jeder bekommt Hilfe nach seinem Bedarf. Die Starken tragen die Schwachen.
Alle *Arbeitnehmer und Azubis* sind *pflichtversichert*. Die Beiträge werden vom *Brutto* berechnet und *fünfzig zu fünfzig* geteilt. Nur die *Unfallversicherung*
zahlt der *Arbeitgeber allein*.""",
  "Sozialversicherung", [it("schützt vor Krankheit, Pflege, Alter, Arbeitslosigkeit, Unfall", "Krankheit"), it("Solidaritätsprinzip", "Solidaritätsprinzip"),
                         it("Arbeitnehmer & Azubis pflichtversichert", "pflichtversichert"), it("vom Brutto, 50 / 50", "fünfzig"),
                         it("Unfall: Arbeitgeber allein", "Arbeitgeber")])
TB("""Die fünf Zweige. *Kranken*, Träger ist die Krankenkasse: Arzt, Medikamente und ab der siebten Woche *Krankengeld*. *Pflege*, Träger ist die Pflegekasse:
Pflegegeld. *Kinderlose* ab dreiundzwanzig zahlen hier mehr. *Rente*, Träger ist die Deutsche Rentenversicherung: Altersrente, Erwerbsminderungsrente,
Hinterbliebenenrente und Reha. Sie funktioniert als *Generationenvertrag*: Die Jungen zahlen heute die Rente der Alten.
*Arbeitslosen*, Träger ist die Bundesagentur für Arbeit: *Arbeitslosengeld eins*, sechzig oder mit Kind siebenundsechzig Prozent, Vermittlung und Weiterbildung.
Und *Unfall*, Träger ist die Berufsgenossenschaft: *Arbeitsunfall*, der *direkte Wegeunfall*, auch zur Berufsschule, und *Berufskrankheit*. Aber *nicht* in der Freizeit.""",
   "Die 5 Zweige", ["Zweig", "Träger", "Leistungen"],
   [(["Kranken", "Krankenkasse", "Arzt, Medikamente, Krankengeld ab 7. Woche"], "Kranken"),
    (["Pflege", "Pflegekasse", "Pflegegeld · Kinderlose ab 23 zahlen mehr"], "Pflege"),
    (["Rente", "Dt. Rentenversicherung", "Alters-, Erwerbsminderungs-, Hinterbliebenenrente, Reha"], "Rente"),
    (["Arbeitslosen", "Bundesagentur für Arbeit", "ALG I 60 / 67 %, Vermittlung, Weiterbildung"], "Arbeitslosen"),
    (["Unfall", "Berufsgenossenschaft", "Arbeitsunfall, direkter Wegeunfall, Berufskrankheit"], "Unfall")])
C("""Die gesetzliche Versicherung hat *Grenzen*: Es gibt eine *Rentenlücke*, keine *Berufsunfähigkeitsrente*, keinen Schutz bei *Schäden an anderen*
und keinen Schutz bei *Freizeitunfällen*. Darum gibt es *Zusatzversicherungen*: die *Berufsunfähigkeitsversicherung*, die zahlt eine Rente, wenn du deinen Beruf
nicht mehr ausüben kannst, egal ob wegen Krankheit oder Unfall. Die *private Altersvorsorge* gegen die Rentenlücke. Und die *Haftpflicht* für Schäden an anderen,
die ist die *wichtigste* von allen.""",
  "Grenzen", ["Rentenlücke", "keine BU-Rente", "Schäden an anderen", "Freizeitunfälle"],
  "Zusatzversicherungen", ["Berufsunfähigkeit (BU)", "private Altersvorsorge", "Haftpflicht – die wichtigste!"], "Zusatzversicherungen")
M("""Merke: Fünf Zweige, fünfzig zu fünfzig, nur die Unfallversicherung zahlt der Arbeitgeber allein. Und die wichtigste private Versicherung ist die Haftpflicht.""",
  "5 Zweige · 50/50 vom Brutto · Unfall: AG allein · wichtigste Zusatzversicherung: Haftpflicht")

thema("Lohnabrechnung")
T("""Thema zehn: die *Lohnabrechnung*.""")
F("""Das Grundschema musst du auswendig können: *Brutto* minus *Steuern* minus *Sozialversicherung* gleich *Netto*.
Und Netto minus *Sparrate* oder *Vorschuss* gleich *Auszahlung*.""",
  [["Brutto", "#2563eb", "Brutto"], ["− Steuern", "#dc2626", "Steuern"], ["− SV", "#dc2626", "Sozialversicherung"], ["= Netto", "#16a34a", "Netto"]],
  note="Netto − Sparrate / Vorschuss = Auszahlung")
P("""Wie rechnet man das *Brutto*? Stundenlohn *mal Stunden*, plus *Überstundenzuschlag*. Oder bei einer Lohnerhöhung: alter Lohn mal eins Komma null x,
also bei drei Prozent mal eins Komma null drei. Die *Kirchensteuer* sind *acht Prozent der Lohnsteuer*, nicht vom Brutto!
Die *Sozialversicherung* wird vom Brutto berechnet, und zwar mit dem *halben Satz*, weil der Arbeitgeber die andere Hälfte zahlt. Achtung beim
*Kinderlosenzuschlag*: Den halbierst du *nicht*. Also erst den Pflegesatz halbieren, *dann* null Komma sechs Prozent dazu. Und ein *Vorschuss* wird am Ende *abgezogen*.""",
  "So rechnest du", [it("Brutto = Stundenlohn × Stunden (+ Überstundenzuschlag)", "Brutto"), it("Lohnerhöhung: alter Lohn × 1,0x", "Lohnerhöhung"),
                     it("Kirchensteuer = 8 % der LOHNSTEUER", "Kirchensteuer"), it("SV vom Brutto, halber Satz", "halben"),
                     it("Kinderlosenzuschlag NICHT halbieren: erst halbieren, dann + 0,6 %", "Kinderlosenzuschlag"), it("Vorschuss wird abgezogen", "Vorschuss")])
RAW("""Rechnen wir ein Beispiel mit Lukas. Er ist dreiundzwanzig und hat keine Kinder. Er arbeitet hundertsechzig Stunden für fünfzehn Euro, dazu zehn *Überstunden*
mit fünfundzwanzig Prozent Zuschlag. Das ergibt ein *Brutto* von zweitausendfünfhundertsiebenundachtzig Euro fünfzig. Die *Lohnsteuer* laut Tabelle: zweihundertfünfzig Euro.
Die *Kirchensteuer*: acht Prozent davon, also zwanzig Euro. Die *Sozialversicherung*, mit Beispielsätzen und Kinderlosenzuschlag: fünfhundertzweiundsechzig Euro achtundsiebzig.
Bleibt ein *Netto* von tausendsiebenhundertvierundfünfzig Euro zweiundsiebzig. Er hatte hundert Euro *Vorschuss*, also werden ihm *tausendsechshundertvierundfünfzig Euro zweiundsiebzig* ausgezahlt.""",
    {"type": "ledger", "title": "Lohnabrechnung Lukas (Beispielwerte)", "rows": [
        {"label": "160 Std. × 15 € + 10 Überstunden × 15 € × 1,25", "amount": 2587.5, "cue": "Überstunden"},
        {"label": "− Lohnsteuer (laut Tabelle)", "amount": -250, "cue": "Lohnsteuer"},
        {"label": "− Kirchensteuer (8 % von 250 €)", "amount": -20, "cue": "Kirchensteuer"},
        {"label": "− Sozialversicherung (AN-Anteil inkl. Kinderlosenzuschlag)", "amount": -562.78, "cue": "Sozialversicherung"},
        {"label": "= Netto", "amount": None, "cue": "Netto", "total": True},
        {"label": "− Vorschuss", "amount": -100, "cue": "Vorschuss"},
        {"label": "= Auszahlung", "amount": None, "cue": "ausgezahlt", "total": True}],
     "note": "Steuer- und SV-Sätze stehen in der Prüfung in der Anlage", "cueNote": "Netto"})
M("""Merke: Brutto minus Steuern minus Sozialversicherung gleich Netto. Kirchensteuer acht Prozent der Lohnsteuer. Kinderlosenzuschlag nicht halbieren.""",
  "Brutto − Steuern − SV = Netto · KiSt = 8 % der LSt · Kinderlosenzuschlag nicht halbieren")

thema("Steuererklärung")
T("""Thema elf, das letzte in diesem Bereich: die *Steuererklärung*.""")
P("""Bei der Steuererklärung *rechnet* das Finanzamt *nach*, ob du übers Jahr zu viel Lohnsteuer gezahlt hast. Oft gibt es *Geld zurück*.
Abziehen kannst du *Werbungskosten*, das sind Kosten für den *Beruf*: Fahrt zur Arbeit, *Fachbuch*, *Arbeitskleidung* und der *Gewerkschaftsbeitrag*.
Wer weniger hat, bekommt automatisch den *Pauschbetrag* von *zwölfhundertdreißig Euro*. Dann die *Sonderausgaben*: *Kirchensteuer*, *Spenden* und *Vorsorge*,
also Beiträge für Rente, Kranken, Berufsunfähigkeit und Haftpflicht. *Nicht abzugsfähig* ist alles für die *Freizeit*: Hobby oder *Sportverein*.""",
  "Was kann ich abziehen?", [it("Werbungskosten = für den Beruf: Fahrt, Fachbuch, Arbeitskleidung, Gewerkschaft", "Werbungskosten"),
                             it("Pauschbetrag 1.230 €", "Pauschbetrag"), it("Sonderausgaben = Kirche, Spenden, Vorsorge (Rente, Kranken, BU, Haftpflicht)", "Sonderausgaben"),
                             it("NICHT: Freizeit, Hobby, Sportverein", "Freizeit")])
F("""Die *Fahrtkosten* rechnest du so: *einfache Strecke* mal *Kilometerpauschale* laut Anlage mal *Arbeitstage*. Beispiel: Lukas fährt zwanzig Kilometer,
die Pauschale ist zum Beispiel achtunddreißig Cent, und er arbeitet zweihundertzwanzig Tage. Das sind *tausendsechshundertzweiundsiebzig Euro*.
Das ist mehr als der Pauschbetrag, also lohnt sich die Steuererklärung.""",
  [["20 km", "#2563eb", "einfache"], ["× 0,38 €", "#1f2937", "Kilometerpauschale"], ["× 220 Tage", "#1f2937", "Arbeitstage"], ["= 1.672 €", "#16a34a", "tausendsechshundertzweiundsiebzig"]],
  note="einfache Strecke × Pauschale (laut Anlage) × Arbeitstage")
P("""Und noch ein Denkfehler, den viele machen: Werbungskosten senken das *zu versteuernde Einkommen*, *nicht eins zu eins* die Steuer.
Hast du tausend Euro Werbungskosten und zahlst zwanzig Prozent Steuer, sparst du ungefähr *zweihundert Euro*, nicht tausend.""",
  "Achtung Denkfehler", [it("Werbungskosten senken das zu versteuernde Einkommen", "versteuernde"), it("nicht 1 : 1 die Steuer", "eins"),
                         it("1.000 € Werbungskosten × 20 % ≈ 200 € gespart", "zweihundert")])
M("""Merke: Werbungskosten sind für den Beruf, Sonderausgaben sind Kirche, Spenden und Vorsorge. Freizeit zählt nicht.""",
  "Werbungskosten = Beruf (mind. 1.230 €) · Sonderausgaben = Kirche, Spenden, Vorsorge · Freizeit zählt nicht")
sc("""Geschafft, das war Kompetenzbereich eins! Hier noch einmal alle *elf Themen* auf einen Blick. Wenn du bei einem Thema unsicher bist,
spring einfach zurück, oben siehst du immer, bei welchem Thema du gerade bist. Weiter geht's mit Kompetenzbereich zwei.""",
   {"type": "kb", "outro": True})

# =====================================================================================
# KB II
# =====================================================================================
kb(2, "Als Verbraucher Rechte anwenden",
   ["Rechtsfähigkeit", "Geschäftsfähigkeit", "Willenserklärung und Rechtsgeschäfte", "Formvorschriften", "Nichtig und anfechtbar", "Kaufvertrag",
    "Besitz und Eigentum", "Mangelhafte Lieferung", "Zahlungsverzug", "Regelmäßige Verjährung", "Verbraucherberatung", "Fernabsatz", "AGB",
    "Girokonto und Zahlungsverkehr", "Geldanlage", "Verbraucherdarlehen", "Überschuldung"])
sc("""Willkommen zum Kompetenzbereich zwei: Als *Verbraucher* Rechte anwenden. Hier geht es um dich als Kunde: Verträge, Rechte beim Einkaufen,
Geld und Schulden. Es sind *siebzehn Themen*, wieder genau wie auf deinem Lernzettel.""", {"type": "kb"})

thema("Rechtsfähigkeit")
T("""Thema eins: die *Rechtsfähigkeit*.""")
D("""Rechtsfähig heißt: Man kann *Rechte und Pflichten haben*. Zum Beispiel das Recht, etwas zu besitzen, oder die Pflicht, Steuern zu zahlen.""",
  "Rechtsfähigkeit", "Man kann Rechte und Pflichten haben.")
C("""Wer ist rechtsfähig? *Menschen* sind es von der *Geburt* bis zum *Tod*. Sogar ein Baby kann schon etwas erben. Und *Firmen* wie eine *GmbH* oder ein *Verein*
sind rechtsfähig ab ihrer *Eintragung* ins Register.""",
  "Menschen", ["von Geburt bis Tod", "auch ein Baby kann erben"], "Firmen (GmbH, Verein)", ["ab Eintragung ins Register"], "Firmen")
M("""Merke: Rechtsfähig heißt Rechte *haben*. Das ist noch nicht dasselbe wie selbst Verträge schließen, das kommt im nächsten Thema.""", "Rechtsfähig = Rechte HABEN")

thema("Geschäftsfähigkeit")
T("""Thema zwei: die *Geschäftsfähigkeit*.""")
D("""Geschäftsfähig heißt: Man kann *selbst gültige Verträge* abschließen.""", "Geschäftsfähigkeit", "Man kann selbst gültige Verträge abschließen.")
RAW("""Es gibt drei Stufen. *Unter sieben* Jahren ist man *geschäftsunfähig*, ein Vertrag ist *nichtig*, also ungültig. Von *sieben bis siebzehn* ist man
*beschränkt geschäftsfähig*: Der Vertrag ist *schwebend unwirksam*. Er hängt sozusagen in der Luft und wird erst gültig, wenn die *Eltern zustimmen*.
Und ab *achtzehn* ist man *voll geschäftsfähig*.""",
    {"type": "stairs", "title": "Die 3 Stufen", "items": [
        it("unter 7: geschäftsunfähig", "sieben", sub="Vertrag nichtig"),
        it("7 bis 17: beschränkt geschäftsfähig", "beschränkt", sub="schwebend unwirksam ➜ gültig, wenn Eltern zustimmen"),
        it("ab 18: voll geschäftsfähig", "achtzehn", sub="Vertrag gültig")]})
P("""Es gibt aber *Ausnahmen*, da braucht ein Jugendlicher die Eltern nicht. Erstens der *Taschengeldparagraf*: Er bezahlt *sofort und komplett* mit seinem Taschengeld.
Zweitens, wenn er *nur einen rechtlichen Vorteil* hat, zum Beispiel ein *Geschenk*. Und drittens Geschäfte rund um ein *Arbeits- oder Ausbildungsverhältnis*,
das die Eltern erlaubt haben.""",
  "Ausnahmen (gültig ohne Eltern)", [it("Taschengeldparagraf: sofort & komplett mit Taschengeld bezahlt", "Taschengeldparagraf"),
                                     it("nur rechtlicher Vorteil (Geschenk)", "Vorteil"), it("Arbeits- / Ausbildungsverhältnis, von Eltern erlaubt", "Arbeits")])
X("""Was passiert? Ein *Sechzehnjähriger* kauft ein Handy auf *Raten*. Taschengeldparagraf? Nein, denn *Raten* sind nicht sofort und komplett bezahlt.
Also ist der Vertrag *schwebend unwirksam*. Die *Eltern sagen Nein*, und damit ist der Vertrag *ungültig*.""",
  [it("16-Jähriger kauft auf Raten", "Sechzehnjähriger"), it("kein Taschengeldparagraf", "Raten"), it("schwebend unwirksam", "schwebend"),
   it("Eltern sagen Nein ➜ ungültig", "Eltern")])
M("""Merke: Unter sieben nichtig, sieben bis siebzehn schwebend unwirksam, ab achtzehn gültig.""", "unter 7 nichtig · 7–17 schwebend unwirksam · ab 18 gültig")

thema("Willenserklärung und Rechtsgeschäfte")
T("""Thema drei: *Willenserklärung und Rechtsgeschäfte*.""")
D("""Eine *Willenserklärung* ist eine Äußerung, mit der man eine *rechtliche Folge* erreichen will. Das kann *mündlich*, *schriftlich* oder sogar durch *Handeln* passieren.
Wenn du an der Kasse wortlos deine Ware aufs Band legst, ist das auch eine Willenserklärung.""",
  "Willenserklärung", "Äußerung, um eine rechtliche Folge zu erreichen – mündlich, schriftlich oder durch Handeln.")
C("""Daraus entstehen *Rechtsgeschäfte*. Beim *einseitigen* Rechtsgeschäft reicht *eine* Willenserklärung, zum Beispiel bei der *Kündigung* oder beim *Testament*.
Beim *zweiseitigen* Rechtsgeschäft braucht man *zwei übereinstimmende* Willenserklärungen, das ist ein *Vertrag*, zum Beispiel ein Kauf-, Miet- oder Arbeitsvertrag.""",
  "einseitig", ["eine Willenserklärung reicht", "Kündigung", "Testament"], "zweiseitig = Vertrag", ["zwei übereinstimmende Willenserklärungen", "Kauf, Miete, Arbeit"], "zweiseitigen")
M("""Merke: Einer reicht gleich einseitig. Zwei nötig gleich Vertrag.""", "Einer reicht = einseitig · Zwei nötig = Vertrag")

thema("Formvorschriften")
T("""Thema vier: *Formvorschriften*.""")
D("""Formvorschriften sind Regeln, *in welcher Form* ein Rechtsgeschäft geschlossen werden muss. Der *Grundsatz* ist aber: *formfrei*, also mündlich reicht.""",
  "Formvorschriften", "Regeln, in welcher Form ein Rechtsgeschäft geschlossen werden muss. Grundsatz: formfrei.")
TB("""Für wichtige Geschäfte gibt es Ausnahmen. Die *Schriftform* mit eigenhändiger Unterschrift, zum Beispiel bei der *Kündigung* eines Arbeitsvertrags, bei der *Bürgschaft*,
beim *Verbraucherdarlehen* und beim *Mietvertrag über ein Jahr*. Die *öffentliche Beglaubigung*: Der Notar bestätigt nur die *Unterschrift*, zum Beispiel fürs Handelsregister.
Und die *notarielle Beurkundung*: Der Notar beurkundet den *ganzen Vertrag* und berät, zum Beispiel beim *Grundstückskauf* oder einer GmbH-Gründung.""",
   "Formen", ["Form", "Was?", "Beispiele"],
   [(["Schriftform", "eigenhändige Unterschrift", "Kündigung, Bürgschaft, Darlehen, Miete > 1 Jahr"], "Schriftform"),
    (["öffentliche Beglaubigung", "Notar bestätigt die Unterschrift", "Handelsregister"], "Beglaubigung"),
    (["notarielle Beurkundung", "Notar beurkundet den ganzen Vertrag", "Grundstückskauf, GmbH-Gründung"], "Beurkundung")])
P("""Warum gibt es das? Als *Beweis*, als Schutz vor *übereilten Entscheidungen* und damit man *beraten* wird. Und was passiert, wenn die Form fehlt?
Dann ist der Vertrag *nichtig*. Ein Grundstück per Handschlag zu kaufen ist also ungültig.""",
  "Warum?", [it("Beweis", "Beweis"), it("Schutz vor übereilten Entscheidungen", "übereilten"), it("Beratung", "beraten"), it("Form fehlt ➜ Vertrag nichtig", "nichtig")])
M("""Merke: Normal formfrei. Wichtig gleich Schrift oder Notar.""", "normal formfrei · wichtig = Schrift oder Notar · Form fehlt ➜ nichtig")

thema("Nichtig und anfechtbar")
T("""Thema fünf: *nichtig und anfechtbar*.""")
C("""Zwei Begriffe, die du sicher unterscheiden musst. *Nichtig* heißt: von *Anfang an ungültig*, der Vertrag hat nie existiert. *Anfechtbar* heißt: Der Vertrag ist erst einmal
*gültig*, aber durch eine *Anfechtung* wird er *rückwirkend* ungültig.""",
  "nichtig", ["von Anfang an ungültig"], "anfechtbar", ["erst gültig", "durch Anfechtung rückwirkend ungültig"], "Anfechtbar")
C("""*Nichtig* ist ein Vertrag bei *Geschäftsunfähigen*, bei einem *Formfehler*, bei einem Verstoß gegen ein *Gesetz* oder gegen die *guten Sitten*, zum Beispiel *Wucher*,
und bei *Scherz-* und *Scheingeschäften*. *Anfechtbar* ist er bei einem *Irrtum*, also verschrieben, versprochen oder etwas falsch verstanden, dann muss man *sofort* anfechten.
Bei *arglistiger Täuschung* und *widerrechtlicher Drohung* hat man *ein Jahr* Zeit.""",
  "nichtig bei …", ["Geschäftsunfähigen", "Formfehler", "Verstoß gegen Gesetz / gute Sitten (Wucher)", "Scherz- & Scheingeschäft"],
  "anfechtbar bei …", ["Irrtum ➜ sofort anfechten", "arglistige Täuschung ➜ 1 Jahr", "widerrechtliche Drohung ➜ 1 Jahr"], "Anfechtbar")
X("""Was passiert? Ein Verkäufer *verschweigt* beim Gebrauchtwagen einen *Unfallschaden*. Das ist *Täuschung*. Der Käufer *ficht an*,
der Vertrag wird *ungültig*, und beide bekommen ihr *Auto und Geld zurück*.""",
  [it("Unfallschaden verschwiegen", "Unfallschaden"), it("Täuschung", "Täuschung"), it("Käufer ficht an", "ficht"), it("Vertrag ungültig ➜ Auto & Geld zurück", "ungültig")])
M("""Merke: Nichtig ist sofort tot. Anfechtbar lebt, bis jemand anficht.""", "Nichtig = sofort tot · Anfechtbar = lebt, bis jemand anficht")

thema("Kaufvertrag")
T("""Thema sechs: der *Kaufvertrag*.""")
D("""Ein Kaufvertrag besteht aus *Antrag* und *Annahme*, also zwei übereinstimmenden Willenserklärungen.""", "Kaufvertrag", "Antrag + Annahme (zwei übereinstimmende Willenserklärungen)")
P("""Jetzt kommt eine Falle: *Werbung*, *Schaufenster*, *Prospekt* und *Online-Shop* sind *kein Antrag*, sondern nur eine *Aufforderung*, ein Angebot zu machen.
Der Antrag ist erst deine *Bestellung*. Wer einen Antrag macht, ist daran *gebunden*: unter Anwesenden oder am *Telefon* nur *sofort*, per Brief oder *E-Mail*
so lange, wie man *normalerweise* eine Antwort erwartet. Mit „*freibleibend*“ oder „solange Vorrat reicht“ bindet man sich nicht oder nur eingeschränkt.
Und kommt die *Annahme zu spät* oder *geändert*, ist das ein *neuer Antrag*.""",
  "Antrag & Bindung", [it("Werbung, Schaufenster, Prospekt, Online-Shop = KEIN Antrag", "Werbung"), it("Bestellung = Antrag", "Bestellung"),
                       it("Bindung: Telefon / anwesend ➜ sofort", "Telefon"), it("Brief / E-Mail ➜ so lange wie normal", "E-Mail"),
                       it("„freibleibend“, „solange Vorrat reicht“ ➜ eingeschränkt", "freibleibend"), it("zu spät / geändert ➜ neuer Antrag", "spät")])
C("""Und die *Pflichten*: Der *Verkäufer* muss die Ware *übergeben*, dir das *Eigentum* verschaffen und *mangelfrei* liefern. Der *Käufer* muss *zahlen* und die Ware *abnehmen*.""",
  "Verkäufer", ["übergeben", "Eigentum verschaffen", "mangelfrei liefern"], "Käufer", ["zahlen", "abnehmen"], "Käufer")
M("""Merke: Werbung ist kein Antrag. Antrag plus Annahme gleich Vertrag.""", "Werbung ≠ Antrag · Antrag + Annahme = Vertrag")

thema("Besitz und Eigentum")
T("""Thema sieben: *Besitz und Eigentum*.""")
C("""*Besitz* ist die *tatsächliche* Herrschaft, also wer die Sache gerade *hat*. *Eigentum* ist die *rechtliche* Herrschaft, also wem sie *gehört*.
Leiht sich Lukas die Bohrmaschine vom Kollegen, ist er Besitzer, der Kollege bleibt Eigentümer.""",
  "Besitz", ["tatsächliche Herrschaft", "➜ haben"], "Eigentum", ["rechtliche Herrschaft", "➜ gehören"], "Eigentum")
P("""Wie geht Eigentum über? Durch *Einigung* und *Übergabe*. Beim *Eigentumsvorbehalt* bleibt die Ware *Eigentum des Verkäufers*, bis sie *komplett bezahlt* ist.
Das muss aber *vereinbart* werden.""",
  "Eigentumsübertragung", [it("Einigung + Übergabe", "Einigung"), it("Eigentumsvorbehalt: gehört dem Verkäufer bis komplett bezahlt", "Eigentumsvorbehalt"),
                           it("muss vereinbart werden", "vereinbart")])
X("""Was passiert? *Ratenkauf* mit Eigentumsvorbehalt, der Käufer *zahlt nicht* mehr. Dann darf der Verkäufer die Ware *zurückholen*, sie gehört ja noch ihm.""",
  [it("Ratenkauf mit Eigentumsvorbehalt", "Ratenkauf"), it("Käufer zahlt nicht", "zahlt"), it("Verkäufer holt die Ware zurück", "zurückholen")])
M("""Merke: Besitz heißt haben, Eigentum heißt gehören. Ein Dieb ist Besitzer, aber nie Eigentümer.""", "Besitz = haben · Eigentum = gehören · Dieb = Besitzer, nie Eigentümer")

thema("Mangelhafte Lieferung")
T("""Thema acht: die *mangelhafte Lieferung*.""")
D("""Ein Mangel liegt vor, wenn die Ware bei der *Übergabe* nicht so ist wie *vereinbart* oder *üblich*.""", "Mangel", "Ware ist bei Übergabe nicht wie vereinbart oder üblich.")
P("""Welche *Mängelarten* gibt es? Der *Qualitätsmangel*, die Ware ist kaputt. Die *Falschlieferung*. Der *Mengenmangel*, es fehlt etwas. Der *Montagemangel*,
die *fehlerhafte Montageanleitung* und eine *falsche Werbeaussage*. Nach der *Erkennbarkeit* unterscheidet man *offene*, *versteckte* und *arglistig verschwiegene* Mängel.""",
  "Mängelarten", [it("Qualitätsmangel", "Qualitätsmangel"), it("Falschlieferung", "Falschlieferung"), it("Mengenmangel", "Mengenmangel"),
                  it("Montagemangel, fehlerhafte Montageanleitung", "Montagemangel"), it("falsche Werbeaussage", "Werbeaussage"),
                  it("Erkennbarkeit: offen, versteckt, arglistig verschwiegen", "Erkennbarkeit")])
RAW("""Welche *Rechte* hast du? Ganz wichtig ist die Reihenfolge. Erst kommt die *Nacherfüllung*, und du *wählst*: *Nachbesserung*, also Reparatur, oder *Ersatzlieferung*.
Erst *danach*, wenn das *fehlgeschlagen* ist, meist nach *zwei Versuchen*, kommen die anderen Rechte: *Rücktritt*, aber nicht bei einem kleinen Mangel,
*Minderung*, also weniger zahlen, und *Schadensersatz*, aber nur, wenn der Verkäufer *schuld* ist.""",
    {"type": "stairs", "title": "Rechte des Käufers", "items": [
        it("1. Nacherfüllung: Nachbesserung oder Ersatzlieferung", "Nacherfüllung", sub="Käufer wählt"),
        it("2. danach (meist nach 2 Versuchen): Rücktritt", "Rücktritt", sub="nicht bei kleinem Mangel"),
        it("… oder Minderung", "Minderung", sub="weniger zahlen"),
        it("… zusätzlich Schadensersatz", "Schadensersatz", sub="nur wenn Verkäufer schuld ist")]})
P("""Die *Fristen*: Die *Gewährleistung* beträgt *zwei Jahre* ab Übergabe. Bei *gebrauchter* Ware an Verbraucher darf sie auf *ein Jahr* verkürzt werden.
Und die *Beweislastumkehr*: Zeigt sich der Mangel im *ersten Jahr*, muss der *Verkäufer* beweisen, dass die Ware in Ordnung war. Danach muss der *Käufer* beweisen.""",
  "Fristen", [it("Gewährleistung: 2 Jahre ab Übergabe", "Gewährleistung"), it("gebraucht an Verbraucher: auf 1 Jahr verkürzbar", "gebrauchter"),
              it("Beweislastumkehr: im 1. Jahr muss der Verkäufer beweisen", "Beweislastumkehr"), it("danach der Käufer", "danach")])
M("""Merke: Erst reparieren oder neu, dann Rücktritt, Minderung, Schadensersatz.""", "erst Reparatur oder neu ➜ dann Rücktritt, Minderung, Schadensersatz")

thema("Zahlungsverzug")
T("""Thema neun: der *Zahlungsverzug*.""")
D("""Zahlungsverzug heißt: Der Käufer zahlt *nicht rechtzeitig*, obwohl die Zahlung *fällig* ist.""", "Zahlungsverzug", "Der Käufer zahlt nicht rechtzeitig, obwohl die Zahlung fällig ist.")
P("""Wann ist man im Verzug? Durch eine *Mahnung* nach Fälligkeit, eine einzige reicht. *Oder* durch ein *festes Kalenderdatum*, zum Beispiel „zahlbar bis fünfzehnten Mai“,
dann ganz ohne Mahnung. *Oder* nach *dreißig Tagen* nach Rechnung, bei Verbrauchern aber nur, wenn das als *Hinweis* auf der Rechnung steht.""",
  "Verzug tritt ein durch …", [it("Mahnung nach Fälligkeit (eine reicht)", "Mahnung"), it("festes Kalenderdatum ➜ ohne Mahnung", "Kalenderdatum"),
                               it("30 Tage nach Rechnung (Verbraucher: nur mit Hinweis)", "dreißig")])
P("""Was darf der *Verkäufer* dann verlangen? Die *Zahlung* plus *Verzugszinsen*, bei Verbrauchern der *Basiszinssatz plus fünf Prozentpunkte*.
Dazu *Schadensersatz*, zum Beispiel die *Mahnkosten*. Und nach einer *Nachfrist* kann er vom Vertrag *zurücktreten*.""",
  "Rechte des Verkäufers", [it("Zahlung + Verzugszinsen (Basiszins + 5 Prozentpunkte)", "Verzugszinsen"), it("Schadensersatz (Mahnkosten)", "Schadensersatz"),
                            it("nach Nachfrist: Rücktritt", "Nachfrist")])
M("""Merke: Fällig plus Mahnung, oder Datum, oder dreißig Tage mit Hinweis, gleich Verzug, und dann gibt es Zinsen.""", "fällig + Mahnung (oder Datum / 30 Tage mit Hinweis) = Verzug ➜ Zinsen")

thema("Regelmäßige Verjährung")
T("""Thema zehn: die *regelmäßige Verjährung*.""")
D("""Verjährung heißt: Nach Ablauf der Frist kann man eine Forderung *nicht mehr vor Gericht durchsetzen*. Der Schuldner darf die Zahlung *verweigern*.""",
  "Verjährung", "Nach Ablauf der Frist kann man eine Forderung nicht mehr vor Gericht durchsetzen.")
RAW("""Die Frist beträgt *drei Jahre*. Sie *beginnt* am *einunddreißigsten Zwölften* des Jahres, in dem die Forderung entstanden ist, und *endet* am einunddreißigsten Zwölften drei Jahre später.
Beispiel: Eine Rechnung vom *fünfzehnten März zweitausendsechsundzwanzig*. Die Frist startet am einunddreißigsten Dezember zweitausendsechsundzwanzig und endet am
*einunddreißigsten Dezember zweitausendneunundzwanzig*. Und: Wer eine *verjährte Schuld* trotzdem bezahlt, bekommt das Geld *nicht zurück*.""",
    {"type": "timeline", "title": "Regelmäßige Verjährung: 3 Jahre ab Jahresende", "cue": "Beispiel",
     "points": ["15.03.2026 Rechnung", "31.12.2026 Start", "31.12.2029 Ende"]})
C("""Zwei Begriffe, die gut zu wissen sind: Der *Neubeginn*: Die Frist startet *komplett neu*, wenn der Schuldner die Schuld *anerkennt*, zum Beispiel durch eine *Teilzahlung*,
eine Zinszahlung oder eine Bitte um Stundung, oder bei einer *Vollstreckung*. Die neuen drei Jahre starten am *Tag danach*, nicht am Jahresende.
Die *Hemmung*: Die Frist wird *angehalten*, zum Beispiel bei *Verhandlungen*, einem *Mahnbescheid* oder einer *Klage*. Die Zeit wird *hinten angehängt*.""",
  "Neubeginn", ["Frist startet komplett neu", "Anerkennung (Teilzahlung …), Vollstreckung", "ab dem Tag danach"],
  "Hemmung", ["Frist wird angehalten", "Verhandlungen, Mahnbescheid, Klage", "Zeit wird hinten angehängt"], "Hemmung")
M("""Merke: Drei Jahre, Start immer am Jahresende. Neubeginn heißt Uhr auf null. Hemmung heißt Uhr angehalten.""", "3 Jahre, Start am Jahresende · Neubeginn = Uhr auf null · Hemmung = Uhr angehalten")

thema("Verbraucherberatung")
T("""Thema elf: die *Verbraucherberatung*.""")
P("""Verbraucherberatung ist Hilfe für Verbraucher, um sich zu *informieren* und ihre *Rechte durchzusetzen*. Die *Verbraucherzentralen* bieten *persönliche Beratung*.
Die *Stiftung Warentest* testet Produkte und veröffentlicht die Hefte *test* und *Finanztest*. Und dann gibt es *Publikationen*: Ratgeber, Broschüren und das Internet.""",
  "Verbraucherberatung", [it("Verbraucherzentralen ➜ persönliche Beratung", "Verbraucherzentralen"), it("Stiftung Warentest ➜ Hefte „test“ & „Finanztest“", "Warentest"),
                          it("Publikationen ➜ Ratgeber, Broschüren, Internet", "Publikationen")])
M("""Merke: Beratung gleich Verbraucherzentrale. Tests gleich Stiftung Warentest.""", "Beratung = Verbraucherzentrale · Tests = Stiftung Warentest")

thema("Fernabsatz")
T("""Thema zwölf: der *Fernabsatz*.""")
D("""Fernabsatz ist ein Vertrag *ohne persönlichen Kontakt*, also im *Internet*, am *Telefon* oder per *Katalog*.""", "Fernabsatz", "Vertrag ohne persönlichen Kontakt (Internet, Telefon, Katalog)")
P("""Hier hast du ein *Widerrufsrecht* von *vierzehn Tagen*, *ohne Grund*. Die Frist beginnt mit dem *Erhalt der Ware* und der *Belehrung*. Fehlt die Belehrung,
hast du maximal *zwölf Monate plus vierzehn Tage*. Den Widerruf musst du *eindeutig erklären*, nur zurückschicken reicht nicht. Die *Rücksendekosten* trägt der *Kunde*,
wenn er vorher informiert wurde. *Kein* Widerruf gibt es bei *individuell angefertigter* Ware, *Verderblichem* und *entsiegelter* Hygieneware, Software oder CDs.""",
  "Widerrufsrecht", [it("14 Tage, ohne Grund", "vierzehn"), it("Beginn: Erhalt der Ware + Belehrung", "Erhalt"), it("ohne Belehrung: max. 12 Monate + 14 Tage", "zwölf"),
                     it("Widerruf eindeutig erklären", "eindeutig"), it("Rücksendekosten: Kunde (wenn informiert)", "Rücksendekosten"),
                     it("kein Widerruf: individuell, verderblich, entsiegelt", "individuell")])
M("""Merke: Online vierzehn Tage ohne Grund. Im Laden *nicht*, dort gibt es nur Kulanz.""", "Online = 14 Tage ohne Grund · im Laden NICHT (nur Kulanz)")

thema("AGB")
T("""Thema dreizehn: die *AGB*, die Allgemeinen Geschäftsbedingungen.""")
D("""AGB sind *vorformulierte* Vertragsbedingungen für *viele Verträge*, also das Kleingedruckte.""", "AGB", "Vorformulierte Vertragsbedingungen für viele Verträge.")
P("""Die *Bedeutung*: Die Firma *spart Zeit und Kosten*. Aber der Kunde kann *nicht mitverhandeln* und könnte *benachteiligt* werden, darum schützt ihn das Gesetz.
AGB gelten nur bei einem *deutlichen Hinweis*, einer *zumutbaren Kenntnisnahme* und dem *Einverständnis* des Kunden. Die gesetzlichen Regeln:
*Überraschende Klauseln* sind *unwirksam*. Die *Gewährleistung* darf bei Verbrauchern *nicht verkürzt* werden. Und ist eine Klausel unwirksam, gilt das *Gesetz*,
der *Rest des Vertrags* bleibt gültig.""",
  "AGB-Regeln", [it("Firma spart Zeit & Kosten – Kunde kann nicht mitverhandeln", "spart"), it("gelten nur: Hinweis, Kenntnisnahme, Einverständnis", "Hinweis"),
                 it("überraschende Klauseln ➜ unwirksam", "Überraschende"), it("Gewährleistung bei Verbrauchern nicht verkürzbar", "Gewährleistung"),
                 it("unwirksame Klausel ➜ Gesetz gilt, Rest bleibt gültig", "Rest")])
M("""Merke: AGB dürfen nicht überraschen und keine gesetzlichen Rechte wegnehmen.""", "AGB dürfen nicht überraschen und keine gesetzlichen Rechte wegnehmen")

thema("Girokonto und Zahlungsverkehr")
T("""Thema vierzehn: *Girokonto und Zahlungsverkehr*.""")
P("""Das *Girokonto* ist das Konto für den *täglichen Zahlungsverkehr*. Vergleiche die *Konditionen*: *Kontoführungsgebühr*, *Kartenkosten*, *Dispozinsen*, Geldautomaten,
*Online-Banking* und ob es eine Filiale gibt.""",
  "Girokonto – Konditionen", [it("Kontoführungsgebühr", "Kontoführungsgebühr"), it("Kartenkosten", "Kartenkosten"), it("Dispozinsen", "Dispozinsen"),
                              it("Geldautomaten, Online-Banking, Filiale", "Online")])
TB("""Die *Zahlungsformen*: *Bar*: sofort, anonym, gute Kontrolle, aber Diebstahlrisiko. *Überweisung*: als *Dauerauftrag* für gleiche Beträge wie die Miete,
die *Lastschrift* für wechselnde Beträge wie Strom, da holt der Empfänger das Geld ab. Die *Girocard*: Das Geld geht *sofort* ab. Die *Kreditkarte*:
wird *später* abgebucht, funktioniert weltweit, aber man kann den Überblick verlieren. Und *elektronisch*, also PayPal oder Apple Pay: schnell online, mit *Käuferschutz*.""",
   "Zahlungsformen", ["Form", "Vorteil / Nachteil"],
   [(["Bar", "sofort, anonym, Kontrolle / Diebstahlrisiko"], "Bar"), (["Dauerauftrag", "gleicher Betrag (Miete)"], "Dauerauftrag"),
    (["Lastschrift", "Empfänger holt ab, wechselnde Beträge (Strom)"], "Lastschrift"), (["Girocard", "Geld geht sofort ab"], "Girocard"),
    (["Kreditkarte", "später abgebucht, weltweit / Überblick, Schulden"], "Kreditkarte"), (["PayPal, Apple Pay", "schnell online, Käuferschutz"], "elektronisch")])
M("""Merke: Die Zahlungsform immer *nach der Situation* begründen.""", "Zahlungsform immer nach Situation begründen")

thema("Geldanlage")
T("""Thema fünfzehn: die *Geldanlage*.""")
RAW("""Geld anlegen heißt: Geld so anlegen, dass es *mehr* wird. Beurteilt wird das mit dem *magischen Dreieck*. *Liquidität*: Wie schnell komme ich an mein Geld?
*Rentabilität*: Wie viel Ertrag bringt es? *Sicherheit*: Wie sicher ist es? Und der *Zielkonflikt*: Nie sind alle drei gleichzeitig maximal. Mehr Rendite heißt mehr Risiko.
Das *Termingeld*: feste Zeit, fester Zins, Sicherheit *hoch*, Liquidität *niedrig*, Rentabilität *mittel*. Der *Aktienfonds*: viele Aktien, das Risiko ist gestreut,
Rentabilität *hoch*, Sicherheit *niedriger*, Liquidität *hoch*.""",
    {"type": "triangle", "corners": [["Sicherheit", "🛡️", "Sicherheit"], ["Liquidität", "💧", "Liquidität"], ["Rentabilität", "📈", "Rentabilität"]],
     "compare": [{"name": "Termingeld", "vals": ["hoch", "niedrig", "mittel"], "cue": "Termingeld"}, {"name": "Aktienfonds", "vals": ["niedriger", "hoch", "hoch"], "cue": "Aktienfonds"}]})
M("""Merke: Sicher und kurzfristig gleich Termingeld. Langfristig mit Chance und Risiko gleich Aktienfonds.""", "sicher & kurzfristig = Termingeld · langfristig, Chance & Risiko = Aktienfonds")

thema("Verbraucherdarlehen")
T("""Thema sechzehn: das *Verbraucherdarlehen*.""")
P("""Ein Verbraucherdarlehen ist ein *Kredit* von einem Unternehmen, meist einer Bank, an einen *Verbraucher*. Die Bank prüft die *Kreditwürdigkeit*: Einkommen, *Arbeitsvertrag*,
die *SCHUFA*, Vermögen und andere Schulden. Der Vertrag muss *schriftlich* sein. *Inhalt*: Nettodarlehensbetrag, *Sollzins*, der *effektive Jahreszins*, mit dem du Angebote vergleichst,
Laufzeit, Raten, Gesamtbetrag und ein *Widerrufsrecht* von vierzehn Tagen.""",
  "Verbraucherdarlehen", [it("Kreditwürdigkeit: Einkommen, Arbeitsvertrag, SCHUFA, Vermögen", "Kreditwürdigkeit"), it("Form: schriftlich", "schriftlich"),
                          it("effektiver Jahreszins zum Vergleichen", "effektive"), it("Widerrufsrecht 14 Tage", "Widerrufsrecht")])
TB("""Die Bank will *Sicherheiten*. Bei der *Sicherungsübereignung* wird die Bank *Eigentümer*, der Kunde bleibt *Besitzer*. Beim Autokredit hat die Bank zum Beispiel den Fahrzeugbrief,
aber du fährst das Auto. Bei der *Bürgschaft* haftet eine *andere Person*, das muss schriftlich sein. Und bei der *Lohnabtretung* bekommt die Bank einen Teil deines *Lohns*
direkt vom *Arbeitgeber*.""",
   "Sicherheiten", ["Sicherheit", "So funktioniert's"],
   [(["Sicherungsübereignung", "Bank = Eigentümer, Kunde = Besitzer (Fahrzeugbrief)"], "Sicherungsübereignung"),
    (["Bürgschaft", "andere Person haftet, schriftlich"], "Bürgschaft"), (["Lohnabtretung", "Bank bekommt Teil vom Lohn vom Arbeitgeber"], "Lohnabtretung")])
M("""Merke: Sicherungsübereignung gleich Bank ist Eigentümer. Bürgschaft gleich ein anderer zahlt. Lohnabtretung gleich vom Lohn.""",
  "Sicherungsübereignung = Bank Eigentümer · Bürgschaft = anderer zahlt · Lohnabtretung = vom Lohn")

thema("Überschuldung")
T("""Thema siebzehn, das letzte: die *Überschuldung*.""")
D("""Überschuldung heißt: Die Schulden können mit Einkommen und Vermögen *auf Dauer nicht mehr bezahlt* werden.""", "Überschuldung", "Schulden können mit Einkommen und Vermögen auf Dauer nicht mehr bezahlt werden.")
P("""Typische *Ursachen*: *Arbeitslosigkeit*, *Trennung*, *Krankheit*, *Konsum auf Raten*, der *Dispo* und teure *Handyverträge*.""",
  "Ursachen", [it("Arbeitslosigkeit", "Arbeitslosigkeit"), it("Trennung, Krankheit", "Trennung"), it("Konsum auf Raten, Dispo", "Konsum"), it("Handyverträge", "Handyverträge")])
X("""Die *Lösungen* in drei Stufen: Erstens ein *Haushaltsplan* mit Einnahmen und Ausgaben, das hilft auch vorbeugend. Zweitens die *Schuldnerberatung*, die ist kostenlos
und verhandelt mit den Gläubigern. Drittens die *Verbraucherinsolvenz*. Die läuft so ab: zuerst ein *außergerichtlicher Einigungsversuch*, dann der *Antrag* beim Insolvenzgericht,
dann die *Wohlverhaltensphase* von *drei Jahren*. Da gibst du den pfändbaren Teil ab, arbeitest oder suchst Arbeit und machst keine neuen Schulden. Und am Ende kommt die *Restschuldbefreiung*.""",
  [it("Haushaltsplan", "Haushaltsplan"), it("Schuldnerberatung", "Schuldnerberatung"), it("Einigungsversuch", "außergerichtlicher"), it("Antrag Insolvenzgericht", "Antrag"),
   it("Wohlverhaltensphase 3 Jahre", "Wohlverhaltensphase"), it("Restschuldbefreiung", "Restschuldbefreiung")], title="Lösungen & Verbraucherinsolvenz")
M("""Merke: Haushaltsplan, Schuldnerberatung, Insolvenz, und nach drei Jahren ein Neustart.""", "Haushaltsplan ➜ Schuldnerberatung ➜ Insolvenz ➜ nach 3 Jahren Neustart")
sc("""Das war Kompetenzbereich zwei mit allen *siebzehn Themen*. Hier siehst du sie noch einmal im Überblick. Weiter geht's mit Kompetenzbereich drei.""",
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
# KB IV
# =====================================================================================
kb(4, "Entscheidungen bei einer Selbstständigkeit", ["Selbstständigkeit", "Geschäftsplan und Standort", "Rechtsformen", "Kapitalbedarfsplan"])
sc("""Willkommen zum Kompetenzbereich vier: *Entscheidungen bei einer Selbstständigkeit*. Hier geht es darum, ein eigenes Unternehmen zu gründen. *Vier Themen*, genau wie auf deinem Lernzettel.""",
   {"type": "kb"})

thema("Selbstständigkeit")
T("""Thema eins: die *Selbstständigkeit*.""")
D("""Selbstständig ist, wer sein *eigenes Unternehmen* führt. Du hast *keinen Chef* mehr, aber du trägst das *ganze Risiko*.""",
  "Selbstständigkeit", "Wer sein eigenes Unternehmen führt. Kein Chef, aber das ganze Risiko.")
P("""Warum macht man das? Die *Motive*: *eigener Chef* sein, *eigene Ideen* umsetzen, *mehr verdienen*, *Selbstverwirklichung*, und manchmal, weil *kein passender Job* in Aussicht ist.
Lukas zum Beispiel möchte sich als Elektriker auf Photovoltaik spezialisieren und sein eigener Chef sein.""",
  "Motive", [it("eigener Chef sein", "eigener"), it("eigene Ideen umsetzen", "Ideen"), it("mehr verdienen", "verdienen"), it("Selbstverwirklichung", "Selbstverwirklichung"),
             it("kein passender Job in Aussicht", "Job")])
TB("""Man braucht *Unternehmereigenschaften*, und die nennst du *immer mit Begründung*. *Belastbarkeit*, weil es viel Arbeit und Stress gibt. *Kommunikationsfähigkeit*,
weil man mit Kunden, Mitarbeitern und der Bank reden muss. *Fachwissen*, um das Handwerk zu beherrschen. *Kaufmännisches Wissen*, um zu rechnen und zu planen.
*Entscheidungsfreude*, weil man allein entscheidet. Und *Risikobereitschaft*, weil das eigene Geld verloren gehen kann.""",
   "Unternehmereigenschaften (mit Begründung!)", ["Eigenschaft", "weil …"],
   [(["Belastbarkeit", "viel Arbeit und Stress"], "Belastbarkeit"), (["Kommunikationsfähigkeit", "mit Kunden, Mitarbeitern, Bank reden"], "Kommunikationsfähigkeit"),
    (["Fachwissen", "das Handwerk beherrschen"], "Fachwissen"), (["Kaufmännisches Wissen", "rechnen und planen"], "Kaufmännisches"),
    (["Entscheidungsfreude", "allein entscheiden"], "Entscheidungsfreude"), (["Risikobereitschaft", "eigenes Geld kann verloren gehen"], "Risikobereitschaft")])
TB("""Jetzt die *Chancen und Risiken*, immer in vier Bereichen. *Einkommen*: Chance, mehr verdienen, der Gewinn gehört einem selbst. Risiko, kein festes Gehalt, eigenes Geld kann verloren gehen,
bis zur *Insolvenz*. *Arbeitszeit*: Chance, Zeit selbst einteilen. Risiko, viel Arbeit, auch am Wochenende, wenig Urlaub. *Verantwortung*: Chance, eigener Chef, selbst entscheiden.
Risiko, für alles verantwortlich, auch für Mitarbeiter. Und *Absicherung*: Chance, Versicherungen frei wählen. Risiko, alles *selbst zahlen*, keine Lohnfortzahlung bei Krankheit,
kein bezahlter Urlaub.""",
   "Chancen & Risiken", ["Bereich", "Chance ➕", "Risiko ➖"],
   [(["Einkommen", "mehr verdienen, Gewinn gehört mir", "kein festes Gehalt, bis Insolvenz"], "Einkommen"),
    (["Arbeitszeit", "Zeit selbst einteilen", "viel Arbeit, Wochenende, wenig Urlaub"], "Arbeitszeit"),
    (["Verantwortung", "eigener Chef, selbst entscheiden", "für alles verantwortlich, auch Mitarbeiter"], "Verantwortung"),
    (["Absicherung", "Versicherungen frei wählen", "alles selbst zahlen, keine Lohnfortzahlung"], "Absicherung")])
M("""Der Trick, damit du die vier Bereiche nie vergisst: *Geld, Zeit, Verantwortung, Absicherung*.""", "Trick: Geld – Zeit – Verantwortung – Absicherung")

thema("Geschäftsplan und Standort")
T("""Thema zwei: *Geschäftsplan und Standort*.""")
D("""Der *Geschäftsplan* ist ein *schriftliches Konzept* für die Gründung. Er beantwortet zwei Fragen: *Was* will ich machen, und *wie* verdiene ich damit Geld?""",
  "Geschäftsplan", "Schriftliches Konzept für die Gründung: Was will ich machen, und wie verdiene ich damit Geld?")
P("""Der *Inhalt*: die *Geschäftsidee*, die *Gründerperson* mit Ausbildung und Erfahrung, *Kunden und Markt*, die *Konkurrenz*, das *Marketing*, der *Standort*, die *Rechtsform*,
das *Personal* und die *Finanzen*, also der Kapitalbedarfsplan. Die *Funktion*: alles *durchdenken*, dann hat man weniger Risiko, und einen *Kredit* bekommen.
Die *Adressaten*, also wer ihn liest: die *Bank*, der *Gründer selbst* und *Förderstellen*, zum Beispiel die Agentur für Arbeit.""",
  "Geschäftsplan", [it("Inhalt: Idee, Gründerperson, Kunden & Markt, Konkurrenz", "Geschäftsidee"), it("… Marketing, Standort, Rechtsform, Personal, Finanzen", "Marketing"),
                    it("Funktion: durchdenken ➜ weniger Risiko + Kredit", "Funktion"), it("Adressaten: Bank, Gründer selbst, Förderstellen", "Adressaten")])
P("""Der *Standort* ist der *Ort*, an dem das Unternehmen sitzt. Er entscheidet oft über *Erfolg oder Misserfolg*. Die *Standortfaktoren*: *Kunden* in der Nähe, *Konkurrenz*
in der Nähe, die *Kosten*, also Miete oder Pacht, die *Erreichbarkeit*, also Parkplätze, Bus und Bahn, und *Größe und Ausstattung*, also Platz und Erweiterungsmöglichkeiten.""",
  "Standortfaktoren", [it("Kunden in der Nähe", "Kunden"), it("Konkurrenz in der Nähe", "Konkurrenz"), it("Kosten (Miete, Pacht)", "Kosten"),
                       it("Erreichbarkeit (Parkplätze, Bus, Bahn)", "Erreichbarkeit"), it("Größe & Ausstattung (Platz, Erweiterung)", "Größe")])
X("""In der Prüfung bekommst du oft eine *Bewertungstabelle*. Erstens: Jeden Faktor pro Standort mit *Punkten* bewerten, passend zur *Anlage*. Zweitens: die Punkte *addieren*.
Drittens: den Standort mit den *meisten Punkten* empfehlen, und zwar *mit Begründung*.""",
  [it("Punkte pro Faktor & Standort (passend zur Anlage)", "Punkten"), it("Punkte addieren", "addieren"), it("meiste Punkte ➜ empfehlen + begründen", "meisten")], title="Bewertungstabelle")

thema("Rechtsformen")
T("""Thema drei: die *Rechtsformen*.""")
D("""Die Rechtsform regelt vor allem, *wer haftet* und *wie viel Geld* man zum Gründen braucht. Verglichen wird nach *drei Merkmalen*: *Mindestkapital*, *Haftung* und *Geschäftsführung*.""",
  "Rechtsform", "Regelt vor allem, wer haftet und wie viel Geld man zum Gründen braucht. Merkmale: Mindestkapital, Haftung, Geschäftsführung.")
TB("""Das *Einzelunternehmen*: *eine Person*, *kein* Mindestkapital, die Haftung ist *unbeschränkt*, also auch mit dem *Privatvermögen*, und die Geschäftsführung macht der *Inhaber allein*.
Die *GbR*: *mindestens zwei* Personen, *kein* Mindestkapital, *alle* haften *unbeschränkt* mit dem Privatvermögen, und zwar *jeder für alles*. Die Geschäftsführung machen *alle gemeinsam*.""",
   "Einzelunternehmen & GbR", ["", "Einzelunternehmen", "GbR"],
   [(["Personen", "1", "mind. 2"], "Person"), (["Mindestkapital", "keins", "keins"], "Mindestkapital"),
    (["Haftung", "unbeschränkt, auch privat", "alle unbeschränkt, jeder für alles"], "unbeschränkt"), (["Geschäftsführung", "Inhaber allein", "alle gemeinsam"], "Inhaber")])
TB("""Die *GmbH*: ab *einer Person*, Mindestkapital *fünfundzwanzigtausend Euro*, die Haftung ist *beschränkt*, das *Privatvermögen* ist *geschützt*, und es gibt einen *Geschäftsführer*.
Die *UG haftungsbeschränkt*, die *Mini-GmbH*: ab einer Person, Mindestkapital schon *ab einem Euro*, ebenfalls beschränkte Haftung und ein Geschäftsführer.
Aber sie muss *fünfundzwanzig Prozent* vom Gewinn zurücklegen, bis fünfundzwanzigtausend Euro erreicht sind.""",
   "GmbH & UG", ["", "GmbH", "UG (haftungsbeschränkt)"],
   [(["Personen", "ab 1", "ab 1"], "GmbH"), (["Mindestkapital", "25.000 €", "ab 1 €"], "fünfundzwanzigtausend"),
    (["Haftung", "beschränkt, privat geschützt", "beschränkt, privat geschützt"], "beschränkt"), (["Geschäftsführung", "Geschäftsführer", "Geschäftsführer"], "Geschäftsführer"),
    (["Besonderheit", "–", "25 % vom Gewinn zurücklegen bis 25.000 €"], "Prozent")])
X("""Wie wählst du die *passende* Rechtsform? Drei Fragen. Erstens: *Wie viele* gründen, allein oder mehrere? Zweitens: *Wie viel Geld* ist da? Wenig Geld, dann keine GmbH.
Drittens: Soll das *Privatvermögen geschützt* sein? Dann GmbH oder UG.""",
  [it("Wie viele gründen?", "viele"), it("Wie viel Geld? Wenig ➜ keine GmbH", "Geld"), it("Privatvermögen schützen? ➜ GmbH / UG", "Privatvermögen")], title="So wählst du die Rechtsform")
M("""Merke: Einzelunternehmen und GbR gleich kein Kapital, aber privat haften. GmbH und UG gleich Privatvermögen geschützt. GmbH fünfundzwanzigtausend Euro, UG ein Euro.""",
  "Einzel + GbR = kein Kapital, aber privat haften · GmbH (25.000 €) + UG (1 €) = Privatvermögen geschützt")

thema("Kapitalbedarfsplan")
T("""Thema vier, das letzte: der *Kapitalbedarfsplan*.""")
D("""Der Kapitalbedarfsplan zeigt, *wie viel Geld* man *insgesamt* für die Gründung braucht, und wie viel man davon *von der Bank* leihen muss.""",
  "Kapitalbedarfsplan", "Zeigt, wie viel Geld man insgesamt für die Gründung braucht und wie viel davon von der Bank geliehen werden muss.")
P("""Was gehört rein? a, die *Investitionen*, also einmalige Anschaffungen: Einrichtung, Umbau, Maschinen, Werkzeug, Fahrzeug, Computer, Kasse. b, die *ersten Waren*,
zum Beispiel Fahrräder für den Laden. c, die *Gründungskosten*: Notar, Gewerbeanmeldung, Beratung. d, die *laufenden Kosten* für die Anfangszeit, für einige Monate:
Miete oder Pacht, Löhne, Werbung. e, die *Lebenshaltungskosten* des Gründers, denn am Anfang verdient man wenig, muss aber trotzdem selbst leben. Und f, eine *Reserve* für Unvorhergesehenes.""",
  "Was gehört rein?", [it("a) Investitionen (Einrichtung, Maschinen, Fahrzeug …)", "Investitionen"), it("b) erste Waren", "Waren"), it("c) Gründungskosten (Notar, Gewerbeanmeldung)", "Gründungskosten"),
                       it("d) laufende Kosten Anfangszeit (Miete, Löhne, Werbung)", "laufenden"), it("e) Lebenshaltungskosten des Gründers", "Lebenshaltungskosten"),
                       it("f) Reserve", "Reserve")])
F("""Ganz wichtig: Bei *monatlichen* Kosten rechnest du *mal die Monate*. Pacht zwölfhundert Euro *mal zwölf* Monate. Und die Rechnung lautet:
*Kapitalbedarf minus Eigenkapital gleich Kredit* von der Bank, also *Fremdkapital*.""",
  [["Kapitalbedarf", "#ea580c", "Kapitalbedarf"], ["− Eigenkapital", "#16a34a", "Eigenkapital"], ["= Kredit (Fremdkapital)", "#dc2626", "Kredit"]],
  note="monatliche Kosten × Monate (z. B. Pacht 1.200 € × 12)")
RAW("""Das Beispiel aus deinem Lernzettel: Stefan gründet einen *Fahrradladen* und hat fünfundzwanzigtausend Euro Eigenkapital. *Einrichtung* fünfzehntausend, *Werkzeug* fünftausend,
*Lieferwagen* zwölftausend, *erste Fahrräder* zwanzigtausend, *Gründungskosten* tausendfünfhundert, *Pacht* zwölfhundert mal zwölf gleich vierzehntausendvierhundert,
*Lebenshaltung* fünfzehnhundert mal zwölf gleich achtzehntausend und eine *Reserve* von fünftausend. Das ergibt einen *Kapitalbedarf* von neunzigtausendneunhundert Euro.
Minus fünfundzwanzigtausend Eigenkapital, das sind *fünfundsechzigtausendneunhundert Euro Kredit*.""",
    {"type": "ledger", "title": "Kapitalbedarf Stefan (Fahrradladen)", "rows": [
        {"label": "Einrichtung", "amount": 15000, "cue": "Einrichtung"}, {"label": "Werkzeug", "amount": 5000, "cue": "Werkzeug"},
        {"label": "Lieferwagen", "amount": 12000, "cue": "Lieferwagen"}, {"label": "Erste Fahrräder", "amount": 20000, "cue": "erste"},
        {"label": "Gründungskosten", "amount": 1500, "cue": "Gründungskosten"}, {"label": "Pacht 1.200 € × 12", "amount": 14400, "cue": "Pacht"},
        {"label": "Lebenshaltung 1.500 € × 12", "amount": 18000, "cue": "Lebenshaltung"}, {"label": "Reserve", "amount": 5000, "cue": "Reserve"},
        {"label": "= Kapitalbedarf", "amount": None, "cue": "Kapitalbedarf", "total": True}],
     "note": "90.900 € − 25.000 € Eigenkapital = 65.900 € Kredit", "cueNote": "fünfundsechzigtausendneunhundert"})
P("""Und zum Schluss das *Merke alles* für Kompetenzbereich vier. Thema eins: Motive, Eigenschaften mit Begründung, Chancen und Risiken: Geld, Zeit, Verantwortung, Absicherung.
Thema zwei: Geschäftsplan gleich Konzept für die *Bank*, Standort per *Punktetabelle* begründet wählen. Thema drei: Einzelunternehmen und GbR haften privat, ohne Kapital,
GmbH und UG schützen das Privatvermögen. Thema vier: Kapitalbedarf minus Eigenkapital gleich Kredit, monatliche Kosten mal Monate. Viel Erfolg in deiner Prüfung, du schaffst das!""",
  "Merke alles 🧠", [it("1: Motive, Eigenschaften + Begründung, Geld – Zeit – Verantwortung – Absicherung", "Motive"), it("2: Geschäftsplan = Konzept für die Bank · Standort per Punktetabelle", "Geschäftsplan"),
                    it("3: Einzel/GbR privat haften · GmbH (25.000 €) / UG (1 €) geschützt", "Einzelunternehmen"), it("4: Kapitalbedarf − Eigenkapital = Kredit · monatlich × Monate", "Kapitalbedarf")])

# ---------------------------------------------------------------------------------- Ausgabe
MAX_WORDS = 650
for n, d in KB.items():
    part, words = 0, 0
    for s in d["sentences"]:
        w = len(s["text"].split())
        if words and words + w > MAX_WORDS:
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
