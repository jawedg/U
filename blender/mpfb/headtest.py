import bpy, sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
HS = __import__("people").HS
h = HS.create_human(); rig = HS.add_builtin_rig(h, "default")
sc = bpy.context.scene
pbn = rig.pose.bones["neck02"]; pbn.rotation_mode = "XYZ"; pbn.rotation_euler = (0, math.radians(40), 0)
sc.render.engine = "BLENDER_WORKBENCH"; sc.render.resolution_x, sc.render.resolution_y = 300, 300
bpy.ops.object.camera_add(location=(0, -1.2, 1.6), rotation=(math.radians(90), 0, 0)); sc.camera = bpy.context.object; sc.camera.data.lens = 50
sc.render.filepath = "/tmp/claude-0/-home-user-U/80c3a1e7-33f7-5f3e-a21c-d7e2dae36db6/scratchpad/head_y40.png"; bpy.ops.render.render(write_still=True)
