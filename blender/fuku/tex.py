# Texturen für den Kontrollraum (Fukushima Daiichi, Block 1/2): Wandtafel, Pult, Monitore, Tür-Schild.
# Jeweils "an" (mit Strom) und "aus" (Blackout, Zeiger auf Null, Lampen dunkel) + Leuchtmasken.
import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex")
os.makedirs(OUT, exist_ok=True)
JP = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
f = lambda p, s: ImageFont.truetype(p, s)
R = random.Random(11)
PANEL = (196, 202, 186)  # hellgrünlich-beige wie in japanischen Leitwarten

ANN = ["原子炉水位低", "原子炉圧力高", "スクラム", "地震加速度大", "主蒸気隔離弁閉", "非常用DG起動", "給水ポンプ停止", "IC作動",
       "D/W圧力高", "タービントリップ", "発電機トリップ", "所内電源喪失", "制御棒全挿入", "炉心流量低", "冷却水温度高", "排気筒放射線高",
       "SRV開", "HPCI起動", "RCIC起動", "CS系起動", "電源切替", "警報", "ポンプ異常", "弁異常"]


def gauge(d, cx, cy, r, val, label, on):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(28, 30, 32))
    d.ellipse((cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6), fill=(238, 236, 226))
    for k in range(11):
        a = math.radians(-225 + k * 27)
        d.line((cx + math.cos(a) * (r - 10), cy + math.sin(a) * (r - 10), cx + math.cos(a) * (r - 22), cy + math.sin(a) * (r - 22)), fill=(20, 20, 20), width=3)
    d.arc((cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14), 270, 315, fill=(200, 30, 30), width=6)
    v = val if on else 0.0
    a = math.radians(-225 + v * 270)
    d.line((cx, cy, cx + math.cos(a) * (r - 18), cy + math.sin(a) * (r - 18)), fill=(15, 15, 15), width=5)
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(15, 15, 15))
    d.text((cx, cy + r * 0.45), label, font=f(JP, int(r * 0.22)), fill=(20, 20, 20), anchor="mm")


def edgewise(d, x, y, w, h, val, on):
    d.rectangle((x, y, x + w, y + h), fill=(28, 30, 32))
    d.rectangle((x + 5, y + 5, x + w - 5, y + h - 5), fill=(238, 236, 226))
    for k in range(9):
        yy = y + 12 + k * (h - 24) / 8
        d.line((x + 8, yy, x + 22, yy), fill=(20, 20, 20), width=2)
    v = val if on else 0.0
    yy = y + h - 12 - v * (h - 24)
    d.polygon([(x + w - 10, yy - 8), (x + w - 10, yy + 8), (x + 26, yy)], fill=(200, 30, 30))


def wall():
    W, H = 4096, 1228  # 8 m x 2,4 m
    for on in (True, False):
        im = Image.new("RGB", (W, H), PANEL)
        em = Image.new("RGB", (W, H), (0, 0, 0))
        ann = Image.new("RGB", (W, H), (0, 0, 0))
        d, de, da = ImageDraw.Draw(im), ImageDraw.Draw(em), ImageDraw.Draw(ann)
        r = random.Random(3)
        for s in range(8):  # Sektionen
            x0 = s * 512
            d.rectangle((x0, 0, x0 + 6, H), fill=(140, 146, 132))
            d.text((x0 + 256, 22), f"UNIT {1 if s < 4 else 2}  ·  {['RX', 'FW', 'ECCS', 'ELEC'][s % 4]}", font=f(SANS, 22), fill=(40, 40, 40), anchor="mm")
            # Warnlampen-Feld (oben)
            for row in range(5):
                for col in range(7):
                    tx, ty = x0 + 30 + col * 66, 50 + row * 46
                    lab = ANN[r.randrange(len(ANN))]
                    d.rectangle((tx, ty, tx + 60, ty + 40), fill=(232, 228, 214), outline=(90, 90, 90), width=2)
                    d.text((tx + 30, ty + 20), lab[:4] + "\n" + lab[4:8], font=f(JP, 12), fill=(60, 60, 60), anchor="mm", align="center")
                    col_l = r.choice([(255, 235, 170), (255, 120, 80), (255, 250, 230)])
                    da.rectangle((tx + 2, ty + 2, tx + 58, ty + 38), fill=col_l)
            # Anlagenschema mit Ventilen (Mitte)
            yb = 300
            d.rectangle((x0 + 20, yb, x0 + 492, yb + 300), fill=(205, 210, 196), outline=(120, 120, 110), width=2)
            for k in range(4):
                yy = yb + 50 + k * 65
                c = [(40, 110, 200), (40, 160, 80), (220, 140, 30), (200, 50, 50)][k]
                d.line((x0 + 40, yy, x0 + 470, yy), fill=c, width=8)
                for vx in range(x0 + 90, x0 + 470, 110):
                    d.rectangle((vx - 14, yy - 14, vx + 14, yy + 14), fill=(30, 30, 30))
                    lit = r.random() < 0.5
                    d.ellipse((vx - 9, yy - 30, vx + 1, yy - 20), fill=(60, 80, 60))
                    d.ellipse((vx + 3, yy - 30, vx + 13, yy - 20), fill=(80, 50, 50))
                    if on:
                        (de.ellipse((vx - 9, yy - 30, vx + 1, yy - 20), fill=(60, 255, 90)) if lit else de.ellipse((vx + 3, yy - 30, vx + 13, yy - 20), fill=(255, 60, 50)))
            # Zeiger-Instrumente (unten)
            for k in range(3):
                gauge(d, x0 + 95 + k * 160, 720, 66, r.uniform(0.35, 0.8), ["水位", "圧力", "流量", "温度", "電圧", "出力"][r.randrange(6)], on)
            for k in range(5):
                edgewise(d, x0 + 30 + k * 94, 820, 64, 170, r.uniform(0.3, 0.85), on)
            # Lampenreihe ganz unten
            for k in range(10):
                lx = x0 + 40 + k * 46
                c = r.choice([(70, 255, 100), (255, 70, 60), (255, 220, 80), (255, 255, 255)])
                d.ellipse((lx, 1040, lx + 26, 1066), fill=tuple(int(v * 0.35) for v in c))
                if on:
                    de.ellipse((lx, 1040, lx + 26, 1066), fill=c)
            d.text((x0 + 256, 1130), "東京電力  福島第一原子力発電所", font=f(JP, 22), fill=(70, 70, 70), anchor="mm")
        tag = "on" if on else "off"
        im.save(f"{OUT}/wall_{tag}.png")
        em.filter(ImageFilter.GaussianBlur(1.5)).save(f"{OUT}/wall_em_{tag}.png")
        if on:
            ann.save(f"{OUT}/wall_ann.png")


def desk():
    W, H = 4096, 512  # schräges Pult 8 m x 1 m
    for on in (True, False):
        im = Image.new("RGB", (W, H), (176, 182, 168))
        em = Image.new("RGB", (W, H), (0, 0, 0))
        d, de = ImageDraw.Draw(im), ImageDraw.Draw(em)
        r = random.Random(9)
        for k in range(70):
            x = 40 + k * 58
            y = 120 + (k % 3) * 120
            d.rectangle((x, y, x + 44, y + 70), fill=(40, 40, 42))
            d.rectangle((x + 16, y + 8, x + 28, y + 50), fill=(200, 60, 40) if k % 4 else (30, 30, 30))
            d.ellipse((x + 2, y - 26, x + 18, y - 10), fill=(50, 80, 50))
            d.ellipse((x + 26, y - 26, x + 42, y - 10), fill=(90, 50, 50))
            if on:
                (de.ellipse((x + 2, y - 26, x + 18, y - 10), fill=(60, 255, 90)) if r.random() < 0.5 else de.ellipse((x + 26, y - 26, x + 42, y - 10), fill=(255, 70, 50)))
        tag = "on" if on else "off"
        im.save(f"{OUT}/desk_{tag}.png")
        em.filter(ImageFilter.GaussianBlur(1.2)).save(f"{OUT}/desk_em_{tag}.png")


def monitors():
    W, H = 640, 480
    im = Image.new("RGB", (W, H), (6, 18, 10))
    d = ImageDraw.Draw(im)
    lines = ["UNIT 1  PLANT STATUS   14:46", "", "RX MODE      SHUTDOWN", "CONTROL RODS  ALL IN", "RX POWER       0.0 %",
             "RPV LEVEL     +1120 mm", "RPV PRESS     6.8 MPa", "D/G A  B      RUN", "IC  A  B      STBY"]
    for i, l in enumerate(lines):
        d.text((30, 30 + i * 46), l, font=f(MONO, 30), fill=(90, 255, 120))
    im.save(f"{OUT}/mon_ok.png")
    im = Image.new("RGB", (W, H), (40, 4, 4))
    d = ImageDraw.Draw(im)
    d.rectangle((16, 16, W - 16, H - 16), outline=(255, 60, 50), width=8)
    d.text((W / 2, 120), "大津波警報", font=f(JP, 92), fill=(255, 235, 230), anchor="mm")
    d.text((W / 2, 235), "TSUNAMI-WARNUNG", font=f(SANS, 52), fill=(255, 80, 60), anchor="mm")
    d.text((W / 2, 320), "FUKUSHIMA-KÜSTE", font=f(SANS, 34), fill=(255, 220, 210), anchor="mm")
    d.text((W / 2, 385), "14:49  SOFORT EVAKUIEREN", font=f(SANS, 30), fill=(255, 220, 210), anchor="mm")
    im.save(f"{OUT}/mon_warn.png")
    im = Image.new("RGB", (W, H), (4, 4, 5))
    im.save(f"{OUT}/mon_off.png")


def sign():
    im = Image.new("RGB", (800, 300), (230, 190, 30))
    d = ImageDraw.Draw(im)
    d.rectangle((10, 10, 790, 290), outline=(20, 20, 20), width=10)
    d.text((400, 100), "原子炉建屋", font=f(JP, 110), fill=(20, 20, 20), anchor="mm")
    d.text((400, 225), "REACTOR BUILDING  ☢", font=f(SANS, 54), fill=(20, 20, 20), anchor="mm")
    im.save(f"{OUT}/sign.png")


if __name__ == "__main__":
    wall()
    desk()
    monitors()
    sign()
    print("ok", sorted(os.listdir(OUT)))
