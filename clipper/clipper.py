#!/usr/bin/env python3
"""
Viral-Clipper: Stream (Twitch-VOD oder Videodatei) -> KI findet virale Momente -> Hochformat-Clips 1080x1920.

  python3 clipper/clipper.py https://www.twitch.tv/videos/123456789
  python3 clipper/clipper.py https://www.twitch.tv/videos/123456789 --von 1:00:00 --bis 4:00:00 --anzahl 8
  python3 clipper/clipper.py public/upload/stream.mp4 --kontext "GTA 6 Story"

Ablauf:
  1. Ton des Streams in 10-min-Stuecken laden -> Whisper (Woerter mit Zeit) + Lautstaerke (Schreie/Lacher)
  2. Gemini liest das ganze Transkript und waehlt die besten Momente (+ Viral-Bewertung 0-100)
  3. Nur diese Stellen als Video laden (1080p), Facecam per Gemini-Bild-Erkennung finden
  4. ffmpeg schneidet jeden Clip in EINEM Durchgang aus dem Original (1080p60): Facecam oben / Spiel unten,
     harte Ansichtswechsel, Wort-fuer-Wort-Untertitel (Anton, Streamer weiss, andere gelb)
Ergebnis: out/clips/<id>/clip_01_viral-87.mp4 ... + bericht.md (Titel, Beschreibung, Hashtags, Bewertung)
Zwischenstaende werden gespeichert -> Abbruch/Neustart setzt fort.
"""
import argparse
import base64
import concurrent.futures as cf
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")  # Xet-Server ist in der Cloud gesperrt

ROOT = Path(__file__).resolve().parent.parent
SR = 16000
CHUNK = 600  # Sekunden pro Analyse-Stueck
TEXT_MODELS = ["gemini-3.5-flash", "gemini-flash-latest", "gemini-3.5-flash-lite", "gemini-flash-lite-latest"]
FONTS = Path(__file__).resolve().parent / "fonts"  # Anton (OFL) fuer die Untertitel


# ---------------------------------------------------------------- Hilfen
def hms(t):
    t = max(0, float(t))
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:04.1f}"


def parse_t(s):
    if s is None or s == "":
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).strip()
    parts = [float(p) for p in s.split(":")]
    v = 0.0
    for p in parts:
        v = v * 60 + p
    return v


def log(*a):
    print(*a, flush=True)


def ffmpeg(*args, inp=None):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args], input=inp, capture_output=True)
    if r.returncode:
        raise RuntimeError("ffmpeg: " + r.stderr.decode(errors="ignore")[-600:])
    return r.stdout


def decode_audio(data_or_path, ss=0.0, dur=None):
    a = []
    if ss:
        a += ["-ss", f"{ss:.3f}"]
    a += ["-i", "pipe:0" if isinstance(data_or_path, bytes) else str(data_or_path)]
    if dur:
        a += ["-t", f"{dur:.3f}"]
    raw = ffmpeg(*a, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-",
                 inp=data_or_path if isinstance(data_or_path, bytes) else None)
    return np.frombuffer(raw, np.float32)


# ---------------------------------------------------------------- Quellen
class TwitchSource:
    """Twitch-VOD: laedt nur die benoetigten 10-s-Stuecke (HLS) direkt herunter."""

    def __init__(self, url):
        import requests
        import yt_dlp

        self.http = requests.Session()
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as y:
            info = y.extract_info(url, download=False)
        self.id = "tw" + str(info["id"]).lstrip("v")
        self.title = info.get("title") or ""
        self.channel = info.get("uploader") or info.get("uploader_id") or ""
        self.duration = float(info.get("duration") or 0)
        fmts = [f for f in info["formats"] if "m3u8" in (f.get("protocol") or "")]
        aud = [f for f in fmts if f.get("vcodec") == "none"]
        vid = [f for f in fmts if f.get("height")]
        best = max(vid, key=lambda f: (f["height"] <= 1080, f["height"], f.get("fps") or 0))
        self.video_url = best["url"]
        self.audio_url = aud[0]["url"] if aud else min(vid, key=lambda f: f["height"])["url"]
        self._pl = {}

    def _playlist(self, url):
        if url not in self._pl:
            txt = self.http.get(url, timeout=30).text
            base = url.rsplit("/", 1)[0] + "/"
            segs, t, dur = [], 0.0, 0.0
            for line in txt.splitlines():
                if line.startswith("#EXTINF:"):
                    dur = float(line[8:].split(",")[0])
                elif line and not line.startswith("#"):
                    segs.append((t, dur, line))
                    t += dur
            self._pl[url] = (base, segs)
        return self._pl[url]

    def _get(self, url):
        for i in range(5):
            try:
                r = self.http.get(url, timeout=60)
                if r.status_code == 200:
                    return r.content
                if r.status_code in (403, 404):
                    return None
            except Exception:
                pass
            time.sleep(1 + 2 * i)
        return None

    def _seg(self, base, name):
        c = self._get(base + name)
        if c is None:  # Twitch benennt stummgeschaltete Stuecke um (-muted / -unmuted)
            stem = re.sub(r"-(un)?muted", "", name.rsplit(".", 1)[0])
            for alt in (stem + "-muted.ts", stem + "-unmuted.ts", stem + ".ts"):
                if alt != name and (c := self._get(base + alt)) is not None:
                    break
        return c or b""

    def fetch(self, url, t0, t1):
        base, segs = self._playlist(url)
        sel = [s for s in segs if s[0] + s[1] > t0 and s[0] < t1]
        if not sel:
            return b"", t0
        with cf.ThreadPoolExecutor(8) as ex:
            parts = list(ex.map(lambda s: self._seg(base, s[2]), sel))
        return b"".join(parts), sel[0][0]

    def audio(self, t0, t1):
        data, s0 = self.fetch(self.audio_url, t0, t1)
        if not data:
            return np.zeros(int((t1 - t0) * SR), np.float32)
        a = decode_audio(data)
        i = int((t0 - s0) * SR)
        return a[i:i + int((t1 - t0) * SR)]

    def raw(self, t0, t1, out):
        """Original-Stuecke (1080p60, unveraendert) als .ts speichern -> (Datei, Stream-Zeit am Dateianfang)."""
        meta = out.with_suffix(".start")
        if not out.exists() or not meta.exists():
            data, s0 = self.fetch(self.video_url, t0, t1)
            out.write_bytes(data)
            meta.write_text(str(s0))
        return out, float(meta.read_text())

    def frame(self, t, out):
        data, s0 = self.fetch(self.video_url, t, t + 0.5)
        ffmpeg("-ss", f"{t - s0:.2f}", "-i", "pipe:0", "-frames:v", "1", "-q:v", "3", str(out), inp=data)


class FileSource:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.id = "f_" + re.sub(r"[^a-zA-Z0-9]+", "_", self.path.stem)[:40]
        self.title, self.channel = self.path.stem, ""
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            str(self.path)], capture_output=True, text=True)
        self.duration = float(r.stdout.strip() or 0)

    def audio(self, t0, t1):
        return decode_audio(self.path, t0, t1 - t0)

    def raw(self, t0, t1, out):
        return self.path, 0.0

    def frame(self, t, out):
        ffmpeg("-ss", f"{t:.2f}", "-i", str(self.path), "-frames:v", "1", "-q:v", "3", str(out))


# ---------------------------------------------------------------- 1. Analyse (Whisper + Lautstaerke)
_whisper = None


def whisper():
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        name = os.environ.get("CLIPPER_WHISPER", "small.en")
        log(f"   Lade Whisper-Modell {name} …")
        _whisper = WhisperModel(name, device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)
    return _whisper


def analyse(src, t0, t1, work):
    cdir = work / "chunks"
    cdir.mkdir(parents=True, exist_ok=True)
    out, starts = [], list(np.arange(t0, t1, CHUNK))
    tstart = time.time()
    for k, c0 in enumerate(starts):
        c1 = min(c0 + CHUNK, t1)
        f = cdir / f"{int(c0)}.json"
        if not f.exists():
            a = src.audio(c0, c1)
            win = SR // 2
            n = len(a) // win
            db = (10 * np.log10(np.mean(a[:n * win].reshape(n, win) ** 2, axis=1) + 1e-10)).round(1).tolist() if n else []
            segs = []
            if len(a) > SR and np.abs(a).max() > 1e-4:
                res, _ = whisper().transcribe(a, language="en", word_timestamps=True, vad_filter=True,
                                              condition_on_previous_text=False)
                for s in res:
                    ws = [[w.word.strip(), round(c0 + w.start, 2), round(c0 + w.end, 2)] for w in (s.words or []) if w.word.strip()]
                    if ws:
                        segs.append({"s": ws[0][1], "e": ws[-1][2], "text": s.text.strip(), "words": ws})
            f.write_text(json.dumps({"t0": c0, "db": db, "segs": segs}))
            done = k + 1
            eta = (time.time() - tstart) / done * (len(starts) - done)
            log(f"   Analyse {hms(c1)} / {hms(t1)}  ({done}/{len(starts)}, noch ca. {int(eta // 60)} min)")
        out.append(json.loads(f.read_text()))
    return out


def loud_peaks(chunks):
    """Momente, die deutlich lauter sind als die Umgebung (Schreien, Lachen, Hype)."""
    db, t = [], []
    for c in chunks:
        db += c["db"]
        t += [c["t0"] + 0.5 * i for i in range(len(c["db"]))]
    if len(db) < 10:
        return []
    db = np.array(db)
    k = 120  # 60 s Umgebung
    pad = np.pad(db, (k // 2, k // 2), mode="edge")
    base = np.array([np.median(pad[i:i + k]) for i in range(0, len(db))])
    exc = db - base
    peaks, last = [], -99
    for i in np.argsort(-exc):
        if exc[i] < 9 or len(peaks) > 400:
            break
        if all(abs(t[i] - p[0]) > 4 for p in peaks):
            peaks.append((t[i], float(exc[i])))
    return sorted(peaks)


# ---------------------------------------------------------------- 2. Gemini
def gemini(parts, schema_hint=True, timeout=600):
    body = json.dumps({"contents": [{"parts": parts}],
                       "generationConfig": {"responseMimeType": "application/json", "temperature": 0.4}}).encode()
    key = os.environ.get("GEMINI_API_KEY") or "proxy"  # in der Cloud setzt der Proxy den Schluessel ein
    last = None
    tried_out = set()
    for model in [m for m in TEXT_MODELS for _ in (0, 1)]:  # jedes Modell 2 Versuche (503 = kurz überlastet)
        if model in tried_out:
            continue
        req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                     data=body, headers={"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.load(r)
            txt = "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"] if not p.get("thought"))
            txt = re.sub(r"^```(json)?|```$", "", txt.strip()).strip()
            return json.loads(txt)
        except urllib.error.HTTPError as e:
            last = f"{model}: HTTP {e.code} {e.read()[:300]!r}"
            if e.code == 429:  # Tageslimit -> gleich naechstes Modell
                tried_out.add(model)
        except Exception as e:  # noqa
            last = f"{model}: {e}"
        log(f"   ⚠️  {last[:160]} – neuer Versuch")
        time.sleep(5)
    raise RuntimeError("Gemini fehlgeschlagen: " + str(last))


SELECT_PROMPT = """You are the editor of a huge streamer-clips channel on TikTok / Instagram Reels / YouTube Shorts
(channels like kaicenatclips or streamer.clipss that regularly get millions of views).

Below is the timestamped transcript of a Twitch stream.
Streamer: {channel}
Stream title: {title}
Context: {kontext}
Lines marked with 🔊 contain a sudden loudness spike (screaming, laughing, hype, explosions, rage).
Lines "(🔊 … no speech)" are loud moments without words.

Find the BEST moments that would go viral as vertical short clips (at most {n}). Be very strict:
only pick a moment if a stranger who has never seen this streamer would stop scrolling, laugh, be shocked or
send it to a friend. Ordinary gameplay, normal conversation, mild reactions or "kind of funny" moments are NOT
enough. If the stream has fewer great moments, return fewer clips – quality over quantity. Rules:
- The LENGTH depends on the moment: as long as the story needs, as short as possible. A quick reaction can be 15–30 s,
  a typical moment 30–60 s, a longer story / chase / argument / build-up 1–3 min. Never cut off the payoff,
  never pad with boring parts. Each clip must be self-contained: setup -> payoff, understandable without the stream.
- Start right at the hook (at most ~1.5 s before the first interesting line), end right after the punchline / reaction
  has played out. No dead air, no boring intro.
- Good: funny fails, rage, shocked or hyped reactions, chaos, unexpected events, hilarious quotes, wins, clutch moments,
  beef/arguments, wholesome moments, crazy stories, reactions to something new or surprising, interactions with
  guests/other streamers/strangers. Works for any kind of stream (games, IRL, just chatting, reactions, events).
- Bad: reading chat / donations, sponsor reads, menus, loading, long silent gameplay, moments that need prior context.
- No overlapping clips. Sort by viral_score (best first).
- viral_score = honest 0–100 estimate of viral potential (90+ only for exceptional moments, typical 50–80).
  Strong signals: screaming/hype (🔊 clusters), everyone laughing, a clear punchline, a shocking event, conflict,
  a quotable line, a big win or an embarrassing fail.
- keywords: 2–8 punchline words that are actually SPOKEN in the clip (they pop bigger on screen).
- other_voice_lines: the timestamps (exactly as written in the transcript, e.g. "1:02:35.9") of every transcript line
  in the clip that is NOT spoken by the streamer (game characters / NPCs, friends on call, guests, TTS, videos).
  Their captions are shown in yellow, the streamer's in white.
- sfx_tags: short non-speech captions in this style: "*LAUGHING*", "*SCREAMS*", "*SHOCKED*", "*CAR CRASHES*",
  "*HANGS UP*", "*SILENCE*", only where clearly happening (use the 🔊 markers and context), 0–5 per clip.
  "who": "streamer" or "other".
- reaction_times: moments where the streamer's face/reaction is the important thing (facecam full screen), 1–5.
- skip: parts inside the clip that are boring and can be cut out without breaking the story (filler, waiting,
  reading chat), as {{"from","to"}}, 0–4.

Return ONLY JSON:
{{"clips":[{{"start":"H:MM:SS.s","end":"H:MM:SS.s","title":"short catchy title (English)",
"viral_score":87,"reason_de":"kurze Begründung auf Deutsch, warum das viral gehen kann",
"description":"English TikTok caption in the style 'Kai Cenat is Shocked After …😂😂' plus 4–6 hashtags",
"keywords":["…"],"other_voice_lines":["H:MM:SS.s"],
"sfx_tags":[{{"time":"H:MM:SS.s","text":"*LAUGHING*","who":"streamer"}}],"reaction_times":["H:MM:SS.s"],
"skip":[{{"from":"H:MM:SS.s","to":"H:MM:SS.s"}}]}}]}}

TRANSCRIPT:
{transcript}
"""


def build_transcript(chunks, peaks):
    lines, pi = [], 0
    segs = [s for c in chunks for s in c["segs"]]
    for s in segs:
        while pi < len(peaks) and peaks[pi][0] < s["s"] - 1:
            lines.append(f"[{hms(peaks[pi][0])}] (🔊 loud moment, no speech)")
            pi += 1
        mark = ""
        while pi < len(peaks) and peaks[pi][0] <= s["e"] + 1:
            mark = " 🔊"
            pi += 1
        lines.append(f"[{hms(s['s'])}]{mark} {s['text']}")
    for p in peaks[pi:]:
        lines.append(f"[{hms(p[0])}] (🔊 loud moment, no speech)")
    return "\n".join(lines)


def select_clips(src, chunks, peaks, n, kontext, work):
    f = work / "auswahl.json"
    if f.exists():
        return json.loads(f.read_text())["clips"]
    tr = build_transcript(chunks, peaks)
    (work / "transkript.txt").write_text(tr)
    log(f"🤖 Gemini sucht die {n} besten Momente ({len(tr) // 4000}k Token Transkript) …")
    res = gemini([{"text": SELECT_PROMPT.format(channel=src.channel or "?", title=src.title, kontext=kontext,
                                                n=n, transcript=tr)}])
    clips = []
    for c in res.get("clips", []):
        s, e = parse_t(c.get("start")), parse_t(c.get("end"))
        if s is None or e is None or e - s < 8:
            continue
        c["start"], c["end"] = s, min(e, s + 240)
        c["sfx_tags"] = [{"time": parse_t(x.get("time")), "text": x.get("text", ""), "who": x.get("who", "streamer")}
                         for x in c.get("sfx_tags") or [] if parse_t(x.get("time")) is not None]
        for k in ("reaction_times", "other_voice_lines"):
            c[k] = [parse_t(x) for x in c.get(k) or [] if parse_t(x) is not None]
        c["skip"] = [(parse_t(x.get("from")), parse_t(x.get("to"))) for x in c.get("skip") or []
                     if parse_t(x.get("from")) is not None and parse_t(x.get("to")) is not None]
        clips.append(c)
    clips.sort(key=lambda c: -int(c.get("viral_score") or 0))
    f.write_text(json.dumps({"clips": clips}, indent=1, ensure_ascii=False))
    return clips


LAYOUT_PROMPT = """Each image is one frame of a livestream (one frame per clip, in order).
For EACH image find the streamer's webcam / facecam: the region showing the real person filmed by a camera
(usually a rectangular overlay in a corner on top of gameplay). Ignore game characters, avatars, emotes and chat.
If the whole frame is the camera (IRL / just chatting, no gameplay), set "fullscreen_camera": true and give the
box of the main person's head and shoulders as "person".
Return ONLY JSON: {"frames":[{"facecam":[ymin,xmin,ymax,xmax] or null,"fullscreen_camera":false,"person":null}]}
with coordinates normalized to 0–1000. The facecam box must tightly cover the whole camera overlay (not just the face)."""


def detect_layouts(src, clips, work):
    f = work / "layout.json"
    if f.exists():
        return json.loads(f.read_text())
    imgs, parts = [], [{"text": LAYOUT_PROMPT}]
    for i, c in enumerate(clips):
        p = work / f"frame_{i + 1:02d}.jpg"
        if not p.exists():
            src.frame(c["start"] + min(5, (c["end"] - c["start"]) / 2), p)
        imgs.append(p)
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(p.read_bytes()).decode()}})
    log("🔎 Gemini sucht die Facecam …")
    try:
        frames = gemini(parts).get("frames", [])
    except Exception as e:  # noqa
        log(f"   ⚠️  Facecam-Erkennung fehlgeschlagen ({e}) – nutze nur Gesichtserkennung")
        frames = []
    out = []
    for i, p in enumerate(imgs):
        fr = frames[i] if i < len(frames) else {}
        out.append(refine_layout(fr, p))
    f.write_text(json.dumps(out, indent=1))
    return out


def norm_box(b):
    if not b or len(b) != 4:
        return None
    y0, x0, y1, x1 = [max(0.0, min(1.0, float(v) / 1000)) for v in b]
    if x1 - x0 < 0.04 or y1 - y0 < 0.04:
        return None
    return {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}


def faces(img):
    import cv2
    if not hasattr(cv2, "CascadeClassifier"):  # OpenCV 5 hat keine Haar-Kaskaden mehr -> "opencv-python-headless<5"
        return []
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    H, W = g.shape
    return [(x / W, y / H, w / W, h / H) for x, y, w, h in cas.detectMultiScale(g, 1.1, 6, minSize=(24, 24))]


def snap(img, box):
    """Kanten der Facecam an die echten Rahmenlinien im Bild anlegen (Gemini-Boxen sind leicht ungenau)."""
    import cv2
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    H, W = g.shape
    e = cv2.Canny(g, 60, 160) > 0
    x0, y0, x1, y1 = box["x"] * W, box["y"] * H, (box["x"] + box["w"]) * W, (box["y"] + box["h"]) * H
    r = int(0.03 * W)

    def best(vals, line, cur):
        lo, hi = int(max(0, cur - r)), int(min(len(vals) - 1, cur + r))
        cand = [(line(v), v) for v in range(lo, hi + 1)]
        s, v = max(cand) if cand else (0, cur)
        return v if s > 0.55 else cur

    ya, yb, xa, xb = int(y0 + 0.15 * (y1 - y0)), int(y1 - 0.15 * (y1 - y0)), int(x0 + 0.15 * (x1 - x0)), int(x1 - 0.15 * (x1 - x0))
    col = lambda x: e[ya:yb, x].mean() if yb > ya else 0  # noqa
    row = lambda y: e[y, xa:xb].mean() if xb > xa else 0  # noqa
    nx0, nx1 = best(range(W), col, x0), best(range(W), col, x1)
    ny0, ny1 = best(range(H), row, y0), best(range(H), row, y1)
    if nx1 - nx0 < 0.5 * (x1 - x0) or ny1 - ny0 < 0.5 * (y1 - y0):
        return box
    m = 0.006  # Rahmenlinie selbst wegschneiden
    return {"x": nx0 / W + m, "y": ny0 / H + m, "w": (nx1 - nx0) / W - 2 * m, "h": (ny1 - ny0) / H - 2 * m}


def refine_layout(fr, path):
    import cv2
    img = cv2.imread(str(path))
    cam = norm_box(fr.get("facecam"))
    fs = bool(fr.get("fullscreen_camera"))
    fc = faces(img)
    if fs:
        person = norm_box(fr.get("person"))
        cx = person["x"] + person["w"] / 2 if person else (max(fc, key=lambda f: f[2])[0] + max(fc, key=lambda f: f[2])[2] / 2 if fc else 0.5)
        return {"mode": "full", "focusX": cx}
    if cam:
        cam = snap(img, cam)
        if cam["w"] * cam["h"] > 0.6:  # "Facecam" ist fast das ganze Bild -> wie Vollbild-Kamera behandeln
            return {"mode": "full", "focusX": cam["x"] + cam["w"] / 2}
        return {"mode": "split", "cam": cam}
    if fc:  # Notfall: groesstes Gesicht -> Box drumherum
        x, y, w, h = max(fc, key=lambda f: f[2])
        if w > 0.12:
            return {"mode": "full", "focusX": x + w / 2}
        bw, bh = min(0.4, w * 3.2), min(0.45, h * 3.2)
        return {"mode": "split", "cam": {"x": max(0, x + w / 2 - bw / 2), "y": max(0, y + h / 2 - bh / 2), "w": bw, "h": bh}}
    return {"mode": "game"}


# ---------------------------------------------------------------- 3. Clip bauen
WORD_RE = re.compile(r"[^\w'?!%$#&-]+", re.UNICODE)


def clean(w):
    return WORD_RE.sub("", w).strip("-").upper()


def keep_segments(words, peaks, s, e, skip=()):
    """Pausen ohne Sprache und ohne Laerm raus (Jump-Cuts), dazu die von Gemini markierten langweiligen Teile."""
    cuts = [(max(s, a), min(e, b)) for a, b in skip if b - a > 0.5 and a < e and b > s]
    times = [(w[1], w[2]) for w in words]
    for (a0, a1), (b0, b1) in zip(times, times[1:]):
        if b0 - a1 > 0.9 and not any(a1 - 0.3 < p[0] < b0 + 0.3 for p in peaks):
            cuts.append((a1 + 0.2, b0 - 0.12))
    cuts.sort()
    segs, cur = [], s
    for a, b in cuts:
        if a > cur:
            segs.append((cur, a))
        cur = max(cur, b)
    segs.append((cur, e))
    return [(a, b) for a, b in segs if b - a > 0.3]


def plan_shots(dur, base, react, cam_full_ok):
    """Ansichten im fertigen Clip – nur harte Schnitte, keine Zooms, Spielbild nie abgeschnitten.
    split = Facecam ueber dem kompletten Spielbild, cam = Facecam im Vollbild (nur wenn die Cam gross/scharf genug ist)."""
    special = []
    if base == "split" and cam_full_ok:
        special = sorted((max(0, t - 0.3), min(dur, t + 2.2), "cam") for t in react)
    shots, t = [], 0.0
    for a, b, v in special:
        a = max(a, t)
        if b - a < 1.2:
            continue
        if a > t:
            shots.append({"from": t, "to": a, "view": base})
        shots.append({"from": a, "to": b, "view": v})
        t = b
    if dur - t > 0.01:
        shots.append({"from": t, "to": dur, "view": base})
    # gleiche Ansichten zusammenfassen, Mini-Einstellungen (< 1 s) an die vorige haengen
    res = []
    for x in shots:
        if res and (x["view"] == res[-1]["view"] or x["to"] - x["from"] < 1.0):
            res[-1]["to"] = x["to"]
        else:
            res.append(dict(x))
    return res or [{"from": 0, "to": dur, "view": base}]


def build_edit(clip, lay, chunks, peaks, cam_full_ok):
    s, e = clip["start"], clip["end"]
    other = clip.get("other_voice_lines") or []
    words = []  # [wort, start, ende, wer]
    for c in chunks:
        for sg in c["segs"]:
            who = "o" if any(abs(sg["s"] - t) < 0.2 for t in other) else "s"
            words += [[w[0], w[1], w[2], who] for w in sg["words"] if s - 0.05 <= w[1] < e]
    segs = keep_segments(words, peaks, s, e, clip.get("skip") or [])

    def out_t(t):  # Zeit im Stream -> Zeit im fertigen Clip
        acc = 0.0
        for a, b in segs:
            if t < a:
                return acc
            if t <= b:
                return acc + t - a
            acc += b - a
        return acc

    dur = sum(b - a for a, b in segs)
    kw = {clean(k) for x in clip.get("keywords") or [] for k in str(x).split()}
    kw.discard("")
    caps, i = [], 0
    ws = [(clean(w[0]), w[1], w[2], w[3]) for w in words if clean(w[0])]
    while i < len(ws):
        txt, a, b, who = ws[i]
        big = txt in kw
        # sehr kurze Woerter mit dem naechsten zusammen zeigen (z. B. "RIGHT NOW")
        if (i + 1 < len(ws) and ws[i + 1][3] == who and (b - a < 0.22 or len(txt) <= 2)
                and len(txt) + len(ws[i + 1][0]) <= 11 and ws[i + 1][1] - b < 0.15):
            txt, b, big = txt + " " + ws[i + 1][0], ws[i + 1][2], big or ws[i + 1][0] in kw
            i += 1
        nxt = ws[i + 1][1] if i + 1 < len(ws) else b + 0.6
        caps.append({"from": out_t(a), "to": out_t(min(nxt, b + 0.8)), "text": txt, "who": who, "big": big})
        i += 1
    for k in range(len(caps) - 1):
        caps[k]["to"] = min(caps[k]["to"], caps[k + 1]["from"])
    for tg in clip.get("sfx_tags") or []:
        if s <= tg["time"] < e and tg["text"]:
            t0 = out_t(tg["time"])
            if not any(c["from"] < t0 + 1.0 and c["to"] > t0 for c in caps):
                caps.append({"from": t0, "to": min(dur, t0 + 1.3), "text": tg["text"].upper(),
                             "who": "o" if tg.get("who") == "other" else "s", "big": False})
    inside = lambda ts: [out_t(t) for t in ts if s <= t < e]  # noqa
    shots = plan_shots(dur, lay["mode"], inside(clip.get("reaction_times") or []), cam_full_ok)
    return {"segs": segs, "dur": dur, "caps": sorted(caps, key=lambda c: c["from"]), "shots": shots}


def ev(n):
    return int(round(n / 2)) * 2


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    w, h, fr = r.stdout.strip().splitlines()[0].split(",")[:3]
    n, d = fr.split("/")
    return int(w), int(h), round(float(n) / float(d))


def geometry(lay, W, H):
    """Ausschnitte in Quell-Pixeln + Feldhoehen im 1080x1920-Bild."""
    g = {"W": W, "H": H}
    if lay["mode"] == "split":
        c = lay["cam"]
        cx, cy, cw, ch = c["x"] * W, c["y"] * H, c["w"] * W, c["h"] * H
        CH = min(860, max(480, 1080 * ch / cw))  # Facecam in ihrem eigenen Seitenverhaeltnis (kein Abschneiden)
        A = 1080 / CH
        if cw / ch > A:
            nw = ch * A
            cx, cw = cx + (cw - nw) / 2, nw
        else:
            nh = cw / A
            cy, ch = cy + (ch - nh) / 2, nh
        g["CH"] = ev(CH)
        g["cam"] = (ev(cw), ev(ch), ev(cx), ev(cy))
        g["camPx"] = ch
        # Facecam-Vollbild: 9:16-Ausschnitt aus der Cam
        fw = min(c["w"] * W, c["h"] * H * 9 / 16)
        g["camfull"] = (ev(fw), ev(fw * 16 / 9), ev((c["x"] + c["w"] / 2) * W - fw / 2), ev(c["y"] * H))
    fw = min(W, ev(H * 9 / 16))
    fx = (lay.get("focusX", 0.5) if lay["mode"] == "full" else 0.5) * W - fw / 2
    g["full"] = (fw, H, ev(min(W - fw, max(0, fx))), 0)
    # ganzes Spielbild in voller Breite, mittig; Facecam direkt darueber
    g["GH"] = ev(1080 * H / W)
    top = ev((1920 - g.get("CH", 0) - g["GH"]) / 2)
    g["camY"] = top
    g["gameY"] = top + g.get("CH", 0)
    return g


def ass_time(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def write_ass(edit, g, path):
    """Untertitel wie im Vorbild: 1 Wort pro Bild, Anton, dicker schwarzer Rand, Streamer weiss / andere gelb."""
    L = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "ScaledBorderAndShadow: yes",
         "WrapStyle: 2", "", "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
         "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
         "MarginR, MarginV, Encoding",
         "Style: Cap,Anton,270,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,13,6,5,40,40,0,1",
         "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    CH = g.get("CH", 0)
    for c in edit["caps"]:
        if c["to"] - c["from"] < 0.04:
            continue
        view = next((sh["view"] for sh in edit["shots"] if sh["from"] <= c["from"] < sh["to"]), edit["shots"][-1]["view"])
        if view in ("split", "game"):
            below = 1920 - (g["gameY"] + g["GH"])
            y = g["gameY"] + g["GH"] + below * 0.45 if below > 260 else g["gameY"] + g["GH"] - 150
        else:
            y = 1920 * 0.79
        # libass-Groesse = Zeilenhoehe; Anton: Grossbuchstabe ~0.48 x Groesse hoch, ~0.3 x Groesse breit
        fs = min(295 if c["big"] else 270, 960 / max(1, len(c["text"]) * 0.3))
        col = r"\c&H1AE8FF&" if c["who"] == "o" else ""
        txt = c["text"].replace("\\", "").replace("{", "(").replace("}", ")")
        L.append(f"Dialogue: 0,{ass_time(c['from'])},{ass_time(c['to'])},Cap,,0,0,0,,"
                 rf"{{\pos(540,{y:.0f})\fs{fs:.0f}\fscx82\fscy82\t(0,80,\fscx100\fscy100){col}}}{txt}")
    path.write_text("\n".join(L) + "\n")


def render(raw, s0, edit, lay, out, work, name):
    """Ein einziger ffmpeg-Durchgang aus dem Original: Schnitte + Ansichten + Untertitel + Lautheit."""
    W, H, fps = probe(raw)
    fps = min(60, max(30, fps))
    g = geometry(lay, W, H)
    # Stuecke = Jump-Cut-Segmente geschnitten mit den Ansichtswechseln
    pieces, acc = [], 0.0
    for a, b in edit["segs"]:
        o0, o1 = acc, acc + (b - a)
        cuts = sorted({o0, o1, *[x for sh in edit["shots"] for x in (sh["from"], sh["to"]) if o0 < x < o1]})
        for x, y in zip(cuts, cuts[1:]):
            if y - x < 0.03:
                continue
            view = next((sh["view"] for sh in edit["shots"] if sh["from"] <= (x + y) / 2 < sh["to"]), edit["shots"][-1]["view"])
            pieces.append((a + (x - o0), y - x, view))
        acc = o1
    inputs, F = [], []
    for i, (ss, d, view) in enumerate(pieces):
        inputs += ["-ss", f"{max(0, ss - s0):.3f}", "-t", f"{d:.3f}", "-i", str(raw)]
        pre = f"[{i}:v]fps={fps},setpts=PTS-STARTPTS"
        bg = (f"scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=12:2,"
              f"scale=1080:1920:flags=bicubic,eq=brightness=-0.18:saturation=1.1")
        if view in ("split", "game"):
            parts = 3 if view == "split" else 2
            outs = "".join(f"[{k}{i}]" for k in "bgc"[:parts])
            F.append(f"{pre},split={parts}{outs}")
            F.append(f"[b{i}]{bg}[bo{i}]")
            F.append(f"[g{i}]scale=1080:{g['GH']}:flags=lanczos[go{i}]")
            if view == "split":
                cw, ch, cx, cy = g["cam"]
                F.append(f"[c{i}]crop={cw}:{ch}:{cx}:{cy},scale=1080:{g['CH']}:flags=lanczos,unsharp=5:5:0.45:5:5:0[co{i}]")
                F.append(f"[bo{i}][co{i}]overlay=0:{g['camY']}[t{i}]")
                F.append(f"[t{i}][go{i}]overlay=0:{g['gameY']},setsar=1,format=yuv420p[v{i}]")
            else:
                F.append(f"[bo{i}][go{i}]overlay=0:{g['gameY']},setsar=1,format=yuv420p[v{i}]")
        else:
            cw, ch, cx, cy = g["camfull"] if view == "cam" else g["full"]
            F.append(f"{pre},crop={cw}:{ch}:{cx}:{cy},scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p[v{i}]")
        F.append(f"[{i}:a]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
                 f"afade=t=in:d=0.012,afade=t=out:st={max(0, d - 0.015):.3f}:d=0.015[a{i}]")
    ass = work / f"{name}.ass"
    write_ass(edit, g, ass)
    F.append("".join(f"[v{i}][a{i}]" for i in range(len(pieces))) + f"concat=n={len(pieces)}:v=1:a=1[vc][ac]")
    F.append(f"[vc]subtitles=filename='{ass}':fontsdir='{FONTS}'[vo]")
    F.append("[ac]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[ao]")
    fc = work / f"{name}.filter"
    fc.write_text(";\n".join(F))
    rate = max(3.0, min(14.0, 52 * 8 / max(1.0, edit["dur"])))  # Datei <= ~55 MB (App-Grenze)
    ffmpeg(*inputs, "-filter_complex_script", str(fc), "-map", "[vo]", "-map", "[ao]", "-r", str(fps),
           "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-maxrate", f"{rate:.1f}M", "-bufsize", f"{2 * rate:.1f}M",
           "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
           str(out))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "clip"


def main():
    ap = argparse.ArgumentParser(description="Viral-Clipper für Streams")
    ap.add_argument("quelle", help="Twitch-VOD-Link oder Videodatei")
    ap.add_argument("--von", help="Start im Stream, z. B. 1:30:00")
    ap.add_argument("--bis", help="Ende im Stream, z. B. 4:00:00")
    ap.add_argument("--anzahl", type=int, default=8, help="Wie viele Clips (Standard 8)")
    ap.add_argument("--kontext", default="unknown – figure out the game / topic from the stream title and transcript",
                    help="Optional: worum geht es im Stream, z. B. 'GTA 6 Story' (hilft der KI)")
    ap.add_argument("--nur-analyse", action="store_true", help="Nur Auswahl + Bericht, nicht rendern")
    ap.add_argument("--clips", help="Nur diese Clip-Nummern rendern, z. B. 1,3")
    a = ap.parse_args()

    q = a.quelle
    src = TwitchSource(q) if q.startswith("http") else FileSource(q)
    t0 = parse_t(a.von) or 0.0
    t1 = min(parse_t(a.bis) or src.duration, src.duration)
    work = ROOT / "out" / "clips" / src.id
    work.mkdir(parents=True, exist_ok=True)
    log(f"🎬 {src.channel} – {src.title}\n   Bereich {hms(t0)} – {hms(t1)} ({(t1 - t0) / 3600:.1f} h)")

    log("🎧 1/4 Ton laden + Spracherkennung …")
    chunks = analyse(src, t0, t1, work)
    peaks = loud_peaks(chunks)
    clips = select_clips(src, chunks, peaks, a.anzahl, a.kontext, work)
    if not clips:
        sys.exit("❌ Gemini hat keine Clips gefunden.")
    log(f"✅ {len(clips)} Momente gefunden:")
    for i, c in enumerate(clips, 1):
        log(f"   {i:2d}. [{c.get('viral_score', '?'):>3}] {hms(c['start'])}  {c.get('title', '')}")

    lays = detect_layouts(src, clips, work)
    write_report(src, clips, work)
    if a.nur_analyse:
        return
    want = {int(x) for x in a.clips.split(",")} if a.clips else None
    for i, (c, lay) in enumerate(zip(clips, lays), 1):
        if want and i not in want:
            continue
        name = f"clip_{i:02d}_viral-{int(c.get('viral_score') or 0)}_{slug(c.get('title', ''))}"
        out = work / f"{name}.mp4"
        c["file"] = out.name
        if out.exists():
            continue
        log(f"🎞️  {i}/{len(clips)} {c.get('title', '')} ({c['end'] - c['start']:.0f} s Rohmaterial)")
        raw, s0 = src.raw(c["start"] - 0.5, c["end"] + 0.5, work / f"raw_{i:02d}.ts")
        W, H, _ = probe(raw)
        cam_ok = lay["mode"] == "split" and geometry(lay, W, H)["camPx"] >= 560
        edit = build_edit(c, lay, chunks, peaks, cam_ok)
        (work / f"{name}.edit.json").write_text(json.dumps(edit))
        t = time.time()
        render(raw, s0, edit, lay, out, work, name)
        log(f"   ✅ {out.relative_to(ROOT)}  ({edit['dur']:.0f} s, {out.stat().st_size / 1e6:.0f} MB, "
            f"{time.time() - t:.0f} s Renderzeit)")
    write_report(src, clips, work)
    log(f"\n📄 Bericht: {(work / 'bericht.md').relative_to(ROOT)}")


def write_report(src, clips, work):
    L = [f"# Clips: {src.channel} – {src.title}", ""]
    for i, c in enumerate(clips, 1):
        L += [f"## {i}. {c.get('title', '')} — Viral-Score {c.get('viral_score', '?')}/100",
              f"- Stelle im Stream: {hms(c['start'])} – {hms(c['end'])} ({c['end'] - c['start']:.0f} s)",
              f"- Datei: `{c.get('file', '(noch nicht gerendert)')}`",
              f"- Warum: {c.get('reason_de', '')}", "", "Beschreibung zum Kopieren:", "```",
              c.get("description", ""), "```", ""]
    (work / "bericht.md").write_text("\n".join(L))


if __name__ == "__main__":
    main()
