#!/usr/bin/env python3
"""QISSAH Folge 3 v2: neu gerenderte Bilder (out/kb_frames2) zu Einstellungs-Videos machen.

Ganze Einstellungen (ankunft, abend2, bau, tuer2, segen) werden neu kodiert (60 fps; segen mit echten Zwischenbildern).
Teilstücke (tuer1 1–360, abend1 1–360, besuch2 210–340) werden in die alten 60-fps-Videos eingesetzt (gleiche Länge, gleicher Zeitplan).
Alte Videos werden vorher als <name>.v1.mp4 gesichert.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
F2 = ROOT / "out" / "kb_frames2"
SH = ROOT / "public" / "qissa_kaaba" / "shots"
X264 = ["-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p"]
MINT = "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"


def nframes(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()
    return int(out)


def pngs(shot, a, b, mid=False):
    d = F2 / (shot + ("_mid" if mid else ""))
    miss = [k for k in range(a, b + 1) if not (d / f"{k:04d}.png").exists() or (d / f"{k:04d}.png").stat().st_size < 1000]
    if miss:
        sys.exit(f"❌ {shot}{' (Zwischenbilder)' if mid else ''}: es fehlen {len(miss)} Bilder, z. B. {miss[:5]}")
    return d


def backup(shot):
    src, bak = SH / f"{shot}.mp4", SH / f"{shot}.v1.mp4"
    if src.exists() and not bak.exists():
        shutil.copy2(src, bak)
    return bak


def full(shot, n, mid=False):
    """ganze Einstellung aus Bildern 1..n (30 fps) -> 60 fps"""
    d = pngs(shot, 1, n)
    backup(shot)
    tmp = SH / f"{shot}.tmp.mp4"
    if mid:
        dm = pngs(shot, 1, n - 1, mid=True)
        seq = ROOT / "out" / "kb_frames2" / f"{shot}_60"
        shutil.rmtree(seq, ignore_errors=True)
        seq.mkdir(parents=True)
        j = 1
        for k in range(1, n + 1):
            for src in ([d / f"{k:04d}.png"] + ([dm / f"{k:04d}.png"] if k < n else [d / f"{k:04d}.png"])):
                os.symlink(src, seq / f"{j:05d}.png")
                j += 1
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", "60", "-i", str(seq / "%05d.png")] + X264 + [str(tmp)], check=True)
    else:
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", "30", "-i", str(d / "%04d.png"), "-vf", MINT] + X264 + [str(tmp)],
                       check=True)
    tmp.replace(SH / f"{shot}.mp4")
    print(f"✅ {shot}: {nframes(SH / f'{shot}.mp4')} Bilder (60 fps)")


def splice(shot, a, b):
    """Bilder a..b (30 fps) ersetzen im alten 60-fps-Video die Zeit (a-1)/30 … b/30."""
    d = pngs(shot, a, b)
    old = backup(shot)
    n_old = nframes(old)
    i0, i1 = 2 * (a - 1), 2 * b          # 60-fps-Bildnummern (0-basiert): ersetzt wird [i0, i1)
    n_new = i1 - i0
    tmp = SH / f"{shot}.tmp.mp4"
    parts, labels = [], []
    fc = []
    if i0 > 0:
        fc.append(f"[0:v]select='lt(n\\,{i0})',setpts=N/60/TB[p0]")
        labels.append("[p0]")
    fc.append(f"[1:v]{MINT},tpad=stop_mode=clone:stop=4,trim=end_frame={n_new},setpts=N/60/TB[p1]")
    labels.append("[p1]")
    if i1 < n_old:
        fc.append(f"[0:v]select='gte(n\\,{i1})',setpts=N/60/TB[p2]")
        labels.append("[p2]")
    fc.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0,format=yuv420p[out]")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(old), "-framerate", "30", "-start_number", str(a), "-i", str(d / "%04d.png"),
                    "-filter_complex", ";".join(fc), "-map", "[out]", "-r", "60"] + X264 + [str(tmp)], check=True)
    n_out = nframes(tmp)
    if n_out != n_old:
        sys.exit(f"❌ {shot}: Länge passt nicht ({n_out} statt {n_old} Bilder)")
    tmp.replace(SH / f"{shot}.mp4")
    print(f"✅ {shot}: Bilder {a}–{b} eingesetzt ({n_out} Bilder)")


def frames_of(shot, tl):
    import json
    return {s["id"]: s for s in json.loads((ROOT / tl).read_text(encoding="utf-8"))["segments"]}[shot]["frames"]


if __name__ == "__main__":
    V1, NEW = "src/qissa_kaaba/timeline_v1.json", "src/qissa_kaaba/timeline.json"
    splice("tuer1", 1, 360)
    splice("abend1", 1, 360)
    splice("besuch2", 210, 340)
    full("ankunft", frames_of("ankunft", V1))
    full("abend2", frames_of("abend2", V1))
    full("bau", frames_of("bau", NEW))
    full("tuer2", frames_of("tuer2", NEW))
    full("segen", frames_of("segen", NEW), mid=True)
