# „Futaba, 11. März 2011“ – Teil 1 (Ich-Sicht, Ink-Pop). SHOT=A: Morgengrauen 12.03. (Lautsprecherwagen),
# SHOT=B: 11.03. Heimweg mit Sota, Oma grüßt, Nachricht von Mama, Erdbeben-Frühwarnung, Beben.
# blender -b --python scene1.py -s <von> -e <bis> -a -- <ausgabe_präfix> <prozent>
import bpy, sys, os, math, random, json
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "futaba"))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
import figure as F, cast as C, street as ST

sc = bpy.context.scene
FPS = 30
T = lambda s: int(round(s * FPS)) + 1
SHOT = os.environ.get("SHOT", "B")
R = random.Random(5)

# ---------- Zeitplan (Sekunden, gesamtes Video) ----------
A_END = 8.6
B0 = 9.6
AT = {"lsp1": 0.4, "m1": 5.8, "s1": 10.2, "m2": 13.6, "o1": 15.3, "s2": 19.6, "s3": 23.0, "s4": 27.6, "m3": 34.5}
PING, EEW, QUAKE, DUCK, END = 18.0, 22.0, 26.6, 28.2, 38.0
SPEED = 1.15
json.dump(dict(AT=AT, A_END=A_END, B0=B0, PING=PING, EEW=EEW, QUAKE=QUAKE, DUCK=DUCK, END=END, FPS=FPS),
          open(os.path.join(ROOT, "src", "futaba2", "timeline.json"), "w"), indent=1)
TIM = json.load(open(os.path.join(ROOT, "src", "futaba2", "timing.json")))
SCR = json.load(open(os.path.join(ROOT, "src", "futaba2", "script.json")))
WAV = {s["id"]: os.path.join(ROOT, "public", l["file"]) for s, l in zip(SCR["sentences"], TIM["lines"])}


def qamp(t):
    if t < QUAKE:
        return 0.0
    return min(1.0, (t - QUAKE) / 0.7) * (0.85 + 0.15 * math.sin(t * 1.7))


# ---------- Welt ----------
S = ST.build()
sun = ST.sky(day=(SHOT != "A"))

# ---------- Figuren ----------
V = lambda x, y: Vector((x, y, 0))


def heading(d):
    return math.atan2(d.x, -d.y)


def walk(f, path, t0, speed, t_stop=None, run=False):
    """Gehen entlang path ab t0; bleibt bei t_stop stehen (weich)."""
    arm = f["arm"]
    segs, tot = [], 0.0
    for a, b in zip(path, path[1:]):
        segs.append((a, b, tot, (b - a).length))
        tot += (b - a).length
    stride = 2.4 if run else 1.4
    A, K, Aa, bob = (40, 85, 40, 0.05) if run else (22, 40, 16, 0.016)
    t1 = t0 + tot / speed if t_stop is None else min(t_stop, t0 + tot / speed)
    f0, f1 = T(t0), T(t1)
    prev = None
    for fr in list(range(f0, f1, 2)) + [f1]:
        t = (fr - 1) / FPS
        s = min(tot, (t - t0) * speed)
        for a, b, s0, L in segs:
            if s <= s0 + L or (a, b, s0, L) == segs[-1]:
                pos = a.lerp(b, 0 if L == 0 else min(1, (s - s0) / L))
                yaw = heading(b - a)
                break
        if prev is not None:
            while yaw - prev > math.pi:
                yaw -= 2 * math.pi
            while yaw - prev < -math.pi:
                yaw += 2 * math.pi
        prev = yaw
        ph = 2 * math.pi * s / stride
        k = min(1.0, (t1 - t) / 0.35) if fr > f1 - 12 else 1.0  # ausklingen
        arm.location = (pos.x, pos.y, bob * k * math.cos(2 * ph))
        arm.keyframe_insert("location", frame=fr)
        arm.rotation_euler = (0, 0, yaw)
        arm.keyframe_insert("rotation_euler", frame=fr)
        for sd, sg in (("L", 1), ("R", -1)):
            sp, cp = math.sin(ph) * sg, math.cos(ph) * sg
            F.rot(f, f"thigh.{sd}", fr, x=k * (-A * sp - (6 if run else 2)))
            F.rot(f, f"shin.{sd}", fr, x=k * (4 + K * max(0.0, cp) ** 1.5))
            if not f.get("arms_busy", {}).get(sd):
                F.rot(f, f"upperarm.{sd}", fr, x=k * Aa * sp + (-25 if run else 0), z=(-6 if sd == "L" else 6))
                F.rot(f, f"forearm.{sd}", fr, x=-(70 if run else 14) - 8 * max(0, sp) * k)
        F.rot(f, "spine", fr, x=(10 if run else 2), y=k * (5 if run else 3) * math.sin(ph))
    return t1


def idle(f, t0, t1, seed, amp=1.0):
    r = random.Random(seed)
    ph = [r.uniform(0, 6.3) for _ in range(4)]
    for fr in range(T(t0), T(t1), 8):
        t = fr / FPS
        F.rot(f, "chest", fr, x=amp * 1.2 * math.sin(t * 2 * math.pi / 3.8 + ph[0]), y=amp * 1.5 * math.sin(t * 0.6 + ph[1]),
              z=amp * 0.8 * math.sin(t * 0.8 + ph[2]))


def head(f, keys):
    """keys: (t, gier°, nick°) – gier + = nach links der Figur, nick + = hoch."""
    for t, yaw, pitch in keys:
        fr = T(t)
        F.rot(f, "neck", fr, y=yaw * 0.45, x=-pitch * 0.4)
        F.rot(f, "head", fr, y=yaw * 0.55, x=-pitch * 0.6)


def blinks(f, ts):
    for t in ts:
        F.blink(f, T(t))


def pose(f, t, dur=0.4, **bones):
    """bones: name=(x,y,z) – weicher Übergang von der aktuellen Pose."""
    for bn, (x, y, z) in bones.items():
        pb = f["arm"].pose.bones[bn.replace("_", ".")]
        F.rot(f, pb.name, T(t))  # Start: wird unten überschrieben, falls schon Schlüssel existieren
    return None


def key_now(f, bone, t):
    """Aktuellen Wert eines Knochens an Zeit t als Schlüssel setzen (für weiche Übergänge)."""
    pb = f["arm"].pose.bones[bone]
    sc.frame_set(T(t))
    pb.keyframe_insert("rotation_euler", frame=T(t))


def set_rot(f, bone, t, x=0.0, y=0.0, z=0.0):
    F.rot(f, bone, T(t), x=x, y=y, z=z)


P = {}
for nm in ("me", "sota", "oma", "tanaka"):
    P[nm] = C.make(nm)
P["yui"] = C.make("yui")
P["yui2"] = F.make_figure("yui2", **dict(C.CAST["yui"], hair=(0.35, 0.22, 0.12), hair_style="long", height=1.57))
ME, SOTA, OMA, TAN = P["me"], P["sota"], P["oma"], P["tanaka"]
for o in ME["head_parts"]:
    o.hide_render = True
for f in P.values():
    F.relaxed(f, 1)
    F.look(f, 1)
    F.mouth(f, 1, 0)
    F.brows(f, 1)

# ---------- Kamera am Kopf von „me“ ----------
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 13.5
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 30
cam.data.clip_start = 0.04


def attach_cam():
    arm = ME["arm"]
    b = arm.data.bones["head"]
    eye = Vector((0, -0.075, 1.555)) * ME["S"]
    cam.parent = arm
    cam.parent_type = "BONE"
    cam.parent_bone = "head"
    rest = arm.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))
    cam.matrix_parent_inverse = rest.inverted()
    cam.matrix_basis = arm.matrix_world @ Matrix.Translation(eye) @ Euler((math.radians(90), 0, math.pi), "XYZ").to_matrix().to_4x4()


# Handy (Nachricht -> Warnung) in meiner rechten Hand per IK
TEXD = os.path.join(HERE, "..", "futaba", "tex")


def phone_mat(files_keys):
    m = bpy.data.materials.new("phonescreen")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    a = nt.nodes.new("ShaderNodeTexImage")
    a.image = bpy.data.images.load(os.path.join(TEXD, "phone_msg.png"))
    b = nt.nodes.new("ShaderNodeTexImage")
    b.image = bpy.data.images.load(os.path.join(TEXD, "phone_eew.png"))
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    nt.links.new(a.outputs[0], mx.inputs[6])
    nt.links.new(b.outputs[0], mx.inputs[7])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[1].default_value = 1.1
    nt.links.new(mx.outputs[2], em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    for t, v in files_keys:
        mx.inputs[0].default_value = v
        mx.inputs[0].keyframe_insert("default_value", frame=T(t))
    m["toon"] = 1
    return m


PH_BODY = F.ink_mat("phonebody", (0.16, 0.17, 0.2), shade=0.7)
EEW_M = ST.texmat("eewscreen", "phone_eew.png", emit=0.5)


def phone(name, screen):
    b = ST.box(name, (0, 0, 0), (0.072, 0.0095, 0.15), PH_BODY, bevel=0.004)
    s = ST.plane(name + "s", (0, -0.0056, 0), 0.064, 0.135, screen, (math.radians(90), 0, 0))
    s.parent = b
    return b


def vis(o, keys):
    for ob in [o] + list(o.children):
        for t, v in keys:
            ob.hide_render = not v
            ob.keyframe_insert("hide_render", frame=T(t) if t > 0 else 1)


# ---------- Ablauf ----------
if SHOT == "A":
    # 12.03., 5:44 – leere Straße, Lautsprecherwagen fährt vorbei, Blick zum Schild
    ME["arm"].location = (0.9, 40.0, 0)
    ME["arm"].rotation_euler = (0, 0, math.pi)
    for f in (SOTA, OMA, TAN, P["yui"], P["yui2"]):
        f["arm"].location = (0, -200, -50)
    idle(ME, 0, A_END, 1, amp=0.6)
    head(ME, [(0, 0, 4), (2.2, 4, 2), (3.6, 22, -2), (4.6, 55, -3), (5.6, 40, 0), (6.6, 6, 6), (A_END, 2, 9)])
    # Lautsprecherwagen (Kei-Truck mit zwei Trichtern auf dem Dach)
    van = bpy.data.objects.new("van", None)
    sc.collection.objects.link(van)
    vc = F.ink_mat("vanw", (0.95, 0.95, 0.94), 0.7)
    parts = [ST.box("vanbody", (0, 0, 0.75), (1.45, 3.3, 1.0), vc, bevel=0.1), ST.box("vancab", (0, -0.9, 1.5), (1.4, 1.3, 0.7), vc, bevel=0.1),
             ST.box("vanws", (0, -1.56, 1.5), (1.25, 0.04, 0.5), F.ink_mat("vglass", (0.4, 0.5, 0.62), 0.8), rot=(math.radians(-15), 0, 0)),
             ST.plane("vanside", (0.735, 0.4, 0.8), 1.8, 0.45, ST.texmat("vansidem", "van_side.png"), (math.radians(90), 0, math.radians(90))),
             ST.box("vanstripe", (0, 0, 0.45), (1.47, 3.32, 0.12), F.ink_mat("vstripe", (0.2, 0.35, 0.7)))]
    for k, dx in enumerate((-0.35, 0.35)):
        parts.append(F.limb("horn", Vector((dx, -0.2, 2.0)), Vector((dx, -0.75, 2.12)), 0.06, 0.2, F.ink_mat("hornm", (0.85, 0.85, 0.8)), seg=16, subsurf=0))
    parts.append(ST.cyl("hornpole", (0, -0.2, 1.95), 0.04, 0.3, F.ink_mat("hp", (0.4, 0.4, 0.42))))
    for wx in (-0.68, 0.68):
        for wy in (-1.05, 1.05):
            parts.append(ST.cyl("vwh", (wx, wy, 0.3), 0.3, 0.2, F.ink_mat("vtire", (0.15, 0.15, 0.17)), verts=20, rot=(0, math.radians(90), 0)))
    rot_lamp = ST.box("vanlamp", (0, -0.6, 1.92), (0.25, 0.25, 0.12), F.flat_mat("vlamp", (1.0, 0.55, 0.15)))
    parts.append(rot_lamp)
    for p in parts:
        p.parent = van
    lamp = bpy.data.objects.new("vanlampL", bpy.data.lights.new("vanlampL", "POINT"))
    sc.collection.objects.link(lamp)
    lamp.data.energy = 60
    lamp.data.color = (1.0, 0.55, 0.2)
    lamp.parent = van
    lamp.location = (0, -0.6, 2.2)
    for t, y in ((0, 56.0), (A_END, 56.0 - 3.2 * A_END)):
        van.location = (-1.45, y, 0)
        van.keyframe_insert("location", frame=T(t) if t else 1)
    for fc in van.animation_data.action.fcurves if hasattr(van.animation_data.action, "fcurves") else []:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    for t in [i * 0.25 for i in range(int(A_END * 4) + 1)]:
        lamp.data.energy = 90 if int(t * 4) % 2 == 0 else 15
        lamp.data.keyframe_insert("energy", frame=T(t) if t else 1)
    # Straßenlaternen an, kühles Licht
    for h in S["lamps"]:
        h.data.materials[0] = F.flat_mat("lampon", (1.0, 0.95, 0.75))
        pl = bpy.data.objects.new("street", bpy.data.lights.new("street", "POINT"))
        sc.collection.objects.link(pl)
        pl.data.energy = 220
        pl.data.color = (1.0, 0.85, 0.6)
        pl.location = h.location + Vector((0, 0, -0.2))
    frame_range = (1, T(A_END))
else:
    # 11.03., ab 14:44 – Heimweg
    stop = EEW
    OMA["arms_busy"] = {"R": True}
    walk(ME, [V(1.2, 2.0), V(1.2, 40.0)], B0, SPEED, t_stop=stop)
    walk(SOTA, [V(0.42, 2.3), V(0.42, 40.0)], B0, SPEED, t_stop=stop + 0.15)
    walk(P["yui"], [V(-0.7, 7.0), V(-0.7, 60.0)], B0, 1.05, t_stop=stop + 0.3)
    walk(P["yui2"], [V(-1.25, 7.4), V(-1.25, 60.0)], B0, 1.05, t_stop=stop + 0.4)
    walk(OMA, [V(-1.5, 17.6), V(-1.5, 0.0)], B0, 0.6, t_stop=16.6)
    TAN["arm"].location = (3.25, 21.2, 0)
    TAN["arm"].rotation_euler = (0, 0, heading(Vector((-1, -0.3, 0))))
    TAN["arm"].keyframe_insert("location", frame=1)
    for f in P.values():
        if f is not ME:
            idle(f, B0, END, sum(map(ord, f["name"])))
    # Oma bleibt stehen, dreht sich zu uns, winkt
    for t, yaw in ((16.6, heading(Vector((0, -1, 0)))), (17.2, heading(Vector((1.0, -0.5, 0))))):
        OMA["arm"].rotation_euler = (0, 0, yaw)
        OMA["arm"].keyframe_insert("rotation_euler", frame=T(t))
    set_rot(OMA, "upperarm.R", B0, x=0, z=4)
    set_rot(OMA, "forearm.R", B0, x=-14)
    set_rot(OMA, "upperarm.R", 15.0, x=0, z=4)
    set_rot(OMA, "upperarm.R", 15.5, x=-110, z=25)
    for k, t in enumerate((15.5, 15.8, 16.1, 16.4, 16.7)):
        set_rot(OMA, "forearm.R", t, x=-40, z=(18 if k % 2 else -18))
    set_rot(OMA, "upperarm.R", 17.2, x=-110, z=25)
    set_rot(OMA, "upperarm.R", 17.7, x=0, z=4)
    set_rot(OMA, "forearm.R", 17.7, x=-14)
    head(OMA, [(B0, 0, -4), (14.6, 0, -4), (15.2, -20, 4), (17.8, -35, 2), (EEW, -30, 0)])
    F.brows(OMA, T(15.2), 0.6, 0.0)
    # Tanaka fegt vor seinem Laden (Besen in beiden Händen)
    broom = bpy.data.objects.new("broom", None)
    sc.collection.objects.link(broom)
    stick = F.limb("broomstick", Vector((0, 0, 0)), Vector((0, 0, 1.25)), 0.016, 0.016, F.ink_mat("wood", (0.72, 0.55, 0.35)), seg=8, subsurf=0)
    brush = ST.box("broomhead", (0, 0, -0.08), (0.32, 0.06, 0.16), F.ink_mat("straw", (0.88, 0.78, 0.45)))
    stick.parent = broom
    brush.parent = broom
    F.bone_parent(broom, TAN["arm"], "hand.R")
    broom.matrix_parent_inverse = Matrix()
    broom.location = (0, -0.05, 0.0)
    broom.rotation_euler = (math.radians(150), 0, 0)
    TAN["arms_busy"] = {"L": True, "R": True}
    for k in range(int((EEW - B0) / 0.9)):
        t = B0 + k * 0.9
        sw = 1 if k % 2 else -1
        set_rot(TAN, "upperarm.R", t, x=-35 + 12 * sw, z=-10)
        set_rot(TAN, "forearm.R", t, x=-40)
        set_rot(TAN, "upperarm.L", t, x=-25 + 12 * sw, z=12)
        set_rot(TAN, "forearm.L", t, x=-60)
        set_rot(TAN, "spine", t, x=12, y=8 * sw)
    head(TAN, [(B0, 0, -18), (EEW, 0, -18), (EEW + 0.6, 10, 10), (QUAKE, 20, 20)])
    # Sota schaut mich an, redet, lehnt sich zu meinem Handy
    SOTA["arms_busy"] = {}
    head(SOTA, [(B0, 0, 0), (10.0, -55, -2), (13.2, -52, -2), (13.8, -10, 0), (15.2, 10, 2), (17.4, 0, 0), (18.6, -55, -18), (21.4, -52, -15),
                (22.4, 0, -20), (22.9, -55, 0), (24.6, -55, 2), (25.3, 15, 10), (QUAKE, 10, 20), (27.4, -55, 0), (29.2, -40, -5), (31.0, -10, 25),
                (33.4, -45, -6), (END, -45, -8)])
    set_rot(SOTA, "spine", 18.4, x=2)
    set_rot(SOTA, "spine", 18.9, x=14, y=-10)
    set_rot(SOTA, "spine", 21.4, x=14, y=-10)
    set_rot(SOTA, "spine", 22.0, x=2)
    F.brows(SOTA, T(B0), 0.0)
    F.brows(SOTA, T(19.6), 0.5)
    F.brows(SOTA, T(21.6), 0.0)
    F.brows(SOTA, T(23.0), 1.0, 0.4)
    F.brows(SOTA, T(QUAKE + 0.5), 0.8, 1.0)
    F.look(SOTA, T(B0))
    F.look(SOTA, T(18.6), -10, -20)
    F.look(SOTA, T(21.4), -10, -20)
    F.look(SOTA, T(22.9), -5, 0)
    blinks(SOTA, (11.3, 14.0, 16.9, 20.8, 24.1, 30.2, 35.0))
    blinks(OMA, (12.0, 16.0, 19.5))
    blinks(TAN, (11.0, 15.4, 20.2))
    # Alle holen beim Alarm das Handy raus
    for k, f in enumerate((SOTA, P["yui"], P["yui2"], OMA, TAN)):
        t0 = EEW + 0.15 + k * 0.12
        ph = phone(f"ph_{f['name']}", EEW_M)
        F.bone_parent(ph, f["arm"], "hand.R")
        ph.matrix_parent_inverse = Matrix()
        ph.location = (0.0, 0.09, -0.02)
        ph.rotation_euler = (math.radians(-90), 0, math.radians(180))
        vis(ph, [(0, False), (t0 + 0.2, True), (QUAKE + 0.8, False)])
        f.setdefault("arms_busy", {})["R"] = True
        set_rot(f, "upperarm.R", t0, x=0, z=6)
        set_rot(f, "forearm.R", t0, x=-14)
        set_rot(f, "upperarm.R", t0 + 0.4, x=-30, z=-12)
        set_rot(f, "forearm.R", t0 + 0.4, x=-105)
        set_rot(f, "upperarm.R", QUAKE + 0.4, x=-30, z=-12)
        set_rot(f, "forearm.R", QUAKE + 0.4, x=-105)
        if f is not SOTA and f is not TAN:
            head(f, [(t0, 0, 0), (t0 + 0.4, 0, -22), (QUAKE, 0, -22), (QUAKE + 0.4, 0, 12)])
        F.brows(f, T(t0 + 0.3), 0.6, 0.6)
    # Beben: in die Hocke, Arme über den Kopf
    def crouch(f, t, cover=True, dz=-0.42):
        a = f["arm"]
        sc.frame_set(T(t))
        loc = a.location.copy()
        a.keyframe_insert("location", frame=T(t))
        for sd in ("L", "R"):
            set_rot(f, f"thigh.{sd}", t)
            set_rot(f, f"shin.{sd}", t, x=4)
            set_rot(f, f"thigh.{sd}", t + 0.5, x=-100)
            set_rot(f, f"shin.{sd}", t + 0.5, x=125)
            if cover:
                set_rot(f, f"upperarm.{sd}", t + 0.5, x=-150, z=(12 if sd == "L" else -12))
                set_rot(f, f"forearm.{sd}", t + 0.5, x=-115)
        set_rot(f, "spine", t, x=2)
        set_rot(f, "spine", t + 0.5, x=30)
        a.location = (loc.x, loc.y, dz)
        a.keyframe_insert("location", frame=T(t + 0.5))
    for f, dt in ((P["yui"], 0.5), (P["yui2"], 0.6), (OMA, 1.1), (TAN, 0.8), (SOTA, 1.2)):
        crouch(f, QUAKE + dt, cover=f is not SOTA)
    F.brows(OMA, T(QUAKE + 0.6), 1.0, 1.0)
    # Sota dreht in der Hocke den Oberkörper zu mir
    set_rot(SOTA, "chest", QUAKE + 1.0)
    set_rot(SOTA, "chest", QUAKE + 1.8, y=-40)
    set_rot(SOTA, "chest", END, y=-42)
    F.brows(TAN, T(QUAKE + 0.6), 0.8, 1.0)
    # Lippen
    for sid, f in (("s1", SOTA), ("s2", SOTA), ("s3", SOTA), ("s4", SOTA), ("o1", OMA)):
        F.lipsync(f, WAV[sid], AT[sid], FPS)

    # ---------- Ich: Blick, Handy, Hocke, Wackeln ----------
    head_keys = [(B0, 2, -3), (10.2, 64, -8), (13.0, 60, -8), (13.6, 8, -2), (15.0, 40, -6), (16.6, 48, -10), (17.6, 10, -4), (18.0, 6, -10),
                 (18.5, 0, -42), (19.7, 2, -40), (20.2, 55, -18), (21.4, 52, -14), (22.0, 2, -38), (22.7, 60, -8), (24.0, 2, 0), (24.8, -42, -4),
                 (25.7, 140, -8), (26.6, 70, 2), (27.4, 60, -8), (28.2, 10, -22), (29.4, -10, 32), (31.0, -48, 10), (32.4, 12, -4), (33.6, 62, -14),
                 (36.3, 58, -14), (END, 56, -14)]
    for t, yaw, pitch in head_keys:
        fr = T(t)
        F.rot(ME, "spine", fr, y=yaw * 0.25, x=-pitch * 0.15)
        F.rot(ME, "neck", fr, y=yaw * 0.4, x=-pitch * 0.4)
        F.rot(ME, "head", fr, y=yaw * 0.35, x=-pitch * 0.45)
    frame_range = (T(B0), T(END))

# ---------- Kamera anhängen, Wackeln, Handy ----------
sc.frame_set(1)
bpy.context.view_layer.update()
attach_cam()
if SHOT != "A":
    for fr in range(T(QUAKE) - 2, T(END) + 1, 2):
        t = (fr - 1) / FPS
        a = qamp(t) * 2.6
        F.rot(ME, "chest", fr, x=a * math.sin(t * 29) + 0.5 * math.sin(t * 7), y=a * 0.7 * math.sin(t * 23 + 1), z=a * 0.7 * math.sin(t * 19))
    sc.frame_set(T(DUCK))
    a = ME["arm"]
    a.keyframe_insert("location", frame=T(DUCK))
    loc = a.location.copy()
    for sd in ("L", "R"):
        F.rot(ME, f"thigh.{sd}", T(DUCK))
        F.rot(ME, f"shin.{sd}", T(DUCK), x=4)
        F.rot(ME, f"thigh.{sd}", T(DUCK + 0.6), x=-100)
        F.rot(ME, f"shin.{sd}", T(DUCK + 0.6), x=125)
    a.location = (loc.x, loc.y, -0.55)
    a.keyframe_insert("location", frame=T(DUCK + 0.6))
    # Handy: IK zur Hand vor der Kamera
    tgt = bpy.data.objects.new("ikR", None)
    sc.collection.objects.link(tgt)
    tgt.parent = cam
    for t, loc in ((PING - 0.1, (0.2, -0.5, -0.3)), (PING + 0.4, (0.06, -0.15, -0.36)), (26.9, (0.06, -0.15, -0.36)), (27.4, (0.2, -0.5, -0.3))):
        tgt.location = loc
        tgt.keyframe_insert("location", frame=T(t))
    tgt.rotation_euler = (math.radians(-60), 0, 0)
    c = ME["arm"].pose.bones["forearm.R"].constraints.new("IK")
    c.target = tgt
    c.chain_count = 2
    for t, v in ((0, 0.0), (PING - 0.15, 0.0), (PING + 0.35, 1.0), (26.9, 1.0), (27.4, 0.0)):
        c.influence = v
        c.keyframe_insert("influence", frame=T(t) if t else 1)
    myph = phone("myphone", phone_mat([(0, 0.0), (EEW - 0.02, 0.0), (EEW, 1.0)]))
    myph.parent = tgt
    myph.location = (0, 0, 0)
    myph.rotation_euler = (math.radians(-48), 0, 0)
    vis(myph, [(0, False), (PING, True), (27.4, False)])
    ME["arms_busy"] = {"R": True}

    # ---------- Beben: Masten, Leitungen, Schilder, Automaten, Klimageräte, Autos ----------
    def wobble(o, amp_deg, freq, k, axes=(0, 1)):
        base = o.rotation_euler.copy()
        for fr in range(T(QUAKE) - 2, T(END) + 1, 2):
            t = (fr - 1) / FPS
            a = qamp(t)
            r = base.copy()
            for ax in axes:
                r[ax] = base[ax] + math.radians(amp_deg * a * math.sin(t * freq + k * (1.3 + ax)))
            o.rotation_euler = r
            o.keyframe_insert("rotation_euler", frame=fr)
    for k, p in enumerate(S["poles"]):
        wobble(p, 2.4, 4.8, k)
    for k, (w, ax) in enumerate(S["wires"]):
        wobble(w, 26, 3.2 + (k % 5) * 0.35, k, axes=(1,) if ax == "y" else (0,))
    for k, o in enumerate(S["signs"] + S["vms"] + S["shake"]):
        wobble(o, 3.0, 8.5 + k % 3, k)
    # Fahrräder kippen, Töpfe fallen
    for k, (b, tf) in enumerate(zip(S["bikes"], (QUAKE + 0.9, QUAKE + 2.1))):
        b.keyframe_insert("rotation_euler", frame=T(tf))
        b.rotation_euler.y += math.radians(85 if k else -85)
        b.keyframe_insert("rotation_euler", frame=T(tf + 0.45))
    EV = {"bike": [QUAKE + 1.35, QUAKE + 2.55], "pot": []}
    for k, pt in enumerate(S["pots"]):
        tf = QUAKE + 1.4 + k * 0.6
        pt.keyframe_insert("rotation_euler", frame=T(tf))
        pt.keyframe_insert("location", frame=T(tf))
        pt.rotation_euler = (0, math.radians(-88 if k % 2 else 88), R.uniform(-0.6, 0.6))
        pt.location.z = 0.18
        pt.keyframe_insert("rotation_euler", frame=T(tf + 0.35))
        pt.keyframe_insert("location", frame=T(tf + 0.35))
        EV["pot"].append(tf + 0.35)
    # Dachziegel vom Haus links vorne
    near = min((h for h in S["houses"] if h[1] < 0), key=lambda h: abs(h[2] - 20.5))
    tile_m = F.ink_mat("tile", (0.3, 0.34, 0.44), 0.62)
    EV["tile"] = []
    for k in range(10):
        y = near[2] - 2.5 + k * 0.55
        tl = ST.box(f"tile{k}", (-4.4, y, near[4] + 0.3), (0.45, 0.32, 0.05), tile_m)
        tf = QUAKE + 2.0 + R.uniform(0, 3.0)
        tl.keyframe_insert("location", frame=T(tf))
        tl.keyframe_insert("rotation_euler", frame=T(tf))
        z0 = near[4] + 0.3
        tland = math.sqrt(2 * z0 / 9.81)
        for st in range(1, 9):
            u = st / 8
            tt = tf + u * tland
            tl.location = (-4.4 + 1.6 * u, y, max(0.03, z0 - 0.5 * 9.81 * (u * tland) ** 2))
            tl.rotation_euler = (R.uniform(-1, 1) * u * 3, u * 4, R.uniform(-1, 1) * u)
            tl.keyframe_insert("location", frame=T(tt))
            tl.keyframe_insert("rotation_euler", frame=T(tt))
        EV["tile"].append(tf + tland)
    json.dump(EV, open(os.path.join(ROOT, "src", "futaba2", "events.json"), "w"), indent=1)

# ---------- Render ----------
import toonlib as TL
humans = {f["arm"] for f in P.values()}
for i, o in enumerate(bpy.data.objects):
    q, hum = o, False
    while q is not None:
        if q in humans:
            hum = True
            break
        q = q.parent
    o.pass_index = 10000 + i if hum else 1 + i
TL.comp_outlines(kn=1.2, kd=0.5, thr=0.55)
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = int(os.environ.get("SAMPLES", 8))
sc.render.fps = FPS
sc.frame_start, sc.frame_end = frame_range
pct = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 67
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, pct
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGB"
sc.render.use_overwrite = False  # Fortsetzen nach Abbruch
sc.render.use_placeholder = False
sc.render.filepath = sys.argv[-2] if sys.argv[-1].isdigit() else "/tmp/f2_"
