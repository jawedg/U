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
- **Menschen dürfen gezeigt werden, aber NIE mit Gesicht** (leerer Kopf). Sahaba/wichtige Personen zusätzlich mit
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
- Serienname vorläufig **QISSA** (قصة = Geschichte), Zusatz „WAHRE GESCHICHTEN“ – Nutzer kann ihn noch ändern (Title/Card in QissaAdhan.tsx).
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
