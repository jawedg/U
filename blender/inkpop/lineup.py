import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "futaba"))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
import figure as F, cast as C
from mathutils import Vector
sc = bpy.context.scene
figs = []
for i, nm in enumerate(("oma", "yui", "sota", "tanaka", "fahrer")):
    f = C.make(nm)
    f["arm"].location = ((i - 2) * 0.62, 0, 0)
    F.relaxed(f, 1)
    figs.append(f)
F.look(figs[2], 1, 30, 0)
F.look(figs[1], 1, -30, 10)
F.brows(figs[0], 1, 1.0, 0.8)
F.mouth(figs[3], 1, 0.7)
bpy.ops.mesh.primitive_plane_add(size=20)
bpy.context.object.data.materials.append(F.ink_mat("floor", (0.62, 0.66, 0.72), shade=0.85))
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 2.5, 3), rotation=(math.radians(90), 0, 0))
bpy.context.object.data.materials.append(F.ink_mat("wall", (0.86, 0.88, 0.9), shade=0.85))
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 1.6; sun.data.angle = math.radians(0.4)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(-40))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.92, 0.95, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.25
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0, -4.2, 1.2); cam.data.lens = 35
cam.rotation_euler = (Vector((0, 0, 0.95)) - cam.location).to_track_quat("-Z", "Y").to_euler()
import toonlib as TL
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16
arms = {f["arm"] for f in figs}
for o in bpy.data.objects:
    o.pass_index = 10000 if o.parent in arms else 1
TL.comp_outlines(kn=1.2, kd=0.5, thr=0.55)
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 60
sc.render.filepath = sys.argv[-1]
