# Futaba-Straße im Ink-Pop-Stil: Wohn-/Ladenstraße, Häuser mit Fenstern, Klimageräten, Regenrinnen, Balkonen,
# Läden mit Markisen + Schildern, Blockmauern mit Büschen, Strommasten mit Trafos + vielen Leitungen,
# Verkehrsspiegel, Getränkeautomaten, Kleinwagen, Fahrräder, Schild „原子力 明るい未来のエネルギー“, Hügel, Wolken.
# Straße läuft entlang +y (x = 0 Mitte, Breite 6 m).
import bpy, bmesh, math, os, random
from mathutils import Vector
import figure as F

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "futaba", "tex")
sc = bpy.context.scene
R = random.Random(11)
M = lambda name, col, shade=0.72: F.ink_mat(name, col, shade=shade)


def texmat(name, file, shade=0.78, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(os.path.join(TEX, file))
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    nt.links.new(dif.outputs[0], s2r.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = (shade, shade, shade * 1.05, 1)
    ramp.color_ramp.elements[1].position = 0.42
    nt.links.new(s2r.outputs[0], ramp.inputs[0])
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    nt.links.new(t.outputs[0], mul.inputs[6])
    nt.links.new(ramp.outputs[0], mul.inputs[7])
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mul.outputs[2], em.inputs[0])
    em.inputs[1].default_value = 1.0 + emit
    nt.links.new(em.outputs[0], out.inputs[0])
    m["toon"] = 1
    return m


def box(name, loc, size, mat, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new("bev", "BEVEL")
        b.width = bevel
        b.segments = 2
    return o


def plane(name, loc, w, h, mat, rot):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (w, h, 1)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mat)
    return o


def cyl(name, loc, r, h, mat, verts=16, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    return o


def gable(name, cx, cy, w, l, z, rise, mat, over=0.55, along_y=True):
    bm = bmesh.new()
    hw, hl = w / 2 + over, l / 2 + over
    if along_y:
        pts = ((-hw, -hl, 0), (hw, -hl, 0), (0, -hl, rise), (-hw, hl, 0), (hw, hl, 0), (0, hl, rise))
    else:
        pts = ((-hw, -hl, 0), (-hw, hl, 0), (-hw, 0, rise), (hw, -hl, 0), (hw, hl, 0), (hw, 0, rise))
    v = [bm.verts.new(p) for p in pts]
    for f in ((0, 1, 2), (3, 5, 4), (0, 2, 5, 3), (1, 4, 5, 2), (0, 3, 4, 1)):
        bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    o.location = (cx, cy, z)
    o.data.materials.append(mat)
    s = o.modifiers.new("s", "SOLIDIFY")
    s.thickness = 0.14
    return o


def wire(p0, p1, sag, mat, name="wire", r=0.011):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 1
    mid = (p0 + p1) / 2
    sp = cu.splines.new("POLY")
    n = 16
    sp.points.add(n - 1)
    for i in range(n):
        u = i / (n - 1)
        q = p0.lerp(p1, u) - mid
        q.z -= sag * 4 * u * (1 - u)
        sp.points[i].co = (q.x, q.y, q.z, 1)
    o = bpy.data.objects.new(name, cu)
    sc.collection.objects.link(o)
    o.location = mid
    o.data.materials.append(mat)
    return o


def bush(name, loc, size, mat):
    objs = []
    for k in range(4):
        o = F.ellipsoid(f"{name}{k}", Vector(loc) + Vector((R.uniform(-0.3, 0.3) * size, R.uniform(-0.2, 0.2) * size, R.uniform(0, 0.25) * size)),
                        (size * R.uniform(0.45, 0.6), size * R.uniform(0.4, 0.55), size * R.uniform(0.35, 0.5)), mat, seg=14, rings=8)
        objs.append(o)
    return objs


# ---------------------------------------------------------------------------
def build(y0=-14.0, y1=96.0, sign_y=78.0):
    S = {"poles": [], "wires": [], "shake": [], "falls": [], "lamps": [], "signs": [], "vms": [], "windows": []}
    asph = M("asphalt", (0.5, 0.51, 0.55), 0.8)
    white = M("roadwhite", (0.96, 0.96, 0.94), 0.85)
    box("road", (0, (y0 + y1) / 2, -0.05), (6.4, y1 - y0, 0.1), asph)
    for x in (-3.0, 3.0):
        box("edgeline", (x, (y0 + y1) / 2, 0.003), (0.13, y1 - y0, 0.01), white)
    for x in (-3.7, 3.7):
        box("gutter", (x, (y0 + y1) / 2, -0.03), (1.3, y1 - y0, 0.1), M("gutter", (0.7, 0.7, 0.68), 0.8))
        box("curbline", (x * 0.86, (y0 + y1) / 2, 0.0), (0.06, y1 - y0, 0.04), M("curb", (0.78, 0.78, 0.76)))
    box("field", (0, (y0 + y1) / 2, -0.15), (300, 400, 0.1), M("grass", (0.56, 0.66, 0.42), 0.8))
    # Gullydeckel + "止まれ"
    for y in (6.0, 21.0, 37.0, 52.0):
        cyl("manhole", (R.choice((-1, 1)) * 1.2, y, 0.005), 0.32, 0.012, M("manhole", (0.36, 0.37, 0.4)), verts=24)
    tm = texmat("tomare", "tomare.png")
    tm.node_tree.nodes["Emission"].inputs[1].default_value = 1.0
    plane("tomare", (-1.5, 28.0, 0.006), 2.2, 1.0, tm, (0, 0, math.pi))
    box("stopline", (-1.5, 29.0, 0.004), (2.8, 0.25, 0.01), white)
    # Querstraße bei y = 30
    box("crossroad", (0, 30.5, -0.049), (60, 6.0, 0.1), asph)

    # ---------- Häuser ----------
    WALLS = [(0.95, 0.92, 0.84), (0.88, 0.88, 0.87), (0.93, 0.86, 0.74), (0.82, 0.87, 0.9), (0.96, 0.94, 0.9), (0.86, 0.8, 0.72), (0.9, 0.82, 0.8)]
    ROOFS = [(0.3, 0.34, 0.44), (0.45, 0.3, 0.26), (0.26, 0.28, 0.32), (0.34, 0.42, 0.5), (0.5, 0.42, 0.36)]
    frame_m = M("winframe", (0.82, 0.84, 0.86))
    glass_m = M("glass", (0.6, 0.74, 0.84), 0.85)
    glass_hi = M("glasshi", (0.86, 0.93, 0.98), 0.9)
    curtain = [M("curt1", (0.95, 0.9, 0.78)), M("curt2", (0.82, 0.88, 0.94)), M("curt3", (0.94, 0.82, 0.82))]
    pipe_m = M("pipe", (0.7, 0.72, 0.72))
    ac_m = M("ac", (0.92, 0.92, 0.9))
    dark = M("dark", (0.18, 0.19, 0.22))
    shops = [("sign_tanaka.png", "awning_red.png"), ("sign_cafe.png", "awning_green.png"), ("sign_barber.png", None), ("sign_drug.png", "awning_red.png")]
    shop_i = 0

    def window(fx, side, y, z, w, h):
        ox = -side * 0.03
        box("wframe", (fx + ox, y, z), (0.08, w + 0.12, h + 0.12), frame_m)
        box("wglass", (fx + ox * 2.2, y, z), (0.04, w, h), glass_m)
        # Glanz-Streifen diagonal
        st = plane("whi", (fx + ox * 2.6, y - w * 0.15, z + h * 0.1), w * 0.18, h * 0.9, glass_hi, (math.radians(90), math.radians(25), math.radians(90)))
        if R.random() < 0.6:
            box("curtain", (fx + ox * 1.6, y + w * 0.3, z), (0.02, w * 0.35, h * 0.95), R.choice(curtain))
        box("wmullion", (fx + ox * 2.5, y, z), (0.03, 0.04, h), frame_m)

    houses = []
    for side in (-1, 1):
        y = y0
        while y < y1 - 4:
            if abs(y - 30.5) < 4.2:  # Kreuzung frei lassen
                y = 34.8
                continue
            l = R.uniform(6.5, 9.0)
            w = R.uniform(7.0, 9.0)
            floors = 2 if R.random() < 0.8 else 1
            hgt = 2.9 * floors
            cx = side * (4.7 + w / 2)
            cy = y + l / 2
            fx = side * 4.7
            wall = M(f"wall{len(houses)}", R.choice(WALLS), 0.74)
            hb = box(f"house{len(houses)}", (cx, cy, hgt / 2), (w, l, hgt), wall)
            gable(f"roof{len(houses)}", cx, cy, w, l, hgt, R.uniform(1.4, 2.2), M(f"roofm{len(houses) % 5}", R.choice(ROOFS), 0.62), along_y=R.random() < 0.6)
            box("fascia", (fx - side * 0.05, cy, hgt - 0.08), (0.12, l + 0.9, 0.16), M("fascia", (0.88, 0.88, 0.86)))
            # Erdgeschoss: Laden oder Wohnung
            is_shop = shop_i < len(shops) and R.random() < 0.5 and 4 < y < 70
            if is_shop:
                sign_f, awn_f = shops[shop_i]
                plane(f"shopsign{shop_i}", (fx - side * 0.06, cy, 2.55), 0.75, min(4.6, l - 1.6), texmat(f"ss{shop_i}", sign_f),
                      (math.radians(90), 0, math.radians(90 if side < 0 else -90)))
                S["signs"].append(bpy.context.object)
                box("shopglass", (fx - side * 0.02, cy, 1.1), (0.05, l - 2.2, 2.0), glass_m)
                for k in range(int((l - 2.2) / 1.0) + 1):
                    box("mull", (fx - side * 0.05, cy - (l - 2.2) / 2 + k * 1.0, 1.1), (0.05, 0.06, 2.0), frame_m)
                if awn_f:
                    aw = plane(f"awning{shop_i}", (fx - side * 0.55, cy, 2.15), 1.2, l - 1.6, texmat(f"aw{shop_i}", awn_f),
                               (0, math.radians(-25 if side > 0 else 25), 0))
                    aw.modifiers.new("s", "SOLIDIFY").thickness = 0.03
                shop_i += 1
                S.setdefault("shopfront", []).append((side, cy, shop_i - 1))
            else:
                window(fx, side, cy + l * 0.22, 1.5, 1.6, 1.1)
                box("door", (fx - side * 0.03, cy - l * 0.25, 1.05), (0.06, 0.95, 2.1), M("door", (0.55, 0.42, 0.32)))
                box("doorroof", (fx - side * 0.35, cy - l * 0.25, 2.3), (0.7, 1.4, 0.06), M("droof", (0.4, 0.42, 0.46)))
            if floors == 2:
                for k in (-1, 1):
                    window(fx, side, cy + k * l * 0.24, 4.3, 1.5, 1.0)
                if R.random() < 0.6:  # Balkon
                    box("balcony", (fx - side * 0.45, cy, 3.2), (0.9, l * 0.55, 0.08), M("balc", (0.8, 0.8, 0.8)))
                    for k in range(9):
                        box("rail", (fx - side * 0.88, cy - l * 0.27 + k * l * 0.55 / 8, 3.6), (0.03, 0.03, 0.8), pipe_m)
                    box("railtop", (fx - side * 0.88, cy, 4.0), (0.05, l * 0.55, 0.05), pipe_m)
            # Klimagerät + Leitung
            if R.random() < 0.7:
                acz = 0.45 if R.random() < 0.5 else 3.35
                ac = box("acunit", (fx - side * 0.2, cy - l * 0.42, acz), (0.3, 0.75, 0.55), ac_m)
                cyl("acfan", (fx - side * 0.36, cy - l * 0.42 + 0.08, acz), 0.19, 0.02, dark, verts=20, rot=(0, math.radians(90), 0))
                S["shake"].append(ac)
            # Regenrinne + Fallrohr
            cyl("downpipe", (fx - side * 0.08, cy + l / 2 - 0.25, hgt / 2), 0.045, hgt, pipe_m, verts=10)
            houses.append((hb, side, cy, l, hgt))
            # Blockmauer mit Busch zwischen den Häusern
            gap = R.uniform(1.4, 3.0)
            box("blockwall", (side * 4.55, y + l + gap / 2, 0.6), (0.16, gap, 1.2), M("block", (0.76, 0.75, 0.72), 0.75), bevel=0.01)
            for k in range(int(gap / 0.4)):
                box("blockjoint", (side * 4.46, y + l + 0.2 + k * 0.4, 0.6), (0.01, 0.015, 1.2), M("blockj", (0.6, 0.6, 0.58)))
            bush("bush", (side * 5.2, y + l + gap / 2, 1.2), 0.9, M(f"bushm{side}", (0.36, 0.56, 0.34), 0.65))
            y += l + gap
    S["houses"] = houses

    # ---------- Strommasten + Leitungen ----------
    pole_m = M("pole", (0.68, 0.68, 0.66), 0.7)
    wire_m = F.flat_mat("wirem", (0.08, 0.08, 0.1))
    stripe = M("stripe", (0.95, 0.8, 0.15))
    for k, y in enumerate(range(int(y0) + 4, int(y1), 24)):
        if abs(y - 30.5) < 4:
            y += 6
        pv = bpy.data.objects.new(f"pole{k}", None)
        sc.collection.objects.link(pv)
        pv.location = (3.35, y, 0)
        parts = [cyl("polec", (0, 0, 4.7), 0.15, 9.4, pole_m, verts=14), box("arm1", (0, 0, 8.6), (2.0, 0.12, 0.12), pole_m),
                 box("arm2", (0, 0, 7.7), (1.5, 0.12, 0.12), pole_m), cyl("guard", (0, 0, 0.9), 0.17, 1.8, stripe, verts=14)]
        for dx in (-0.85, 0.0, 0.85):
            parts.append(cyl("insul", (dx, 0, 8.75), 0.05, 0.18, M("insulm", (0.9, 0.9, 0.92)), verts=8))
        if k % 2 == 0:
            parts.append(cyl("trafo", (0.42, 0, 6.6), 0.3, 1.0, M("trafom", (0.6, 0.63, 0.66)), verts=16))
            parts.append(cyl("trafo2", (-0.42, 0, 6.6), 0.26, 0.9, M("trafom", (0.6, 0.63, 0.66)), verts=16))
        for p in parts:
            p.parent = pv
        S["poles"].append(pv)
    for a, b in zip(S["poles"], S["poles"][1:]):
        for dx, z, sag in ((-0.85, 8.85, 0.45), (0.0, 8.85, 0.5), (0.85, 8.85, 0.45), (-0.65, 7.75, 0.6), (0.65, 7.75, 0.55), (0.1, 7.2, 0.7)):
            S["wires"].append((wire(a.location + Vector((dx, 0, z)), b.location + Vector((dx, 0, z)), sag + R.uniform(-0.08, 0.08), wire_m), "y"))
        # Hausanschlüsse über die Straße
        for t in (0.3, 0.7):
            yy = a.location.y + (b.location.y - a.location.y) * t
            S["wires"].append((wire(Vector((a.location.x - 0.7, yy, 7.4)), Vector((-4.8, yy + 1.5, 5.4)), 0.35, wire_m, "drop", 0.008), "x"))

    # ---------- Verkehrsspiegel an der Kreuzung ----------
    mp = cyl("mirrorpole", (-3.5, 27.2, 1.6), 0.05, 3.2, M("mpole", (0.95, 0.5, 0.15)), verts=10)
    mirror = cyl("mirror", (-3.5, 27.0, 3.2), 0.42, 0.06, M("mframe", (0.95, 0.5, 0.15)), verts=24, rot=(math.radians(90), 0, math.radians(30)))
    mglass = cyl("mirrorg", (-3.47, 26.96, 3.2), 0.36, 0.065, M("mglass", (0.75, 0.82, 0.9), 0.9), verts=24, rot=(math.radians(90), 0, math.radians(30)))
    S["shake"] += [mirror, mglass]

    # ---------- Getränkeautomaten ----------
    vm_m = texmat("vend", "vending.png", emit=0.3)
    for k, y in enumerate((16.6, 17.45)):
        v = box(f"vm{k}", (4.25, y, 0.92), (0.75, 0.82, 1.84), M("vmbody", (0.92, 0.92, 0.94)), bevel=0.02)
        f = plane("vmf", (3.86, y, 0.95), 0.76, 1.7, vm_m, (math.radians(90), 0, math.radians(-90)))
        f.parent = v
        f.matrix_parent_inverse = v.matrix_world.inverted()
        S["vms"].append(v)

    # ---------- Kleinwagen (Kei-Car) + Fahrräder ----------
    def keicar(name, loc, col, rot=0.0):
        body = box(name, (0, 0, 0.62), (1.45, 3.3, 0.75), M(name + "m", col, 0.68), bevel=0.12)
        cab = box(name + "cab", (0, 0.25, 1.25), (1.35, 2.2, 0.62), M(name + "m", col, 0.68), bevel=0.1)
        gl = box(name + "gl", (0, 0.25, 1.27), (1.38, 2.0, 0.45), glass_m, bevel=0.06)
        ws = box(name + "ws", (0, -0.86, 1.25), (1.2, 0.04, 0.48), glass_m, rot=(math.radians(-20), 0, 0))
        parts = [body, cab, gl, ws]
        for wx in (-0.68, 0.68):
            for wy in (-1.05, 1.05):
                parts.append(cyl(name + "wh", (wx, wy, 0.3), 0.3, 0.2, dark, verts=20, rot=(0, math.radians(90), 0)))
                parts.append(cyl(name + "hub", (wx * 1.08, wy, 0.3), 0.13, 0.02, M("hub", (0.8, 0.8, 0.82)), verts=12, rot=(0, math.radians(90), 0)))
        for lx in (-0.5, 0.5):
            parts.append(box(name + "lamp", (lx, -1.66, 0.75), (0.32, 0.03, 0.16), M("lampm", (0.98, 0.95, 0.85))))
        e = bpy.data.objects.new(name, None)
        sc.collection.objects.link(e)
        for p in parts:
            p.parent = e
        e.location = loc
        e.rotation_euler.z = rot
        return e

    S["cars"] = [keicar("car1", (-2.3, 12.5, 0), (0.92, 0.92, 0.9)), keicar("car2", (2.35, 44.0, 0), (0.55, 0.72, 0.85), math.pi),
                 keicar("car3", (-2.3, 58.0, 0), (0.85, 0.42, 0.36))]
    S["shake"] += S["cars"]

    def bike(name, loc, rot):
        e = bpy.data.objects.new(name, None)
        sc.collection.objects.link(e)
        fr = M("bikef", (0.75, 0.2, 0.22))
        for wy in (-0.5, 0.5):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.33, minor_radius=0.025, location=(0, wy, 0.34), rotation=(0, math.radians(90), 0))
            t = bpy.context.object
            t.data.materials.append(dark)
            t.parent = e
        for a, b in (((0, -0.5, 0.34), (0, 0.0, 0.75)), ((0, 0.0, 0.75), (0, 0.5, 0.34)), ((0, -0.15, 0.36), (0, 0.0, 0.75)), ((0, -0.15, 0.36), (0, 0.5, 0.34)),
                     ((0, 0.0, 0.75), (0, 0.05, 0.92)), ((0, -0.5, 0.34), (0, -0.42, 0.95))):
            l = F.limb("bikebar", Vector(a), Vector(b), 0.018, 0.018, fr, seg=8, subsurf=0)
            l.parent = e
        bx = box("basket", (0, -0.55, 0.95), (0.35, 0.3, 0.22), M("basketm", (0.75, 0.75, 0.78)))
        bx.parent = e
        e.location = loc
        e.rotation_euler = rot
        return e

    S["bikes"] = [bike("bike1", (-3.6, 15.2, 0), (0, 0, math.radians(8))), bike("bike2", (3.9, 21.0, 0), (0, 0, math.radians(-5)))]
    S["falls"] += S["bikes"]
    # Blumentöpfe vor dem Laden
    pots = []
    for k in range(4):
        pt = cyl(f"pot{k}", (-4.35, 18.5 + k * 0.55, 0.2), 0.18, 0.4, M("potm", (0.72, 0.42, 0.28)), verts=14)
        pl = F.ellipsoid("plant", Vector((-4.35, 18.5 + k * 0.55, 0.52)), (0.22, 0.22, 0.2), M("plantm", (0.38, 0.6, 0.35)), seg=12, rings=8)
        pl.parent = pt
        pl.matrix_parent_inverse = pt.matrix_world.inverted()
        pots.append(pt)
    S["pots"] = pots

    # ---------- Schild über der Straße ----------
    sg = texmat("signfut", "sign_futaba.png", shade=0.85)
    post_m = M("signpost", (0.55, 0.58, 0.62))
    for x in (-3.7, 3.7):
        cyl("signpost", (x, sign_y, 3.3), 0.14, 6.6, post_m, verts=12)
    box("signframe", (0, sign_y, 5.9), (7.8, 0.22, 1.1), post_m, bevel=0.03)
    plane("signface", (0, sign_y - 0.12, 5.9), 7.5, 0.94, sg, (math.radians(90), 0, 0))
    plane("signface2", (0, sign_y + 0.12, 5.9), 7.5, 0.94, sg, (math.radians(90), 0, math.pi))
    # Straßenlaternen (für die Dämmerung)
    for k, y in enumerate((8.0, 32.0, 56.0, 80.0)):
        x = -3.4
        cyl("lamppole", (x, y, 3.0), 0.07, 6.0, pole_m, verts=10)
        box("lamparm", (x + 0.45, y, 5.95), (0.9, 0.08, 0.08), pole_m)
        head = box("lamphead", (x + 0.85, y, 5.85), (0.45, 0.22, 0.1), M("lamphead", (0.9, 0.9, 0.85)))
        S["lamps"].append(head)

    # ---------- Hügel, Wolken ----------
    hill = M("hill", (0.42, 0.58, 0.42), 0.75)
    hill2 = M("hill2", (0.5, 0.64, 0.5), 0.8)
    for k, (x, y, s, m) in enumerate(((-50, 160, 45, hill), (20, 185, 60, hill2), (70, 150, 40, hill), (-95, 100, 50, hill2), (95, 90, 45, hill2))):
        o = F.ellipsoid(f"hillo{k}", Vector((x, y, -s * 0.55)), (s * 1.7, s, s), m, seg=24, rings=12)
    cloud = F.flat_mat("cloud", (0.99, 0.99, 1.0))
    S["clouds"] = []
    for k in range(7):
        cx, cy, cz = R.uniform(-90, 90), R.uniform(140, 220), R.uniform(35, 70)
        for j in range(4):
            o = F.ellipsoid(f"cloud{k}_{j}", Vector((cx + j * 7 - 10, cy + R.uniform(-2, 2), cz + R.uniform(-1.5, 2.5))), (R.uniform(6, 9), 4, R.uniform(3, 5)), cloud, seg=16, rings=8)
            S["clouds"].append(o)
    return S


def sky(day=True):
    w = bpy.data.worlds.new("sky")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    if day:
        e[0].position, e[0].color = 0.0, (0.86, 0.9, 0.95, 1)
        e[1].position, e[1].color = 0.35, (0.5, 0.7, 0.92, 1)
        bg.inputs[1].default_value = 1.0
    else:
        e[0].position, e[0].color = 0.0, (0.95, 0.72, 0.6, 1)
        e[1].position, e[1].color = 0.3, (0.24, 0.3, 0.5, 1)
        bg.inputs[1].default_value = 1.0
    nt.links.new(sep.outputs[2], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], bg.inputs[0])
    # Licht für die Figuren kommt aus der Sonne; der Himmel selbst soll nicht zu stark aufhellen
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    amb = nt.nodes.new("ShaderNodeBackground")
    amb.inputs[0].default_value = (0.75, 0.8, 0.9, 1) if day else (0.25, 0.3, 0.45, 1)
    amb.inputs[1].default_value = 0.3 if day else 0.25
    out = nt.nodes["World Output"]
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sc.collection.objects.link(sun)
    sun.data.angle = math.radians(0.5)
    if day:
        sun.data.energy = 1.7
        sun.data.color = (1.0, 0.97, 0.9)
        sun.rotation_euler = (math.radians(52), math.radians(0), math.radians(-45))
    else:
        sun.data.energy = 0.45
        sun.data.color = (0.75, 0.82, 1.0)
        sun.rotation_euler = (math.radians(75), math.radians(0), math.radians(-60))
    return sun
