# POV-Erinnerung „Was, wenn das dein letzter Flug ist?“ – alle Einstellungen in Blender. Aufruf:
#   blender -b --factory-startup --python blender/qissa/flug.py -- <einstellung> <ausgabe_ordner> [prozent] [samples] [standbild-zeiten]
# Längen und Ereignisse: src/flug/timeline.json (scripts/build_flug.py). Welt: blender/qissa/flug_world.py.
# Regeln: Menschen ohne Gesicht; ich bin die Kamera (Fensterplatz 0A, Sitznachbar 0B); keine KI-Koranrezitation (Ton: echte Aufnahme).
import bpy, sys, os, math, json, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import lib as Q
import mekka as MK
import medina as MD
import flug_world as FW

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
    "takbir": {"L": ((-0.125, -0.1, -0.26), (6, 0, 12)), "R": ((0.125, -0.1, -0.26), (6, 0, -12))},
    "reach": {"L": ((-0.1, -0.35, -0.42), (-80, 0, -10)), "R": ((0.1, -0.35, -0.42), (-80, 0, 10))},
}


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
    ph, pm, ps = FW.phone("nbp", P["hand.R"], "flug_feed_nb.png", loc=(-0.06, -0.05, -0.05), rot=(math.radians(-80), 0, math.radians(90)))
    P["phone"], P["phone_mat"], P["phone_scr"] = ph, pm, ps
    nb_pose(P, 0, "phone")
    return P


NBP = {   # (Schulter L, Ellenbogen L, Schulter R, Ellenbogen R, Brust, Nacken) in Grad
    "phone": ((62, 18, 0), (-75, 0, 0), (62, -18, 0), (-75, 0, 0), (-2, 0, 0), (28, 0, 0)),
    "laugh": ((66, 18, 0), (-80, 0, 0), (66, -18, 0), (-80, 0, 0), (8, 0, 0), (34, 0, 0)),
    "turn": ((40, 18, 0), (-60, 0, 0), (62, -18, 0), (-75, 0, 0), (-4, 0, -14), (6, 0, -38)),
    "wave": ((40, 18, 0), (-60, 0, 0), (80, -30, -30), (-40, 0, 0), (-6, 0, -10), (2, 0, -30)),
    "scream": ((150, 30, 0), (-60, 0, 0), (150, -30, 0), (-60, 0, 0), (-18, 0, 0), (-30, 0, 0)),
    "brace": ((150, 30, 0), (-110, 0, 0), (150, -30, 0), (-110, 0, 0), (48, 0, 0), (30, 0, 0)),
    "relief": ((30, 18, 0), (-90, 0, 0), (110, -40, 0), (-120, 0, 0), (-12, 0, 0), (-12, 0, -20)),
    "post": ((70, 18, 0), (-95, 0, 0), (70, -18, 0), (-95, 0, 0), (2, 0, 0), (34, 0, 0)),
    "rest": ((28, 14, 0), (-50, 0, 0), (28, -14, 0), (-50, 0, 0), (-6, 0, 0), (4, 0, 0)),
}


def nb_pose(P, t, name):
    shL, elL, shR, elR, ch, nk = NBP[name]
    FW.kf_rot(P["sh.L"], t, shL)
    FW.kf_rot(P["el.L"], t, elL)
    FW.kf_rot(P["sh.R"], t, shR)
    FW.kf_rot(P["el.R"], t, elR)
    FW.kf_rot(P["chest"], t, ch)
    FW.kf_rot(P["neck"], t, nk)


def laugh(P, t0, t1, amp=5.0):
    """Lachen: Schultern/Brust hüpfen schnell."""
    t = t0
    k = 0
    base = math.degrees(P["chest"].rotation_euler.x)
    while t < t1:
        P["chest"].rotation_euler.x = math.radians(base + (amp if k % 2 else 0))
        P["chest"].keyframe_insert("rotation_euler", index=0, frame=max(1, Q.T(t)))
        t += 0.13
        k += 1


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
    kinds = {(-1, "C"): "hijab", (-1, "B"): "child"}
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
    for k, P in pax.items():
        if k not in ((-1, "B"), (-1, "C")):
            FW.breathe(P, 0, D, seed=hash(k) % 100)
    reading_lights([(3, "D"), (6, "B"), (9, "F"), (-2, "E"), (1, "F")])
    window_light([(0, 6.0)])
    rig, shake, cam = me_cam(19.0)
    tw = ev("video_k1", 4.3)
    tk = ev("hinten_k1", 5.5)
    ew = Vector((-1.44, 0.4, 1.13))   # zum Fenster gelehnt: Blick schräg nach hinten auf den Flügel
    e1 = SEATA + Vector((0.02, 0.16, 0.04))
    e2 = SEATA + Vector((0.24, -0.04, 0.24))
    ck(rig, [(0, tuple(ew), (134, -15, 0)), (tw - 1.5, tuple(ew + Vector((0, -0.04, 0))), (128, -13, 0)),
             (tw - 0.9, tuple(SEATA + Vector((0.02, 0.1, 0))), (40, -6, 0)), (tw - 0.35, tuple(e1), (-96, -18, 0)),
             (tk - 0.45, None, (-100, -20, 0)), (tk + 0.4, tuple(e2), (-138, -14, 0)), (D, None, (-143, -16, 0))])
    nb_pose(NB, 0, "phone")
    nb_pose(NB, tw - 0.6, "laugh")
    laugh(NB, tw - 0.5, tw + 1.6)
    nb_pose(NB, tw + 1.7, "phone")
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
    nb_pose(NB, 0, "phone")
    Q.handheld(shake, 0, D, amp=0.2)
    window_light([(0, 4.0)])
    return {"mist_col": (0.02, 0.025, 0.05), "mist_amt": 0.0, "exposure": 0.1}


def shot_gong():
    """Gong: das Anschnallzeichen leuchtet, der Kapitän meldet Turbulenzen, der Nachbar winkt ab („Chill“) – dann sackt das
    Flugzeug ab: Becher und Dose fliegen hoch, ein Gepäckfach springt auf, Schreie."""
    C, seats, pax, world, W = cabin_base(occupancy=0.78)
    bg, st = outside_night(world, W, t_end=D, storm=True)
    NB = neighbor()
    tray, objs = my_tray()
    belt = FW.img_mat("belt", "flug_belt.png", emit=0.0, base=(0.02, 0.02, 0.02))
    for r in range(-2, 10):
        for s_ in (-1, 1):
            FW.plane(f"beltsign{r}{s_}", 0.1, 0.04, belt, loc=(1.06 * s_, r * FW.ROW + 0.4, 1.588), rot=(math.radians(180), 0, 0))
    t_gong = 0.35
    FW.emit_strength(belt, t_gong - 0.02, 0.0)
    FW.emit_strength(belt, t_gong, 1.1)
    tt = ls("t2")
    t_drop = D - TL.get("xfade", 0.4) - 1.45
    rig, shake, cam = me_cam(19.0)
    ck(rig, [(0, tuple(SEATA), (-4, 38, 0)), (t_gong + 1.4, None, (-6, 30, 0)), (t_gong + 2.6, None, (-14, -4, 0)),
             (tt - 0.6, None, (-18, -6, 0)), (tt, tuple(SEATA + Vector((-0.04, 0.1, 0))), (-92, -14, 0)), (t_drop - 0.1, None, (-88, -12, 0)),
             (t_drop + 0.25, None, (-30, 8, 0)), (D, None, (-12, -2, 0))])
    nb_pose(NB, 0, "phone")
    nb_pose(NB, tt - 0.2, "turn")
    nb_pose(NB, tt + 0.5, "wave")
    laugh(NB, tt + 0.2, tt + 1.6, 4)
    nb_pose(NB, t_drop - 0.05, "wave")
    nb_pose(NB, t_drop + 0.3, "scream")
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
    heads = [P["neck"] for P in pax.values()]
    amp = lambda t: 0.08 + (0.25 if t > t_gong + 1.5 else 0) + (0.9 if t > t_drop else 0)
    jiggle(heads, 0, D, amp, step=0.12)
    for P in pax.values():   # beim Absacken: Köpfe hoch, Arme hoch
        if random.random() < 0.5:
            FW.kf_rot(P["sh.L"], t_drop, (28, -14, 0))
            FW.kf_rot(P["sh.L"], t_drop + 0.25, (110, -30, 0))
    turbulence(shake, 0, D, amp, jolts=[(t_gong + 1.8, 0.4), (t_drop, 1.4)], lift=[(t_drop, 0.9, 0.12)])
    window_light([(0, 4.0)])
    FW.lightning(t_drop + 0.3, [(bpy.data.objects["winlight"], 700)], st[1] if st else FW.M["cove"], bg, seed=2)
    flicker_lights(C, t_drop + 0.05, D, seed=4, low=0.05, high=1.0)
    return {"mist_col": (0.02, 0.025, 0.05), "mist_amt": 0.0, "exposure": 0.2}


def storm_cabin(t_end, seed=0):
    """Gemeinsam für absturz/beten: Masken unten, Sturm draußen, Blitze, flackerndes Licht, schwere Erschütterung."""
    C, seats, pax, world, W = cabin_base(kinds={(0, "D"): "hijab", (0, "E"): "child"}, occupancy=0.8, seed=3)
    bg, st = outside_night(world, W, t_end=t_end, storm=True, speed=70.0)
    masks = FW.oxygen_masks(range(-1, 9), -1.0, seed=seed)
    NB = neighbor()
    wl = window_light([(0, 3.0)])
    return C, pax, world, W, bg, st, masks, NB, wl


def shot_absturz():
    """Absturzgefahr: Masken pendeln, Licht flackert, die Flugbegleiterin schreit „Kopf runter!“, draußen Blitze, die Nase kippt
    nach unten – Handy, Geldscheine, Zettel schweben hoch; der Nachbar schreit „Ya Allah!“."""
    C, pax, world, W, bg, st, masks, NB, wl = storm_cabin(D)
    S = stewardess(2.7)
    rig, shake, cam = me_cam(18.0)
    ta1, ta2, ta3 = ls("a1"), ls("a2"), ls("a3")
    t_fall = ev("fällt_a2", ta2 + 0.6)
    t_egal = ev("egal_a2", ta2 + 3.6)
    t_handy = ev("handy_a2", ta2 + 5.4)
    ck(rig, [(0, tuple(SEATA), (-22, -6, 0)), (ta1 + 1.0, None, (-18, -2, 0)), (ta2 - 0.1, None, (-14, -4, 0)),
             (t_fall - 0.2, None, (70, -18, 0)), (t_egal - 0.6, None, (96, -26, 8)), (t_handy - 0.4, None, (10, 4, -6)),
             (ta3 - 0.3, None, (-6, 2, 0)), (ta3 + 0.2, tuple(SEATA + Vector((-0.04, 0.1, 0))), (-90, -8, 0)), (D, None, (-96, -6, 0))])
    # Flugbegleiterin: hält sich fest, schreit (Kopf vor), Arm deutet nach unten
    FW.kf_rot(S["chest"], ta1, (-6, 0, 0))
    FW.kf_rot(S["chest"], ta1 + 0.3, (16, 0, 0))
    FW.kf_rot(S["sh.R"], ta1 + 0.3, (120, -10, 0))
    FW.kf_rot(S["sh.R"], ta1 + 0.8, (70, -10, 0))
    FW.kf_rot(S["sh.R"], ta1 + 1.2, (125, -10, 0))
    # Nase kippt nach unten: die Welt draußen dreht sich (Wolken stürzen nach oben)
    FW.kf_rot(world, t_fall - 0.3, (0, 0, 0))
    FW.kf_rot(world, t_fall + 1.4, (-24, 0, 8))
    FW.kf_rot(world, D, (-30, 0, 12))
    # schwebende Gegenstände (Handy, Geldscheine, Zettel)
    FW.mats()
    money = Q.pbr("money", (0.55, 0.62, 0.45), 0.8, var=0.2, scale=40)
    paper = Q.pbr("paper", (0.92, 0.92, 0.9), 0.8)
    floaters = []
    rnd = random.Random(8)
    for k in range(9):
        m_ = money if k < 5 else paper
        o = Q.box(f"float{k}", (FW.SX["A"] + rnd.uniform(-0.15, 0.4), rnd.uniform(0.35, 0.7), 0.62), (0.15, 0.07, 0.002) if k < 5 else (0.12, 0.17, 0.002), m_)
        o["person"] = 1
        floaters.append(o)
    ph, pm, ps = FW.phone("fl", None, "flug_feed_mine.png", loc=(FW.SX["A"] + 0.05, 0.3, 0.6), emit=2.0)
    ph["person"] = 1
    floaters.append(ph)
    for k, o in enumerate(floaters):
        p0 = Vector(o.location)
        o.keyframe_insert("location", frame=max(1, Q.T(t_fall)))
        FW.kf_rot(o, t_fall, (0, 0, 0))
        tgt = Vector((FW.SX["A"] + rnd.uniform(-0.2, 0.5), rnd.uniform(0.45, 0.85), rnd.uniform(0.95, 1.35)))
        if o is ph:
            tgt = Vector((FW.SX["A"] + 0.05, 0.42, 1.12))
        for u in (0.6, 1.2, 2.5, 4.0):
            o.location = p0.lerp(tgt, min(1, u / 2.0)) + Vector((rnd.uniform(-0.04, 0.04), rnd.uniform(-0.04, 0.04), 0.03 * math.sin(u * 3 + k)))
            o.keyframe_insert("location", frame=max(1, Q.T(t_fall + u)))
            FW.kf_rot(o, t_fall + u, (rnd.uniform(-90, 90) * u, rnd.uniform(-60, 60) * u, rnd.uniform(-90, 90) * u))
    # Nachbar: klammert sich fest, dann schreit er mit erhobenen Armen
    nb_pose(NB, 0, "brace")
    nb_pose(NB, ta3 - 0.4, "brace")
    nb_pose(NB, ta3, "scream")
    for P in pax.values():
        FW.brace(P, rnd.uniform(0.0, ta2), seed=rnd.randint(0, 99))
    heads = [P["neck"] for P in pax.values()] + [NB["neck"], S["neck"]]
    amp = lambda t: 1.0 if t < t_fall else 1.25
    jiggle(heads, 0, D, amp, step=0.1, axis_deg=6)
    turbulence(shake, 0, D, amp, seed=3, jolts=[(0.2, 1.0), (t_fall, 1.6), (ta3, 1.0)], lift=[(t_fall, 1.6, 0.16)])
    flicker_lights(C, 0, D, seed=7, low=0.0, high=0.7)
    rnd2 = random.Random(5)
    for k, tl_ in enumerate((0.6, t_fall + 0.1, t_egal - 0.4, ta3 + 0.5, D - 1.5)):
        FW.lightning(tl_, [(wl, 800)], st[1], bg, seed=k)
    return {"mist_col": (0.02, 0.025, 0.05), "mist_amt": 0.0, "exposure": 0.25, "mblur": 0.35}


def shot_beten():
    """Alle beten: die Frau gegenüber schützt ihr Kind („Ya Rabbi … meine Kinder“), Leute mit erhobenen Händen, Masken pendeln;
    dann meine eigenen Hände – Bittgebet: „Ya Allah … gib mir noch eine Chance.“"""
    C, pax, world, W, bg, st, masks, NB, wl = storm_cabin(D, seed=2)
    rig, shake, cam = me_cam(19.0)
    H = my_hands(cam)
    ta4, ta5, ta6 = ls("a4"), ls("a5"), ls("a6")
    t_du = ev("du_a5", ta5 + 5.4)
    ck(rig, [(0, tuple(SEATA + Vector((0.0, 0.05, -0.06))), (-84, -12, 0)), (ta5 - 0.2, None, (-80, -10, 0)),
             (ta5 + 1.2, tuple(SEATA + Vector((0.06, 0.06, -0.06))), (-16, -4, 0)), (t_du - 0.5, None, (-10, -8, 0)),
             (t_du + 0.3, tuple(SEATA + Vector((0.02, 0.04, -0.1))), (-2, -22, 0)), (D, None, (0, -24, 0))])
    hp(H, 0, "hidden")
    hp(H, t_du - 0.1, "dua_low")
    hp(H, t_du + 0.5, "dua")
    hp(H, ta6 + 1.6, "dua")
    hp(H, ta6 + 2.2, "dua_low")
    hp(H, D, "dua")
    # Frau gegenüber (0D) beugt sich über ihr Kind (0E)
    mo, ch = pax.get((0, "D")), pax.get((0, "E"))
    if mo:
        FW.kf_rot(mo["chest"], 0, (30, 0, -18))
        FW.kf_rot(mo["neck"], 0, (20, 0, -20))
        FW.kf_rot(mo["sh.L"], 0, (70, 40, 0))
        FW.kf_rot(mo["sh.R"], 0, (90, -10, 0))
        t = 0
        while t < D:   # Schluchzen
            FW.kf_rot(mo["chest"], t, (30 + (4 if int(t * 3) % 2 else 0), 0, -18))
            t += 0.33
    if ch:
        FW.kf_rot(ch["chest"], 0, (20, 0, 10))
    # andere: Köpfe unten, manche Hände erhoben (Bittgebet)
    rnd = random.Random(4)
    for k, P in pax.items():
        if k in ((0, "D"), (0, "E")):
            continue
        if rnd.random() < 0.45:
            FW.kf_rot(P["chest"], 0, (14, 0, 0))
            FW.kf_rot(P["neck"], 0, (26, 0, 0))
            for nm, s_ in (("L", -1), ("R", 1)):
                FW.kf_rot(P[f"sh.{nm}"], 0, (62, 18 * s_, 0))
                FW.kf_rot(P[f"el.{nm}"], 0, (-95, 0, 0))
        else:
            FW.brace(P, 0, seed=rnd.randint(0, 99))
    nb_pose(NB, 0, "brace")
    heads = [P["neck"] for P in pax.values()] + [NB["neck"]]
    amp = lambda t: 0.85 if t < ta6 else 0.7
    jiggle(heads, 0, D, amp, step=0.11, axis_deg=5)
    turbulence(shake, 0, D, amp, seed=5, jolts=[(1.2, 0.8), (ta5 + 2.5, 1.0), (ta6 + 1.0, 0.7)])
    flicker_lights(C, 0, D, seed=11, low=0.0, high=0.55)
    for k, tl_ in enumerate((0.8, ta5 + 0.4, ta5 + 3.6, t_du + 0.3, ta6 + 2.6, D - 1.0)):
        FW.lightning(tl_, [(wl, 700)], st[1], bg, seed=k + 3)
    return {"mist_col": (0.02, 0.025, 0.05), "mist_amt": 0.0, "exposure": 0.25, "mblur": 0.3}


def shot_stille():
    """Plötzlich Ruhe: das Rütteln hört auf, das Licht geht an, die Masken hängen still; Köpfe heben sich. Durchsage des Kapitäns."""
    C, seats, pax, world, W = cabin_base(kinds={(0, "D"): "hijab", (0, "E"): "child"}, occupancy=0.8)
    bg, st = outside_night(world, W, t_end=D, speed=50.0)
    FW.city_lights(world, z=-900, center=(-400, 300))
    masks = FW.oxygen_masks(range(-1, 9), -10.0, seed=2)
    NB = neighbor()
    rig, shake, cam = me_cam(19.0)
    ts = ls("s1")
    ck(rig, [(0, tuple(SEATA + Vector((0.04, 0.08, -0.1))), (-6, -26, 0)), (1.2, None, (-8, -14, 0)), (ts - 0.2, tuple(SEATA), (-12, 2, 0)),
             (ts + 2.6, None, (-24, 0, 0)), (D, None, (-34, -2, 0))])
    rnd = random.Random(3)
    for P in pax.values():
        FW.brace(P, 0, seed=rnd.randint(0, 99))
        FW.brace(P, 0.4 + rnd.uniform(0, 1.0), seed=rnd.randint(0, 99), down=True)
        FW.brace(P, 1.6 + rnd.uniform(0, 2.6), seed=rnd.randint(0, 99), down=False)
    nb_pose(NB, 0, "brace")
    nb_pose(NB, 2.0, "brace")
    nb_pose(NB, 3.2, "rest")
    amp = lambda t: max(0.04, 0.7 * math.exp(-t / 0.5))
    turbulence(shake, 0, D, amp, seed=8)
    for k, P in enumerate(pax.values()):
        FW.breathe(P, 4.0, D, seed=k)
    flicker_lights(C, 0, 0.9, seed=2, low=0.0, high=0.6)
    lights_level(C, 1.2, 1.0)
    main_lights([(0, 0), (1.0, 0), (1.15, 260), (D, 260)])
    window_light([(0, 3.0)])
    return {"mist_col": (0.02, 0.025, 0.05), "mist_amt": 0.0, "exposure": 0.15}


def shot_landung():
    """Landung: draußen Anflugbefeuerung und Landebahn, Aufsetzen (Ruck), Applaus; der Nachbar lacht erleichtert und holt das Handy:
    „Das muss ich posten.“"""
    C, seats, pax, world, W = cabin_base(occupancy=0.8)
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
    FW.strobe(W, 0, D)
    NB = neighbor()
    rig, shake, cam = me_cam(19.0)
    tl1, tl2 = ls("l1"), ls("l2")
    ck(rig, [(0, tuple(SEATA + Vector((-0.02, -0.06, 0))), (58, -20, 0)), (t_td + 0.8, None, (66, -14, 0)), (tl1 - 0.5, None, (30, -10, 0)),
             (tl1 + 0.1, tuple(SEATA + Vector((-0.06, 0.12, 0))), (-96, -14, 0)), (tl2, None, (-100, -18, 0)), (D, None, (-104, -22, 0))])
    nb_pose(NB, 0, "brace")
    nb_pose(NB, t_td + 0.6, "brace")
    nb_pose(NB, tl1 - 0.3, "relief")
    laugh(NB, tl1, tl1 + 1.6, 5)
    nb_pose(NB, tl2 - 0.1, "relief")
    nb_pose(NB, tl2 + 0.4, "post")
    pm2 = FW.img_mat("nbpost", "flug_post.png", emit=2.2, base=(0.01, 0.01, 0.012), rough=0.15)
    NB["phone_scr"].data.materials[0] = pm2
    # Applaus: Fluggäste klatschen (Hände vor der Brust, schnell)
    rnd = random.Random(6)
    for P in pax.values():
        if rnd.random() < 0.55:
            t = t_td + 0.8 + rnd.uniform(0, 0.6)
            while t < D:
                for nm, s_ in (("L", -1), ("R", 1)):
                    FW.kf_rot(P[f"sh.{nm}"], t, (75, (6 if int(t * 7) % 2 else 22) * s_, 0))
                    FW.kf_rot(P[f"el.{nm}"], t, (-80, 0, 0))
                t += 0.14
    amp = lambda t: 0.25 + (0.5 if t_td < t < t_td + 2.5 else 0)
    turbulence(shake, 0, D, amp, seed=9, jolts=[(t_td, 1.3), (t_td + 0.5, 0.5)])
    lights_level(C, 0, 0.6)
    main_lights([(0, 60), (D, 60)])
    wl = window_light([(0, 2.0), (t_td - 0.4, 40.0), (t_td + 1.0, 14.0), (D, 6.0)], color=(1.0, 0.92, 0.8))
    return {"mist_col": (0.01, 0.012, 0.02), "mist_amt": 0.0, "exposure": 0.2, "mblur": 0.3}


def shot_vergessen():
    """Am Gate: helles Licht, alle stehen im Gang, holen Taschen, schauen aufs Handy – als wäre nichts gewesen."""
    C, seats, pax, world, W = cabin_base(occupancy=0.0)
    FW.night_world(moon=False)
    # Terminal-Lichter draußen (Gate)
    gate = Q.glow_mat("gatelight", (1.0, 0.85, 0.6), 6.0)
    Q.box("gatewall", (-40, 0, 2), (2, 80, 8), gate).parent = world
    NB = neighbor()
    nb_pose(NB, 0, "post")
    rnd = random.Random(12)
    people = []
    for k in range(9):   # Leute stehen im Gang, Handy in der Hand
        y = -2.0 + k * 1.0 + rnd.uniform(-0.2, 0.2)
        P = Q.person(f"st{k}", (rnd.uniform(-0.08, 0.08), y, 0), yaw=rnd.choice((0.0, 0.3, -0.3, math.pi)), robe=rnd.choice(FW.CLOTH),
                     skin=rnd.choice(Q.SKINS), wrap=rnd.choice(FW.HIJAB if k % 3 == 0 else FW.HAIR),
                     head="khimar" if k % 3 == 0 else "bare", seed=40 + k, height=rnd.uniform(0.92, 1.04))
        FW.kf_rot(P["sh.R"], 0, (70, -10, 0))
        FW.kf_rot(P["el.R"], 0, (-70, 0, 0))
        FW.kf_rot(P["neck"], 0, (30, 0, 0))
        ph, pm, ps = FW.phone(f"stp{k}", P["hand.R"], rnd.choice(("flug_feed_mine.png", "flug_feed_nb.png")), loc=(0, -0.04, -0.06),
                              rot=(math.radians(-60), 0, 0), emit=1.6)
        FW.breathe(P, 0, D, seed=k)
        people.append(P)
    # zwei Fächer offen
    for key in ((1, 9), (-1, 10)):
        h = C["bins"].get(key)
        if h:
            FW.kf_rot(h, 0, (0, -70 * key[0], 0))
    # sitzende Gäste (einige) mit Handy
    pax = FW.cabin_people(range(1, 10), occupancy=0.35, seed=8, skip={(0, "A"), (0, "B")})
    for P in pax.values():
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
             rot=(math.radians(90), 0, math.radians(90)))
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
    # Licht von der offenen Tür (Halle draußen, Morgen)
    Q.box("prhall", (0, -3, 1.4), (6, 0.1, 3), Q.glow_mat("hallglow", (1.0, 0.86, 0.7), 1.6))
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
    for k in range(sc.frame_start, sc.frame_end):
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
