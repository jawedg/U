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
- Rendern 2D (ohne --gl): `npx remotion render ErsterAdhan2D out/erster-adhan-2d.mp4 --concurrency=6 --browser-executable=...`
