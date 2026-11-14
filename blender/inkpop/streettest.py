import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "futaba"))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
import street as ST, figure as F
from mathutils import Vector
sc = bpy.context.scene
S = ST.build()
ST.sky(os.environ.get("DAY", "1") == "1")
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.location = Vector((0.6, 3.0, 1.6)); cam.data.lens = 14; cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 30
cam.rotation_euler = (Vector((0.2, 30, 2.4)) - cam.location).to_track_quat("-Z", "Y").to_euler()
import toonlib as TL
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 8
for o in bpy.data.objects: o.pass_index = 1
TL.comp_outlines(kn=1.2, kd=0.5, thr=0.55)
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, 67
sc.render.filepath = sys.argv[-1]
