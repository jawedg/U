#!/usr/bin/env python3
"""
Live-Clipper: nimmt einen laufenden Twitch-Stream auf und macht alle ~30 min neue virale Clips daraus.

  python3 clipper/live.py ishowspeed
  python3 clipper/live.py ishowspeed --runde 30 --anzahl 3

- Rekorder (eigener Thread): laedt die 2-s-Stuecke des Live-Streams (1080p60) laufend herunter, Werbung wird uebersprungen.
- Pro Runde: neues Stueck analysieren (Whisper + Lautstaerke) -> Gemini waehlt Highlights -> ffmpeg rendert die Clips.
- Facecam-Position wird zwischen den Runden wiederverwendet (spart Gemini-Anfragen; Tageslimit!).
- Endet automatisch, wenn der Stream vorbei ist (letzte Runde wird noch fertig gemacht).
Benoetigt die Netzwerk-Freigabe *.ttvnw.net (Live-Server von Twitch).
Ergebnis: out/clips/live_<kanal>_<datum>/rNN_NN_viral-XX_….mp4 + bericht.md
"""
import argparse
import json
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clipper as C  # noqa: E402


def live_info(channel):
    import yt_dlp
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as y:
        info = y.extract_info(f"https://www.twitch.tv/{channel}", download=False)
    fmts = [f for f in info["formats"] if f.get("height")]
    best = max(fmts, key=lambda f: (f["height"] <= 1080, f["height"], f.get("fps") or 0))
    return best["url"], info.get("description") or info.get("title") or channel, info.get("uploader") or channel


class Recorder(threading.Thread):
    """Haelt den Live-Stream fest: jedes neue Stueck -> seg/<nr>.ts + Zeile in index.jsonl (Zeit, Dauer, Datei)."""

    def __init__(self, channel, work):
        super().__init__(daemon=True)
        self.channel, self.work = channel, work
        self.seg = work / "seg"
        self.seg.mkdir(parents=True, exist_ok=True)
        self.index = work / "index.jsonl"
        self.http = requests.Session()
        self.lock = threading.Lock()
        self.segs = [json.loads(x) for x in self.index.read_text().splitlines()] if self.index.exists() else []
        self.t = self.segs[-1]["t"] + self.segs[-1]["d"] if self.segs else 0.0
        self.last_seq = max((s["seq"] for s in self.segs), default=-1)
        self.ended = False
        self.ads = 0

    def run(self):
        url, fails = None, 0
        while not self.ended:
            try:
                if url is None:
                    url = live_info(self.channel)[0]
                r = self.http.get(url, timeout=15)
                if r.status_code != 200:
                    raise RuntimeError(f"HTTP {r.status_code}")
                self._take(r.text, url.rsplit("/", 1)[0] + "/")
                fails = 0
            except Exception as e:  # noqa
                fails += 1
                url = None
                if fails >= 6:  # ~1 min nichts mehr -> Stream vorbei?
                    try:
                        live_info(self.channel)
                        fails = 3
                    except Exception:
                        C.log(f"📴 Stream ist vorbei ({e}).")
                        self.ended = True
                        break
                time.sleep(5)
                continue
            time.sleep(1.5)

    def _take(self, txt, base):
        seq, title, dur = None, "", 0.0
        for line in txt.splitlines():
            if line.startswith("#EXT-X-MEDIA-SEQUENCE:"):
                seq = int(line.split(":")[1])
            elif line.startswith("#EXTINF:"):
                dur_s, _, title = line[8:].partition(",")
                dur = float(dur_s)
            elif line and not line.startswith("#"):
                if seq is None:
                    continue
                if seq > self.last_seq:
                    self.last_seq = seq
                    if title.strip() != "live":  # eingeblendete Werbung
                        self.ads += 1
                    else:
                        data = None
                        for _ in range(3):
                            try:
                                rr = self.http.get(line if line.startswith("http") else base + line, timeout=20)
                                if rr.status_code == 200:
                                    data = rr.content
                                    break
                            except Exception:  # noqa
                                time.sleep(1)
                        if data:
                            name = f"{seq}.ts"
                            (self.seg / name).write_bytes(data)
                            e = {"seq": seq, "t": round(self.t, 3), "d": dur, "f": name}
                            with self.lock:
                                self.segs.append(e)
                                self.t += dur
                            with self.index.open("a") as fh:
                                fh.write(json.dumps(e) + "\n")
                seq += 1


class LiveSource:
    """Wie TwitchSource, liest aber die aufgenommenen Stuecke von der Platte."""

    def __init__(self, rec, title, channel, sid):
        self.rec, self.title, self.channel, self.id = rec, title, channel, sid

    @property
    def duration(self):
        return self.rec.t

    def fetch(self, t0, t1):
        with self.rec.lock:
            sel = [s for s in self.rec.segs if s["t"] + s["d"] > t0 and s["t"] < t1]
        parts = []
        for s in sel:
            p = self.rec.seg / s["f"]
            parts.append(p.read_bytes() if p.exists() else b"")
        return b"".join(parts), (sel[0]["t"] if sel else t0)

    def audio(self, t0, t1):
        data, s0 = self.fetch(t0, t1)
        if not data:
            return C.np.zeros(int((t1 - t0) * C.SR), C.np.float32)
        a = C.decode_audio(data)
        i = int((t0 - s0) * C.SR)
        return a[i:i + int((t1 - t0) * C.SR)]

    def raw(self, t0, t1, out):
        data, s0 = self.fetch(t0, t1)
        out.write_bytes(data)
        return out, s0

    def frame(self, t, out):
        data, s0 = self.fetch(t, t + 2.5)
        C.ffmpeg("-ss", f"{max(0, t - s0):.2f}", "-i", "pipe:0", "-frames:v", "1", "-q:v", "3", str(out), inp=data)

    def cleanup(self, before):
        """Stuecke, die fertig verarbeitet sind, loeschen (1080p60 = ~4 GB pro Stunde)."""
        with self.rec.lock:
            old = [s for s in self.rec.segs if s["t"] + s["d"] < before]
        for s in old:
            (self.rec.seg / s["f"]).unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser(description="Live-Clipper für Twitch")
    ap.add_argument("kanal", help="Twitch-Kanal, z. B. ishowspeed (oder Kanal-Link)")
    ap.add_argument("--runde", type=float, default=30, help="Minuten pro Runde (Standard 30)")
    ap.add_argument("--anzahl", type=int, default=3, help="max. Clips pro Runde (Standard 3)")
    ap.add_argument("--kontext", default="", help="Optional: worum geht es im Stream")
    ap.add_argument("--ordner", help="vorhandenen Live-Ordner fortsetzen")
    a = ap.parse_args()
    channel = re.sub(r"^https?://(www\.|m\.)?twitch\.tv/", "", a.kanal).split("?")[0].split("/")[0].lower()

    _, title, uploader = live_info(channel)
    sid = Path(a.ordner).name if a.ordner else f"live_{channel}_{datetime.now(timezone.utc):%Y%m%d-%H%M}"
    work = C.ROOT / "out" / "clips" / sid
    work.mkdir(parents=True, exist_ok=True)
    rec = Recorder(channel, work)
    rec.start()
    src = LiveSource(rec, title, uploader, sid)
    kontext = a.kontext or f"Live stream: {title}"
    C.log(f"🔴 Nehme {uploader} live auf: {title}\n   Ordner: {work.relative_to(C.ROOT)} – Runde alle {a.runde:.0f} min")

    state_f = work / "live_state.json"
    st = json.loads(state_f.read_text()) if state_f.exists() else {"done": 0.0, "round": 1, "clips": [], "layout": None}
    step = a.runde * 60
    last_log = 0
    while True:
        target = st["done"] + step
        if rec.t < target and not rec.ended:
            if time.time() - last_log > 300:
                C.log(f"   ⏺  aufgenommen: {C.hms(rec.t)} (Werbung übersprungen: {rec.ads} Stücke) – "
                      f"nächste Runde bei {C.hms(target)}")
                last_log = time.time()
            time.sleep(10)
            continue
        t1 = rec.t if rec.ended else (rec.t // C.CHUNK) * C.CHUNK
        if t1 - st["done"] < 90:
            if rec.ended:
                break
            time.sleep(10)
            continue
        r = st["round"]
        try:
            C.log(f"\n🎬 Runde {r}: {C.hms(st['done'])} – {C.hms(t1)}")
            chunks = C.analyse(src, st["done"], t1, work)
            peaks = C.loud_peaks(chunks)
            clips = [c for c in C.select_clips(src, chunks, peaks, a.anzahl, kontext, work, tag=f"_r{r:02d}")
                     if c["start"] >= st["done"] and c["end"] <= t1 + 1]
            for c in clips:
                c["end"] = min(c["end"], t1)
            if clips:
                for i, c in enumerate(clips, 1):
                    C.log(f"   {i}. [{c.get('viral_score', '?'):>3}] {C.hms(c['start'])}  {c.get('title', '')}")
                lays = C.detect_layouts(src, clips, work, tag=f"_r{r:02d}", reuse=st["layout"])
                st["layout"] = next((l for l in lays if l.get("mode") == "split"), st["layout"])
                C.render_clips(src, clips, lays, chunks, peaks, work, prefix=f"r{r:02d}")
                st["clips"] += clips
                C.write_report(src, sorted(st["clips"], key=lambda c: -int(c.get("viral_score") or 0)), work)
            else:
                C.log("   (keine starken Momente in dieser Runde)")
        except Exception as e:  # z. B. Gemini ueberlastet -> spaeter nochmal, Aufnahme laeuft weiter
            C.log(f"   ⚠️  Runde {r} fehlgeschlagen ({str(e)[:150]}) – neuer Versuch in 3 min")
            time.sleep(180)
            continue
        src.cleanup(t1 - 30)
        st["done"], st["round"] = t1, r + 1
        state_f.write_text(json.dumps(st, ensure_ascii=False))
        if rec.ended and st["done"] >= rec.t - 1:
            break
    C.log(f"\n✅ Fertig. Bericht: {(work / 'bericht.md').relative_to(C.ROOT)}")


if __name__ == "__main__":
    main()
