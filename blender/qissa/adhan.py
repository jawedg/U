# QISSA · „Der erste Adhan“ – alle Einstellungen in Blender (Ich-Sicht, Medina 622).
# Aufruf:  blender -b --factory-startup --python blender/qissa/adhan.py -- <einstellung> <ausgabe_ordner> [prozent] [samples] [standbild-zeiten]
#   z. B.  ... -- gasse /tmp/frames/gasse 50 8           (ganze Einstellung als PNG-Bilder 0001.png …)
#          ... -- gasse /tmp/stills 50 8 1.0,5.0          (nur Standbilder bei 1,0 s und 5,0 s)
# Längen und Ereignisse kommen aus src/qissa_adhan/timeline.json (scripts/build_qissa_adhan.py).
# Regeln: Menschen ohne Gesicht; Sahaba mit Licht über dem Kopf; der Prophet ﷺ NIE als Figur, nur als Licht-Säule.
import bpy, sys, os, math, json, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import lib as Q
import medina as MD

TL = json.load(open(os.path.join(ROOT, "src", "qissa_adhan", "timeline.json"), encoding="utf-8"))
SEG = {s["id"]: s for s in TL["segments"]}
LINE = {l["id"]: l for l in TL["lines"]}
QUOTE = {q["id"]: q for q in TL["quotes"]}
EV = TL["events"]

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SHOT = argv[0] if argv else "gasse"
OUT = argv[1] if len(argv) > 1 else "/tmp/qissa"
PCT = int(argv[2]) if len(argv) > 2 else 50
SAMPLES = int(argv[3]) if len(argv) > 3 else 8
STILLS = [float(x) for x in argv[4].split(",")] if len(argv) > 4 and argv[4] else None

S0 = SEG[SHOT]["start"]
D = SEG[SHOT]["dur"]


def lt(t_abs):
    """absolute Zeit (Video) -> Zeit in dieser Einstellung"""
    return t_abs - S0


def ls(i):
    return lt(LINE[i]["start"])


def le(i):
    return lt(LINE[i]["start"] + LINE[i]["dur"])


def qs(i):
    return lt(QUOTE[i]["start"])


def night():
    Q.world_sky("night", amb=((0.25, 0.32, 0.55), 0.35))
    Q.sun("moon", (55, 0, 155), 0.55, (0.6, 0.7, 1.0), shadow=True, angle=1.0)
    return dict(mist_col=(0.02, 0.025, 0.05), mist_amt=0.5)


def dawn(level=1.0):
    Q.world_sky("dawn", amb=((0.85, 0.66, 0.58), 0.6))
    Q.sun("sun", (83, 0, 95), 3.6 * level, (1.0, 0.58, 0.32), shadow=True, angle=2.0)
    return dict(mist_col=(0.75, 0.55, 0.45), mist_amt=0.3)


def crowd(spots, seed=0, glow=False, prefix="c"):
    """spots: [(x, y, blickziel(x,y) oder yaw-Radiant, sitzt), ...] -> Liste von Figuren (gewöhnliche Leute)."""
    rnd = random.Random(seed)
    out = []
    for i, sp in enumerate(spots):
        x, y, look, sit = sp
        yaw = look if isinstance(look, (int, float)) else Q.face_yaw((x, y), look)
        P = Q.person(f"{prefix}{i}", (x, y, 0), yaw=yaw, sit=sit, glow=glow, seed=rnd.randint(0, 9999),
                     head=rnd.choice(["turban", "turban", "scarf", "cap"]), height=rnd.uniform(0.95, 1.05))
        Q.idle(P, 0, D, seed=i + seed)
        out.append(P)
    return out


# ============================================================ Einstellungen
def shot_gasse():
    L = night()
    I = MD.town(night=True)
    rig, shake, cam = Q.pov_camera()
    H = Q.pov_hands(cam)
    Q.flicker(H["lamp"]["light"], 0, D, 9.0, seed=1)
    for k, nl in enumerate(I["niche_lamps"]):
        Q.flicker(nl["light"], 0, D, 35.0, seed=10 + k)
    y0, y1 = -37.5, -24.0
    tw = D - 1.0
    keys = []
    for k in range(0, 11):
        t = tw * k / 10
        keys.append((t, (0.3 - 0.15 * k / 10, y0 + (y1 - y0) * k / 10, 1.62), None))
    keys.append((D, (0.15, y1 + 0.2, 1.62), None))
    Q.cam_keys(rig, keys, loc_interp="LINEAR")
    Q.cam_keys(rig, [(0, None, (4, -3, 0)), (1.8, None, (16, -2, 0)), (4.2, None, (-14, -4, 0)), (6.6, None, (-2, 1, 0)),
                     (D, None, (2, 4, 0))])
    Q.handheld(shake, 0, D, amp=1.0, walk_from=0, walk_to=tw, walk_amp=1.0)
    # Leute: einer geht vorn zur Moschee, einer sitzt an einer Tür, einer steht im Eingang
    a = Q.person("vor", (-0.5, -31.0, 0), seed=21, head="turban")
    Q.walk(a, [(-0.5, -31.0), (-0.3, -22.0), (0.0, -15.0)], 0.0, speed=1.15)
    b = Q.person("sitz", (1.75, -32.6, 0), yaw=-math.pi / 2, sit=True, seed=22, head="scarf")
    Q.idle(b, 0, D, seed=3, look=[(0, -10, 0), (3.5, -40, 5), (6.5, -60, 5)])
    c = Q.person("tuer", (-1.9, -27.8, 0), yaw=math.pi / 2, seed=23, head="cap")
    Q.idle(c, 0, D, seed=4)
    return L


def shot_moschee():
    L = night()
    I = MD.town(night=True)
    rig, shake, cam = Q.pov_camera()
    H = Q.pov_hands(cam)
    Q.flicker(H["lamp"]["light"], 0, D, 9.0, seed=2)
    m1, m2 = (2.7, -10.9), (3.7, -12.1)
    pos_stop = (0.6, -14.2, 1.62)
    Q.cam_keys(rig, [(0, (0.35, -20.0, 1.62), None), (4.0, pos_stop, None), (D, (0.7, -13.8, 1.62), None)], loc_interp="BEZIER")
    a1 = Q.yaw_to(pos_stop, m1)
    Q.cam_keys(rig, [(0, None, (2, 0, 0)), (2.6, None, (-6, 2, 0)), (max(3.4, ls("m1") - 0.5), None, (a1 * 0.8, -3, 0)),
                     (le("m2") + 0.1, None, (a1 * 0.7, -3, 0)), (ls("d2") + 0.9, None, (8, 3, 0)), (D, None, (12, 4, 0))])
    Q.handheld(shake, 0, D, amp=0.9, walk_from=0, walk_to=4.0)
    P1 = Q.person("mann1", (*m1, 0), yaw=Q.face_yaw(m1, m2), seed=31, head="turban", cloak=(0.3, 0.24, 0.18))
    P2 = Q.person("mann2", (*m2, 0), yaw=Q.face_yaw(m2, m1), seed=32, head="scarf")
    cam_pt = (pos_stop[0], pos_stop[1], 1.62)
    Q.idle(P1, 0, D, seed=5, look=[(0, 0, 0)])
    Q.idle(P2, 0, D, seed=6, look=[(0, 0, 0)])
    Q.head_to(P1, 0.0, (*m2, 1.6))
    Q.head_to(P1, ls("m1") - 0.2, cam_pt)
    Q.head_to(P1, le("m1") + 0.3, cam_pt)
    Q.head_to(P1, ls("m2") + 0.3, (*m2, 1.6))
    Q.head_to(P2, 0.0, (*m1, 1.6))
    Q.head_to(P2, ls("m2") - 0.3, (*m1, 1.6))
    Q.head_to(P2, ls("m2") + 0.6, cam_pt)
    Q.head_to(P2, le("m2") + 0.6, (8, 13, 1.0))
    Q.arm_pose(P2, ls("m2"), "R", 0, -14)
    Q.arm_pose(P2, ls("m2") + 0.4, "R", -35, -60)
    Q.arm_pose(P2, le("m2") + 0.4, "R", 0, -14)
    # wartende Leute im Hof und unter dem Dach
    spots = [(-5.0, -3.0, (-4.2, -2.0), False), (-4.1, -2.4, (-5.0, -3.0), False), (-4.7, -1.8, (-4.4, 5.0), False),
             (-7.8, 12.0, (-7.8, 0), True), (-3.6, 12.6, (0, 0), True), (5.2, 12.2, (4, 0), True), (9.4, 13.1, (8, 0), True),
             (11.8, 11.6, (10, 0), True), (-10.5, 14.8, (-10, 0), True), (1.2, 15.6, (1, 0), True)]
    ppl = crowd(spots, seed=40)
    Q.head_to(ppl[2], 0.0, (-4.7, 4.0, 9.0))
    walker = Q.person("kommt", (14.0, 1.1, 0), seed=44, head="turban")
    Q.walk(walker, [(14.6, 1.1), (9.0, 3.5), (6.0, 9.0)], 0.0, speed=1.0)
    for k, (x, y) in enumerate(((-4.5, -2.8), (8.0, 11.4), (-6.0, 11.6))):
        Lp = Q.oil_lamp(f"floor{k}", (x, y, 0.03), energy=0.0)
        Lp["light"].data.energy = 22
        Q.flicker(Lp["light"], 0, D, 22, seed=k)
    return L


def holy(loc, t0=0.0, t1=None):
    H = Q.holy_light("nur", loc)
    Q.animate_motes(H, Q.T(t0), Q.T(t1 if t1 is not None else D))
    return H


def shot_beratung():
    L = night()
    L["mist_amt"] = 0.3
    I = MD.town(night=True)
    C = Vector((0.0, 13.75))
    R = 1.75
    Hl = holy((C.x, C.y + R + 0.05, 0))
    rig, shake, cam = Q.pov_camera(lens=18)
    pov = (0.0, C.y - 3.35, 0.98)
    angs = [32, 70, 106, 138, 222, 254, 290, 328]
    sah = []
    for i, a in enumerate(angs):
        r = math.radians(a)
        p = (C.x - R * math.sin(r), C.y + R * math.cos(r))
        P = Q.person(f"sah{i}", (*p, 0), yaw=Q.face_yaw(p, C), sit=True, glow=True, seed=60 + i,
                     head="turban" if i % 3 else "scarf", cloak=(0.32, 0.26, 0.2) if i % 2 else None)
        Q.idle(P, 0, D, seed=i, look=[(0, 0, 0)])
        Q.head_to(P, 0.0, (Hl["root"].location.x, Hl["root"].location.y, 1.0))
        sah.append((P, p))
    light_pt = (C.x, C.y + R, 1.4)
    # wer schlägt was vor (Glocke links, Horn rechts, Feuer links hinten)
    who = {"glocke_d4": 1, "horn_d4": 6, "feuer_d4": 2}
    cam_rot = [(0, (0, -4, 0)), (ls("d3") + 2.0, (0, -2, 0))]
    for ev, idx in who.items():
        t = lt(EV[ev])
        P, p = sah[idx]
        Q.head_to(P, t - 0.6, (*light_pt[:2], 1.0))
        Q.head_to(P, t - 0.2, (C.x, C.y - 1.2, 0.9))
        Q.arm_pose(P, t - 0.5, "R", 28, -50)
        Q.arm_pose(P, t + 0.1, "R", -40, -70)
        Q.arm_pose(P, t + 1.4, "R", 28, -50)
        Q.head_to(P, t + 1.8, (*light_pt[:2], 1.0))
        for j, (Pj, pj) in enumerate(sah):  # die anderen schauen kurz hin
            if j != idx and (j + idx) % 2 == 0:
                Q.head_to(Pj, t + 0.1, (p[0], p[1], 0.9))
                Q.head_to(Pj, t + 1.6, (*light_pt[:2], 1.0))
        cam_rot.append((t - 0.3, (Q.yaw_to(pov, p) * 0.6, -6, 0)))
        cam_rot.append((t + 1.3, (Q.yaw_to(pov, p) * 0.6, -6, 0)))
    cam_rot.append((ls("d5") + 0.3, (0, -3, 0)))
    cam_rot.append((D, (0, -1, 0)))
    Q.cam_keys(rig, [(0, pov, None), (D, (0.0, pov[1] + 0.45, 0.98), None)], loc_interp="BEZIER")
    Q.cam_keys(rig, [(t, None, a) for t, a in cam_rot])
    Q.handheld(shake, 0, D, amp=0.55)
    Q.point("fill", (0, C.y - 4, 2.5), 8, color=(0.8, 0.7, 0.6))
    return L


def shot_traum():
    Q.world_sky("dream")
    X0 = Vector((3000, 0, 0))
    mfloor = Q.glow_mat("dream_floor", (1.0, 0.82, 0.55), 1.6)
    fl = Q.cyl("dream_floor", X0 - Vector((0, 0, 0.026)), 60, 0.05, Q.pbr("dream_ground", (0.7, 0.55, 0.38), 0.5, emit=(1.0, 0.8, 0.5), es=0.12), seg=64)
    # Lichtschleier (große, schwache Leuchtkugeln)
    for i in range(7):
        a = i / 7 * 2 * math.pi
        Q.ball(f"veil{i}", X0 + Vector((9 * math.cos(a), 9 * math.sin(a), 2.5)), (4, 4, 3),
               Q.glow_mat(f"veil{i}", (1.0, 0.85, 0.6), 0.8, 0.3, fresnel=True), seg=24)
    for i in range(6):
        a = i / 6 * 2 * math.pi + 0.4
        ray = Q.cyl(f"ray{i}", X0 + Vector((3.5 * math.cos(a), 3.5 * math.sin(a), 6)), 0.6, 14,
                    Q.glow_mat(f"ray{i}", (1.0, 0.86, 0.6), 1.0, 0.14, fresnel=True, grad_z=(-7, 7)), seg=20, caps=False, r2=0.15)
        ray.rotation_euler = (math.radians(14) * math.sin(a), math.radians(14) * math.cos(a), 0)
    ab = Q.person("abdullah", tuple(X0), yaw=0.0, glow=True, seed=91, robe=(0.92, 0.9, 0.84), wrap=(0.95, 0.94, 0.9), head="turban")
    Q.idle(ab, 0, D, seed=2, look=[(0, 0, 0)])
    gm = Q.person("gruen", tuple(X0 + Vector((0, -2.2, 0))), seed=92, robe=(0.1, 0.36, 0.2), wrap=(0.86, 0.84, 0.76),
                  head="turban", cloak=(0.06, 0.26, 0.13))
    # Glocke in der rechten Hand
    mb = Q.pbr("bronze", (0.6, 0.42, 0.2), 0.35, metal=0.9)
    hb = gm["hand.R"]
    bell = Q.loft("bell", [(-0.22, 0.11, 0.11), (-0.2, 0.1, 0.1), (-0.12, 0.075, 0.075), (-0.04, 0.06, 0.06), (0.0, 0.045, 0.045),
                           (0.02, 0.012, 0.012)], mb, seg=24, parent=hb, cap_bot=False)
    bell.location = (0, 0, -0.08)
    Q.ball("bell_clap", (0, 0, -0.28), 0.025, mb, parent=hb, seg=10)
    # Der Mann geht um Abdullah herum (Abu Dawud 499: „ein Mann ging um mich herum“), dann bleibt er vor ihm stehen
    r = 2.2
    t_stop = max(4.0, qs("q1") - 0.6)
    pts = []
    n = 24
    for k in range(n + 1):
        a = -math.pi / 2 + 1.5 * math.pi * k / n
        pts.append((X0.x + r * math.cos(a), X0.y + r * math.sin(a)))
    sp = (1.5 * math.pi * r) / max(1.0, t_stop - 0.3)
    end_t = Q.walk(gm, pts, 0.3, speed=sp)
    end_p = Vector((pts[-1][0], pts[-1][1], 0))
    gm["root"].rotation_euler.z = Q.face_yaw(end_p, X0)
    gm["root"].keyframe_insert("rotation_euler", frame=Q.T(end_t + 0.4))
    Q.hold(gm, end_t + 0.4, D)
    Q.arm_pose(gm, 0.2, "R", -35, -55)
    Q.arm_pose(gm, qs("q2"), "R", -35, -55)
    Q.arm_pose(gm, qs("q2") + 0.5, "R", -10, -30)
    Q.arm_pose(gm, ls("d8"), "L", 0, -14)
    Q.arm_pose(gm, ls("d8") + 0.6, "L", -70, -40, sh_y=-20)
    # Abdullah dreht sich zum Mann
    for k in range(6):
        t = 0.3 + (end_t - 0.3) * k / 5
        a = -math.pi / 2 + 1.5 * math.pi * k / 5
        Q.head_to(ab, t, (X0.x + r * math.cos(a), X0.y + r * math.sin(a), 1.6), clamp=60)
    ab["root"].keyframe_insert("rotation_euler", frame=Q.T(end_t))
    ab["root"].rotation_euler.z = Q.face_yaw(X0, end_p)
    ab["root"].keyframe_insert("rotation_euler", frame=Q.T(end_t + 0.8))
    Q.head_to(ab, end_t + 0.8, (end_p.x, end_p.y, 1.6))
    # Lichtpunkte steigen auf (Worte des Adhan)
    rnd = random.Random(3)
    mm = Q.glow_mat("word_mote", (1.0, 0.85, 0.5), 25.0)
    for i in range(40):
        o = Q.ball(f"wm{i}", X0 + Vector((rnd.uniform(-2, 2), rnd.uniform(-2, 2), 0.2)), 0.015, mm, seg=8)
        t0 = ls("d8") + rnd.uniform(0, 2.5)
        o.scale = (0.01, 0.01, 0.01)
        o.keyframe_insert("scale", frame=Q.T(max(0, t0 - 0.1)))
        o.scale = (1, 1, 1)
        o.keyframe_insert("scale", frame=Q.T(t0))
        o.keyframe_insert("location", frame=Q.T(t0))
        o.location.z += rnd.uniform(3, 6)
        o.keyframe_insert("location", frame=Q.T(D))
    Q.point("dream_key", tuple(X0 + Vector((-3, -4, 5))), 220, color=(1.0, 0.85, 0.65), radius=1.0)
    Q.point("dream_rim", tuple(X0 + Vector((2, 4, 3))), 160, color=(1.0, 0.75, 0.45), radius=1.0)
    bpy.context.scene.world.mist_settings.start = 6.0
    bpy.context.scene.world.mist_settings.depth = 45.0
    # Kamera: langsamer Bogen + Annäherung (dritte Person, traumhaft)
    rig, shake, cam = Q.pov_camera(lens=24)
    keys = []
    for k in range(9):
        u = k / 8
        a = math.radians(-100 + 55 * u)
        rr = 6.0 - 2.2 * u
        p = (X0.x + rr * math.cos(a), X0.y + rr * math.sin(a), 1.7 + 0.5 * u)
        keys.append((D * u, p, (Q.yaw_to(p, (X0.x, X0.y)), Q.pitch_to(p, (X0.x, X0.y, 1.2)), 0)))
    Q.cam_keys(rig, keys, interp="BEZIER")
    Q.handheld(shake, 0, D, amp=0.3)
    return dict(mist_col=(0.8, 0.62, 0.42), mist_amt=0.55)


def shot_morgen():
    L = dawn(0.8)
    I = MD.town(night=False)
    light_p = (0.0, 12.4, 0)
    Hl = holy(light_p)
    rig, shake, cam = Q.pov_camera()
    pov0, pov1 = (-2.6, -1.0, 1.62), (-2.2, 1.0, 1.62)
    ab = Q.person("abdullah", (-1.3, 3.5, 0), seed=91, robe=(0.92, 0.9, 0.84), wrap=(0.95, 0.94, 0.9), glow=True)
    t_end = Q.walk(ab, [(-1.3, 3.5), (-0.6, 7.5), (-0.2, 10.6)], ls("d9") + 0.3, speed=1.15)
    Q.hold(ab, t_end, D)
    Q.head_to(ab, t_end + 0.2, (0, 12.4, 1.5))
    Q.head_to(ab, qs("q3") + 0.5, (0, 12.4, 1.2))
    bil_p0, bil_p1 = (3.4, 11.3), (0.9, 10.6)
    bil = Q.person("bilal", (*bil_p0, 0), yaw=Q.face_yaw(bil_p0, (0, 10.6)), seed=93, skin=(0.2, 0.12, 0.08),
                   robe=(0.84, 0.8, 0.7), wrap=(0.9, 0.88, 0.82), glow=True, height=1.04)
    Q.idle(bil, 0, D, seed=7, look=[(0, 0, 0)])
    tb = lt(EV["bilal_d10"])
    Q.hold(bil, 0, tb - 0.2)
    t2 = Q.walk(bil, [bil_p0, bil_p1], tb - 0.2, speed=1.0)
    bil["root"].rotation_euler.z = Q.face_yaw(bil_p1, (0, 12.4))
    bil["root"].keyframe_insert("rotation_euler", frame=Q.T(t2 + 0.5))
    Q.hold(bil, t2 + 0.5, D)
    Q.head_to(ab, tb + 0.6, (*bil_p1, 1.6))
    spots = [(-7.5, 12.4, (-7.5, 0), True), (-4.2, 12.2, (0, 12.4), True), (5.6, 12.6, (0, 12.4), True), (8.8, 12.0, (8, 0), True),
             (-9.8, 3.0, (0, 12), False), (7.0, -2.0, (0, 12), False), (6.2, -2.6, (7.0, -2.0), False)]
    crowd(spots, seed=70)
    Q.cam_keys(rig, [(0, pov0, None), (5.0, pov1, None), (D, (-2.0, 1.4, 1.62), None)], loc_interp="BEZIER")
    Q.cam_keys(rig, [(0, None, (Q.yaw_to(pov0, (-1.3, 3.5)) * 0.6, -2, 0)), (ls("d9") + 2.0, None, (Q.yaw_to(pov1, (0, 10)), 0, 0)),
                     (tb - 0.3, None, (Q.yaw_to(pov1, (0, 11)), 0, 0)), (tb + 0.4, None, (Q.yaw_to(pov1, bil_p0) * 0.85, 0, 0)),
                     (t2 + 0.6, None, (Q.yaw_to(pov1, (0.5, 10.8)), 1, 0)), (D, None, (Q.yaw_to(pov1, (0.5, 10.8)), 2, 0))])
    Q.handheld(shake, 0, D, amp=0.8, walk_from=0, walk_to=5.0, walk_amp=0.6)
    return L


def bilal_on_roof(I, t_hands):
    rp = I["roof_bilal"]
    bil = Q.person("bilal", (rp.x - 1.2, rp.y - 1.0, rp.z), seed=93, skin=(0.2, 0.12, 0.08), robe=(0.84, 0.8, 0.7),
                   wrap=(0.9, 0.88, 0.82), glow=True, height=1.04, cloak=(0.42, 0.34, 0.26))
    return bil


def shot_dach_a():
    L = dawn(1.0)
    I = MD.town(night=False)
    rp = I["roof_bilal"]
    bil = bilal_on_roof(I, 0)
    t_walk = Q.walk(bil, [(rp.x - 1.2, rp.y - 1.0), (rp.x, rp.y)], 0.2, speed=0.7)
    bil["root"].rotation_euler.z = math.pi / 2 + 0.25
    bil["root"].keyframe_insert("rotation_euler", frame=Q.T(t_walk + 0.6))
    Q.hold(bil, t_walk + 0.6, D)
    ta = lt(EV["athan"])
    Q.arms_rest(bil, ta - 0.9)
    Q.hands_to_ears(bil, ta - 0.1)
    Q.head_to(bil, ta - 0.9, (0, -10, 7.5), up=5)
    Q.head_to(bil, ta + 0.4, (0, -10, 9), up=14)
    rig, shake, cam = Q.pov_camera(lens=17)
    pov = (-7.6, -8.6, 1.62)
    tgt = (rp.x, rp.y, rp.z + 1.0)
    Q.cam_keys(rig, [(0, (-5.8, -7.8, 1.62), None), (D, pov, None)], loc_interp="BEZIER")
    zoom = cam.data
    zoom.keyframe_insert("lens", frame=1)
    zoom.keyframe_insert("lens", frame=Q.T(1.4))
    zoom.lens = 38
    zoom.keyframe_insert("lens", frame=Q.T(3.6))
    Q.cam_keys(rig, [(0, None, (Q.yaw_to(pov, tgt) - 25, 4, 0)), (1.6, None, (Q.yaw_to(pov, tgt) - 8, 14, 0)),
                     (ta, None, (Q.yaw_to(pov, tgt), Q.pitch_to(pov, tgt) - 2, 0)), (D, None, (Q.yaw_to(pov, tgt), Q.pitch_to(pov, tgt), 0))])
    Q.handheld(shake, 0, D, amp=0.7, walk_from=0, walk_to=1.5, walk_amp=0.5)
    spots = [(-9.5, -5.0, (rp.x, rp.y), False), (-7.0, -11.5, (-4, -4), False), (-6.3, -10.8, (-7.0, -11.5), False)]
    ppl = crowd(spots, seed=80)
    for P in ppl:
        Q.head_to(P, ta + 0.6 + random.random(), (rp.x, rp.y, rp.z + 1.5))
    return L


def shot_dach_b():
    L = dawn(1.0)
    I = MD.town(night=False)
    rig, shake, cam = Q.pov_camera()
    pov = (0.2, -33.0, 1.62)
    Q.cam_keys(rig, [(0, pov, (2, 2, 0)), (D, (0.2, -32.6, 1.62), (-4, 6, 0))])
    Q.handheld(shake, 0, D, amp=0.8)
    sky = (-15, -12, 12)
    a = Q.person("geh", (0.4, -28.5, 0), seed=101)
    t1 = Q.walk(a, [(0.4, -28.5), (0.3, -30.3)], 0.0, speed=1.0)
    Q.hold(a, t1, D)
    Q.head_to(a, t1 + 0.3, sky, up=30)
    b = Q.person("tuer1", (-2.6, -26.0, 0), yaw=math.pi / 2, seed=102, head="scarf")
    t2 = Q.walk(b, [(-2.6, -26.0), (-1.2, -26.4)], 0.4, speed=0.9)
    Q.hold(b, t2, D)
    Q.head_to(b, t2 + 0.2, sky, up=35)
    c = Q.person("tuer2", (1.7, -36.5, 0), yaw=-math.pi / 2, seed=103, head="cap")
    Q.idle(c, 0, D, seed=1, look=[(0.3, -20, 25), (1.5, -10, 32)])
    d = Q.person("kind", (-1.0, -34.0, 0), yaw=math.pi, seed=104, head="cap", height=0.72)
    Q.idle(d, 0, D, seed=2, look=[(0.2, 30, 30), (2.0, 10, 35)])
    return L


def shot_dach_c():
    L = dawn(1.0)
    I = MD.town(night=False)
    rp = I["roof_bilal"]
    bil = bilal_on_roof(I, 0)
    bil["root"].location = (rp.x, rp.y, rp.z)
    bil["root"].rotation_euler.z = math.pi / 2 + 0.25
    Q.hands_to_ears(bil, 0.0)
    Q.head_to(bil, 0.0, (0, -10, 9), up=14)
    Q.idle(bil, 0, D, seed=3, look=[(0, 0, -14)])
    rig, shake, cam = Q.pov_camera(lens=16)
    p0 = (rp.x - 2.3, rp.y - 0.5, rp.z + 1.75)
    p1 = (rp.x - 2.0, rp.y - 0.2, rp.z + 1.9)
    Q.cam_keys(rig, [(0, p0, (-66, -9, 0)), (D, p1, (-70, -7, 0))])
    Q.handheld(shake, 0, D, amp=0.4)
    crowd([(-8.0, -6.0, (-19, -10), False), (-6.5, -2.0, (-19, -10), False), (3.0, 4.0, (0, 12), False), (4.5, 6.5, (0, 12), False),
           (-2.0, 9.0, (0, 12), False)], seed=90)
    return L


def shot_dach_d():
    L = dawn(1.0)
    I = MD.town(night=False)
    rig, shake, cam = Q.pov_camera()
    pov0, pov1 = (-3.5, 1.5, 1.62), (-3.0, 3.0, 1.62)
    Q.cam_keys(rig, [(0, pov0, (-22, 0, 0)), (D, pov1, (-8, 1, 0))])
    Q.handheld(shake, 0, D, amp=0.8, walk_from=0, walk_to=D, walk_amp=0.5)
    rnd = random.Random(5)
    for i in range(9):
        if i < 5:
            x0, y0 = rnd.uniform(-1.0, 1.0), -12.0 - i * 1.6
            path = [(x0, y0), (x0 * 0.5, -6.5), (-3 + i * 1.5, 8.5)]
        else:
            x0, y0 = 10.0 + (i - 5) * 1.4, 1.0 + rnd.uniform(-0.5, 0.5)
            path = [(x0, y0), (6.0, 3.0), (2 + (i - 5) * 1.5, 8.5)]
        P = Q.person(f"zug{i}", (x0, y0, 0), seed=110 + i, head=rnd.choice(["turban", "scarf", "cap"]))
        tt = Q.walk(P, path, rnd.uniform(0, 0.8), speed=rnd.uniform(1.15, 1.45))
    spots = [(-6.0, 12.3, (-6, 20), False), (-4.5, 12.3, (-4.5, 20), False), (-3.0, 12.3, (-3, 20), False), (1.5, 12.3, (1.5, 20), False),
             (3.0, 12.3, (3, 20), False), (4.5, 12.3, (4.5, 20), False)]
    crowd(spots, seed=120)
    return L


def shot_umar():
    L = dawn(1.0)
    I = MD.town(night=False)
    hinge = I["umar_door"]
    ud = I["umar_door_pos"]
    td = lt(EV["door_umar"])
    hinge.rotation_euler.z = 0
    hinge.keyframe_insert("rotation_euler", frame=Q.T(max(0, td - 0.05)))
    hinge.rotation_euler.z = math.radians(-105)
    hinge.keyframe_insert("rotation_euler", frame=Q.T(td + 0.25))
    hinge.rotation_euler.z = math.radians(-92)
    hinge.keyframe_insert("rotation_euler", frame=Q.T(td + 0.6))
    um = Q.person("umar", (ud.x + 1.4, ud.y, 0), yaw=-math.pi / 2, seed=95, glow=True, height=1.08, robe=(0.8, 0.74, 0.62),
                  wrap=(0.92, 0.9, 0.84), cloak=(0.24, 0.19, 0.15), long_cloak=True)
    path = [(ud.x + 1.4, ud.y), (ud.x - 0.8, ud.y + 0.2), (0.6, ud.y + 3.0), (0.4, -26.0), (0.2, -16.0)]
    Q.hold(um, 0, td)
    Q.walk(um, path, td + 0.05, speed=4.4, run=True)
    if "trail" in um:  # Umhang flattert/schleift
        tr = um["trail"]
        for k in range(0, int(D * 24), 3):
            tr.rotation_euler = (math.sin(k * 0.7) * 0.06, 0, math.sin(k * 0.45) * 0.08)
            tr.keyframe_insert("rotation_euler", frame=k + 1)
    rig, shake, cam = Q.pov_camera()
    pov = (-0.6, -46.5, 1.62)
    door_pt = (ud.x, ud.y, 1.2)
    Q.cam_keys(rig, [(0, pov, None), (td + 2.0, pov, None), (D, (-0.2, -40.0, 1.62), None)], loc_interp="BEZIER")
    Q.cam_keys(rig, [(0, None, (-3, 0, 0)), (td - 0.15, None, (-6, 0, 0)), (td + 0.2, None, (Q.yaw_to(pov, door_pt), 0, 0)),
                     (td + 0.9, None, (Q.yaw_to(pov, (1.0, ud.y + 2.0)), 1, 0)), (td + 2.2, None, (-2, 3, 0)), (D, None, (0, 4, 0))])
    Q.handheld(shake, 0, D, amp=1.1, walk_from=td + 2.0, walk_to=D, walk_amp=1.0)
    a = Q.person("weiche", (-0.9, -36.0, 0), yaw=math.pi, seed=131)
    Q.idle(a, 0, D, seed=2, look=[(0, 0, 10), (td + 1.0, 30, 0), (td + 1.6, 60, 0)])
    return L


def shot_ende():
    L = dawn(1.15)
    I = MD.town(night=False)
    Hl = holy((0.0, 10.6, 0))
    rows = []
    for r_ in range(3):
        for k in range(-6, 7):
            x, y = k * 0.85, 9.2 - r_ * 1.3
            P = Q.person(f"reihe{r_}_{k}", (x, y, 0), yaw=math.pi, seed=200 + r_ * 20 + k, head=random.Random(k).choice(["turban", "scarf"]))
            rows.append(P)
    rp = I["roof_bilal"]
    bil = bilal_on_roof(I, 0)
    bil["root"].location = (rp.x, rp.y, rp.z)
    bil["root"].rotation_euler.z = math.pi / 2 + 0.25
    rig, shake, cam = Q.pov_camera(lens=17)
    p0 = (0.0, -26.0, 4.2)
    p1 = (6.0, -40.0, 30.0)
    Q.cam_keys(rig, [(0, p0, (Q.yaw_to(p0, (0, 6)), Q.pitch_to(p0, (0, 6, 1.5)), 0)),
                     (D, p1, (Q.yaw_to(p1, (0, 4)) + 6, Q.pitch_to(p1, (0, 4, 0)) + 9, 0))], interp="BEZIER")
    Q.handheld(shake, 0, D, amp=0.25)
    return L


SHOTS = {"gasse": shot_gasse, "moschee": shot_moschee, "beratung": shot_beratung, "traum": shot_traum, "morgen": shot_morgen,
         "dach_a": shot_dach_a, "dach_b": shot_dach_b, "dach_c": shot_dach_c, "dach_d": shot_dach_d, "umar": shot_umar, "ende": shot_ende}

Q.reset()
cfg = SHOTS[SHOT]()
if SHOT != "traum" and os.environ.get("JOIN", "1") == "1":
    MD.join_static()
Q.render_setup(pct=PCT, samples=SAMPLES, mist_col=cfg["mist_col"], mist_amt=cfg["mist_amt"])
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, SEG[SHOT]["frames"]
os.makedirs(OUT, exist_ok=True)
if STILLS:
    for t in STILLS:
        sc.frame_set(Q.T(t))
        sc.render.filepath = os.path.join(OUT, f"{SHOT}_{t:05.2f}.png")
        bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath = os.path.join(OUT, "")
    sc.render.use_overwrite = False
    sc.render.use_placeholder = True
    bpy.ops.render.render(animation=True)
