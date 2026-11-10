# Projekt: TikTok-Videos mit Claude (Remotion)

## Vorlieben des Nutzers (immer beachten)
- Sprache: Deutsch, einfach erklären.
- **Stimme: Google Gemini TTS, Stimme „Charon“** (`npm run voice:3d` bzw. `python3 scripts/voice_gemini.py --voice Charon`).
  - Piper/edge-tts gefallen dem Nutzer NICHT (zu roboterhaft).
- **Stil: 2D-Strichzeichnung („von früher“)** wie `src/athan2d/` – helle Linien auf dunklem Grund, Gold-Akzente,
  Papier-Körnung, Ort-Label + arabischer Text oben, Satz-Untertitel unten (gesprochene Wörter hell, Schlüsselwörter gold).
  3D (`src/train`, `src/athan`) gefällt dem Nutzer NICHT mehr (zu holprig).
- Format 1080×1920.

## Gemini-TTS – wichtig
- API-Schlüssel kommt aus der Umgebungsvariable `GEMINI_API_KEY`. Niemals ins Repo schreiben.
  Fehlt er: Nutzer bitten, ihn in den Umgebungs-Einstellungen als Secret `GEMINI_API_KEY` einzutragen.
- Das Modell liest Stil-Anweisungen im Text MIT VOR → nur den reinen Text schicken.
- Free Tier: nur ~10 Anfragen/Tag pro Modell → ganzen Text in EINER Anfrage erzeugen
  (macht das Skript automatisch, schneidet dann an den Pausen). Ausweichmodell:
  `GEMINI_TTS_MODEL=gemini-3.1-flash-tts-preview`.
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
- `LernFuellstand` (kb = 6, Label „BT“, gleiches dunkles Bewegungs-Design wie `LernGK`), Skript `scripts/build_fs_script.py`
  → `src/lern_fs/`. Nutzerwunsch: echte Prüfungsaufgabe Schritt für Schritt lösen (Bild, Schaubild, Rechnung), dann eigenes
  Beispiel im Prüfungsstil. Technik-Grafiken in `src/lern/Tech.tsx`: `tank` (Behälter + Ultraschall, Füllstand animiert),
  `graph` (Schaubild mit Punkten, Gerade, Steigungsdreieck, Ablesen), `scales` (Volt ↔ Digitalwert), `calc` (Rechenweg tippt sich).
- Zahlen im Sprechtext als Ziffern schreiben (Gemini liest sie richtig, Untertitel zeigen Ziffern). Cue-Wörter: Satzzeichen
  werden entfernt („1,5“ → „15“), daher Wort-Cues verwenden. Videos für den Nutzer ≤ ~60 MB halten (größere lassen sich in der App nicht speichern).
