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
      "tv3": 35.2, "ma2": 40.6, "lsp": 45.0, "h5": 50.0, "m4": 51.1}
EEW, QUAKE, QEND, CAM2, UNDER, OUT, MAMA, POWER, END = 12.0, 15.8, 33.0, 17.6, 19.2, 35.0, 37.0, 43.8, 55.5
json.dump(dict(AT=AT, EEW=EEW, QUAKE=QUAKE, QEND=QEND, POWER=POWER, END=END, FPS=FPS, CAM2=CAM2),
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
UH = Vector((-0.33, 0.62, 0))
yaw_u = heading(Vector((0.32, 0.42, 0)) - UH)
place(hana, 16.0, (HK[0], HK[1], -0.47), math.radians(-60))
place(hana, 17.4, (UH.x, UH.y, -0.52), yaw_u + math.pi)
for sd in ("L", "R"):
    rot(hana, f"thigh.{sd}", 16.0, x=-92, z=(-8 if sd == "L" else 8))
    rot(hana, f"thigh.{sd}", 17.4, x=-125, z=(-10 if sd == "L" else 10))
    rot(hana, f"shin.{sd}", 17.4, x=150)
    rot(hana, f"upperarm.{sd}", 16.0, x=-35, z=(10 if sd == "L" else -10))
    rot(hana, f"upperarm.{sd}", 17.4, x=-155, z=(18 if sd == "L" else -18))
    rot(hana, f"forearm.{sd}", 17.4, x=-120)
rot(hana, "spine", 16.0, x=10)
rot(hana, "spine", 17.4, x=38)
head(hana, [(17.4, 0, 55), (QEND, 0, 55)])
F.look(hana, T(17.4), 0, 10)
blinks = (2.0, 6.0, 9.5, 18.6, 21.0, 24.6, 28.2, 31.5, 38.2, 42.0, 47.0, 52.6)
for t in blinks:
    F.blink(hana, T(t))
F.brows(hana, T(QEND), 1.0, 1.0)
# wieder hoch (33,5–35,5), steht neben dem Tisch, Angst
place(hana, OUT - 1.2, (UH.x, UH.y, -0.52), yaw_u + math.pi)
STAND = (-0.75, 0.05)
place(hana, OUT + 0.6, (STAND[0], STAND[1], 0.0), heading(Vector((0.2, -0.6, 0)) - Vector((STAND[0], STAND[1], 0))))
for sd in ("L", "R"):
    rot(hana, f"thigh.{sd}", OUT - 1.2, x=-125, z=(-10 if sd == "L" else 10))
    rot(hana, f"shin.{sd}", OUT - 1.2, x=150)
    rot(hana, f"thigh.{sd}", OUT + 0.6, x=-2)
    rot(hana, f"shin.{sd}", OUT + 0.6, x=4)
    rot(hana, f"upperarm.{sd}", OUT - 1.2, x=-155, z=(18 if sd == "L" else -18))
    rot(hana, f"forearm.{sd}", OUT - 1.2, x=-120)
    rot(hana, f"upperarm.{sd}", OUT + 0.6, x=-20, z=(6 if sd == "L" else -6))
    rot(hana, f"forearm.{sd}", OUT + 0.6, x=-95)  # Hände vor der Brust
rot(hana, "spine", OUT - 1.2, x=38)
rot(hana, "spine", OUT + 0.6, x=4)
head(hana, [(QEND, 0, 55), (OUT + 0.6, 0, 0), (36.0, 30, 10), (37.4, -70, 5), (41.0, -70, 5), (42.4, 20, 10), (44.6, 40, 5), (48.4, 40, 5),
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
for k, z in enumerate((0.024, 0.007, -0.010, -0.027)):
    rr = 0.042 + 0.0085
    a0, a1 = math.radians(176), math.radians(70 + k * 6)
    pts = [(rr * math.cos(a0 + (a1 - a0) * u), rr * math.sin(a0 + (a1 - a0) * u), z - 0.003 * u) for u in (0, 0.25, 0.5, 0.75, 1.0)]
    fl = F.curve_line(f"gripf{k}", pts, 0.0088 - 0.0006 * k, skin)
    fl.parent = mug
    fl.location = fl.location  # Kurve liegt in Becher-Koordinaten
    tip = F.ellipsoid(f"griptip{k}", Vector(pts[-1]), (0.0086, 0.0086, 0.0086), skin, seg=12, rings=8)
    tip.parent = mug
    grip += [fl, tip]
palm = F.ellipsoid("grippalm", Vector((-0.06, -0.006, -0.004)), (0.015, 0.036, 0.046), skin, seg=20, rings=12)
palm.parent = mug
tpts = [(0.05 * math.cos(math.radians(a)), 0.05 * math.sin(math.radians(a)), 0.034 + 0.004 * i) for i, a in enumerate((178, 160, 142, 126))]
th = F.curve_line("gripthumb", tpts, 0.0102, skin)
th.parent = mug
tt = F.ellipsoid("gripthumbtip", Vector(tpts[-1]), (0.01, 0.01, 0.01), skin, seg=12, rings=8)
tt.parent = mug
grip += [palm, th, tt]
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
key_cam(44.4, (0.15, -0.35, 1.42), (-1.15, 2.8, 1.2))  # zum Fenster: Durchsage
key_cam(48.6, (0.1, -0.2, 1.42), (-1.2, 2.8, 1.25))
key_cam(49.6, (0.1, -0.25, 1.4), (-0.75, 0.05, 1.0))   # zu Hana
key_cam(END, (0.0, -0.1, 1.38), (-0.75, 0.05, 1.0))
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
    cam2.delta_rotation_euler = (math.radians(1.6 * am * math.sin(t * 31)), math.radians(1.2 * am * math.sin(t * 27 + 1)), math.radians(1.4 * am * math.sin(t * 21)))
    cam2.delta_location = (0.012 * am * math.sin(t * 37), 0.01 * am * math.sin(t * 33), 0.008 * am * math.sin(t * 41))
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
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = int(os.environ.get("SAMPLES", 10))
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, T(END)
pct = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 85
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, pct
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGB"
sc.render.use_overwrite = False
sc.render.filepath = sys.argv[-2] if sys.argv[-1].isdigit() else "/tmp/room_"
