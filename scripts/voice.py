#!/usr/bin/env python3
"""Erzeugt KOSTENLOS eine KI-Stimme pro Szene mit edge-tts (Microsoft-Neural-Stimmen).

Einmalig installieren:  pip install edge-tts
Starten:                npm run voice      (oder: python3 scripts/voice.py)

Stimme ändern: VOICE unten anpassen. Gute deutsche Stimmen:
  de-DE-ConradNeural (männlich), de-DE-KatjaNeural (weiblich),
  de-DE-FlorianMultilingualNeural, de-DE-SeraphinaMultilingualNeural
Alle Stimmen anzeigen: edge-tts --list-voices
"""
import asyncio
import json
import re
import subprocess
from pathlib import Path

import edge_tts

VOICE = "de-DE-ConradNeural"
RATE = "+8%"  # etwas schneller klingt mehr nach TikTok

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "src" / "script.ts"
OUT_DIR = ROOT / "public" / "voice"
VOICE_JSON = ROOT / "src" / "voice.json"


def read_scenes() -> list[str]:
    src = SCRIPT.read_text(encoding="utf-8")
    block = src[src.index("SCENES") :]
    texts = re.findall(r'text:\s*"((?:[^"\\]|\\.)*)"', block)
    return [t.replace("*", "") for t in texts]


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(out.strip())


async def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scenes = []
    for i, text in enumerate(read_scenes()):
        target = OUT_DIR / f"scene-{i}.mp3"
        print(f"🎙️  Szene {i + 1}: {text}")
        await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(target))
        scenes.append({"file": f"voice/scene-{i}.mp3", "seconds": round(duration(target), 3)})
    VOICE_JSON.write_text(json.dumps({"scenes": scenes}, indent=2) + "\n", encoding="utf-8")
    print(f"✅ {len(scenes)} Sprachdateien erstellt -> jetzt `npm run render`")


if __name__ == "__main__":
    asyncio.run(main())
