# „Ink Pop“-Figuren im Code: großer Kopf, gemalte Augen (Weiß, Iris, Pupille, Glanzpunkt, dicker Lidstrich),
# Brauen, Nase, Mund (Mimik), Haar-Masse mit Strähnen, Jacke, Hände mit Fingern, Hose, Schuhe.
# Starre Teile hängen an einem Skelett (Bone-Parenting) -> Posen/Animation über Knochen.
import bpy, bmesh, math
from mathutils import Vector, Matrix

sc = bpy.context.scene
_M = {}


def ink_mat(name, col, shade=0.68, tint=(0.82, 0.86, 1.0), emit=0.0):
    """2-Ton-Cel-Shading: Licht = Farbe, Schatten = Farbe * shade (leicht kühl)."""
    key = (name, tuple(round(c, 3) for c in col))
    if key in _M:
        return _M[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    nt.links.new(dif.outputs[0], s2r.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    e = ramp.color_ramp.elements
    e[0].position = 0.0
    e[0].color = (col[0] * shade * tint[0], col[1] * shade * tint[1], col[2] * shade * tint[2], 1)
    e[1].position = 0.42
    e[1].color = (*col, 1)
    nt.links.new(s2r.outputs[0], ramp.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(ramp.outputs[0], em.inputs[0])
    if emit:
        em.inputs[1].default_value = 1.0 + emit
    nt.links.new(em.outputs[0], out.inputs[0])
    m["toon"] = 1
    _M[key] = m
    return m


def flat_mat(name, col):
    """Ohne Schattierung (Augenweiß, Lidstrich, Pupille ...)."""
    key = ("flat", name, tuple(round(c, 3) for c in col))
    if key in _M:
        return _M[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*col, 1)
    nt.links.new(em.outputs[0], out.inputs[0])
    m["toon"] = 1
    _M[key] = m
    return m


def link(o, coll=None):
    (coll or sc.collection).objects.link(o)
    return o


def mesh_from_bm(name, bm, mat, smooth=True, subsurf=0):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    o = link(bpy.data.objects.new(name, me))
    o.data.materials.append(mat)
    if subsurf:
        s = o.modifiers.new("sub", "SUBSURF")
        s.levels = s.render_levels = subsurf
    return o


def ellipsoid(name, c, r, mat, seg=32, rings=16, subsurf=0):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1)
    for v in bm.verts:
        v.co = Vector((v.co.x * r[0], v.co.y * r[1], v.co.z * r[2]))
    o = mesh_from_bm(name, bm, mat, subsurf=subsurf)
    o.location = c
    return o


def loft(name, rings, mat, seg=24, cap=True, subsurf=1):
    """rings: [(z, rx, ry, cx, cy)] von unten nach oben -> glatter Schlauch (Rumpf, Ärmel, Beine)."""
    bm = bmesh.new()
    loops = []
    for z, rx, ry, cx, cy in rings:
        loops.append([bm.verts.new((cx + rx * math.cos(2 * math.pi * i / seg), cy + ry * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)])
    for a, b in zip(loops, loops[1:]):
        for i in range(seg):
            bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]))
    if cap:
        bm.faces.new(list(reversed(loops[0])))
        bm.faces.new(loops[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_from_bm(name, bm, mat, subsurf=subsurf)


def limb(name, p0, p1, r0, r1, mat, seg=20, subsurf=1):
    """Schlauch zwischen zwei Punkten (Ärmel/Hosenbein/Finger)."""
    d = (p1 - p0)
    L = d.length
    o = loft(name, [(0, r0, r0, 0, 0), (L * 0.5, (r0 + r1) / 2, (r0 + r1) / 2, 0, 0), (L, r1, r1, 0, 0)], mat, seg=seg, subsurf=subsurf)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    o.matrix_world = Matrix.Translation(p0) @ q.to_matrix().to_4x4()
    return o


def disc(name, c, rx, rz, mat, seg=32):
    """Flache Scheibe, Vorderseite nach -y (Iris, Pupille, Glanz)."""
    bm = bmesh.new()
    ctr = bm.verts.new((0, 0, 0))
    ring = [bm.verts.new((rx * math.cos(2 * math.pi * i / seg), 0, rz * math.sin(2 * math.pi * i / seg))) for i in range(seg)]
    for i in range(seg):
        bm.faces.new((ctr, ring[(i + 1) % seg], ring[i]))
    o = mesh_from_bm(name, bm, mat, smooth=False)
    o.location = c
    return o


def curve_line(name, pts, depth, mat, closed=False):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = depth
    cu.bevel_resolution = 3
    sp = cu.splines.new("NURBS")
    sp.points.add(len(pts) - 1)
    ctr = sum((Vector(p) for p in pts), Vector()) / len(pts)
    for i, p in enumerate(pts):
        sp.points[i].co = (*(Vector(p) - ctr), 1)
    sp.use_endpoint_u = True
    sp.order_u = 3
    sp.use_cyclic_u = closed
    o = link(bpy.data.objects.new(name, cu))
    o.location = ctr
    o.data.materials.append(mat)
    return o


def bone_parent(o, arm, bone):
    mw = o.matrix_basis.copy()
    b = arm.data.bones[bone]
    o.parent = arm
    o.parent_type = "BONE"
    o.parent_bone = bone
    o.matrix_parent_inverse = (arm.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))).inverted()
    o.matrix_basis = mw


# ---------------------------------------------------------------------------
def make_figure(name, skin=(0.88, 0.66, 0.48), hair=(0.07, 0.07, 0.09), jacket=(0.13, 0.17, 0.31), shirt=(0.93, 0.93, 0.9),
                pants=(0.33, 0.35, 0.4), shoes=(0.95, 0.95, 0.95), iris=(0.36, 0.22, 0.12), height=1.72, hair_style="block",
                build=1.0, lower="pants", socks=(0.15, 0.17, 0.25), cap=(0.2, 0.25, 0.4), glasses=False, zipper=True):
    S = height / 1.72
    W = build
    INK = flat_mat("ink", (0.04, 0.035, 0.05))
    m_skin = ink_mat(name + "_skin", skin, shade=0.8, tint=(1.0, 0.8, 0.78))
    m_hair = ink_mat(name + "_hair", hair, shade=0.6, tint=(1.0, 1.0, 1.15))
    m_jacket = ink_mat(name + "_jacket", jacket, shade=0.66, tint=(0.9, 0.95, 1.1))
    m_shirt = ink_mat(name + "_shirt", shirt)
    m_pants = ink_mat(name + "_pants", pants, shade=0.62)
    m_shoes = ink_mat(name + "_shoes", shoes)
    m_sole = ink_mat("sole", (0.2, 0.2, 0.22))
    m_white = flat_mat("eyewhite", (0.98, 0.97, 0.94))
    m_iris = flat_mat(name + "_iris", iris)
    m_pupil = flat_mat("pupil", (0.03, 0.02, 0.02))
    m_mouth = flat_mat("mouth", (0.35, 0.08, 0.1))

    # ---------- Skelett ----------
    ad = bpy.data.armatures.new(name + "_arm")
    arm = link(bpy.data.objects.new(name, ad))
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = ad.edit_bones
    J = {
        "root": ((0, 0, 0), (0, 0.2, 0), None),
        "hips": ((0, 0, 0.95), (0, 0, 1.05), "root"),
        "spine": ((0, 0, 1.05), (0, 0, 1.2), "hips"),
        "chest": ((0, 0, 1.2), (0, 0, 1.36), "spine"),
        "neck": ((0, 0, 1.36), (0, 0, 1.44), "chest"),
        "head": ((0, 0, 1.44), (0, 0, 1.72), "neck"),
    }
    for s, x in (("L", 1), ("R", -1)):
        J[f"upperarm.{s}"] = ((x * 0.2, 0, 1.31), (x * 0.235, 0.01, 1.05), "chest")
        J[f"forearm.{s}"] = ((x * 0.235, 0.01, 1.05), (x * 0.25, -0.02, 0.83), f"upperarm.{s}")
        J[f"hand.{s}"] = ((x * 0.25, -0.02, 0.83), (x * 0.255, -0.03, 0.71), f"forearm.{s}")
        J[f"thigh.{s}"] = ((x * 0.09, 0, 0.93), (x * 0.095, 0, 0.5), "hips")
        J[f"shin.{s}"] = ((x * 0.095, 0, 0.5), (x * 0.095, 0.02, 0.09), f"thigh.{s}")
        J[f"foot.{s}"] = ((x * 0.095, 0.02, 0.09), (x * 0.095, -0.12, 0.03), f"shin.{s}")
        J[f"eye.{s}"] = ((x * 0.042, -0.106, 1.54), (x * 0.042, -0.15, 1.54), "head")
    for bn, (h, t, par) in J.items():
        b = eb.new(bn)
        b.head = Vector(h) * S
        b.tail = Vector(t) * S
        if par:
            b.parent = eb[par]
            b.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"
    arm.data.display_type = "STICK"
    arm.hide_render = True
    P = {}

    def part(o, bone):
        bone_parent(o, arm, bone)
        P.setdefault(bone, []).append(o)
        return o

    v = lambda x, y, z: Vector((x, y, z)) * S

    def face_y(x, z, off=0.0):
        """Vorderseite des Kopfes bei (x, z) – damit Brauen/Mund auf der Haut sitzen."""
        dz = (z - 1.535) / 0.142
        w = 1.0 - 0.2 * max(0.0, -dz) ** 1.8
        fy = 1.0 - 0.12 * max(0.0, -dz)
        q = max(0.0, 1 - (x / (0.112 * w)) ** 2 - dz ** 2)
        return -0.122 * fy * math.sqrt(q) - (0.008 if dz < -0.3 else 0) - off

    # ---------- Kopf ----------
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=24, radius=1)
    for vt in bm.verts:
        x, y, z = vt.co
        w = 1.0 - 0.2 * max(0.0, -z) ** 1.8   # Kinn: etwas eckiger
        fy = 1.0 - 0.12 * max(0.0, -z)          # Kinn leicht nach hinten
        vt.co = Vector((x * 0.112 * w, y * 0.122 * fy - (0.008 if z < -0.3 else 0), z * 0.142))
    head = mesh_from_bm(name + "_head", bm, m_skin, subsurf=1)
    head.location = v(0, 0.0, 1.535)
    part(head, "head")
    for s, x in (("L", 1), ("R", -1)):  # Ohren
        part(ellipsoid(f"{name}_ear{s}", v(x * 0.108, 0.01, 1.53), (0.01 * S, 0.02 * S, 0.03 * S), m_skin), "head")
    nose = ellipsoid(name + "_nose", v(0, -0.122, 1.505), (0.012 * S, 0.014 * S, 0.02 * S), m_skin)
    part(nose, "head")
    part(limb(name + "_neck", v(0, 0.008, 1.33), v(0, 0.008, 1.46), 0.038 * S, 0.036 * S, m_skin), "neck")

    # Augen: Weiß (flach), Iris + Pupille + Glanz an Augen-Knochen, dicker Lidstrich, Unterlid-Strich
    eyes = {}
    for s, x in (("L", 1), ("R", -1)):
        c = v(x * 0.042, -0.106, 1.54)
        w = ellipsoid(f"{name}_white{s}", c, (0.0275 * S, 0.012 * S, 0.032 * S), m_white)
        part(w, "head")
        grp = []
        for nm, r, mt, dz, dy in (("iris", 0.0162, m_iris, -0.001, -0.0125), ("pupil", 0.0084, m_pupil, -0.001, -0.0131), ("glint", 0.0035, m_white, 0.007, -0.0137)):
            o = disc(f"{name}_{nm}{s}", c + v(x * (0.004 if nm == "glint" else 0), dy, dz), r * S, r * 1.1 * S, mt)
            part(o, f"eye.{s}")
            grp.append(o)
        lid = curve_line(f"{name}_lid{s}", [tuple(c + v(x * dx, -0.0105 - 0.004 * (1 - abs(dx) / 0.031), 0.021 + 0.012 * (1 - (dx / 0.031) ** 2))) for dx in (-0.031, -0.016, 0, 0.017, 0.033)],
                         0.0038 * S, INK)
        part(lid, "head")
        low = None
        brow = curve_line(f"{name}_brow{s}", [tuple(v(x * bx, face_y(bx, 1.585 + bz, 0.005), 1.585 + bz)) for bx, bz in ((0.02, -0.002), (0.042, 0.006), (0.064, 0.002))],
                          0.0048 * S, flat_mat(name + "_browc", hair))
        part(brow, "head")
        eyes[s] = dict(white=w, lid=lid, low=low, brow=brow, grp=grp)
    # Mund: Linie + offener Mund (Ellipse, per Skalierung)
    mouth_line = curve_line(name + "_mline", [tuple(v(dx, face_y(dx, 1.462 - 0.002 * (1 - (dx / 0.02) ** 2), 0.003), 1.462 - 0.002 * (1 - (dx / 0.02) ** 2))) for dx in (-0.015, 0, 0.015)], 0.0019 * S, INK)
    part(mouth_line, "head")
    mouth_open = ellipsoid(name + "_mopen", v(0, face_y(0, 1.46, 0.0), 1.46), (0.012 * S, 0.006 * S, 0.004 * S), m_mouth)
    part(mouth_open, "head")

    # Haare: Masse über dem Kopf, vorne/unten weggeschnitten + Strähnen-Büschel
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=24, radius=1)
    for vt in bm.verts:
        x, y, z = vt.co
        vt.co = Vector((x * 0.126, y * 0.138 + 0.006, z * 0.135 + 0.03 * max(0, z) ** 1.5))
    kill = [vt for vt in bm.verts if (vt.co.z < 0.03 and vt.co.y < -0.06) or (vt.co.z < -0.12 and vt.co.y < 0.03) or vt.co.z < -0.62
            or (vt.co.z < 0.0 and vt.co.y < 0.0 and abs(vt.co.x) > 0.06)]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    hair_o = mesh_from_bm(name + "_hair", bm, m_hair, subsurf=1)
    sol = hair_o.modifiers.new("dick", "SOLIDIFY")
    sol.thickness = 0.012
    sol.offset = 1.0
    hair_o.location = v(0, 0, 1.56)
    part(hair_o, "head")
    tufts = ((-0.06, 0.618, -0.4), (-0.02, 0.63, -0.1), (0.025, 0.632, 0.15), (0.065, 0.62, 0.45)) if hair_style in ("block", "long") else ()
    for k, (hx, hz, rot) in enumerate(tufts):
        tuft = ellipsoid(f"{name}_tuft{k}", v(hx, -0.1, 1.0 + hz), (0.036 * S, 0.03 * S, 0.03 * S), m_hair, seg=20, rings=12)
        tuft.rotation_euler = (math.radians(-20), math.radians(rot * 30), 0)
        part(tuft, "head")

    # Haarstile: "block" (Tolle + Strähnen), "short" (kurz, ohne Tolle), "long" (lang bis Schulter, Pony),
    # "bun" (Dutt, ältere Frau), "cap" (Mütze mit Schirm)
    if hair_style == "long":
        back = ellipsoid(name + "_hairback", v(0, 0.04, 1.43), (0.125 * S, 0.075 * S, 0.17 * S), m_hair, seg=28, rings=16)
        part(back, "head")
        for k, hx in enumerate((-0.105, 0.105)):
            side = ellipsoid(f"{name}_hairside{k}", v(hx, -0.01, 1.47), (0.03 * S, 0.06 * S, 0.12 * S), m_hair, seg=20, rings=12)
            part(side, "head")
    if hair_style == "bun":
        bun = ellipsoid(name + "_bun", v(0, 0.09, 1.66), (0.06 * S, 0.055 * S, 0.055 * S), m_hair, seg=24, rings=14)
        part(bun, "head")
    if hair_style == "cap":
        m_cap = ink_mat(name + "_cap", cap, shade=0.6)
        crown = ellipsoid(name + "_capc", v(0, 0.005, 1.63), (0.13 * S, 0.142 * S, 0.075 * S), m_cap, seg=32, rings=16)
        part(crown, "head")
        brim = ellipsoid(name + "_capb", v(0, -0.15, 1.625), (0.1 * S, 0.07 * S, 0.008 * S), m_cap, seg=32, rings=8)
        part(brim, "head")
        band = loft(name + "_capband", [(1.6, 0.128, 0.14, 0, 0.004), (1.625, 0.13, 0.142, 0, 0.004)], flat_mat("capband", (0.9, 0.85, 0.3)), seg=32, cap=False)
        band.scale = (S, S, S)
        part(band, "head")
    if glasses:
        for s_, x in (("L", 1), ("R", -1)):
            ring = curve_line(f"{name}_gl{s_}", [tuple(v(x * 0.042 + 0.03 * math.cos(a), -0.128, 1.54 + 0.026 * math.sin(a))) for a in [i * math.pi / 6 for i in range(12)]], 0.0022 * S, INK, closed=True)
            part(ring, "head")
        part(curve_line(name + "_glb", [tuple(v(-0.012, -0.13, 1.545)), tuple(v(0, -0.133, 1.548)), tuple(v(0.012, -0.13, 1.545))], 0.002 * S, INK), "head")
    if hair_style in ("cap", "bun", "short"):
        tops, spikes = (), ()
    else:
        tops = ((0.0, -0.035, 1.672, 0.075, 0.075, 0.036, -15, 0), (-0.05, -0.02, 1.662, 0.055, 0.065, 0.034, -10, 20), (0.05, -0.02, 1.662, 0.055, 0.065, 0.034, -10, -20),
                (-0.1, -0.03, 1.6, 0.03, 0.05, 0.05, 0, 25), (0.1, -0.03, 1.6, 0.03, 0.05, 0.05, 0, -25))
        spikes = ((-0.085, 1.6, -30, 0.05), (-0.045, 1.615, -12, 0.045), (0.0, 1.62, 6, 0.05), (0.05, 1.615, 18, 0.045), (0.088, 1.6, 32, 0.05))
    # Volumen oben (Tolle) + Strähnen-Spitzen an Seiten und Stirn
    for k, (hx, hy, hz, rx, ry, rz, ax, ay) in enumerate(tops):
        o = ellipsoid(f"{name}_vol{k}", v(hx, hy, hz), (rx * S, ry * S, rz * S), m_hair, seg=24, rings=14)
        o.rotation_euler = (math.radians(ax), math.radians(ay), 0)
        part(o, "head")
    for k, (hx, hz, ang, ln) in enumerate(spikes):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.022 * S, radius2=0.0, depth=ln * S)
        o = mesh_from_bm(f"{name}_spike{k}", bm, m_hair)
        o.location = v(hx, face_y(hx * 0.9, hz, -0.004) - 0.012, hz - ln * 0.3)
        o.rotation_euler = (math.radians(200), math.radians(ang), 0)
        part(o, "head")

    # ---------- Rumpf / Jacke ----------
    torso = loft(name + "_jacket", [(0.9, 0.155, 0.1, 0, 0.0), (1.02, 0.15, 0.098, 0, 0), (1.15, 0.165, 0.105, 0, 0), (1.27, 0.178, 0.108, 0, 0),
                                     (1.33, 0.16, 0.098, 0, 0.005), (1.37, 0.08, 0.06, 0, 0.01)], m_jacket, seg=28)
    torso.scale = (S * W, S * W, S)
    part(torso, "chest")
    collar = loft(name + "_collar", [(1.34, 0.072, 0.062, 0, 0.006), (1.395, 0.066, 0.057, 0, 0.008)], m_jacket, seg=24, cap=False)
    collar.scale = (S, S, S)
    sol = collar.modifiers.new("d", "SOLIDIFY")
    sol.thickness = 0.01
    part(collar, "chest")
    zip_ = None if not zipper else curve_line(name + "_zip", [tuple(v(0, -0.1 - 0.012 * math.sin(math.pi * (z - 0.9) / 0.4), z)) for z in (0.9, 1.0, 1.1, 1.2, 1.27)], 0.0022 * S, INK)
    if zip_:
        part(zip_, "chest")
    pelvis = loft(name + "_pelvis", [(0.76, 0.1, 0.07, 0, 0), (0.8, 0.15, 0.092, 0, 0), (0.95, 0.155, 0.098, 0, 0)], m_pants, seg=24)
    pelvis.scale = (S * W, S * W, S)
    part(pelvis, "hips")

    if lower == "skirt":
        m_legs_up = m_skin
        m_legs_low = ink_mat(name + "_socks", socks, shade=0.6)
        skirt = loft(name + "_skirt", [(0.6, 0.235, 0.17, 0, 0), (0.75, 0.2, 0.135, 0, 0), (0.92, 0.152, 0.097, 0, 0)], m_pants, seg=32)
        skirt.scale = (S * W, S * W, S)
        part(skirt, "hips")
    else:
        m_legs_up = m_legs_low = m_pants

    # ---------- Arme + Hände ----------
    for s, x in (("L", 1), ("R", -1)):
        sh = v(x * 0.19, 0, 1.3)
        el = v(x * 0.235, 0.01, 1.05)
        wr = v(x * 0.25, -0.02, 0.85)
        part(ellipsoid(f"{name}_shoulder{s}", sh - v(x * 0.03, 0, 0.022), (0.044 * S * W, 0.048 * S * W, 0.044 * S), m_jacket), f"upperarm.{s}")
        part(limb(f"{name}_uarm{s}", sh - v(x * 0.01, 0, 0.01), el, 0.052 * S * W, 0.047 * S * W, m_jacket), f"upperarm.{s}")
        part(ellipsoid(f"{name}_elbow{s}", el, (0.047 * S * W, 0.047 * S * W, 0.047 * S), m_jacket), f"forearm.{s}")
        part(limb(f"{name}_farm{s}", el, wr + v(0, 0, 0.01), 0.046 * S * W, 0.043 * S * W, m_jacket), f"forearm.{s}")
        part(limb(f"{name}_cuff{s}", wr + v(0, 0, 0.03), wr - v(0, 0, 0.0), 0.046 * S, 0.046 * S, m_jacket, subsurf=0), f"forearm.{s}")
        # Hand: Handfläche + 4 Finger + Daumen (leicht gekrümmt)
        H = 1.3
        pc = wr + v(x * 0.004, -0.004, -0.055 * H)
        palm = ellipsoid(f"{name}_palm{s}", pc, (0.016 * H * S, 0.035 * H * S, 0.042 * H * S), m_skin, subsurf=0)
        part(palm, f"hand.{s}")
        for k in range(4):
            fy = -0.024 + k * 0.016
            base = pc + v(*[q * H for q in (x * 0.002, fy, -0.036)])
            mid = base + H * v(x * 0.004, -0.004, -0.028 + abs(k - 1.5) * 0.004)
            tip = mid + H * v(x * 0.008, -0.01, -0.02 + abs(k - 1.5) * 0.004)
            part(limb(f"{name}_f{s}{k}a", base, mid, 0.0078 * H * S, 0.0072 * H * S, m_skin, seg=10, subsurf=0), f"hand.{s}")
            part(limb(f"{name}_f{s}{k}b", mid, tip, 0.0072 * H * S, 0.0062 * H * S, m_skin, seg=10, subsurf=0), f"hand.{s}")
            part(ellipsoid(f"{name}_ft{s}{k}", tip, (0.0062 * H * S, 0.0062 * H * S, 0.0062 * H * S), m_skin, seg=10, rings=6), f"hand.{s}")
        tb = pc + v(*[q * H for q in (x * 0.004, -0.03, -0.0)])
        tm = tb + v(*[q * H for q in (x * 0.004, -0.018, -0.022)])
        tt = tm + v(*[q * H for q in (x * 0.002, -0.008, -0.018)])
        part(limb(f"{name}_th{s}a", tb, tm, 0.0095 * H * S, 0.0082 * H * S, m_skin, seg=10, subsurf=0), f"hand.{s}")
        part(limb(f"{name}_th{s}b", tm, tt, 0.0082 * H * S, 0.007 * H * S, m_skin, seg=10, subsurf=0), f"hand.{s}")
        part(ellipsoid(f"{name}_tht{s}", tt, (0.007 * H * S, 0.007 * H * S, 0.007 * H * S), m_skin, seg=10, rings=6), f"hand.{s}")
        # Beine
        hp = v(x * 0.082, 0, 0.93)
        kn = v(x * 0.095, 0, 0.5)
        an = v(x * 0.095, 0.02, 0.1)
        part(limb(f"{name}_thigh{s}", hp, kn, (0.07 if lower == "skirt" else 0.088) * S * W, (0.058 if lower == "skirt" else 0.068) * S * W, m_legs_up), f"thigh.{s}")
        part(ellipsoid(f"{name}_knee{s}", kn, (0.067 * S * W, 0.067 * S * W, 0.067 * S), m_legs_low), f"shin.{s}")
        part(limb(f"{name}_shin{s}", kn, an + v(0, 0, 0.02), 0.065 * S * W, 0.06 * S * W, m_legs_low), f"shin.{s}")
        shoe = ellipsoid(f"{name}_shoe{s}", v(x * 0.095, -0.035, 0.05), (0.056 * S, 0.13 * S, 0.055 * S), m_shoes, subsurf=0)
        part(shoe, f"foot.{s}")
        sole = ellipsoid(f"{name}_sole{s}", v(x * 0.095, -0.035, 0.018), (0.058 * S, 0.132 * S, 0.018 * S), m_sole, subsurf=0)
        part(sole, f"foot.{s}")
    head_parts = P.get("head", []) + P.get("eye.L", []) + P.get("eye.R", []) + P.get("neck", [])
    return dict(arm=arm, name=name, eyes=eyes, mouth=mouth_open, mline=mouth_line, parts=P, S=S, head_parts=head_parts)


# ---------------------------------------------------------------------------
# Posen + Mimik
def rot(f, bone, frame, x=0.0, y=0.0, z=0.0):
    pb = f["arm"].pose.bones[bone]
    pb.rotation_euler = (math.radians(x), math.radians(y), math.radians(z))
    pb.keyframe_insert("rotation_euler", frame=frame)


def relaxed(f, frame):
    for s, k in (("L", 1), ("R", -1)):
        rot(f, f"upperarm.{s}", frame, x=0, z=0)
        rot(f, f"forearm.{s}", frame, x=-12)
        rot(f, f"hand.{s}", frame)


def blink(f, frame, dur=4):
    for s, e in f["eyes"].items():
        for o in [e["white"]] + e["grp"]:
            s0 = o.scale.copy()
            for fr, k in ((frame - 1, 1.0), (frame + 1, 0.06), (frame + dur, 1.0)):
                o.scale = (s0[0], s0[1], s0[2] * k)
                o.keyframe_insert("scale", frame=fr)
            o.scale = s0
        lid = e["lid"]
        z0 = lid.location.z
        for fr, dz in ((frame - 1, 0), (frame + 1, -0.03 * f["S"]), (frame + dur, 0)):
            lid.location.z = z0 + dz
            lid.keyframe_insert("location", frame=fr)
        lid.location.z = z0


def look(f, frame, yaw=0.0, pitch=0.0):
    """Augen schauen: yaw/pitch in Grad (+ = nach links der Figur / hoch). Iris gleitet über das Augenweiß."""
    dx = max(-1.0, min(1.0, yaw / 30.0)) * 0.0085 * f["S"]
    dz = max(-1.0, min(1.0, pitch / 25.0)) * 0.009 * f["S"]
    for s in ("L", "R"):
        pb = f["arm"].pose.bones[f"eye.{s}"]
        pb.location = (-dx, 0.0, dz)  # lokale Knochenachsen: x = Welt -x, z = Welt +z
        pb.keyframe_insert("location", frame=frame)


def lipsync(f, wav, t0, fps, gain=1.0):
    """Mund nach Lautstärke der Sprachdatei öffnen."""
    import wave as _w
    import numpy as _np
    with _w.open(wav) as wf:
        sr = wf.getframerate()
        a = _np.frombuffer(wf.readframes(wf.getnframes()), dtype=_np.int16).astype(float)
    hop = sr // fps
    rms = _np.array([_np.sqrt(_np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    rms = rms / (rms.max() or 1)
    f0 = int(round(t0 * fps)) + 1
    mouth(f, f0 - 2, 0)
    for i in range(0, len(rms), 2):
        mouth(f, f0 + i, min(1.0, (rms[i] ** 0.6) * gain))
    mouth(f, f0 + len(rms) + 2, 0)


def mouth(f, frame, openness):
    m = f["mouth"]
    m.scale = (1.0 + 0.2 * openness, 1.0, max(0.05, openness * 3.2))
    m.keyframe_insert("scale", frame=frame)
    f["mline"].hide_render = openness > 0.15
    f["mline"].keyframe_insert("hide_render", frame=frame)


def brows(f, frame, up=0.0, inner=0.0):
    """up: beide hoch (Überraschung), inner: innen hoch (Sorge/Angst), negativ = böse."""
    S = f["S"]
    for s, e in f["eyes"].items():
        b = e["brow"]
        if "z0" not in e:
            e["z0"] = b.location.z
            e["r0"] = b.rotation_euler.y
        b.location.z = e["z0"] + 0.012 * up * S
        b.rotation_euler.y = e["r0"] + math.radians(14 * inner) * (1 if s == "L" else -1)
        b.keyframe_insert("location", frame=frame)
        b.keyframe_insert("rotation_euler", frame=frame)
