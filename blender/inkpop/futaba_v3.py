# Futaba v3 – „11. März 2011“ als ein Video. Ich-Sicht, Ink-Pop.
# Hook (Welle am Fenster) → 14:45 Sofa, Papa-Nachricht → 14:46 Warnung, Beben, Hana unter den Tisch ziehen →
# Papa anrufen: kein Netz → Tsunami-Warnung, Mama, Strom weg, Durchsage → 15:27 Welle → Treppe hoch → oben: Flut.
# blender -b --python futaba_v3.py -s A -e B -a -- <ausgabe_präfix> <prozent>
import bpy, sys, os, math, random, json
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "futaba"))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
import figure as F, cast as C, livingroom as LR, sets_v3 as SV

sc = bpy.context.scene
FPS = 24
T = lambda s: int(round(s * FPS)) + 1
R = random.Random(12)

# ---------- Zeitleiste (Sekunden) ----------
HOOK = 2.2          # 0–2.2: Welle am Fenster (Vorgriff)
PING = 2.8          # Papa schreibt
EEW = 7.0
QUAKE = 9.4
QEND = 24.5
CALL = 27.4         # Papa anrufen → kein Netz
TVW = 30.6          # Tsunami-Warnung im TV
MAMA = 33.4
POWER = 39.6
T2 = 49.8           # Zeitsprung 15:27 (Karte 49.8–50.9)
RUN = 58.2          # Treppe
UP = 62.2           # oben am Fenster
END = 69.0
AT = {"h1": 4.6, "tv2": 7.4, "h3": 8.7, "m2": 9.9, "h4": 15.0, "m3": 18.8, "m6": 29.0, "tv3": 30.8, "ma2": 36.4, "lsp": 40.6,
      "h5": 45.3, "m4": 46.4, "h6": 51.6, "m5": 54.2, "ma3": 55.6, "h7": 60.0, "m7": 63.4}
json.dump(dict(AT=AT, HOOK=HOOK, PING=PING, EEW=EEW, QUAKE=QUAKE, QEND=QEND, CALL=CALL, TVW=TVW, MAMA=MAMA, POWER=POWER, T2=T2, RUN=RUN,
               UP=UP, END=END, FPS=FPS), open(os.path.join(ROOT, "src", "futaba4", "timeline.json"), "w"), indent=1)
TIM = json.load(open(os.path.join(ROOT, "src", "futaba3", "timing.json")))
SCR = json.load(open(os.path.join(ROOT, "src", "futaba3", "script.json")))
WAV = {s["id"]: os.path.join(ROOT, "public", l["file"]) for s, l in zip(SCR["sentences"], TIM["lines"])}


def qamp(t):
    if t < QUAKE or t > QEND + 1.5:
        return 0.0
    a = min(1.0, (t - QUAKE) / 1.0) * min(1.0, max(0.0, (QEND + 1.5 - t) / 2.5))
    return a * (0.8 + 0.2 * math.sin(t * 1.3))


# ---------- Sets ----------
S = LR.build()
LR.tv_material(S["screens"]["tv"], [(1, "off"), (T(HOOK), "tv_news.png"), (T(EEW), "tv_eew.png"), (T(TVW - 0.2), "tv_tsunami.png"), (T(POWER), "off")])
tb = S["table"]
tb.scale.z = 1.16
bpy.data.objects["tb_shelf"].hide_render = True
ST_ = SV.stairs()
UPS = SV.upstairs()
O, FZ = UPS["O"], UPS["FZ"]

# ---------- Figuren ----------
me = C.make("me", jacket=(0.2, 0.24, 0.34), pants=(0.3, 0.3, 0.34))
hana = F.make_figure("hana", skin=(0.96, 0.8, 0.68), hair=(0.12, 0.08, 0.07), jacket=(0.93, 0.6, 0.66), pants=(0.25, 0.28, 0.4),
                     hair_style="long", height=1.32, build=0.9, iris=(0.32, 0.2, 0.12), zipper=False, shoes=(0.95, 0.95, 0.95))
mama = F.make_figure("mama", skin=(0.93, 0.76, 0.62), hair=(0.1, 0.08, 0.07), jacket=(0.86, 0.8, 0.66), pants=(0.36, 0.3, 0.32),
                     hair_style="bun", height=1.6, build=1.0, iris=(0.3, 0.18, 0.1), zipper=False, lower="skirt", socks=(0.85, 0.75, 0.68),
                     shoes=(0.8, 0.8, 0.8))
for o in me["head_parts"]:
    o.hide_render = True
for f in (me, hana, mama):
    F.look(f, 1)
    F.mouth(f, 1, 0)
    F.brows(f, 1)


def rot(f, bone, t, x=0.0, y=0.0, z=0.0):
    F.rot(f, bone, T(t), x=x, y=y, z=z)


def head(f, keys):
    for t, yaw, pitch in keys:
        rot(f, "neck", t, y=yaw * 0.45, x=-pitch * 0.4)
        rot(f, "head", t, y=yaw * 0.55, x=-pitch * 0.6)


def heading(d):
    return math.atan2(d.x, -d.y)


def place(f, t, loc, yaw, rx=0.0):
    a_ = f["arm"]
    a_.location = loc
    a_.rotation_euler = (rx, 0, yaw)
    a_.keyframe_insert("location", frame=T(t))
    a_.keyframe_insert("rotation_euler", frame=T(t))


vis = lambda o, keys: [(setattr(ob, "hide_render", not v), ob.keyframe_insert("hide_render", frame=T(t) if t else 1)) for ob in [o] + list(o.children_recursive) for t, v in keys]


def alive(f, t0, t1, seed, amp=1.0, darts=True):
    """Lebendig: Atmen, Gewicht verlagern, kleine Blicksprünge, Blinzeln alle 2–4 s."""
    r = random.Random(seed)
    ph = [r.uniform(0, 6.3) for _ in range(5)]
    for fr in range(T(t0), T(t1), 6):
        t = fr / FPS
        F.rot(f, "chest", fr, x=amp * 1.6 * math.sin(t * 2 * math.pi / 3.4 + ph[0]), y=amp * 2.2 * math.sin(t * 0.55 + ph[1]),
              z=amp * 1.2 * math.sin(t * 0.8 + ph[2]))
    t = t0 + r.uniform(0.5, 2.0)
    while t < t1:
        F.blink(f, T(t))
        t += r.uniform(2.0, 4.2)


def gesture(f, side, t, dur):
    """Hand-Geste beim Sprechen (Unterarm hoch, kleine Schwünge)."""
    rot(f, f"upperarm.{side}", t, x=0, z=(4 if side == "L" else -4))
    rot(f, f"forearm.{side}", t, x=-14)
    for k, dt in enumerate((0.25, 0.55, 0.85, 1.15)):
        if dt > dur:
            break
        rot(f, f"upperarm.{side}", t + dt, x=-35 - 10 * (k % 2), z=(14 if side == "L" else -14))
        rot(f, f"forearm.{side}", t + dt, x=-70 - 15 * (k % 2))
    rot(f, f"upperarm.{side}", t + dur + 0.3, x=0, z=(4 if side == "L" else -4))
    rot(f, f"forearm.{side}", t + dur + 0.3, x=-14)


# --- ich (nur bis zum Abtauchen sichtbar: Beine/Arme vom Sofa) ---
a = me["arm"]
place(me, 0, (0.25, -1.92, -0.44), math.pi)
for sd in ("L", "R"):
    rot(me, f"thigh.{sd}", 0, x=-88, z=(-6 if sd == "L" else 6))
    rot(me, f"shin.{sd}", 0, x=88)
rot(me, "upperarm.L", 0, x=-28, z=-10)
rot(me, "forearm.L", 0, x=-40)
# Blick (gier + = links, nick + = hoch); ständige kleine Kopfbewegung kommt über die Brust
for t, yaw, pitch in ((HOOK, 2, -30), (PING + 0.4, 2, -32), (4.3, 2, -30), (4.8, 32, -14), (6.6, 30, -12), (7.2, 4, -4), (8.6, 32, -10),
                      (9.4, 20, -6), (10.4, 34, -16), (11.2, 30, -24)):
    rot(me, "spine", t, y=yaw * 0.2, x=-pitch * 0.1)
    rot(me, "neck", t, y=yaw * 0.4, x=2 - pitch * 0.35)
    rot(me, "head", t, y=yaw * 0.4, x=2 - pitch * 0.45)
for fr in range(T(HOOK), T(11.4), 2):
    t = (fr - 1) / FPS
    am = qamp(t) * 2.8 + 0.45
    F.rot(me, "chest", fr, x=am * math.sin(t * (29 if qamp(t) else 1.7)) + 0.4 * math.sin(t * 0.9), y=am * 0.7 * math.sin(t * (23 if qamp(t) else 1.3) + 1),
          z=am * 0.6 * math.sin(t * (19 if qamp(t) else 1.1)))
for o in [x for x in bpy.data.objects if x.parent == a]:
    if o not in me["head_parts"]:
        vis(o, [(0, False), (HOOK, True), (11.4, False)])

# --- Hana ---
HK = (-0.95, 0.5)
place(hana, 0, (HK[0], HK[1], -0.47), math.radians(-60))
for sd in ("L", "R"):
    rot(hana, f"thigh.{sd}", 0, x=-92, z=(-8 if sd == "L" else 8))
    rot(hana, f"shin.{sd}", 0, x=165)
    rot(hana, f"upperarm.{sd}", 0, x=-35, z=(10 if sd == "L" else -10))
    rot(hana, f"forearm.{sd}", 0, x=-75)
rot(hana, "spine", 0, x=10)
alive(hana, 0, END, 7)
ds = LR.group("ds")
F.bone_parent(ds, hana["arm"], "hand.R")
ds.matrix_parent_inverse = Matrix()
ds.location = (0.07, 0.04, 0.0)
LR.box("dsbot", (0, 0, 0), (0.13, 0.075, 0.018), LR.soft("dsm", (0.95, 0.95, 0.97)), parent=ds)
LR.box("dsscr", (0, 0, 0.0095), (0.1, 0.055, 0.002), F.flat_mat("dsglow", (0.6, 0.85, 1.0)), parent=ds)
vis(ds, [(0, True), (10.4, False)])
# Daumen tippen auf der Konsole
for fr in range(T(HOOK), T(EEW), 3):
    F.rot(hana, "hand.R", fr, x=4 * math.sin(fr * 1.7))
    F.rot(hana, "hand.L", fr, x=4 * math.sin(fr * 1.3 + 1))
head(hana, [(0, 0, -20), (4.4, 0, -20), (4.8, -40, 5), (6.8, -38, 5), (7.3, 20, 5), (8.6, -45, 2), (9.6, -45, 2)])
F.look(hana, T(4.8), -15, 0)
F.look(hana, T(7.3), 10, 5)
F.look(hana, T(8.6), -20, 0)
F.brows(hana, T(4.6), 0.5)
F.brows(hana, T(7.4), 0.8, 0.3)
F.brows(hana, T(8.7), 1.0, 1.0)
gesture(hana, "L", 4.7, 1.8)
# ich ziehe sie am Arm unter den Tisch (10.2–11.8): Hana kippt zur Seite, taucht seitlich unter den Tisch
CAMU = Vector((0.32, 0.42, 0))
dirc = (Vector((-1.6, 0.8, 0)) - CAMU).normalized()
HEADU = CAMU + dirc * 0.62
face_d = -dirc
yaw_u = heading(face_d)
ROOTU = HEADU - face_d * (1.18 * 0.92)
pre = ROOTU - face_d * 0.75
place(hana, 10.2, (HK[0], HK[1], -0.47), math.radians(-60))
place(hana, 11.0, (pre.x, pre.y, 0.06), yaw_u, math.radians(84))
place(hana, 11.9, (ROOTU.x, ROOTU.y, 0.05), yaw_u, math.radians(84))
for sd in ("L", "R"):
    rot(hana, f"thigh.{sd}", 10.2, x=-92, z=(-8 if sd == "L" else 8))
    rot(hana, f"shin.{sd}", 10.2, x=165)
    rot(hana, f"thigh.{sd}", 11.6, x=4, z=(-4 if sd == "L" else 4))
    rot(hana, f"shin.{sd}", 11.6, x=25)
    rot(hana, f"upperarm.{sd}", 11.6, x=-95, z=(-14 if sd == "L" else 14))
    rot(hana, f"forearm.{sd}", 11.6, x=-70)
rot(hana, "spine", 10.2, x=10)
rot(hana, "spine", 11.6, x=-16)
head(hana, [(11.0, 0, 30), (11.9, 0, 52), (QEND, 0, 52)])
F.look(hana, T(11.9), 0, 6)
F.brows(hana, T(12.0), 0.8, 1.0)
for o in [o for o in bpy.data.objects if o.name.startswith(("hana_hairside", "hana_hairback"))]:
    vis(o, [(0, True), (10.9, False), (26.6, True)])
for fr in range(T(11.9), T(QEND), 2):  # zittert
    t = (fr - 1) / FPS
    am = qamp(t)
    F.rot(hana, "chest", fr, x=1.5 * am * math.sin(t * 37), y=2.5 * am * math.sin(t * 29 + 1), z=2.0 * am * math.sin(t * 23))
rot(hana, "upperarm.R", 19.6, x=-95, z=14)
rot(hana, "forearm.R", 19.6, x=-70)
rot(hana, "upperarm.R", 20.6, x=-150, z=6)
rot(hana, "forearm.R", 20.6, x=-12)
rot(hana, "upperarm.R", QEND, x=-150, z=6)
rot(hana, "forearm.R", QEND, x=-12)
F.brows(hana, T(19.8), 1.0, 1.0)
# raus und aufstehen (25.0–27.0), steht neben dem Tisch
STAND = Vector((-0.75, 0.05, 0))
place(hana, 25.0, (ROOTU.x, ROOTU.y, 0.05), yaw_u, math.radians(84))
place(hana, 25.8, (pre.x, pre.y, 0.06), yaw_u, math.radians(84))
ys = heading(Vector((0.2, -0.6, 0)) - STAND)
while ys - yaw_u > math.pi:
    ys -= 2 * math.pi
while ys - yaw_u < -math.pi:
    ys += 2 * math.pi
place(hana, 27.0, (STAND.x, STAND.y, 0.0), ys)
for sd in ("L", "R"):
    rot(hana, f"thigh.{sd}", 25.0, x=4, z=(-4 if sd == "L" else 4))
    rot(hana, f"shin.{sd}", 25.0, x=25)
    rot(hana, f"thigh.{sd}", 27.0, x=-2)
    rot(hana, f"shin.{sd}", 27.0, x=4)
    rot(hana, f"upperarm.{sd}", 25.0, x=-95, z=(-14 if sd == "L" else 14))
    rot(hana, f"forearm.{sd}", 25.0, x=-70)
    rot(hana, f"upperarm.{sd}", 27.0, x=-20, z=(6 if sd == "L" else -6))
    rot(hana, f"forearm.{sd}", 27.0, x=-95)
rot(hana, "spine", 25.0, x=-16)
rot(hana, "spine", 27.0, x=4)
head(hana, [(QEND, 0, 52), (27.0, 0, 0), (28.0, 30, 10), (29.2, -30, -20), (30.4, 40, 0), (33.6, 40, 0), (34.2, -70, 5), (37.4, -70, 5),
            (38.4, 20, 10), (40.6, 40, 5), (44.4, 40, 5), (45.2, 0, 18), (49.8, 0, 18)])
F.look(hana, T(27.0), 0, 0)
F.look(hana, T(34.2), -20, 0)
F.look(hana, T(45.2), 0, 12)
gesture(hana, "R", 45.3, 0.8)

# --- Mama: kommt aus der Küche (Noren schwingt), Gestik ---
place(mama, 0, (1.6, LR.Y0 - 1.2, 0), heading(Vector((0, 1, 0))))
place(mama, MAMA, (1.6, LR.Y0 - 1.2, 0), heading(Vector((0, 1, 0))))
alive(mama, 0, END, 3)
path = [(MAMA, (1.6, LR.Y0 - 1.2)), (MAMA + 1.0, (1.6, LR.Y0 + 0.2)), (MAMA + 2.0, (1.15, -1.45))]
for (t0, p0), (t1, p1) in zip(path, path[1:]):
    n = int((t1 - t0) * FPS / 2)
    for i in range(n + 1):
        u = i / n
        t = t0 + u * (t1 - t0)
        ph = 2 * math.pi * (t - MAMA) / 0.85
        mama["arm"].location = (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u, 0.014 * math.cos(2 * ph))
        mama["arm"].keyframe_insert("location", frame=T(t))
        for sd, sg in (("L", 1), ("R", -1)):
            rot(mama, f"thigh.{sd}", t, x=-24 * math.sin(ph) * sg)
            rot(mama, f"shin.{sd}", t, x=4 + 42 * max(0, math.cos(ph) * sg) ** 1.5)
            rot(mama, f"upperarm.{sd}", t, x=18 * math.sin(ph) * sg, z=(6 if sd == "L" else -6))
mama["arm"].rotation_euler = (0, 0, heading(Vector((-0.6, 1.0, 0))) + 2 * math.pi)
mama["arm"].keyframe_insert("rotation_euler", frame=T(MAMA + 2.0))
for sd in ("L", "R"):
    rot(mama, f"thigh.{sd}", MAMA + 2.3)
    rot(mama, f"shin.{sd}", MAMA + 2.3, x=4)
gesture(mama, "R", 36.3, 2.6)
gesture(mama, "L", 36.6, 2.0)
rot(mama, "upperarm.R", 39.8, x=-25, z=0)
rot(mama, "forearm.R", 39.8, x=-95)
head(mama, [(MAMA, 0, 0), (MAMA + 2.2, 15, -5), (36.2, 20, 0), (40.8, 60, 8), (44.4, 60, 8), (45.4, 25, -10), (49.8, 25, -10)])
F.brows(mama, T(MAMA + 1.5), 1.0, 1.0)
F.look(mama, T(MAMA + 2.2), 10, -5)
for n_, k in zip(S["noren"], range(3)):
    for v in n_.data.vertices:
        v.co.y -= 0.36
    n_.location.z += 0.36
    base = n_.rotation_euler.copy()
    push = (1.0 if k == 1 else 0.75)
    for t, ang in ((MAMA + 0.55, 0), (MAMA + 0.85, 62 * push), (MAMA + 1.2, 48 * push), (MAMA + 1.6, -18 * push), (MAMA + 2.0, 10 * push),
                   (MAMA + 2.5, -4 * push), (MAMA + 3.0, 0), (RUN + 0.6, 0), (RUN + 0.9, -60 * push), (RUN + 1.5, 20 * push), (RUN + 2.2, 0)):
        n_.rotation_euler = (base.x + math.radians(-ang), base.y, base.z)
        n_.keyframe_insert("rotation_euler", frame=T(t))

# --- 15:27: am Fenster; dann Treppe; oben ---
place(hana, T2 - 0.05, (STAND.x, STAND.y, 0.0), ys)
place(mama, T2 - 0.05, (1.15, -1.45, 0.0), heading(Vector((-0.6, 1.0, 0))) + 2 * math.pi)
place(hana, T2, (-1.55, 2.25, 0.0), heading(Vector((0.1, 1.0, 0))))
for sd in ("L", "R"):
    rot(hana, f"thigh.{sd}", T2)
    rot(hana, f"shin.{sd}", T2, x=4)
    rot(hana, f"upperarm.{sd}", T2, x=-40, z=(8 if sd == "L" else -8))
    rot(hana, f"forearm.{sd}", T2, x=-60)
head(hana, [(T2 + 0.1, 0, 0), (51.2, 0, 0), (51.7, -80, 5), (53.8, -80, 5), (54.4, 0, 0), (RUN, 0, 0)])
rot(hana, "upperarm.R", 51.5, x=-40, z=-8)
rot(hana, "upperarm.R", 51.9, x=-95, z=-30)
rot(hana, "forearm.R", 51.9, x=-10)
F.look(hana, T(51.7), -20, 0)
place(mama, T2, (1.3, 0.2, 0.0), heading(Vector((-1.0, 0.5, 0))))
place(mama, 55.2, (1.3, 0.2, 0.0), heading(Vector((-1.0, 0.5, 0))))
place(mama, 56.2, (0.45, 0.9, 0.0), heading(Vector((-1.0, 0.6, 0))))
for k in range(5):
    t = 55.2 + k * 0.2
    for sd, sg in (("L", 1), ("R", -1)):
        rot(mama, f"thigh.{sd}", t, x=-30 * sg * (1 if k % 2 else -1))
        rot(mama, f"shin.{sd}", t, x=10 + 30 * (k % 2))
gesture(mama, "R", 55.6, 2.5)
head(mama, [(T2 + 0.1, 0, 0), (56.2, 0, 0), (56.6, -10, 0)])
place(hana, RUN, (-1.55, 2.25, 0.0), heading(Vector((0.1, 1.0, 0))))
# Hana folgt die Treppe hoch (für den Blick zurück)
sy, rr, ru = ST_["y_start"], ST_["rise"], ST_["run"]
for k in range(9):
    t = RUN + 1.3 + k * 0.33
    i = k + 1
    yv = sy - i * ru + 0.95
    place(hana, t, (1.12, yv, max(0.0, (i - 1) * rr)), heading(Vector((0, -1, 0))))
    for sd, sg in (("L", 1), ("R", -1)):
        rot(hana, f"thigh.{sd}", t, x=-45 * sg * (1 if k % 2 else -1) - 10)
        rot(hana, f"shin.{sd}", t, x=30 + 30 * ((k + (sd == "R")) % 2))
head(hana, [(RUN + 1.3, 0, 18), (RUN + 4.0, 0, 18)])
# oben am Fenster
place(hana, UP - 0.05, (O.x - 0.55, O.y + 0.9, FZ), heading(Vector((0.4, 1.0, 0))))
for sd in ("L", "R"):
    rot(hana, f"thigh.{sd}", UP - 0.05)
    rot(hana, f"shin.{sd}", UP - 0.05, x=4)
    rot(hana, f"upperarm.{sd}", UP - 0.05, x=-25, z=(6 if sd == "L" else -6))
    rot(hana, f"forearm.{sd}", UP - 0.05, x=-100)
head(hana, [(UP, 0, -10), (64.6, 0, -12), (65.4, -55, 0), (END, -55, 0)])
F.brows(hana, T(UP), 1.0, 1.0)
F.look(hana, T(65.4), -15, 0)
for sid, f in (("h1", hana), ("h3", hana), ("h4", hana), ("h5", hana), ("h6", hana), ("h7", hana), ("ma2", mama), ("ma3", mama)):
    F.lipsync(f, WAV[sid], AT[sid], FPS)
place(mama, RUN + 0.2, (0.45, 0.9, 0.0), heading(Vector((-1.0, 0.6, 0))))
place(mama, RUN + 0.3, (0, -60, -20), 0)  # aus dem Bild

# ---------- Kameras ----------
sc.frame_set(1)
bpy.context.view_layer.update()


def make_cam(name, lens=10.5):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    sc.collection.objects.link(c)
    c.data.lens = lens
    c.data.sensor_fit = "VERTICAL"
    c.data.sensor_height = 30
    c.data.clip_start = 0.02
    return c


cam1 = make_cam("cam1")
b = a.data.bones["head"]
cam1.parent = a
cam1.parent_type = "BONE"
cam1.parent_bone = "head"
cam1.matrix_parent_inverse = (a.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))).inverted()
cam1.matrix_basis = a.matrix_world @ Matrix.Translation(Vector((0, -0.075, 1.555)) * me["S"]) @ Euler((math.radians(90), 0, math.pi), "XYZ").to_matrix().to_4x4()

# Handy in meiner rechten Hand (IK) + Greif-Hand (Finger an der linken Kante, Daumen rechts)
tgt = bpy.data.objects.new("ikR", None)
sc.collection.objects.link(tgt)
tgt.parent = cam1
for t, loc in ((0, (0.25, -0.75, -0.3)), (PING - 0.2, (0.25, -0.75, -0.3)), (PING + 0.3, (0.03, -0.13, -0.31)), (6.9, (0.03, -0.13, -0.31)),
               (7.4, (0.08, -0.12, -0.34)), (9.6, (0.08, -0.12, -0.34)), (10.1, (0.25, -0.75, -0.3))):
    tgt.location = loc
    tgt.keyframe_insert("location", frame=T(t) if t else 1)
c = a.pose.bones["forearm.R"].constraints.new("IK")
c.target = tgt
c.chain_count = 2
skin = bpy.data.materials["me_skin"]


def phone_with_grip(name, screens):
    """Handy + rechte Greif-Hand; screens: [(t, Datei)]"""
    g = LR.group(name)
    LR.box(name + "_body", (0, 0, 0), (0.072, 0.0095, 0.15), LR.soft("phonebody", (0.16, 0.17, 0.2), shade=0.7), bevel=0.004).parent = g
    m = bpy.data.materials.new(name + "_scr")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    prev = None
    mixes = []
    for i, (tt, fn) in enumerate(screens):
        tx = nt.nodes.new("ShaderNodeTexImage")
        tx.image = bpy.data.images.load(os.path.join(HERE, "tex", fn) if os.path.exists(os.path.join(HERE, "tex", fn)) else os.path.join(HERE, "..", "futaba", "tex", fn), check_existing=True)
        if prev is None:
            prev = tx.outputs[0]
        else:
            mx = nt.nodes.new("ShaderNodeMix")
            mx.data_type = "RGBA"
            nt.links.new(prev, mx.inputs[6])
            nt.links.new(tx.outputs[0], mx.inputs[7])
            prev = mx.outputs[2]
            mixes.append((tt, mx))
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[1].default_value = 1.1
    nt.links.new(prev, em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    for tt, mx in mixes:
        mx.inputs[0].default_value = 0.0
        mx.inputs[0].keyframe_insert("default_value", frame=1)
        mx.inputs[0].keyframe_insert("default_value", frame=T(tt) - 1)
        mx.inputs[0].default_value = 1.0
        mx.inputs[0].keyframe_insert("default_value", frame=T(tt))
    m["toon"] = 1
    LR.uvplane(name + "_screen", (0, -0.0056, 0), 0.064, 0.135, m, (math.radians(90), 0, 0)).parent = g
    # Hand: Handfläche hinten, vier Fingerkuppen an der linken Kante, Daumen rechts
    F.ellipsoid(name + "_palm", Vector((0.006, 0.026, -0.03)), (0.045, 0.018, 0.055), skin, seg=20, rings=12).parent = g
    for k in range(4):
        z = 0.03 - k * 0.022
        fl = F.curve_line(f"{name}_f{k}", [(0.03, 0.022, z), (-0.03, 0.02, z), (-0.044, 0.006, z), (-0.042, -0.008, z + 0.002)], 0.0078 - 0.0005 * k, skin)
        fl.parent = g
        F.ellipsoid(f"{name}_ft{k}", Vector((-0.042, -0.009, z + 0.002)), (0.0078, 0.0078, 0.0078), skin, seg=10, rings=6).parent = g
    th = F.curve_line(name + "_th", [(0.04, 0.02, -0.05), (0.048, 0.002, -0.02), (0.044, -0.008, 0.005)], 0.0098, skin)
    th.parent = g
    F.ellipsoid(name + "_tht", Vector((0.044, -0.009, 0.006)), (0.0098, 0.0098, 0.0098), skin, seg=10, rings=6).parent = g
    return g


ph1 = phone_with_grip("ph1", [(0, "phone_papa.png"), (EEW, "phone_eew.png")])
ph1.parent = tgt
ph1.location = (0.0, 0.0, 0.02)
ph1.rotation_euler = (math.radians(-76), 0, 0)
vis(ph1, [(0, False), (PING - 0.1, True), (10.0, False)])
for o_ in me["parts"].get("hand.R", []):
    vis(o_, [(0, False)])

cam2 = make_cam("cam2")
CAM2 = 11.4
sc.frame_set(T(CAM2))
bpy.context.view_layer.update()
start = cam1.matrix_world.copy()
_prev = [None]


def key_cam(t, pos, look):
    cam2.location = pos
    e = (Vector(look) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    if _prev[0] is not None:
        for i in range(3):
            while e[i] - _prev[0][i] > math.pi:
                e[i] -= 2 * math.pi
            while e[i] - _prev[0][i] < -math.pi:
                e[i] += 2 * math.pi
    _prev[0] = e.copy()
    cam2.rotation_euler = e
    cam2.keyframe_insert("location", frame=T(t))
    cam2.keyframe_insert("rotation_euler", frame=T(t))


p0 = start.to_translation()
key_cam(0, (-0.55, 1.75, 1.36), (-1.15, 4.4, 0.9))      # Hook: Fenster, Welle
key_cam(HOOK - 0.05, (-0.7, 2.0, 1.36), (-1.2, 4.4, 0.9))
key_cam(CAM2, p0, p0 + start.to_3x3() @ Vector((0, 0, -1)))
key_cam(12.0, (0.32, 0.42, 0.2), (-1.6, 0.8, 0.34))      # unter dem Tisch
key_cam(16.0, (0.32, 0.44, 0.2), (-1.6, 1.3, 0.36))
key_cam(17.8, (0.32, 0.44, 0.2), (-1.2, 2.6, 0.6))       # zum Fenster
key_cam(19.4, (0.32, 0.42, 0.2), (-1.6, 0.7, 0.3))       # zu Hana
key_cam(QEND, (0.32, 0.42, 0.2), (-1.6, 0.7, 0.3))
key_cam(25.6, (0.08, -0.2, 0.5), (0.2, 2.8, 0.7))
key_cam(26.9, (0.2, -0.45, 1.42), (0.15, 1.0, 0.6))      # aufstehen, aufs Handy schauen
key_cam(30.4, (0.2, -0.45, 1.42), (0.15, 1.0, 0.6))
key_cam(31.2, (0.2, -0.45, 1.42), (1.1, 2.55, 0.9))      # TV: Tsunami-Warnung
key_cam(33.0, (0.2, -0.45, 1.42), (1.1, 2.55, 0.9))
key_cam(33.9, (0.2, -0.4, 1.42), (1.4, -2.5, 1.2))       # Mama kommt
key_cam(38.0, (0.2, -0.4, 1.42), (1.15, -1.5, 1.35))
key_cam(39.2, (0.2, -0.4, 1.42), (1.1, 2.55, 0.9))       # Strom weg
key_cam(40.6, (0.05, -0.95, 1.36), (-1.15, 2.8, 1.05))   # Fenster: Durchsage
key_cam(44.4, (-0.05, -0.85, 1.36), (-1.2, 2.8, 1.1))
key_cam(45.2, (0.0, -0.8, 1.34), (-0.75, 0.05, 1.0))     # Hana: „Und Papa?“
key_cam(T2, (-0.15, -0.6, 1.3), (-0.75, 0.05, 1.0))
key_cam(T2 + 1.1, (-0.55, 1.55, 1.36), (-1.1, 4.4, 0.95))  # 15:27 Fenster
key_cam(51.1, (-0.6, 1.7, 1.36), (-1.15, 4.4, 0.95))
key_cam(51.8, (-0.62, 1.72, 1.36), (-1.6, 2.35, 1.15))
key_cam(53.6, (-0.62, 1.75, 1.36), (-1.6, 2.35, 1.15))
key_cam(54.3, (-0.75, 2.05, 1.36), (-1.2, 4.4, 0.9))
key_cam(55.4, (-0.8, 2.2, 1.36), (-1.2, 4.4, 0.9))
key_cam(56.1, (-0.7, 2.0, 1.38), (0.35, 0.9, 1.35))      # Mama
key_cam(RUN, (-0.6, 1.8, 1.38), (0.6, 0.3, 1.3))
key_cam(RUN + 0.7, (0.6, -0.9, 1.38), (1.6, -2.6, 1.3))  # rennen zur Küchentür
key_cam(RUN + 1.3, (1.55, -2.4, 1.4), (1.2, -3.6, 1.6))  # durch die Tür, Treppe
yv = lambda i: sy - i * ru
key_cam(RUN + 2.0, (1.18, yv(1.5), 1.45 + 1.5 * rr), (1.18, yv(6), 1.6 + 6 * rr))
key_cam(RUN + 2.4, (1.18, yv(3), 1.45 + 3 * rr), (1.3, yv(-1), 1.1))  # kurz zurück zu Hana
key_cam(RUN + 2.9, (1.18, yv(4.5), 1.45 + 4.5 * rr), (1.2, yv(0), 1.1))
key_cam(RUN + 3.3, (1.18, yv(6), 1.45 + 6 * rr), (1.18, yv(11), 1.6 + 11 * rr))
key_cam(UP - 0.2, (1.18, yv(10), 1.45 + 10 * rr), (1.18, yv(14), 1.6 + 14 * rr))
key_cam(UP, (O.x + 0.2, O.y - 0.6, FZ + 1.45), (O.x + 0.0, O.y + 9, 0.8))   # oben: Fenster, Flut
key_cam(64.4, (O.x + 0.15, O.y + 0.3, FZ + 1.45), (O.x - 0.6, O.y + 9, 0.6))
key_cam(65.2, (O.x + 0.15, O.y + 0.4, FZ + 1.42), (O.x - 0.55, O.y + 0.9, FZ + 1.0))  # zu Hana
key_cam(66.6, (O.x + 0.15, O.y + 0.45, FZ + 1.42), (O.x - 0.55, O.y + 0.9, FZ + 1.0))
key_cam(END, (O.x + 0.2, O.y + 0.6, FZ + 1.45), (O.x + 1.0, O.y + 12, 1.4))     # Blick in die Ferne (Kraftwerk)
# Schnitte ohne Kamerafahrt: konstante Interpolation an Schnittstellen
ad = cam2.animation_data.action
fcs = ad.fcurves if hasattr(ad, "fcurves") else [fc for l in ad.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]
for fc in fcs:
    for kp in fc.keyframe_points:
        tt = (kp.co[0] - 1) / FPS
        if abs(tt - (HOOK - 0.05)) < 0.03 or abs(tt - T2) < 0.03 or abs(tt - (UP - 0.2)) < 0.03:
            kp.interpolation = "CONSTANT"
sc.camera = cam2
for nm, t, c_ in (("c0", 0, cam2), ("c1", HOOK, cam1), ("c2", CAM2, cam2)):
    mk = sc.timeline_markers.new(nm, frame=T(t) if t else 1)
    mk.camera = c_
# Handkamera überall + Beben + Rennen
for fr in range(1, T(END) + 1, 2):
    t = (fr - 1) / FPS
    am = qamp(t)
    run = 1.0 if RUN + 0.4 < t < UP - 0.2 else 0.0
    base = 0.55
    rx = base * math.sin(t * 1.3) + 0.35 * math.sin(t * 2.9 + 1) + 2.8 * am * math.sin(t * 31) + 3.0 * run * math.sin(t * 15)
    ry = base * 0.8 * math.sin(t * 0.9 + 2) + 2.0 * am * math.sin(t * 27 + 1) + 1.5 * run * math.sin(t * 7.5)
    rz = 0.3 * math.sin(t * 0.7) + 2.4 * am * math.sin(t * 21)
    cam2.delta_rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))
    cam2.delta_location = (0.02 * am * math.sin(t * 37), 0.016 * am * math.sin(t * 33), 0.012 * math.sin(t * 2.2) + 0.014 * am * math.sin(t * 41) + 0.05 * run * abs(math.sin(t * 7.5)))
    cam2.keyframe_insert("delta_rotation_euler", frame=fr)
    cam2.keyframe_insert("delta_location", frame=fr)

# Meine Hände an Kamera 2: (1) Hana am Arm packen 10.4–11.6 wird von Kamera 1 gezeigt (IK links), (2) unter dem Tisch Hand reichen,
# (3) Handy „Kein Netz“, (4) Hand am Geländer
def my_hand(name):
    g = LR.group(name)
    g.parent = cam2
    jm = bpy.data.materials["me_jacket"]
    F.limb(name + "_sl", Vector((0, -0.02, 0.16)), Vector((0, 0, 0.02)), 0.042, 0.038, jm, seg=16).parent = g
    F.ellipsoid(name + "_pa", Vector((0, 0, -0.03)), (0.04, 0.016, 0.045), skin, seg=18, rings=10).parent = g
    for k in range(4):
        fx = -0.026 + k * 0.017
        F.limb(f"{name}_f{k}", Vector((fx, 0, -0.065)), Vector((fx * 1.1, -0.012, -0.115 + abs(k - 1.5) * 0.008)), 0.008, 0.007, skin, seg=10, subsurf=0).parent = g
        F.ellipsoid(f"{name}_ft{k}", Vector((fx * 1.1, -0.012, -0.115 + abs(k - 1.5) * 0.008)), (0.007, 0.007, 0.007), skin, seg=10, rings=6).parent = g
    F.limb(name + "_th", Vector((0.04, 0, -0.035)), Vector((0.06, -0.01, -0.075)), 0.009, 0.008, skin, seg=10, subsurf=0).parent = g
    return g


h_reach = my_hand("reach")
for t, loc, rx in ((19.6, (0.32, -0.55, -0.3), -20), (20.8, (0.07, -0.17, -0.45), -12), (QEND, (0.07, -0.17, -0.45), -12), (25.2, (0.32, -0.55, -0.3), -20)):
    h_reach.location = loc
    h_reach.rotation_euler = (math.radians(rx), math.radians(-25), 0)
    h_reach.keyframe_insert("location", frame=T(t))
    h_reach.keyframe_insert("rotation_euler", frame=T(t))
vis(h_reach, [(0, False), (19.5, True), (25.3, False)])
# Hana am Arm packen (Kamera 1, linke Hand per IK)
tgtL = bpy.data.objects.new("ikL", None)
sc.collection.objects.link(tgtL)
tgtL.parent = cam1
for t, loc in ((0, (-0.2, -0.6, -0.2)), (10.0, (-0.2, -0.6, -0.2)), (10.6, (-0.12, -0.18, -0.55)), (11.2, (-0.15, -0.3, -0.4))):
    tgtL.location = loc
    tgtL.keyframe_insert("location", frame=T(t) if t else 1)
cL = a.pose.bones["forearm.L"].constraints.new("IK")
cL.target = tgtL
cL.chain_count = 2
for t, v in ((0, 0.0), (9.9, 0.0), (10.4, 1.0), (11.4, 1.0)):
    cL.influence = v
    cL.keyframe_insert("influence", frame=T(t) if t else 1)
# Handy 2: Papa anrufen → kein Netz (an Kamera 2)
ph2 = phone_with_grip("ph2", [(0, "phone_nosignal.png")])
ph2.parent = cam2
sl2 = F.limb("ph2_sleeve", Vector((0.05, 0.05, -0.24)), Vector((0.012, 0.03, -0.05)), 0.042, 0.038, bpy.data.materials["me_jacket"], seg=16)
sl2.parent = ph2
for t, loc in ((CALL - 0.4, (0.25, -0.6, -0.3)), (CALL + 0.2, (0.03, -0.12, -0.33)), (30.0, (0.03, -0.12, -0.33)), (30.6, (0.25, -0.6, -0.3))):
    ph2.location = loc
    ph2.rotation_euler = (math.radians(-78), 0, 0)
    ph2.keyframe_insert("location", frame=T(t))
vis(ph2, [(0, False), (CALL - 0.45, True), (30.65, False)])
# Hand am Geländer beim Treppenlaufen
h_rail = my_hand("rail")
for t, loc in ((RUN + 1.6, (0.32, -0.5, -0.2)), (RUN + 2.0, (0.2, -0.16, -0.32)), (UP - 0.25, (0.2, -0.16, -0.32))):
    h_rail.location = loc
    h_rail.rotation_euler = (math.radians(-35), math.radians(-60), 0)
    h_rail.keyframe_insert("location", frame=T(t))
    h_rail.keyframe_insert("rotation_euler", frame=T(t))
vis(h_rail, [(0, False), (RUN + 1.6, True), (UP - 0.2, False)])

# ---------- Beben: Lampe, Kram, fallende Dinge, Mandarinen, Tasse ----------
def wobble(o, amp, freq, k, axes=(0, 1), loc=0.0):
    base_ = o.rotation_euler.copy()
    bl = o.location.copy()
    for fr in range(T(QUAKE) - 2, T(QEND + 2.5) + 1, 2):
        t = (fr - 1) / FPS
        am = qamp(t)
        r_ = base_.copy()
        for ax in axes:
            r_[ax] = base_[ax] + math.radians(amp * am * math.sin(t * freq + k * (1.3 + ax)))
        o.rotation_euler = r_
        o.keyframe_insert("rotation_euler", frame=fr)
        if loc:
            o.location = bl + Vector((loc * am * math.sin(t * 23 + k), loc * am * math.sin(t * 19 + 2 * k), 0))
            o.keyframe_insert("location", frame=fr)


lamp = S["lamp"]
for fr in range(T(QUAKE) - 2, T(T2) + 1, 2):
    t = (fr - 1) / FPS
    am = qamp(t) if t < QEND else max(0.0, math.exp(-(t - QEND) * 0.35)) * 0.8
    lamp.rotation_euler = (math.radians(24 * am * math.sin(t * 3.4)), math.radians(18 * am * math.sin(t * 2.9 + 1)), 0)
    lamp.keyframe_insert("rotation_euler", frame=fr)
for k, o in enumerate(S["swing"]):
    wobble(o, 7.0, 6.0 + k % 3, k)
for k, o in enumerate(S["rattle"]):
    wobble(o, 9.0, 17 + k % 5, k, axes=(0, 1, 2), loc=0.014)
wobble(S["tv"], 3.5, 7.5, 1)
wobble(tb, 1.4, 9.0, 2, axes=(2,), loc=0.018)
EV = {"fall": []}
for k, o in enumerate([o for o in S["falls"] if o.name.startswith("photo")]):
    tf = QUAKE + 1.5 + k * 1.0
    o.keyframe_insert("rotation_euler", frame=T(tf))
    o.rotation_euler.y += math.radians(-80 if k % 2 else 80)
    o.keyframe_insert("rotation_euler", frame=T(tf + 0.35))
    EV["fall"].append(tf + 0.35)
books = [o for o in S["falls"] if o.name.startswith("book")]
R.shuffle(books)
for k, o in enumerate(books[:16]):
    tf = QUAKE + 2.0 + R.uniform(0, 9.0)
    o.keyframe_insert("location", frame=T(tf))
    o.keyframe_insert("rotation_euler", frame=T(tf))
    dur = math.sqrt(2 * max(0.1, o.location.z) / 9.81)
    o.location = (o.location.x - R.uniform(0.25, 0.6), o.location.y + R.uniform(-0.15, 0.15), 0.03)
    o.rotation_euler = (R.uniform(-1.5, 1.5), math.radians(90) * R.choice((-1, 1)), R.uniform(-0.5, 0.5))
    o.keyframe_insert("location", frame=T(tf + dur))
    o.keyframe_insert("rotation_euler", frame=T(tf + dur))
    EV["fall"].append(tf + dur)
for o in [o for o in S["falls"] if o.name.startswith("randoseru")]:
    o.keyframe_insert("rotation_euler", frame=T(QUAKE + 3.0))
    o.rotation_euler.x += math.radians(85)
    o.keyframe_insert("rotation_euler", frame=T(QUAKE + 3.4))
    EV["fall"].append(QUAKE + 3.4)
mk_ = LR.soft("mikan2", (0.95, 0.56, 0.12))
for k, (x0, t0, x1, y1) in enumerate(((0.05, 14.0, -0.25, 0.22), (0.15, 14.8, 0.02, 0.18), (-0.1, 16.4, -0.45, 0.3), (0.25, 17.6, 0.12, 0.28))):
    o = F.ellipsoid(f"rollmikan{k}", Vector((x0, 0.06, 0.5)), (0.038, 0.038, 0.034), mk_, seg=16, rings=10)
    o.keyframe_insert("location", frame=T(t0))
    o.keyframe_insert("rotation_euler", frame=T(t0))
    o.location = (x0 - 0.02, -0.02, 0.04)
    o.keyframe_insert("location", frame=T(t0 + 0.32))
    o.location = (x1, y1, 0.04)
    o.rotation_euler = (R.uniform(4, 9), R.uniform(4, 9), 0)
    o.keyframe_insert("location", frame=T(t0 + 1.9))
    o.keyframe_insert("rotation_euler", frame=T(t0 + 1.9))
    EV["fall"].append(t0 + 0.32)
cup2 = LR.cyl("fallcup", (-0.3, 0.08, 0.5), 0.035, 0.08, LR.soft("cupm2", (0.82, 0.86, 0.8)), verts=16, r2=0.04)
for t, loc, rr_ in ((18.0, (-0.3, 0.08, 0.5), (0, 0, 0)), (18.35, (-0.36, -0.05, 0.04), (90, 0, 30)), (19.0, (-0.42, -0.02, 0.04), (90, 0, 70))):
    cup2.location = loc
    cup2.rotation_euler = tuple(math.radians(v) for v in rr_)
    cup2.keyframe_insert("location", frame=T(t))
    cup2.keyframe_insert("rotation_euler", frame=T(t))
EV["fall"].append(18.35)
EV["kettle"] = QUAKE + 5.0
json.dump(EV, open(os.path.join(ROOT, "src", "futaba4", "events.json"), "w"), indent=1)

# ---------- Strom weg ----------
for L in S["lights"] + [S["kitchenlight"]]:
    e0 = L.data.energy
    for t, k in ((0, 0.25), (HOOK - 0.05, 0.25), (HOOK, 1.0), (QUAKE + 3.0, 1.0), (QUAKE + 3.1, 0.3), (QUAKE + 3.25, 1.0), (QUAKE + 8.0, 0.3), (QUAKE + 8.1, 1.0), (POWER - 0.05, 1.0),
                 (POWER, 0.25 if L.name != "kitchenlight" else 0.0)):
        L.data.energy = e0 * k
        L.data.keyframe_insert("energy", frame=T(t) if t else 1)

# ---------- Welle vor dem Fenster (Hook + 15:27) ----------
def alpha_mat(name, file, emit=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(os.path.join(HERE, "tex", file), check_existing=True)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[1].default_value = emit
    nt.links.new(tx.outputs[0], em.inputs[0])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tx.outputs[1], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    m["toon"] = 1
    return m


WM = alpha_mat("wavem", "wave.png", 0.95)
WX = (-2.05 - 0.25) / 2
for k, (yy, w, h, z0, z1, x0, x1, t0) in enumerate(((LR.Y1 + 1.5, 7.0, 2.9, -0.75, 0.3, -1.8, -0.9, 51.0), (LR.Y1 + 1.3, 7.0, 2.6, -0.95, 0.12, -2.3, -1.2, 52.2))):
    wv = LR.uvplane(f"wave{k}", (WX, yy, z0), w, h, WM, (math.radians(90), 0, 0))
    for t, z, x in ((0, z1 - 0.1, x1 - 0.3), (HOOK, z1, x1), (HOOK + 0.05, -3.0, x0), (T2, z0, x0), (t0, z0, x0), (54.5, (z0 + z1) / 2 + 0.15, (x0 + x1) / 2), (RUN, z1, x1)):
        wv.location = (WX + x, yy, z)
        wv.keyframe_insert("location", frame=T(t) if t else 1)
    for fc in (wv.animation_data.action.fcurves if hasattr(wv.animation_data.action, "fcurves") else []):
        for kp in fc.keyframe_points:
            if abs((kp.co[0] - 1) / FPS - HOOK) < 0.03:
                kp.interpolation = "CONSTANT"

# ---------- Oben: Flut auf der Straße ----------
wm, mp = UPS["water_mat"]("floodm", [(T(UP), 0.0), (T(END), 1.2)])
water = LR.box("flood", (O.x, O.y + 12, 1.0), (70, 26, 0.05), wm)
for t, z in ((UP, 1.1), (END, 1.65)):
    water.location.z = z
    water.keyframe_insert("location", frame=T(t))
import street as ST
car = ST.S if False else None
carg = LR.group("floatcar")
cm = LR.soft("floatcarm", (0.92, 0.92, 0.9))
LR.box("fc_body", (0, 0, 0.4), (1.4, 3.2, 0.7), cm, bevel=0.1, parent=carg)
LR.box("fc_cab", (0, 0.25, 0.95), (1.3, 2.0, 0.55), cm, bevel=0.08, parent=carg)
LR.box("fc_glass", (0, 0.25, 0.97), (1.33, 1.8, 0.4), LR.soft("glassout", (0.6, 0.72, 0.82)), bevel=0.05, parent=carg)
for t, x, z, rz in ((UP, O.x - 9, 0.6, 0.3), (END, O.x + 1.5, 1.05, 0.9)):
    carg.location = (x, O.y + 7.5, z)
    carg.rotation_euler = (math.radians(6), math.radians(-8), rz)
    carg.keyframe_insert("location", frame=T(t))
    carg.keyframe_insert("rotation_euler", frame=T(t))
debm = LR.soft("debris", (0.5, 0.36, 0.24))
for k in range(12):
    d = LR.box(f"fdebris{k}", (0, 0, 0), (R.uniform(0.4, 1.4), 0.12, R.uniform(0.05, 0.2)), debm if k % 3 else LR.soft("debroof", (0.35, 0.38, 0.46)))
    y = O.y + R.uniform(4.5, 9.5)
    for t, u in ((UP, 0.0), (END, 1.0)):
        d.location = (O.x - 12 + k * 1.8 + u * R.uniform(3, 6), y, 1.1 + u * 0.55 + 0.05)
        d.rotation_euler = (0, 0, R.uniform(-1, 1) + u)
        d.keyframe_insert("location", frame=T(t))
        d.keyframe_insert("rotation_euler", frame=T(t))

upl = bpy.data.objects.new("uplight", bpy.data.lights.new("uplight", "AREA"))
sc.collection.objects.link(upl)
upl.data.energy = 120
upl.data.size = 2.5
upl.location = (O.x, O.y, FZ + 2.3)

# ---------- Render ----------
import toonlib as TL
arms = {me["arm"]: "me", hana["arm"]: "hana", mama["arm"]: "mama"}
idx = {}
nxt = [1]
for o in bpy.data.objects:
    q, owner = o, None
    while q is not None:
        if q in arms:
            owner = arms[q]
            break
        q = q.parent
    if owner and o.type in ("MESH", "CURVE") and o.data.materials:
        # gleiche Figur + gleiches Material -> gleiche ID: keine Linien zwischen Körperteilen (keine Gliederpuppe)
        key = (owner, o.data.materials[0].name)
        if key not in idx:
            idx[key] = 10000 + len(idx)
        o.pass_index = idx[key]
    else:
        o.pass_index = nxt[0]
        nxt[0] += 1
TL.comp_outlines(kn=1.0, kd=0.5, thr=0.7, fade_near=4.0, fade_far=9.0)
for f_ in (me, hana, mama):
    head_o = bpy.data.objects[f_["name"] + "_head"]
    for o in bpy.data.objects:
        if o.name.startswith(f_["name"] + "_") and any(k in o.name for k in ("_white", "_iris", "_pupil", "_glint")):
            o.pass_index = head_o.pass_index
for m in bpy.data.materials:
    if m.name.endswith("_skin") or m.name in ("eyewhite", "pupil") or m.name.endswith("_iris"):
        for n in m.node_tree.nodes:
            if n.type == "COMBXYZ":
                n.inputs[0].default_value = 9999.0
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = int(os.environ.get("SAMPLES", 10))
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, T(END)
pct = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 75
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, pct
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGB"
sc.render.use_overwrite = False
sc.render.filepath = sys.argv[-2] if sys.argv[-1].isdigit() else "/tmp/f4_"
