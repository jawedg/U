# Testbühne für Sota: Porträt + Ganzkörper, Drehung, Blinzeln, Blick, Sprechen.
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "futaba"))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
import figure as F
sc = bpy.context.scene
sota = F.make_figure("sota")
arm = sota["arm"]
F.relaxed(sota, 1)
# Drehung 360° über 4 s, dann vorne: blinzeln, schauen, reden
for fr, z in ((1, 0), (97, 360)):
    arm.rotation_euler = (0, 0, math.radians(z))
    arm.keyframe_insert("rotation_euler", frame=fr)
for fc in arm.animation_data.action.fcurves if hasattr(arm.animation_data.action, "fcurves") else []:
    for k in fc.keyframe_points:
        k.interpolation = "LINEAR"
F.look(sota, 1)
F.look(sota, 100, 0, 0)
F.look(sota, 108, 25, 0)
F.look(sota, 124, 25, 0)
F.look(sota, 130, -20, 5)
F.look(sota, 146, -20, 5)
F.look(sota, 152, 0, 0)
F.blink(sota, 40)
F.blink(sota, 118)
F.blink(sota, 160)
F.brows(sota, 1)
F.brows(sota, 150, 0)
F.brows(sota, 158, 1.0, 0.6)
F.mouth(sota, 1, 0)
import random
r = random.Random(3)
for fr in range(165, 205, 3):
    F.mouth(sota, fr, r.uniform(0.2, 1.0))
F.mouth(sota, 206, 0)
# Kopf/Arm-Gesten
F.rot(sota, "head", 150)
F.rot(sota, "head", 158, x=-6, y=8)
F.rot(sota, "upperarm.R", 160, x=0)
F.rot(sota, "upperarm.R", 170, x=35, z=-10)
F.rot(sota, "forearm.R", 160, x=-12)
F.rot(sota, "forearm.R", 170, x=-70)
# Raum: Wand + Boden
import bmesh
def plane(name, loc, rot, size, col):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(F.ink_mat(name, col, shade=0.85))
    return o
plane("floor", (0, 0, 0), (0, 0, 0), 12, (0.62, 0.66, 0.72))
plane("wall", (0, 2.5, 3), (math.radians(90), 0, 0), 12, (0.86, 0.88, 0.9))
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sc.collection.objects.link(sun)
sun.data.energy = 1.6
sun.data.angle = math.radians(0.4)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(-40))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.92, 0.95, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.25
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
shot = os.environ.get("SHOT", "face")
if shot == "face":
    cam.location = (0.15, -1.25, 1.5)
    cam.data.lens = 42
    target = (0, 0, 1.38)
else:
    cam.location = (0.2, -3.2, 1.1)
    cam.data.lens = 35
    target = (0, 0, 0.9)
from mathutils import Vector
d = Vector(target) - cam.location
cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
cam.data.sensor_fit = "VERTICAL"
import toonlib as TL
TL.sc = sc
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 16
for o in bpy.data.objects:
    o.pass_index = 10000 if (o.parent == arm) else 1
TL.comp_outlines(kn=1.2, kd=0.5, thr=0.55)
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.render.resolution_percentage = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 50
sc.render.filepath = sys.argv[-2] if sys.argv[-1].isdigit() else "/tmp/ink_"
sc.frame_start, sc.frame_end = 1, 210
sc.render.fps = 24
