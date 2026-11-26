# Welt für das POV-Video „Was, wenn das dein letzter Flug ist?“ (blender/qissa/flug.py):
# Kabine eines Mittelstreckenflugzeugs bei Nacht (3+3 Sitze, Fenster mit echten Öffnungen, Gepäckfächer mit Klappen,
# Service-Leiste mit Leselampen/Anschnallzeichen, Sauerstoffmasken, Stimmungslicht), draußen Flügel mit Positionslichtern,
# Wolkenmeer, Gewitterwolken mit Blitzen, Landebahn mit Anflug- und Stadtlichtern; Flughafen-Halle bei Morgendämmerung;
# Gebetsraum. Menschen ohne Gesicht (lib.person). Flugzeug-Achse: vorn = +Y, Boden z = 0, Sitzreihe r bei y = r * ROW.
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix
import lib as Q

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "tex")
ROW = 0.81                       # Sitzabstand
SX = {"A": -1.38, "B": -0.92, "C": -0.46, "D": 0.46, "E": 0.92, "F": 1.38}
EYE = 1.17                       # Augenhöhe sitzend
WIN_Z = 1.1                      # Fenstermitte
CAB_Y0, CAB_Y1 = -12.5, 13.0     # Kabine hinten/vorn
ROWS = list(range(-14, 16))
M = {}


def mats():
    if M:
        return M
    M["carpet"] = Q.pbr("carpet", (0.07, 0.08, 0.13), 0.95, var=0.12, scale=40, bump=0.15, bscale=300)
    M["aisle"] = Q.pbr("aisle", (0.12, 0.1, 0.12), 0.95, var=0.1, scale=60, bump=0.1, bscale=300)
    M["wall"] = Q.pbr("wall", (0.78, 0.78, 0.76), 0.55, var=0.02, scale=4, bump=0.01, bscale=40)
    M["panel"] = Q.pbr("panel", (0.86, 0.86, 0.84), 0.45, var=0.015, scale=6)
    M["bin"] = Q.pbr("bin", (0.84, 0.84, 0.83), 0.4, var=0.01, scale=6)
    M["grey"] = Q.pbr("grey", (0.32, 0.33, 0.35), 0.5)
    M["dark"] = Q.pbr("darkplast", (0.05, 0.05, 0.06), 0.4)
    M["metal"] = Q.pbr("seatmetal", (0.45, 0.46, 0.48), 0.35, metal=0.8)
    M["seat"] = Q.pbr("seatfab", (0.07, 0.09, 0.17), 0.95, var=0.12, scale=25, bump=0.25, bscale=220)
    M["seat2"] = Q.pbr("seatleather", (0.05, 0.06, 0.09), 0.55, var=0.05, scale=10)
    M["cover"] = Q.pbr("headcover", (0.82, 0.83, 0.85), 0.95, var=0.05, scale=20, bump=0.2, bscale=250)
    M["seatback"] = Q.pbr("seatback", (0.18, 0.19, 0.21), 0.5, var=0.02, scale=6)
    M["window_frame"] = Q.pbr("winframe", (0.9, 0.9, 0.88), 0.35)
    M["shade"] = Q.pbr("shade", (0.88, 0.88, 0.86), 0.5)
    M["mask"] = Q.pbr("mask", (0.95, 0.78, 0.12), 0.5)
    M["tube"] = Q.pbr("tube", (0.8, 0.82, 0.8), 0.3, alpha=0.45)
    M["wing"] = Q.pbr("wing", (0.55, 0.57, 0.6), 0.35, metal=0.35, var=0.03, scale=3)
    M["wing_dark"] = Q.pbr("wingdark", (0.2, 0.21, 0.23), 0.4, metal=0.3)
    M["cove"] = Q.glow_mat("cove", (0.42, 0.36, 1.0), 2.4)
    M["read"] = Q.glow_mat("readlamp", (1.0, 0.85, 0.6), 14.0)
    M["exit_g"] = Q.glow_mat("floorpath", (0.25, 1.0, 0.45), 3.0)
    M["navR"] = Q.glow_mat("navR", (1.0, 0.05, 0.03), 40.0)
    M["strobe"] = Q.glow_mat("strobe", (1.0, 1.0, 1.0), 0.0)
    M["cloth_b"] = Q.pbr("blanket", (0.15, 0.22, 0.42), 0.95, var=0.1, scale=12, bump=0.2, bscale=60)
    M["cup"] = Q.pbr("cup", (0.95, 0.95, 0.94), 0.4)
    M["can"] = Q.pbr("can", (0.75, 0.08, 0.1), 0.3, metal=0.7)
    M["bag"] = Q.pbr("bag", (0.12, 0.12, 0.14), 0.6, var=0.08, scale=8)
    M["bag2"] = Q.pbr("bag2", (0.45, 0.22, 0.12), 0.7, var=0.1, scale=8)
    M["phone"] = Q.pbr("phonebody", (0.03, 0.03, 0.035), 0.3, metal=0.4)
    return M


def img_mat(name, file, emit=0.0, alpha=False, rough=0.35, base=None):
    """Bild-Material (Bildschirme, Schilder): Emission = Bild (leuchtet), Grundfarbe dunkel bzw. das Bild."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N.get("Principled BSDF")
    tx = N.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(os.path.join(TEX, file), check_existing=True)
    tx.interpolation = "Cubic"
    if base is None:
        L.new(tx.outputs["Color"], b.inputs["Base Color"])
    else:
        b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = rough
    if emit > 0:
        L.new(tx.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    if alpha:
        L.new(tx.outputs["Alpha"], b.inputs["Alpha"])
        m.surface_render_method = "BLENDED"
    m["emit_socket"] = 1
    return m


def emit_strength(m, t, val):
    """Leuchtstärke eines Bild-/Leuchtmaterials zu Zeit t setzen (Schlüsselbild)."""
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    if b is not None:
        s = b.inputs["Emission Strength"]
    else:
        s = next(n for n in nt.nodes if n.type == "EMISSION").inputs["Strength"]
    s.default_value = val
    s.keyframe_insert("default_value", frame=max(1, Q.T(t)))


def plane(name, w, h, mat, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    """Rechteck mit UV (Bild füllt die Fläche), liegt in XY, schaut nach +Z."""
    bm = bmesh.new()
    bm.loops.layers.uv.new("UVMap")   # ohne UV-Lage füllt calc_uvs nichts -> Bild wäre eine Farbe
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5, calc_uvs=True)
    bmesh.ops.scale(bm, vec=(w / (2 * max(abs(v.co.x) for v in bm.verts)), h / (2 * max(abs(v.co.y) for v in bm.verts)), 1), verts=bm.verts)
    o = Q._obj(name, bm, mat, parent=parent)
    o.location = loc
    o.rotation_euler = rot
    o["person"] = 1   # nicht mit join_static verschmelzen (dabei ging die UV-Lage verloren -> Bild leer)
    return o


def merge(name, objs, keep_world=True):
    """Objekte zu EINEM Netz (Weltlage, Materialien übernommen) – Vorlage für verlinkte Kopien."""
    dg = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    mats_ = []
    for o in objs:
        eo = o.evaluated_get(dg)
        me = eo.to_mesh()
        me.transform(o.matrix_world)
        remap = []
        for m in o.data.materials:
            if m not in mats_:
                mats_.append(m)
            remap.append(mats_.index(m))
        n0 = len(bm.faces)
        bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        for f in bm.faces[n0:]:
            f.material_index = remap[f.material_index] if f.material_index < len(remap) else 0
        eo.to_mesh_clear()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats_:
        me.materials.append(m)
    for o in objs:
        bpy.data.objects.remove(o)
    return me


def inst(name, me, loc, rot=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, me)
    Q.link(o)
    o.location = loc
    o.rotation_euler = rot
    if parent is not None:
        o.parent = parent
    return o


# ------------------------------------------------------------------------------------------ Kabinenhülle
WALL = [(1.5, 0.0), (1.64, 0.18), (1.74, 0.45), (1.8, 0.78), (1.82, 1.1), (1.8, 1.38), (1.74, 1.58), (1.68, 1.66)]


def _profile_mesh(name, pts, y0, y1, step, mat, mirror=False):
    bm = bmesh.new()
    ys = [y0 + i * step for i in range(int((y1 - y0) / step) + 1)]
    rows_ = []
    for y in ys:
        rows_.append([bm.verts.new(((-x if mirror else x), y, z)) for x, z in pts])
    for a, b in zip(rows_, rows_[1:]):
        for i in range(len(pts) - 1):
            q = (a[i], a[i + 1], b[i + 1], b[i])
            bm.faces.new(q if mirror else tuple(reversed(q)))
    o = Q._obj(name, bm, mat, smooth=True)
    return o


def window_ys():
    return [r * ROW + 0.16 for r in ROWS if CAB_Y0 + 0.5 < r * ROW < CAB_Y1 - 0.8]


def cabin_shell(shades=None, seed=0):
    """Boden, Seitenwände mit Fensteröffnungen (Boolean), Fensterrahmen + Rollos, Gepäckfächer (Klappen einzeln),
    Service-Leisten, Decke, Stimmungslicht, vorn/hinten Trennwand. Rückgabe: dict mit animierbaren Teilen."""
    mats()
    rnd = random.Random(seed)
    C = {"bins": {}, "psu": {}, "read": [], "cove_lights": [], "lamps": []}
    Q.box("floor", (0, (CAB_Y0 + CAB_Y1) / 2, -0.04), (3.1, CAB_Y1 - CAB_Y0, 0.08), M["carpet"])
    Q.box("aisle_run", (0, (CAB_Y0 + CAB_Y1) / 2, 0.003), (0.42, CAB_Y1 - CAB_Y0, 0.006), M["aisle"])
    for s_ in (-1, 1):
        w = _profile_mesh(f"wall{s_}", WALL, CAB_Y0, CAB_Y1, 0.27, M["wall"], mirror=(s_ < 0))
        sol = w.modifiers.new("sol", "SOLIDIFY")
        sol.thickness = 0.07
        sol.offset = 1.0 if s_ < 0 else -1.0
        # Fensteröffnungen: ein Schneidekörper mit allen Fenstern (Ovale, quer durch die Wand)
        bm = bmesh.new()
        for y in window_ys():
            g = bmesh.ops.create_cone(bm, cap_ends=True, segments=28, radius1=1.0, radius2=1.0, depth=1.0)
            vs = g["verts"]
            bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "Y"))
            bmesh.ops.scale(bm, vec=(0.9, 0.125, 0.18), verts=vs)
            bmesh.ops.translate(bm, verts=vs, vec=(1.8 * s_, y, WIN_Z))
        cut = Q._obj(f"wincut{s_}", bm, None)
        bo = w.modifiers.new("win", "BOOLEAN")
        bo.object = cut
        bo.solver = "EXACT"
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(w.evaluated_get(dg))
        w.modifiers.clear()
        w.data = me
        bpy.data.objects.remove(cut)
        for p in me.polygons:
            p.use_smooth = True
        # Rahmen + Rollo je Fenster
        for k, y in enumerate(window_ys()):
            fr = Q.torus(f"winfr{s_}_{k}", (1.76 * s_, y, WIN_Z), 0.15, 0.014, M["window_frame"], seg=32, rseg=8,
                         scale=(0.9, 1.0, 1.25))
            fr.rotation_euler = (0, math.radians(90 + 6 * s_), 0)
            op = 1.0
            if shades is not None:
                op = shades.get((s_, k), 1.0)
            elif rnd.random() < 0.55:
                op = rnd.choice((0.0, 0.0, 0.3, 0.6))
            if op < 0.98:   # Rollo (oben eingefahren, op = wie weit offen)
                h = 0.38 * (1 - op)
                Q.box(f"shade{s_}_{k}", (1.775 * s_, y, WIN_Z + 0.19 - h / 2), (0.012, 0.27, h), M["shade"])
            Q.box(f"pane{s_}_{k}", (1.86 * s_, y, WIN_Z), (0.004, 0.26, 0.37), Q.pbr("pane", (0.08, 0.1, 0.13), 0.08, alpha=0.18))
        # Gepäckfächer: Körper + Klappen je 2 Reihen (Klappe dreht oben um die Y-Achse)
        Q.box(f"binbody{s_}", (1.34 * s_, (CAB_Y0 + CAB_Y1) / 2, 1.86), (0.68, CAB_Y1 - CAB_Y0, 0.44), M["bin"])
        y = CAB_Y0 + 0.2
        k = 0
        while y + 1.62 < CAB_Y1:
            hinge = Q.empty(f"binhinge{s_}_{k}", (0.985 * s_, y + 0.81, 2.08))
            dr = Q.box(f"bindoor{s_}_{k}", (0.03 * s_, 0, -0.22), (0.035, 1.6, 0.44), M["panel"], parent=hinge, bevel=0.01)
            dr.rotation_euler = (0, math.radians(-10 * s_), 0)
            Q.box(f"binhandle{s_}_{k}", (0.012 * s_, 0, -0.38), (0.02, 0.28, 0.035), M["grey"], parent=hinge)
            hinge["person"] = 1   # bleibt beweglich (nicht verschmelzen)
            C["bins"][(s_, k)] = hinge
            y += 1.62
            k += 1
        # Service-Leiste unter den Fächern (Leselampen, Düsen, Anschnallzeichen, Maskenklappen)
        Q.box(f"psu{s_}", (1.32 * s_, (CAB_Y0 + CAB_Y1) / 2, 1.615), (0.62, CAB_Y1 - CAB_Y0, 0.05), M["panel"])
        Q.box(f"cove{s_}", (0.99 * s_, (CAB_Y0 + CAB_Y1) / 2, 2.085), (0.02, CAB_Y1 - CAB_Y0, 0.012), M["cove"])
    # Decke (leicht gewölbt) + Lichtleisten
    Q.box("ceil", (0, (CAB_Y0 + CAB_Y1) / 2, 2.22), (2.1, CAB_Y1 - CAB_Y0, 0.04), M["panel"])
    for s_ in (-1, 1):
        Q.box(f"ceil_side{s_}", (0.86 * s_, (CAB_Y0 + CAB_Y1) / 2, 2.15), (0.3, CAB_Y1 - CAB_Y0, 0.03), M["panel"],
              rot=(0, math.radians(18 * s_), 0))
    # Trennwände vorn/hinten
    Q.box("bulk_front", (0, CAB_Y1 + 0.05, 1.1), (3.7, 0.1, 2.3), M["panel"])
    Q.box("curtain_front", (0, CAB_Y1 - 0.02, 1.2), (0.6, 0.03, 1.9), Q.pbr("curtain", (0.12, 0.16, 0.32), 0.95, var=0.08, scale=12, bump=0.3, bscale=40))
    Q.box("bulk_back", (0, CAB_Y0 - 0.05, 1.1), (3.7, 0.1, 2.3), M["panel"])
    ex = img_mat("exitsign", "flug_exit.png", emit=3.0)
    plane("exit_front", 0.32, 0.11, ex, loc=(0, CAB_Y1 - 0.01, 2.0), rot=(math.radians(90), 0, 0))
    plane("exit_back", 0.32, 0.11, ex, loc=(0, CAB_Y0 + 0.01, 2.0), rot=(math.radians(90), 0, math.radians(180)))
    # Bodenmarkierung (Fluchtweg) + Stimmungslicht als echte Lampen (Flächenlichter nach oben an die Decke)
    Q.box("floorpath", (-0.24, (CAB_Y0 + CAB_Y1) / 2, 0.008), (0.012, CAB_Y1 - CAB_Y0, 0.004), M["exit_g"])
    for s_ in (-1, 1):
        for k in range(6):
            yy = CAB_Y0 + (k + 0.5) * (CAB_Y1 - CAB_Y0) / 6
            ld = bpy.data.lights.new(f"cove_l{s_}_{k}", "AREA")
            ld.shape = "RECTANGLE"
            ld.size, ld.size_y = 0.1, (CAB_Y1 - CAB_Y0) / 6
            ld.energy = 220
            ld.color = (0.55, 0.45, 1.0)
            ld.use_shadow = False
            lo = bpy.data.objects.new(f"cove_l{s_}_{k}", ld)
            Q.link(lo)
            lo.location = (0.95 * s_, yy, 2.1)
            lo.rotation_euler = (0, math.radians(-150 * s_), 0)
            C["cove_lights"].append(lo)
    return C


# ------------------------------------------------------------------------------------------ Sitze
def seat_proto():
    """Ein Sitz (Kissen, Lehne, Kopfstütze mit Bezug, Armlehne, Beine, hinten Bildschirm-Rahmen + Tablett) als Netz."""
    mats()
    parts = []
    B = Q.box
    parts.append(B("sp_cush", (0, -0.02, 0.48), (0.44, 0.48, 0.12), M["seat"], bevel=0.03))
    bk = B("sp_back", (0, -0.27, 0.9), (0.44, 0.1, 0.74), M["seat"], rot=(math.radians(-10), 0, 0), bevel=0.035)
    parts.append(bk)
    parts.append(B("sp_shell", (0, -0.33, 0.88), (0.45, 0.04, 0.78), M["seatback"], rot=(math.radians(-10), 0, 0), bevel=0.015))
    parts.append(B("sp_cover", (0, -0.235, 1.15), (0.36, 0.035, 0.2), M["cover"], rot=(math.radians(-10), 0, 0), bevel=0.012))
    parts.append(B("sp_tray", (0, -0.36, 0.86), (0.36, 0.02, 0.26), M["seatback"], rot=(math.radians(-10), 0, 0), bevel=0.008))
    parts.append(B("sp_scrn", (0, -0.36, 1.08), (0.24, 0.015, 0.155), M["dark"], rot=(math.radians(-10), 0, 0), bevel=0.006))
    parts.append(B("sp_arm", (0.235, -0.04, 0.66), (0.05, 0.44, 0.05), M["seat2"], bevel=0.015))
    parts.append(B("sp_armpost", (0.235, -0.2, 0.55), (0.04, 0.05, 0.2), M["metal"]))
    for x in (-0.16, 0.16):
        parts.append(B(f"sp_leg{x}", (x, 0.0, 0.2), (0.04, 0.04, 0.4), M["metal"]))
        parts.append(B(f"sp_foot{x}", (x, -0.05, 0.02), (0.04, 0.55, 0.03), M["metal"]))
    parts.append(B("sp_pocket", (0, -0.355, 0.62), (0.34, 0.03, 0.14), M["seat2"], rot=(math.radians(-10), 0, 0)))
    bpy.context.view_layer.update()
    return merge("seat_mesh", parts)


def seats(rows=ROWS, skip=()):
    """Alle Sitze (verlinkte Kopien) + Bildschirme hinten (Flugkarte, leuchtet)."""
    me = seat_proto()
    ife = img_mat("ife", "flug_ife.png", emit=1.6, base=(0.01, 0.01, 0.012), rough=0.2)
    out = {}
    for r in rows:
        y = r * ROW
        if not (CAB_Y0 + 0.6 < y < CAB_Y1 - 0.6):
            continue
        for k, x in SX.items():
            if (r, k) in skip:
                continue
            o = inst(f"seat{r}{k}", me, (x, y, 0))
            out[(r, k)] = o
            sc_ = plane(f"ife{r}{k}", 0.22, 0.135, ife, loc=(x, y - 0.369, 1.08), rot=(math.radians(80), 0, 0))
            sc_["ife"] = 1
    return out


# ------------------------------------------------------------------------------------------ Menschen
CLOTH = [(0.12, 0.12, 0.14), (0.3, 0.32, 0.36), (0.55, 0.52, 0.46), (0.18, 0.22, 0.34), (0.38, 0.12, 0.12), (0.25, 0.3, 0.2),
         (0.7, 0.7, 0.72), (0.45, 0.34, 0.24), (0.08, 0.1, 0.2), (0.6, 0.45, 0.35)]
HAIR = [(0.03, 0.025, 0.02), (0.08, 0.05, 0.03), (0.2, 0.13, 0.07), (0.02, 0.02, 0.02)]
HIJAB = [(0.1, 0.1, 0.12), (0.55, 0.45, 0.4), (0.25, 0.3, 0.45), (0.6, 0.2, 0.25), (0.82, 0.78, 0.7), (0.3, 0.38, 0.32)]


EYE_COL = [(0.12, 0.07, 0.04), (0.06, 0.04, 0.03), (0.2, 0.14, 0.08), (0.1, 0.12, 0.08)]


def face(P, seed=0, sleep=False, brows=None):
    """Gesicht (Nutzer: bei diesem Video dürfen Gesichter sein): Augen mit Iris + Lidern, Brauen, Nase, Mund, Ohren.
    Kopf schaut lokal nach -Y. Rückgabe: dict mit Mund (für Lachen/Schreien) und Augen (für Blinzeln/Schließen)."""
    rnd = random.Random(seed)
    name = P["name"]
    h = P["head"]
    skin = bpy.data.materials.get(f"skin_{name}")
    sk = skin.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value[:3] if skin else (0.55, 0.38, 0.27)
    dark = Q.pbr(f"skind_{name}", tuple(c * 0.78 for c in sk), 0.6)
    white = Q.pbr("eyewhite", (0.85, 0.84, 0.8), 0.25)
    iris = Q.pbr(f"iris{seed % 4}", rnd.choice(EYE_COL), 0.2)
    brow_m = Q.pbr("brow", brows or (0.04, 0.03, 0.025), 0.8)
    lip = Q.pbr(f"lip_{name}", (sk[0] * 0.75, sk[1] * 0.5, sk[2] * 0.48), 0.5)
    mouth_in = Q.pbr("mouthin", (0.12, 0.03, 0.03), 0.6)
    F = {"eyes": [], "lids": []}
    for s_ in (-1, 1):
        x = 0.036 * s_
        e = Q.ball(f"{name}_eye{s_}", (x, -0.088, 0.128), (0.017, 0.012, 0.011), white, parent=h, seg=14)
        i_ = Q.ball(f"{name}_iris{s_}", (x, -0.0985, 0.128), (0.0085, 0.004, 0.0085), iris, parent=h, seg=12)
        lid = Q.ball(f"{name}_lid{s_}", (x, -0.091, 0.133), (0.019, 0.012, 0.0125 if sleep else 0.006), skin, parent=h, seg=12)
        Q.box(f"{name}_brow{s_}", (x, -0.098, 0.153), (0.03, 0.008, 0.006), brow_m, parent=h,
              rot=(0, math.radians(-8 * s_), 0))
        Q.ball(f"{name}_ear{s_}", (0.097 * s_, -0.002, 0.115), (0.012, 0.022, 0.03), skin, parent=h, seg=10)
        F["eyes"] += [e, i_]
        F["lids"].append(lid)
    Q.ball(f"{name}_nose", (0, -0.104, 0.105), (0.012, 0.02, 0.022), dark, parent=h, seg=12)
    Q.ball(f"{name}_nosetip", (0, -0.117, 0.096), (0.011, 0.01, 0.01), skin, parent=h, seg=10)
    m = Q.ball(f"{name}_mouth", (0, -0.097, 0.071), (0.022, 0.008, 0.0045), mouth_in, parent=h, seg=14)
    Q.ball(f"{name}_lipu", (0, -0.099, 0.077), (0.023, 0.007, 0.004), lip, parent=h, seg=12)
    Q.ball(f"{name}_chin", (0, -0.08, 0.035), (0.045, 0.035, 0.03), skin, parent=h, seg=12)
    F["mouth"] = m
    hair = bpy.data.objects.get(f"{name}_hair")
    if hair:   # Haar nicht über das Gesicht: nach hinten/oben
        hair.location = (0, 0.03, 0.152)
        hair.scale = (1.0, 0.92, 0.88)
    return F


def mouth(F, t, open_=0.0):
    """Mund auf (0 zu … 1 weit offen – Schreien) zu Zeit t."""
    m = F["mouth"]
    m.scale = (1.0 + 0.2 * open_, 1.0, 1.0 + 5.0 * open_)
    m.location = (0, -0.097, 0.071 - 0.012 * open_)
    m.keyframe_insert("scale", frame=max(1, Q.T(t)))
    m.keyframe_insert("location", frame=max(1, Q.T(t)))


def blink(F, t0, t1, seed=0):
    rnd = random.Random(seed)
    t = t0 + rnd.uniform(0.5, 2.5)
    for lid in F["lids"]:
        lid.keyframe_insert("scale", frame=max(1, Q.T(t0)))
    while t < t1:
        for lid in F["lids"]:
            for dt, sz in ((0.0, 1.0), (0.05, 2.1), (0.12, 1.0)):
                lid.scale = (1, 1, sz)
                lid.keyframe_insert("scale", frame=max(1, Q.T(t + dt)))
        t += rnd.uniform(2.5, 5.0)


def seat_knees(name):
    """Im engen Flugzeugsitz: Knie nach vorn statt breit (lib.person sitzt im Schneidersitz), kein Kontaktschatten."""
    for o in list(bpy.data.objects):
        if o.name.startswith(f"{name}_blob"):
            bpy.data.objects.remove(o)
    for s_ in (-1, 1):
        k = bpy.data.objects.get(f"{name}_knee{s_}")
        if k:
            k.location = (0.1 * s_, -0.34, -0.15)
            k.scale = (0.7, 1.4, 1.0)
    lap = bpy.data.objects.get(f"{name}_lap")
    if lap:
        lap.scale = (0.6, 1.0, 1.0)


def passenger(name, r, seat, seed=0, kind=None, height=0.88, lean=-6.0):
    """Sitzender Fluggast (ohne Gesicht), schaut nach vorn (+Y). kind: man | woman | hijab | child."""
    rnd = random.Random(seed)
    kind = kind or rnd.choice(("man", "man", "woman", "hijab", "hijab"))
    head = {"man": rnd.choice(("bare", "bare", "cap")), "woman": "bare", "hijab": "khimar", "child": "bare"}[kind]
    P = Q.person(name, (SX[seat], r * ROW - 0.02, 0.5), yaw=math.pi, robe=rnd.choice(CLOTH), skin=rnd.choice(Q.SKINS),
                 wrap=rnd.choice(HIJAB if kind == "hijab" else HAIR), head=head, sit=True, seed=seed,
                 height=0.62 if kind == "child" else height * rnd.uniform(0.95, 1.04))
    seat_knees(name)
    if kind == "woman":   # langes Haar/Zopf hinten
        hm = bpy.data.materials.get(f"wrap_{name}")
        Q.ball(f"{name}_hairlong", (0, 0.06, 0.06), (0.11, 0.08, 0.17), hm, parent=P["head"])
    if head == "cap":
        bpy.data.objects[f"{name}_cap"].scale = (1.05, 1.05, 1.0)
        Q.ball(f"{name}_visor", (0, -0.1, 0.17), (0.08, 0.06, 0.012), bpy.data.materials.get(f"wrap_{name}"), parent=P["head"])
    P["chest"].rotation_euler = (math.radians(lean), 0, 0)
    P["kind"] = kind
    P["face"] = face(P, seed=seed, sleep=(kind == "child"))
    return P


def kf_rot(o, t, rot_deg):
    o.rotation_euler = [math.radians(a) for a in rot_deg]
    o.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))


def kf_loc(o, t, loc):
    o.location = loc
    o.keyframe_insert("location", frame=max(1, Q.T(t)))


def breathe(P, t0, t1, seed=0, amp=1.5, sleep=False):
    """Lebendig sitzen: Atmen (Brust), leichte Kopfbewegungen; schlafend: Kopf zur Seite gesunken, langsam."""
    rnd = random.Random(seed)
    base = P["chest"].rotation_euler.x
    t = t0 + rnd.uniform(0, 1.0)
    while t < t1 + 1:
        a = math.degrees(base) + (amp if int((t - t0) / 1.8) % 2 else -amp * 0.4)
        P["chest"].rotation_euler.x = math.radians(a)
        P["chest"].keyframe_insert("rotation_euler", index=0, frame=max(1, Q.T(t)))
        t += (2.6 if sleep else 1.8) + rnd.uniform(-0.2, 0.3)
    t = t0 + rnd.uniform(0, 2.0)
    while t < t1 + 1:
        if sleep:
            kf_rot(P["neck"], t, (12 + rnd.uniform(-2, 2), 24 + rnd.uniform(-2, 2), 0))
            t += 3.0
        else:
            kf_rot(P["neck"], t, (rnd.uniform(-6, 8), rnd.uniform(-8, 8), rnd.uniform(-14, 14)))
            t += rnd.uniform(1.6, 3.5)


def brace(P, t, seed=0, down=True):
    """Notfall-Haltung: Oberkörper nach vorn auf die Knie, Arme um den Kopf (Kopf runter!)."""
    rnd = random.Random(seed)
    if down:
        kf_rot(P["chest"], t, (48 + rnd.uniform(-6, 6), 0, rnd.uniform(-4, 4)))
        kf_rot(P["neck"], t, (30, 0, 0))
        for nm, s_ in (("L", -1), ("R", 1)):
            kf_rot(P[f"sh.{nm}"], t, (150, 30 * s_, 0))
            kf_rot(P[f"el.{nm}"], t, (-110, 0, 0))
    else:
        kf_rot(P["chest"], t, (-6, 0, 0))
        kf_rot(P["neck"], t, (rnd.uniform(-4, 6), rnd.uniform(-10, 10), 0))
        for nm, s_ in (("L", -1), ("R", 1)):
            kf_rot(P[f"sh.{nm}"], t, (28, 14 * s_, 0))
            kf_rot(P[f"el.{nm}"], t, (-50, 0, 0))


def cabin_people(rows, occupancy=0.72, seed=3, skip=(), kinds=None):
    """Fluggäste in den Reihen `rows` (Plätze in `skip` frei)."""
    rnd = random.Random(seed)
    out = {}
    for r in rows:
        for k in SX:
            if (r, k) in skip or rnd.random() > occupancy:
                continue
            kind = (kinds or {}).get((r, k))
            out[(r, k)] = passenger(f"pax{r}{k}", r, k, seed=seed * 1000 + r * 10 + "ABCDEF".index(k), kind=kind)
    return out


def phone(name, parent, screen_file, loc=(0, 0, 0), rot=(0, 0, 0), emit=2.2, w=0.072, h=0.155):
    """Handy (dünner Körper + leuchtender Bildschirm). Bildschirm schaut lokal nach +Z."""
    mats()
    e = Q.empty(f"{name}_ph", loc, parent, rot=rot)
    Q.box(f"{name}_body", (0, 0, -0.004), (w + 0.006, h + 0.006, 0.008), M["phone"], parent=e, bevel=0.003)
    m = img_mat(f"{name}_scr", screen_file, emit=emit, base=(0.01, 0.01, 0.012), rough=0.15)
    s = plane(f"{name}_screen", w, h, m, loc=(0, 0, 0.0005), parent=e)
    gl = Q.point(f"{name}_glow", (0, 0, 0.05), 0.25 * emit, (0.75, 0.85, 1.0), radius=0.05, parent=e)
    return e, m, s


# ------------------------------------------------------------------------------------------ Sauerstoffmasken
def oxygen_masks(rows, t_drop, seed=0, sides=(-1, 1)):
    """Je Platz eine gelbe Maske am Schlauch: fällt bei t_drop aus der Service-Leiste, federt nach und pendelt.
    Vor dem Fall steckt der Schlauch IN den Gepäckfächern (unsichtbar)."""
    mats()
    rnd = random.Random(seed)
    out = []
    for r in rows:
        y = r * ROW + 0.18
        for s_ in sides:
            for k, x in enumerate((1.38, 0.92, 0.46)):
                L = rnd.uniform(0.36, 0.48)
                piv = Q.empty(f"msk{r}_{s_}_{k}", (x * s_, y, 1.6 + L))
                Q.limb(f"msktube{r}_{s_}_{k}", (0, 0, 0), (0, 0, -L), 0.0028, 0.0028, M["tube"], parent=piv, seg=6)
                Q.cyl(f"mskcup{r}_{s_}_{k}", (0, 0, -L - 0.03), 0.045, 0.07, M["mask"], seg=16, parent=piv, r2=0.03)
                Q.box(f"mskstrap{r}_{s_}_{k}", (0, 0, -L - 0.03), (0.1, 0.004, 0.01), M["tube"], parent=piv)
                piv["person"] = 1
                td = t_drop + rnd.uniform(0, 0.25)
                f0 = max(1, Q.T(td))
                piv.keyframe_insert("location", frame=f0)
                for dt, dz in ((0.18, -L - 0.06), (0.3, -L + 0.05), (0.42, -L - 0.02), (0.55, -L)):
                    piv.location = (x * s_, y, 1.6 + L + dz)
                    piv.keyframe_insert("location", frame=max(1, Q.T(td + dt)))
                # pendeln (gedämpft), danach im Takt der Erschütterung weiter schwingen
                amp, ph = rnd.uniform(14, 24), rnd.uniform(0, 6.28)
                t = td + 0.3
                while t < td + 40:
                    a = amp * math.exp(-(t - td) / 6.0) + 4
                    piv.rotation_euler = (math.radians(a * math.sin(ph + (t - td) * 4.2)), math.radians(0.6 * a * math.cos(ph + (t - td) * 3.1)), 0)
                    piv.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))
                    t += 0.12
                out.append(piv)
    return out


# ------------------------------------------------------------------------------------------ draußen: Flügel, Wolken, Gewitter
def wing(side=-1):
    """Linker Flügel (vom Fensterplatz A aus zu sehen): gepfeilt, leichte V-Form, Triebwerk, Winglet mit Positionslicht.
    Bleibt am Flugzeug (bewegt sich nicht mit der Welt)."""
    mats()
    bm = bmesh.new()
    root_le, root_te = Vector((1.95 * side, 3.2, -0.45)), Vector((1.95 * side, -3.4, -0.35))
    tip_le, tip_te = Vector((16.5 * side, -6.0, 0.75)), Vector((16.5 * side, -8.2, 0.82))
    n = 14
    top, bot = [], []
    for i in range(n + 1):
        u = i / n
        le, te = root_le.lerp(tip_le, u), root_te.lerp(tip_te, u)
        th = 0.42 * (1 - u) + 0.1 * u
        for j in range(9):
            v = j / 8
            p = le.lerp(te, v)
            z = th * 4 * v * (1 - v) * (1.3 if v < 0.35 else 1.0)
            top.append(bm.verts.new((p.x, p.y, p.z + z * 0.5)))
            bot.append(bm.verts.new((p.x, p.y, p.z - z * 0.25)))
    for i in range(n):
        for j in range(8):
            a, b, c, d = i * 9 + j, i * 9 + j + 1, (i + 1) * 9 + j + 1, (i + 1) * 9 + j
            q = (top[a], top[b], top[c], top[d])
            bm.faces.new(q if side < 0 else tuple(reversed(q)))
            q = (bot[a], bot[d], bot[c], bot[b])
            bm.faces.new(q if side < 0 else tuple(reversed(q)))
    o = Q._obj("wing", bm, M["wing"], smooth=True)
    Q.box("flap", (9.0 * side, -6.0, 0.08), (11.5, 0.5, 0.04), M["wing_dark"], rot=(0, math.radians(-4 * side), math.radians(-24 * side)))
    # Triebwerk unter dem Flügel
    eng = Q.cyl("engine", (5.6 * side, 1.6, -1.55), 1.0, 3.6, M["wing"], seg=32, rot=(math.radians(90), 0, 0), r2=0.85)
    Q.cyl("engine_in", (5.6 * side, 3.41, -1.55), 0.9, 0.02, M["dark"], seg=32, rot=(math.radians(90), 0, 0))
    Q.box("pylon", (5.6 * side, 0.6, -0.7), (0.25, 3.0, 0.9), M["wing"])
    # Winglet + Positionslicht (links rot) + Blitzlicht (weiß, blinkt)
    Q.box("winglet", (16.6 * side, -7.4, 1.6), (0.08, 1.6, 1.7), M["wing"], rot=(0, math.radians(-8 * side), 0))
    Q.ball("navlight", (16.55 * side, -6.2, 0.82), 0.07, M["navR"], seg=12)
    nav = Q.point("navlight_l", (16.6 * side, -6.2, 0.9), 220, (1.0, 0.08, 0.05), radius=0.05)
    sb = Q.ball("strobe", (16.6 * side, -8.0, 0.88), 0.06, M["strobe"], seg=12)
    stl = Q.point("strobe_l", (16.6 * side, -8.0, 1.1), 0, (1.0, 1.0, 1.0), radius=0.05)
    return {"wing": o, "engine": eng, "strobe_mat": M["strobe"], "strobe_light": stl, "nav": nav}


def strobe(W, t0, t1, every=1.15):
    """Weißes Blitzlicht am Flügel: kurzes Doppel-Blitzen."""
    t = t0 + 0.3
    while t < t1:
        for dt, v, e in ((0.0, 0.0, 0), (0.02, 120.0, 4000), (0.08, 0.0, 0), (0.16, 120.0, 4000), (0.22, 0.0, 0)):
            emit_strength(W["strobe_mat"], t + dt, v)
            W["strobe_light"].data.energy = e
            W["strobe_light"].data.keyframe_insert("energy", frame=max(1, Q.T(t + dt)))
        t += every


def cloud_mat(name="cloud", dark=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.32, 0.34, 0.4, 1) if dark else (0.8, 0.82, 0.88, 1)
    b.inputs["Roughness"].default_value = 1.0
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.035
    nz.inputs["Detail"].default_value = 6.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].position = 0.38
    cr.color_ramp.elements[1].position = 0.7
    L.new(nz.outputs["Fac"], cr.inputs["Fac"])
    mx = N.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    L.new(cr.outputs["Color"], mx.inputs["Factor"])
    mx.inputs[6].default_value = (0.25, 0.28, 0.36, 1) if not dark else (0.08, 0.09, 0.12, 1)
    mx.inputs[7].default_value = (0.85, 0.88, 0.95, 1) if not dark else (0.4, 0.42, 0.5, 1)
    L.new(mx.outputs[2], b.inputs["Base Color"])
    em = b.inputs["Emission Color"]
    em.default_value = (0.75, 0.8, 1.0, 1)
    b.inputs["Emission Strength"].default_value = 0.0
    return m


def cloud_sea(world, z=-70.0, size=900.0, seed=0):
    """Wolkenmeer unter dem Flugzeug: Höhenfeld mit Rauschen (Kuppen), vom Mond beleuchtet."""
    from mathutils import noise
    bm = bmesh.new()
    n = 120
    bmesh.ops.create_grid(bm, x_segments=n, y_segments=n, size=size / 2)
    for v in bm.verts:
        p = v.co
        h = noise.fractal(Vector((p.x * 0.012 + seed, p.y * 0.012, 0.3)), 0.55, 2.1, 4)
        h2 = noise.noise(Vector((p.x * 0.05, p.y * 0.05 + seed, 1.7)))
        v.co.z = 14 * max(-0.4, h) + 3 * h2
    o = Q._obj("cloudsea", bm, cloud_mat(), smooth=True)
    o.location = (0, 0, z)
    o.parent = world
    o.visible_shadow = False
    return o


def storm_clouds(world, cam_side=-1, seed=1, n=46, spread=(260, 900)):
    """Gewittertürme rings um das Flugzeug (dunkle Klumpen), durch die man fliegt."""
    rnd = random.Random(seed)
    m = cloud_mat("stormcloud", dark=True)
    m.node_tree.nodes.get("Principled BSDF").inputs["Emission Strength"].default_value = 0.12
    out = []
    for k in range(n):
        x = rnd.uniform(18, 140) * rnd.choice((cam_side, cam_side, -cam_side))
        y = rnd.uniform(-spread[0], spread[1])
        z = rnd.uniform(-60, 30)
        r = rnd.uniform(14, 45)
        o = Q.ball(f"storm{k}", (x, y, z), (r, r * rnd.uniform(0.8, 1.3), r * rnd.uniform(0.6, 1.1)), m, seg=20)
        o.parent = world
        o.visible_shadow = False
        out.append(o)
    return out, m


def lightning(t, lights, cloud_m, world_bg=None, strength=1.0, seed=0, base=0.0):
    """Blitz: kurzes zweifaches Aufflackern (Licht draußen + Wolken leuchten von innen + Himmel)."""
    rnd = random.Random(seed)
    seq = ((0.0, 0.0), (0.03, 1.0), (0.09, 0.15), (0.14, 0.8), (0.26, 0.05), (0.5, 0.0))
    for dt, v in seq:
        for L_, e in lights:
            L_.data.energy = e * v * strength
            L_.data.keyframe_insert("energy", frame=max(1, Q.T(t + dt)))
        emit_strength(cloud_m, t + dt, base + 2.5 * v * strength)
        if world_bg is not None:
            world_bg.inputs["Strength"].default_value = 1.0 + 6.0 * v * strength
            world_bg.inputs["Strength"].keyframe_insert("default_value", frame=max(1, Q.T(t + dt)))


def night_world(moon=True, stars=True):
    w = Q.world_sky("night")
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    if moon:
        Q.sun("moon", (58, 0, -35), 0.9, (0.65, 0.72, 1.0), angle=1.0)
    return bg


def city_lights(world, n=5000, area=(3000, 3000), z=0.0, seed=4, center=(0, 0)):
    """Stadtlichter am Boden (ein Netz aus winzigen leuchtenden Flächen, warm/kalt gemischt), Straßenzüge als Linien."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    warm = Q.glow_mat("citywarm", (1.0, 0.62, 0.25), 10.0)
    cold = Q.glow_mat("citycold", (0.8, 0.9, 1.0), 8.0)
    me_faces = []
    streets = [(rnd.uniform(-area[0] / 2, area[0] / 2), rnd.uniform(0, math.pi)) for _ in range(40)]
    for k in range(n):
        if k % 3 == 0:   # Straßen
            sx, ang = rnd.choice(streets)
            d = rnd.uniform(-area[1] / 2, area[1] / 2)
            x, y = center[0] + sx + math.cos(ang) * d, center[1] + math.sin(ang) * d
        else:
            x, y = center[0] + rnd.gauss(0, area[0] / 4), center[1] + rnd.gauss(0, area[1] / 4)
        s = rnd.uniform(1.2, 3.0)
        vs = [bm.verts.new((x - s, y - s, z)), bm.verts.new((x + s, y - s, z)), bm.verts.new((x + s, y + s, z)), bm.verts.new((x - s, y + s, z))]
        f = bm.faces.new(vs)
        f.material_index = 0 if rnd.random() < 0.75 else 1
    o = Q._obj("city", bm, warm)
    o.data.materials.append(cold)
    o.parent = world
    o.visible_shadow = False
    return o


def runway(world, y0=0.0, length=3200, z=0.0):
    """Landebahn (dunkler Streifen, Mittellinie), Randfeuer weiß, Schwelle grün, Anflugbefeuerung (Lichterbalken vor der Bahn)."""
    mats()
    asphalt = Q.pbr("asphalt", (0.05, 0.05, 0.055), 0.8, var=0.1, scale=0.05)
    grass = Q.pbr("grass_night", (0.015, 0.02, 0.015), 1.0, var=0.2, scale=0.01)
    g = Q.box("ground", (0, y0 + length / 2, z - 0.05), (6000, 9000, 0.1), grass)
    g.parent = world
    g.visible_shadow = False
    r = Q.box("runway", (0, y0 + length / 2, z), (45, length, 0.04), asphalt)
    r.parent = world
    white = Q.glow_mat("rwlight", (1.0, 0.95, 0.85), 30.0)
    green = Q.glow_mat("thrlight", (0.2, 1.0, 0.35), 30.0)
    bm = bmesh.new()

    def lamp(x, y, s=0.5, mi=0):
        vs = [bm.verts.new((x - s, y - s, z + 0.3)), bm.verts.new((x + s, y - s, z + 0.3)), bm.verts.new((x + s, y + s, z + 0.3)),
              bm.verts.new((x - s, y + s, z + 0.3))]
        f = bm.faces.new(vs)
        f.material_index = mi
    for k in range(int(length / 60)):
        y = y0 + k * 60
        lamp(-23, y)
        lamp(23, y)
        lamp(0, y + 30, 0.35)
    for x in range(-20, 21, 3):
        lamp(x, y0, 0.5, 1)
    for k in range(1, 30):   # Anflug-Lichterbalken
        y = y0 - k * 30
        for x in range(-8, 9, 2):
            lamp(x, y, 0.6)
    lo = Q._obj("rwlights", bm, white)
    lo.data.materials.append(green)
    lo.parent = world
    lo.visible_shadow = False
    return r


# ------------------------------------------------------------------------------------------ Terminal (Morgendämmerung)
def terminal(length=90.0, seed=2):
    """Lange, leere Abflughalle: Glasfront links mit Sonnenaufgang + Flugzeugen draußen, Sitzreihen, Teppich/Steinboden mit
    Spiegelung, Säulen, Abflugtafel, Schilder (Gate, Gebetsraum). Gehweg entlang +Y bei x = 0."""
    mats()
    rnd = random.Random(seed)
    floor = Q.pbr("termfloor", (0.55, 0.55, 0.56), 0.18, var=0.04, scale=0.4, bump=0.01, bscale=2)
    Q.box("tfloor", (0, length / 2 - 10, -0.05), (40, length + 40, 0.1), floor)
    ceil = Q.pbr("termceil", (0.85, 0.85, 0.86), 0.6)
    Q.box("tceil", (0, length / 2 - 10, 7.0), (40, length + 40, 0.2), ceil)
    wallm = Q.pbr("termwall", (0.7, 0.7, 0.68), 0.5)
    Q.box("twall_r", (9.0, length / 2 - 10, 3.5), (0.3, length + 40, 7.0), wallm)
    frame = Q.pbr("glassframe", (0.2, 0.21, 0.23), 0.3, metal=0.8)
    glass = Q.pbr("glass", (0.6, 0.7, 0.8), 0.02, alpha=0.08)
    Q.box("tglass", (-9.0, length / 2 - 10, 3.5), (0.05, length + 40, 7.0), glass)
    for k in range(int(length / 4) + 10):
        Q.box(f"mullion{k}", (-9.0, -10 + k * 4.0, 3.5), (0.12, 0.12, 7.0), frame)
    for z in (2.4, 4.8):
        Q.box(f"transom{z}", (-9.0, length / 2 - 10, z), (0.1, length + 40, 0.1), frame)
    col = Q.pbr("column", (0.78, 0.78, 0.8), 0.35)
    for k in range(int(length / 12) + 2):
        Q.cyl(f"tcol{k}", (-5.5, -6 + k * 12, 3.5), 0.4, 7.0, col, seg=24)
    # Sitzreihen (verbundene Sitze, leer) zwischen Säulen und Glas
    seat = Q.pbr("tseat", (0.12, 0.13, 0.15), 0.5)
    for k in range(int(length / 12) + 1):
        y = -2 + k * 12
        for j in range(2):
            x = -7.4 + j * 1.5
            Q.box(f"tbench{k}_{j}", (x, y, 0.45), (0.5, 5.0, 0.08), seat)
            Q.box(f"tback{k}_{j}", (x + 0.24, y, 0.75), (0.06, 5.0, 0.6), seat, rot=(0, math.radians(-8), 0))
            for i in range(9):
                Q.box(f"tarm{k}_{j}_{i}", (x, y - 2.4 + i * 0.6, 0.6), (0.5, 0.04, 0.03), frame)
    # Lichtbänder an der Decke
    lm = Q.glow_mat("termlight", (1.0, 0.97, 0.9), 6.0)
    for k in range(int(length / 3) + 10):
        Q.box(f"tlight{k}", (2.5, -10 + k * 3.0, 6.88), (0.25, 2.2, 0.02), lm)
    # Abflugtafel, Gate-Schild, Gebetsraum-Schild (rechts an der Wand, am Ende)
    plane("tboard", 3.2, 1.6, img_mat("board", "flug_board.png", emit=2.2, base=(0.02, 0.02, 0.03)),
          loc=(8.84, 18.0, 3.6), rot=(math.radians(90), 0, math.radians(-90)))
    plane("tgate", 1.8, 0.6, img_mat("gate", "flug_gate.png", emit=1.5), loc=(0.0, 30.0, 5.4), rot=(math.radians(90), 0, 0))
    plane("tgate2", 1.8, 0.6, bpy.data.materials["gate"], loc=(0.0, 30.02, 5.4), rot=(math.radians(90), 0, math.radians(180)))
    # Flugzeuge draußen (Silhouetten mit Lichtern) + Vorfeld
    apron = Q.pbr("apron", (0.32, 0.32, 0.33), 0.6, var=0.05, scale=0.05)
    Q.box("apron", (-80, length / 2, -0.3), (140, length + 300, 0.2), apron)
    body = Q.pbr("acbody", (0.82, 0.83, 0.86), 0.35)
    for k, (x, y, yaw) in enumerate(((-30, 6, 90), (-34, 34, 90), (-60, 58, 60))):
        e = Q.empty(f"ac{k}", (x, y, 0), rot=(0, 0, math.radians(yaw)))
        Q.cyl(f"acf{k}", (0, 0, 3.6), 2.0, 34, body, seg=28, rot=(math.radians(90), 0, 0), parent=e)
        Q.ball(f"acn{k}", (0, 17, 3.6), (2.0, 3.0, 2.0), body, parent=e)
        Q.box(f"acw{k}", (0, 1, 2.6), (34, 5, 0.4), body, parent=e)
        Q.box(f"act{k}", (0, -16, 7), (0.4, 4, 6), body, rot=(math.radians(-20), 0, 0), parent=e)
        Q.box(f"acs{k}", (0, -16, 4), (11, 3, 0.3), body, parent=e)
    return {"floor": floor}


def dawn_light():
    """Sonnenaufgang draußen vor der Glasfront (links, -X): Morgenrot-Himmel + tiefe, warme Sonne."""
    w = Q.world_sky("dawn")
    s = Q.sun("sun", (84, 0, 98), 2.6, (1.0, 0.62, 0.36), angle=1.5, shadow=True)
    return w, s


# ------------------------------------------------------------------------------------------ Gebetsraum
def prayer_room(seed=5):
    """Kleiner, ruhiger Gebetsraum: Teppich, Regal für Schuhe, Qibla-Schild, gerollte Gebetsteppiche, warmes Licht.
    Eingang bei y = 0 (Tür), Raum nach +Y bis y = 5,5; Qibla an der Stirnwand (+Y)."""
    mats()
    wallm = Q.pbr("prwall", (0.86, 0.83, 0.77), 0.8, var=0.02, scale=3)
    carpet = Q.pbr("prcarpet", (0.18, 0.32, 0.26), 0.95, var=0.08, scale=8, bump=0.2, bscale=200)
    Q.box("prfloor", (0, 2.75, -0.05), (4.4, 5.9, 0.1), carpet)
    for x in (-2.2, 2.2):
        Q.box(f"prw{x}", (x, 2.75, 1.4), (0.1, 5.9, 2.8), wallm)
    Q.box("prw_front", (0, 5.7, 1.4), (4.4, 0.1, 2.8), wallm)
    Q.box("prw_back_l", (-1.45, -0.2, 1.4), (1.5, 0.1, 2.8), wallm)
    Q.box("prw_back_r", (1.45, -0.2, 1.4), (1.5, 0.1, 2.8), wallm)
    Q.box("prw_top", (0, -0.2, 2.5), (1.4, 0.1, 0.6), wallm)
    Q.box("prceil", (0, 2.75, 2.85), (4.4, 5.9, 0.1), Q.pbr("prceil", (0.9, 0.9, 0.88), 0.8))
    # Streifen-Muster im Teppich (Reihen), Qibla-Schild, Lampen
    stripe = Q.pbr("prstripe", (0.55, 0.45, 0.25), 0.95)
    for k in range(5):
        Q.box(f"prrow{k}", (0, 1.2 + k * 0.95, 0.002), (4.3, 0.05, 0.004), stripe)
    plane("prqibla", 0.6, 0.31, img_mat("qibla", "flug_qibla.png", emit=0.25), loc=(0, 5.64, 1.9), rot=(math.radians(90), 0, 0))
    plane("prsign", 0.9, 0.29, img_mat("prsign", "flug_gebetsraum.png", emit=0.4), loc=(1.1, -0.26, 2.1), rot=(math.radians(90), 0, 0))
    shelf = Q.pbr("shelf", (0.45, 0.32, 0.2), 0.6, var=0.1, scale=4)
    Q.box("prshelf", (-1.85, 0.6, 0.45), (0.4, 1.4, 0.9), shelf)
    for k in range(4):   # gerollte Teppiche im Regal
        Q.cyl(f"prroll{k}", (-1.85, 0.2 + k * 0.28, 0.98), 0.07, 0.38, Q.pbr(f"roll{k}", ((0.5, 0.12, 0.12), (0.12, 0.3, 0.45), (0.55, 0.45, 0.2), (0.2, 0.4, 0.25))[k], 0.9),
              seg=14, rot=(0, math.radians(90), 0))
    for k, y in enumerate((1.4, 3.6)):
        Q.point(f"prlamp{k}", (0, y, 2.6), 160, (1.0, 0.82, 0.6), radius=0.3)
        Q.cyl(f"prlampm{k}", (0, y, 2.78), 0.25, 0.06, Q.glow_mat(f"prl{k}", (1.0, 0.88, 0.7), 4.0), seg=24)
    return {"carpet": carpet}


def prayer_rug(name, loc, yaw=0.0):
    """Gebetsteppich, der sich ausrollt: flacher Teppich (Skalierung in Länge) + Rolle, die nach vorn wandert."""
    rug_m = Q.pbr("rug", (0.55, 0.1, 0.12), 0.95, var=0.12, scale=14, bump=0.25, bscale=150)
    edge = Q.pbr("rugedge", (0.85, 0.7, 0.35), 0.8)
    e = Q.empty(f"{name}_root", loc, rot=(0, 0, yaw))
    flat = Q.empty(f"{name}_flat", (0, 0, 0), e)
    Q.box(f"{name}_mat", (0, 0.55, 0.006), (0.66, 1.1, 0.012), rug_m, parent=flat)
    Q.box(f"{name}_mih", (0, 0.92, 0.0125), (0.3, 0.3, 0.002), edge, parent=flat)
    for x in (-0.31, 0.31):
        Q.box(f"{name}_edge{x}", (x, 0.55, 0.0125), (0.03, 1.1, 0.002), edge, parent=flat)
    roll = Q.cyl(f"{name}_roll", (0, 0, 0.05), 0.05, 0.66, rug_m, seg=16, rot=(0, math.radians(90), 0), parent=e)
    e["person"] = 1
    return {"root": e, "flat": flat, "roll": roll}


def airport_side(world, seed=6):
    """Links neben der Landebahn: Rollwege mit blauen Randfeuern + grüner Mittellinie, Vorfeld-Masten, Gebäude mit hellen Fenstern."""
    rnd = random.Random(seed)
    blue = Q.glow_mat("taxiblue", (0.2, 0.35, 1.0), 25.0)
    green = Q.glow_mat("taxigreen", (0.2, 1.0, 0.4), 18.0)
    amber = Q.glow_mat("apronlight", (1.0, 0.75, 0.4), 40.0)
    win = Q.glow_mat("bldgwin", (1.0, 0.85, 0.6), 5.0)
    bm = bmesh.new()

    def quad(x, y, z, s, mi):
        vs = [bm.verts.new((x - s, y - s, z)), bm.verts.new((x + s, y - s, z)), bm.verts.new((x + s, y + s, z)), bm.verts.new((x - s, y + s, z))]
        bm.faces.new(vs).material_index = mi
    for xl in (-70, -78, -150, -158):
        for k in range(110):
            quad(xl, -400 + k * 30, 0.3, 0.35, 0)
    for xl in (-74, -154):
        for k in range(220):
            quad(xl, -400 + k * 15, 0.15, 0.25, 1)
    for k in range(40):   # Verbindungswege schräg
        y0 = rnd.uniform(-200, 3000)
        for j in range(12):
            quad(-30 - j * 3.5, y0 + j * 4, 0.3, 0.3, 0)
    for k in range(18):   # Vorfeld-Masten
        quad(-260 + rnd.uniform(-30, 30), rnd.uniform(-200, 3000), 18.0, 0.8, 2)
    o = Q._obj("airport_l", bm, blue)
    o.data.materials.append(green)
    o.data.materials.append(amber)
    o.parent = world
    o.visible_shadow = False
    bm = bmesh.new()
    wall = Q.pbr("bldg", (0.08, 0.085, 0.1), 0.7)
    for k in range(8):   # Hallen/Terminal-Gebäude mit Fensterbändern
        x, y = rnd.uniform(-420, -300), rnd.uniform(-100, 2800)
        b_ = Q.box(f"bldg{k}", (x, y, 8), (rnd.uniform(40, 90), rnd.uniform(60, 200), 16), wall)
        b_.parent = world
        b_.visible_shadow = False
        Q.box(f"bldgw{k}", (x + 0.1 + b_.dimensions.x / 2 * 0 + (rnd.uniform(-1, 1)), y, 10), (b_.dimensions.x + 0.2, b_.dimensions.y * 0.9, 1.2), win).parent = world
    return o
