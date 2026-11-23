#!/usr/bin/env python3
"""QISSAH Folge 3: Aussprache eines Namens im Erzähler verbessern, OHNE den Zeitplan zu ändern.

Jeder Erzähler-Satz, der den Namen enthält, wird mit der neuen Schreibweise einzeln neu erzeugt (ElevenLabs, gleiche Stimme,
gleiche Regie-Tags), auf genau die Sprechdauer des alten Satzes gebracht (atempo) und an derselben Stelle in die alte Datei
gelegt (gleiche Ränder). Wortzeiten der Untertitel kommen aus den neuen Buchstaben-Zeiten. So bleiben Bild, Schnitte und Ereignisse.

  python3 scripts/fix_names_kaaba.py "زمزم" "زَمْزَم" e12     # alt -> neu (im Feld el), nur diese Satz-IDs
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import voice_gemini as V  # noqa: E402

D = ROOT / "src" / "qissa_kaaba"
SR = 48000


def pcm(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(float) / 32768


def span(x, thr=-42):
    hop = 480
    n = len(x) // hop
    rms = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) for i in range(n)]) + 1e-9
    on = np.where(20 * np.log10(rms) > thr)[0]
    return on[0] * hop / SR, (on[-1] + 1) * hop / SR


def main():
    old, new = sys.argv[1], sys.argv[2]
    only = set(sys.argv[3:])  # optionale Satz-IDs
    script = json.loads((D / "script.json").read_text(encoding="utf-8"))
    timing = json.loads((D / "timing.json").read_text(encoding="utf-8"))
    pc = script["voiceParts"]["0"]
    voice = next(iter(pc["speakers"].values()))
    cache = ROOT / "out" / "stimmproben"
    for i, s in enumerate(script["sentences"]):
        if s.get("part") != 0 or old not in s.get("el", "") or (only and s["id"] not in only):
            continue
        ln = timing["lines"][i]
        f = ROOT / "public" / ln["file"]
        el = s["el"].replace(old, new)
        if not el.rstrip().endswith("..."):
            el = el + " ..."  # Ausklang, sonst schneidet ElevenLabs hart ab
        mp3, al = V.eleven_tts(el, voice, pc["model"], pc.get("settings"), cache)
        wav = mp3.with_suffix(".proc.wav")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), "-af", "highpass=f=60,loudnorm=I=-16:TP=-1.5:LRA=11",
                        "-ar", str(SR), "-ac", "1", str(wav)], check=True)
        xo, xn = pcm(f), pcm(wav)
        o0, o1 = span(xo)
        n0, n1 = span(xn)
        k = (n1 - n0) / (o1 - o0)  # > 1: neuer Satz länger -> schneller abspielen
        gap_at, extra = None, 0.0
        if k < 0.93:  # neuer Satz deutlich kürzer: NICHT langsamer sprechen (klingt zäh), sondern die längste Sprechpause verlängern
            hop = 480
            xs = xn[int(n0 * SR):int(n1 * SR)]
            db = 20 * np.log10(np.array([np.sqrt(np.mean(xs[i * hop:(i + 1) * hop] ** 2)) for i in range(len(xs) // hop)]) + 1e-9)
            best, run, bs = (0, 0), 0, 0
            for i, q in enumerate(db < -42):
                run = run + 1 if q else 0
                if run == 1:
                    bs = i
                if run > best[1]:
                    best = (bs, run)
            gap_at = n0 + (best[0] + best[1] / 2) * hop / SR if best[1] * hop / SR > 0.12 else n1
            extra = 0.55 * ((o1 - o0) - (n1 - n0))  # Rest bleibt als Atempause am Satzende
            k = 1.0
        seg = ROOT / "out" / f"zz_fix_{s['id']}.wav"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{max(0, n0 - 0.02):.4f}", "-t", f"{n1 - n0 + 0.04:.4f}", "-i", str(wav),
                        "-af", f"atempo={k:.5f}", "-ar", str(SR), "-ac", "1", str(seg)], check=True)
        y = pcm(seg)
        if gap_at is not None:
            g = int((gap_at - max(0, n0 - 0.02)) * SR)
            y = np.concatenate([y[:g], np.zeros(int(extra * SR)), y[g:]])
            print(f"   {s['id']}: Pause bei {gap_at - n0:.2f}s um {extra:.2f}s verlängert (Tempo bleibt)")
        out = np.zeros_like(xo)
        a = int(max(0, o0 - 0.02) * SR)
        m = min(len(y), len(out) - a)
        out[a:a + m] = y[:m]
        fl = int(0.012 * SR)  # weiche Ränder
        out[a:a + fl] *= np.linspace(0, 1, fl)
        e = a + m
        out[max(a, e - int(0.05 * SR)):e] *= np.linspace(1, 0, e - max(a, e - int(0.05 * SR)))
        import wave
        with wave.open(str(f), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
        # Wortzeiten: gesprochene Wörter aus den neuen Buchstaben-Zeiten, auf den Platz im alten Satz umgerechnet
        ch, st = al["characters"], al["character_start_times_seconds"]
        mask = [True] * len(el)
        for mt in V.TAG.finditer(el):
            for j in range(mt.start(), mt.end()):
                mask[j] = False
        sp, j = [], 0  # (Beginn, Wort) je gesprochenem Wort (auch „...“ zählt wie im Untertitel-Text)
        while j < len(el):
            if mask[j] and not ch[j].isspace():
                w0 = j
                while j < len(el) and mask[j] and not ch[j].isspace():
                    j += 1
                sp.append((st[w0], el[w0:j]))
            else:
                j += 1
        disp = s["text"].split()
        if len(sp) > len(disp) and sp[-1][1] == "...":
            sp = sp[:-1]  # angehängter Ausklang
        if len(sp) != len(disp) and "..." not in disp:
            sp = [x for x in sp if x[1] != "..."]  # Sprechpausen „...“ nur im el-Text
        t_of = lambda t: round(max(0.0, (o0 - 0.02) + (t - (n0 - 0.02)) / k + (extra if gap_at is not None and t > gap_at else 0.0)), 3)  # noqa: E731
        if len(sp) == len(disp):
            ln["words"] = [{"word": w, "start": t_of(t)} for w, (t, _) in zip(disp, sp)]
        else:  # andere Wortzahl: nach Position im Satz
            tot = sum(len(w) + 1 for w in disp)
            ws, pos = [], 0
            for w in disp:
                ws.append({"word": w, "start": t_of(sp[min(len(sp) - 1, int(pos / tot * len(sp)))][0])})
                pos += len(w) + 1
            ln["words"] = ws
        print(f"   {s['id']}: Tempo {k:.3f}, {len(disp)} Wörter, alt {o1 - o0:.2f}s neu {n1 - n0:.2f}s")
    (D / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    # Hinweis im Skript (el bleibt, damit der ElevenLabs-Cache passt): nach voice_gemini.py dieses Skript erneut ausführen
    script_new = json.loads((D / "script.json").read_text(encoding="utf-8"))
    fixes = script_new.pop("nameFix", None)
    fixes = script_new.get("nameFixes", [fixes] if fixes else [])
    fixes = [f for f in fixes if not (f["old"] == old and f["new"] == new)] + [{"old": old, "new": new, "ids": sorted(only)}]
    script_new["nameFixes"] = fixes
    script_new["nameFixNote"] = "nach voice_gemini.py alle nameFixes der Reihe nach: python3 scripts/fix_names_kaaba.py old new ids…"
    (D / "script.json").write_text(json.dumps(script_new, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("✅ Namen ersetzt; jetzt build_qissa_zamzam.py + sfx_qissa_zamzam.py + Video zusammenfügen")


if __name__ == "__main__":
    main()
