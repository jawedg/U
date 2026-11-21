# Tal von Mekka zur Zeit Ibrahims (Folge 2 „Der Ursprung von Zamzam“) + Mas'a heute.
# Alles prozedural: Talboden mit Trockenbett, dunkle Granitberge ringsum, Hügel Safa und Marwa, Akazie (unter ihr liegt das Baby),
# Hügelchen (Ort des späteren Hauses), Quelle mit Wall, Engel-Licht, Kamele, Vögel, Zelte, Mas'a-Halle mit Pilgern.
# Regeln: Propheten (Ibrahim, Ismail) und der Engel NUR als Licht; Menschen ohne Gesicht.
import bpy, bmesh, math, random
from mathutils import Vector, Euler, noise
import lib as Q

M = {}
# Orte (Meter)
TREE = Vector((6.0, -14.0, 0.0))        # Akazie, darunter Hadschar mit dem Baby
BABY = Vector((5.0, -12.9, 0.0))
SPRING = Vector((4.1, -12.0, 0.0))     # Zamzam: dort, wo das Baby liegt
HILLOCK = Vector((-7.0, -25.0, 0.0))   # Hügelchen: hier wird das Haus Allahs stehen
SAFA = Vector((-46.0, 18.0, 0.0))
MARWA = Vector((46.0, 22.0, 0.0))
SAFA_H, MARWA_H = 7.6, 6.6
PASS = Vector((-20.0, 92.0, 0.0))      # Pass im Norden: dort geht Ibrahim aus dem Tal
AX, AY = 170.0, 120.0                  # Talboden (Ellipse)


def mats():
    M["sand"] = Q.pbr("z_sand", (0.62, 0.49, 0.35), 1.0, var=0.22, scale=0.25, bump=0.15, bscale=5, spec=0.12)
    M["rock"] = Q.pbr("z_rock", (0.28, 0.22, 0.18), 0.9, var=0.4, scale=1.2, bump=0.6, bscale=6, spec=0.25)
    M["rock2"] = Q.pbr("z_rock2", (0.38, 0.3, 0.23), 0.9, var=0.35, scale=1.5, bump=0.6, bscale=8, spec=0.25)
    M["hillrock"] = Q.pbr("z_hillrock", (0.27, 0.21, 0.17), 0.92, var=0.5, scale=0.9, bump=0.9, bscale=3.0, spec=0.2, plaster=0.35)
    M["stone"] = Q.pbr("z_stone", (0.33, 0.26, 0.2), 0.9, var=0.45, scale=9, bump=0.4, bscale=30)
    M["bark"] = Q.pbr("z_bark", (0.24, 0.18, 0.13), 0.95, var=0.3, scale=6, bump=0.6, bscale=30)
    M["leaf"] = Q.pbr("z_leaf", (0.16, 0.19, 0.08), 0.8, var=0.4, scale=3, two=((0.3, 0.29, 0.13), 2.5), bump=0.6, bscale=25)
    M["shrub"] = Q.pbr("z_shrub", (0.3, 0.24, 0.15), 0.9, var=0.3, scale=4)
    M["shrub_g"] = Q.pbr("z_shrub_g", (0.3, 0.29, 0.16), 0.85, var=0.3, scale=4)
    M["cloth"] = Q.pbr("z_cloth", (0.46, 0.39, 0.29), 0.95, var=0.14, scale=6, bump=0.45, bscale=45)
    M["mat"] = Q.pbr("z_mat", (0.55, 0.38, 0.22), 0.95, var=0.2, scale=6, rings=40)
    M["leather"] = Q.pbr("z_leather", (0.32, 0.19, 0.1), 0.6, var=0.25, scale=8, bump=0.3, bscale=40)
    M["dates"] = Q.pbr("z_dates", (0.36, 0.13, 0.05), 0.35, var=0.2, scale=20)
    M["wet"] = Q.pbr("z_wet", (0.3, 0.22, 0.15), 0.35, var=0.2, scale=2, bump=0.2, bscale=10, spec=0.6)
    M["mound"] = Q.pbr("z_mound", (0.56, 0.4, 0.29), 1.0, var=0.2, scale=0.6, bump=0.15, bscale=6)
    M["camel"] = Q.pbr("z_camel", (0.62, 0.46, 0.3), 0.95, var=0.12, scale=3, bump=0.2, bscale=60)
    M["camel_d"] = Q.pbr("z_camel_d", (0.3, 0.2, 0.13), 0.9, var=0.1, scale=3)
    M["rope"] = Q.pbr("z_rope", (0.45, 0.37, 0.24), 0.9, var=0.1)
    M["blanket_r"] = Q.pbr("z_blanket_r", (0.2, 0.12, 0.08), 0.95, var=0.3, scale=6, bump=0.3, bscale=50)
    M["blanket_b"] = Q.pbr("z_blanket_b", (0.12, 0.13, 0.3), 0.9, var=0.2, scale=6, bump=0.1, bscale=50)
    M["sack"] = Q.pbr("z_sack", (0.62, 0.55, 0.42), 1.0, var=0.18, scale=5, bump=0.4, bscale=60)
    M["tent"] = Q.pbr("z_tent", (0.16, 0.12, 0.1), 0.95, var=0.3, scale=3, bump=0.3, bscale=40)
    M["tent2"] = Q.pbr("z_tent2", (0.55, 0.45, 0.32), 0.95, var=0.25, scale=3, bump=0.3, bscale=40)
    M["wood"] = Q.pbr("z_wood", (0.27, 0.17, 0.1), 0.75, var=0.25, scale=8, bump=0.2, bscale=40)
    M["bird"] = Q.pbr("z_bird", (0.08, 0.07, 0.06), 0.8)
    return M


def water_mat(name="z_water", col=(0.06, 0.1, 0.1), alpha=0.92):
    """Klares Wasser: glänzend, leicht durchsichtig, bewegte Wellen (Noise mit W über die Zeit)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = 0.12
    b.inputs["Specular IOR Level"].default_value = 1.0
    b.inputs["Alpha"].default_value = alpha
    if "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = 0.3
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise")
    nz.noise_dimensions = "4D"
    nz.inputs["Scale"].default_value = 9.0
    nz.inputs["Detail"].default_value = 4.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    nz.inputs["W"].default_value = 0.0
    nz.inputs["W"].keyframe_insert("default_value", frame=1)
    nz.inputs["W"].default_value = 40.0
    nz.inputs["W"].keyframe_insert("default_value", frame=4001)
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.35
    bp.inputs["Distance"].default_value = 0.02
    L.new(nz.outputs["Fac"], bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    for fc in Q.fcurves(nt):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    m.surface_render_method = "BLENDED"
    return m


def terrain_mat(force_rock=False):
    """Talboden: Sand mit großen hellen/dunklen Flecken, Kies-Sprenkeln und feinen Rippeln; steile und hohe Stellen
    dunkler, verwitterter Granit (wie die Berge um Mekka) mit großen Rissen."""
    m = bpy.data.materials.new("z_rockmat" if force_rock else "z_terrain")
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N.get("Principled BSDF")
    b.inputs["Roughness"].default_value = 0.95
    b.inputs["Specular IOR Level"].default_value = 0.12
    tc = N.new("ShaderNodeTexCoord")
    geo = N.new("ShaderNodeNewGeometry")
    sz = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sz.inputs[0])
    sn = N.new("ShaderNodeSeparateXYZ")
    L.new(geo.outputs["Normal"], sn.inputs[0])

    def mr(sock, a, b_, lo=0.0, hi=1.0):
        n = N.new("ShaderNodeMapRange")
        n.inputs["From Min"].default_value = a
        n.inputs["From Max"].default_value = b_
        n.inputs["To Min"].default_value = lo
        n.inputs["To Max"].default_value = hi
        L.new(sock, n.inputs["Value"])
        return n.outputs[0]

    def math_(op, a, b_):
        n = N.new("ShaderNodeMath")
        n.operation = op
        for k, v in enumerate((a, b_)):
            if isinstance(v, (int, float)):
                n.inputs[k].default_value = v
            else:
                L.new(v, n.inputs[k])
        return n.outputs[0]

    def noise_(scale, detail=6.0, rough=0.55):
        n = N.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough
        L.new(tc.outputs["Object"], n.inputs["Vector"])
        return n.outputs["Fac"]

    def ramp(fac, stops):
        r = N.new("ShaderNodeValToRGB")
        E = r.color_ramp.elements
        E[0].position, E[0].color = stops[0][0], (*stops[0][1], 1)
        E[1].position, E[1].color = stops[-1][0], (*stops[-1][1], 1)
        for p_, c_ in stops[1:-1]:
            e = E.new(p_)
            e.color = (*c_, 1)
        L.new(fac, r.inputs["Fac"])
        return r.outputs["Color"]

    def mix(fac, c0, c1, blend="MIX"):
        n = N.new("ShaderNodeMix")
        n.data_type = "RGBA"
        n.blend_type = blend
        if isinstance(fac, (int, float)):
            n.inputs["Factor"].default_value = fac
        else:
            L.new(fac, n.inputs["Factor"])
        for k, c_ in ((6, c0), (7, c1)):
            if isinstance(c_, tuple):
                n.inputs[k].default_value = (*c_, 1)
            else:
                L.new(c_, n.inputs[k])
        return n.outputs[2]
    # Fels-Anteil: Höhe + Steilheit + Rauschen (unregelmäßige Grenze)
    rockf = math_("MAXIMUM", mr(sz.outputs["Z"], 3.0, 14.0), mr(sn.outputs["Z"], 0.9, 0.7))
    rockf = math_("ADD", rockf, math_("MULTIPLY", noise_(0.06, 4), 0.5))
    if force_rock:  # Hügel Safa/Marwa: ganz Fels, kleine Sandflecken
        rockf = math_("ADD", 0.62, math_("MULTIPLY", noise_(0.5, 4), 0.25))
    rk = ramp(rockf, [(0.5, (0, 0, 0)), (0.68, (1, 1, 1))])
    # Sand: große Flecken + mittlere Variation + Kies-Sprenkel
    sand = ramp(noise_(0.025, 3), [(0.3, (0.45, 0.34, 0.23)), (0.55, (0.6, 0.47, 0.33)), (0.75, (0.68, 0.55, 0.4))])
    sand = mix(0.35, sand, ramp(noise_(0.4, 6), [(0.35, (0.55, 0.43, 0.3)), (0.65, (0.72, 0.58, 0.42))]), "MIX")
    vo = N.new("ShaderNodeTexVoronoi")
    vo.inputs["Scale"].default_value = 26.0
    vo.inputs["Randomness"].default_value = 1.0
    L.new(tc.outputs["Object"], vo.inputs["Vector"])
    grav = mr(vo.outputs["Distance"], 0.12, 0.05)
    grav = math_("MULTIPLY", grav, mr(noise_(0.18, 3), 0.45, 0.65))
    sand = mix(grav, sand, (0.25, 0.19, 0.15))
    # Fels: dunkler Granit, hellere verwitterte Flächen, Schichten
    rock = ramp(noise_(0.05, 5), [(0.3, (0.15, 0.115, 0.095)), (0.55, (0.27, 0.21, 0.17)), (0.8, (0.42, 0.33, 0.26))])
    wv = N.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.bands_direction = "Z"
    wv.inputs["Scale"].default_value = 0.08
    wv.inputs["Distortion"].default_value = 6.0
    wv.inputs["Detail"].default_value = 3.0
    L.new(tc.outputs["Object"], wv.inputs["Vector"])
    rock = mix(math_("MULTIPLY", wv.outputs["Fac"], 0.1), rock, (0.36, 0.28, 0.22))
    col = mix(rk, sand, rock)
    L.new(col, b.inputs["Base Color"])
    # Relief: große Risse im Fels (Voronoi-Kanten) + feines Korn
    vc = N.new("ShaderNodeTexVoronoi")
    vc.feature = "DISTANCE_TO_EDGE"
    vc.inputs["Scale"].default_value = 0.6 if force_rock else 0.35
    L.new(tc.outputs["Object"], vc.inputs["Vector"])
    crack = mr(vc.outputs["Distance"], 0.0, 0.08)
    hgt = math_("ADD", math_("MULTIPLY", crack, math_("MULTIPLY", rk, 0.22 if force_rock else 1.0)),
                math_("MULTIPLY", noise_(1.2, 8), 0.9 if force_rock else 0.6))
    hgt = math_("ADD", hgt, math_("MULTIPLY", grav, 0.3))
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.45
    bp.inputs["Distance"].default_value = 0.15
    L.new(hgt, bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


# ---------------------------------------------------------------- Himmel + Sonne
def sun_dir(rot_deg):
    return (Euler([math.radians(a) for a in rot_deg]).to_matrix() @ Vector((0, 0, 1))).normalized()


def sky(mode, sun_rot, amb, sun_glow=1.0, stars=0.0):
    """Himmel per Verlauf + Sonnenscheibe + Schein um die Sonne (kein Nebel-Effekt nötig).
    mode: day | noon | golden | morning | dusk"""
    w = bpy.data.worlds.new(mode)
    Q.sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    N, L = nt.nodes, nt.links
    for n in list(N):
        N.remove(n)
    out = N.new("ShaderNodeOutputWorld")
    bg = N.new("ShaderNodeBackground")
    tc = N.new("ShaderNodeTexCoord")
    nrm = N.new("ShaderNodeVectorMath")
    nrm.operation = "NORMALIZE"
    L.new(tc.outputs["Generated"], nrm.inputs[0])
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(nrm.outputs[0], sep.inputs[0])
    cr = N.new("ShaderNodeValToRGB")
    L.new(sep.outputs["Z"], cr.inputs["Fac"])
    E = cr.color_ramp.elements
    pal = {
        "day": [(0.0, (0.78, 0.74, 0.66)), (0.12, (0.5, 0.6, 0.75)), (0.6, (0.16, 0.3, 0.6))],
        "noon": [(0.0, (0.95, 0.9, 0.8)), (0.15, (0.62, 0.7, 0.82)), (0.65, (0.25, 0.42, 0.72))],
        "golden": [(0.0, (1.0, 0.62, 0.34)), (0.1, (0.72, 0.52, 0.45)), (0.3, (0.33, 0.37, 0.55)), (0.7, (0.1, 0.16, 0.36))],
        "morning": [(0.0, (0.95, 0.72, 0.55)), (0.12, (0.6, 0.6, 0.68)), (0.6, (0.2, 0.32, 0.58))],
        "dusk": [(0.0, (0.7, 0.33, 0.16)), (0.08, (0.32, 0.18, 0.2)), (0.25, (0.07, 0.07, 0.16)), (0.7, (0.01, 0.015, 0.05))],
    }[mode]
    E[0].position, E[0].color = pal[0][0], (*pal[0][1], 1)
    E[1].position, E[1].color = pal[-1][0], (*pal[-1][1], 1)
    for p, c in pal[1:-1]:
        e = E.new(p)
        e.color = (*c, 1)
    col = cr.outputs["Color"]
    sd = sun_dir(sun_rot)
    dot = N.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    L.new(nrm.outputs[0], dot.inputs[0])
    dot.inputs[1].default_value = tuple(sd)
    cl = N.new("ShaderNodeMath")
    cl.operation = "MAXIMUM"
    L.new(dot.outputs["Value"], cl.inputs[0])
    cl.inputs[1].default_value = 0.0
    scol = {"day": (1.0, 0.95, 0.85), "noon": (1.0, 0.97, 0.9), "golden": (1.0, 0.7, 0.4), "morning": (1.0, 0.8, 0.6),
            "dusk": (1.0, 0.5, 0.25)}[mode]
    acc = col
    for pw, gain in ((1800.0, 60.0 * sun_glow), (60.0, 1.2 * sun_glow), (6.0, 0.25 * sun_glow)):
        p = N.new("ShaderNodeMath")
        p.operation = "POWER"
        L.new(cl.outputs[0], p.inputs[0])
        p.inputs[1].default_value = pw
        g = N.new("ShaderNodeMath")
        g.operation = "MULTIPLY"
        L.new(p.outputs[0], g.inputs[0])
        g.inputs[1].default_value = gain
        ad = N.new("ShaderNodeMix")
        ad.data_type = "RGBA"
        ad.blend_type = "ADD"
        L.new(g.outputs[0], ad.inputs["Factor"])
        L.new(acc, ad.inputs[6])
        ad.inputs[7].default_value = (*scol, 1)
        acc = ad.outputs[2]
    if stars:
        vo = N.new("ShaderNodeTexVoronoi")
        vo.inputs["Scale"].default_value = 200.0
        L.new(tc.outputs["Generated"], vo.inputs["Vector"])
        mr = N.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.05
        mr.inputs["From Max"].default_value = 0.0
        mr.inputs["To Max"].default_value = stars
        L.new(vo.outputs["Distance"], mr.inputs["Value"])
        hz = N.new("ShaderNodeMapRange")
        hz.inputs["From Min"].default_value = 0.15
        hz.inputs["From Max"].default_value = 0.45
        L.new(sep.outputs["Z"], hz.inputs["Value"])
        st = N.new("ShaderNodeMath")
        st.operation = "MULTIPLY"
        L.new(mr.outputs[0], st.inputs[0])
        L.new(hz.outputs[0], st.inputs[1])
        ad = N.new("ShaderNodeMix")
        ad.data_type = "RGBA"
        ad.blend_type = "ADD"
        ad.inputs["Factor"].default_value = 1.0
        L.new(acc, ad.inputs[6])
        L.new(st.outputs[0], ad.inputs[7])
        acc = ad.outputs[2]
    L.new(acc, bg.inputs["Color"])
    lp = N.new("ShaderNodeLightPath")
    bg2 = N.new("ShaderNodeBackground")
    bg2.inputs["Color"].default_value = (*amb[0], 1)
    bg2.inputs["Strength"].default_value = amb[1]
    mx = N.new("ShaderNodeMixShader")
    L.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
    L.new(bg2.outputs[0], mx.inputs[1])
    L.new(bg.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], out.inputs[0])
    w.mist_settings.start = 45.0
    w.mist_settings.depth = 650.0
    w.mist_settings.falloff = "QUADRATIC"
    return w


LIGHT = {  # Sonnenstand je Tageszeit: (Rotation, Stärke, Farbe, Umgebung, Dunst-Farbe, Dunst)
    "day": ((52, 0, -35), 4.2, (1.0, 0.9, 0.78), ((0.62, 0.68, 0.82), 0.75), (0.78, 0.72, 0.64), 0.35),
    "noon": ((18, 0, -20), 4.4, (1.0, 0.96, 0.9), ((0.7, 0.72, 0.78), 0.65), (0.9, 0.84, 0.74), 0.38),
    "golden": ((74, 0, -62), 3.6, (1.0, 0.62, 0.34), ((0.55, 0.5, 0.62), 0.6), (0.85, 0.58, 0.4), 0.38),
    "morning": ((70, 0, 75), 3.2, (1.0, 0.72, 0.48), ((0.6, 0.6, 0.72), 0.65), (0.82, 0.68, 0.58), 0.36),
    "dusk": ((84, 0, -70), 2.2, (1.0, 0.48, 0.24), ((0.32, 0.34, 0.52), 0.55), (0.32, 0.22, 0.24), 0.36),
}


def light(mode, stars=0.0):
    rot, en, colr, amb, mc, ma = LIGHT[mode]
    sky(mode, rot, amb, stars=stars)
    Q.sun("sun", rot, en, colr, shadow=True, angle=0.4)
    return dict(mist_col=mc, mist_amt=ma)


# ---------------------------------------------------------------- Gelände
_PEAKS = []


def _peaks():
    """Einzelne Granitgipfel rings um das Tal (verschieden hoch und breit), dazwischen Sättel; Pass im Norden frei."""
    if _PEAKS:
        return _PEAKS
    rnd = random.Random(17)
    for i in range(70):
        a = rnd.uniform(0, 2 * math.pi)
        big = i < 46
        rn = rnd.uniform(1.45, 3.2) if big else rnd.uniform(0.98, 1.4)
        x, y = AX * rn * math.cos(a), AY * rn * math.sin(a)
        h = (rnd.uniform(38, 80) + 60 * rnd.random() ** 2 * (rn - 1.2)) if big else rnd.uniform(6, 22)
        r = rnd.uniform(55, 120) if big else rnd.uniform(14, 32)
        if y > 0 and abs(x - PASS.x) < 45:  # Pass im Norden: niedrig
            h *= 0.3
        _PEAKS.append((x, y, h, r, rnd.uniform(0, 100)))
    return _PEAKS


def height(x, y):
    """Höhe des Geländes (m): fast ebener Talboden mit Trockenbett, ringsum einzelne, zerklüftete Granitberge."""
    r = math.sqrt((x / AX) ** 2 + (y / AY) ** 2)
    h = 0.35 * noise.noise(Vector((x * 0.05, y * 0.05, 1.3))) + 0.15 * noise.noise(Vector((x * 0.2, y * 0.2, 3.1)))
    h += 4.0 * max(0.0, r - 0.6) ** 2  # Rand steigt sanft an
    # Trockenbett (Wadi) quer durchs Tal (Nord-Süd, leicht gewunden): hier rannte Hadschar „im Tal“
    cx = 1.5 + 6.0 * math.sin(y * 0.03)
    h -= 0.75 * math.exp(-((x - cx) / 5.0) ** 2) * (1 - min(1.0, max(0.0, (r - 0.5) / 0.3)))
    m, msum = 0.0, 0.0
    for px, py, ph, pr, seed in _peaks():
        d2 = ((x - px) ** 2 + (y - py) ** 2) / (pr * pr)
        if d2 < 6.0:
            v = ph * math.exp(-1.6 * d2)
            m = max(m, v)
            msum += v
    m += 0.3 * (msum - m)  # Gipfel nicht aufeinanderstapeln (sonst riesige Wände)
    if m > 0.5:
        p = Vector((x * 0.02, y * 0.02, 0.0))
        rid = 1.0 - abs(noise.noise(p * 1.7 + Vector((3, 1, 0))))
        rid2 = 1.0 - abs(noise.noise(p * 4.5 + Vector((7, 2, 0))))
        gully = noise.fractal(p * 9.0, 0.7, 2.0, 4)
        m *= 0.55 + 0.5 * rid + 0.12 * rid2
        m += min(1.0, m / 30.0) * (0.045 * m * gully + 1.5 * noise.noise(p * 22.0))
    return h + max(0.0, m)


def terrain(n=260, size=620.0):
    bm = bmesh.new()
    def warp(u):
        return size * (0.22 * u + 0.78 * u ** 3)
    vs = []
    for j in range(n + 1):
        y = warp(-1 + 2 * j / n)
        row = []
        for i in range(n + 1):
            x = warp(-1 + 2 * i / n)
            row.append(bm.verts.new((x, y, height(x, y))))
        vs.append(row)
    for j in range(n):
        for i in range(n):
            bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
    me = bpy.data.meshes.new("terrain")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    if "terrain_m" not in M:
        M["terrain_m"] = terrain_mat()
    me.materials.append(M["terrain_m"])
    o = bpy.data.objects.new("terrain", me)
    Q.link(o)
    return o


def ground_z(x, y):
    return height(x, y)


# ---------------------------------------------------------------- Felsen, Büsche, Bäume
_TPL = {}


def _rock_mesh(name, seed, sub=3, rough=0.35):
    rnd = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    off = Vector((rnd.uniform(0, 50), rnd.uniform(0, 50), rnd.uniform(0, 50)))
    sc = Vector((rnd.uniform(0.8, 1.4), rnd.uniform(0.7, 1.2), rnd.uniform(0.45, 0.8)))
    for v in bm.verts:
        d = v.co.normalized()
        k = 1.0 + rough * noise.noise(d * 1.6 + off) + 0.12 * noise.noise(d * 5.0 + off)
        v.co = Vector((d.x * sc.x, d.y * sc.y, d.z * sc.z)) * k
        if v.co.z < -0.15:
            v.co.z = -0.15 + (v.co.z + 0.15) * 0.3
    # flache Bruchflächen
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0.55 * sc.z),
                           plane_no=Vector((rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), 1)).normalized(), clear_outer=True)
    bmesh.ops.contextual_create(bm, geom=[e for e in bm.edges if e.is_boundary])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def _templates():
    if _TPL:
        return
    for k in range(7):
        me = _rock_mesh(f"tpl_rock{k}", 100 + k)
        me.materials.append(M["rock"] if k % 3 else M["rock2"])
        _TPL[f"rock{k}"] = me
    for k in range(4):
        _TPL[f"shrub{k}"] = _shrub_mesh(f"tpl_shrub{k}", 200 + k, green=(k == 3))


def _inst(key, name, loc, rot=(0, 0, 0), scale=1.0):
    o = bpy.data.objects.new(name, _TPL[key])
    Q.link(o)
    o.location = loc
    o.rotation_euler = rot
    o.scale = (scale, scale, scale) if isinstance(scale, (int, float)) else scale
    return o


def _shrub_mesh(name, seed, green=False):
    """Trockener Dornbusch: viele dünne, verzweigte Äste + kleine Blattbüschel (ein Objekt)."""
    rnd = random.Random(seed)
    bm = bmesh.new()

    def twig(p, d, L_, r, depth):
        q = p + d * L_
        steps = 3
        for s in range(steps):
            a = p + (q - p) * (s / steps)
            b = p + (q - p) * ((s + 1) / steps)
            rr = r * (1 - 0.6 * s / steps)
            g = bmesh.ops.create_cone(bm, cap_ends=False, segments=5, radius1=rr, radius2=rr * 0.7, depth=(b - a).length)
            rot = (b - a).to_track_quat("Z", "Y").to_matrix().to_4x4()
            for v in g["verts"]:
                v.co = rot @ v.co + (a + b) / 2
        if depth > 0:
            for _ in range(rnd.randint(2, 3)):
                nd = (d + Vector((rnd.uniform(-0.8, 0.8), rnd.uniform(-0.8, 0.8), rnd.uniform(-0.1, 0.6)))).normalized()
                twig(q, nd, L_ * rnd.uniform(0.55, 0.75), r * 0.6, depth - 1)
        else:
            for _ in range(2):
                g = bmesh.ops.create_icosphere(bm, subdivisions=SHRUB_SUB, radius=rnd.uniform(0.04, 0.08))
                c = q + Vector((rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05), rnd.uniform(-0.03, 0.05)))
                for v in g["verts"]:
                    v.co = Vector((v.co.x * 1.4, v.co.y * 1.4, v.co.z * 0.7)) + c
    for _ in range(rnd.randint(4, 6)):
        d = Vector((rnd.uniform(-0.7, 0.7), rnd.uniform(-0.7, 0.7), 1)).normalized()
        twig(Vector((0, 0, 0)), d, rnd.uniform(0.25, 0.4), 0.02, 2)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M["shrub_g"] if green else M["shrub"])
    return me


def scatter(seed=3, n_rocks=620, n_shrubs=None, keep=()):
    """Felsbrocken am Rand der Berge und im Tal, Dornbüsche im Talboden. keep = [(x, y, r)] frei lassen (Wege, Szenen)."""
    _templates()
    rnd = random.Random(seed)
    n_shrubs = N_SHRUBS if n_shrubs is None else n_shrubs

    def free(x, y):
        return all((x - a) ** 2 + (y - b) ** 2 > r * r for a, b, r in keep)
    k = 0
    tries = 0
    while k < n_rocks and tries < n_rocks * 8:
        tries += 1
        near = k < n_rocks * 0.6
        if near:  # im Tal (dort spielt alles): kleine bis mittlere Brocken
            rr = 78.0 * math.sqrt(rnd.random())
            a = rnd.uniform(0, 2 * math.pi)
            x, y = rr * math.cos(a), rr * math.sin(a) * 0.85
            s = rnd.choice([rnd.uniform(0.12, 0.35), rnd.uniform(0.2, 0.6), rnd.uniform(0.4, 1.1)])
        else:  # Fuß der Berge: große Blöcke
            a = rnd.uniform(0, 2 * math.pi)
            r = rnd.uniform(0.78, 1.35)
            x, y = AX * r * math.cos(a), AY * r * math.sin(a)
            s = rnd.uniform(1.0, 4.5)
        if not free(x, y):
            continue
        _inst(f"rock{rnd.randint(0, 6)}", f"rk{k}", (x, y, ground_z(x, y) - 0.15 * s),
              rot=(rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), rnd.uniform(0, 6.28)), scale=s)
        k += 1
    k = 0
    tries = 0
    while k < n_shrubs and tries < n_shrubs * 8:
        tries += 1
        rr = 95.0 * math.sqrt(rnd.random())
        a = rnd.uniform(0, 2 * math.pi)
        x, y = rr * math.cos(a), rr * math.sin(a) * 0.85
        if not free(x, y):
            continue
        s = rnd.uniform(0.5, 1.3)
        _inst(f"shrub{rnd.randint(0, 3)}", f"sb{k}", (x, y, ground_z(x, y) - 0.03), rot=(0, 0, rnd.uniform(0, 6.28)), scale=s)
        k += 1


PEB_SUB = 2       # Kiesel-Unterteilung (Folge 3: 1 = schneller)
SHRUB_SUB = 1     # Blattbüschel der Dornbüsche
FAR_LEAVES = 2600  # Blattbüschel der fernen Akazien
N_SHRUBS = 170


def pebbles(name, center, size, n, seed=0, rmin=0.015, rmax=0.06):
    rnd = random.Random(seed)
    bm = bmesh.new()
    for _ in range(n):
        r = rnd.uniform(rmin, rmax)
        x, y = center[0] + rnd.uniform(-size[0] / 2, size[0] / 2), center[1] + rnd.uniform(-size[1] / 2, size[1] / 2)
        c = Vector((x, y, ground_z(x, y) + r * 0.25))
        g = bmesh.ops.create_icosphere(bm, subdivisions=PEB_SUB, radius=r)
        sc = Vector((rnd.uniform(0.7, 1.3), rnd.uniform(0.7, 1.3), rnd.uniform(0.4, 0.7)))
        for v in g["verts"]:
            v.co = Vector((v.co.x * sc.x, v.co.y * sc.y, v.co.z * sc.z)) + c
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p_ in me.polygons:
        p_.use_smooth = True
    me.materials.append(M["stone"])
    o = bpy.data.objects.new(name, me)
    Q.link(o)
    return o


def acacia(name, loc, h=5.2, spread=4.2, seed=1):
    """Schirmakazie: knorriger Stamm teilt sich in mehrere Äste, flache, breite Krone aus Blattbüscheln."""
    rnd = random.Random(seed)
    root = Q.empty(name, loc)
    bm = bmesh.new()

    def seg_(a, b, r0, r1):
        g = bmesh.ops.create_cone(bm, cap_ends=False, segments=9, radius1=r0, radius2=r1, depth=(b - a).length)
        rot = (b - a).to_track_quat("Z", "Y").to_matrix().to_4x4()
        for v in g["verts"]:
            v.co = rot @ v.co + (a + b) / 2
    def limb_(p, d, L_, r0, r1, n=4, bend=0.35, depth=0):
        """gebogener Ast aus n Stücken; verzweigt sich am Ende (depth > 0)"""
        d = d.normalized()
        pts = [p]
        for k in range(n):
            d = (d + Vector((rnd.uniform(-bend, bend), rnd.uniform(-bend, bend), rnd.uniform(-bend * 0.4, bend * 0.6)))).normalized()
            pts.append(pts[-1] + d * (L_ / n))
        for k in range(n):
            seg_(pts[k], pts[k + 1], r0 + (r1 - r0) * k / n, r0 + (r1 - r0) * (k + 1) / n)
        if depth > 0:
            for _ in range(rnd.randint(2, 3)):
                nd = (d + Vector((rnd.uniform(-0.9, 0.9), rnd.uniform(-0.9, 0.9), rnd.uniform(0.1, 0.6)))).normalized()
                limb_(pts[-1], nd, L_ * rnd.uniform(0.45, 0.65), r1, r1 * 0.45, n=3, bend=0.4, depth=depth - 1)
        return pts[-1]
    lean = Vector((rnd.uniform(-0.15, 0.15), rnd.uniform(-0.15, 0.15), 1.0))
    fork = limb_(Vector((0, 0, -0.2)), lean, h * 0.4, 0.24, 0.17, n=4, bend=0.12)
    nlimb = rnd.randint(3, 4)
    for i in range(nlimb):
        a = 2 * math.pi * i / nlimb + rnd.uniform(-0.4, 0.4)
        d = Vector((math.cos(a) * 0.95, math.sin(a) * 0.95, rnd.uniform(0.8, 1.2)))
        limb_(fork, d, spread * rnd.uniform(0.62, 0.8), 0.14, 0.07, n=4, bend=0.22, depth=2)
    me = bpy.data.meshes.new(f"{name}_wood")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(M["bark"])
    o = bpy.data.objects.new(f"{name}_wood", me)
    Q.link(o)
    o.parent = root
    # Krone: flacher Schirm aus sehr vielen kleinen Blattbüscheln (spitzenartig, Lücken zum Himmel)
    bm = bmesh.new()
    for i in range(FAR_LEAVES if name.startswith("tree_far") else 2600):
        a = rnd.uniform(0, 2 * math.pi)
        rr = spread * (rnd.random() ** 0.6) * 1.1
        if noise.noise(Vector((math.cos(a) * rr * 0.8, math.sin(a) * rr * 0.8, seed))) > 0.25:
            continue  # Lücken
        c = Vector((math.cos(a) * rr * 1.08, math.sin(a) * rr * 0.92, h * 0.86 + rnd.uniform(-0.2, 0.28) - 0.4 * (rr / spread) ** 2))
        g = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
        s_ = rnd.uniform(0.07, 0.16)
        for v in g["verts"]:
            v.co = Vector((v.co.x * s_ * 1.5, v.co.y * s_ * 1.5, v.co.z * 0.5 * s_)) + c
    me = bpy.data.meshes.new(f"{name}_crown")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(M["leaf"])
    o = bpy.data.objects.new(f"{name}_crown", me)
    Q.link(o)
    o.parent = root
    return root


def hill_z(loc, r, h, x, y):
    """Höhe der Hügeloberfläche (ohne Brocken) an (x, y); außerhalb 0."""
    d = math.hypot(x - loc.x, y - loc.y)
    if d >= r + 0.4:
        return 0.0
    q = max(0.0, (d - 0.4) / r)
    u = 1 - q ** (1 / 0.8)
    return h * (1 - (1 - u) ** 1.6) - 0.4


def rock_hill(name, loc, r, h, seed=0, clear=()):
    """Felsiger Hügel (Safa / Marwa): aufgetürmte Granitblöcke über einem Kegel."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    n = 120
    rings = 36
    vs = []
    for j in range(rings + 1):
        u = j / rings
        row = []
        for i in range(n):
            a = 2 * math.pi * i / n
            rr = r * (1 - u) ** 0.8 + 0.4
            d = Vector((math.cos(a), math.sin(a), 0))
            k = 1 + 0.18 * noise.noise(d * 2 + Vector((seed, u * 3, 0)))
            z = h * (1 - (1 - u) ** 1.6) + 0.5 * noise.noise(Vector((a * 2, u * 4, seed))) + 0.25 * noise.noise(Vector((a * 9, u * 14, seed)))
            px, py = loc.x + d.x * rr * k, loc.y + d.y * rr * k
            z += (0.15 * noise.noise(Vector((px * 0.9, py * 0.9, seed))) + 0.08 * noise.noise(Vector((px * 2.6, py * 2.6, seed + 3)))) * min(1.0, u * 4)
            row.append(bm.verts.new((px, py, z - 0.4)))
        vs.append(row)
    for j in range(rings):
        for i in range(n):
            bm.faces.new((vs[j][i], vs[j][(i + 1) % n], vs[j + 1][(i + 1) % n], vs[j + 1][i]))
    bm.faces.new(vs[-1])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    if "rock_m" not in M:
        M["rock_m"] = terrain_mat(force_rock=True)
    me.materials.append(M["rock_m"])
    o = bpy.data.objects.new(name, me)
    Q.link(o)
    _templates()
    for k in range(340):
        a = rnd.uniform(0, 2 * math.pi)
        u = rnd.uniform(0.0, 0.92)
        rr = r * (1 - u) ** 0.8
        z = h * (1 - (1 - u) ** 1.6)
        s = (rnd.uniform(0.35, 1.2) if k % 3 else rnd.uniform(1.0, 2.4)) * (1.25 - 0.55 * u)
        bx, by = loc.x + rr * math.cos(a), loc.y + rr * math.sin(a)
        if any((bx - cx) ** 2 + (by - cy) ** 2 < cr * cr for cx, cy, cr in clear):
            continue
        _inst(f"rock{rnd.randint(0, 6)}", f"{name}_b{k}", (loc.x + rr * math.cos(a), loc.y + rr * math.sin(a), z - 0.5 * s),
              rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(0, 6.28)), scale=s)
    return o


def hill_pebbles(name, loc, r, h, n=1600, seed=0):
    """Steine und Geröll auf dem Hügel (sieht man beim Hinauflaufen von nah)."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        d = r * math.sqrt(rnd.random()) * 0.98
        x, y = loc.x + d * math.cos(a), loc.y + d * math.sin(a)
        rad = rnd.choice([rnd.uniform(0.02, 0.06), rnd.uniform(0.05, 0.14)])
        c = Vector((x, y, hill_z(loc, r, h, x, y) + rad * 0.2))
        g = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=rad)
        sc = Vector((rnd.uniform(0.7, 1.3), rnd.uniform(0.7, 1.3), rnd.uniform(0.4, 0.75)))
        for v in g["verts"]:
            v.co = Vector((v.co.x * sc.x, v.co.y * sc.y, v.co.z * sc.z)) + c
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p_ in me.polygons:
        p_.use_smooth = True
    me.materials.append(M["stone"])
    o = bpy.data.objects.new(name, me)
    Q.link(o)
    return o


def hill_top(loc, h):
    return Vector((loc.x, loc.y, h + 0.15))


def hillock():
    """Leicht erhöhtes, rötliches Hügelchen: hier wird das Haus Allahs stehen (Bukhari 3364: „wie ein Hügel“)."""
    bm = bmesh.new()
    n, rings = 40, 8
    vs = []
    for j in range(rings + 1):
        u = j / rings
        row = []
        for i in range(n):
            a = 2 * math.pi * i / n
            rr = 7.0 * (1 - u) + 0.3
            row.append(bm.verts.new((HILLOCK.x + rr * math.cos(a), HILLOCK.y + rr * math.sin(a) * 0.85,
                                     1.3 * math.sin(u * math.pi / 2) ** 1.5 - 0.15 + 0.08 * noise.noise(Vector((a, u * 3, 4))))))
        vs.append(row)
    for j in range(rings):
        for i in range(n):
            bm.faces.new((vs[j][i], vs[j][(i + 1) % n], vs[j + 1][(i + 1) % n], vs[j + 1][i]))
    bm.faces.new(vs[-1])
    me = bpy.data.meshes.new("hillock")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(M["mound"])
    o = bpy.data.objects.new("hillock", me)
    Q.link(o)
    return o


def valley(seed=3, keep=(), tree=True, hills=True):
    """Das ganze Tal (statisch)."""
    mats()
    terrain()
    if tree:
        acacia("tree", TREE, seed=2)
        for i, (x, y, s) in enumerate(((-28, -40, 0.7), (35, -30, 0.6), (-60, 40, 0.75), (70, 5, 0.65), (20, 48, 0.55))):
            acacia(f"tree_far{i}", Vector((x, y, ground_z(x, y))), h=4.0 * s / 0.7, spread=3.4 * s / 0.7, seed=10 + i)
    if hills:
        def line(a, b, n=10):
            return [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n, 1.3) for k in range(n + 1)]
        rock_hill("safa", SAFA, 12.0, SAFA_H, seed=1, clear=line((SAFA.x + 1.2, SAFA.y - 1.0), (-31.5, 11.5)))
        rock_hill("marwa", MARWA, 11.0, MARWA_H, seed=2, clear=line((MARWA.x - 1.0, MARWA.y - 0.4), (27.0, 18.5)))
        hill_pebbles("peb_safa", SAFA, 12.0, SAFA_H, seed=3)
        hill_pebbles("peb_marwa", MARWA, 11.0, MARWA_H, seed=4)
    hillock()
    keep = list(keep) + [(TREE.x, TREE.y, 5.5), (SAFA.x, SAFA.y, 13), (MARWA.x, MARWA.y, 12), (HILLOCK.x, HILLOCK.y, 8)]

    def seg_keep(pts, r=2.6):
        out = []
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            n = max(1, int(math.hypot(bx - ax, by - ay) / 1.5))
            out += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n, r) for k in range(n + 1)]
        return out
    keep += seg_keep([(6.4, -9.0), (2.5, 0.0), (-3.0, 10.0), (-8.5, 22.0), (-12.0, 34.0), (-16.0, 50.0), (-18.0, 64.0)])
    keep += seg_keep([(-3.5, 7.6), (3.3, -8.0)]) + seg_keep([(11.5, -3.2), (7.6, -8.4)]) + seg_keep([(-15.5, -7.0), (-4.6, -10.8)])
    keep += seg_keep([(-31.5, 11.5), (-44.8, 17.0)]) + seg_keep([(27.0, 18.5), (45.0, 21.6)])
    scatter(seed, keep=keep)
    pebbles("peb_tree", (TREE.x - 2, TREE.y + 1), (16, 14), 900, seed=1)
    pebbles("peb_wadi", (2, 12), (14, 30), 900, seed=2, rmax=0.09)
    return {}


# ---------------------------------------------------------------- Dinge unter dem Baum
def bundle(name, loc, parent=None, rot=(0, 0, 0), light=1.0, scale=1.0):
    """Baby Ismail (Prophet): NUR als Licht – ein gewickeltes Tuch-Bündel, aus dessen Öffnung warmes Licht scheint.
    Lokal: lange Achse = Y, Kopfende (Licht) bei -Y, oben = +Z."""
    root = Q.empty(name, loc, parent, rot=rot)
    root.scale = (scale, scale * 1.12, scale)
    cl = Q.loft(f"{name}_cloth", [(-0.25, 0.025, 0.02), (-0.21, 0.075, 0.065), (-0.12, 0.1, 0.088), (0.0, 0.112, 0.096),
                                  (0.1, 0.11, 0.096), (0.17, 0.104, 0.094), (0.21, 0.098, 0.09)],
                M["cloth"], parent=root, seg=32, folds=(7, 0.05, 0.06, 3), cap_top=False)
    cl.rotation_euler = (math.pi / 2, 0, 0)
    cl.modifiers.new("solid", "SOLIDIFY").thickness = 0.012
    Q.ball(f"{name}_wrap", (0.0, 0.04, 0.045), (0.105, 0.19, 0.065), M["cloth"], parent=root, seg=24).rotation_euler = (0.0, 0.35, 0.4)
    # Kopfende: Tuch-Kapuze (Wulst), darin nur Licht
    core = Q.ball(f"{name}_light", (0, -0.235, 0.05), 0.07, Q.glow_mat(f"{name}_lm", (1.0, 0.93, 0.72), 14.0 * light), parent=root, seg=24)
    soft = Q.ball(f"{name}_soft", (0, -0.235, 0.06), (0.17, 0.17, 0.15), Q.glow_mat(f"{name}_sm", (1.0, 0.82, 0.5), 1.8 * light, 0.5,
                  fresnel=True), parent=root, seg=24)
    lt = Q.point(f"{name}_pl", (0, -0.3, 0.12), 1.6 * light, color=(1.0, 0.82, 0.55), radius=0.08, parent=root)
    return {"root": root, "core": core, "soft": soft, "light": lt}


def wiggle(o, t0, t1, amp=4.0, hz=2.2, seed=0):
    """Bündel bewegt sich unruhig (das Baby windet sich vor Durst)."""
    rnd = random.Random(seed)
    base = o.rotation_euler.copy()
    for f in range(Q.T(t0), Q.T(t1) + 1, 2):
        t = (f - 1) / Q.FPS
        e = 0.5 + 0.5 * math.sin(t * 0.9 + seed)
        o.rotation_euler = (base.x + math.radians(amp * e * math.sin(t * hz * 6.28 + 1)),
                            base.y + math.radians(amp * 0.6 * e * math.sin(t * hz * 1.3 * 6.28)),
                            base.z + math.radians(amp * 0.5 * math.sin(t * 1.1 * 6.28 + rnd.random())))
        o.keyframe_insert("rotation_euler", frame=f)


def waterskin(name, loc, full=True, rot=0.0):
    k = 1.0 if full else 0.35
    root = Q.empty(name, loc, rot=(0, 0, rot))
    Q.ball(f"{name}_body", (0, 0, 0.11 * k + 0.02), (0.22, 0.14 * (0.7 + 0.3 * k), 0.12 * k + 0.025), M["leather"], parent=root, seg=20)
    Q.limb(f"{name}_neck", (0.2, 0, 0.06 * k + 0.02), (0.32, 0, 0.1 * k + 0.05), 0.035, 0.025, M["leather"], parent=root)
    Q.torus(f"{name}_tie", (0.3, 0, 0.1 * k + 0.045), 0.03, 0.008, M["rope"], parent=root).rotation_euler = (0, math.pi / 2, 0)
    return root


def dates_bag(name, loc):
    root = Q.empty(name, loc)
    Q.loft(f"{name}_bag", [(0.0, 0.14, 0.12), (0.08, 0.17, 0.15), (0.2, 0.14, 0.12), (0.26, 0.1, 0.09), (0.28, 0.12, 0.1)], M["sack"],
           parent=root, seg=16, cap_top=False, folds=(6, 0.06, 0.1, 2))
    rnd = random.Random(3)
    for i in range(7):
        a = rnd.uniform(0, 6.28)
        Q.ball(f"{name}_d{i}", (0.06 * math.cos(a), 0.05 * math.sin(a), 0.27), (0.022, 0.014, 0.014), M["dates"], parent=root, seg=8)
    return root


def rug(name, loc, size=(1.6, 1.0), rot=0.0, mat=None):
    o = Q.box(name, (loc[0], loc[1], loc[2] + 0.01), (size[0], size[1], 0.02), mat or M["blanket_r"], rot=(0, 0, rot), bevel=0.005)
    return o


def camp_under_tree(full_skin=True, baby_rot=-1.57):
    """Hadschars Platz unter der Akazie: Decke, Baby-Bündel, Wasserschlauch, Dattelbeutel."""
    z = ground_z(BABY.x, BABY.y)
    rug("rug", (BABY.x - 0.2, BABY.y - 0.3, z), (1.5, 1.0), rot=0.4, mat=M["blanket_r"])
    B = bundle("baby", (BABY.x, BABY.y, z + 0.1), rot=(0, 0, baby_rot))
    ws = waterskin("skin", (BABY.x + 0.75, BABY.y - 0.55, z + 0.02), full=full_skin, rot=1.2)
    db = dates_bag("dates", (BABY.x - 0.85, BABY.y - 0.45, z + 0.02))
    return B, ws, db


# ---------------------------------------------------------------- Licht-Gestalten (Prophet Ibrahim, Engel)
def prophet_light(name, loc, strength=0.9, day=True):
    """Prophet Ibrahim: nur als goldene Licht-Säule (wie der Prophet ﷺ in Folge 1). Am Tag schwächeres Bodenlicht."""
    H = Q.holy_light(name, loc, height=2.2, strength=strength)
    if day:
        H["light"].data.energy = 22.0
        em = next(n for n in H["parts"][3].active_material.node_tree.nodes if n.type == "EMISSION")
        em.inputs["Strength"].default_value = 0.6
    return H


def glide(H, path, t0, speed=1.25):
    """Licht-Säule gleitet ruhig entlang path [(x, y)] (Höhe = Gelände). Gibt Ende-Zeit zurück."""
    root = H["root"]
    pts = [Vector((p[0], p[1], 0)) for p in path]
    total = sum((b - a).length for a, b in zip(pts, pts[1:]))
    dur = total / speed
    for f in range(Q.T(t0), Q.T(t0 + dur) + 1, 2):
        d = min(total, (f - Q.T(t0)) / Q.FPS * speed)
        acc = 0.0
        pos = pts[-1]
        for a, b in zip(pts, pts[1:]):
            L_ = (b - a).length
            if d <= acc + L_:
                pos = a + (b - a) * ((d - acc) / L_)
                break
            acc += L_
        root.location = (pos.x, pos.y, ground_z(pos.x, pos.y))
        root.keyframe_insert("location", frame=f)
    return t0 + dur


def hold_at(H, t, pos=None):
    if pos is not None:
        H["root"].location = (pos[0], pos[1], ground_z(pos[0], pos[1]))
    H["root"].keyframe_insert("location", frame=Q.T(t))


def pulse(mat, t, base, peak, up=0.25, down=1.2):
    """Licht leuchtet kurz auf (Emission-Stärke eines glow_mat)."""
    em = next(n for n in mat.node_tree.nodes if n.type == "EMISSION")
    s = em.inputs["Strength"]
    for tt, v in ((t - 0.05, base), (t + up, peak), (t + up + down, base)):
        s.default_value = v
        s.keyframe_insert("default_value", frame=max(1, Q.T(tt)))


def angel(name, loc, scale=1.0):
    """Der Engel: nur Licht – eine hohe, weiß-goldene Lichtsäule mit Strahlen und schwebenden Funken (keine Gestalt)."""
    root = Q.empty(name, loc)
    h = 3.4 * scale
    parts = []
    for k, (r, s, a, c) in enumerate(((0.9, 2.2, 0.45, (0.85, 0.9, 1.0)), (0.48, 6.0, 0.7, (0.95, 0.96, 1.0)),
                                      (0.14, 30.0, 1.0, (1.0, 1.0, 0.98)))):
        m = Q.glow_mat(f"{name}_m{k}", c, s, a, fresnel=True, grad_z=(-h / 2 * 0.25, h / 2))
        parts.append(Q.cyl(f"{name}_c{k}", (0, 0, h / 2), r * scale, h * (1 - 0.05 * k), m, seg=40, parent=root, caps=False))
    # weiche Aura (große, sehr transparente Hülle) + leuchtender Fleck am Boden
    rays = Q.empty(f"{name}_rays", (0, 0, h * 0.55), root)
    Q.ball(f"{name}_aura", (0, 0, 0), (1.6 * scale, 1.6 * scale, h * 0.62), Q.glow_mat(f"{name}_am", (0.95, 0.96, 1.0), 0.9, 0.35,
           fresnel=True), parent=rays, seg=32)
    gl = Q.cyl(f"{name}_pool", (0, 0, 0.02), 2.2 * scale, 0.01, Q.glow_mat(f"{name}_pm", (0.95, 0.95, 1.0), 1.2, 0.35, fresnel=False),
               seg=48, parent=root)
    rnd = random.Random(5)
    mm = Q.glow_mat(f"{name}_mote", (1.0, 0.95, 0.85), 22.0)
    motes = []
    for i in range(40):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0.2, 1.4) * scale
        o = Q.ball(f"{name}_mo{i}", (r * math.cos(a), r * math.sin(a), rnd.uniform(0.1, h)), rnd.uniform(0.007, 0.016), mm, seg=8,
                   parent=root)
        motes.append((o, rnd.uniform(0.2, 0.6)))
    lt = Q.point(f"{name}_l", (0, 0, 1.6), 900 * scale, color=(0.92, 0.95, 1.0), radius=0.6, parent=root)
    return {"root": root, "parts": parts, "rays": rays, "motes": motes, "light": lt, "h": h}


def angel_anim(A, t_on, t1, t_off=None):
    """Erscheinen (aus dem Nichts aufleuchten), Strahlen drehen sich langsam, Funken steigen."""
    root = A["root"]
    if t_on > 0:
        root.scale = (0.001, 0.001, 0.001)
        root.keyframe_insert("scale", frame=max(1, Q.T(t_on - 0.05)))
        root.scale = (1.15, 1.15, 1.15)
        root.keyframe_insert("scale", frame=Q.T(t_on + 0.6))
        root.scale = (1, 1, 1)
        root.keyframe_insert("scale", frame=Q.T(t_on + 1.4))
    if t_off is not None:
        root.keyframe_insert("scale", frame=Q.T(t_off))
        root.scale = (0.001, 0.001, 0.001)
        root.keyframe_insert("scale", frame=Q.T(t_off + 1.0))
    A["rays"].rotation_euler = (0, 0, 0)
    A["rays"].keyframe_insert("rotation_euler", frame=1)
    A["rays"].rotation_euler = (0, 0, 0.35 * (t1 + 2))
    A["rays"].keyframe_insert("rotation_euler", frame=Q.T(t1 + 2))
    Q.set_interp(A["rays"], "LINEAR")
    for o, sp in A["motes"]:
        z0 = o.location.z
        for f in range(1, Q.T(t1) + 2, 10):
            t = (f - 1) / Q.FPS
            o.location.z = (z0 + sp * t) % A["h"] + 0.05
            o.keyframe_insert("location", index=2, frame=f)


# ---------------------------------------------------------------- Quelle
def spring(t_burst, t1, wall_t0=None, wall_t1=None, loc=SPRING):
    """Zamzam bricht hervor: Lichtblitz am Boden, Wasserfontäne (Tropfen), Wasserfläche wächst, später Wall aus Sand.
    Ohne t_burst (None) ist die Quelle schon da (ruhig sprudelnd)."""
    z = ground_z(loc.x, loc.y)
    root = Q.empty("spring", (loc.x, loc.y, z))
    wm = water_mat()
    zmax = max(ground_z(loc.x + r_ * math.cos(a_ / 24 * 2 * math.pi), loc.y + r_ * math.sin(a_ / 24 * 2 * math.pi))
               for r_ in (0.2, 0.4, 0.62) for a_ in range(24))
    pz = max(0.03, zmax - z + 0.03)
    pool = Q.cyl("spring_pool", (0, 0, pz), 0.62, 0.04, wm, seg=48, parent=root)
    wet = Q.cyl("spring_wet", (0, 0, 0.008), 1.05, 0.012, M["wet"], seg=48, parent=root)
    rnd = random.Random(4)
    drops = []
    dm = water_mat("z_drop", (0.5, 0.62, 0.64), 0.75)
    gm = Q.glow_mat("z_drop_glint", (1.0, 0.96, 0.88), 4.0)
    for i in range(150):
        o = Q.ball(f"drop{i}", (0, 0, 0.05), rnd.uniform(0.004, 0.011), dm if i % 4 else gm, seg=8, parent=root)
        drops.append((o, rnd.uniform(0, 2 * math.pi), rnd.uniform(0.6, 2.2), rnd.uniform(0.0, 0.9), rnd.uniform(0.15, 0.6)))
    jet = []
    jm = water_mat("z_jet", (0.55, 0.68, 0.7), 0.6)
    for i in range(36):  # Strahl: senkrecht gestreckte Tropfen
        o = Q.ball(f"jet{i}", (0, 0, 0.05), (0.022, 0.022, rnd.uniform(0.08, 0.16)), jm if i % 3 else gm, seg=8, parent=root)
        jet.append((o, rnd.uniform(0, 1), rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05)))
    bub = []
    for i in range(10):  # Sprudeln an der Oberfläche
        o = Q.ball(f"bub{i}", (rnd.uniform(-0.15, 0.15), rnd.uniform(-0.15, 0.15), 0.05), (0.05, 0.05, 0.015), dm, seg=12, parent=root)
        bub.append((o, rnd.uniform(0, 1)))
    wall = None
    lumps = []
    if wall_t0 is not None:  # Wall aus vielen Sandklumpen (von Hand aufgeschüttet), feucht-dunkel zur Wasserseite
        wall = Q.empty("spring_wall", (0, 0, 0), root)
        msd = Q.pbr("z_wallsand", (0.42, 0.32, 0.22), 1.0, var=0.3, scale=5, bump=0.8, bscale=35)
        ring = Q.torus("wall_ring", (0, 0, -0.02), 0.78, 0.13, msd, seg=64, rseg=12, parent=wall, scale=(1, 1, 0.55))
        lumps.append((ring, 0))
        for i in range(64):
            a = 2 * math.pi * i / 64 + rnd.uniform(-0.03, 0.03)
            rr = 0.78 + rnd.uniform(-0.07, 0.07)
            o = Q.ball(f"wl{i}", (rr * math.cos(a), rr * math.sin(a), rnd.uniform(-0.02, 0.03)),
                       (rnd.uniform(0.05, 0.09), rnd.uniform(0.07, 0.12), rnd.uniform(0.04, 0.08)),
                       M["wet"] if (i * 7) % 5 == 0 else msd, seg=10, parent=wall)
            o.rotation_euler = (rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), a + rnd.uniform(-0.6, 0.6))
            lumps.append((o, i))
    def keys(o, f, **kw):
        for k, v in kw.items():
            setattr(o, k, v)
            o.keyframe_insert(k, frame=f)
    fb = Q.T(t_burst) if t_burst is not None else 1
    t_off = 0.0 if t_burst is not None else 6.0  # Quelle schon da: nur ruhiges Sprudeln
    if t_burst is not None:
        for o in (pool, wet):
            keys(o, max(1, fb - 1), scale=(0.001, 0.001, 1))
        keys(pool, fb + int(0.6 * Q.FPS), scale=(1, 1, 1))
        keys(wet, fb + int(1.2 * Q.FPS), scale=(1, 1, 1))
        flash = Q.ball("burst_flash", (0, 0, 0.05), (0.6, 0.6, 0.2), Q.glow_mat("burst_m", (0.9, 0.95, 1.0), 25.0, 0.8, fresnel=True),
                       parent=root, seg=24)
        keys(flash, max(1, fb - 3), scale=(0.001, 0.001, 0.001))
        keys(flash, fb + 2, scale=(1.4, 1.4, 1.4))
        keys(flash, fb + int(0.8 * Q.FPS), scale=(0.001, 0.001, 0.001))
    # Tropfen: steigen in Bögen auf und fallen (Fontäne, am Anfang höher), danach ruhiges Sprudeln
    f_end = Q.T(t1) + 2
    for o, a, v, ph, spread in drops:
        o.scale = (0.001, 0.001, 0.001)
        o.keyframe_insert("scale", frame=1)
        o.keyframe_insert("scale", frame=max(1, fb - 1))
        o.scale = (1, 1, 1)
        o.keyframe_insert("scale", frame=fb)
        for f in range(fb, f_end, 2):
            t = (f - fb) / Q.FPS + t_off
            big = max(0.25, 1.0 - t / 3.0)  # nach 3 s nur noch sprudeln
            per = 0.55 + 0.35 * v * big
            u = ((t + ph * per) % per) / per
            h = 4 * u * (1 - u) * (0.25 + 0.95 * v * big)
            rr = spread * u * (0.4 + 0.6 * big)
            o.location = (rr * math.cos(a), rr * math.sin(a), 0.04 + h)
            o.keyframe_insert("location", frame=f)
    for o, ph, jx, jy in jet:  # Strahl: anfangs hoch (bis ~1,4 m), dann niedriger
        o.scale = (0.001, 0.001, 0.001)
        o.keyframe_insert("scale", frame=1)
        o.keyframe_insert("scale", frame=max(1, fb - 1))
        for f in range(fb, f_end, 2):
            t = (f - fb) / Q.FPS + t_off
            hmax = 0.25 + 1.2 * max(0.0, 1.0 - t / 2.5)
            u = ((t * 1.6 + ph) % 1.0)
            o.location = (jx * (1 + u), jy * (1 + u), 0.05 + hmax * (1 - (1 - u) ** 2))
            o.scale = (1, 1, 1) if hmax > 0.3 else (0.6, 0.6, 0.5)
            o.keyframe_insert("location", frame=f)
            o.keyframe_insert("scale", frame=f)
    for o, ph in bub:
        for f in range(fb, f_end, 3):
            t = (f - fb) / Q.FPS
            s = 0.6 + 0.6 * abs(math.sin((t + ph) * 5.0))
            o.scale = (s, s, s * 0.8)
            o.keyframe_insert("scale", frame=f)
        o.scale = (0.001, 0.001, 0.001)
        o.keyframe_insert("scale", frame=max(1, fb - 1))
    if wall is not None:  # Klumpen wachsen nacheinander (vorn zuerst, wo die Hände schieben)
        order = sorted(lumps, key=lambda x: (abs(((2 * math.pi * x[1] / 64) - math.pi / 2 + math.pi) % (2 * math.pi) - math.pi)))
        for k, (o, i) in enumerate(order):
            tk = wall_t0 + (wall_t1 - wall_t0) * k / len(order)
            sc_ = o.scale.copy()
            o.scale = (0.001, 0.001, 0.001)
            o.keyframe_insert("scale", frame=1)
            o.keyframe_insert("scale", frame=max(1, Q.T(tk)))
            o.scale = sc_
            o.keyframe_insert("scale", frame=max(2, Q.T(tk + 0.35)))
        # Wasser steigt im Wall
        keys(pool, Q.T(wall_t0), location=(0, 0, pz))
        keys(pool, Q.T(wall_t1 + 1.0), location=(0, 0, max(0.1, pz + 0.01)))
    return {"root": root, "pool": pool, "wall": wall, "z": z}


def kaaba_ghost(t_on, loc=HILLOCK, size=(4.6, 5.2, 6.0)):
    """Vorausblick: goldene Umrisslinien eines Würfels auf dem Hügelchen (hier wird das Haus Allahs stehen)."""
    z = 1.0
    root = Q.empty("kaaba_ghost", (loc.x, loc.y, z))
    m = Q.glow_mat("ghost_m", (1.0, 0.8, 0.45), 6.0, 0.85)
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2]
    corners = [Vector((x, y, zz)) for zz in (0, sz) for x in (-sx, sx) for y in (-sy, sy)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (4, 5), (4, 6), (5, 7), (6, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
    segs = []
    for k, (a, b) in enumerate(edges):
        o = Q.limb(f"ghost_e{k}", corners[a], corners[b], 0.035, 0.035, m, seg=8, parent=root)
        segs.append(o)
    face = Q.box("ghost_face", (0, 0, sz / 2), (size[0], size[1], sz), Q.glow_mat("ghost_f", (1.0, 0.78, 0.4), 0.6, 0.12), parent=root)
    root.scale = (1, 1, 0.001)
    root.keyframe_insert("scale", frame=max(1, Q.T(t_on - 0.05)))
    root.scale = (1, 1, 1)
    root.keyframe_insert("scale", frame=Q.T(t_on + 2.2))
    Q.point("ghost_l", (loc.x, loc.y, 3.0), 300, color=(1.0, 0.8, 0.5), radius=1.0)
    return root


# ---------------------------------------------------------------- Kamele, Vögel, Zelte
def camel(name, loc, yaw=0.0, seed=0, load=True, sit=False):
    """Dromedar (Blick lokal -Y wie die Figuren). Gelenke: neck (Kopf nickt), Beine leg.FL/FR/BL/BR."""
    rnd = random.Random(seed)
    mc = Q.pbr(f"camel_{seed % 3}", [c * rnd.uniform(0.85, 1.1) for c in (0.62, 0.46, 0.3)], 0.95, var=0.12, scale=3, bump=0.2, bscale=60)
    C = {"name": name}
    root = Q.empty(f"{name}_root", loc, rot=(0, 0, yaw))
    C["root"] = root
    bz = 1.75 if not sit else 0.75
    body = Q.empty(f"{name}_body", (0, 0, bz), root)
    C["body"] = body
    tor = Q.loft(f"{name}_torso", [(-1.02, 0.1, 0.12, 0, 0.0), (-0.92, 0.28, 0.33, 0, 0.02), (-0.7, 0.36, 0.42, 0, 0.0),
                                   (-0.35, 0.38, 0.44, 0, 0.0), (0.0, 0.4, 0.46, 0, -0.02), (0.35, 0.39, 0.45, 0, -0.05),
                                   (0.65, 0.35, 0.44, 0, -0.08), (0.85, 0.28, 0.38, 0, -0.1), (0.98, 0.12, 0.18, 0, -0.08)],
                 mc, parent=body, seg=32, folds=(5, 0.02, 0.02, seed))
    tor.rotation_euler = (math.pi / 2, 0, 0)
    Q.ball(f"{name}_hump", (0, 0.08, 0.36), (0.28, 0.48, 0.36), mc, parent=body, seg=24)
    neck = Q.empty(f"{name}_neck", (0, -0.85, 0.05), body)
    C["neck"] = neck
    pts = [Vector((0, 0, 0)), Vector((0, -0.35, -0.12)), Vector((0, -0.6, 0.15)), Vector((0, -0.7, 0.6))]
    Q.ball(f"{name}_nj0", pts[0], 0.24, mc, parent=neck, seg=16)
    for k in range(3):
        Q.limb(f"{name}_nk{k}", pts[k], pts[k + 1], 0.24 - 0.05 * k, 0.19 - 0.05 * k, mc, seg=16, parent=neck)
        Q.ball(f"{name}_nj{k + 1}", pts[k + 1], 0.19 - 0.05 * k, mc, parent=neck, seg=14)
    head = Q.empty(f"{name}_head", (0, -0.72, 0.68), neck)
    C["head"] = head
    Q.ball(f"{name}_skull", (0, -0.05, 0.02), (0.12, 0.2, 0.13), mc, parent=head, seg=16)
    Q.ball(f"{name}_snout", (0, -0.27, -0.03), (0.08, 0.14, 0.09), mc, parent=head, seg=14)
    for s_ in (-1, 1):
        Q.ball(f"{name}_ear{s_}", (0.08 * s_, 0.08, 0.12), (0.025, 0.02, 0.05), mc, parent=head, seg=8)
        Q.ball(f"{name}_eye{s_}", (0.095 * s_, -0.1, 0.06), 0.018, M["camel_d"], parent=head, seg=8)
    # Halfter
    Q.torus(f"{name}_halter", (0, -0.2, -0.01), 0.1, 0.01, M["rope"], parent=head, scale=(1.0, 0.8, 1)).rotation_euler = (1.4, 0, 0)
    for nm, (x, y) in (("FL", (-0.2, -0.62)), ("FR", (0.2, -0.62)), ("BL", (-0.2, 0.62)), ("BR", (0.2, 0.62))):
        hip = Q.empty(f"{name}_leg.{nm}", (x, y, -0.25), body)
        if sit:
            Q.ball(f"{name}_fold.{nm}", (0, 0, -0.45), (0.12, 0.35, 0.1), mc, parent=hip, seg=10)
        else:
            Q.limb(f"{name}_thigh.{nm}", (0, 0, 0.15), (0, 0.04, -0.72), 0.16, 0.075, mc, seg=12, parent=hip)
            knee = Q.empty(f"{name}_knee.{nm}", (0, 0.04, -0.72), hip)
            Q.ball(f"{name}_kn.{nm}", (0, 0, 0), 0.075, mc, parent=knee, seg=10)
            Q.limb(f"{name}_shin.{nm}", (0, 0, 0), (0, 0, -0.68), 0.055, 0.045, mc, seg=10, parent=knee)
            Q.ball(f"{name}_foot.{nm}", (0, -0.04, -0.7), (0.085, 0.11, 0.035), M["camel_d"], parent=knee, seg=10)
            C[f"knee.{nm}"] = knee
        C[f"leg.{nm}"] = hip
    Q.limb(f"{name}_tail", (0, 1.05, 0.0), (0, 1.12, -0.5), 0.03, 0.015, mc, parent=body, seg=6)
    if load:  # Sattel mit Decke + Lasten
        Q.ball(f"{name}_saddle", (0, 0.05, 0.62), (0.34, 0.5, 0.12), M["wood"], parent=body, seg=16)
        Q.box(f"{name}_blanket", (0, 0.05, 0.52), (0.95, 1.1, 0.04), rnd.choice([M["blanket_r"], M["blanket_b"]]), parent=body,
              rot=(0, 0, 0), bevel=0.01)
        for s_ in (-1, 1):
            Q.loft(f"{name}_bag{s_}", [(0.0, 0.16, 0.2), (0.15, 0.2, 0.25), (0.35, 0.18, 0.22), (0.45, 0.12, 0.15)], M["sack"],
                   parent=body, seg=14, folds=(5, 0.05, 0.08, seed + s_)).location = (0.5 * s_, 0.25, 0.0)
    Q.blob(f"{name}_blob", root, 0.9)
    root["person"] = 1
    return C


def camel_walk(C, path, t0, speed=1.3, z_of=None):
    """Kamel geht (Passgang: beide Beine einer Seite zugleich), Körper schaukelt, Hals nickt."""
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
        z = z_of(pos.x, pos.y) if z_of else ground_z(pos.x, pos.y)
        root.location = (pos.x, pos.y, z)
        root.keyframe_insert("location", frame=f)
        root.rotation_euler = (0, 0, math.atan2(dv.x, -dv.y))
        root.keyframe_insert("rotation_euler", index=2, frame=f)
        ph = d / 1.6 * math.pi
        body.location.z = bz + 0.04 * abs(math.sin(ph))
        body.rotation_euler = (math.radians(1.5 * math.sin(2 * ph)), math.radians(3.5 * math.sin(ph)), 0)
        body.keyframe_insert("location", index=2, frame=f)
        body.keyframe_insert("rotation_euler", frame=f)
        neck.rotation_euler = (math.radians(6 * math.sin(2 * ph + 0.6)), 0, 0)
        neck.keyframe_insert("rotation_euler", frame=f)
        for nm, s in (("FL", 1), ("BL", 1), ("FR", -1), ("BR", -1)):
            hip = C.get(f"leg.{nm}")
            kn = C.get(f"knee.{nm}")
            if hip is None or kn is None:
                continue
            sw = math.sin(ph) * s
            hip.rotation_euler = (math.radians(22 * sw), 0, 0)
            hip.keyframe_insert("rotation_euler", frame=f)
            kn.rotation_euler = (math.radians(max(0.0, -math.cos(ph) * s) * 38), 0, 0)
            kn.keyframe_insert("rotation_euler", frame=f)
    return t0 + dur


def rider(name, C, seed=0, **kw):
    """Reiter auf dem Kamel (sitzt auf dem Sattel)."""
    P = Q.person(name, (0, 0, 0), sit=True, seed=seed, **kw)
    P["root"].parent = C["body"]
    P["root"].location = (0, 0.05, 0.5)
    P["root"].rotation_euler = (0, 0, 0)
    for s_, nm in ((-1, "L"), (1, "R")):  # Beine hängen seitlich herab
        Q.limb(f"{name}_legh.{nm}", (0.3 * s_, -0.1, 0.35), (0.42 * s_, -0.2, -0.25), 0.07, 0.06,
               Q.pbr(f"robe_{name}", (0.7, 0.62, 0.5), 0.9), parent=C["body"], seg=10)
    return P


def bird(name, seed=0):
    root = Q.empty(name)
    Q.ball(f"{name}_b", (0, 0, 0), (0.06, 0.2, 0.05), M["bird"], parent=root, seg=10)
    wings = []
    for s_ in (-1, 1):
        h = Q.empty(f"{name}_wh{s_}", (0.04 * s_, -0.02, 0.01), root)
        o = Q.ball(f"{name}_w{s_}", (0.32 * s_, 0.02, 0), (0.32, 0.09, 0.012), M["bird"], parent=h, seg=10)
        wings.append((h, s_))
    Q.ball(f"{name}_t", (0, 0.22, 0), (0.05, 0.08, 0.01), M["bird"], parent=root, seg=8)
    return root, wings


def birds_circle(center, radius, height, n, t1, seed=0, scale=2.2, speed=0.22):
    """Vögel kreisen über der Quelle (Bukhari 3364: die Karawane sah einen Vogel kreisen)."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        root, wings = bird(f"bird{i}", seed + i)
        root.scale = (scale, scale, scale)
        r = radius * rnd.uniform(0.6, 1.2)
        hz = height + rnd.uniform(-6, 8)
        ph = rnd.uniform(0, 2 * math.pi)
        sp = speed * rnd.uniform(0.8, 1.2) * (1 if i % 3 else -1)
        for f in range(1, Q.T(t1) + 2, 2):
            t = (f - 1) / Q.FPS
            a = ph + sp * t
            root.location = (center[0] + r * math.cos(a), center[1] + r * math.sin(a), hz + 1.5 * math.sin(t * 0.7 + ph))
            root.rotation_euler = (0, math.radians(-25 * (1 if sp > 0 else -1)), a + (math.pi if sp > 0 else 0))
            root.keyframe_insert("location", frame=f)
            root.keyframe_insert("rotation_euler", frame=f)
            flap = math.sin(t * 9 + ph) if (t + ph) % 4 < 1.4 else 0.15
            for h, s_ in wings:
                h.rotation_euler = (0, math.radians(-30 * flap * s_), 0)
                h.keyframe_insert("rotation_euler", frame=f)
        out.append(root)
    return out


def tent(name, loc, yaw=0.0, w=4.0, d=2.6, h=1.9, mat=None, seed=0):
    """Zelt (A-Form): zwei schräge, leicht durchhängende Stoffbahnen über einer Firststange, Giebel hinten zu, vorn offen."""
    rnd = random.Random(seed)
    root = Q.empty(name, loc, rot=(0, 0, yaw))
    mt = mat or M["tent"]
    bm = bmesh.new()
    nx, ny = 10, 6
    for side in (-1, 1):
        g = []
        for j in range(ny + 1):
            row = []
            for i in range(nx + 1):
                x = -w / 2 + w * i / nx
                v = j / ny
                y = side * (d / 2) * v
                z = h * (1 - v) - 0.12 * math.sin(math.pi * v) * (0.6 + 0.4 * math.sin(math.pi * i / nx)) + rnd.uniform(-0.015, 0.015)
                row.append(bm.verts.new((x, y, max(0.03, z))))
            g.append(row)
        for j in range(ny):
            for i in range(nx):
                q = (g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i])
                bm.faces.new(q if side > 0 else tuple(reversed(q)))
    # Giebel hinten (Dreieck)
    v0, v1, v2 = bm.verts.new((w / 2, -d / 2, 0.03)), bm.verts.new((w / 2, d / 2, 0.03)), bm.verts.new((w / 2, 0, h))
    bm.faces.new((v0, v1, v2))
    me = bpy.data.meshes.new(f"{name}_me")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mt)
    o = bpy.data.objects.new(f"{name}_cloth", me)
    Q.link(o)
    o.parent = root
    o.modifiers.new("solid", "SOLIDIFY").thickness = 0.02
    Q.limb(f"{name}_ridge", (-w / 2 - 0.1, 0, h + 0.02), (w / 2 + 0.1, 0, h + 0.02), 0.03, 0.03, M["wood"], parent=root, seg=6)
    for k, x in enumerate((-w / 2, w / 2)):
        Q.limb(f"{name}_pole{k}", (x, 0, 0), (x, 0, h + 0.05), 0.03, 0.025, M["wood"], parent=root, seg=6)
    for k in range(4):  # Spannseile
        sx = -1 if k < 2 else 1
        sy = -1 if k % 2 else 1
        Q.limb(f"{name}_rope{k}", (sx * w / 2, 0, h), (sx * (w / 2 + 0.8), sy * 0.6, 0.0), 0.006, 0.006, M["rope"], parent=root, seg=4)
    return root


def campfire(name, loc, energy=60.0):
    root = Q.empty(name, loc)
    for k in range(5):
        a = k * 1.26
        Q.cyl(f"{name}_w{k}", (0.12 * math.cos(a), 0.12 * math.sin(a), 0.05), 0.03, 0.4, M["wood"], seg=6,
              rot=(math.pi / 2, 0, a + math.pi / 2), parent=root)
    fl = Q.ball(f"{name}_fl", (0, 0, 0.18), (0.12, 0.12, 0.25), Q.glow_mat(f"{name}_fm", (1.0, 0.5, 0.15), 12.0, 0.9, fresnel=True),
                parent=root, seg=12)
    lt = Q.point(f"{name}_l", (0, 0, 0.5), energy, color=(1.0, 0.55, 0.25), radius=0.2, parent=root)
    return {"root": root, "light": lt, "flame": fl}


def no_glow_shadows():
    """Licht-Gestalten (reine Emission) werfen keinen Schatten (sonst: große, harte Schatten-Vielecke am Boden)."""
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.data.materials:
            continue
        if all(m is not None and m.node_tree and not any(n.type == "BSDF_PRINCIPLED" for n in m.node_tree.nodes)
               for m in o.data.materials):
            o.visible_shadow = False


def pop_in(o, t, dur=0.6):
    s = o.scale.copy()
    o.scale = (0.001, 0.001, 0.001)
    o.keyframe_insert("scale", frame=1)
    o.keyframe_insert("scale", frame=max(1, Q.T(t)))
    o.scale = s * 1.05
    o.keyframe_insert("scale", frame=Q.T(t + dur * 0.7))
    o.scale = s
    o.keyframe_insert("scale", frame=Q.T(t + dur))


# ---------------------------------------------------------------- Hadschars Hände (Ich-Sicht)
def pov_arms(cam, skin=(0.42, 0.28, 0.19), sleeve=(0.12, 0.1, 0.12)):
    """Beide Hände + Ärmel (Kind der Kamera). Kamera-Raum: x rechts, y oben, -z nach vorn.
    Rückgabe: {"L": wrist, "R": wrist}; Pose per pose_hands()."""
    ms = Q.pbr("pov_skin_h", skin, 0.55, var=0.05, scale=12)
    mr = Q.pbr("pov_sleeve_h", sleeve, 0.95, var=0.1, scale=8, bump=0.1, bscale=40)
    H = {}
    for s_, nm in ((-1, "L"), (1, "R")):
        w = Q.empty(f"pov_wrist.{nm}", (0.15 * s_, -0.3, -0.5), cam)
        # Hand: lokal +Y = Finger nach vorn, +Z = Handrücken
        Q.ball(f"pov_palm.{nm}", (0, 0.05, 0), (0.042, 0.055, 0.016), ms, parent=w, seg=18)
        for i in range(4):
            x = (-0.025 + 0.017 * i) * s_
            Q.limb(f"pov_f{i}.{nm}", (x, 0.09, 0.0), (x * 1.05, 0.15 - 0.008 * abs(i - 1.5), -0.012), 0.0085, 0.007, ms, parent=w, seg=8)
            Q.ball(f"pov_ft{i}.{nm}", (x * 1.05, 0.15 - 0.008 * abs(i - 1.5), -0.012), 0.0075, ms, parent=w, seg=8)
        Q.limb(f"pov_th.{nm}", (-0.035 * s_, 0.03, -0.004), (-0.06 * s_, 0.08, -0.01), 0.011, 0.009, ms, parent=w, seg=8)
        Q.limb(f"pov_wr.{nm}", (0, 0.0, 0), (0, -0.09, -0.01), 0.026, 0.03, ms, parent=w, seg=12)
        Q.limb(f"pov_sl.{nm}", (0, -0.06, -0.005), (0.04 * s_, -0.6, -0.05), 0.048, 0.07, mr, parent=w, seg=16)
        H[nm] = w
    return H


HAND_POSES = {
    # (Ort im Kamera-Raum, Drehung in Grad) je Hand – x rechts, y oben, z nach hinten (vorn = -z)
    "carry": {"L": ((-0.15, -0.47, -0.47), (-70, -10, -55)), "R": ((0.15, -0.48, -0.5), (-70, 10, 55))},
    "reach": {"L": ((-0.14, -0.36, -0.4), (-62, -18, -35)), "R": ((0.13, -0.06, -0.55), (-8, 10, -8))},
    "low": {"L": ((-0.2, -0.5, -0.35), (-80, 0, -10)), "R": ((0.2, -0.5, -0.35), (-80, 0, 10))},
    "dig": {"L": ((-0.17, -0.2, -0.48), (-115, -10, 20)), "R": ((0.17, -0.2, -0.48), (-115, 10, -20))},
    "dig_in": {"L": ((-0.08, -0.24, -0.52), (-115, -10, 45)), "R": ((0.08, -0.24, -0.52), (-115, 10, -45))},
    "hidden": {"L": ((-0.2, -0.9, -0.3), (-80, 0, -10)), "R": ((0.2, -0.9, -0.3), (-80, 0, 10))},
}


def pose_hands(H, t, pose, only=None):
    for nm in ("L", "R"):
        if only and nm != only:
            continue
        loc, rot = HAND_POSES[pose][nm]
        w = H[nm]
        w.location = loc
        w.rotation_euler = [math.radians(a) for a in rot]
        w.keyframe_insert("location", frame=max(1, Q.T(t)))
        w.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))


def hand_bob(H, t0, t1, amp=0.02, hz=1.9, seed=0):
    """Hände wippen beim Gehen/Laufen mit (zusätzlich zur Pose)."""
    for nm, ph in (("L", 0.0), ("R", 1.3)):
        w = H[nm]
        base = w.location.copy()
        for f in range(Q.T(t0), Q.T(t1) + 1, 2):
            t = (f - 1) / Q.FPS
            w.location = base + Vector((0, amp * abs(math.sin(t * hz * math.pi + ph)), amp * 0.5 * math.sin(t * hz * math.pi * 0.5 + ph)))
            w.keyframe_insert("location", frame=f)


# ---------------------------------------------------------------- Mas'a heute (Halle zwischen Safa und Marwa)
def masaa_mats():
    M["marble"] = Q.pbr("z_marble", (0.84, 0.83, 0.8), 0.28, var=0.06, scale=2.0, bump=0.02, bscale=10, spec=0.6)
    M["marble_g"] = Q.pbr("z_marble_g", (0.55, 0.53, 0.5), 0.15, var=0.08, scale=3.0, spec=0.7)
    M["ceil"] = Q.pbr("z_ceil", (0.82, 0.78, 0.7), 0.6, var=0.05, scale=1.0)
    M["gold"] = Q.pbr("z_gold", (0.85, 0.65, 0.3), 0.3, metal=0.9)
    M["lamp"] = Q.glow_mat("z_lamp", (1.0, 0.92, 0.8), 9.0)
    M["green"] = Q.glow_mat("z_green", (0.25, 1.0, 0.45), 14.0)
    M["steel"] = Q.pbr("z_steel", (0.75, 0.76, 0.78), 0.25, metal=0.9)
    M["white"] = Q.pbr("z_ihram", (0.93, 0.92, 0.89), 0.85, var=0.04, scale=8, bump=0.05, bscale=40)


def masaa(length=300.0, width=19.0, height=9.0):
    """Lange, helle Halle (x = Richtung Safa -> Marwa), Säulen, Bögen, Lichter, grüne Leuchten im Bereich des Tals,
    Trennwand in der Mitte, Zamzam-Wasserspender an der Seite."""
    masaa_mats()
    Q.box("m_floor", (0, 0, -0.05), (length, width, 0.1), M["marble"])
    Q.box("m_ceiling", (0, 0, height + 0.2), (length, width, 0.4), M["ceil"])
    for s_ in (-1, 1):
        Q.box(f"m_wall{s_}", (0, s_ * (width / 2 + 0.2), height / 2), (length, 0.4, height), M["ceil"])
    Q.box("m_divider", (0, 0, 0.45), (length, 0.5, 0.9), M["marble_g"], bevel=0.02)
    for i in range(int(length / 3.5)):  # Marmor-Bänder im Boden
        Q.box(f"m_band{i}", (i * 3.5 - length / 2, 0, 0.002), (0.35, width, 0.01), M["marble_g"])
    green = (-14.0, 14.0)
    k = 0
    for x in [i * 7.0 - length / 2 for i in range(int(length / 7.0) + 1)]:
        for y in (-width / 2 + 0.9, -width / 4, width / 4, width / 2 - 0.9):
            Q.cyl(f"m_col{k}", (x, y, height / 2), 0.42, height, M["marble"], seg=20)
            Q.cyl(f"m_cap{k}", (x, y, height - 0.3), 0.55, 0.3, M["gold"], seg=20)
            Q.cyl(f"m_base{k}", (x, y, 0.15), 0.55, 0.3, M["marble_g"], seg=20)
            k += 1
        # Querbalken + Leuchten
        Q.box(f"m_beam{x}", (x, 0, height - 0.15), (0.5, width, 0.3), M["ceil"])
        if green[0] <= x <= green[1]:
            for y in (-width / 3, 0, width / 3):
                Q.box(f"m_g{k}_{y}", (x + 3.5, y, height - 0.05), (5.5, 0.18, 0.08), M["green"])
        else:
            for y in (-width / 3, 0, width / 3):
                Q.cyl(f"m_l{k}_{y}", (x + 3.5, y, height - 0.05), 0.4, 0.08, M["lamp"], seg=16)
    # Lichtquellen (wenige, groß) + grünes Licht im Tal-Bereich
    for x in range(-96, 97, 16):
        Q.point(f"m_pl{x}", (x, 0, height - 1.0), 2600, color=(1.0, 0.93, 0.82), radius=2.0)
    for x in (-10, 0, 10):
        Q.point(f"m_gl{x}", (x, 0, height - 1.2), 1600, color=(0.35, 1.0, 0.5), radius=2.0)
    # Zamzam-Wasserspender an der Seite (Edelstahl-Behälter mit Hähnen + Becherständer)
    for i, x in enumerate((-30.0, -18.0, 22.0, 34.0)):
        for j in range(3):
            xx = x + j * 1.0
            Q.cyl(f"m_zz{i}_{j}", (xx, -width / 2 + 0.75, 0.75), 0.32, 1.5, M["steel"], seg=24)
            Q.limb(f"m_zt{i}_{j}", (xx, -width / 2 + 1.04, 0.55), (xx, -width / 2 + 1.16, 0.52), 0.02, 0.02, M["steel"], seg=8)
    return {"length": length, "width": width, "height": height, "green": green}


def pilgrim(name, loc, yaw, seed, woman=False):
    rnd = random.Random(seed)
    if woman:
        return Q.person(name, loc, yaw=yaw, seed=seed, head="khimar", robe=rnd.choice([(0.05, 0.05, 0.06), (0.9, 0.89, 0.86)]),
                        wrap=rnd.choice([(0.06, 0.06, 0.07), (0.92, 0.91, 0.88)]), height=rnd.uniform(0.92, 0.98))
    return Q.person(name, loc, yaw=yaw, seed=seed, head="bare", robe=(0.93, 0.92, 0.89), wrap=(0.93, 0.92, 0.89),
                    cloak=(0.94, 0.93, 0.9), height=rnd.uniform(0.96, 1.05))


def clear_cols(y):
    """Abstand zu den Säulenreihen der Mas'a-Halle (y = ±4,75 und ±8,6): sonst laufen Pilger durch Säulen."""
    a, sg = abs(y), (1 if y >= 0 else -1)
    if 3.85 < a < 5.65:
        a = 3.85 if a < 4.75 else 5.65
    a = min(a, 7.9)
    return sg * a


def far_crowd(name, x0, x1, y0, y1, n, seed=0):
    """Ferne Pilger als EIN Objekt (weiße Gestalten), bewegt sich als Ganzes langsam."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), clear_cols(rnd.uniform(y0, y1))
        h = rnd.uniform(1.6, 1.8)
        g = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.26, radius2=0.2, depth=h - 0.25)
        for v in g["verts"]:
            v.co += Vector((x, y, (h - 0.25) / 2))
        g = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.12)
        for v in g["verts"]:
            v.co += Vector((x, y, h - 0.1))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M["white"])
    o = bpy.data.objects.new(name, me)
    Q.link(o)
    return o
