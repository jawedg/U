# QISSA – Bausteine für die Islam-POV-Serie (Blender 5, EEVEE, ohne Grafikkarte).
# Stil: echte 3D-Räume mit warmem Licht (wie „Signal Lost“), Menschen OHNE Gesicht (leerer Kopf),
# Sahaba mit Licht über dem Kopf (glow=True), der Prophet ﷺ NIE als Figur – nur als Licht-Säule (holy_light).
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler

sc = bpy.context.scene
FPS = 24
_MATS = {}


def T(s):
    return int(round(s * FPS)) + 1


def reset():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.curves):
        for d in list(c):
            c.remove(d)
    _MATS.clear()


def link(o):
    sc.collection.objects.link(o)
    return o


def empty(name, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.05
    link(e)
    if parent is not None:
        e.parent = parent
    e.location = loc
    e.rotation_euler = rot
    return e


# ---------------------------------------------------------------- Materialien
def pbr(name, col, rough=0.85, metal=0.0, var=0.0, scale=3.0, bump=0.0, bscale=30.0, emit=None, es=0.0,
        alpha=None, brick=0.0, rings=0.0, two=None, spec=0.3, grime=0.0, plaster=0.0):
    """Principled-Material mit optionaler Farb-Variation (Noise), Relief (Bump), Ziegel- oder Ring-Muster."""
    key = (name, tuple(round(c, 3) for c in col), var, bump, emit, es, alpha, grime, plaster)
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = spec
    tc = None
    if var or bump or brick or rings or two or grime or plaster:
        tc = N.new("ShaderNodeTexCoord")
    col_sock = None
    if var:
        nz = N.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = scale
        nz.inputs["Detail"].default_value = 6.0
        L.new(tc.outputs["Object"], nz.inputs["Vector"])
        cr = N.new("ShaderNodeValToRGB")
        cr.color_ramp.elements[0].position = 0.3
        cr.color_ramp.elements[0].color = (*[c * (1 - var) for c in col], 1)
        cr.color_ramp.elements[1].position = 0.7
        cr.color_ramp.elements[1].color = (*[min(1, c * (1 + var)) for c in col], 1)
        L.new(nz.outputs["Fac"], cr.inputs["Fac"])
        col_sock = cr.outputs["Color"]
    if two:  # zweite Farbe (z. B. grüne Palmblatt-Spitzen) über Noise gemischt
        nz2 = N.new("ShaderNodeTexNoise")
        nz2.inputs["Scale"].default_value = two[1]
        L.new(tc.outputs["Object"], nz2.inputs["Vector"])
        mx = N.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        L.new(nz2.outputs["Fac"], mx.inputs["Factor"])
        if col_sock is not None:
            L.new(col_sock, mx.inputs[6])
        else:
            mx.inputs[6].default_value = (*col, 1)
        mx.inputs[7].default_value = (*two[0], 1)
        col_sock = mx.outputs[2]
    if brick:  # Lehmziegel: dezente Fugen
        bt = N.new("ShaderNodeTexBrick")
        bt.inputs["Scale"].default_value = 1.0
        bt.inputs["Mortar Size"].default_value = 0.008
        bt.inputs["Mortar Smooth"].default_value = 0.6
        bt.inputs["Brick Width"].default_value = 0.5
        bt.inputs["Row Height"].default_value = 0.17
        bt.offset = 0.5
        bt.inputs["Color1"].default_value = (1, 1, 1, 1)
        bt.inputs["Color2"].default_value = (0.92, 0.92, 0.92, 1)
        bt.inputs["Mortar"].default_value = (1 - brick, 1 - brick, 1 - brick, 1)
        sx = N.new("ShaderNodeSeparateXYZ")  # Ziegel auf senkrechten Wänden: u = x + y, v = z
        L.new(tc.outputs["Object"], sx.inputs[0])
        ad = N.new("ShaderNodeMath")
        ad.operation = "ADD"
        L.new(sx.outputs["X"], ad.inputs[0])
        L.new(sx.outputs["Y"], ad.inputs[1])
        cx = N.new("ShaderNodeCombineXYZ")
        L.new(ad.outputs[0], cx.inputs["X"])
        L.new(sx.outputs["Z"], cx.inputs["Y"])
        L.new(cx.outputs[0], bt.inputs["Vector"])
        mm = N.new("ShaderNodeMix")
        mm.data_type = "RGBA"
        mm.blend_type = "MULTIPLY"
        mm.inputs["Factor"].default_value = 1.0
        if col_sock is not None:
            L.new(col_sock, mm.inputs[6])
        else:
            mm.inputs[6].default_value = (*col, 1)
        L.new(bt.outputs["Color"], mm.inputs[7])
        col_sock = mm.outputs[2]
    if rings:  # Palmstamm: Ringe
        wv = N.new("ShaderNodeTexWave")
        wv.wave_type = "BANDS"
        wv.bands_direction = "Z"
        wv.inputs["Scale"].default_value = rings
        wv.inputs["Distortion"].default_value = 2.0
        L.new(tc.outputs["Object"], wv.inputs["Vector"])
        mm = N.new("ShaderNodeMix")
        mm.data_type = "RGBA"
        mm.blend_type = "MULTIPLY"
        mm.inputs["Factor"].default_value = 0.45
        if col_sock is not None:
            L.new(col_sock, mm.inputs[6])
        else:
            mm.inputs[6].default_value = (*col, 1)
        L.new(wv.outputs["Color"], mm.inputs[7])
        col_sock = mm.outputs[2]
        bp = N.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = 0.6
        L.new(wv.outputs["Fac"], bp.inputs["Height"])
        L.new(bp.outputs["Normal"], b.inputs["Normal"])
    if plaster:  # Putz-Flecken: hellere, scharf begrenzte Flächen (alter Lehmputz)
        nzp = N.new("ShaderNodeTexNoise")
        nzp.inputs["Scale"].default_value = 0.9
        nzp.inputs["Detail"].default_value = 5.0
        nzp.inputs["Roughness"].default_value = 0.65
        L.new(tc.outputs["Object"], nzp.inputs["Vector"])
        rp = N.new("ShaderNodeValToRGB")
        rp.color_ramp.elements[0].position = 0.52
        rp.color_ramp.elements[0].color = (0, 0, 0, 1)
        rp.color_ramp.elements[1].position = 0.57
        rp.color_ramp.elements[1].color = (plaster, plaster, plaster, 1)
        L.new(nzp.outputs["Fac"], rp.inputs["Fac"])
        mp = N.new("ShaderNodeMix")
        mp.data_type = "RGBA"
        L.new(rp.outputs["Color"], mp.inputs["Factor"])
        if col_sock is not None:
            L.new(col_sock, mp.inputs[6])
        else:
            mp.inputs[6].default_value = (*col, 1)
        mp.inputs[7].default_value = (*[min(1, c * 1.13 + 0.02) for c in col], 1)
        col_sock = mp.outputs[2]
    if grime:  # Schmutz/Feuchte unten an Wänden (dunkler zum Boden hin, unregelmäßig)
        geo = N.new("ShaderNodeNewGeometry")
        sz = N.new("ShaderNodeSeparateXYZ")
        L.new(geo.outputs["Position"], sz.inputs[0])
        nzg = N.new("ShaderNodeTexNoise")
        nzg.inputs["Scale"].default_value = 2.5
        nzg.inputs["Detail"].default_value = 6.0
        L.new(tc.outputs["Object"], nzg.inputs["Vector"])
        hz = N.new("ShaderNodeMath")
        hz.operation = "MULTIPLY_ADD"  # Höhe + Noise * 0.5 -> unregelmäßige Kante
        L.new(nzg.outputs["Fac"], hz.inputs[0])
        hz.inputs[1].default_value = 0.55
        L.new(sz.outputs["Z"], hz.inputs[2])
        mr = N.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.25
        mr.inputs["From Max"].default_value = 1.15
        mr.inputs["To Min"].default_value = grime
        mr.inputs["To Max"].default_value = 0.0
        L.new(hz.outputs[0], mr.inputs["Value"])
        mg = N.new("ShaderNodeMix")
        mg.data_type = "RGBA"
        mg.blend_type = "MULTIPLY"
        L.new(mr.outputs["Result"], mg.inputs["Factor"])
        if col_sock is not None:
            L.new(col_sock, mg.inputs[6])
        else:
            mg.inputs[6].default_value = (*col, 1)
        mg.inputs[7].default_value = (0.42, 0.36, 0.3, 1)
        col_sock = mg.outputs[2]
    if col_sock is not None:
        L.new(col_sock, b.inputs["Base Color"])
    if bump and not rings:
        nz3 = N.new("ShaderNodeTexNoise")
        nz3.inputs["Scale"].default_value = bscale
        nz3.inputs["Detail"].default_value = 8.0
        L.new(tc.outputs["Object"], nz3.inputs["Vector"])
        bp = N.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        bp.inputs["Distance"].default_value = 0.02
        L.new(nz3.outputs["Fac"], bp.inputs["Height"])
        L.new(bp.outputs["Normal"], b.inputs["Normal"])
    if emit is not None:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = es
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
        m.use_transparency_overlap = False
    _MATS[key] = m
    return m


def glow_mat(name, col, strength=8.0, alpha=1.0, fresnel=False, grad_z=None):
    """Reines Licht-Material (Emission, optional transparent, weicher Rand per Fresnel/Facing)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    for n in list(N):
        N.remove(n)
    out = N.new("ShaderNodeOutputMaterial")
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*col, 1)
    em.inputs["Strength"].default_value = strength
    if alpha >= 1.0 and not fresnel and grad_z is None:
        L.new(em.outputs[0], out.inputs[0])
        return m
    tr = N.new("ShaderNodeBsdfTransparent")
    mix = N.new("ShaderNodeMixShader")
    fac = None
    if fresnel:  # Mitte stark, Rand weich (zur Kamera gewandte Flächen)
        lw = N.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.5
        inv = N.new("ShaderNodeMath")
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1.0
        L.new(lw.outputs["Facing"], inv.inputs[1])
        pw = N.new("ShaderNodeMath")
        pw.operation = "POWER"
        L.new(inv.outputs[0], pw.inputs[0])
        pw.inputs[1].default_value = 2.2
        fac = pw.outputs[0]
    if grad_z is not None:  # nach oben/unten ausblenden (Objekt-Z in [z0, z1])
        tc = N.new("ShaderNodeTexCoord")
        sep = N.new("ShaderNodeSeparateXYZ")
        L.new(tc.outputs["Object"], sep.inputs[0])
        mr = N.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = grad_z[0]
        mr.inputs["From Max"].default_value = grad_z[1]
        mr.inputs["To Min"].default_value = 1.0
        mr.inputs["To Max"].default_value = 0.0
        L.new(sep.outputs["Z"], mr.inputs["Value"])
        if fac is not None:
            mul = N.new("ShaderNodeMath")
            mul.operation = "MULTIPLY"
            L.new(fac, mul.inputs[0])
            L.new(mr.outputs[0], mul.inputs[1])
            fac = mul.outputs[0]
        else:
            fac = mr.outputs[0]
    am = N.new("ShaderNodeMath")
    am.operation = "MULTIPLY"
    am.inputs[1].default_value = alpha
    if fac is not None:
        L.new(fac, am.inputs[0])
    else:
        am.inputs[0].default_value = 1.0
    L.new(am.outputs[0], mix.inputs[0])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs[0])
    m.surface_render_method = "BLENDED"
    m.use_transparency_overlap = False
    return m


# ---------------------------------------------------------------- Formen
def _obj(name, bm, mat, smooth=False, parent=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    link(o)
    if mat is not None:
        me.materials.append(mat)
    if parent is not None:
        o.parent = parent
    return o


def box(name, loc, size, mat, rot=(0, 0, 0), bevel=0.0, parent=None, jitter=0.0, seed=0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    if jitter:  # leicht unregelmäßig (Lehmbau)
        rnd = random.Random(seed)
        for v in bm.verts:
            v.co += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.3, 1))) * jitter
    o = _obj(name, bm, mat, parent=parent)
    o.location = loc
    o.rotation_euler = rot
    if bevel:
        b = o.modifiers.new("bev", "BEVEL")
        b.width = bevel
        b.segments = 2
        b.limit_method = "ANGLE"
    return o


def cyl(name, loc, r, h, mat, seg=16, rot=(0, 0, 0), parent=None, r2=None, smooth=True, caps=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    o = _obj(name, bm, mat, smooth=smooth, parent=parent)
    o.location = loc
    o.rotation_euler = rot
    return o


def ball(name, loc, rad, mat, seg=24, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(8, seg // 2), radius=1.0)
    rx, ry, rz = rad if isinstance(rad, (tuple, list)) else (rad, rad, rad)
    bmesh.ops.scale(bm, vec=(rx, ry, rz), verts=bm.verts)
    o = _obj(name, bm, mat, smooth=True, parent=parent)
    o.location = loc
    return o


def torus(name, loc, R, r, mat, seg=32, rseg=10, parent=None, scale=(1, 1, 1)):
    bm = bmesh.new()
    verts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ring = []
        for j in range(rseg):
            b = 2 * math.pi * j / rseg
            x = (R + r * math.cos(b)) * math.cos(a) * scale[0]
            y = (R + r * math.cos(b)) * math.sin(a) * scale[1]
            z = r * math.sin(b) * scale[2]
            ring.append(bm.verts.new((x, y, z)))
        verts.append(ring)
    for i in range(seg):
        for j in range(rseg):
            a, b = verts[i][j], verts[(i + 1) % seg][j]
            c, d = verts[(i + 1) % seg][(j + 1) % rseg], verts[i][(j + 1) % rseg]
            bm.faces.new((a, b, c, d))
    o = _obj(name, bm, mat, smooth=True, parent=parent)
    o.location = loc
    return o


def loft(name, rings, mat, seg=24, parent=None, cap_top=True, cap_bot=True, smooth=True, folds=None):
    """rings: [(z, rx, ry, cx, cy), ...] von unten nach oben -> geschlossene, glatte Hülle.
    folds = (anzahl, amp_unten, amp_oben, seed): senkrechte Stofffalten (Radius wellt sich je Winkel)."""
    bm = bmesh.new()
    vr = []
    zs = [rg[0] for rg in rings]
    z0, z1 = min(zs), max(zs)
    if folds:
        fr = random.Random(folds[3])
        ph = [fr.uniform(0, 6.28) for _ in range(3)]
    for rg in rings:
        z, rx, ry = rg[0], rg[1], rg[2]
        cx = rg[3] if len(rg) > 3 else 0.0
        cy = rg[4] if len(rg) > 4 else 0.0
        ring = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            k = 1.0
            if folds:
                u = (z - z0) / max(1e-6, z1 - z0)
                amp = folds[1] * (1 - u) + folds[2] * u
                k += amp * (0.6 * math.sin(folds[0] * a + ph[0]) + 0.3 * math.sin(folds[0] * 1.7 * a + ph[1] + z * 3)
                            + 0.25 * math.sin(folds[0] * 0.5 * a + ph[2]))
            ring.append(bm.verts.new((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a), z)))
        vr.append(ring)
    for k in range(len(vr) - 1):
        for i in range(seg):
            bm.faces.new((vr[k][i], vr[k][(i + 1) % seg], vr[k + 1][(i + 1) % seg], vr[k + 1][i]))
    if cap_bot:
        bm.faces.new(list(reversed(vr[0])))
    if cap_top:
        bm.faces.new(vr[-1])
    return _obj(name, bm, mat, smooth=smooth, parent=parent)


def limb(name, p0, p1, r0, r1, mat, seg=12, parent=None):
    """Zylinder von p0 nach p1 (lokale Koordinaten des Elternteils)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    o = cyl(name, (0, 0, 0), r0, d.length, mat, seg=seg, r2=r1, parent=parent)
    o.location = (p0 + p1) / 2
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


def kf(o, path, frame, val):
    setattr(o, path, val)
    o.keyframe_insert(path, frame=frame)


def fcurves(o):
    ad = o.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "fcurves"):
        return list(act.fcurves)
    return [fc for l in act.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]


def set_interp(o, kind="LINEAR"):
    for fc in fcurves(o):
        for kp in fc.keyframe_points:
            kp.interpolation = kind


# ---------------------------------------------------------------- Menschen (ohne Gesicht)
SKINS = [(0.55, 0.38, 0.27), (0.47, 0.31, 0.21), (0.62, 0.45, 0.33), (0.36, 0.23, 0.15), (0.58, 0.41, 0.3)]
ROBES = [(0.86, 0.82, 0.72), (0.74, 0.66, 0.53), (0.55, 0.45, 0.34), (0.9, 0.88, 0.82), (0.42, 0.36, 0.3),
         (0.66, 0.58, 0.46), (0.8, 0.74, 0.62)]
WRAPS = [(0.93, 0.92, 0.88), (0.82, 0.78, 0.68), (0.25, 0.22, 0.2), (0.7, 0.62, 0.5), (0.9, 0.9, 0.86)]


def person(name, loc=(0, 0, 0), yaw=0.0, robe=None, skin=None, wrap=None, head="turban", sit=False, glow=False,
           cloak=None, seed=0, height=1.0, long_cloak=False, hands_up=False):
    """Mensch im Gewand, Kopf OHNE Gesicht. Gelenke = Empties (Pose per Rotation):
    root, hips, chest, neck, head, sh.L/R (Schulter), el.L/R (Ellenbogen), foot.L/R.
    Blickrichtung: lokal -Y."""
    rnd = random.Random(seed)
    robe = robe or rnd.choice(ROBES)
    skin = skin or rnd.choice(SKINS)
    wrap = wrap or rnd.choice(WRAPS)
    mr = pbr(f"robe_{name}", robe, 0.9, var=0.07, scale=6, bump=0.04, bscale=25)
    ms = pbr(f"skin_{name}", skin, 0.6, var=0.04, scale=10)
    mw = pbr(f"wrap_{name}", wrap, 0.9, var=0.05, scale=12, bump=0.08, bscale=40)
    msand = pbr("sandal", (0.32, 0.2, 0.12), 0.7)
    P = {"name": name}
    root = empty(f"{name}_root", loc, rot=(0, 0, yaw))
    root.scale = (height, height, height)
    P["root"] = root
    hz = 0.25 if sit else 0.95
    hips = empty(f"{name}_hips", (0, 0, hz), root)
    chest = empty(f"{name}_chest", (0, 0, 0.0), hips)
    neck = empty(f"{name}_neck", (0, 0.0, 0.45), chest)
    headE = empty(f"{name}_head", (0, -0.005, 0.06), neck)
    P.update(hips=hips, chest=chest, neck=neck, head=headE)
    # Oberkörper (immer gleich), darunter Rock (stehend) bzw. Schoß + Knie (sitzend)
    bot = -0.16 if sit else -0.06
    loft(f"{name}_torso", [(bot, 0.2 if sit else 0.17, 0.16 if sit else 0.13), (0.1, 0.175, 0.125), (0.27, 0.195, 0.12),
                           (0.37, 0.2, 0.11), (0.43, 0.13, 0.085), (0.47, 0.06, 0.055)], mr, parent=chest, seg=40,
         folds=(7, 0.03, 0.008, seed + 1))
    if sit:
        ball(f"{name}_lap", (0, -0.12, -0.17), (0.4, 0.3, 0.1), mr, parent=hips)
        for s_ in (-1, 1):
            ball(f"{name}_knee{s_}", (0.29 * s_, -0.2, -0.16), (0.15, 0.18, 0.095), mr, parent=hips)
    else:
        loft(f"{name}_skirt", [(-0.88, 0.27, 0.22), (-0.75, 0.255, 0.205), (-0.6, 0.235, 0.185), (-0.45, 0.218, 0.17),
                               (-0.3, 0.2, 0.155), (-0.15, 0.186, 0.144), (0.0, 0.175, 0.135), (0.06, 0.17, 0.13)], mr,
             parent=hips, cap_bot=False, seg=48, folds=(9, 0.07, 0.005, seed))
        for s_, nm in ((-1, "L"), (1, "R")):
            ft = empty(f"{name}_foot.{nm}", (0.1 * s_, -0.02, -hz + 0.035), hips)
            ball(f"{name}_sand.{nm}", (0, -0.05, -0.025), (0.055, 0.13, 0.015), msand, parent=ft, seg=12)
            ball(f"{name}_ft.{nm}", (0, -0.05, 0.0), (0.045, 0.11, 0.035), ms, parent=ft, seg=12)
            limb(f"{name}_ank.{nm}", (0, 0, 0.0), (0, 0, 0.2), 0.045, 0.05, ms, parent=ft)
            P[f"foot.{nm}"] = ft
    limb(f"{name}_neckm", (0, 0, -0.04), (0, 0, 0.09), 0.052, 0.05, ms, parent=neck)
    # Kopf: glatt, OHNE Gesicht
    ball(f"{name}_skull", (0, 0, 0.11), (0.096, 0.106, 0.125), ms, parent=headE)
    if head == "turban":
        for k, (z, R, rr) in enumerate(((0.165, 0.1, 0.034), (0.2, 0.096, 0.035), (0.232, 0.08, 0.032))):
            t = torus(f"{name}_tb{k}", (0, 0.006, z), R, rr, mw, parent=headE, scale=(1.0, 1.08, 1.0))
            t.rotation_euler = (math.radians(rnd.uniform(-6, 6) - 8), math.radians(rnd.uniform(-4, 4)), rnd.uniform(0, 3))
        ball(f"{name}_tcap", (0, 0.012, 0.245), (0.072, 0.078, 0.045), mw, parent=headE)
        tail = loft(f"{name}_ttail", [(-0.2, 0.034, 0.011), (0.0, 0.04, 0.013), (0.1, 0.035, 0.013)], mw, parent=headE, seg=10)
        tail.location = (0, 0.105, 0.06)
        tail.rotation_euler = (math.radians(12), 0, 0)
    elif head == "scarf":
        sf = loft(f"{name}_scarf", [(-0.22, 0.19, 0.16, 0, 0.035), (-0.06, 0.14, 0.14, 0, 0.025), (0.08, 0.118, 0.128, 0, 0.012),
                                    (0.19, 0.105, 0.115), (0.245, 0.055, 0.065)], mw, parent=headE, cap_bot=False, seg=28)
        me = sf.data
        bm = bmesh.new()
        bm.from_mesh(me)
        dels = [f for f in bm.faces if f.calc_center_median().y < -0.07 and f.calc_center_median().z < 0.16
                and abs(f.calc_center_median().x) < 0.085]
        bmesh.ops.delete(bm, geom=dels, context="FACES")
        bm.to_mesh(me)
        bm.free()
        sf.modifiers.new("solid", "SOLIDIFY").thickness = 0.01
        torus(f"{name}_agal", (0, 0.004, 0.19), 0.104, 0.011, pbr("agal", (0.08, 0.07, 0.07), 0.6), parent=headE,
              scale=(1.03, 1.1, 1))
    elif head == "cap":
        ball(f"{name}_cap", (0, 0.0, 0.18), (0.1, 0.11, 0.07), mw, parent=headE)
    # Arme (Ärmel + Hände), Schultern außen am Körper
    for s_, nm in ((-1, "L"), (1, "R")):
        sh = empty(f"{name}_sh.{nm}", (0.215 * s_, 0.0, 0.36), chest)
        ball(f"{name}_shm.{nm}", (0, 0, 0.0), (0.07, 0.07, 0.065), mr, parent=sh, seg=14)
        limb(f"{name}_ua.{nm}", (0, 0, 0.0), (0, 0, -0.28), 0.062, 0.056, mr, parent=sh)
        el = empty(f"{name}_el.{nm}", (0, 0, -0.28), sh)
        ball(f"{name}_elm.{nm}", (0, 0, 0.0), 0.056, mr, parent=el, seg=12)
        limb(f"{name}_fa.{nm}", (0, 0, 0.0), (0, 0, -0.24), 0.056, 0.075, mr, parent=el)
        hd = empty(f"{name}_hand.{nm}", (0, 0, -0.27), el)
        ball(f"{name}_palm.{nm}", (0, 0, -0.03), (0.03, 0.047, 0.07), ms, parent=hd, seg=12)
        ball(f"{name}_thumb.{nm}", (-0.018 * s_, -0.035, -0.0), (0.015, 0.015, 0.038), ms, parent=hd, seg=8)
        P[f"sh.{nm}"], P[f"el.{nm}"], P[f"hand.{nm}"] = sh, el, hd
        sh.rotation_euler = (0, math.radians(6 * s_), 0)
        el.rotation_euler = (math.radians(-14), 0, 0)
    if sit:  # Hände auf den Knien
        for s_, nm in ((-1, "L"), (1, "R")):
            P[f"sh.{nm}"].rotation_euler = (math.radians(28), math.radians(14 * s_), 0)
            P[f"el.{nm}"].rotation_euler = (math.radians(-50), 0, 0)
    if cloak:  # offener Umhang über den Schultern
        mc = pbr(f"cloak_{name}", cloak, 0.95, var=0.08, scale=5, bump=0.05, bscale=25)
        z0 = -0.92 if not long_cloak else -0.95
        rings = [(z0, 0.31, 0.27, 0, 0.04), (-0.5, 0.28, 0.23, 0, 0.03), (-0.1, 0.25, 0.18, 0, 0.02),
                 (0.2, 0.265, 0.165, 0, 0.015), (0.36, 0.28, 0.15, 0, 0.01), (0.45, 0.14, 0.1)]
        if sit:
            rings = [(-0.12, 0.3, 0.24, 0, 0.04), (0.2, 0.265, 0.17, 0, 0.02), (0.36, 0.28, 0.15), (0.45, 0.14, 0.1)]
        cl = loft(f"{name}_cloak", rings, mc, parent=chest, cap_bot=False, cap_top=False, seg=48, folds=(8, 0.09, 0.01, seed + 2))
        # vorne offen: Flächen mit -Y-Normalen in der Mitte löschen
        me = cl.data
        bm = bmesh.new()
        bm.from_mesh(me)
        dels = [f for f in bm.faces if f.calc_center_median().y < -0.12 and abs(f.calc_center_median().x) < 0.11]
        bmesh.ops.delete(bm, geom=dels, context="FACES")
        bm.to_mesh(me)
        bm.free()
        cl.modifiers.new("solid", "SOLIDIFY").thickness = 0.012
        P["cloak"] = cl
        if long_cloak:  # schleift hinten über den Boden
            tr = loft(f"{name}_trail", [(-0.02, 0.22, 0.03), (0.0, 0.26, 0.04), (0.02, 0.27, 0.04)], mc, parent=hips,
                      seg=16)
            tr.location = (0, 0.45, -0.93)
            tr.scale = (1.0, 2.6, 1.0)
            P["trail"] = tr
    if glow:
        halo(P)
    blob(f"{name}_blob", root, 0.42 if sit else 0.34)
    root["person"] = 1
    return P


def blob(name, parent, r=0.35, dark=0.55, loc=(0, 0, 0.004)):
    """Weicher Kontaktschatten (statt teurer Schatten aller Lampen)."""
    m = bpy.data.materials.get("blob_shadow")
    if m is None:
        m = bpy.data.materials.new("blob_shadow")
        m.use_nodes = True
        nt = m.node_tree
        N, L = nt.nodes, nt.links
        for n in list(N):
            N.remove(n)
        out = N.new("ShaderNodeOutputMaterial")
        tr = N.new("ShaderNodeBsdfTransparent")
        bk = N.new("ShaderNodeBsdfDiffuse")
        bk.inputs["Color"].default_value = (0, 0, 0, 1)
        mix = N.new("ShaderNodeMixShader")
        tc = N.new("ShaderNodeTexCoord")
        gr = N.new("ShaderNodeTexGradient")
        gr.gradient_type = "QUADRATIC_SPHERE"
        L.new(tc.outputs["Object"], gr.inputs["Vector"])
        mul = N.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = dark
        L.new(gr.outputs["Fac"], mul.inputs[0])
        L.new(mul.outputs[0], mix.inputs[0])
        L.new(tr.outputs[0], mix.inputs[1])
        L.new(bk.outputs[0], mix.inputs[2])
        L.new(mix.outputs[0], out.inputs[0])
        m.surface_render_method = "BLENDED"
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
    o = _obj(name, bm, m, parent=parent)
    o.location = loc
    o.scale = (r, r * 0.85, 1)
    return o


def halo(P, strength=6.0):
    """Licht über dem Kopf (Sahaba): leuchtender Kern + weicher Schein + kleines Punktlicht."""
    h = P["head"]
    n = P["name"]
    core = ball(f"{n}_halo_core", (0, 0, 0.4), 0.018, glow_mat(f"halo_core_{n}", (1.0, 0.88, 0.6), 18.0), parent=h, seg=12)
    soft = ball(f"{n}_halo_soft", (0, 0, 0.4), (0.2, 0.2, 0.12), glow_mat(f"halo_soft_{n}", (1.0, 0.8, 0.48), 2.2, 0.6,
                fresnel=True), parent=h, seg=24)
    lt = bpy.data.lights.new(f"{n}_halo_l", "POINT")
    lt.energy = 9 * strength / 6
    lt.color = (1.0, 0.82, 0.55)
    lt.shadow_soft_size = 0.2
    lt.use_shadow = False
    lo = bpy.data.objects.new(f"{n}_halo_l", lt)
    link(lo)
    lo.parent = h
    lo.location = (0, 0, 0.45)
    P["halo"] = (core, soft, lo)


def holy_light(name, loc, height=2.3, strength=1.0):
    """Der Prophet ﷺ wird NIE gezeigt – nur als Licht-Säule (keine menschliche Form)."""
    root = empty(name, loc)
    outer = cyl(f"{name}_outer", (0, 0, height / 2), 0.55, height, glow_mat(f"{name}_om", (1.0, 0.86, 0.6), 3.5 * strength,
                0.55, fresnel=True, grad_z=(-height / 2 * 0.2, height / 2)), seg=40, parent=root, caps=False)
    mid = cyl(f"{name}_mid", (0, 0, height / 2), 0.3, height, glow_mat(f"{name}_mm", (1.0, 0.92, 0.75), 9.0 * strength,
              0.8, fresnel=True, grad_z=(-height / 2 * 0.3, height / 2)), seg=32, parent=root, caps=False)
    core = cyl(f"{name}_core", (0, 0, height / 2), 0.1, height * 0.95, glow_mat(f"{name}_cm", (1.0, 0.97, 0.9), 25.0 * strength,
               1.0, fresnel=True, grad_z=(-height / 2, height / 2)), seg=24, parent=root, caps=False)
    pool = cyl(f"{name}_pool", (0, 0, 0.01), 1.1, 0.01, glow_mat(f"{name}_pm", (1.0, 0.85, 0.55), 3.0 * strength, 0.5,
               fresnel=False), seg=40, parent=root)
    # Boden-Schein: Kreis mit weichem Rand
    pm = pool.active_material
    nt = pm.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    gr = nt.nodes.new("ShaderNodeTexGradient")
    gr.gradient_type = "SPHERICAL"
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / 1.1, 1 / 1.1, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs[0], gr.inputs["Vector"])
    mul = [n for n in nt.nodes if n.type == "MATH"][0]
    nt.links.new(gr.outputs["Fac"], mul.inputs[0])
    lt = bpy.data.lights.new(f"{name}_l", "POINT")
    lt.energy = 140 * strength
    lt.color = (1.0, 0.85, 0.62)
    lt.shadow_soft_size = 0.5
    lt.use_shadow = False
    lo = bpy.data.objects.new(f"{name}_l", lt)
    link(lo)
    lo.parent = root
    lo.location = (0, 0, 1.3)
    # schwebende Lichtpunkte
    rnd = random.Random(7)
    motes = []
    mm = glow_mat(f"{name}_mote", (1.0, 0.9, 0.7), 20.0)
    for i in range(18):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0.15, 0.7)
        m = ball(f"{name}_mote{i}", (r * math.cos(a), r * math.sin(a), rnd.uniform(0.1, height)), 0.008 + rnd.random() * 0.008,
                 mm, seg=8, parent=root)
        motes.append((m, rnd.uniform(0.15, 0.4), rnd.uniform(0, 6)))
    return {"root": root, "light": lo, "motes": motes, "height": height, "parts": (outer, mid, core, pool)}


def animate_motes(H, f0, f1):
    h = H["height"]
    for m, sp, ph in H["motes"]:
        z0 = m.location.z
        for f in range(f0, f1 + 1, 12):
            t = (f - f0) / FPS
            m.location.z = (z0 + sp * t) % h + 0.05
            m.keyframe_insert("location", index=2, frame=f)


# ---------------------------------------------------------------- Bewegung
def walk(P, path, t0, speed=1.2, run=False, step_every=None, face=True):
    """Gehen entlang path [(x,y), ...] ab Sekunde t0. Füße setzen abwechselnd, Hüfte wippt, Arme schwingen."""
    root, hips = P["root"], P["hips"]
    pts = [Vector((p[0], p[1], root.location.z)) for p in path]
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum((b - a).length for a, b in segs)
    dur = total / speed
    stride = (0.75 if not run else 1.3)
    f0, f1 = T(t0), T(t0 + dur)
    hz = hips.location.z
    for f in range(f0, f1 + 1):
        d = min(total, (f - f0) / FPS * speed)
        acc = 0.0
        pos, dirv = pts[-1], (segs[-1][1] - segs[-1][0]).normalized()
        for a, b in segs:
            L = (b - a).length
            if d <= acc + L:
                pos = a + (b - a) * ((d - acc) / L)
                dirv = (b - a).normalized()
                break
            acc += L
        root.location = pos
        root.keyframe_insert("location", frame=f)
        if face:
            yaw = math.atan2(dirv.x, -dirv.y)
            root.rotation_euler = (0, 0, yaw)
            root.keyframe_insert("rotation_euler", index=2, frame=f)
        ph = d / stride * math.pi
        bob = abs(math.sin(ph)) * (0.025 if not run else 0.06)
        hips.location.z = hz + bob - (0.0 if not run else 0.05)
        hips.rotation_euler = (math.radians(4 if not run else 16), 0, math.sin(ph) * math.radians(4))
        hips.keyframe_insert("location", index=2, frame=f)
        hips.keyframe_insert("rotation_euler", frame=f)
        for s, nm in ((1, "L"), (-1, "R")):
            ft = P.get(f"foot.{nm}")
            if ft is not None:
                sw = math.sin(ph) * s
                ft.location.y = -0.02 - sw * (0.22 if not run else 0.42)
                lift = max(0.0, math.cos(ph) * s) * (0.06 if not run else 0.16)
                ft.location.z = -hz + 0.035 + lift
                ft.keyframe_insert("location", frame=f)
            sh = P[f"sh.{nm}"]
            sh.rotation_euler = (-math.sin(ph) * s * math.radians(18 if not run else 45), sh.rotation_euler.y, 0)
            sh.keyframe_insert("rotation_euler", frame=f)
            el = P[f"el.{nm}"]
            el.rotation_euler = (math.radians(-15 if not run else -70), 0, 0)
            el.keyframe_insert("rotation_euler", frame=f)
    return t0 + dur


def idle(P, t0, t1, seed=0, look=None):
    """Atmen + kleine Kopfbewegungen; look = [(t, yaw_grad, pitch_grad), ...]."""
    rnd = random.Random(seed)
    ch, hd = P["chest"], P["head"]
    for f in range(T(t0), T(t1) + 1, 6):
        t = (f - 1) / FPS
        br = math.sin(t * 1.6 + seed) * 0.012
        ch.rotation_euler = (br, 0, 0)
        ch.keyframe_insert("rotation_euler", frame=f)
    if look:
        for t, yw, pt in look:
            hd.rotation_euler = (math.radians(pt), 0, math.radians(yw))
            hd.keyframe_insert("rotation_euler", frame=T(t))
    else:
        for k in range(int((t1 - t0) / 2.5) + 1):
            t = t0 + k * 2.5 + rnd.uniform(0, 1)
            hd.rotation_euler = (math.radians(rnd.uniform(-6, 6)), 0, math.radians(rnd.uniform(-20, 20)))
            hd.keyframe_insert("rotation_euler", frame=T(t))


# ---------------------------------------------------------------- Ich-Kamera + Hände
def pov_camera(lens=17.0):
    rig = empty("pov_rig")
    shake = empty("pov_shake", parent=rig)
    cd = bpy.data.cameras.new("pov")
    cd.lens = lens
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = 24.0
    cd.clip_start = 0.03
    cd.clip_end = 600
    cam = bpy.data.objects.new("pov", cd)
    link(cam)
    cam.parent = shake
    cam.rotation_euler = (math.radians(90), 0, 0)  # Kamera schaut entlang +Y des Rigs
    sc.camera = cam
    return rig, shake, cam


def cam_keys(rig, keys, interp="BEZIER", loc_interp=None):
    """keys: [(t, (x,y,z), (yaw_grad, pitch_grad, roll_grad)), ...]  yaw 0 = Blick nach +Y, positiv = nach links.
    pos oder Winkel None = an dieser Stelle nicht setzen."""
    for t, pos, ang in keys:
        if pos is not None:
            rig.location = pos
            rig.keyframe_insert("location", frame=T(t))
        if ang is not None:
            yw, pt, rl = ang
            rig.rotation_euler = (math.radians(pt), math.radians(rl), math.radians(yw))
            rig.keyframe_insert("rotation_euler", frame=T(t))
    for fc in fcurves(rig):
        loc = fc.data_path == "location"
        for kp in fc.keyframe_points:
            kp.interpolation = (loc_interp or interp) if loc else interp
            kp.easing = "EASE_IN_OUT"


def yaw_to(src, dst):
    """Kamera-Gierwinkel (Grad) von src nach dst (yaw 0 = +Y, positiv = links)."""
    return math.degrees(math.atan2(-(dst[0] - src[0]), dst[1] - src[1]))


def pitch_to(src, dst):
    d = math.hypot(dst[0] - src[0], dst[1] - src[1])
    return math.degrees(math.atan2(dst[2] - src[2], d))


def face_yaw(src, dst):
    """Gierwinkel (Radiant) für eine Figur an src, die nach dst schaut (Figur blickt lokal nach -Y)."""
    return math.atan2(dst[0] - src[0], -(dst[1] - src[1]))


def head_to(P, t, target, up=None, clamp=70):
    """Kopf zur Zielposition drehen (relativ zur Körperdrehung). up = Neigung nach oben in Grad (sonst berechnet)."""
    root = P["root"]
    p = root.location
    yaw_world = math.atan2(target[0] - p.x, -(target[1] - p.y))
    rel = (yaw_world - root.rotation_euler.z + math.pi) % (2 * math.pi) - math.pi
    rel = max(-math.radians(clamp), min(math.radians(clamp), rel))
    if up is None:
        d = math.hypot(target[0] - p.x, target[1] - p.y)
        up = math.degrees(math.atan2(target[2] - 1.6 * root.scale.z, max(0.3, d)))
    hd = P["head"]
    hd.rotation_euler = (-math.radians(up), 0, rel)
    hd.keyframe_insert("rotation_euler", frame=T(t))


def arm_pose(P, t, side, sh_x, el_x, sh_y=None, el_y=0.0):
    """Arm-Pose: Schulter nach vorn heben (sh_x Grad, negativ = nach vorn/oben), seitlich (sh_y; rechts negativ = abspreizen),
    Ellenbogen beugen (el_x negativ = nach vorn, el_y = zur Seite/zum Kopf)."""
    sh, el = P[f"sh.{side}"], P[f"el.{side}"]
    sy = sh.rotation_euler.y if sh_y is None else math.radians(sh_y)
    sh.rotation_euler = (math.radians(sh_x), sy, 0)
    el.rotation_euler = (math.radians(el_x), math.radians(el_y), 0)
    sh.keyframe_insert("rotation_euler", frame=T(t))
    el.keyframe_insert("rotation_euler", frame=T(t))


def hands_to_ears(P, t):
    """Gebetsruf-Haltung: Hände an die Ohren."""
    arm_pose(P, t, "L", -32, -15, sh_y=60, el_y=142)
    arm_pose(P, t, "R", -32, -15, sh_y=-60, el_y=-142)


def arms_rest(P, t):
    arm_pose(P, t, "L", 0, -14, sh_y=-6)
    arm_pose(P, t, "R", 0, -14, sh_y=6)


def hold(P, t0, t1):
    """Position/Drehung der Figur zwischen t0 und t1 festhalten (Schlüsselbild an beiden Enden)."""
    r = P["root"]
    for t in (t0, t1):
        r.keyframe_insert("location", frame=T(t))
        r.keyframe_insert("rotation_euler", frame=T(t))


def handheld(shake, t0, t1, amp=1.0, walk_from=None, walk_to=None, walk_amp=1.0, seed=1):
    """Handkamera: weiches Zittern (Summe von Sinus) + Geh-Wippen."""
    for f in range(T(t0), T(t1) + 1):
        t = (f - 1) / FPS
        a = amp
        rx = (math.sin(t * 1.7 + seed) * 0.5 + math.sin(t * 3.1 + 2 * seed) * 0.3 + math.sin(t * 7.3) * 0.08) * math.radians(0.8) * a
        rz = (math.sin(t * 1.3 + 3 * seed) * 0.6 + math.sin(t * 2.9) * 0.25) * math.radians(1.0) * a
        ry = math.sin(t * 1.1 + seed) * math.radians(0.6) * a
        dz = 0.0
        if walk_from is not None and walk_from <= t <= walk_to:
            ph = (t - walk_from) * 2 * math.pi * 0.95
            dz = abs(math.sin(ph)) * 0.035 * walk_amp
            ry += math.sin(ph) * math.radians(0.9) * walk_amp
        shake.rotation_euler = (rx, ry, rz)
        shake.location = (0, 0, dz)
        shake.keyframe_insert("rotation_euler", frame=f)
        shake.keyframe_insert("location", index=2, frame=f)


def pov_hands(cam, skin=(0.4, 0.26, 0.17), sleeve=(0.62, 0.55, 0.43), lamp=True, lamp_energy=9.0):
    """Eigene rechte Hand im Bild (Kind der Kamera): flache Hand trägt die Öllampe, Daumen hält sie seitlich.
    Hand-Koordinaten: +Y = nach vorn, +Z = oben, +X = rechts."""
    ms = pbr("pov_skin", skin, 0.55, var=0.05, scale=12)
    mr = pbr("pov_sleeve", sleeve, 0.9, var=0.06, scale=8, bump=0.1, bscale=40)
    hr = empty("pov_hand.R", (0.11, -0.27, -0.52), cam, rot=(math.radians(-90 + 22), math.radians(-4), math.radians(12)))
    ball("pov_palm.R", (0, 0, 0), (0.044, 0.05, 0.017), ms, parent=hr, seg=20)
    ball("pov_fingers.R", (0.004, 0.06, 0.006), (0.04, 0.035, 0.014), ms, parent=hr, seg=16)
    for i in range(4):  # Fingerspitzen biegen sich um den Lampenrand
        ball(f"pov_tip{i}.R", (-0.024 + 0.017 * i, 0.088, 0.018), (0.0085, 0.01, 0.014), ms, parent=hr, seg=8)
    limb("pov_th.R", (-0.042, -0.005, 0.004), (-0.05, 0.03, 0.03), 0.012, 0.01, ms, parent=hr, seg=10)
    limb("pov_wr.R", (0.0, -0.03, -0.006), (0.02, -0.12, -0.03), 0.027, 0.031, ms, parent=hr, seg=12)
    limb("pov_sl.R", (0.006, -0.075, -0.016), (0.08, -0.6, -0.17), 0.05, 0.075, mr, parent=hr, seg=16)
    H = {"R": hr}
    if lamp:
        H["lamp"] = oil_lamp("pov_lamp", (0.0, 0.025, 0.04), parent=hr, energy=lamp_energy, forward=True)
    return H


def oil_lamp(name, loc, parent=None, energy=40.0, forward=False):
    """Tonlampe mit Flamme + warmem Punktlicht (flackert per Keyframes über flicker()). Tülle zeigt nach -Y
    (forward=True: nach +Y)."""
    mc = pbr("clay", (0.5, 0.27, 0.15), 0.8, var=0.1, scale=20, bump=0.15, bscale=90)
    root = empty(name, loc, parent)
    if forward:
        root.rotation_euler = (0, 0, math.pi)
    body = ball(f"{name}_body", (0, 0, 0), (0.045, 0.06, 0.02), mc, parent=root, seg=24)
    torus(f"{name}_rim", (0, 0.0, 0.016), 0.022, 0.005, mc, parent=root, seg=20, rseg=8)
    ball(f"{name}_hole", (0, 0.0, 0.015), (0.017, 0.017, 0.004), pbr("lamp_oil", (0.06, 0.04, 0.02), 0.2), parent=root, seg=12)
    ball(f"{name}_spout", (0, -0.065, 0.004), (0.016, 0.04, 0.011), mc, parent=root, seg=14)
    fl = ball(f"{name}_flame", (0, -0.1, 0.03), (0.008, 0.008, 0.024), glow_mat(f"{name}_fm", (1.0, 0.62, 0.22), 40.0), parent=root, seg=10)
    lt = bpy.data.lights.new(f"{name}_l", "POINT")
    lt.energy = energy
    lt.color = (1.0, 0.58, 0.28)
    lt.shadow_soft_size = 0.05
    lt.use_shadow = False
    lo = bpy.data.objects.new(f"{name}_l", lt)
    link(lo)
    lo.parent = root
    lo.location = (0, -0.11, 0.11)
    return {"root": root, "light": lo, "flame": fl}


def flicker(light_obj, t0, t1, base, amt=0.18, seed=0):
    rnd = random.Random(seed)
    for f in range(T(t0), T(t1) + 1, 3):
        light_obj.data.energy = base * (1 + rnd.uniform(-amt, amt))
        light_obj.data.keyframe_insert("energy", frame=f)


# ---------------------------------------------------------------- Welt, Licht, Rendern
def world_sky(mode="night", amb=None):
    """Himmel per Verlauf (Blickrichtung Z). night: Nachtblau + Sterne; dawn: Morgenrot; dream: goldener Dunst."""
    w = bpy.data.worlds.new(mode)
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    N, L = nt.nodes, nt.links
    for n in list(N):
        N.remove(n)
    out = N.new("ShaderNodeOutputWorld")
    bg = N.new("ShaderNodeBackground")
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Generated"], sep.inputs[0])
    cr = N.new("ShaderNodeValToRGB")
    L.new(sep.outputs["Z"], cr.inputs["Fac"])
    E = cr.color_ramp.elements
    if mode == "night":
        E[0].position, E[0].color = 0.0, (0.02, 0.025, 0.045, 1)
        E[1].position, E[1].color = 0.6, (0.002, 0.003, 0.01, 1)
        mid = E.new(0.12)
        mid.color = (0.012, 0.016, 0.034, 1)
        strength = 1.0
    elif mode == "dusk":
        E[0].position, E[0].color = 0.0, (0.35, 0.15, 0.08, 1)
        E[1].position, E[1].color = 0.55, (0.01, 0.018, 0.05, 1)
        mid = E.new(0.12)
        mid.color = (0.08, 0.06, 0.12, 1)
        strength = 1.0
    elif mode == "dawn":
        E[0].position, E[0].color = 0.0, (0.95, 0.6, 0.42, 1)
        E[1].position, E[1].color = 0.75, (0.1, 0.17, 0.4, 1)
        mid = E.new(0.2)
        mid.color = (0.42, 0.42, 0.62, 1)
        strength = 1.0
    elif mode == "dreamnight":  # Traum bei Nacht: goldener Horizont, Indigo, Sterne
        E[0].position, E[0].color = 0.0, (0.42, 0.26, 0.13, 1)
        E[1].position, E[1].color = 0.6, (0.006, 0.008, 0.026, 1)
        mid = E.new(0.13)
        mid.color = (0.05, 0.055, 0.15, 1)
        strength = 1.0
    else:  # dream
        E[0].position, E[0].color = -0.1, (0.9, 0.68, 0.42, 1)
        E[1].position, E[1].color = 0.7, (0.16, 0.12, 0.1, 1)
        mid = E.new(0.12)
        mid.color = (0.55, 0.4, 0.26, 1)
        strength = 1.0
    col = cr.outputs["Color"]
    if mode == "dawn":  # Glühen im Osten (+X), nahe am Horizont
        mrx = N.new("ShaderNodeMapRange")
        mrx.inputs["From Min"].default_value = -0.3
        mrx.inputs["From Max"].default_value = 1.0
        L.new(sep.outputs["X"], mrx.inputs["Value"])
        pw = N.new("ShaderNodeMath")
        pw.operation = "POWER"
        L.new(mrx.outputs[0], pw.inputs[0])
        pw.inputs[1].default_value = 2.5
        mrz = N.new("ShaderNodeMapRange")
        mrz.inputs["From Min"].default_value = 0.45
        mrz.inputs["From Max"].default_value = -0.02
        L.new(sep.outputs["Z"], mrz.inputs["Value"])
        fz = N.new("ShaderNodeMath")
        fz.operation = "MULTIPLY"
        L.new(pw.outputs[0], fz.inputs[0])
        L.new(mrz.outputs[0], fz.inputs[1])
        gm = N.new("ShaderNodeMix")
        gm.data_type = "RGBA"
        L.new(fz.outputs[0], gm.inputs["Factor"])
        L.new(col, gm.inputs[6])
        gm.inputs[7].default_value = (1.6, 0.72, 0.32, 1)
        col = gm.outputs[2]
    if mode in ("night", "dusk", "dreamnight"):
        vo = N.new("ShaderNodeTexVoronoi")
        vo.inputs["Scale"].default_value = 180.0
        L.new(tc.outputs["Generated"], vo.inputs["Vector"])
        mr = N.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.06
        mr.inputs["From Max"].default_value = 0.0
        mr.inputs["To Min"].default_value = 0.0
        mr.inputs["To Max"].default_value = {"night": 2.5, "dreamnight": 3.2}.get(mode, 0.6)
        L.new(vo.outputs["Distance"], mr.inputs["Value"])
        hz = N.new("ShaderNodeMapRange")  # nur oberhalb des Horizonts
        hz.inputs["From Min"].default_value = 0.02
        hz.inputs["From Max"].default_value = 0.2
        L.new(sep.outputs["Z"], hz.inputs["Value"])
        st = N.new("ShaderNodeMath")
        st.operation = "MULTIPLY"
        L.new(mr.outputs[0], st.inputs[0])
        L.new(hz.outputs[0], st.inputs[1])
        ad = N.new("ShaderNodeMix")
        ad.data_type = "RGBA"
        ad.blend_type = "ADD"
        ad.inputs["Factor"].default_value = 1.0
        L.new(col, ad.inputs[6])
        L.new(st.outputs[0], ad.inputs[7])
        col = ad.outputs[2]
    L.new(col, bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    if amb is not None:  # Umgebungslicht getrennt vom sichtbaren Himmel (Kamera sieht den Verlauf, Licht kommt von amb)
        lp = N.new("ShaderNodeLightPath")
        bg2 = N.new("ShaderNodeBackground")
        bg2.inputs["Color"].default_value = (*amb[0], 1)
        bg2.inputs["Strength"].default_value = amb[1]
        mx = N.new("ShaderNodeMixShader")
        L.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
        L.new(bg2.outputs[0], mx.inputs[1])
        L.new(bg.outputs[0], mx.inputs[2])
        L.new(mx.outputs[0], out.inputs[0])
    else:
        L.new(bg.outputs[0], out.inputs[0])
    w.mist_settings.start = 8.0
    w.mist_settings.depth = 80.0
    w.mist_settings.falloff = "QUADRATIC"
    return w


def sun(name, rot_deg, energy, color, angle=2.0, shadow=False):
    s = bpy.data.lights.new(name, "SUN")
    s.energy = energy
    s.color = color
    s.angle = math.radians(angle)
    s.use_shadow = shadow
    o = bpy.data.objects.new(name, s)
    link(o)
    o.rotation_euler = [math.radians(a) for a in rot_deg]
    return o


def point(name, loc, energy, color=(1.0, 0.6, 0.3), radius=0.1, shadow=False, parent=None):
    l = bpy.data.lights.new(name, "POINT")
    l.energy = energy
    l.color = color
    l.shadow_soft_size = radius
    l.use_shadow = shadow
    o = bpy.data.objects.new(name, l)
    link(o)
    o.location = loc
    if parent is not None:
        o.parent = parent
    return o


def render_setup(pct=50, samples=12, mist_col=(0.05, 0.06, 0.1), mist_amt=0.6, bloom=0.6, exposure=0.0, look="AgX - Punchy",
                 shadow_res=0.5):
    sc.render.engine = "BLENDER_EEVEE"
    e = sc.eevee
    e.taa_render_samples = samples
    e.use_shadows = True
    e.shadow_ray_count = 1
    e.shadow_step_count = 4
    e.shadow_resolution_scale = shadow_res
    sc.render.fps = FPS
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.render.resolution_percentage = pct
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = look
    except TypeError:
        pass
    sc.view_settings.exposure = exposure
    vl = sc.view_layers[0]
    vl.use_pass_mist = True
    # Compositor: Dunst nach Tiefe (Mist) + Leuchten (Bloom)
    ng = bpy.data.node_groups.new("qissa_comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    N, L = ng.nodes, ng.links
    rl = N.new("CompositorNodeRLayers")
    out = N.new("NodeGroupOutput")
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    img = rl.outputs["Image"]
    if mist_amt > 0:
        mm = N.new("ShaderNodeMath")
        mm.operation = "MULTIPLY"
        L.new(rl.outputs["Mist"], mm.inputs[0])
        mm.inputs[1].default_value = mist_amt
        mix = N.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        L.new(mm.outputs[0], mix.inputs["Factor"])
        L.new(img, mix.inputs[6])
        mix.inputs[7].default_value = (*mist_col, 1)
        img = mix.outputs[2]
    if bloom > 0:
        g = N.new("CompositorNodeGlare")
        g.inputs["Type"].default_value = "Bloom"
        g.inputs["Quality"].default_value = "Medium"
        for k, v in (("Threshold", 0.9), ("Strength", bloom), ("Size", 0.6), ("Saturation", 1.0)):
            g.inputs[k].default_value = v
        L.new(img, g.inputs["Image"])
        img = g.outputs["Image"]
    L.new(img, out.inputs[0])
