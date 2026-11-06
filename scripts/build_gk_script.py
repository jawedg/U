#!/usr/bin/env python3
"""Lernvideo Gemeinschaftskunde (alle Themen in EINEM Video) nach dem Lernzettel des Nutzers
(WiSo_Lernzettel_Gemeinschaftskunde.pdf). Lehrer-Erklärstil: ganze Sätze, Beispiele, Quizfragen, Merke.
Inhalt folgt exakt dem Lernzettel (nichts weglassen, nichts Neues erfinden).
Ausgabe: src/lern_gk/script.json (gleiches Format wie src/lern_kbN, kb = 5 -> Label „GK“).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOPICS = ["Demokratie und Wahlen", "Friedenssicherung", "Globalisierung und Migration", "Medien und Social Media",
          "Europäische Union (EU)", "Demografischer Wandel und Fachkräftemangel", "Grundrechte und Rechtsstaat",
          "Parteien und Verbände", "Familie, Männer und Frauen", "Prüfungstipps"]
S = []
topic_no, topic_name = 0, "Überblick"


def thema(name):
    global topic_no, topic_name
    topic_no += 1
    topic_name = name
    assert TOPICS[topic_no - 1] == name, name


def sc(text, v):
    S.append({"topic": topic_no, "tname": topic_name, "text": " ".join(text.split()), "v": v})


def it(text, cue, **kw):
    return {"text": text, "cue": cue, **kw}


def T(text):
    sc(text, {"type": "topic"})


def P(text, title, items, label=None, note=None, cue_note=None):
    sc(text, {"type": "points", "title": title, "label": label, "items": items, "note": note, "cueNote": cue_note})


def D(text, term, definition):
    sc(text, {"type": "def", "term": term, "text": definition})


def C(text, lt, li, rt, ri, cue_right, note=None, cue_note=None):
    sc(text, {"type": "compare", "left": {"title": lt, "items": li}, "right": {"title": rt, "items": ri},
              "cueRight": cue_right, "note": note, "cueNote": cue_note})


def PRO(text, pro, con, cue_con, note=None, cue_note=None):
    C(text, "Pro ➕", pro, "Contra ➖", con, cue_con, note, cue_note)


def TB(text, title, head, rows, note=None):
    sc(text, {"type": "table", "title": title, "head": head,
              "rows": [{"cells": r[0], "cue": r[1], "hl": (len(r) > 2 and r[2])} for r in rows], "note": note})


def X(text, steps, title):
    sc(text, {"type": "case", "title": title, "items": steps})


def M(text, merke):
    sc(text, {"type": "merke", "text": merke})


def BIG(text, big, sub=None, items=None):
    sc(text, {"type": "big", "big": big, "sub": sub, "items": items or []})


def ST(text, title, items):
    sc(text, {"type": "stairs", "title": title, "items": items})


def Q(text, question, answer, cue_answer):
    sc(text, {"type": "quiz", "q": question, "a": answer, "cueA": cue_answer})


# =====================================================================================
sc("""Hallo und willkommen zu *Gemeinschaftskunde*! In diesem Video gehen wir *alle neun Themen* deines Lernzettels durch,
und zum Schluss bekommst du noch *Prüfungstipps*, mit denen du die Punkte holst. Die Reihenfolge ist nach *Wichtigkeit* sortiert:
Die Themen *eins bis sechs* solltest du wirklich können. Die Themen *sieben bis neun* kamen seltener dran, da reicht es, wenn du sie einmal gut verstanden hast.
Ich erkläre dir alles in Ruhe, mit Beispielen, und zwischendurch stelle ich dir kurze Fragen. Also, los geht's.""", {"type": "kb"})

# ---------------------------------------------------------------- 1
thema("Demokratie und Wahlen")
T("""Thema eins: *Demokratie und Wahlen*. Das ist das wichtigste Thema überhaupt. Es kam in den letzten Jahren *sechsmal* in der Prüfung dran.""")
D("""Fangen wir mit dem Wort selbst an. *Demokratie* bedeutet *Volksherrschaft*. Das heißt: Nicht ein König oder ein Diktator bestimmt, sondern das *Volk*.
Und wie bestimmt das Volk? Durch *Wahlen* und *Abstimmungen*. Damit legt es fest, *wer regiert* und *was entschieden* wird.""",
  "Demokratie", "Volksherrschaft: Das Volk bestimmt durch Wahlen und Abstimmungen, wer regiert und was entschieden wird.")
C("""Jetzt gibt es zwei Arten, wie das Volk herrschen kann. Bei der *direkten* Demokratie entscheidet das Volk *selbst* über politische Themen, und zwar durch *Abstimmungen*.
Zum Beispiel: Die Bürger einer Stadt stimmen ab, ob ein neues *Stadion* gebaut wird. Bei der *indirekten* Demokratie, die nennt man auch *repräsentative* Demokratie,
wählt das Volk *Vertreter*, und die entscheiden dann für das Volk. So ist es in *Deutschland*: Die Bürger wählen den *Bundestag*, und der beschließt die Gesetze.
Merk dir den Unterschied ganz einfach: Direkt heißt, das Volk entscheidet *selbst*. Indirekt heißt, das Volk wählt *Politiker*, die entscheiden.""",
  "Direkte Demokratie", ["Volk entscheidet selbst", "durch Abstimmungen", "Bsp.: Stadion – ja oder nein?"],
  "Indirekte Demokratie", ["Volk wählt Vertreter", "die entscheiden für das Volk", "So ist es in Deutschland (Bundestag)"], "indirekten")
P("""Woran erkennst du, ob ein Land wirklich eine Demokratie ist? Das ist eine Lieblingsfrage in der Prüfung. Es gibt *sieben Merkmale*.
Erstens die *Volkssouveränität*: Die Macht kommt vom Volk. Zweitens *freie Wahlen*: Die Bürger wählen regelmäßig. Drittens die *Gewaltenteilung*: Die Macht ist verteilt, dazu gleich mehr.
Viertens die *Grundrechte*: Du darfst zum Beispiel deine Meinung sagen. Fünftens *mehrere Parteien*: Es gibt eine *Opposition*, die die Regierung kritisiert.
Sechstens der *Rechtsstaat*: Auch der Staat muss sich an die Gesetze halten. Und siebtens die *Pressefreiheit*: Die Medien dürfen frei berichten.
Fehlt eins davon, gibt es zum Beispiel nur eine Partei, dann ist es keine echte Demokratie.""",
  "Merkmale einer Demokratie", [it("Volkssouveränität – Macht kommt vom Volk", "Volkssouveränität"), it("Freie Wahlen – regelmäßig", "freie"),
                                it("Gewaltenteilung – Macht ist verteilt", "Gewaltenteilung"), it("Grundrechte – z. B. Meinung sagen", "Grundrechte"),
                                it("Mehrere Parteien – Opposition kritisiert", "mehrere"), it("Rechtsstaat – auch der Staat hält sich an Gesetze", "Rechtsstaat"),
                                it("Pressefreiheit – Medien berichten frei", "Pressefreiheit")])
TB("""Schauen wir uns die *Gewaltenteilung* genauer an. Die Idee: Die Macht im Staat wird auf *drei Bereiche* verteilt, damit *keiner zu viel Macht* hat.
Die *Legislative*, das sind *Bundestag und Bundesrat*. Die *machen* die Gesetze. Die *Exekutive*, das sind die *Regierung* und zum Beispiel die *Polizei*. Die *setzen* die Gesetze *um*.
Und die *Judikative*, das sind die *Gerichte*. Die *sprechen Recht*. Und *warum* das Ganze? Weil sich die drei *gegenseitig kontrollieren*. So wird *Machtmissbrauch* verhindert.
Ein Beispiel: Die Regierung macht ein Gesetz gegen das *Grundgesetz*. Dann *stoppt* es das *Bundesverfassungsgericht*. Die eine Gewalt bremst also die andere.""",
   "Gewaltenteilung", ["Gewalt", "Wer?", "Aufgabe"],
   [[["Legislative", "Bundestag, Bundesrat", "machen die Gesetze"], "Legislative"],
    [["Exekutive", "Regierung, Polizei", "setzen Gesetze um"], "Exekutive"],
    [["Judikative", "Gerichte", "sprechen Recht"], "Judikative"]],
   note="Kontrollieren sich gegenseitig → kein Machtmissbrauch")
D("""Und dann hörst du manchmal noch von einer *vierten Gewalt*. So nennt man die *Medien*. Warum? Weil sie die drei Gewalten *beobachten* und *kritisieren*.
Dazu kommen wir in Thema vier noch mal.""",
  "Vierte Gewalt", "So nennt man die Medien: Sie beobachten und kritisieren die drei Gewalten.")
P("""Jetzt zu den Wahlen. Damit eine Wahl in Deutschland *fair* ist, gibt es fünf *Wahlgrundsätze*. Die stehen im Grundgesetz, in *Artikel achtunddreißig*.
*Allgemein* heißt: *Jeder* darf wählen, egal ob arm oder reich, Mann oder Frau. *Unmittelbar* heißt: Du wählst *direkt*, ohne Zwischenpersonen.
*Frei* heißt: *Niemand* darf dich zwingen. Du entscheidest selbst, *ob* du wählst und *wen* du wählst. *Gleich* heißt: *Jede Stimme* zählt gleich viel.
Und *geheim* heißt: *Keiner* sieht, was du wählst. Deshalb gibt es die *Wahlkabine*.""",
  "Wahlgrundsätze (Art. 38 GG)", [it("allgemein – jeder darf wählen", "Allgemein"), it("unmittelbar – direkt, ohne Zwischenpersonen", "Unmittelbar"),
                                  it("frei – niemand zwingt dich (ob und wen)", "Frei"), it("gleich – jede Stimme zählt gleich viel", "Gleich"),
                                  it("geheim – keiner sieht es (Wahlkabine)", "geheim")])
Q("""Kurze Frage an dich: Dein Chef sagt dir, welche Partei du wählen sollst, sonst gibt es Ärger. Welcher Wahlgrundsatz wird da verletzt? Überleg kurz …
Richtig: der Grundsatz *frei*. Niemand darf dich zwingen, wen du wählst.""",
  "Dein Chef sagt dir, wen du wählen sollst. Welcher Wahlgrundsatz wird verletzt?", "frei – niemand darf dich zwingen", "Richtig")
C("""Bei der *Bundestagswahl* hast du *zwei Stimmen*. Mit der *Erststimme* wählst du eine *Person* aus deinem *Wahlkreis*, also einen Politiker aus deiner Gegend.
Mit der *Zweitstimme* wählst du eine *Partei*. Und jetzt die Frage, die oft kommt: Welche ist *wichtiger*? Die *Zweitstimme*!
Denn sie entscheidet, *wie viele Sitze* eine Partei bekommt. Also nicht verwirren lassen: Die Erststimme ist nicht die wichtigere, nur weil sie zuerst kommt.""",
  "Erststimme", ["eine Person", "aus deinem Wahlkreis"],
  "Zweitstimme", ["eine Partei", "entscheidet die Sitze", "→ wichtiger!"], "Zweitstimme")
BIG("""Dazu passt die *Fünfprozenthürde*. Eine Partei braucht *mindestens fünf Prozent* der *Zweitstimmen*, um in den Bundestag zu kommen.
*Warum* gibt es die? Stell dir vor, im Bundestag sitzen sehr viele kleine Parteien. Dann wird es schwer, überhaupt etwas zu beschließen.
Die Hürde sorgt also dafür, dass *nicht zu viele kleine Parteien* reinkommen und der Bundestag *arbeitsfähig* bleibt.""",
    "5 %", "Fünfprozenthürde", [it("mindestens 5 % der Zweitstimmen", "mindestens"), it("Warum? Nicht zu viele kleine Parteien – Bundestag bleibt arbeitsfähig", "nicht")])
P("""Ein Thema, das gerade dich betrifft: das *Wahlalter sechzehn*. Beim *Bundestag* darfst du erst ab *achtzehn* wählen.
In *Baden-Württemberg* darfst du aber bei der *Landtagswahl*, bei der *Kommunalwahl* und bei der *Europawahl* schon ab *sechzehn* wählen.""",
  "Wahlalter", [it("Bundestag: ab 18", "Bundestag"), it("Baden-Württemberg: Landtag, Kommune, Europa schon ab 16", "Baden-Württemberg")])
PRO("""Ist das gut? Dafür spricht: Erstens sind Jugendliche am *längsten betroffen* von den Entscheidungen, die heute getroffen werden.
Zweitens *interessieren* sie sich dann mehr für Politik. Und drittens *lernen* sie früh, wie Demokratie funktioniert.
Dagegen spricht: Manche sind vielleicht noch *nicht reif* genug. Sie lassen sich *leichter beeinflussen*, zum Beispiel über *TikTok*. Und viele *wissen* noch wenig über Politik.""",
    ["am längsten betroffen", "interessieren sich mehr", "lernen Demokratie früh"],
    ["manche noch nicht reif", "leichter beeinflussbar (TikTok)", "wissen noch wenig"], "Dagegen")
P("""Wählen ist aber nicht die einzige Möglichkeit, mitzumachen. Auch das kam schon öfter dran: Wie kann man sich *noch* politisch beteiligen?
Du kannst in eine *Partei* eintreten. Du kannst bei einer *Bürgerinitiative* mitmachen. Du kannst auf eine *Demo* gehen. Du kannst eine *Petition* unterschreiben.
In der Schule kannst du in der *SMV* mitmachen, oder in deiner Stadt im *Jugendgemeinderat*. Und du kannst deine *Meinung* in Social Media sagen.""",
  "Mitmachen außer Wählen", [it("in eine Partei eintreten", "Partei"), it("bei einer Bürgerinitiative mitmachen", "Bürgerinitiative"), it("auf eine Demo gehen", "Demo"),
                             it("eine Petition unterschreiben", "Petition"), it("SMV oder Jugendgemeinderat", "SMV"), it("Meinung in Social Media sagen", "Meinung")])
P("""Und wenn jemand sagt: Ich geh nicht wählen, bringt eh nichts? Dann hast du *zwei Argumente*. Erstens: Wer nicht wählt, lässt *andere* entscheiden, vielleicht auch *Extremisten*.
Zweitens: Es geht um *deine Zukunft*: um deine *Ausbildung*, deinen *Lohn* und deine *Rente*.""",
  "Nichtwähler überzeugen", [it("Wer nicht wählt, lässt andere entscheiden – vielleicht Extremisten", "andere"), it("Es geht um deine Zukunft: Ausbildung, Lohn, Rente", "Zukunft")])
PRO("""Eine Idee dagegen wäre die *Wahlpflicht*: *Jeder Bürger müsste* wählen gehen. Was spricht dafür? *Mehr Menschen* gehen wählen.
Das Ergebnis zeigt *besser*, was *alle* wollen. Und die Leute *beschäftigen* sich mehr mit Politik. Und was spricht dagegen? Der wichtigste Punkt:
Sie *widerspricht* dem Wahlgrundsatz *frei*. Erinnerst du dich? Frei heißt, du entscheidest selbst, *ob* du wählst. Außerdem wählen manche dann *ohne Ahnung* oder *ungültig*.
Und *Zwang* macht die Leute *unzufriedener* mit der Politik.""",
    ["mehr Menschen wählen", "Ergebnis zeigt besser, was alle wollen", "mehr Beschäftigung mit Politik"],
    ["widerspricht „frei“", "manche wählen ohne Ahnung oder ungültig", "Zwang macht unzufriedener"], "dagegen", "Wahlpflicht: Jeder Bürger müsste wählen.", "Wahlpflicht")
D("""Zum Schluss von Thema eins: der *Volksentscheid*. Da stimmen die Bürger *selbst* über eine politische Frage ab. Das ist also *direkte* Demokratie,
genau das Beispiel mit dem *Stadion* von vorhin. So etwas gibt es in *Gemeinden* und in *Bundesländern*.""",
  "Volksentscheid", "Die Bürger stimmen selbst über eine politische Frage ab (direkte Demokratie) – in Gemeinden und Bundesländern.")
PRO("""Dafür spricht: Die Bürger dürfen *selbst mitbestimmen*. Die Politiker müssen *mehr auf die Bürger hören*. Und die Bürger fühlen sich *ernst genommen*.
Dagegen spricht: Die Bürger entscheiden vielleicht *falsch*, weil ihnen *Wissen fehlt*. Sie können durch *falsche Infos* beeinflusst werden. Und Entscheidungen können *blockiert* werden.""",
    ["Bürger bestimmen selbst mit", "Politiker hören mehr auf Bürger", "Bürger fühlen sich ernst genommen"],
    ["vielleicht falsch – Wissen fehlt", "falsche Infos beeinflussen", "Entscheidungen können blockiert werden"], "Dagegen")
Q("""Noch eine Frage: Welche Stimme ist bei der Bundestagswahl wichtiger, die Erststimme oder die Zweitstimme? Überleg kurz …
Genau: die *Zweitstimme*. Sie wählt die Partei und entscheidet, wie viele Sitze die Partei bekommt.""",
  "Welche Stimme ist wichtiger – Erststimme oder Zweitstimme?", "Die Zweitstimme: Sie entscheidet, wie viele Sitze eine Partei bekommt.", "Genau")
M("""Das Merke zu Thema eins: Demokratie heißt, das *Volk* hat die Macht. Wahlen sind *allgemein, unmittelbar, frei, gleich und geheim*.
Und die *Zweitstimme* wählt die *Partei*, und sie ist *wichtiger*.""",
  "Demokratie = Das Volk hat die Macht. Wahlen: allgemein, unmittelbar, frei, gleich, geheim. Zweitstimme = Partei = wichtiger.")

# ---------------------------------------------------------------- 2
thema("Friedenssicherung")
T("""Thema zwei: *Friedenssicherung*. Das ist gerade sehr *aktuell*, Stichwort *neuer Wehrdienst*.""")
D("""Was heißt *Friedenssicherung*? *Kriege verhindern* und *Frieden erhalten*. Dafür gibt es drei wichtige Akteure, die du kennen musst:
die *UNO*, die *NATO* und die *Bundeswehr*. Alle drei schauen wir uns gleich an.""",
  "Friedenssicherung", "Kriege verhindern und Frieden erhalten. Dafür gibt es die UNO, die NATO und die Bundeswehr.")
P("""Aber erst mal: *Warum* gibt es überhaupt Kriege und Streit zwischen Ländern? Es gibt *sechs Ursachen*. Die *Wirtschaft*: Länder streiten um *Rohstoffe*, zum Beispiel um *Öl*.
Die *Psychologie*: Da geht es um *Vorurteile*, *Feindbilder* und die *Angst vor Machtverlust*. Die *Ideologie*: Die Länder haben ganz *unterschiedliche Werte* und Ansichten.
Die *Religion*: Religionen stehen in *Konkurrenz*. Der *Rassismus*: Andere Völker werden *abgewertet*. Und die *Umwelt*: zum Beispiel Streit um *Wasser*, wenn es eine *Dürre* gibt.""",
  "Ursachen von Konflikten", [it("Wirtschaft – Rohstoffe, z. B. Öl", "Wirtschaft"), it("Psychologie – Vorurteile, Feindbilder, Angst vor Machtverlust", "Psychologie"),
                              it("Ideologie – ganz unterschiedliche Werte", "Ideologie"), it("Religion – Religionen in Konkurrenz", "Religion"),
                              it("Rassismus – andere Völker abgewertet", "Rassismus"), it("Umwelt – Streit um Wasser (Dürre)", "Umwelt")])
D("""Eine besondere Form ist der *Terrorismus*. Das ist *Gewalt* durch *Gruppen*, also *nicht* durch Staaten. Die wollen *Angst verbreiten* und so ihre *politischen Ziele* durchsetzen.
Das bekannteste Beispiel sind die Anschläge vom *elften September zweitausendeins* in den *USA*. Seitdem gilt Terror als *neue weltweite Bedrohung*.""",
  "Terrorismus", "Gewalt durch Gruppen (nicht Staaten), um Angst zu verbreiten und politische Ziele durchzusetzen. Bsp.: 11. September 2001.")
D("""Kommen wir zu den Akteuren. Zuerst die *UNO*, auf Deutsch die *Vereinten Nationen*. Das ist eine Organisation, in der *fast alle Staaten* der Welt Mitglied sind.
Ihre wichtigste Aufgabe: den *Weltfrieden* sichern.""",
  "UNO (Vereinte Nationen)", "Fast alle Staaten der Welt sind Mitglied. Wichtigste Aufgabe: den Weltfrieden sichern.")
P("""Das wichtigste Gremium der UNO ist der *Sicherheitsrat*. Und da gibt es eine Besonderheit, die du unbedingt kennen musst: *Fünf Länder* haben dort ein *Vetorecht*.
Das sind die *USA*, *Russland*, *China*, *Großbritannien* und *Frankreich*. Veto heißt: Sagt *eins* davon *Nein*, dann wird *nichts* beschlossen.
Und genau das ist das Problem. Ein Beispiel: *Russland blockiert* Beschlüsse gegen den *Ukraine-Krieg*, weil es *selbst* angreift.""",
  "Sicherheitsrat", [it("5 mit Vetorecht: USA, Russland, China, Großbritannien, Frankreich", "Vetorecht"), it("Einer sagt Nein → nichts wird beschlossen", "Nein"),
                     it("Bsp.: Russland blockiert Beschlüsse zum Ukraine-Krieg", "blockiert")])
X("""Wie *hilft* die UNO konkret? Auf *vier Wegen*. Erstens: Sie *vermittelt* zwischen den Streitparteien. Zweitens: Sie beschließt *Sanktionen*, das sind *Strafen*,
zum Beispiel *Handelsverbote*. Drittens: Sie schickt *Blauhelme*, das sind die *Soldaten der UNO*. Und viertens: Sie leistet *humanitäre Hilfe*, also zum Beispiel *Essen* und *Medizin*.""",
  [it("vermitteln zwischen Streitparteien", "vermittelt"), it("Sanktionen (z. B. Handelsverbote)", "Sanktionen"), it("Blauhelme = UNO-Soldaten", "Blauhelme"),
   it("humanitäre Hilfe (Essen, Medizin)", "humanitäre")], "So hilft die UNO")
ST("""Für die Prüfung solltest du auch die *fünf Instrumente* der UNO kennen. Sie gehen der Reihe nach: Zuerst die *vorbeugende Diplomatie*, dann die *Friedensschaffung*,
die *Friedenserzwingung*, die *Friedenssicherung* und am Ende die *Friedenskonsolidierung*.""",
   "Die 5 Instrumente der UNO", [it("vorbeugende Diplomatie", "vorbeugende"), it("Friedensschaffung", "Friedensschaffung"), it("Friedenserzwingung", "Friedenserzwingung"),
                                 it("Friedenssicherung", "Friedenssicherung"), it("Friedenskonsolidierung", "Friedenskonsolidierung")])
D("""Neben der UNO gibt es die *OSZE*. Die kannst du dir als die *europäische UNO* merken. Sie hat die *gleichen Aufgaben*, aber eben *nur für Europa*.""",
  "OSZE", "Die „europäische UNO“: gleiche Aufgaben, aber nur für Europa.")
BIG("""Jetzt die *NATO*. Die ist etwas ganz anderes als die UNO. Die NATO ist ein *militärisches Verteidigungsbündnis* von *zweiunddreißig Staaten*, und Deutschland ist dabei.
Das Prinzip ist: *Einer für alle*. Wird *ein* Mitglied *angegriffen*, dann helfen *alle anderen*. Ein Beispiel: Greift jemand *Polen* an, dann muss auch *Deutschland* Polen *verteidigen*.""",
    "Einer für alle", "NATO – Verteidigungsbündnis, 32 Staaten", [it("Ein Mitglied angegriffen → alle helfen", "angegriffen"), it("Bsp.: Angriff auf Polen → Deutschland verteidigt mit", "Polen")])
P("""Und dann die *Bundeswehr*, die Armee von Deutschland. Sie hat *drei Aufgaben*: Erstens Deutschland und die *NATO-Partner verteidigen*. Zweitens *Auslandseinsätze*.
Und drittens *Hilfe bei Katastrophen*, zum Beispiel bei *Hochwasser*. Und dazu ein wichtiger Begriff: die *Parlamentsarmee*. Die Bundeswehr darf nur *bewaffnet ins Ausland*,
wenn der *Bundestag zustimmt*. Das entscheidet also das Parlament, das wir gewählt haben.""",
  "Bundeswehr", [it("Deutschland und NATO-Partner verteidigen", "Deutschland"), it("Auslandseinsätze", "Auslandseinsätze"), it("Hilfe bei Katastrophen, z. B. Hochwasser", "Hilfe")],
  note="Parlamentsarmee: bewaffnet ins Ausland nur, wenn der Bundestag zustimmt", cue_note="Parlamentsarmee")
C("""Zwei Begriffe, die man nicht verwechseln darf. Die *Wehrpflicht* heißt: *Junge Männer müssen* zur Bundeswehr. Die ist aber seit *zweitausendelf ausgesetzt*.
Und die *Kriegsdienstverweigerung* heißt: *Niemand muss gegen sein Gewissen* mit der *Waffe* kämpfen. Das steht im Grundgesetz, in *Artikel vier*.""",
  "Wehrpflicht", ["Junge Männer müssen zur Bundeswehr", "seit 2011 ausgesetzt"],
  "Kriegsdienstverweigerung", ["Niemand muss gegen sein Gewissen mit der Waffe kämpfen", "Art. 4 GG"], "Kriegsdienstverweigerung")
P("""Und jetzt das Aktuelle: der *neue Wehrdienst* seit *zweitausendsechsundzwanzig*. So funktioniert er: *Alle Achtzehnjährigen* bekommen einen *Fragebogen*.
*Männer müssen* ihn ausfüllen, für *Frauen* ist es *freiwillig*. Junge Männer müssen außerdem zur *Musterung*. Der *Dienst selbst* ist aber *freiwillig*:
mindestens *sechs Monate*, und man bekommt ungefähr *zweitausendsechshundert Euro* im Monat. Und jetzt kommt's: Melden sich *zu wenige*, dann *kann* der Bundestag eine *Wehrpflicht* beschließen.""",
  "Neuer Wehrdienst (seit 2026)", [it("Alle 18-Jährigen: Fragebogen (Männer Pflicht, Frauen freiwillig)", "Fragebogen"), it("Junge Männer: Musterung", "Musterung"),
                                   it("Dienst freiwillig: mind. 6 Monate, ca. 2.600 € im Monat", "Dienst"), it("Zu wenige? → Bundestag kann Wehrpflicht beschließen", "Melden")])
PRO("""Wäre eine Wehrpflicht gut? Dafür spricht: Deutschland ist *besser geschützt*, weil es *mehr Soldaten* gibt. *Alle* jungen Menschen leisten einen *Beitrag* für die Gesellschaft.
Und die Bundeswehr ist *näher* an der *normalen Bevölkerung*. Dagegen spricht: Sie greift in die *Freiheit* und die *Lebensplanung* ein. *Ausbildung* und *Studium* beginnen *später*,
dadurch fehlen *noch mehr Fachkräfte*. Und es ist *ungerecht*, wenn *nur Männer* müssen. Ein Tipp: Die *gleichen Argumente* passen auch zum *sozialen Pflichtjahr*.""",
    ["besser geschützt – mehr Soldaten", "alle leisten einen Beitrag", "Bundeswehr näher an der Bevölkerung"],
    ["greift in Freiheit und Lebensplanung ein", "Ausbildung später → mehr Fachkräftemangel", "ungerecht, wenn nur Männer müssen"], "Dagegen",
    "💡 Gleiche Argumente passen zum sozialen Pflichtjahr", "Tipp")
P("""Zum Schluss ein wichtiger Gedanke: *Frieden* ist *mehr* als nur *kein Krieg*. *Echten* Frieden gibt es erst mit *Gerechtigkeit*, *Wohlstand*, *Menschenrechten* und *Demokratie*,
und wenn Konflikte *ohne Gewalt* gelöst werden. Vorbilder dafür sind *Martin Luther King* und *Mahatma Gandhi*.""",
  "Frieden ohne Militär", [it("Frieden ist mehr als kein Krieg", "mehr"), it("Gerechtigkeit, Wohlstand, Menschenrechte, Demokratie", "Gerechtigkeit"),
                           it("Konflikte ohne Gewalt lösen", "ohne"), it("Vorbilder: Martin Luther King, Mahatma Gandhi", "Vorbilder")])
Q("""Kurze Frage: Was ist der Unterschied zwischen *UNO* und *NATO*? Überleg kurz … Also: Die *UNO* sichert den *Weltfrieden*, und fast alle Staaten sind dabei.
Die *NATO* ist ein *Verteidigungsbündnis*: Einer für alle.""",
  "Was ist der Unterschied zwischen UNO und NATO?", "UNO = Weltfrieden, fast alle Staaten · NATO = Verteidigungsbündnis, einer für alle", "Also")
M("""Das Merke zu Thema zwei: Die *UNO* sichert den *Weltfrieden*, aber das *Veto der fünf* kann alles blockieren. Die *NATO* heißt: *Einer für alle*.
Und bei der *Bundeswehr* entscheidet der *Bundestag*, und der Dienst ist *freiwillig*.""",
  "UNO = Weltfrieden, aber das Veto der 5 kann alles blockieren. NATO = einer für alle. Bundeswehr = Bundestag entscheidet, Dienst ist freiwillig.")

# ---------------------------------------------------------------- 3
thema("Globalisierung und Migration")
T("""Thema drei: *Globalisierung und Migration*. Auch das kam sehr oft dran, fünfmal in den letzten Jahren.""")
D("""Was ist *Globalisierung*? Schau mal auf dein *Handy*. Das wird in den *USA entwickelt*, die *Teile* kommen aus *vielen Ländern*, zusammengebaut wird es in *China*,
und verkauft wird es in *Deutschland*. Genau das ist Globalisierung: Die Länder der Welt sind immer *enger miteinander verbunden*. *Waren*, *Geld*, *Informationen* und *Menschen*
gehen um die ganze Welt. Und wenn du es in der Prüfung *prüfungsreif* schreiben willst, dann so: Globalisierung ist die *weltweite Verflechtung* von *Wirtschaft*, *Kommunikation*, *Kultur* und *Politik*.""",
  "Globalisierung", "Die weltweite Verflechtung von Wirtschaft, Kommunikation, Kultur und Politik.")
P("""Diese vier Wörter sind gleich die *vier Bereiche* der Globalisierung. *Wirtschaft*: Waren werden weltweit hergestellt und gehandelt, zum Beispiel ein *T-Shirt* aus *Bangladesch*.
*Kommunikation*: Nachrichten gehen in *Sekunden* um die Welt, zum Beispiel wenn du per *WhatsApp* mit Freunden in der *Türkei* schreibst.
*Kultur*: Überall gibt es *dieselben Marken*, Filme und Musik, denk an *Netflix* oder *McDonald's*. Und *Politik*: Probleme wie *Klimawandel*, *Pandemien* oder *Terror* betreffen *alle*.
Deshalb müssen die Länder *zusammenarbeiten*. Das Beispiel dafür ist *Corona*.""",
  "Bereiche der Globalisierung", [it("Wirtschaft – T-Shirt aus Bangladesch", "Wirtschaft"), it("Kommunikation – WhatsApp mit Freunden in der Türkei", "Kommunikation"),
                                  it("Kultur – Netflix, McDonald's", "Kultur"), it("Politik – Klimawandel, Pandemien, Terror (Corona)", "Politik")])
P("""*Warum* ist das alles überhaupt *möglich*? Drei Gründe. Erstens: *Transport* ist *billig* und *schnell*, denk an riesige *Containerschiffe* und *Flugzeuge*.
Zweitens: Das *Internet* verbindet alle. Und drittens: Viele Länder haben *Zölle abgebaut*. Das nennt man *Freihandel*.""",
  "Warum ist Globalisierung möglich?", [it("Transport billig und schnell (Containerschiffe, Flugzeuge)", "Transport"), it("Internet verbindet alle", "Internet"),
                                        it("Zölle abgebaut (Freihandel)", "Zölle")])
P("""Und *warum produzieren* Firmen im *Ausland*? Das ist ein *Dauerbrenner* in der Prüfung. Vier Gründe: *Niedrige Löhne*. *Weniger Regeln* für *Umwelt-* und *Arbeitsschutz*.
*Niedrigere Steuern*. Und *neue Kunden* direkt vor Ort. Das Beispiel dazu: Ein *T-Shirt* wird in *Bangladesch* genäht, weil die *Näherin* dort nur *ein paar Euro am Tag* verdient.""",
  "Warum produzieren Firmen im Ausland?", [it("niedrige Löhne", "Niedrige"), it("weniger Regeln für Umwelt- und Arbeitsschutz", "Weniger"),
                                           it("niedrigere Steuern", "Steuern"), it("neue Kunden direkt vor Ort", "neue")],
  note="Bsp.: T-Shirt aus Bangladesch – Näherin verdient ein paar Euro am Tag", cue_note="Näherin")
C("""Ist Globalisierung jetzt *gut* oder *schlecht*? Beides. Die *Chancen*: Waren werden *billiger* für die Kunden. Firmen finden *neue Märkte* und verkaufen mehr,
das ist gut für *Exportländer* wie *Deutschland*. Und *ärmere Länder* bekommen *Arbeitsplätze* und können sich *entwickeln*. Die *Risiken*: Erstens *Ausbeutung*,
also sehr *niedrige Löhne* und *schlechte Arbeitsbedingungen* in Billiglohnländern. Zweitens fallen *Arbeitsplätze bei uns* weg, weil die Produktion ins Ausland geht.
Und drittens leidet die *Umwelt*, und man wird *abhängig* von *Lieferketten*. Bei *Corona* zum Beispiel fehlten plötzlich Waren.""",
  "Chancen", ["Waren billiger", "neue Märkte (gut für Exportländer)", "Arbeitsplätze für ärmere Länder"],
  "Risiken", ["Ausbeutung in Billiglohnländern", "Arbeitsplätze bei uns fallen weg", "Umwelt leidet, Abhängigkeit von Lieferketten"], "Risiken")
C("""Daraus folgt: Wer *gewinnt*, und wer *verliert*? *Gewinner* sind die *großen Firmen*, die *Kunden*, weil sie billige Waren bekommen, und *Exportländer* wie Deutschland.
Die *Verlierer* sind die *Arbeiter* in *Billiglohnländern*, die *Arbeitnehmer hier*, deren Job ins Ausland geht, und die *Umwelt*.""",
  "Gewinner", ["große Firmen", "Kunden (billige Waren)", "Exportländer wie Deutschland"],
  "Verlierer", ["Arbeiter in Billiglohnländern", "Arbeitnehmer hier (Job geht ins Ausland)", "die Umwelt"], "Verlierer")
D("""Eng damit verbunden ist die *Nachhaltigkeit*. Nachhaltig heißt: So *leben* und *wirtschaften*, dass auch *spätere Generationen* noch *gut leben* können.
Ein Beispiel aus dem Alltag: *Kleidung länger tragen*, statt jede Saison neue zu kaufen.""",
  "Nachhaltigkeit", "So leben und wirtschaften, dass auch spätere Generationen noch gut leben können.")
P("""Was kann man *tun*? Da gibt es drei Ebenen. Du als *Verbraucher*: *fair gehandelte* Produkte kaufen, mit dem *Fairtrade-Siegel*, *weniger* kaufen und *Second Hand* kaufen.
Die *Firmen*: Sie achten auf *faire Löhne* und *Umweltschutz* bei ihren *Zulieferern*. Und die *Politik*: Sie macht *Gesetze*, zum Beispiel das *Lieferkettengesetz*.
Danach müssen *große Firmen* darauf achten, dass ihre Zulieferer die *Menschenrechte* einhalten.""",
  "Was kann man tun?", [it("Verbraucher: Fairtrade, weniger und Second Hand kaufen", "Verbraucher"), it("Firmen: faire Löhne und Umweltschutz bei Zulieferern", "Firmen"),
                        it("Politik: Lieferkettengesetz (Menschenrechte bei Zulieferern)", "Politik")])
D("""Jetzt zum zweiten Teil von Thema drei: *Migration*. Das bedeutet: Menschen *verlassen* ihre *Heimat* und ziehen *dauerhaft* in ein *anderes Land*.
Zum Beispiel: Eine Familie flieht vor dem *Krieg* aus *Syrien* nach *Deutschland*.""",
  "Migration", "Menschen verlassen ihre Heimat und ziehen dauerhaft in ein anderes Land.")
P("""*Warum* machen Menschen das? Die Ursachen sind: *Krieg*, *Verfolgung*, *Armut*, *Arbeitslosigkeit*, der *Klimawandel* mit *Dürren* und *Überschwemmungen*,
*bessere Bildung* und die *Familie*.""",
  "Ursachen von Migration", [it("Krieg, Verfolgung", "Krieg"), it("Armut, Arbeitslosigkeit", "Armut"), it("Klimawandel (Dürren, Überschwemmungen)", "Klimawandel"),
                             it("bessere Bildung, Familie", "bessere")])
C("""Diese Gründe kann man in *zwei Gruppen* sortieren. *Push-Faktoren*, Push heißt *drücken*. Das sind die *schlechten Gründe* im *Heimatland*, die einen *wegdrücken*.
Zum Beispiel: In *Syrien* herrscht *Krieg*. Und *Pull-Faktoren*, Pull heißt *ziehen*. Das sind die *guten Gründe* im *Zielland*, die einen *anziehen*.
Zum Beispiel: In *Deutschland* gibt es *Arbeit* und *Sicherheit*. Stell dir eine Tür vor: Von hinten *drückt* jemand, und von vorne *zieht* jemand.""",
  "Push-Faktoren (drücken weg)", ["schlechte Gründe im Heimatland", "Bsp.: In Syrien herrscht Krieg"],
  "Pull-Faktoren (ziehen an)", ["gute Gründe im Zielland", "Bsp.: In Deutschland gibt es Arbeit und Sicherheit"], "Pull-Faktoren")
P("""Und wie kann man *Vorurteile abbauen*? Vier Ideen: *Gemeinsame Projekte* in der *Schule* und im *Betrieb*. *Sprachkurse*. *Begegnung*, zum Beispiel im *Sportverein* oder bei *Festen*.
Und *Aufklärung* mit *Fakten* statt *Gerüchten*.""",
  "Vorurteile abbauen", [it("gemeinsame Projekte in Schule und Betrieb", "Gemeinsame"), it("Sprachkurse", "Sprachkurse"), it("Begegnung: Sportverein, Feste", "Begegnung"),
                         it("Aufklärung mit Fakten statt Gerüchten", "Aufklärung")])
Q("""Kurze Frage: Ist *Krieg im Heimatland* ein Push- oder ein Pull-Faktor? Überleg kurz … Richtig: ein *Push-Faktor*. Er *drückt* die Menschen weg.
*Arbeit* und *Sicherheit* im Zielland wären *Pull-Faktoren*.""",
  "Krieg im Heimatland – Push- oder Pull-Faktor?", "Push-Faktor: drückt weg. (Arbeit und Sicherheit im Zielland = Pull)", "Richtig")
M("""Das Merke zu Thema drei: Globalisierung heißt, die *Welt wächst zusammen*. *Firmen und Kunden gewinnen*, *Arbeiter und Umwelt verlieren*.
Und bei Migration: *Push drückt weg*, *Pull zieht an*.""",
  "Globalisierung = die Welt wächst zusammen. Firmen und Kunden gewinnen, Arbeiter und Umwelt verlieren. Migration: Push drückt weg, Pull zieht an.")

# ---------------------------------------------------------------- 4
thema("Medien und Social Media")
T("""Thema vier: *Medien und Social Media*.""")
D("""Was sind *Medien*? *Zeitung*, *Fernsehen*, *Radio* und *Internet*. In einer Demokratie sind sie *sehr wichtig*. Denn nur wer *informiert* ist, kann auch *mitreden*.
Die Grundlage dafür ist die *Pressefreiheit*. Die steht im Grundgesetz, in *Artikel fünf*.""",
  "Medien", "Zeitung, Fernsehen, Radio, Internet. Wichtig, damit die Bürger informiert mitreden können. Grundlage: Pressefreiheit (Art. 5 GG).")
X("""Medien haben *drei Aufgaben*. Erstens: *Information*. Sie berichten, was passiert. Zum Beispiel berichtet die *Tagesschau* über den neuen *Wehrdienst*.
Zweitens: *Meinungsbildung*. Sie zeigen *verschiedene Meinungen*, damit du dir deine *eigene* bilden kannst. Zum Beispiel eine *Talkshow* mit *Pro und Contra*.
Und drittens: *Kontrolle und Kritik*. Sie decken *Skandale* auf und kritisieren Politiker. Zum Beispiel: Zeitungen decken auf, dass ein Politiker *Geld angenommen* hat.""",
  [it("Information – Tagesschau berichtet", "Information"), it("Meinungsbildung – Talkshow mit Pro und Contra", "Meinungsbildung"),
   it("Kontrolle und Kritik – Skandale aufdecken", "Kontrolle")], "Die 3 Aufgaben der Medien")
D("""Und wegen dieser *Kontrolle* nennt man die Medien die *vierte Gewalt*. Das hatten wir in Thema eins schon kurz. Aber Achtung, das ist eine Fangfrage:
Die Medien sind *keine echte* Staatsgewalt. Denn sie werden *nicht gewählt* und dürfen *nichts entscheiden*.""",
  "Vierte Gewalt", "Medien kontrollieren die drei Staatsgewalten – sind aber keine echte Staatsgewalt: nicht gewählt, entscheiden nichts.")
C("""Jetzt zu *Social Media*, also dem, was du wahrscheinlich jeden Tag benutzt. Die *Vorteile*: Man bleibt *schnell in Kontakt* mit Freunden und Familie, auch *weltweit*.
Man bekommt *schnell Informationen* und kann seine *Meinung teilen*. Und man kann sich *politisch engagieren*, zum Beispiel *Petitionen teilen*.
Die *Nachteile*: *Fake News* und *Hass* verbreiten sich schnell. Es gibt die Gefahr von *Sucht*, *Stress* und *weniger echten Kontakten*.
Und der *Datenschutz*: Firmen *sammeln deine Daten*, das nennt man *Big Data*.""",
  "Vorteile", ["schnell in Kontakt, auch weltweit", "schnell informiert, Meinung teilen", "politisch engagieren (Petitionen)"],
  "Nachteile", ["Fake News und Hass", "Sucht, Stress, weniger echte Kontakte", "Datenschutz (Big Data)"], "Nachteile")
D("""Was sind *Fake News* genau? Das sind *absichtlich falsche* Nachrichten, die Menschen *täuschen* oder *beeinflussen* sollen. Wichtig ist das Wort *absichtlich*.
Ein aktuelles Beispiel: Ein *KI-Video* zeigt einen *Politiker*, der etwas sagt, was er *nie gesagt* hat.""",
  "Fake News", "Absichtlich falsche Nachrichten, die Menschen täuschen oder beeinflussen sollen. Bsp.: KI-Video eines Politikers.")
X("""Wie *erkennst* du Fake News? Erstens: *Quelle prüfen*. Wer hat das veröffentlicht? Zweitens: Berichten auch *andere seriöse Medien* darüber?
Drittens: Einen *Faktenchecker* nutzen. Und viertens: Bei sehr *schockierenden* Inhalten *besonders vorsichtig* sein.""",
  [it("Quelle prüfen", "Quelle"), it("Berichten andere seriöse Medien?", "andere"), it("Faktenchecker nutzen", "Faktenchecker"),
   it("Bei Schockierendem vorsichtig sein", "schockierenden")], "Fake News erkennen")
C("""Zwei Begriffe, die zusammengehören, aber *gegeneinander* arbeiten. *Big Data* heißt: Firmen sammeln *riesige Mengen* an Daten über die Nutzer, zum Beispiel um *Werbung* genau anzupassen.
*Datenschutz* heißt: der *Schutz* deiner *persönlichen Daten*. Das ist ein *Gegensatz*: Die Firmen wollen *viele* Daten, du willst deine Daten *schützen*.
Das kennst du bestimmt: Du suchst *einmal* nach *Sneakern*, und danach bekommst du *überall Sneaker-Werbung*.""",
  "Big Data", ["Firmen sammeln riesige Datenmengen", "z. B. für passende Werbung"],
  "Datenschutz", ["Schutz deiner persönlichen Daten", "→ Gegensatz zu Big Data"], "Datenschutz",
  "Bsp.: einmal Sneaker gesucht → überall Sneaker-Werbung", "Sneakern")
D("""Ein ernstes Thema: *Extremismus*. Das bedeutet: Man *lehnt* die *Demokratie* und das *Grundgesetz ab* und will sie *abschaffen*, oft auch mit *Gewalt*.""",
  "Extremismus", "Man lehnt die Demokratie und das Grundgesetz ab und will sie abschaffen, oft auch mit Gewalt.")
P("""Es gibt *drei Formen*. Der *Rechtsextremismus*: Da heißt es, Menschen seien *nicht gleich viel wert*, zum Beispiel wegen ihrer *Herkunft*. Das Ziel ist ein Staat *ohne Demokratie*.
Der *Linksextremismus*: Er will den *Staat* und den *Kapitalismus abschaffen*. Und der *religiöse Extremismus*, zum Beispiel der *Islamismus*: Da sollen *religiöse Regeln über den Gesetzen* stehen.
Und warum gehört das zum Thema Medien? Weil Extremisten *gezielt* auf *TikTok* und Co. werben, oft *versteckt* in *harmlos wirkenden Lifestyle-Videos*.""",
  "Formen von Extremismus", [it("Rechtsextremismus – Menschen angeblich nicht gleich viel wert; Staat ohne Demokratie", "Rechtsextremismus"),
                             it("Linksextremismus – Staat und Kapitalismus abschaffen", "Linksextremismus"),
                             it("Religiöser Extremismus (z. B. Islamismus) – religiöse Regeln über Gesetzen", "religiöse")],
  note="Werben gezielt auf TikTok & Co. – oft versteckt in Lifestyle-Videos", cue_note="gezielt")
P("""Was heißt also *verantwortungsvoll* mit Social Media umgehen? Erstens: *Bildschirmzeit begrenzen*, zum Beispiel mit einem *Handy-Timer* oder *handyfreien Zeiten*.
Zweitens: *Quellen prüfen*, *bevor* man etwas teilt. Drittens: *Hass* und *Fake News melden*. Und viertens: In der Schule *Workshops* zur *Medienkompetenz* machen.""",
  "Verantwortungsvoll mit Social Media", [it("Bildschirmzeit begrenzen (Timer, handyfreie Zeiten)", "Bildschirmzeit"), it("Quellen prüfen, bevor man teilt", "Quellen"),
                                          it("Hass und Fake News melden", "Hass"), it("Workshops zu Medienkompetenz", "Workshops")])
PRO("""Und dann noch eine *aktuelle* Diskussion: *Social Media erst ab sechzehn*? Gerade wird diskutiert, Social Media für *Kinder unter sechzehn* zu *verbieten*.
Dafür spricht: Kinder sind *besser geschützt* vor *Sucht* und *Stress*. Es gibt *weniger Mobbing* und *gefährliche Inhalte*. Und sie haben *mehr Zeit* für *echte Kontakte*, *Sport* und *Schule*.
Dagegen spricht: Es ist *schwer zu kontrollieren*, Kinder *umgehen* es einfach. Kinder werden von *Infos* und vom *Kontakt* zu Freunden *ausgeschlossen*.
Und *besser* wäre es, den *richtigen Umgang* zu *lernen*, statt zu *verbieten*.""",
    ["besser geschützt vor Sucht und Stress", "weniger Mobbing, gefährliche Inhalte", "mehr Zeit für Kontakte, Sport, Schule"],
    ["schwer zu kontrollieren", "von Infos und Freunden ausgeschlossen", "besser: richtigen Umgang lernen"], "Dagegen",
    "Social Media erst ab 16?", "Social")
Q("""Kurze Frage: Warum sind die Medien *keine echte* Staatsgewalt, obwohl man sie vierte Gewalt nennt? Überleg kurz … Genau: Sie werden *nicht gewählt* und dürfen *nichts entscheiden*.""",
  "Warum sind Medien keine echte Staatsgewalt?", "Sie werden nicht gewählt und dürfen nichts entscheiden.", "Genau")
M("""Das Merke zu Thema vier: Medien *informieren*, helfen bei der *Meinungsbildung* und *kontrollieren*. Social Media ist *schnell* und *vernetzt*,
aber es gibt *Fake News*, *Sucht* und das Problem mit den *Daten*.""",
  "Medien = informieren, Meinung bilden, kontrollieren. Social Media: schnell und vernetzt, aber Fake News, Sucht und Daten.")

# ---------------------------------------------------------------- 5
thema("Europäische Union (EU)")
T("""Thema fünf: die *Europäische Union*, kurz *EU*.""")
D("""Die *EU* ist ein *Zusammenschluss* von *siebenundzwanzig* europäischen Ländern. Die arbeiten *eng zusammen*, zum Beispiel beim *Handel*, beim *Geld* und bei *Gesetzen*.
Und *warum* hat man das gemacht? Das *Ziel* nach dem *Zweiten Weltkrieg* war: *Frieden* und *Wohlstand* in Europa.""",
  "EU", "Zusammenschluss von 27 europäischen Ländern (Handel, Geld, Gesetze). Ziel nach dem 2. Weltkrieg: Frieden und Wohlstand.")
P("""Die EU ist nicht auf einmal entstanden, sondern *Schritt für Schritt*. Wenn die Länder *immer enger* zusammenarbeiten, nennt man das *Vertiefung*. Die wichtigsten Etappen:
*Neunzehnhundertsiebenundfünfzig* die *Römischen Verträge*: *Sechs Länder* gründen die Gemeinschaft, auch *Deutschland*. *Neunzehnhundertachtundsechzig* die *Zollunion*:
*keine Zölle* mehr zwischen den Ländern. *Neunzehnhundertdreiundneunzig* der *Binnenmarkt* mit den *vier Freiheiten*: *Waren*, *Personen*, *Dienstleistungen* und *Geld*
dürfen *frei* über die Grenzen.""",
  "Vertiefung = immer enger zusammenarbeiten", [it("1957 Römische Verträge – 6 Länder gründen, auch Deutschland", "Römischen"),
                                                it("1968 Zollunion – keine Zölle mehr", "Zollunion"),
                                                it("1993 Binnenmarkt – 4 Freiheiten: Waren, Personen, Dienstleistungen, Geld", "Binnenmarkt")], label="Wichtige Etappen")
P("""Im selben Jahr, also auch *neunzehnhundertdreiundneunzig*, kam der *Vertrag von Maastricht*: Damit wurde die *EU gegründet*. *Neunzehnhundertfünfundneunzig* kam *Schengen*:
*keine Grenzkontrollen* mehr. *Zweitausendzwei* der *Euro* als *Bargeld*. Und *zweitausendneun* der *Vertrag von Lissabon*: *neue Regeln* und *mehr Rechte* für das *Parlament*.""",
  "Vertiefung = immer enger zusammenarbeiten", [it("1993 Vertrag von Maastricht – Gründung der EU", "Maastricht"), it("1995 Schengen – keine Grenzkontrollen", "Schengen"),
                                                it("2002 Euro als Bargeld", "Euro"), it("2009 Vertrag von Lissabon – mehr Rechte fürs Parlament", "Lissabon")],
  label="Wichtige Etappen")
C("""Das Gegenstück zur Vertiefung ist die *Erweiterung*. Das heißt: Es kommen *mehr Mitglieder* dazu. Von *sechs* Ländern im Jahr neunzehnhundertsiebenundfünfzig auf heute *siebenundzwanzig*.
Der *größte Schritt* war *zweitausendvier*: Da kamen *zehn Länder* dazu, vor allem aus *Osteuropa*, zum Beispiel *Polen*. Und es ging auch mal in die andere Richtung:
*Zweitausendzwanzig* ist *Großbritannien ausgetreten*, das nennt man den *Brexit*.""",
  "Vertiefung", ["immer enger zusammenarbeiten", "Zollunion, Binnenmarkt, Euro …"],
  "Erweiterung", ["mehr Mitglieder: von 6 auf 27", "2004: +10 Länder (v. a. Osteuropa)", "2020: Brexit"], "Erweiterung")
TB("""Jetzt ein *Dauerbrenner*: die *Organe* der EU. Es gibt *vier*. Der *Europäische Rat*, das sind die *Regierungschefs* der Länder. Er gibt die *Richtung* der EU vor.
Die *EU-Kommission*: *siebenundzwanzig Kommissare*, *einer pro Land*. Sie macht die *Gesetzesvorschläge*. Der *Rat der EU*, auch *Ministerrat* genannt:
Das sind die *Fachminister* der Länder. Er *beschließt* die Gesetze zusammen mit dem Parlament. Und das *Europäische Parlament*: *siebenhundertzwanzig Abgeordnete*,
von den Bürgern *direkt gewählt*, in Deutschland schon ab *sechzehn*. Es *beschließt* die Gesetze *mit* und *kontrolliert* die *Kommission*.
Achtung, Verwechslungsgefahr: *Europäischer Rat* und *Rat der EU* klingen fast gleich. Merk dir: Beim Europäischen Rat sitzen die *Chefs*, beim Rat der EU die *Minister*.""",
   "Organe der EU", ["Organ", "Wer?", "Aufgabe"],
   [[["Europäischer Rat", "Regierungschefs", "Richtung vorgeben"], "Europäische"],
    [["Kommission", "27 Kommissare", "Gesetze vorschlagen"], "EU-Kommission"],
    [["Rat der EU", "Fachminister", "Gesetze beschließen"], "Ministerrat"],
    [["Parlament", "720 gewählte Abgeordnete", "Gesetze beschließen, kontrollieren"], "siebenhundertzwanzig"]])
X("""Wie *entsteht* ein EU-Gesetz? In *drei Schritten*. Erstens: Die *Kommission* macht einen *Vorschlag*. Zweitens: *Parlament* und *Rat beraten* und *ändern*.
Drittens: *Beide* müssen *zustimmen*. Genau so ist zum Beispiel das *KI-Gesetz* der EU entstanden.""",
  [it("Kommission macht einen Vorschlag", "Kommission"), it("Parlament und Rat beraten und ändern", "Parlament"), it("Beide müssen zustimmen (Bsp.: KI-Gesetz)", "Beide")],
  "So entsteht ein EU-Gesetz")
C("""Ist die EU eigentlich *demokratisch*? Es hat sich viel *verbessert*: Das Parlament darf heute *viel mitentscheiden* und muss dem *Haushalt* und der *Kommission zustimmen*.
Aber es gibt noch *Schwächen*: Das Parlament darf *keine Gesetze vorschlagen*. Und der *Rat* wird *kaum kontrolliert*.""",
  "Verbessert", ["Parlament entscheidet viel mit", "muss Haushalt und Kommission zustimmen"],
  "Noch Schwächen", ["Parlament darf keine Gesetze vorschlagen", "Rat wird kaum kontrolliert"], "Schwächen")
P("""Was hast *du* im Alltag von der EU? Ganz schön viel. Du kannst *reisen* ohne *Grenzkontrollen* und ohne *Geld wechseln*, dank *Euro*. Du kannst *überall* in der EU *arbeiten* und *studieren*.
Es gibt *keine Roaming-Gebühren* mehr fürs Handy. Waren werden *billiger* durch den *Binnenmarkt*. Wir haben *Frieden* in Europa seit *vielen Jahrzehnten*.
Und *Verbraucherschutz*: Zum Beispiel gibt es jetzt ein *einheitliches Ladekabel*, nämlich *USB-C*.""",
  "Vorteile der EU im Alltag", [it("Reisen ohne Grenzkontrollen und Geldwechsel (Euro)", "reisen"), it("überall arbeiten und studieren", "überall"),
                                it("keine Roaming-Gebühren", "keine"), it("billigere Waren (Binnenmarkt)", "billiger"),
                                it("Frieden seit vielen Jahrzehnten", "Frieden"), it("Verbraucherschutz, z. B. USB-C-Ladekabel", "Verbraucherschutz")])
P("""Aber die EU hat auch *Herausforderungen*. Die Länder haben *unterschiedliche Interessen* und *einigen sich schwer*. Es gibt *Streit* um die *Verteilung* von *Flüchtlingen*.
Die *Sicherheit* ist ein Thema wegen des *Kriegs* in der *Ukraine*. Manche Länder haben *hohe Schulden* oder sind *ärmer* als andere. Und *EU-Gegner* und *Populisten* werden *stärker*.""",
  "Herausforderungen der EU", [it("unterschiedliche Interessen – schwer zu einigen", "unterschiedliche"), it("Streit um Verteilung von Flüchtlingen", "Streit"),
                               it("Sicherheit (Krieg in der Ukraine)", "Sicherheit"), it("hohe Schulden, ärmere Länder", "hohe"),
                               it("EU-Gegner und Populisten werden stärker", "EU-Gegner")])
Q("""Kurze Frage: Wer *schlägt* in der EU die Gesetze *vor*? Überleg kurz … Richtig: die *Kommission*. *Parlament* und *Rat* beschließen sie dann.""",
  "Wer schlägt in der EU die Gesetze vor?", "Die Kommission. Parlament und Rat beschließen.", "Richtig")
M("""Das Merke zu Thema fünf: Die EU, das sind *siebenundzwanzig Länder*. Die *Kommission schlägt vor*, *Parlament und Rat beschließen*.""",
  "EU = 27 Länder. Kommission schlägt vor, Parlament und Rat beschließen.")

# ---------------------------------------------------------------- 6
thema("Demografischer Wandel und Fachkräftemangel")
T("""Thema sechs: *Demografischer Wandel und Fachkräftemangel*.""")
D("""*Demografischer Wandel*, das klingt kompliziert, ist aber ganz einfach: Die *Bevölkerung verändert sich*, vor allem beim *Alter*, bei den *Geburten* und bei den *Sterbefällen*.
Prüfungsreif formuliert: Der demografische Wandel bezeichnet die *Entwicklung der Bevölkerung* in Bezug auf *Altersstruktur*, *Geburtenzahl* und *Sterbefälle*.""",
  "Demografischer Wandel", "Die Entwicklung der Bevölkerung in Bezug auf Altersstruktur, Geburtenzahl und Sterbefälle.")
P("""Und was passiert in *Deutschland*? Erstens: Seit den *Siebzigerjahren* werden *weniger Kinder geboren*, als Menschen *sterben*. Zweitens: Die Menschen *leben länger*,
die *Lebenserwartung* ist höher. Und drittens, daraus folgt: Es gibt *immer mehr Ältere* und *immer weniger Junge*.
Ein Beispiel: Früher kamen auf *einen Rentner viele Arbeitnehmer*. Heute sind es nur noch *etwa zwei*.""",
  "Was passiert in Deutschland?", [it("seit den 1970ern: weniger Geburten als Sterbefälle", "Siebzigerjahren"), it("Menschen leben länger", "leben"),
                                   it("mehr Ältere, weniger Junge", "drittens")],
  note="Früher viele Arbeitnehmer pro Rentner – heute nur noch etwa zwei", cue_note="Früher")
D("""Warum ist das ein Problem? Dafür musst du den *Generationenvertrag* verstehen. Der funktioniert so: Die *Jungen* zahlen mit ihren *Beiträgen* die *Rente* der *Alten*.
Und *später*, wenn du alt bist, zahlen die *nächsten Jungen* deine Rente.""",
  "Generationenvertrag", "Die Jungen zahlen mit ihren Beiträgen die Rente der Alten. Später zahlen die nächsten Jungen ihre Rente.")
X("""Jetzt siehst du das Problem. Es gibt *drei Auswirkungen*. Erstens die *Rente*: *Weniger Junge* müssen für *mehr Rentner* zahlen. Dadurch *steigen die Beiträge*,
und man geht *später* in Rente, mit *siebenundsechzig*, vielleicht sogar mit *siebzig*. Zweitens *Gesundheit und Pflege*: Mehr *ältere* Menschen brauchen *Ärzte* und *Pflege*.
Dadurch steigen die *Kosten* und die *Beiträge* für die *Kranken-* und *Pflegeversicherung*. Und drittens der *Fachkräftemangel*: Es fehlen *Arbeitskräfte*,
vor allem in der *Pflege*, in der *Kita*, im *Handwerk* und im Bereich *Elektro*.""",
  [it("Rente: höhere Beiträge, später in Rente (67, vielleicht 70)", "Rente"), it("Gesundheit & Pflege: höhere Kosten und Beiträge", "Gesundheit"),
   it("Fachkräftemangel: Pflege, Kita, Handwerk, Elektro", "Fachkräftemangel")], "Auswirkungen")
P("""Wie merkst du den Fachkräftemangel im *Alltag*? Man *wartet lange* auf einen *Handwerker* oder *Elektriker*. Es gibt *zu wenig Pflegeplätze* für Oma und Opa.
Es fehlen *Kitaplätze* und *Erzieher*. Und jetzt die gute Nachricht für *dich als Elektroniker*: Du hast einen *sicheren Job* und *gute Chancen* auf *mehr Lohn*.""",
  "Fachkräftemangel im Alltag", [it("lange Wartezeit auf Handwerker / Elektriker", "wartet"), it("zu wenig Pflegeplätze", "zu"),
                                 it("zu wenig Kitaplätze und Erzieher", "Kitaplätze"), it("Für dich: sicherer Job, gute Chancen auf mehr Lohn", "dich")])
P("""Was sind die *Lösungen*? Auch das ist ein Dauerbrenner. Sechs Ideen. Erstens: *Zuwanderung* von *Fachkräften* aus dem Ausland. Zweitens: *Familien fördern*,
mit *mehr Kitaplätzen*, *mehr Kindergeld* und *Elternzeit* für *beide*. Drittens: *Flexible Arbeit*, also *Homeoffice* und *Teilzeit*, damit *Eltern* arbeiten können.
Viertens: Die *Ausbildung attraktiver* machen, mit *besserer Bezahlung* und *mehr Werbung*. Fünftens: *Ältere* länger arbeiten lassen.
Und sechstens: *Technik* und *KI* übernehmen *einfache Aufgaben*.""",
  "Lösungen", [it("Zuwanderung von Fachkräften", "Zuwanderung"), it("Familien fördern: Kitas, Kindergeld, Elternzeit für beide", "Familien"),
               it("flexible Arbeit: Homeoffice, Teilzeit", "Flexible"), it("Ausbildung attraktiver: Bezahlung, Werbung", "Ausbildung"),
               it("Ältere länger arbeiten lassen", "Ältere"), it("Technik und KI für einfache Aufgaben", "Technik")])
Q("""Kurze Frage: Warum steigen durch den demografischen Wandel die *Rentenbeiträge*? Überleg kurz … Genau: wegen des *Generationenvertrags*.
*Weniger Junge* müssen die Rente für *mehr Alte* bezahlen.""",
  "Warum steigen die Rentenbeiträge?", "Generationenvertrag: Weniger Junge müssen die Rente für mehr Alte zahlen.", "Genau")
M("""Das Merke zu Thema sechs: *Weniger Geburten* plus *länger leben* ergibt *mehr Alte* und *weniger Junge*. Das macht Probleme bei der *Rente*, bei der *Pflege* und bei den *Fachkräften*.""",
  "Weniger Geburten + länger leben = mehr Alte, weniger Junge. Probleme bei Rente, Pflege und Fachkräften.")

# ---------------------------------------------------------------- 7
thema("Grundrechte und Rechtsstaat")
T("""Ab jetzt kommen die Themen sieben bis neun. Die kamen seltener dran, aber du solltest sie verstanden haben. Thema sieben: *Grundrechte und Rechtsstaat*.""")
D("""*Grundrechte* sind die *wichtigsten Rechte* jedes Menschen *gegenüber dem Staat*. Sie stehen in den *Artikeln eins bis neunzehn* des *Grundgesetzes*.
Und das allerwichtigste steht ganz vorne, in *Artikel eins*: *Die Würde des Menschen ist unantastbar*.""",
  "Grundrechte", "Die wichtigsten Rechte jedes Menschen gegenüber dem Staat (Art. 1–19 GG). Art. 1: Die Würde des Menschen ist unantastbar.")
TB("""Die Grundrechte kann man in *drei Gruppen* einteilen. Die *Abwehrrechte* schützen dich *vor dem Staat*: Der Staat darf sich *nicht einmischen*.
Zum Beispiel die *Meinungsfreiheit*: Der Staat darf dich *nicht bestrafen*, weil du die *Regierung kritisierst*. Weitere sind die *Glaubensfreiheit* und die *Unverletzlichkeit der Wohnung*.
Dann die *Beteiligungsrechte*: Du darfst beim Staat *mitmachen*. Zum Beispiel das *Wahlrecht* oder die *Versammlungsfreiheit*, also Demos.
Und die *Anspruchsrechte*: Du darfst etwas *vom Staat verlangen*. Zum Beispiel den *Schutz der Familie* oder das Recht, *vor Gericht zu gehen*.""",
   "Arten von Grundrechten", ["Art", "Bedeutung", "Beispiele"],
   [[["Abwehrrechte", "Staat darf sich nicht einmischen", "Meinungs-, Glaubensfreiheit, Wohnung"], "Abwehrrechte"],
    [["Beteiligungsrechte", "beim Staat mitmachen", "Wahlrecht, Versammlungsfreiheit"], "Beteiligungsrechte"],
    [["Anspruchsrechte", "etwas vom Staat verlangen", "Schutz der Familie, vor Gericht gehen"], "Anspruchsrechte"]])
C("""Dann gibt es noch den Unterschied zwischen *Menschenrechten* und *Bürgerrechten*. Menschenrechte gelten für *jeden Menschen*, sogar für Leute, die das *Grundgesetz ablehnen*.
Bürgerrechte gelten *nur für Deutsche*, zum Beispiel die *Versammlungsfreiheit* oder die *freie Berufswahl*. Ein Beispiel aus der *Prüfung*:
Auch ein *Extremist* hat ein Recht auf ein *faires Gerichtsverfahren*.""",
  "Menschenrechte", ["für jeden Menschen", "auch für Gegner des Grundgesetzes"],
  "Bürgerrechte", ["nur für Deutsche", "z. B. Versammlungsfreiheit, freie Berufswahl"], "nur",
  "Prüfung: Auch ein Extremist hat ein Recht auf ein faires Gerichtsverfahren.", "Extremist")
P("""Und was ist ein *Rechtsstaat*? In einem Rechtsstaat muss sich *auch der Staat* an die *Gesetze* halten. Dafür sorgen drei Dinge: Die *Grundrechte* schützen die Bürger.
*Unabhängige Gerichte* kontrollieren den Staat. Und die *Gewaltenteilung* verhindert *Machtmissbrauch*. Ein Beispiel: Die *Polizei* darf deine *Wohnung* nur mit einem *Beschluss*
vom *Gericht* durchsuchen.""",
  "Rechtsstaat: Auch der Staat hält sich an Gesetze", [it("Grundrechte schützen die Bürger", "Grundrechte"), it("unabhängige Gerichte kontrollieren den Staat", "Unabhängige"),
                                                       it("Gewaltenteilung verhindert Machtmissbrauch", "Gewaltenteilung")],
  note="Bsp.: Wohnungsdurchsuchung nur mit Gerichtsbeschluss", cue_note="Polizei")
Q("""Kurze Frage: Du gehst auf eine *Demo*. Welche Art von Grundrecht nutzt du da? Überleg kurz … Richtig: ein *Beteiligungsrecht*. Du machst beim Staat *mit*.""",
  "Du gehst auf eine Demo. Welche Art von Grundrecht ist das?", "Ein Beteiligungsrecht (Versammlungsfreiheit).", "Richtig")
M("""Das Merke zu Thema sieben, mit drei kurzen Sätzen: *Abwehr* heißt: Staat, bleib weg. *Beteiligung* heißt: Ich mach mit. Und *Anspruch* heißt: Staat, hilf mir.""",
  "Abwehr = Staat, bleib weg. Beteiligung = ich mach mit. Anspruch = Staat, hilf mir.")

# ---------------------------------------------------------------- 8
thema("Parteien und Verbände")
T("""Thema acht: *Parteien und Verbände*.""")
D("""Eine *Partei* ist eine *Gruppe von Bürgern* mit *ähnlichen politischen Zielen*. Und das Entscheidende: Sie will bei *Wahlen gewinnen* und *regieren*.""",
  "Partei", "Eine Gruppe von Bürgern mit ähnlichen politischen Zielen. Sie will bei Wahlen gewinnen und regieren.")
P("""Die Aufgaben der Parteien stehen im Grundgesetz, in *Artikel einundzwanzig*. Es sind *fünf*. Erstens: Bürger können über Parteien *politisch mitmachen*.
Zweitens: Sie *vertreten* die *Interessen* ihrer Mitglieder. Drittens: Sie helfen den Bürgern, sich eine *politische Meinung* zu bilden.
Viertens: Sie stellen *Kandidaten* für Wahlen auf. Und fünftens: Sie wollen *regieren* und *Verantwortung* übernehmen.""",
  "Aufgaben der Parteien (Art. 21 GG)", [it("Bürger können politisch mitmachen", "mitmachen"), it("Interessen der Mitglieder vertreten", "vertreten"),
                                         it("bei der Meinungsbildung helfen", "Meinung"), it("Kandidaten für Wahlen aufstellen", "Kandidaten"),
                                         it("regieren, Verantwortung übernehmen", "regieren")])
C("""Neben den Parteien gibt es noch *Verbände* und *Bürgerinitiativen*. Ein Verband heißt: *Viele Menschen* mit *gleichen Interessen* schließen sich zusammen.
Zum Beispiel eine *Gewerkschaft*, der *ADAC* oder ein *Umweltverband*. Eine Bürgerinitiative heißt: Bürger *kämpfen gemeinsam* für ein *bestimmtes Ziel*.
Zum Beispiel: *Anwohner* kämpfen gegen eine *neue Straße* im Wohngebiet.""",
  "Verband", ["viele Menschen mit gleichen Interessen", "Bsp.: Gewerkschaft, ADAC, Umweltverband"],
  "Bürgerinitiative", ["Bürger kämpfen gemeinsam für ein Ziel", "Bsp.: Anwohner gegen neue Straße"], "kämpfen")
C("""Und jetzt der *wichtigste Unterschied*, der in der Prüfung gefragt wird: Parteien wollen *regieren*. Verbände und Bürgerinitiativen dagegen nehmen *nicht an Wahlen teil*
und wollen *nicht regieren*. Sie wollen *nur Einfluss nehmen*.""",
  "Parteien", ["nehmen an Wahlen teil", "wollen regieren"],
  "Verbände & Bürgerinitiativen", ["nicht an Wahlen", "wollen nur Einfluss nehmen"], "Verbände")
X("""Wie nehmen Verbände *Einfluss*? Vier Wege. Erstens *Lobbyarbeit*: Sie führen *Gespräche* mit *Politikern*. Zweitens *Öffentlichkeitsarbeit*: *Kampagnen*, *Social Media*, *Plakate*.
Drittens *Demos* und *Petitionen*, also *Unterschriften sammeln*. Und viertens liefern sie *Fachwissen* und *Gutachten* für die Politik.""",
  [it("Lobbyarbeit – Gespräche mit Politikern", "Lobbyarbeit"), it("Öffentlichkeitsarbeit – Kampagnen, Social Media, Plakate", "Öffentlichkeitsarbeit"),
   it("Demos und Petitionen", "Demos"), it("Fachwissen und Gutachten", "Fachwissen")], "So nehmen Verbände Einfluss")
Q("""Kurze Frage: Ist der *ADAC* eine Partei oder ein Verband? Überleg kurz … Richtig: ein *Verband*. Er will *Einfluss* nehmen, aber *nicht regieren*.""",
  "Ist der ADAC eine Partei oder ein Verband?", "Ein Verband: Er will Einfluss nehmen, aber nicht regieren.", "Richtig")
M("""Das Merke zu Thema acht: *Parteien* wollen *regieren*. *Verbände* und *Bürgerinitiativen* wollen *nur Einfluss nehmen*.""",
  "Parteien wollen regieren. Verbände und Bürgerinitiativen wollen nur Einfluss nehmen.")

# ---------------------------------------------------------------- 9
thema("Familie, Männer und Frauen")
T("""Thema neun: *Familie, Männer und Frauen*.""")
D("""Die *Familie* ist die *beständigste Form* des *Zusammenlebens*. Und sie steht unter dem *Schutz* des *Grundgesetzes*, in *Artikel sechs*.""",
  "Familie", "Die beständigste Form des Zusammenlebens. Steht unter dem Schutz des Grundgesetzes (Art. 6).")
P("""Heute gibt es *verschiedene Familienformen*. Die *traditionelle*: Mutter, Vater, Kinder. *Alleinerziehende*: ein Elternteil mit Kind. *Gleichgeschlechtliche Paare* mit Kindern.
Und die *Patchworkfamilie*: Da leben Kinder aus *früheren Beziehungen* zusammen.""",
  "Familienformen", [it("traditionell: Mutter, Vater, Kinder", "traditionelle"), it("Alleinerziehende: ein Elternteil mit Kind", "Alleinerziehende"),
                     it("gleichgeschlechtliche Paare mit Kindern", "Gleichgeschlechtliche"), it("Patchworkfamilie: Kinder aus früheren Beziehungen", "Patchworkfamilie")])
P("""Wie *unterstützt* der Staat Familien? Mit *Kindergeld*, mit *Steuererleichterungen*, mit *Kitaplätzen* und *Ganztagsschulen*, und mit *Elternzeit* und *Elterngeld*.
Und zur *Ehe*: Die wird vor dem *Standesamt* geschlossen. Seit *zweitausendsiebzehn* gibt es die *Ehe für alle*: Auch *gleichgeschlechtliche Paare* dürfen heiraten.
Eine *Scheidung* gibt es nur über das *Familiengericht*, wenn die Ehe *gescheitert* ist.""",
  "Staat und Familie", [it("Kindergeld, Steuererleichterungen", "Kindergeld"), it("Kitaplätze, Ganztagsschulen", "Kitaplätzen"), it("Elternzeit und Elterngeld", "Elternzeit"),
                        it("Ehe: Standesamt; seit 2017 „Ehe für alle“", "Ehe"), it("Scheidung nur über das Familiengericht", "Scheidung")])
D("""Jetzt zur *Gleichberechtigung*. Laut *Grundgesetz*, *Artikel drei*, sind *Männer und Frauen gleichberechtigt*. In der *Wirklichkeit* gibt es aber noch *Unterschiede*.""",
  "Gleichberechtigung", "Laut Grundgesetz (Art. 3) sind Männer und Frauen gleichberechtigt. In der Wirklichkeit gibt es noch Unterschiede.")
P("""Welche Unterschiede? Erstens der *Gender Pay Gap*: Frauen *verdienen* im Schnitt *weniger* als Männer. Zweitens: Frauen sind *seltener* in *Führungspositionen*.
Drittens: Frauen übernehmen *öfter Haushalt und Kinder*, das nennt man *traditionelle Rollenverteilung*. Und viertens: Es gibt noch *typische Männer-* und *Frauenberufe*.
Zum Beispiel gibt es *wenige Elektronikerinnen* und *wenige Erzieher*.""",
  "Die Wirklichkeit", [it("Gender Pay Gap: Frauen verdienen weniger", "Gender"), it("seltener in Führungspositionen", "seltener"),
                       it("öfter Haushalt und Kinder (traditionelle Rollen)", "öfter"), it("typische Berufe: wenige Elektronikerinnen, wenige Erzieher", "typische")])
P("""Was kann man *tun*? Erstens: *Girls' Day* und *Boys' Day*. Da lernen *Mädchen Technikberufe* kennen und *Jungs soziale Berufe*. Zweitens: *Mehr Kitaplätze* und *Elternzeit für Väter*,
damit *beide* arbeiten können. Drittens: *Lohntransparenz*, also Gehälter *offenlegen*, damit Frauen *gleich viel* bekommen. Und viertens: die *Frauenquote*.""",
  "Was kann man tun?", [it("Girls' Day und Boys' Day", "Girls'"), it("mehr Kitaplätze, Elternzeit für Väter", "Mehr"), it("Lohntransparenz – Gehälter offenlegen", "Lohntransparenz"),
                        it("Frauenquote", "Frauenquote")])
PRO("""Die *Frauenquote* schauen wir uns genauer an, denn die kam schon in der Prüfung. Frauenquote heißt: Ein *bestimmter Anteil* der *Posten* muss an *Frauen* gehen.
Dafür spricht: *Mehr Frauen* kommen in *Führungspositionen*. Frauen werden zum *Vorbild* für andere. Und *gemischte Teams* treffen oft *bessere Entscheidungen*.
Dagegen spricht: Frauen bekommen den Posten vielleicht nur *wegen der Quote*, nicht wegen *Leistung*. *Männer* fühlen sich *benachteiligt*.
Und die *Ursachen*, zum Beispiel die *Kinderbetreuung*, werden *nicht gelöst*.""",
    ["mehr Frauen in Führung", "Vorbild für andere", "gemischte Teams entscheiden oft besser"],
    ["Posten wegen Quote statt Leistung?", "Männer fühlen sich benachteiligt", "Ursachen (Kinderbetreuung) nicht gelöst"], "Dagegen",
    "Frauenquote: Ein bestimmter Anteil der Posten muss an Frauen gehen.", "Frauenquote")
M("""Das Merke zu Thema neun ist ganz kurz: Männer und Frauen sind *auf dem Papier gleich*, in der *Realität* aber *noch nicht*.""",
  "Auf dem Papier gleich, in der Realität noch nicht.")

# ---------------------------------------------------------------- 10
thema("Prüfungstipps")
T("""Und zum Schluss das, was dir die meisten *Punkte* bringt: die *Prüfungstipps*.""")
BIG("""Erst mal eine gute Nachricht: Nur etwa *jede dritte* Aufgabe braucht *echtes Vorwissen*. Der *Rest* kommt aus der *Anlage*, aus der *Karikatur* und aus deiner *eigenen Meinung*.
Du kannst also auch Punkte holen, wenn du gut liest und gut begründest.""",
    "1 von 3", "Aufgaben braucht echtes Vorwissen", [it("Der Rest: Anlage, Karikatur, eigene Meinung", "Rest")])
P("""Diese *neun Themen* kamen *mehrmals* dran, das sind die *Dauerbrenner*. Die solltest du *auf jeden Fall* können. Eins: die *Definition* der *Globalisierung* mit ihren *Bereichen*.
Zwei: die *Merkmale* einer *Demokratie*. Drei: *Mitmachen außer Wählen*. Vier: *Warum Firmen im Ausland produzieren*. Fünf: die *Wahlgrundsätze*.""",
  "Die 9 Dauerbrenner (1–5)", [it("Definition Globalisierung (+ Bereiche)", "Definition"), it("Merkmale einer Demokratie", "Merkmale"), it("Mitmachen außer Wählen", "Mitmachen"),
                               it("Warum Firmen im Ausland produzieren", "Warum"), it("Wahlgrundsätze", "Wahlgrundsätze")])
P("""Sechs: die *Nachteile* der Globalisierung, also *Gewinner und Verlierer*. Sieben: *demografischer Wandel* und *Fachkräftemangel*, vor allem die *Lösungen*.
Acht: die *EU*, mit ihren *Vorteilen* und *Organen*. Und neun: *Social Media*, *Vorteile* und *Risiken*. Alle neun hast du in diesem Video schon gehört.""",
  "Die 9 Dauerbrenner (6–9)", [it("Nachteile der Globalisierung, Gewinner und Verlierer", "Nachteile"), it("Demografischer Wandel / Fachkräftemangel: Lösungen", "demografischer"),
                               it("EU: Vorteile und Organe", "EU"), it("Social Media: Vorteile und Risiken", "Social")])
X("""Jetzt zur *Karikatur*. Geh in *vier Schritten* vor. Erstens: *Sehen*. Wer ist zu sehen, und wo? Zweitens: *Lesen*. Was steht in den *Sprechblasen*, auf den *Aufschriften*,
und aus welchem *Jahr* ist sie? Drittens: *Stolpern*. Wo ist der *Widerspruch*? *Da* steckt die *Botschaft*. Und viertens: die *Aussage*.
Die formulierst du so: Der Zeichner will *zeigen* oder *kritisieren*, dass … Und ein Tipp: Die *Ausgangssituation* und die *Aufgaben drumherum* verraten dir fast immer das *Thema*.""",
  [it("Sehen – wer, wo?", "Sehen"), it("Lesen – Sprechblasen, Aufschriften, Jahr", "Lesen"), it("Stolpern – Widerspruch = Botschaft", "Stolpern"),
   it("Aussage – „Der Zeichner will zeigen / kritisieren, dass …“", "Aussage")], "Karikatur in 4 Schritten")
P("""Damit du nicht ins Stocken kommst, hier zwei *Mustersätze*. Zum *Beschreiben*: Die Karikatur von … aus dem Jahr … zeigt … Links, in der Mitte oder rechts sieht man …
Auf … steht … Und zum *Interpretieren*: Der Karikaturist möchte damit zeigen oder kritisieren, dass … Das erkennt man daran, dass …""",
  "Mustersätze", [it("Beschreiben: „Die Karikatur von … aus dem Jahr … zeigt … Links / In der Mitte / Rechts sieht man … Auf … steht …“", "Beschreiben"),
                  it("Interpretieren: „Der Karikaturist möchte damit zeigen / kritisieren, dass … Das erkennt man daran, dass …“", "Interpretieren")])
PRO("""Bei *Pro-und-Contra-Aufgaben* gibt es einen richtig guten Trick: den *Klassen-Trick*. Stell dir einfach vor, *deine Klasse* entscheidet *selbst*.
Was spricht dafür? *Mehr Mitbestimmung*, die *Verantwortlichen müssen reagieren*, und *alle* sind *zufriedener*. Was spricht dagegen? *Fehlendes Wissen*, *Manipulation*,
*Blockade* oder *Kosten*. Denk mal an den *Volksentscheid* von vorhin: Da passen genau diese Argumente.""",
    ["mehr Mitbestimmung", "Verantwortliche müssen reagieren", "alle zufriedener"],
    ["fehlendes Wissen", "Manipulation", "Blockade oder Kosten"], "dagegen", "Klassen-Trick: Deine Klasse entscheidet selbst.", "Klassen-Trick")
X("""Wenn du *Stellung nehmen* sollst, dann immer in *drei Schritten*. Erstens: ein *Argument dafür*, mit *Begründung*, also mit *weil*. Zweitens: ein *Argument dagegen*,
ebenfalls mit Begründung. Und drittens: ein *Fazit*, also deine *eigene Meinung*, auch wieder *mit Begründung*. Und noch ein wichtiger Tipp: Formuliere *neutral*.
Schreib zum Beispiel *extreme Parteien*, statt eine *bestimmte Partei* zu nennen.""",
  [it("Argument dafür („…, weil …“)", "dafür"), it("Argument dagegen mit Begründung", "dagegen"), it("Fazit: eigene Meinung mit Begründung", "Fazit")], "Stellung nehmen")
P("""Und drei *allgemeine Regeln* zum Schluss: *Immer* in *ganzen Sätzen* antworten. *Immer begründen*. Und bei *Text-Aufgaben* die Aussagen in *eigenen Worten* wiedergeben,
*nicht abschreiben*.""",
  "Allgemein", [it("immer in ganzen Sätzen antworten", "ganzen"), it("immer begründen", "begründen"), it("Text-Aufgaben: eigene Worte, nicht abschreiben", "Text-Aufgaben")])

topic_no, topic_name = 0, "Geschafft"
sc("""Das war's! Du hast jetzt *alle neun Themen* von Gemeinschaftskunde und die *Prüfungstipps* durch. Denk dran: Die Themen *eins bis sechs* wirklich können,
*sieben bis neun* kurz drüberlesen. Und in der Prüfung: *ganze Sätze* und *immer begründen*. Viel *Erfolg* bei deiner Abschlussprüfung, du schaffst das!""",
   {"type": "kb", "outro": True})

# =====================================================================================
MAX_WORDS = 800  # gemini-3.8 schafft ~800 Wörter pro Anfrage
part, words = 0, 0
for s in S:
    w = len(s["text"].split())
    if words and words + w > MAX_WORDS:
        part, words = part + 1, 0
    s["part"] = part
    words += w
d = {"kb": 5, "label": "GK", "title": "Gemeinschaftskunde", "topics": TOPICS, "sentences": S}
out = ROOT / "src" / "lern_gk" / "script.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
total = sum(len(s["text"].split()) for s in S)
print(f"GK: {len(S)} Szenen, {total} Wörter (~{total / 150:.0f} min), {part + 1} Blöcke")
