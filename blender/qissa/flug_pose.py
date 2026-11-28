# Flug-Video v2 (Nutzer: „keine Köpfe/Hände/Körper durch Sitze, Bildschirme, Wände – verhalten wie im echten Leben“):
# Haltungen werden GERECHNET statt geraten:
#   - solve_arm(): Zwei-Gelenk-IK für Schulter/Ellenbogen (Hand an einen Punkt in der Welt),
#   - brace_real(): Schutzhaltung – Oberkörper so weit vor, bis der Kopf (mit Maske) 3 cm vor der Lehne des Vordersitzes ist,
#     Hände auf der Lehne über dem Kopf,
#   - Sauerstoffmasken: greifen, aufsetzen (Maske am Kopf, Schlauch dehnt sich per STRETCH_TO von der Service-Leiste zum Gesicht),
#     wieder abnehmen.
# Prüfen: blender/qissa/flug_check.py.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler
import lib as Q
import flug_world as FW

A_LEN, B_LEN = 0.28, 0.30          # Oberarm, Unterarm bis Handmitte (Rig-Einheiten, vor Skalierung)
PSU_Z = 1.59                       # Unterkante Service-Leiste (Masken-Austritt)


# ------------------------------------------------------------------------------------------ Grundlagen
def chain(P, *names):
    """Welt-Matrix eines Gelenks aus den AKTUELLEN Werten (ohne Szenen-Update; Eltern-Inverse sind Einheit)."""
    M = P["root"].matrix_basis.copy()
    for n in names:
        M = M @ P[n].matrix_basis
    return M


def front_y(r, z):
    """Vorderkante (zum Fluggast in Reihe r hin) der Lehne des Vordersitzes auf Höhe z (inkl. Bildschirm/Tablett)."""
    return (r + 1) * FW.ROW - 0.372 + 0.176 * (z - 0.88)


def kf_rot(o, t, rot_rad):
    o.rotation_euler = rot_rad
    o.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))


def set_body(P, chest=None, neck=None):
    if chest is not None:
        P["chest"].rotation_euler = [math.radians(a) for a in chest]
    if neck is not None:
        P["neck"].rotation_euler = [math.radians(a) for a in neck]


def key_body(P, t):
    P["chest"].keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))
    P["neck"].keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))


def solve_arm(P, side, target, pole=(0, 0, -1)):
    """Schulter-Euler + Ellenbogenwinkel, damit die Handmitte bei `target` (Welt) liegt; Ellenbogen zeigt Richtung `pole`."""
    Mc = chain(P, "hips", "chest")
    Ci = Mc.inverted()
    T = Ci @ Vector(target)
    S = P[f"sh.{side}"].location.copy()
    d = T - S
    if d.length < 1e-5:
        d = Vector((0, -1, 0))
    dh = d.normalized()
    L = min(max(d.length, abs(A_LEN - B_LEN) + 0.03), (A_LEN + B_LEN) * 0.995)
    ca = (A_LEN ** 2 + L ** 2 - B_LEN ** 2) / (2 * A_LEN * L)
    cg = (A_LEN ** 2 + B_LEN ** 2 - L ** 2) / (2 * A_LEN * B_LEN)
    al = math.acos(max(-1.0, min(1.0, ca)))
    g = math.acos(max(-1.0, min(1.0, cg)))
    p = (Ci.to_3x3() @ Vector(pole)).normalized()
    pp = p - p.dot(dh) * dh
    if pp.length < 1e-4:
        alt = Vector((0, 0, -1)) if abs(dh.z) < 0.9 else Vector((0, 1, 0))
        pp = alt - alt.dot(dh) * dh
    pp.normalize()
    u = math.cos(al) * dh + math.sin(al) * pp
    E = S + A_LEN * u
    f = (S + dh * L - E).normalized()
    w = f - f.dot(u) * u
    if w.length < 1e-4:
        w = -pp
    w.normalize()
    X, Y, Z = w.cross(u), -w, -u
    R = Matrix((X, Y, Z)).transposed()
    return R.to_euler("XYZ"), -(math.pi - g)


def pose_arm(P, side, target, pole=(0, 0, -1), hand_twist=0.0):
    """Wie set_arm, aber ohne Schlüssel (Grundhaltung beim Aufbau)."""
    e, ex = solve_arm(P, side, target, pole)
    P[f"sh.{side}"].rotation_euler = e
    P[f"el.{side}"].rotation_euler = (ex, 0, 0)
    P[f"hand.{side}"].rotation_euler = (0, 0, math.radians(hand_twist))


def lap_pose(P, spread=0.09):
    """Grundhaltung sitzend: Hände auf den Oberschenkeln (über dem Kissen, nicht darin)."""
    c = chain(P, "hips", "chest").translation
    for side in ("L", "R"):
        sx = outward(P, side)
        pose_arm(P, side, Vector((c.x + spread * sx, P["root"].location.y + 0.24, 0.73)), pole=(0.2 * sx, 0.7, -1.0))


def set_arm(P, side, t, target, pole=(0, 0, -1), hand_twist=0.0):
    e, ex = solve_arm(P, side, target, pole)
    kf_rot(P[f"sh.{side}"], t, e)
    kf_rot(P[f"el.{side}"], t, (ex, 0, 0))
    kf_rot(P[f"hand.{side}"], t, (0, 0, math.radians(hand_twist)))


def shoulder_world(P, side):
    return chain(P, "hips", "chest", f"sh.{side}").translation


def outward(P, side):
    """Welt-Richtung (x) von der Körpermitte zur Schulter."""
    c = chain(P, "hips", "chest").translation
    return 1.0 if shoulder_world(P, side).x > c.x else -1.0


def head_points(P):
    """Punktwolke aller Kopf-Teile (inkl. Maske) im Kopf-Raum (zwischengespeichert, nach neuen Kopf-Teilen löschen)."""
    if P.get("_hp") is not None:
        return P["_hp"]
    pts = []

    def walk(o, M):
        for c in o.children:
            Mc = M @ c.matrix_basis
            if c.type == "MESH" and not c.name.startswith("mskwtube"):
                me = c.data
                n = len(me.vertices)
                st = max(1, n // 50)
                pts.extend(Mc @ me.vertices[i].co for i in range(0, n, st))
            walk(c, Mc)

    walk(P["head"], Matrix.Identity(4))
    P["_hp"] = pts
    return pts


def head_world(P, loc=(0, 0, 0.11)):
    return chain(P, "hips", "chest", "neck", "head") @ Vector(loc)


def head_clear(P, r=None):
    """Kleinster Abstand (m) aller Kopfpunkte zur Lehne des Vordersitzes (negativ = steckt drin)."""
    r = P["row"] if r is None else r
    M = chain(P, "hips", "chest", "neck", "head")
    best = 9.0
    for p in head_points(P):
        w = M @ p
        best = min(best, front_y(r, w.z) - w.y)
    return best


def head_top(P):
    M = chain(P, "hips", "chest", "neck", "head")
    return max((M @ p for p in head_points(P)), key=lambda v: v.z)


# ------------------------------------------------------------------------------------------ Haltungen
def upright(P, t, seed=0, lean=-4.0, neck=(0, 0, 0)):
    set_body(P, (lean, 0, 0), neck)
    key_body(P, t)


def brace_real(P, t, seed=0, margin=0.03, neck=20.0, hands="seat", max_chest=52):
    """Schutzhaltung wie auf der Sicherheitskarte: Oberkörper vor, Stirn knapp an der Lehne des Vordersitzes,
    Hände übereinander auf der Lehne über dem Kopf. Gibt den Oberkörper-Winkel zurück."""
    rnd = random.Random(seed)
    tilt = rnd.uniform(-3, 3)
    nk = neck + rnd.uniform(-4, 4)
    best = 0
    for th in range(0, max_chest + 1, 2):
        set_body(P, (th, 0, tilt), (nk, 0, 0))
        if head_clear(P) < margin:
            break
        best = th
    set_body(P, (best, 0, tilt), (nk, 0, 0))
    key_body(P, t)
    if hands == "seat":
        top = head_top(P)
        hz = min(top.z + 0.07, 1.2)
        for side in ("L", "R"):
            sx = outward(P, side)
            c = chain(P, "hips", "chest").translation
            tgt = Vector((c.x + 0.075 * sx, front_y(P["row"], hz) - 0.045, hz))
            set_arm(P, side, t, tgt, pole=(0.8 * sx, -0.3, -1.0), hand_twist=90 * sx)
    elif hands == "lap":
        hands_lap(P, t)
    return best


def hands_lap(P, t, spread=0.09):
    c = chain(P, "hips", "chest").translation
    for side in ("L", "R"):
        sx = outward(P, side)
        set_arm(P, side, t, Vector((c.x + spread * sx, P["root"].location.y + 0.24, 0.73)), pole=(0.2 * sx, 0.7, -1.0))


def hands_armrest(P, t, window_side=None):
    """Hände umklammern die Armlehnen (Fensterplatz: außen Hand auf dem Oberschenkel)."""
    x0 = P["root"].location.x
    y0 = P["root"].location.y
    for side in ("L", "R"):
        sx = outward(P, side)
        ax = x0 + (0.235 if sx > 0 else -0.225)
        if abs(ax) > 1.55:   # keine Armlehne an der Wand: Hand auf dem Oberschenkel, Ellenbogen am Körper
            set_arm(P, side, t, Vector((x0 + 0.09 * sx, y0 + 0.22, 0.735)), pole=(0.1 * sx, 0.7, -1.0), hand_twist=90 * sx)
        else:
            set_arm(P, side, t, Vector((ax, y0 + 0.06, 0.72)), pole=(0.9 * sx, 0.3, -1.0), hand_twist=90 * sx)


def hands_dua(P, t, seed=0, high=0.0):
    """Bittgebet: Hände vor dem Gesicht/der Brust, Handflächen nach oben (sicher vor der Lehne)."""
    rnd = random.Random(seed)
    hc = head_world(P)
    r = P["row"]
    z = hc.z - 0.17 + high + rnd.uniform(-0.03, 0.03)
    y = min(hc.y + 0.24, front_y(r, z) - 0.08)
    for side in ("L", "R"):
        sx = outward(P, side)
        set_arm(P, side, t, Vector((hc.x + 0.075 * sx, y, z)), pole=(0.7 * sx, 0.2, -1.0), hand_twist=-60 * sx)


def hands_clap(P, t0, t1, seed=0):
    """Applaus: Hände vor der Brust klatschen (gerechnet, nicht in die Lehne)."""
    rnd = random.Random(seed)
    c = chain(P, "hips", "chest").translation
    r = P["row"]
    z = 1.0 + rnd.uniform(-0.04, 0.04)
    y = min(P["root"].location.y + 0.27, front_y(r, z) - 0.1)
    t = t0
    k = 0
    while t < t1:
        gap = 0.012 if k % 2 else 0.09
        for side in ("L", "R"):
            sx = outward(P, side)
            set_arm(P, side, t, Vector((c.x + gap * sx, y, z)), pole=(0.8 * sx, 0.3, -1.0), hand_twist=-80 * sx)
        t += 0.13 + rnd.uniform(-0.015, 0.015)
        k += 1


# ------------------------------------------------------------------------------------------ Sauerstoffmasken
def obj_matrix_at(o, t):
    """Lokale Matrix eines animierten Objekts zur Zeit t (aus den F-Kurven, ohne Szenen-Update)."""
    f = 1 + t * Q.FPS
    loc = list(o.location)
    rot = list(o.rotation_euler)
    for fc in Q.fcurves(o):
        if fc.data_path == "location":
            loc[fc.array_index] = fc.evaluate(f)
        elif fc.data_path == "rotation_euler":
            rot[fc.array_index] = fc.evaluate(f)
    return Matrix.Translation(loc) @ Euler(rot, "XYZ").to_matrix().to_4x4()


def mask_for(P, masks_by_seat):
    return masks_by_seat.get((P["row"], P["seat"]))


def dangling_cup(piv, t):
    """Welt-Ort der hängenden Maske zur Zeit t."""
    L = piv.get("L", 0.42)
    return obj_matrix_at(piv, t) @ Vector((0, 0, -L - 0.03))


def _vis(objs, t, visible):
    for o in objs:
        o.hide_render = not visible
        o.keyframe_insert("hide_render", frame=max(1, Q.T(t)))
        if t > 0:   # vorher umgekehrt
            o.hide_render = visible
            o.keyframe_insert("hide_render", frame=max(1, Q.T(t) - 1))
            o.hide_render = not visible


def tube_mesh(name, r=0.0036):
    bm = bmesh.new()
    g = bmesh.ops.create_cone(bm, cap_ends=False, segments=8, radius1=r, radius2=r, depth=1.0)
    bmesh.ops.rotate(bm, verts=g["verts"], cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(-90), 3, "X"))
    bmesh.ops.translate(bm, verts=g["verts"], vec=(0, 0.5, 0))
    return Q._obj(name, bm, FW.M["tube"], smooth=True)


def worn_mask(name, parent, cup_loc, cup_rot, psu_pt, strap=None):
    """Getragene Maske: Becher am Gesicht (Kind von `parent`), Gummiband, Beutel, Schlauch (dehnt sich zur Service-Leiste)."""
    FW.mats()
    parts = []
    cup = Q.cyl(f"mskw{name}_cup", cup_loc, 0.045, 0.07, FW.M["mask"], seg=18, parent=parent, r2=0.03)
    cup.rotation_euler = cup_rot
    parts.append(cup)
    bag = Q.ball(f"mskw{name}_bag", (0, 0.01, -0.07), (0.032, 0.026, 0.055), FW.M["maskbag"], parent=cup, seg=12)
    parts.append(bag)
    if strap:
        st = Q.torus(f"mskw{name}_strap", strap[0], strap[1], 0.0035, FW.M["tube"], seg=28, rseg=6, parent=parent, scale=strap[2])
        parts.append(st)
    end = Q.empty(f"mskw{name}_end", (0, 0, 0.04), cup)
    tb = tube_mesh(f"mskwtube{name}")
    tb.location = psu_pt
    c = tb.constraints.new("STRETCH_TO")
    c.target = end
    c.rest_length = 1.0
    c.volume = "NO_VOLUME"
    c.keep_axis = "PLANE_X"
    parts.append(tb)
    for o in parts:
        o["person"] = 1
    return parts


def mask_parts(piv):
    return [c for c in piv.children_recursive if c.type == "MESH"]


def person_mask(P, piv):
    """Getragene Maske für Fluggast P (versteckt, bis wear_* sie einblendet)."""
    psu = Vector((piv.location.x, piv.location.y, PSU_Z))
    parts = worn_mask(P["name"], P["head"], (0, -0.142, 0.083), (math.radians(90), 0, 0), psu,
                      strap=((0, 0.0, 0.1), 0.108, (1.0, 1.1, 1.0)))
    for o in parts:
        o.hide_render = True
    P["_hp"] = None
    P["worn"] = parts
    return parts


def wear_from_start(P, piv):
    """Maske schon auf (Einstellung beginnt danach)."""
    parts = P.get("worn") or person_mask(P, piv)
    for o in parts:
        o.hide_render = False
    for o in mask_parts(piv):
        o.hide_render = True


def put_on(P, piv, t_grab, t_on):
    """Greift die hängende Maske (Hände dorthin), zieht sie ans Gesicht, setzt sie auf."""
    parts = P.get("worn") or person_mask(P, piv)
    cupw = dangling_cup(piv, t_grab)
    upright(P, t_grab - 0.35, lean=-2)
    upright(P, t_on + 0.1, lean=4)
    for side in ("L", "R"):
        sx = outward(P, side)
        set_arm(P, side, t_grab - 0.35, cupw + Vector((0.05 * sx, -0.06, -0.1)), pole=(0.35 * sx, 0.5, -1.0))
        set_arm(P, side, t_grab, cupw + Vector((0.035 * sx, -0.02, 0)), pole=(0.35 * sx, 0.5, -1.0), hand_twist=60 * sx)
    face = head_world(P, (0, -0.15, 0.08))
    for side in ("L", "R"):
        sx = outward(P, side)
        set_arm(P, side, t_on, face + Vector((0.04 * sx, -0.02, 0.0)), pole=(0.9 * sx, 0.0, -1.0), hand_twist=70 * sx)
    _vis(mask_parts(piv), t_on, False)
    _vis(parts, t_on, True)


def take_off(P, piv, t_off, t_rel):
    """Maske ab: Hände ans Gesicht, Maske weg (hängt wieder an der Leiste)."""
    parts = P.get("worn") or person_mask(P, piv)
    face = head_world(P, (0, -0.15, 0.08))
    for side in ("L", "R"):
        sx = outward(P, side)
        set_arm(P, side, t_off, face + Vector((0.04 * sx, -0.02, 0.0)), pole=(0.9 * sx, 0.0, -1.0), hand_twist=70 * sx)
    _vis(parts, t_off + 0.15, False)
    _vis(mask_parts(piv), t_off + 0.15, True)
