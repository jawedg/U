# „Blindflug im Reaktor“ – Kontrollraum Fukushima Daiichi Block 1/2, 11.03.2011, Ich-Perspektive.
# blender -b --python fuku.py -- <ausgabe_präfix> <prozent>   (+ -a / -f N)
import bpy, sys, os, math, random, json
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "mpfb"))
import people as P

FPS = 24
T = lambda s: int(round(s * FPS)) + 1
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
TEX = os.path.join(HERE, "tex")
random.seed(3)

# ---------- Zeitplan (Sekunden) ----------
QUAKE = (1.2, 9.6)
WARN = 22.0          # Tsunami-Warnung auf dem Monitor
IMPACT = 30.2        # Welle schlägt ein
BLACK = 31.0         # Stromausfall
K2LIGHT = 35.2       # Kollege 2 Taschenlampe an
MYLIGHT = 40.6       # eigene Taschenlampe an
END = 59.4           # Schnitt auf Schwarz


def img(name):
    return bpy.data.images.load(os.path.join(TEX, name))


def nodes_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(b.outputs[0], out.inputs[0])
    return m, nt, b


def value(nt, v=1.0):
    n = nt.nodes.new("ShaderNodeValue")
    n.outputs[0].default_value = v
    return n


def key_value(node, f, v):
    node.outputs[0].default_value = v
    node.outputs[0].keyframe_insert("default_value", frame=f)


def tex(nt, image):
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = image
    return t


def vmath(nt, op, a, b=None, s=None):
    n = nt.nodes.new("ShaderNodeVectorMath")
    n.operation = op
    nt.links.new(a, n.inputs[0])
    if b is not None:
        nt.links.new(b, n.inputs[1])
    if s is not None:
        nt.links.new(s, n.inputs["Scale"])
    return n.outputs[0]


def simple(name, col, rough=0.6, metal=0.0, emit=None, strength=0.0):
    m, nt, b = nodes_mat(name)
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def box(name, loc, size, m, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def plane(name, loc, w, h, m, rot):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (w, h, 1)
    o.data.materials.append(m)
    return o


# ---------- Strom-Steuerung: ein Wert für alles ----------
POWER_NODES = []   # (node, factor) – alles was mit Strom leuchtet


def power_curve(node, scale=1.0, flicker=True):
    """Strom an bis BLACK; beim Beben kurzes Flackern; Einschlag: Flackern, dann aus."""
    key_value(node, 1, scale)
    if flicker:
        for t, v in ((2.0, 1.0), (2.08, 0.35), (2.16, 1.0), (5.1, 1.0), (5.15, 0.5), (5.22, 1.0), (IMPACT, 1.0), (IMPACT + 0.12, 0.3), (IMPACT + 0.2, 1.0), (BLACK - 0.04, 1.0)):
            key_value(node, T(t), v * scale)
    else:
        key_value(node, T(BLACK - 0.04), scale)
    key_value(node, T(BLACK), 0.0)


# ---------- Raum ----------
RX0, RX1, RY0, RY1, RZ = -4.2, 4.2, -3.2, 2.0, 3.3
WALLC = simple("wallc", (0.62, 0.64, 0.6), 0.85)
FLOOR = simple("floor", (0.28, 0.32, 0.3), 0.7)
CEIL = simple("ceil", (0.78, 0.78, 0.76), 0.9)
box("floor", (0, (RY0 + RY1) / 2, -0.05), (RX1 - RX0, RY1 - RY0, 0.1), FLOOR)
box("ceil", (0, (RY0 + RY1) / 2, RZ + 0.05), (RX1 - RX0, RY1 - RY0, 0.1), CEIL)
box("wallB", (0, RY1 + 0.25, RZ / 2), (RX1 - RX0, 0.1, RZ), WALLC)
box("wallF", (0, RY0 - 0.05, RZ / 2), (RX1 - RX0, 0.1, RZ), WALLC)
box("wallL", (RX0 - 0.05, (RY0 + RY1) / 2, RZ / 2), (0.1, RY1 - RY0, RZ), WALLC)
box("wallR", (RX1 + 0.05, (RY0 + RY1) / 2, RZ / 2), (0.1, RY1 - RY0, RZ), WALLC)

# Kontrollwand (senkrecht) mit Strom/ohne Strom + Warnlampen
m, nt, b = nodes_mat("wallpanel")
t_on, t_off = tex(nt, img("wall_on.png")), tex(nt, img("wall_off.png"))
t_em, t_ann = tex(nt, img("wall_em_on.png")), tex(nt, img("wall_ann.png"))
pw, an = value(nt, 1.0), value(nt, 0.0)
mix = nt.nodes.new("ShaderNodeMix")
mix.data_type = "RGBA"
nt.links.new(pw.outputs[0], mix.inputs["Factor"])
nt.links.new(t_off.outputs[0], mix.inputs[6])
nt.links.new(t_on.outputs[0], mix.inputs[7])
nt.links.new(mix.outputs[2], b.inputs["Base Color"])
e = vmath(nt, "ADD", vmath(nt, "SCALE", t_em.outputs[0], s=pw.outputs[0]), vmath(nt, "SCALE", t_ann.outputs[0], s=an.outputs[0]))
nt.links.new(e, b.inputs["Emission Color"])
b.inputs["Emission Strength"].default_value = 3.0
b.inputs["Roughness"].default_value = 0.45
plane("controlwall", (0, RY1 + 0.19, 2.1), 8.0, 2.4, m, (math.pi / 2, 0, 0))
power_curve(pw)
# Warnlampen: aus -> Beben: blinken -> danach viele dauerhaft an -> Blackout aus
key_value(an, 1, 0.0)
key_value(an, T(1.6), 0.0)
t = 1.7
while t < 9.5:
    key_value(an, T(t), 0.9)
    key_value(an, T(t + 0.18), 0.15)
    t += 0.36
key_value(an, T(9.7), 0.55)
t = 21.2
while t < BLACK - 0.2:
    key_value(an, T(t), 0.75)
    key_value(an, T(t + 0.25), 0.4)
    t += 0.5
key_value(an, T(BLACK - 0.04), 0.6)
key_value(an, T(BLACK), 0.0)

# Schräges Pult vor der Wand
m, nt, b = nodes_mat("desk")
d_on, d_off, d_em = tex(nt, img("desk_on.png")), tex(nt, img("desk_off.png")), tex(nt, img("desk_em_on.png"))
dpw = value(nt, 1.0)
mix = nt.nodes.new("ShaderNodeMix")
mix.data_type = "RGBA"
nt.links.new(dpw.outputs[0], mix.inputs["Factor"])
nt.links.new(d_off.outputs[0], mix.inputs[6])
nt.links.new(d_on.outputs[0], mix.inputs[7])
nt.links.new(mix.outputs[2], b.inputs["Base Color"])
nt.links.new(vmath(nt, "SCALE", d_em.outputs[0], s=dpw.outputs[0]), b.inputs["Emission Color"])
b.inputs["Emission Strength"].default_value = 3.0
power_curve(dpw)
plane("benchtop", (0, RY1 - 0.3, 0.98), 8.0, 0.9, m, (math.radians(-28) + 0, 0, 0))
CAB = simple("cab", (0.6, 0.63, 0.57), 0.6)
box("benchcab", (0, RY1 - 0.25, 0.45), (8.0, 0.8, 0.9), CAB)

# Leitstand-Tisch mit zwei Röhrenmonitoren vor mir
box("console", (0, -0.62, 0.74), (1.9, 0.6, 0.04), simple("ctop", (0.42, 0.44, 0.42), 0.5))
box("consoleBody", (0, -0.55, 0.36), (1.85, 0.45, 0.72), CAB)
monitors = []
for i, x in enumerate((-0.42, 0.42)):
    crt = box(f"crt{i}", (x, -0.42, 0.98), (0.46, 0.42, 0.38), simple(f"crtc{i}", (0.36, 0.35, 0.32), 0.55))
    bev = crt.modifiers.new("b", "BEVEL")
    bev.width = 0.03
    bev.segments = 3
    box(f"bezel{i}", (x, -0.632, 0.99), (0.44, 0.012, 0.34), simple(f"bez{i}", (0.08, 0.08, 0.085), 0.4))
    m, nt, b = nodes_mat(f"screen{i}")
    s_ok, s_warn = tex(nt, img("mon_ok.png")), tex(nt, img("mon_warn.png"))
    a_ok, a_warn = value(nt, 1.0), value(nt, 0.0)
    col = vmath(nt, "ADD", vmath(nt, "SCALE", s_ok.outputs[0], s=a_ok.outputs[0]), vmath(nt, "SCALE", s_warn.outputs[0], s=a_warn.outputs[0]))
    nt.links.new(col, b.inputs["Base Color"])
    nt.links.new(col, b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 1.6
    b.inputs["Roughness"].default_value = 0.15
    plane(f"scr{i}", (x, -0.64, 0.99), 0.37, 0.28, m, (math.pi / 2, 0, 0))
    monitors.append((a_ok, a_warn))
for i, (a_ok, a_warn) in enumerate(monitors):
    power_curve(a_ok)
    if i == 1:  # rechter Monitor zeigt die Warnung (blinkend)
        key_value(a_ok, T(WARN - 0.05), 1.0)
        key_value(a_ok, T(WARN), 0.0)
        key_value(a_warn, 1, 0.0)
        key_value(a_warn, T(WARN - 0.05), 0.0)
        t = WARN
        while t < BLACK - 0.1:
            key_value(a_warn, T(t), 1.0)
            key_value(a_warn, T(t + 0.55), 0.35)
            t += 0.8
        key_value(a_warn, T(BLACK - 0.04), 1.0)
        key_value(a_warn, T(BLACK), 0.0)

# Ordner/Papiere auf dem Tisch (einer fällt beim Beben)
binder = box("binder", (-0.75, -0.7, 0.88), (0.06, 0.3, 0.26), simple("bind", (0.15, 0.3, 0.6), 0.6))
box("papers", (0.05, -0.68, 0.765), (0.3, 0.22, 0.01), simple("pap", (0.92, 0.92, 0.88), 0.8), rot=(0, 0, 0.2))
binder.keyframe_insert("location", frame=T(3.4))
binder.keyframe_insert("rotation_euler", frame=T(3.4))
binder.location = (-0.83, -0.62, 0.79)
binder.rotation_euler = (0, math.radians(-88), 0.3)
binder.keyframe_insert("location", frame=T(3.75))
binder.keyframe_insert("rotation_euler", frame=T(3.75))

# Stahltür zum Reaktorgebäude (rechte Wand) + Schild + rote Notlampe
STEEL = simple("steel", (0.36, 0.38, 0.4), 0.35, 0.7)
door = box("door", (RX1 - 0.04, 0.4, 1.08), (0.08, 1.15, 2.16), STEEL)
box("doorframe", (RX1 - 0.02, 0.4, 1.12), (0.04, 1.3, 2.3), simple("frame", (0.2, 0.2, 0.22), 0.4, 0.6))
for k in range(3):
    box(f"hinge{k}", (RX1 - 0.09, 0.94, 0.4 + k * 0.7), (0.03, 0.04, 0.14), simple("hg", (0.15, 0.15, 0.15), 0.3, 0.8))
box("bar", (RX1 - 0.11, 0.35, 1.05), (0.04, 0.8, 0.06), simple("bar", (0.75, 0.75, 0.72), 0.3, 0.8))
ms, nt, b = nodes_mat("sign")
nt.links.new(tex(nt, img("sign.png")).outputs[0], b.inputs["Base Color"])
plane("sign", (RX1 - 0.09, 0.4, 2.45), 0.9, 0.34, ms, (math.pi / 2, 0, -math.pi / 2))
redl = simple("redlamp", (0.4, 0.05, 0.05), 0.3, emit=(1, 0.08, 0.05), strength=0.0)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(RX1 - 0.08, 1.05, 2.5))
bpy.context.object.data.materials.append(redl)
rs = redl.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
rs.keyframe_insert("default_value", frame=T(51.0))
t = 51.2
while t < END:
    rs.default_value = 6.0
    rs.keyframe_insert("default_value", frame=T(t))
    rs.default_value = 0.4
    rs.keyframe_insert("default_value", frame=T(t + 0.6))
    t += 1.2
bpy.ops.object.light_add(type="POINT", location=(RX1 - 0.3, 1.05, 2.45))
rl = bpy.context.object
rl.data.color = (1, 0.1, 0.06)
rl.data.energy = 0
rl.data.keyframe_insert("energy", frame=T(51.0))
t = 51.2
while t < END:
    rl.data.energy = 25
    rl.data.keyframe_insert("energy", frame=T(t))
    rl.data.energy = 2
    rl.data.keyframe_insert("energy", frame=T(t + 0.6))
    t += 1.2

# Deckenleuchten (Neon) + Deckenplatten
PANEL = simple("lpanel", (1, 1, 1), 0.3, emit=(0.92, 0.97, 1.0), strength=7.0)
pe = PANEL.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
lamps = []
for x in (-2.6, -0.9, 0.9, 2.6):
    for y in (-2.0, -0.4, 1.2):
        box(f"lp{x}{y}", (x, y, RZ - 0.015), (1.2, 0.3, 0.03), PANEL)
for x in (-1.75, 1.75):
    for y in (-1.2, 0.9):
        bpy.ops.object.light_add(type="AREA", location=(x, y, RZ - 0.05))
        l = bpy.context.object
        l.data.shape = "RECTANGLE"
        l.data.size, l.data.size_y = 3.0, 1.6
        l.data.energy = 96
        l.data.color = (0.92, 0.97, 1.0)
        lamps.append(l)
for l in lamps:
    l.data.keyframe_insert("energy", frame=1)
    for t, v in ((2.0, 96), (2.08, 27), (2.16, 96), (5.1, 96), (5.15, 42), (5.22, 96), (IMPACT, 96), (IMPACT + 0.12, 15), (IMPACT + 0.2, 96), (BLACK - 0.04, 96), (BLACK, 0)):
        l.data.energy = v
        l.data.keyframe_insert("energy", frame=T(t))
for t, v in ((1, 2.2), (2.0, 2.2), (2.08, 0.6), (2.16, 2.2), (5.1, 2.2), (5.15, 1), (5.22, 2.2), (IMPACT, 2.2), (IMPACT + 0.12, 0.3), (IMPACT + 0.2, 2.2), (BLACK - 0.04, 2.2), (BLACK, 0)):
    pe.default_value = v
    pe.keyframe_insert("default_value", frame=T(t) if t != 1 else 1)
# Deckenplatten klappern beim Beben
tiles = []
for k in range(10):
    o = box(f"tile{k}", (random.uniform(-3.5, 3.5), random.uniform(-2.5, 1.5), RZ - 0.01), (0.6, 0.6, 0.012), CEIL)
    tiles.append(o)
    for f in range(T(QUAKE[0]), T(QUAKE[1]), 2):
        o.location.z = RZ - 0.01 - random.uniform(0, 0.025)
        o.keyframe_insert("location", index=2, frame=f)
    o.location.z = RZ - 0.01
    o.keyframe_insert("location", index=2, frame=T(QUAKE[1]) + 2)
w = bpy.data.worlds.new("w")
sc.world = w
w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.055, 0.06, 1)
bg = w.node_tree.nodes["Background"].inputs["Strength"]
bg.default_value = 0.15
bg.keyframe_insert("default_value", frame=T(BLACK - 0.04))
bg.default_value = 0.0
bg.keyframe_insert("default_value", frame=T(BLACK))

# Staub in der Luft (sichtbar nur im Lichtkegel)
DUST = simple("dust", (1, 1, 1), 0.9)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.003)
dmesh = bpy.context.object
dmesh.data.materials.append(DUST)
import bmesh as _bm
bm = _bm.new()
src = dmesh.data
for k in range(260):
    off = Vector((random.uniform(-2.5, 3.5), random.uniform(-1.5, 1.6), random.uniform(0.6, 2.4)))
    vmap = [bm.verts.new(v.co + off) for v in src.vertices]
    for poly in src.polygons:
        bm.faces.new([vmap[i] for i in poly.vertices])
dm = bpy.data.meshes.new("dust")
bm.to_mesh(dm)
bm.free()
dust = bpy.data.objects.new("dust", dm)
sc.collection.objects.link(dust)
dm.materials.append(DUST)
bpy.data.objects.remove(dmesh, do_unlink=True)
dust.hide_render = True
dust.keyframe_insert("hide_render", frame=1)
dust.hide_render = False
dust.keyframe_insert("hide_render", frame=T(BLACK))
dust.keyframe_insert("location", frame=1)
dust.location = (0.15, 0, 0.12)
dust.keyframe_insert("location", frame=T(END))

# ---------- Menschen ----------
ME = P.make_person("me", gender=1.0, age=0.45, skin="young_asian_male", race=("asian", 1.0), hair="short01",
                   clothes=("male_worksuit01", "shoes01"))
ME["rig"].location = (0, -1.28, 0)
ME["rig"].rotation_euler = (0, 0, math.pi)
for o in bpy.data.objects:
    if o.parent in (ME["h"], ME["rig"]) and any(k in o.name for k in ("short01", "eyebrow", "eyelash", "low-poly", "teeth", "tongue")):
        o.hide_render = True
K1 = P.make_person("k1", gender=1.0, age=0.4, skin="young_asian_male", race=("asian", 1.0), hair="short03",
                   clothes=("male_worksuit01", "shoes02"), eyebrows="eyebrow007")
K2 = P.make_person("k2", gender=1.0, age=0.6, muscle=0.45, weight=0.55, skin="middleage_asian_male", race=("asian", 1.0), hair="short04",
                   clothes=("male_worksuit01", "shoes01"), eyebrows="eyebrow003")
K1["rig"].location = (-0.55, 0.35, 0)
K2["rig"].location = (0.6, 0.3, 0)

# Kamera am Kopf von "me"
bpy.ops.object.camera_add()
cam = bpy.context.object
sc.camera = cam
cam.data.lens = 18
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 30
cam.data.clip_start = 0.03
bpy.context.view_layer.update()
rig = ME["rig"]
cam.parent = rig
cam.parent_type = "BONE"
cam.parent_bone = "head"
bpy.context.view_layer.update()
eye = rig.matrix_world @ Vector((0, -0.17, 1.62))
cam.matrix_world = Matrix.Translation(eye) @ Euler((math.radians(90), 0, math.pi + math.pi), "XYZ").to_matrix().to_4x4()
cam.matrix_world = Matrix.Translation(eye) @ Euler((math.radians(90), 0, 0), "XYZ").to_matrix().to_4x4()

# Taschenlampen
def flashlight(name, hand_rig, bone):
    body = simple(name + "m", (0.08, 0.08, 0.09), 0.35, 0.6)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.022, depth=0.2)
    fl = bpy.context.object
    fl.name = name
    fl.data.materials.append(body)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.03, depth=0.04, location=(0, 0, 0.11))
    head = bpy.context.object
    head.data.materials.append(body)
    head.parent = fl
    lens = simple(name + "lens", (1, 1, 0.9), 0.1, emit=(1, 0.95, 0.85), strength=0.0)
    bpy.ops.mesh.primitive_circle_add(vertices=20, radius=0.026, fill_type="NGON", location=(0, 0, 0.131))
    ln = bpy.context.object
    ln.data.materials.append(lens)
    ln.parent = fl
    bpy.ops.object.light_add(type="SPOT", location=(0, 0, 0.14))
    sp = bpy.context.object
    sp.parent = fl
    sp.data.spot_size = math.radians(30)
    sp.data.spot_blend = 0.35
    sp.data.color = (1.0, 0.95, 0.85)
    sp.data.energy = 0
    sp.data.shadow_soft_size = 0.02
    # Spot zeigt entlang −Z des Lichts -> nach +Z der Lampe drehen
    sp.rotation_euler = (math.pi, 0, 0)
    fl.parent = hand_rig
    fl.parent_type = "BONE"
    fl.parent_bone = bone
    return fl, sp, lens


# ---------- Bewegungen ----------
def head_track(p, keys):
    """keys: (sek, gier°, nick°) – verteilt auf Rumpf/Hals/Kopf, weich."""
    for t, yaw, pitch in keys:
        f = T(t)
        P.rot(p, "spine03", f, y=yaw * 0.25, x=-pitch * 0.2)
        P.rot(p, "neck01", f, y=yaw * 0.4, x=-pitch * 0.4)
        P.rot(p, "head", f, y=yaw * 0.35, x=-pitch * 0.4)


# Ich: Blick (positiv = nach links)
head_track(ME, [(0, 8, -6), (1.0, 6, -5), (4.0, -4, 2), (8.5, 10, -2), (10.6, 21, -4), (14.6, 22, -4), (16.4, -18, -20), (19.0, -28, -30),
                (27.5, -28, -28), (29.6, 0, -4), (BLACK + 0.2, 0, -2), (34.6, -5, -2), (35.4, -22, -4), (39.6, -21, -4), (40.4, -6, -10),
                (41.8, 4, 8), (44.0, -12, 12), (46.6, 10, 4), (48.0, 21, -2), (50.6, 22, -3), (52.6, -60, 2), (55.5, -68, 4), (END, -68, 4)])
# Wackeln: Beben und Einschlag (zusätzlich auf neck02)
for f in range(1, T(END)):
    t = (f - 1) / FPS
    a = 0.0
    if QUAKE[0] < t < QUAKE[1]:
        a = 2.6 * min(1, (t - QUAKE[0]) / 0.6) * min(1, (QUAKE[1] - t) / 1.5)
    if IMPACT - 0.1 < t < IMPACT + 1.4:
        a = max(a, 4.0 * math.exp(-(t - IMPACT) * 2.2))
    if 50.8 < t < 53:
        a = max(a, 0.6)  # Grollen
    if f % 2 == 0:
        P.rot(ME, "neck02", f, x=a * math.sin(t * 37) + 0.4 * math.sin(t * 0.9), y=a * 0.7 * math.sin(t * 29 + 1), z=a * 0.5 * math.sin(t * 23))
# Ich: Arme
for s in ("L", "R"):
    P.rot(ME, f"upperarm01.{s}", 1, z=(-40 if s == "L" else 40))
    P.rot(ME, f"lowerarm01.{s}", 1, x=10)
# Hände per IK: rechte Hand zeigt auf den Monitor, linke hält die Taschenlampe
def ik(bone, target, chain=5):
    c = ME["rig"].pose.bones[bone].constraints.new("IK")
    c.target = target
    c.chain_count = chain
    c.use_tail = True
    return c


tgtR = bpy.data.objects.new("ikR", None)
sc.collection.objects.link(tgtR)
tgtR.location = (0.3, -0.69, 0.99)
cR = ik("wrist.R", tgtR)
for t, v in ((0, 0), (17.2, 0), (18.5, 1), (27.6, 1), (28.9, 0)):
    cR.influence = v
    cR.keyframe_insert("influence", frame=T(t) if t else 1)
for t, pos in ((18.5, (0.3, -0.69, 0.99)), (21.5, (0.36, -0.68, 1.01)), (24.0, (0.33, -0.68, 1.02)), (27.6, (0.31, -0.69, 1.0))):
    tgtR.location = pos
    tgtR.keyframe_insert("location", frame=T(t))
tgtL = bpy.data.objects.new("ikL", None)
sc.collection.objects.link(tgtL)
tgtL.parent = cam
tgtL.location = (-0.1, -0.2, -0.3)
cL = ik("wrist.L", tgtL)
for t, v in ((0, 0), (39.6, 0), (40.4, 1), (END, 1)):
    cL.influence = v
    cL.keyframe_insert("influence", frame=T(t) if t else 1)
P.idle(ME, 1, T(END), seed=1, head=False)

myfl, myspot, mylens = flashlight("myflash", ME["rig"], "wrist.L")
k2fl, k2spot, k2lens = flashlight("k2flash", K2["rig"], "wrist.R")
k2fl.location = (0, 0.08, 0.02)
k2fl.rotation_euler = (math.radians(-90), 0, 0)
myfl.parent = cam
myfl.parent_type = "OBJECT"
myfl.location = (-0.1, -0.16, -0.34)
myfl.rotation_euler = (math.radians(180), 0, 0)
for o in [myfl] + [c for c in myfl.children if c.type == "MESH"]:
    o.hide_render = True
    o.keyframe_insert("hide_render", frame=1)
    o.hide_render = False
    o.keyframe_insert("hide_render", frame=T(MYLIGHT) - 8)
# K2s Lichtkegel zielt auf ein animiertes Ziel
k2t = bpy.data.objects.new("k2target", None)
sc.collection.objects.link(k2t)
for t, pos in ((K2LIGHT, (-0.4, -1.0, 1.4)), (36.5, (-1.6, 2.0, 1.9)), (38.5, (0.4, 2.0, 1.7)), (40.5, (1.8, 2.0, 1.5)), (END, (2.2, 2.0, 1.2))):
    k2t.location = pos
    k2t.keyframe_insert("location", frame=T(t))
c = k2spot.constraints.new("TRACK_TO")
c.target = k2t
c.track_axis = "TRACK_NEGATIVE_Z"
c.up_axis = "UP_Y"
for sp, ln, t0 in ((myspot, mylens, MYLIGHT), (k2spot, k2lens, K2LIGHT)):
    sp.data.energy = 0
    sp.data.keyframe_insert("energy", frame=T(t0) - 1)
    sp.data.energy = 140
    sp.data.keyframe_insert("energy", frame=T(t0))
    li = ln.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    li.default_value = 0
    li.keyframe_insert("default_value", frame=T(t0) - 1)
    li.default_value = 25
    li.keyframe_insert("default_value", frame=T(t0))
# Unterlicht auf K2s Gesicht von seiner Lampe
bpy.ops.object.light_add(type="POINT", location=(0, 0.1, 0.25))
k2fill = bpy.context.object
k2fill.parent = k2fl
k2fill.data.energy = 0
k2fill.data.shadow_soft_size = 0.1
k2fill.data.keyframe_insert("energy", frame=T(K2LIGHT) - 1)
k2fill.data.energy = 6
k2fill.data.keyframe_insert("energy", frame=T(K2LIGHT))

# Kollegen: Haltung, Drehung, Mimik
for p, base_yaw in ((K1, 175), (K2, 185)):
    for s in ("L", "R"):
        P.rot(p, f"upperarm01.{s}", 1, z=(-40 if s == "L" else 40))
        P.rot(p, f"lowerarm01.{s}", 1, x=0)
    p["rig"].rotation_euler = (0, 0, math.radians(base_yaw))
    p["rig"].keyframe_insert("rotation_euler", frame=1)
    P.idle(p, 1, T(END), seed=hash(p["name"]) % 100)
    P.set_face(p, 1, "neutral")
# Beben: festhalten, leicht in die Knie
for p in (K1, K2):
    for s in ("L", "R"):
        P.rot(p, f"upperleg01.{s}", T(1.6))
        P.rot(p, f"lowerleg01.{s}", T(1.6))
        P.rot(p, f"upperleg01.{s}", T(2.4), x=-14)
        P.rot(p, f"lowerleg01.{s}", T(2.4), x=24)
        P.rot(p, f"upperleg01.{s}", T(9.4), x=-14)
        P.rot(p, f"lowerleg01.{s}", T(9.4), x=24)
        P.rot(p, f"upperleg01.{s}", T(10.4))
        P.rot(p, f"lowerleg01.{s}", T(10.4))
        P.rot(p, f"upperarm01.{s}", T(1.6), z=(-40 if s == "L" else 40))
        P.rot(p, f"upperarm01.{s}", T(2.4), x=35, z=(-22 if s == "L" else 22))
        P.rot(p, f"upperarm01.{s}", T(9.4), x=35, z=(-22 if s == "L" else 22))
        P.rot(p, f"upperarm01.{s}", T(10.4), z=(-40 if s == "L" else 40))
    P.set_face(p, T(1.5), "neutral")
    P.set_face(p, T(2.1), "fear", 0.9)
    P.set_face(p, T(9.8), "worried", 0.8)
# K1 dreht sich zu mir und ruft (10,8 s); später: Dunkelheit, Flüstern im Lichtkegel
for t, yaw in ((10.2, 175), (10.9, 20), (15.0, 20), (16.2, 175), (BLACK, 175), (47.8, 175), (48.6, 20), (END, 20)):
    K1["rig"].rotation_euler = (0, 0, math.radians(yaw))
    K1["rig"].keyframe_insert("rotation_euler", frame=T(t))
for t, yaw in ((K2LIGHT - 0.6, 185), (K2LIGHT + 0.3, 337), (40.0, 337), (41.0, 300), (END, 300)):
    K2["rig"].rotation_euler = (0, 0, math.radians(yaw))
    K2["rig"].keyframe_insert("rotation_euler", frame=T(t))
# K2 hebt die Lampe
P.rot(K2, "upperarm01.R", T(K2LIGHT - 0.5), z=40)
P.rot(K2, "lowerarm01.R", T(K2LIGHT - 0.5), x=12)
P.rot(K2, "upperarm01.R", T(K2LIGHT + 0.3), x=36, z=16)
P.rot(K2, "lowerarm01.R", T(K2LIGHT + 0.3), x=45)
P.set_face(K1, T(10.7), "surprise", 0.8)
P.set_face(K1, T(15.5), "worried", 0.9)
P.set_face(K1, T(BLACK), "fear", 1.0)
P.set_face(K2, T(K2LIGHT), "fear", 0.85)
P.set_face(K2, T(42.0), "worried", 1.0)
P.set_face(K1, T(48.4), "fear", 1.0)
for p, ts in ((K1, (4.5, 13.2, 19.0, 24.5, 44.0, 52.0)), (K2, (6.2, 12.0, 17.5, 26.0, 37.8, 46.0, 55.0))):
    for t in ts:
        P.blink(p, T(t))

# Lippen passend zur Stimme
TIM = json.load(open(os.path.join(HERE, "..", "..", "src", "fuku", "timing.json")))
SCR = json.load(open(os.path.join(HERE, "..", "..", "src", "fuku", "script.json")))
LINE_AT = {"n1": 1.0, "k1a": 10.8, "n2": 15.6, "k1b": 32.4, "k2a": 35.8, "n3": 41.2, "k1c": 48.9, "n4": 51.4}
json.dump(LINE_AT, open(os.path.join(HERE, "..", "..", "src", "fuku", "line_at.json"), "w"))


def lipsync(p, wav, t0):
    import wave as _w, numpy as _np
    with _w.open(wav) as wf:
        sr = wf.getframerate()
        a = _np.frombuffer(wf.readframes(wf.getnframes()), dtype=_np.int16).astype(float)
        if wf.getnchannels() > 1:
            a = a[:: wf.getnchannels()]
    step = int(sr / 12)
    rms = _np.array([_np.sqrt(_np.mean(a[i:i + step] ** 2)) for i in range(0, len(a) - step, step)])
    rms = _np.clip(rms / (rms.max() * 0.65 + 1e-6), 0, 1)
    for obj in [p["h"]] + p["heads"]:
        kb = obj.data.shape_keys.key_blocks.get("ex_mouth-open")
        if kb is None:
            continue
        kb.value = 0
        kb.keyframe_insert("value", frame=T(t0) - 2)
        for k, v in enumerate(rms):
            kb.value = float(v) * 0.75
            kb.keyframe_insert("value", frame=T(t0 + k / 12))
        kb.value = 0
        kb.keyframe_insert("value", frame=T(t0 + len(rms) / 12) + 2)


for i, s in enumerate(SCR["sentences"]):
    who = {"k1": K1, "k2": K2}.get(s["id"][:2])
    if who:
        lipsync(who, os.path.join(HERE, "..", "..", "public", TIM["lines"][i]["file"]), LINE_AT[s["id"]])

# ---------- Leistung: Glättung nur auf Körpern der Kollegen ----------
keep = {K1["h"].name, K2["h"].name}
for o in bpy.data.objects:
    for m in getattr(o, "modifiers", []):
        if m.type == "SUBSURF":
            m.render_levels = 1 if o.name in keep else 0
            m.levels = 0
# ---------- Render ----------
sc.frame_start, sc.frame_end = 1, T(END)
sc.render.fps = FPS
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 8
try:
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass
pct = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 50
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, pct
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = sys.argv[-2] if sys.argv[-1].isdigit() else "/tmp/fuku_"
