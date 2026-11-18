#!/usr/bin/env python3
"""Hörprobe Erzähler im Doku-Stil (QISSA Adhan, Nutzer 18.11.2026: „überall roboterhaft – will so eine Erzählerstimme
wie bei YouTube-Dokus“). Zwei Regie-Varianten, je die ersten zwei Stücke (Einstieg + Beratung) – genau so erzeugt wie
später im Video (kurze Anfragen, Stück-Modus). Die gewählte Variante wird direkt weiterverwendet:

  GEMINI_API_KEY=proxy-injected python3 scripts/qissa_doku_probe.py          # 4 Anfragen (gemini-2.5-flash-tts)
  python3 scripts/qissa_doku_probe.py --waehle 1                            # Variante 1 übernehmen (keine Anfrage)

Ergebnis zum Anhören: out/stimmproben/doku-variante-1.m4a / -2.m4a
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import voice_gemini as V  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "src" / "qissa_adhan" / "script.json"
OUT = ROOT / "out" / "stimmproben"
CHUNKS = ["d3", "d6", "d9", "e6"]  # neues Stück ab diesen Sätzen (Szenenwechsel)

BASE = (
    "# AUDIO PROFILE\n"
    "Erzaehler: a deep, warm German documentary narrator, like the narrator of a high-quality history documentary on YouTube "
    "or German TV. A real human voice: relaxed, natural, effortless and confident, with calm authority. Rich and full, close "
    "to the microphone. He also speaks Arabic like a native speaker.\n"
    "Junge: a young man from Medina, about 20 years old, worried and emotional, natural, a little breathless.\n"
    "## THE SCENE\nA true story from Medina in the year 622, told in a cinematic history documentary.\n"
    "### DIRECTOR'S NOTES\n"
    "Erzaehler: natural documentary storytelling with a natural German sentence melody, as if he really tells the story to "
    "the listener - never reading, never theatrical, never sing-song, never robotic. Unhurried, even pace; let the sentences "
    "breathe, with natural breaths between them. {extra}Calm and reverent whenever he mentions the Prophet. The words in Arabic "
    "script are Arabic names and terms: pronounce them exactly like a native Arabic speaker, in the same voice and without any "
    "extra pause, then continue fluently in German.\n"
    "Junge: natural and emotional, like a real person; Arabic-script names spoken like a native Arabic speaker.\n"
    "Leave a clear short pause between the lines."
)
VARIANTS = {
    1: BASE.format(extra="Understated and warm, like a calm documentary voice-over. "),
    2: BASE.format(extra="Subtle suspense: at mysterious moments he slows down and gets a little quieter and gently "
                         "emphasizes the key words - but stays natural and understated, like a documentary, not a trailer. "),
}


def main() -> None:
    script = json.loads(SCRIPT.read_text(encoding="utf-8"))
    pc = script["voiceParts"]["0"]
    full = OUT / f"qissa_adhan-p0-{'+'.join(pc['speakers'].values())}.k.wav"
    if "--waehle" in sys.argv:
        n = int(sys.argv[sys.argv.index("--waehle") + 1])
        pc["notes"], pc["chunks"] = VARIANTS[n], CHUNKS
        SCRIPT.write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        for k in (0, 1):
            shutil.copy(OUT / f"doku-{n}-k{k}.wav", full.with_name(f"{full.stem}{k}.wav"))
        print(f"✅ Variante {n} übernommen: Regie in script.json, Stücke 1+2 als {full.stem}0/1.wav")
        return
    block = [s for s in script["sentences"] if s.get("text") and s.get("part", 0) == 0]
    groups, starts = [], set(CHUNKS)
    for s in block:
        if not groups or s["id"] in starts:
            groups.append([])
        groups[-1].append(s)
    cfg = {"model": pc["model"], "speakers": pc["speakers"]}
    for n, notes in VARIANTS.items():
        parts = []
        for k, g in enumerate(groups[:2]):
            f = OUT / f"doku-{n}-k{k}.wav"
            if not f.exists():
                text = notes + "\n#### TRANSCRIPT\n" + "\n".join(f"{s['speaker']}: {V.spoken(s)}" for s in g)
                print(f"🎙️  Variante {n}, Stück {k + 1} …", flush=True)
                V.save_audio(f, V.tts(text, pc["speakers"]["Erzaehler"], cfg))
            parts.append(f)
        lst = OUT / f"doku-{n}.list"
        lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
        m4a = OUT / f"doku-variante-{n}.m4a"
        vf = script.get("voiceFilter", "")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-af",
                        f"{vf + ',' if vf else ''}loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                        str(m4a)], check=True)
        lst.unlink()
        print(f"🎧 {m4a.relative_to(ROOT)}  ({V.duration(m4a):.1f}s)")


if __name__ == "__main__":
    main()
