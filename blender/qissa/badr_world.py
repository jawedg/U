# QISSAH Folge 4 – „Die Schlacht von Badr“: Bausteine.
# Tal von Badr (weite Sandebene, Brunnen, Dünen im Süden = „ferne Talseite“, Koran 8:42), Schattendach (Arisch) auf einer
# kleinen Anhöhe, Baum, Pferde (Galopp, Aufbäumen), Kämpfer mit Schwert/Schild/Speer/Kettenhemd/Helm, Fahnen (wehen),
# ferne Heere als ein Objekt, Staubwolken (Karten zur Kamera), Regen, nasser Sand, Licht-Reiter (Engel NUR als Licht).
# Regeln: der Prophet ﷺ NUR als Licht, Menschen ohne Gesicht, kein Blut – Treffer nur auf Schild/Schwert.
import bpy, bmesh, math, random
from mathutils import Vector, noise
import lib as Q
import mekka as MK
import medina as MD
import kaaba_world as KW

M = {}
AX, AY = 230.0, 165.0                 # Talboden (Ellipse)
ARISH = Vector((-16.0, 44.0, 0.0))    # Schattendach für den Propheten ﷺ (kleine Anhöhe hinter den Reihen)
TREE = Vector((24.0, 60.0, 0.0))      # Baum: dort betete er die ganze Nacht
WELLS = [Vector((-3.0, 30.0, 0.0)), Vector((10.0, 26.0, 0.0)), Vector((3.0, 40.0, 0.0))]
CAMP = Vector((6.0, 48.0, 0.0))       # Lager der Muslime (Kamele, Gepäck)
LINE_M = 14.0                         # Reihe der Muslime (y)
LINE_Q = -34.0                        # Reihe der Quraisch (y)
QCAMP = Vector((0.0, -125.0, 0.0))    # Lager der Quraisch (hinter den Dünen)
SPASS = Vector((-30.0, -240.0, 0.0))  # Pass im Süden: von dort kommt das Heer aus Mekka
NPASS = Vector((26.0, 230.0, 0.0))    # Weg im Norden (nach Medina)
_PK = []


def _peaks():
    if _PK:
        return _PK
    rnd = random.Random(29)
    for i in range(66):
        a = rnd.uniform(0, 2 * math.pi)
        big = i < 46
        rn = rnd.uniform(1.35, 2.7) if big else rnd.uniform(1.05, 1.35)
        x, y = AX * rn * math.cos(a), AY * rn * math.sin(a)
        h = rnd.uniform(30, 72) if big else rnd.uniform(6, 18)
        r = rnd.uniform(50, 110) if big else rnd.uniform(14, 30)
        if y < 0 and abs(x - SPASS.x) < 70:   # Pass im Süden niedrig
            h *= 0.22
        if y > 0 and abs(x - NPASS.x) < 55:   # Weg nach Norden niedrig
            h *= 0.35
        _PK.append((x, y, h, r))
    return _PK


def _sstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


def height(x, y):
    """Sandebene mit sanften Wellen, Dünen im Süden, kleine Anhöhe beim Schattendach, ringsum dunkle Berge."""
    r = math.sqrt((x / AX) ** 2 + (y / AY) ** 2)
    h = 0.3 * noise.noise(Vector((x * 0.04, y * 0.04, 1.7))) + 0.1 * noise.noise(Vector((x * 0.19, y * 0.19, 4.2)))
    h += 5.0 * max(0.0, r - 0.65) ** 2
    s = _sstep(-62.0, -120.0, y) * (1.0 - _sstep(0.85, 1.15, r))
    if s > 0:
        h += s * (1.6 + 1.3 * math.sin(x * 0.05 + y * 0.018 + 1.8 * noise.noise(Vector((x * 0.012, y * 0.012, 7.0)))))
    h += 1.3 * math.exp(-((x - ARISH.x) ** 2 + (y - ARISH.y) ** 2) / 70.0)
    m, msum = 0.0, 0.0
    for px, py, ph, pr in _peaks():
        d2 = ((x - px) ** 2 + (y - py) ** 2) / (pr * pr)
        if d2 < 6.0:
            v = ph * math.exp(-1.6 * d2)
            m = max(m, v)
            msum += v
    m += 0.3 * (msum - m)
    if m > 0.5:
        p = Vector((x * 0.02, y * 0.02, 0.0))
        rid = 1.0 - abs(noise.noise(p * 1.7 + Vector((5, 1, 0))))
        gully = noise.fractal(p * 9.0, 0.7, 2.0, 4)
        m *= 0.55 + 0.5 * rid
        m += min(1.0, m / 30.0) * (0.045 * m * gully + 1.5 * noise.noise(p * 22.0))
    return h + max(0.0, m)


# Gelände von mekka.py mit eigener Höhe (MK.terrain/ground_z/scatter rufen „height“, AX, AY im Modul mekka auf)
MK.height = height
MK.AX, MK.AY = AX, AY
gz = MK.ground_z


def mats():
    KW.mats()
    MD.mats()
    M["mail"] = Q.pbr("b_mail", (0.27, 0.27, 0.28), 0.6, metal=0.55, var=0.3, scale=25, bump=0.25, bscale=90)
    M["steel"] = Q.pbr("b_steel", (0.62, 0.62, 0.64), 0.22, metal=1.0, var=0.1, scale=12)
    M["steel_d"] = Q.pbr("b_steel_d", (0.34, 0.33, 0.33), 0.35, metal=0.9, var=0.2, scale=10, bump=0.2, bscale=40)
    M["shield"] = Q.pbr("b_shield", (0.36, 0.23, 0.13), 0.7, var=0.3, scale=6, bump=0.3, bscale=30, rings=10)
    M["shield2"] = Q.pbr("b_shield2", (0.24, 0.15, 0.09), 0.6, var=0.3, scale=6, bump=0.3, bscale=30)
    M["grip"] = Q.pbr("b_grip", (0.12, 0.08, 0.05), 0.6, var=0.2)
    M["shaft"] = Q.pbr("b_shaft", (0.42, 0.3, 0.18), 0.7, var=0.2, scale=20)
    M["flag_w"] = Q.pbr("b_flag_w", (0.86, 0.84, 0.78), 0.9, var=0.1, scale=4, bump=0.1, bscale=30)
    M["flag_k"] = Q.pbr("b_flag_k", (0.05, 0.05, 0.055), 0.9, var=0.1, scale=4)
    M["flag_r"] = Q.pbr("b_flag_r", (0.45, 0.06, 0.05), 0.9, var=0.15, scale=4)
    M["flag_y"] = Q.pbr("b_flag_y", (0.62, 0.42, 0.1), 0.9, var=0.15, scale=4)
    M["horse"] = [Q.pbr(f"b_horse{k}", c, 0.7, var=0.12, scale=3, bump=0.15, bscale=60, spec=0.4)
                  for k, c in enumerate(((0.22, 0.12, 0.07), (0.32, 0.19, 0.1), (0.08, 0.06, 0.05), (0.55, 0.5, 0.45), (0.4, 0.25, 0.13)))]
    M["hair"] = Q.pbr("b_hair", (0.04, 0.03, 0.025), 0.8, var=0.2, scale=20)
    M["hoof"] = Q.pbr("b_hoof", (0.08, 0.07, 0.06), 0.6)
    M["tack"] = Q.pbr("b_tack", (0.18, 0.1, 0.06), 0.55, var=0.2, scale=8)
    M["far_m"] = Q.pbr("b_far_m", (0.78, 0.74, 0.66), 0.95, var=0.2, scale=0.3)
    M["far_q"] = Q.pbr("b_far_q", (0.3, 0.17, 0.12), 0.9, var=0.35, scale=0.3)
    M["far_h"] = Q.pbr("b_far_h", (0.24, 0.14, 0.08), 0.8, var=0.3, scale=0.3)
    M["far_metal"] = Q.pbr("b_far_metal", (0.4, 0.4, 0.42), 0.35, metal=0.8, var=0.2, scale=0.5)
    return M


QROBES = [(0.36, 0.1, 0.07), (0.22, 0.14, 0.1), (0.12, 0.1, 0.1), (0.45, 0.3, 0.16), (0.16, 0.16, 0.22), (0.5, 0.2, 0.1),
          (0.3, 0.22, 0.16)]
QWRAPS = [(0.08, 0.07, 0.07), (0.42, 0.08, 0.06), (0.25, 0.2, 0.16), (0.6, 0.5, 0.36)]
MROBES = [(0.86, 0.82, 0.72), (0.74, 0.66, 0.53), (0.9, 0.88, 0.82), (0.66, 0.58, 0.46), (0.8, 0.74, 0.62), (0.55, 0.45, 0.34)]
MWRAPS = [(0.93, 0.92, 0.88), (0.82, 0.78, 0.68), (0.9, 0.9, 0.86), (0.7, 0.62, 0.5)]


# ---------------------------------------------------------------- Licht
def daylight(mode, dust=0.0, stars=0.0):
    """Tageslicht aus mekka.py; dust > 0: dichter Staub in der Luft (Dunst näher, wärmer)."""
    cfg = MK.light(mode, stars=stars)
    w = Q.sc.world
    if dust > 0:
        w.mist_settings.start = 2.0 + 30.0 * (1 - dust)
        w.mist_settings.depth = 60.0 + 500.0 * (1 - dust)
        cfg["mist_col"] = (0.6, 0.48, 0.36) if mode != "golden" else (0.78, 0.54, 0.34)
        cfg["mist_amt"] = 0.45 + 0.35 * dust
    return cfg


def night(overcast=False, moon=0.5):
    if overcast:  # Regennacht: dunkle, gleichmäßige Wolkendecke, keine Sterne
        w = bpy.data.worlds.new("overcast")
        Q.sc.world = w
        w.use_nodes = True
        nt = w.node_tree
        bg = nt.nodes.get("Background")
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs["Generated"], sep.inputs[0])
        cr = nt.nodes.new("ShaderNodeValToRGB")
        nt.links.new(sep.outputs["Z"], cr.inputs["Fac"])
        E = cr.color_ramp.elements
        E[0].position, E[0].color = 0.0, (0.035, 0.04, 0.055, 1)
        E[1].position, E[1].color = 0.6, (0.012, 0.014, 0.022, 1)
        e = E.new(0.12)
        e.color = (0.05, 0.055, 0.075, 1)
        nt.links.new(cr.outputs["Color"], bg.inputs["Color"])
        bg.inputs["Strength"].default_value = 1.0
        Q.sun("moon", (60, 0, 150), moon * 0.5, (0.55, 0.65, 0.9), shadow=False, angle=12.0)
        mist = dict(mist_col=(0.03, 0.035, 0.05), mist_amt=0.55)
    else:
        Q.world_sky("night", amb=((0.25, 0.32, 0.55), 0.3))
        Q.sun("moon", (55, 0, 155), moon, (0.6, 0.7, 1.0), shadow=True, angle=1.0)
        mist = dict(mist_col=(0.02, 0.025, 0.05), mist_amt=0.5)
    w = Q.sc.world
    w.mist_settings.start = 20.0
    w.mist_settings.depth = 400.0
    w.mist_settings.falloff = "QUADRATIC"
    return mist


# ---------------------------------------------------------------- Tal
def prune_rocks(x0, x1, y0, y1, smax=0.35):
    """Große Brocken auf dem Schlachtfeld weg (dort rennen Leute und Pferde)."""
    for o in list(bpy.data.objects):
        if o.name.startswith("rk") and x0 < o.location.x < x1 and y0 < o.location.y < y1 and max(o.scale) > smax:
            bpy.data.objects.remove(o, do_unlink=True)


def valley(keep=(), n_rocks=420, n_shrubs=90, tree=True, wells=True, arish_=True, palms=True, field=True):
    mats()
    MK.terrain()
    if tree:
        MK.acacia("tree", Vector((TREE.x, TREE.y, gz(TREE.x, TREE.y))), h=5.6, spread=4.6, seed=4)
        for i, (x, y, s) in enumerate(((-70, 70, 0.7), (60, 30, 0.6), (-110, -20, 0.75), (95, -60, 0.65), (40, 105, 0.55),
                                       (-45, 115, 0.6))):
            MK.acacia(f"tree_far{i}", Vector((x, y, gz(x, y))), h=4.0 * s / 0.7, spread=3.4 * s / 0.7, seed=20 + i)
    if wells:
        for k, w in enumerate(WELLS):
            KW.well(f"well{k}", Vector((w.x, w.y, 0.0)))
    if palms:
        rnd = random.Random(8)
        for k, (x, y) in enumerate(((-9, 33), (15, 22), (-1, 47), (16, 34), (-12, 26), (8, 52), (21, 27))):
            MD.palm(f"palm{k}", (x, y, gz(x, y) - 0.05), h=rnd.uniform(6.5, 9.5), lean=(rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05)),
                    seed=300 + k)
    if arish_:
        arish()
    keep = list(keep) + [(w.x, w.y, 4.0) for w in WELLS] + [(ARISH.x, ARISH.y, 7.0), (TREE.x, TREE.y, 6.0)]
    MK.scatter(seed=7, n_rocks=n_rocks, n_shrubs=n_shrubs, keep=keep)
    if field:
        prune_rocks(-90, 90, -70, 30)
    MK.pebbles("peb_camp", (4.0, 36.0), (40, 30), 900, seed=3)
    return {}


def arish(name="arish", loc=ARISH, yaw=0.0):
    """Schattendach aus Palmstämmen und Palmzweigen auf der kleinen Anhöhe."""
    z = gz(loc.x, loc.y)
    root = Q.empty(name, (loc.x, loc.y, z), rot=(0, 0, yaw))
    W_, D_, H_ = 3.6, 3.0, 2.45
    for k, (x, y) in enumerate(((-W_ / 2, -D_ / 2), (W_ / 2, -D_ / 2), (-W_ / 2, D_ / 2), (W_ / 2, D_ / 2))):
        Q.cyl(f"{name}_post{k}", (x, y, H_ / 2 - 0.1), 0.1, H_ + 0.2, MD.M["trunk"], seg=10, parent=root)
    for k, y in enumerate((-D_ / 2, D_ / 2)):
        Q.cyl(f"{name}_beam{k}", (0, y, H_), 0.08, W_ + 0.4, MD.M["trunk"], seg=8, rot=(0, math.pi / 2, 0), parent=root)
    for i in range(14):
        x = -W_ / 2 - 0.1 + i * (W_ + 0.2) / 13
        Q.cyl(f"{name}_raf{i}", (x, 0, H_ + 0.1), 0.04, D_ + 0.5, MD.M["trunk"], seg=6, rot=(math.pi / 2, 0, 0), parent=root)
    Q.box(f"{name}_roof", (0, 0, H_ + 0.2), (W_ + 0.7, D_ + 0.8, 0.12), MD.M["roof"], bevel=0.04, jitter=0.04, parent=root)
    rnd = random.Random(5)
    for i in range(40):  # Fransen der Palmzweige
        side = rnd.choice((-1, 1))
        if rnd.random() < 0.5:
            p = (rnd.uniform(-W_ / 2, W_ / 2), side * (D_ / 2 + 0.42), H_ + 0.12)
            sz = (rnd.uniform(0.25, 0.6), 0.04, rnd.uniform(0.15, 0.4))
        else:
            p = (side * (W_ / 2 + 0.37), rnd.uniform(-D_ / 2, D_ / 2), H_ + 0.12)
            sz = (0.04, rnd.uniform(0.25, 0.6), rnd.uniform(0.15, 0.4))
        Q.box(f"{name}_fr{i}", p, sz, MD.M["dead"], rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), 0), parent=root)
    Q.box(f"{name}_mat", (0, 0, 0.02), (2.4, 2.0, 0.02), MD.M["mat"], parent=root)
    return root


# ---------------------------------------------------------------- Waffen
def sword(name, parent, rot=(0, 0, 0), loc=(0, 0, -0.05), drawn=True):
    """Gerades, zweischneidiges Schwert. Lokal: Griff durch die Faust (Y), Klinge nach -Y."""
    root = Q.empty(name, loc, parent=parent, rot=rot)
    Q.cyl(f"{name}_grip", (0, 0.0, 0), 0.016, 0.13, M["grip"], seg=8, rot=(math.pi / 2, 0, 0), parent=root)
    Q.ball(f"{name}_pom", (0, 0.075, 0), 0.025, M["steel_d"], seg=10, parent=root)
    Q.box(f"{name}_guard", (0, -0.075, 0), (0.17, 0.025, 0.03), M["steel_d"], bevel=0.008, parent=root)
    if drawn:
        bl = Q.box(f"{name}_blade", (0, -0.45, 0), (0.045, 0.72, 0.007), M["steel"], bevel=0.003, parent=root)
        Q.box(f"{name}_tip", (0, -0.83, 0), (0.032, 0.06, 0.006), M["steel"], rot=(0, 0, math.radians(45)), parent=root)
        bl["blade"] = 1
    return root


def shield(name, parent, loc=(0.0, 0.0, -0.06), r=0.32):
    """Runder Schild (Holz + Leder, Metallbuckel). Lokal: Vorderseite nach -Z (vom Unterarm weg nach vorn)."""
    root = Q.empty(name, loc, parent=parent, rot=(math.radians(90), 0, 0))
    Q.cyl(f"{name}_disc", (0, 0, 0), r, 0.03, M["shield"] if hash(name) % 2 else M["shield2"], seg=28, parent=root)
    Q.torus(f"{name}_rim", (0, 0, 0), r, 0.018, M["steel_d"], seg=32, rseg=6, parent=root)
    Q.ball(f"{name}_boss", (0, 0, -0.025), (0.07, 0.07, 0.04), M["steel"], seg=14, parent=root)
    return root


def spear(name, parent, length=2.6):
    root = Q.empty(name, (0, 0, -0.04), parent=parent)
    Q.cyl(f"{name}_shaft", (0, -length * 0.35, 0), 0.016, length, M["shaft"], seg=6, rot=(math.pi / 2, 0, 0), parent=root)
    Q.cyl(f"{name}_tip", (0, -length * 0.85 - 0.1, 0), 0.03, 0.22, M["steel"], seg=6, rot=(-math.pi / 2, 0, 0), r2=0.002, parent=root)
    return root


def banner(name, loc, mat, pole_h=3.6, size=(1.1, 0.75), parent=None, rot=(0, 0, 0), wind=1.0):
    """Fahne an einer Stange; der Stoff weht (Wellen-Modifikator läuft mit der Zeit)."""
    root = Q.empty(name, loc, parent=parent, rot=rot)
    if parent is None:
        root["person"] = 1   # nicht mit join_static verschmelzen (sonst steht der Wellen-Modifikator still)
    Q.cyl(f"{name}_pole", (0, 0, pole_h / 2), 0.025, pole_h, M["shaft"], seg=8, parent=root)
    Q.ball(f"{name}_knob", (0, 0, pole_h + 0.03), 0.04, M["steel_d"], seg=10, parent=root)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=16, y_segments=10, size=0.5)
    for v in bm.verts:
        v.co = Vector(((v.co.x + 0.5) * size[0], (v.co.y - 0.5) * size[1], 0))
    me = bpy.data.meshes.new(f"{name}_cl")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    cl = bpy.data.objects.new(f"{name}_cloth", me)
    Q.link(cl)
    cl.parent = root
    cl.location = (0.02, 0, pole_h - 0.05)
    cl.rotation_euler = (math.radians(90), 0, 0)
    sm = cl.modifiers.new("solid", "SOLIDIFY")
    sm.thickness = 0.008
    wv = cl.modifiers.new("wave", "WAVE")
    wv.use_y = False
    wv.height = 0.09 * wind
    wv.width = 0.55
    wv.narrowness = 1.2
    wv.speed = 0.06 * wind
    wv.start_position_x = 0.0
    wv.use_normal = False
    wv.time_offset = random.Random(hash(name)).uniform(-40, 0)
    return root


# ---------------------------------------------------------------- Kämpfer
def warrior(name, loc, yaw=0.0, side="m", seed=0, weapon="sword", shield_=True, mail=None, helmet=None, head=None, sit=False,
            height=None, cloak=None, glow=False, robe=None):
    """Kämpfer ohne Gesicht. side "m" = Muslime (helle Gewänder), "q" = Quraisch (dunkler, rot, öfter Kettenhemd + Helm)."""
    rnd = random.Random(seed)
    if side == "q":
        robe = robe or rnd.choice(QROBES)
        wrap = rnd.choice(QWRAPS)
        mail = rnd.random() < 0.55 if mail is None else mail
        helmet = rnd.random() < 0.45 if helmet is None else helmet
    else:
        robe = robe or rnd.choice(MROBES)
        wrap = rnd.choice(MWRAPS)
        mail = rnd.random() < 0.12 if mail is None else mail
        helmet = rnd.random() < 0.08 if helmet is None else helmet
    head = head or ("cap" if helmet else rnd.choice(["turban", "turban", "scarf"]))
    P = Q.person(name, loc, yaw=yaw, robe=robe, wrap=wrap, head=head, seed=seed, sit=sit, cloak=cloak, glow=glow,
                 height=height or rnd.uniform(0.95, 1.05))
    if mail:
        tor = bpy.data.objects.get(f"{name}_torso")
        if tor:
            tor.data.materials[0] = M["mail"]
    if helmet:
        Q.ball(f"{name}_helm", (0, 0.0, 0.17), (0.108, 0.118, 0.1), M["steel_d"], seg=16, parent=P["head"])
        Q.cyl(f"{name}_spike", (0, 0, 0.29), 0.022, 0.08, M["steel_d"], seg=8, r2=0.003, parent=P["head"])
    if weapon == "sword":
        P["sword"] = sword(f"{name}_sw", P["hand.R"])
    elif weapon == "spear":
        P["spear"] = spear(f"{name}_sp", P["hand.R"])
    elif weapon == "bow":
        KW.bow(f"{name}_bow", (0, 0, -0.05), parent=P["hand.L"], rot=(0, 0, math.pi / 2))
    if shield_ and weapon != "bow":
        P["shield"] = shield(f"{name}_shd", P["hand.L"])
    P["side"] = side
    return P


def guard_pose(P, t):
    """Kampfhaltung: Schild vorn, Schwert erhoben."""
    Q.arm_pose(P, t, "L", -62, -58, sh_y=-12)
    Q.arm_pose(P, t, "R", -128, -40, sh_y=8)


def strike(P, t, dur=0.32):
    """Hieb von oben: ausholen, zuschlagen (trifft nur Schild/Schwert des Gegners), zurück."""
    Q.arm_pose(P, t - dur * 1.2, "R", -165, -55, sh_y=10)
    Q.arm_pose(P, t, "R", -55, -10, sh_y=4)
    Q.arm_pose(P, t + dur * 1.5, "R", -128, -40, sh_y=8)


def block(P, t):
    """Schild hoch."""
    Q.arm_pose(P, t - 0.18, "L", -62, -58, sh_y=-12)
    Q.arm_pose(P, t, "L", -105, -70, sh_y=-20)
    Q.arm_pose(P, t + 0.45, "L", -62, -58, sh_y=-12)


def duel(A, B, t0, t1, seed=0, period=1.1):
    """Zwei Kämpfer: abwechselnd Hieb und Abwehr (Klinge trifft Schild), leichte Schritte vor und zurück."""
    rnd = random.Random(seed)
    guard_pose(A, t0)
    guard_pose(B, t0)
    hits = []
    t = t0 + rnd.uniform(0.2, 0.6)
    k = 0
    while t < t1:
        a, b = (A, B) if k % 2 == 0 else (B, A)
        strike(a, t)
        block(b, t)
        hits.append((t, a, b))
        t += period * rnd.uniform(0.8, 1.2)
        k += 1
    return hits


def run_to(P, path, t0, speed=4.2):
    return Q.walk(P, path, t0, speed=speed, run=True)


def fall_back(P, t, dur=0.7, side=1):
    """Gegner stürzt rückwärts in den Sand (kein Blut; Schnitt kurz danach)."""
    r = P["root"]
    r.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))
    r.keyframe_insert("location", frame=max(1, Q.T(t)))
    e = r.rotation_euler.copy()
    r.rotation_euler = (e.x - math.radians(84), e.y + math.radians(6 * side), e.z)
    yaw = e.z
    back = Vector((-math.sin(yaw), math.cos(yaw), 0))  # hinter der Figur (sie schaut nach -Y lokal)
    r.location = r.location + back * 0.5 + Vector((0, 0, 0.22))
    r.keyframe_insert("rotation_euler", frame=Q.T(t + dur))
    r.keyframe_insert("location", frame=Q.T(t + dur))
    Q.arm_pose(P, t + 0.1, "L", -120, -20, sh_y=-40)
    Q.arm_pose(P, t + 0.1, "R", -120, -20, sh_y=40)


# ---------------------------------------------------------------- Pferd
def horse(name, loc, yaw=0.0, seed=0, saddle=True, colour=None):
    """Araberpferd (Blick lokal -Y). Gelenke wie beim Kamel: body, neck, head, leg.FL/FR/BL/BR + knee.*, tail."""
    rnd = random.Random(seed)
    mc = M["horse"][colour if colour is not None else rnd.randint(0, len(M["horse"]) - 1)]
    C = {"name": name}
    root = Q.empty(f"{name}_root", loc, rot=(0, 0, yaw))
    C["root"] = root
    body = Q.empty(f"{name}_body", (0, 0, 1.18), root)
    C["body"] = body
    tor = Q.loft(f"{name}_torso", [(-0.8, 0.08, 0.1, 0, 0.06), (-0.74, 0.22, 0.26, 0, 0.04), (-0.55, 0.27, 0.31, 0, 0.0),
                                   (-0.25, 0.26, 0.3, 0, -0.03), (0.1, 0.25, 0.31, 0, -0.04), (0.42, 0.25, 0.34, 0, -0.01),
                                   (0.62, 0.22, 0.31, 0, 0.04), (0.74, 0.14, 0.2, 0, 0.1), (0.8, 0.05, 0.08, 0, 0.14)],
                 mc, parent=body, seg=28, folds=(4, 0.015, 0.015, seed))
    tor.rotation_euler = (math.pi / 2, 0, 0)
    neck = Q.empty(f"{name}_neck", (0, -0.66, 0.16), body)
    C["neck"] = neck
    pts = [Vector((0, 0, 0)), Vector((0, -0.18, 0.28)), Vector((0, -0.3, 0.58))]
    for k in range(2):
        Q.limb(f"{name}_nk{k}", pts[k], pts[k + 1], 0.19 - 0.05 * k, 0.14 - 0.03 * k, mc, seg=14, parent=neck)
        Q.ball(f"{name}_nj{k}", pts[k], 0.19 - 0.05 * k, mc, parent=neck, seg=14)
    head = Q.empty(f"{name}_head", (0, -0.32, 0.64), neck)
    C["head"] = head
    hs = Q.empty(f"{name}_hs", (0, 0, 0), head, rot=(math.radians(-38), 0, 0))
    Q.ball(f"{name}_skull", (0, -0.04, 0.02), (0.085, 0.13, 0.1), mc, parent=hs, seg=16)
    Q.limb(f"{name}_muz", (0, -0.1, 0.0), (0, -0.36, -0.02), 0.075, 0.062, mc, seg=14, parent=hs)
    Q.ball(f"{name}_nose", (0, -0.37, -0.02), (0.065, 0.05, 0.06), mc, parent=hs, seg=12)
    for s_ in (-1, 1):
        Q.cyl(f"{name}_ear{s_}", (0.05 * s_, 0.05, 0.12), 0.022, 0.1, mc, seg=6, r2=0.004, parent=hs)
        Q.ball(f"{name}_eye{s_}", (0.075 * s_, -0.08, 0.04), 0.017, M["hoof"], parent=hs, seg=8)
    Q.torus(f"{name}_bridle", (0, -0.25, -0.01), 0.075, 0.008, M["tack"], parent=hs, scale=(1.0, 0.7, 1.0)).rotation_euler = (1.5, 0, 0)
    # Mähne
    for k in range(9):
        u = k / 8
        p = pts[0] + (pts[2] - pts[0]) * u + Vector((0, 0.11 - 0.03 * u, 0.05 + 0.02 * u))
        Q.box(f"{name}_mane{k}", p, (0.025, 0.08, 0.14), M["hair"], rot=(math.radians(-25), rnd.uniform(-0.3, 0.3), 0), parent=neck)
    for nm, (x, y) in (("FL", (-0.14, -0.52)), ("FR", (0.14, -0.52)), ("BL", (-0.14, 0.56)), ("BR", (0.14, 0.56))):
        hip = Q.empty(f"{name}_leg.{nm}", (x, y, -0.12), body)
        rear = nm[0] == "B"
        Q.limb(f"{name}_thigh.{nm}", (0, 0, 0.12), (0, 0.06 if rear else 0.0, -0.48), 0.13 if rear else 0.1, 0.06, mc, seg=12, parent=hip)
        knee = Q.empty(f"{name}_knee.{nm}", (0, 0.06 if rear else 0.0, -0.48), hip)
        Q.ball(f"{name}_kn.{nm}", (0, 0, 0), 0.06, mc, parent=knee, seg=10)
        Q.limb(f"{name}_shin.{nm}", (0, 0, 0), (0, -0.02, -0.5), 0.042, 0.036, mc, seg=10, parent=knee)
        Q.cyl(f"{name}_hoof.{nm}", (0, -0.03, -0.53), 0.05, 0.08, M["hoof"], seg=10, r2=0.04, parent=knee)
        C[f"leg.{nm}"], C[f"knee.{nm}"] = hip, knee
    tail = Q.empty(f"{name}_tailr", (0, 0.8, 0.12), body)
    C["tail"] = tail
    Q.limb(f"{name}_tail0", (0, 0, 0), (0, 0.18, -0.25), 0.06, 0.05, M["hair"], seg=8, parent=tail)
    Q.limb(f"{name}_tail1", (0, 0.18, -0.25), (0, 0.2, -0.75), 0.06, 0.03, M["hair"], seg=8, parent=tail)
    if saddle:
        Q.box(f"{name}_blanket", (0, -0.02, 0.33), (0.6, 0.7, 0.04), rnd.choice([MK.M["blanket_r"], MK.M["blanket_b"], M["flag_r"]]),
              bevel=0.01, parent=body)
        Q.ball(f"{name}_saddle", (0, -0.02, 0.36), (0.22, 0.3, 0.07), M["tack"], parent=body, seg=14)
    Q.blob(f"{name}_blob", root, 0.75)
    root["person"] = 1
    return C


GALLOP = {"BL": 0.0, "BR": 0.12, "FL": 0.5, "FR": 0.62}


def horse_run(C, path, t0, speed=8.0, stride=2.8, z_of=None, trot=False):
    """Galopp (bzw. Trab) entlang path: Beine im Viertakt, Körper wiegt, Hals nickt, Schweif weht."""
    root, body, neck = C["root"], C["body"], C["neck"]
    pts = [Vector((p[0], p[1], 0)) for p in path]
    segs = list(zip(pts, pts[1:]))
    total = sum((b - a).length for a, b in segs)
    dur = total / speed
    f0, f1 = Q.T(t0), Q.T(t0 + dur)
    bz = body.location.z
    for f in range(f0, f1 + 1):
        d = min(total, (f - f0) / Q.FPS * speed)
        acc = 0.0
        pos, dv = pts[-1], (segs[-1][1] - segs[-1][0]).normalized()
        for a, b in segs:
            L_ = (b - a).length
            if d <= acc + L_:
                pos = a + (b - a) * ((d - acc) / L_)
                dv = (b - a).normalized()
                break
            acc += L_
        z = z_of(pos.x, pos.y) if z_of else gz(pos.x, pos.y)
        root.location = (pos.x, pos.y, z)
        root.keyframe_insert("location", frame=f)
        root.rotation_euler = (0, 0, math.atan2(dv.x, -dv.y))
        root.keyframe_insert("rotation_euler", index=2, frame=f)
        cyc = d / stride
        ph = 2 * math.pi * cyc
        amp = 0.5 if trot else 1.0
        body.location.z = bz + (0.05 if trot else 0.09) * math.sin(2 * ph if trot else ph)
        body.rotation_euler = (math.radians(5 * amp * math.sin(ph + 0.8)), 0, 0)
        body.keyframe_insert("location", index=2, frame=f)
        body.keyframe_insert("rotation_euler", frame=f)
        neck.rotation_euler = (math.radians(-8 * amp * math.sin(ph + 0.3)), 0, 0)
        neck.keyframe_insert("rotation_euler", frame=f)
        C["tail"].rotation_euler = (math.radians(35 * amp + 8 * math.sin(ph * 2)), 0, math.radians(6 * math.sin(ph)))
        C["tail"].keyframe_insert("rotation_euler", frame=f)
        for nm, off in GALLOP.items():
            if trot:
                off = {"BL": 0.0, "FR": 0.0, "BR": 0.5, "FL": 0.5}[nm]
            u = (cyc + off) % 1.0
            # Stütze (u < 0.4): Bein schwingt nach hinten; Flug (u >= 0.4): Bein angewinkelt nach vorn
            if u < 0.4:
                sw = 1.0 - 2.0 * u / 0.4
                kb = 0.0
            else:
                v = (u - 0.4) / 0.6
                sw = -1.0 + 2.0 * v
                kb = math.sin(math.pi * v)
            hip, kn = C[f"leg.{nm}"], C[f"knee.{nm}"]
            front = nm[0] == "F"
            hip.rotation_euler = (math.radians(-(32 if front else 28) * amp * sw), 0, 0)
            hip.keyframe_insert("rotation_euler", frame=f)
            kn.rotation_euler = (math.radians((70 if front else -55) * amp * kb), 0, 0)
            kn.keyframe_insert("rotation_euler", frame=f)
    return t0 + dur


def horse_rear(C, t, dur=1.4):
    """Pferd bäumt sich auf (Vorderbeine in der Luft), dann wieder herunter."""
    body = C["body"]
    for tt, pitch, dz, dy, fk in ((t - 0.25, 0, 0, 0, 0), (t + 0.35, -42, 0.45, 0.35, 85), (t + dur - 0.4, -36, 0.4, 0.3, 70),
                                  (t + dur, 0, 0, 0, 0)):
        body.rotation_euler = (math.radians(pitch), 0, 0)
        body.location = (0, dy, 1.18 + dz)
        body.keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
        body.keyframe_insert("location", frame=max(1, Q.T(tt)))
        for nm in ("FL", "FR"):
            C[f"leg.{nm}"].rotation_euler = (math.radians(-0.7 * fk), 0, 0)
            C[f"knee.{nm}"].rotation_euler = (math.radians(fk * 1.2), 0, 0)
            C[f"leg.{nm}"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
            C[f"knee.{nm}"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
        for nm in ("BL", "BR"):
            C[f"leg.{nm}"].rotation_euler = (math.radians(-pitch * 0.9), 0, 0)
            C[f"leg.{nm}"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
        C["neck"].rotation_euler = (math.radians(-pitch * 0.3), 0, 0)
        C["neck"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))


def mounted(name, C, side="q", seed=0, weapon="sword", **kw):
    """Reiter auf dem Pferd."""
    P = warrior(name, (0, 0, 0), side=side, seed=seed, weapon=weapon, sit=True, **kw)
    P["root"].parent = C["body"]
    P["root"].location = (0, 0.02, 0.38)
    P["root"].rotation_euler = (0, 0, 0)
    rob = Q.pbr(f"robe_leg_{name}", (0.4, 0.3, 0.22) if side == "q" else (0.75, 0.7, 0.6), 0.9)
    for s_, nm in ((-1, "L"), (1, "R")):
        Q.limb(f"{name}_legh.{nm}", (0.22 * s_, -0.12, 0.3), (0.3 * s_, -0.22, -0.3), 0.07, 0.055, rob, parent=C["body"], seg=10)
    return P


# ---------------------------------------------------------------- ferne Heere (ein Objekt, bewegt sich als Ganzes)
def far_army(name, x0, x1, y0, y1, n_men, n_horse=0, n_camel=0, side="q", seed=0, banners=4, facing=0.0, avoid=(), spears=True):
    """Viele ferne Gestalten als EIN Objekt: Männer (Kegel + Kopf), Pferde, Kamele, Speere, Fahnen."""
    rnd = random.Random(seed)
    groups = {"men": bmesh.new(), "horse": bmesh.new(), "metal": bmesh.new()}

    def add_cone(bm, x, y, z, r0, r1, h, seg=7):
        g = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r0, radius2=r1, depth=h)
        for v in g["verts"]:
            v.co += Vector((x, y, z + h / 2))

    def add_ball(bm, x, y, z, r):
        g = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        for v in g["verts"]:
            v.co += Vector((x, y, z))

    def add_box(bm, c, s, yaw=0.0):
        g = bmesh.ops.create_cube(bm, size=1.0)
        cy, sy = math.cos(yaw), math.sin(yaw)
        for v in g["verts"]:
            p = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2]))
            v.co = Vector((c[0] + p.x * cy - p.y * sy, c[1] + p.x * sy + p.y * cy, c[2] + p.z))
    def free(x, y):
        return all((x - a) ** 2 + (y - b) ** 2 > r * r for a, b, r in avoid)
    for _ in range(n_men):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if not free(x, y):
            continue
        z = gz(x, y)
        h = rnd.uniform(1.55, 1.8)
        add_cone(groups["men"], x, y, z, 0.27, 0.19, h - 0.25)
        add_ball(groups["men"], x, y, z + h - 0.1, 0.12)
        add_box(groups["men"], (x, y, z + h - 0.36), (0.46, 0.2, 0.12))   # Schultern
        if spears and rnd.random() < 0.35:  # Speer
            add_box(groups["metal"], (x + 0.25, y, z + h * 0.9), (0.03, 0.03, 2.4))
    sgn = -1 if abs(facing) < 1.0 else 1   # Kopf vorn: facing 0 -> Blick nach -Y? (Figuren schauen lokal -Y)
    for _ in range(n_horse):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        z = gz(x, y)
        yaw = rnd.uniform(-0.2, 0.2)
        add_box(groups["horse"], (x, y, z + 1.15), (0.5, 1.5, 0.6), yaw)
        add_box(groups["horse"], (x, y + 0.8 * sgn, z + 1.6), (0.25, 0.55, 0.3), yaw)
        for dx, dy in ((-0.15, -0.55), (0.15, -0.55), (-0.15, 0.55), (0.15, 0.55)):
            add_box(groups["horse"], (x + dx, y + dy, z + 0.45), (0.08, 0.08, 0.9), yaw)
        add_cone(groups["men"], x, y, z + 1.4, 0.24, 0.17, 0.75)
        add_ball(groups["men"], x, y, z + 2.25, 0.12)
    for _ in range(n_camel):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        z = gz(x, y)
        add_box(groups["horse"], (x, y, z + 1.75), (0.7, 1.8, 0.75))
        add_ball(groups["horse"], x, y, z + 2.25, 0.35)
        add_box(groups["horse"], (x, y + 1.1 * sgn, z + 2.4), (0.22, 0.6, 0.25))
        for dx, dy in ((-0.2, -0.65), (0.2, -0.65), (-0.2, 0.65), (0.2, 0.65)):
            add_box(groups["horse"], (x + dx, y + dy, z + 0.7), (0.1, 0.1, 1.4))
    objs = []
    mm = {"men": M["far_q"] if side == "q" else M["far_m"], "horse": M["far_h"], "metal": M["far_metal"]}
    root = Q.empty(name, (0, 0, 0))
    root["person"] = 1
    for k, bm in groups.items():
        me = bpy.data.meshes.new(f"{name}_{k}")
        bm.to_mesh(me)
        bm.free()
        if not len(me.vertices):
            continue
        me.materials.append(mm[k])
        o = bpy.data.objects.new(f"{name}_{k}", me)
        Q.link(o)
        o.parent = root
        o.visible_shadow = False
        objs.append(o)
    cols = [M["flag_r"], M["flag_k"], M["flag_y"]] if side == "q" else [M["flag_w"], M["flag_k"]]
    for k in range(banners):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        banner(f"{name}_fl{k}", (x, y, gz(x, y)), cols[k % len(cols)], pole_h=4.2, size=(1.4, 0.9), parent=root, wind=1.3)
    return root


def far_wobble(root, t1, amp=0.05, hz=1.6):
    """Ganzes Heer wippt leicht (Gehen)."""
    for f in range(1, Q.T(t1) + 2, 3):
        t = (f - 1) / Q.FPS
        root.location.z = amp * abs(math.sin(t * hz * math.pi))
        root.keyframe_insert("location", index=2, frame=f)


def move(root, path_t, interp="LINEAR"):
    """path_t = [(t, (x, y, z)), ...]"""
    for t, p in path_t:
        root.location = p
        root.keyframe_insert("location", frame=max(1, Q.T(t)))
    for fc in Q.fcurves(root):
        for kp in fc.keyframe_points:
            kp.interpolation = interp


# ---------------------------------------------------------------- Staub
def dust_mat():
    if "dust" in M:
        return M["dust"]
    m = bpy.data.materials.new("b_dust")
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.66, 0.53, 0.4, 1)
    b.inputs["Roughness"].default_value = 1.0
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = 0.0
    tc = N.new("ShaderNodeTexCoord")
    oi = N.new("ShaderNodeObjectInfo")
    gr = N.new("ShaderNodeTexGradient")
    gr.gradient_type = "QUADRATIC_SPHERE"
    L.new(tc.outputs["Object"], gr.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise")
    nz.noise_dimensions = "4D"
    nz.inputs["Scale"].default_value = 2.2
    nz.inputs["Detail"].default_value = 3.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    rw = N.new("ShaderNodeMath")
    rw.operation = "MULTIPLY"
    L.new(oi.outputs["Random"], rw.inputs[0])
    rw.inputs[1].default_value = 50.0
    L.new(rw.outputs[0], nz.inputs["W"])
    mr = N.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.35
    mr.inputs["From Max"].default_value = 0.75
    L.new(nz.outputs["Fac"], mr.inputs["Value"])
    m1 = N.new("ShaderNodeMath")
    m1.operation = "MULTIPLY"
    L.new(gr.outputs["Fac"], m1.inputs[0])
    L.new(mr.outputs[0], m1.inputs[1])
    m2 = N.new("ShaderNodeMath")
    m2.operation = "MULTIPLY"
    L.new(m1.outputs[0], m2.inputs[0])
    L.new(oi.outputs["Alpha"], m2.inputs[1])
    L.new(m2.outputs[0], b.inputs["Alpha"])
    m.surface_render_method = "BLENDED"
    M["dust"] = m
    return m


def dust_card(name, loc, size, cam, t0=0.0, t1=60.0, alpha=0.55, grow=1.6, drift=(0.0, 0.0, 0.25), fade_in=0.5, fade_out=1.0,
              col=None):
    """Staubwolke als Karte, die immer zur Kamera schaut; wird größer, treibt, blendet ein/aus (Objekt-Alpha)."""
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(dust_mat())
    o = bpy.data.objects.new(name, me)
    Q.link(o)
    o.location = loc
    o.visible_shadow = False
    c = o.constraints.new("TRACK_TO")
    c.target = cam
    c.track_axis = "TRACK_Z"
    c.up_axis = "UP_Y"
    rgb = col or (1.0, 1.0, 1.0)
    for t, a, s, d in ((t0, 0.0, 1.0, 0.0), (t0 + fade_in, alpha, 1.0 + (grow - 1) * 0.2, 0.2), (max(t0 + fade_in + 0.1, t1 - fade_out), alpha,
                                                                                                       grow * 0.9, 0.85), (t1, 0.0, grow, 1.0)):
        o.color = (*rgb, a)
        o.keyframe_insert("color", frame=max(1, Q.T(t)))
        o.scale = (size[0] * s, size[1] * s, 1)
        o.keyframe_insert("scale", frame=max(1, Q.T(t)))
        o.location = Vector(loc) + Vector(drift) * (t1 - t0) * d
        o.keyframe_insert("location", frame=max(1, Q.T(t)))
    return o


def dust_cloud(prefix, center, spread, n, cam, t0, t1, seed=0, size=(6, 4), alpha=0.5, drift=(0.6, 0.0, 0.3)):
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        p = Vector((center[0] + rnd.uniform(-spread[0], spread[0]), center[1] + rnd.uniform(-spread[1], spread[1]), 0))
        p.z = gz(p.x, p.y) + size[1] * rnd.uniform(0.25, 0.5)
        s = rnd.uniform(0.7, 1.3)
        a0 = t0 + rnd.uniform(0, 0.6 * max(0.1, t1 - t0))
        out.append(dust_card(f"{prefix}{k}", p, (size[0] * s, size[1] * s), cam, a0, t1 + rnd.uniform(0, 1.5), alpha * rnd.uniform(0.6, 1.0),
                             grow=rnd.uniform(1.3, 2.0), drift=(drift[0] * rnd.uniform(0.5, 1.5), drift[1], drift[2])))
    return out


def hoof_dust(prefix, C, t0, t1, cam, every=0.25, alpha=0.4, seed=0):
    """Staub hinter einem laufenden Pferd/Läufer (Karten an den Positionen der Figur)."""
    rnd = random.Random(seed)
    root = C["root"]
    out = []
    t = t0
    k = 0
    fc = {}
    while t < t1:
        Q.sc.frame_set(Q.T(t))
        p = root.matrix_world.translation.copy()
        p.z = gz(p.x, p.y) + 0.5
        out.append(dust_card(f"{prefix}{k}", p, (1.6, 1.1), cam, t, t + rnd.uniform(1.6, 2.6), alpha * rnd.uniform(0.6, 1.0), grow=2.4,
                             drift=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), 0.35), fade_in=0.15, fade_out=1.0))
        t += every * rnd.uniform(0.8, 1.2)
        k += 1
    Q.sc.frame_set(1)
    return out


# ---------------------------------------------------------------- Regen + nasser Sand
def rain(name, center, cam_loc, size=(26.0, 26.0, 14.0), n=1600, speed=9.0, t1=30.0, seed=0, alpha=0.35):
    """Regenstreifen (zur Kamera gedreht) in einem Kasten um die Kamera; zwei Kästen übereinander fallen endlos (Zyklus)."""
    rnd = random.Random(seed)
    m = Q.glow_mat(f"{name}_m", (0.62, 0.68, 0.78), 0.55, alpha=alpha)
    objs = []
    for layer in range(2):
        bm = bmesh.new()
        for _ in range(n):
            c = Vector((center[0] + rnd.uniform(-size[0] / 2, size[0] / 2), center[1] + rnd.uniform(-size[1] / 2, size[1] / 2),
                        rnd.uniform(0, size[2])))
            L_ = rnd.uniform(0.35, 0.6)
            to_cam = Vector((cam_loc[0] - c.x, cam_loc[1] - c.y, 0))
            if to_cam.length < 0.5:
                continue
            side = Vector((-to_cam.y, to_cam.x, 0)).normalized() * 0.006
            slant = Vector((0.06, 0.02, 0))
            vs = [bm.verts.new(c - side), bm.verts.new(c + side), bm.verts.new(c + side + Vector((0, 0, L_)) + slant),
                  bm.verts.new(c - side + Vector((0, 0, L_)) + slant)]
            bm.faces.new(vs)
        me = bpy.data.meshes.new(f"{name}{layer}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(m)
        o = bpy.data.objects.new(f"{name}{layer}", me)
        Q.link(o)
        o.visible_shadow = False
        z0 = layer * size[2]
        per = size[2] / speed
        o.location = (0, 0, z0)
        o.keyframe_insert("location", index=2, frame=1)
        o.location = (0, 0, z0 - size[2])
        o.keyframe_insert("location", index=2, frame=1 + int(per * Q.FPS))
        for fc_ in Q.fcurves(o):
            for kp in fc_.keyframe_points:
                kp.interpolation = "LINEAR"
            fc_.modifiers.new("CYCLES")
        objs.append(o)
    return objs


def wet_ground(t0, t1, amount=0.55):
    """Sand wird im Regen dunkler und glänzt etwas (Koran 8:11: der Regen festigte den Boden)."""
    m = MK.M.get("terrain_m")
    if m is None:
        return
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    sock = b.inputs["Base Color"]
    src = sock.links[0].from_socket if sock.is_linked else None
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs[7].default_value = (0.5, 0.47, 0.45, 1)
    if src is not None:
        nt.links.new(src, mix.inputs[6])
    else:
        mix.inputs[6].default_value = sock.default_value
    nt.links.new(mix.outputs[2], sock)
    f = mix.inputs["Factor"]
    f.default_value = 0.0
    f.keyframe_insert("default_value", frame=max(1, Q.T(t0)))
    f.default_value = amount
    f.keyframe_insert("default_value", frame=Q.T(t1))
    r = b.inputs["Roughness"]
    if not r.is_linked:
        r.keyframe_insert("default_value", frame=max(1, Q.T(t0)))
        r.default_value = 0.55
        r.keyframe_insert("default_value", frame=Q.T(t1))


# ---------------------------------------------------------------- Licht-Reiter (Engel NUR als Licht)
def light_rider(name, p0, p1, t0, dur, length=7.0, width=0.45, strength=1.0, lamp=600.0):
    """Lichtstreif, der von p0 nach p1 fliegt (Kopf hell, Schweif verblasst). Kein Körper, keine Gestalt."""
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    root = Q.empty(name, p0)
    root.rotation_euler = d.to_track_quat("-Y", "Z").to_euler()
    m_out = Q.glow_mat(f"{name}_mo", (1.0, 0.86, 0.6), 4.0 * strength, 0.5, fresnel=True)
    m_core = Q.glow_mat(f"{name}_mc", (1.0, 0.97, 0.9), 22.0 * strength, 1.0, fresnel=True)
    Q.cyl(f"{name}_tail", (0, length / 2, 0), 0.02, length, m_out, seg=16, rot=(math.pi / 2, 0, 0), r2=width, parent=root)
    Q.cyl(f"{name}_core", (0, length * 0.3, 0), 0.01, length * 0.6, m_core, seg=12, rot=(math.pi / 2, 0, 0), r2=width * 0.35, parent=root)
    Q.ball(f"{name}_head", (0, 0, 0), width * 0.9, m_core, seg=16, parent=root)
    lt = Q.point(f"{name}_l", (0, 0, 0), lamp * strength, color=(1.0, 0.86, 0.62), radius=0.5, parent=root)
    root.scale = (0.001, 0.001, 0.001)
    root.keyframe_insert("scale", frame=max(1, Q.T(t0 - 0.05)))
    root.keyframe_insert("location", frame=max(1, Q.T(t0)))
    root.scale = (1, 1, 1)
    root.keyframe_insert("scale", frame=max(1, Q.T(t0 + 0.12)))
    root.location = p1
    root.keyframe_insert("location", frame=Q.T(t0 + dur))
    root.keyframe_insert("scale", frame=Q.T(t0 + dur - 0.1))
    root.scale = (0.001, 0.001, 0.001)
    root.keyframe_insert("scale", frame=Q.T(t0 + dur + 0.15))
    for fc in Q.fcurves(root):
        if fc.data_path == "location":
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
    lt.data.energy = 0.0
    lt.data.keyframe_insert("energy", frame=max(1, Q.T(t0 - 0.05)))
    lt.data.energy = lamp * strength
    lt.data.keyframe_insert("energy", frame=max(1, Q.T(t0 + 0.12)))
    lt.data.keyframe_insert("energy", frame=Q.T(t0 + dur - 0.1))
    lt.data.energy = 0.0
    lt.data.keyframe_insert("energy", frame=Q.T(t0 + dur + 0.15))
    return root


def sparks(name, loc, t, n=26, seed=0, lamp=120.0):
    """Funken, wo Klinge auf Schild/Klinge trifft (kurz, hell) + kurzer Lichtblitz."""
    rnd = random.Random(seed)
    m = Q.glow_mat(f"{name}_m", (1.0, 0.75, 0.4), 30.0)
    loc = Vector(loc)
    for k in range(n):
        d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.2, 1.0))).normalized()
        o = Q.box(f"{name}{k}", loc, (0.006, 0.05, 0.006), m)
        o.rotation_euler = d.to_track_quat("Y", "Z").to_euler()
        o.visible_shadow = False
        o.scale = (0.001, 0.001, 0.001)
        o.keyframe_insert("scale", frame=max(1, Q.T(t) - 1))
        o.keyframe_insert("location", frame=max(1, Q.T(t)))
        o.scale = (1, 1, 1)
        o.keyframe_insert("scale", frame=max(1, Q.T(t)))
        sp = rnd.uniform(2.0, 5.0)
        dur = rnd.uniform(0.15, 0.35)
        o.location = loc + d * sp * dur + Vector((0, 0, -4.9 * dur * dur))
        o.keyframe_insert("location", frame=Q.T(t + dur))
        o.scale = (0.001, 0.001, 0.001)
        o.keyframe_insert("scale", frame=Q.T(t + dur) + 1)
    lt = Q.point(f"{name}_l", loc, 0.0, color=(1.0, 0.75, 0.45), radius=0.05)
    lt.data.keyframe_insert("energy", frame=max(1, Q.T(t) - 1))
    lt.data.energy = lamp
    lt.data.keyframe_insert("energy", frame=max(1, Q.T(t)))
    lt.data.energy = 0.0
    lt.data.keyframe_insert("energy", frame=Q.T(t + 0.12))


# ---------------------------------------------------------------- Mondsichel (Ramadan)
def crescent(name, loc, size=6.0, face=None, strength=6.0):
    """Schmale Mondsichel als flache, leuchtende Form (zeigt zur Kamera)."""
    bm = bmesh.new()
    n = 40
    outer = [Vector((math.cos(a), math.sin(a), 0)) for a in [math.pi * (-0.5 + i / n) for i in range(n + 1)]]
    inner = [Vector((0.25 + 0.78 * math.cos(a), 0.96 * math.sin(a), 0)) for a in [math.pi * (-0.5 + i / n) for i in range(n + 1)]]
    vo = [bm.verts.new(p * size) for p in outer]
    vi = [bm.verts.new(p * size) for p in inner]
    for i in range(n):
        bm.faces.new((vo[i], vo[i + 1], vi[i + 1], vi[i]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(Q.glow_mat(f"{name}_m", (1.0, 0.95, 0.82), strength))
    o = bpy.data.objects.new(name, me)
    Q.link(o)
    o.location = loc
    o.visible_shadow = False
    o["person"] = 1
    if face is not None:
        c = o.constraints.new("TRACK_TO")
        c.target = face
        c.track_axis = "TRACK_Z"
        c.up_axis = "UP_Y"
    return o


def sleeper(name, loc, yaw, seed=0, side=1):
    """Schlafender: liegt auf dem Rücken, in den Umhang gehüllt, Arme auf der Brust."""
    rnd = random.Random(seed)
    P = Q.person(name, (loc[0], loc[1], gz(loc[0], loc[1]) + 0.16), yaw=0.0, seed=seed, head=rnd.choice(["turban", "scarf"]),
                 robe=rnd.choice(MROBES), wrap=rnd.choice(MWRAPS), cloak=rnd.choice([(0.3, 0.24, 0.18), (0.42, 0.35, 0.26), (0.2, 0.17, 0.14)]))
    P["root"].rotation_euler = (math.radians(-90), math.radians(6 * side), yaw)
    Q.arm_pose(P, 0, "L", -25, -100, sh_y=15)
    Q.arm_pose(P, 0, "R", -25, -100, sh_y=-15)
    P["neck"].rotation_euler = (math.radians(-12), 0, math.radians(20 * side))
    return P
