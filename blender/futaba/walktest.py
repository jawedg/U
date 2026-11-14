import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
import toonlib as TL
from toonlib import P, sc
from mathutils import Vector
a = P.make_person("a", gender=1.0, age=0.4, skin="young_asian_male", race=("asian", 1.0), hair="short02", clothes=("male_casualsuit02", "shoes02"))
b = P.make_person("b", gender=0.0, age=0.4, skin="young_asian_female", race=("asian", 1.0), hair="bob02", clothes=("female_casualsuit01", "shoes03"))
TL.toon_all()
TL.toon_person(a, (0.95, 0.78, 0.64), (0.1, 0.08, 0.07))
TL.toon_person(b, (0.95, 0.8, 0.68), (0.12, 0.08, 0.06))
TL.locomotion(a, [Vector((-3, 0, 0)), Vector((3, 0, 0))], 1, 1.3)
TL.locomotion(b, [Vector((-6, 1.2, 0)), Vector((6, 1.2, 0))], 1, 4.0, run=True)
bpy.ops.mesh.primitive_plane_add(size=40)
g = bpy.context.object
m = TL.flat_mat("ground", (0.6, 0.62, 0.6)); g.data.materials.append(m)
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3; sun.rotation_euler = (0.7, 0.3, 0.5)
w = sc.world or bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.75, 0.82, 0.9, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0, -7, 1.2); cam.rotation_euler = (math.radians(88), 0, 0); cam.data.lens = 28
TL.outlines()
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 4
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 30
sc.frame_start, sc.frame_end, sc.frame_step = 1, 48, 3
sc.render.filepath = sys.argv[-1]
