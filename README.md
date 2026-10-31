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

---

# 3D-Erklärvideo (wie die „Zug-Videos“ auf TikTok)

Fertiges Beispiel: [`out/erklaervideo-3d.mp4`](out/erklaervideo-3d.mp4)
– Low-Poly-3D-Welt bei Nacht, Kamerafahrten, KI-Stimme, ein Wort pro Moment als Untertitel (Schlüsselwörter gelb).

**Komplett kostenlos & offline:** 3D mit Remotion + Three.js, Stimme mit Piper „Thorsten“ (deutsch).

## Einmalig
```bash
npm install
pip install "sherpa-onnx==1.12.40" soundfile
mkdir -p models && cd models
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-de_DE-thorsten-high.tar.bz2
tar xjf vits-piper-de_DE-thorsten-high.tar.bz2 && cd ..
```

## Video machen
1. Text ändern in `src/train/script.json` (ein Satz = eine Kameraeinstellung, `*Wort*` = gelb).
2. `npm run video:3d` → Stimme + Video in `out/erklaervideo-3d.mp4`.
   Live-Vorschau: `npm run studio`.

## Mit Claude neue Themen machen
Öffne Claude Code in diesem Ordner und sag z. B.:
> „Mach ein neues 3D-Erklärvideo im gleichen Stil über *Warum Flugzeuge Kondensstreifen machen*.
> Bau dafür eine passende 3D-Szene in `src/`, schreib das Skript, erzeug die Stimme und rendere es.“

| Datei | Inhalt |
|---|---|
| `src/train/script.json` | Text + welche Kameraeinstellung pro Satz |
| `src/train/shots.ts` | Kamerafahrten & Effekte pro Einstellung |
| `src/train/world.ts` | 3D-Modelle (Zug, Gleise, Signale, Landschaft) |
| `src/train/TrainVideo.tsx` | Untertitel, Übergänge, Ton |
| `scripts/voice_piper.py` | kostenlose Offline-Stimme |
