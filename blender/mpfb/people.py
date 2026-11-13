# Menschen mit MPFB: Haut, Haare, Kleidung, Skelett, Mimik-Formen (auch auf Brauen/Wimpern übertragen),
# Sitz-/Stehpose, weiche Idle-Bewegung (Atmen, kleine Kopfbewegungen), Blinzeln.
import bpy, sys, importlib, math, random
from mathutils import Euler, Vector


def _imp(pkg, key):
    for m in list(sys.modules):
        if m.endswith(pkg):
            return getattr(importlib.import_module(m), key)
    raise ValueError(pkg)


HS = _imp("mpfb.services.humanservice", "HumanService")
AS = _imp("mpfb.services.assetservice", "AssetService")
TS = _imp("mpfb.services.targetservice", "TargetService")
CS = _imp("mpfb.services.clothesservice", "ClothesService")
HOP = _imp("mpfb.entities.objectproperties", "HumanObjectProperties")
UNITS = "/home/user/mh/mpfb2/src/mpfb/data/targets/expression/units/caucasian/"
EX = ["eyebrows-left-inner-up", "eyebrows-right-inner-up", "eyebrows-left-up", "eyebrows-right-up", "eyebrows-left-down", "eyebrows-right-down",
      "eye-left-opened-up", "eye-right-opened-up", "eye-left-closure", "eye-right-closure", "mouth-open", "mouth-depression-retraction",
      "mouth-retraction", "mouth-compression", "neck-platysma", "mouth-corner-puller"]
# Ausdrücke als Mischung der Formen
EXPR = {
    "neutral": {},
    "surprise": {"eyebrows-left-up": 0.9, "eyebrows-right-up": 0.9, "eye-left-opened-up": 0.7, "eye-right-opened-up": 0.7, "mouth-open": 0.25},
    "fear": {"eyebrows-left-inner-up": 1.0, "eyebrows-right-inner-up": 1.0, "eyebrows-left-up": 0.35, "eyebrows-right-up": 0.35,
             "eye-left-opened-up": 0.85, "eye-right-opened-up": 0.85, "mouth-open": 0.22, "mouth-retraction": 0.35, "neck-platysma": 0.45},
    "worried": {"eyebrows-left-inner-up": 0.7, "eyebrows-right-inner-up": 0.7, "eye-left-opened-up": 0.3, "eye-right-opened-up": 0.3,
                "mouth-compression": 0.3},
    "stern": {"eyebrows-left-down": 0.6, "eyebrows-right-down": 0.6, "mouth-compression": 0.4},
}


def make_person(name, gender=0.0, age=0.4, muscle=0.5, weight=0.5, race=("caucasian", 1.0), skin="young_caucasian_male",
                hair="short02", clothes=("male_casualsuit04", "shoes02"), eyebrows="eyebrow001", iris=(0.18, 0.1, 0.05)):
    h = HS.create_human()
    for k, v in (("gender", gender), ("age", age), ("muscle", muscle), ("weight", weight), ("african", 0.0), ("asian", 0.0), ("caucasian", 0.0)):
        HOP.set_value(k, v, entity_reference=h)
    HOP.set_value(race[0], race[1], entity_reference=h)
    TS.reapply_macro_details(h)
    rig = HS.add_builtin_rig(h, "default")
    HS.set_character_skin(AS.find_asset_absolute_path(skin + ".mhmat", asset_subdir="skins"), h, skin_type="MAKESKIN")
    head_assets = []
    for sub, fn, typ, mt in (("eyes", "low-poly", "Eyes", "PROCEDURAL_EYES"), ("eyebrows", eyebrows, "Eyebrows", "MAKESKIN"),
                             ("eyelashes", "eyelashes01", "Eyelashes", "MAKESKIN"), ("teeth", "teeth_base", "Teeth", "MAKESKIN"),
                             ("tongue", "tongue01", "Tongue", "MAKESKIN"), ("hair", hair, "Hair", "MAKESKIN")) + tuple(("clothes", c, "Clothes", "MAKESKIN") for c in clothes):
        if not fn:
            continue
        p = AS.find_asset_absolute_path(fn + ".mhclo", asset_subdir=sub)
        if not p:
            print("FEHLT", fn)
            continue
        o = HS.add_mhclo_asset(p, h, asset_type=typ, material_type=mt)
        if typ in ("Eyebrows", "Eyelashes"):
            head_assets.append(o)
        if typ == "Eyes":
            try:
                g = [n for n in o.active_material.node_tree.nodes if n.type == "GROUP"][0]
                for k in ("IrisMajorColor", "IrisMinorColor"):
                    if k in g.inputs:
                        g.inputs[k].default_value = (*[c * (1.0 if k == "IrisMajorColor" else 0.55) for c in iris], 1)
            except Exception as ex:
                print("Augenfarbe:", ex)
    # Zunge im Mund lassen
    for o in bpy.data.objects:
        if o.parent in (h, rig) and "tongue" in o.name:
            o.hide_render = True
    # Mimik-Formen laden (Wert 0) und auf Brauen/Wimpern übertragen
    for u in EX:
        TS.load_target(h, UNITS + u + ".target.gz", weight=0.0, name="ex_" + u)
    keys = h.data.shape_keys.key_blocks
    for o in head_assets:
        base = [v.co.copy() for v in o.data.vertices]
        shapes = {}
        for u in EX:
            for k in EX:
                keys["ex_" + k].value = 0.0
            keys["ex_" + u].value = 1.0
            CS.fit_clothes_to_human(o, h, set_parent=False)
            shapes[u] = [v.co.copy() for v in o.data.vertices]
        keys["ex_" + EX[-1]].value = 0.0
        for v, c in zip(o.data.vertices, base):
            v.co = c
        o.shape_key_add(name="Basis", from_mix=False)
        for u in EX:
            sk = o.shape_key_add(name="ex_" + u, from_mix=False)
            for i, c in enumerate(shapes[u]):
                sk.data[i].co = c
    for t in [n for n in keys.keys() if n.startswith("temporary_fitting_key")]:
        h.shape_key_remove(keys[t])
    rig.name = name
    return {"h": h, "rig": rig, "heads": head_assets, "name": name}


def set_face(p, frame, expr="neutral", amount=1.0, extra=None):
    vals = {u: 0.0 for u in EX}
    for k, v in EXPR[expr].items():
        vals[k] = v * amount
    for k, v in (extra or {}).items():
        vals[k] = v
    for obj in [p["h"]] + p["heads"]:
        kb = obj.data.shape_keys.key_blocks
        for u, v in vals.items():
            k = kb.get("ex_" + u)
            if k is not None:
                k.value = v
                k.keyframe_insert("value", frame=frame)
    p.setdefault("face_keys", []).append((frame, vals))


def blink(p, frame):
    """Lid zu und wieder auf, ohne die übrige Mimik zu stören."""
    prev = [v for f, v in sorted(p.get("face_keys", [])) if f <= frame]
    cur = prev[-1] if prev else {u: 0.0 for u in EX}
    for obj in [p["h"]] + p["heads"]:
        kb = obj.data.shape_keys.key_blocks
        for side in ("left", "right"):
            k = kb.get(f"ex_eye-{side}-closure")
            if k is None:
                continue
            for f, v in ((frame - 2, cur.get(f"eye-{side}-closure", 0)), (frame, 1.0), (frame + 3, cur.get(f"eye-{side}-closure", 0))):
                k.value = v
                k.keyframe_insert("value", frame=f)
            ko = kb.get(f"ex_eye-{side}-opened-up")
            if ko is not None:
                for f, v in ((frame - 2, cur.get(f"eye-{side}-opened-up", 0)), (frame, 0.0), (frame + 3, cur.get(f"eye-{side}-opened-up", 0))):
                    ko.value = v
                    ko.keyframe_insert("value", frame=f)


def pb(p, name):
    return p["rig"].pose.bones[name]


def rot(p, bone, frame, x=0.0, y=0.0, z=0.0):
    b = pb(p, bone)
    b.rotation_mode = "XYZ"
    b.rotation_euler = (math.radians(x), math.radians(y), math.radians(z))
    b.keyframe_insert("rotation_euler", frame=frame)


def seated(p, frame, arms_on_desk=True):
    for s in ("L", "R"):
        rot(p, f"upperleg01.{s}", frame, x=-88)
        rot(p, f"lowerleg01.{s}", frame, x=92)
        rot(p, f"foot.{s}", frame, x=-10)
        if arms_on_desk:
            rot(p, f"upperarm01.{s}", frame, x=30, y=(40 if s == "L" else -40))
            rot(p, f"lowerarm01.{s}", frame, x=65)
        else:
            rot(p, f"upperarm01.{s}", frame, y=(48 if s == "L" else -48))
    rot(p, "spine03", frame, x=6)


def idle(p, f0, f1, seed=0, breath=True, head=True, amp=1.0):
    """Atmen + kleine, weiche Kopfbewegungen (keine Roboter-Starre)."""
    r = random.Random(seed)
    ph = [r.uniform(0, 6.28) for _ in range(6)]
    for f in range(f0, f1, 6):
        t = f / 24.0
        if breath:
            b = math.sin(t * 2 * math.pi / 3.6 + ph[0])
            rot(p, "spine02", f, x=0.8 * b * amp)
        if head:
            rot(p, "neck02", f, x=1.5 * amp * math.sin(t * 0.7 + ph[1]) + 0.8 * math.sin(t * 1.9 + ph[2]),
                z=2.0 * amp * math.sin(t * 0.5 + ph[3]), y=0.8 * amp * math.sin(t * 0.9 + ph[4]))
