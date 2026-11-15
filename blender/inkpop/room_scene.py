# „Futaba, 11. März 2011, 14:45“ – Wohnzimmer, Ich-Sicht. Tee auf dem Sofa, Schwester Hana spielt, Fernseher;
# 14:46 Erdbeben-Frühwarnung, Beben (unter den Tisch), Tsunami-Warnung, Mama kommt, Strom weg, Durchsage, „Und Papa?“.
# blender -b --python room_scene.py -a -- <ausgabe_präfix> <prozent>
import bpy, sys, os, math, random, json
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "futaba"))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
import figure as F, cast as C, livingroom as LR

sc = bpy.context.scene
FPS = 24
T = lambda s: int(round(s * FPS)) + 1
R = random.Random(9)
AT = {"tv1": 0.6, "h1": 4.4, "m1": 7.3, "ma1": 9.0, "h2": 10.9, "tv2": 12.6, "h3": 13.9, "m2": 16.4, "h4": 22.5, "m3": 26.5,
      "tv3": 35.2, "ma2": 40.6, "lsp": 45.0, "h5": 50.0, "m4": 51.1, "h6": 57.4, "m5": 60.0, "ma3": 61.7}
EEW, QUAKE, QEND, CAM2, UNDER, OUT, MAMA, POWER, END = 12.0, 15.8, 33.0, 17.6, 19.2, 35.0, 37.0, 43.8, 55.5
T2, END2 = 55.5, 65.0  # 15:27 – die Welle kommt (Fenster)
json.dump(dict(AT=AT, EEW=EEW, QUAKE=QUAKE, QEND=QEND, POWER=POWER, END=END, T2=T2, END2=END2, FPS=FPS, CAM2=CAM2),
          open(os.path.join(ROOT, "src", "futaba3", "timeline.json"), "w"), indent=1)
TIM = json.load(open(os.path.join(ROOT, "src", "futaba3", "timing.json")))
SCR = json.load(open(os.path.join(ROOT, "src", "futaba3", "script.json")))
WAV = {s["id"]: os.path.join(ROOT, "public", l["file"]) for s, l in zip(SCR["sentences"], TIM["lines"])}


def qamp(t):
    if t < QUAKE or t > QEND + 1.5:
        return 0.0
    a = min(1.0, (t - QUAKE) / 1.2) * min(1.0, max(0.0, (QEND + 1.5 - t) / 2.5))
    return a * (0.8 + 0.2 * math.sin(t * 1.3))


S = LR.build()
LR.tv_material(S["screens"]["tv"], [(1, "tv_news.png"), (T(EEW), "tv_eew.png"), (T(34.6), "tv_tsunami.png"), (T(POWER), "off")])
tb = S["table"]
tb.scale.z = 1.16  # etwas höherer Tisch, damit man darunter passt
bpy.data.objects["tb_shelf"].hide_render = True

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


def head(f, keys, w=(0.45, 0.55)):
    for t, yaw, pitch in keys:
        rot(f, "neck", t, y=yaw * w[0], x=-pitch * 0.4)
        rot(f, "head", t, y=yaw * w[1], x=-pitch * 0.6)


def heading(d):
    return math.atan2(d.x, -d.y)


def place(f, t, loc, yaw):
    a = f["arm"]
    a.location = loc
    a.rotation_euler = (0, 0, yaw)
    a.keyframe_insert("location", frame=T(t))
    a.keyframe_insert("rotation_euler", frame=T(t))


def idle(f, t0, t1, seed, amp=1.0):
    r = random.Random(seed)
    ph = [r.uniform(0, 6.3) for _ in range(3)]
    for fr in range(T(t0), T(t1), 8):
        t = fr / FPS
        F.rot(f, "chest", fr, x=amp * 1.4 * math.sin(t * 2 * math.pi / 3.6 + ph[0]), y=amp * 1.6 * math.sin(t * 0.7 + ph[1]),
              z=amp * 0.8 * math.sin(t * 0.9 + ph[2]))


# --- ich: sitze auf dem Sofa mit Tee ---
a = me["arm"]
place(me, 0, (0.25, -1.92, -0.44), math.pi)
for sd in ("L", "R"):
    rot(me, f"thigh.{sd}", 0, x=-88, z=(-6 if sd == "L" else 6))
    rot(me, f"shin.{sd}", 0, x=88)
rot(me, "upperarm.L", 0, x=-28, z=-10)
rot(me, "forearm.L", 0, x=-40)
idle(me, 0, CAM2, 1, amp=0.6)
# Blick (gier + = links, nick + = hoch) – Rumpf/Hals/Kopf
for t, yaw, pitch in ((0, 0, -4), (3.9, 2, -4), (4.6, 34, -14), (7.0, 30, -12), (7.9, 6, -4), (8.9, -28, 2), (10.4, -22, 2), (11.0, 30, -12),
                      (12.1, 4, -2), (13.6, 32, -10), (15.0, 8, -2), (15.8, 6, 2), (16.6, 24, -16), (CAM2, 24, -20)):
    rot(me, "spine", t, y=yaw * 0.2, x=-pitch * 0.1)
    rot(me, "neck", t, y=yaw * 0.4, x=2 - pitch * 0.35)
    rot(me, "head", t, y=yaw * 0.4, x=2 - pitch * 0.45)
vis = lambda o, keys: [(setattr(ob, "hide_render", not v), ob.keyframe_insert("hide_render", frame=T(t) if t else 1)) for ob in [o] + list(o.children_recursive) for t, v in keys]
for o in [x for x in bpy.data.objects if x.parent == a]:
    if o not in me["head_parts"]:
        vis(o, [(0, True), (CAM2, False)])

# --- Hana ---
HK = (-0.95, 0.5)
place(hana, 0, (HK[0], HK[1], -0.47), math.radians(-60))
for sd in ("L", "R"):
    rot(hana, f"thigh.{sd}", 0, x=-92, z=(-8 if sd == "L" else 8))
    rot(hana, f"shin.{sd}", 0, x=165)
    rot(hana, f"upperarm.{sd}", 0, x=-35, z=(10 if sd == "L" else -10))
    rot(hana, f"forearm.{sd}", 0, x=-75)
rot(hana, "spine", 0, x=10)
idle(hana, 0, END, 7)
ds = LR.group("ds")
F.bone_parent(ds, hana["arm"], "hand.R")
ds.matrix_parent_inverse = Matrix()
ds.location = (0.07, 0.04, 0.0)
LR.box("dsbot", (0, 0, 0), (0.13, 0.075, 0.018), LR.soft("dsm", (0.95, 0.95, 0.97)), parent=ds)
dsl = LR.box("dsscr", (0, 0, 0.0095), (0.1, 0.055, 0.002), F.flat_mat("dsglow", (0.6, 0.85, 1.0)), parent=ds)
vis(ds, [(0, True), (16.0, False)])
head(hana, [(0, 0, -25), (4.2, 0, -25), (4.6, -40, 5), (7.4, -38, 5), (8.0, 0, -25), (10.6, -50, 15), (11.6, 0, -25), (12.3, 20, 5),
            (13.7, -45, 2), (15.5, -45, 2)])
F.look(hana, T(4.6), -15, 0)
F.look(hana, T(8.0), 0, -20)
F.look(hana, T(12.3), 10, 5)
F.look(hana, T(13.7), -20, 0)
F.brows(hana, T(4.4), 0.5)
F.brows(hana, T(8.0), 0.0)
F.brows(hana, T(12.4), 0.8, 0.3)
F.brows(hana, T(13.8), 1.0, 1.0)
# unter den Tisch (16,0–17,6): kniet, Oberkörper flach, Arme über dem Kopf, schaut zu mir (Kamera unter dem Tisch)
# Unter dem Tisch: Hana liegt bäuchlings, Kopf zu mir (Kamera), stützt sich auf die Unterarme – Gesicht sichtbar
CAMU = Vector((0.32, 0.42, 0))
dirc = Vector((-1.6, 0.8, 0)) - CAMU
dirc.normalize()
HEADU = CAMU + dirc * 0.62
face_d = -dirc
yaw_u = heading(face_d)
ROOTU = HEADU - face_d * (1.18 * 0.92)


def place_r(f, t, loc, rx, yaw):
    a_ = f["arm"]
    a_.location = loc
    a_.rotation_euler = (rx, 0, yaw)
    a_.keyframe_insert("location", frame=T(t))
    a_.keyframe_insert("rotation_euler", frame=T(t))


place_r(hana, 16.0, (HK[0], HK[1], -0.47), 0.0, math.radians(-60))
_pre = ROOTU - face_d * 0.75
place_r(hana, 16.8, (_pre.x, _pre.y, 0.06), math.radians(84), yaw_u)
place_r(hana, 17.6, (ROOTU.x, ROOTU.y, 0.05), math.radians(84), yaw_u)
for sd in ("L", "R"):
    rot(hana, f"thigh.{sd}", 16.0, x=-92, z=(-8 if sd == "L" else 8))
    rot(hana, f"shin.{sd}", 16.0, x=165)
    rot(hana, f"thigh.{sd}", 17.4, x=4, z=(-4 if sd == "L" else 4))
    rot(hana, f"shin.{sd}", 17.4, x=25)
    rot(hana, f"upperarm.{sd}", 16.0, x=-35, z=(10 if sd == "L" else -10))
    rot(hana, f"upperarm.{sd}", 17.4, x=-95, z=(-14 if sd == "L" else 14))
    rot(hana, f"forearm.{sd}", 17.4, x=-70)
rot(hana, "spine", 16.0, x=10)
rot(hana, "spine", 17.4, x=-16)
head(hana, [(16.8, 0, 30), (17.6, 0, 52), (QEND, 0, 52)])
# Hana zittert, rutscht näher, streckt mir die Hand entgegen
for fr in range(T(17.6), T(QEND), 2):
    t = (fr - 1) / FPS
    am = qamp(t)
    F.rot(hana, "chest", fr, x=1.5 * am * math.sin(t * 37), y=2.5 * am * math.sin(t * 29 + 1), z=2.0 * am * math.sin(t * 23))
rot(hana, "upperarm.R", 28.4, x=-95, z=14)
rot(hana, "forearm.R", 28.4, x=-70)
rot(hana, "upperarm.R", 29.4, x=-150, z=6)
rot(hana, "forearm.R", 29.4, x=-12)
rot(hana, "upperarm.R", QEND, x=-150, z=6)
rot(hana, "forearm.R", QEND, x=-12)
F.brows(hana, T(28.6), 1.0, 1.0)
F.look(hana, T(17.4), 0, 6)
F.brows(hana, T(17.6), 0.8, 1.0)
for o in [o for o in bpy.data.objects if o.name.startswith(("hana_hairside", "hana_hairback"))]:
    vis(o, [(0, True), (17.0, False), (OUT - 0.4, True)])
blinks = (2.0, 6.0, 9.5, 18.6, 21.0, 24.6, 28.2, 31.5, 38.2, 42.0, 47.0, 52.6)
for t in blinks:
    F.blink(hana, T(t))
F.brows(hana, T(QEND), 1.0, 1.0)
# wieder hoch (33,5–35,5), steht neben dem Tisch, Angst
place_r(hana, OUT - 1.2, (ROOTU.x, ROOTU.y, 0.05), math.radians(84), yaw_u)
place_r(hana, OUT - 0.4, (_pre.x, _pre.y, 0.06), math.radians(84), yaw_u)
STAND = (-0.75, 0.05)
_ys = heading(Vector((0.2, -0.6, 0)) - Vector((STAND[0], STAND[1], 0)))
while _ys - yaw_u > math.pi:
    _ys -= 2 * math.pi
while _ys - yaw_u < -math.pi:
    _ys += 2 * math.pi
place_r(hana, OUT + 0.6, (STAND[0], STAND[1], 0.0), 0.0, _ys)
for sd in ("L", "R"):
    rot(hana, f"thigh.{sd}", OUT - 1.2, x=4, z=(-4 if sd == "L" else 4))
    rot(hana, f"shin.{sd}", OUT - 1.2, x=25)
    rot(hana, f"thigh.{sd}", OUT + 0.6, x=-2)
    rot(hana, f"shin.{sd}", OUT + 0.6, x=4)
    rot(hana, f"upperarm.{sd}", OUT - 1.2, x=-95, z=(-14 if sd == "L" else 14))
    rot(hana, f"forearm.{sd}", OUT - 1.2, x=-70)
    rot(hana, f"upperarm.{sd}", OUT + 0.6, x=-20, z=(6 if sd == "L" else -6))
    rot(hana, f"forearm.{sd}", OUT + 0.6, x=-95)  # Hände vor der Brust
rot(hana, "spine", OUT - 1.2, x=-16)
rot(hana, "spine", OUT + 0.6, x=4)
head(hana, [(QEND, 0, 52), (OUT + 0.6, 0, 0), (36.0, 30, 10), (37.4, -70, 5), (41.0, -70, 5), (42.4, 20, 10), (44.6, 40, 5), (48.4, 40, 5),
            (49.6, 0, 18), (END, 0, 18)])
F.look(hana, T(OUT + 0.6), 0, 0)
F.look(hana, T(37.4), -20, 0)
F.look(hana, T(49.6), 0, 12)

# --- Mama kommt aus der Küche ---
place(mama, 0, (1.6, LR.Y0 - 1.2, 0), heading(Vector((0, 1, 0))))
place(mama, MAMA, (1.6, LR.Y0 - 1.2, 0), heading(Vector((0, 1, 0))))
idle(mama, 0, END, 3)
# Gehen: einfache Schritte
path = [(MAMA, (1.6, LR.Y0 - 1.2)), (MAMA + 1.0, (1.6, LR.Y0 + 0.2)), (MAMA + 2.0, (1.15, -1.45))]
for (t0, p0), (t1, p1) in zip(path, path[1:]):
    n = int((t1 - t0) * FPS / 2)
    for i in range(n + 1):
        u = i / n
        t = t0 + u * (t1 - t0)
        x = p0[0] + (p1[0] - p0[0]) * u
        y = p0[1] + (p1[1] - p0[1]) * u
        ph = 2 * math.pi * (t - MAMA) / 0.9
        mama["arm"].location = (x, y, 0.012 * math.cos(2 * ph))
        mama["arm"].keyframe_insert("location", frame=T(t))
        for sd, sg in (("L", 1), ("R", -1)):
            rot(mama, f"thigh.{sd}", t, x=-22 * math.sin(ph) * sg)
            rot(mama, f"shin.{sd}", t, x=4 + 40 * max(0, math.cos(ph) * sg) ** 1.5)
            rot(mama, f"upperarm.{sd}", t, x=16 * math.sin(ph) * sg)
mama["arm"].rotation_euler = (0, 0, heading(Vector((-0.6, 1.0, 0))) + 2 * math.pi)
mama["arm"].keyframe_insert("rotation_euler", frame=T(MAMA + 2.0))
for sd in ("L", "R"):
    rot(mama, f"thigh.{sd}", MAMA + 2.3)
    rot(mama, f"shin.{sd}", MAMA + 2.3, x=4)
# Gestik beim Rufen, dann Hand zur Brust; zum Fenster schauen bei der Durchsage
rot(mama, "upperarm.R", 40.3, x=0, z=6)
rot(mama, "upperarm.R", 40.9, x=-70, z=-25)
rot(mama, "forearm.R", 40.9, x=-40)
rot(mama, "upperarm.R", 43.0, x=-70, z=-25)
rot(mama, "upperarm.R", 43.6, x=-25, z=0)
rot(mama, "forearm.R", 43.6, x=-95)
head(mama, [(MAMA, 0, 0), (MAMA + 2.2, 15, -5), (40.4, 20, 0), (44.6, 60, 8), (48.4, 60, 8), (49.6, 25, -10), (END, 25, -10)])
F.brows(mama, T(MAMA + 1.5), 1.0, 1.0)
F.look(mama, T(MAMA + 2.2), 10, -5)
for t in (39.0, 42.8, 47.5, 52.0):
    F.blink(mama, T(t))
for sid, f in (("h1", hana), ("h2", hana), ("h3", hana), ("h4", hana), ("h5", hana), ("ma2", mama)):
    F.lipsync(f, WAV[sid], AT[sid], FPS)

# ---------- Kamera 1: an meinem Kopf (Sofa) ----------
sc.frame_set(1)
bpy.context.view_layer.update()


def make_cam(name):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    sc.collection.objects.link(c)
    c.data.lens = 10.5
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
# Becher in der rechten Hand (IK)
tgt = bpy.data.objects.new("ikR", None)
sc.collection.objects.link(tgt)
tgt.parent = cam1
for t, loc in ((0, (0.07, -0.2, -0.37)), (12.2, (0.07, -0.2, -0.37)), (12.7, (0.09, -0.24, -0.36)), (15.8, (0.09, -0.24, -0.36)), (16.5, (0.25, -0.75, -0.3))):
    tgt.location = loc
    tgt.keyframe_insert("location", frame=T(t) if t else 1)
c = a.pose.bones["forearm.R"].constraints.new("IK")
c.target = tgt
c.chain_count = 2
mug = LR.group("mug")
LR.cyl("mugbody", (0, 0, 0), 0.042, 0.095, LR.soft("mugm", (0.95, 0.94, 0.9)), verts=24).parent = mug
LR.cyl("mugband", (0, 0, 0.01), 0.0425, 0.03, LR.soft("mugb", (0.3, 0.45, 0.72)), verts=24).parent = mug
LR.cyl("tea", (0, 0, 0.0485), 0.035, 0.002, LR.soft("team", (0.5, 0.58, 0.28)), verts=24).parent = mug
bpy.ops.mesh.primitive_torus_add(major_radius=0.026, minor_radius=0.007, location=(0.05, 0, 0.005), rotation=(math.radians(90), 0, 0))
hd = bpy.context.object
hd.data.materials.append(LR.soft("mugm", (0.95, 0.94, 0.9)))
hd.parent = mug
# Becher aufrecht (oben leicht zur Kamera geneigt), Henkel nach links; rechte Hand umgreift den Becher (eigene Greif-Hand)
from mathutils import Matrix as _M
_Z = Vector((0, 0.953, 0.301)).normalized()
_X = Vector((-1, 0, 0))
_Y = _Z.cross(_X)
_Rm = _M((_X, _Y, _Z)).transposed().to_4x4()
mug.parent = tgt
_wrist_local = Vector((-0.062, -0.012, -0.05))
mug.matrix_basis = _M.Translation(-(_Rm.to_3x3() @ _wrist_local)) @ _Rm
skin = bpy.data.materials["me_skin"]
grip = []
for k, (z, r, end) in enumerate(((0.026, 0.0079, 72), (0.0075, 0.0081, 68), (-0.0112, 0.0077, 76), (-0.0292, 0.0067, 96))):
    rr = 0.042 + r * 0.95
    a0, a1 = math.radians(172), math.radians(end)
    pts = [(rr * math.cos(a0 + (a1 - a0) * u), rr * math.sin(a0 + (a1 - a0) * u), z - 0.002 * u) for u in (0, 0.2, 0.4, 0.6, 0.8, 1.0)]
    fl = F.curve_line(f"gripf{k}", pts, r, skin)
    fl.parent = mug
    tip = F.ellipsoid(f"griptip{k}", Vector(pts[-1]), (r, r, r), skin, seg=12, rings=8)
    tip.parent = mug
    nail = F.ellipsoid(f"gripnail{k}", Vector(pts[-1]) + Vector((math.cos(a1), math.sin(a1), 0)) * 0.0045 + Vector((0, 0, 0.0)),
                       (r * 0.55, r * 0.55, r * 0.6), LR.soft("nail", (0.98, 0.88, 0.84), shade=0.85), seg=10, rings=6)
    nail.parent = mug
    kn = F.ellipsoid(f"gripknuckle{k}", Vector((0.056 * math.cos(math.radians(170)), 0.056 * math.sin(math.radians(170)), z)), (0.009, 0.009, r * 1.15), skin, seg=12, rings=8)
    kn.parent = mug
    grip += [fl, tip, nail, kn]
palm = F.ellipsoid("grippalm", Vector((-0.064, 0.004, -0.006)), (0.017, 0.033, 0.047), skin, seg=24, rings=14)
palm.parent = mug
back = F.ellipsoid("gripback", Vector((-0.071, -0.006, -0.012)), (0.012, 0.032, 0.05), skin, seg=24, rings=14)
back.parent = mug
tpts = [(0.051 * math.cos(math.radians(a)), 0.051 * math.sin(math.radians(a)), 0.036 + 0.004 * i) for i, a in enumerate((176, 160, 145, 131))]
th = F.curve_line("gripthumb", tpts, 0.0104, skin)
th.parent = mug
tt = F.ellipsoid("gripthumbtip", Vector(tpts[-1]), (0.0102, 0.0102, 0.0102), skin, seg=12, rings=8)
tt.parent = mug
grip += [palm, back, th, tt]
for o in grip:
    o.parent = mug
vis(mug, [(0, True), (16.3, False)])
for o in me["parts"].get("hand.R", []):
    vis(o, [(0, False), (16.3, True), (CAM2, False)])

# ---------- Kamera 2: frei (unter den Tisch, wieder raus, umsehen) ----------
cam2 = make_cam("cam2")
sc.frame_set(T(CAM2))
bpy.context.view_layer.update()
start = cam1.matrix_world.copy()


_prev = [None]


def key_cam(t, pos, look, roll=0.0):
    cam2.location = pos
    d = Vector(look) - Vector(pos)
    q = d.to_track_quat("-Z", "Y")
    e = q.to_euler()
    if _prev[0] is not None:
        for i in range(3):
            while e[i] - _prev[0][i] > math.pi:
                e[i] -= 2 * math.pi
            while e[i] - _prev[0][i] < -math.pi:
                e[i] += 2 * math.pi
    _prev[0] = e.copy()
    if roll:
        e.rotate_axis("Z", math.radians(roll))
    cam2.rotation_euler = e
    cam2.keyframe_insert("location", frame=T(t))
    cam2.keyframe_insert("rotation_euler", frame=T(t))


p0 = start.to_translation()
fwd = start.to_3x3() @ Vector((0, 0, -1))
key_cam(CAM2, p0, p0 + fwd)
key_cam(18.4, (0.35, -0.45, 0.5), (-0.4, 0.8, 0.25))
key_cam(UNDER, (0.32, 0.42, 0.2), (-1.6, 0.8, 0.34))
key_cam(24.0, (0.32, 0.44, 0.2), (-1.6, 1.3, 0.36))
key_cam(26.4, (0.32, 0.44, 0.2), (-1.2, 2.6, 0.6))   # Blick zum Fenster
key_cam(28.6, (0.32, 0.42, 0.2), (-1.6, 0.7, 0.3))  # zu Hana
key_cam(QEND, (0.32, 0.42, 0.2), (-1.6, 0.7, 0.3))
key_cam(OUT - 0.8, (0.08, -0.2, 0.5), (0.2, 2.8, 0.7))
key_cam(OUT, (0.2, -0.45, 1.42), (1.1, 2.55, 0.9))     # Fernseher: Tsunami-Warnung
key_cam(36.6, (0.2, -0.45, 1.42), (1.1, 2.55, 0.9))
key_cam(37.6, (0.2, -0.4, 1.42), (1.4, -2.5, 1.2))     # Mama kommt
key_cam(41.6, (0.2, -0.4, 1.42), (1.15, -1.5, 1.35))
key_cam(42.8, (0.2, -0.4, 1.42), (1.1, 2.55, 0.9))     # zurück zum Fernseher: Strom weg
key_cam(44.4, (0.05, -0.95, 1.36), (-1.15, 2.8, 1.05))  # zum Fenster: Durchsage
key_cam(48.6, (-0.05, -0.85, 1.36), (-1.2, 2.8, 1.1))
key_cam(49.6, (0.0, -0.8, 1.34), (-0.75, 0.05, 1.0))   # zu Hana
key_cam(END, (-0.15, -0.6, 1.3), (-0.75, 0.05, 1.0))
key_cam(T2 + 0.6, (-0.55, 1.55, 1.36), (-1.1, 4.4, 0.95))       # 15:27 am Fenster
key_cam(57.2, (-0.6, 1.7, 1.36), (-1.15, 4.4, 0.95))
key_cam(57.9, (-0.62, 1.72, 1.36), (-1.6, 2.35, 1.15))          # zu Hana
key_cam(59.6, (-0.62, 1.75, 1.36), (-1.6, 2.35, 1.15))
key_cam(60.4, (-0.75, 2.05, 1.36), (-1.2, 4.4, 0.9))            # näher ans Fenster: die Welle
key_cam(61.6, (-0.8, 2.2, 1.36), (-1.2, 4.4, 0.9))
key_cam(62.3, (-0.7, 2.0, 1.38), (0.35, 0.9, 1.35))             # Mama stürmt rein
key_cam(END2, (-0.7, 1.95, 1.38), (0.2, 1.1, 1.35))
# Beben + Gehen: Wackeln der Kamera
noise_fr = list(range(T(CAM2), T(END) + 1, 2))
for fr in noise_fr:
    t = (fr - 1) / FPS
    am = qamp(t)
    if am <= 0 and not (OUT - 0.8 < t < OUT + 0.4):
        continue
sc.camera = cam1
m = sc.timeline_markers.new("c1", frame=1)
m.camera = cam1
m2 = sc.timeline_markers.new("c2", frame=T(CAM2))
m2.camera = cam2
# Wackeln: Kamera 2 per Delta-Rotation, Kamera 1 über die Brust
for fr in range(T(QUAKE) - 2, T(QEND + 1.5) + 1, 2):
    t = (fr - 1) / FPS
    am = qamp(t)
    if fr < T(CAM2):
        F.rot(me, "chest", fr, x=2.5 * am * math.sin(t * 29), y=1.8 * am * math.sin(t * 23 + 1), z=1.8 * am * math.sin(t * 19))
    cam2.delta_rotation_euler = (math.radians(2.8 * am * math.sin(t * 31) + 0.8 * am * math.sin(t * 7)), math.radians(2.0 * am * math.sin(t * 27 + 1)), math.radians(2.4 * am * math.sin(t * 21)))
    cam2.delta_location = (0.02 * am * math.sin(t * 37), 0.016 * am * math.sin(t * 33), 0.014 * am * math.sin(t * 41))
    cam2.keyframe_insert("delta_rotation_euler", frame=fr)
    cam2.keyframe_insert("delta_location", frame=fr)
# leichtes Atmen der freien Kamera nach dem Beben
for fr in range(T(QEND + 1.6), T(END) + 1, 6):
    t = (fr - 1) / FPS
    cam2.delta_rotation_euler = (math.radians(0.5 * math.sin(t * 1.3)), math.radians(0.4 * math.sin(t * 0.9)), 0)
    cam2.delta_location = (0, 0, 0.01 * math.sin(t * 2.2))
    cam2.keyframe_insert("delta_rotation_euler", frame=fr)
    cam2.keyframe_insert("delta_location", frame=fr)

# ---------- Beben: Lampe, Bilder, Bücher, Pflanze, Vorhänge, Fernseher, Kleinkram ----------
def wobble(o, amp, freq, k, axes=(0, 1), loc=0.0):
    base = o.rotation_euler.copy()
    bl = o.location.copy()
    for fr in range(T(QUAKE) - 2, T(QEND + 2.5) + 1, 2):
        t = (fr - 1) / FPS
        am = qamp(t)
        r = base.copy()
        for ax in axes:
            r[ax] = base[ax] + math.radians(amp * am * math.sin(t * freq + k * (1.3 + ax)))
        o.rotation_euler = r
        o.keyframe_insert("rotation_euler", frame=fr)
        if loc:
            o.location = bl + Vector((loc * am * math.sin(t * 23 + k), loc * am * math.sin(t * 19 + 2 * k), 0))
            o.keyframe_insert("location", frame=fr)


lamp = S["lamp"]
for fr in range(T(QUAKE) - 2, T(END) + 1, 2):  # Lampe schwingt nach
    t = (fr - 1) / FPS
    am = qamp(t) if t < QEND else max(0.0, math.exp(-(t - QEND) * 0.35)) * 0.8
    lamp.rotation_euler = (math.radians(24 * am * math.sin(t * 3.4)), math.radians(18 * am * math.sin(t * 2.9 + 1)), 0)
    lamp.keyframe_insert("rotation_euler", frame=fr)
for k, o in enumerate(S["swing"]):
    wobble(o, 6.0, 6.0 + k % 3, k)
for k, o in enumerate(S["rattle"]):
    wobble(o, 8.0, 17 + k % 5, k, axes=(0, 1, 2), loc=0.012)
wobble(S["tv"], 3.0, 7.5, 1)
wobble(tb, 1.2, 9.0, 2, axes=(2,), loc=0.015)
for k, n in enumerate(S["noren"]):
    wobble(n, 14, 4.0 + k * 0.3, k)
EV = {"fall": []}
# Fotos kippen um / fallen, Ranzen fällt, einige Bücher fallen aus dem Regal, Pflanze kippt
for k, o in enumerate([o for o in S["falls"] if o.name.startswith("photo")]):
    tf = QUAKE + 2.0 + k * 1.1
    o.keyframe_insert("rotation_euler", frame=T(tf))
    o.keyframe_insert("location", frame=T(tf))
    o.rotation_euler.y += math.radians(-80 if k % 2 else 80)
    o.location.z -= 0.0
    o.keyframe_insert("rotation_euler", frame=T(tf + 0.35))
    EV["fall"].append(tf + 0.35)
books = [o for o in S["falls"] if o.name.startswith("book")]
R.shuffle(books)
for k, o in enumerate(books[:14]):
    tf = QUAKE + 3.0 + R.uniform(0, 9.0)
    o.keyframe_insert("location", frame=T(tf))
    o.keyframe_insert("rotation_euler", frame=T(tf))
    z0 = o.location.z
    dur = math.sqrt(2 * max(0.1, z0) / 9.81)
    o.location = (o.location.x - R.uniform(0.25, 0.6), o.location.y + R.uniform(-0.15, 0.15), 0.03)
    o.rotation_euler = (R.uniform(-1.5, 1.5), math.radians(90) * R.choice((-1, 1)), R.uniform(-0.5, 0.5))
    o.keyframe_insert("location", frame=T(tf + dur))
    o.keyframe_insert("rotation_euler", frame=T(tf + dur))
    EV["fall"].append(tf + dur)
for o in [o for o in S["falls"] if o.name.startswith("randoseru")]:
    tf = QUAKE + 4.0
    o.keyframe_insert("rotation_euler", frame=T(tf))
    o.rotation_euler.x += math.radians(85)
    o.keyframe_insert("rotation_euler", frame=T(tf + 0.4))
    EV["fall"].append(tf + 0.4)
EV["kettle"] = QUAKE + 6.0  # Kessel fällt in der Küche (nur Ton)
json.dump(EV, open(os.path.join(ROOT, "src", "futaba3", "events.json"), "w"), indent=1)

# ---------- Strom weg ----------
for L in S["lights"] + [S["kitchenlight"]]:
    e0 = L.data.energy
    L.data.keyframe_insert("energy", frame=1)
    L.data.keyframe_insert("energy", frame=T(QUAKE + 3.0))
    L.data.keyframe_insert("energy", frame=T(POWER) - 1)
    L.data.energy = e0 * (0.25 if L.name != "kitchenlight" else 0.0)
    L.data.keyframe_insert("energy", frame=T(POWER))
    # Flackern beim Beben
    for k, t in enumerate((QUAKE + 3.1, QUAKE + 3.25, QUAKE + 8.0, QUAKE + 8.1)):
        L.data.energy = e0 * (0.3 if k % 2 == 0 else 1.0)
        L.data.keyframe_insert("energy", frame=T(t))
dsl.data.materials[0] = F.flat_mat("dsglow", (0.6, 0.85, 1.0))

# ---------- Mehr Bewegung unter dem Tisch ----------
# Mandarinen fallen vom Tisch und rollen über den Teppich, eine Tasse fällt und kippt
mk = LR.soft("mikan2", (0.95, 0.56, 0.12))
rolls = []
for k, (x0, t0, x1, y1) in enumerate(((0.05, 20.6, -0.25, 0.22), (0.15, 21.4, 0.02, 0.18), (-0.1, 23.0, -0.45, 0.3), (0.25, 24.2, 0.12, 0.28))):
    o = F.ellipsoid(f"rollmikan{k}", Vector((x0, 0.06, 0.5)), (0.038, 0.038, 0.034), mk, seg=16, rings=10)
    o.keyframe_insert("location", frame=T(t0))
    o.keyframe_insert("rotation_euler", frame=T(t0))
    o.location = (x0 - 0.02, -0.02, 0.04)
    o.keyframe_insert("location", frame=T(t0 + 0.32))
    o.location = (x1, y1, 0.04)
    o.rotation_euler = (R.uniform(4, 9), R.uniform(4, 9), 0)
    o.keyframe_insert("location", frame=T(t0 + 1.9))
    o.keyframe_insert("rotation_euler", frame=T(t0 + 1.9))
    rolls.append(o)
cup2 = LR.cyl("fallcup", (0.0, 0.0, 0), 0.035, 0.08, LR.soft("cupm2", (0.82, 0.86, 0.8)), verts=16, r2=0.04)
cup2.location = (-0.3, 0.08, 0.5)
cup2.keyframe_insert("location", frame=T(24.6))
cup2.keyframe_insert("rotation_euler", frame=T(24.6))
cup2.location = (-0.36, -0.05, 0.04)
cup2.rotation_euler = (math.radians(90), 0, math.radians(30))
cup2.keyframe_insert("location", frame=T(24.95))
cup2.keyframe_insert("rotation_euler", frame=T(24.95))
cup2.location = (-0.42, -0.02, 0.04)
cup2.rotation_euler = (math.radians(90), 0, math.radians(70))
cup2.keyframe_insert("location", frame=T(25.6))
cup2.keyframe_insert("rotation_euler", frame=T(25.6))
EV.setdefault("fall", []).append(24.95)
json.dump(EV, open(os.path.join(ROOT, "src", "futaba3", "events.json"), "w"), indent=1)
# Meine Hand greift nach Hanas Hand (an Kamera 2)
myarm = LR.group("myarm")
myarm.parent = cam2
jm = bpy.data.materials["me_jacket"]
sk = bpy.data.materials["me_skin"]
F.limb("mysleeve", Vector((0, -0.02, 0.16)), Vector((0, 0, 0.02)), 0.042, 0.038, jm, seg=16).parent = myarm
pm = F.ellipsoid("mypalm", Vector((0, 0, -0.03)), (0.04, 0.016, 0.045), sk, seg=18, rings=10)
pm.parent = myarm
for k in range(4):
    fx = -0.026 + k * 0.017
    fg = F.limb(f"myfinger{k}", Vector((fx, 0, -0.065)), Vector((fx * 1.1, -0.012, -0.115 + abs(k - 1.5) * 0.008)), 0.008, 0.007, sk, seg=10, subsurf=0)
    fg.parent = myarm
    F.ellipsoid(f"myfingertip{k}", Vector((fx * 1.1, -0.012, -0.115 + abs(k - 1.5) * 0.008)), (0.007, 0.007, 0.007), sk, seg=10, rings=6).parent = myarm
F.limb("mythumb", Vector((0.04, 0, -0.035)), Vector((0.06, -0.01, -0.075)), 0.009, 0.008, sk, seg=10, subsurf=0).parent = myarm
for t, loc, rx in ((28.4, (0.32, -0.55, -0.3), -20), (29.6, (0.07, -0.17, -0.45), -12), (QEND, (0.07, -0.17, -0.45), -12), (OUT - 1.0, (0.32, -0.55, -0.3), -20)):
    myarm.location = loc
    myarm.rotation_euler = (math.radians(rx), math.radians(-25), 0)
    myarm.keyframe_insert("location", frame=T(t))
    myarm.keyframe_insert("rotation_euler", frame=T(t))
vis(myarm, [(0, False), (28.3, True), (OUT - 0.9, False)])

# ---------- 15:27 – die Welle (am Fenster) ----------
# Hana steht am Fenster, dreht sich zu mir; Mama stürmt herein
place_r(hana, END, (hana["arm"].location.x, hana["arm"].location.y, 0.0), 0.0, hana["arm"].rotation_euler.z)
place_r(hana, T2 + 0.4, (-1.55, 2.25, 0.0), 0.0, heading(Vector((0.1, 1.0, 0))))
for sd in ("L", "R"):
    rot(hana, f"thigh.{sd}", T2 + 0.4)
    rot(hana, f"shin.{sd}", T2 + 0.4, x=4)
    rot(hana, f"upperarm.{sd}", T2 + 0.4, x=-40, z=(8 if sd == "L" else -8))
    rot(hana, f"forearm.{sd}", T2 + 0.4, x=-60)
rot(hana, "spine", T2 + 0.4, x=4)
head(hana, [(T2 + 0.4, 0, 0), (57.2, 0, 0), (57.7, -80, 5), (59.8, -80, 5), (60.4, 0, 0), (END2, 0, 0)])
rot(hana, "upperarm.R", 57.6, x=-40, z=-8)
rot(hana, "upperarm.R", 58.0, x=-95, z=-30)  # zeigt nach draußen
rot(hana, "forearm.R", 58.0, x=-10)
F.look(hana, T(57.7), -20, 0)
F.brows(hana, T(57.6), 1.0, 1.0)
F.lipsync(hana, WAV["h6"], AT["h6"], FPS)
place_r(mama, END, (mama["arm"].location.x, mama["arm"].location.y, 0.0), 0.0, mama["arm"].rotation_euler.z)
place_r(mama, T2 + 0.4, (1.3, 0.2, 0.0), 0.0, heading(Vector((-1.0, 0.5, 0))))
place_r(mama, 61.4, (1.3, 0.2, 0.0), 0.0, heading(Vector((-1.0, 0.5, 0))))
place_r(mama, 62.4, (0.45, 0.9, 0.0), 0.0, heading(Vector((-1.0, 0.6, 0))))
for k in range(5):
    t = 61.4 + k * 0.2
    for sd, sg in (("L", 1), ("R", -1)):
        rot(mama, f"thigh.{sd}", t, x=-30 * sg * (1 if k % 2 else -1))
        rot(mama, f"shin.{sd}", t, x=10 + 30 * (k % 2))
for sd in ("L", "R"):
    rot(mama, f"thigh.{sd}", 62.5)
    rot(mama, f"shin.{sd}", 62.5, x=4)
rot(mama, "upperarm.R", 62.3, x=-20, z=0)
rot(mama, "upperarm.R", 62.8, x=-85, z=-20)
rot(mama, "forearm.R", 62.8, x=-20)
head(mama, [(T2 + 0.4, 0, 0), (62.4, 0, 0), (62.8, -10, 0)])
F.brows(mama, T(61.6), 1.0, 1.0)
F.lipsync(mama, WAV["ma3"], AT["ma3"], FPS)
# Welle: Wasserfläche + Gischt steigen zwischen Fenster und Ausblick, strömen von links nach rechts
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
waves = []
for k, (yy, w, h, z0, z1, x0, x1, t0) in enumerate(((LR.Y1 + 1.5, 7.0, 2.9, -0.75, 0.3, -1.8, -0.9, 56.2), (LR.Y1 + 1.3, 7.0, 2.6, -0.95, 0.12, -2.3, -1.2, 57.4))):
    wv = LR.uvplane(f"wave{k}", (WX, yy, z0), w, h, WM, (math.radians(90), 0, 0))
    for t, z, x in ((T2, z0, x0), (t0, z0, x0), (60.5, (z0 + z1) / 2 + 0.15, (x0 + x1) / 2), (END2, z1, x1)):
        wv.location = (WX + x, yy, z)
        wv.keyframe_insert("location", frame=T(t))
    vis(wv, [(0, False), (T2, True)])
    waves.append(wv)
# Trümmer auf dem Wasser
debm = LR.soft("debris", (0.5, 0.36, 0.24))
roofm = LR.soft("debroof", (0.35, 0.38, 0.46))
for k in range(7):
    d = LR.box(f"debris{k}", (0, 0, 0), (R.uniform(0.12, 0.35), 0.04, R.uniform(0.03, 0.08)), debm if k % 3 else roofm)
    yy = LR.Y1 + 1.4
    for t in (T2, 57.6 + k * 0.3, END2):
        u = (t - 57.6) / (END2 - 57.6)
        zt = -0.2 + 0.85 * max(0.0, min(1.0, (t - 56.2) / (END2 - 56.2)))
        d.location = (WX - 1.8 + k * 0.55 + max(0.0, u) * 1.4, yy, (zt if t > T2 else -3.0) + 0.04 * math.sin(k + t))
        d.rotation_euler = (0, R.uniform(-0.6, 0.6), R.uniform(-0.3, 0.3))
        d.keyframe_insert("location", frame=T(t))
        d.keyframe_insert("rotation_euler", frame=T(t))
# leichtes Handkamera-Wackeln in der Fenster-Szene, stärker als die Welle näher kommt
for fr in range(T(T2), T(END2) + 1, 2):
    t = (fr - 1) / FPS
    am = 0.3 + 0.9 * max(0.0, min(1.0, (t - 58.0) / 6.0))
    cam2.delta_rotation_euler = (math.radians(0.9 * am * math.sin(t * 9)), math.radians(0.7 * am * math.sin(t * 7 + 1)), math.radians(0.6 * am * math.sin(t * 5)))
    cam2.delta_location = (0.006 * am * math.sin(t * 11), 0.005 * am * math.sin(t * 13), 0.006 * am * math.sin(t * 17))
    cam2.keyframe_insert("delta_rotation_euler", frame=fr)
    cam2.keyframe_insert("delta_location", frame=fr)

# ---------- Render ----------
import toonlib as TL
arms = {me["arm"], hana["arm"], mama["arm"]}
for i, o in enumerate(bpy.data.objects):
    q, hum = o, False
    while q is not None:
        if q in arms:
            hum = True
            break
        q = q.parent
    o.pass_index = 10000 + i if hum else 1 + i
TL.comp_outlines(kn=1.0, kd=0.5, thr=0.7, fade_near=4.0, fade_far=9.0)
# Augen ohne eigene Umrisslinien (sonst wirken sie aus der Entfernung wie Sonnenbrillen):
# Augenweiß/Iris/Pupille/Glanz bekommen dieselbe Material- und Objekt-ID wie die Haut des Kopfes.
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
sc.frame_start, sc.frame_end = 1, T(END2)
pct = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 85
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, pct
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGB"
sc.render.use_overwrite = False
sc.render.filepath = sys.argv[-2] if sys.argv[-1].isdigit() else "/tmp/room_"
