# Medina um 622: Moschee des Propheten ﷺ (Lehmmauern, Säulen aus Palmstämmen, Dach aus Palmzweigen),
# Lehmhäuser mit Flachdach, Gassen, Palmen, Berge am Horizont. Alles prozedural (Zufall mit festem Seed).
import bpy, bmesh, math, random
from mathutils import Vector
import lib as Q

M = {}


def mats():
    M["sand"] = Q.pbr("sand", (0.52, 0.4, 0.28), 1.0, var=0.16, scale=0.35, bump=0.06, bscale=4, spec=0.1)
    M["court"] = Q.pbr("court", (0.5, 0.39, 0.28), 1.0, var=0.2, scale=0.7, bump=0.05, bscale=8, spec=0.1)
    M["adobe"] = Q.pbr("adobe", (0.58, 0.44, 0.32), 0.95, var=0.16, scale=0.9, bump=0.12, bscale=5, brick=0.09)
    M["adobe2"] = Q.pbr("adobe2", (0.64, 0.5, 0.37), 0.95, var=0.16, scale=0.9, bump=0.12, bscale=5, brick=0.07)
    M["adobe3"] = Q.pbr("adobe3", (0.5, 0.38, 0.28), 0.95, var=0.16, scale=0.9, bump=0.12, bscale=5, brick=0.1)
    M["wood"] = Q.pbr("wood", (0.27, 0.17, 0.1), 0.75, var=0.25, scale=8, bump=0.2, bscale=40)
    M["wood_dark"] = Q.pbr("wood_dark", (0.14, 0.09, 0.06), 0.7, var=0.2, scale=8)
    M["trunk"] = Q.pbr("trunk", (0.34, 0.25, 0.17), 0.95, var=0.12, scale=4, rings=18)
    M["frond"] = Q.pbr("frond", (0.16, 0.24, 0.08), 0.75, var=0.25, scale=3, two=((0.32, 0.3, 0.12), 2.0))
    M["dead"] = Q.pbr("dead", (0.4, 0.3, 0.17), 0.9, var=0.2, scale=4)
    M["dates"] = Q.pbr("dates", (0.45, 0.16, 0.05), 0.4, var=0.2, scale=20)
    M["roof"] = Q.pbr("roof", (0.3, 0.23, 0.14), 0.95, var=0.25, scale=6, bump=0.3, bscale=30)
    M["dark"] = Q.pbr("dark_open", (0.015, 0.012, 0.01), 1.0)
    M["win_lit"] = Q.pbr("win_lit", (0.1, 0.06, 0.03), 0.9, emit=(1.0, 0.55, 0.22), es=1.6)
    M["mount"] = Q.pbr("mount", (0.3, 0.22, 0.17), 0.95, var=0.2, scale=0.05)
    M["mat"] = Q.pbr("mat_reed", (0.55, 0.42, 0.24), 0.9, var=0.15, scale=10, rings=60)
    return M


# ---------------------------------------------------------------- Palme
_PALM = {}


def _frond_mesh(name, length=2.6, droop=0.9, n=26, leaf=0.55, mat=None):
    bm = bmesh.new()
    pts = []
    for i in range(n + 1):
        u = i / n
        x = u * length
        z = 0.35 * math.sin(u * math.pi * 0.6) - droop * u * u
        pts.append(Vector((x, 0, z)))
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        u = i / n
        w = leaf * math.sin(min(1.0, u * 1.25) * math.pi) * (1 - 0.35 * u) + 0.02
        for s in (-1, 1):
            tip = a + Vector((0.18 * w, s * w, -0.22 * w))
            v1, v2 = bm.verts.new(a), bm.verts.new(b)
            v3 = bm.verts.new(tip)
            v4 = bm.verts.new(tip + (b - a) * 0.6)
            bm.faces.new((v1, v2, v4, v3))
    # Mittelrippe
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        v1 = bm.verts.new(a + Vector((0, -0.015, 0.0)))
        v2 = bm.verts.new(b + Vector((0, -0.015, 0.0)))
        v3 = bm.verts.new(b + Vector((0, 0.015, 0.0)))
        v4 = bm.verts.new(a + Vector((0, 0.015, 0.0)))
        bm.faces.new((v1, v2, v3, v4))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    return me


def palm(name, loc, h=8.0, lean=(0.0, 0.0), seed=0, crown=16):
    rnd = random.Random(seed)
    root = Q.empty(name, loc)
    rings = []
    for k in range(13):
        u = k / 12
        rr = 0.2 * (1 - 0.25 * u) + (0.08 if k == 0 else 0)
        rings.append((u * h, rr, rr, lean[0] * u * u * h, lean[1] * u * u * h))
    Q.loft(f"{name}_trunk", rings, M["trunk"], seg=12, parent=root)
    top = Vector((lean[0] * h, lean[1] * h, h))
    if "frond" not in _PALM:
        _PALM["frond"] = _frond_mesh("frond_me", mat=M["frond"])
        _PALM["frond2"] = _frond_mesh("frond_me2", length=2.2, droop=1.3, leaf=0.5, mat=M["frond"])
        _PALM["dead"] = _frond_mesh("frond_dead", length=1.8, droop=1.9, leaf=0.35, mat=M["dead"])
    for i in range(crown):
        me = _PALM["frond"] if i % 2 == 0 else _PALM["frond2"]
        o = bpy.data.objects.new(f"{name}_fr{i}", me)
        Q.link(o)
        o.parent = root
        o.location = top + Vector((0, 0, rnd.uniform(-0.15, 0.1)))
        o.rotation_euler = (rnd.uniform(-0.15, 0.15), math.radians(rnd.uniform(-35, 25)), 2 * math.pi * i / crown + rnd.uniform(-0.2, 0.2))
        o.scale = [rnd.uniform(0.85, 1.15)] * 3
    for i in range(5):
        o = bpy.data.objects.new(f"{name}_dd{i}", _PALM["dead"])
        Q.link(o)
        o.parent = root
        o.location = top + Vector((0, 0, -0.35))
        o.rotation_euler = (0, math.radians(rnd.uniform(20, 50)), 2 * math.pi * i / 5 + rnd.uniform(0, 1))
    Q.ball(f"{name}_head", top + Vector((0, 0, -0.1)), (0.26, 0.26, 0.4), M["trunk"], seg=12, parent=root)
    if rnd.random() < 0.6:
        for i in range(rnd.randint(2, 4)):
            a = rnd.uniform(0, 6.28)
            Q.ball(f"{name}_dt{i}", top + Vector((0.28 * math.cos(a), 0.28 * math.sin(a), -0.45)), (0.12, 0.12, 0.22), M["dates"],
                   seg=10, parent=root)
    return root


# ---------------------------------------------------------------- Haus
def house(name, x0, y0, w, d, h, mat=None, door_side=None, door_at=0.5, seed=0, lit=False, parapet=True, windows=2,
          stairs=False):
    """Lehmhaus mit Flachdach, Brüstung, Balkenköpfen, kleinen Fenstern, Holztür. (x0,y0) = Ecke links unten."""
    rnd = random.Random(seed)
    mat = mat or rnd.choice([M["adobe"], M["adobe2"], M["adobe3"]])
    cx, cy = x0 + w / 2, y0 + d / 2
    Q.box(f"{name}_body", (cx, cy, h / 2), (w, d, h), mat, bevel=0.06, jitter=0.03, seed=seed)
    if parapet:
        t = 0.22
        ph = 0.55
        for k, (lx, ly, sx, sy) in enumerate(((cx, y0 + t / 2, w, t), (cx, y0 + d - t / 2, w, t), (x0 + t / 2, cy, t, d),
                                               (x0 + w - t / 2, cy, t, d))):
            Q.box(f"{name}_par{k}", (lx, ly, h + ph / 2), (sx, sy, ph), mat, bevel=0.05, jitter=0.02, seed=seed + k)
    # Balkenköpfe unter der Dachkante
    for side in ("S", "N", "W", "E"):
        n = int((w if side in "SN" else d) / 0.7)
        for i in range(1, n):
            if rnd.random() < 0.25:
                continue
            if side == "S":
                p = (x0 + i * w / n, y0 - 0.12, h - 0.35)
                rot = (math.pi / 2, 0, 0)
            elif side == "N":
                p = (x0 + i * w / n, y0 + d + 0.12, h - 0.35)
                rot = (math.pi / 2, 0, 0)
            elif side == "W":
                p = (x0 - 0.12, y0 + i * d / n, h - 0.35)
                rot = (0, math.pi / 2, 0)
            else:
                p = (x0 + w + 0.12, y0 + i * d / n, h - 0.35)
                rot = (0, math.pi / 2, 0)
            Q.cyl(f"{name}_v{side}{i}", p, 0.06, 0.3, M["wood"], seg=7, rot=rot)
    door = None
    if door_side:
        dw, dh = 0.95, 1.95
        if door_side in "SN":
            px = x0 + w * door_at
            py = y0 - 0.02 if door_side == "S" else y0 + d + 0.02
            Q.box(f"{name}_dhole", (px, py + (0.04 if door_side == "S" else -0.04), dh / 2), (dw, 0.12, dh), M["dark"])
            Q.box(f"{name}_lint", (px, py, dh + 0.1), (dw + 0.5, 0.18, 0.16), M["wood"], bevel=0.02)
            hinge = Q.empty(f"{name}_hinge", (px - dw / 2, py, 0))
            door = Q.box(f"{name}_door", (dw / 2, 0, dh / 2), (dw, 0.06, dh), M["wood"], bevel=0.015, parent=hinge)
        else:
            py = y0 + d * door_at
            px = x0 - 0.02 if door_side == "W" else x0 + w + 0.02
            Q.box(f"{name}_dhole", (px + (0.04 if door_side == "W" else -0.04), py, dh / 2), (0.12, dw, dh), M["dark"])
            Q.box(f"{name}_lint", (px, py, dh + 0.1), (0.18, dw + 0.5, 0.16), M["wood"], bevel=0.02)
            hinge = Q.empty(f"{name}_hinge", (px, py - dw / 2, 0))
            door = Q.box(f"{name}_door", (0, dw / 2, dh / 2), (0.06, dw, dh), M["wood"], bevel=0.015, parent=hinge)
        for i in range(4):  # Bretter
            off = (i - 1.5) * dw / 4
            if door_side in "SN":
                Q.box(f"{name}_pl{i}", (dw / 2 + off, -0.035 if door_side == "S" else 0.035, dh / 2), (0.012, 0.01, dh - 0.05), M["wood_dark"], parent=door)
            else:
                Q.box(f"{name}_pl{i}", (-0.035 if door_side == "W" else 0.035, dw / 2 + off, dh / 2), (0.01, 0.012, dh - 0.05), M["wood_dark"], parent=door)
        door = hinge
    # Fenster
    for i in range(windows):
        side = rnd.choice("SNWE")
        z = rnd.choice([1.6, 1.8]) if h < 4 else rnd.choice([1.8, h - 1.4])
        m = M["win_lit"] if (lit and rnd.random() < 0.7) else M["dark"]
        if side in "SN":
            px = x0 + rnd.uniform(0.25, 0.75) * w
            py = y0 - 0.0 if side == "S" else y0 + d
            Q.box(f"{name}_w{i}", (px, py, z), (0.5, 0.1, 0.45), m)
            Q.box(f"{name}_wl{i}", (px, py + (-0.05 if side == "S" else 0.05), z - 0.25), (0.65, 0.12, 0.06), M["wood"])
        else:
            py = y0 + rnd.uniform(0.25, 0.75) * d
            px = x0 if side == "W" else x0 + w
            Q.box(f"{name}_w{i}", (px, py, z), (0.1, 0.5, 0.45), m)
            Q.box(f"{name}_wl{i}", (px + (-0.05 if side == "W" else 0.05), py, z - 0.25), (0.12, 0.65, 0.06), M["wood"])
    if stairs:  # Außentreppe zum Dach (an der Westseite)
        n = int(h / 0.3)
        for i in range(n):
            Q.box(f"{name}_st{i}", (x0 - 0.45, y0 + 0.4 + i * 0.32, (i + 1) * h / n / 2), (0.9, 0.34, (i + 1) * h / n), mat)
    return door


# ---------------------------------------------------------------- Moschee
def mosque():
    W, D, H, T_ = 30.0, 34.0, 2.8, 0.6
    x0, x1, y0, y1 = -W / 2, W / 2, -D / 2, D / 2
    mw = M["adobe2"]
    Q.box("court", (0, 0, 0.012), (W - 0.2, D - 0.2, 0.02), M["court"])

    def wall(name, a, b, gaps=()):  # gerade Mauer von a nach b mit Lücken [(von, bis), ...] in Metern ab a
        a, b = Vector(a), Vector(b)
        L = (b - a).length
        d = (b - a).normalized()
        cuts = [0.0] + [v for g in gaps for v in g] + [L]
        for k in range(0, len(cuts), 2):
            s0, s1 = cuts[k], cuts[k + 1]
            if s1 - s0 < 0.05:
                continue
            c = a + d * (s0 + s1) / 2
            sz = (s1 - s0 + (T_ if abs(d.x) > 0.5 else 0), T_, H) if abs(d.x) > 0.5 else (T_, s1 - s0 + T_, H)
            Q.box(f"{name}{k}", (c.x, c.y, H / 2), sz, mw, bevel=0.07, jitter=0.04, seed=k + len(name))
    wall("mwS", (x0, y0), (x1, y0), gaps=((W / 2 - 1.3, W / 2 + 1.3),))
    wall("mwN", (x0, y1), (x1, y1))
    wall("mwW", (x0, y0), (x0, y1), gaps=((10.5, 12.8),))
    wall("mwE", (x1, y0), (x1, y1), gaps=((16.0, 18.3),))
    # überdachter Teil im Norden: Säulen aus Palmstämmen, Balken, Dach aus Palmzweigen + Lehm
    cols = []
    rows = (11.0, 13.75, 16.3)
    xs = [s * (2.25 + 3 * k) for k in range(5) for s in (-1, 1)]
    for ry in rows:
        for x in xs:
            Q.cyl(f"col_{x:.1f}_{ry}", (x, ry, 1.55), 0.17, 3.1, M["trunk"], seg=12)
            cols.append((x, ry))
    RZ = 3.1
    for ry in rows:
        Q.cyl(f"beam_{ry}", (0, ry, RZ + 0.1), 0.14, W, M["trunk"], seg=10, rot=(0, math.pi / 2, 0))
    for i in range(46):
        x = x0 + 0.4 + i * (W - 0.8) / 45
        Q.cyl(f"rafter_{i}", (x, (rows[0] + y1) / 2, RZ + 0.27), 0.07, y1 - rows[0] + 1.0, M["trunk"], seg=7, rot=(math.pi / 2, 0, 0))
    Q.box("roof", (0, (rows[0] + y1) / 2 - 0.1, RZ + 0.45), (W + 0.2, y1 - rows[0] + 1.4, 0.18), M["roof"], bevel=0.05, jitter=0.03)
    # Fransen der Palmzweige an der Dachkante
    rnd = random.Random(3)
    for i in range(70):
        x = x0 + rnd.uniform(0, W)
        Q.box(f"fringe{i}", (x, rows[0] - 0.62, RZ + 0.3 + rnd.uniform(-0.05, 0.05)), (rnd.uniform(0.25, 0.6), 0.05, rnd.uniform(0.15, 0.35)),
              M["dead"], rot=(rnd.uniform(-0.3, 0.3), 0, rnd.uniform(-0.2, 0.2)))
    # Matten unter dem Dach
    for i, x in enumerate((-9, -3, 3, 9)):
        Q.box(f"mat{i}", (x, 13.6, 0.03), (4.6, 5.2, 0.02), M["mat"])
    return {"cols": cols, "rows": rows, "roof_z": RZ, "W": W, "D": D, "H": H}


# ---------------------------------------------------------------- Stadt
def town(night=True, seed=11):
    """Baut alles. Gibt wichtige Orte zurück (Gasse, Umars Tür, hohes Haus, ...)."""
    mats()
    rnd = random.Random(seed)
    Q.box("ground", (0, 0, -0.1), (900, 900, 0.2), M["sand"])
    info = {"mosque": mosque()}
    # Gasse nach Süden (vor dem Südtor), leicht versetzte Häuserzeilen
    doors = {}
    y = -18.5
    k = 0
    while y > -78:
        d = rnd.uniform(5.0, 8.5)
        for side in (-1, 1):
            w = rnd.uniform(6, 9)
            x0 = (2.0 + rnd.uniform(0, 0.5)) if side > 0 else -(2.0 + rnd.uniform(0, 0.5)) - w
            h = rnd.choice([3.0, 3.2, 3.4, 5.6, 6.0]) if abs(y + 40) > 6 else 3.2
            nm = f"hA{k}{'E' if side > 0 else 'W'}"
            ds = "W" if side > 0 else "E"
            dr = house(nm, x0, y - d, w, d, h, door_side=ds if rnd.random() < 0.7 else None, door_at=rnd.uniform(0.3, 0.7),
                       seed=rnd.randint(0, 9999), lit=night, windows=2)
            doors[nm] = (dr, x0, y - d, w, d)
        y -= d + rnd.uniform(0.0, 0.6)
        k += 1
    # Umars Haus: Ostseite, Tür nach Westen in die Gasse
    UY = -40.0
    info["umar_door"] = house("hUmar", 2.2, UY - 3.5, 7.0, 7.0, 3.3, mat=M["adobe2"], door_side="W", door_at=0.5, seed=77, lit=night)
    info["umar_door_pos"] = Vector((2.2, UY, 0))
    # das höchste Haus neben der Moschee (Südwest-Ecke außen): Bilal ruft vom Dach
    house("hHigh", -22.5, -14.0, 6.5, 7.0, 6.6, mat=M["adobe"], door_side="E", seed=5, lit=night, windows=3, stairs=True)
    info["roof_bilal"] = Vector((-16.75, -10.4, 6.6))
    # Häuser um die Moschee (Westen, Osten, Norden) + weiter weg
    for (xa, xb, ya, yb, n) in ((-60, -17, -16, 40, 26), (17, 60, -16, 40, 24), (-40, 40, 19.5, 60, 26), (-70, -6, -90, -18, 30),
                                (6, 70, -90, -18, 30)):
        placed = 0
        tries = 0
        while placed < n and tries < 400:
            tries += 1
            w, d = rnd.uniform(5, 10), rnd.uniform(5, 9)
            x0, y0 = rnd.uniform(xa, xb - w), rnd.uniform(ya, yb - d)
            if -22.8 < x0 + w and x0 < -15.5 and -14.5 < y0 + d and y0 < -6.5:  # hohes Haus frei lassen
                continue
            if -3.0 < x0 + w and x0 < 3.0 and y0 < -17:  # Gasse frei lassen
                continue
            if -16 < x0 + w and x0 < 16 and -18 < y0 + d and y0 < 18:  # Moschee frei
                continue
            if abs(x0 + w / 2 - 0) < 6 and y0 + d > -24 and y0 < -17:  # Vorplatz Südtor
                continue
            house(f"hB{placed}_{xa}", x0, y0, w, d, rnd.choice([3.0, 3.3, 3.6, 5.8]), seed=rnd.randint(0, 9999), lit=night,
                  windows=rnd.randint(1, 3))
            placed += 1
    # Palmen: Gruppen außen, einzelne zwischen Häusern
    spots = [(-8, -20.5), (7.5, -21.0), (-17.5, 22), (18, 21), (-26, 4), (25, -3), (-12, 26), (11, 27), (30, 15), (-31, -20),
             (4.0, 21.5), (-5.5, 22.5)]
    for i in range(55):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(70, 160)
        spots.append((r * math.cos(a), r * math.sin(a)))
    for i, (x, y) in enumerate(spots):
        palm(f"palm{i}", (x, y, 0), h=rnd.uniform(6.5, 10.5), lean=(rnd.uniform(-0.04, 0.04), rnd.uniform(-0.04, 0.04)),
             seed=i + 100)
    # Berge (Uhud im Norden) + flache Hügel ringsum: Bergkamm-Streifen mit gezacktem Rand
    for k, (ang0, ang1, R, hmax) in enumerate(((-40, 40, 420, 90), (40, 140, 470, 35), (140, 220, 500, 45), (220, 320, 480, 40))):
        bm = bmesh.new()
        n = 90
        top, bot = [], []
        for i in range(n + 1):
            a = math.radians(ang0 + (ang1 - ang0) * i / n)
            hh = hmax * (0.35 + 0.65 * abs(math.sin(i * 0.13 + k)) * (0.6 + 0.4 * math.sin(i * 0.41 + 2 * k))) * (0.6 + 0.4 * rnd.random())
            if k == 0:
                hh *= 0.4 + 0.6 * math.sin(math.pi * i / n)
            bot.append(bm.verts.new((R * math.sin(a), R * math.cos(a), -2)))
            top.append(bm.verts.new(((R + 25) * math.sin(a), (R + 25) * math.cos(a), hh)))
        for i in range(n):
            bm.faces.new((bot[i], bot[i + 1], top[i + 1], top[i]))
        me = bpy.data.meshes.new(f"ridge{k}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(M["mount"])
        Q.link(bpy.data.objects.new(f"ridge{k}", me))
    # Öllampen in Mauernischen entlang der Gasse (warmes Licht für die Nacht)
    info["niche_lamps"] = []
    if night:
        for i, (x, y) in enumerate(((-2.05, -22.5), (2.05, -29.0), (-2.05, -36.5), (2.05, -47.0), (-2.05, -55.0), (2.05, -63.0), (-2.05, -71.0))):
            sx = 1 if x > 0 else -1
            Q.box(f"niche{i}", (x + 0.05 * sx, y, 1.75), (0.14, 0.35, 0.3), M["dark"])
            L = Q.oil_lamp(f"nl{i}", (x - 0.02 * sx, y, 1.63), energy=0.0)
            L["root"].rotation_euler = (0, 0, math.pi / 2 if sx > 0 else -math.pi / 2)
            L["root"].scale = (1.3, 1.3, 1.3)
            L["light"].data.energy = 35
            L["light"].location.z += 0.1
            info["niche_lamps"].append(L)
    info["doors"] = doors
    return info


def join_static(keep=()):
    """Alle unbewegten Mesh-Objekte (Häuser, Mauern, Palmen, Boden …) zu EINEM Objekt verschmelzen:
    weniger Objekte = schnelleres Rendern pro Bild. keep = Namen-Präfixe, die einzeln bleiben (Animation)."""
    def top(o):
        while o.parent is not None:
            o = o.parent
        return o

    def movable(o):
        t = top(o)
        if t.get("person") or t.name.startswith(("pov", "nur", "hUmar_hinge")) or t.animation_data:
            return True
        return any(o.name.startswith(k) or t.name.startswith(k) for k in keep)

    objs = [o for o in bpy.data.objects if o.type == "MESH" and not movable(o) and not o.name.startswith(("nl", "floor"))]
    if len(objs) < 2:
        return
    for o in bpy.data.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    vl = bpy.context.view_layer
    vl.objects.active = objs[0]
    with bpy.context.temp_override(selected_objects=objs, selected_editable_objects=objs, active_object=objs[0], object=objs[0]):
        bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
        bpy.ops.object.make_single_user(object=True, obdata=True)
        bpy.ops.object.convert(target="MESH")
        bpy.ops.object.join()
    print("join_static:", len(objs), "Objekte ->", len(bpy.data.objects), "gesamt")
