# Comic-Look: Cel-Shading-Materialien, Umrisse, Cartoon-Gesichter für MPFB-Menschen, Geh-/Renn-Zyklen.
import bpy, bmesh, math, os, sys, random
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "mpfb"))
import people as P

sc = bpy.context.scene


def src_of(nt, sock):
    """Verknüpfte Ausgabe oder None."""
    return sock.links[0].from_socket if sock.is_linked else None


def toonify(m):
    if not m.use_nodes or m.get("toon"):
        return
    m["toon"] = 1
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



WHITE = PUPIL = None


def toon_all(skip=("lens", "beam", "toon_")):
    for m in bpy.data.materials:
        if any(s in m.name.lower() for s in skip):
            continue
        try:
            toonify(m)
        except Exception as ex:
            print("toon skip", m.name, ex)


def outlines(th=2.2):
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = "ABSOLUTE"
    sc.render.line_thickness = th
    vl = sc.view_layers[0]
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    ls = fs.linesets[0] if fs.linesets else fs.linesets.new("L")
    ls.select_by_visibility = True
    for k in ("select_crease", "select_silhouette", "select_border", "select_external_contour"):
        setattr(ls, k, True)
    fs.crease_angle = 2.2
    ls.linestyle.color = (0.04, 0.04, 0.06)
    ls.linestyle.thickness = th
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"


def toon_person(p, skin_col, hair_col, eye_r=0.0175):
    """Haut/Haare flach, echte Augen weg, große Comic-Augen (folgen den Augen-Knochen), Blinzeln über eye_blink()."""
    global WHITE, PUPIL
    if WHITE is None:
        WHITE = flat_mat("toon_eyewhite", (0.97, 0.96, 0.93))
        PUPIL = flat_mat("toon_pupil", (0.05, 0.04, 0.04))
    h, rig, nm = p["h"], p["rig"], p["name"]
    skin = flat_mat("toon_skin_" + nm, skin_col)
    for i in range(len(h.material_slots)):
        h.material_slots[i].material = skin
    for o in [o for o in bpy.data.objects if o.parent in (h, rig) and o.type == "MESH" and o != h]:
        n = o.name.lower()
        if "eyelash" in n or ("eye" in n and "brow" not in n):
            o.hide_render = True
        elif "brow" in n:
            o.data.materials.clear()
            o.data.materials.append(flat_mat("toon_brow_" + nm, hair_col))
        elif any(s in n for s in ("short", "hair", "bob", "long", "ponytail", "braid", "afro")):
            o.data.materials.clear()
            o.data.materials.append(flat_mat("toon_hair_" + nm, hair_col))
            so = o.modifiers.new("dick", "SOLIDIFY")
            so.thickness, so.offset = 0.012, -1.0
    sq = 0.55
    p["eyes"] = []
    rw = rig.matrix_world.copy()
    for side in ("L", "R"):
        b = rig.data.bones["eye." + side]
        c = rw @ b.head_local
        fwd = (rw.to_3x3() @ Vector((0, -1, 0))).normalized()
        rot = rw.to_3x3().to_4x4()
        w = sphere(f"{nm}_eye{side}", eye_r, WHITE)
        pu = sphere(f"{nm}_pup{side}", eye_r * 0.42, PUPIL)
        bone_child(w, rig, "eye." + side, Matrix.Translation(c + fwd * 0.011) @ rot @ Matrix.Diagonal((1, sq, 1.12, 1)))
        bone_child(pu, rig, "eye." + side, Matrix.Translation(c + fwd * (0.011 + eye_r * sq * 0.92)) @ rot @ Matrix.Diagonal((1, 0.35, 1.1, 1)))
        p["eyes"] += [w, pu]


def eye_blink(p, frame):
    for o in p["eyes"]:
        s0 = o.scale.copy()
        for f, k in ((frame - 2, 1.0), (frame, 0.08), (frame + 3, 1.0)):
            o.scale = (s0[0], s0[1], s0[2] * k)
            o.keyframe_insert("scale", frame=f)
        o.scale = s0


def look_pupils(p, frame, dx=0.0, dz=0.0):
    """Augen-Knochen drehen (Blick links/rechts, hoch/runter) in Grad."""
    for s in ("L", "R"):
        P.rot(p, "eye." + s, frame, x=dz, z=dx)


def heading(d):
    return math.atan2(d.x, -d.y)


def locomotion(p, path, f0, speed, run=False, fps=24, step=2, arms=True, until=None, spine=True):
    """path: Liste von Vector-Punkten (z=0). Läuft mit speed m/s ab Frame f0; gibt End-Frame zurück."""
    rig = p["rig"]
    segs = []
    tot = 0.0
    for a, b in zip(path, path[1:]):
        L = (b - a).length
        segs.append((a, b, tot, L))
        tot += L
    stride = 2.5 if run else 1.45
    A, K, Aa, bob = (42, 95, 45, 0.045) if run else (24, 48, 18, 0.014)
    f1 = f0 + int(tot / speed * fps)
    if until:
        f1 = min(f1, until)
    yaw_prev = None
    for f in list(range(f0, f1, step)) + [f1]:
        s = min(tot, (f - f0) / fps * speed)
        for a, b, t0, L in segs:
            if s <= t0 + L or (a, b, t0, L) == segs[-1]:
                u = 0 if L == 0 else min(1, (s - t0) / L)
                pos = a.lerp(b, u)
                yaw = heading(b - a)
                break
        if yaw_prev is not None:
            while yaw - yaw_prev > math.pi:
                yaw -= 2 * math.pi
            while yaw - yaw_prev < -math.pi:
                yaw += 2 * math.pi
        yaw_prev = yaw
        ph = 2 * math.pi * s / stride
        rig.location = (pos.x, pos.y, bob * math.cos(2 * ph) - (0.03 if run else 0))
        rig.keyframe_insert("location", frame=f)
        rig.rotation_euler = (0, 0, yaw)
        rig.keyframe_insert("rotation_euler", frame=f)
        for sd, sg in (("L", 1), ("R", -1)):
            sp = math.sin(ph) * sg
            cp = math.cos(ph) * sg
            P.rot(p, f"upperleg01.{sd}", f, x=-A * sp - (8 if run else 2))
            P.rot(p, f"lowerleg01.{sd}", f, x=5 + K * max(0.0, cp) ** 1.5)
            P.rot(p, f"foot.{sd}", f, x=-6 * sp)
            if arms:
                P.rot(p, f"upperarm01.{sd}", f, x=Aa * sp * -1 + (10 if run else 0), z=(-40 if sd == "L" else 40) * (0.8 if run else 1))
                P.rot(p, f"lowerarm01.{sd}", f, x=(75 if run else 14) + (10 * max(0, -sp)))
        if spine:
            P.rot(p, "spine03", f, x=(12 if run else 2), y=(7 if run else 4) * math.sin(ph))
    return f1


def stand(p, frame, arms=True, spine=True):
    for sd in ("L", "R"):
        P.rot(p, f"upperleg01.{sd}", frame)
        P.rot(p, f"lowerleg01.{sd}", frame, x=3)
        P.rot(p, f"foot.{sd}", frame)
        if arms:
            P.rot(p, f"upperarm01.{sd}", frame, z=(-40 if sd == "L" else 40))
            P.rot(p, f"lowerarm01.{sd}", frame, x=12)
    if spine:
        P.rot(p, "spine03", frame)
    p["rig"].keyframe_insert("location", frame=frame)


def comp_outlines(kn=1.5, kd=0.4, thr=0.6, human_min=10000, fade_near=8.0, fade_far=30.0):
    """Schnelle Umrisse im Compositor statt Freestyle:
    - Objekt- und Material-Grenzen (Index-Pässe) -> saubere Comic-Linien, auch bei Menschen (Haut/Kleidung/Haare)
    - Normalen-Kanten nur für Nicht-Menschen (Hauskanten), Tiefen-Kanten überall."""
    sc.render.use_freestyle = False
    vl = sc.view_layers[0]
    vl.use_pass_normal = True
    vl.use_pass_z = True
    if "ids" not in [a.name for a in vl.aovs]:
        aov = vl.aovs.add()
        aov.name, aov.type = "ids", "COLOR"
    for i, m in enumerate(bpy.data.materials):
        if not m.use_nodes:
            continue
        nt = m.node_tree
        oi = nt.nodes.new("ShaderNodeObjectInfo")
        cx = nt.nodes.new("ShaderNodeCombineXYZ")
        cx.inputs[0].default_value = float(i + 1)
        nt.links.new(oi.outputs["Object Index"], cx.inputs[1])
        ao = nt.nodes.new("ShaderNodeOutputAOV")
        ao.aov_name = "ids"
        nt.links.new(cx.outputs[0], ao.inputs["Color"])
    ng = bpy.data.node_groups.new("toon_comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    N, Lk = ng.nodes, ng.links
    rl = N.new("CompositorNodeRLayers")
    out = N.new("NodeGroupOutput")
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    def math(op, a, b=None, v=None):
        m = N.new("ShaderNodeMath")
        m.operation = op
        Lk.new(a, m.inputs[0])
        if b is not None:
            Lk.new(b, m.inputs[1])
        elif v is not None:
            m.inputs[1].default_value = v
        return m.outputs[0]

    def sobel(sock, single=False):
        f = N.new("CompositorNodeFilter")
        f.inputs["Type"].default_value = "Sobel"
        Lk.new(sock, f.inputs["Image"])
        sp = N.new("CompositorNodeSeparateColor")
        Lk.new(f.outputs[0], sp.inputs[0])
        if single:
            return sp.outputs[0]
        return math("ADD", math("ADD", sp.outputs[0], sp.outputs[1]), sp.outputs[2])

    idsp = N.new("CompositorNodeSeparateColor")
    Lk.new(rl.outputs["ids"], idsp.inputs[0])
    mat_i, ob_i = idsp.outputs[0], idsp.outputs[1]
    human = math("GREATER_THAN", ob_i, v=human_min - 0.5)
    en = math("MULTIPLY", math("MULTIPLY", sobel(rl.outputs["Normal"]), v=kn), math("SUBTRACT", math("ADD", human, v=0), v=1.0))
    en = math("ABSOLUTE", en)
    depth = rl.outputs["Depth"]
    # Normalen-Kanten nur in der Nähe (weit weg nur Umriss) -> keine schwarzen Kleckse bei Büschen/Wolken
    fade = N.new("ShaderNodeClamp")
    Lk.new(math("DIVIDE", math("SUBTRACT", depth, v=fade_far), v=fade_near - fade_far), fade.inputs[0])
    en = math("MULTIPLY", en, fade.outputs[0])
    ed = math("MULTIPLY", math("DIVIDE", sobel(depth, True), math("ADD", depth, v=0.05)), v=kd)
    geo = math("MULTIPLY", math("SUBTRACT", math("MAXIMUM", en, ed), v=thr), v=3.0)
    ids = math("ADD", sobel(mat_i, True), sobel(ob_i, True))
    ids = math("MULTIPLY", ids, v=2.0)
    e = N.new("ShaderNodeClamp")
    Lk.new(math("MAXIMUM", geo, ids), e.inputs[0])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    Lk.new(e.outputs[0], mix.inputs["Factor"])
    Lk.new(rl.outputs["Image"], mix.inputs[6])
    mix.inputs[7].default_value = (0.04, 0.04, 0.06, 1)
    Lk.new(mix.outputs[2], out.inputs[0])
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"


def mark_indices(humans):
    """Objekt-Index: Menschen ab 10000, Rest ab 1."""
    hs = set()
    for p in humans:
        hs.add(p["rig"])
        for o in bpy.data.objects:
            q = o
            while q.parent:
                q = q.parent
                if q == p["rig"]:
                    hs.add(o)
                    break
    a, b = 1, 10000
    for o in bpy.data.objects:
        if o in hs:
            o.pass_index = b
            b += 1
        else:
            o.pass_index = a
            a += 1
