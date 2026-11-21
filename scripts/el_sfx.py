#!/usr/bin/env python3
"""Geräusche per ElevenLabs-Soundeffekt-Generator (POST /v1/sound-generation) -> assets/sfx/el_<name>.flac (-20 LUFS).
Schlüssel: Network Secret für api.elevenlabs.io (Proxy setzt ihn ein). Vorhandene Dateien werden nicht neu erzeugt.

  python3 scripts/el_sfx.py name "prompt, no music" sekunden [name "…" sek …]
"""
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "sfx"


def gen(name, prompt, sec):
    dst = OUT / f"el_{name}.flac"
    if dst.exists():
        print("✓ vorhanden", dst.name)
        return
    body = {"text": prompt, "duration_seconds": float(sec), "prompt_influence": 0.6}
    req = urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_192", data=json.dumps(body).encode(),
                                 headers={"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "proxy-injected"),
                                          "Content-Type": "application/json"})
    mp3 = OUT / f"el_{name}.mp3"
    with urllib.request.urlopen(req, timeout=180) as r:
        mp3.write_bytes(r.read())
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), "-af", "loudnorm=I=-20:TP=-2:LRA=11", "-ar", "48000", "-ac", "2",
                    str(dst)], check=True)
    mp3.unlink()
    print("🔉", dst.name, sec, "s")


if __name__ == "__main__":
    a = sys.argv[1:]
    for i in range(0, len(a), 3):
        gen(a[i], a[i + 1], a[i + 2])
