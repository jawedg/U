import bpy, sys, importlib, math, os
def imp(pkg, key):
    for m in list(sys.modules):
        if m.endswith(pkg):
            return getattr(importlib.import_module(m), key)
    raise ValueError(pkg)
HumanService = imp("mpfb.services.humanservice", "HumanService")
AssetService = imp("mpfb.services.assetservice", "AssetService")
TargetService = imp("mpfb.services.targetservice", "TargetService")
HOP = imp("mpfb.entities.objectproperties", "HumanObjectProperties")
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
h = HumanService.create_human()
for k, v in (("gender", 1.0), ("age", 0.45), ("muscle", 0.6), ("weight", 0.5), ("caucasian", 1.0), ("african", 0.0), ("asian", 0.0)):
    HOP.set_value(k, v, entity_reference=h)
TargetService.reapply_macro_details(h)
rig = HumanService.add_builtin_rig(h, "default")
skin = AssetService.find_asset_absolute_path("young_caucasian_male.mhmat", asset_subdir="skins")
print("SKIN", skin)
HumanService.set_character_skin(skin, h, skin_type="MAKESKIN")
for sub, fn, typ in (("eyes", "low-poly.mhclo", "Eyes"), ("eyebrows", "eyebrow001.mhclo", "Eyebrows"), ("eyelashes", "eyelashes01.mhclo", "Eyelashes"),
                     ("teeth", "teeth_base.mhclo", "Teeth"), ("tongue", "tongue01.mhclo", "Tongue"), ("hair", "short02.mhclo", "Hair"),
                     ("clothes", "male_casualsuit04.mhclo", "Clothes"), ("clothes", "shoes02.mhclo", "Clothes")):
    p = AssetService.find_asset_absolute_path(fn, asset_subdir=sub)
    print("ASSET", fn, p)
    if p: HumanService.add_mhclo_asset(p, h, asset_type=typ)
print("OBJS", [o.name for o in bpy.data.objects])
UD = "/home/user/mh/mpfb2/src/mpfb/data/targets/expression/units/caucasian/"
def unit(name, w):
    TargetService.load_target(h, UD + name + ".target.gz", weight=w, name="ex_" + name)
mode = sys.argv[-1]
if mode == "fear":
    for n, w in (("eyebrows-left-inner-up", 1.0), ("eyebrows-right-inner-up", 1.0), ("eyebrows-left-up", 0.4), ("eyebrows-right-up", 0.4),
                 ("eye-left-opened-up", 0.8), ("eye-right-opened-up", 0.8), ("mouth-open", 0.45), ("mouth-depression-retraction", 0.5), ("neck-platysma", 0.4)):
        unit(n, w)
sc = bpy.context.scene
bpy.ops.object.camera_add(location=(0.12, -0.75, 1.62), rotation=(math.radians(90), 0, math.radians(8)))
sc.camera = bpy.context.object; sc.camera.data.lens = 50
bpy.ops.object.light_add(type="AREA", location=(-0.8, -1.0, 2.0)); l = bpy.context.object; l.data.energy = 120; l.data.size = 1.0
l.rotation_euler = (math.radians(60), 0, math.radians(-40))
bpy.ops.object.light_add(type="AREA", location=(1.0, -0.6, 1.8)); l = bpy.context.object; l.data.energy = 40; l.data.size = 1.0
l.rotation_euler = (math.radians(70), 0, math.radians(55))
bpy.ops.object.light_add(type="AREA", location=(0.3, 0.8, 2.1)); l = bpy.context.object; l.data.energy = 60; l.data.size = 0.8
l.rotation_euler = (math.radians(-60), 0, 0)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.25, 0.27, 0.3, 1)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1350, 50
sc.render.filepath = "/tmp/claude-0/-home-user-U/80c3a1e7-33f7-5f3e-a21c-d7e2dae36db6/scratchpad/mpfb_" + mode + ".png"
bpy.ops.render.render(write_still=True)
print("H", max((h.matrix_world @ v.co).z for v in h.data.vertices))
