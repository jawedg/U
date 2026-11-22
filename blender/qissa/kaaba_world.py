# QISSAH Folge 3 – „Die Erbauer der Kaaba“: Bausteine (Tal von Mekka Jahre später, Ismails Haus mit Türschwelle, Ziegen,
# Zamzam-Brunnen, Grab, Pfeile + Bogen, Essen, Bau des Hauses Stein auf Stein, Maqam-Stein; Kaaba + Maqam Ibrahim heute).
# Welt des Tals aus mekka.py (Folge 2). Regeln: Ibrahim + Ismail NUR als Licht, Menschen ohne Gesicht.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
import lib as Q
import mekka as MK

M = {}
gz = MK.ground_z
SP = MK.SPRING           # Zamzam (jetzt Brunnen)
TREE = MK.TREE           # großer Baum nahe Zamzam (Bukhari 3364: „unter einem großen Baum nahe Zamzam“)
HILL = MK.HILLOCK        # Hügel: hier bauen Ibrahim und Ismail das Haus
HUT = Vector((12.5, 3.0, 0.0))     # Ismails Haus
HUT_LOOK = Vector((-6.0, 17.0))    # Tür schaut nach Nordwesten (Weg ins Tal, auf dem Ibrahim kommt)
GRAVE = Vector((-19.0, -13.5, 0.0))
PATH_N = [(-18.0, 64.0), (-16.0, 50.0), (-12.0, 34.0), (-8.5, 22.0), (-3.0, 10.0), (2.5, 0.0)]   # Weg vom Pass ins Tal


def mats():
    MK.mats()
    M["drystone"] = Q.pbr("k_drystone", (0.34, 0.28, 0.23), 0.95, var=0.5, scale=2.5, bump=0.8, bscale=5, brick=0.13, grime=0.45)
    M["thresh"] = Q.pbr("k_thresh", (0.62, 0.53, 0.41), 0.6, var=0.4, scale=3, bump=0.5, bscale=9, spec=0.5)
    M["earth"] = Q.pbr("k_earth", (0.42, 0.32, 0.23), 1.0, var=0.25, scale=3, bump=0.25, bscale=20)
    M["beam"] = Q.pbr("k_beam", (0.22, 0.15, 0.09), 0.8, var=0.3, scale=6, bump=0.35, bscale=30, rings=12)
    M["frond"] = Q.pbr("k_frond", (0.42, 0.34, 0.2), 0.9, var=0.3, scale=8, rings=70)
    M["clay"] = Q.pbr("k_clay", (0.55, 0.32, 0.19), 0.8, var=0.2, scale=6, bump=0.15, bscale=25)
    M["clay2"] = Q.pbr("k_clay2", (0.66, 0.5, 0.36), 0.85, var=0.2, scale=6, bump=0.15, bscale=25)
    M["meat"] = Q.pbr("k_meat", (0.24, 0.12, 0.06), 0.5, var=0.35, scale=14, bump=0.6, bscale=50, spec=0.45)
    M["meat2"] = Q.pbr("k_meat2", (0.36, 0.21, 0.11), 0.55, var=0.35, scale=14, bump=0.6, bscale=50, spec=0.4)
    M["goat"] = Q.pbr("k_goat", (0.08, 0.065, 0.055), 0.9, var=0.2, scale=6, bump=0.3, bscale=60)
    M["goat2"] = Q.pbr("k_goat2", (0.36, 0.25, 0.16), 0.9, var=0.25, scale=6, bump=0.3, bscale=60)
    M["goat3"] = Q.pbr("k_goat3", (0.62, 0.57, 0.5), 0.9, var=0.2, scale=6, bump=0.3, bscale=60)
    M["horn"] = Q.pbr("k_horn", (0.25, 0.22, 0.18), 0.5, var=0.2, scale=10)
    M["granite"] = Q.pbr("k_granite", (0.31, 0.27, 0.24), 0.85, var=0.4, scale=6, bump=0.45, bscale=14, spec=0.3)
    M["granite2"] = Q.pbr("k_granite2", (0.39, 0.33, 0.28), 0.85, var=0.4, scale=6, bump=0.45, bscale=14, spec=0.3)
    M["maqam"] = Q.pbr("k_maqam", (0.66, 0.56, 0.42), 0.8, var=0.3, scale=5, bump=0.35, bscale=16)
    M["shaft"] = Q.pbr("k_shaft", (0.62, 0.5, 0.33), 0.6, var=0.15, scale=20)
    M["feather"] = Q.pbr("k_feather", (0.85, 0.82, 0.75), 0.9, var=0.2, scale=20)
    M["water"] = MK.water_mat("k_water", (0.05, 0.09, 0.1), 0.95)
    M["ash"] = Q.pbr("k_ash", (0.12, 0.11, 0.1), 1.0, var=0.3, scale=8)
    M["tent3"] = Q.pbr("k_tent3", (0.28, 0.19, 0.12), 0.95, var=0.3, scale=3, bump=0.3, bscale=40)
    M["dough"] = Q.pbr("k_cushion", (0.45, 0.16, 0.1), 0.95, var=0.25, scale=6, bump=0.2, bscale=40)
    return M


def R2(yaw):
    c, s = math.cos(yaw), math.sin(yaw)
    return lambda x, y: (x * c - y * s, x * s + y * c)


# ---------------------------------------------------------------- Ismails Haus (Trockenmauer, Holztür, Steinschwelle)
HUT_W, HUT_D, HUT_H, WALL = 3.6, 3.4, 2.15, 0.42


def hut(name="hut", loc=HUT, look=HUT_LOOK, lamp=False, door_open=1.0, tidy=True, seed=0):
    """Kleines Steinhaus. Lokal: Tür in der Wand bei -Y (Blick der Tür = lokal -Y). Rückgabe: Weltpunkte + Objekte."""
    yaw = Q.face_yaw((loc.x, loc.y), (look.x, look.y))
    z0 = gz(loc.x, loc.y)
    root = Q.empty(name, (loc.x, loc.y, z0), rot=(0, 0, yaw))
    w, d, h, t = HUT_W, HUT_D, HUT_H, WALL
    ms = M["drystone"]
    # Wände (Fundament reicht in den Boden)
    Q.box(f"{name}_wb", (0, d / 2 - t / 2, h / 2 - 0.15), (w, t, h + 0.3), ms, parent=root, bevel=0.04, jitter=0.03, seed=seed)
    for s_ in (-1, 1):
        Q.box(f"{name}_ws{s_}", (s_ * (w / 2 - t / 2), 0, h / 2 - 0.15), (t, d, h + 0.3), ms, parent=root, bevel=0.04, jitter=0.03,
              seed=seed + 2 + s_)
    dw, dh = 0.98, 1.7
    side = (w - dw) / 2
    for s_ in (-1, 1):
        Q.box(f"{name}_wf{s_}", (s_ * (dw / 2 + side / 2), -d / 2 + t / 2, h / 2 - 0.15), (side, t, h + 0.3), ms, parent=root, bevel=0.04,
              jitter=0.03, seed=seed + 7 + s_)
    Q.box(f"{name}_wl", (0, -d / 2 + t / 2, (dh + h) / 2 + 0.05), (dw + 0.02, t, h - dh + 0.1), ms, parent=root, bevel=0.03, jitter=0.02,
          seed=seed + 11)
    # Türrahmen (Holz), Sturz
    for s_ in (-1, 1):
        Q.box(f"{name}_jamb{s_}", (s_ * (dw / 2 + 0.05), -d / 2 + t / 2, dh / 2 + 0.07), (0.1, t + 0.04, dh), M["beam"], parent=root,
              bevel=0.012)
    Q.box(f"{name}_lintel", (0, -d / 2 + t / 2, dh + 0.12), (dw + 0.5, t + 0.06, 0.16), M["beam"], parent=root, bevel=0.015)
    # DIE SCHWELLE: abgetretene Steinplatte quer in der Türöffnung
    th = Q.box(f"{name}_threshold", (0, -d / 2 + t / 2 - 0.03, 0.08), (dw + 0.26, t + 0.2, 0.18), M["thresh"], parent=root, bevel=0.05,
               jitter=0.012, seed=seed + 13)
    # Holztür (nach innen offen, Angel links)
    hinge = Q.empty(f"{name}_hinge", (-dw / 2 + 0.02, -d / 2 + t - 0.02, 0.16), root, rot=(0, 0, math.radians(-100 * door_open)))
    Q.box(f"{name}_door", (dw / 2 - 0.03, 0.025, (dh - 0.1) / 2), (dw - 0.06, 0.05, dh - 0.12), M["beam"], parent=hinge, bevel=0.01)
    for k in range(3):
        Q.box(f"{name}_dbar{k}", (dw / 2 - 0.03, 0.06, 0.2 + k * 0.6), (dw - 0.1, 0.03, 0.08), MK.M["wood"], parent=hinge, bevel=0.005)
    # Dach: Balken + Palmwedel-Matten + Erde
    for k in range(7):
        x = -w / 2 + 0.2 + k * (w - 0.4) / 6
        Q.cyl(f"{name}_rb{k}", (x, 0, h + 0.05), 0.07, d + 0.35, M["beam"], seg=8, rot=(math.pi / 2, 0, 0), parent=root)
    Q.box(f"{name}_mat", (0, 0, h + 0.15), (w + 0.1, d + 0.1, 0.06), M["frond"], parent=root)
    Q.box(f"{name}_roof", (0, 0, h + 0.27), (w + 0.2, d + 0.2, 0.18), M["earth"], parent=root, bevel=0.06, jitter=0.03, seed=seed + 5)
    # Boden innen
    Q.box(f"{name}_floor", (0, 0, 0.03), (w - 2 * t + 0.02, d - 2 * t + 0.02, 0.06), M["earth"], parent=root)
    out = {"root": root, "yaw": yaw, "z": z0, "threshold": th}
    if tidy:
        inside(name, root, seed)
    if lamp:
        L = Q.oil_lamp(f"{name}_lamp", (w / 2 - t - 0.12, d / 2 - t - 0.35, 1.05), parent=root, energy=30.0)
        Q.box(f"{name}_niche", (w / 2 - t - 0.1, d / 2 - t - 0.35, 1.02), (0.22, 0.4, 0.04), M["beam"], parent=root)
        out["lamp"] = L
    # Licht von innen (aufgehellte Schatten, wie Licht von der Tür)
    out["fill"] = Q.point(f"{name}_fill", (0, 0.2, 1.6), 25.0, color=(1.0, 0.8, 0.6), radius=0.6, parent=root)
    rot = R2(yaw)

    def world(lx, ly, lz=0.0):
        dx, dy = rot(lx, ly)
        return (loc.x + dx, loc.y + dy, z0 + lz)
    out["world"] = world
    out["door"] = world(0, -d / 2 + t / 2, 0)
    out["front"] = world(0, -d / 2 - 1.9, 0)
    return out


def inside(name, root, seed=0):
    """Einrichtung: Matten, Kissen, Wasserkrug, Schalen, Korb, Wasserschlauch an der Wand, Bogen an der Wand."""
    w, d, t = HUT_W, HUT_D, WALL
    MK.rug(f"{name}_rug1", (-0.55, 0.45, 0.06), (1.5, 1.1), rot=0.05, mat=M["frond"]).parent = root
    MK.rug(f"{name}_rug2", (0.7, 0.75, 0.06), (1.2, 0.9), rot=-0.1, mat=MK.M["blanket_r"]).parent = root
    Q.ball(f"{name}_cush", (-w / 2 + t + 0.3, 0.6, 0.18), (0.22, 0.4, 0.12), M["dough"], parent=root, seg=14)
    jug(f"{name}_jug", (w / 2 - t - 0.25, -0.2, 0.06), parent=root)
    Q.cyl(f"{name}_basket", (w / 2 - t - 0.3, 0.45, 0.2), 0.2, 0.3, MK.M["mat"], seg=16, parent=root, r2=0.24)
    ws = MK.waterskin(f"{name}_skin", (-w / 2 + t + 0.15, -0.7, 0.9), full=True, rot=1.57)
    ws.parent = root
    ws.rotation_euler = (math.radians(70), 0, math.radians(90))
    bow(f"{name}_bow", (0.4, d / 2 - t - 0.05, 1.2), parent=root, rot=(math.radians(90), 0, 0))


def jug(name, loc, parent=None, scale=1.0):
    root = Q.empty(name, loc, parent)
    root.scale = (scale, scale, scale)
    Q.loft(f"{name}_b", [(0.0, 0.07, 0.07), (0.05, 0.12, 0.12), (0.16, 0.15, 0.15), (0.3, 0.12, 0.12), (0.38, 0.06, 0.06),
                         (0.44, 0.055, 0.055), (0.46, 0.07, 0.07)], M["clay2"], parent=root, seg=20, cap_top=False)
    Q.torus(f"{name}_h", (0.12, 0, 0.32), 0.06, 0.012, M["clay2"], parent=root).rotation_euler = (math.pi / 2, 0, 0)
    return root


def bowl(name, loc, parent=None, meat=True, r=0.17, seed=0):
    """Holzschale, optional mit Fleischstücken."""
    root = Q.empty(name, loc, parent)
    Q.loft(f"{name}_b", [(0.0, 0.0, 0.0), (0.0, r * 0.45, r * 0.45), (0.03, r * 0.8, r * 0.8), (0.07, r, r), (0.085, r * 1.02, r * 1.02)],
           MK.M["wood"], parent=root, seg=24, cap_top=False)
    if meat:
        rnd = random.Random(seed)
        for k in range(9):
            a = rnd.uniform(0, 6.28)
            rr = rnd.uniform(0, r * 0.62)
            Q.ball(f"{name}_m{k}", (rr * math.cos(a), rr * math.sin(a), 0.05 + rnd.uniform(0, 0.025)),
                   (rnd.uniform(0.04, 0.065), rnd.uniform(0.022, 0.035), rnd.uniform(0.014, 0.02)), M["meat"] if k % 3 else M["meat2"],
                   parent=root, seg=10).rotation_euler = (rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), a)
    return root


def cup(name, loc, parent=None, water=True):
    root = Q.empty(name, loc, parent)
    Q.loft(f"{name}_b", [(0.0, 0.0, 0.0), (0.0, 0.045, 0.045), (0.02, 0.06, 0.06), (0.09, 0.065, 0.065), (0.1, 0.068, 0.068)],
           M["clay"], parent=root, seg=20, cap_top=False)
    if water:
        Q.cyl(f"{name}_w", (0, 0, 0.082), 0.06, 0.004, M["water"], seg=20, parent=root)
    return root


def bow(name, loc, parent=None, rot=(0, 0, 0)):
    """Bogen (gebogenes Holz + Sehne). Lokal: Bogen in der XZ-Ebene."""
    root = Q.empty(name, loc, parent, rot=rot)
    pts = []
    for k in range(9):
        u = -1 + 2 * k / 8
        pts.append(Vector((u * 0.6, 0, 0.12 * (1 - u * u))))
    for k in range(8):
        Q.limb(f"{name}_s{k}", pts[k], pts[k + 1], 0.014, 0.014, MK.M["wood"], seg=6, parent=root)
    Q.limb(f"{name}_str", pts[0], pts[-1], 0.003, 0.003, MK.M["rope"], seg=4, parent=root)
    return root


def arrow(name, loc, parent=None, rot=(0, 0, 0), length=0.75, done=True):
    root = Q.empty(name, loc, parent, rot=rot)
    Q.limb(f"{name}_sh", (0, -length / 2, 0), (0, length / 2, 0), 0.0065, 0.0065, M["shaft"], seg=6, parent=root)
    if done:
        Q.cyl(f"{name}_tip", (0, -length / 2 - 0.03, 0), 0.012, 0.06, M["granite"], seg=6, rot=(math.pi / 2, 0, 0), parent=root, r2=0.0)
        for k in range(3):
            f = Q.box(f"{name}_f{k}", (0, length / 2 - 0.07, 0), (0.002, 0.11, 0.028), M["feather"], parent=root)
            f.rotation_euler = (0, k * 2.09, 0)
    return root


# ---------------------------------------------------------------- Tiere
def goat(name, loc, yaw=0.0, seed=0, scale=1.0, kid=False):
    """Ziege (Blick lokal -Y). Gelenke: neck (Kopf senkt sich zum Grasen)."""
    rnd = random.Random(seed)
    mg = [M["goat"], M["goat2"], M["goat3"]][seed % 3]
    s = scale * (0.65 if kid else 1.0)
    root = Q.empty(f"{name}_root", loc, rot=(0, 0, yaw))
    root.scale = (s, s, s)
    body = Q.empty(f"{name}_body", (0, 0, 0.55), root)
    Q.ball(f"{name}_torso", (0, 0, 0), (0.17, 0.4, 0.19), mg, parent=body, seg=18)
    Q.ball(f"{name}_chest", (0, -0.26, 0.02), (0.16, 0.18, 0.19), mg, parent=body, seg=14)
    neck = Q.empty(f"{name}_neck", (0, -0.36, 0.08), body)
    Q.limb(f"{name}_nk", (0, 0, 0), (0, -0.14, 0.2), 0.08, 0.06, mg, seg=10, parent=neck)
    head = Q.empty(f"{name}_head", (0, -0.16, 0.24), neck)
    Q.ball(f"{name}_skull", (0, -0.06, 0), (0.065, 0.1, 0.07), mg, parent=head, seg=12)
    Q.ball(f"{name}_snout", (0, -0.17, -0.04), (0.045, 0.07, 0.045), mg, parent=head, seg=10)
    for s_ in (-1, 1):
        Q.ball(f"{name}_ear{s_}", (0.08 * s_, -0.02, 0.02), (0.06, 0.02, 0.025), mg, parent=head, seg=8).rotation_euler = (0, 0.5 * s_, 0)
        if not kid:
            Q.limb(f"{name}_hn{s_}", (0.03 * s_, -0.03, 0.06), (0.05 * s_, 0.1, 0.17), 0.016, 0.006, M["horn"], seg=6, parent=head)
    Q.limb(f"{name}_beard", (0, -0.17, -0.08), (0, -0.15, -0.16), 0.015, 0.004, mg, seg=6, parent=head)
    legs = {}
    for nm, (x, y) in (("FL", (-0.09, -0.27)), ("FR", (0.09, -0.27)), ("BL", (-0.09, 0.28)), ("BR", (0.09, 0.28))):
        hp = Q.empty(f"{name}_leg.{nm}", (x, y, -0.1), body)
        Q.limb(f"{name}_l.{nm}", (0, 0, 0.05), (0, 0.01, -0.45), 0.035, 0.018, mg, seg=8, parent=hp)
        Q.ball(f"{name}_hoof.{nm}", (0, 0.0, -0.45), (0.022, 0.028, 0.02), M["horn"], parent=hp, seg=8)
        legs[nm] = hp
    Q.limb(f"{name}_tail", (0, 0.38, 0.08), (0, 0.44, 0.2), 0.02, 0.01, mg, seg=6, parent=body)
    Q.blob(f"{name}_blob", root, 0.35)
    root["person"] = 1
    return {"root": root, "body": body, "neck": neck, "head": head, "legs": legs, "seed": seed}


def goat_graze(G, t0, t1, wander=0.6):
    """Grasen: Kopf runter/hoch, kleine Schritte, Schwanz wackelt."""
    rnd = random.Random(G["seed"] * 7 + 1)
    root, neck = G["root"], G["neck"]
    base = root.location.copy()
    yaw0 = root.rotation_euler.z
    t = t0
    while t < t1 + 2.0:
        down = rnd.random() < 0.6
        neck.rotation_euler = (math.radians(rnd.uniform(55, 75) if down else rnd.uniform(-10, 10)), 0, math.radians(rnd.uniform(-15, 15)))
        neck.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))
        neck.keyframe_insert("rotation_euler", frame=max(1, Q.T(t + rnd.uniform(1.2, 3.0))))
        if rnd.random() < 0.35:
            a = yaw0 + rnd.uniform(-0.6, 0.6)
            step = rnd.uniform(0.15, wander)
            base = base + Vector((-math.sin(a) * step, math.cos(a) * -step, 0))
            base.z = gz(base.x, base.y)
            root.keyframe_insert("location", frame=max(1, Q.T(t)))
            root.location = base
            root.keyframe_insert("location", frame=max(1, Q.T(t + 0.9)))
        t += rnd.uniform(1.6, 3.6)


def herd(name, center, n, seed=0, spread=4.0, t1=30.0):
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(0, spread)
        x, y = center[0] + r * math.cos(a), center[1] + r * math.sin(a)
        G = goat(f"{name}{k}", (x, y, gz(x, y)), yaw=rnd.uniform(0, 6.28), seed=seed + k, kid=rnd.random() < 0.25)
        goat_graze(G, 0, t1)
        out.append(G)
    return out


# ---------------------------------------------------------------- Zamzam-Brunnen, Grab, Feuer mit Topf
def well(name="well", loc=SP):
    """Zamzam Jahre später: Ring aus Steinen um die Quelle, Wasser darin, Holzgestell mit Seil + Ledereimer."""
    z = gz(loc.x, loc.y)
    root = Q.empty(name, (loc.x, loc.y, z))
    rnd = random.Random(4)
    for ring in range(3):
        n = 16
        for k in range(n):
            a = 2 * math.pi * (k + 0.5 * (ring % 2)) / n
            r = 0.95
            Q.box(f"{name}_s{ring}_{k}", (r * math.cos(a), r * math.sin(a), 0.1 + ring * 0.19), (0.34, 0.28, 0.2),
                  M["granite2"] if (k + ring) % 3 else M["granite"], rot=(0, 0, a + math.pi / 2), parent=root, bevel=0.03,
                  jitter=0.025, seed=ring * 50 + k)
    Q.cyl(f"{name}_water", (0, 0, 0.08), 0.8, 0.02, M["water"], seg=40, parent=root)
    Q.cyl(f"{name}_wetring", (0, 0, 0.005), 1.6, 0.01, MK.M["wet"], seg=40, parent=root)
    top = Vector((0, 0, 2.1))
    for k in range(3):
        a = k * 2.094 + 0.3
        Q.limb(f"{name}_leg{k}", (1.25 * math.cos(a), 1.25 * math.sin(a), 0), top, 0.05, 0.04, M["beam"], seg=8, parent=root)
    Q.limb(f"{name}_rope", top, (0.1, 0.0, 0.85), 0.008, 0.008, MK.M["rope"], seg=4, parent=root)
    Q.cyl(f"{name}_bucket", (0.1, 0.0, 0.72), 0.13, 0.24, MK.M["leather"], seg=14, parent=root, r2=0.15)
    return root


def grave(name="grave", loc=GRAVE, yaw=0.4):
    z = gz(loc.x, loc.y)
    root = Q.empty(name, (loc.x, loc.y, z), rot=(0, 0, yaw))
    Q.ball(f"{name}_mound", (0, 0, 0.02), (0.55, 1.05, 0.2), M["earth"], parent=root, seg=18)
    rnd = random.Random(8)
    for k in range(18):
        a = 2 * math.pi * k / 18
        Q.ball(f"{name}_st{k}", (0.68 * math.cos(a), 1.2 * math.sin(a), 0.04), (rnd.uniform(0.07, 0.11), rnd.uniform(0.06, 0.1), 0.06),
               M["granite2"], parent=root, seg=8)
    Q.box(f"{name}_head", (0, -1.12, 0.25), (0.32, 0.1, 0.5), M["granite"], parent=root, bevel=0.03, jitter=0.03, seed=3)
    Q.box(f"{name}_foot", (0, 1.12, 0.14), (0.24, 0.09, 0.28), M["granite"], parent=root, bevel=0.03, jitter=0.03, seed=4)
    return root


def cook_fire(name, loc, energy=45.0, pot=True):
    F = MK.campfire(name, loc, energy=energy)
    if pot:
        F["flame"].scale = (0.7, 0.7, 0.45)
        for k in range(3):
            a = k * 2.094
            Q.box(f"{name}_ps{k}", (0.24 * math.cos(a), 0.24 * math.sin(a), 0.13), (0.14, 0.12, 0.26), M["granite"], parent=F["root"],
                  rot=(0, 0, a), bevel=0.02, jitter=0.02, seed=k)
        Q.loft(f"{name}_pot", [(0.0, 0.06, 0.06), (0.05, 0.16, 0.16), (0.16, 0.2, 0.2), (0.27, 0.16, 0.16), (0.31, 0.14, 0.14)],
               M["clay"], parent=F["root"], seg=20, cap_top=False).location = (0, 0, 0.27)
        Q.cyl(f"{name}_broth", (0, 0, 0.53), 0.135, 0.01, Q.pbr("k_broth", (0.3, 0.17, 0.08), 0.2, spec=0.6), seg=20, parent=F["root"])
    return F


def tents(n=16, seed=21, avoid=(), fire_lights=True):
    """Zelte der Dschurhum rings um Zamzam (schwarze Ziegenhaar-Zelte + helle), mit Feuern, sitzenden Kamelen, Holz, Säcken."""
    rnd = random.Random(seed)
    spots = []
    tries = 0
    while len(spots) < n and tries < 2000:
        tries += 1
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(10, 40)
        x, y = SP.x + r * math.cos(a), SP.y + r * 0.85 * math.sin(a)
        p = Vector((x, y))
        bad = (p - HILL.xy).length < 11 or (p - TREE.xy).length < 7 or (p - HUT.xy).length < 7.5 or (p - GRAVE.xy).length < 4
        bad = bad or any((p - Vector(q[:2])).length < q[2] for q in avoid)
        for (ax, ay), (bx, by) in zip(PATH_N, PATH_N[1:]):
            ab = Vector((bx - ax, by - ay))
            u = max(0.0, min(1.0, (p - Vector((ax, ay))).dot(ab) / ab.length_squared))
            if (p - (Vector((ax, ay)) + ab * u)).length < 3.6:
                bad = True
        bad = bad or any((p - Vector(s[:2])).length < 6.2 for s in spots)
        if not bad:
            spots.append((x, y, a))
    for k, (x, y, a) in enumerate(spots):
        T_ = MK.tent(f"tent{k}", (x, y, gz(x, y)), yaw=a + math.pi / 2 + rnd.uniform(-0.4, 0.4), w=rnd.uniform(3.4, 5.2),
                     d=rnd.uniform(2.3, 3.1), mat=MK.M["tent"] if k % 3 else M["tent3"], seed=k)
        if k % 2 == 0:
            F = cook_fire(f"fire{k}", (x + 2.6 * math.cos(a), y + 2.6 * math.sin(a), gz(x, y)), energy=30.0, pot=k % 4 == 0)
            if not fire_lights:  # am Tag unsichtbar, kostet aber je Bildpunkt Rechenzeit
                bpy.data.objects.remove(F["light"])
        if k % 3 == 1:
            MK.camel(f"cm{k}", (x - 2.6 * math.sin(a), y + 2.6 * math.cos(a), gz(x, y)), yaw=a + 1.2, seed=k, load=False, sit=True)
        if k % 3 == 2:
            for j in range(4):
                Q.cyl(f"wood{k}_{j}", (x + 1.5 * math.cos(a + 0.8), y + 1.5 * math.sin(a + 0.8), gz(x, y) + 0.05 + 0.06 * (j % 2)), 0.04, 1.1,
                      MK.M["wood"], seg=6, rot=(math.pi / 2, 0, a + j * 0.25))
        MK.dates_bag(f"bag{k}", (x + 1.0 * math.cos(a - 0.6), y + 1.0 * math.sin(a - 0.6), gz(x, y) + 0.02))
    return spots


def villagers(spots, t1, seed=31, n=14, near=None):
    """Leute im Lager: sitzen am Feuer, stehen, gehen kurze Wege (ohne Gesicht)."""
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        x, y, a = spots[k % len(spots)]
        woman = rnd.random() < 0.45
        px, py = x + rnd.uniform(1.6, 3.2) * math.cos(a + rnd.uniform(-1, 1)), y + rnd.uniform(1.6, 3.2) * math.sin(a + rnd.uniform(-1, 1))
        sit = rnd.random() < 0.45
        P_ = Q.person(f"vl{k}", (px, py, gz(px, py)), yaw=rnd.uniform(0, 6.28), sit=sit, seed=300 + k,
                      head="khimar" if woman else rnd.choice(["turban", "scarf", "turban"]),
                      height=rnd.uniform(0.9, 1.04) if not woman else rnd.uniform(0.88, 0.96))
        if not sit and rnd.random() < 0.5:
            b = (px + rnd.uniform(-6, 6), py + rnd.uniform(-6, 6))
            t_ = Q.walk(P_, [(px, py), b], rnd.uniform(0, 3), speed=rnd.uniform(0.8, 1.1))
            if t_ < t1:
                Q.walk(P_, [b, (px, py)], t_ + rnd.uniform(1, 3), speed=rnd.uniform(0.8, 1.1))
        else:
            Q.idle(P_, 0, t1, seed=k)
        out.append(P_)
    return out


def path_life(t1, seed=41, n_down=3, n_up=3, camel=True, kids=True):
    """Leben auf dem Weg ins Tal: Leute gehen hinab und herauf (seitlich versetzt), ein Mann führt ein Kamel, Kinder laufen."""
    rnd = random.Random(seed)
    pts = [Vector(p) for p in PATH_N]
    out = []

    def along(off, rev=False):
        ps = list(reversed(pts)) if rev else pts
        res = []
        for i, p in enumerate(ps):
            q = ps[min(i + 1, len(ps) - 1)] - ps[max(i - 1, 0)]
            nrm = Vector((-q.y, q.x)).normalized()
            res.append((p.x + nrm.x * off, p.y + nrm.y * off))
        return res
    for k in range(n_down + n_up):
        up = k >= n_down
        off = rnd.choice([-1, 1]) * rnd.uniform(1.4, 2.4)
        path = along(off, rev=up)
        # Startpunkt irgendwo auf dem Weg
        cut = rnd.randint(0, 2)
        path = path[cut:]
        woman = rnd.random() < 0.4
        P_ = Q.person(f"pl{k}", (path[0][0], path[0][1], gz(*path[0])), seed=600 + k, head="khimar" if woman else "turban",
                      height=rnd.uniform(0.9, 1.03))
        Q.walk(P_, path, rnd.uniform(-6, 2), speed=rnd.uniform(0.95, 1.2))
        if woman and rnd.random() < 0.7:  # Krug auf der Schulter
            jug(f"pl{k}_jug", (0.12, 0.0, 0.62), parent=P_["chest"], scale=0.8)
        out.append(P_)
    if camel:
        a = (SP.x + 22.0, SP.y + 18.0)
        b = (SP.x - 6.0, SP.y + 9.0)
        C = MK.camel("pcm", (a[0], a[1], gz(*a)), seed=5, load=True)
        MK.camel_walk(C, [a, b], 0.0, speed=0.9)
        L_ = Q.person("pcm_lead", (a[0] - 1.6, a[1] - 0.6, gz(*a)), seed=650, head="turban")
        Q.walk(L_, [(a[0] - 1.6, a[1] - 0.6), (b[0] - 1.6, b[1] - 0.6)], 0.0, speed=0.9)
        Q.limb("pcm_rope", (0, -0.9, 1.6), (0, -1.5, 1.0), 0.008, 0.008, MK.M["rope"], seg=4, parent=C["root"])
    if kids:
        for k in range(3):
            c = (SP.x + rnd.uniform(-14, 10), SP.y + rnd.uniform(10, 22))
            K_ = Q.person(f"kid{k}", (c[0], c[1], gz(*c)), seed=680 + k, head=rnd.choice(["cap", "bare"]), height=0.62)
            pts_k = [c] + [(c[0] + rnd.uniform(-7, 7), c[1] + rnd.uniform(-5, 5)) for _ in range(4)]
            Q.walk(K_, pts_k, rnd.uniform(0, 2), speed=2.4, run=True)
    return out


def settle_world(mode="day", stars=0.0, tents_n=26, people=14, goats=True, t1=30.0, seed=21, extra_keep=(), life=True, tent_avoid=(),
                 life_kids=False):
    """Das Tal Jahre später: Gelände + Baum + Safa/Marwa + Hügel (aus Folge 2), Zamzam-Brunnen, Zelte, Leute, Ziegen."""
    import os
    if os.environ.get("LITE"):  # Test: ohne bewegte Leute/Tiere
        people, life, goats = 0, False, False
    if os.environ.get("KIDS_ALL"):  # Test: Kinder überall (Prüfung der alten Fassung)
        life_kids = True
    L = MK.light(mode, stars=stars)
    mats()
    keep = [(HUT.x, HUT.y, 6.0), (GRAVE.x, GRAVE.y, 3.0), (SP.x, SP.y, 4.0)] + list(extra_keep)
    MK.valley(keep=keep)
    well()
    spots = tents(tents_n, seed=seed, avoid=tent_avoid, fire_lights=mode in ("dusk", "golden"))
    vl = villagers(spots, t1, n=people) if people else []
    if life:
        path_life(t1, kids=life_kids)  # Kinder nur, wo es passt (Nutzer: Kind rannte sinnlos vor die Tür)
    if goats:
        herd("gA", (SP.x + 16, SP.y + 14), 6, seed=1, t1=t1)
        herd("gB", (SP.x - 18, SP.y + 22), 5, seed=7, t1=t1)
        herd("gC", (HUT.x + 5, HUT.y + 6), 3, seed=13, t1=t1)
    return L, spots, vl


# ---------------------------------------------------------------- Der Bau des Hauses (Bukhari 3364: Ismail bringt Steine, Ibrahim baut)
KA_W, KA_D, KA_T, COURSE, N_COURSES = 5.2, 6.4, 0.7, 0.3, 15
DOOR_SIDE_W = 1.4


def hillock_z(x, y):
    """Oberfläche des Hügelchens (wie MK.hillock) bzw. Gelände."""
    rr = math.hypot(x - HILL.x, (y - HILL.y) / 0.85)
    u = min(1.0, max(0.0, (7.3 - rr) / 7.0))
    return max(gz(x, y), 1.3 * math.sin(u * math.pi / 2) ** 1.5 - 0.15)


def hill_top_z():
    return 1.1


def _stone_block(bm, cx, cy, cz, L, Dd, H, along_x, rnd):
    g = bmesh.ops.create_cube(bm, size=1.0)
    sx, sy = (L, Dd) if along_x else (Dd, L)
    for v in g["verts"]:
        v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * H))
        v.co += Vector((rnd.uniform(-1, 1) * 0.025, rnd.uniform(-1, 1) * 0.025, rnd.uniform(-1, 1) * 0.03))
        v.co += Vector((cx, cy, cz))


def walls(name="ka", t_of=None, n_courses=N_COURSES, chunks_per_side=3, built_to=None):
    """Mauern aus Granit-Blöcken (Trockenmauer), Lage für Lage. t_of(lage, stück, n_stücke) -> Zeit, ab der das Stück steht
    (None = von Anfang an). built_to = so viele Lagen stehen schon (ohne Animation). Rückgabe: Liste (lage, stück, Objekt, Zeit)."""
    z0 = hill_top_z() - 0.6   # Fundament reicht in den Hügel
    cx, cy = HILL.x, HILL.y
    rnd = random.Random(5)
    hw, hd, t = KA_W / 2, KA_D / 2, KA_T
    # Umfang als Strecken (gegen den Uhrzeigersinn, wie beim Umrunden), Tür-Lücke in der Ostseite (unten)
    sides = [((cx + hw, cy - hd), (cx + hw, cy + hd), True), ((cx + hw, cy + hd), (cx - hw, cy + hd), False),
             ((cx - hw, cy + hd), (cx - hw, cy - hd), True), ((cx - hw, cy - hd), (cx + hw, cy - hd), False)]
    out = []
    n_ch = 4 * chunks_per_side
    for c in range(n_courses):
        zc = z0 + (c + 0.5) * COURSE + (0.6 if c > 0 else 0.0) * 0
        z_c = z0 + c * COURSE + COURSE / 2
        k = 0
        for si, (a, b, is_x_side) in enumerate(sides):
            a, b = Vector(a), Vector(b)
            for ch in range(chunks_per_side):
                p0 = a + (b - a) * (ch / chunks_per_side)
                p1 = a + (b - a) * ((ch + 1) / chunks_per_side)
                bm = bmesh.new()
                Lseg = (p1 - p0).length
                dirv = (p1 - p0).normalized()
                pos = 0.0
                offs = 0.3 * (c % 2)
                first = True
                while pos < Lseg - 0.05:
                    Ls = rnd.uniform(0.45, 0.8) if not first else offs + 0.3
                    first = False
                    Ls = min(Ls, Lseg - pos)
                    mid = p0 + dirv * (pos + Ls / 2)
                    # Tür-Lücke: Ostseite (si == 0), Mitte, untere 8 Lagen
                    if si == 0 and abs(mid.y - cy + 0.6) < DOOR_SIDE_W / 2 and c < 8:
                        pos += Ls
                        continue
                    along_x = abs(dirv.x) > abs(dirv.y)
                    _stone_block(bm, mid.x, mid.y, z_c, Ls - 0.02, t + rnd.uniform(-0.04, 0.04), COURSE - 0.015, along_x, rnd)
                    pos += Ls
                me = bpy.data.meshes.new(f"{name}_c{c}_{k}")
                bm.to_mesh(me)
                bm.free()
                me.materials.append(M["granite"] if (c + k) % 3 else M["granite2"])
                o = bpy.data.objects.new(f"{name}_c{c}_{k}", me)
                Q.link(o)
                tk = None
                if built_to is not None and c < built_to:
                    tk = None
                elif t_of is not None:
                    tk = t_of(c, k, n_ch)
                if tk is not None:
                    # Stück erscheint: wächst aus der Lage darunter
                    o.scale = (1, 1, 0.001)
                    o.location = (0, 0, 0)
                    ctr = Vector((0, 0, z_c - COURSE / 2))
                    # Ursprung an die Unterkante legen, damit es nach oben wächst
                    me.transform(Matrix.Translation(-ctr))
                    o.location = ctr
                    o.keyframe_insert("scale", frame=1)
                    o.keyframe_insert("scale", frame=max(1, Q.T(tk)))
                    o.scale = (1, 1, 1)
                    o.keyframe_insert("scale", frame=max(2, Q.T(tk + 0.35)))
                    # vorher unsichtbar (flach gedrückte Lagen sonst als dünne Platten sichtbar)
                    if Q.T(tk) > 1:
                        o.hide_render = True
                        o.keyframe_insert("hide_render", frame=1)
                        o.keyframe_insert("hide_render", frame=Q.T(tk) - 1)
                        o.hide_render = False
                        o.keyframe_insert("hide_render", frame=Q.T(tk))
                elif built_to is not None and c >= built_to:
                    bpy.data.objects.remove(o)
                    k += 1
                    continue
                out.append((c, k, o, tk))
                k += 1
    # Lintel über der Tür (ab Lage 8)
    return out


def side_point(u, out=1.1):
    """Punkt auf dem Umfang (u = 0..1 gegen den Uhrzeigersinn ab Südost-Ecke), out Meter außerhalb der Mauer."""
    hw, hd = KA_W / 2 + KA_T / 2 + out, KA_D / 2 + KA_T / 2 + out
    per = 2 * (2 * hw + 2 * hd)
    s = (u % 1.0) * per / 2
    cx, cy = HILL.x, HILL.y
    pts = [(cx + hw, cy - hd), (cx + hw, cy + hd), (cx - hw, cy + hd), (cx - hw, cy - hd), (cx + hw, cy - hd)]
    acc = 0.0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L_ = math.hypot(bx - ax, by - ay)
        if s <= acc + L_:
            f = (s - acc) / L_
            return (ax + (bx - ax) * f, ay + (by - ay) * f)
        acc += L_
    return pts[-1]


def maqam_stone(name="maqam", loc=None, t_on=None):
    """Der Stein, auf dem Ibrahim beim Bauen stand (Bukhari 3364)."""
    root = Q.empty(name, loc or (0, 0, 0))
    Q.box(f"{name}_s", (0, 0, 0.24), (0.58, 0.5, 0.48), M["maqam"], parent=root, bevel=0.06, jitter=0.03, seed=9)
    # zwei Fußabdrücke oben (flache, dunklere Mulden)
    for s_ in (-1, 1):
        foot(f"{name}_fp{s_}", (0.12 * s_, 0.0, 0.482), parent=root, scale=1.0, mat=Q.pbr("k_fp", (0.4, 0.33, 0.24), 0.9, var=0.3,
             scale=10, bump=0.3, bscale=30))
    if t_on is not None:
        MK.pop_in(root, t_on, dur=0.5)
    return root


def foot(name, loc, parent=None, scale=1.0, mat=None):
    """Fußabdruck-Form (Ferse + Ballen + Zehen) als flache Scheibe – liegt auf einer Oberfläche."""
    bm = bmesh.new()
    pts = []
    for k in range(28):
        a = 2 * math.pi * k / 28
        x = 0.045 * math.cos(a)
        y = 0.12 * math.sin(a)
        if y < 0:
            x *= 0.82
        if y > 0.06:
            x *= 1.12
        pts.append(bm.verts.new((x * scale, (y + 0.01) * scale, 0)))
    bm.faces.new(pts)
    for k in range(5):
        r = 0.016 - 0.0018 * k
        x = (-0.035 + 0.017 * k) * scale
        g = bmesh.ops.create_circle(bm, cap_ends=True, segments=10, radius=r * scale)
        for v in g["verts"]:
            v.co += Vector((x, (0.15 - 0.006 * abs(k - 1)) * scale, 0))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat or M["granite"])
    o = bpy.data.objects.new(name, me)
    Q.link(o)
    o.parent = parent
    o.location = loc
    return o


# ---------------------------------------------------------------- Heute: Kaaba, Hijr Ismail, Maqam Ibrahim, Mataf, Säulengänge, Pilger
K_W, K_D, K_H = 11.0, 12.9, 13.1   # x (Nordost-/Südwestseite), y, Höhe
MAQAM_T = Vector((0.0, -K_D / 2 - 11.0, 0.0))   # vor der Tür (Seite -Y)


def today_mats():
    M["kiswa"] = Q.pbr("k_kiswa", (0.012, 0.012, 0.014), 0.55, var=0.08, scale=3, bump=0.25, bscale=18, spec=0.35)
    M["gold"] = Q.pbr("k_gold", (0.88, 0.66, 0.3), 0.32, metal=0.95, var=0.06, scale=8, bump=0.06, bscale=30)
    M["marble"] = Q.pbr("k_marble", (0.9, 0.89, 0.87), 0.22, var=0.05, scale=1.0, bump=0.01, bscale=8, spec=0.55)
    M["marble_d"] = Q.pbr("k_marble_d", (0.62, 0.6, 0.57), 0.2, var=0.08, scale=2.0, spec=0.6)
    M["glass"] = Q.pbr("k_glass", (0.85, 0.9, 0.92), 0.04, alpha=0.18, spec=0.8)
    M["silver"] = Q.pbr("k_silver", (0.8, 0.8, 0.82), 0.25, metal=0.95, var=0.1, scale=30, bump=0.2, bscale=100)
    M["arc"] = Q.pbr("k_arc", (0.86, 0.82, 0.74), 0.5, var=0.06, scale=1.5, bump=0.05, bscale=10)
    M["lamp"] = Q.glow_mat("k_lamp", (1.0, 0.93, 0.8), 10.0)
    M["white"] = Q.pbr("k_ihram", (0.93, 0.92, 0.89), 0.85, var=0.04, scale=8, bump=0.05, bscale=40)
    M["black"] = Q.pbr("k_abaya", (0.04, 0.04, 0.045), 0.8, var=0.05, scale=8)
    M["stone_core"] = Q.pbr("k_core", (0.7, 0.62, 0.5), 0.8, var=0.3, scale=6, bump=0.3, bscale=20)


def kaaba_today(name="kt"):
    today_mats()
    root = Q.empty(name)
    Q.box(f"{name}_body", (0, 0, K_H / 2), (K_W, K_D, K_H), M["kiswa"], parent=root, bevel=0.05)
    # Kiswa-Falten (leichte senkrechte Bahnen)
    for s_ in (-1, 1):
        for k in range(9):
            x = -K_W / 2 + (k + 0.5) * K_W / 9
            Q.box(f"{name}_fy{s_}_{k}", (x, s_ * (K_D / 2 + 0.012), K_H / 2 - 0.5), (0.05, 0.02, K_H - 1.5), M["kiswa"], parent=root)
        for k in range(10):
            y = -K_D / 2 + (k + 0.5) * K_D / 10
            Q.box(f"{name}_fx{s_}_{k}", (s_ * (K_W / 2 + 0.012), y, K_H / 2 - 0.5), (0.02, 0.05, K_H - 1.5), M["kiswa"], parent=root)
    # goldenes Band (Hizam) auf 2/3 Höhe + Muster
    zb = K_H * 0.68
    Q.box(f"{name}_band", (0, 0, zb), (K_W + 0.06, K_D + 0.06, 0.95), M["gold"], parent=root)
    Q.box(f"{name}_bandk", (0, 0, zb), (K_W + 0.08, K_D + 0.08, 0.7), M["kiswa"], parent=root)
    rnd = random.Random(3)
    for s_ in (-1, 1):
        for k in range(26):
            x = -K_W / 2 + 0.3 + k * (K_W - 0.6) / 25
            Q.box(f"{name}_glyph{s_}_{k}", (x, s_ * (K_D / 2 + 0.05), zb + rnd.uniform(-0.15, 0.15)), (rnd.uniform(0.12, 0.32), 0.02,
                  rnd.uniform(0.12, 0.42)), M["gold"], parent=root)
        for k in range(30):
            y = -K_D / 2 + 0.3 + k * (K_D - 0.6) / 29
            Q.box(f"{name}_glyphx{s_}_{k}", (s_ * (K_W / 2 + 0.05), y, zb + rnd.uniform(-0.15, 0.15)), (0.02, rnd.uniform(0.12, 0.32),
                  rnd.uniform(0.12, 0.42)), M["gold"], parent=root)
    # Tür (Gold) in der Seite -Y, 2,2 m über dem Boden, mit Vorhang darüber
    Q.box(f"{name}_door", (-1.6, -K_D / 2 - 0.08, 2.2 + 1.55), (2.0, 0.14, 3.1), M["gold"], parent=root, bevel=0.02)
    for k in range(6):
        Q.box(f"{name}_dp{k}", (-1.6 + (-0.75 + 0.3 * k), -K_D / 2 - 0.16, 3.75), (0.18, 0.03, 2.6), M["gold"], parent=root)
    Q.box(f"{name}_curtain", (-1.6, -K_D / 2 - 0.05, 6.4), (2.8, 0.04, 2.2), M["kiswa"], parent=root)
    for k in range(5):
        Q.box(f"{name}_cg{k}", (-1.6, -K_D / 2 - 0.08, 5.6 + 0.35 * k), (2.5, 0.02, 0.12), M["gold"], parent=root)
    # Sockel (Shadharwan) aus Marmor
    Q.box(f"{name}_base", (0, 0, 0.2), (K_W + 0.9, K_D + 0.9, 0.4), M["marble_d"], parent=root, bevel=0.15)
    # Schwarzer Stein (Ecke Südost: +x, -y) in Silberfassung
    corner = (K_W / 2, -K_D / 2, 1.5)
    Q.ball(f"{name}_hajar_f", corner, (0.38, 0.38, 0.32), M["silver"], parent=root, seg=20)
    Q.ball(f"{name}_hajar", (corner[0] + 0.05, corner[1] - 0.05, corner[2]), (0.22, 0.22, 0.2), Q.pbr("k_hajar", (0.05, 0.03, 0.03), 0.3),
           parent=root, seg=16)
    # Hijr Ismail: halbrunde Marmormauer an der Seite +y
    n = 28
    for k in range(n + 1):
        a = math.pi * k / n
        x = (K_W / 2 - 0.3) * math.cos(a)
        y = K_D / 2 + 1.6 + 8.0 * math.sin(a) * 0.95
        Q.box(f"{name}_hijr{k}", (x * 1.05, y, 0.65), (1.4, 1.3, 1.3), M["marble"], rot=(0, 0, a), parent=root, bevel=0.08)
    return root


def maqam_today(name="mq", loc=MAQAM_T):
    """Maqam Ibrahim heute: Sockel, Glocke aus Glas mit goldenem Gitter, darin der Stein mit zwei Fußabdrücken."""
    today_mats()
    root = Q.empty(name, (loc.x, loc.y, 0))
    Q.cyl(f"{name}_ped", (0, 0, 0.2), 1.05, 0.4, M["marble_d"], seg=8, parent=root)
    Q.cyl(f"{name}_ped2", (0, 0, 0.46), 0.95, 0.12, M["gold"], seg=8, parent=root)
    # Stein in Gold-Silber-Fassung, oben zwei Fußabdrücke
    Q.box(f"{name}_case", (0, 0, 0.78), (0.72, 0.62, 0.52), M["silver"], parent=root, bevel=0.06)
    Q.box(f"{name}_top", (0, 0, 1.045), (0.6, 0.5, 0.02), M["stone_core"], parent=root, bevel=0.01)
    fm = Q.pbr("k_fp2", (0.36, 0.3, 0.22), 0.6, var=0.35, scale=12, bump=0.5, bscale=40)
    for s_ in (-1, 1):
        f = foot(f"{name}_fp{s_}", (0.11 * s_, 0.0, 1.057), parent=root, scale=1.25, mat=fm)
        f.rotation_euler = (0, 0, math.radians(-4 * s_))
        Q.torus(f"{name}_rim{s_}", (0.11 * s_, 0.015, 1.058), 0.075, 0.008, M["gold"], parent=root, scale=(0.85, 2.05, 0.4))
    # Glocke: Glas + goldene Rippen
    prof = [(0.5, 0.92), (0.9, 0.95), (1.4, 0.9), (1.9, 0.78), (2.2, 0.6), (2.4, 0.38), (2.52, 0.12)]
    Q.loft(f"{name}_glass", [(z, r, r) for z, r in prof], M["glass"], parent=root, seg=40, cap_bot=False)
    for k in range(12):
        a = 2 * math.pi * k / 12
        pts = [Vector((r * math.cos(a), r * math.sin(a), z)) for z, r in prof]
        for j in range(len(pts) - 1):
            Q.limb(f"{name}_rib{k}_{j}", pts[j], pts[j + 1], 0.018, 0.018, M["gold"], seg=6, parent=root)
    for z, r in prof[1:-1]:
        Q.torus(f"{name}_ring{z}", (0, 0, z), r, 0.02, M["gold"], parent=root, seg=40, rseg=6)
    Q.ball(f"{name}_crown", (0, 0, 2.6), 0.12, M["gold"], parent=root, seg=16)
    Q.cyl(f"{name}_spire", (0, 0, 2.85), 0.03, 0.4, M["gold"], seg=8, parent=root, r2=0.005)
    return root


def mataf(r_floor=95.0):
    """Marmorboden, Säulengänge rundherum (2 Etagen), Lampen, Minarette in der Ferne."""
    today_mats()
    Q.cyl("mt_floor", (0, 0, -0.05), r_floor, 0.1, M["marble"], seg=96)
    for k in range(48):  # Fugen/Bänder im Boden
        r = 9 + k * 1.7
        Q.torus(f"mt_band{k}", (0, 0, 0.002), r, 0.025, M["marble_d"], seg=96, rseg=4, scale=(1, 1, 0.1))
    for ring, (r, h) in enumerate(((46.0, 0.0), (52.0, 7.5))):
        n = 64
        for k in range(n):
            a = 2 * math.pi * k / n
            x, y = r * math.cos(a), r * math.sin(a)
            Q.cyl(f"mt_col{ring}_{k}", (x, y, h + 3.2), 0.45, 6.4, M["arc"], seg=12)
            Q.cyl(f"mt_lmp{ring}_{k}", (x * 0.985, y * 0.985, h + 5.9), 0.25, 0.25, M["lamp"], seg=8)
        Q.cyl(f"mt_slab{ring}", (0, 0, h + 6.8), r + 4.5, 0.8, M["arc"], seg=96, caps=False)
        Q.torus(f"mt_edge{ring}", (0, 0, h + 6.6), r - 0.4, 0.25, M["lamp"], seg=96, rseg=6)
    Q.cyl("mt_back", (0, 0, 9.0), 60.0, 18.0, M["arc"], seg=96, caps=False)
    for k in range(7):  # Minarette
        a = 2 * math.pi * k / 7 + 0.3
        x, y = 78 * math.cos(a), 78 * math.sin(a)
        Q.cyl(f"mn_{k}", (x, y, 40), 2.2, 80, M["arc"], seg=16)
        for j, z in enumerate((30, 52, 70)):
            Q.cyl(f"mn_{k}_b{j}", (x, y, z), 3.0, 1.2, M["arc"], seg=16)
            Q.torus(f"mn_{k}_l{j}", (x, y, z + 0.7), 2.9, 0.15, M["lamp"], seg=24, rseg=4)
        Q.cyl(f"mn_{k}_top", (x, y, 83), 1.6, 6, M["gold"], seg=12, r2=0.05)
    # Flutlichter (wenige, starke) + Himmel nachts
    for k in range(8):
        a = 2 * math.pi * k / 8
        Q.point(f"mt_fl{k}", (40 * math.cos(a), 40 * math.sin(a), 22), 60000, color=(1.0, 0.95, 0.88), radius=3.0)
    Q.point("mt_top", (0, 0, 40), 30000, color=(1.0, 0.96, 0.9), radius=6.0)


def crowd_ring(name, r0, r1, n, seed=0, women=0.3, gap=None):
    """Ferne Pilger als EIN Objekt (weiße und schwarze Gestalten) zwischen Radius r0 und r1.
    gap = (Winkel-Mitte, halbe Breite) in Grad: dort niemand (z. B. hinter dem Maqam, wo Leute in Reihen beten)."""
    rnd = random.Random(seed)
    bm_w, bm_b = bmesh.new(), bmesh.new()
    for _ in range(n):
        a, r = rnd.uniform(0, 2 * math.pi), math.sqrt(rnd.uniform(r0 * r0, r1 * r1))
        if gap and abs((math.degrees(a) - gap[0] + 180) % 360 - 180) < gap[1]:
            continue
        x, y = r * math.cos(a), r * math.sin(a)
        if abs(x) < K_W / 2 + 1.2 and abs(y) < K_D / 2 + 1.2:
            continue
        if y > K_D / 2 and x * x / (K_W / 2 + 0.8) ** 2 + (y - K_D / 2 - 1.6) ** 2 / 8.6 ** 2 < 1.0:
            continue   # nicht in der Hijr-Mauer (dort gehen auch Leute, aber nicht durch die Mauer)
        if (Vector((x, y)) - MAQAM_T.xy).length < 1.6:
            continue
        bm = bm_b if rnd.random() < women else bm_w
        h = rnd.uniform(1.55, 1.8)
        g = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.25, radius2=0.19, depth=h - 0.25)
        for v in g["verts"]:
            v.co += Vector((x, y, (h - 0.25) / 2))
        g = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.115)
        for v in g["verts"]:
            v.co += Vector((x, y, h - 0.1))
    objs = []
    for bm, m, tag in ((bm_w, M["white"], "w"), (bm_b, M["black"], "b")):
        me = bpy.data.meshes.new(f"{name}{tag}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(m)
        o = bpy.data.objects.new(f"{name}{tag}", me)
        Q.link(o)
        objs.append(o)
    return objs


def circle_crowd(objs, t1, deg_per_s):
    """Pilger umrunden die Kaaba gegen den Uhrzeigersinn (von oben): ganzes Objekt dreht sich um die Mitte."""
    for o in objs:
        o.rotation_euler = (0, 0, 0)
        o.keyframe_insert("rotation_euler", frame=1)
        o.rotation_euler = (0, 0, math.radians(deg_per_s * t1))
        o.keyframe_insert("rotation_euler", frame=Q.T(t1) + 1)
        for fc in Q.fcurves(o):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"


def tawaf_walkers(n, r0, r1, t1, seed=0, a_range=(0, 2 * math.pi), speed=(0.8, 1.05)):
    """Pilger in der Nähe der Kamera als echte Figuren: gehen auf Kreisbögen gegen den Uhrzeigersinn."""
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        a0 = rnd.uniform(*a_range)
        r = rnd.uniform(r0, r1)
        sp = rnd.uniform(*speed)
        da = sp * (t1 + 1) / r
        pts = [(r * math.cos(a0 + da * j / 24), r * math.sin(a0 + da * j / 24)) for j in range(25)]
        woman = rnd.random() < 0.3
        P_ = MK.pilgrim(f"tw{k}", (pts[0][0], pts[0][1], 0), yaw=0, seed=900 + k, woman=woman)
        Q.walk(P_, pts, 0.0, speed=sp)
        out.append(P_)
    return out
