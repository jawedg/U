# POV-Klassenzimmer „Plan Rot“ (Blender, EEVEE). Aufruf:
#   blender -b --python classroom.py -- <ausgabe_präfix> [prozent]   und dann -a / -f N
import bpy, math, random, sys, os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 24
random.seed(7)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
T = lambda s: int(round(s * FPS)) + 1  # Sekunde -> Bild


# ---------- Materialien ----------
def mat(name, col, rough=0.6, metal=0.0, emit=None, strength=0.0, tex=None, noise=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if tex:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(os.path.join(HERE, tex))
        nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
        if emit is not None:
            nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
    if noise:
        n = nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = 40
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.blend_type = "MULTIPLY"
        mix.inputs["Fac"].default_value = noise
        mix.inputs["Color1"].default_value = (*col, 1)
        nt.links.new(n.outputs["Color"], mix.inputs["Color2"])
        nt.links.new(mix.outputs["Color"], b.inputs["Base Color"])
    if emit is not None:
        if not tex:
            b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


M = {
    "wall": mat("wall", (0.86, 0.84, 0.79), 0.9),
    "dado": mat("dado", (0.78, 0.72, 0.58), 0.8),
    "floor": mat("floor", (0.42, 0.45, 0.47), 0.45, noise=0.25),
    "ceil": mat("ceil", (0.92, 0.92, 0.9), 0.9, emit=(0.9, 0.9, 0.88), strength=0.35),
    "wood": mat("wood", (0.72, 0.53, 0.34), 0.5, noise=0.15),
    "metal": mat("metal", (0.55, 0.57, 0.6), 0.35, 0.8),
    "dark": mat("dark", (0.06, 0.06, 0.07), 0.5),
    "chair": mat("chair", (0.62, 0.42, 0.25), 0.55),
    "board": mat("board", (1, 1, 1), 0.7, tex="board.png"),
    "frame": mat("frame", (0.93, 0.93, 0.92), 0.4),
    "sky": mat("sky", (0.8, 0.88, 1.0), 0.2, emit=(0.8, 0.9, 1.0), strength=2.2),
    "panel": mat("panel", (1, 1, 1), 0.3, emit=(1.0, 0.98, 0.94), strength=6.0),
    "door": mat("door", (0.55, 0.38, 0.24), 0.5, noise=0.1),
    "locker": mat("locker", (0.58, 0.62, 0.66), 0.45, 0.4),
    "clock": mat("clock", (1, 1, 1), 0.5, tex="clockface.png"),
    "paper": mat("paper", (0.95, 0.95, 0.93), 0.8),
    "skin": mat("skin", (0.78, 0.57, 0.43), 0.55),
    "skin2": mat("skin2", (0.52, 0.34, 0.24), 0.55),
    "sleeve": mat("sleeve", (0.08, 0.16, 0.3), 0.85),
    "phone": mat("phone", (0.02, 0.02, 0.025), 0.25, 0.3),
    "scr1": mat("scr1", (1, 1, 1), 0.3, emit=(1, 1, 1), strength=1.4, tex="phone1.png"),
    "scr2": mat("scr2", (1, 1, 1), 0.3, emit=(1, 1, 1), strength=1.4, tex="phone2.png"),
    "hall": mat("hall", (0.7, 0.72, 0.7), 0.3, emit=(0.75, 0.78, 0.75), strength=1.2),
    "blind": mat("blind", (0.7, 0.72, 0.74), 0.6),
    "pin": mat("pin", (0.62, 0.48, 0.3), 0.9),
}
HOODIES = [(0.75, 0.2, 0.18), (0.2, 0.35, 0.6), (0.85, 0.75, 0.6), (0.25, 0.5, 0.35), (0.45, 0.45, 0.5), (0.9, 0.55, 0.2), (0.55, 0.3, 0.55), (0.15, 0.15, 0.18)]
HAIRS = [(0.06, 0.04, 0.03), (0.35, 0.2, 0.1), (0.75, 0.55, 0.3), (0.12, 0.08, 0.05), (0.55, 0.25, 0.12)]


def box(name, loc, size, m, rot=(0, 0, 0), bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(m)
    if bevel:
        bpy.ops.object.transform_apply(scale=True)
        b = o.modifiers.new("b", "BEVEL")
        b.width = bevel
        b.segments = 3
    if parent:
        o.parent = parent
    return o


def cyl(name, loc, r, depth, m, rot=(0, 0, 0), verts=16, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def ball(name, loc, scale, m, parent=None, seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    if parent:
        o.parent = parent
    return o


def kf(o, path, frame, val, idx=None):
    if idx is None:
        setattr(o, path, val)
        o.keyframe_insert(path, frame=frame)
    else:
        getattr(o, path)[idx] = val
        o.keyframe_insert(path, index=idx, frame=frame)


# ---------- Raum ----------
RX, RY, RZ = 4.5, 4.0, 3.2
box("floor", (0, 0, -0.05), (2 * RX, 2 * RY, 0.1), M["floor"])
box("ceil", (0, 0, RZ + 0.05), (2 * RX, 2 * RY, 0.1), M["ceil"])
box("wF", (0, RY + 0.05, RZ / 2), (2 * RX, 0.1, RZ), M["wall"])
box("wB", (0, -RY - 0.05, RZ / 2), (2 * RX, 0.1, RZ), M["wall"])
box("wR", (RX + 0.05, 0, RZ / 2), (0.1, 2 * RY, RZ), M["wall"])
box("wL", (-RX - 0.05, 0, RZ / 2), (0.1, 2 * RY, RZ), M["wall"])
# Sockel-/Brüstungsband
for n, loc, size in (("dF", (0, RY - 0.01, 0.5), (2 * RX, 0.02, 1.0)), ("dB", (0, -RY + 0.01, 0.5), (2 * RX, 0.02, 1.0)), ("dR", (RX - 0.01, 0, 0.5), (0.02, 2 * RY, 1.0)), ("dL", (-RX + 0.01, 0, 0.5), (0.02, 2 * RY, 1.0))):
    box(n, loc, size, M["dado"])
# Tafel + Rahmen + Ablage
box("boardframe", (0, RY - 0.03, 1.55), (4.2, 0.04, 1.4), M["metal"])
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, RY - 0.055, 1.55), rotation=(math.pi / 2, 0, 0))
bo = bpy.context.object
bo.scale = (4.0, 1.25, 1)
bo.data.materials.append(M["board"])
box("tray", (0, RY - 0.1, 0.9), (4.0, 0.12, 0.03), M["metal"])
# Uhr
cyl("clock", (1.6 + 1.0, RY - 0.04, 2.6), 0.18, 0.04, M["clock"], rot=(math.pi / 2, 0, math.pi), verts=48)
cyl("clockrim", (2.6, RY - 0.03, 2.6), 0.19, 0.035, M["dark"], rot=(math.pi / 2, 0, 0), verts=48)
hh = box("hourhand", (2.6, RY - 0.075, 2.6), (0.018, 0.005, 0.1), M["dark"])
mh = box("minhand", (2.6, RY - 0.08, 2.6), (0.012, 0.005, 0.15), M["dark"])
for h, ang, off in ((hh, -(10 + 41 / 60) / 12 * 2 * math.pi, 0.05), (mh, -41 / 60 * 2 * math.pi, 0.075)):
    h.location = (2.6 + math.sin(-ang) * off * 0 + math.sin(-ang) * off, RY - 0.075, 2.6 + math.cos(ang) * off)
    h.rotation_euler = (0, ang, 0)
# Fenster links (leuchtender Himmel), Rahmen, Jalousien
blinds = []
for k, y in enumerate((-2.6, -0.4, 1.8)):
    box(f"sky{k}", (-RX + 0.02, y, 1.95), (0.02, 1.8, 1.5), M["sky"])
    box(f"wf{k}a", (-RX + 0.05, y, 1.2), (0.08, 1.9, 0.08), M["frame"])
    box(f"wf{k}b", (-RX + 0.05, y, 2.7), (0.08, 1.9, 0.08), M["frame"])
    box(f"wf{k}c", (-RX + 0.05, y, 1.95), (0.06, 0.06, 1.5), M["frame"])
    bl = box(f"blind{k}", (-RX + 0.12, y, 2.68), (0.02, 1.85, 0.04), M["blind"])
    blinds.append(bl)
    cyl(f"radi{k}", (-RX + 0.12, y, 0.55), 0.04, 1.6, M["frame"], rot=(math.pi / 2, 0, 0))
    box(f"rad{k}", (-RX + 0.1, y, 0.55), (0.08, 1.5, 0.5), M["frame"])
# Tür rechts vorne
DY = 2.6
box("doorframe", (RX - 0.03, DY, 1.08), (0.06, 1.12, 2.18), M["metal"])
door = box("door", (RX - 0.06, DY, 1.05), (0.05, 1.0, 2.1), M["door"])
box("doorwin", (RX - 0.09, DY + 0.25, 1.55), (0.012, 0.18, 0.7), M["hall"])
hpiv = bpy.data.objects.new("handlePivot", None)
sc.collection.objects.link(hpiv)
hpiv.location = (RX - 0.12, DY - 0.38, 1.05)
cyl("handleRose", (RX - 0.1, DY - 0.38, 1.05), 0.03, 0.03, M["metal"], rot=(0, math.pi / 2, 0))
lever = box("lever", (0, 0.06, 0), (0.025, 0.14, 0.022), M["metal"], bevel=0.008, parent=hpiv)
box("keyplate", (RX - 0.095, DY - 0.38, 0.88), (0.015, 0.04, 0.09), M["metal"])
kpiv = bpy.data.objects.new("keyPivot", None)
sc.collection.objects.link(kpiv)
kpiv.location = (RX - 0.12, DY - 0.38, 0.87)
box("key", (-0.02, 0, 0), (0.04, 0.008, 0.03), M["metal"], parent=kpiv)
box("speaker", (RX - 0.1, DY, 2.75), (0.12, 0.35, 0.25), M["frame"], bevel=0.02)
for i in range(5):
    box(f"spk{i}", (RX - 0.165, DY - 0.12 + i * 0.06, 2.75), (0.005, 0.02, 0.17), M["dark"])
# Schränke/Spinde rechts hinten, Pinnwand hinten
for i in range(4):
    box(f"locker{i}", (RX - 0.25, -2.9 + i * 0.52, 1.0), (0.48, 0.5, 2.0), M["locker"], bevel=0.01)
    box(f"lockgrip{i}", (RX - 0.5, -2.9 + i * 0.52 + 0.15, 1.1), (0.02, 0.02, 0.12), M["dark"])
box("pinboard", (-1.0, -RY + 0.03, 1.7), (2.6, 0.03, 1.1), M["pin"])
for i in range(9):
    c = random.choice([(0.95, 0.9, 0.5), (0.6, 0.8, 0.95), (0.95, 0.6, 0.6), (0.95, 0.95, 0.95), (0.7, 0.9, 0.6)])
    box(f"note{i}", (-2.1 + (i % 5) * 0.5 + random.uniform(-0.05, 0.05), -RY + 0.05, 1.45 + (i // 5) * 0.5), (0.36, 0.01, 0.42), mat(f"n{i}", c, 0.9))
# Deckenleuchten
panels, lamps = [], []
for x in (-2.3, 0.0, 2.3):
    for y in (-2.2, 0.6, 3.0):
        panels.append(box(f"panel{x}{y}", (x, y, RZ - 0.02), (0.6, 1.2, 0.03), M["panel"]))
        bpy.ops.object.light_add(type="AREA", location=(x, y, RZ - 0.06))
        l = bpy.context.object
        l.data.shape = "RECTANGLE"
        l.data.size, l.data.size_y = 0.6, 1.2
        l.data.energy = 140
        l.data.color = (1.0, 0.97, 0.92)
        lamps.append(l)
# Tageslicht durch die Fenster
day = []
for y in (-2.6, -0.4, 1.8):
    bpy.ops.object.light_add(type="AREA", location=(-RX + 0.3, y, 1.95), rotation=(0, math.radians(90), 0))
    l = bpy.context.object
    l.data.shape = "RECTANGLE"
    l.data.size, l.data.size_y = 1.5, 1.8
    l.data.energy = 220
    l.data.color = (0.85, 0.92, 1.0)
    day.append(l)
w = bpy.data.worlds.new("w")
sc.world = w
w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.2, 0.21, 0.23, 1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35


# ---------- Tische, Stühle ----------
def desk(x, y, items=True):
    box("dt", (x, y, 0.74), (1.3, 0.55, 0.03), M["wood"], bevel=0.008)
    for dx in (-0.6, 0.6):
        for dy in (-0.22, 0.22):
            cyl("dl", (x + dx, y + dy, 0.37), 0.015, 0.74, M["metal"], verts=8)
    box("dfront", (x, y + 0.26, 0.6), (1.25, 0.015, 0.25), M["metal"])
    if items:
        for k in range(random.randint(1, 3)):
            c = random.choice([(0.8, 0.2, 0.2), (0.2, 0.4, 0.8), (0.9, 0.8, 0.2), (0.3, 0.6, 0.3), (0.9, 0.9, 0.9)])
            box("book", (x + random.uniform(-0.5, 0.5), y + random.uniform(-0.1, 0.1), 0.765), (0.21, 0.29, 0.02), mat("b", c, 0.6), rot=(0, 0, random.uniform(-0.3, 0.3)))
        if random.random() < 0.6:
            cyl("bottle", (x + random.uniform(-0.55, 0.55), y + 0.18, 0.87), 0.035, 0.22, mat("bo", random.choice([(0.2, 0.6, 0.8), (0.9, 0.3, 0.4), (0.3, 0.3, 0.3)]), 0.3), verts=16)


def chair(x, y):
    box("cs", (x, y, 0.45), (0.42, 0.4, 0.025), M["chair"], bevel=0.005)
    box("cb", (x, y - 0.2, 0.72), (0.42, 0.02, 0.3), M["chair"], bevel=0.005, rot=(0.12, 0, 0))
    for dx in (-0.18, 0.18):
        for dy in (-0.18, 0.18):
            cyl("cl", (x + dx, y + dy, 0.22), 0.012, 0.45, M["metal"], verts=8)


def person(name, x, y, seated=True, hood=None, hair=None, skin=None, teacher=False):
    root = bpy.data.objects.new(name, None)
    sc.collection.objects.link(root)
    root.location = (x, y, 0)
    hood = mat(name + "h", hood or random.choice(HOODIES), 0.85)
    hair = mat(name + "hr", hair or random.choice(HAIRS), 0.6)
    skinm = skin or random.choice([M["skin"], M["skin"], M["skin2"]])
    base = 0.45 if seated else 0.9
    if seated:
        box("legs", (0, 0.2, 0.52), (0.34, 0.42, 0.13), M["dark"], parent=root, bevel=0.04)
        box("shins", (0, 0.4, 0.26), (0.32, 0.12, 0.45), M["dark"], parent=root, bevel=0.03)
    else:
        for dx in (-0.09, 0.09):
            cyl("leg", (dx, 0, 0.45), 0.07, 0.9, M["dark"], parent=root)
    box("torso", (0, 0, base + 0.3), (0.38, 0.22, 0.58), hood, parent=root, bevel=0.07)
    for s in (-1, 1):
        cyl("arm", (s * 0.22, 0.12 if seated else 0.0, base + 0.3), 0.055, 0.5, hood, rot=(0.9 if seated else 0.1, 0, 0), parent=root)
    neck = bpy.data.objects.new(name + "_neck", None)
    sc.collection.objects.link(neck)
    neck.parent = root
    neck.location = (0, 0, base + 0.62)
    cyl("neckc", (0, 0, 0.04), 0.05, 0.1, skinm, parent=neck)
    ball("head", (0, 0.01, 0.17), (0.1, 0.115, 0.125), skinm, parent=neck)
    ball("hair", (0, -0.015, 0.21), (0.108, 0.12, 0.11), hair, parent=neck)
    for s in (-1, 1):
        ball("ear", (s * 0.1, 0.0, 0.16), (0.015, 0.03, 0.035), skinm, parent=neck, seg=12)
    if teacher:
        ball("bun", (0, -0.1, 0.26), (0.06, 0.06, 0.06), hair, parent=neck)
    return root, neck


COLS = (-2.6, 0.0, 2.6)
ROWS = (1.5, 0.1, -1.3, -2.7)
students = []
for y in ROWS:
    for x in COLS:
        own = abs(x - 2.6) < 0.01 and abs(y + 1.3) < 0.01
        desk(x, y, items=not own)
        for sx in (-0.33, 0.33):
            if own and sx > 0:
                chair(x + sx, y - 0.45)
                continue  # mein Platz
            chair(x + sx, y - 0.45)
            if random.random() < 0.8 or (own and sx < 0):
                r, n = person(f"s{len(students)}", x + sx, y - 0.45)
                students.append((r, n))
# eigener Tisch: Arbeitsblatt + Stift + Handy liegt
box("sheet", (2.9, -1.33, 0.758), (0.21, 0.29, 0.002), M["paper"], rot=(0, 0, 0.08))
cyl("pen", (2.75, -1.25, 0.762), 0.005, 0.15, mat("penm", (0.1, 0.3, 0.8), 0.4), rot=(math.pi / 2, 0, 0.6))
# Lehrertisch + Lehrerin
box("tdesk", (-2.4, 2.9, 0.75), (1.6, 0.75, 0.04), M["wood"], bevel=0.01)
box("tdeskb", (-2.4, 3.25, 0.4), (1.55, 0.04, 0.7), M["wood"])
teacher, tneck = person("teacher", 1.2, 3.35, seated=False, hood=(0.55, 0.2, 0.25), hair=(0.3, 0.18, 0.1), skin=M["skin"], teacher=True)
teacher.rotation_euler = (0, 0, math.pi)  # schaut zur Klasse (−y)

# ---------- Kamera (Ich-Perspektive) + Hand mit Handy ----------
bpy.ops.object.camera_add(location=(2.92, -1.78, 1.17))
cam = bpy.context.object
sc.camera = cam
cam.data.lens = 20
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 30
cam.data.clip_start = 0.02
rig = bpy.data.objects.new("handRig", None)
sc.collection.objects.link(rig)
rig.parent = cam
# Handy in der rechten Hand (Kamera-Koordinaten: −z = nach vorne)
ph = box("phone", (0, 0, 0), (0.075, 0.155, 0.009), M["phone"], bevel=0.008, parent=rig)
scr1 = box("scr1", (0, 0, 0.0047), (0.068, 0.145, 0.0005), M["scr1"], parent=rig, rot=(0, 0, 0))
scr2 = box("scr2", (0, 0, 0.0048), (0.068, 0.145, 0.0005), M["scr2"], parent=rig)
for o in (scr1, scr2):
    for p in o.data.polygons:
        pass
# Bildschirm-UV: Oberseite zeigt das Bild – einfache planare Projektion über ein Plane-Objekt
bpy.data.objects.remove(scr1, do_unlink=True)
bpy.data.objects.remove(scr2, do_unlink=True)
screens = []
for k, m in enumerate((M["scr1"], M["scr2"])):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.0048 + k * 0.0002))
    s = bpy.context.object
    s.scale = (0.068, 0.145, 1)
    s.data.materials.append(m)
    s.parent = rig
    screens.append(s)
hand = mat("handm", (0.78, 0.57, 0.43), 0.55)
box("palm", (0.005, -0.04, -0.03), (0.085, 0.1, 0.03), hand, bevel=0.012, parent=rig)
for i in range(4):
    box(f"fing{i}", (0.05, -0.065 + i * 0.022, -0.008), (0.022, 0.018, 0.035), hand, bevel=0.006, parent=rig)
box("thumb", (-0.045, -0.02, 0.0), (0.02, 0.06, 0.02), hand, bevel=0.007, parent=rig, rot=(0, 0, 0.3))
cyl("sleeve", (0.0, -0.17, -0.04), 0.045, 0.16, M["sleeve"], rot=(math.pi / 2, 0, 0), parent=rig)


def cam_pose(f, pos, yaw, pitch, roll=0.0):
    cam.location = pos
    cam.keyframe_insert("location", frame=f)
    cam.rotation_euler = (math.radians(90 + pitch), math.radians(roll), math.radians(yaw))
    cam.keyframe_insert("rotation_euler", frame=f)


P0 = Vector((2.92, -1.78, 1.17))
CROUCH = Vector((2.98, -1.95, 0.72))
cam_pose(T(0), P0, 24, -8)
cam_pose(T(1.6), P0 + Vector((0, 0, 0.005)), 22, -7)
cam_pose(T(3.3), P0, 14, -2)
cam_pose(T(4.6), P0 + Vector((0.02, 0, 0.01)), -18, 2)
cam_pose(T(6.5), P0, -22, 0)
cam_pose(T(8.2), P0, -16, -3)
cam_pose(T(9.6), P0 + Vector((0, 0, 0.03)), -8, -2)
cam_pose(T(10.8), CROUCH, -14, 4, 3)
cam_pose(T(12.0), CROUCH + Vector((0, 0, -0.02)), -20, -6, 2)
cam_pose(T(13.2), CROUCH, -18, -14, 1)
cam_pose(T(15.0), CROUCH + Vector((0.01, 0, 0.01)), -19, -12, 1)
cam_pose(T(16.0), CROUCH + Vector((0, 0, 0.16)), -19, 2, 1)
cam_pose(T(17.5), CROUCH + Vector((0, 0.03, 0.17)), -19, 2.5, 1)
# kleines Atmen/Zittern
for f in range(1, T(17.5), 6):
    pass

# Hand mit Handy: unten aus dem Bild -> hoch -> wieder etwas runter (Blick zur Tür)
def hand_pose(f, x, y, z, rx):
    rig.location = (x, y, z)
    rig.keyframe_insert("location", frame=f)
    rig.rotation_euler = (math.radians(rx), 0, 0)
    rig.keyframe_insert("rotation_euler", frame=f)


hand_pose(T(0), 0.06, -0.45, -0.3, 0)
hand_pose(T(12.0), 0.06, -0.45, -0.3, 0)
hand_pose(T(12.9), 0.03, -0.075, -0.3, 8)
hand_pose(T(15.0), 0.03, -0.07, -0.3, 8)
hand_pose(T(16.0), 0.07, -0.2, -0.32, 20)
hand_pose(T(17.5), 0.07, -0.21, -0.32, 20)
# Bildschirm wechselt bei neuer Nachricht (13,6 s) + Vibration
s2 = screens[1]
s2.hide_render = True
s2.keyframe_insert("hide_render", frame=1)
s2.hide_render = False
s2.keyframe_insert("hide_render", frame=T(13.6))
for k, f in enumerate(range(T(13.6), T(14.1), 2)):
    rig.location = (0.03 + (0.004 if k % 2 else -0.004), -0.075, -0.3)
    rig.keyframe_insert("location", frame=f)
rig.location = (0.03, -0.075, -0.3)
rig.keyframe_insert("location", frame=T(14.2))

# Mitschüler drehen die Köpfe zur Durchsage (rechts vorne), dann zur Tür
for i, (r, n) in enumerate(students):
    d = random.uniform(0, 0.6)
    n.rotation_euler = (0, 0, 0)
    n.keyframe_insert("rotation_euler", frame=T(3.0 + d))
    n.rotation_euler = (math.radians(8), 0, math.radians(random.uniform(-70, -45)))
    n.keyframe_insert("rotation_euler", frame=T(3.8 + d))
    n.keyframe_insert("rotation_euler", frame=T(9.5 + d))
    # ducken: ganzer Körper runter
    r.keyframe_insert("location", frame=T(9.8 + d))
    r.location.z = -0.35
    r.keyframe_insert("location", frame=T(11.0 + d))
# Lehrerin: geht zur Tür, schließt ab, dreht sich zur Klasse
path = [(0, (1.2, 3.35)), (4.4, (1.2, 3.35)), (5.6, (2.6, 3.1)), (6.8, (3.85, 2.25)), (8.4, (3.85, 2.25)), (9.6, (3.2, 0.9))]
for t, (x, y) in path:
    teacher.location = (x, y, 0)
    teacher.keyframe_insert("location", frame=T(t))
for t, yaw in ((4.4, 0), (4.9, -60), (6.8, -95), (8.3, -95), (8.9, 20), (9.6, 10)):
    teacher.rotation_euler = (0, 0, math.radians(yaw) + math.pi)
    teacher.keyframe_insert("rotation_euler", frame=T(t))
for t in range(int(4.6 * 10), int(6.8 * 10), 3):  # Schritt-Wippen
    teacher.location.z = 0.025 if (t // 3) % 2 else 0
    teacher.keyframe_insert("location", index=2, frame=T(t / 10))
teacher.location.z = 0
teacher.keyframe_insert("location", index=2, frame=T(6.9))
teacher.keyframe_insert("location", index=2, frame=T(9.7))
teacher.location.z = -0.45
teacher.keyframe_insert("location", index=2, frame=T(10.5))
cam.data.lens = 20
cam.data.keyframe_insert("lens", frame=T(15.6))
cam.data.lens = 34
cam.data.keyframe_insert("lens", frame=T(16.9))
# Schlüssel dreht (7,4 s)
kpiv.rotation_euler = (0, 0, 0)
kpiv.keyframe_insert("rotation_euler", frame=T(7.2))
kpiv.rotation_euler = (math.radians(90), 0, 0)
kpiv.keyframe_insert("rotation_euler", frame=T(7.6))
# Licht aus (10,0 s) + Jalousien runter (9,4–10,6 s)
for l in lamps:
    l.data.energy = 140
    l.data.keyframe_insert("energy", frame=T(9.95))
    l.data.energy = 0
    l.data.keyframe_insert("energy", frame=T(10.0))
pe = M["panel"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
pe.default_value = 6
pe.keyframe_insert("default_value", frame=T(9.95))
pe.default_value = 0
pe.keyframe_insert("default_value", frame=T(10.0))
for k, bl in enumerate(blinds):
    bl.keyframe_insert("location", frame=T(9.4 + k * 0.15))
    bl.keyframe_insert("scale", frame=T(9.4 + k * 0.15))
    bl.scale.z = 0.725
    bl.location.z = 2.7 - 0.725
    bl.keyframe_insert("location", frame=T(10.6 + k * 0.15))
    bl.keyframe_insert("scale", frame=T(10.6 + k * 0.15))
for l in day:
    l.data.energy = 220
    l.data.keyframe_insert("energy", frame=T(9.6))
    l.data.energy = 110
    l.data.keyframe_insert("energy", frame=T(10.7))
ce = M["ceil"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
ce.default_value = 0.35
ce.keyframe_insert("default_value", frame=T(9.95))
ce.default_value = 0.03
ce.keyframe_insert("default_value", frame=T(10.0))
bpy.ops.object.light_add(type="POINT", location=(RX - 0.35, DY + 0.1, 1.45))
hl = bpy.context.object
hl.data.energy = 18
hl.data.color = (0.8, 0.88, 1.0)
hl.data.shadow_soft_size = 0.2
# Türklinke wird langsam runtergedrückt (15,8–16,8 s), kurzes Rütteln (17,0 s)
hpiv.rotation_euler = (0, 0, 0)
hpiv.keyframe_insert("rotation_euler", frame=T(15.8))
hpiv.rotation_euler = (math.radians(-38), 0, 0)
hpiv.keyframe_insert("rotation_euler", frame=T(16.8))
hpiv.rotation_euler = (math.radians(-30), 0, 0)
hpiv.keyframe_insert("rotation_euler", frame=T(17.0))
hpiv.rotation_euler = (math.radians(-40), 0, 0)
hpiv.keyframe_insert("rotation_euler", frame=T(17.15))
door.keyframe_insert("location", frame=T(16.95))
door.location.x -= 0.006
door.keyframe_insert("location", frame=T(17.05))
door.location.x += 0.006
door.keyframe_insert("location", frame=T(17.15))

# ---------- Render-Einstellungen ----------
sc.frame_start, sc.frame_end = 1, T(17.5)
sc.render.fps = FPS
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 10
try:
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass
pct = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 50
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, pct
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = sys.argv[-2] if sys.argv[-1].isdigit() else sys.argv[-1]
