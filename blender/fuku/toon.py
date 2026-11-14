# Comic-Look-Test: baut die Szene aus fuku.py und stellt alle Materialien auf Cel-Shading (flache Farben,
# 3 Helligkeitsstufen) + schwarze Umrisse (Freestyle) um.
# blender -b --python toon.py -f N -- <ausgabe_präfix> <prozent>
import bpy, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "fuku.py")
g = {"__file__": SRC, "__name__": "__fuku__"}
exec(compile(open(SRC).read().replace('hair="short03"', 'hair="short02"'), SRC, "exec"), g)
sc = bpy.context.scene


def src_of(nt, sock):
    """Verknüpfte Ausgabe oder None."""
    return sock.links[0].from_socket if sock.is_linked else None


def toonify(m):
    if not m.use_nodes:
        return
    nt = m.node_tree
    out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output), None)
    p = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not out or not p:
        return
    L = nt.links
    base_src = src_of(nt, p.inputs["Base Color"])
    base_val = p.inputs["Base Color"].default_value[:]
    alpha_src = src_of(nt, p.inputs["Alpha"])
    alpha_val = p.inputs["Alpha"].default_value
    em_src = src_of(nt, p.inputs["Emission Color"])
    em_val = p.inputs["Emission Color"].default_value[:]
    es_src = src_of(nt, p.inputs["Emission Strength"])
    es_val = p.inputs["Emission Strength"].default_value

    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    L.new(dif.outputs[0], s2r.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (0.30, 0.31, 0.38, 1)
    e[1].position, e[1].color = 0.05, (0.62, 0.63, 0.70, 1)
    e3 = e.new(0.28)
    e3.color = (1, 1, 1, 1)
    L.new(s2r.outputs[0], ramp.inputs[0])
    mul = nt.nodes.new("ShaderNodeMixRGB")
    mul.blend_type = "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    if base_src:
        L.new(base_src, mul.inputs[1])
    else:
        mul.inputs[1].default_value = base_val
    L.new(ramp.outputs[0], mul.inputs[2])
    flat = nt.nodes.new("ShaderNodeEmission")
    L.new(mul.outputs[0], flat.inputs[0])
    glow = nt.nodes.new("ShaderNodeEmission")
    if em_src:
        L.new(em_src, glow.inputs[0])
    else:
        glow.inputs[0].default_value = em_val
    if es_src:
        L.new(es_src, glow.inputs[1])
    else:
        glow.inputs[1].default_value = es_val
    add = nt.nodes.new("ShaderNodeAddShader")
    L.new(flat.outputs[0], add.inputs[0])
    L.new(glow.outputs[0], add.inputs[1])
    final = add.outputs[0]
    if alpha_src or alpha_val < 0.999:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        if alpha_src:
            L.new(alpha_src, mix.inputs[0])
        else:
            mix.inputs[0].default_value = alpha_val
        L.new(tr.outputs[0], mix.inputs[1])
        L.new(final, mix.inputs[2])
        final = mix.outputs[0]
    for lk in list(out.inputs[0].links):
        L.remove(lk)
    L.new(final, out.inputs[0])


skip = {"lens", "beam"}
for m in bpy.data.materials:
    if any(s in m.name.lower() for s in skip):
        continue
    try:
        toonify(m)
    except Exception as ex:
        print("toon skip", m.name, ex)

# Umrisse
sc.render.use_freestyle = True
sc.render.line_thickness_mode = "ABSOLUTE"
sc.render.line_thickness = 2.2
vl = sc.view_layers[0]
vl.use_freestyle = True
fs = vl.freestyle_settings
ls = fs.linesets[0] if fs.linesets else fs.linesets.new("L")
ls.select_by_visibility = True
ls.select_crease = True
ls.select_silhouette = True
ls.select_border = True
ls.select_external_contour = True
fs.crease_angle = 2.2
ls.linestyle.color = (0.04, 0.04, 0.06)
ls.linestyle.thickness = 2.2
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
sc.eevee.taa_render_samples = 4
# Staub/Nebel aus (passt nicht zum Comic)
for o in bpy.data.objects:
    if o.name.lower().startswith("dust"):
        o.hide_render = True

# ---------- Cartoon-Gesichter ----------
from mathutils import Matrix, Vector
import bmesh


def flat_mat(name, col):
    m = bpy.data.materials.new(name)
    m.blend_method = "OPAQUE" if hasattr(m, "blend_method") else None
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1)
    toonify(m)
    return m


def sphere(name, r, mat):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=r)
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def bone_child(o, rig, bone, world):
    b = rig.data.bones[bone]
    rest = rig.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))
    o.parent = rig
    o.parent_type = "BONE"
    o.parent_bone = bone
    o.matrix_parent_inverse = rest.inverted()
    o.matrix_basis = world


WHITE = flat_mat("toon_eyewhite", (0.97, 0.96, 0.93))
PUPIL = flat_mat("toon_pupil", (0.05, 0.04, 0.04))
HAIRC = {"me": (0.08, 0.07, 0.07), "k1": (0.10, 0.07, 0.05), "k2": (0.16, 0.15, 0.15)}
SKINC = {"me": (0.93, 0.76, 0.62), "k1": (0.95, 0.78, 0.64), "k2": (0.86, 0.68, 0.54)}
EYE_R, EYE_SQ = 0.0175, 0.55
for key in ("ME", "K1", "K2"):
    p = g[key]
    h, rig, nm = p["h"], p["rig"], p["name"]
    skin = flat_mat("toon_skin_" + nm, SKINC[nm])
    for i in range(len(h.material_slots)):
        h.material_slots[i].material = skin
    kids = [o for o in bpy.data.objects if o.parent in (h, rig) and o.type == "MESH" and o != h]
    for o in kids:
        n = o.name.lower()
        if "eyelash" in n or (("eye" in n) and "brow" not in n):
            o.hide_render = True
        elif "brow" in n:
            o.data.materials.clear()
            o.data.materials.append(flat_mat("toon_brow_" + nm, HAIRC[nm]))
        elif "teeth" in n:
            pass
        elif any(s in n for s in ("short", "hair", "bob", "long", "ponytail")):
            o.data.materials.clear()
            o.data.materials.append(flat_mat("toon_hair_" + nm, HAIRC[nm]))
            so = o.modifiers.new("dick", "SOLIDIFY")
            so.thickness, so.offset = 0.012, -1.0
    print("PERSON", nm, [o.name for o in kids])
    whites = []
    for side in ("L", "R"):
        b = rig.data.bones["eye." + side]
        c = rig.matrix_world @ b.head_local
        fwd = (rig.matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
        w = sphere(f"{nm}_eye{side}", EYE_R, WHITE)
        pu = sphere(f"{nm}_pup{side}", EYE_R * 0.42, PUPIL)
        rot = rig.matrix_world.to_3x3().to_4x4()
        mw = Matrix.Translation(c + fwd * 0.011) @ rot @ Matrix.Diagonal((1, EYE_SQ, 1.12, 1))
        mp = Matrix.Translation(c + fwd * (0.011 + EYE_R * EYE_SQ * 0.92)) @ rot @ Matrix.Diagonal((1, 0.35, 1.1, 1))
        bone_child(w, rig, "eye." + side, mw)
        bone_child(pu, rig, "eye." + side, mp)
        whites.append((w, pu))
    # Blinzeln: Augen in der Höhe zusammendrücken, wenn das Lid-Shape-Key auf 1 geht
    ad = h.data.shape_keys.animation_data
    if ad and ad.action:
        frames = set()
        for fc in ad.action.fcurves if hasattr(ad.action, "fcurves") else []:
            if "eye-left-closure" in fc.data_path:
                for kp in fc.keyframe_points:
                    if kp.co[1] > 0.9:
                        frames.add(int(kp.co[0]))
        for w, pu in whites:
            for o in (w, pu):
                s0 = o.scale.copy()
                o.keyframe_insert("scale", frame=1)
                for f in sorted(frames):
                    o.scale = s0
                    o.keyframe_insert("scale", frame=f - 2)
                    o.keyframe_insert("scale", frame=f + 3)
                    o.scale = (s0[0], s0[1], s0[2] * 0.08)
                    o.keyframe_insert("scale", frame=f)
                o.scale = s0
        print("BLINKS", nm, sorted(frames))

# Testkamera vor einem Gesicht (TOONCAM=k1|k2)
if os.environ.get("TOONCAM"):
    p = g[os.environ["TOONCAM"].upper()]
    bpy.context.view_layer.update()
    hb = p["rig"].pose.bones["head"]
    hp = p["rig"].matrix_world @ hb.head
    fwd = (p["rig"].matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
    cam = bpy.data.objects.new("tcam", bpy.data.cameras.new("tcam"))
    sc.collection.objects.link(cam)
    cam.data.lens = 50
    cam.location = hp + fwd * 0.9 + Vector((0, 0, 0.08))
    d = (hp + Vector((0, 0, 0.08))) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
