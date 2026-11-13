import bpy, sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
HS = __import__("people").HS
h = HS.create_human(); rig = HS.add_builtin_rig(h, "default")
sc = bpy.context.scene
def R(b, x=0, y=0, z=0):
    pbn = rig.pose.bones[b]; pbn.rotation_mode = "XYZ"; pbn.rotation_euler = (math.radians(x), math.radians(y), math.radians(z))
combos = [(40, 0, 0), (-40, 0, -40), (0, 0, -45), (0, 45, 0), (0, -45, 0)]
sc.render.engine = "BLENDER_WORKBENCH"; sc.render.resolution_x, sc.render.resolution_y = 300, 400
out = "/tmp/claude-0/-home-user-U/80c3a1e7-33f7-5f3e-a21c-d7e2dae36db6/scratchpad/arm_"
bpy.ops.object.camera_add(location=(1.8, -1.8, 1.2), rotation=(math.radians(88), 0, math.radians(45))); sc.camera = bpy.context.object; sc.camera.data.lens = 35
for i, (x, y, z) in enumerate(combos):
    R("upperarm01.L", x, y, z); R("upperarm01.R", 0, 0, 0)
    sc.render.filepath = out + str(i) + ".png"; bpy.ops.render.render(write_still=True)
