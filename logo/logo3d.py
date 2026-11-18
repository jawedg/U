"""QISSAH – 3D-Profilbild: goldene Buchstaben (Cycles), dunkler Raum, Goldstaub mit Bokeh.
  blender -b --factory-startup --python logo/logo3d.py -- <outline.json> <out.png> [samples] [stil]
stil: "ar" (arabisches Wort, darunter QISSAH) | "q" (Monogramm Q, darunter QISSAH)
Umrisse vorher mit logo/outline.py erzeugen (Blender kann Arabisch nicht selbst verbinden)."""
import json
import math
import random
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUTLINE, OUT = argv[0], argv[1]
SAMPLES = int(argv[2]) if len(argv) > 2 else 128
STYLE = argv[3] if len(argv) > 3 else "ar"
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---------------------------------------------------------------- Material
def gold(name="Gold", rough=0.17, col=(1.0, 0.60, 0.16)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = rough
    return m


def emit(name, col, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*col, 1)
    e.inputs["Strength"].default_value = strength
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


GOLD = gold()

# ---------------------------------------------------------------- Buchstaben aus Umrissen
d = json.load(open(OUTLINE))
x0, y0, x1, y1 = d["bbox"]
width = 2.15 if STYLE == "ar" else 1.45
s = width / (x1 - x0)
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
cu = bpy.data.curves.new("Wort", "CURVE")
cu.dimensions = "2D"
cu.fill_mode = "BOTH"
cu.resolution_u = 24
for c in d["contours"]:
    segs = c["segs"]
    if not segs:
        continue
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(segs) - 1)
    pts = [c["start"]] + [sg[2] for sg in segs[:-1]]
    P = lambda p: Vector(((p[0] - cx) * s, (p[1] - cy) * s, 0))
    for i, bp in enumerate(sp.bezier_points):
        bp.handle_left_type = bp.handle_right_type = "FREE"
        bp.co = P(pts[i])
        bp.handle_right = P(segs[i][0])
        bp.handle_left = P(segs[i - 1][1])
    sp.use_cyclic_u = True
cu.extrude = 0.11 if STYLE == "ar" else 0.13
cu.bevel_depth = 0.018
cu.bevel_resolution = 5
word = bpy.data.objects.new("Wort", cu)
sc.collection.objects.link(word)
word.data.materials.append(GOLD)
word.rotation_euler = (math.radians(90), 0, 0)  # aufrecht, Blick zur Kamera (-Y)
word.location = (0, 0, 1.42 if STYLE == "ar" else 1.45)

# „QISSAH“ klein darunter
bpy.ops.object.text_add(location=(0, 0, 0.5 if STYLE == "ar" else 0.42), rotation=(math.radians(90), 0, 0))
t = bpy.context.object
t.data.body = "QISSAH"
t.data.font = bpy.data.fonts.load("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf")
t.data.size = 0.3
t.data.space_character = 1.45
t.data.align_x = "CENTER"
t.data.extrude = 0.03
t.data.bevel_depth = 0.006
t.data.materials.append(GOLD)

w = bpy.data.worlds.new("Welt")
sc.world = w
w.use_nodes = True
nt = w.node_tree
bg = nt.nodes["Background"]
env = nt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(bpy.utils.resource_path("LOCAL") + "/datafiles/studiolights/world/sunset.exr")
mp = nt.nodes.new("ShaderNodeMapping")
mp.inputs["Rotation"].default_value = (0, 0, math.radians(140))
tc = nt.nodes.new("ShaderNodeTexCoord")
nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
nt.links.new(mp.outputs[0], env.inputs["Vector"])
lp = nt.nodes.new("ShaderNodeLightPath")
mix = nt.nodes.new("ShaderNodeMixShader")
bg2 = nt.nodes.new("ShaderNodeBackground")
bg2.inputs["Color"].default_value = (0.004, 0.0035, 0.003, 1)
bg.inputs["Strength"].default_value = 0.9
nt.links.new(env.outputs[0], bg.inputs["Color"])
nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
nt.links.new(bg.outputs[0], mix.inputs[1])  # Spiegelungen: Sonnenuntergang
nt.links.new(bg2.outputs[0], mix.inputs[2])  # Kamera sieht: fast schwarz
nt.links.new(mix.outputs[0], nt.nodes["World Output"].inputs[0])

# ---------------------------------------------------------------- Licht
def area(name, loc, rot, size, energy, col):
    L = bpy.data.lights.new(name, "AREA")
    L.size = size
    L.energy = energy
    L.color = col
    o = bpy.data.objects.new(name, L)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    sc.collection.objects.link(o)


area("Key", (-2.6, -3.2, 3.6), (52, 0, -38), 2.5, 700, (1.0, 0.86, 0.66))
area("Rim", (0.0, 2.2, 3.0), (-60, 0, 180), 4.0, 900, (1.0, 0.68, 0.32))
area("Fill", (3.2, -2.4, 1.0), (80, 0, 50), 2.0, 160, (0.55, 0.62, 0.9))

# weicher warmer Schein hinter den Buchstaben (Fläche mit kugeligem Verlauf)
bpy.ops.mesh.primitive_plane_add(size=9, location=(0, 4.0, 1.3), rotation=(math.radians(90), 0, 0))
pl = bpy.context.object
pm = bpy.data.materials.new("Schein")
pm.use_nodes = True
pn = pm.node_tree
for n in list(pn.nodes):
    pn.nodes.remove(n)
tco = pn.nodes.new("ShaderNodeTexCoord")
mpp = pn.nodes.new("ShaderNodeMapping")
mpp.inputs["Location"].default_value = (-1.0, -1.55, 0)
mpp.inputs["Scale"].default_value = (2.0, 3.1, 1)
grd = pn.nodes.new("ShaderNodeTexGradient")
grd.gradient_type = "SPHERICAL"
pw = pn.nodes.new("ShaderNodeMath")
pw.operation = "POWER"
pw.inputs[1].default_value = 3.0
em = pn.nodes.new("ShaderNodeEmission")
em.inputs["Color"].default_value = (1.0, 0.42, 0.10, 1)
mul = pn.nodes.new("ShaderNodeMath")
mul.operation = "MULTIPLY"
mul.inputs[1].default_value = 0.55
oo = pn.nodes.new("ShaderNodeOutputMaterial")
pn.links.new(tco.outputs["UV"], mpp.inputs["Vector"])
pn.links.new(mpp.outputs[0], grd.inputs["Vector"])
pn.links.new(grd.outputs["Fac"], pw.inputs[0])
pn.links.new(pw.outputs[0], mul.inputs[0])
pn.links.new(mul.outputs[0], em.inputs["Strength"])
pn.links.new(em.outputs[0], oo.inputs[0])
pl.data.materials.append(pm)
pl.visible_shadow = False
pl.visible_glossy = False

# Goldstaub (Bokeh hinter den Buchstaben)
dust = emit("Staub", (1.0, 0.62, 0.25), 9.0)
for i in range(150):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=random.uniform(0.005, 0.016),
                                          location=(random.uniform(-3.2, 3.2), random.uniform(0.8, 3.6), random.uniform(-0.2, 3.0)))
    o = bpy.context.object
    o.data.materials.append(dust)
    o.visible_shadow = False
    o.visible_glossy = False

# ---------------------------------------------------------------- Kamera
cam_d = bpy.data.cameras.new("Cam")
cam_d.lens = 58
cam_d.dof.use_dof = True
cam_d.dof.focus_distance = 5.05
cam_d.dof.aperture_fstop = 2.2
cam = bpy.data.objects.new("Cam", cam_d)
sc.collection.objects.link(cam)
cam.location = (0.0, -5.0, 1.05)
target = Vector((0, 0, 1.18 if STYLE == "ar" else 1.1))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam

# ---------------------------------------------------------------- Rendern
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.render.resolution_x = sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "Khronos PBR Neutral"
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("✓", OUT)
