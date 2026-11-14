# Standbild-Test Wohnzimmer (Ich-Sicht vom Sofa)
import bpy, sys, os, math
from mathutils import Vector, Matrix, Euler
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "futaba"))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
import figure as F, cast as C, livingroom as LR
sc = bpy.context.scene
S = LR.build()
LR.tv_material(S["screens"]["tv"], [(1, "tv_news.png")])
me = C.make("me", jacket=(0.2, 0.24, 0.34), pants=(0.3, 0.3, 0.34))
hana = F.make_figure("hana", skin=(0.96, 0.8, 0.68), hair=(0.12, 0.08, 0.07), jacket=(0.93, 0.6, 0.66), pants=(0.25, 0.28, 0.4),
                     hair_style="long", height=1.32, build=0.9, iris=(0.32, 0.2, 0.12), zipper=False, shoes=(0.95, 0.95, 0.95))
for o in me["head_parts"]:
    o.hide_render = True
# ich sitze auf dem Sofa
a = me["arm"]; a.location = (0.25, -1.92, -0.44); a.rotation_euler = (0, 0, math.pi)
for sd in ("L", "R"):
    F.rot(me, f"thigh.{sd}", 1, x=-88, z=(-6 if sd == "L" else 6)); F.rot(me, f"shin.{sd}", 1, x=88)
F.rot(me, "upperarm.L", 1, x=-28, z=-10); F.rot(me, "forearm.L", 1, x=-40)
F.rot(me, "spine", 1, x=2); F.rot(me, "neck", 1, x=2); F.rot(me, "head", 1, x=2, y=6)
# Schwester kniet auf dem Kissen links, spielt Konsole
h = hana["arm"]; h.location = (-0.95, 0.5, -0.0); h.rotation_euler = (0, 0, math.radians(-60))
z0 = 0.95 * hana["S"]
h.location.z = -(z0 * 0.64)
for sd in ("L", "R"):
    F.rot(hana, f"thigh.{sd}", 1, x=-92, z=(-8 if sd == "L" else 8)); F.rot(hana, f"shin.{sd}", 1, x=165)
    F.rot(hana, f"upperarm.{sd}", 1, x=-35, z=(10 if sd == "L" else -10)); F.rot(hana, f"forearm.{sd}", 1, x=-75)
F.rot(hana, "spine", 1, x=10); F.rot(hana, "head", 1, x=20)
F.look(hana, 1, 0, -15); F.mouth(hana, 1, 0); F.brows(hana, 1)
# Konsole in ihren Händen
ds = LR.group("ds", (0, 0, 0))
F.bone_parent(ds, hana["arm"], "hand.R"); ds.matrix_parent_inverse = Matrix(); ds.location = (0.07, 0.04, 0.0)
LR.box("dsbot", (0, 0, 0), (0.13, 0.075, 0.018), LR.soft("dsm", (0.95, 0.95, 0.97)), parent=ds)
# Kamera
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 10.5; cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 30; cam.data.clip_start = 0.03
bpy.context.view_layer.update()
b = a.data.bones["head"]
cam.parent = a; cam.parent_type = "BONE"; cam.parent_bone = "head"
cam.matrix_parent_inverse = (a.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))).inverted()
cam.matrix_basis = a.matrix_world @ Matrix.Translation(Vector((0, -0.075, 1.555)) * me["S"]) @ Euler((math.radians(90), 0, math.pi), "XYZ").to_matrix().to_4x4()
# Becher in meiner rechten Hand (IK)
tgt = bpy.data.objects.new("ikR", None); sc.collection.objects.link(tgt); tgt.parent = cam; tgt.location = (0.1, -0.24, -0.46)
c = a.pose.bones["forearm.R"].constraints.new("IK"); c.target = tgt; c.chain_count = 2
mug = LR.group("mug")
body = LR.cyl("mugbody", (0, 0, 0), 0.042, 0.095, LR.soft("mugm", (0.95, 0.94, 0.9)), verts=24); body.parent = mug
band = LR.cyl("mugband", (0, 0, 0.01), 0.0425, 0.03, LR.soft("mugb", (0.3, 0.45, 0.72)), verts=24); band.parent = mug
tea = LR.cyl("tea", (0, 0, 0.043), 0.038, 0.005, LR.soft("team", (0.55, 0.62, 0.3)), verts=24); tea.parent = mug
bpy.ops.mesh.primitive_torus_add(major_radius=0.026, minor_radius=0.007, location=(0.05, 0, 0.005), rotation=(math.radians(90), 0, 0))
hd = bpy.context.object; hd.data.materials.append(LR.soft("mugm", (0.95, 0.94, 0.9))); hd.parent = mug
mug.parent = tgt; mug.location = (-0.065, 0.0, 0.0); mug.rotation_euler = (math.radians(-72), 0, math.radians(200))
import toonlib as TL
arms = {me["arm"], hana["arm"]}
for i, o in enumerate(bpy.data.objects):
    q, hum = o, False
    while q is not None:
        if q in arms: hum = True; break
        q = q.parent
    o.pass_index = 10000 + i if hum else 1 + i
TL.comp_outlines(kn=1.0, kd=0.5, thr=0.7, fade_near=4.0, fade_far=9.0)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = int(os.environ.get("SAMPLES", 16))
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.render.resolution_percentage = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 100
sc.render.filepath = sys.argv[-2] if sys.argv[-1].isdigit() else "/tmp/room_"
sc.render.image_settings.color_mode = "RGB"
