#!/usr/bin/env python3
"""Bildschirm- und Schilder-Texturen für das Flug-Video (Blender: blender/qissa/flug_world.py) -> blender/qissa/tex/flug_*.png
Handy mit Gebetszeit-Hinweis „Isha“, Video-Feed, Flugkarte im Sitz, Anschnallzeichen, Notausgang, Abflugtafel, Gebetsraum-Schild."""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "blender" / "qissa" / "tex"
OUT.mkdir(parents=True, exist_ok=True)
INTER = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
INTER_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
INTER_R = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
AMIRI = None   # arabische Schrift: woff2 kann PIL nicht – DejaVu hat arabische Zeichen
DEJAVU_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(p, s):
    try:
        return ImageFont.truetype(p, s)
    except OSError:
        return ImageFont.truetype(DEJAVU_B, s)


def rr(d, box, r, fill, outline=None, width=1):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def blob_bg(w, h, seed, cols):
    rnd = random.Random(seed)
    im = Image.new("RGB", (w, h), cols[0])
    d = ImageDraw.Draw(im)
    for _ in range(14):
        c = rnd.choice(cols)
        x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(w * 0.15, w * 0.5)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    return im.filter(ImageFilter.GaussianBlur(w * 0.08))


def feed(name, seed, cols, user, caption):
    """Kurzvideo-Feed (Hochformat-Handy 9:19.5): unscharfes buntes Video, rechts Symbole, unten Name + Text."""
    w, h = 720, 1560
    im = blob_bg(w, h, seed, cols)
    d = ImageDraw.Draw(im, "RGBA")
    # Person im Video (nur Umriss, ohne Gesicht) – lacht in die Kamera: Kopf + Schultern
    d.ellipse((w * 0.32, h * 0.3, w * 0.68, h * 0.48), fill=(250, 214, 170, 255))
    d.rounded_rectangle((w * 0.2, h * 0.47, w * 0.8, h * 0.75), 120, fill=(60, 70, 160, 255))
    d.rectangle((0, h * 0.78, w, h), fill=(0, 0, 0, 120))
    for i, k in enumerate(("♥", "💬", "➤")):
        y = h * 0.52 + i * 130
        d.ellipse((w - 120, y, w - 40, y + 80), fill=(255, 255, 255, 60))
    d.text((w - 80, h * 0.52 + 40), "♥", font=font(DEJAVU_B, 46), fill=(255, 70, 90), anchor="mm")
    d.text((w - 80, h * 0.52 + 170), "≡", font=font(DEJAVU_B, 40), fill=(255, 255, 255), anchor="mm")
    d.text((w - 80, h * 0.52 + 300), "➤", font=font(DEJAVU_B, 40), fill=(255, 255, 255), anchor="mm")
    d.text((40, h * 0.83), user, font=font(INTER_B, 40), fill=(255, 255, 255))
    d.text((40, h * 0.87), caption, font=font(INTER_R, 34), fill=(235, 235, 235))
    d.rectangle((40, h - 40, w - 40, h - 34), fill=(255, 255, 255, 90))
    d.rectangle((40, h - 40, w * 0.45, h - 34), fill=(255, 255, 255, 230))
    # Statusleiste
    d.text((50, 30), "21:40", font=font(INTER, 34), fill=(255, 255, 255))
    d.text((w - 60, 30), "✈", font=font(DEJAVU_B, 34), fill=(255, 255, 255), anchor="ra")
    im.save(OUT / f"flug_{name}.png")


def banner():
    """Gebetszeit-Hinweis (oben im Handy), wird weggewischt."""
    w, h = 680, 200
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rr(d, (0, 0, w - 1, h - 1), 44, fill=(245, 245, 247, 238))
    d.ellipse((30, 40, 120, 130), fill=(22, 120, 86, 255))
    # Mondsichel im Symbol
    d.ellipse((50, 55, 104, 115), fill=(250, 250, 240, 255))
    d.ellipse((64, 50, 116, 106), fill=(22, 120, 86, 255))
    d.text((150, 36), "GEBETSZEIT", font=font(INTER_B, 28), fill=(110, 110, 118))
    d.text((w - 36, 36), "jetzt", font=font(INTER_R, 28), fill=(140, 140, 148), anchor="ra")
    d.text((150, 78), "Isha", font=font(INTER_B, 46), fill=(18, 18, 22))
    d.text((150, 134), "Zeit für das Nachtgebet · 21:40", font=font(INTER_R, 30), fill=(60, 60, 66))
    im.save(OUT / "flug_banner.png")


def ife_map():
    """Flugkarte im Sitz-Bildschirm."""
    w, h = 800, 500
    im = Image.new("RGB", (w, h), (8, 20, 44))
    d = ImageDraw.Draw(im)
    rnd = random.Random(3)
    for _ in range(9):   # Landmassen
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        pts = [(x + math.cos(a) * rnd.uniform(60, 170), y + math.sin(a) * rnd.uniform(40, 120)) for a in [i * 0.7 for i in range(9)]]
        d.polygon(pts, fill=(28, 56, 52))
    im = im.filter(ImageFilter.GaussianBlur(6))
    d = ImageDraw.Draw(im)
    d.line([(120, 380), (330, 250), (620, 140)], fill=(240, 200, 90), width=5)
    d.line([(330, 250), (620, 140)], fill=(240, 200, 90, 90), width=3)
    d.ellipse((112, 372, 128, 388), fill=(240, 200, 90))
    d.ellipse((612, 132, 628, 148), fill=(255, 255, 255))
    d.text((340, 228), "✈", font=font(DEJAVU_B, 44), fill=(255, 255, 255), anchor="mm")
    d.rectangle((0, h - 70, w, h), fill=(4, 10, 24))
    f = font(INTER, 28)
    d.text((30, h - 52), "HÖHE 11.000 m", font=f, fill=(200, 215, 235))
    d.text((330, h - 52), "850 km/h", font=f, fill=(200, 215, 235))
    d.text((w - 30, h - 52), "ANKUNFT 23:05", font=f, fill=(200, 215, 235), anchor="ra")
    im.save(OUT / "flug_ife.png")


def seatbelt():
    w, h = 400, 160
    im = Image.new("RGB", (w, h), (20, 20, 22))
    d = ImageDraw.Draw(im)
    for cx, kind in ((110, "belt"), (290, "nosmoke")):
        d.ellipse((cx - 62, 18, cx + 62, 142), outline=(255, 236, 200), width=8)
        if kind == "belt":
            d.ellipse((cx - 16, 38, cx + 16, 66), fill=(255, 236, 200))
            d.rounded_rectangle((cx - 26, 70, cx + 26, 118), 10, fill=(255, 236, 200))
            d.line([(cx - 36, 98), (cx + 36, 98)], fill=(20, 20, 22), width=8)
            d.rectangle((cx - 8, 92, cx + 8, 104), fill=(255, 236, 200))
        else:
            d.rectangle((cx - 40, 74, cx + 30, 90), fill=(255, 236, 200))
            d.line([(cx - 44, 42), (cx + 44, 122)], fill=(255, 236, 200), width=8)
    im.save(OUT / "flug_belt.png")


def exit_sign():
    w, h = 400, 140
    im = Image.new("RGB", (w, h), (12, 150, 70))
    d = ImageDraw.Draw(im)
    d.text((w / 2, h / 2), "EXIT", font=font(INTER_B, 92), fill=(240, 255, 240), anchor="mm")
    im.save(OUT / "flug_exit.png")


def board():
    """Abflug-/Ankunftstafel im Terminal (früher Morgen)."""
    w, h = 1200, 600
    im = Image.new("RGB", (w, h), (10, 12, 18))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 80), fill=(22, 40, 90))
    d.text((30, 18), "ABFLUG  DEPARTURES", font=font(INTER_B, 40), fill=(255, 255, 255))
    d.text((w - 30, 18), "05:52", font=font(INTER_B, 40), fill=(255, 210, 80), anchor="ra")
    rows = [("06:10", "ISTANBUL", "B12", "BOARDING"), ("06:25", "DUBAI", "C04", "PÜNKTLICH"), ("06:40", "AMSTERDAM", "A21", "PÜNKTLICH"),
            ("07:05", "KAIRO", "B07", "PÜNKTLICH"), ("07:15", "MADRID", "A03", "VERSPÄTET"), ("07:30", "JEDDAH", "C11", "PÜNKTLICH"),
            ("07:55", "WIEN", "A14", "PÜNKTLICH")]
    f = font(INTER, 36)
    for i, (t, c, g, s) in enumerate(rows):
        y = 100 + i * 70
        if i % 2:
            d.rectangle((0, y - 8, w, y + 56), fill=(16, 18, 26))
        d.text((30, y), t, font=f, fill=(255, 210, 80))
        d.text((200, y), c, font=f, fill=(240, 240, 240))
        d.text((720, y), g, font=f, fill=(240, 240, 240))
        d.text((w - 30, y), s, font=f, fill=(120, 230, 140) if s != "VERSPÄTET" else (255, 120, 90), anchor="ra")
    im.save(OUT / "flug_board.png")


def prayer_sign():
    w, h = 800, 260
    im = Image.new("RGB", (w, h), (235, 236, 232))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 220, 240), 30, fill=(22, 98, 74))
    # Person auf Gebetsteppich (Piktogramm, ohne Gesicht)
    d.rectangle((70, 190, 170, 204), fill=(240, 240, 230))
    d.ellipse((104, 60, 136, 92), fill=(240, 240, 230))
    d.rounded_rectangle((98, 96, 142, 160), 14, fill=(240, 240, 230))
    d.rounded_rectangle((100, 150, 140, 190), 10, fill=(240, 240, 230))
    d.text((260, 50), "Gebetsraum", font=font(INTER_B, 64), fill=(30, 34, 40))
    d.text((260, 140), "Prayer Room  ·  Raum der Stille", font=font(INTER_R, 36), fill=(80, 84, 90))
    im.save(OUT / "flug_gebetsraum.png")


def gate_sign():
    w, h = 600, 200
    im = Image.new("RGB", (w, h), (250, 205, 40))
    d = ImageDraw.Draw(im)
    d.text((40, h / 2), "B", font=font(INTER_B, 130), fill=(20, 20, 20), anchor="lm")
    d.text((170, h / 2), "10 – 18   →", font=font(INTER_B, 84), fill=(20, 20, 20), anchor="lm")
    im.save(OUT / "flug_gate.png")


def qibla_sign():
    w, h = 500, 260
    im = Image.new("RGB", (w, h), (240, 238, 230))
    d = ImageDraw.Draw(im)
    d.text((w / 2, 70), "QIBLA", font=font(INTER_B, 72), fill=(22, 98, 74), anchor="mm")
    d.polygon([(w / 2, 130), (w / 2 + 50, 190), (w / 2 + 18, 190), (w / 2 + 18, 240), (w / 2 - 18, 240), (w / 2 - 18, 190),
               (w / 2 - 50, 190)], fill=(22, 98, 74))
    im.save(OUT / "flug_qibla.png")


def post_ui():
    """Handy des Sitznachbarn nach der Landung: „Neuer Beitrag“."""
    w, h = 720, 1560
    im = blob_bg(w, h, 9, [(40, 46, 60), (90, 70, 120), (200, 120, 90), (30, 40, 70)])
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, 0, w, 150), fill=(0, 0, 0, 160))
    d.text((w / 2, 85), "Neuer Beitrag", font=font(INTER_B, 44), fill=(255, 255, 255), anchor="mm")
    d.rounded_rectangle((60, 240, w - 60, 900), 30, fill=(20, 24, 34, 220))
    d.text((100, 280), "Wir wären fast abgestürzt!!", font=font(INTER_B, 38), fill=(255, 255, 255))
    d.text((100, 340), "#turbulenzen #überlebt", font=font(INTER_R, 34), fill=(140, 190, 255))
    d.rounded_rectangle((w / 2 - 170, h - 260, w / 2 + 170, h - 160), 50, fill=(255, 60, 90))
    d.text((w / 2, h - 210), "Posten", font=font(INTER_B, 44), fill=(255, 255, 255), anchor="mm")
    im.save(OUT / "flug_post.png")


if __name__ == "__main__":
    feed("feed_mine", 4, [(30, 30, 50), (240, 90, 60), (255, 190, 60), (60, 120, 230), (20, 20, 30)], "@daily.laughs", "Wenn der Lehrer sagt …")
    feed("feed_nb", 7, [(60, 20, 70), (255, 80, 160), (80, 220, 200), (250, 230, 90), (20, 10, 30)], "@prank.king", "Er hat es NICHT kommen sehen")
    banner()
    ife_map()
    seatbelt()
    exit_sign()
    board()
    prayer_sign()
    gate_sign()
    qibla_sign()
    post_ui()
    print("Texturen:", sorted(p.name for p in OUT.glob("flug_*.png")))
