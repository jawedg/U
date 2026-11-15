# Zusatz-Sets für Futaba v3: Treppe in der Küche (nach oben) und Obergeschoss mit Blick auf die überflutete Straße.
import bpy, math, os, random
from mathutils import Vector
import figure as F
import livingroom as LR

R = random.Random(33)


def stairs():
    """Treppe hinter der Küchentür: startet bei y=-2.95, steigt Richtung -y. Gibt Infos für Kamera/Hand zurück."""
    Y0 = LR.Y0
    for n in ("k_back", "k_counter", "k_cab", "k_kettle", "k_ceil"):
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = True
    wood = LR.soft("stairwood", (0.62, 0.43, 0.26))
    dark = LR.soft("stairdark", (0.42, 0.28, 0.17))
    wallm = LR.painted("wallcream", "wall_cream.png", scale=1.4)
    white = LR.soft("offwhite", (0.94, 0.93, 0.9), shade=0.78)
    n, rise, run = 13, 0.2, 0.24
    x0, x1 = 0.72, 1.62
    y_start = Y0 - 0.35
    for i in range(n):
        y = y_start - i * run
        z = (i + 1) * rise
        LR.box(f"step{i}", ((x0 + x1) / 2, y - run / 2, z - 0.025), (x1 - x0, run + 0.02, 0.05), wood, bevel=0.006)
        LR.box(f"riser{i}", ((x0 + x1) / 2, y, z - rise / 2), (x1 - x0, 0.02, rise), white)
    L = n * run
    # Wange + Handlauf rechts
    ang = math.atan2(n * rise, L)
    mid = Vector(((x1 + 0.03), y_start - L / 2, n * rise / 2))
    LR.box("stringer", tuple(mid), (0.05, L / math.cos(ang) + 0.1, 0.22), dark, rot=(ang, 0, 0))
    rail_h = 0.85
    rail_mid = mid + Vector((0.0, 0.0, rail_h))
    LR.box("handrail", tuple(rail_mid), (0.05, L / math.cos(ang) + 0.2, 0.045), wood, rot=(ang, 0, 0), bevel=0.01)
    for i in range(0, n, 2):
        y = y_start - i * run - run / 2
        z = (i + 1) * rise
        LR.cyl("baluster", (x1 + 0.03, y, z + rail_h / 2), 0.016, rail_h, white, verts=8)
    # Treppenhaus-Wände, Decke mit Öffnung, Fenster mit Licht von oben
    LR.box("sw_left", (x0 - 0.06, y_start - L / 2, 2.6), (0.1, L + 1.0, 5.2), wallm)
    LR.box("sw_back", ((x0 + x1) / 2 + 0.5, y_start - L - 0.5, 2.6), (2.4, 0.1, 5.2), wallm)
    LR.box("sw_right", (x1 + 1.0, y_start - L / 2, 2.6), (0.1, L + 1.0, 5.2), wallm)
    LR.box("sw_ceilfront", ((x0 + x1) / 2 + 0.5, y_start + 0.1, 2.5), (2.4, 0.6, 0.1), white)
    LR.box("landing", ((x0 + x1) / 2, y_start - L - 0.3, n * rise - 0.025), (x1 - x0 + 0.6, 0.6, 0.05), wood)
    win = LR.box("sw_window", (x0 - 0.0, y_start - L * 0.7, 3.4), (0.04, 0.7, 0.9), F.flat_mat("stairwin", (0.92, 0.95, 1.0)))
    lt = bpy.data.objects.new("stairlight", bpy.data.lights.new("stairlight", "AREA"))
    bpy.context.scene.collection.objects.link(lt)
    lt.data.energy = 90
    lt.data.size = 1.2
    lt.location = ((x0 + x1) / 2, y_start - L * 0.6, 4.6)
    for i in range(4):  # ein paar Schuhe/Kram unten
        LR.box(f"shoe{i}", (x0 + 0.12 + i * 0.18, y_start + 0.18, 0.04), (0.1, 0.24, 0.08), LR.soft(f"shoe{i % 2}", ((0.8, 0.3, 0.3), (0.2, 0.25, 0.4))[i % 2]), bevel=0.02)
    return dict(x0=x0, x1=x1, y_start=y_start, run=run, rise=rise, n=n, rail_h=rail_h, top_y=y_start - L, top_z=n * rise)


def upstairs(O=Vector((60, 0, 0))):
    """Zimmer im 1. Stock (Boden z=2.6) mit großem Fenster nach +y; draußen die überflutete Straße."""
    S = {"water": [], "float": []}
    FZ = 2.6
    wallm = LR.painted("wallcream", "wall_cream.png", scale=1.4)
    white = LR.soft("offwhite", (0.94, 0.93, 0.9), shade=0.78)
    alu = LR.soft("alu", (0.78, 0.8, 0.82), shade=0.7)
    LR.box("up_floor", (O.x, O.y, FZ - 0.05), (3.4, 3.4, 0.1), LR.painted("floorwood", "floor_wood.png", scale=1.6, proj="FLAT"))
    LR.box("up_ceil", (O.x, O.y, FZ + 2.45), (3.4, 3.4, 0.1), LR.painted("ceil", "ceiling.png", scale=2.0))
    LR.box("up_back", (O.x, O.y - 1.7, FZ + 1.2), (3.4, 0.1, 2.5), wallm)
    LR.box("up_left", (O.x - 1.7, O.y, FZ + 1.2), (0.1, 3.4, 2.5), LR.painted("wallgreen", "wall_green.png", scale=1.4))
    LR.box("up_right", (O.x + 1.7, O.y, FZ + 1.2), (0.1, 3.4, 2.5), wallm)
    # Vorderwand mit großem Fenster (Loch über Bool)
    fw = LR.box("up_front", (O.x, O.y + 1.7, FZ + 1.2), (3.4, 0.1, 2.5), wallm)
    hole = LR.box("up_hole", (O.x, O.y + 1.7, FZ + 1.15), (2.2, 0.4, 1.5), white)
    m = fw.modifiers.new("hole", "BOOLEAN")
    m.object = hole
    m.operation = "DIFFERENCE"
    hole.hide_render = hole.hide_viewport = True
    for nm, loc, size in (("uf_t", (0, 1.7, FZ + 1.9), (2.3, 0.14, 0.07)), ("uf_b", (0, 1.7, FZ + 0.4), (2.3, 0.14, 0.07)),
                          ("uf_l", (-1.1, 1.7, FZ + 1.15), (0.07, 0.14, 1.55)), ("uf_r", (1.1, 1.7, FZ + 1.15), (0.07, 0.14, 1.55)),
                          ("uf_m", (0, 1.67, FZ + 1.15), (0.06, 0.06, 1.5))):
        LR.box(nm, (O.x + loc[0], O.y + loc[1], loc[2]), size, alu, bevel=0.008)
    LR.box("up_sill", (O.x, O.y + 1.6, FZ + 0.38), (2.4, 0.22, 0.05), white)
    # Einrichtung: gefalteter Futon, Regal, Poster, Lampe
    LR.box("futon", (O.x - 1.1, O.y - 1.1, FZ + 0.25), (0.9, 1.0, 0.5), LR.painted("cushm", "cushion.png", scale=0.3), bevel=0.08)
    LR.box("up_shelf", (O.x + 1.45, O.y - 0.6, FZ + 0.6), (0.35, 1.0, 1.2), LR.soft("woodmid", (0.66, 0.46, 0.28)), bevel=0.01)
    LR.uvplane("poster", (O.x - 1.64, O.y + 0.2, FZ + 1.5), 0.6, 0.85, LR.painted("posterm", "photo2.png", proj="UV", shade=0.9), (math.radians(90), 0, math.radians(90)))
    # Draußen: Straße mit Häusern gegenüber, Masten; Wasser steigt; Auto + Trümmer treiben
    gnd = LR.box("out_ground", (O.x, O.y + 12, -0.05), (60, 30, 0.1), LR.soft("outgrass", (0.48, 0.6, 0.42)))
    LR.box("out_houseself", (O.x, O.y, FZ / 2 - 0.05), (3.6, 3.6, FZ - 0.1), wallm)
    roofs = [(0.3, 0.34, 0.44), (0.45, 0.3, 0.26), (0.26, 0.28, 0.32), (0.34, 0.42, 0.5)]
    walls = [(0.95, 0.92, 0.84), (0.88, 0.88, 0.87), (0.93, 0.86, 0.74), (0.82, 0.87, 0.9)]
    for k in range(6):
        x = O.x - 14 + k * 5.6 + R.uniform(-0.6, 0.6)
        y = O.y + 10.5 + R.uniform(-0.4, 0.6)
        w, l, h = R.uniform(4.0, 5.0), R.uniform(5, 6.5), 5.4
        LR.box(f"oh{k}", (x, y, h / 2), (w, l, h), LR.soft(f"ohw{k}", walls[k % 4], shade=0.72))
        import street as ST
        ST.gable(f"ohr{k}", x, y, w, l, h, 1.6, LR.soft(f"ohr{k % 4}", roofs[k % 4], shade=0.62), along_y=False)
        for wx in (-1.0, 1.0):
            LR.box(f"ohwin{k}", (x + wx, y - l / 2 - 0.02, 4.0), (0.9, 0.05, 0.8), LR.soft("glassout", (0.6, 0.72, 0.82), shade=0.85))
    for k in range(5):
        LR.cyl(f"opole{k}", (O.x - 12 + k * 6.5, O.y + 6.5, 4.5), 0.13, 9.0, LR.soft("pole", (0.68, 0.68, 0.66)), verts=12)
    # Wasser: zwei Flächen mit Wellen-Textur (bewegt), eine trübe Unterfläche
    def water_mat(name, scroll_keys):
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        for nd in list(nt.nodes):
            nt.nodes.remove(nd)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (0.12, 0.25, 1)
        nt.links.new(tc.outputs["Object"], mp.inputs[0])
        tx = nt.nodes.new("ShaderNodeTexImage")
        tx.image = bpy.data.images.load(os.path.join(LR.TEX, "water_top.png"), check_existing=True)
        tx.projection = "FLAT"
        nt.links.new(mp.outputs[0], tx.inputs[0])
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs[1].default_value = 0.95
        nt.links.new(tx.outputs[0], em.inputs[0])
        nt.links.new(em.outputs[0], out.inputs[0])
        for fr, x in scroll_keys:
            mp.inputs["Location"].default_value = (x, x * 0.3, 0)
            mp.inputs["Location"].keyframe_insert("default_value", frame=fr)
        m["toon"] = 1
        return m, mp
    S["water_mat"] = water_mat
    S["O"] = O
    S["FZ"] = FZ
    return S
