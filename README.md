# TikTok-Textvideos – kostenlos mit Claude + Remotion + edge-tts

Fertiges Beispiel: [`out/video.mp4`](out/video.mp4) (1080×1920, 30 fps, ~23 s)

## Was du brauchst (alles gratis außer deinem Claude-Pro-Abo)
| Teil | Tool | Kosten |
|---|---|---|
| Ideen, Skript, Code | Claude Pro (Claude Code) | hast du schon |
| Video rendern | [Remotion](https://www.remotion.dev) | gratis für Privatpersonen |
| KI-Stimme | [edge-tts](https://github.com/rany2/edge-tts) (Microsoft-Neural-Stimmen) | gratis |
| Programme | [Node.js](https://nodejs.org), [Python](https://python.org), [FFmpeg](https://ffmpeg.org) | gratis |

## Einmalig einrichten
```bash
git clone <dieses-repo> && cd U
npm install
pip install edge-tts
```

## Video machen
1. Text in `src/script.ts` ändern (oder Claude Code sagen: *„Mach ein Video über XY“*).
2. `npm run video` → erzeugt die Stimme und rendert `out/video.mp4`.
   - Ohne Stimme: `npm run render`
   - Live-Vorschau im Browser: `npm run studio`
3. Video aufs Handy schicken und bei TikTok hochladen (Musik kannst du in TikTok drüberlegen).

## Stimme ändern
In `scripts/voice.py` → `VOICE = "de-DE-KatjaNeural"` (weiblich) oder `de-DE-ConradNeural` (männlich).
Alle Stimmen: `edge-tts --list-voices`
