# Gemalte Texturen für den Ink-Pop-Look (wie im Vorbild: Holzdielen mit Maserung, Wände mit Pinselstrichen,
# Teppich mit Muster, Stoff, Vorhangfalten, Fensterblick, Fernsehbild, Kalender). -> blender/inkpop/tex/
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex")
os.makedirs(OUT, exist_ok=True)
JP = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
SB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
fnt = lambda p, s: ImageFont.truetype(p, s)
R = random.Random(7)


def jitter(c, a):
    return tuple(max(0, min(255, int(v + R.uniform(-a, a)))) for v in c)


def wood_floor(name="floor_wood.png", W=2048, base=(196, 136, 82)):
    im = Image.new("RGB", (W, W), base)
    d = ImageDraw.Draw(im)
    pw = W // 9  # Dielenbreite
    for i in range(10):
        x0 = i * pw
        y = -R.randint(0, W)
        while y < W:
            L = R.randint(W // 2, W)
            kb = R.uniform(0.86, 1.08)
            col = tuple(int(min(255, c * kb)) for c in base)
            d.rectangle((x0, y, x0 + pw, y + L), fill=col)
            # Maserung: lange, leicht wellige Linien
            for k in range(R.randint(5, 9)):
                gx = x0 + R.randint(6, pw - 6)
                pts = []
                for yy in range(y, y + L, 24):
                    pts.append((gx + 4 * math.sin(yy / R.uniform(60, 140) + k), yy))
                if len(pts) > 1:
                    d.line(pts, fill=tuple(int(c * kb * R.uniform(0.8, 0.9)) for c in base), width=R.choice((1, 2, 2, 3)))
            # Astloch
            if R.random() < 0.3:
                ky = y + R.randint(40, max(41, L - 40))
                kx = x0 + R.randint(20, pw - 20)
                d.ellipse((kx - 7, ky - 14, kx + 7, ky + 14), outline=(120, 76, 40), width=3)
            d.line((x0, y, x0 + pw, y), fill=(60, 38, 22), width=4)
            y += L
        d.line((x0, 0, x0, W), fill=(60, 38, 22), width=4)
    return im.filter(ImageFilter.GaussianBlur(0.6)).save(os.path.join(OUT, name))


def painted_wall(name, base, W=1024, streak=10):
    im = Image.new("RGB", (W, W), base)
    d = ImageDraw.Draw(im)
    for _ in range(260):
        x = R.randint(0, W)
        w = R.randint(6, 26)
        y0 = R.randint(-200, W)
        L = R.randint(80, 420)
        d.rectangle((x, y0, x + w, y0 + L), fill=jitter(base, streak))
    im = im.filter(ImageFilter.GaussianBlur(3))
    im.save(os.path.join(OUT, name))


def rug(name="rug.png", W=2048):
    im = Image.new("RGB", (W, int(W * 0.7)), (176, 64, 52))
    d = ImageDraw.Draw(im)
    H = im.size[1]
    for k, (inset, col, w) in enumerate(((40, (238, 222, 190), 26), (90, (60, 82, 112), 14), (120, (238, 222, 190), 8))):
        d.rectangle((inset, inset, W - inset, H - inset), outline=col, width=w)
    step = 170
    for yy in range(200, H - 150, step):
        for xx in range(200 + (yy // step % 2) * step // 2, W - 150, step):
            d.polygon([(xx, yy - 40), (xx + 40, yy), (xx, yy + 40), (xx - 40, yy)], fill=(56, 84, 110))
    im = im.filter(ImageFilter.GaussianBlur(0.8))
    # Faser-Rauschen
    px = im.load()
    for _ in range(90000):
        x, y = R.randrange(W), R.randrange(H)
        r, g, b = px[x, y]
        k = R.uniform(0.9, 1.08)
        px[x, y] = (int(min(255, r * k)), int(min(255, g * k)), int(min(255, b * k)))
    im.save(os.path.join(OUT, name))


def fabric(name, base, W=512, stripe=None):
    im = Image.new("RGB", (W, W), base)
    px = im.load()
    for y in range(W):
        for x in range(W):
            n = ((x * 7 + y * 13) % 5) - 2
            r, g, b = base
            px[x, y] = (max(0, min(255, r + n * 2)), max(0, min(255, g + n * 2)), max(0, min(255, b + n * 2)))
    if stripe:
        d = ImageDraw.Draw(im)
        for x in range(0, W, 64):
            d.rectangle((x, 0, x + 6, W), fill=stripe)
    im.filter(ImageFilter.GaussianBlur(0.7)).save(os.path.join(OUT, name))


def curtain(name, base, W=512):
    im = Image.new("RGB", (W, W), base)
    d = ImageDraw.Draw(im)
    for x in range(W):
        k = 0.82 + 0.18 * (0.5 + 0.5 * math.sin(x / W * 2 * math.pi * 7))
        d.line((x, 0, x, W), fill=tuple(int(c * k) for c in base))
    im.save(os.path.join(OUT, name))


def window_view(name="window_view.png", W=1600, H=1000):
    """Blick aus dem Fenster: Himmel, Wolken, Garten mit Zaun, Nachbarhäuser, Hügel – gemalt mit Tuschelinien."""
    im = Image.new("RGB", (W, H), (150, 196, 232))
    d = ImageDraw.Draw(im)
    for y in range(H // 2):
        t = y / (H / 2)
        d.line((0, y, W, y), fill=(int(130 + 90 * t), int(180 + 50 * t), int(230 + 15 * t)))
    for _ in range(6):
        cx, cy = R.randint(0, W), R.randint(40, 300)
        for j in range(4):
            r = R.randint(40, 80)
            d.ellipse((cx + j * 55 - r, cy - r * 0.6, cx + j * 55 + r, cy + r * 0.6), fill=(250, 250, 252))
    # Hügel
    d.polygon([(0, 560), (300, 430), (700, 500), (1100, 420), (1600, 520), (1600, H), (0, H)], fill=(118, 160, 110), outline=(40, 50, 40))
    d.polygon([(0, 640), (500, 560), (900, 610), (1600, 570), (1600, H), (0, H)], fill=(140, 180, 120), outline=(40, 50, 40))
    # Nachbarhäuser
    for k in range(5):
        x = 80 + k * 320 + R.randint(-30, 30)
        w, h = R.randint(200, 260), R.randint(160, 220)
        top = 700 - h
        d.rectangle((x, top, x + w, 700), fill=jitter((232, 226, 214), 12), outline=(30, 30, 34), width=4)
        d.polygon([(x - 20, top), (x + w // 2, top - 70), (x + w + 20, top)], fill=jitter((90, 96, 116), 15), outline=(30, 30, 34))
        for wx in range(x + 30, x + w - 50, 80):
            d.rectangle((wx, top + 40, wx + 45, top + 90), fill=(150, 180, 205), outline=(30, 30, 34), width=3)
    # Garten + Zaun
    d.rectangle((0, 700, W, H), fill=(120, 170, 96))
    for x in range(0, W, 46):
        d.rectangle((x, 640, x + 30, 760), fill=(222, 210, 186), outline=(40, 36, 30), width=3)
    d.rectangle((0, 660, W, 676), fill=(210, 196, 170), outline=(40, 36, 30), width=3)
    for _ in range(14):
        bx, by = R.randint(0, W), R.randint(760, H)
        d.ellipse((bx - 60, by - 40, bx + 60, by + 40), fill=jitter((84, 140, 80), 15), outline=(30, 50, 30), width=3)
    im.save(os.path.join(OUT, name))


def tv_screen(name, mode):
    W, H = 960, 540
    im = Image.new("RGB", (W, H), (24, 40, 92))
    d = ImageDraw.Draw(im)
    if mode == "news":
        d.rectangle((0, 0, W, H), fill=(40, 70, 130))
        for x in range(0, W, 120):
            d.rectangle((x, 300 - (x * 7) % 140, x + 90, 430), fill=(60, 96, 160))
        d.ellipse((410, 120, 550, 260), fill=(240, 200, 170), outline=(20, 20, 20), width=4)
        d.rectangle((380, 260, 580, 430), fill=(40, 40, 50), outline=(20, 20, 20), width=4)
        d.rectangle((0, 430, W, 540), fill=(250, 250, 250))
        d.rectangle((0, 430, 260, 480), fill=(220, 40, 40))
        d.text((130, 455), "ニュース", font=fnt(JP, 36), fill="white", anchor="mm")
        d.text((280, 455), "東北地方 きょうの天気 晴れ", font=fnt(JP, 34), fill=(20, 20, 20), anchor="lm")
        d.text((20, 510), "14:40", font=fnt(SB, 30), fill=(20, 20, 20), anchor="lm")
    elif mode == "eew":
        d.rectangle((0, 0, W, H), fill=(40, 70, 130))
        d.ellipse((410, 120, 550, 260), fill=(240, 200, 170), outline=(20, 20, 20), width=4)
        d.rectangle((380, 260, 580, 430), fill=(40, 40, 50), outline=(20, 20, 20), width=4)
        d.rectangle((0, 0, W, 120), fill=(210, 20, 30))
        d.text((W / 2, 60), "緊急地震速報", font=fnt(JP, 76), fill="white", anchor="mm")
        d.rectangle((0, 400, W, H), fill=(210, 20, 30))
        d.text((W / 2, 445), "宮城 福島 岩手 山形 秋田", font=fnt(JP, 40), fill="white", anchor="mm")
        d.text((W / 2, 500), "強い揺れに警戒", font=fnt(JP, 44), fill=(255, 235, 120), anchor="mm")
    elif mode == "tsunami":
        d.rectangle((0, 0, W, H), fill=(14, 22, 60))
        pts = [(220, 40), (300, 120), (330, 230), (320, 330), (360, 430), (420, 520)]
        d.line(pts, fill=(240, 30, 30), width=26)
        d.line(pts[2:], fill=(255, 140, 0), width=14)
        d.rectangle((520, 40, 940, 500), fill=(30, 40, 90))
        d.text((730, 110), "大津波警報", font=fnt(JP, 64), fill=(255, 60, 60), anchor="mm")
        d.text((730, 220), "福島県", font=fnt(JP, 56), fill="white", anchor="mm")
        d.text((730, 300), "予想 3m", font=fnt(JP, 52), fill=(255, 220, 90), anchor="mm")
        d.text((730, 420), "すぐ逃げて！", font=fnt(JP, 58), fill="white", anchor="mm")
    im.save(os.path.join(OUT, name))


def calendar(name="calendar.png"):
    W, H = 600, 800
    im = Image.new("RGB", (W, H), (250, 248, 240))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 300), fill=(120, 170, 210))
    d.ellipse((60, 60, 260, 260), fill=(250, 200, 210))
    d.text((420, 150), "2011", font=fnt(SB, 60), fill="white", anchor="mm")
    d.text((W / 2, 350), "3月", font=fnt(JP, 64), fill=(30, 30, 30), anchor="mm")
    days = "日月火水木金土"
    for i, ch in enumerate(days):
        d.text((50 + i * 80, 420), ch, font=fnt(JP, 30), fill=(200, 40, 40) if i == 0 else (40, 40, 40), anchor="mm")
    day = 1
    col = 2  # 1. März 2011 = Dienstag
    row = 0
    while day <= 31:
        x, y = 50 + col * 80, 480 + row * 60
        d.text((x, y), str(day), font=fnt(SB, 30), fill=(200, 40, 40) if col == 0 else (40, 40, 40), anchor="mm")
        if day == 11:
            d.ellipse((x - 26, y - 26, x + 26, y + 26), outline=(220, 40, 40), width=4)
        day += 1
        col += 1
        if col == 7:
            col, row = 0, row + 1
    im.save(os.path.join(OUT, name))


def photo(name, seed):
    r = random.Random(seed)
    im = Image.new("RGB", (300, 220), (200, 225, 240))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 140, 300, 220), fill=(130, 180, 110))
    for k in range(r.randint(2, 4)):
        x = 50 + k * 70
        d.ellipse((x - 18, 60, x + 18, 96), fill=(240, 200, 170), outline=(30, 30, 30), width=3)
        d.rectangle((x - 22, 96, x + 22, 170), fill=r.choice([(200, 60, 60), (60, 90, 160), (230, 190, 60)]), outline=(30, 30, 30), width=3)
    im.save(os.path.join(OUT, name))


def books(name="books.png"):
    W, H = 1024, 256
    im = Image.new("RGB", (W, H), (60, 40, 30))
    d = ImageDraw.Draw(im)
    x = 0
    while x < W:
        w = R.randint(18, 42)
        h = R.randint(170, 250)
        col = R.choice([(180, 50, 50), (50, 80, 140), (220, 190, 80), (60, 120, 80), (230, 230, 220), (120, 60, 110), (210, 120, 50)])
        d.rectangle((x, H - h, x + w, H), fill=col, outline=(25, 20, 18), width=3)
        d.rectangle((x + 4, H - h + 20, x + w - 4, H - h + 34), fill=jitter(col, 40))
        x += w
    im.save(os.path.join(OUT, name))


if __name__ == "__main__":
    wood_floor()
    painted_wall("wall_cream.png", (226, 218, 196))
    painted_wall("wall_green.png", (196, 206, 188))
    painted_wall("ceiling.png", (232, 230, 224), streak=5)
    rug()
    fabric("sofa.png", (92, 112, 140))
    fabric("cushion.png", (196, 120, 70), stripe=(220, 180, 120))
    fabric("zabuton.png", (150, 60, 70), stripe=(200, 160, 90))
    curtain("curtain.png", (70, 110, 90))
    window_view()
    for m in ("news", "eew", "tsunami"):
        tv_screen(f"tv_{m}.png", m)
    calendar()
    for k in range(4):
        photo(f"photo{k}.png", k)
    books()
    print(sorted(os.listdir(OUT)))
