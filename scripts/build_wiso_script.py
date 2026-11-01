#!/usr/bin/env python3
"""Baut src/wiso/script.json: das komplette Lernvideo „KB IV: Selbstständigkeit“ (AP2 WiSo).

Jede Szene: part (Sprachaufnahme-Block), topic (0 Intro, 1-4 Themen, 5 Zusammenfassung),
step (Unterrichtsphase), text (gesprochen, *Wort* = hervorgehoben), v (Visualisierung).
Items in v erscheinen, sobald ihr "cue"-Wort gesprochen wird.
"""
import json
from pathlib import Path

S = []


def sc(part, topic, step, text, v):
    S.append({"part": part, "topic": topic, "step": step, "text": " ".join(text.split()), "v": v})


def it(text, cue, **kw):
    return {"text": text, "cue": cue, **kw}


# =====================================================================
# PART 0 – Einstieg + Thema 1 (Teil 1)
# =====================================================================
P = 0
sc(P, 0, "intro", """Hallo und willkommen! Heute machen wir zusammen den Kompetenzbereich vier:
*Entscheidungen* im Rahmen einer beruflichen *Selbstständigkeit*. In einer Woche schreibst du deine *AP2*,
und genau diese vier Themen können dort drankommen.""",
   {"type": "title", "title": "Kompetenzbereich IV", "subtitle": "Entscheidungen im Rahmen einer beruflichen Selbstständigkeit", "badge": "AP2 · WiSo"})
sc(P, 0, "intro", """Wir gehen in vier Schritten vor. Erstens: Was bedeutet *Selbstständigkeit*, und passt das überhaupt zu mir?
Zweitens: der *Geschäftsplan* und der richtige *Standort*. Drittens: die *Rechtsformen*.
Und viertens: der *Kapitalbedarfsplan*, also wie viel Geld ich zum Gründen brauche.""",
   {"type": "roadmap", "cues": ["Selbstständigkeit", "Geschäftsplan", "Rechtsformen", "Kapitalbedarfsplan"]})
sc(P, 0, "intro", """Damit das nicht trocken bleibt, begleitet uns dabei Lukas. Lukas ist, genau wie du,
*Elektroniker für Betriebstechnik*. Er hat ein paar Jahre Berufserfahrung und denkt sich:
Eigentlich könnte ich auch meinen *eigenen Betrieb* aufmachen. Bei jedem Thema schauen wir,
welche Entscheidung Lukas als Nächstes treffen muss.""",
   {"type": "lukas", "pose": "think", "bubble": "Mein eigener Betrieb? ⚡", "items": [
       it("Elektroniker für Betriebstechnik", "Elektroniker", icon="🧑‍🔧"),
       it("ein paar Jahre Berufserfahrung", "Berufserfahrung", icon="🛠️"),
       it("Idee: eigener Elektrobetrieb", "eigenen", icon="💡")]})
sc(P, 0, "intro", """Am Ende bekommst du außerdem eine komplette *Zusammenfassung* aller vier Themen,
wie ein Spickzettel zum Wiederholen. Also: Stift raus, los geht's!""",
   {"type": "board", "title": "So lernst du mit diesem Video", "items": [
       it("4 Themen Schritt für Schritt", "Zusammenfassung", icon="🪜"),
       it("Prüfungswissen + Definitionen", "Spickzettel", icon="🎯"),
       it("Am Ende: kompletter Spickzettel", "Wiederholen", icon="📝"),
       it("Stift raus – mitschreiben!", "Stift", icon="✏️")]})

# ---------------- Thema 1 ----------------
sc(P, 1, "intro", """Thema eins: *Selbstständigkeit*. Fangen wir ganz vorne an.""",
   {"type": "topic", "n": 1, "title": "Selbstständigkeit", "icon": "🧑‍💼"})
sc(P, 1, "intro", """Stell dir vor, du arbeitest gerade in einem Betrieb. Du bekommst jeden Monat dein *Gehalt*,
egal ob der Betrieb gerade viele Aufträge hat oder wenige. Dein Chef kümmert sich um Kunden, Rechnungen und Werkzeug.
Als Selbstständiger bist du plötzlich *selbst* dieser *Chef*.""",
   {"type": "compare", "left": {"title": "Angestellt", "icon": "👷", "items": ["festes Gehalt jeden Monat", "Chef kümmert sich um Kunden & Rechnungen", "Werkzeug wird gestellt"]},
    "right": {"title": "Selbstständig", "icon": "🧑‍💼", "items": ["Einkommen schwankt", "du kümmerst dich um alles", "du kaufst alles selbst"]}, "cueRight": "Selbstständiger"})
sc(P, 1, "erklaerung", """Selbstständig ist also, wer sein *eigenes Unternehmen* führt, auf *eigene Rechnung* und auf *eigenes Risiko*.
Du hast *keinen Chef* mehr, der dir sagt, was du tun sollst. Aber du trägst auch das *ganze Risiko*.
Wenn es schlecht läuft, zahlt dir keiner ein Gehalt.""",
   {"type": "board", "title": "Selbstständig heißt …", "items": [
       it("eigenes Unternehmen führen", "eigenes", icon="🏢"),
       it("auf eigene Rechnung & eigenes Risiko", "Rechnung", icon="⚖️"),
       it("➕ kein Chef, der Anweisungen gibt", "keinen", color="green"),
       it("➖ das ganze Risiko trägst du", "ganze", color="red")]})
sc(P, 1, "intro", """Warum ist das Thema wichtig? Weil es in der Prüfung fast immer um eine Person geht, die sich überlegt zu gründen.
Und du sollst dann beurteilen können: Welche *Motive* hat sie? Bringt sie die richtigen *Eigenschaften* mit?
Und welche *Chancen* und *Risiken* gibt es?""",
   {"type": "board", "title": "Typische Prüfungsfragen zu Thema 1", "items": [
       it("Welche Motive hat die Person?", "Motive", icon="❓"),
       it("Hat sie die richtigen Unternehmereigenschaften?", "Eigenschaften", icon="❓"),
       it("Welche Chancen und Risiken gibt es?", "Chancen", icon="❓")]})
sc(P, 1, "erklaerung", """Beginnen wir mit den *Motiven*, also den Gründen, warum sich jemand selbstständig macht.
Bei Lukas klingt das so: Er hat keine Lust mehr, dass ihm jemand vorschreibt, wie er eine Anlage verdrahten soll.
Er will sein *eigener Chef* sein. Er hat *eigene Ideen*: Er will sich auf *Photovoltaik* und *Wallboxen* spezialisieren.
Er hofft, *mehr zu verdienen*, denn der Gewinn gehört ihm selbst. Und er will sich *selbst verwirklichen*,
also etwas Eigenes aufbauen, auf das er stolz sein kann.""",
   {"type": "lukas", "pose": "happy", "bubble": "Warum gründen?", "title": "Motive", "items": [
       it("eigener Chef sein", "eigener", icon="👑"),
       it("eigene Ideen umsetzen (PV & Wallboxen)", "Ideen", icon="💡"),
       it("mehr verdienen – Gewinn gehört mir", "verdienen", icon="💶"),
       it("Selbstverwirklichung", "verwirklichen", icon="🌱")]})
sc(P, 1, "erklaerung", """Es gibt aber auch Motive aus der *Not* heraus: Manche gründen, weil sie *keinen passenden Job* finden
oder *arbeitslos* sind. Und manchmal übernimmt jemand einfach den *Betrieb der Eltern*.
Merke dir: Motive können positiv sein, also etwas erreichen wollen, oder aus einer *Notlage* entstehen.""",
   {"type": "compare", "left": {"title": "„Ich will!“", "icon": "🚀", "items": ["eigener Chef", "eigene Ideen", "mehr verdienen", "Selbstverwirklichung"]},
    "right": {"title": "„Ich muss!“", "icon": "🆘", "items": ["kein passender Job", "Arbeitslosigkeit vermeiden", "Betrieb der Eltern übernehmen"]}, "cueRight": "Not"})
sc(P, 1, "erklaerung", """Nur weil man gründen will, heißt das noch nicht, dass man auch ein guter Unternehmer ist.
Dafür braucht man bestimmte *Unternehmereigenschaften*. Und jetzt kommt ein wichtiger Prüfungstipp:
Nenne die Eigenschaft nie allein, sondern immer *mit Begründung*.""",
   {"type": "tip", "title": "Prüfungstipp", "text": "Eigenschaft + Begründung", "example": "„Belastbarkeit, weil man als Selbstständiger oft 60 Stunden pro Woche arbeitet.“", "cue": "Prüfungstipp"})
sc(P, 1, "beispiel", """*Belastbarkeit*: Als Selbstständiger arbeitest du oft sechzig Stunden pro Woche.
Abends schreibst du noch Angebote und Rechnungen. Das musst du aushalten.
*Kommunikationsfähigkeit*: Lukas muss mit Kunden reden, mit Mitarbeitern, mit Lieferanten und mit der Bank.
Wer nicht gut erklären und verhandeln kann, bekommt keine Aufträge und keinen Kredit.""",
   {"type": "traits", "items": [
       it("Belastbarkeit", "Belastbarkeit", why="viel Arbeit & Stress, oft 60 Std./Woche", icon="💪"),
       it("Kommunikationsfähigkeit", "Kommunikationsfähigkeit", why="mit Kunden, Mitarbeitern, Lieferanten & Bank reden", icon="🗣️")]})
sc(P, 1, "beispiel", """*Fachwissen*: Lukas muss sein Handwerk beherrschen. Wenn eine Anlage nach seiner Montage nicht sicher ist,
haftet er dafür. Und Achtung: Das Elektrohandwerk ist *zulassungspflichtig*. Für einen eigenen Elektrobetrieb
braucht man in der Regel einen *Meisterbrief* oder eine gleichwertige Qualifikation und die Eintragung in die *Handwerksrolle*.""",
   {"type": "traits", "items": [
       it("Fachwissen", "Fachwissen", why="das Handwerk sicher beherrschen – Fehler können teuer werden", icon="⚡"),
       it("Elektrohandwerk = zulassungspflichtig", "zulassungspflichtig", why="meist Meisterbrief + Eintrag in die Handwerksrolle nötig", icon="📜")]})

# =====================================================================
# PART 1 – Thema 1 (Teil 2)
# =====================================================================
P = 1
sc(P, 1, "beispiel", """*Kaufmännisches Wissen*: Lukas muss rechnen können. Was kostet ihn eine Arbeitsstunde, damit er einen fairen Preis machen kann?
Wie viel Geld ist auf dem Konto? Wer das nicht im Blick hat, ist schnell pleite, obwohl er viele Aufträge hat.
*Entscheidungsfreude*: Kein Chef nimmt ihm Entscheidungen ab. Nimmt er den großen Auftrag an? Stellt er einen Gesellen ein?
Er muss entscheiden, und zwar oft schnell.""",
   {"type": "traits", "items": [
       it("Kaufmännisches Wissen", "Kaufmännisches", why="rechnen & planen: Preise, Kosten, Kontostand", icon="🧮"),
       it("Entscheidungsfreude", "Entscheidungsfreude", why="allein entscheiden – oft schnell", icon="🎯")]})
sc(P, 1, "beispiel", """*Risikobereitschaft*: Lukas setzt sein eigenes Erspartes ein. Das kann verloren gehen.
Wer bei jedem Risiko Angst bekommt, sollte lieber angestellt bleiben.
Weitere Eigenschaften, die du nennen kannst, sind *Durchhaltevermögen*, *Führungsfähigkeit* und *Kreativität*.
Wichtig ist immer: Eigenschaft plus Begründung.""",
   {"type": "traits", "items": [
       it("Risikobereitschaft", "Risikobereitschaft", why="eigenes Geld kann verloren gehen", icon="🎲"),
       it("Weitere: Durchhaltevermögen, Führungsfähigkeit, Kreativität", "Durchhaltevermögen", why="immer mit Begründung nennen!", icon="➕")]})
sc(P, 1, "erklaerung", """Jetzt zum Herzstück von Thema eins: den *Chancen* und *Risiken*. Im Bildungsplan stehen dafür vier Bereiche.
Und hier ist ein Trick, mit dem du sie nie vergisst: *Geld*, *Zeit*, *Verantwortung*, *Absicherung*.
Zu jedem Bereich gibt es eine Chance und ein Risiko. Es ist wie eine Waage.""",
   {"type": "balance", "row": -1, "mnemonic": True})
sc(P, 1, "erklaerung", """Erstens: Geld, im Bildungsplan heißt das *Einkommen und Vermögen*. Die Chance: Lukas kann *mehr verdienen*.
Der Gewinn gehört ihm, und mit der Zeit baut er sich ein eigenes *Vermögen* auf, also einen Betrieb, der etwas wert ist.
Das Risiko: Es gibt *kein festes Gehalt*. In einem schlechten Monat kommt vielleicht fast nichts rein.
Im schlimmsten Fall verliert er sein eingesetztes Geld, bis hin zur *Insolvenz*, also der Zahlungsunfähigkeit.""",
   {"type": "balance", "row": 0, "cueChance": "Chance", "cueRisk": "Risiko"})
sc(P, 1, "erklaerung", """Zweitens: Zeit, im Bildungsplan *Arbeitsbelastung*. Die Chance: Lukas kann sich seine Zeit *selbst einteilen*.
Will er am Mittwochnachmittag zum Elternabend, geht das. Das Risiko: Gerade am Anfang arbeitet er *viel mehr* als ein Angestellter,
oft auch am *Wochenende*, und Urlaub ist selten.""",
   {"type": "balance", "row": 1, "cueChance": "Chance", "cueRisk": "Risiko"})
sc(P, 1, "erklaerung", """Drittens: *Verantwortung*. Die Chance: Er ist sein *eigener Chef* und *entscheidet selbst*.
Das Risiko: Er ist für *alles verantwortlich*. Für Fehler auf der Baustelle, für Rechnungen und, sobald er Leute einstellt,
auch für die *Arbeitsplätze* seiner Mitarbeiter. Die müssen jeden Monat bezahlt werden, auch wenn es mal nicht läuft.""",
   {"type": "balance", "row": 2, "cueChance": "Chance", "cueRisk": "Risiko"})
sc(P, 1, "erklaerung", """Viertens: Absicherung, im Bildungsplan *soziale Sicherung*. Hier musst du gut aufpassen, das wird gern gefragt.
Als Angestellter zahlt dein Arbeitgeber die Hälfte deiner Sozialversicherung. Wirst du krank, bekommst du sechs Wochen
*Lohnfortzahlung*, und du hast bezahlten Urlaub. Als Selbstständiger fällt das alles weg.""",
   {"type": "compare", "left": {"title": "Angestellt", "icon": "🛡️", "items": ["Arbeitgeber zahlt ca. die Hälfte der Sozialversicherung", "6 Wochen Lohnfortzahlung bei Krankheit", "bezahlter Urlaub"]},
    "right": {"title": "Selbstständig", "icon": "⚠️", "items": ["alles selbst und komplett zahlen", "keine Lohnfortzahlung", "kein bezahlter Urlaub"]}, "cueRight": "Selbstständiger"})
sc(P, 1, "erklaerung", """Lukas muss seine Versicherungen *selbst zahlen*, und zwar komplett. Eine *Krankenversicherung* ist Pflicht.
Um seine *Rente* muss er sich meistens selbst kümmern. Eine Ausnahme: *Handwerker* mit Eintrag in der Handwerksrolle
sind in der Rentenversicherung pflichtversichert. Die *Arbeitslosenversicherung* ist nur *freiwillig* möglich.
Die Chance dabei: Er kann seine Absicherung *frei wählen* und auf seine Situation zuschneiden.""",
   {"type": "balance", "row": 3, "cueChance": "Chance", "cueRisk": "Lukas", "extra": [
       it("🏥 Krankenversicherung: Pflicht, selbst zahlen", "Krankenversicherung"),
       it("👴 Rente: meist selbst vorsorgen (Handwerker: Pflicht)", "Rente"),
       it("📉 Arbeitslosenversicherung: nur freiwillig", "Arbeitslosenversicherung")]})
sc(P, 1, "zusammenhang", """Siehst du den Zusammenhang? Die *Motive* sind genau die *Chancen*, die jemand nutzen will.
Die *Unternehmereigenschaften* braucht man, um mit den *Risiken* klarzukommen. Wer belastbar ist, verkraftet die hohe Arbeitsbelastung.
Wer kaufmännisch denkt, hat sein Einkommen im Griff. Und wer risikobereit ist, kommt mit dem fehlenden festen Gehalt klar.""",
   {"type": "links", "nodes": ["Motive", "Chancen", "Eigenschaften", "Risiken"], "edges": [
       {"from": 0, "to": 1, "label": "wollen nutzen", "cue": "Chancen"},
       {"from": 2, "to": 3, "label": "helfen gegen", "cue": "Risiken"}],
    "notes": [it("belastbar ➜ hohe Arbeitsbelastung", "belastbar"), it("kaufmännisch ➜ Einkommen im Griff", "kaufmännisch"), it("risikobereit ➜ kein festes Gehalt", "risikobereit")]})
sc(P, 1, "pruefung", """Was musst du für die *Prüfung* aus Thema eins können? Erstens: *Motive* nennen.
Zweitens: *Unternehmereigenschaften* immer mit Begründung nennen. Drittens: *Chancen und Risiken* in den vier Bereichen
Einkommen und Vermögen, Arbeitsbelastung, Verantwortung und soziale Sicherung gegenüberstellen.
Typische Aufgabe: *Beurteile*, ob Person X sich selbstständig machen sollte. Dann wägst du Chancen und Risiken ab
und schaust auf ihre Eigenschaften.""",
   {"type": "exam", "items": [
       it("Motive nennen (Wollen & Not)", "Motive"),
       it("Unternehmereigenschaften MIT Begründung", "Unternehmereigenschaften"),
       it("Chancen ⚖️ Risiken: Einkommen/Vermögen · Arbeitsbelastung · Verantwortung · soziale Sicherung", "Chancen"),
       it("„Beurteile …“ ➜ abwägen + Eigenschaften prüfen", "Beurteile")]})
sc(P, 1, "definition", """Und hier die Definition zum Auswendiglernen: *Selbstständig* ist, wer ein eigenes Unternehmen auf eigene Rechnung
und eigenes Risiko führt. Er ist nicht weisungsgebunden, trägt aber das volle unternehmerische Risiko.""",
   {"type": "definition", "term": "Selbstständigkeit", "text": "Selbstständig ist, wer ein eigenes Unternehmen auf eigene Rechnung und eigenes Risiko führt. Er ist nicht weisungsgebunden, trägt aber das volle unternehmerische Risiko."})

# =====================================================================
# PART 2 – Thema 2: Geschäftsplan & Standort
# =====================================================================
P = 2
sc(P, 2, "intro", """Thema zwei: *Geschäftsplan* und *Standort*.""",
   {"type": "topic", "n": 2, "title": "Geschäftsplan & Standort", "icon": "🗺️"})
sc(P, 2, "intro", """Lukas hat sich entschieden: Er will es wagen. Aber einfach loslegen? Keine gute Idee.
Stell dir vor, du baust eine große Schaltanlage ohne *Schaltplan*. Das geht schief.
Genau so ist es bei einer Gründung. Der Schaltplan einer Gründung heißt *Geschäftsplan*, oder auf Englisch *Businessplan*.""",
   {"type": "analogy", "left": {"icon": "📐", "title": "Schaltplan", "text": "ohne ihn keine sichere Anlage"}, "right": {"icon": "📘", "title": "Geschäftsplan", "text": "ohne ihn keine sichere Gründung"}, "cue": "Geschäftsplan"})
sc(P, 2, "erklaerung", """Der Geschäftsplan ist ein *schriftliches Konzept* für die Gründung. Er beantwortet zwei Fragen:
*Was* will ich machen? Und *wie* verdiene ich damit Geld?""",
   {"type": "board", "title": "Geschäftsplan = schriftliches Konzept", "items": [
       it("WAS will ich machen?", "Was", icon="❓"),
       it("WIE verdiene ich damit Geld?", "wie", icon="💶")]})
sc(P, 2, "erklaerung", """Was steht drin? Gehen wir das mit Lukas durch. Ganz oben die *Geschäftsidee*: Elektrobetrieb mit Schwerpunkt Photovoltaik und Wallboxen.
Dann die *Gründerperson*: Welche Ausbildung und Erfahrung hat Lukas? Danach *Kunden und Markt*: Wer braucht seine Leistung?
Zum Beispiel Hausbesitzer und kleine Firmen in der Region. Dann die *Konkurrenz*: Wie viele Elektrobetriebe gibt es schon,
und was macht Lukas besser?""",
   {"type": "plan", "upto": 4, "cues": ["Geschäftsidee", "Gründerperson", "Kunden", "Konkurrenz"]})
sc(P, 2, "erklaerung", """Weiter mit *Marketing*: Wie erfahren die Kunden von ihm? Über eine Website, Social Media oder Empfehlungen.
Dann der *Standort*, die *Rechtsform* und das *Personal*. Und zum Schluss das Wichtigste für die Bank: die *Finanzen*,
also vor allem der *Kapitalbedarfsplan*, oft ergänzt durch eine Planung von Umsatz und Gewinn.""",
   {"type": "plan", "upto": 9, "cues": ["", "", "", "", "Marketing", "Standort", "Rechtsform", "Personal", "Finanzen"]})
sc(P, 2, "erklaerung", """Wozu das Ganze? Der Geschäftsplan hat zwei *Funktionen*. Erstens zwingt er den Gründer, alles *durchzudenken*.
Viele Fehler fallen schon auf dem Papier auf, bevor sie echtes Geld kosten. Das *senkt das Risiko*.
Zweitens ist er die Grundlage, um einen *Kredit* oder *Fördergelder* zu bekommen.""",
   {"type": "board", "title": "Funktion des Geschäftsplans", "items": [
       it("alles durchdenken ➜ Fehler auf dem Papier finden", "durchzudenken", icon="🧠"),
       it("➜ senkt das Risiko", "senkt", color="green"),
       it("Grundlage für Kredit & Fördergelder", "Kredit", icon="🏦")]})
sc(P, 2, "erklaerung", """Und wer liest ihn? Das sind die *Adressaten*. Der wichtigste ist die *Bank*. Ohne überzeugenden Geschäftsplan gibt sie keinen Kredit.
Dann *Förderstellen*, zum Beispiel die *Agentur für Arbeit* beim Gründungszuschuss oder Förderbanken wie die *KfW*.
Weitere mögliche Adressaten sind *Investoren* oder *Geschäftspartner*. Und nicht zu vergessen: der *Gründer selbst*,
als Fahrplan für die ersten Jahre.""",
   {"type": "addressees", "items": [
       it("Bank", "Bank", icon="🏦", sub="Kredit"),
       it("Förderstellen", "Förderstellen", icon="🏛️", sub="Agentur für Arbeit, KfW"),
       it("Investoren / Partner", "Investoren", icon="🤝", sub="Beteiligung"),
       it("Gründer selbst", "Gründer", icon="🧑‍🔧", sub="Fahrplan")]})
sc(P, 2, "erklaerung", """Ein Punkt im Geschäftsplan ist so wichtig, dass er im Bildungsplan extra steht: der *Standort*.
Der Standort ist der *Ort*, an dem das Unternehmen sitzt. Und er entscheidet oft über *Erfolg oder Misserfolg*.""",
   {"type": "board", "title": "Standort", "items": [
       it("= der Ort, an dem das Unternehmen sitzt", "Ort", icon="📍"),
       it("entscheidet oft über Erfolg oder Misserfolg", "Erfolg", icon="⚠️")]})
sc(P, 2, "erklaerung", """Welche *Standortfaktoren* gibt es? Die *Kunden*: Sind genug Kunden in der Nähe? Die *Konkurrenz*: Gibt es schon viele Anbieter direkt nebenan?
Die *Kosten*, also Miete oder Pacht. Die *Erreichbarkeit*: Parkplätze, Bus und Bahn, Anbindung an die Autobahn.
Und *Größe und Ausstattung*: Gibt es genug Platz, ein Lager, Möglichkeiten zur Erweiterung?
Weitere Faktoren können *Arbeitskräfte* in der Region oder die Höhe der *Gewerbesteuer* sein.""",
   {"type": "factors", "items": [
       it("Kunden in der Nähe", "Kunden", icon="👥"),
       it("Konkurrenz", "Konkurrenz", icon="🏪"),
       it("Kosten (Miete, Pacht)", "Kosten", icon="💶"),
       it("Erreichbarkeit", "Erreichbarkeit", icon="🚗"),
       it("Größe & Ausstattung", "Größe", icon="📦"),
       it("Arbeitskräfte, Gewerbesteuer", "Arbeitskräfte", icon="➕")]})
sc(P, 2, "beispiel", """Jetzt kommt der Punkt, den viele übersehen: Welcher Faktor wichtig ist, hängt von der *Geschäftsidee* ab.
Ein *Fahrradladen* oder eine Bäckerei lebt von *Laufkundschaft*. Da muss der Standort zentral liegen, mit vielen Menschen und Parkplätzen.
Bei Lukas ist das anders. Seine Kunden kommen nicht zu ihm. Er fährt zu den Kunden. Für ihn zählen also eher *günstige Miete*,
ein *Lager* für Kabel und Material und eine gute *Verkehrsanbindung*. Eine teure Lage in der Fußgängerzone wäre für ihn rausgeschmissenes Geld.""",
   {"type": "compare", "left": {"title": "Fahrradladen / Bäckerei", "icon": "🚲", "items": ["lebt von Laufkundschaft", "zentrale Lage, viele Menschen", "Parkplätze direkt vor der Tür"]},
    "right": {"title": "Elektrobetrieb (Lukas)", "icon": "🚐", "items": ["fährt selbst zum Kunden", "günstige Miete + Lager", "gute Verkehrsanbindung"]}, "cueRight": "Lukas"})
sc(P, 2, "erklaerung", """In der Prüfung bekommst du oft eine *Bewertungstabelle*. Das geht in drei Schritten. Erstens: Jeden Faktor für jeden Standort
mit *Punkten* bewerten, und zwar passend zu den Infos in der Anlage. Zweitens: die Punkte *addieren*.
Drittens: den Standort mit den *meisten Punkten* empfehlen, und zwar *mit Begründung*.
Manchmal sind die Faktoren noch *gewichtet*. Dann rechnest du Punkte mal Gewichtung und addierst erst danach.""",
   {"type": "steps", "title": "Bewertungstabelle in 3 Schritten", "items": [
       it("Punkte je Faktor & Standort vergeben (passend zur Anlage)", "Punkten"),
       it("Punkte addieren", "addieren"),
       it("meiste Punkte ➜ empfehlen + begründen", "meisten"),
       it("Gewichtung? ➜ erst Punkte × Gewicht, dann addieren", "gewichtet")]})
sc(P, 2, "beispiel", """Schau dir das Beispiel an. Lukas vergleicht ein Ladenlokal in der *Innenstadt* mit einer Halle im *Gewerbegebiet*.
Die Innenstadt hat mehr Laufkundschaft, ist aber teuer und hat kaum Parkplätze. Das Gewerbegebiet ist günstig, gut erreichbar
und hat Platz für ein Lager. Ergebnis: Das Gewerbegebiet bekommt *mehr Punkte*. Und die Begründung lautet:
Lukas ist auf Laufkundschaft nicht angewiesen, er braucht günstigen Platz und eine gute Anbindung.""",
   {"type": "standort", "cueResult": "Ergebnis"})
sc(P, 2, "zusammenhang", """Der Zusammenhang: Der Standort ist ein Teil des *Geschäftsplans*. Und er beeinflusst später direkt das Geld.
Die *Miete* taucht nämlich im *Kapitalbedarfsplan* wieder auf. Das schauen wir uns in Thema vier an.""",
   {"type": "links", "nodes": ["Standort", "Geschäftsplan", "Miete", "Kapitalbedarfsplan"], "edges": [
       {"from": 0, "to": 1, "label": "ist Teil von", "cue": "Geschäftsplans"},
       {"from": 2, "to": 3, "label": "taucht auf in", "cue": "Kapitalbedarfsplan"}], "notes": [it("Standort ➜ Miete ➜ Geldbedarf", "Miete")]})
sc(P, 2, "pruefung", """Für die Prüfung musst du können: *Inhalt*, *Funktion* und *Adressaten* des Geschäftsplans nennen.
*Standortfaktoren* nennen und *passend zur Geschäftsidee* bewerten. Und eine *Bewertungstabelle* ausfüllen
und den Standort begründet empfehlen.""",
   {"type": "exam", "items": [
       it("Geschäftsplan: Inhalt · Funktion · Adressaten", "Inhalt"),
       it("Standortfaktoren nennen", "Standortfaktoren"),
       it("Faktoren passend zur Geschäftsidee bewerten", "passend"),
       it("Bewertungstabelle ausfüllen + begründet empfehlen", "Bewertungstabelle")]})
sc(P, 2, "definition", """Die Definitionen: Ein *Geschäftsplan* ist ein schriftliches Konzept, das alle wichtigen Bereiche einer Unternehmensgründung beschreibt.
Er dient dem Gründer zur Planung und Banken und Förderstellen als Entscheidungsgrundlage für Kredite.
Und: *Standortfaktoren* sind alle Einflussgrößen, die bei der Wahl des Unternehmensstandorts eine Rolle spielen,
zum Beispiel Kundennähe, Kosten und Erreichbarkeit.""",
   {"type": "definition", "term": "Geschäftsplan & Standortfaktoren", "text": "Ein Geschäftsplan ist ein schriftliches Konzept, das alle wichtigen Bereiche einer Unternehmensgründung beschreibt. Er dient dem Gründer zur Planung und Banken und Förderstellen als Entscheidungsgrundlage.",
    "text2": "Standortfaktoren sind alle Einflussgrößen, die bei der Wahl des Unternehmensstandorts eine Rolle spielen (z. B. Kundennähe, Kosten, Erreichbarkeit).", "cue2": "Standortfaktoren"})

# =====================================================================
# PART 3 – Thema 3: Rechtsformen
# =====================================================================
P = 3
sc(P, 3, "intro", """Thema drei: die *Rechtsformen*.""", {"type": "topic", "n": 3, "title": "Rechtsformen", "icon": "⚖️"})
sc(P, 3, "intro", """Lukas hat einen Plan und einen Standort. Jetzt muss er seinem Betrieb eine *Rechtsform* geben.
Klingt trocken, ist aber eine der wichtigsten Entscheidungen überhaupt. Denn die Rechtsform regelt vor allem eine Frage:
Wenn es schiefgeht, wer *zahlt*, und mit *welchem Geld*?""",
   {"type": "lukas", "pose": "worried", "bubble": "Wer zahlt, wenn's schiefgeht? 😬", "items": [it("Rechtsform = rechtlicher Rahmen", "Rechtsform", icon="📑"), it("Wer zahlt – mit welchem Geld?", "zahlt", icon="💸")]})
sc(P, 3, "erklaerung", """Wir vergleichen die Rechtsformen nach drei *Merkmalen*: dem *Mindestkapital*, also wie viel Geld man zum Gründen mindestens einbringen muss.
Der *Haftung*, also wer für die Schulden einstehen muss. Und der *Geschäftsführung*, also wer das Sagen hat.""",
   {"type": "board", "title": "Die 3 Vergleichsmerkmale", "items": [
       it("Mindestkapital – wie viel Geld mindestens?", "Mindestkapital", icon="💰"),
       it("Haftung – wer steht für Schulden ein?", "Haftung", icon="🛡️"),
       it("Geschäftsführung – wer hat das Sagen?", "Geschäftsführung", icon="🧭")]})
sc(P, 3, "erklaerung", """Bevor es losgeht, ein Bild zur *Haftung*. Stell dir zwei Töpfe vor. Im ersten Topf liegt das *Geschäftsvermögen*:
Werkzeug, Transporter, Geld auf dem Firmenkonto. Im zweiten Topf liegt dein *Privatvermögen*: dein Auto, dein Erspartes, vielleicht deine Wohnung.""",
   {"type": "pots", "mode": "intro"})
sc(P, 3, "erklaerung", """*Unbeschränkte Haftung* heißt: Wenn das Geschäft Schulden hat, dürfen die Gläubiger an *beide Töpfe*.
*Beschränkte Haftung* heißt: Die Gläubiger dürfen nur an den Geschäftstopf. Dein *Privatvermögen* ist *geschützt*.""",
   {"type": "pots", "mode": "both", "cueLimited": "Beschränkte"})
sc(P, 3, "erklaerung", """Erste Rechtsform: das *Einzelunternehmen*. Das ist der Klassiker, wenn jemand *allein* gründet. Lukas meldet einfach sein Gewerbe an und legt los.
*Mindestkapital*: *keins*. Das ist der große Vorteil, denn man kann sofort starten.
*Haftung*: *unbeschränkt*, also auch mit dem *Privatvermögen*.""",
   {"type": "form", "form": "einzel", "cues": ["Mindestkapital", "Haftung", "Geschäftsführung"]})
sc(P, 3, "beispiel", """Beispiel: Lukas kauft für einen großen Auftrag Material für zwanzigtausend Euro, und der Kunde geht pleite.
Kann Lukas die Rechnung des Großhändlers nicht bezahlen, kann der Großhändler notfalls auch an sein privates Auto oder sein Erspartes.
*Geschäftsführung*: der *Inhaber allein*. Er entscheidet alles, und der Gewinn gehört ihm allein.""",
   {"type": "form", "form": "einzel", "cues": ["", "", "Geschäftsführung"], "story": "Kunde pleite ➜ Großhändler will 20.000 € ➜ notfalls auch Lukas' Auto & Erspartes 🚗", "cueStory": "Beispiel"})
sc(P, 3, "erklaerung", """Zweite Rechtsform: die *GbR*, die *Gesellschaft bürgerlichen Rechts*. Die entsteht, wenn sich *mindestens zwei Personen* zusammentun.
Zum Beispiel gründet Lukas mit seinem Kollegen Ben. *Mindestkapital*: *keins*.
*Haftung*: *alle* Gesellschafter haften *unbeschränkt* mit ihrem Privatvermögen, und zwar *jeder für alles*. Das nennt man *gesamtschuldnerisch*.""",
   {"type": "form", "form": "gbr", "cues": ["Mindestkapital", "Haftung", "Geschäftsführung"]})
sc(P, 3, "beispiel", """Beispiel: Ben bestellt ohne Absprache teures Material. Der Lieferant kann sich das Geld *komplett von Lukas* holen,
auch wenn Lukas gar nichts davon wusste. *Geschäftsführung*: grundsätzlich *alle gemeinsam*, außer sie vereinbaren im Vertrag etwas anderes.""",
   {"type": "form", "form": "gbr", "cues": ["", "", "Geschäftsführung"], "story": "Ben bestellt allein ➜ Lieferant holt sich alles von Lukas 😱", "cueStory": "Beispiel"})
sc(P, 3, "erklaerung", """Dritte Rechtsform: die *GmbH*, die *Gesellschaft mit beschränkter Haftung*. Schon der Name verrät den Vorteil.
Gründen kann man sie schon *allein*, also ab *einer Person*. *Mindestkapital*: *fünfundzwanzigtausend Euro* Stammkapital.
Davon muss bei der Gründung mindestens die *Hälfte*, also zwölftausendfünfhundert Euro, eingezahlt sein.
Außerdem braucht man einen *Notar* und den Eintrag ins *Handelsregister*.""",
   {"type": "form", "form": "gmbh", "cues": ["Mindestkapital", "", ""], "story": "Gründung: Notar + Handelsregister 📜", "cueStory": "Notar"})
sc(P, 3, "erklaerung", """*Haftung*: *beschränkt*. Die GmbH haftet nur mit ihrem *Gesellschaftsvermögen*. Das *Privatvermögen* der Gesellschafter ist *geschützt*.
*Geschäftsführung*: durch den *Geschäftsführer*. Das kann der Gesellschafter selbst sein oder eine angestellte Person.""",
   {"type": "form", "form": "gmbh", "cues": ["", "Haftung", "Geschäftsführung"]})
sc(P, 3, "erklaerung", """Vierte Rechtsform: die *UG*, die *Unternehmergesellschaft haftungsbeschränkt*. Man nennt sie auch *Mini-GmbH*.
Sie ist für Gründer gedacht, die die fünfundzwanzigtausend Euro nicht haben. *Mindestkapital*: schon *ab einem Euro*, und ab einer Person.
*Haftung*: *beschränkt*, das Privatvermögen ist geschützt, genau wie bei der GmbH. *Geschäftsführung*: durch den *Geschäftsführer*.""",
   {"type": "form", "form": "ug", "cues": ["Mindestkapital", "Haftung", "Geschäftsführung"]})
sc(P, 3, "erklaerung", """Der Haken: Die UG muss jedes Jahr *fünfundzwanzig Prozent* ihres *Gewinns* zurücklegen, so lange,
bis *fünfundzwanzigtausend Euro* zusammen sind. Dann kann sie zur richtigen GmbH werden.
Die UG ist also eine Art *Sparstufe* auf dem Weg zur GmbH.""",
   {"type": "ugbar", "cue": "fünfundzwanzig"})
sc(P, 3, "erklaerung", """Schau dir jetzt die Tabelle an, die musst du im Kopf haben. Merke dir die zwei Gruppen: *Einzelunternehmen* und *GbR*:
kein Mindestkapital, aber man haftet *privat*. *GmbH* und *UG*: das *Privatvermögen* ist *geschützt*.
Die GmbH braucht *fünfundzwanzigtausend Euro*, die UG nur *einen Euro*.""",
   {"type": "formtable", "cueGroup1": "Einzelunternehmen", "cueGroup2": "GmbH"})
sc(P, 3, "erklaerung", """Wie wählst du in der Prüfung die passende Rechtsform? Stell dir drei Fragen. Erstens: *Wie viele* gründen?
Eine Person: dann Einzelunternehmen, GmbH oder UG. Mehrere Personen: dann GbR, GmbH oder UG. Zweitens: *Wie viel Geld* ist da?
Wer keine fünfundzwanzigtausend Euro hat, kann keine GmbH gründen. Drittens: Soll das *Privatvermögen geschützt* sein? Dann GmbH oder UG.""",
   {"type": "steps", "title": "Die passende Rechtsform in 3 Fragen", "items": [
       it("Wie viele gründen? 1 ➜ Einzel/GmbH/UG · 2+ ➜ GbR/GmbH/UG", "viele"),
       it("Wie viel Geld ist da? < 25.000 € ➜ keine GmbH", "Geld"),
       it("Privatvermögen schützen? ➜ GmbH oder UG", "Privatvermögen")]})
sc(P, 3, "beispiel", """Und bei Lukas? Er gründet *allein* und hat *zwanzigtausend Euro* Erspartes, also weniger als die fünfundzwanzigtausend für eine GmbH.
Als Elektriker trägt er aber ein *hohes Haftungsrisiko*, denn ein Fehler in einer Anlage kann teuer werden.
Deshalb passt die *UG* gut: Privatvermögen geschützt, Start schon ab einem Euro. Wenn er lieber ganz klein und unkompliziert starten will,
wäre das *Einzelunternehmen* die Alternative, dann aber unbedingt mit einer guten *Betriebshaftpflichtversicherung*.""",
   {"type": "lukas", "pose": "happy", "bubble": "Ich nehme die UG! ✅", "title": "Lukas entscheidet", "items": [
       it("gründet allein", "allein", icon="1️⃣"),
       it("20.000 € Erspartes – keine 25.000 €", "zwanzigtausend", icon="💶"),
       it("hohes Haftungsrisiko als Elektriker", "Haftungsrisiko", icon="⚡"),
       it("➜ UG: Privatvermögen geschützt, ab 1 €", "UG", icon="✅"),
       it("Alternative: Einzelunternehmen + Betriebshaftpflicht", "Einzelunternehmen", icon="↔️")]})
sc(P, 3, "zusammenhang", """Siehst du den Zusammenhang zu den anderen Themen? Die Rechtsform gehört in den *Geschäftsplan*.
Sie hängt mit dem *Risiko* aus Thema eins zusammen, denn eine beschränkte Haftung verringert das private Risiko.
Und sie hängt vom *Geld* ab, also vom Kapital, und damit von Thema vier.""",
   {"type": "links", "nodes": ["Rechtsform", "Geschäftsplan", "Risiko (Thema 1)", "Kapital (Thema 4)"], "edges": [
       {"from": 0, "to": 1, "label": "steht im", "cue": "Geschäftsplan"},
       {"from": 0, "to": 2, "label": "beschränkte Haftung senkt", "cue": "Risiko"},
       {"from": 0, "to": 3, "label": "hängt ab vom", "cue": "Geld"}]})
sc(P, 3, "pruefung", """Für die Prüfung: Du musst die vier Rechtsformen nach *Mindestkapital*, *Haftung* und *Geschäftsführung* vergleichen können.
Und du musst für eine Person *begründet* die passende Rechtsform empfehlen. Die Zahlen *fünfundzwanzigtausend Euro*, *ein Euro*
und *fünfundzwanzig Prozent* musst du sicher können.""",
   {"type": "exam", "items": [
       it("4 Rechtsformen nach Mindestkapital · Haftung · Geschäftsführung vergleichen", "Mindestkapital"),
       it("passende Rechtsform begründet empfehlen", "begründet"),
       it("Zahlen: GmbH 25.000 € · UG 1 € · UG legt 25 % zurück", "Zahlen")]})
sc(P, 3, "definition", """Definitionen: *Haftung* bedeutet, mit seinem Vermögen für die Schulden des Unternehmens einstehen zu müssen.
*Unbeschränkte Haftung* heißt, man haftet mit Geschäfts- und Privatvermögen. *Beschränkte Haftung* heißt, es haftet nur das Gesellschaftsvermögen,
das Privatvermögen ist geschützt.""",
   {"type": "definition", "term": "Haftung", "text": "Haftung bedeutet, mit seinem Vermögen für die Schulden des Unternehmens einstehen zu müssen.",
    "text2": "Unbeschränkt: mit Geschäfts- UND Privatvermögen. Beschränkt: nur mit dem Gesellschaftsvermögen – das Privatvermögen ist geschützt.", "cue2": "Unbeschränkte"})

# =====================================================================
# PART 4 – Thema 4: Kapitalbedarfsplan
# =====================================================================
P = 4
sc(P, 4, "intro", """Und damit sind wir beim letzten Thema: dem *Kapitalbedarfsplan*.""", {"type": "topic", "n": 4, "title": "Kapitalbedarfsplan", "icon": "🧮"})
sc(P, 4, "intro", """Jetzt geht es ums *Geld*. Lukas weiß, was er machen will, wo und in welcher Rechtsform. Aber wie viel Geld braucht er eigentlich, um loszulegen?
Viele Gründer *unterschätzen* das. Sie denken nur an Werkzeug und Transporter und vergessen, dass in den ersten Monaten noch kaum Geld reinkommt.
Genau davor schützt der Kapitalbedarfsplan.""",
   {"type": "lukas", "pose": "think", "bubble": "Wie viel Geld brauche ich? 🤔", "items": [it("Fehler vieler Gründer: Geldbedarf unterschätzen", "unterschätzen", icon="⚠️"), it("erste Monate: kaum Einnahmen", "Monaten", icon="📉")]})
sc(P, 4, "erklaerung", """Der Kapitalbedarfsplan zeigt, *wie viel Geld* man *insgesamt* für die Gründung braucht.
Und daraus ergibt sich, wie viel man davon *von der Bank* leihen muss.""",
   {"type": "board", "title": "Kapitalbedarfsplan", "items": [
       it("Wie viel Geld brauche ich insgesamt?", "insgesamt", icon="💰"),
       it("Wie viel davon muss ich mir von der Bank leihen?", "Bank", icon="🏦")]})
sc(P, 4, "erklaerung", """Was gehört rein? Merke dir *sechs Bausteine*. Erstens, die *Investitionen*. Das sind *einmalige Anschaffungen*, die lange im Betrieb bleiben.
Bei Lukas: ein *Transporter*, *Werkzeug* und *Messgeräte*, die *Einrichtung* für Büro und Lager und ein *Computer*.""",
   {"type": "blocks", "upto": 1, "cues": ["Investitionen"]})
sc(P, 4, "erklaerung", """Zweitens, die *Erstausstattung* an Material oder Waren. Bei einem Fahrradladen wären das die ersten Fahrräder.
Bei Lukas ist es das erste *Material*: Kabel, Schalter, Sicherungen. Drittens, die *Gründungskosten*:
zum Beispiel *Gewerbeanmeldung*, *Notar*, *Beratung* und Eintrag ins Register.""",
   {"type": "blocks", "upto": 3, "cues": ["", "Erstausstattung", "Gründungskosten"]})
sc(P, 4, "erklaerung", """Viertens, die *laufenden Kosten* für die *Anfangszeit*. Das sind Kosten, die jeden Monat anfallen, zum Beispiel *Miete*, *Versicherungen*,
*Werbung* und, wenn es Mitarbeiter gibt, *Löhne*. Die plant man für mehrere Monate ein, weil am Anfang noch wenig Umsatz kommt.""",
   {"type": "blocks", "upto": 4, "cues": ["", "", "", "laufenden"]})
sc(P, 4, "erklaerung", """Fünftens, und das wird oft vergessen: die *Lebenshaltungskosten* des Gründers. Lukas muss ja auch von etwas leben.
Miete für seine Wohnung, Essen, Versicherungen. Die muss er für die ersten Monate einplanen. Sechstens, eine *Reserve* für *Unvorhergesehenes*.
Der Transporter geht kaputt, oder ein Kunde zahlt zu spät. Dann braucht man einen Puffer.""",
   {"type": "blocks", "upto": 6, "cues": ["", "", "", "", "Lebenshaltungskosten", "Reserve"]})
sc(P, 4, "pruefung", """Ganz wichtig für die Rechnung: Bei *monatlichen* Kosten rechnest du immer *mal die Anzahl der Monate*.
Steht in der Aufgabe: Miete achthundert Euro, für sechs Monate einplanen, dann sind das achthundert mal sechs, also *viertausendachthundert Euro*.
Das ist der *häufigste Fehler* in der Prüfung.""",
   {"type": "calc", "line": "800 € × 6 Monate = 4.800 €", "cue": "achthundert", "warn": "Häufigster Prüfungsfehler!", "cueWarn": "häufigste"})
sc(P, 4, "erklaerung", """Und dann kommt die wichtigste Formel: *Kapitalbedarf minus Eigenkapital gleich Fremdkapital*.
Das *Eigenkapital* ist das eigene Geld, das der Gründer mitbringt. Das *Fremdkapital* ist das geliehene Geld, meistens ein *Kredit* von der Bank.""",
   {"type": "formula", "cues": ["Kapitalbedarf", "Eigenkapital", "Fremdkapital"], "explain": [it("Eigenkapital = eigenes Geld des Gründers", "eigene"), it("Fremdkapital = geliehenes Geld (Bankkredit)", "geliehene")]})
sc(P, 4, "beispiel", """Rechnen wir das für Lukas durch. *Transporter* achtzehntausend Euro. *Werkzeug* und Messgeräte siebentausend.
*Einrichtung* für Büro und Lager viertausend. *Computer* und Software zweitausend. Erstes *Material* sechstausend. *Gründungskosten* tausend Euro.""",
   {"type": "kapital", "upto": 6})
sc(P, 4, "beispiel", """*Miete* achthundert Euro mal sechs Monate, also viertausendachthundert. *Versicherungen* und Werbung vierhundert mal sechs, also zweitausendvierhundert.
Seine *Lebenshaltung*: tausendsechshundert mal sechs, macht neuntausendsechshundert. Und eine *Reserve* von fünftausend Euro.
Alles zusammen ergibt einen *Kapitalbedarf* von *neunundfünfzigtausendachthundert Euro*.""",
   {"type": "kapital", "upto": 10, "showTotal": "Kapitalbedarf"})
sc(P, 4, "beispiel", """Lukas hat *zwanzigtausend Euro* Eigenkapital. Also rechnen wir: neunundfünfzigtausendachthundert minus zwanzigtausend
gleich *neununddreißigtausendachthundert Euro*. So viel *Kredit* muss Lukas bei der Bank beantragen.""",
   {"type": "kapital", "upto": 10, "showTotal": "", "showKredit": "Eigenkapital"})
sc(P, 4, "beispiel", """Übrigens: Das Beispiel aus deinen Unterlagen mit Stefans *Fahrradladen* habe ich nachgerechnet.
Kapitalbedarf *neunzigtausendneunhundert* Euro, minus fünfundzwanzigtausend Euro Eigenkapital, ergibt *fünfundsechzigtausendneunhundert Euro* Kredit.
Das stimmt genau so.""",
   {"type": "check", "title": "Check: Stefans Fahrradladen 🚲", "lines": ["Kapitalbedarf: 90.900 €", "− Eigenkapital: 25.000 €", "= Kredit: 65.900 € ✅"], "cue": "neunzigtausendneunhundert"})
sc(P, 4, "zusammenhang", """Jetzt schließt sich der Kreis. Der Kapitalbedarfsplan ist der *Finanzteil* des *Geschäftsplans*. Die *Miete* hängt vom *Standort* ab.
Das *Eigenkapital* entscheidet mit über die *Rechtsform*, denn ohne fünfundzwanzigtausend Euro keine GmbH.
Und der *Kredit* ist ein Teil des *Risikos* aus Thema eins, denn er muss zurückgezahlt werden, egal ob das Geschäft läuft oder nicht.""",
   {"type": "circle", "cues": ["Finanzteil", "Miete", "Eigenkapital", "Kredit"]})
sc(P, 4, "pruefung", """Für die Prüfung: Kenne die *Bausteine* des Kapitalbedarfsplans. Vergiss nie die *Lebenshaltungskosten* und die *Reserve*.
Rechne monatliche Kosten immer *mal die Monate*. Und wende die Formel an: *Kapitalbedarf minus Eigenkapital gleich Kredit*.""",
   {"type": "exam", "items": [
       it("6 Bausteine kennen", "Bausteine"),
       it("Lebenshaltungskosten + Reserve nie vergessen!", "Lebenshaltungskosten"),
       it("monatliche Kosten × Monate", "monatliche"),
       it("Kapitalbedarf − Eigenkapital = Kredit (Fremdkapital)", "Formel")]})
sc(P, 4, "definition", """Definition: Der *Kapitalbedarfsplan* ermittelt den gesamten Geldbedarf einer Unternehmensgründung. Er umfasst Investitionen, Erstausstattung,
Gründungskosten, Anlaufkosten, private Lebenshaltungskosten und eine Reserve. Zieht man das Eigenkapital ab, erhält man das benötigte Fremdkapital.""",
   {"type": "definition", "term": "Kapitalbedarfsplan", "text": "Der Kapitalbedarfsplan ermittelt den gesamten Geldbedarf einer Unternehmensgründung: Investitionen, Erstausstattung, Gründungskosten, Anlaufkosten, private Lebenshaltungskosten und Reserve.",
    "text2": "Kapitalbedarf − Eigenkapital = benötigtes Fremdkapital (Kredit)", "cue2": "Zieht"})

# =====================================================================
# PART 5 – Gesamtzusammenfassung (1)
# =====================================================================
P = 5
sc(P, 5, "summary", """Super, du hast alle vier Themen geschafft! Jetzt kommt das Wichtigste vor der Prüfung: die *Gesamtzusammenfassung*.
Das ist dein mündlicher *Spickzettel*. Hör gut zu, oder halte das Video an, wenn du mitschreiben willst.""",
   {"type": "topic", "n": 5, "title": "Gesamtzusammenfassung", "icon": "📝"})
sc(P, 5, "summary", """*Thema eins: Selbstständigkeit*. Selbstständig ist, wer ein eigenes Unternehmen auf eigene Rechnung und eigenes Risiko führt.
Kein Chef, aber volles Risiko. Die *Motive*: eigener Chef sein, eigene Ideen umsetzen, mehr verdienen, Selbstverwirklichung,
und aus der Not heraus: kein passender Job, Arbeitslosigkeit oder eine Betriebsübernahme.""",
   {"type": "sum", "n": 1, "title": "Thema 1 · Selbstständigkeit", "items": [
       it("Def.: eigenes Unternehmen auf eigene Rechnung & eigenes Risiko", "Selbstständig"),
       it("Motive (Wollen): eigener Chef · eigene Ideen · mehr verdienen · Selbstverwirklichung", "Motive"),
       it("Motive (Not): kein passender Job · Arbeitslosigkeit · Betriebsübernahme", "Not")]})
sc(P, 5, "summary", """Die *Unternehmereigenschaften*, immer mit Begründung: *Belastbarkeit* wegen viel Arbeit und Stress. *Kommunikationsfähigkeit* für Kunden, Mitarbeiter und Bank.
*Fachwissen*, um das Handwerk zu beherrschen, im Elektrohandwerk meist mit Meisterbrief. *Kaufmännisches Wissen* zum Rechnen und Planen.
*Entscheidungsfreude*, weil man allein entscheidet. Und *Risikobereitschaft*, weil das eigene Geld verloren gehen kann.""",
   {"type": "sum", "n": 1, "title": "Unternehmereigenschaften (+ Begründung!)", "items": [
       it("Belastbarkeit ➜ viel Arbeit & Stress", "Belastbarkeit"),
       it("Kommunikationsfähigkeit ➜ Kunden, Mitarbeiter, Bank", "Kommunikationsfähigkeit"),
       it("Fachwissen ➜ Handwerk beherrschen (Elektro: meist Meister)", "Fachwissen"),
       it("Kaufmännisches Wissen ➜ rechnen & planen", "Kaufmännisches"),
       it("Entscheidungsfreude ➜ allein entscheiden", "Entscheidungsfreude"),
       it("Risikobereitschaft ➜ eigenes Geld kann weg sein", "Risikobereitschaft")]})
sc(P, 5, "summary", """Die *Chancen und Risiken* merkst du dir mit *Geld, Zeit, Verantwortung, Absicherung*.
Geld: Chance höheres Einkommen und eigenes Vermögen, Risiko kein festes Gehalt bis zur Insolvenz.
Zeit: Chance freie Zeiteinteilung, Risiko hohe Arbeitsbelastung, auch am Wochenende.
Verantwortung: Chance selbst entscheiden, Risiko Verantwortung für alles, auch für Mitarbeiter.
Absicherung: Chance freie Wahl der Versicherungen, Risiko alles selbst zahlen, keine Lohnfortzahlung, kein bezahlter Urlaub, Rente meist selbst vorsorgen.""",
   {"type": "balance", "row": 9, "summaryMode": True, "cues": ["Geld:", "Zeit:", "Verantwortung:", "Absicherung:"]})
sc(P, 5, "summary", """*Thema zwei: Geschäftsplan und Standort*. Der Geschäftsplan ist ein schriftliches Konzept für die Gründung: Was will ich machen,
und wie verdiene ich damit Geld? *Inhalt*: Geschäftsidee, Gründerperson, Kunden und Markt, Konkurrenz, Marketing, Standort, Rechtsform, Personal
und Finanzen mit dem Kapitalbedarfsplan.""",
   {"type": "sum", "n": 2, "title": "Thema 2 · Geschäftsplan", "items": [
       it("Def.: schriftliches Konzept – WAS mache ich, WIE verdiene ich Geld?", "Geschäftsplan"),
       it("Inhalt: Idee · Gründerperson · Kunden/Markt · Konkurrenz · Marketing", "Inhalt"),
       it("… Standort · Rechtsform · Personal · Finanzen (Kapitalbedarfsplan)", "Standort")]})
sc(P, 5, "summary", """*Funktion*: alles durchdenken und so das Risiko senken, und die Grundlage für Kredit und Förderung.
*Adressaten*: vor allem die Bank, außerdem Förderstellen wie die Agentur für Arbeit oder die KfW, Investoren und der Gründer selbst.""",
   {"type": "sum", "n": 2, "title": "Funktion & Adressaten", "items": [
       it("Funktion: durchdenken ➜ Risiko senken", "Funktion"),
       it("Funktion: Grundlage für Kredit & Förderung", "Grundlage"),
       it("Adressaten: Bank · Förderstellen (Agentur für Arbeit, KfW) · Investoren · Gründer", "Adressaten")]})

# =====================================================================
# PART 6 – Gesamtzusammenfassung (2)
# =====================================================================
P = 6
sc(P, 5, "summary", """Der *Standort* ist der Ort des Unternehmens und entscheidet oft über Erfolg oder Misserfolg. *Standortfaktoren*: Kundennähe, Konkurrenz,
Kosten wie Miete oder Pacht, Erreichbarkeit sowie Größe und Ausstattung. Welche Faktoren zählen, hängt von der Geschäftsidee ab:
Ein Laden braucht Laufkundschaft, ein Handwerksbetrieb eher Platz, günstige Kosten und gute Anbindung.
Die *Bewertungstabelle*: Punkte pro Faktor vergeben, eventuell mal Gewichtung, addieren und den Standort mit den meisten Punkten begründet empfehlen.""",
   {"type": "sum", "n": 2, "title": "Standort", "items": [
       it("Standort = Ort des Unternehmens ➜ Erfolg oder Misserfolg", "Standort"),
       it("Faktoren: Kunden · Konkurrenz · Kosten · Erreichbarkeit · Größe/Ausstattung", "Standortfaktoren"),
       it("hängt von der Geschäftsidee ab (Laden ≠ Handwerksbetrieb)", "hängt"),
       it("Tabelle: Punkte (× Gewicht) ➜ addieren ➜ Sieger begründen", "Bewertungstabelle")]})
sc(P, 5, "summary", """*Thema drei: Rechtsformen*. Die Rechtsform regelt vor allem, wer haftet und wie viel Kapital man braucht.
Verglichen wird nach Mindestkapital, Haftung und Geschäftsführung.
*Einzelunternehmen*: eine Person, kein Mindestkapital, unbeschränkte Haftung auch mit dem Privatvermögen, Geschäftsführung durch den Inhaber allein.
*GbR*: mindestens zwei Personen, kein Mindestkapital, alle haften unbeschränkt und jeder für alles, Geschäftsführung grundsätzlich gemeinsam.""",
   {"type": "formtable", "cueGroup1": "Einzelunternehmen", "cueGroup2": "zzz", "highlight": ["einzel", "gbr"]})
sc(P, 5, "summary", """*GmbH*: ab einer Person, fünfundzwanzigtausend Euro Stammkapital, mindestens die Hälfte bei Gründung eingezahlt. Haftung beschränkt auf das Gesellschaftsvermögen,
das Privatvermögen ist geschützt. Geschäftsführung durch den Geschäftsführer.
*UG haftungsbeschränkt*: die Mini-GmbH. Ab einer Person, ab einem Euro, Haftung beschränkt, Geschäftsführung durch den Geschäftsführer.
Sie muss fünfundzwanzig Prozent des Gewinns zurücklegen, bis fünfundzwanzigtausend Euro erreicht sind.""",
   {"type": "formtable", "cueGroup1": "zzz", "cueGroup2": "GmbH", "highlight": ["gmbh", "ug"]})
sc(P, 5, "summary", """Die *Auswahl* in drei Fragen: Wie viele gründen? Wie viel Geld ist da? Soll das Privatvermögen geschützt sein?
Merksatz: Einzelunternehmen und GbR heißt kein Kapital, aber privat haften. GmbH und UG heißt Privatvermögen geschützt.""",
   {"type": "sum", "n": 3, "title": "Rechtsform wählen", "items": [
       it("1. Wie viele gründen?", "viele"),
       it("2. Wie viel Geld ist da? (GmbH: 25.000 €)", "Geld"),
       it("3. Privatvermögen schützen? ➜ GmbH/UG", "Privatvermögen"),
       it("Merksatz: Einzel + GbR = kein Kapital, aber privat haften", "Merksatz")]})
sc(P, 5, "summary", """*Thema vier: Kapitalbedarfsplan*. Er zeigt, wie viel Geld man insgesamt für die Gründung braucht und wie viel davon als Kredit nötig ist.
Die sechs *Bausteine*: Investitionen wie Fahrzeug, Werkzeug und Einrichtung. Erstausstattung an Waren oder Material.
Gründungskosten wie Notar und Gewerbeanmeldung. Laufende Kosten für die Anfangszeit wie Miete, Löhne und Werbung.
Die Lebenshaltungskosten des Gründers. Und eine Reserve.
Monatliche Kosten immer *mal die Monate* rechnen. Und die Formel: *Kapitalbedarf minus Eigenkapital gleich Kredit*, also Fremdkapital.""",
   {"type": "sum", "n": 4, "title": "Thema 4 · Kapitalbedarfsplan", "items": [
       it("1 Investitionen (Fahrzeug, Werkzeug, Einrichtung)", "Investitionen"),
       it("2 Erstausstattung (Waren / Material)", "Erstausstattung"),
       it("3 Gründungskosten (Notar, Gewerbeanmeldung)", "Gründungskosten"),
       it("4 Laufende Kosten Anfangszeit (Miete, Löhne, Werbung)", "Laufende"),
       it("5 Lebenshaltungskosten des Gründers", "Lebenshaltungskosten"),
       it("6 Reserve", "Reserve"),
       it("monatlich × Monate · Kapitalbedarf − Eigenkapital = Kredit", "Monatliche")]})
sc(P, 5, "summary", """Zum Schluss das große Bild: Erst prüfst du, ob die *Selbstständigkeit* zu dir passt. Dann planst du alles im *Geschäftsplan*, inklusive *Standort*.
Du wählst die passende *Rechtsform*. Und mit dem *Kapitalbedarfsplan* rechnest du aus, wie viel Geld du brauchst und wie viel Kredit.
Alles hängt zusammen, und genau so denkst du auch in der Prüfung.""",
   {"type": "roadmap", "cues": ["Selbstständigkeit", "Geschäftsplan", "Rechtsform", "Kapitalbedarfsplan"], "flow": True})
sc(P, 5, "definition", """Und die *Definitionen* zum Auswendiglernen noch einmal am Stück. Selbstständig ist, wer ein eigenes Unternehmen auf eigene Rechnung und eigenes Risiko führt.
Ein *Geschäftsplan* ist ein schriftliches Konzept, das alle wichtigen Bereiche einer Gründung beschreibt und Banken und Förderstellen als Entscheidungsgrundlage dient.
*Standortfaktoren* sind alle Einflussgrößen für die Wahl des Standorts, zum Beispiel Kundennähe, Kosten und Erreichbarkeit.""",
   {"type": "deflist", "items": [
       it("Selbstständigkeit: eigenes Unternehmen auf eigene Rechnung & eigenes Risiko", "Selbstständig"),
       it("Geschäftsplan: schriftliches Konzept aller Gründungsbereiche, Entscheidungsgrundlage für Bank & Förderstellen", "Geschäftsplan"),
       it("Standortfaktoren: Einflussgrößen für die Standortwahl (Kundennähe, Kosten, Erreichbarkeit …)", "Standortfaktoren")]})
sc(P, 5, "definition", """*Haftung* bedeutet, mit seinem Vermögen für die Schulden des Unternehmens einzustehen. Unbeschränkt heißt mit Geschäfts- und Privatvermögen,
beschränkt heißt nur mit dem Gesellschaftsvermögen. Der *Kapitalbedarfsplan* ermittelt den gesamten Geldbedarf einer Gründung.
Kapitalbedarf minus Eigenkapital ergibt das benötigte Fremdkapital.""",
   {"type": "deflist", "items": [
       it("Haftung: mit dem Vermögen für Unternehmensschulden einstehen", "Haftung"),
       it("unbeschränkt = Geschäfts- + Privatvermögen · beschränkt = nur Gesellschaftsvermögen", "Unbeschränkt"),
       it("Kapitalbedarfsplan: ermittelt den gesamten Geldbedarf einer Gründung", "Kapitalbedarfsplan"),
       it("Kapitalbedarf − Eigenkapital = Fremdkapital", "minus")]})
sc(P, 5, "outro", """Das war's! Wenn du diese Zusammenfassung verstanden hast, bist du für Kompetenzbereich vier richtig gut vorbereitet.
Ich drücke dir die Daumen für deine AP2. Du schaffst das!""",
   {"type": "title", "title": "Viel Erfolg in der AP2! 💪", "subtitle": "Du schaffst das!", "badge": "KB IV · Selbstständigkeit"})

out = {
    "title": "KB IV – Selbstständigkeit (AP2 WiSo)",
    "sentences": S,
}
p = Path(__file__).resolve().parent.parent / "src" / "wiso" / "script.json"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
words = sum(len(s["text"].split()) for s in S)
print(f"{len(S)} Szenen, {words} Wörter, ~{words / 160:.0f} min")
for k in range(7):
    print("Teil", k, sum(len(s["text"].split()) for s in S if s["part"] == k), "Wörter")
