# Wohnzimmer in Futaba (11.03.2011) im Ink-Pop-Look wie im Vorbild: gemalte Texturen, dünne Linien, viele Details.
# build() gibt ein Dict mit wichtigen Objekten zurück (Fernseher, Lampe, Bücher … für das Beben).
import bpy, bmesh, math, os, random
from mathutils import Vector
import figure as F

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "tex")
sc = bpy.context.scene
R = random.Random(21)
_cache = {}


def _ramp(nt, shade, tint):
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    nt.links.new(dif.outputs[0], s2r.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "EASE"
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.08, (shade * tint[0], shade * tint[1], shade * tint[2], 1)
    e[1].position, e[1].color = 0.5, (1.0, 1.0, 1.0, 1)
    mid = e.new(0.28)
    m = (1 + shade) / 2
    mid.color = (m * (1 + tint[0]) / 2, m * (1 + tint[1]) / 2, m * (1 + tint[2]) / 2, 1)
    nt.links.new(s2r.outputs[0], ramp.inputs[0])
    return ramp


def soft(name, col, shade=0.66, tint=(0.88, 0.9, 1.0)):
    """Weiche 3-Ton-Schattierung (kein harter Comic-Schnitt) – Farbe einfarbig."""
    key = ("soft", name, tuple(round(c, 3) for c in col))
    if key in _cache:
        return _cache[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    ramp = _ramp(nt, shade, tint)
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type, mul.blend_type = "RGBA", "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    mul.inputs[6].default_value = (*col, 1)
    nt.links.new(ramp.outputs[0], mul.inputs[7])
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mul.outputs[2], em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    m["toon"] = 1
    _cache[key] = m
    return m


def painted(name, file, scale=1.0, shade=0.68, tint=(0.88, 0.9, 1.0), emit=0.0, proj="BOX", tint_col=None, fit=None):
    """Gemalte Textur (Box-Projektion über Objektkoordinaten, keine UVs nötig) × weiche Schattierung."""
    key = ("pt", name, file, scale)
    if key in _cache:
        return _cache[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / scale, 1 / scale, 1 / scale)
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(os.path.join(TEX, file), check_existing=True)
    if proj == "BOX":
        t.projection = "BOX"
        t.projection_blend = 0.15
        nt.links.new(tc.outputs["Object"], mp.inputs[0])
    elif proj == "FLAT":
        t.projection = "FLAT"
        nt.links.new(tc.outputs["Object"], mp.inputs[0])
        if fit:
            mp.inputs["Scale"].default_value = (1 / fit[0], 1 / fit[1], 1)
            mp.inputs["Location"].default_value = (0.5, 0.5, 0)
    else:
        nt.links.new(tc.outputs["UV"], mp.inputs[0])
    nt.links.new(mp.outputs[0], t.inputs[0])
    col = t.outputs[0]
    if tint_col:
        tm = nt.nodes.new("ShaderNodeMix")
        tm.data_type, tm.blend_type = "RGBA", "MULTIPLY"
        tm.inputs[0].default_value = 1.0
        nt.links.new(col, tm.inputs[6])
        tm.inputs[7].default_value = (*tint_col, 1)
        col = tm.outputs[2]
    if emit:
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs[1].default_value = emit
        nt.links.new(col, em.inputs[0])
        nt.links.new(em.outputs[0], out.inputs[0])
    else:
        ramp = _ramp(nt, shade, tint)
        mul = nt.nodes.new("ShaderNodeMix")
        mul.data_type, mul.blend_type = "RGBA", "MULTIPLY"
        mul.inputs[0].default_value = 1.0
        nt.links.new(col, mul.inputs[6])
        nt.links.new(ramp.outputs[0], mul.inputs[7])
        em = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(mul.outputs[2], em.inputs[0])
        nt.links.new(em.outputs[0], out.inputs[0])
    m["toon"] = 1
    _cache[key] = m
    return m


def box(name, loc, size, mat, rot=(0, 0, 0), bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new("bev", "BEVEL")
        b.width = bevel
        b.segments = 3
    if parent:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o


def cyl(name, loc, r, h, mat, verts=24, rot=(0, 0, 0), r2=None, parent=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=h, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    if parent:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o


def uvplane(name, loc, w, h, mat, rot):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (w, h, 1)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mat)
    return o


def ell(name, loc, r, mat, seg=20, rings=12, parent=None):
    o = F.ellipsoid(name, Vector(loc), r, mat, seg=seg, rings=rings)
    if parent:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o


def group(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.location = loc
    return e


# Raummaße
X0, X1, Y0, Y1, H = -2.4, 2.4, -2.6, 2.8, 2.45


def build():
    S = {"falls": [], "swing": [], "rattle": [], "screens": {}}
    wood_dark = soft("wooddark", (0.48, 0.32, 0.2))
    wood_mid = soft("woodmid", (0.66, 0.46, 0.28))
    white = soft("offwhite", (0.94, 0.93, 0.9), shade=0.78)
    alu = soft("alu", (0.78, 0.8, 0.82), shade=0.7)
    black = soft("blackplastic", (0.12, 0.12, 0.14), shade=0.8)
    # ---------- Hülle ----------
    floor = box("floor", (0, (Y0 + Y1) / 2, -0.05), (X1 - X0, Y1 - Y0, 0.1), painted("floorwood", "floor_wood.png", scale=1.6, proj="FLAT"))
    wallm = painted("wallcream", "wall_cream.png", scale=1.4)
    box("wall_front", (0, Y1 + 0.05, H / 2), (X1 - X0, 0.1, H), wallm)
    box("wall_back", (0, Y0 - 0.05, H / 2), (X1 - X0, 0.1, H), wallm)
    box("wall_left", (X0 - 0.05, (Y0 + Y1) / 2, H / 2), (0.1, Y1 - Y0, H), painted("wallgreen", "wall_green.png", scale=1.4))
    box("wall_right", (X1 + 0.05, (Y0 + Y1) / 2, H / 2), (0.1, Y1 - Y0, H), wallm)
    box("ceiling", (0, (Y0 + Y1) / 2, H + 0.05), (X1 - X0, Y1 - Y0, 0.1), painted("ceil", "ceiling.png", scale=2.0))
    for nm, loc, size in (("skirt_f", (0, Y1 - 0.01, 0.045), (X1 - X0, 0.025, 0.09)), ("skirt_b", (0, Y0 + 0.01, 0.045), (X1 - X0, 0.025, 0.09)),
                          ("skirt_l", (X0 + 0.01, (Y0 + Y1) / 2, 0.045), (0.025, Y1 - Y0, 0.09)), ("skirt_r", (X1 - 0.01, (Y0 + Y1) / 2, 0.045), (0.025, Y1 - Y0, 0.09)),
                          ("crown_f", (0, Y1 - 0.02, H - 0.04), (X1 - X0, 0.05, 0.08)), ("crown_l", (X0 + 0.02, (Y0 + Y1) / 2, H - 0.04), (0.05, Y1 - Y0, 0.08)),
                          ("crown_r", (X1 - 0.02, (Y0 + Y1) / 2, H - 0.04), (0.05, Y1 - Y0, 0.08)), ("crown_b", (0, Y0 + 0.02, H - 0.04), (X1 - X0, 0.05, 0.08))):
        box(nm, loc, size, white)
    # ---------- Fenster (Schiebetür zum Garten) vorne links ----------
    wx0, wx1, wz0, wz1 = -2.05, -0.25, 0.25, 2.1
    cx = (wx0 + wx1) / 2
    for nm, loc, size in (("wf_top", (cx, Y1, wz1), (wx1 - wx0 + 0.1, 0.14, 0.08)), ("wf_bot", (cx, Y1, wz0), (wx1 - wx0 + 0.1, 0.14, 0.08)),
                          ("wf_l", (wx0, Y1, (wz0 + wz1) / 2), (0.08, 0.14, wz1 - wz0)), ("wf_r", (wx1, Y1, (wz0 + wz1) / 2), (0.08, 0.14, wz1 - wz0)),
                          ("wf_mid", (cx, Y1 - 0.03, (wz0 + wz1) / 2), (0.07, 0.06, wz1 - wz0)), ("wf_trans", (cx, Y1 - 0.02, 1.75), (wx1 - wx0, 0.05, 0.05))):
        box(nm, loc, size, alu, bevel=0.01)
    # Wand um das Fenster herum: Loch -> wir decken die Wand dort mit dem Ausblick ab (Ausblick liegt hinter der Wand)
    hole = box("wall_hole_cut", (cx, Y1 + 0.05, (wz0 + wz1) / 2), (wx1 - wx0, 0.3, wz1 - wz0), white)
    mod = bpy.data.objects["wall_front"].modifiers.new("hole", "BOOLEAN")
    mod.object = hole
    mod.operation = "DIFFERENCE"
    hole.hide_render = True
    hole.hide_viewport = True
    glass = uvplane("glass", (cx, Y1 + 0.02, (wz0 + wz1) / 2), wx1 - wx0, wz1 - wz0, soft("glassm", (0.86, 0.92, 0.96), shade=0.95), (math.radians(90), 0, 0))
    glass.hide_render = True  # Glas unsichtbar, nur Spiegelstreifen
    view = uvplane("view", (cx, Y1 + 1.6, 1.15), 4.6, 2.9, painted("viewm", "window_view.png", emit=1.0, proj="UV"), (math.radians(90), 0, 0))
    box("sill", (cx, Y1 - 0.1, wz0 - 0.02), (wx1 - wx0 + 0.3, 0.22, 0.05), white, bevel=0.01)
    # Vorhänge (gefaltet) + Stange
    cyl("rod", (cx, Y1 - 0.12, wz1 + 0.12), 0.018, wx1 - wx0 + 0.7, alu, verts=10, rot=(0, math.radians(90), 0))
    curt = painted("curtm", "curtain.png", scale=0.6, shade=0.6)
    for side, x in (("L", wx0 - 0.12), ("R", wx1 + 0.12)):
        bm = bmesh.new()
        nx, nz = 18, 6
        w = 0.55
        verts = []
        for j in range(nz + 1):
            row = []
            for i in range(nx + 1):
                u = i / nx
                row.append(bm.verts.new(((u - 0.5) * w, 0.05 * math.sin(u * math.pi * 6), j / nz * (wz1 + 0.1))))
            verts.append(row)
        for j in range(nz):
            for i in range(nx):
                bm.faces.new((verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]))
        me = bpy.data.meshes.new("curtain" + side)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new("curtain" + side, me)
        sc.collection.objects.link(o)
        o.location = (x, Y1 - 0.14, 0.02)
        o.data.materials.append(curt)
        o.modifiers.new("s", "SOLIDIFY").thickness = 0.015
        S["swing"].append(o)
    # Klimaanlage über dem Fenster
    ac = box("aircon", (cx, Y1 - 0.13, 2.2), (0.85, 0.24, 0.26), white, bevel=0.04)
    box("aclouver", (cx, Y1 - 0.255, 2.12), (0.78, 0.01, 0.05), soft("acgrey", (0.7, 0.72, 0.74)))
    # ---------- Fernseher auf Lowboard vorne rechts ----------
    tvx = 1.1
    lb = group("lowboard", (tvx, Y1 - 0.25, 0))
    box("lb_body", (tvx, Y1 - 0.25, 0.25), (1.6, 0.42, 0.42), wood_mid, bevel=0.01, parent=lb)
    for k in range(3):
        box("lb_drawer", (tvx - 0.52 + k * 0.52, Y1 - 0.465, 0.25), (0.48, 0.01, 0.32), wood_dark, parent=lb)
        box("lb_handle", (tvx - 0.52 + k * 0.52, Y1 - 0.475, 0.34), (0.14, 0.015, 0.02), alu, parent=lb)
    for k, lx in enumerate((tvx - 0.75, tvx + 0.75)):
        cyl("lb_leg", (lx, Y1 - 0.25, 0.02), 0.02, 0.04, black, verts=8, parent=lb)
    tv = group("tv", (tvx, Y1 - 0.25, 0.46))
    box("tv_frame", (tvx, Y1 - 0.25, 0.86), (0.95, 0.06, 0.58), black, bevel=0.01, parent=tv)
    box("tv_neck", (tvx, Y1 - 0.25, 0.52), (0.08, 0.05, 0.12), black, parent=tv)
    box("tv_foot", (tvx, Y1 - 0.25, 0.47), (0.36, 0.2, 0.02), black, parent=tv)
    scr = uvplane("tv_screen", (tvx, Y1 - 0.285, 0.87), 0.87, 0.49, bpy.data.materials.new("tvscr"), (math.radians(90), 0, 0))
    scr.data.materials.clear()
    S["screens"]["tv"] = scr
    S["tv"] = tv
    box("dvd", (tvx - 0.45, Y1 - 0.3, 0.485), (0.4, 0.28, 0.05), black, bevel=0.005, parent=lb)
    box("console", (tvx + 0.5, Y1 - 0.3, 0.5), (0.16, 0.22, 0.08), white, bevel=0.01, parent=lb)
    pot = cyl("tvplantpot", (tvx + 0.72, Y1 - 0.3, 0.53), 0.06, 0.12, soft("potw", (0.9, 0.88, 0.84)), verts=14, parent=lb)
    for k in range(6):
        ell("tvleaf", (tvx + 0.72 + 0.05 * math.cos(k), Y1 - 0.3 + 0.05 * math.sin(k), 0.64 + 0.03 * (k % 2)), (0.035, 0.02, 0.07), soft("leaf", (0.32, 0.56, 0.32)), parent=lb)
    # ---------- Bücherregal rechts ----------
    sx = X1 - 0.2
    SY = 0.85
    shelf = group("shelf", (sx, 0.7 + SY, 0))
    box("sh_side1", (sx, 0.05 + SY, 0.95), (0.36, 0.03, 1.9), wood_mid, parent=shelf)
    box("sh_side2", (sx, 1.35 + SY, 0.95), (0.36, 0.03, 1.9), wood_mid, parent=shelf)
    box("sh_back", (X1 - 0.02, 0.7 + SY, 0.95), (0.02, 1.3, 1.9), wood_dark, parent=shelf)
    bookm = painted("booksm", "books.png", emit=0.0, proj="UV")
    for k, z in enumerate((0.02, 0.48, 0.94, 1.4, 1.88)):
        box("sh_board", (sx, 0.7 + SY, z), (0.36, 1.3, 0.025), wood_mid, parent=shelf)
        if k < 4:
            nb = R.randint(9, 16)
            yb = 0.08
            for b in range(nb):
                w = R.uniform(0.03, 0.06)
                h = R.uniform(0.25, 0.38)
                if yb + w > 1.32:
                    break
                tilt = math.radians(R.choice((0, 0, 0, 8, -6)))
                bk = box("book", (sx + 0.02, yb + w / 2 + SY, z + 0.013 + h / 2), (0.24, w, h),
                         soft(f"book{R.randint(0, 6)}", R.choice([(0.72, 0.22, 0.2), (0.22, 0.32, 0.56), (0.86, 0.74, 0.3), (0.26, 0.5, 0.32), (0.9, 0.9, 0.86), (0.5, 0.26, 0.44), (0.84, 0.5, 0.22)])),
                         rot=(tilt, 0, 0), parent=shelf)
                S["falls"].append(bk)
                yb += w + 0.004
            if k == 2:
                dar = ell("daruma", (sx, yb + 0.12 + SY, z + 0.1), (0.07, 0.07, 0.085), soft("darum", (0.85, 0.15, 0.12)), parent=shelf)
                ell("darumaface", (sx - 0.06, yb + 0.12 + SY, z + 0.11), (0.02, 0.045, 0.04), soft("darumf", (0.97, 0.93, 0.86)), parent=shelf)
                S["falls"].append(dar)
    CX, CZ, FY = 1.1, 1.82, Y1 - 0.03
    clock = group("clock", (CX, FY, CZ))
    cyl("clockrim", (CX, FY, CZ), 0.17, 0.04, wood_dark, verts=32, rot=(math.radians(90), 0, 0), parent=clock)
    cyl("clockface", (CX, FY - 0.025, CZ), 0.15, 0.01, white, verts=32, rot=(math.radians(90), 0, 0), parent=clock)
    for k in range(12):
        a = k * math.pi / 6
        box("tick", (CX + 0.12 * math.cos(a), FY - 0.032, CZ + 0.12 * math.sin(a)), (0.012, 0.004, 0.012), black, parent=clock)
    for nm, ang, ln, w in (("hhand", math.pi / 2 - (2 + 46 / 60) * math.pi / 6, 0.07, 0.012), ("mhand", math.pi / 2 - 46 * math.pi / 30, 0.11, 0.008)):
        box(nm, (CX + ln / 2 * math.cos(ang), FY - 0.036, CZ + ln / 2 * math.sin(ang)), (w, 0.004, ln), black, rot=(0, -(math.pi / 2 - ang), 0), parent=clock)
    S["swing"].append(clock)
    cal = uvplane("calendar", (2.05, Y1 - 0.02, 1.4), 0.42, 0.56, painted("calm", "calendar.png", emit=0.0, proj="UV", shade=0.85), (math.radians(90), 0, 0))
    S["swing"].append(cal)
    art = group("painting", (X0 + 0.03, 0.2, 1.65))
    box("artframe", (X0 + 0.03, 0.2, 1.65), (0.04, 0.95, 0.62), wood_dark, parent=art)
    uvplane("artimg", (X0 + 0.055, 0.2, 1.65), 0.86, 0.53, painted("artm", "window_view.png", proj="UV", shade=0.9), (math.radians(90), 0, math.radians(-90))).parent = art
    S["swing"].append(art)
    # ---------- Sideboard links mit Geschirr, Fotos, Pflanze ----------
    sbx = X0 + 0.25
    sb = group("sideboard", (sbx, 0.2, 0))
    box("sb_body", (sbx, 0.2, 0.45), (0.45, 1.5, 0.9), wood_dark, bevel=0.01, parent=sb)
    for k in range(2):
        box("sb_glass", (sbx + 0.226, -0.17 + k * 0.74, 0.55), (0.01, 0.66, 0.5), soft("sbglass", (0.7, 0.8, 0.86), shade=0.85), parent=sb)
        box("sb_knob", (sbx + 0.235, 0.15 + k * 0.1, 0.55), (0.02, 0.02, 0.06), alu, parent=sb)
    for k in range(8):
        d = cyl("dish", (sbx + 0.1, -0.4 + k * 0.17, 0.42), 0.07, 0.02, soft("dishm", (0.95, 0.95, 0.97), shade=0.8), verts=20, rot=(0, math.radians(80), 0), parent=sb)
        S["rattle"].append(d)
    for k in range(4):
        pf = group(f"photo{k}", (sbx, -0.3 + k * 0.33, 0.91))
        box("pframe", (sbx, -0.3 + k * 0.33, 1.02), (0.03, 0.24, 0.19), wood_mid, rot=(0, math.radians(-12), 0), parent=pf)
        uvplane("pimg", (sbx + 0.021, -0.3 + k * 0.33, 1.025), 0.2, 0.15, painted(f"ph{k}", f"photo{k}.png", proj="UV", emit=0.0, shade=0.85),
                (math.radians(90), math.radians(-12), math.radians(90))).parent = pf
        S["falls"].append(pf)
    bigpot = cyl("bigpot", (X0 + 0.3, 1.8, 0.2), 0.16, 0.4, soft("bigpotm", (0.22, 0.24, 0.26)), verts=18)
    leafm = soft("bigleaf", (0.26, 0.5, 0.3), shade=0.6)
    stemm = soft("stemm", (0.3, 0.42, 0.24))
    for k in range(14):
        a = k * 2.4
        ln = R.uniform(0.3, 0.75)
        rr = R.uniform(0.12, 0.3)
        tip = Vector((X0 + 0.3 + rr * math.cos(a), 1.8 + rr * math.sin(a), 0.4 + ln))
        F.limb("stem", Vector((X0 + 0.3, 1.8, 0.38)), tip, 0.007, 0.005, stemm, seg=6, subsurf=0)
        lf = ell("bigleafo", tip + Vector((0.08 * math.cos(a), 0.08 * math.sin(a), 0.02)), (0.15, 0.022, 0.1), leafm, seg=16, rings=8)
        lf.rotation_euler = (R.uniform(-0.5, 0.2), R.uniform(-0.4, 0.4), a + math.pi / 2)
        S["swing"].append(lf)
    # ---------- Teppich, Tisch, Snacks ----------
    box("rug", (0.0, 0.35, 0.006), (2.6, 1.9, 0.012), painted("rugm", "rug.png", proj="FLAT", fit=(2.6, 1.9), shade=0.7))
    tb = group("table", (0, 0.4, 0))
    box("tb_top", (0, 0.4, 0.38), (1.2, 0.75, 0.05), painted("tbwood", "floor_wood.png", scale=1.2, tint_col=(0.85, 0.75, 0.7), proj="FLAT"), bevel=0.015, parent=tb)
    box("tb_shelf", (0, 0.4, 0.12), (1.08, 0.64, 0.03), wood_mid, parent=tb)
    for lx in (-0.55, 0.55):
        for ly in (0.08, 0.72):
            box("tb_leg", (lx, ly, 0.19), (0.05, 0.05, 0.36), wood_dark, parent=tb)
    plate = cyl("plate", (-0.25, 0.32, 0.41), 0.12, 0.015, soft("platem", (0.97, 0.97, 0.95), shade=0.8), verts=24, parent=tb)
    for k in range(6):
        a = k * math.pi / 3
        S["rattle"].append(cyl("senbei", (-0.25 + 0.06 * math.cos(a), 0.32 + 0.06 * math.sin(a), 0.425), 0.035, 0.012, soft("senb", (0.74, 0.5, 0.26)), verts=14, parent=tb))
    bowl = cyl("bowl", (0.3, 0.55, 0.43), 0.11, 0.07, soft("bowlm", (0.3, 0.42, 0.62)), verts=22, r2=0.07, rot=(math.pi, 0, 0), parent=tb)
    for k in range(5):
        S["rattle"].append(ell("mikan", (0.3 + 0.05 * math.cos(k * 1.3), 0.55 + 0.05 * math.sin(k * 1.3), 0.48 + 0.02 * (k % 2)), (0.04, 0.04, 0.035), soft("mikanm", (0.95, 0.56, 0.12)), parent=tb))
    for k, (x, y) in enumerate(((0.05, 0.2), (-0.45, 0.6))):
        S["rattle"].append(cyl("teacup", (x, y, 0.445), 0.035, 0.08, soft("cupm", (0.82, 0.86, 0.8)), verts=16, r2=0.04, parent=tb))
    teapot = ell("teapot", (0.0, 0.62, 0.47), (0.08, 0.08, 0.07), soft("teapotm", (0.3, 0.32, 0.3)), parent=tb)
    S["rattle"].append(teapot)
    remote = box("remote", (0.4, 0.2, 0.413), (0.05, 0.18, 0.02), black, rot=(0, 0, 0.3), bevel=0.006, parent=tb)
    for k in range(6):
        box("rbtn", (0.4 + 0.012 * (k % 2) - 0.006, 0.17 + 0.02 * (k // 2), 0.425), (0.008, 0.008, 0.004), soft("btn", (0.85, 0.3, 0.3)), parent=tb)
    S["rattle"].append(remote)
    manga = box("manga", (-0.35, 0.12, 0.415), (0.13, 0.18, 0.018), soft("mangam", (0.9, 0.3, 0.35)), rot=(0, 0, -0.2), parent=tb)
    box("mangapages", (-0.35, 0.12, 0.415), (0.125, 0.175, 0.012), white, rot=(0, 0, -0.2), parent=tb)
    tis = box("tissue", (0.45, 0.62, 0.44), (0.22, 0.11, 0.08), soft("tism", (0.9, 0.84, 0.92)), bevel=0.01, parent=tb)
    ell("tissuepop", (0.45, 0.62, 0.49), (0.03, 0.02, 0.03), white, parent=tb)
    S["rattle"].append(tis)
    S["table"] = tb
    # Kissen (Zabuton) + Ranzen
    zab = painted("zabm", "zabuton.png", scale=0.5)
    for x, y in ((-0.95, 0.5), (0.95, 0.35)):
        box("zabuton", (x, y, 0.04), (0.5, 0.55, 0.07), zab, bevel=0.025)
    rand = group("randoseru", (1.7, -0.8, 0))
    box("rnd_body", (1.7, -0.8, 0.2), (0.28, 0.2, 0.36), soft("randm", (0.75, 0.12, 0.14), shade=0.6), bevel=0.04, parent=rand)
    box("rnd_flap", (1.7, -0.905, 0.25), (0.29, 0.02, 0.3), soft("randm", (0.75, 0.12, 0.14), shade=0.6), bevel=0.02, parent=rand)
    box("rnd_lock", (1.7, -0.92, 0.12), (0.05, 0.01, 0.04), alu, parent=rand)
    S["falls"].append(rand)
    # ---------- Sofa (ich sitze darauf, hinten) ----------
    sofam = painted("sofam", "sofa.png", scale=0.4, shade=0.62)
    sofa = group("sofa", (0, -2.05, 0))
    box("sofa_base", (0, -2.05, 0.22), (2.0, 0.85, 0.3), sofam, bevel=0.05, parent=sofa)
    box("sofa_back", (0, -2.42, 0.62), (2.0, 0.22, 0.6), sofam, bevel=0.08, parent=sofa)
    for x in (-0.95, 0.95):
        box("sofa_arm", (x, -2.05, 0.45), (0.2, 0.85, 0.36), sofam, bevel=0.08, parent=sofa)
    for x in (-0.45, 0.45):
        box("sofa_cush", (x, -1.98, 0.42), (0.86, 0.72, 0.14), sofam, bevel=0.06, parent=sofa)
    box("throwpillow", (-0.7, -2.2, 0.62), (0.34, 0.12, 0.34), painted("cushm", "cushion.png", scale=0.3), rot=(math.radians(-15), 0, math.radians(20)), bevel=0.06, parent=sofa)
    # ---------- Deckenlampe (rund, japanisch, mit Zugschnur) ----------
    lamp = group("ceillamp", (0, 0.2, H))
    cyl("lamp_base", (0, 0.2, H - 0.04), 0.1, 0.06, white, verts=24, parent=lamp)
    cyl("lamp_cord", (0, 0.2, H - 0.3), 0.008, 0.5, black, verts=6, parent=lamp)
    cyl("lamp_shade", (0, 0.2, H - 0.6), 0.32, 0.1, soft("shade", (0.96, 0.95, 0.9), shade=0.82), verts=40, parent=lamp)
    cyl("lamp_rim", (0, 0.2, H - 0.66), 0.33, 0.02, soft("lrim", (0.65, 0.5, 0.35)), verts=40, parent=lamp)
    cyl("pull", (0.12, 0.2, H - 0.85), 0.003, 0.35, black, verts=6, parent=lamp)
    ell("pullknob", (0.12, 0.2, H - 1.03), (0.012, 0.012, 0.02), soft("knob", (0.9, 0.85, 0.3)), parent=lamp)
    S["lamp"] = lamp
    # Tür zur Küche hinten rechts mit Noren-Vorhang
    box("door_frame", (1.6, Y0 + 0.02, 1.0), (0.9, 0.06, 2.0), wood_mid)
    box("door_dark", (1.6, Y0 + 0.04, 1.0), (0.8, 0.02, 1.95), soft("kitchen", (0.35, 0.32, 0.3)))
    noren = painted("norenm", "curtain.png", scale=0.3, tint_col=(1.3, 0.6, 0.6))
    for k in range(3):
        uvplane("noren", (1.33 + k * 0.27, Y0 + 0.08, 1.6), 0.26, 0.75, noren, (math.radians(90), 0, 0))
    # ---------- Licht ----------
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sc.collection.objects.link(sun)
    sun.data.energy = 2.2
    sun.data.color = (1.0, 0.95, 0.86)
    sun.data.angle = math.radians(2.0)
    sun.rotation_euler = (math.radians(58), 0, math.radians(200))  # fällt durchs Fenster schräg auf den Boden
    fill = bpy.data.objects.new("fill", bpy.data.lights.new("fill", "AREA"))
    sc.collection.objects.link(fill)
    fill.data.energy = 120
    fill.data.size = 2.0
    fill.data.color = (0.86, 0.9, 1.0)
    fill.location = (cx, Y1 - 0.6, 1.3)
    fill.rotation_euler = (math.radians(-90), 0, 0)
    room = bpy.data.objects.new("roomlight", bpy.data.lights.new("roomlight", "AREA"))
    sc.collection.objects.link(room)
    room.data.energy = 140
    room.data.size = 3.5
    room.location = (0, 0, H - 0.05)
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.82, 0.84, 0.88, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.35
    return S


def tv_material(scr, keys):
    """keys: [(frame, Datei)] – wechselt das Fernsehbild (Nachrichten -> Warnung -> Tsunami -> aus)."""
    m = bpy.data.materials.new("tvscreen")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    files = []
    for _, f in keys:
        if f not in files:
            files.append(f)
    prev = None
    mixes = []
    for i, f in enumerate(files):
        if f == "off":
            c = nt.nodes.new("ShaderNodeRGB")
            c.outputs[0].default_value = (0.02, 0.02, 0.03, 1)
            col = c.outputs[0]
        else:
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(os.path.join(TEX, f), check_existing=True)
            col = t.outputs[0]
        if prev is None:
            prev = col
        else:
            mx = nt.nodes.new("ShaderNodeMix")
            mx.data_type = "RGBA"
            nt.links.new(prev, mx.inputs[6])
            nt.links.new(col, mx.inputs[7])
            mixes.append((f, mx))
            prev = mx.outputs[2]
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[1].default_value = 1.15
    nt.links.new(prev, em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    for f, mx in mixes:
        on = False
        idx = files.index(f)
        for fr, kf in keys:
            on_now = files.index(kf) >= idx
            mx.inputs[0].default_value = 1.0 if on_now else 0.0
            mx.inputs[0].keyframe_insert("default_value", frame=fr)
    for fc in (m.node_tree.animation_data.action.fcurves if m.node_tree.animation_data and hasattr(m.node_tree.animation_data.action, "fcurves") else []):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"
    m["toon"] = 1
    scr.data.materials.append(m)
    return m
