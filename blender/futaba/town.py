# „Futaba, 11. März 2011“ – Testclip: Heimweg mit Sota, Handy-Nachricht, Erdbeben-Warnung, Beben. Comic-Look, Ich-Sicht.
# blender -b --python town.py -a -- <ausgabe_präfix> <prozent>
import bpy, sys, os, math, random, json
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
import toonlib as TL
from toonlib import P, sc

FPS = 24
T = lambda s: int(round(s * FPS)) + 1
TEX = os.path.join(HERE, "tex")
R = random.Random(7)

# ---------- Zeitplan (Sekunden) ----------
PING = 4.6        # Nachricht von Mama
STOP = 8.1        # alle bleiben stehen
ALARM = 8.1       # Erdbeben-Frühwarnung auf allen Handys
QUAKE = 9.8       # Beben beginnt
DUCK = 10.9       # ich gehe in die Hocke
END = 16.0
LINE_AT = {"s1": 0.5, "m1": 3.3, "s2": 5.4, "m2": 6.8, "s3": 8.9, "s4": 10.4, "m3": 13.6}


def quake_amp(t):
    if t < QUAKE:
        return 0.0
    return min(1.0, (t - QUAKE) / 0.8) * (0.85 + 0.15 * math.sin(t * 1.3))


# ---------- Bausteine ----------
_mats = {}


def flat(col):
    k = tuple(round(c, 3) for c in col)
    if k not in _mats:
        _mats[k] = TL.flat_mat("c%d" % len(_mats), col)
    return _mats[k]


def texmat(name, file, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(os.path.join(TEX, file))
    nt.links.new(t.outputs[0], p.inputs["Base Color"])
    if emit:
        nt.links.new(t.outputs[0], p.inputs["Emission Color"])
        p.inputs["Emission Strength"].default_value = emit
    TL.toonify(m)
    return m


def box(name, loc, size, m, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def textured_plane(name, loc, w, h, m, rot):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (w, h, 1)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    return o


def cyl(name, loc, r, h, m, verts=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    return o


def prism_roof(name, cx, cy, w, l, z, rise, m, over=0.45):
    """Satteldach, First entlang y."""
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    hw, hl = w / 2 + over, l / 2 + over
    v = [bm.verts.new(p) for p in ((-hw, -hl, 0), (hw, -hl, 0), (0, -hl, rise), (-hw, hl, 0), (hw, hl, 0), (0, hl, rise))]
    for f in ((0, 1, 2), (3, 5, 4), (0, 2, 5, 3), (1, 4, 5, 2), (0, 3, 4, 1)):
        bm.faces.new([v[i] for i in f])
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    o.location = (cx, cy, z)
    o.data.materials.append(m)
    sol = o.modifiers.new("s", "SOLIDIFY")
    sol.thickness = 0.12
    return o


# ---------- Straße ----------
ASPH = flat((0.42, 0.43, 0.46))
box("road", (0, 40, -0.05), (6.4, 140, 0.1), ASPH)
box("verge_l", (-4.2, 40, -0.04), (2.0, 140, 0.1), flat((0.66, 0.65, 0.6)))
box("verge_r", (4.2, 40, -0.04), (2.0, 140, 0.1), flat((0.66, 0.65, 0.6)))
WHITE = flat((0.95, 0.95, 0.92))
for x in (-3.0, 3.0):
    box("line", (x, 40, 0.005), (0.12, 140, 0.01), WHITE)
box("field", (0, 40, -0.12), (200, 260, 0.1), flat((0.55, 0.6, 0.42)))

# ---------- Häuser ----------
WALLS = [(0.93, 0.9, 0.82), (0.86, 0.86, 0.84), (0.9, 0.84, 0.72), (0.78, 0.84, 0.88), (0.95, 0.93, 0.88), (0.82, 0.78, 0.7)]
ROOFS = [(0.27, 0.3, 0.38), (0.38, 0.26, 0.22), (0.22, 0.24, 0.27), (0.3, 0.36, 0.42)]
WIN = flat((0.28, 0.36, 0.44))
SHUT = flat((0.7, 0.72, 0.74))
shop_i = 0
houses = []
for side in (-1, 1):
    y = -12.0
    while y < 92:
        l = R.uniform(6.5, 9.5)
        w = R.uniform(6.5, 8.5)
        hgt = R.choice((5.6, 5.8, 3.2)) if abs(y - 40) > 3 else 5.6
        cx = side * (5.6 + w / 2)
        cy = y + l / 2
        wall = flat(R.choice(WALLS))
        hb = box(f"house{len(houses)}", (cx, cy, hgt / 2), (w, l, hgt), wall)
        roof = prism_roof(f"roof{len(houses)}", cx, cy, w, l, hgt, R.uniform(1.4, 2.1), flat(R.choice(ROOFS)))
        houses.append((hb, roof, side, cy))
        fx = side * 5.6 - side * 0.02  # Straßenseite der Fassade
        is_shop = R.random() < 0.45 and shop_i < 6
        if is_shop:
            sm = texmat(f"shopm{shop_i}", f"shop{shop_i}.png")
            textured_plane(f"shopsign{shop_i}", (fx - side * 0.05, cy, 3.25), 0.9, min(4.5, l - 1.5), sm,
                           (math.radians(90), 0, math.radians(90 if side < 0 else -90)))
            box("glass", (fx - side * 0.01, cy, 1.25), (0.06, l - 2.0, 2.2), flat((0.55, 0.7, 0.78)))
            for k in range(int((l - 2) / 0.9)):
                box("mullion", (fx - side * 0.04, cy - (l - 2) / 2 + 0.45 + k * 0.9, 1.25), (0.04, 0.06, 2.2), flat((0.3, 0.3, 0.32)))
            shop_i += 1
        else:
            box("door", (fx - side * 0.01, cy - l / 4, 1.05), (0.06, 1.0, 2.1), flat((0.45, 0.33, 0.24)))
            box("win", (fx - side * 0.01, cy + l / 5, 1.5), (0.06, 1.8, 1.1), WIN)
        if hgt > 4:
            for k in (-1, 1):
                box("win2", (fx - side * 0.01, cy + k * l / 4, 4.2), (0.06, 1.5, 1.0), WIN)
            box("rail", (fx - side * 0.35, cy, 3.4), (0.7, l * 0.6, 0.06), flat((0.35, 0.35, 0.36)))
        # Mäuerchen zwischen den Häusern
        gap = R.uniform(1.2, 2.8)
        box("wall", (side * 5.0, y + l + gap / 2, 0.55), (0.18, gap, 1.1), flat((0.72, 0.71, 0.68)))
        y += l + gap

# ---------- Strommasten + Leitungen ----------
POLE = flat((0.62, 0.62, 0.6))
DARK = flat((0.12, 0.12, 0.13))
poles = []
for k, y in enumerate(range(-8, 96, 26)):
    x = 3.45
    pv = bpy.data.objects.new(f"pole{k}", None)
    sc.collection.objects.link(pv)
    pv.location = (x, y, 0)
    c = cyl("polec", (0, 0, 4.6), 0.14, 9.2, POLE)
    c.parent = pv
    a = box("arm", (0, 0, 8.4), (1.8, 0.12, 0.12), POLE, parent=pv)
    a2 = box("arm2", (0, 0, 7.6), (1.4, 0.12, 0.12), POLE, parent=pv)
    if k % 2 == 0:
        tr = cyl("trafo", (0.35, 0, 6.6), 0.26, 0.9, flat((0.55, 0.57, 0.58)))
        tr.parent = pv
    poles.append(pv)
wires = []


def wire(p0, p1, sag, name="wire"):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.012
    mid = (p0 + p1) / 2
    sp = cu.splines.new("POLY")
    n = 14
    sp.points.add(n - 1)
    for i in range(n):
        u = i / (n - 1)
        q = p0.lerp(p1, u) - mid
        q.z -= sag * 4 * u * (1 - u)
        sp.points[i].co = (q.x, q.y, q.z, 1)
    o = bpy.data.objects.new(name, cu)
    sc.collection.objects.link(o)
    o.location = mid
    o.data.materials.append(DARK)
    wires.append((o, (p1 - p0).normalized()))
    return o


for a, b in zip(poles, poles[1:]):
    for dx, z in ((-0.8, 8.45), (0.0, 8.45), (0.8, 8.45), (-0.6, 7.65), (0.6, 7.65)):
        wire(a.location + Vector((dx, 0, z)), b.location + Vector((dx, 0, z)), R.uniform(0.35, 0.6))
    # Hausanschluss über die Straße
    wire(a.location + Vector((-0.6, 0, 7.6)), Vector((-5.6, a.location.y + 3, 5.2)), 0.2, "drop")

# ---------- Getränkeautomaten, Fahrrad-Ständer, Kram ----------
VM = texmat("vend", "vending.png", emit=0.6)
vms = []
for k, y in enumerate((13.0, 13.85)):
    v = box(f"vm{k}", (4.75, y, 0.92), (0.75, 0.8, 1.84), flat((0.9, 0.9, 0.9)))
    textured_plane("vmf", (4.37, y, 0.95), 0.76, 1.7, VM, (math.radians(90), 0, math.radians(-90))).parent = v
    vms.append(v)
pots = []
for k in range(5):
    y = 20 + k * 0.6
    pt = cyl(f"pot{k}", (-4.9, y, 0.18), 0.17, 0.36, flat((0.65, 0.35, 0.2)))
    pl = cyl("plant", (-4.9, y, 0.45), 0.2, 0.3, flat((0.3, 0.55, 0.3)), verts=8)
    pl.parent = pt
    pl.location = (0, 0, 0.27)
    pots.append(pt)

# Schild über der Straße (Futaba)
SIGN_Y = 74
SG = texmat("signm", "sign_futaba.png")
for x in (-3.6, 3.6):
    box("signpost", (x, SIGN_Y, 3.1), (0.25, 0.25, 6.2), flat((0.5, 0.52, 0.55)))
sframe = box("signframe", (0, SIGN_Y, 5.6), (7.6, 0.18, 1.05), flat((0.5, 0.52, 0.55)))
textured_plane("signface", (0, SIGN_Y - 0.1, 5.6), 7.4, 0.92, SG, (math.radians(90), 0, 0))

# Hügel + Himmel
HILL = flat((0.4, 0.55, 0.38))
for k, (x, y, s) in enumerate(((-40, 150, 40), (10, 170, 55), (55, 140, 35), (-80, 90, 45), (80, 80, 40))):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1, location=(x, y, -s * 0.55))
    hl = bpy.context.object
    hl.scale = (s * 1.6, s, s)
    hl.data.materials.append(HILL)
w = sc.world or bpy.data.worlds.new("w")
sc.world = w
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.66, 0.76, 0.86, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.9
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sc.collection.objects.link(sun)
sun.data.energy = 3.2
sun.data.angle = math.radians(3)
sun.rotation_euler = (math.radians(50), math.radians(-25), math.radians(-35))

# ---------- Menschen ----------
TL.toon_all()
CAST = {
    "me": dict(gender=1.0, age=0.3, skin="young_asian_male", hair="short01", clothes=("male_casualsuit03", "shoes02")),
    "sota": dict(gender=1.0, age=0.3, skin="young_asian_male", hair="short02", clothes=("male_casualsuit02", "shoes01"), eyebrows="eyebrow003"),
    "g1": dict(gender=0.0, age=0.3, skin="young_asian_female", hair="ponytail01", clothes=("female_casualsuit01", "shoes03")),
    "g2": dict(gender=0.0, age=0.3, skin="young_asian_female", hair="bob02", clothes=("female_casualsuit02", "shoes03")),
    "oma": dict(gender=0.0, age=0.9, weight=0.6, skin="old_asian_female", hair="bob01", clothes=("female_elegantsuit01", "shoes04")),
    "mann": dict(gender=1.0, age=0.55, weight=0.65, skin="middleage_asian_male", hair="short04", clothes=("male_worksuit01", "shoes01")),
}
SKIN = {"me": (0.95, 0.78, 0.64), "sota": (0.93, 0.74, 0.58), "g1": (0.97, 0.82, 0.7), "g2": (0.95, 0.8, 0.68), "oma": (0.9, 0.74, 0.62), "mann": (0.86, 0.66, 0.5)}
HAIR = {"me": (0.08, 0.07, 0.07), "sota": (0.12, 0.08, 0.06), "g1": (0.1, 0.07, 0.06), "g2": (0.2, 0.12, 0.08), "oma": (0.75, 0.75, 0.74), "mann": (0.14, 0.13, 0.13)}
CLOTH = {"me": (0.18, 0.22, 0.34), "sota": (0.2, 0.24, 0.36), "g1": (0.18, 0.22, 0.36), "g2": (0.18, 0.22, 0.36), "oma": (0.5, 0.4, 0.55), "mann": (0.35, 0.42, 0.3)}
PP = {}
for nm, kw in CAST.items():
    kw = dict(kw)
    p = P.make_person(nm, race=("asian", 1.0), **kw)
    TL.toon_all()
    TL.toon_person(p, SKIN[nm], HAIR[nm])
    for o in [o for o in bpy.data.objects if o.parent in (p["h"], p["rig"]) and o.type == "MESH"]:
        n = o.name.lower()
        if "suit" in n:
            o.data.materials.clear()
            o.data.materials.append(flat(CLOTH[nm]))
    PP[nm] = p
ME, SOTA = PP["me"], PP["sota"]
for o in bpy.data.objects:
    if o.parent in (ME["h"], ME["rig"]) and any(k in o.name.lower() for k in ("short01", "eyebrow", "eyelash", "low-poly", "teeth", "tongue", "me_eye", "me_pup")):
        o.hide_render = True
for o in ME["eyes"]:
    o.hide_render = True

# Wege
V = lambda x, y: Vector((x, y, 0))
SPEED = 1.15
TL.locomotion(ME, [V(0.55, 0), V(0.55, SPEED * STOP)], 1, SPEED, until=T(STOP), spine=False)
TL.locomotion(SOTA, [V(-0.22, 0.7), V(-0.22, 0.7 + SPEED * STOP)], 1, SPEED, until=T(STOP))
TL.locomotion(PP["g1"], [V(-1.3, 7.5), V(-1.3, 7.5 + 1.05 * 8.4)], 1, 1.05, until=T(STOP + 0.3))
TL.locomotion(PP["g2"], [V(-0.75, 7.9), V(-0.75, 7.9 + 1.05 * 8.4)], 1, 1.05, until=T(STOP + 0.3))
TL.locomotion(PP["oma"], [V(2.3, 22.0), V(2.3, 22.0 - 0.6 * 9)], 1, 0.6, until=T(STOP + 0.2))
mann = PP["mann"]
mann["rig"].location = (3.8, 13.4, 0)
mann["rig"].rotation_euler = (0, 0, math.pi / 2)  # schaut zum Automaten (+x)
mann["rig"].keyframe_insert("location", frame=1)
mann["rig"].keyframe_insert("rotation_euler", frame=1)
for nm in ("me", "sota", "g1", "g2", "oma"):
    TL.stand(PP[nm], T(STOP + 0.5), spine=(nm != "me"))
TL.stand(mann, 1)
P.rot(mann, "upperarm01.R", 1, x=55, z=30)
P.rot(mann, "lowerarm01.R", 1, x=50)
P.rot(mann, "upperarm01.R", T(4.0), x=55, z=30)
P.rot(mann, "upperarm01.R", T(4.6), z=40)
P.rot(mann, "lowerarm01.R", T(4.6), x=12)

# Handys: alle holen beim Alarm ihr Handy raus
PHONE = flat((0.12, 0.12, 0.14))
SCREEN = texmat("screen", "phone_eew.png", emit=1.4)
MYSCREEN = bpy.data.materials.new("myscreen")
MYSCREEN.use_nodes = True
_nt = MYSCREEN.node_tree
for _n in list(_nt.nodes):
    _nt.nodes.remove(_n)
_o = _nt.nodes.new("ShaderNodeOutputMaterial")
_a = _nt.nodes.new("ShaderNodeTexImage"); _a.image = bpy.data.images.load(os.path.join(TEX, "phone_msg.png"))
_b = _nt.nodes.new("ShaderNodeTexImage"); _b.image = bpy.data.images.load(os.path.join(TEX, "phone_eew.png"))
_mx = _nt.nodes.new("ShaderNodeMix"); _mx.data_type = "RGBA"
_nt.links.new(_a.outputs[0], _mx.inputs[6]); _nt.links.new(_b.outputs[0], _mx.inputs[7])
_em = _nt.nodes.new("ShaderNodeEmission"); _em.inputs[1].default_value = 1.0
_nt.links.new(_mx.outputs[2], _em.inputs[0]); _nt.links.new(_em.outputs[0], _o.inputs[0])
MYSCREEN["toon"] = 1


def phone_obj(name, scr=None):
    b = box(name, (0, 0, 0), (0.07, 0.009, 0.145), PHONE)
    s = textured_plane(name + "s", (0, -0.0055, 0), 0.062, 0.13, scr or SCREEN, (math.radians(90), 0, 0))
    s.parent = b
    return b


def show(o, frames):
    """frames: [(frame, sichtbar)]"""
    for ob in [o] + list(o.children):
        for f, v in frames:
            ob.hide_render = not v
            ob.keyframe_insert("hide_render", frame=f)


for k, nm in enumerate(("sota", "g1", "g2", "oma", "mann")):
    p = PP[nm]
    ph = phone_obj(f"phone_{nm}")
    ph.parent = p["rig"]
    ph.parent_type = "BONE"
    ph.parent_bone = "wrist.R"
    ph.location = (0, 0.08, -0.02)
    ph.rotation_euler = (math.radians(-80), 0, 0)
    t0 = ALARM + 0.15 + k * 0.12
    show(ph, [(1, False), (T(t0 + 0.25), True), (T(QUAKE + 0.9), False)])
    P.rot(p, "upperarm01.R", T(t0), z=40)
    P.rot(p, "lowerarm01.R", T(t0), x=12)
    P.rot(p, "upperarm01.R", T(t0 + 0.45), x=48, z=22)
    P.rot(p, "lowerarm01.R", T(t0 + 0.45), x=95)
    P.rot(p, "upperarm01.R", T(QUAKE + 0.3), x=48, z=22)
    P.rot(p, "lowerarm01.R", T(QUAKE + 0.3), x=95)
    P.rot(p, "neck01", T(t0), x=0)
    P.rot(p, "neck01", T(t0 + 0.4), x=22)
    P.rot(p, "neck01", T(QUAKE + 0.2), x=22)
    P.rot(p, "neck01", T(QUAKE + 0.6), x=-8)
    P.set_face(p, 1, "neutral")
    P.set_face(p, T(t0 + 0.4), "worried", 0.8)
    P.set_face(p, T(QUAKE + 0.5), "fear", 1.0)

# Beben: alle gehen in die Hocke, Hände über den Kopf
def crouch(p, t, dz=-0.42, cover=True):
    rig = p["rig"]
    f0, f1 = T(t), T(t + 0.55)
    loc = rig.location.copy()
    rig.keyframe_insert("location", frame=f0)
    for sd in ("L", "R"):
        P.rot(p, f"upperleg01.{sd}", f0)
        P.rot(p, f"lowerleg01.{sd}", f0, x=3)
        P.rot(p, f"upperleg01.{sd}", f1, x=-100)
        P.rot(p, f"lowerleg01.{sd}", f1, x=128)
        P.rot(p, f"foot.{sd}", f1, x=-28)
        if cover:
            P.rot(p, f"upperarm01.{sd}", f1, x=150, z=(-25 if sd == "L" else 25))
            P.rot(p, f"lowerarm01.{sd}", f1, x=115)
    P.rot(p, "spine03", f0)
    P.rot(p, "spine03", f1, x=28)
    rig.location = (loc.x, loc.y, dz)
    rig.keyframe_insert("location", frame=f1)


bpy.context.view_layer.update()
for nm, dt in (("sota", 0.75), ("g1", 0.45), ("g2", 0.55), ("oma", 0.9), ("mann", 0.6)):
    sc.frame_set(T(QUAKE + dt))
    crouch(PP[nm], QUAKE + dt)
sc.frame_set(1)
# Sota dreht den Kopf zu mir (rechts von ihm = negativ)
for t, y in ((0.4, 0), (0.9, -38), (2.8, -38), (3.4, -10), (5.2, -10), (5.6, -40), (6.6, -40), (7.2, 0), (STOP + 0.6, 0), (8.9, -40), (10.2, -40),
             (10.5, -45), (12.4, -45), (13.0, 10), (END, 10)):
    P.rot(SOTA, "neck01", T(t), y=y, x=(22 if ALARM + 0.6 < t < QUAKE + 0.3 else 0))
P.set_face(SOTA, T(0.4), "neutral", 1.0, extra={"mouth-corners-up": 0.0} if False else None)
P.set_face(SOTA, T(5.4), "neutral")
P.set_face(SOTA, T(10.4), "fear", 1.0)
for p, ts in ((SOTA, (2.1, 4.4, 7.0, 12.0)), (PP["g1"], (3.0, 9.0)), (PP["g2"], (5.0,)), (PP["oma"], (2.5, 6.0)), (PP["mann"], (1.5, 5.5))):
    for t in ts:
        P.blink(p, T(t))
        TL.eye_blink(p, T(t))
for nm in ("g1", "g2", "oma", "mann"):
    P.idle(PP[nm], 1, T(END), seed=hash(nm) % 50)

# ---------- Ich: Kamera, Blick, Handy ----------
sc.frame_set(1)
bpy.context.view_layer.update()
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 15
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 30
cam.data.clip_start = 0.03
rig = ME["rig"]
cam.parent = rig
cam.parent_type = "BONE"
cam.parent_bone = "head"
bpy.context.view_layer.update()
eye = rig.matrix_world @ Vector((0, -0.16, 1.6))
cam.matrix_world = Matrix.Translation(eye) @ Euler((math.radians(90), 0, 0), "XYZ").to_matrix().to_4x4()


def head_track(p, keys):
    for t, yaw, pitch in keys:
        f = T(t)
        P.rot(p, "spine03", f, y=yaw * 0.25, x=-pitch * 0.2)
        P.rot(p, "neck01", f, y=yaw * 0.4, x=-pitch * 0.4)
        P.rot(p, "head", f, y=yaw * 0.35, x=-pitch * 0.4)


# Blick (gier + = links, nick + = hoch)
head_track(ME, [(0, 0, -4), (0.6, 4, -3), (1.1, 50, -6), (2.9, 48, -6), (3.6, 4, -2), (4.7, 2, -8), (5.1, 0, -38), (6.6, 2, -36),
                (7.0, 46, -10), (7.8, 6, -30), (8.3, 2, -32), (8.8, -2, -4), (9.2, 48, -6), (9.9, 46, -6), (10.6, 4, 20), (11.6, -10, 30),
                (12.6, -40, 2), (13.6, -4, 4), (14.6, 52, -14), (END, 54, -16)])
ME_SPINE = None
# Beben: Wackeln
for f in range(1, T(END) + 1):
    t = (f - 1) / FPS
    a = 3.2 * quake_amp(t)
    if f % 2 == 0 and a > 0:
        P.rot(ME, "neck02", f, x=a * math.sin(t * 31) + 0.6 * math.sin(t * 7), y=a * 0.6 * math.sin(t * 27 + 1), z=a * 0.6 * math.sin(t * 19))
P.rot(ME, "neck02", T(QUAKE) - 1)
# Ich gehe in die Hocke
sc.frame_set(T(DUCK))
crouch(ME, DUCK, dz=-0.55, cover=False)
sc.frame_set(1)
# Handy in meiner rechten Hand (IK zu einem Ziel vor der Kamera)
tgt = bpy.data.objects.new("ikR", None)
sc.collection.objects.link(tgt)
tgt.parent = cam
tgt.location = (0.05, -0.17, -0.36)
tgt.rotation_euler = (math.radians(-30), 0, 0)
for t, loc in ((PING, (0.12, -0.45, -0.25)), (PING + 0.5, (0.05, -0.17, -0.37)), (8.3, (0.05, -0.17, -0.37)), (8.8, (0.04, -0.14, -0.35)),
               (QUAKE + 0.6, (0.06, -0.2, -0.3)), (QUAKE + 1.0, (0.18, -0.55, -0.25))):
    tgt.location = loc
    tgt.keyframe_insert("location", frame=T(t))
c = rig.pose.bones["wrist.R"].constraints.new("IK")
c.target = tgt
c.chain_count = 5
c.use_tail = True
for t, v in ((0, 0), (PING - 0.1, 0), (PING + 0.4, 1), (QUAKE + 0.8, 1), (QUAKE + 1.1, 0)):
    c.influence = v
    c.keyframe_insert("influence", frame=T(t) if t else 1)
myphone = phone_obj("myphone", MYSCREEN)
for t, v in ((0, 0.0), (ALARM, 0.0), (ALARM + 0.05, 1.0)):
    _mx.inputs[0].default_value = v
    _mx.inputs[0].keyframe_insert("default_value", frame=T(t) if t else 1)
myphone.parent = tgt
myphone.location = (0, 0.0, 0.0)
myphone.rotation_euler = (math.radians(-60), 0, 0)
show(myphone, [(1, False), (T(PING + 0.1), True), (T(QUAKE + 1.0), False)])

EVENTS = {}
# ---------- Beben: Masten, Leitungen, Automaten, Töpfe, Dachziegel ----------
for k, pv in enumerate(poles):
    for f in range(T(QUAKE) - 2, T(END) + 1, 2):
        t = (f - 1) / FPS
        a = quake_amp(t)
        pv.rotation_euler = (math.radians(2.2 * a * math.sin(t * 5.1 + k)), math.radians(1.8 * a * math.sin(t * 4.3 + k * 2)), 0)
        pv.keyframe_insert("rotation_euler", frame=f)
for k, (o, d) in enumerate(wires):
    axis = 1 if abs(d.y) > abs(d.x) else 0
    for f in range(T(QUAKE) - 2, T(END) + 1, 2):
        t = (f - 1) / FPS
        a = quake_amp(t)
        r = [0.0, 0.0, 0.0]
        r[axis] = math.radians(28 * a * math.sin(t * (3.0 + (k % 5) * 0.4) + k))
        o.rotation_euler = r
        o.keyframe_insert("rotation_euler", frame=f)
for k, v in enumerate(vms):
    for f in range(T(QUAKE) - 2, T(END) + 1, 2):
        t = (f - 1) / FPS
        a = quake_amp(t)
        v.rotation_euler = (math.radians(3.5 * a * math.sin(t * 9 + k)), math.radians(2.0 * a * math.sin(t * 7)), 0)
        v.keyframe_insert("rotation_euler", frame=f)
for k, pt in enumerate(pots):  # Blumentöpfe kippen um
    tf = QUAKE + 1.2 + k * 0.5
    EVENTS.setdefault("pot", []).append(round(tf + 0.35, 3))
    pt.keyframe_insert("rotation_euler", frame=T(tf))
    pt.keyframe_insert("location", frame=T(tf))
    pt.rotation_euler = (0, math.radians(-85 if k % 2 else 85), R.uniform(-0.5, 0.5))
    pt.location.z = 0.17
    pt.location.x += 0.15 * (1 if k % 2 else -1)
    pt.keyframe_insert("rotation_euler", frame=T(tf + 0.35))
    pt.keyframe_insert("location", frame=T(tf + 0.35))
# Dachziegel rutschen vom Haus rechts vorne und fallen auf die Straße
TILE = flat((0.27, 0.3, 0.38))
for k in range(9):
    y = 17.0 + k * 0.7
    tl = box(f"tile{k}", (5.4, y, 5.75), (0.5, 0.3, 0.05), TILE)
    tf = QUAKE + 1.8 + R.uniform(0, 2.5)
    EVENTS.setdefault("tile", []).append(round(tf + 0.97, 3))
    tl.keyframe_insert("location", frame=T(tf))
    tl.keyframe_insert("rotation_euler", frame=T(tf))
    steps = 10
    for s in range(1, steps + 1):
        u = s / steps
        tt = tf + u * 1.0
        tl.location = (5.4 - 1.8 * u, y + R.uniform(-0.05, 0.05), max(0.03, 5.75 - 9.81 * 0.5 * u * u * 1.2))
        tl.rotation_euler = (R.uniform(-1, 1) * u * 3, u * 4, R.uniform(-1, 1) * u)
        tl.keyframe_insert("location", frame=T(tt))
        tl.keyframe_insert("rotation_euler", frame=T(tt))
# Ladenschild verrutscht
for o in bpy.data.objects:
    if o.name.startswith("shopsign"):
        k = int(o.name[8:9] or 0)
        for f in range(T(QUAKE) - 2, T(END) + 1, 2):
            t = (f - 1) / FPS
            o.rotation_euler.y = math.radians(4 * quake_amp(t) * math.sin(t * 6 + k))
            o.keyframe_insert("rotation_euler", frame=f)

# ---------- Lippen ----------
TIM = json.load(open(os.path.join(HERE, "..", "..", "src", "futaba", "timing.json")))
SCR = json.load(open(os.path.join(HERE, "..", "..", "src", "futaba", "script.json")))
json.dump(LINE_AT, open(os.path.join(HERE, "..", "..", "src", "futaba", "line_at.json"), "w"))
json.dump(dict(EVENTS, ping=PING, alarm=ALARM, quake=QUAKE, stop=STOP, duck=DUCK, end=END), open(os.path.join(HERE, "..", "..", "src", "futaba", "events.json"), "w"), indent=1)


def lipsync(p, wav, t0):
    import wave as _w, numpy as _np
    with _w.open(wav) as wf:
        sr = wf.getframerate()
        a = _np.frombuffer(wf.readframes(wf.getnframes()), dtype=_np.int16).astype(float)
    hop = sr // FPS
    rms = [_np.sqrt(_np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)]
    mx = max(rms) or 1
    kb = p["h"].data.shape_keys.key_blocks.get("ex_mouth-open")
    if kb is None:
        return
    f0 = T(t0)
    kb.value = 0
    kb.keyframe_insert("value", frame=f0 - 2)
    for i, r in enumerate(rms[::2]):
        kb.value = min(1.0, (r / mx) ** 0.7 * 0.9)
        kb.keyframe_insert("value", frame=f0 + i * 2)
    kb.value = 0
    kb.keyframe_insert("value", frame=f0 + len(rms) + 2)


for s, ln in zip(SCR["sentences"], TIM["lines"]):
    if s["id"].startswith("s"):
        lipsync(SOTA, os.path.join(HERE, "..", "..", "public", ln["file"]), LINE_AT[s["id"]])

# ---------- Render ----------
TL.outlines(2.0)
OUTL = os.environ.get("OUTL", "comp")
# Leitungen/Hügel/Boden ohne Freestyle-Umrisse (spart viel Zeit; Leitungen sind ohnehin dunkel)
noline = bpy.data.collections.new("noline")
sc.collection.children.link(noline)
for o in [w for w, _ in wires] + [o for o in bpy.data.objects if o.name.startswith(("Sphere", "field", "road", "verge"))]:
    for c in list(o.users_collection):
        c.objects.unlink(o)
    noline.objects.link(o)
ls = sc.view_layers[0].freestyle_settings.linesets[0]
ls.select_by_collection = True
ls.collection = noline
ls.collection_negation = "EXCLUSIVE"
for k in ("shadow_ray_count", "shadow_step_count"):
    if hasattr(sc.eevee, k):
        setattr(sc.eevee, k, 1)
if hasattr(sc.eevee, "shadow_resolution_scale"):
    sc.eevee.shadow_resolution_scale = 0.5
if OUTL == "comp":
    TL.mark_indices(list(PP.values()))
    TL.comp_outlines(kn=float(os.environ.get("KN", 1.5)), kd=float(os.environ.get("KD", 0.4)), thr=float(os.environ.get("THR", 0.6)))
for o in bpy.data.objects:
    for m in getattr(o, "modifiers", []):
        if m.type == "SUBSURF":
            m.render_levels = 1 if o in (SOTA["h"],) else 0
            m.levels = 0
sc.frame_start, sc.frame_end = 1, T(END)
sc.render.fps = FPS
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 4
pct = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 50
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, pct
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = sys.argv[-2] if sys.argv[-1].isdigit() else "/tmp/futaba_"
