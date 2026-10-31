# Projekt: TikTok-Videos mit Claude (Remotion)

## Vorlieben des Nutzers (immer beachten)
- Sprache: Deutsch, einfach erklären.
- **Stimme: Google Gemini TTS, Stimme „Charon“** (`npm run voice:3d` bzw. `python3 scripts/voice_gemini.py --voice Charon`).
  - Piper/edge-tts gefallen dem Nutzer NICHT (zu roboterhaft).
- Stil: 3D-Erklärvideo wie `src/train/` (Low-Poly-Nachtszene, Kamerafahrten, ein großes Wort pro Moment als Untertitel, Schlüsselwörter gelb), Format 1080×1920.

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
- Erstes Video: `src/athan/` (Komposition `ErsterAdhan`) – „Der erste Adhan“, ca. 1:55 min.
- Zielänge: **1:30–2:00 min** (über 1 min für Creator Rewards, nicht gehetzt, max. ~2:30).
- **Keine Darstellung von Propheten, Sahaba oder anderen Menschen** – nur Orte, Licht, Symbole.
- Bei Erwähnung des Propheten: „Friede sei mit ihm“ sprechen.
- Fakten nur mit Quellen (Hadith-Nummern) – Quellen in `script.json` -> `sources` und in die TikTok-Beschreibung.
- Echte Adhan-Aufnahme: Datei vom Nutzer nach `public/athan/athan.mp3`, dann in `src/athan/script.json`
  `"athanFile": "athan/athan.mp3"` setzen (Länge über `athanSeconds`). Ohne Datei bleibt die Stelle still (nur Wind).
- Kein Musik-Hintergrund, nur leiser Wind (`public/athan/wind.mp3`).
- Stimme: `npm run voice:athan` (Gemini Charon). Tageslimit beachten.
