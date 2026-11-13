import bpy, sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
import people as P
p = P.make_person("nb", gender=1.0, age=0.42, hair="short02", clothes=("male_casualsuit02", "shoes02"))
p["rig"].location = (0, 0, -0.33)
P.seated(p, 1); P.set_face(p, 1, "neutral"); P.set_face(p, 10, "fear")
P.rot(p, "neck02", 1); P.rot(p, "head", 1)
sc = bpy.context.scene
bpy.ops.mesh.primitive_cube_add(location=(0, 0.05, 0.44)); c = bpy.context.object; c.scale = (0.22, 0.2, 0.02)
bpy.ops.object.light_add(type="AREA", location=(-1.0, -1.5, 2.2)); l = bpy.context.object; l.data.energy = 250; l.data.size = 1.5; l.rotation_euler = (math.radians(55), 0, math.radians(-35))
bpy.ops.object.light_add(type="AREA", location=(1.2, -1.0, 1.8)); l = bpy.context.object; l.data.energy = 80; l.data.size = 1.2; l.rotation_euler = (math.radians(65), 0, math.radians(50))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.3, 0.32, 0.35, 1)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 12
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 800, 1000, 50
out = "/tmp/claude-0/-home-user-U/80c3a1e7-33f7-5f3e-a21c-d7e2dae36db6/scratchpad/pt_"
for tag, loc, rotz, f, lens in (("side", (2.6, 0.0, 0.85), 90, 1, 35), ("front0", (0.0, -2.4, 0.9), 0, 1, 35)):
    bpy.ops.object.camera_add(location=loc, rotation=(math.radians(90 if tag != "side" else 88), 0, math.radians(rotz)))
    sc.camera = bpy.context.object; sc.camera.data.lens = lens
    sc.frame_set(f); sc.render.filepath = out + tag + ".png"; bpy.ops.render.render(write_still=True)
