# QISSAH Folge 5 – „Die Hidschra – der Jäger in der Wüste“: Bausteine.
# Mekka (Tal aus mekka.py, flacher Stadtboden, Lehmhäuser, Kaaba), Höhle im Berg Thaur (Fels mit Hohlraum + Öffnung,
# Spinnennetz), Küstenebene am Roten Meer (Meer im Westen, Strand, Dünen, Berge im Osten), Beduinenzelt (Suraqas Stamm),
# Medina (Palmenhaine, schwarzes Lavafeld). Regeln: der Prophet ﷺ NUR als Licht, Menschen ohne Gesicht, Abu Bakr mit Licht
# über dem Kopf. Koran-Rezitation wird nie hörbar gemacht.
import bpy, bmesh, math, random
from mathutils import Vector, noise
import lib as Q
import mekka as MK
MK_HEIGHT = MK.height          # Tal von Mekka (vor badr_world sichern – badr_world tauscht MK.height aus)
MK_AX, MK_AY = MK.AX, MK.AY
import medina as MD
import kaaba_world as KW
import badr_world as BW

M = {}


def gz(x, y):
    return MK.ground_z(x, y)


def _sstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


# ================================================================ Mekka
KAABA = Vector((-7.0, -25.0, 0.0))     # auf dem Hügelchen von Folge 2
TOWN_R = 95.0


_CAVE = []


def cave_spot():
    """Ort der Höhle: am Hang des Berges im Süden, ca. 30 m über dem Tal (einmal gesucht)."""
    if not _CAVE:
        x = 14.0
        for d in range(100, 400):
            h = MK_HEIGHT(x, -float(d))
            if h > 30.0:
                _CAVE.append(Vector((x, -float(d), h)))
                break
        else:
            _CAVE.append(Vector((x, -200.0, MK_HEIGHT(x, -200.0))))
    return _CAVE[0]


def mecca_height(x, y):
    """Tal von Mekka, aber der Stadtboden ist eben (Häuser stehen auf z = 0); kleine ebene Stelle vor der Höhle."""
    h = MK_HEIGHT(x, y)
    r = math.hypot(x / 1.15, y)
    h *= _sstep(TOWN_R * 0.72, TOWN_R * 1.15, r)
    c = cave_spot()
    dc = math.hypot(x - c.x, y - c.y)
    if dc < 14.0:
        w = 1.0 - _sstep(5.0, 14.0, dc)
        h = h * (1 - w) + c.z * w
    return h


def use_mecca():
    MK.height = mecca_height
    MK.AX, MK.AY = MK_AX, MK_AY


def mecca_town(night=True, seed=5, keep=(), kaaba=True):
    """Tal, Lehmhäuser um die Kaaba (Gassen frei nach keep), Berge ringsum."""
    use_mecca()
    MK.mats()
    BW.mats()
    MD.mats()
    KW.mats()
    MK.terrain()
    rnd = random.Random(seed)
    houses = []

    def free(x0, y0, w, d):
        for (a, b, r) in keep:
            cx = min(max(a, x0), x0 + w)
            cy = min(max(b, y0), y0 + d)
            if (cx - a) ** 2 + (cy - b) ** 2 < r * r:
                return False
        for (hx, hy, hw, hd) in houses:
            if x0 < hx + hw + 1.6 and hx < x0 + w + 1.6 and y0 < hy + hd + 1.6 and hy < y0 + d + 1.6:
                return False
        if math.hypot(x0 + w / 2 - KAABA.x, y0 + d / 2 - KAABA.y) < 22:
            return False
        return True
    tries = 0
    while len(houses) < 110 and tries < 3000:
        tries += 1
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(24, 88)
        w, d = rnd.uniform(5, 9), rnd.uniform(5, 8.5)
        x0, y0 = KAABA.x + r * math.cos(a) * 1.1 - w / 2, KAABA.y + r * math.sin(a) - d / 2
        if math.hypot(x0, y0) > TOWN_R * 0.75 or not free(x0, y0, w, d):
            continue
        MD.house(f"mh{len(houses)}", x0, y0, w, d, rnd.choice([3.0, 3.2, 3.5, 5.6]), seed=rnd.randint(0, 9999), lit=night,
                 windows=rnd.randint(1, 3))
        houses.append((x0, y0, w, d))
    if kaaba:
        kaaba_old("kaaba", KAABA)
    MK.scatter(seed=7, n_rocks=260, n_shrubs=30, keep=list(keep) + [(0, 0, TOWN_R * 0.8)])
    return houses


def kaaba_old(name, loc):
    """Die Kaaba zur Zeit der Quraisch: Steinbau mit dunkler Verhüllung (ohne die heutige Goldborte)."""
    root = Q.empty(name, loc)
    cloth = Q.pbr("kaaba_cloth", (0.05, 0.045, 0.045), 0.75, var=0.08, scale=8, bump=0.1, bscale=40)
    stone = Q.pbr("kaaba_stone", (0.42, 0.38, 0.33), 0.9, var=0.2, scale=4, bump=0.3, bscale=20)
    Q.box(f"{name}_base", (0, 0, 0.25), (11.4, 9.6, 0.5), stone, parent=root, bevel=0.03)
    Q.box(f"{name}_body", (0, 0, 0.5 + 6.5), (11.0, 9.2, 13.0), cloth, parent=root, bevel=0.05)
    return root


# ================================================================ Höhle im Berg Thaur
def _hollow(name, loc, size, seed, open_dir=(0, -1, 0)):
    """Fels mit Hohlraum und Öffnung: grosser Brocken minus Innenraum minus Durchgang (Boolean)."""
    MK._templates()
    rock = MK._rock_mesh(f"{name}_rm", seed, sub=3, rough=0.32)
    rock.materials.append(MK.M["rock"])
    o = bpy.data.objects.new(f"{name}_rock", rock)
    Q.link(o)
    o.location = loc
    o.scale = size
    def ell(nm, c, s, seg=3, rough=0.12, sd=1):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=seg, radius=1.0)
        rnd = random.Random(sd)
        for v in bm.verts:
            n = noise.noise(v.co * 2.3 + Vector((sd, 0, 0)))
            v.co *= 1.0 + rough * n
        me = bpy.data.meshes.new(nm)
        bm.to_mesh(me)
        bm.free()
        e = bpy.data.objects.new(nm, me)
        Q.link(e)
        e.location = c
        e.scale = s
        e.hide_render = True
        return e
    inner = ell(f"{name}_in", Vector(loc) + Vector((0, 0, 1.0)), (2.3, 1.7, 1.15), seg=4, rough=0.14, sd=seed)
    od = Vector(open_dir).normalized()
    tun = ell(f"{name}_tun", Vector(loc) + Vector((0, 0, 0.95)) + od * 2.4, (0.66 if abs(od.y) > 0.5 else 1.6, 1.6 if abs(od.y) > 0.5 else 0.66, 0.72),
              seg=3, rough=0.1, sd=seed + 3)
    for cut in (inner, tun):
        mo = o.modifiers.new(f"b_{cut.name}", "BOOLEAN")
        mo.operation = "DIFFERENCE"
        mo.solver = "EXACT"
        mo.object = cut
    with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o], selected_editable_objects=[o]):
        for mo in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=mo.name)
    for cut in (inner, tun):
        bpy.data.objects.remove(cut)
    for p in o.data.polygons:
        p.use_smooth = False
    return o


def cave(name="cave", loc=(0, 0, 0), yaw=0.0):
    """Die Höhle: Fels mit Hohlraum (Boden aus Sand), Öffnung nach lokal -Y. Rückgabe: Mitte der Öffnung (Welt)."""
    root = Q.empty(name, loc, rot=(0, 0, yaw))
    o = _hollow(name, (0, 0, -0.6), (4.2, 3.8, 3.0), seed=41)
    o.parent = root
    Q.box(f"{name}_floor", (0, -0.4, -0.02), (5.0, 5.0, 0.06), MK.M["sand"], parent=root)
    MK.pebbles(f"peb_{name}", (loc[0], loc[1]), (3.4, 3.0), 260, seed=3, rmin=0.01, rmax=0.05)
    # Felsbrocken rund um den Eingang (aussen) + Hang
    rnd = random.Random(5)
    for k in range(16):
        a = rnd.uniform(-1.2, 1.2) - math.pi / 2
        r = rnd.uniform(3.6, 7.5)
        x, y = r * math.cos(a), r * math.sin(a)
        s = rnd.uniform(0.4, 1.6)
        b = MK._inst(f"rock{rnd.randint(0, 6)}", f"crk{k}", (x, y, -0.3 * s), rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(0, 6.3)),
                     scale=s)
        b.parent = root
    bpy.context.view_layer.update()
    entrance = root.matrix_world @ Vector((0, -3.5, 0.5))
    return {"root": root, "rock": o, "entrance": entrance}


def spider_web(name, center, normal_yaw, r=0.55, rings=13, spokes=11, parent=None, seed=2):
    """Spinnennetz: Speichen + Spirale aus dünnen Fäden (glänzen im Gegenlicht), kleine Spinne. Ebene senkrecht, Blick lokal -Y."""
    rnd = random.Random(seed)
    m = bpy.data.materials.new(f"{name}_silk")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.9, 0.9, 0.88, 1)
    b.inputs["Roughness"].default_value = 0.25
    b.inputs["Emission Color"].default_value = (1.0, 0.97, 0.9, 1)
    b.inputs["Emission Strength"].default_value = 0.6
    root = Q.empty(name, center, parent=parent, rot=(0, 0, normal_yaw))
    bm = bmesh.new()
    th = 0.0022

    def strand(p0, p1, w=th):
        d = p1 - p0
        L = d.length
        if L < 1e-4:
            return
        ax = d.normalized()
        up = Vector((0, 1, 0)) if abs(ax.y) < 0.9 else Vector((1, 0, 0))
        s1 = ax.cross(up).normalized() * w
        s2 = ax.cross(s1).normalized() * w
        vs = [bm.verts.new(p + o) for p in (p0, p1) for o in (s1, s2, -s1, -s2)]
        for i in range(4):
            bm.faces.new((vs[i], vs[(i + 1) % 4], vs[4 + (i + 1) % 4], vs[4 + i]))
    angs = sorted(rnd.uniform(0, 2 * math.pi) for _ in range(spokes))
    lens = [r * rnd.uniform(0.8, 1.15) for _ in angs]
    for a, L in zip(angs, lens):
        strand(Vector((0, 0, 0)), Vector((L * math.cos(a), 0, L * math.sin(a))))
    # Spirale (von aussen nach innen), zwischen den Speichen gerade Stücke, leicht durchhängend
    n = rings * spokes
    prev = None
    for i in range(n + 1):
        k = i % spokes
        u = 1.0 - i / n * 0.88
        a = angs[k] + 2 * math.pi * (i // spokes)
        p = Vector((lens[k] * u * math.cos(angs[k]), 0, lens[k] * u * math.sin(angs[k])))
        if prev is not None:
            mid = (prev + p) * 0.5 + Vector((0, 0, -0.008 * u))
            strand(prev, mid, th * 0.8)
            strand(mid, p, th * 0.8)
        prev = p
    # Ankerfäden zum Felsrand
    for a in (0.3, 1.9, 3.4, 4.8):
        strand(Vector((r * 0.95 * math.cos(a), 0, r * 0.95 * math.sin(a))), Vector((r * 1.6 * math.cos(a), 0, r * 1.45 * math.sin(a))))
    me = bpy.data.meshes.new(f"{name}_me")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(m)
    o = bpy.data.objects.new(f"{name}_web", me)
    Q.link(o)
    o.parent = root
    o.visible_shadow = False
    # Spinne (klein, dunkel) etwas neben der Mitte
    sp = Q.empty(f"{name}_spider", (0.05, -0.004, 0.07), root)
    ms = Q.pbr(f"{name}_sp_m", (0.03, 0.025, 0.02), 0.4)
    Q.ball(f"{name}_sp_b", (0, 0, 0), (0.012, 0.009, 0.016), ms, parent=sp, seg=10)
    Q.ball(f"{name}_sp_h", (0, 0, 0.017), 0.007, ms, parent=sp, seg=8)
    for s_ in (-1, 1):
        for j in range(4):
            a = math.radians(-50 + j * 33)
            Q.limb(f"{name}_sp_l{j}{s_}", (0, 0, 0.008), (s_ * 0.03 * math.cos(a), -0.002, 0.03 * math.sin(a) + 0.008), 0.0012, 0.0008,
                   ms, parent=sp, seg=4)
    return root


# ================================================================ Küstenebene am Roten Meer
SHORE_X = -70.0
_CP = []


def shore(y):
    return SHORE_X + 9.0 * math.sin(y * 0.011) + 4.0 * math.sin(y * 0.031 + 1.0)


def _cpeaks():
    if _CP:
        return _CP
    rnd = random.Random(12)
    for i in range(46):   # Hedschas-Berge im Osten
        x, y = rnd.uniform(330, 760), rnd.uniform(-760, 760)
        _CP.append((x, y, rnd.uniform(45, 130), rnd.uniform(60, 150)))
    for (x, y, h, r) in ((150, 120, 14, 26), (190, -60, 18, 30), (120, -230, 10, 22), (230, 300, 16, 34), (95, 330, 8, 18)):
        _CP.append((x, y, h, r))   # niedrige Felshügel in der Ebene
    return _CP


def coast_height(x, y):
    s = x - shore(y)
    if s < 0:
        return max(-3.0, 0.045 * s + 0.12)
    n1 = noise.noise(Vector((x * 0.03, y * 0.03, 2.2)))
    h = 0.12 + 0.55 * (1 - math.exp(-s / 14.0)) + 0.0035 * s
    dune = _sstep(28.0, 75.0, s) * (1.0 - _sstep(260.0, 330.0, s))
    if dune > 0:
        h += dune * (0.7 + 0.7 * math.sin(x * 0.06 + y * 0.025 + 2.2 * noise.noise(Vector((x * 0.01, y * 0.01, 5.0)))))
    h += 0.22 * n1 + 0.06 * noise.noise(Vector((x * 0.2, y * 0.2, 4.0)))
    m, msum = 0.0, 0.0
    for px, py, ph, pr in _cpeaks():
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


def use_coast():
    MK.height = coast_height
    MK.AX, MK.AY = 260.0, 260.0


def sea_mat():
    m = bpy.data.materials.new("sea")
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.015, 0.075, 0.095, 1)
    b.inputs["Roughness"].default_value = 0.07
    b.inputs["Specular IOR Level"].default_value = 0.9
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise")
    nz.noise_dimensions = "4D"
    nz.inputs["Scale"].default_value = 0.55
    nz.inputs["Detail"].default_value = 6.0
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 2.2, 1.0)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    L.new(mp.outputs[0], nz.inputs["Vector"])
    nz.inputs["W"].default_value = 0.0
    nz.inputs["W"].keyframe_insert("default_value", frame=1)
    nz.inputs["W"].default_value = 30.0
    nz.inputs["W"].keyframe_insert("default_value", frame=4001)
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.22
    bp.inputs["Distance"].default_value = 0.08
    L.new(nz.outputs["Fac"], bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    for fc in Q.fcurves(nt):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    return m


def sea():
    """Meer: grosse Fläche auf z = 0 westlich der Küste, Schaumstreifen an der Wasserlinie."""
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
    me = bpy.data.meshes.new("sea")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(sea_mat())
    o = bpy.data.objects.new("sea", me)
    Q.link(o)
    o.location = (SHORE_X - 600.0, 0.0, 0.0)
    o.scale = (620.0, 900.0, 1.0)
    o.visible_shadow = False
    o["person"] = 1   # nicht verschmelzen (animiertes Material bleibt)
    # Schaum: schmale helle Linie entlang der Wasserlinie
    foam = Q.pbr("foam", (0.85, 0.86, 0.84), 0.6, var=0.3, scale=30)
    bm = bmesh.new()
    prev = None
    for k in range(-240, 241):
        y = k * 2.5
        x0 = shore(y) - 2.6
        a = bm.verts.new((x0 - 0.5, y, 0.012))
        b = bm.verts.new((x0 + 0.5, y, 0.012))
        if prev:
            bm.faces.new((prev[0], prev[1], b, a))
        prev = (a, b)
    me = bpy.data.meshes.new("foam")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(foam)
    fo = bpy.data.objects.new("foam", me)
    Q.link(fo)
    fo.visible_shadow = False
    return o


def coast_scatter(seed=3, n_rocks=260, n_shrubs=110, keep=(), area=(-40.0, 260.0, -320.0, 320.0)):
    MK._templates()
    rnd = random.Random(seed)

    def ok(x, y):
        if x - shore(y) < 10:
            return False
        return all((x - a) ** 2 + (y - b) ** 2 > r * r for a, b, r in keep)
    k = t = 0
    while k < n_rocks and t < n_rocks * 10:
        t += 1
        x, y = rnd.uniform(area[0], area[1]), rnd.uniform(area[2], area[3])
        if not ok(x, y):
            continue
        s = rnd.choice([rnd.uniform(0.1, 0.3), rnd.uniform(0.2, 0.5), rnd.uniform(0.4, 1.2)])
        MK._inst(f"rock{rnd.randint(0, 6)}", f"rk{k}", (x, y, gz(x, y) - 0.15 * s), rot=(rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2),
                 rnd.uniform(0, 6.28)), scale=s)
        k += 1
    k = t = 0
    while k < n_shrubs and t < n_shrubs * 10:
        t += 1
        x, y = rnd.uniform(area[0], area[1]), rnd.uniform(area[2], area[3])
        if not ok(x, y):
            continue
        MK._inst(f"shrub{rnd.randint(0, 3)}", f"sb{k}", (x, y, gz(x, y) - 0.03), rot=(0, 0, rnd.uniform(0, 6.28)), scale=rnd.uniform(0.5, 1.3))
        k += 1


def coast_world(keep=(), rocks=260, shrubs=110, sea_=True, area=(-40.0, 260.0, -320.0, 320.0)):
    use_coast()
    MK.mats()
    BW.mats()
    KW.mats()
    MD.mats()
    MK.terrain(n=240, size=760.0)
    if sea_:
        sea()
    coast_scatter(keep=keep, n_rocks=rocks, n_shrubs=shrubs, area=area)
    for i, (x, y) in enumerate(((60, 40), (110, -90), (40, -170), (150, 200), (80, 260))):
        MK.acacia(f"tree_far{i}", Vector((x, y, gz(x, y))), h=4.0, spread=3.4, seed=10 + i)


# ================================================================ Beduinenzelt (Suraqas Stamm)
def tent_mat():
    m = Q.pbr("goathair", (0.07, 0.055, 0.045), 0.95, var=0.25, scale=3, bump=0.25, bscale=60)
    return m


def bedouin_tent(name, loc, yaw=0.0, w=9.0, d=5.0, h=2.2):
    """Schwarzes Ziegenhaar-Zelt: flaches, durchhängendes Dach auf Stangen, Rückwand zu, vorn offen."""
    root = Q.empty(name, loc, rot=(0, 0, yaw))
    mt = tent_mat()
    stripe = Q.pbr("tent_stripe", (0.5, 0.42, 0.3), 0.95, var=0.2, scale=4)
    bm = bmesh.new()
    nx, ny = 18, 10
    poles = [(-w / 2, -d / 2), (w / 2, -d / 2), (-w / 2, d / 2), (0, d / 2), (w / 2, d / 2), (-w / 4, 0.4), (w / 4, 0.4)]
    g = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            x = -w / 2 - 0.3 + (w + 0.6) * i / nx
            y = -d / 2 - 0.25 + (d + 0.5) * j / ny
            z = h + 0.25 - 0.35 * (abs(y) / (d / 2)) ** 1.5 - 0.18 * math.sin(math.pi * ((x + w / 2) / (w / 2)) % math.pi) ** 2
            row.append(bm.verts.new((x, y, z)))
        g.append(row)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]))
    me = bpy.data.meshes.new(f"{name}_roof")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mt)
    o = bpy.data.objects.new(f"{name}_roof", me)
    Q.link(o)
    o.parent = root
    o.modifiers.new("solid", "SOLIDIFY").thickness = 0.03
    # Rückwand (hinten = +Y) mit hellem Streifen
    Q.box(f"{name}_back", (0, d / 2 + 0.2, h * 0.45), (w + 0.5, 0.04, h * 0.95), mt, parent=root, rot=(math.radians(-6), 0, 0))
    Q.box(f"{name}_strip", (0, d / 2 + 0.17, h * 0.6), (w + 0.5, 0.045, 0.18), stripe, parent=root, rot=(math.radians(-6), 0, 0))
    for side in (-1, 1):   # Seitenwände halb
        Q.box(f"{name}_side{side}", (side * (w / 2 + 0.2), d / 4, h * 0.4), (0.04, d / 2 + 0.3, h * 0.85), mt, parent=root)
    for k, (x, y) in enumerate(poles):
        Q.limb(f"{name}_pole{k}", (x, y, 0), (x, y, h + (0.25 if abs(y) < 0.1 else 0.0)), 0.035, 0.03, MK.M["wood"], parent=root, seg=6)
    for k, (x, y) in enumerate(poles[:2]):   # Spannseile vorn
        Q.limb(f"{name}_rope{k}", (x, y - 0.25, h - 0.1), (x * 1.05, y - 2.2, 0.0), 0.007, 0.007, MK.M["rope"], parent=root, seg=4)
    # Teppiche, Sitzpolster, Sättel
    for k, (x, y, sx, sy) in enumerate(((-2.3, 0.6, 3.6, 2.6), (2.0, 0.8, 3.4, 2.4), (0.0, 1.8, 4.0, 1.4))):
        Q.box(f"{name}_rug{k}", (x, y, 0.012), (sx, sy, 0.02), [MK.M["blanket_r"], MK.M["blanket_b"], MK.M["blanket_r"]][k], parent=root)
    for k in range(6):
        Q.ball(f"{name}_cush{k}", (-3.6 + k * 1.45, d / 2 - 0.35, 0.2), (0.5, 0.22, 0.2), [MK.M["blanket_b"], MK.M["sack"]][k % 2],
               parent=root, seg=12)
    return root


# ================================================================ Medina
def medina_height(x, y):
    h = 0.25 * noise.noise(Vector((x * 0.03, y * 0.03, 3.3))) + 0.08 * noise.noise(Vector((x * 0.18, y * 0.18, 1.1)))
    r = math.hypot(x, y)
    h += 0.02 * max(0.0, r - 120.0)
    # Lavafeld (Harra) südlich: unruhiger, dunkler Grund
    hr = _sstep(-8.0, -30.0, y)
    h += hr * 0.5 * (noise.noise(Vector((x * 0.25, y * 0.25, 7.0))) + 0.6)
    return h


def use_medina():
    MK.height = medina_height
    MK.AX, MK.AY = 300.0, 300.0


def medina_world(keep=()):
    use_medina()
    MK.mats()
    MD.mats()
    KW.mats()
    BW.mats()
    MK.terrain(n=200, size=640.0)
    rnd = random.Random(23)
    lava = Q.pbr("lava", (0.05, 0.045, 0.045), 0.85, var=0.3, scale=3, bump=0.5, bscale=25)
    MK._templates()
    for j in range(7):
        me = MK._TPL[f"rock{j}"].copy()
        me.materials.clear()
        me.materials.append(lava)
        MK._TPL[f"lava{j}"] = me
    k = t = 0
    while k < 240 and t < 3000:
        t += 1
        x, y = rnd.uniform(-60, 60), rnd.uniform(-70, -12)
        if any((x - a) ** 2 + (y - b) ** 2 < r * r for a, b, r in keep):
            continue
        s = rnd.uniform(0.25, 1.1)
        MK._inst(f"lava{rnd.randint(0, 6)}", f"lv{k}", (x, y, gz(x, y) - 0.2 * s), rot=(rnd.uniform(-0.3, 0.3), 0, rnd.uniform(0, 6.3)), scale=s)
        k += 1
    # Palmenhaine + Häuser im Norden
    for i in range(70):
        a = rnd.uniform(0.15, math.pi - 0.15)
        r = rnd.uniform(28, 140)
        x, y = r * math.cos(a), r * math.sin(a) * 0.8 + 4
        if any((x - a_) ** 2 + (y - b) ** 2 < rr * rr for a_, b, rr in keep):
            continue
        MD.palm(f"palm{i}", (x, y, gz(x, y)), h=rnd.uniform(6.5, 10.5), lean=(rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05)), seed=i + 300)
    hs = 0
    t = 0
    while hs < 22 and t < 400:
        t += 1
        x0, y0 = rnd.uniform(-70, 70), rnd.uniform(40, 120)
        w, d = rnd.uniform(5, 8), rnd.uniform(5, 8)
        if any((x0 + w / 2 - a) ** 2 + (y0 + d / 2 - b) ** 2 < (r + 5) ** 2 for a, b, r in keep):
            continue
        MD.house(f"mdh{hs}", x0, y0, w, d, rnd.choice([3.0, 3.3, 5.6]), seed=rnd.randint(0, 999), lit=False, windows=2)
        hs += 1


def embers(name, loc, energy=30.0):
    """Glut einer Feuerstelle: Steinring, glimmende Holzreste, schwaches rotes Licht."""
    root = Q.empty(name, loc)
    st = MK.M["stone"]
    for k in range(9):
        a = k * 2 * math.pi / 9
        Q.ball(f"{name}_st{k}", (0.32 * math.cos(a), 0.32 * math.sin(a), 0.03), (0.06, 0.05, 0.04), MK.M["rock"], parent=root, seg=8)
    gm = Q.glow_mat(f"{name}_gm", (1.0, 0.28, 0.06), 3.0)
    ash = Q.pbr(f"{name}_ash", (0.12, 0.11, 0.1), 1.0, var=0.3)
    Q.cyl(f"{name}_ash", (0, 0, 0.01), 0.26, 0.02, ash, parent=root, seg=16)
    for k in range(5):
        a = k * 1.3
        Q.cyl(f"{name}_w{k}", (0.08 * math.cos(a), 0.08 * math.sin(a), 0.035), 0.022, 0.26, MK.M["wood"], seg=6,
              rot=(math.pi / 2, 0, a + math.pi / 2), parent=root)
        Q.ball(f"{name}_g{k}", (0.05 * math.cos(a + 0.4), 0.05 * math.sin(a + 0.4), 0.04), 0.025, gm, parent=root, seg=8)
    lt = Q.point(f"{name}_l", (0, 0, 0.25), energy, color=(1.0, 0.4, 0.15), radius=0.15, parent=root)
    return {"root": root, "light": lt}
