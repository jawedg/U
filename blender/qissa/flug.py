# POV-Erinnerung „Was, wenn das dein letzter Flug ist?“ – alle Einstellungen in Blender. Aufruf:
#   blender -b --factory-startup --python blender/qissa/flug.py -- <einstellung> <ausgabe_ordner> [prozent] [samples] [standbild-zeiten]
# Längen und Ereignisse: src/flug/timeline.json (scripts/build_flug.py). Welt: blender/qissa/flug_world.py.
# Regeln: Menschen ohne Gesicht; ich bin die Kamera (Fensterplatz 0A, Sitznachbar 0B); keine KI-Koranrezitation (Ton: echte Aufnahme).
import bpy, sys, os, math, json, random
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import lib as Q
import mekka as MK
import medina as MD
import flug_world as FW
import flug_pose as FP

TL = json.load(open(os.environ.get("TL_FILE") or os.path.join(ROOT, "src", "flug", "timeline.json"), encoding="utf-8"))
SEG = {s["id"]: s for s in TL["segments"]}
LINE = {l["id"]: l for l in TL["lines"]}
REC = {r["id"]: r for r in TL.get("recites", [])}
EV = TL["events"]
Q.FPS = TL.get("render_fps", 30)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SHOT = argv[0] if argv else "kabine"
OUT = argv[1] if len(argv) > 1 else "/tmp/flug"
PCT = int(argv[2]) if len(argv) > 2 else 50
SAMPLES = int(argv[3]) if len(argv) > 3 else 8
STILLS = [float(x) for x in argv[4].split(",")] if len(argv) > 4 and argv[4] else None

S0 = SEG[SHOT]["start"]
D = SEG[SHOT]["dur"] + TL.get("xfade", 0.4)   # mit Handle für die Überblendung
SEATA = Vector((FW.SX["A"] + 0.06, -0.02, FW.EYE))


def lt(t_abs):
    return t_abs - S0


def ls(i):
    return lt(LINE[i]["start"])


def le(i):
    return lt(LINE[i]["start"] + LINE[i]["dur"])


def ev(k, alt=None):
    return lt(EV[k]) if k in EV else alt


def look(src, dst):
    return (Q.yaw_to(src, dst), Q.pitch_to(src, dst), 0)


def ck(rig, keys, **kw):
    """Q.cam_keys mit entfalteten Gierwinkeln (kein Dreh über ±180°)."""
    out, prev = [], None
    for t, pos, ang in keys:
        if ang is not None:
            y = ang[0]
            if prev is not None:
                while y - prev > 180:
                    y -= 360
                while y - prev < -180:
                    y += 360
            prev = y
            ang = (y, ang[1], ang[2])
        out.append((t, pos, ang))
    Q.cam_keys(rig, out, **kw)


def turbulence(shake, t0, t1, amp, seed=1, jolts=(), lift=()):
    """Erschütterung im Flugzeug: amp(t) = Stärke (0 ruhig … 1 schwer), jolts = [(t, stärke)] harte Stöße,
    lift = [(t, dauer, höhe)] Absacken (Magen hebt ab: Blick ruckt nach oben, dann nach unten)."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(8)]
    for f in range(Q.T(t0), Q.T(t1) + 1):
        t = (f - 1) / Q.FPS
        a = amp(t)
        n1 = math.sin(t * 9.3 + ph[0]) * 0.5 + math.sin(t * 15.7 + ph[1]) * 0.3 + math.sin(t * 23.1 + ph[2]) * 0.2
        n2 = math.sin(t * 7.1 + ph[3]) * 0.6 + math.sin(t * 19.3 + ph[4]) * 0.4
        n3 = math.sin(t * 2.3 + ph[5]) * 0.7 + math.sin(t * 5.9 + ph[6]) * 0.3
        rx = (n1 * 1.6 + n3 * 0.8) * a
        rz = (n2 * 1.3) * a
        ry = (n3 * 1.0 + n1 * 0.4) * a
        dz = (n1 * 0.012 + n3 * 0.01) * a
        dx = n2 * 0.006 * a
        for th, st in jolts:
            if 0 <= t - th < 0.7:
                e = math.exp(-(t - th) * 7.0) * st
                rx += math.sin((t - th) * 48) * 3.2 * e
                rz += math.sin((t - th) * 39 + 1) * 2.4 * e
                ry += math.sin((t - th) * 33 + 2) * 2.0 * e
                dz += math.sin((t - th) * 30) * 0.04 * e
        for th, du, hz in lift:
            if 0 <= t - th < du:
                u = (t - th) / du
                dz += hz * math.sin(math.pi * u) * (1 - u * 0.3)
                rx += -6 * hz * math.sin(math.pi * u)
        shake.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))
        shake.location = (dx, 0, dz)
        shake.keyframe_insert("rotation_euler", frame=f)
        shake.keyframe_insert("location", frame=f)


def jiggle(objs, t0, t1, amp, seed=0, step=0.1, axis_deg=4.0):
    """Köpfe/Körper der Fluggäste wackeln mit der Erschütterung (Nacken)."""
    rnd = random.Random(seed)
    for k, o in enumerate(objs):
        base = tuple(o.rotation_euler)
        t = t0 + rnd.uniform(0, step)
        while t < t1:
            a = amp(t) * axis_deg
            o.rotation_euler = (base[0] + math.radians(rnd.uniform(-a, a)), base[1] + math.radians(rnd.uniform(-a, a) * 0.6),
                                base[2] + math.radians(rnd.uniform(-a, a) * 0.8))
            o.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))
            t += step * rnd.uniform(0.8, 1.3)


def lights_level(C, t, cove=1.0, color=None):
    """Stimmungslicht (Lampen + leuchtende Leisten) auf Stufe `cove` (0 aus … 1 Nacht-Stimmung … 3 hell)."""
    for lo in C["cove_lights"]:
        lo.data.energy = 220 * cove
        lo.data.keyframe_insert("energy", frame=max(1, Q.T(t)))
        if color:
            lo.data.color = color
            lo.data.keyframe_insert("color", frame=max(1, Q.T(t)))
    FW.emit_strength(FW.M["cove"], t, 2.4 * cove)


def flicker_lights(C, t0, t1, seed=0, low=0.0, high=1.0):
    rnd = random.Random(seed)
    t = t0
    while t < t1:
        lights_level(C, t, rnd.choice((low, low, high * 0.3, high)))
        t += rnd.uniform(0.05, 0.25)
    lights_level(C, t1, high)


def main_lights(t_states, color=(1.0, 0.96, 0.9)):
    """Weiße Kabinenbeleuchtung (Decke, Flächenlichter nach unten): [(t, stärke)]."""
    out = []
    for k in range(5):
        ld = bpy.data.lights.new(f"main{k}", "AREA")
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = 0.6, 4.6
        ld.color = color
        ld.use_shadow = False
        lo = bpy.data.objects.new(f"main{k}", ld)
        Q.link(lo)
        lo.location = (0, FW.CAB_Y0 + 2.5 + k * 5.0, 2.16)
        for t, e in t_states:
            ld.energy = e
            ld.keyframe_insert("energy", frame=max(1, Q.T(t)))
        out.append(lo)
    return out


def window_light(t_states, color=(0.75, 0.82, 1.0), loc=(-2.4, 0.2, 1.15)):
    """Licht, das durch MEIN Fenster hereinfällt (Blitze, Mond, Lichter beim Landen)."""
    ld = bpy.data.lights.new("winlight", "AREA")
    ld.size = 0.6
    ld.color = color
    ld.use_shadow = False
    lo = bpy.data.objects.new("winlight", ld)
    Q.link(lo)
    lo.location = loc
    lo.rotation_euler = (0, math.radians(-90), 0)
    for t, e in t_states:
        ld.energy = e
        ld.keyframe_insert("energy", frame=max(1, Q.T(t)))
    return lo


def reading_lights(rows_seats, energy=18.0):
    """Ein paar Leselampen an (Lichtkegel nach unten auf den Sitz)."""
    out = []
    for r, k in rows_seats:
        x = FW.SX[k]
        ld = bpy.data.lights.new(f"read{r}{k}", "SPOT")
        ld.energy = energy
        ld.color = (1.0, 0.85, 0.62)
        ld.spot_size = math.radians(38)
        ld.spot_blend = 0.6
        ld.use_shadow = False
        lo = bpy.data.objects.new(f"read{r}{k}", ld)
        Q.link(lo)
        lo.location = (x * 0.95, r * FW.ROW + 0.15, 1.58)
        Q.cyl(f"readm{r}{k}", (x * 0.95, r * FW.ROW + 0.15, 1.59), 0.02, 0.01, FW.M["read"], seg=10)
        out.append(lo)
    return out


# ------------------------------------------------------------------------------------------ Grundaufbau Kabine
def cabin_base(people_rows=range(-3, 12), skip=(), kinds=None, outside="night", t_drop=None, occupancy=0.75, seed=3):
    FW.mats()
    C = FW.cabin_shell(seed=seed)
    # mein Fenster (0A) offen, Nachbarfenster gemischt
    for o in list(bpy.data.objects):
        if o.name.startswith("shade-1_"):
            k = int(o.name.split("_")[1])
            y = FW.window_ys()[k]
            if abs(y - 0.16) < 0.3 or abs(y - 0.97) < 0.3:
                bpy.data.objects.remove(o)
    seats = FW.seats()
    skip = set(skip) | {(0, "A"), (0, "B"), (0, "C")}
    pax = FW.cabin_people(people_rows, occupancy=occupancy, seed=seed, skip=skip, kinds=kinds)
    for P in pax.values():
        FP.lap_pose(P, spread=0.05 if P["kind"] == "child" else 0.09)
    world = Q.empty("outside", (0, 0, 0))
    world["person"] = 1
    W = FW.wing(-1)
    return C, seats, pax, world, W


def me_cam(lens=19.0):
    rig, shake, cam = Q.pov_camera(lens=lens)
    return rig, shake, cam


def my_hands(cam):
    H = MK.pov_arms(cam, skin=(0.52, 0.36, 0.25), sleeve=(0.1, 0.11, 0.14))
    MK.pose_hands(H, 0, "hidden")
    return H


HP = {   # eigene Hände (Kamera-Raum: x rechts, y oben, -z vorn), Drehung in Grad
    "hidden": {"L": ((-0.2, -0.9, -0.3), (-80, 0, -10)), "R": ((0.2, -0.9, -0.3), (-80, 0, 10))},
    "phone": {"R": ((0.04, -0.1, -0.32), (12, 4, 18)), "L": ((-0.2, -0.9, -0.3), (-80, 0, -10))},
    "armrest": {"L": ((-0.24, -0.5, -0.42), (-85, 0, -8)), "R": ((0.24, -0.5, -0.42), (-85, 0, 8))},
    "grip": {"L": ((-0.26, -0.44, -0.46), (-70, 0, -30)), "R": ((0.26, -0.44, -0.46), (-70, 0, 30))},
    "dua": {"L": ((-0.075, -0.17, -0.33), (58, 180, -14)), "R": ((0.075, -0.17, -0.33), (58, 180, 14))},
    "dua_low": {"L": ((-0.08, -0.26, -0.3), (45, 180, -14)), "R": ((0.08, -0.26, -0.3), (45, 180, 14))},
    "cover": {"L": ((-0.12, -0.05, -0.2), (60, 0, -30)), "R": ((0.12, -0.05, -0.2), (60, 0, 30))},
    "takbir": {"L": ((-0.105, 0.0, -0.36), (5, 0, 12)), "R": ((0.105, 0.0, -0.36), (5, 0, -12))},
    "reach": {"L": ((-0.1, -0.35, -0.42), (-80, 0, -10)), "R": ((0.1, -0.35, -0.42), (-80, 0, 10))},
    "mask_reach": {"L": ((-0.09, -0.24, -0.3), (-70, 0, -20)), "R": ((0.03, -0.2, -0.28), (-70, 0, 10))},
    "mask_face": {"L": ((-0.07, -0.16, -0.12), (-35, 0, -40)), "R": ((0.03, -0.13, -0.1), (-35, 0, 30))},
}


if os.environ.get("TAKBIR"):
    _v = [float(x) for x in os.environ["TAKBIR"].split(",")]
    HP["takbir"] = {"L": ((-_v[0], _v[1], _v[2]), (_v[3], 0, _v[4])), "R": ((_v[0], _v[1], _v[2]), (_v[3], 0, -_v[4]))}


def hp(H, t, name, only=None):
    for side, (loc, rot) in HP[name].items():
        if only and side != only:
            continue
        w = H[side]
        w.location = loc
        w.rotation_euler = [math.radians(a) for a in rot]
        w.keyframe_insert("location", frame=max(1, Q.T(t)))
        w.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))


def neighbor(seed=21):
    """Sitznachbar (0B): junger Mann im grauen Hoodie, kurze Haare, Handy in den Händen."""
    P = Q.person("nb", (FW.SX["C"], -0.02, 0.5), yaw=math.pi, robe=(0.34, 0.35, 0.38), skin=(0.6, 0.44, 0.32),
                 wrap=(0.04, 0.03, 0.025), head="bare", sit=True, seed=seed, height=0.9)
    FW.seat_knees("nb")
    P["face"] = FW.face(P, seed=seed, brows=(0.03, 0.02, 0.015))
    FW.blink(P["face"], 0, D, seed=seed)
    R_ = Matrix(((-1, 0, 0), (0, -0.866, 0.5), (0, 0.5, 0.866))).transposed()   # Spalten: Breite, Oberkante (vor+hoch), Bildschirm (zum Gesicht)
    ph, pm, ps = FW.phone("nbp", P["chest"], "flug_feed_nb.png", loc=(0, -0.3, 0.33), rot=tuple(R_.to_euler("XYZ")))
    P["phone"], P["phone_mat"], P["phone_scr"] = ph, pm, ps
    P["row"], P["seat"] = 0, "C"
    nb_phone(P, 0)
    return P


def nb_phone(NB, t, chest=(-2, 0, 0), neck=(28, 0, 0)):
    """Handy mit beiden Händen vor dem Bauch (Hände gerechnet an die Handykanten)."""
    FP.set_body(NB, chest, neck)
    FP.key_body(NB, t)
    M = FP.chain(NB, "hips", "chest")
    edges = [M @ Vector((x, -0.3, 0.33)) for x in (0.045, -0.045)]
    for side in ("L", "R"):
        sw = FP.shoulder_world(NB, side)
        e = min(edges, key=lambda v: (v - sw).length)
        sx = FP.outward(NB, side)
        FP.set_arm(NB, side, t, e + Vector((0.012 * sx, 0, -0.01)), pole=(0.25 * sx, 0.7, -1.0), hand_twist=80 * sx)


def nb_relief(NB, t):
    """Erleichtert: Hand aufs Herz, andere Hand im Schoß, Kopf leicht zurück."""
    FP.set_body(NB, (-2, 0, 0), (-6, 0, -8))
    FP.key_body(NB, t)
    heart = FP.chain(NB, "hips", "chest") @ Vector((0.05, -0.2, 0.3))
    a = "L" if FP.outward(NB, "L") > 0 else "R"
    b = "R" if a == "L" else "L"
    FP.set_arm(NB, b, t, heart, pole=(-0.3, 0.6, -1.0), hand_twist=-70)
    c = FP.chain(NB, "hips", "chest").translation
    FP.set_arm(NB, a, t, Vector((c.x + 0.09, NB["root"].location.y + 0.24, 0.73)), pole=(0.2, 0.7, -1.0))


NBP = {   # (Schulter L, Ellenbogen L, Schulter R, Ellenbogen R, Brust, Nacken) in Grad
    "phone": ((62, 7, 0), (-75, 0, 0), (62, -7, 0), (-75, 0, 0), (-2, 0, 0), (28, 0, 0)),
    "laugh": ((66, 7, 0), (-80, 0, 0), (66, -7, 0), (-80, 0, 0), (8, 0, 0), (34, 0, 0)),
    "turn": ((40, 18, 0), (-60, 0, 0), (62, -18, 0), (-75, 0, 0), (-4, 0, -14), (6, 0, -38)),
    "wave": ((40, 18, 0), (-60, 0, 0), (80, -30, -30), (-40, 0, 0), (-6, 0, -10), (2, 0, -30)),
    "scream": ((150, 30, 0), (-60, 0, 0), (150, -30, 0), (-60, 0, 0), (-18, 0, 0), (-30, 0, 0)),
    "brace": ((150, 30, 0), (-110, 0, 0), (150, -30, 0), (-110, 0, 0), (48, 0, 0), (30, 0, 0)),
    "relief": ((30, 18, 0), (-90, 0, 0), (110, -40, 0), (-120, 0, 0), (-12, 0, 0), (-12, 0, -20)),
    "post": ((70, 7, 0), (-95, 0, 0), (70, -7, 0), (-95, 0, 0), (2, 0, 0), (34, 0, 0)),
    "rest": ((28, 14, 0), (-50, 0, 0), (28, -14, 0), (-50, 0, 0), (-6, 0, 0), (4, 0, 0)),
    "pray": ((72, 12, 0), (-125, 0, 0), (72, -12, 0), (-125, 0, 0), (56, 0, 0), (40, 0, 0)),   # tief vorgebeugt, Hände vor dem Gesicht
}


def nb_pose(P, t, name):
    shL, elL, shR, elR, ch, nk = NBP[name]
    FW.kf_rot(P["sh.L"], t, shL)
    FW.kf_rot(P["el.L"], t, elL)
    FW.kf_rot(P["sh.R"], t, shR)
    FW.kf_rot(P["el.R"], t, elR)
    FW.kf_rot(P["chest"], t, ch)
    FW.kf_rot(P["neck"], t, nk)


def nb_chill(NB, t0, t1):
    """„Chill. Das passiert ständig.“ – dreht sich halb zu mir, grinst, Handy bleibt in den Händen."""
    nb_phone(NB, t0, chest=(-3, 0, -10), neck=(6, 0, -30))
    laugh(NB, t0 + 0.2, t0 + 1.6, 3)
    nb_phone(NB, t1, chest=(-3, 0, -10), neck=(8, 0, -24))


def laugh(P, t0, t1, amp=5.0):
    """Lachen: Schultern/Brust hüpfen schnell."""
    t = t0
    k = 0
    base = math.degrees(P["chest"].rotation_euler.x)
    while t < t1:
        P["chest"].rotation_euler.x = math.radians(base + (amp if k % 2 else 0))
        P["chest"].keyframe_insert("rotation_euler", index=0, frame=max(1, Q.T(t)))
        if P.get("face"):
            FW.mouth(P["face"], t, 0.55 if k % 2 else 0.35)
        t += 0.13
        k += 1
    if P.get("face"):
        FW.mouth(P["face"], t1 + 0.15, 0.08)


def my_tray(cup=True):
    """Ausgeklapptes Tablett vor mir (Lehne 1A) mit Becher und Dose."""
    FW.mats()
    tr = Q.box("mytray", (FW.SX["A"], 0.42, 0.74), (0.38, 0.27, 0.018), FW.M["seatback"], bevel=0.005)
    objs = {}
    if cup:
        objs["cup"] = Q.cyl("mycup", (FW.SX["A"] + 0.06, 0.4, 0.795), 0.035, 0.1, FW.M["cup"], seg=20, r2=0.028)
        objs["can"] = Q.cyl("mycan", (FW.SX["A"] - 0.08, 0.46, 0.81), 0.033, 0.12, FW.M["can"], seg=20)
        for o in objs.values():
            o["person"] = 1
    return tr, objs


def fly_up(o, t, v=(0, 0.3, 2.2), spin=(380, 120, 60), dur=1.4, g=-2.0):
    """Gegenstand hebt beim Absacken ab (fliegt nach oben, dreht sich, fällt ab dur zurück)."""
    p0 = Vector(o.location)
    r0 = Vector(o.rotation_euler)
    o.keyframe_insert("location", frame=max(1, Q.T(t)))
    o.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))
    for k in range(1, 15):
        u = k / 14 * dur
        p = p0 + Vector(v) * u + Vector((0, 0, 0.5 * g * u * u))
        p.z = max(p.z, 0.05)
        o.location = p
        o.rotation_euler = r0 + Vector([math.radians(s * u) for s in spin])
        o.keyframe_insert("location", frame=max(1, Q.T(t + u)))
        o.keyframe_insert("rotation_euler", frame=max(1, Q.T(t + u)))


def stewardess(y, seed=31):
    """Flugbegleiterin im Gang (dunkelblaue Uniform, Haar zum Knoten), hält sich an den Lehnen fest."""
    P = Q.person("stw", (0.0, y, 0.0), yaw=0.0, robe=(0.06, 0.09, 0.2), skin=(0.62, 0.46, 0.35), wrap=(0.06, 0.04, 0.03),
                 head="bare", seed=seed, height=0.98)
    Q.ball("stw_bun", (0, 0.1, 0.17), 0.05, bpy.data.materials.get("wrap_stw"), parent=P["head"])
    P["face"] = FW.face(P, seed=seed, brows=(0.05, 0.035, 0.025))
    Q.box("stw_scarf", (0, -0.1, 0.4), (0.12, 0.03, 0.08), Q.pbr("scarfred", (0.6, 0.08, 0.1), 0.7), parent=P["chest"])
    for nm, s_ in (("L", -1), ("R", 1)):
        FW.kf_rot(P[f"sh.{nm}"], 0, (60, 55 * s_, 0))
        FW.kf_rot(P[f"el.{nm}"], 0, (-30, 0, 0))
    return P


def outside_night(world, W, cloud_z=-70.0, storm=False, t_end=20.0, speed=40.0, seed=0):
    bg = FW.night_world()
    FW.cloud_sea(world, z=cloud_z, seed=seed)
    st = None
    if storm:
        st = FW.storm_clouds(world, seed=seed + 1)
    world.keyframe_insert("location", frame=1)
    world.location = (0, -speed * (t_end + 1), 0)
    world.keyframe_insert("location", frame=Q.T(t_end + 1))
    Q.set_interp(world, "LINEAR")
    FW.strobe(W, 0, t_end)
    return bg, st


# ------------------------------------------------------------------------------------------ Einstellungen
def shot_kabine():
    """Nachtflug: Blick aus dem Fenster (Flügel, Wolken im Mondlicht, Blitzlicht am Flügel), dann zum Nachbarn, der über ein Video
    lacht, dann über die Schulter nach hinten: ein Kind schläft an seine Mutter gelehnt."""
    kinds = dict(FAMILY)
    C, seats, pax, world, W = cabin_base(kinds=kinds, occupancy=0.7)
    outside_night(world, W, t_end=D)
    NB = neighbor()
    # Mutter (-1C) mit schlafendem Kind (-1B), Kind lehnt an ihr, Decke
    ch = pax.get((-1, "B"))
    if ch:
        FW.kf_rot(ch["chest"], 0, (10, -24, 0))
        FW.kf_rot(ch["neck"], 0, (20, -34, 0))
        bl = Q.ball("blanket", (FW.SX["B"] + 0.06, -0.86, 0.68), (0.26, 0.24, 0.22), Q.pbr("blanket2", (0.55, 0.68, 0.85), 0.95, var=0.1, scale=12, bump=0.25, bscale=60))
        Q.ball("pillow", (FW.SX["B"] + 0.2, -0.9, 0.98), (0.11, 0.07, 0.08), FW.M["cover"])
        FW.breathe(ch, 0, D, seed=5, amp=2.0, sleep=True)
    mo = pax.get((-1, "C"))
    if mo:
        FW.kf_rot(mo["neck"], 0, (14, 0, 18))
        FW.breathe(mo, 0, D, seed=6, amp=1.0, sleep=True)
    k2 = pax.get(KID2)
    if k2:   # zweites Kind schläft ans Fenster gelehnt
        FW.kf_rot(k2["chest"], 0, (6, 12, 0))
        FW.kf_rot(k2["neck"], 0, (16, 0, 22))
        FW.breathe(k2, 0, D, seed=7, amp=1.5, sleep=True)
    for k, P in pax.items():
        if k not in (KID1, MOM, KID2):
            FW.breathe(P, 0, D, seed=hash(k) % 100)
            FW.blink(P["face"], 0, D, seed=hash(k) % 100)
    reading_lights([(3, "D"), (6, "B"), (9, "F"), (-2, "E"), (1, "F")])
    window_light([(0, 6.0)])
    rig, shake, cam = me_cam(19.0)
    tw = ev("video_k1", 4.3)
    tk = ev("hinten_k1", 5.5)
    ew = Vector((-1.58, 0.38, 1.12))   # ans Fenster gelehnt (v2: näher, Nutzer: „besser rausschauen“): Blick schräg nach hinten auf den Flügel
    e1 = SEATA + Vector((0.02, 0.16, 0.04))
    e2 = SEATA + Vector((0.24, -0.04, 0.24))
    ck(rig, [(0, tuple(ew), (134, -15, 0)), (tw - 1.5, tuple(ew + Vector((0, -0.04, 0))), (128, -13, 0)),
             (tw - 0.9, tuple(SEATA + Vector((0.02, 0.1, 0))), (40, -6, 0)), (tw - 0.35, tuple(e1), (-96, -18, 0)),
             (tk - 0.45, None, (-100, -20, 0)), (tk + 0.4, tuple(e2), (-138, -14, 0)), (D, None, (-143, -16, 0))])
    nb_phone(NB, tw - 0.9)
    nb_phone(NB, tw - 0.6, chest=(6, 0, 0), neck=(32, 0, 0))
    laugh(NB, tw - 0.5, tw + 1.6)
    nb_phone(NB, tw + 1.7)
    Q.handheld(shake, 0, D, amp=0.25)
    return {"mist_col": (0.02, 0.025, 0.05), "mist_amt": 0.0, "exposure": 0.8}


def shot_handy():
    """Mein Handy: Video läuft, oben erscheint „Isha – Zeit für das Nachtgebet“, mein Daumen wischt es weg; ich scrolle weiter."""
    C, seats, pax, world, W = cabin_base(occupancy=0.6)
    outside_night(world, W, t_end=D)
    NB = neighbor()
    rig, shake, cam = me_cam(22.0)
    ck(rig, [(0, tuple(SEATA + Vector((0.04, 0.02, -0.04))), (-4, -50, 0)), (D, None, (-3, -52, 0))])
    # Handy fest in der rechten Hand (am Kamera-Raum befestigt), Bildschirm zu mir
    hold = Q.empty("myphone_hold", (0.02, -0.035, -0.27), cam, rot=(math.radians(8), 0, math.radians(-3)))
    ph, pm, ps = FW.phone("my", hold, "flug_feed_mine.png", emit=2.6, w=0.072, h=0.155)
    # zweites Video (nach dem Scrollen)
    pm2 = FW.img_mat("my_scr2", "flug_feed_nb.png", emit=2.6, base=(0.01, 0.01, 0.012), rough=0.15)
    s2 = FW.plane("my_screen2", 0.072, 0.155, pm2, loc=(0, -0.155, 0.0006), parent=ph)
    H = my_hands(cam)
    hp(H, 0, "phone")
    # Hinweis „Isha“ fährt oben ein (Ereignis „leuchtet“), Daumen wischt ihn nach rechts weg („wischst“)
    bm = FW.img_mat("banner", "flug_banner.png", emit=2.4, alpha=True)
    ban = FW.plane("banner", 0.066, 0.0194, bm, loc=(0, 0.11, 0.0012), parent=ph)
    t_in = ev("leuchtet_k2", 1.4) - 0.1
    t_sw = ev("wischst_k2", 3.6) + 0.1
    ban.location = (0, 0.11, 0.0012)
    ban.keyframe_insert("location", frame=1)
    ban.hide_render = True
    ban.keyframe_insert("hide_render", frame=max(1, Q.T(t_in) - 1))
    ban.hide_render = False
    ban.keyframe_insert("hide_render", frame=max(1, Q.T(t_in)))
    ban.keyframe_insert("location", frame=max(1, Q.T(t_in)))
    ban.location = (0, 0.056, 0.0012)
    ban.keyframe_insert("location", frame=max(1, Q.T(t_in + 0.3)))
    ban.keyframe_insert("location", frame=max(1, Q.T(t_sw)))
    ban.location = (0.05, 0.058, 0.0012)
    ban.keyframe_insert("location", frame=max(1, Q.T(t_sw + 0.3)))
    # Maske: nur der Bildschirm-Bereich zeigt den Hinweis (außerhalb verdeckt der Rahmen/Hand)
    FW.emit_strength(bm, 0, 2.4)
    # Daumen (linke Hand, Zeigefinger) wischt + scrollt
    th = Q.empty("thumb", (0.06, 0.02, 0.012), ph)
    ms = bpy.data.materials.get("pov_skin_h")
    Q.limb("thumbm", (0, 0, 0), (0.07, -0.05, -0.0), 0.011, 0.013, ms, parent=th, seg=10)
    Q.ball("thumbtip", (0, 0, 0), (0.011, 0.014, 0.008), ms, parent=th, seg=10)
    seq = [(0, (0.075, -0.02, 0.012)), (t_sw - 0.35, (0.06, 0.02, 0.012)), (t_sw - 0.15, (-0.02, 0.058, 0.004)),
           (t_sw + 0.25, (0.07, 0.06, 0.006)), (t_sw + 0.6, (0.075, -0.02, 0.014))]
    t_scr = ev("landung_k3", t_sw + 1.6) + 0.2
    seq += [(t_scr - 0.3, (0.02, -0.05, 0.004)), (t_scr + 0.25, (0.02, 0.05, 0.004)), (t_scr + 0.6, (0.075, -0.02, 0.014))]
    for t, p in seq:
        th.location = p
        th.keyframe_insert("location", frame=max(1, Q.T(t)))
    # Scrollen: zweites Video ersetzt das erste (kurz hochgeschoben), Hinweis verschwindet nach dem Wischen
    s2.location = (0, 0, 0.0007)
    for o_, vis in ((ps, (True, False)), (s2, (False, True))):
        o_.hide_render = not vis[0]
        o_.keyframe_insert("hide_render", frame=max(1, Q.T(t_scr + 0.1) - 1))
        o_.hide_render = not vis[1]
        o_.keyframe_insert("hide_render", frame=max(1, Q.T(t_scr + 0.1)))
    ban.hide_render = False
    ban.keyframe_insert("hide_render", frame=max(1, Q.T(t_sw + 0.22) - 1))
    ban.hide_render = True
    ban.keyframe_insert("hide_render", frame=max(1, Q.T(t_sw + 0.22)))
    Q.handheld(shake, 0, D, amp=0.2)
    window_light([(0, 4.0)])
    return {"mist_col": (0.02, 0.025, 0.05), "mist_amt": 0.0, "exposure": 0.1}


def shot_gong():
    """Gong: das Anschnallzeichen leuchtet, der Kapitän meldet Turbulenzen, der Nachbar winkt ab („Chill“) – dann sackt das
    Flugzeug ab: Becher und Dose fliegen hoch, ein Gepäckfach springt auf, Schreie."""
    C, seats, pax, world, W = cabin_base(kinds=FAMILY, occupancy=0.78)
    bg, st = outside_night(world, W, t_end=D, storm=True)
    NB = neighbor()
    tray, objs = my_tray()
    belt = FW.img_mat("belt", "flug_belt.png", emit=0.001, base=(0.02, 0.02, 0.02))   # emit > 0: Bild -> Leuchtfarbe (sonst gleichmäßig weiß)
    for r in range(-2, 10):
        for s_ in (-1, 1):
            # schräg zum Passagier geneigt (Oberkante zur Leiste), sonst sieht man es von unten nur als weißen Strich
            bs_ = FW.plane(f"beltsign{r}{s_}", 0.14, 0.056, belt, loc=(1.2 * s_, r * FW.ROW + 0.42, 1.565), rot=(math.radians(130), 0, 0))
            bs_["person"] = 1   # nicht verschmelzen (join_static verliert die UVs -> Bild wäre eine graue Fläche)
    t_gong = 0.35
    FW.emit_strength(belt, 0.0, 0.0)
    FW.emit_strength(belt, t_gong, 2.0)
    tt = ls("t2")
    t_drop = D - TL.get("xfade", 0.4) - 1.45
    rig, shake, cam = me_cam(19.0)
    ck(rig, [(0, tuple(SEATA), (-12, 36, 0)), (t_gong + 1.4, None, (-10, 30, 0)), (t_gong + 2.6, None, (-14, -4, 0)),
             (tt - 0.6, None, (-18, -6, 0)), (tt, tuple(SEATA + Vector((-0.04, 0.1, 0))), (-92, -14, 0)), (t_drop - 0.1, None, (-88, -12, 0)),
             (t_drop + 0.25, None, (-30, 8, 0)), (D, None, (-12, -2, 0))])
    nb_phone(NB, tt - 0.35)
    nb_chill(NB, tt - 0.1, t_drop - 0.05)
    hold(NB, t_drop + 0.02)
    FP.set_body(NB, (4, 0, 0), (6, 0, -6))
    FP.key_body(NB, t_drop + 0.3)
    FP.hands_armrest(NB, t_drop + 0.3)
    for o in NB["phone"].children_recursive:   # Handy fällt ihm aus der Hand
        o.keyframe_insert("hide_render", frame=max(1, Q.T(t_drop + 0.15)))
        o.hide_render = True
        o.keyframe_insert("hide_render", frame=max(1, Q.T(t_drop + 0.2)))
    FW.mouth(NB["face"], t_drop + 0.1, 0.1)
    FW.mouth(NB["face"], t_drop + 0.35, 0.8)
    MMg = mask_map(FW.oxygen_masks(range(-3, 12), t_drop + 0.25, seed=0))
    for o in objs.values():
        fly_up(o, t_drop, v=(random.uniform(-0.2, 0.2), 0.15, 2.4), dur=1.5)
    # ein Gepäckfach gegenüber springt auf, Tasche fällt in den Gang
    hinge = C["bins"].get((1, 8))
    if hinge:
        FW.kf_rot(hinge, t_drop + 0.12, (0, 0, 0))
        FW.kf_rot(hinge, t_drop + 0.3, (0, -75, 0))
        FW.kf_rot(hinge, t_drop + 0.5, (0, -62, 0))
        bag = Q.box("fallbag", (1.25, hinge.location.y, 1.85), (0.36, 0.5, 0.24), FW.M["bag"], bevel=0.04)
        bag["person"] = 1
        bag.keyframe_insert("location", frame=max(1, Q.T(t_drop + 0.25)))
        for u, p in ((0.25, (0.95, hinge.location.y, 1.7)), (0.55, (0.55, hinge.location.y - 0.1, 0.5)), (0.75, (0.35, hinge.location.y - 0.15, 0.12))):
            bag.location = p
            bag.keyframe_insert("location", frame=max(1, Q.T(t_drop + 0.25 + u)))
        FW.kf_rot(bag, t_drop + 0.25, (0, 0, 0))
        FW.kf_rot(bag, t_drop + 1.0, (20, 70, 30))
    amp = lambda t: 0.08 + (0.25 if t > t_gong + 1.5 else 0) + (0.9 if t > t_drop else 0)
    shake_heads(pax.values(), 0, D, amp, seed=1, step=0.12, deg=4.0)
    rg = random.Random(17)
    for P in pax.values():   # beim Absacken: zusammenzucken, an die Armlehnen krallen (wie im echten Leben)
        t_ = t_drop + rg.uniform(0.08, 0.3)
        hold(P, t_ - 0.08)
        FP.set_body(P, (4 + rg.uniform(-2, 3), 0, 0), (rg.uniform(2, 10), rg.uniform(-10, 10), 0))
        FP.key_body(P, t_)
        FP.hands_armrest(P, t_)
    turbulence(shake, 0, D, amp, jolts=[(t_gong + 1.8, 0.4), (t_drop, 1.4)], lift=[(t_drop, 0.9, 0.12)])
    window_light([(0, 4.0)])
    FW.lightning(t_drop + 0.3, [(bpy.data.objects["winlight"], 700)], st[1] if st else FW.M["cove"], bg, seed=2)
    flicker_lights(C, t_drop + 0.05, D, seed=4, low=0.05, high=1.0)
    return {"mist_col": (0.02, 0.025, 0.05), "mist_amt": 0.0, "exposure": 0.2}


MOM, KID1, KID2 = (-1, "C"), (-1, "B"), (-1, "A")   # Familie direkt HINTER mir (wie in „kabine“): Mutter, Kind daneben, Kind am Fenster
FAMILY = {MOM: "hijab", KID1: "child", KID2: "child"}


def mask_map(masks):
    return {(m["row"], m["seat"]): m for m in masks}


def hold(P, t):
    """Aktuelle Haltung bei t festhalten (vor einer neuen Pose – sonst gilt die neue schon ab Bild 1)."""
    for n in ("chest", "neck", "sh.L", "sh.R", "el.L", "el.R", "hand.L", "hand.R"):
        P[n].keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))


def shake_heads(Ps, t0, t1, amp, seed=0, step=0.1, deg=2.0):
    """Kopf wackelt mit der Erschütterung – am Kopf-Gelenk (Nacken/Brust tragen die gerechnete Haltung)."""
    jiggle([P["head"] for P in Ps], t0, t1, amp, seed=seed, step=step, axis_deg=deg)


def kneel_stewardess(y, seed=31):
    """Flugbegleiterin kniet im Gang (wie bei schweren Turbulenzen üblich), schaut zu den Fluggästen, hält sich an den Sitzen."""
    P = Q.person("stw", (0.0, y, 0.175), yaw=0.0, robe=(0.06, 0.09, 0.2), skin=(0.62, 0.46, 0.35), wrap=(0.06, 0.04, 0.03),
                 head="bare", sit=True, seed=seed, height=0.98)
    FW.seat_knees("stw")
    for s_ in (-1, 1):   # Knie auf dem Boden, Gesäß auf den Fersen
        k = bpy.data.objects.get(f"stw_knee{s_}")
        if k:
            k.location = (0.12 * s_, -0.25, -0.33)
            k.scale = (0.75, 1.2, 1.0)
    Q.ball("stw_bun", (0, 0.1, 0.17), 0.05, bpy.data.materials.get("wrap_stw"), parent=P["head"])
    P["face"] = FW.face(P, seed=seed, brows=(0.05, 0.035, 0.025))
    Q.box("stw_scarf", (0, -0.1, 0.4), (0.12, 0.03, 0.08), Q.pbr("scarfred", (0.6, 0.08, 0.1), 0.7), parent=P["chest"])
    P["root"]["person"] = 1
    return P


def stw_hold(S, t, y_row):
    """Hände vorn an der Armlehne (Sitz C) und an der Sitzkante (Sitz D) der Reihe vor ihr; Ellenbogen nach hinten (im Gang)."""
    FP.set_arm(S, "L" if FP.outward(S, "L") < 0 else "R", t, Vector((-0.215, y_row + 0.17, 0.765)), pole=(0.25, 0.8, -1.0))
    FP.set_arm(S, "L" if FP.outward(S, "L") > 0 else "R", t, Vector((0.235, y_row + 0.19, 0.6)), pole=(-0.25, 0.8, -1.0))


def my_mask(cam, H, piv, t_grab=None, t_on=None, worn_from_start=False):
    """Meine Maske: greifen (rechte Hand), ans Gesicht ziehen, aufsetzen. Aufgesetzt sitzt der Becher knapp UNTER dem Bild
    (sonst gelber Fleck), man sieht den Schlauch von der Service-Leiste nach unten laufen."""
    psu = Vector((piv.location.x, piv.location.y, FP.PSU_Z))
    worn = FP.worn_mask("me", cam, (0, -0.088, -0.035), (math.radians(180), 0, 0), psu)
    for o in worn:
        o.hide_render = True
        if o.name.startswith("mskwtube"):   # eigener Schlauch läuft direkt vor der Linse -> unscharfer Balken: für die Kamera unsichtbar
            o.visible_camera = False
    if worn_from_start:
        for o in worn:
            o.hide_render = False
        for o in FP.mask_parts(piv):
            o.hide_render = True
        return worn, None
    held = FP.worn_mask("meheld", H["R"], (0.0, 0.08, -0.055), (math.radians(180), 0, 0), psu)
    for o in held:
        o.hide_render = True
        if o.name.startswith("mskwtube"):
            o.visible_camera = False
    FP._vis(FP.mask_parts(piv), t_grab, False)
    FP._vis(held, t_grab, True)
    FP._vis(held, t_on, False)
    FP._vis(worn, t_on, True)
    return worn, held


def pov_grab_keys(cam, H, piv, t_grab, t_on):
    """Hände zur hängenden Maske (Ort aus Kamera + Pendel zur Zeit t_grab) – erst NACH allen anderen Schlüsseln aufrufen."""
    sc = bpy.context.scene
    sc.frame_set(Q.T(t_grab))
    cw = FP.dangling_cup(piv, t_grab)
    loc = cam.matrix_world.inverted() @ cw
    H["R"].location = loc + Vector((0.0, -0.075, 0.06))
    H["R"].rotation_euler = [math.radians(a) for a in (-70, 0, 10)]
    for f in (Q.T(t_grab),):
        H["R"].keyframe_insert("location", frame=f)
        H["R"].keyframe_insert("rotation_euler", frame=f)
    H["L"].location = loc + Vector((-0.07, -0.1, 0.07))
    H["L"].rotation_euler = [math.radians(a) for a in (-70, 0, -20)]
    H["L"].keyframe_insert("location", frame=Q.T(t_grab))
    H["L"].keyframe_insert("rotation_euler", frame=Q.T(t_grab))
    sc.frame_set(1)


def kid_dir(pax):
    mo, k1 = pax.get(MOM), pax.get(KID1)
    return 1.0 if k1["root"].location.x > mo["root"].location.x else -1.0


def family(pax, t, MM=None, mode="hug", seed=0):
    """Mutter über ihr Kind gebeugt (Arme schützend davor, Hände an seinen Schultern); Kind lehnt sich an sie;
    das zweite Kind am Fenster in Schutzhaltung. Seitenneigung: Brust-Y negativ = zur Welt-+x."""
    mo, k1, k2 = pax.get(MOM), pax.get(KID1), pax.get(KID2)
    if not (mo and k1):
        return mo, k1, k2
    dx = kid_dir(pax)
    FP.set_body(k1, (6, 10 * dx, 0), (10, 0, 6 * dx))
    FP.key_body(k1, t)
    FP.hands_lap(k1, t, spread=0.04)
    if k2:
        FP.brace_real(k2, t, seed=seed + 1)
    FP.set_body(mo, (14, -16 * dx, 0), (24, 0, -14 * dx))
    FP.key_body(mo, t)
    kid_side = "L" if FP.outward(mo, "L") == dx else "R"
    other = "R" if kid_side == "L" else "L"
    shs = sorted((FP.chain(k1, "hips", "chest", f"sh.{sd}").translation for sd in ("L", "R")), key=lambda v: v.x * dx)
    near, far = shs[0], shs[1]
    # beide Hände halten das Kind an den Schultern (von vorn), Arme schützend vor ihm
    FP.set_arm(mo, kid_side, t, far + Vector((0.0, 0.09, 0.0)), pole=(0.5 * dx, -0.1, -1.0), hand_twist=60 * dx)
    FP.set_arm(mo, other, t, near + Vector((0.01 * dx, 0.1, -0.03)), pole=(-0.4 * dx, 0.2, -1.0), hand_twist=-60 * dx)
    return mo, k1, k2


def storm_cabin(t_end, seed=0, t_drop=-1.6):
    """Gemeinsam für absturz/beten: Masken unten, Sturm draußen, Blitze, flackerndes Licht, schwere Erschütterung."""
    C, seats, pax, world, W = cabin_base(kinds=FAMILY, occupancy=0.8, seed=3)
    bg, st = outside_night(world, W, t_end=t_end, storm=True, speed=70.0)
    MM = mask_map(FW.oxygen_masks(range(-3, 12), t_drop, seed=seed))
    NB = neighbor()
    for o in NB["phone"].children_recursive:   # Handy steckt weg
        o.hide_render = True
    reading_lights([(MOM[0], MOM[1]), (KID1[0], KID1[1])], energy=9.0)   # Leselampen der Familie hinter mir an
    wl = window_light([(0, 3.0)])
    return C, pax, world, W, bg, st, MM, NB, wl


def shot_absturz():
    """Absturzgefahr (wie im echten Notfall): alle ziehen die Sauerstoffmasken auf (die Mutter erst sich, dann dem Kind),
    die Flugbegleiterin kniet im Gang und ruft „Kopf runter!“, alle gehen in die Schutzhaltung (Stirn an die Lehne, Hände darüber);
    auch ich setze meine Maske auf. Die Nase kippt nach unten – Handy, Geld, Zettel schweben hoch. Die Mutter ruft „Ya Allah, rette uns!“."""
    C, pax, world, W, bg, st, MM, NB, wl = storm_cabin(D)
    S = kneel_stewardess(2.70)
    rig, shake, cam = me_cam(18.0)
    H = my_hands(cam)
    ta1, ta2, ta3 = ls("a1"), ls("a2"), ls("a3")
    t_fall = ev("fällt_a2", ta2 + 0.6)
    t_egal = ev("egal_a2", ta2 + 3.6)
    t_handy = ev("handy_a2", ta2 + 5.4)
    t_grab, t_on = 0.75, 1.45
    ck(rig, [(0, tuple(SEATA), (12, 2, 0)), (t_grab, None, (10, -4, 0)), (t_on, None, (2, -14, 0)),
             (t_on + 0.55, tuple(SEATA + Vector((0.02, 0.04, 0.03))), (-72, -14, 0)), (ta2 - 0.3, None, (-76, -18, 0)),
             (t_fall - 0.2, tuple(SEATA), (10, -26, 0)), (t_egal - 0.6, None, (6, -8, 8)),
             (t_handy - 0.4, None, (4, 2, -6)), (ta3 - 0.4, None, (-6, 2, 0)),
             (ta3 + 0.2, tuple(SEATA + Vector((0.12, -0.05, 0.24))), (-145, -20, 0)), (D, None, (-148, -18, 0))])
    my_mask(cam, H, MM[(0, "A")], t_grab, t_on)
    hp(H, 0, "hidden")
    hp(H, t_grab - 0.45, "mask_reach")
    hp(H, t_on, "mask_face")
    hp(H, t_on + 0.5, "hidden")
    # Flugbegleiterin: kniet, hält sich fest, ruft, zeigt mit der Hand nach unten
    hold(S, 0)
    stw_hold(S, 0, 2.43)
    FP.set_body(S, (14, 0, 0), (-4, 0, 0))
    FP.key_body(S, ta1)
    FP.set_body(S, (22, 0, 0), (-10, 0, 0))
    FP.key_body(S, ta1 + 0.3)
    push = "L" if FP.outward(S, "L") > 0 else "R"
    for k_, (tt_, zz) in enumerate(((ta1 + 0.35, 0.98), (ta1 + 0.75, 0.74), (ta1 + 1.15, 0.98), (ta1 + 1.6, 0.74))):
        FP.set_arm(S, push, tt_, Vector((0.1, 2.3, zz)), pole=(0.15, 0.8, -0.8), hand_twist=0)
    FP.set_arm(S, push, ta1 + 2.0, Vector((0.18, 2.52, 0.68)), pole=(0.1, 0.8, -0.8), hand_twist=0)
    stw_hold(S, ta1 + 2.4, 2.43)
    for tt_, o_ in ((ta1 - 0.1, 0.1), (ta1 + 0.1, 0.9), (ta1 + 0.55, 0.5), (ta1 + 0.9, 0.95), (ta1 + 1.9, 0.3), (ta1 + 2.4, 0.6), (D, 0.4)):
        FW.mouth(S["face"], tt_, o_)
    # Nase kippt nach unten: die Welt draußen dreht sich (Wolken stürzen nach oben)
    FW.kf_rot(world, t_fall - 0.3, (0, 0, 0))
    FW.kf_rot(world, t_fall + 1.4, (-24, 0, 8))
    FW.kf_rot(world, D, (-30, 0, 12))
    # schwebende Gegenstände (Handy, Geldscheine, Zettel) zwischen mir und der Lehne vor mir, mittig (Hochformat ist schmal)
    FW.mats()
    money = Q.pbr("money", (0.55, 0.62, 0.45), 0.8, var=0.2, scale=40)
    paper = Q.pbr("paper", (0.92, 0.92, 0.9), 0.8)
    floaters = []
    rnd = random.Random(8)
    for k in range(9):
        m_ = money if k < 6 else paper
        o = Q.box(f"float{k}", (FW.SX["A"] + 0.06 + rnd.uniform(-0.2, 0.2), rnd.uniform(0.26, 0.4), 0.62), (0.12, 0.055, 0.002) if k < 6 else (0.075, 0.105, 0.002), m_)
        o["person"] = 1
        floaters.append(o)
    ph, pm, ps = FW.phone("fl", None, "flug_feed_mine.png", loc=(FW.SX["A"] + 0.05, 0.3, 0.6), emit=2.0)
    ph["person"] = 1
    floaters.append(ph)
    for k, o in enumerate(floaters):
        p0 = Vector(o.location)
        o.keyframe_insert("location", frame=max(1, Q.T(t_fall)))
        FW.kf_rot(o, t_fall, (0, 0, 0))
        tgt = Vector((FW.SX["A"] + 0.06 + rnd.uniform(-0.15, 0.15), rnd.uniform(0.3, 0.4), rnd.uniform(0.82, 1.36)))
        if o is ph:
            tgt = Vector((FW.SX["A"] + 0.06, 0.34, 1.08))
        for u in (0.6, 1.2, 2.5, 4.0):
            o.location = p0.lerp(tgt, min(1, u / 2.0)) + Vector((rnd.uniform(-0.04, 0.04), rnd.uniform(-0.03, 0.03), 0.03 * math.sin(u * 3 + k)))
            o.keyframe_insert("location", frame=max(1, Q.T(t_fall + u)))
            if o is ph:
                FW.kf_rot(o, t_fall + u, (72 * min(1, u / 2.0) + 8 * math.sin(u * 2), 6 * math.cos(u * 1.7), 10 * math.sin(u * 1.3)))
            else:
                FW.kf_rot(o, t_fall + u, (rnd.uniform(-90, 90) * u, rnd.uniform(-60, 60) * u, rnd.uniform(-90, 90) * u))
    # Fluggäste: Maske auf, dann Schutzhaltung (gerechnet – Stirn 3 cm vor der Lehne)
    rnd = random.Random(21)
    fam = set(FAMILY)
    for k, P in pax.items():
        if k in fam:
            continue
        hold(P, 0)
        t_o = rnd.uniform(0.4, 2.3)
        if MM.get(k):
            FP.put_on(P, MM[k], t_o - 0.45, t_o)
        FP.brace_real(P, max(t_o + 0.5, ta1 + 0.9) + rnd.uniform(0, 0.7), seed=rnd.randint(0, 999))
        if rnd.random() < 0.4:
            FW.mouth(P["face"], rnd.uniform(0, 1.0), rnd.uniform(0.5, 0.9))
    hold(NB, 0)
    FP.put_on(NB, MM[(0, "C")], 0.55, 1.0)
    FP.brace_real(NB, 1.9, seed=3)
    # Familie: Mutter setzt erst ihre Maske auf, dann die des kleinen Kindes; das große Kind seine eigene
    mo, k1, k2 = pax.get(MOM), pax.get(KID1), pax.get(KID2)
    if mo and k1:
        dx = kid_dir(pax)
        for P in (mo, k1) + ((k2,) if k2 else ()):
            hold(P, 0)
        FP.put_on(mo, MM[MOM], 0.35, 0.8)
        kp = FP.person_mask(k1, MM[KID1])
        cup_k = FP.dangling_cup(MM[KID1], 1.25)
        FP.set_body(mo, (10, -12 * dx, 0), (8, 0, -6 * dx))
        FP.key_body(mo, 1.25)
        for side in ("L", "R"):
            sx = FP.outward(mo, side)
            FP.set_arm(mo, side, 1.25, cup_k + Vector((0.04 * sx, -0.03, -0.02)), pole=(0.8 * sx, 0.0, -1.0), hand_twist=60 * sx)
        fk = FP.head_world(k1, (0, -0.15, 0.08))
        for side in ("L", "R"):
            sx = FP.outward(mo, side)
            FP.set_arm(mo, side, 1.95, fk + Vector((0.04 * sx, -0.03, 0.0)), pole=(0.8 * sx, 0.0, -1.0), hand_twist=70 * sx)
        FP._vis(FP.mask_parts(MM[KID1]), 1.95, False)
        FP._vis(kp, 1.95, True)
        if k2:
            FP.put_on(k2, MM[KID2], 1.0, 1.6)
        family(pax, 2.7, seed=4)
        # „Ya Allah, rette uns!“: Kopf hoch, freie Hand erhoben
        family(pax, ta3 - 0.5, seed=4)
        FP.set_body(mo, (4, -8 * dx, 0), (-14, 0, 12))   # schaut auf (nach vorn zu mir, ich drehe mich um)
        FP.key_body(mo, ta3 + 0.05)
        free = "R" if FP.outward(mo, "L") == dx else "L"
        hm = FP.head_world(mo)
        sxf = FP.outward(mo, free)
        # offene Hand, Handfläche nach oben, auf Brusthöhe (Bittgebet) – nicht über den Kopf gestreckt
        FP.set_arm(mo, free, ta3 + 0.1, hm + Vector((0.09 * sxf, 0.17, -0.2)), pole=(0.6 * sxf, 0.4, -1.0), hand_twist=-110 * sxf)
        FP.set_arm(mo, free, D, hm + Vector((0.09 * sxf, 0.18, -0.17)), pole=(0.6 * sxf, 0.4, -1.0), hand_twist=-110 * sxf)
    shake_heads(list(pax.values()) + [NB], 0, D, lambda t: 1.0 if t < t_fall else 1.25, seed=2, step=0.1, deg=2.0)
    shake_heads([S], 0, D, lambda t: 1.0, seed=5, step=0.1, deg=4.0)
    amp = lambda t: 1.0 if t < t_fall else 1.25
    turbulence(shake, 0, D, amp, seed=3, jolts=[(0.2, 1.0), (t_fall, 1.6), (ta3, 1.0)], lift=[(t_fall, 1.6, 0.16)])
    flicker_lights(C, 0, D, seed=7, low=0.0, high=0.7)
    for k, (tl_, s_) in enumerate(((0.6, 0.9), (t_fall + 0.1, 0.12), (t_fall + 1.1, 0.1), (t_egal - 0.4, 0.2), (t_egal + 0.6, 0.12),
                                    (ta3 + 0.5, 0.15), (D - 1.5, 0.25))):
        FW.lightning(tl_, [(wl, 800)], st[1], bg, strength=s_, seed=k, base=0.3)
    pov_grab_keys(cam, H, MM[(0, "A")], t_grab, t_on)
    return {"mist_col": (0.02, 0.025, 0.05), "mist_amt": 0.0, "exposure": 0.25, "mblur": 0.35}


def shot_beten():
    """Alle beten – mit Masken, wie im echten Notfall: die Mutter gegenüber hält ihr Kind („Ya Rabbi … meine Kinder“), viele in
    Schutzhaltung, einige mit erhobenen Händen; dann meine eigenen Hände – Bittgebet: „Ya Allah … gib mir noch eine Chance.“"""
    C, pax, world, W, bg, st, MM, NB, wl = storm_cabin(D, seed=2, t_drop=-20.0)
    rig, shake, cam = me_cam(19.0)
    H = my_hands(cam)
    my_mask(cam, H, MM[(0, "A")], worn_from_start=True)
    ta4, ta5, ta6 = ls("a4"), ls("a5"), ls("a6")
    t_du = ev("du_a5", ta5 + 5.4)
    ck(rig, [(0, tuple(SEATA + Vector((0.12, -0.05, 0.24))), (-147, -20, 0)), (ta5 - 0.2, None, (-143, -19, 0)),
             (ta5 + 1.2, tuple(SEATA + Vector((0.12, 0.08, 0.18))), (-36, -9, 0)), (t_du - 0.5, tuple(SEATA + Vector((0.1, 0.08, 0.16))), (-26, -8, 0)),
             (t_du + 0.3, tuple(SEATA + Vector((0.02, 0.0, -0.08))), (-2, -20, 0)), (D, None, (0, -22, 0))])
    hp(H, 0, "hidden")
    hp(H, t_du - 0.1, "dua_low")
    hp(H, t_du + 0.5, "dua")
    hp(H, ta6 + 1.6, "dua")
    hp(H, ta6 + 2.2, "dua_low")
    hp(H, D, "dua")
    for k, P in pax.items():
        if MM.get(k):
            FP.wear_from_start(P, MM[k])
    FP.wear_from_start(NB, MM[(0, "C")])
    FP.brace_real(NB, 0, seed=5)
    mo, k1, k2 = family(pax, 0, seed=4)
    if mo:   # leises Schluchzen: Schultern zucken
        base = list(mo["chest"].rotation_euler)
        t = 0.2
        while t < D:
            mo["chest"].rotation_euler = (base[0] + math.radians(3.0 if int(t * 3) % 2 else 0.0), base[1], base[2])
            mo["chest"].keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))
            t += 0.33
    rnd = random.Random(4)
    for k, P in pax.items():
        if k in FAMILY:
            continue
        if rnd.random() < 0.4:   # aufrecht, Hände zum Bittgebet erhoben
            FP.upright(P, 0, lean=-2, neck=(rnd.uniform(-8, 4), 0, 0))
            FP.hands_dua(P, 0, seed=rnd.randint(0, 99), high=rnd.uniform(0.0, 0.08))
        else:
            FP.brace_real(P, 0, seed=rnd.randint(0, 999))
    amp = lambda t: 0.85 if t < ta6 else 0.7
    shake_heads(list(pax.values()) + [NB], 0, D, amp, seed=3, step=0.11, deg=2.0)
    turbulence(shake, 0, D, amp, seed=5, jolts=[(1.2, 0.8), (ta5 + 2.5, 1.0), (ta6 + 1.0, 0.7)])
    flicker_lights(C, 0, D, seed=11, low=0.0, high=0.55)
    for k, tl_ in enumerate((0.8, ta5 + 0.4, ta5 + 3.6, t_du + 0.3, ta6 + 2.6)):
        FW.lightning(tl_, [(wl, 700)], st[1], bg, seed=k + 3, strength=0.6 if tl_ < t_du else 0.25)
    FW.lightning(D - 1.02, [(wl, 700)], st[1], bg, seed=8, strength=0.3)
    return {"mist_col": (0.02, 0.025, 0.05), "mist_amt": 0.0, "exposure": 0.25, "mblur": 0.3}


def shot_stille():
    """Plötzlich Ruhe: das Rütteln hört auf, das Licht geht an; die Leute heben die Köpfe, einige nehmen die Maske ab (auch der Nachbar),
    die Mutter hält ihre Kinder. Durchsage des Kapitäns – der Bildschirm zeigt: noch 20 Minuten."""
    C, seats, pax, world, W = cabin_base(kinds=FAMILY, occupancy=0.8)
    FW.set_ife("flug_ife_s.png")   # „Wir landen in zwanzig Minuten“ -> Karte: NOCH 20 MIN
    bg, st = outside_night(world, W, t_end=D, speed=50.0)
    FW.city_lights(world, z=-900, center=(-400, 300))
    MM = mask_map(FW.oxygen_masks(range(-3, 12), -20.0, seed=2))
    NB = neighbor()
    for o in NB["phone"].children_recursive:
        o.hide_render = True
    rig, shake, cam = me_cam(19.0)
    H = my_hands(cam)
    my_mask(cam, H, MM[(0, "A")], worn_from_start=True)
    hp(H, 0, "hidden")
    ts = ls("s1")
    ck(rig, [(0, tuple(SEATA + Vector((0.04, 0.08, -0.1))), (-6, -26, 0)), (1.2, None, (-8, -14, 0)), (ts - 0.2, tuple(SEATA), (-12, 2, 0)),
             (ts + 2.6, None, (-24, 0, 0)), (D, None, (-34, -2, 0))])
    rnd = random.Random(3)
    for k, P in pax.items():
        if MM.get(k):
            FP.wear_from_start(P, MM[k])
        if k in FAMILY:
            continue
        FP.brace_real(P, 0, seed=rnd.randint(0, 999))
        tu = 0.6 + rnd.uniform(0, 2.8)
        FP.brace_real(P, tu - 0.4, seed=rnd.randint(0, 999))
        FP.upright(P, tu, lean=-1, neck=(rnd.uniform(-2, 8), rnd.uniform(-10, 10), 0))
        FP.hands_lap(P, tu)
        if MM.get(k) and rnd.random() < 0.45:
            to = tu + 0.8 + rnd.uniform(0, 3.0)
            hold(P, to - 0.4)
            FP.take_off(P, MM[k], to, to + 0.4)
            FP.hands_lap(P, to + 0.7)
    FP.wear_from_start(NB, MM[(0, "C")])
    FP.brace_real(NB, 0, seed=5)
    FP.brace_real(NB, 1.4, seed=5)
    FP.upright(NB, 2.0, lean=-2, neck=(-2, 0, 0))
    FP.hands_lap(NB, 2.0)
    hold(NB, 2.9)
    FP.take_off(NB, MM[(0, "C")], 3.3, 3.7)
    FP.hands_lap(NB, 4.0)
    family(pax, 0, seed=4)
    family(pax, 2.0, seed=4)
    turbulence(shake, 0, D, lambda t: max(0.04, 0.7 * math.exp(-t / 0.5)), seed=8)
    flicker_lights(C, 0, 0.9, seed=2, low=0.0, high=0.6)
    lights_level(C, 1.2, 1.0)
    main_lights([(0, 0), (1.0, 0), (1.15, 260), (D, 260)])
    window_light([(0, 3.0)])
    return {"mist_col": (0.02, 0.025, 0.05), "mist_amt": 0.0, "exposure": 0.15}


def shot_landung():
    """Landung: draußen Anflugbefeuerung und Landebahn, Aufsetzen (Ruck), Applaus; der Nachbar lacht erleichtert und holt das Handy:
    „Das muss ich posten.“"""
    C, seats, pax, world, W = cabin_base(kinds=FAMILY, occupancy=0.8)
    FW.set_ife("flug_ife_l.png")
    bg = FW.night_world(moon=False)
    t_td = 1.4
    rw = FW.runway(world, y0=0.0, length=3200, z=0.0)
    FW.city_lights(world, n=5000, z=-2.0, center=(-700, 900), area=(1600, 2600))
    FW.airport_side(world)
    # Flugzeug sinkt: Welt kommt von unten/vorn (vor dem Aufsetzen), dann Rollen + Bremsen
    world.location = (0, 260, -35)
    world.keyframe_insert("location", frame=1)
    world.location = (0, -40, -1.9)
    world.keyframe_insert("location", frame=Q.T(t_td))
    world.location = (0, -260, -1.9)
    world.keyframe_insert("location", frame=Q.T(t_td + 3.4))
    world.location = (0, -330, -1.9)
    world.keyframe_insert("location", frame=Q.T(D))
    FW.kf_rot(world, 0, (2.5, 0, 0))
    FW.kf_rot(world, t_td, (0.5, 0, 0))
    FW.kf_rot(world, t_td + 0.6, (0, 0, 0))   # Bugrad setzt auf: sonst hebt die 0,5°-Neigung den Boden beim Ausrollen durch die Kabine
    FW.strobe(W, 0, D)
    NB = neighbor()
    rig, shake, cam = me_cam(19.0)
    tl1, tl2 = ls("l1"), ls("l2")
    ck(rig, [(0, tuple(SEATA + Vector((-0.2, 0.04, -0.02))), (56, -18, 0)), (t_td + 0.8, None, (64, -12, 0)), (tl1 - 0.6, None, (40, -8, 0)),
             (tl1 - 0.3, tuple(SEATA + Vector((-0.06, 0.06, 0))), (10, -10, 0)),
             (tl1 + 0.1, tuple(SEATA + Vector((-0.06, 0.12, 0))), (-96, -14, 0)), (tl2, None, (-100, -18, 0)), (D, None, (-104, -22, 0))])
    MMl = mask_map(FW.oxygen_masks(range(-3, 12), -30.0, seed=2))
    for key in ((0, "A"), (0, "B")):   # eigene Masken zur Seite geschoben (sonst gelber Fleck vor Fenster/Kamera)
        for o in FP.mask_parts(MMl[key]):
            o.hide_render = True
    t_rel = min(tl1 - 0.3, t_td + 0.6)
    FP.brace_real(NB, 0, seed=5)
    FP.brace_real(NB, min(t_td + 0.3, t_rel - 0.35), seed=5)
    for o in NB["phone"].children_recursive:   # Handy erst beim „posten“ in der Hand
        o.hide_render = True
        o.keyframe_insert("hide_render", frame=max(1, Q.T(tl2 - 0.35)))
        o.hide_render = False
        o.keyframe_insert("hide_render", frame=max(1, Q.T(tl2 - 0.3)))
    nb_relief(NB, t_rel)
    laugh(NB, tl1 + 0.6, tl1 + 1.8, 3)
    nb_relief(NB, tl2 - 0.1)
    nb_phone(NB, tl2 + 0.4, chest=(2, 0, 0), neck=(32, 0, 0))
    pm2 = FW.img_mat("nbpost", "flug_post.png", emit=2.2, base=(0.01, 0.01, 0.012), rough=0.15)
    NB["phone_scr"].data.materials[0] = pm2
    # Applaus: Fluggäste klatschen (Hände vor der Brust, schnell)
    rnd = random.Random(6)
    for P in pax.values():
        FP.brace_real(P, 0, seed=rnd.randint(0, 999), hands="lap")
        FP.brace_real(P, t_td + 0.3, seed=rnd.randint(0, 999), hands="lap")
        tu = t_td + 0.6 + rnd.uniform(0, 0.8)
        FP.upright(P, tu, lean=-5, neck=(rnd.uniform(-8, 4), rnd.uniform(-8, 8), 0))
        FP.hands_lap(P, tu)
        if rnd.random() < 0.55:
            FP.hands_clap(P, tu + 0.2, D, seed=rnd.randint(0, 99))
    amp = lambda t: 0.25 + (0.5 if t_td < t < t_td + 2.5 else 0)
    turbulence(shake, 0, D, amp, seed=9, jolts=[(t_td, 1.3), (t_td + 0.5, 0.5)])
    lights_level(C, 0, 0.6)
    main_lights([(0, 60), (D, 60)])
    wl = window_light([(0, 2.0), (t_td - 0.4, 40.0), (t_td + 1.0, 14.0), (D, 6.0)], color=(1.0, 0.92, 0.8))
    return {"mist_col": (0.01, 0.012, 0.02), "mist_amt": 0.0, "exposure": 0.2, "mblur": 0.3}


def gate_apron(world, G=-3.6):
    """Vorfeld bei Nacht (links vor dem Fenster): Flugzeug am Nachbar-Gate mit hellen Kabinenfenstern + Blinklicht,
    Pier-Gebäude mit Glasband, Lichtmasten, Gepäckschlepper mit Rundumleuchte, Führungslinien."""
    FW.mats()
    par = lambda o: (setattr(o, "parent", world), o)[1]
    apron = Q.pbr("apron_v", (0.16, 0.16, 0.17), 0.55, var=0.08, scale=0.04)
    par(Q.box("apron_v", (-70, 0, G - 0.1), (160, 260, 0.2), apron))
    yel = Q.glow_mat("leadline", (1.0, 0.72, 0.12), 0.5)
    par(Q.box("lead0", (-24, 0, G + 0.01), (0.22, 120, 0.01), yel))
    par(Q.box("lead1", (-46, 26, G + 0.01), (0.22, 30, 0.01), yel))
    par(Q.box("stop0", (-46, 11, G + 0.01), (4.0, 0.25, 0.01), yel))
    # Flugzeug am Nachbar-Gate (parallel, ~46 m links), rechte Seite zu uns
    body = Q.pbr("acbody_v", (0.8, 0.81, 0.84), 0.35)
    dark = Q.pbr("acdark_v", (0.12, 0.13, 0.15), 0.5)
    xa, za = -40.0, 0.5
    par(Q.cyl("nbac_f", (xa, -4, za), 2.0, 36, body, seg=32, rot=(math.radians(90), 0, 0)))
    par(Q.ball("nbac_n", (xa, 14, za), (2.0, 3.4, 2.0), body))
    par(Q.ball("nbac_t", (xa, -22, za + 0.5), (1.6, 6.0, 1.5), body))
    fin = Q.box("nbac_fin", (xa, -23.5, za + 5.0), (0.4, 5.0, 7.0), body, rot=(math.radians(-24), 0, 0))
    par(fin)
    par(Q.box("nbac_hs", (xa, -24.5, za + 1.0), (12, 2.6, 0.25), body))
    par(Q.box("nbac_w", (xa + 8.5, -2.5, za - 1.1), (17, 5.0, 0.45), body, rot=(0, math.radians(-5), math.radians(-12))))
    par(Q.cyl("nbac_eng", (xa + 7.0, 0.2, za - 2.6), 1.05, 3.6, dark, seg=24, rot=(math.radians(90), 0, 0)))
    par(Q.cyl("nbac_engr", (xa + 7.0, 2.0, za - 2.6), 1.08, 0.3, body, seg=24, rot=(math.radians(90), 0, 0)))
    par(Q.cyl("nbac_gear", (xa + 2.5, -1, G + 1.3), 0.12, 2.6, dark, seg=8))
    par(Q.cyl("nbac_gearn", (xa, 11, G + 1.3), 0.1, 2.6, dark, seg=8))
    for gx in (xa + 2.1, xa + 2.9):
        par(Q.cyl(f"nbac_tyre{gx}", (gx, -1, G + 0.55), 0.55, 0.35, dark, seg=16, rot=(0, math.radians(90), 0)))
    win = Q.glow_mat("acwin_v", (1.0, 0.88, 0.66), 5.0)
    for k in range(34):   # Kabinenfenster (rechte Seite) – drinnen ist Licht an
        par(Q.box(f"nbac_win{k}", (xa + 1.93, -17.5 + k * 0.92, za + 0.55), (0.06, 0.26, 0.34), win))
    par(Q.box("nbac_door", (xa + 1.95, 10.5, za + 0.2), (0.05, 0.9, 1.9), win))
    grn = Q.glow_mat("navgreen_v", (0.2, 1.0, 0.35), 30.0)
    par(Q.ball("nbac_navg", (xa + 17.0, -5.0, za - 0.2), (0.12, 0.12, 0.12), grn, seg=8))
    beacon = Q.glow_mat("beacon_v", (1.0, 0.08, 0.04), 0.0)
    par(Q.ball("nbac_bcn", (xa, -3, za + 2.05), (0.16, 0.16, 0.1), beacon, seg=8))
    t = 0.2
    while t < D + 0.5:   # rotes Blinklicht (Triebwerke laufen noch an)
        FW.emit_strength(beacon, t - 0.01, 0.0)
        FW.emit_strength(beacon, t, 60.0)
        FW.emit_strength(beacon, t + 0.12, 0.0)
        t += 1.1
    # Pier-Gebäude dahinter mit hellem Glasband
    wall = Q.pbr("pier_v", (0.1, 0.105, 0.12), 0.7)
    par(Q.box("pier", (-98, 0, G + 6.5), (12, 240, 13), wall))
    glass = Q.glow_mat("pierglass_v", (1.0, 0.86, 0.62), 3.2)
    par(Q.box("pierglass", (-91.9, 0, G + 8.0), (0.1, 236, 4.2), glass))
    par(Q.box("pierglass2", (-91.9, 0, G + 2.4), (0.1, 236, 1.6), Q.glow_mat("pierlow_v", (0.85, 0.9, 1.0), 1.6)))
    for k in range(80):
        par(Q.box(f"piermul{k}", (-91.8, -118 + k * 3.0, G + 6.5), (0.12, 0.25, 13), wall))
    # Fluggastbrücke am Nachbar-Flugzeug (vorn, Tür)
    jb = Q.pbr("jetbridge_v", (0.55, 0.56, 0.58), 0.45, metal=0.3)
    par(Q.box("jbridge", (-68, 10.5, za + 0.9), (40, 3.0, 2.8), jb))
    par(Q.box("jbwin", (-68, 9.0, za + 1.2), (38, 0.05, 0.5), Q.glow_mat("jbwin_v", (1.0, 0.9, 0.75), 2.0)))
    par(Q.cyl("jbleg", (-52, 10.5, (G + za) / 2), 0.25, za - G, dark, seg=8))
    # Lichtmasten (orange) – beleuchten Vorfeld und Flugzeug
    head = Q.glow_mat("masthead_v", (1.0, 0.72, 0.4), 40.0)
    for k, (mx, my) in enumerate(((-30, 30), (-66, -12), (-64, 34), (-30, -30))):
        par(Q.cyl(f"mast{k}", (mx, my, G + 12.5), 0.22, 25, dark, seg=8))
        par(Q.box(f"masth{k}", (mx, my, G + 25.2), (2.4, 1.2, 0.5), head))
        L_ = Q.point(f"mastl{k}", (mx, my, G + 24.5), 8000, (1.0, 0.7, 0.4), radius=1.0)
        L_.parent = world
    # Gepäckschlepper mit Wagen + Rundumleuchte
    tug = Q.pbr("tug_v", (0.85, 0.62, 0.1), 0.5)
    par(Q.box("tug", (-38, 4.0, G + 0.7), (1.6, 2.6, 1.2), tug))
    for k in range(3):
        par(Q.box(f"cart{k}", (-38, 0.6 - k * 3.0, G + 0.8), (1.5, 2.4, 1.0), Q.pbr("cart_v", (0.3, 0.32, 0.36), 0.6)))
    amb = Q.glow_mat("tugbcn_v", (1.0, 0.6, 0.1), 0.0)
    par(Q.ball("tugbcn", (-38, 4.4, G + 1.42), (0.12, 0.12, 0.1), amb, seg=8))
    t = 0.0
    while t < D + 0.5:
        FW.emit_strength(amb, t, 40.0)
        FW.emit_strength(amb, t + 0.35, 2.0)
        t += 0.7


def shot_vergessen():
    """Am Gate: helles Licht, alle stehen im Gang, holen Taschen, schauen aufs Handy – als wäre nichts gewesen."""
    C, seats, pax, world, W = cabin_base(occupancy=0.0)
    FW.set_ife("flug_ife_welcome.png")   # 20 Minuten nach der Landung am Gate (Nutzer: „zeigt immer noch 23:05“)
    FW.night_world(moon=False)
    gate_apron(world)
    MMv = mask_map(FW.oxygen_masks(range(-3, 12), -40.0, seed=2))
    for key in ((0, "A"), (0, "B")):   # eigene Masken zur Seite geschoben (sonst gelber Fleck vor der Kamera)
        for o in FP.mask_parts(MMv[key]):
            o.hide_render = True
    NB = neighbor()
    nb_phone(NB, 0, chest=(2, 0, 0), neck=(32, 0, 0))
    rnd = random.Random(12)
    people = []
    for k in range(9):   # Leute stehen im Gang, Handy in der Hand
        y = -2.0 + k * 1.0 + rnd.uniform(-0.2, 0.2)
        P = Q.person(f"st{k}", (rnd.uniform(-0.04, 0.04), y, 0), yaw=rnd.choice((0.0, 0.08, -0.08, math.pi)), robe=rnd.choice(FW.CLOTH),
                     skin=rnd.choice(Q.SKINS), wrap=rnd.choice(FW.HIJAB if k % 3 == 0 else FW.HAIR),
                     head="khimar" if k % 3 == 0 else "bare", seed=40 + k, height=rnd.uniform(0.92, 1.04))
        FW.kf_rot(P["neck"], 0, (30, 0, 0))
        ph, pm, ps = FW.phone(f"stp{k}", P["hand.R"], rnd.choice(("flug_feed_mine.png", "flug_feed_nb.png")), loc=(0, -0.04, -0.06),
                              rot=(math.radians(-60), 0, 0), emit=1.6)
        P["face"] = FW.face(P, seed=40 + k)
        FW.blink(P["face"], 0, D, seed=k)
        FW.breathe(P, 0, D, seed=k)
        # Gang ist schmal (Sitzkanten bei x = ±0,24): beide Hände VOR dem Körper (Handy + Hand am Gurt), Ellenbogen am Körper
        Mc = FP.chain(P, "hips", "chest")
        back = (Mc.to_3x3() @ Vector((0, 1, 0))).normalized()
        for side, loc in (("R", (-0.03, -0.24, 0.3)), ("L", (0.07, -0.17, 0.08))):
            FP.pose_arm(P, side, Mc @ Vector(loc), pole=tuple(back * 0.8 + Vector((0, 0, -1))))
        people.append(P)
    # zwei Fächer offen
    for key in ((1, 9), (-1, 10)):
        h = C["bins"].get(key)
        if h:
            FW.kf_rot(h, 0, (0, -70 * key[0], 0))
    # sitzende Gäste (einige) mit Handy
    pax = FW.cabin_people(range(1, 10), occupancy=0.35, seed=8, skip={(0, "A"), (0, "B")})
    for P in pax.values():
        FP.lap_pose(P)
        FW.kf_rot(P["neck"], 0, (32, 0, 0))
    rig, shake, cam = me_cam(20.0)
    tq = ls("q0")
    ck(rig, [(0, tuple(SEATA + Vector((0.02, 0.1, 0.02))), (-58, 2, 0)), (tq - 0.6, None, (-66, 0, 0)), (tq + 0.4, None, (20, -4, 0)),
             (D, tuple(SEATA + Vector((-0.1, 0.0, 0))), (72, -8, 0))])
    Q.handheld(shake, 0, D, amp=0.25)
    lights_level(C, 0, 0.4, color=(1.0, 0.95, 0.9))
    main_lights([(0, 340), (D, 340)])
    window_light([(0, 5.0)], color=(1.0, 0.85, 0.6))
    return {"mist_col": (0.02, 0.025, 0.05), "mist_amt": 0.0, "exposure": 0.0}


def shot_terminal():
    """Stunden später, Morgendämmerung: ich gehe allein durch die leere Halle (Glasfront, Sonnenaufgang, Flugzeuge draußen),
    vorbei an der Abflugtafel, auf das Schild „Gebetsraum“ zu."""
    FW.mats()
    FW.terminal(length=60.0)
    w, s = FW.dawn_light()
    # Gebetsraum-Tür + Schild rechts an der Wand am Ende
    door_y = 22.0
    FW.plane("prsign_t", 0.9, 0.29, FW.img_mat("prsign_t", "flug_gebetsraum.png", emit=0.6), loc=(8.82, door_y, 2.55),
             rot=(math.radians(90), 0, math.radians(-90)))
    Q.box("prdoor", (8.84, door_y, 1.1), (0.06, 1.2, 2.2), Q.pbr("doorwood", (0.42, 0.3, 0.2), 0.5, var=0.1, scale=6))
    Q.box("prdoorhandle", (8.79, door_y - 0.45, 1.05), (0.04, 0.12, 0.03), FW.M["metal"])
    rig, shake, cam = me_cam(18.0)
    path = [(0.6, -3.0), (0.8, 6.0), (1.6, 14.0), (4.6, 19.6), (7.2, door_y)]
    keys = []
    te1 = le("e1")
    r2 = REC["r2"]
    tr2 = lt(r2["start"])
    te2 = ls("e2")
    T_end = D
    times = [0.0, te1 + 0.4, tr2 + r2["dur"] * 0.8, te2 + 3.0, T_end]
    yaws = [(-8, 2), (24, -2), (6, 6), (-40, 0), (-88, 2)]
    for t, (x, y), (yw, pt) in zip(times, path, yaws):
        keys.append((t, (x, y, 1.62), (yw, pt, 0)))
    ck(rig, keys)
    Q.handheld(shake, 0, D, amp=0.4, walk_from=0.0, walk_to=D - 0.6, walk_amp=0.6, run_hz=0.9)
    return {"mist_col": (0.6, 0.45, 0.35), "mist_amt": 0.12, "exposure": 0.0, "sky_sep": True}


def shot_gebetsraum():
    """Gebetsraum: ich trete ein (Qibla-Schild), rolle einen Gebetsteppich aus, schaue zurück zur offenen Tür („Die Tür ist offen …“),
    stelle mich auf den Teppich und hebe die Hände zum Takbir („Jetzt.“)."""
    FW.mats()
    FW.prayer_room()
    # Halle vor der offenen Tür: Terminal-Boden, Lichtbänder, Wartesitze, große Fensterfront im Morgenrot
    hfl = Q.pbr("prh_floor", (0.4, 0.41, 0.45), 0.22, var=0.03, scale=2, spec=0.6)
    Q.box("prh_floor", (0, -4.4, -0.05), (12, 8.2, 0.1), hfl)
    Q.box("prh_ceil", (0, -4.4, 3.6), (12, 8.2, 0.1), Q.pbr("prh_ceil", (0.82, 0.81, 0.8), 0.8))
    for k in range(4):
        Q.box(f"prh_strip{k}", (0, -1.3 - k * 1.9, 3.54), (9.0, 0.1, 0.02), Q.glow_mat("prh_strip", (1.0, 0.95, 0.88), 6.0))
    Q.box("prh_wall", (0, -8.5, 1.8), (12, 0.1, 3.6), Q.pbr("prh_wall", (0.72, 0.7, 0.68), 0.7))
    Q.box("prh_win_lo", (0, -8.42, 0.9), (10.0, 0.02, 1.0), Q.glow_mat("prh_dawn_lo", (1.0, 0.66, 0.42), 2.4))
    Q.box("prh_win_hi", (0, -8.42, 2.25), (10.0, 0.02, 1.7), Q.glow_mat("prh_dawn_hi", (0.78, 0.66, 0.72), 1.8))
    frm = Q.pbr("prh_frame", (0.2, 0.21, 0.23), 0.4, metal=0.6)
    for k in range(9):
        Q.box(f"prh_mull{k}", (-4.8 + k * 1.2, -8.38, 1.75), (0.06, 0.05, 2.7), frm)
    Q.box("prh_trans", (0, -8.38, 1.2), (10.0, 0.05, 0.05), frm)
    seat = Q.pbr("prh_seat", (0.16, 0.18, 0.22), 0.5)
    for k in range(7):
        x = -3.3 + k * 1.1
        Q.box(f"prh_seat{k}", (x, -6.6, 0.45), (0.5, 0.48, 0.06), seat)
        Q.box(f"prh_back{k}", (x, -6.36, 0.72), (0.5, 0.05, 0.5), seat)
    Q.box("prh_bar", (0, -6.6, 0.25), (8.0, 0.08, 0.06), frm)
    Q.point("prh_light", (0, -3.0, 3.0), 500, (1.0, 0.86, 0.72), radius=1.0)
    Q.world_sky("dawn")
    rug = FW.prayer_rug("rug", (0, 2.4, 0.0))
    rig, shake, cam = me_cam(18.0)
    H = my_hands(cam)
    te3, tq, te4, te5 = ls("e3"), ls("qh"), ls("e4"), ls("e5")
    t_jetzt = ev("jetzt_e5", te5 + 1.6)
    t_unroll = tq + 0.4
    ck(rig, [(0, (0.15, -0.9, 1.62), (4, -4, 0)), (te3 + 1.6, (0.1, 1.0, 1.62), (0, -10, 0)), (tq - 0.2, (0.0, 1.9, 1.05), (0, -48, 0)),
             (t_unroll + 1.4, (0.0, 2.0, 0.98), (0, -52, 0)), (te4 - 0.4, (0.0, 2.2, 1.6), (6, -8, 0)), (te4 + 0.4, None, (170, -4, 0)),
             (te5 - 0.4, None, (180, -2, 0)), (te5 + 0.2, (0.0, 2.55, 1.62), (360, -6, 0)), (t_jetzt - 0.2, None, (360, -4, 0)), (D, None, (360, 2, 0))])
    hp(H, 0, "hidden")
    hp(H, tq - 0.4, "reach")
    hp(H, t_unroll + 1.2, "reach")
    hp(H, t_unroll + 1.6, "hidden")
    hp(H, t_jetzt - 0.5, "hidden")
    hp(H, t_jetzt, "takbir")
    # Teppich rollt sich aus (Fläche wächst nach vorn, Rolle wandert mit)
    rug["flat"].scale = (1, 0.02, 1)
    rug["flat"].keyframe_insert("scale", frame=max(1, Q.T(t_unroll)))
    rug["roll"].keyframe_insert("location", frame=max(1, Q.T(t_unroll)))
    rug["flat"].scale = (1, 1, 1)
    rug["flat"].keyframe_insert("scale", frame=max(1, Q.T(t_unroll + 1.1)))
    rug["roll"].location = (0, 1.1, 0.02)
    rug["roll"].keyframe_insert("location", frame=max(1, Q.T(t_unroll + 1.1)))
    rug["roll"].scale = (0.2, 1, 0.2)
    rug["roll"].keyframe_insert("scale", frame=max(1, Q.T(t_unroll + 1.1)))
    rug["roll"].scale = (1, 1, 1)
    rug["roll"].keyframe_insert("scale", frame=max(1, Q.T(t_unroll)))
    Q.handheld(shake, 0, D, amp=0.3, walk_from=0.0, walk_to=te3 + 1.6, walk_amp=0.5, run_hz=0.85)
    return {"mist_col": (0.6, 0.5, 0.4), "mist_amt": 0.0, "exposure": 0.0}


SHOTS = {"kabine": shot_kabine, "handy": shot_handy, "gong": shot_gong, "absturz": shot_absturz, "beten": shot_beten,
         "stille": shot_stille, "landung": shot_landung, "vergessen": shot_vergessen, "terminal": shot_terminal,
         "gebetsraum": shot_gebetsraum}

Q.reset()
cfg = SHOTS[SHOT]()
bpy.context.view_layer.update()
if os.environ.get("JOIN", "1") == "1":
    MD.join_static(keep=("pov", "outside", "msk", "winlight", "main", "cove_l", "read", "nb", "stw", "float", "fl_", "my", "banner",
                         "thumb", "rug", "fallbag", "storm", "cloud", "city", "rw", "ground", "runway", "gatewall", "strobe", "nav", "stw",
                         "stp", "phmask"))
Q.render_setup(pct=PCT, samples=SAMPLES, mist_col=cfg["mist_col"], mist_amt=cfg["mist_amt"], shadow_res=0.5,
               sky_sep=cfg.get("sky_sep", False), exposure=cfg.get("exposure", 0.0))
sc = bpy.context.scene
for o in bpy.data.objects:
    if o.type == "CAMERA":
        o.data.clip_end = 6000
        o.data.clip_start = 0.02
if cfg.get("mblur") and os.environ.get("MBLUR", "1") == "1":
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = cfg["mblur"]
    try:
        sc.eevee.motion_blur_steps = int(os.environ.get("MBSTEPS", "1"))
    except AttributeError:
        pass
if os.environ.get("NOCOMP"):
    sc.render.use_compositing = False
sc.frame_start, sc.frame_end = 1, SEG[SHOT]["frames"]
if os.environ.get("FRAMES"):
    sc.frame_start, sc.frame_end = map(int, os.environ["FRAMES"].split("-"))
if os.environ.get("DBGPY"):
    exec(open(os.environ["DBGPY"]).read())
    sys.exit(0)
if os.environ.get("CAMDBG"):
    camo = sc.camera
    for t_ in map(float, os.environ["CAMDBG"].split(",")):
        sc.frame_set(Q.T(t_))
        fw = camo.matrix_world.to_3x3() @ Vector((0, 0, -1))
        print("CAMDBG", t_, tuple(round(v, 2) for v in camo.matrix_world.translation), "fwd", tuple(round(v, 2) for v in fw))
    sys.exit(0)
os.makedirs(OUT, exist_ok=True)
if os.environ.get("MID") == "1":
    ks = range(sc.frame_start, sc.frame_end)
    if os.environ.get("MIDLIST"):   # nur diese Zwischenbilder, z. B. "8-18,44-52" (schnelle Schwenks, sonst minterpolate)
        ks = [k for part in os.environ["MIDLIST"].split(",") for k in range(int(part.split("-")[0]), int(part.split("-")[-1]) + 1)]
    for k in ks:
        fp = os.path.join(OUT, f"{k:04d}.png")
        try:
            os.close(os.open(fp, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        except FileExistsError:
            continue
        sc.frame_set(k, subframe=0.5)
        sc.render.filepath = fp
        bpy.ops.render.render(write_still=True)
elif STILLS:
    for t in STILLS:
        sc.frame_set(Q.T(t))
        sc.render.filepath = os.path.join(OUT, f"{SHOT}_{t:05.2f}.png")
        bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath = os.path.join(OUT, "")
    sc.render.use_overwrite = False
    sc.render.use_placeholder = True
    bpy.ops.render.render(animation=True)
