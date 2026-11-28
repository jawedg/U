# Projekt: TikTok-Videos mit Claude (Remotion)

## Vorlieben des Nutzers (immer beachten)
- Sprache: Deutsch, einfach erklären.
- **Stimme: Google Gemini TTS, Stimme „Charon“** (`npm run voice:3d` bzw. `python3 scripts/voice_gemini.py --voice Charon`).
  - Piper/edge-tts gefallen dem Nutzer NICHT (zu roboterhaft).
  - Chatterbox (Open Source) will der Nutzer auch NICHT. Google Cloud (Chirp 3 HD) NICHT – Nutzer will keine Karte/Bankdaten hinterlegen.
    Reserve bei Gemini-Tageslimit: `voice_gemini.py` wechselt automatisch auf das Ausweichmodell (FALLBACKS), gleiche Stimme Charon.
- **Islam-Kanal NEU (Nov. 2026): Serie „QISSA – wahre Geschichten“ im POV-3D-Stil** wie die TikToks von „Signal Lost“
  (@signalost0): Ich-Sicht in echten 3D-Räumen (Blender), großer Frage-Titel oben, Ort/Zeit-Zeile in Schreibmaschinenschrift,
  Untertitel in Serifenschrift, schwarze Zwischentafeln, Auswahltafel ① ② am Ende, Logo. Siehe Abschnitt „QISSA“ unten.
  Älterer Stil: 2D-Strichzeichnung wie `src/athan2d/`. 3D mit Three.js in Remotion (`src/train`, `src/athan`) gefällt NICHT (zu holprig).
- Format 1080×1920.

## ElevenLabs – Erzählerstimme (aktuell, Nov. 2026)
- Nutzer: Gemini klingt „wie Computerstimme“ → Erzähler jetzt **ElevenLabs, Stimme „Helmut Stieglbauer – Deep and Dynamic“**
  (Voice Library, ID `JiW03c2Gt43XNUQAumRP`), Modell **`eleven_v3`** (Nutzer wählte v3 statt multilingual_v2). Nutzer hat Creator-Plan.
- Schlüssel = Network Secret (Host `api.elevenlabs.io`, Header `xi-api-key`) in der Umgebung „Standard“; Skripte senden `proxy-injected`.
  Dem Schlüssel fehlen `voices_read`/`user_read` (Stimmen auflisten geht nicht, Sprachausgabe per ID geht).
- In script.json: voicePart `{"engine":"eleven","model":"eleven_v3","speakers":{"Erzaehler":"<voice_id>"},"chunks":[…],"flow":true}`;
  je Satz Feld **`el`** = Text mit v3-Regie-Tags (`[whispers]`, `[curious]`, `[excited]`, `[softly]`, `[warm, reverent]` …), Gefühl passend
  zum Inhalt (Nutzerwunsch: leise wo leise, andere Tonlage bei Fragen). Eine Anfrage je Szene (`chunks`), Endpunkt `/with-timestamps`:
  Schnitte + Untertitel-Wortzeiten aus den Buchstaben-Zeiten (`eleven_block` in voice_gemini.py), Schnitt an echter Stille (Zeiten nach
  Tags ~0,3 s zu spät). Szenen-Ende: `" ..."` ans Ende des letzten `el` + 50-ms-Ausblendung (ElevenLabs schneidet hart ab).
  Cache: `out/stimmproben/eleven-<sig>.mp3/.json` (committet → keine Credits beim Neubau). Kosten ~1.500 Credits je Video-Erzählung.
- Arabische Namen: **arabische Schrift im `el`-Text** (Nutzer verglich 3 Schreibweisen, wählte diese). Zahlen als Wort (Gemini las 622 als 662).
  Abu Bakr MIT Harakat schreiben: `أَبُو بَكْر` (ohne -> Spracherkennung hörte „Abubakar“), geflüstert lieber `[softly, tense]`.
- **FIGUREN-STIMMEN (Nutzer, 25.11.2026, gilt für ALLE künftigen Folgen):** Gemini-Dialogstimmen klangen „billig, ohne Emotion,
  alle gleich“. Jetzt JEDE Figur mit eigener deutscher ElevenLabs-Stimme (Voice Library, `GET /v1/shared-voices?language=de&gender=…&age=…`
  geht mit dem Schlüssel; Bibliotheks-Stimmen per ID direkt nutzbar) + `eleven_v3` + Regie-Tags je Satz passend zum Gefühl
  ([hopeful, eager], [whispers, frightened], [dismissive, sly], [shouting from far away, desperate], [out of breath, excited] …).
  Immer viel Mühe geben: je Figur 2 Kandidaten erzeugen und als **EINZELNE Dateien** schicken (Name = Figur + A/B,
  z. B. `03-Abu-Bakr-A.m4a`) – eine Sammeldatei mit Zeitmarken verstand der Nutzer nicht. Erst nach Wahl die Dialog-Einstellungen rendern.
  Folge 5 gewählt: Prophet ﷺ = Christian `NBqeXKdZHweef6y0B67V` (Hall), Abu Bakr = Cornelius `2baru8J0e15nxuG3bzXy` (Hall),
  Suraqa = Torsten `iCEMyUhOwgAy0egMANye`, Stammesmann = Ben `aTTiK3YzK3dXETpuDE2h`, Verfolger = Frederick `uVKHymY7OYMd6OailpG5`.
  In script.json je Figur ein voicePart (`engine: eleven`, `chunks` = je Satz, `capPause` 0.45), Satzfeld `el` mit Tags.
- **Untertitel-Zeiten aus Spracherkennung:** nach voice_gemini.py immer `python3 scripts/stt_retime.py --project <p>` (ElevenLabs
  Speech-to-Text scribe_v1, zwischengespeichert `out/stimmproben/stt-*.json`; korrigiert auch Wörter am falschen Satz, z. B. „Er kommt“),
  dann build_*.py. Gesprochenes und Untertitel müssen gleich sein (Nutzer: „al-Madina“ gesprochen, „Medina“ gezeigt -> Untertitel „al-Madina“).

## Gemini-TTS – wichtig
- API-Schlüssel kommt aus der Umgebungsvariable `GEMINI_API_KEY`. Niemals ins Repo schreiben.
  Fehlt er: Nutzer bitten, ihn in den Umgebungs-Einstellungen als Secret `GEMINI_API_KEY` einzutragen.
- Das Modell liest Stil-Anweisungen im Text MIT VOR → nur den reinen Text schicken.
- Free Tier: nur ~10 Anfragen/Tag pro Modell → ganzen Text in EINER Anfrage erzeugen
  (macht das Skript automatisch, schneidet dann an den Pausen). Ausweichmodell:
  `GEMINI_TTS_MODEL=gemini-3.1-flash-tts-preview`.
- **Erzählstimme mit Ausdruck (Nov. 2026, Nutzer: Charon „klingt billig/langweilig“):** `gemini-2.5-flash-preview-tts` versteht
  Regie-Anweisungen im Prompt (`# AUDIO PROFILE … ### DIRECTOR'S NOTES … #### TRANSCRIPT` + `Sprecher: Text`), liest sie NICHT vor,
  und kann 2 Sprecher in einer Anfrage (`multiSpeakerVoiceConfig`). `gemini-3.8-flash-tts` liest solche Anweisungen/[Tags] teils mit vor,
  will bei Mehrsprechern `speechMetadata.speaker` je Textteil und kennt keine systemInstruction. `gemini-2.5-pro-preview-tts`: im Free Tier gesperrt (429).
  Hörproben-Skripte (Erzähler + Dialog, Zitat mit Hall per Faltung): Ergebnis `out/stimmproben/qissa-probe-*.m4a`.
- Schlüssel liegt als Network Secret (Host `generativelanguage.googleapis.com`, Header `x-goog-api-key`) in der Umgebung „Standard“ →
  Skripte mit `GEMINI_API_KEY=proxy-injected` starten (der Proxy ersetzt den Platzhalter).
- Bereits erzeugte Erzählung liegt in `out/stimmproben/<Stimme>.wav` und wird wiederverwendet –
  nach Textänderung diese Datei löschen, sonst passt die Stimme nicht zum neuen Text.

## Rendern (in der Cloud-Umgebung ohne GPU)
```bash
npx remotion render Erklaervideo3D out/<name>.mp4 --gl=swangle --concurrency=4 \
  --browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
```
Lokal reicht `npm run render:3d`.

## TikTok-Kanal: Islam (Geschichten, Fakten)
- Erstes Video: `src/athan2d/` (Komposition `ErsterAdhan2D`) – „Der erste Adhan“, ca. 1:55 min.
  Neue Videos: Ordner kopieren, `script.json` + `scenes.tsx` anpassen, `art.tsx` wiederverwenden.
- Zielänge: **1:30–2:00 min** (über 1 min für Creator Rewards, nicht gehetzt, max. ~2:30).
- **QISSAH-Folgen (Nutzer, 23.11.2026): höchstens 3:00 min** – Folge 3 (4:17) war zu lang. Vorbild Folge 1 „Der erste Adhan“
  (2:41 = „irgendwie perfekt“). Ziel ~2:30–2:50; Text vorher auf die Länge kürzen (ElevenLabs-Erzähler ≈ 2,3 Wörter/s inkl. Pausen).
- **Menschen dürfen gezeigt werden, aber NIE mit Gesicht** (leerer Kopf) – gilt für die Geschichten (Sahaba, Propheten, damalige Zeit).
  **Ausnahme (Nutzer, 26.11.2026):** bei modernen, erfundenen Erinnerungs-Videos (z. B. Flug-Video) dürfen Gesichter sein (`flug_world.face()`). Sahaba/wichtige Personen zusätzlich mit
  Licht über dem Kopf (`glow`). **Den Propheten ﷺ nie darstellen** – nur als Licht (`HolyLight`).
- **Immer Sound:** Atmo in jeder Szene (nie Stille) + passende Effekte (`scripts/sfx.py`, synthetisch erzeugt,
  in `scenes.tsx` per `sfx` an gesprochene Wörter gekoppelt). Keine Musik.
- Bei Erwähnung des Propheten: „Friede sei mit ihm“ sprechen.
- Fakten nur mit Quellen (Hadith-Nummern) – Quellen in `script.json` -> `sources` und in die TikTok-Beschreibung.
- Echte Adhan-Aufnahme: Datei vom Nutzer nach `public/athan/athan.mp3`, dann in `src/athan2d/script.json`
  `"athanFile": "athan/athan.mp3"` setzen (Länge über `athanSeconds`). Ohne Datei bleibt die Stelle still (nur Wind).
- Kein Musik-Hintergrund.
- Stimme: `python3 scripts/voice_gemini.py --project athan2d` (Gemini Charon). Tageslimit beachten.
- Rendern 2D (ohne --gl): `npx remotion render ErsterAdhan2D out/erster-adhan-2d.mp4 --concurrency=4 --browser-executable=...`

## Lernvideos (Schule / AP2)
- `src/wiso/` (Komposition `WisoKB4`, 1920×1080, 25 fps): Lernvideo WiSo KB IV „Selbstständigkeit“.
  Skript entsteht aus `scripts/build_wiso_script.py` (Szenen mit `part`, `topic`, `step`, `text`, `v` = Visualisierung).
  Visualisierungen in `src/wiso/Visuals.tsx` (title, board, balance, form, formtable, kapital, definition, exam, …).
- Stil Lernvideo: Karopapier, Handschrift-Überschriften (Caveat), Farbe pro Thema, Lukas als roter Faden,
  Kopfzeile mit Unterrichtsphase, Untertitel unten. Leise UI-Sounds (`scripts/sfx_wiso.py`).
- Lange Sprachaufnahmen: Szenen per `part` in Blöcke (je ~500–700 Wörter, 1 TTS-Anfrage pro Block).
  Schnitt in Szenen per **lokaler Whisper-Erkennung** (sherpa-onnx, Modell von GitHub:
  `sherpa-onnx-whisper-base`, nach `models/` oder `/tmp/models/`), danach `npm run check:wiso` zur Kontrolle.
- Gemini-Textmodelle (flash) haben nur ~20 Anfragen/Tag – nicht für Massen-Transkription verwenden.
- `src/wiso_all/` (Komposition `WisoAlle`): WiSo komplett KB I–IV in einem Video (~24 min), Skript aus
  `scripts/build_wiso_all_script.py` (Szenen mit `sub` = Unterthema in der Kopfzeile). Nutzt `src/wiso/Visuals.tsx`
  (zusätzlich: grid, pillars, table, flow, stairs, ledger, timeline, triangle, chart, formula2, cycle).
  Spickzettel: `videos/wiso-komplett-spickzettel.md`.

## Ausführliche Lernvideos nach Lernzettel (aktueller Wunsch-Stil)
- 4 Videos `LernKB1`–`LernKB4` (1920×1080, 25 fps), Skripte aus `scripts/build_lern_scripts.py` (folgt exakt dem
  Lernzettel des Nutzers: Definition, Stichpunkte, „Was passiert?“, Merke) → `src/lern_kbN/script.json`.
- **Minimal-Design** (`src/lern/Min.tsx`, `src/lern/LernVideo.tsx`): heller Hintergrund, viel Weißraum, Inter,
  eine Akzentfarbe pro KB, Kopfzeile „KB I · Titel“ + „Thema x/n“, Untertitel ohne Box. Gefällt dem Nutzer.
- Stimme: alle 4 Videos mit gemini-3.8-flash-tts (Charon), Blöcke bis ~800 Wörter. 3.1-preview scheitert an langen
  Blöcken (keine Audio-Antwort). Fortsetzung KB I–III: `./scripts/run_lern_rest.sh` (Setup: `scripts/setup_cloud.sh`).
- **Erklärstil (Nutzer-Feedback!):** NICHT Stichpunkte vorlesen. Wie ein Lehrer: Alltagseinstieg, „warum“, Vergleiche,
  Beispiele mit Lukas, Quizfrage an den Zuschauer (Typ `quiz`), dann Merke. Die PDF gibt nur Struktur/Inhalt vor.
- Tagesplan Vertonung: Tag 1 KB I + KB IV, Tag 2 KB II + KB III (`./scripts/run_lern_today.sh 2 3`).
- YouTube/Bing sind in der Cloud-Umgebung gesperrt – für Stil-Vorbilder Bildschirmaufnahme hochladen lassen.

## Gemeinschaftskunde (ein Video, alle Themen)
- Komposition `LernGK` (EIGENES Design auf Nutzerwunsch: dunkel Nachtblau + Mint, Themen-Leiste links mit Fortschritt,
  große Themennummern, Inter Display + JetBrains Mono; Farben per CSS-Variablen in `LernVideo.tsx` GK_VARS, kb = 5), Skript aus `scripts/build_gk_script.py`
  (folgt exakt `WiSo_Lernzettel_Gemeinschaftskunde.pdf`: 9 Themen + Prüfungstipps, Lehrer-Erklärstil) → `src/lern_gk/script.json`.
- ~5400 Wörter / 7 TTS-Blöcke (~36 min). Erzeugen + Rendern: `./scripts/run_gk.sh` → `out/lern-gk-lege-klein.mp4` + `out/lern-gk-dunkel-klein.mp4`.
- Nutzer-Feedback: statisches Design wirkt „wie PowerPoint“ → mehr Bewegung. Zwei Varianten:
  - `LernGK` (dunkel, `src/lern/MinGK.tsx`): gefederte Einblendungen, Fokus auf gerade gesprochenem Punkt, bewegter Hintergrund.
  - `LernGK2` **Legetechnik** (`src/lern/LegeVideo.tsx`, Symbole `src/lern/LegeIcons.tsx`): Papier-Hintergrund, Strichzeichnungen
    als Papier-Ausschnitte, Handschrift (Caveat), gezeichnete Hand schiebt Teile rein, Papier-Schiebegeräusch (`public/lege/`).
    Symbol-Zuordnung per Stichwort + `ICON_FOR_TEXT` (exakte Texte).

## Berufstheorie-Rechenvideos (z. B. Füllstandsmessung)
- `LernFuellstand` (kb = 6, Label „BT“) im **Tafel-Design** (Nutzer: Seitenleiste nervt, will volles Bild): grüne Schultafel
  (`public/board/board.jpg`), Kreide-Handschrift (Caveat, `--sans`/`--fscale`), Kreide-Filter `#chalk`, Farben gelb/rosa/hellblau
  (`accent`/`accent2`/`water` in `Min.tsx`), Kopfzeile oben statt Seitenleiste (`BoardScene` in `LernVideo.tsx`), Skript `scripts/build_fs_script.py`
  → `src/lern_fs/`. Nutzerwunsch: echte Prüfungsaufgabe Schritt für Schritt lösen (Bild, Schaubild, Rechnung), dann eigenes
  Beispiel im Prüfungsstil. Technik-Grafiken in `src/lern/Tech.tsx`: `tank` (Behälter + Ultraschall, Füllstand animiert),
  `graph` (Schaubild mit Punkten, Gerade, Steigungsdreieck, Ablesen), `scales` (Volt ↔ Digitalwert), `calc` (Rechenweg tippt sich).
- Zahlen im Sprechtext als Ziffern schreiben (Gemini liest sie richtig, Untertitel zeigen Ziffern). Cue-Wörter: Satzzeichen
  werden entfernt („1,5“ → „15“), daher Wort-Cues verwenden. Videos für den Nutzer ≤ ~60 MB halten (größere lassen sich in der App nicht speichern).

## Praktische Prüfung AP T2 – Prüfungssimulation
- Nutzer: Elektroniker/-in für Betriebstechnik, praktische Prüfung Ende Januar (IHK, Gestell + Änderungsauftrag), SPS = Siemens S7.
  Unterlagen Winter 2026/27: Blechbearbeitungsmaschine (Haspel M1 mit Wendeschützen Q1/Q2, Ventil M2, F3 RCBO B16/10 mA für Steckdose X5,
  F4 Motorschutz 3,25 A, X1: 1=L1 3=L2 5=L3 7=N 9=PE). Prüfprotokoll-Auszug VDE 0100-600: Besichtigung, R-PE, R-ISO (X1-Paare), RCD U_B + t_A, Drehfeld, Erprobung.
- Komposition `PruefSim` (kb = 7, `src/pruef/`), Skript `scripts/build_pruef_script.py`: Ich-Perspektive (Charon) + Prüfer (Orus).
  Szenen haben `who`/`voice`; alle Prüfer-Sätze in einem TTS-Block (`voice_gemini.py` ordnet Blöcke wieder der Szenenreihenfolge zu).
  Werkstatt-Look (hell, Orange), gezeichnetes Gestell `src/pruef/Gestell.tsx` (Messpunkte `PT`, Hervorhebung `BOX`), Szenentypen:
  title, phase, board (Kamera, Zustände LEDs/Schütze), talk (Sprechblase mit Wort-Hervorhebung, Diagramme flanke/verriegelung/typenschild),
  measure (Installationstester + Prüfspitzen), protocol (füllt sich über alle Szenen), change, docs, tip, check.

## Mess-Video POV 3D (Fluke 1664 FC)
- Komposition `MessPOV` (kb = 8, `src/mess/`, 1920×1080, 25 fps, ~5:39): nur Messteil + Protokoll aus Ich-Sicht (Charon),
  Skript `scripts/build_mess_script.py` (Szenen-`v`: `cam`, `pr` = Prüfspitzen rot/grün/blau, `fl` = Fluke-Zustand, `st` = Anlagenzustand
  T1off/F3trip/plug/cee).
- **Realistische Version** (Nutzer: „sieht nicht echt aus“): alles echtes 3D in `src/mess/scene/` – `Gestell3D.tsx` (Lochblech, Hutschienen,
  Kanäle mit Kammfingern, LS/FI-LS, Schütze, Netzteil, Motorschutz, Steckdose, S7-1200, X10-Platine, Reihenklemmen mit Schrauben + Markierern,
  Adern, Bedieneinheit, CEE-Stecker, Alu-Rahmen), `Probe3D.tsx` (Prüfspitzen mit Fingerschutz, Krokodilklemme, Handschuh-Hände + Ärmel,
  Messleitungen zu den Buchsen), `Fluke3D.tsx` (3D-Gerät, 7-Segment-LCD per Canvas, Drehknopf, Tasten), `tex.ts` (prozedurale Texturen).
  Prüfspitzen fächern nach Lage auf (keine Durchdringung). Licht: RoomEnvironment + Schatten + N8AO (`@react-three/postprocessing@3.0.4`).
- Rendern: `--props='{"fx":"ao","dpr":0.75}' --timeout=300000` (dpr = 3D-Auflösung; Kosten sind pixelgebunden, ~1,3 s/Bild → ~3 h).
  Länger als 2 h → mit `setsid nohup` starten (Skript-Vorlage: render + 2-Pass 1250 kbit/s → ≤ 60 MB).

## QISSA – Islam-POV-Serie in 3D (Stil „Signal Lost“, aktueller Wunsch des Nutzers)
- Folge 1 „Der erste Adhan“: Komposition `QissaAdhan` (1080×1920, **60 fps**), Ordner `src/qissa_adhan/`, Blender `blender/qissa/`.
- **Version 5 (Nutzer, 18.11.2026):** Erzähler **Algieba** (aus 14 tiefen Gemini-Stimmen gewählt, `out/stimmproben/stimme-05*`),
  Hörbuch-Stil mit Regie-Anweisungen (gemini-2.5-flash, Block 0 mit Junge=Puck). Arabische Namen ARABISCH aussprechen (Nutzer!):
  im Satz `"say"` mit arabischer Schrift (أذان, عبد الله بن زيد, بلال, عمر), Untertitel zeigen `"text"`.
  **Fließend** (Nutzer: Erzähler klang „gehackt“): `"flow": true` im voicePart → Aufnahme am Stück EINMAL filtern + Lautheit
  angleichen, dann exakt schneiden (Ränder max. 0,3 s Stille), kein tighten/clean je Satz; build_qissa_adhan.py setzt zwischen
  aufeinanderfolgenden Flow-Sätzen keine Extra-Pause. Schnittstellen von Hand geprüft (`out/stimmproben/*.cuts.json`).
  Zitat-Stimmen je Person eigener Block: Abdullah=Iapetus, Grüner Mann=Enceladus, Umar=Alnilam (3.8 + Hall), q3 = Charon.
  Ende neu: „Seit über 1400 Jahren … Und alles begann … mit einem Traum.“ (kein „Wusstest du das?“, keine Auswahltafel: `"choice": null`).
  Stimme klonen (Seed-VC, `scripts/voice_clone.py`, `/home/user/venv-vc`) hat der Nutzer ABGELEHNT – nicht wieder anbieten.
  Blender: Bilal läuft vor der Säulenreihe (y=11), Mutter kommt aus echter Tür, Beratung mit ruhigen Kopfbewegungen.
  Einstellungen, die nur 2–3 % länger wurden, per minterpolate gestreckt statt neu gerendert (`scripts/v5_qissa_adhan.sh`).
- **Version 4 (Nutzer, 17.11.2026):** Erzähler **Orus** (Doku-Stil: „tief, warm, wie Dokumentation“ – Regie wie in
  `out/stimmproben/erzaehler-3-orus.m4a`), arabische Namen DEUTSCH ausgesprochen (arabische Schrift im Sprechtext gefiel nicht),
  KEIN atempo/starkes Pausen-Kürzen beim Erzähler (klingt robotisch; `tighten` je Block, Dialoge behalten 0,34 s/1,07).
  Zitate mit Hall sind in Wahrheit **Charon** (voiceParts 3; Nutzer mag sie). Gasse: echtes Gespräch – junger Mann fragt den Mann
  an der Tür, der antwortet (Block 4, Stimme Achird). `"retime": "rate1"`: gerenderte Einstellungen laufen nach neuer Vertonung im
  Originaltempo (nur gekürzt) – so musste nur die Gasse neu gerendert werden (`scripts/v4_qissa_adhan.sh`). ﷺ immer in Amiri setzen.
- **Version 3 (Nutzer-Feedback Nov. 2026: „langweilig, nicht flüssig (will 120 Hz), Geräusche übersteuert, Horn klingt nicht wie Horn,
  Grafik leer – mehr Details, Zuschauer wischen nach Sekunden weg“):**
  - Einstieg (Hook, erste 9 s): echtes „Allahu akbar“ + Frage-Titel „WOHER KOMMT DER ADHAN?“ + „Diese Worte hörst du jeden Tag … Aus einem
    Traum.“ als Ausschnitte späterer Einstellungen (`clip`-Segmente in build_qissa_adhan.py). Twist am Ende (Umar 20 Tage, Abu Dawud 498).
  - `tighten` in script.json: voice_gemini.py kürzt lange Sprechpausen (max. 0,34 s) und spricht 7 % schneller (atempo).
  - Flüssig: TikTok spielt max. 60 fps → Blender rendert 30 fps in VOLLER Auflösung (100 %, 2 Samples – mehr Samples sehen gleich aus,
    kosten aber ~2,8 s je Sample), ffmpeg `minterpolate` → 60 fps. Bei vielen Lichtpunkten (Traum) macht minterpolate Klötzchen/Doppelpunkte →
    dort rendert Blender die ECHTEN Zwischenbilder (`MID=1`: Bild k+0,5 per `frame_set(k, subframe=0.5)`; `MID_SHOTS="traum"`).
    Kein playbackRate-Umrechnen mehr (ruckelt) – nach neuer Vertonung neu rendern.
  - Keine Verpixelung (Nutzer!): kein Filmkorn (wird beim Verkleinern zu Klötzchen), kleine Version als HEVC (`-tag:v hvc1`, 2 Durchgänge, 58 MB).
  - Der Cloud-Rechner startet alle paar Stunden neu (Prozesse weg, Dateien bleiben) → alles fortsetzbar: render_qissa_adhan.sh überspringt
    fertige Bilder (vorher 0-Byte-Platzhalter löschen), `scripts/finish_qissa_adhan.sh` rendert Remotion in 4 Teilstücken ohne Ton
    (fertige werden übersprungen), fügt master.wav an und macht die HEVC-Kleinversion. Nach Text-Änderungen in Blender-Einstellungen prüfen,
    ob sie gestrichene Satz-IDs benutzen (ls("d2") ließ Blender stundenlang abstürzen).
  - Mehr Details: `MD.props()` (Krüge, Körbe, Säcke, Leitern, Sonnendächer, Wäsche, Steine, Brennholz), Wände mit Putzflecken + Schmutz unten
    (`pbr(..., grime, plaster)`), Traum als „Traum bei Nacht“ (`world_sky("dreamnight")`, Dünen, Medina im Dunst, Mond, Goldstaub-Wirbel,
    leuchtende Fußspuren). Testbilder: `FRAMES=a-b` bzw. Standbild-Zeiten als 5. Argument von adhan.py.
  - Ton: `sfx_qissa_adhan.py` mischt ALLES zu `public/qissa_adhan/master.wav` (Stimmen, Adhan, Atmo mit Ducking, Effekte; -14 LUFS, True Peak
    -1,5 dB, Begrenzer) → Remotion spielt nur diese Spur (vorher übersteuerte die Summe). Echte Geräusche (Schofar, Glocke, Feuer, Grillen,
    Hahn, Schritte, Tür …) in `assets/sfx/*.flac`, Nachweise `assets/sfx/CREDITS.md`. Quellen: SFXMint (CC0, KI-erzeugt; Katalog
    `flreey/sfxmint-cc0-sound-effects` auf Hugging Face, Dateien über sfxmint.com/dl/<id>.wav – Tageslimit pro IP!) und SFX Kit
    (`wyzowl/sfx-kit`, CC0) – HF-Downloads laufen über us.aws.cdn.hf.co. Schofar von Wikimedia Commons (CC BY-SA → Urheber in
    TikTok-Beschreibung nennen); Commons drosselt die Cloud-IP stark (429, Retry-After 600 s).
- **Erzähl-Version (Nutzer-Feedback Nov. 2026: „klingt billig, langweilig, stille Stellen gefallen nicht“):** Charon ERZÄHLT spannend
  (Gemini 2.5 flash TTS mit Regie-Anweisungen, `voiceParts` in script.json, bis 2 Sprecher je Anfrage), erfundene Leute in Dialogen mit
  eigenen Stimmen (Puck, Algenib, Fenrir, Aoede, Leda – Untertitel kursiv). Worte von Sahaba und dem Propheten ﷺ: Erzähler sagt „… sagte:“,
  dann spricht eine Zitat-Stimme (Iapetus, `fx: hall`, gemini-3.8 als reiner Text) + goldene Schrift Wort für Wort. Keine stummen Stellen.
  Adhan: 2 Takbir pur (nicht drüber sprechen), dann leise unter kurzen Reaktionen, dann aus.
  Schnitte: `beep_align` in voice_gemini.py (Stücke an Pausen + Pieptöne → 1 Transkript-Anfrage). Lokale Whisper-Installation wurde abgelehnt.
  Schon gerenderte Einstellungen: `rendered_ref.json` + Zeit-Anker (`ANCHORS` in build_qissa_adhan.py) → stückweises Bildtempo in Remotion;
  passt es nicht (Fehler > 1 s / Tempo außerhalb 0,8–1,25) → `rerender` → `./scripts/run_qissa_adhan.sh` rendert nur diese neu.
- **Variante A (vom Nutzer gewählt, alte Fassung):** „Du“ = erfundener junger Mann aus Medina (Stimme Charon). Mit eigener Stimme sprechen nur du
  und erfundene Leute (z. B. Orus, Iapetus). Worte von Sahaba und dem Propheten ﷺ NUR als goldene Schrift (`quotes` in script.json).
  Menschen ohne Gesicht (leerer Kopf), Sahaba mit Licht über dem Kopf (`glow=True`), Prophet ﷺ nur als Licht-Säule (`holy_light`).
  Adhan nie per KI – echte Aufnahme vom Nutzer (`public/qissa_adhan/athan_full.mp3`, nicht im Repo), nur ein passender Ausschnitt.
- Kanal-/Serienname **QISSAH** (قصة = Geschichte), Zusatz „WAHRE GESCHICHTEN“. Logo/Profilbild (Nutzer-Wahl): `logo/qissah-profilbild.png`
  = geschwungenes Q (Playfair Display kursiv 700) + „QISSAH“ (Cinzel 600) in Gold (#e8b54d) im leuchtenden Gold-Doppelring auf Schwarz
  (Quelle `logo/kursiv_varianten.html`, Variante 2). Schlusstafel im Video (Nutzer zog diese vor): gerades Q (EB Garamond) im Gold-Doppelring, der sich einzeichnet, darunter QISSAH (JetBrains Mono), قصة und „WAHRE GESCHICHTEN“ (QissaAdhan.tsx, Card „logo“, 2,8 s).
  Nutzer mag: 2D, Gold auf Schwarz, kein 3D-Logo, keine schmalen Schriften.
- Ablauf:
  1. `src/qissa_adhan/script.json` (Sätze mit `part`/`voice`, Zitate, Quellen) → `python3 scripts/voice_gemini.py --project qissa_adhan`
     (3 Anfragen: Charon-Block, Orus, Iapetus) → `timing.json`.
  2. `python3 scripts/build_qissa_adhan.py` → `timeline.json` (Einstellungen, Sätze, Zitate, Ereignisse; ohne Vertonung geschätzt).
  3. `./scripts/render_qissa_adhan.sh [einstellungen…]` → Blender-Bilder `out/qissa_frames/<einstellung>/` → `public/qissa_adhan/shots/*.mp4`
     (60 fps; 4 Blender-Prozesse als Warteschlange, 100 %, 2 Samples, 30 Bilder/s, ~8–14 Bilder/min; ~3500 Bilder ≈ 5–6 h; immer mit
     `setsid nohup`, z. B. `SAMPLES=2 MID_SHOTS="traum" setsid nohup ./scripts/render_qissa_adhan.sh > out/qissa_render.log 2>&1 &`).
     Danach `python3 scripts/build_qissa_adhan.py --mark-rendered <einstellungen…>`.
  4. `python3 scripts/sfx_qissa_adhan.py` → `public/qissa_adhan/master.wav` (fertige Tonspur, keine Musik).
  5. `./scripts/finish_qissa_adhan.sh` → `out/qissa-erster-adhan.mp4` + `out/qissa-erster-adhan-klein.mp4` (Remotion ~16 min, HEVC ~20 min).
- Blender-Bausteine (`blender/qissa/lib.py`): `person()` (Gewand mit Falten, Turban/Tuch/Kappe, Umhang, sitzend/stehend, Gelenke als Empties),
  `walk()`, `idle()`, `head_to()`, `arm_pose()`, `hands_to_ears()`, `holy_light()`, `halo()`, `pov_camera()` + `cam_keys()` + `handheld()`,
  `pov_hands()` (Hand mit Öllampe), `world_sky("night"|"dawn"|"dream")`, `render_setup()` (AgX Punchy, Dunst per Mist, Bloom).
  `blender/qissa/medina.py`: Moschee (Lehmmauern, Palmstamm-Säulen, Palmzweig-Dach), Gassen, Häuser, Palmen, Berge; `join_static()`
  verschmilzt alles Unbewegte (halbiert die Renderzeit). Schatten nur von Mond/Sonne (weiche Punktlicht-Schatten rauschen und sind teuer).
- Schriften lokal in `public/fonts/` (EB Garamond, Amiri; OFL), Untertitel-Serifenschrift wie im Vorbild.
- TikTok-Beschreibung + Quellen: `videos/qissa-erster-adhan.md`.

## QISSAH Folge 2 „Der Ursprung von Zamzam“ (Nov. 2026)
- Titel im Video „WOHER KOMMT ZAMZAM?“, Folgen-Name „Der Ursprung von Zamzam“ (Nutzer wählte). Quelle: Bukhari 3364/3365.
  Ich-Sicht Hadschar. Ibrahim, Ismail (Baby-Bündel mit Licht statt Kopf) und der Engel NUR als Licht.
- Dateien: `src/qissa_zamzam/` (script.json, timeline.json, QissaZamzam.tsx, Komposition `QissaZamzam`), `scripts/build_qissa_zamzam.py`
  (PLAN, `montage` = schnelle Schnitte je Wort beim Zählen „Zwei … Sechs“, Zähler-Overlay „SAFA ⇄ MARWA n/7“),
  Blender `blender/qissa/zamzam.py` (Einstellungen) + `blender/qissa/mekka.py` (Tal mit einzelnen Granitgipfeln, Trockenbett,
  Akazie, Safa/Marwa als Felshügel, Quelle mit Strahl + Wall aus Sandklumpen, Engel-Licht, Kamele, Vögel, Zelte, Mas'a-Halle mit Pilgern).
  Ablauf: `scripts/render_qissa_zamzam.sh` → `scripts/v1_qissa_zamzam.sh` (wartet, Ton `scripts/sfx_qissa_zamzam.py`, `finish_qissa_zamzam.sh`)
  → `out/qissah-zamzam-klein.mp4`. TikTok-Text: `videos/qissah-zamzam.md`.
- Erzähler-Schnitte: voicePart `"cutmode": "latest", "snap": true` (sonst landete „… [whispers] niemand.“ im nächsten Stück, Untertitel zu spät).
- Durchsichtige Licht-Säulen schrieben Tiefe in den Dunst-Kanal (blaue Ellipse am Himmel) → `render_setup(..., sky_sep=True)`:
  Himmel getrennt (Environment-Pass), Dunst nur auf Undurchsichtiges. Licht-Gestalten werfen keinen Schatten (`MK.no_glow_shadows()`).
- SFXMint-Downloads brauchen jetzt einen API-Schlüssel (anonym 0/Tag) → nicht nutzbar. **Geräusche jetzt per ElevenLabs** (Nutzer-Idee):
  `POST /v1/sound-generation` {text, duration_seconds, prompt_influence 0.6}, ~11 Credits/s, Ergebnis `assets/sfx/el_*.flac` (auf -20 LUFS);
  Prompts immer mit „no music“.
- Text-Änderung (vom Nutzer genehmigter Text): „Kein Baum“ → „Nur Stein … und Sand“, weil der Hadith einen großen Baum nennt.

## QISSAH Folge 3 „Die Erbauer der Kaaba“ (Nov. 2026)
- Titel im Video „WER HAT DIE KAABA GEBAUT?“, Fortsetzung von Folge 2 (gleicher Hadith Bukhari 3364: drei Besuche Ibrahims, die Türschwelle,
  Fleisch und Wasser, Bau des Hauses, Maqam-Stein; Ende heute: Kaaba + Maqam Ibrahim mit Fußabdrücken). Text vom Nutzer genehmigt.
- Stimmen: Erzähler ElevenLabs (Helmut), Ibrahim = Orus, Ismail = Achird, Frauen = Kore/Despina (gemini-2.5-flash mit Regie), Prophet ﷺ = Charon (3.8 + Hall).
  Koran 2:127 nur auf Deutsch. Gemini-Schnitte von Hand geprüft (`out/stimmproben/qissa_kaaba-p*.cuts.json`).
- Dateien: `src/qissa_kaaba/`, `scripts/build_qissa_kaaba.py`, Blender `blender/qissa/kaaba.py` (18 Einstellungen) + `kaaba_world.py`
  (Ismails Haus mit Steinschwelle, Ziegen, Zamzam-Brunnen, Grab, Pfeile/Bogen, Schale/Becher, Mauern Lage für Lage, Maqam-Stein,
  Kaaba heute mit Hijr, Maqam-Glocke, Mataf, Pilger-Ringe), Ton `scripts/sfx_qissa_kaaba.py`, Geräusche per `scripts/el_sfx.py`.
  Ablauf: `JOBS=2 setsid nohup ./scripts/v1_qissa_kaaba.sh > out/kb_v1.log 2>&1 &` → `out/qissah-kaaba-klein.mp4`. TikTok-Text: `videos/qissah-kaaba.md`.
- Renderzeit (CPU, kein GPU): Kosten hängen an der Dreieckszahl je Sample. Daher: Kiesel/Büsche/ferne Bäume/kleine Steine OHNE Schatten
  zu einem Objekt (`join_noshadow`), Felsen-Vorlagen Unterteilung 2, Büsche-Blätter Ikosaeder 0, 100 Büsche, ferne Akazien 700 Blattbüschel,
  am Tag keine Feuer-Lichter → ~7 Bilder/min mit 2 Prozessen (3 Prozesse bringen nichts, Speicher wird knapp).
- WICHTIG Cloud: Läuft in der Sitzung kein Prozess mehr (Antwort beendet, kein Hintergrund-Befehl), wird der Rechner nach wenigen Minuten
  pausiert und `setsid nohup`-Renderjobs sterben. Bei langen Renderläufen daher immer einen Hintergrund-Warter laufen lassen
  (Bash run_in_background, timeout 7200000, until-Schleife) und nach Ablauf neu starten; zusätzlich Check-ins per send_later.
- Plattenplatz Cloud: Einzelbilder (~2 MB/PNG) füllen die Sitzung (Folge 3 lief voll) → `render_qissa_kaaba.sh` kodiert jede fertige
  Einstellung sofort zu MP4 und löscht ihre PNGs (`try_enc`). Alte Einzelbilder fertiger Folgen (out/*_frames) löschen, Videos behalten.
- Nutzer (21.11.2026): Ablauf und Qualität GENAU so lassen wie bei Folge 1–3 (volle Auflösung, 2 Samples, 30 fps → 60 fps, CPU-Rendern
  in der Cloud). Keine Grafikkarte/Miet-GPU, keine Qualitätsabstriche vorschlagen. Pannen (Pause ohne Warter, volle Platte) vermeiden.

## QISSAH Folge 4 „Die Schlacht von Badr“ (Nov. 2026)
- Titel im Video „WAS GESCHAH BEI BADR?“, Überblick über die ganze Schlacht (Nutzerwunsch), 2:42 min, Text vom Nutzer genehmigt.
  Quellen: Muslim 1763 (Bittgebet, Umhang/Abu Bakr, Haizum, 70/70), Bukhari 3951/3952 (al-Miqdad)/3957/3995, Ahmad 1023/3901, Koran 8:7–11, 8:41, 3:123.
- Kampf OHNE Blut (Nutzer einverstanden): Hiebe treffen nur Schild/Klinge, Staub, Schnitt; der stürzende Gegner wird von einer Staubwolke verdeckt.
  Prophet ﷺ = Licht-Säule, Engel = Lichtstreifen (`BW.light_rider`), Sahaba mit Namen (al-Miqdad, Abu Bakr) mit Licht über dem Kopf.
- Stimmen: Erzähler ElevenLabs (Helmut), al-Miqdad = Algenib, Abu Bakr = Sadaltager (2.5-flash, Hall), Prophet ﷺ = Charon (3.8 + Hall).
- Dateien: `src/qissa_badr/`, `scripts/build_qissa_badr.py` (PLAN-Typ `extra` = Einstellung nur als Quelle für Ausschnitte: `kampf`, `kolonne`),
  Blender `blender/qissa/badr.py` (15 Einstellungen) + `badr_world.py` (Tal von Badr über `MK.height`-Austausch, Pferd mit Galopp/Aufbäumen,
  Kämpfer mit Schwert/Schild/Kettenhemd/Helm, ferne Heere als ein Objekt, Staubkarten, Regen, nasser Sand, Fahnen mit Wellen-Modifikator),
  Ton `scripts/sfx_qissa_badr.py` (+15 ElevenLabs-Geräusche), Gesamtablauf fortsetzbar: `setsid nohup ./scripts/v1_qissa_badr.sh > out/bd_v1.log 2>&1 &`.
- Gelernt: Kamera-Gierwinkel zwischen Schlüsselbildern über ±180° → Kamera dreht den langen Weg (`ck()` in badr.py entfaltet die Winkel).
  Flaches Gelände bei tiefer Sonne warf Schatten auf sich selbst (großes Vieleck-Muster) → Gelände `visible_shadow = False`, nicht mit
  join_static verschmelzen. Fahnen/ferne Heere/Mondsichel mit `["person"] = 1` markieren (sonst friert join_static den Wellen-Modifikator ein).
  Ferne Kegel-Figuren nur weit weg (> 20 m) – nah sehen sie aus wie Grabsteine.
- **v2 (Nutzer, 23.11.2026: „gut aber langweilig, wenig los, Schlafende wie tot, Kampf robotik – mehr Action“):**
  neuer Text (genehmigt) mit Zweikampf Hamza/Ali/Ubaida (Abu Dawud 2665, Bukhari 3969) und Abu Jahl + zwei Jungen „wie Falken“
  (Bukhari 3141/3988), Miqdad-Zitat gekürzt, 2:52. Einstieg mit Kampf-Ausschnitten statt Marsch.
  Kampf mit ganzem Körper: `BW.brawl()` (Bild-für-Bild: ausholen mit Oberkörper-Drehung, schneller Hieb + Ausfallschritt,
  Block/Rückstoß, Umkreisen, Füße), `swing_at`, `stagger`, `charge`, `arrows`, `dust_puff`; Kamera-Ruck `Q.handheld(hits=…)`.
  Schlafende NICHT auf dem Rücken: `BW.dozer` (sitzt, Hände im Schoß, nickt ein, atmet, z. T. Kapuze), `BW.curled` (eingerollt
  unter Decke, atmet), `BW.tarp` (Regendach + Lampe). Weniger Dunst (`BW.daylight`). Harte Schnitte in einer Einstellung:
  zwei Schlüsselbilder in aufeinanderfolgenden Bildern, das erste CONSTANT (duell, abujahl). Hochformat ist schmal (±18°):
  Action muss nahe der Blickrichtung liegen. Positionen von Figuren immer per `BW.pos_at(P, t)` lesen (frame_set setzt
  root.location zurück – sonst teleportieren Figuren). Erzähler: zu lange Pausen per `capPause` (0,72 s) gekürzt.
  Ablauf: `setsid nohup ./scripts/v2_qissa_badr.sh > out/bd_v2.log 2>&1 &` → `out/qissah-badr-klein.mp4`.

## QISSAH Folge 5 „Die Hidschra – der Jäger in der Wüste“ (Nov. 2026)
- Titel im Video „WER JAGTE DEN PROPHETEN ﷺ?“, Ich-Sicht Suraqa (er ist die Kamera). Text vom Nutzer genehmigt (Spinnennetz rein –
  Musnad Ahmad 3251, Kette umstritten; Kisra-Armreifen raus, mursal). Wegen Länge gekürzt (erst 3:25 → 2:52). Quellen: Bukhari 3905, 3906,
  3615, 3653, 3911, 3902, 3934; Muslim 2381, 1218; Koran 8:30, 9:40.
- Stimmen: Erzähler ElevenLabs (Helmut), Prophet ﷺ = Charon (3.8 + Hall), Abu Bakr = Sadaltager (Hall), Suraqa = Zubenelgenubi (Dialog),
  Stammesmann = Puck, Verfolger = Algenib (2.5-flash).
- Dateien: `src/qissa_hijra/`, `scripts/build_qissa_hijra.py`, Blender `blender/qissa/hijra.py` (19 Einstellungen, `jagd` = Quelle für den
  Einstieg) + `hijra_world.py` (Mekka = Tal aus mekka.py mit ebenem Stadtboden + Lehmhäuser + alte Kaaba; Höhle = Fels mit Hohlraum per
  Boolean + Spinnennetz; Küstenebene mit Meer im Westen; Beduinenzelt; Medina mit Lavafeld + Palmen), Ton `scripts/sfx_qissa_hijra.py`
  (+11 ElevenLabs-Geräusche), Ablauf `setsid nohup ./scripts/v1_qissa_hijra.sh >> out/hj_v1.log 2>&1 < /dev/null &` → `out/qissah-hijra-klein.mp4`.
- Gelernt: `join_noshadow` mit bpy.ops.object.join verwürfelte Objekte mit geteiltem Netz (Sträucher/Bäume schwebten im Himmel) →
  in hijra.py eigenes Verschmelzen per bmesh (Weltmatrix je Objekt). Ich-Sicht im Sattel: `ride()` setzt Kamera je Bild auf das Pferd
  (Pferd ohne Sattel, Mähne als glatter Kamm, Fäuste + Zügel, Blick geradeaus – sonst wirkt der Pferdekopf von oben seltsam).
  Hochformat ist schmal: in der Höhle beide Figuren nahe der Blickachse setzen.
  `ck()` entfaltet Gierwinkel relativ zum vorigen Schlüssel, `ride()` setzt sie roh → beim Übergang zu ride() kann ein 360°-Sprung
  entstehen (Kamera dreht sich einmal im Kreis). Sattel-Schlüssel daher per `Q.cam_keys` mit demselben atan2-Winkel wie ride().
  Nachbesserung einer Einstellung: `scripts/fix_qissa_hijra_pferd.sh` (Einstellung neu, nur betroffenen Remotion-Teil neu, `pN.mp4.ok` löschen).
- **v2 (Nutzer, 25.11.2026):** Reiten neu (`SPath` = weiche Catmull-Rom-Kurve statt Ecken, `Gait` = Anlauf/Abbremsen, `horse_go` statt
  BW.horse_run: steht lebendig mit geraden Beinen, Kamera halbes Wippen, Bewegungsunschärfe `cfg["mblur"]` kostet nichts), Zügel per
  Constraint von der Faust zum Gebissring (`reins()`), Mähne aus flatternden Büscheln, `horse_idle` (atmet, schnuppert, scharrt),
  Sturz nach vorn über die Schulter (`fall_off`), Versinken mit Sandwall um die VORDERbeine (`sand_ring`/`sand_spray`/`sand_drip`, Material
  = Boden-Sand), Staubsäule, Lospfeile: Hand-Weltmatrix per `_hand_world` angeglichen (Übergabe Köcher -> Hand -> andere Hand unsichtbar),
  Türnische per Boolean (Schnittkörper muss über Wand/Boden HINAUSragen, sonst kein Loch), Netz per Strahlen in die echte Felsöffnung
  (`fitted_web`), dunkle Platte hinter dem Netz, Verfolger nahe der Blickachse. `set_z` je Bild (jedes 3. Bild ließ Läufer „hängen“).
  Überblendungen: jede Einstellung XF = 0,4 s länger gerendert (build: `frames` + Handle), Remotion blendet weich über (`FadeIn`).
  Einstieg: „KOPFGELD · 100 KAMELE“ / „TOT ODER LEBENDIG“ mit Einschlag. Ablauf: `setsid nohup ./scripts/v2_qissa_hijra.sh >> out/hj_v2.log 2>&1 < /dev/null &`.
  Staubsäule: `smoke_column` (viele SCHMALE Karten steigen nacheinander auf, `smoke_mat` mit feinerem Rauschen, leichter Wind) –
  wenige große Karten verschmolzen zu einem verschwommenen Fleck; Kamera dabei nicht in den Himmel schwenken (Pferd bleibt im Bild).
  Ort-Zeile = gesprochene Form („AL-MADINA“, nicht „MEDINA“). Fertige Einstellungen während des Renderns per Kontaktbogen prüfen
  (ffmpeg select+tile) – Nachbessern ist dann billiger. Änderungen an hijra.py während laufender Renderjobs: erst Kopie testen,
  dann per `mv` tauschen (neue Blender-Prozesse laden die Datei neu), Einstellung erst danach löschen (keine alten Zwischenbilder).
  v2-Ergebnis: 2:57,7, 58,9 MB, −14 LUFS.

## POV-Erinnerung „Was, wenn das dein letzter Flug ist?“ (Nov. 2026, ohne QISSAH-Logo)
- Nutzerwunsch: anderes Format – Ich-Sicht im Flugzeug, Turbulenzen/Absturzgefahr, alle rufen Allah an, sichere Landung, nach 20 min
  alles vergessen (Koran 17:67), Erinnerung: jederzeit kann es der letzte Moment sein → zu Allah zurückkehren. Text genehmigt. KEIN QISSAH-Logo
  („ohne diesmal, einfach was Passendes“) – Ende = schwarze Tafel mit 2:156. Länge 2:35 (inkl. ~35 s Rezitation).
- **Koran: ECHTER Rezitator** (Nutzer wollte erst KI – Probe C „Erzähler liest Arabisch“ und arabische KI-Stimmen A/B verworfen, dann
  „mach einfach echte Rezitator“): **Maher al-Muaiqly** (Nutzer wählte aus 8 Proben), Aufnahmen Vers für Vers von **everyayah.com**
  (Host in Umgebung „Standard“ freigeschaltet, `https://everyayah.com/data/<Rezitator>/<SSSVVV>.mp3`), Teilstücke per Lautstärke-Hüllkurve +
  Spracherkennung (Arabisch) geschnitten, **leichter Hall** (`voice_gemini.hall(sec=2.0, wet=0.25)`; Nutzer fragte, ob erlaubt – leichter
  Hall ändert die Worte nicht). Bild: arabische Schrift in Gold Wort für Wort (Zeiten aus STT) + deutsche Übersetzung (Bubenheim/Elyas) darunter.
- Figuren (je Figur 2 Proben, Nutzer wählte jeweils A): Du = Juan `lx8LAX2EUAKftVz0Dk5z`, Sitznachbar = Albert `f2yUVfK5jdm78zlpcZ8C`,
  Kapitän = Thomas Schendel `Fghah4fztZORbiKfIGAs` (Bordlautsprecher-Filter in sfx_flug.py), Flugbegleiterin = Anna `DEZHhPbmb8LVZmWufkCh`,
  Frau = Amira `FOfJ2PMgU6HOGbNYnzto`, Worte des Propheten ﷺ = Christian (wie Folge 5). **„Ya Allah“ im el-Text als „Yaa Allaah“**
  (arabische Schrift / „Ya Allah“ wurde zu „Yallah“ = andere Bedeutung!), Frau „Ya Rabbi“; jede Figurenzeile per STT geprüft.
- Ton „wie im Film, nie still“ (Nutzer): 28 ElevenLabs-Geräusche `assets/sfx/el_fl_*.flac` (Kabine, Gong, Durchsage, Turbulenz, Absacken,
  Alarm, Masken, Sturm, Schreie, Donner, Baby, Sturzflug, Aufsetzen, Applaus, Gate, Terminal, Schritte, Tür, Raum, Teppich, Handy, Herzschlag …),
  Mix `scripts/sfx_flug.py` (Atmo präsenter: 0.22).
- Dateien: `src/flug/` (script.json mit `recitations`, Flug.tsx, Komposition `Flug`), `scripts/build_flug.py` (Schritt ("r", id) = Rezitation,
  Tafeln mit Schritten), Blender `blender/qissa/flug.py` (10 Einstellungen) + `flug_world.py` (Kabine 3+3 mit echten Fensteröffnungen per
  Boolean, Gepäckfächer mit Klappen, Service-Leiste, Masken fallen + pendeln, Flügel mit Positions-/Blitzlicht, Wolkenmeer, Gewittertürme +
  Blitze, Landebahn + Flughafenlichter, Terminal bei Dämmerung, Gebetsraum + Teppich zum Ausrollen), Texturen `scripts/flug_textures.py`
  → `blender/qissa/tex/flug_*.png` (Handy-Feed, „Isha“-Hinweis, Flugkarte, Schilder). Ablauf: `setsid nohup ./scripts/v1_flug.sh >> out/fl_v1.log 2>&1 < /dev/null &`
  → `out/flug-letzter-flug-klein.mp4`. TikTok-Text: `videos/flug-letzter-flug.md`.
- Gelernt: Bild-Flächen brauchen eine UV-Lage VOR `create_grid(calc_uvs=True)`, und join_static verlor die UVs → Bildflächen mit
  `["person"]=1` einzeln lassen. `lib.person(sit=True)` sitzt im Schneidersitz (Knie breit) → im Flugzeugsitz `seat_knees()`. Nachbar direkt
  daneben (0,46 m) klebte an der Kamera → Platz 0B frei, Nachbar am Gang (0C). Blitz-Licht durchs Fenster max. ~800 W (sonst alles weiß);
  schaut die Kamera auf die nahe Lehne, schon ~280 W zu hell → dort Blitz-Stärke 0,1–0,2. Eigene Sauerstoffmaske hängt 0,2 m vor dem Auge
  (gelber Fleck füllt das Bild) → im Absturz 0,27 m höher. Schwebende Sachen nur zwischen Auge und Lehne (Lehne bei y ≈ 0,44) und mittig
  (Hochformat ist auf 0,3 m Abstand nur ~0,25 m breit). `FW.img_mat(emit=0)` verbindet das Bild NICHT mit der Leuchtfarbe → später per
  `emit_strength` eingeschaltet leuchtet die Fläche gleichmäßig weiß (Anschnallzeichen) → `emit=0.001` nehmen.
  Bewegte Außenwelt (`world`) dreht um IHREN Ursprung: eine Restneigung (0,5°) hebt den Boden beim Ausrollen um y·sin(Winkel)
  durch die Kabine (Nachbar schien zu versinken) → nach dem Aufsetzen Neigung auf 0 schlüsseln.
  Blitz-Schlüssel (`FW.lightning`, 0 → 1 nach 0,03 s) fielen bei 30 fps teils auf DASSELBE Bild → die 0 wurde überschrieben und das
  Fensterlicht stieg sekundenlang an (Bild fast weiß). Helfer legt Schlüssel jetzt auf verschiedene Bilder. Teil-Neurendern einer Einstellung:
  `FRAMES=a-b` (Haupt- und `MID=1`-Bilder) in eigenen Ordner, erstes Bild per PSNR mit dem alten Video vergleichen, dann einsetzen.
- **v2 (Nutzer, 28.11.2026: „Köpfe/Arme durch Sitze/TV, Masken benutzt keiner, Positionen komisch, Fensterlücken, Ya-Allah-Frau
  kitschig, Chill = Clown-Stimme, Bruder-Satz passt nicht, TV zeigt nach Landung 23:05, Geschrei bei Landung“):**
  - Stimmen: Albert (Nachbar) lag bei 300–500 Hz (klang wie Frau/Clown) -> Nachbar = Lennart `GoXyzBapJk3AoCJoMQl9` (Nutzer B),
    „Ya Allah, rette uns“ + „Ya Rabbi … meine Kinder“ = Mutter, Stimme Freya `9zTcBiIWSks5baYw5ntG` (Nutzer A: mittlere Lage MIT Gefühl –
    zu hoch = kitschig, zu tief = ohne Gefühl). Tonhöhe der Kandidaten messen (`scripts/flug_v2_voices.py`). l1 = „Alhamdulillah … ich dachte
    echt, das war's.“
  - Haltungen GERECHNET (`blender/qissa/flug_pose.py`): Zwei-Gelenk-IK `set_arm` (Hand an Weltpunkt), `brace_real` (Stirn 3 cm vor der
    Lehne, Hände darüber), `hands_armrest`/`hands_lap`/`hands_dua`/`hands_clap`, Masken `put_on`/`take_off`/`wear_from_start`
    (Maske am Kopf, Schlauch per STRETCH_TO zur Service-Leiste, Namen `mskw…` = nicht verschmelzen). Wackeln am KOPF-Gelenk, nicht am Nacken.
    Prüfung `blender/qissa/flug_check.py` (DBGPY, nur sichtbare Punkte, Tiefe > 1 cm) -> vor dem Rendern alle Einstellungen auf ~0.
  - Familie direkt HINTER mir (Reihe -1, wie in „kabine“): bei a3/a4 dreht sich die Kamera über die eigene Lehne um (Gesichter von vorn).
    Eigener Maskenschlauch `visible_camera = False` (lief als unscharfer Balken vor der Linse). Flugbegleiterin kniet im Gang.
  - Fenster: Superellipse-Schnitt GRÖSSER als der Schacht + Blende bündig auf der Wand + Schacht bis zur Scheibe (`window_well`), Rollo im Schacht.
  - Bildschirm-Bilder `flug_ife*.png` (22:25 / NOCH 20 MIN / GELANDET / WILLKOMMEN 22:46) per `FW.set_ife`. Applaus neu `el_fl_applause2`
    (altes hatte Jubelrufe – Geräusche per STT `tag_audio_events=true` prüfen).
