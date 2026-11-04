#!/usr/bin/env python3
"""Baut src/wiso_all/script.json: Lernvideo „WiSo komplett – KB I bis KB IV“ (Berufsschule BW, Abschlussprüfung).

Szene: part (Sprach-Block), topic (0 Intro, 1–4 = KB, 5 Schluss), sub (Unterthema für die Kopfzeile),
text (gesprochen, *Wort* = hervorgehoben), v (Visualisierung, Items erscheinen bei ihrem cue-Wort).
"""
import json
from pathlib import Path

S = []
P = 0


def sc(topic, sub, text, v):
    S.append({"part": P, "topic": topic, "sub": sub, "text": " ".join(text.split()), "v": v})


def it(text, cue, **kw):
    return {"text": text, "cue": cue, **kw}


# =====================================================================
# Block 0 – Einstieg + KB I: Ausbildung
# =====================================================================
P = 0
sc(0, "Einstieg", """Hallo! In diesem Video gehen wir *alle Themen* aus Wirtschaft und Sozialkunde für deine *Abschlussprüfung* durch.
Einfach erklärt, aber so, dass du damit Prüfungsfragen beantworten kannst.""",
   {"type": "title", "title": "WiSo komplett", "subtitle": "Alle Themen für die Abschlussprüfung – einfach erklärt", "badge": "KB I – KB IV · Baden-Württemberg"})
sc(0, "Einstieg", """Der Bildungsplan hat vier *Kompetenzbereiche*. Eins: deine Rolle als *Mitarbeiter* in der Arbeitswelt.
Zwei: du als *Konsument*, also Verträge, Geld und Schulden. Drei: die *Wirtschaft* als Ganzes, also Markt, Preise und Konjunktur.
Und vier: die *Selbstständigkeit*. Begleiten wird uns wieder Lukas, Azubi zum Elektroniker für Betriebstechnik.""",
   {"type": "roadmap", "names": [["👷", "KB I", "Mitarbeiter in der Arbeitswelt"], ["🛒", "KB II", "Konsument & Recht"], ["📈", "KB III", "Markt & Wirtschaft"], ["🧑‍💼", "KB IV", "Selbstständigkeit"]],
    "cues": ["Mitarbeiter", "Konsument", "Wirtschaft", "Selbstständigkeit"]})

sc(1, "Kompetenzbereich I", """Kompetenzbereich eins: Die Rolle des *Mitarbeiters* in der Arbeitswelt.""",
   {"type": "topic", "n": 1, "label": "KOMPETENZBEREICH I", "title": "Mitarbeiter in der Arbeitswelt", "icon": "👷"})
sc(1, "Duale Ausbildung", """Lukas macht eine *duale Ausbildung*. Dual heißt: Es gibt zwei *Lernorte*. Im *Betrieb* lernt er die Praxis,
in der *Berufsschule* die Theorie. Manchmal kommt noch eine *überbetriebliche* Ausbildung dazu.
Beteiligt sind der Azubi, der Ausbildungsbetrieb mit dem Ausbilder, die Berufsschule und die *zuständige Stelle*,
also die Kammer, zum Beispiel die IHK oder die Handwerkskammer. Die Kammer *überwacht* die Ausbildung und nimmt die Prüfungen ab.""",
   {"type": "compare", "left": {"title": "Betrieb", "icon": "🏭", "items": ["Praxis", "Ausbilder", "Ausbildungsplan"]},
    "right": {"title": "Berufsschule", "icon": "🏫", "items": ["Theorie", "Lehrer", "Lehrplan"]}, "cueRight": "Berufsschule",
    "footer": "Kammer (IHK / HWK) überwacht & prüft", "cueFooter": "zuständige"})
sc(1, "Ausbildungsvertrag", """Grundlage ist der *Ausbildungsvertrag*. Er wird vor Beginn abgeschlossen und muss *schriftlich*, inzwischen auch in Textform, festgehalten werden.
Bei Minderjährigen unterschreiben die *Eltern* mit. Drin stehen laut *Berufsbildungsgesetz*: Art und Ziel der Ausbildung, Beginn und *Dauer*,
die tägliche Arbeitszeit, die *Probezeit* von einem bis vier Monaten, die *Vergütung*, der *Urlaub* und die Voraussetzungen für eine Kündigung.""",
   {"type": "grid", "title": "📄 Inhalt des Ausbildungsvertrags (BBiG)", "items": [
       it("Art & Ziel der Ausbildung", "Art", icon="🎯"), it("Beginn & Dauer", "Dauer", icon="📅"), it("tägliche Arbeitszeit", "Arbeitszeit", icon="⏰"),
       it("Probezeit 1–4 Monate", "Probezeit", icon="🧪"), it("Vergütung", "Vergütung", icon="💶"), it("Urlaub & Kündigung", "Urlaub", icon="🏖️")]})
sc(1, "Rechte & Pflichten", """Aus dem Vertrag folgen *Rechte und Pflichten*. Das Recht des einen ist meist die Pflicht des anderen.
Lukas hat eine *Lernpflicht*, muss *Weisungen* befolgen, die *Berufsschule* besuchen, den *Ausbildungsnachweis* führen und Betriebsgeheimnisse für sich behalten.
Der Betrieb muss *ausbilden*, also nur Arbeiten geben, die zum Beruf gehören, die *Ausbildungsmittel* kostenlos stellen,
für Schule und Prüfung *freistellen*, die *Vergütung* zahlen und am Ende ein *Zeugnis* ausstellen.""",
   {"type": "compare", "left": {"title": "Pflichten Azubi", "icon": "👷", "items": ["lernen", "Weisungen befolgen", "Berufsschule besuchen", "Ausbildungsnachweis führen", "Schweigepflicht"]},
    "right": {"title": "Pflichten Betrieb", "icon": "🏭", "items": ["ausbilden (nur Berufsbezogenes)", "Ausbildungsmittel kostenlos", "freistellen für Schule & Prüfung", "Vergütung zahlen", "Zeugnis ausstellen"]}, "cueRight": "Betrieb"})
sc(1, "Konflikte & Ende", """Gibt es *Konflikte*, zum Beispiel weil Lukas nur Hof fegen muss, ist der Weg: erst das *Gespräch*, dann der *Ausbildungsberater* der Kammer,
dann der *Schlichtungsausschuss* und als letztes das *Arbeitsgericht*.
Die Ausbildung *endet* mit dem *Bestehen* der Abschlussprüfung oder mit Ablauf der Ausbildungszeit. Fällt man durch, kann man auf Wunsch *verlängern*,
bis zur nächsten Wiederholungsprüfung, höchstens ein Jahr.""",
   {"type": "flow", "title": "Konflikt in der Ausbildung", "items": [
       it("Gespräch", "Gespräch", icon="💬"), it("Ausbildungsberater (Kammer)", "Ausbildungsberater", icon="🧑‍⚖️"),
       it("Schlichtungsausschuss", "Schlichtungsausschuss", icon="🤝"), it("Arbeitsgericht", "Arbeitsgericht", icon="⚖️")],
    "note": "Ende: Bestehen der Prüfung · Verlängerung bei Nichtbestehen max. 1 Jahr", "cueNote": "endet"})
sc(1, "Kündigung Ausbildung", """Und die *Kündigung*? In der *Probezeit* können beide *jederzeit ohne Frist* kündigen. Nach der Probezeit kann der Betrieb nur noch
*fristlos aus wichtigem Grund* kündigen, zum Beispiel bei Diebstahl. Der Azubi kann außerdem mit *vier Wochen* Frist kündigen,
wenn er die Ausbildung *aufgibt* oder den *Beruf wechselt*. Nach der Probezeit muss die Kündigung *schriftlich* und mit *Gründen* erfolgen.""",
   {"type": "table", "title": "Kündigung des Ausbildungsvertrags", "head": ["Wann?", "Wer?", "Wie?"], "rows": [
       {"cells": ["in der Probezeit", "beide", "jederzeit, ohne Frist, ohne Grund"], "cue": "Probezeit"},
       {"cells": ["nach der Probezeit", "beide", "fristlos aus wichtigem Grund"], "cue": "fristlos"},
       {"cells": ["nach der Probezeit", "nur Azubi", "4 Wochen Frist bei Aufgabe / Berufswechsel"], "cue": "vier"},
       {"cells": ["immer nach Probezeit", "–", "schriftlich + mit Gründen"], "cue": "schriftlich"}]})

# =====================================================================
# Block 1 – KB I: Schutzvorschriften, Arbeitsvertrag
# =====================================================================
P = 1
sc(1, "Schutzvorschriften", """Weiter mit den *Schutzvorschriften*. Für Jugendliche unter achtzehn gilt das *Jugendarbeitsschutzgesetz*: höchstens *acht Stunden* am Tag
und *vierzig* in der Woche, an fünf Tagen. *Pausen*: dreißig Minuten ab viereinhalb Stunden, sechzig Minuten ab sechs Stunden.
Mindestens *zwölf Stunden* Freizeit zwischen zwei Arbeitstagen. *Urlaub*: unter sechzehn dreißig, unter siebzehn siebenundzwanzig und unter achtzehn fünfundzwanzig Werktage.""",
   {"type": "table", "title": "🧒 Jugendarbeitsschutzgesetz (unter 18)", "head": ["Regel", "Wert"], "rows": [
       {"cells": ["Arbeitszeit", "max. 8 Std./Tag · 40 Std./Woche · 5 Tage"], "cue": "acht"},
       {"cells": ["Pausen", "30 Min. ab 4,5 Std. · 60 Min. ab 6 Std."], "cue": "Pausen"},
       {"cells": ["Freizeit", "mind. 12 Std. zwischen zwei Arbeitstagen"], "cue": "zwölf"},
       {"cells": ["Urlaub", "<16: 30 · <17: 27 · <18: 25 Werktage"], "cue": "Urlaub"}]})
sc(1, "Schutzvorschriften", """Für Erwachsene gilt das *Arbeitszeitgesetz*: acht Stunden am Tag, ausnahmsweise *zehn*, wenn es im Schnitt wieder auf acht ausgeglichen wird.
*Pausen*: dreißig Minuten ab sechs Stunden, fünfundvierzig ab neun. *Elf Stunden* Ruhezeit. Der *Mindesturlaub* liegt bei vierundzwanzig Werktagen,
das sind zwanzig Arbeitstage bei einer Fünf-Tage-Woche. Beim *Mutterschutz* darf eine Frau sechs Wochen vor und acht Wochen nach der Geburt nicht arbeiten.
*Elternzeit* gibt es bis zu drei Jahre pro Kind. *Überwacht* wird das vom *Gewerbeaufsichtsamt*, der *Berufsgenossenschaft* und dem *Betriebsrat*.""",
   {"type": "grid", "title": "🛡️ Weitere Schutzgesetze", "items": [
       it("Arbeitszeit: 8 Std. (max. 10 mit Ausgleich)", "Arbeitszeitgesetz", icon="⏰"), it("Pausen: 30 Min. ab 6 Std. · 45 ab 9 Std.", "Pausen", icon="☕"),
       it("Ruhezeit: 11 Std.", "Ruhezeit", icon="🛌"), it("Urlaub: mind. 24 Werktage (= 20 Arbeitstage)", "Mindesturlaub", icon="🏖️"),
       it("Mutterschutz: 6 Wochen vor, 8 nach Geburt", "Mutterschutz", icon="🤰"), it("Elternzeit: bis 3 Jahre pro Kind", "Elternzeit", icon="👶")],
    "note": "Überwachung: Gewerbeaufsicht · Berufsgenossenschaft · Betriebsrat", "cueNote": "Überwacht"})
sc(1, "Arbeitsvertrag", """Nach der Ausbildung bewirbt sich Lukas. Im *Vorstellungsgespräch* gibt es *zulässige* und *unzulässige Fragen*.
Zulässig ist alles, was mit der *Arbeit* zu tun hat: Ausbildung, Noten, Berufserfahrung. *Unzulässig* sind Fragen nach *Schwangerschaft*,
*Religion*, *Partei* oder *Gewerkschaft*. Hier darf man sogar *lügen*, ohne dass es Folgen hat.""",
   {"type": "compare", "left": {"title": "Zulässig ✅", "icon": "🙂", "items": ["Ausbildung & Noten", "Berufserfahrung", "Kenntnisse (z. B. Führerschein, wenn nötig)"]},
    "right": {"title": "Unzulässig ❌", "icon": "🚫", "items": ["Schwangerschaft / Familienplanung", "Religion, Partei, Gewerkschaft", "➜ Recht zur Lüge!"]}, "cueRight": "Unzulässig"})
sc(1, "Arbeitsvertrag", """Der *Arbeitsvertrag* kommt durch zwei übereinstimmende Willenserklärungen zustande. Er ist grundsätzlich *formfrei*, aber der Arbeitgeber
muss die wichtigsten Bedingungen *schriftlich* nachweisen: Beginn, Tätigkeit, Arbeitsort, *Lohn*, Arbeitszeit, Urlaub und Kündigungsfristen.
Die *Pflichten*: Der Arbeitnehmer hat eine *Arbeitspflicht* und eine *Treuepflicht*, also zum Beispiel Verschwiegenheit.
Der Arbeitgeber hat eine *Vergütungspflicht*, eine *Fürsorgepflicht*, also für Sicherheit sorgen, und muss Urlaub gewähren und ein Zeugnis ausstellen.""",
   {"type": "compare", "left": {"title": "Arbeitnehmer", "icon": "👷", "items": ["Arbeitspflicht", "Treuepflicht (Verschwiegenheit, kein Wettbewerb)", "Weisungen befolgen"]},
    "right": {"title": "Arbeitgeber", "icon": "🏢", "items": ["Vergütungspflicht", "Fürsorgepflicht (Sicherheit)", "Urlaub & Zeugnis"]}, "cueRight": "Arbeitgeber",
    "footer": "formfrei – aber wichtigste Bedingungen schriftlich nachweisen (Nachweisgesetz)", "cueFooter": "formfrei"})
sc(1, "Befristet / unbefristet", """Verträge können *unbefristet* oder *befristet* sein. Ein befristeter Vertrag *endet automatisch*, ohne Kündigung.
*Ohne Sachgrund* darf man höchstens *zwei Jahre* befristen und dabei bis zu dreimal verlängern. *Mit Sachgrund*, zum Beispiel als *Vertretung* bei Elternzeit,
geht es auch länger. Wichtig: Die Befristung muss *schriftlich* vereinbart sein, sonst gilt der Vertrag als unbefristet.""",
   {"type": "compare", "left": {"title": "Unbefristet", "icon": "♾️", "items": ["läuft bis zur Kündigung", "mehr Sicherheit", "Kündigungsschutz gilt"]},
    "right": {"title": "Befristet", "icon": "⏳", "items": ["endet automatisch", "ohne Sachgrund max. 2 Jahre, 3× verlängern", "mit Sachgrund (z. B. Vertretung) länger", "Befristung schriftlich!"]}, "cueRight": "befristeter"})

# =====================================================================
# Block 2 – KB I: Kündigung, Zeugnis, Betriebsrat, Tarif
# =====================================================================
P = 2
sc(1, "Kündigung", """Ein Arbeitsverhältnis endet durch *Kündigung*, *Aufhebungsvertrag*, Fristablauf oder Rente. Eine Kündigung muss immer *schriftlich* sein,
eine E-Mail oder WhatsApp reicht nicht. Die *ordentliche* Kündigung hält eine Frist ein: gesetzlich *vier Wochen* zum *Fünfzehnten* oder zum *Monatsende*.
Für den Arbeitgeber wird die Frist länger, je länger jemand im Betrieb ist, zum Beispiel nach fünf Jahren *zwei Monate* zum Monatsende.
In der Probezeit sind es *zwei Wochen*. Die *außerordentliche* Kündigung ist *fristlos* und braucht einen *wichtigen Grund*.""",
   {"type": "table", "title": "✉️ Kündigungsfristen (gesetzlich)", "head": ["Fall", "Frist"], "rows": [
       {"cells": ["Grundfrist (beide)", "4 Wochen zum 15. oder Monatsende"], "cue": "vier"},
       {"cells": ["Arbeitgeber nach 2 / 5 / 8 Jahren", "1 / 2 / 3 Monate zum Monatsende …"], "cue": "länger"},
       {"cells": ["Probezeit", "2 Wochen"], "cue": "Probezeit"},
       {"cells": ["außerordentlich", "fristlos – wichtiger Grund"], "cue": "außerordentliche"}],
    "note": "Kündigung immer schriftlich (keine E-Mail / WhatsApp)!", "cueNote": "schriftlich"})
sc(1, "Kündigungsschutz", """Dann gibt es den *allgemeinen Kündigungsschutz*. Er gilt, wenn der Betrieb *mehr als zehn* Mitarbeiter hat und man *länger als sechs Monate* dabei ist.
Dann muss eine Kündigung *sozial gerechtfertigt* sein: *personenbedingt*, zum Beispiel lange Krankheit, *verhaltensbedingt*, meist nach einer *Abmahnung*,
oder *betriebsbedingt*, zum Beispiel weil Aufträge wegfallen. Bei betriebsbedingten Kündigungen gibt es eine *Sozialauswahl*.
Wer sich wehren will, muss innerhalb von *drei Wochen* beim *Arbeitsgericht* klagen.""",
   {"type": "stairs", "title": "Allgemeiner Kündigungsschutz", "note": "gilt: Betrieb > 10 Mitarbeiter UND > 6 Monate beschäftigt", "cueNote": "zehn",
    "items": [it("personenbedingt", "personenbedingt", sub="z. B. lange Krankheit"), it("verhaltensbedingt", "verhaltensbedingt", sub="meist nach Abmahnung"),
              it("betriebsbedingt", "betriebsbedingt", sub="Sozialauswahl!"), it("Klage: 3 Wochen, Arbeitsgericht", "drei", sub="Kündigungsschutzklage")]})
sc(1, "Kündigungsschutz", """Der *besondere Kündigungsschutz* schützt bestimmte Gruppen noch stärker: *Schwangere* und Mütter, Menschen in *Elternzeit*,
*Schwerbehinderte*, Mitglieder des *Betriebsrats* und *Azubis* nach der Probezeit. Und: Gibt es einen Betriebsrat, muss er *vor jeder Kündigung angehört* werden,
sonst ist sie unwirksam.""",
   {"type": "grid", "title": "🛡️ Besonderer Kündigungsschutz", "items": [
       it("Schwangere & Mütter", "Schwangere", icon="🤰"), it("Elternzeit", "Elternzeit", icon="👶"), it("Schwerbehinderte", "Schwerbehinderte", icon="♿"),
       it("Betriebsrat", "Betriebsrats", icon="🗳️"), it("Azubis nach Probezeit", "Azubis", icon="👷"), it("Betriebsrat vorher anhören!", "angehört", icon="❗")]})
sc(1, "Arbeitszeugnis", """Beim Ende gibt es ein *Arbeitszeugnis*. Das *einfache* Zeugnis nennt nur Art und *Dauer* der Tätigkeit. Das *qualifizierte* Zeugnis bewertet zusätzlich
*Leistung* und *Führung*, also Verhalten. Ein Zeugnis muss *wahr* und *wohlwollend* sein. Deshalb gibt es eine *Zeugnissprache*:
„stets zu unserer vollsten Zufriedenheit“ ist eine *Eins*, „stets zu unserer vollen Zufriedenheit“ eine *Zwei*,
„zu unserer vollen Zufriedenheit“ eine *Drei* und „zu unserer Zufriedenheit“ nur noch eine *Vier*.""",
   {"type": "table", "title": "📜 Zeugnissprache", "head": ["Formulierung", "Note"], "rows": [
       {"cells": ["stets zu unserer vollsten Zufriedenheit", "1 – sehr gut"], "cue": "Eins"},
       {"cells": ["stets zu unserer vollen Zufriedenheit", "2 – gut"], "cue": "Zwei"},
       {"cells": ["zu unserer vollen Zufriedenheit", "3 – befriedigend"], "cue": "Drei"},
       {"cells": ["zu unserer Zufriedenheit", "4 – ausreichend"], "cue": "Vier"}],
    "note": "einfach = Art & Dauer · qualifiziert = + Leistung & Führung", "cueNote": "qualifizierte"})
sc(1, "Betriebsrat", """Weiter zur *Mitbestimmung*. Einen *Betriebsrat* kann man in Betrieben mit mindestens *fünf* ständigen Arbeitnehmern wählen, alle *vier Jahre*.
*Wählen* darf man ab sechzehn, *gewählt werden* ab achtzehn. Für junge Leute gibt es die *Jugend- und Auszubildendenvertretung*, kurz *JAV*.
Der Betriebsrat *überwacht*, ob Gesetze und Tarifverträge eingehalten werden, und vertritt die Interessen der Mitarbeiter.""",
   {"type": "grid", "title": "🗳️ Betriebsrat", "items": [
       it("ab 5 ständigen Arbeitnehmern", "fünf", icon="👥"), it("Wahl alle 4 Jahre", "vier", icon="📅"), it("wählen ab 16 · gewählt werden ab 18", "Wählen", icon="✅"),
       it("JAV für Jugendliche & Azubis", "JAV", icon="🧑‍🎓"), it("überwacht Gesetze & Tarifverträge", "überwacht", icon="🔍"), it("vertritt die Mitarbeiter", "vertritt", icon="📣")]})
sc(1, "Betriebsrat", """Ganz wichtig für die Prüfung sind die *drei Stufen* der Beteiligung. Stufe eins: das *Informationsrecht*, zum Beispiel über die *wirtschaftliche Lage*.
Stufe zwei: das *Mitwirkungsrecht*, also Anhörung und Beratung, zum Beispiel bei einer *Kündigung*. Der Betriebsrat kann widersprechen, aber nicht verhindern.
Stufe drei: die echte *Mitbestimmung*. Ohne Zustimmung geht nichts, zum Beispiel bei *Beginn und Ende* der Arbeitszeit, bei *Überstunden* oder beim *Urlaubsplan*.""",
   {"type": "stairs", "title": "Die 3 Stufen der Beteiligung", "items": [
       it("Information", "Informationsrecht", sub="z. B. wirtschaftliche Lage, Personalplanung"),
       it("Mitwirkung (Anhörung / Beratung)", "Mitwirkungsrecht", sub="z. B. Kündigung – Widerspruch möglich"),
       it("Mitbestimmung", "Mitbestimmung", sub="z. B. Arbeitszeit, Überstunden, Urlaubsplan – ohne Zustimmung nichts")]})
sc(1, "Tarifvertrag", """Löhne werden oft in *Tarifverträgen* geregelt. Die schließen *Gewerkschaften* und *Arbeitgeberverbände* ohne den Staat ab, das nennt man *Tarifautonomie*.
Es gibt drei Arten: Der *Entgelttarifvertrag* regelt die *Lohnhöhe* und läuft kurz, meist ein bis zwei Jahre. Der *Rahmenentgelttarifvertrag* regelt die *Lohngruppen*,
also wer wie eingestuft wird. Und der *Manteltarifvertrag* regelt die allgemeinen *Arbeitsbedingungen* wie Arbeitszeit, Urlaub und Zuschläge, er läuft am längsten.""",
   {"type": "table", "title": "Tarifvertragsarten", "head": ["Art", "regelt", "Laufzeit"], "rows": [
       {"cells": ["Entgelttarifvertrag", "Lohnhöhe", "kurz (1–2 Jahre)"], "cue": "Entgelttarifvertrag"},
       {"cells": ["Rahmenentgelttarifvertrag", "Lohngruppen / Eingruppierung", "mittel"], "cue": "Rahmenentgelttarifvertrag"},
       {"cells": ["Manteltarifvertrag", "Arbeitszeit, Urlaub, Zuschläge …", "lang"], "cue": "Manteltarifvertrag"}],
    "note": "Tarifautonomie: Gewerkschaften + Arbeitgeberverbände verhandeln ohne Staat", "cueNote": "Tarifautonomie"})

# =====================================================================
# Block 3 – KB I: Tarif-Ablauf, Sozialversicherung
# =====================================================================
P = 3
sc(1, "Tarifvertrag", """Der Tarifvertrag gilt bei *Tarifbindung*: Der Arbeitnehmer ist in der Gewerkschaft und der Arbeitgeber im Verband. Er legt *Mindestbedingungen* fest,
besser darf es immer sein. Und während der Laufzeit herrscht *Friedenspflicht*, also kein Streik.
Wie läuft eine *Tarifrunde* ab? Der alte Vertrag wird gekündigt, dann wird *verhandelt*. Scheitern die Verhandlungen, kommt oft eine *Schlichtung*.
Scheitert auch die, gibt es eine *Urabstimmung*: Mindestens *fünfundsiebzig Prozent* der Mitglieder müssen für den *Streik* stimmen.
Die Arbeitgeber können mit *Aussperrung* antworten. Gibt es eine Einigung, stimmen die Mitglieder noch einmal ab, hier reichen *fünfundzwanzig Prozent*.""",
   {"type": "flow", "title": "Ablauf einer Tarifrunde", "items": [
       it("Kündigung & Verhandlung", "verhandelt", icon="🤝"), it("Schlichtung", "Schlichtung", icon="🧑‍⚖️"), it("Urabstimmung ≥ 75 %", "Urabstimmung", icon="🗳️"),
       it("Streik ↔ Aussperrung", "Streik", icon="✊"), it("Einigung: 2. Urabstimmung ≥ 25 %", "Einigung", icon="✅")],
    "note": "Tarifbindung · Mindestbedingungen · Friedenspflicht während der Laufzeit", "cueNote": "Friedenspflicht"})
sc(1, "Sozialversicherung", """Jetzt zur *Sozialversicherung*. Als Arbeitnehmer oder Azubi bist du *pflichtversichert*. Es gibt *fünf Säulen*:
*Krankenversicherung*, *Pflegeversicherung*, *Rentenversicherung*, *Arbeitslosenversicherung* und *Unfallversicherung*.
Die Beiträge zahlen Arbeitnehmer und Arbeitgeber grundsätzlich *je zur Hälfte*. Ausnahme: Die *Unfallversicherung* zahlt der *Arbeitgeber allein*.""",
   {"type": "pillars", "title": "Die 5 Säulen der Sozialversicherung", "items": [
       it("Kranken", "Krankenversicherung", icon="🏥", sub="Krankenkassen"), it("Pflege", "Pflegeversicherung", icon="🧓", sub="Pflegekassen"),
       it("Renten", "Rentenversicherung", icon="👴", sub="Dt. Rentenversicherung"), it("Arbeitslosen", "Arbeitslosenversicherung", icon="📉", sub="Bundesagentur f. Arbeit"),
       it("Unfall", "Unfallversicherung", icon="🦺", sub="Berufsgenossenschaft")],
    "note": "Beiträge: AN + AG je zur Hälfte · Unfall: Arbeitgeber allein", "cueNote": "Hälfte"})
sc(1, "Sozialversicherung", """Was leisten die Versicherungen? Die *Krankenversicherung* zahlt Arzt, Medikamente und Krankenhaus, und ab der siebten Woche *Krankengeld*,
denn die ersten sechs Wochen zahlt der Arbeitgeber den Lohn weiter. Die *Pflegeversicherung* zahlt Pflegegeld. Die *Rentenversicherung* zahlt die *Altersrente*,
die *Erwerbsminderungsrente* und *Reha*. Die *Arbeitslosenversicherung* zahlt *Arbeitslosengeld* und Weiterbildung.
Die *Unfallversicherung* zahlt bei *Arbeitsunfällen*, *Wegeunfällen* und *Berufskrankheiten*.""",
   {"type": "table", "title": "Leistungen", "head": ["Versicherung", "Leistung (Beispiele)"], "rows": [
       {"cells": ["🏥 Kranken", "Arzt, Krankenhaus, Krankengeld ab 7. Woche"], "cue": "Krankenversicherung"},
       {"cells": ["🧓 Pflege", "Pflegegeld, Pflegesachleistungen"], "cue": "Pflegeversicherung"},
       {"cells": ["👴 Renten", "Altersrente, Erwerbsminderungsrente, Reha"], "cue": "Rentenversicherung"},
       {"cells": ["📉 Arbeitslosen", "Arbeitslosengeld, Weiterbildung, Vermittlung"], "cue": "Arbeitslosenversicherung"},
       {"cells": ["🦺 Unfall", "Arbeits- & Wegeunfall, Berufskrankheit"], "cue": "Unfallversicherung"}]})
sc(1, "Private Vorsorge", """Die gesetzliche Versicherung hat aber *Grenzen*. Deshalb braucht man private *Zusatzversicherungen*. Die *Berufsunfähigkeitsversicherung*,
weil die gesetzliche Erwerbsminderungsrente sehr niedrig ist. Gerade als Elektroniker kann ein Unfall das Berufsleben beenden.
Die *private Altersvorsorge*, weil die gesetzliche Rente später nicht reicht, das nennt man *Rentenlücke*.
Und die *Privathaftpflicht*, denn wer einem anderen einen Schaden zufügt, haftet unbegrenzt, und das ist gar nicht gesetzlich abgesichert.""",
   {"type": "grid", "title": "➕ Private Zusatzversicherungen", "items": [
       it("Berufsunfähigkeit – gesetzliche Rente zu gering", "Berufsunfähigkeitsversicherung", icon="🦽"),
       it("private Altersvorsorge – Rentenlücke schließen", "Altersvorsorge", icon="🐷"),
       it("Privathaftpflicht – Schäden an anderen", "Privathaftpflicht", icon="🛡️")]})

# =====================================================================
# Block 4 – KB I: Lohnabrechnung, Steuer, Prüfungs-Check KB I
# =====================================================================
P = 4
sc(1, "Lohnabrechnung", """Jetzt rechnen wir: die *Lohnabrechnung*. Lukas verdient im Zeitlohn, also Stundenlohn mal Stunden, plus Zuschläge. Das ist sein *Bruttolohn*.
Davon gehen *Steuern* ab: die *Lohnsteuer*, eventuell *Kirchensteuer*, in Baden-Württemberg acht Prozent der Lohnsteuer, und meist kein Solidaritätszuschlag mehr.
Dazu kommen die *Sozialversicherungsbeiträge*, also sein Arbeitnehmeranteil. Was übrig bleibt, ist der *Nettolohn*.
Gehen noch Abzüge wie die Sparrate für *vermögenswirksame Leistungen* ab, erhält man den *Auszahlungsbetrag*.""",
   {"type": "ledger", "title": "💶 Lohnabrechnung (Beispielwerte)", "rows": [
       {"label": "Bruttolohn (160 Std. × 18 €)", "amount": 2880, "cue": "Bruttolohn"},
       {"label": "− Lohnsteuer", "amount": -260, "cue": "Lohnsteuer"},
       {"label": "− Kirchensteuer (8 % der LSt)", "amount": -20.8, "cue": "Kirchensteuer"},
       {"label": "− Sozialversicherung (AN-Anteil ca. 21 %)", "amount": -604.8, "cue": "Sozialversicherungsbeiträge"},
       {"label": "= Nettolohn", "amount": None, "cue": "Nettolohn", "total": True},
       {"label": "− VL-Sparrate", "amount": -40, "cue": "vermögenswirksame"},
       {"label": "= Auszahlungsbetrag", "amount": None, "cue": "Auszahlungsbetrag", "total": True}],
    "note": "Die aktuellen Prozentsätze stehen in der Prüfung meist in der Anlage.", "cueNote": "Auszahlungsbetrag"})
sc(1, "Steuererklärung", """Am Jahresende kann Lukas eine *Einkommensteuererklärung* machen, mit der *Anlage N* für nichtselbstständige Arbeit. Oft gibt es Geld zurück.
Das Prinzip: Vom Bruttoarbeitslohn zieht man die *Werbungskosten* ab, das sind Kosten für den Beruf, zum Beispiel die *Fahrtkosten* zur Arbeit über die *Entfernungspauschale*,
Arbeitskleidung, Werkzeug, Fachbücher oder Fortbildungen. Mindestens wird der *Pauschbetrag* von zwölfhundertdreißig Euro abgezogen.
Dann kommen die *Sonderausgaben*, zum Beispiel *Versicherungsbeiträge*, Kirchensteuer und Spenden. Am Ende steht das *zu versteuernde Einkommen*.""",
   {"type": "ledger", "title": "🧾 Einkommensteuererklärung (Anlage N)", "plain": True, "rows": [
       {"label": "Bruttoarbeitslohn", "text": "", "cue": "Bruttoarbeitslohn"},
       {"label": "− Werbungskosten", "text": "Fahrtkosten, Arbeitsmittel, Fortbildung · mind. 1.230 € Pauschbetrag", "cue": "Werbungskosten"},
       {"label": "= Einkünfte", "text": "", "cue": "Pauschbetrag", "total": True},
       {"label": "− Sonderausgaben", "text": "Versicherungen, Kirchensteuer, Spenden", "cue": "Sonderausgaben"},
       {"label": "= zu versteuerndes Einkommen", "text": "", "cue": "versteuernde", "total": True}],
    "note": "Fahrtkosten: einfache Strecke (km) × Arbeitstage × Pauschale je km (Wert steht in der Aufgabe)", "cueNote": "Entfernungspauschale"})
sc(1, "Prüfungs-Check KB I", """Kurzer *Prüfungs-Check* für Kompetenzbereich eins. Du solltest können: die *duale Ausbildung* und den *Ausbildungsvertrag* erklären,
die *Schutzgesetze* anwenden, *Kündigungsfristen* und *Kündigungsschutz* prüfen, ein *Zeugnis* lesen, die *drei Stufen* der Mitbestimmung zuordnen,
*Tarifverträge* und *Arbeitskampf* erklären, die *fünf Säulen* der Sozialversicherung nennen und eine *Lohnabrechnung* rechnen.""",
   {"type": "exam", "items": [
       it("Duale Ausbildung, Ausbildungsvertrag, Rechte & Pflichten", "duale"),
       it("Schutzgesetze (JArbSchG, ArbZG, Urlaub, Mutterschutz)", "Schutzgesetze"),
       it("Kündigungsfristen & Kündigungsschutz, Zeugnis", "Kündigungsfristen"),
       it("Betriebsrat: 3 Stufen · Tarifverträge & Arbeitskampf", "drei"),
       it("Sozialversicherung: 5 Säulen · Lohnabrechnung & Steuer", "fünf")]})

# =====================================================================
# Block 5 – KB II: Rechtsgeschäfte, Kaufvertrag, Störungen
# =====================================================================
P = 5
sc(2, "Kompetenzbereich II", """Kompetenzbereich zwei: Als *Konsument* rechtliche Bestimmungen anwenden.""",
   {"type": "topic", "n": 2, "label": "KOMPETENZBEREICH II", "title": "Konsument & Recht", "icon": "🛒"})
sc(2, "Rechtsgeschäfte", """Alles beginnt mit der *Willenserklärung*: Jemand äußert seinen Willen, eine Rechtsfolge herbeizuführen. Bei *einseitigen* Rechtsgeschäften reicht eine Willenserklärung,
zum Beispiel bei einer *Kündigung* oder einem *Testament*. *Zweiseitige* Rechtsgeschäfte sind *Verträge*: Es braucht zwei übereinstimmende Willenserklärungen,
zum Beispiel beim *Kaufvertrag*.""",
   {"type": "compare", "left": {"title": "einseitig", "icon": "☝️", "items": ["1 Willenserklärung", "Kündigung", "Testament"]},
    "right": {"title": "zweiseitig = Vertrag", "icon": "🤝", "items": ["2 übereinstimmende Willenserklärungen", "Kaufvertrag", "Mietvertrag, Arbeitsvertrag"]}, "cueRight": "Zweiseitige"})
sc(2, "Rechts- & Geschäftsfähigkeit", """*Rechtsfähigkeit* heißt: Träger von Rechten und Pflichten sein, das ist jeder Mensch ab der *Geburt*. *Geschäftsfähigkeit* heißt: selbst wirksam Verträge schließen.
Unter *sieben* Jahren ist man *geschäftsunfähig*, Verträge sind *nichtig*. Von sieben bis siebzehn ist man *beschränkt geschäftsfähig*: Verträge sind *schwebend unwirksam*,
bis die Eltern zustimmen. Ausnahmen: der *Taschengeldparagraf* und Geschenke, die nur Vorteile bringen. Ab *achtzehn* ist man *voll geschäftsfähig*.""",
   {"type": "stairs", "title": "Geschäftsfähigkeit", "note": "Rechtsfähigkeit: ab Geburt (Träger von Rechten & Pflichten)", "cueNote": "Rechtsfähigkeit",
    "items": [it("0–6 Jahre: geschäftsunfähig", "geschäftsunfähig", sub="Verträge nichtig"),
              it("7–17 Jahre: beschränkt geschäftsfähig", "beschränkt", sub="schwebend unwirksam · Ausnahme: Taschengeld, nur Vorteile"),
              it("ab 18: voll geschäftsfähig", "achtzehn", sub="Verträge voll wirksam")]})
sc(2, "Form, nichtig, anfechtbar", """Verträge sind grundsätzlich *formfrei*. Manche brauchen aber eine *Form*, als *Beweis* und zum Schutz vor Übereilung: *Schriftform* zum Beispiel bei der Kündigung,
*notarielle Beurkundung* beim *Grundstückskauf*. Und: *Nichtig*, also von Anfang an ungültig, sind Geschäfte von Geschäftsunfähigen, bei *Formfehlern*,
bei Verstößen gegen Gesetz oder gute Sitten, wie *Wucher*, und Scherzgeschäfte. *Anfechtbar*, also erst gültig, aber rückgängig zu machen,
sind Geschäfte aus *Irrtum*, durch *arglistige Täuschung* oder *Drohung*.""",
   {"type": "compare", "left": {"title": "nichtig", "icon": "❌", "items": ["von Anfang an ungültig", "Geschäftsunfähige", "Formfehler", "Gesetz / gute Sitten (Wucher)", "Scherzgeschäft"]},
    "right": {"title": "anfechtbar", "icon": "⚠️", "items": ["gültig, bis angefochten", "Irrtum (Inhalt / Erklärung)", "arglistige Täuschung", "widerrechtliche Drohung"]}, "cueRight": "Anfechtbar",
    "footer": "Formvorschriften: Schriftform (Kündigung) · notariell (Grundstück)", "cueFooter": "Form"})
sc(2, "Kaufvertrag", """Der *Kaufvertrag* kommt durch *Antrag* und *Annahme* zustande. Achtung: Ein Schaufenster, Werbung oder ein Online-Shop sind noch *kein Antrag*,
sondern nur eine *Aufforderung*, ein Angebot zu machen. Wer einen Antrag macht, ist daran *gebunden*: unter Anwesenden nur sofort,
per Brief oder E-Mail so lange, wie man normalerweise mit einer Antwort rechnen kann. Die *Pflichten*: Der Verkäufer muss die Ware *mangelfrei übergeben*
und das *Eigentum* verschaffen. Der Käufer muss *zahlen* und die Ware *annehmen*.""",
   {"type": "flow", "title": "Kaufvertrag", "items": [
       it("Anpreisung (Werbung, Shop) = kein Antrag", "Schaufenster", icon="🪧"), it("Antrag", "Antrag", icon="📨"), it("Annahme", "Annahme", icon="✅"), it("Vertrag ➜ Pflichten", "Pflichten", icon="🤝")],
    "note": "Verkäufer: mangelfrei übergeben + Eigentum verschaffen · Käufer: zahlen + annehmen", "cueNote": "Verkäufer"})
sc(2, "Besitz & Eigentum", """Wichtig ist der Unterschied zwischen *Besitz* und *Eigentum*. Besitz ist die *tatsächliche* Herrschaft, also wer die Sache gerade hat.
Eigentum ist die *rechtliche* Herrschaft, also wem sie gehört. Beispiel: Leiht Lukas sich die Bohrmaschine vom Kollegen, ist er *Besitzer*, der Kollege bleibt *Eigentümer*.
Eigentum an beweglichen Sachen geht über durch *Einigung* und *Übergabe*. Beim *Eigentumsvorbehalt* bleibt die Ware Eigentum des Verkäufers, bis sie *vollständig bezahlt* ist.""",
   {"type": "compare", "left": {"title": "Besitz", "icon": "✋", "items": ["tatsächliche Herrschaft", "„Ich habe es.“", "z. B. geliehene Bohrmaschine"]},
    "right": {"title": "Eigentum", "icon": "📜", "items": ["rechtliche Herrschaft", "„Es gehört mir.“", "Übertragung: Einigung + Übergabe"]}, "cueRight": "Eigentum",
    "footer": "Eigentumsvorbehalt: gehört dem Verkäufer bis zur vollständigen Bezahlung", "cueFooter": "Eigentumsvorbehalt"})
sc(2, "Mangelhafte Lieferung", """Was, wenn etwas schiefgeht? Erste *Kaufvertragsstörung*: die *mangelhafte Lieferung*, zum Beispiel ist das neue Handy kaputt, es fehlt etwas, oder die falsche Ware kommt.
Dann hat der Käufer zuerst ein Recht auf *Nacherfüllung*: Er wählt *Reparatur* oder *Ersatzlieferung*. Erst wenn das scheitert, kann er *zurücktreten*,
den Preis *mindern* oder *Schadensersatz* verlangen. Die *Gewährleistung* beträgt *zwei Jahre* ab Übergabe.""",
   {"type": "stairs", "title": "Rechte bei mangelhafter Lieferung", "note": "Gewährleistung: 2 Jahre ab Übergabe", "cueNote": "Gewährleistung",
    "items": [it("1. Nacherfüllung (Vorrang!)", "Nacherfüllung", sub="Käufer wählt: Reparatur oder Ersatzlieferung"),
              it("2. danach: Rücktritt", "zurücktreten", sub="Geld zurück"), it("… oder Minderung", "mindern", sub="Preis senken"), it("… und / oder Schadensersatz", "Schadensersatz", sub="bei Verschulden")]})
sc(2, "Zahlungsverzug", """Zweite Störung: der *Zahlungsverzug*. Der Käufer zahlt nicht. In Verzug ist er nach einer *Mahnung*, sofort bei einem *festen Zahlungstermin*,
oder spätestens *dreißig Tage* nach Fälligkeit und Rechnung. Der Verkäufer kann dann *Zahlung* plus *Verzugszinsen* verlangen,
Schadensersatz wie Mahnkosten, und nach einer Nachfrist *zurücktreten*. Zahlt der Käufer immer noch nicht, folgt das *gerichtliche Mahnverfahren* mit *Mahnbescheid*.""",
   {"type": "flow", "title": "Zahlungsverzug", "items": [
       it("Fälligkeit", "Zahlungsverzug", icon="📅"), it("Mahnung / fester Termin / 30 Tage", "Mahnung", icon="⏰"),
       it("Zahlung + Verzugszinsen + Schadensersatz", "Verzugszinsen", icon="💶"), it("gerichtl. Mahnverfahren (Mahnbescheid)", "gerichtliche", icon="⚖️")]})
sc(2, "Verjährung", """Ansprüche gelten aber nicht ewig: die *Verjährung*. Die *regelmäßige* Verjährungsfrist beträgt *drei Jahre*. Sie beginnt am *Ende des Jahres*,
in dem der Anspruch entstanden ist. Beispiel: Eine Rechnung vom März zweitausendsechsundzwanzig verjährt erst mit Ablauf des einunddreißigsten Dezember zweitausendneunundzwanzig.
Danach kann der Schuldner die Zahlung *verweigern*.""",
   {"type": "timeline", "title": "⏳ Regelmäßige Verjährung: 3 Jahre ab Jahresende", "cue": "Beispiel",
    "points": ["März 2026: Anspruch entsteht", "31.12.2026: Frist beginnt", "31.12.2029: verjährt"]})

# =====================================================================
# Block 6 – KB II: Verbraucher, Zahlung, Geld, Schulden
# =====================================================================
P = 6
sc(2, "Verbraucherschutz", """Als Verbraucher bekommst du Hilfe bei der *Verbraucherberatung*: den *Verbraucherzentralen*, der *Stiftung Warentest* mit ihren Testberichten und Vergleichsportalen.
Beim *Fernabsatz*, also Kauf im Internet, am Telefon oder per Katalog, hast du ein *Widerrufsrecht* von *vierzehn Tagen* ab Erhalt der Ware, ohne Begründung.
Der Widerruf muss *erklärt* werden, nur zurückschicken reicht nicht. Ausnahmen sind zum Beispiel *individuell angefertigte* oder verderbliche Waren.""",
   {"type": "grid", "title": "🛡️ Verbraucherschutz", "items": [
       it("Verbraucherzentrale", "Verbraucherzentralen", icon="🏛️"), it("Stiftung Warentest", "Warentest", icon="🧪"), it("Vergleichsportale", "Vergleichsportale", icon="🔍"),
       it("Fernabsatz: 14 Tage Widerruf", "vierzehn", icon="📦"), it("Widerruf erklären!", "erklärt", icon="✉️"), it("Ausnahme: Maßanfertigung, Verderbliches", "individuell", icon="🚫")]})
sc(2, "AGB", """Fast jeder Vertrag hat *Allgemeine Geschäftsbedingungen*, kurz *AGB*, also das Kleingedruckte. Das sind *vorformulierte* Bedingungen für viele Verträge.
Sie gelten nur, wenn auf sie *hingewiesen* wurde und man sie lesen konnte. Persönliche Absprachen haben *Vorrang*. Und es gibt Schutzregeln:
*Überraschende Klauseln*, mit denen niemand rechnet, gelten nicht. Und die gesetzliche *Gewährleistung* von zwei Jahren darf bei neuen Sachen gegenüber Verbrauchern
*nicht verkürzt* werden.""",
   {"type": "board", "title": "📃 AGB – das Kleingedruckte", "items": [
       it("vorformulierte Bedingungen für viele Verträge", "vorformulierte", icon="📄"),
       it("gelten nur nach Hinweis + Möglichkeit zum Lesen", "hingewiesen", icon="👀"),
       it("persönliche Absprache hat Vorrang", "Vorrang", icon="🤝"),
       it("überraschende Klauseln sind unwirksam", "Überraschende", icon="❌", color="red"),
       it("Gewährleistung (2 Jahre, neue Ware) nicht verkürzbar", "Gewährleistung", icon="❌", color="red")]})
sc(2, "Girokonto & Zahlung", """Für den Zahlungsverkehr brauchst du ein *Girokonto*. Vergleiche die *Konditionen*: Kontoführungsgebühr, Kosten für die Karte, *Dispozinsen* und Geldautomaten.
Zahlen kannst du *bar*, per *Überweisung*, auch als *Dauerauftrag* für die Miete, per *Lastschrift*, mit der *Girocard*, bei der sofort abgebucht wird,
mit der *Kreditkarte*, bei der erst später abgerechnet wird, oder elektronisch, zum Beispiel mit *PayPal* oder dem Handy.
Welche Zahlungsform passt, hängt von der *Situation* ab: Miete per Dauerauftrag, Bäcker bar oder kontaktlos, im Ausland oft die Kreditkarte.""",
   {"type": "table", "title": "💳 Zahlungsformen", "head": ["Form", "passt z. B. für"], "rows": [
       {"cells": ["Bargeld", "Bäcker, kleine Beträge"], "cue": "bar"},
       {"cells": ["Überweisung / Dauerauftrag", "Rechnungen, Miete"], "cue": "Überweisung"},
       {"cells": ["Lastschrift", "Handyvertrag, Strom"], "cue": "Lastschrift"},
       {"cells": ["Girocard (sofort abgebucht)", "Einkauf im Laden"], "cue": "Girocard"},
       {"cells": ["Kreditkarte (später abgerechnet)", "Reisen, Ausland, online"], "cue": "Kreditkarte"},
       {"cells": ["PayPal / Handy", "Online-Shopping"], "cue": "PayPal"}]})
sc(2, "Geldanlage", """Wer *Geld anlegen* will, achtet auf drei Ziele: *Liquidität*, also wie schnell komme ich an mein Geld, *Rentabilität*, also wie viel Ertrag bringt es,
und *Sicherheit*. Das ist das *magische Dreieck*, magisch, weil man nie alle drei gleichzeitig maximal erreicht.
Beispiel *Termingeld*: fester Zins, feste Laufzeit, sehr *sicher*, aber während der Laufzeit nicht verfügbar und eher geringer Ertrag.
Beispiel *Aktienfonds*: viele Aktien in einem Topf, *höhere Ertragschancen*, jederzeit verkaufbar, aber mit *Kursrisiko*.""",
   {"type": "triangle", "corners": [["Sicherheit", "🛡️", "Sicherheit"], ["Liquidität", "💧", "Liquidität"], ["Rentabilität", "📈", "Rentabilität"]],
    "compare": [{"name": "Termingeld", "vals": ["hoch", "gering (Laufzeit)", "gering"], "cue": "Termingeld"}, {"name": "Aktienfonds", "vals": ["mittel (Kursrisiko)", "hoch", "hoch (Chance)"], "cue": "Aktienfonds"}]})
sc(2, "Kredit", """Für größere Anschaffungen nimmt man vielleicht einen *Verbraucherkredit*. Die Bank prüft die *Kreditwürdigkeit*: Einkommen, Ausgaben und die *Schufa*.
Der Vertrag muss *schriftlich* sein und unter anderem den *effektiven Jahreszins*, die Laufzeit und die Raten nennen. Man hat vierzehn Tage *Widerrufsrecht*.
Die Bank will *Sicherheiten*: Bei der *Sicherungsübereignung* wird die Bank Eigentümer, zum Beispiel vom Auto, Lukas bleibt Besitzer und fährt es weiter.
Bei der *Bürgschaft* haftet eine andere Person mit. Und bei der *Lohnabtretung* darf sich die Bank den pfändbaren Teil des Lohns direkt beim Arbeitgeber holen.""",
   {"type": "table", "title": "🏦 Kreditsicherheiten", "head": ["Sicherheit", "So funktioniert's"], "rows": [
       {"cells": ["Sicherungsübereignung", "Bank = Eigentümer, Kreditnehmer = Besitzer (z. B. Auto)"], "cue": "Sicherungsübereignung"},
       {"cells": ["Bürgschaft", "ein Dritter haftet mit, wenn nicht gezahlt wird"], "cue": "Bürgschaft"},
       {"cells": ["Lohnabtretung", "Bank holt pfändbaren Lohn direkt beim Arbeitgeber"], "cue": "Lohnabtretung"}],
    "note": "Vorher: Kreditwürdigkeit (Einkommen, Schufa) · schriftlich · effektiver Jahreszins · 14 Tage Widerruf", "cueNote": "Kreditwürdigkeit"})
sc(2, "Überschuldung", """Werden die Schulden zu groß, droht *Überschuldung*: Die Einnahmen reichen nicht mehr für die Ausgaben und Raten. Ursachen sind oft *Arbeitslosigkeit*,
Trennung, Krankheit oder zu viele Ratenkäufe. Was tun? Erstens einen *Haushaltsplan* machen. Zweitens zur kostenlosen *Schuldnerberatung*.
Und als letzter Schritt die *Verbraucherinsolvenz*: Nach einem Einigungsversuch und der *Wohlverhaltensphase* von *drei Jahren* gibt es die *Restschuldbefreiung*.""",
   {"type": "stairs", "title": "Wege aus der Überschuldung", "items": [
       it("Haushaltsplan", "Haushaltsplan", sub="Einnahmen und Ausgaben aufschreiben"), it("Schuldnerberatung", "Schuldnerberatung", sub="kostenlos, z. B. Caritas, Diakonie, Verbraucherzentrale"),
       it("Verbraucherinsolvenz", "Verbraucherinsolvenz", sub="Einigungsversuch ➜ Gericht ➜ 3 Jahre Wohlverhalten ➜ Restschuldbefreiung")]})
sc(2, "Prüfungs-Check KB II", """*Prüfungs-Check* Kompetenzbereich zwei: *Geschäftsfähigkeit* und nichtig oder anfechtbar unterscheiden, *Kaufvertrag* mit Antrag und Annahme,
*Besitz* und *Eigentum*, die Rechte bei *Mängeln* und *Zahlungsverzug*, die *Verjährung*, das *Widerrufsrecht* und die *AGB*,
*Zahlungsformen*, das *magische Dreieck* und die *Kreditsicherheiten*.""",
   {"type": "exam", "items": [
       it("Geschäftsfähigkeit · nichtig vs. anfechtbar · Form", "Geschäftsfähigkeit"),
       it("Kaufvertrag (Antrag/Annahme) · Besitz & Eigentum", "Kaufvertrag"),
       it("Mängel (Nacherfüllung zuerst!) · Zahlungsverzug · Verjährung 3 J.", "Mängeln"),
       it("Fernabsatz 14 Tage · AGB-Schutzregeln", "Widerrufsrecht"),
       it("Zahlungsformen · magisches Dreieck · Kreditsicherheiten", "Zahlungsformen")]})

# =====================================================================
# Block 7 – KB III: Markt, Preisbildung, Staat
# =====================================================================
P = 7
sc(3, "Kompetenzbereich III", """Kompetenzbereich drei: *Wirtschaftliches Handeln* in der Sozialen Marktwirtschaft.""",
   {"type": "topic", "n": 3, "label": "KOMPETENZBEREICH III", "title": "Markt & Wirtschaft", "icon": "📈"})
sc(3, "Markt & Marktformen", """Ein *Markt* ist der Ort, an dem *Angebot* und *Nachfrage* zusammentreffen, und dort bildet sich der *Preis*. Märkte unterscheidet man nach der Anzahl der Anbieter.
*Polypol*: viele Anbieter, viele Nachfrager, zum Beispiel Bäckereien oder ein Wochenmarkt. Keiner kann den Preis allein bestimmen.
*Angebotsoligopol*: wenige Anbieter, zum Beispiel Tankstellen oder Mobilfunk. Sie beobachten sich gegenseitig, oft gibt es einen *Preisführer*.
*Angebotsmonopol*: nur *ein* Anbieter, zum Beispiel das Schienennetz. Er kann den Preis weitgehend *selbst festlegen*.""",
   {"type": "table", "title": "Marktformen", "head": ["Marktform", "Anbieter", "Beispiel", "Verhalten"], "rows": [
       {"cells": ["Polypol", "viele", "Bäckereien, Wochenmarkt", "keiner bestimmt den Preis"], "cue": "Polypol"},
       {"cells": ["Angebotsoligopol", "wenige", "Tankstellen, Mobilfunk", "beobachten sich, Preisführer"], "cue": "Angebotsoligopol"},
       {"cells": ["Angebotsmonopol", "einer", "Schienennetz", "legt Preis selbst fest"], "cue": "Angebotsmonopol"}]})
sc(3, "Gleichgewichtspreis", """Im *Polypol* auf dem *vollkommenen Markt* bildet sich der *Gleichgewichtspreis*. Die *Nachfrage* sinkt, wenn der Preis steigt.
Das *Angebot* steigt, wenn der Preis steigt. Im *Schnittpunkt* sind beide gleich groß: Das ist der Gleichgewichtspreis mit der *Gleichgewichtsmenge*.
Ist der Preis *höher*, gibt es einen *Angebotsüberhang*, die Ware bleibt liegen und der Preis sinkt. Ist er *niedriger*, gibt es einen *Nachfrageüberhang*, und der Preis steigt.""",
   {"type": "chart", "mode": "basic", "cueEq": "Schnittpunkt", "cueOver": "höher", "cueUnder": "niedriger"})
sc(3, "Gleichgewichtspreis", """In der Prüfung bekommst du oft eine *Tabelle*. Zu jedem Preis stehen Angebot und Nachfrage. Du suchst die Zeile, in der *Angebot gleich Nachfrage* ist.
Hier zum Beispiel bei *drei Euro*: sechzig Stück werden angeboten und sechzig nachgefragt. Das ist der Gleichgewichtspreis, die Gleichgewichtsmenge ist sechzig.""",
   {"type": "table", "title": "📋 Gleichgewicht aus der Tabelle", "head": ["Preis", "Nachfrage", "Angebot", "Situation"], "rows": [
       {"cells": ["1 €", "100", "20", "Nachfrageüberhang"], "cue": "Tabelle"},
       {"cells": ["2 €", "80", "40", "Nachfrageüberhang"], "cue": "Preis"},
       {"cells": ["3 €", "60", "60", "✅ Gleichgewicht"], "cue": "drei", "hl": True},
       {"cells": ["4 €", "40", "80", "Angebotsüberhang"], "cue": "drei"},
       {"cells": ["5 €", "20", "100", "Angebotsüberhang"], "cue": "drei"}]})
sc(3, "Änderungen", """Was passiert bei Änderungen? *Steigt die Nachfrage*, zum Beispiel nach Eis bei einer Hitzewelle, verschiebt sich die Nachfragekurve nach rechts: *Preis und Menge steigen*.
*Steigt das Angebot*, zum Beispiel bei einer Rekordernte, verschiebt sich die Angebotskurve nach rechts: Der *Preis sinkt*, die *Menge steigt*.
Und umgekehrt: Sinkt das Angebot, etwa bei einer Missernte, *steigt der Preis*.""",
   {"type": "chart", "mode": "shift", "cueDemand": "Nachfrage", "cueSupply": "Angebot"})
sc(3, "Staat & Soziale Marktwirtschaft", """Der freie Markt hat *Nachteile*: Preise können für manche zu hoch werden, große Firmen werden zu mächtig, und die Umwelt wird nicht geschützt.
Deshalb greift der Staat ein. Mit einem *Höchstpreis* unter dem Gleichgewichtspreis schützt er die *Verbraucher*, zum Beispiel bei Mieten.
Folge: Nachfrageüberhang, oft Schwarzmarkt. Mit einem *Mindestpreis* über dem Gleichgewichtspreis schützt er die *Anbieter*, zum Beispiel den *Mindestlohn* als Mindestpreis für Arbeit.
Folge: Angebotsüberhang.""",
   {"type": "compare", "left": {"title": "Höchstpreis", "icon": "⬇️", "items": ["liegt UNTER dem Gleichgewichtspreis", "schützt Verbraucher (z. B. Mieten)", "Folge: Nachfrageüberhang, Schwarzmarkt"]},
    "right": {"title": "Mindestpreis", "icon": "⬆️", "items": ["liegt ÜBER dem Gleichgewichtspreis", "schützt Anbieter (z. B. Mindestlohn)", "Folge: Angebotsüberhang"]}, "cueRight": "Mindestpreis"})
sc(3, "Staat & Soziale Marktwirtschaft", """So entsteht die *Soziale Marktwirtschaft*: grundsätzlich freier Markt, aber der Staat sorgt für *sozialen Ausgleich*. Ihre *Instrumente*:
*Sozialpolitik*, zum Beispiel Sozialversicherung, Bürgergeld und Kindergeld. *Einkommenspolitik*, zum Beispiel die *progressive* Einkommensteuer und der Mindestlohn.
*Wettbewerbspolitik*, zum Beispiel das *Kartellverbot*, überwacht vom Bundeskartellamt. Und *Umweltpolitik*, zum Beispiel der *CO₂-Preis* nach dem Verursacherprinzip.""",
   {"type": "grid", "title": "Instrumente der Sozialen Marktwirtschaft", "items": [
       it("Sozialpolitik – Sozialversicherung, Bürgergeld, Kindergeld", "Sozialpolitik", icon="🤲"),
       it("Einkommenspolitik – progressive Steuer, Mindestlohn", "Einkommenspolitik", icon="💶"),
       it("Wettbewerbspolitik – Kartellverbot, Bundeskartellamt", "Wettbewerbspolitik", icon="⚖️"),
       it("Umweltpolitik – CO₂-Preis, Verursacherprinzip", "Umweltpolitik", icon="🌱")]})

# =====================================================================
# Block 8 – KB III: Inflation, BIP, Konjunktur, Check
# =====================================================================
P = 8
sc(3, "Preisindex & Inflation", """Wie misst man, ob das Leben teurer wird? Mit dem *Verbraucherpreisindex*. Das Statistische Bundesamt beobachtet einen *Warenkorb*
mit Hunderten Waren und Dienstleistungen, gewichtet nach ihrem Anteil am Haushaltsbudget. Ein *Basisjahr* wird gleich hundert gesetzt.
Die *Inflationsrate* ist die Veränderung dieses Index in Prozent zum Vorjahr. Steigen die Preise, sinkt die *Kaufkraft*: Für denselben Euro bekommst du weniger.""",
   {"type": "grid", "title": "🧺 Verbraucherpreisindex", "items": [
       it("Warenkorb mit Hunderten Gütern", "Warenkorb", icon="🧺"), it("gewichtet (Wägungsschema)", "gewichtet", icon="⚖️"), it("Basisjahr = 100", "Basisjahr", icon="💯"),
       it("Inflationsrate = Veränderung in % zum Vorjahr", "Inflationsrate", icon="📈"), it("Preise ↑ ➜ Kaufkraft ↓", "Kaufkraft", icon="💸")]})
sc(3, "Reallohn", """Und was heißt das für deinen Lohn? Der *Nominallohn* ist die Zahl auf der Abrechnung. Der *Reallohn* zeigt, was du dir davon *wirklich kaufen* kannst.
Faustregel: Reallohnänderung gleich Nominallohnänderung minus Inflationsrate. Bekommt Lukas *fünf Prozent* mehr Lohn, die Inflation liegt aber bei *drei Prozent*,
dann ist sein Reallohn nur um etwa *zwei Prozent* gestiegen. Ist die Inflation höher als die Lohnerhöhung, *sinkt* der Reallohn.""",
   {"type": "formula2", "parts": [["Nominallohn + 5 %", "#2563eb", "fünf"], ["−", "#1f2937", "drei"], ["Inflation 3 %", "#dc2626", "drei"], ["=", "#1f2937", "zwei"], ["Reallohn ≈ + 2 %", "#16a34a", "zwei"]],
    "note": "Inflation > Lohnerhöhung ➜ Reallohn sinkt", "cueNote": "sinkt"})
sc(3, "Inflation & Deflation", """Die *Ursachen* einer Inflation, ohne Geldmenge betrachtet: *Nachfragesog*, die Nachfrage ist größer als das Angebot. *Kostendruck*, zum Beispiel teure Energie
oder steigende Löhne, die als Preise weitergegeben werden, bis zur *Lohn-Preis-Spirale*. Und *Gewinndruck* durch Firmen mit Marktmacht.
*Folgen*: Sparer verlieren, Schuldner gewinnen, Menschen mit festem Einkommen werden ärmer. Bei der *Deflation* sinken die Preise allgemein.
Klingt gut, ist aber gefährlich: Die Leute *warten* mit dem Kauf, Firmen verkaufen weniger, entlassen Mitarbeiter, eine *Abwärtsspirale*.""",
   {"type": "compare", "left": {"title": "Inflation", "icon": "🎈", "items": ["Ursachen: Nachfragesog, Kostendruck, Gewinndruck", "Lohn-Preis-Spirale", "Folgen: Sparer verlieren, Schuldner gewinnen"]},
    "right": {"title": "Deflation", "icon": "🧊", "items": ["Preise sinken allgemein", "Kaufzurückhaltung (warten)", "Umsatz ↓ ➜ Entlassungen ➜ Abwärtsspirale"]}, "cueRight": "Deflation"})
sc(3, "Bruttoinlandsprodukt", """Die wichtigste Messgröße der Wirtschaft ist das *Bruttoinlandsprodukt*, kurz *BIP*: der Wert aller Waren und Dienstleistungen, die in einem Jahr
im *Inland* hergestellt werden. Das *nominale* BIP rechnet mit aktuellen Preisen. Das *reale* BIP ist *preisbereinigt* und zeigt das *echte Wachstum*.
Als *Wohlstandsindikator* hat es Schwächen: *Hausarbeit*, *Ehrenamt* und *Schwarzarbeit* fehlen, *Umweltschäden* können es sogar erhöhen, und es sagt nichts über die *Verteilung* oder die Zufriedenheit.""",
   {"type": "compare", "left": {"title": "BIP", "icon": "🏭", "items": ["Wert aller Güter & Dienstleistungen eines Jahres im Inland", "nominal: aktuelle Preise", "real: preisbereinigt = echtes Wachstum"]},
    "right": {"title": "Kritik als Wohlstandsmaß", "icon": "🤔", "items": ["Hausarbeit, Ehrenamt, Schwarzarbeit fehlen", "Umweltschäden erhöhen es", "Verteilung & Zufriedenheit fehlen"]}, "cueRight": "Wohlstandsindikator"})
sc(3, "Konjunktur", """Die Wirtschaft wächst nicht gleichmäßig, sie schwankt: die *Konjunktur*. Der idealtypische Verlauf hat vier Phasen: *Aufschwung*, *Hochkonjunktur* oder Boom,
*Abschwung* und *Tiefstand*, auch Depression genannt. Woran erkennt man die Phase? An *Indikatoren*: Die *Auftragseingänge* sind ein *Frühindikator*, sie zeigen die Zukunft.
Das *BIP* zeigt die Gegenwart. Und die *Arbeitslosenquote* ist ein *Spätindikator*, sie reagiert erst verzögert.""",
   {"type": "cycle", "cues": ["Aufschwung", "Hochkonjunktur", "Abschwung", "Tiefstand"],
    "ind": [it("Auftragseingänge = Frühindikator", "Auftragseingänge"), it("BIP = Präsenzindikator", "BIP"), it("Arbeitslosenquote = Spätindikator", "Arbeitslosenquote")]})
sc(3, "Konjunkturpolitik", """Der Staat steuert *antizyklisch*, also gegen den Trend. Im *Abschwung* erhöht er die *Staatsnachfrage*, baut zum Beispiel Straßen und Schulen,
und *senkt* die *Einkommensteuer*. Dann haben die Leute mehr Netto und kaufen mehr. Im *Boom* macht er das Gegenteil.
Probleme: *Staatsschulden*, die Wirkung kommt oft *zu spät*, und die Leute *sparen* das Geld vielleicht, statt es auszugeben.
Für dich heißt eine Steuersenkung: mehr Netto vom Brutto.""",
   {"type": "compare", "left": {"title": "im Abschwung", "icon": "📉", "items": ["Staatsnachfrage erhöhen (Straßen, Schulen)", "Einkommensteuer senken ➜ mehr Netto ➜ mehr Konsum"]},
    "right": {"title": "Probleme", "icon": "⚠️", "items": ["Staatsschulden steigen", "Wirkung kommt zu spät", "Leute sparen statt kaufen"]}, "cueRight": "Probleme",
    "footer": "antizyklisch: gegen den Trend steuern (im Boom: Ausgaben runter, Steuern rauf)", "cueFooter": "antizyklisch"})
sc(3, "Prüfungs-Check KB III", """*Prüfungs-Check* Kompetenzbereich drei: *Marktformen* unterscheiden, den *Gleichgewichtspreis* aus Tabelle und Grafik bestimmen, *Verschiebungen* erklären,
*Höchst- und Mindestpreis*, die *Instrumente* der Sozialen Marktwirtschaft, *Inflation* und *Reallohn*, das *BIP* kritisch beurteilen und den *Konjunkturzyklus* mit seinen *Indikatoren*.""",
   {"type": "exam", "items": [
       it("Marktformen · Gleichgewichtspreis (Tabelle + Grafik)", "Marktformen"),
       it("Verschiebungen von Angebot und Nachfrage", "Verschiebungen"),
       it("Höchst-/Mindestpreis · Soziale Marktwirtschaft (4 Instrumente)", "Höchst"),
       it("Preisindex, Inflation, Reallohn · BIP nominal/real + Kritik", "Inflation"),
       it("Konjunktur: 4 Phasen, Indikatoren, antizyklische Politik", "Konjunkturzyklus")]})

# =====================================================================
# Block 9 – KB IV kompakt + Schluss
# =====================================================================
P = 9
sc(4, "Kompetenzbereich IV", """Und zum Schluss Kompetenzbereich vier: Entscheidungen bei der *Selbstständigkeit*. Dazu hast du schon ein eigenes, ausführliches Video, hier die *Kurzfassung*.""",
   {"type": "topic", "n": 4, "label": "KOMPETENZBEREICH IV", "title": "Selbstständigkeit", "icon": "🧑‍💼"})
sc(4, "Selbstständigkeit", """Selbstständig ist, wer ein *eigenes Unternehmen* auf eigene Rechnung und eigenes *Risiko* führt. *Motive*: eigener Chef, eigene Ideen, mehr verdienen.
Man braucht *Unternehmereigenschaften*, immer mit Begründung, zum Beispiel *Belastbarkeit*, weil man viel arbeitet. *Chancen und Risiken* merkst du dir mit
*Geld*, *Zeit*, *Verantwortung*, *Absicherung*: zum Beispiel mehr verdienen, aber kein festes Gehalt, und alle Versicherungen selbst zahlen.""",
   {"type": "balance", "row": 9, "summaryMode": True, "cues": ["Geld", "Zeit", "Verantwortung", "Absicherung"]})
sc(4, "Geschäftsplan & Standort", """Der *Geschäftsplan* ist ein schriftliches Konzept für die Gründung. *Funktion*: alles durchdenken und einen Kredit bekommen. *Adressat* ist vor allem die *Bank*.
Der *Standort* entscheidet über Erfolg. *Standortfaktoren* wie Kundennähe, Kosten und Erreichbarkeit bewertest du in einer *Punktetabelle*, passend zur Geschäftsidee.""",
   {"type": "sum", "n": 4, "title": "Geschäftsplan & Standort", "items": [
       it("Geschäftsplan = schriftliches Konzept (Idee, Markt, Konkurrenz, Standort, Rechtsform, Finanzen)", "Geschäftsplan"),
       it("Funktion: durchdenken + Kredit · Adressat: v. a. Bank", "Funktion"),
       it("Standortfaktoren: Kunden, Konkurrenz, Kosten, Erreichbarkeit, Größe", "Standortfaktoren"),
       it("Punktetabelle ➜ meiste Punkte + Begründung", "Punktetabelle")]})
sc(4, "Rechtsformen", """Bei den *Rechtsformen* vergleichst du *Mindestkapital*, *Haftung* und *Geschäftsführung*. *Einzelunternehmen* und *GbR*: kein Mindestkapital, aber man haftet *privat*.
*GmbH* mit fünfundzwanzigtausend Euro und *UG* ab einem Euro: Das *Privatvermögen* ist *geschützt*.""",
   {"type": "formtable", "cueGroup1": "Einzelunternehmen", "cueGroup2": "GmbH"})
sc(4, "Kapitalbedarfsplan", """Und der *Kapitalbedarfsplan*: Investitionen, erste Waren, Gründungskosten, laufende Kosten und *Lebenshaltung* für einige Monate, plus *Reserve*.
Monatliche Kosten *mal die Monate*. Und die Formel: *Kapitalbedarf minus Eigenkapital gleich Kredit*.""",
   {"type": "formula", "cues": ["Kapitalbedarf", "Eigenkapital", "Kredit"], "explain": [it("monatliche Kosten × Monate!", "Monatliche"), it("Lebenshaltung + Reserve nicht vergessen", "Lebenshaltung")]})
sc(5, "Geschafft!", """Das waren alle vier Kompetenzbereiche. Mein Tipp: Schau dir vor der Prüfung die *Prüfungs-Checks* noch einmal an, und rechne die *Lohnabrechnung*,
den *Gleichgewichtspreis* und den *Kapitalbedarfsplan* einmal selbst durch. Viel Erfolg bei deiner Abschlussprüfung. Du schaffst das!""",
   {"type": "title", "title": "Viel Erfolg! 💪", "subtitle": "Prüfungs-Checks wiederholen · Rechnungen selbst üben", "badge": "WiSo · KB I – KB IV"})

# kleine Blöcke zusammenlegen (spart TTS-Anfragen)
MERGE = {0: 0, 1: 1, 2: 2, 3: 3, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 7}
for x in S:
    x["part"] = MERGE[x["part"]]
out = {"title": "WiSo komplett – KB I bis KB IV", "sentences": S}
p = Path(__file__).resolve().parent.parent / "src" / "wiso_all" / "script.json"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
words = sum(len(s["text"].split()) for s in S)
print(f"{len(S)} Szenen, {words} Wörter, ~{words / 150:.0f} min")
for k in range(8):
    print("Block", k, sum(len(s["text"].split()) for s in S if s["part"] == k), "Wörter")
