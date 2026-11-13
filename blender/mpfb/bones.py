import bpy, sys, importlib
def imp(pkg, key):
    for m in list(sys.modules):
        if m.endswith(pkg): return getattr(importlib.import_module(m), key)
HS = imp("mpfb.services.humanservice", "HumanService")
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
h = HS.create_human(); rig = HS.add_builtin_rig(h, "default")
print("BONES", [b.name for b in rig.data.bones if not any(x in b.name for x in ("finger","toe","metacarpal","eye","lip","tongue","jaw","brow","cheek","nose","lid","ear","temple","chin","oris","levator","orbicularis","risorius"))])
print("FACE", [b.name for b in rig.data.bones if any(x in b.name for x in ("jaw","eye","lid","brow"))][:30])
import mathutils
for n in ("upperleg01.L","lowerleg01.L","spine01","neck01","head","upperarm01.L","lowerarm01.L","root"):
    b = rig.data.bones.get(n)
    if b: print(n, tuple(round(x,3) for x in b.head_local), tuple(round(x,3) for x in b.tail_local))
