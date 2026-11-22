# QISSAH Folge 3 – „Die Erbauer der Kaaba“: alle Einstellungen in Blender (Ich-Sicht: Frauen Ismails, ein Junge der Dschurhum,
# ein Pilger heute). Aufruf:
#   blender -b --factory-startup --python blender/qissa/kaaba.py -- <einstellung> <ausgabe_ordner> [prozent] [samples] [standbild-zeiten]
# Längen und Ereignisse: src/qissa_kaaba/timeline.json (scripts/build_qissa_kaaba.py).
# Regeln: Ibrahim und Ismail (Propheten) NUR als Licht; Menschen ohne Gesicht; keine Darstellung des Propheten ﷺ.
import bpy, sys, os, math, json, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import lib as Q
import medina as MD
import mekka as MK
import kaaba_world as KW

TL = json.load(open(os.environ.get("TL_FILE") or os.path.join(ROOT, "src", "qissa_kaaba", "timeline.json"), encoding="utf-8"))  # TL_FILE: alter Zeitplan für Teil-Neurender
SEG = {s["id"]: s for s in TL["segments"]}
LINE = {l["id"]: l for l in TL["lines"]}
EV = TL["events"]
Q.FPS = TL.get("render_fps", 30)
MK.PEB_SUB = 1      # Kiesel einfacher (Rechner ohne Grafikkarte: jedes Dreieck kostet je Sample)
MK.N_SHRUBS = 100
MK.FAR_LEAVES = 700
MK.SHRUB_SUB = 0


def _fast_templates():
    """Felsbrocken mit weniger Dreiecken (Unterteilung 2 statt 3) – gleiche Formen, viel schneller."""
    if MK._TPL:
        return
    for k in range(7):
        me = MK._rock_mesh(f"tpl_rock{k}", 100 + k, sub=2)
        me.materials.append(MK.M["rock"] if k % 3 else MK.M["rock2"])
        MK._TPL[f"rock{k}"] = me
    for k in range(4):
        MK._TPL[f"shrub{k}"] = MK._shrub_mesh(f"tpl_shrub{k}", 200 + k, green=(k == 3))


MK._templates = _fast_templates

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SHOT = argv[0] if argv else "zelte"
OUT = argv[1] if len(argv) > 1 else "/tmp/kaaba"
PCT = int(argv[2]) if len(argv) > 2 else 50
SAMPLES = int(argv[3]) if len(argv) > 3 else 8
STILLS = [float(x) for x in argv[4].split(",")] if len(argv) > 4 and argv[4] else None

S0 = SEG[SHOT]["start"]
D = SEG[SHOT]["dur"]
EYE = 1.55
SIT = 0.98
gz = MK.ground_z
SP, TREE, HILL, HUT = KW.SP, KW.TREE, KW.HILL, KW.HUT


def lt(t_abs):
    return t_abs - S0


def ls(i):
    return lt(LINE[i]["start"])


def le(i):
    return lt(LINE[i]["start"] + LINE[i]["dur"])


def ev(k):
    return lt(EV[k])


def P(x, y, eye=EYE):
    return (x, y, gz(x, y) + eye)


def look(src, dst):
    return (Q.yaw_to(src, dst), Q.pitch_to(src, dst), 0)


def smooth(a, b, x):
    u = min(1.0, max(0.0, (x - a) / max(1e-6, b - a)))
    return u * u * (3 - 2 * u)


def lerp3(a, b, u):
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))


def prophet(name, loc, height=2.2, strength=0.9, day=True):
    """Ibrahim / Ismail: nur als Licht-Säule (wie Folge 2). Sitzend = niedrigere Säule."""
    H = Q.holy_light(name, loc, height=height, strength=strength)
    if day:
        H["light"].data.energy = 22.0
        em = next(n for n in H["parts"][3].active_material.node_tree.nodes if n.type == "EMISSION")
        em.inputs["Strength"].default_value = 0.6
    Q.animate_motes(H, 1, Q.T(D) + 2)
    return H


def rise(H, t0, t1, h0, h1):
    """Licht-Säule wird höher (steht auf) – Skalierung in z."""
    r = H["root"]
    r.scale = (1, 1, h0 / H["height"])
    r.keyframe_insert("scale", frame=max(1, Q.T(t0)))
    r.scale = (1, 1, h1 / H["height"])
    r.keyframe_insert("scale", frame=max(2, Q.T(t1)))


def glow_pulse(H, t, peak=2.2):
    """Licht leuchtet kurz stärker (Segen, Begrüßung)."""
    lo = H["light"]
    base = lo.data.energy
    for tt, v in ((t - 0.1, base), (t + 0.5, base * peak), (t + 2.0, base)):
        lo.data.energy = v
        lo.data.keyframe_insert("energy", frame=max(1, Q.T(tt)))
    for part in H["parts"][:3]:
        em = next(n for n in part.active_material.node_tree.nodes if n.type == "EMISSION")
        s = em.inputs["Strength"]
        b = s.default_value
        for tt, v in ((t - 0.1, b), (t + 0.5, b * (1 + (peak - 1) * 0.6)), (t + 2.0, b)):
            s.default_value = v
            s.keyframe_insert("default_value", frame=max(1, Q.T(tt)))


def motes_burst(name, center, t0, n=40, radius=0.5, rise_h=1.6, dur=4.0, seed=0, col=(1.0, 0.85, 0.5)):
    """Goldene Lichtpunkte steigen auf (Segen)."""
    rnd = random.Random(seed)
    m = Q.glow_mat(f"{name}_m", col, 9.0)
    for k in range(n):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(0.05, radius)
        p0 = Vector((center[0] + r * math.cos(a), center[1] + r * math.sin(a), center[2] + rnd.uniform(-0.05, 0.1)))
        o = Q.ball(f"{name}{k}", p0, 0.0035 + rnd.random() * 0.004, m, seg=8)
        o.scale = (0.001, 0.001, 0.001)
        ts = t0 + rnd.uniform(0, dur * 0.5)
        o.keyframe_insert("scale", frame=max(1, Q.T(ts)))
        o.keyframe_insert("location", frame=max(1, Q.T(ts)))
        o.scale = (1, 1, 1)
        o.keyframe_insert("scale", frame=Q.T(ts + 0.3))
        o.location = p0 + Vector((rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), rise_h * rnd.uniform(0.6, 1.2)))
        o.keyframe_insert("location", frame=Q.T(ts + dur * rnd.uniform(0.6, 1.0)))
        o.scale = (0.001, 0.001, 0.001)
        o.keyframe_insert("scale", frame=Q.T(ts + dur * rnd.uniform(0.6, 1.0)))


# ---------------------------------------------------------------- Hände (Ich-Sicht der Frauen) und gehaltene Dinge
POSES = {
    "lap": {"L": ((-0.16, -0.52, -0.33), (-85, 0, -15)), "R": ((0.16, -0.52, -0.33), (-85, 0, 15))},
    "complain": {"L": ((-0.14, -0.11, -0.64), (-42, 180, 18)), "R": ((0.14, -0.11, -0.64), (-42, 180, -18))},
    "complain2": {"L": ((-0.18, -0.08, -0.63), (-38, 180, 26)), "R": ((0.18, -0.08, -0.63), (-38, 180, -26))},
    "tell": {"L": ((-0.2, -0.5, -0.34), (-85, 0, -15)), "R": ((0.12, -0.16, -0.46), (-62, 160, -10))},
    "bowl": {"L": ((-0.07, -0.3, -0.44), (-80, 180, -28)), "R": ((0.07, -0.3, -0.44), (-80, 180, 28))},
    "offer": {"L": ((-0.07, -0.2, -0.56), (-75, 180, -25)), "R": ((0.07, -0.2, -0.56), (-75, 180, 25))},
    "cup": {"L": ((-0.2, -0.5, -0.34), (-85, 0, -15)), "R": ((0.05, -0.2, -0.56), (-70, 180, 10))},
    "stir": {"L": ((-0.2, -0.46, -0.38), (-85, 0, -15)), "R": ((0.1, -0.34, -0.46), (-115, 0, -10))},
    "hidden": {"L": ((-0.2, -0.95, -0.3), (-80, 0, -10)), "R": ((0.2, -0.95, -0.3), (-80, 0, 10))},
}


def pose(H, t, name, only=None):
    for nm in ("L", "R"):
        if only and nm != only:
            continue
        loc, rot = POSES[name][nm]
        w = H[nm]
        w.location = loc
        w.rotation_euler = [math.radians(a) for a in rot]
        w.keyframe_insert("location", frame=max(1, Q.T(t)))
        w.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))


def gesture(H, t0, t1, amp=0.025, hz=1.3, seed=0):
    """Hände bewegen sich beim Reden leicht (zusätzlich zur Pose)."""
    rnd = random.Random(seed)
    for nm, ph in (("L", 0.0), ("R", 1.1)):
        w = H[nm]
        base = w.location.copy()
        for f in range(Q.T(t0), Q.T(t1) + 1, 3):
            t = (f - 1) / Q.FPS
            w.location = base + Vector((amp * 0.5 * math.sin(t * hz * 3.1 + ph), amp * abs(math.sin(t * hz * 2.2 + ph + rnd.random() * 0.2)),
                                        amp * 0.4 * math.sin(t * hz * 1.7 + ph)))
            w.keyframe_insert("location", frame=f)


WIFE1 = dict(skin=(0.42, 0.28, 0.19), sleeve=(0.2, 0.13, 0.1))
WIFE2 = dict(skin=(0.45, 0.3, 0.2), sleeve=(0.13, 0.17, 0.32))


def hut_pov(rig, keys_rot, H, seat_l=(0.0, 0.35), eye=SIT):
    """Kamera sitzt im Haus (lokal seat_l), schaut durch die Tür nach draußen."""
    return HUTD["world"](seat_l[0], seat_l[1], eye)


HUTD = {}


def make_hut(lamp=False, door_open=1.0):
    HUTD.update(KW.hut(lamp=lamp, door_open=door_open))
    return HUTD


def threshold_pt():
    return HUTD["world"](0, -KW.HUT_D / 2 + KW.WALL / 2, 0.12)


# ============================================================ Einstellungen
def shot_zelte():
    """Morgen: Ich gehe den Weg vom Norden hinunter ins Tal – Zelte der Dschurhum, Leute, Ziegen, Rauch; am Ende Zamzam (Brunnen)."""
    L, spots, vl = KW.settle_world("morning", t1=D + 1, life_kids=True)
    make_hut()
    # zwei Frauen am Brunnen: eine zieht den Eimer hoch, eine wartet mit Krug
    w1 = Q.person("wellw1", (SP.x + 1.3, SP.y + 0.6, gz(SP.x, SP.y)), yaw=Q.face_yaw((SP.x + 1.3, SP.y + 0.6), (SP.x, SP.y)), seed=71,
                  head="khimar", robe=(0.3, 0.2, 0.14), wrap=(0.16, 0.12, 0.1))
    Q.arm_pose(w1, 0, "L", -70, -30)
    Q.arm_pose(w1, 0, "R", -95, -20)
    for k in range(int(D / 1.6) + 1):
        t = k * 1.6
        Q.arm_pose(w1, t, "R", -95 if k % 2 else -150, -20)
        Q.arm_pose(w1, t + 0.8, "L", -150 if k % 2 else -70, -30)
    w2 = Q.person("wellw2", (SP.x - 1.6, SP.y + 1.0, gz(SP.x, SP.y)), yaw=Q.face_yaw((SP.x - 1.6, SP.y + 1.0), (SP.x, SP.y)), seed=72,
                  head="khimar", robe=(0.5, 0.36, 0.26), wrap=(0.42, 0.12, 0.08))
    Q.idle(w2, 0, D, seed=2)
    KW.jug("wjug", (SP.x - 1.2, SP.y + 0.8, gz(SP.x, SP.y) + 0.02), scale=1.0)
    rig, shake, cam = Q.pov_camera(lens=17)
    a, b = (-6.0, 16.6), (0.9, 2.6)

    def at(t):
        u = min(1.0, t / D)
        return P(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    Q.cam_keys(rig, [(0, at(0), None), (D, at(D), None)], loc_interp="LINEAR")
    tz = ev("zelte_e1")
    tzz = ev("zamzam_e2")
    cz_ = at(tz)
    near_t = min(spots, key=lambda q: (q[0] - cz_[0]) ** 2 + (q[1] - cz_[1]) ** 2 + (0 if q[0] > cz_[0] else 400))
    rot = [(0.0, look(at(0), (SP.x + 6, SP.y - 10, 2.0))), (3.4, look(at(3.4), (SP.x - 4, SP.y - 2, 0.5))),
           (tz - 0.3, look(at(tz - 0.3), (near_t[0], near_t[1], 1.0))), (tz + 2.6, look(at(tz + 2.6), (12, 8, 1.4))),
           (tzz - 1.6, look(at(tzz - 1.6), (SP.x, SP.y, 1.0))), (D, look(at(D), (SP.x, SP.y, 0.4)))]
    Q.cam_keys(rig, [(t, None, r) for t, r in rot])
    Q.handheld(shake, 0, D, amp=0.6, walk_from=0, walk_to=D, walk_amp=0.7)
    return L


def shot_ismail():
    """Goldene Stunde am Feuer: Ismail (Licht) sitzt bei den Männern des Stammes; sie reden mit ihm.
    „… verheiraten ihn mit einer Frau aus ihrem Stamm“: eine Frau kommt mit ihrer Mutter dazu."""
    fc = Vector((-12.0, -4.0, 0.0))
    L, spots, vl = KW.settle_world("golden", t1=D + 1, people=8, tent_avoid=[(fc.x, fc.y, 9.0)])
    make_hut()
    KW.cook_fire("gfire", (fc.x, fc.y, gz(fc.x, fc.y)), energy=70.0, pot=False)
    MK.rug("grug", (fc.x, fc.y, gz(fc.x, fc.y)), (4.6, 3.6), rot=0.2, mat=MK.M["blanket_r"])
    men = []
    for k, a in enumerate((0.6, 1.45, 3.55, 4.4, 6.25)):
        x, y = fc.x + 1.7 * math.cos(a), fc.y + 1.7 * math.sin(a)
        m = Q.person(f"man{k}", (x, y, gz(x, y)), yaw=Q.face_yaw((x, y), (fc.x, fc.y)), sit=True, seed=400 + k,
                     head=["turban", "scarf", "turban", "scarf", "turban"][k])
        men.append(m)
    ia = 5.5
    ip = (fc.x + 1.7 * math.cos(ia), fc.y + 1.7 * math.sin(ia))
    Is = prophet("ismail", (ip[0], ip[1], gz(*ip)), height=1.35, strength=0.85)
    for k, m in enumerate(men):  # alle schauen zu ihm, einer gestikuliert
        Q.head_to(m, 0.0, (ip[0], ip[1], gz(*ip) + 1.0))
        Q.idle(m, 0, D, seed=k, look=None) if k == 4 else None
        if k in (1, 3):
            for j in range(int(D / 2.2)):
                Q.arm_pose(m, j * 2.2, "R", -60 if j % 2 else -35, -30 if j % 2 else -70)
    # Frau des Stammes + ihre Mutter kommen (e4 „… mit einer Frau aus ihrem Stamm“)
    t_w = ls("e4") + 3.6
    bride = Q.person("bride", (fc.x + 7.5, fc.y - 6.0, 0), seed=81, head="khimar", robe=(0.42, 0.12, 0.09), wrap=(0.55, 0.2, 0.12),
                     height=0.94)
    mother = Q.person("bmother", (fc.x + 8.2, fc.y - 6.8, 0), seed=82, head="khimar", robe=(0.16, 0.12, 0.1), wrap=(0.12, 0.1, 0.09))
    Q.walk(bride, [(fc.x + 7.5, fc.y - 6.0), (ip[0] + 1.6, ip[1] - 1.2)], t_w, speed=0.9)
    Q.walk(mother, [(fc.x + 8.2, fc.y - 6.8), (ip[0] + 2.4, ip[1] - 1.9)], t_w + 0.2, speed=0.9)
    rig, shake, cam = Q.pov_camera(lens=17)
    sa = 2.5
    c0 = (fc.x + 1.95 * math.cos(sa), fc.y + 1.95 * math.sin(sa), gz(fc.x, fc.y) + 1.02)
    c1 = (fc.x + 2.05 * math.cos(sa + 0.12), fc.y + 2.05 * math.sin(sa + 0.12), gz(fc.x, fc.y) + 1.05)
    ipz = (ip[0], ip[1], gz(*ip) + 0.9)
    Q.cam_keys(rig, [(0, c0, look(c0, (fc.x, fc.y, 0.4))), (ev("ismail_e3") - 0.4, None, look(c0, ipz)),
                     (ls("e4") + 2.0, None, look(c0, (fc.x - 0.4, fc.y, 1.0))),
                     (t_w + 1.0, c1, look(c1, (ip[0] + 3.0, ip[1] - 2.5, 1.2))), (D, None, look(c1, (ip[0] + 1.0, ip[1] - 0.6, 1.0)))])
    Q.handheld(shake, 0, D, amp=0.45)
    return L


def shot_grab():
    """Dämmerung: ein einfaches Grab im Tal, daneben sitzt Ismail (Licht)."""
    L = MK.light("dusk", stars=1.5)
    KW.mats()
    MK.valley(keep=[(KW.GRAVE.x, KW.GRAVE.y, 3.0)])
    KW.grave()
    gp = KW.GRAVE
    Is = prophet("ismail", (gp.x + 1.3, gp.y - 0.4, gz(gp.x + 1.3, gp.y - 0.4)), height=1.3, strength=0.8, day=False)
    rig, shake, cam = Q.pov_camera(lens=17)
    p0 = (gp.x + 4.8, gp.y + 4.6, gz(gp.x, gp.y) + 1.5)
    p1 = (gp.x + 3.6, gp.y + 3.4, gz(gp.x, gp.y) + 1.4)
    tgt = (gp.x + 0.5, gp.y - 0.3, 0.3)
    Q.cam_keys(rig, [(0, p0, look(p0, tgt)), (D, p1, look(p1, tgt))], interp="BEZIER")
    Q.handheld(shake, 0, D, amp=0.25)
    return L


def wife_cam(lens=17, wife=WIFE1):
    rig, shake, cam = Q.pov_camera(lens=lens)
    H = MK.pov_arms(cam, skin=wife["skin"], sleeve=wife["sleeve"])
    return rig, shake, cam, H


def shot_ankunft():
    """Mittag, Ich-Sicht der ersten Frau Ismails im Haus: sie flickt einen Wasserschlauch, schaut auf – ein Licht kommt den Weg herab."""
    L, spots, vl = KW.settle_world("noon", t1=D + 1, people=8)
    make_hut()
    rig, shake, cam, H = wife_cam(wife=WIFE1)
    seat = HUTD["world"](0.15, 0.55, SIT)
    pose(H, 0, "lap")
    stop = HUTD["world"](0.1, -KW.HUT_D / 2 - 1.5)
    start = (-3.2, 11.8)
    Ib = prophet("ibrahim", (start[0], start[1], gz(*start)))
    path = [start, (1.5, 6.8), (stop[0], stop[1])]
    L_ = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))
    t0 = D - 0.2 - L_ / 1.25
    MK.hold_at(Ib, 0, start)
    MK.glide(Ib, path, t0, speed=1.25)
    th = threshold_pt()
    ibz = (stop[0], stop[1], gz(stop[0], stop[1]) + 1.2)
    Q.cam_keys(rig, [(0, seat, look(seat, (th[0], th[1], th[2] + 0.4))), (ev("ibrahim_e6") - 1.2, None, look(seat, (th[0], th[1], th[2] + 0.6))),
                     (ev("ibrahim_e6") - 0.1, None, look(seat, (start[0] + 1.0, start[1] - 1.0, 1.6))),
                     (D, None, look(seat, ibz))])
    Q.handheld(shake, 0, D, amp=0.3)
    return L


def shot_tuer1():
    """Ibrahim (Licht) steht vor der Tür. Die Frau klagt (Hände). „… die Schwelle seiner Tür wechseln“: Blick auf die Schwelle."""
    L, spots, vl = KW.settle_world("noon", t1=D + 1, people=8)
    make_hut()
    rig, shake, cam, H = wife_cam(wife=WIFE1)
    seat = HUTD["world"](0.15, 0.55, SIT)
    fr = HUTD["world"](0.1, -KW.HUT_D / 2 - 1.5)
    Ib = prophet("ibrahim", fr)
    MK.hold_at(Ib, 0)
    pose(H, 0, "lap")
    pose(H, ls("f1") - 0.25, "lap")
    pose(H, ls("f1") + 0.15, "complain")
    gesture(H, ls("f1") + 0.15, le("f1") - 0.4, amp=0.03, hz=1.2)
    pose(H, le("f1"), "complain2")
    pose(H, le("f1") + 0.7, "lap")
    ibz = (fr[0], fr[1], gz(fr[0], fr[1]) + 1.25)
    th = threshold_pt()
    ts = ev("schwelle_q1")
    Q.cam_keys(rig, [(0, seat, look(seat, ibz)), (ls("e7") + 3.0, None, look(seat, (ibz[0] + 0.3, ibz[1], ibz[2] - 0.1))),
                     (ls("f1") - 0.2, None, look(seat, (ibz[0], ibz[1], ibz[2] - 0.3))),
                     (ls("f1") + 0.6, None, look(seat, (ibz[0] - 0.2, ibz[1], ibz[2] - 0.5))),
                     (ls("q1") + 0.3, None, look(seat, ibz)), (ts - 0.6, None, look(seat, (ibz[0], ibz[1], ibz[2] - 0.1))),
                     (ts + 0.4, None, look(seat, th)), (D, None, look(seat, (th[0], th[1], th[2] + 0.05)))])
    Q.handheld(shake, 0, D, amp=0.3)
    return L


def shot_abend1():
    """Abend, Lampe brennt. Ismail (Licht) kommt zur Tür. Sie erzählt. „Geh zurück zu deiner Familie“: sie steht auf und geht über die Schwelle hinaus."""
    L, spots, vl = KW.settle_world("dusk", stars=1.8, t1=D + 1, people=6, goats=False)
    make_hut(lamp=True)
    Q.flicker(HUTD["lamp"]["light"], 0, D, 30.0)
    rig, shake, cam, H = wife_cam(wife=WIFE1)
    seat = HUTD["world"](0.15, 0.55, SIT)
    fr = HUTD["world"](0.1, -KW.HUT_D / 2 - 1.4)
    st = HUTD["world"](-2.6, -KW.HUT_D / 2 - 4.5)
    Is = prophet("ismail", (st[0], st[1], gz(st[0], st[1])), strength=0.85, day=False)
    MK.glide(Is, [(st[0], st[1]), (fr[0], fr[1])], ev("ismail_e8") - 0.4, speed=1.3)
    side = HUTD["world"](1.4, -KW.HUT_D / 2 - 1.6)
    MK.hold_at(Is, ev("trennen_q2") + 0.8, (fr[0], fr[1]))
    MK.glide(Is, [(fr[0], fr[1]), (side[0], side[1])], ev("trennen_q2") + 0.8, speed=0.9)
    pose(H, 0, "lap")
    pose(H, ls("f2"), "lap")
    pose(H, ls("f2") + 0.4, "tell")
    gesture(H, ls("f2") + 0.4, le("f2"), amp=0.02, hz=1.1)
    pose(H, le("f2") + 0.3, "lap")
    pose(H, ev("trennen_q2") + 0.8, "lap")
    pose(H, ev("trennen_q2") + 1.6, "hidden")
    isz = (fr[0], fr[1], gz(fr[0], fr[1]) + 1.25)
    door = HUTD["world"](0.05, -KW.HUT_D / 2 + 0.45, EYE)
    out1 = HUTD["world"](-0.35, -KW.HUT_D / 2 - 1.1, EYE)
    away = HUTD["world"](-3.0, -KW.HUT_D / 2 - 6.0, EYE - 0.2)
    stand = HUTD["world"](0.15, 0.4, EYE)
    tu = ev("trennen_q2")
    tf = ev("familie_q2")
    th = threshold_pt()
    # „… mich von dir zu trennen“: sie senkt den Blick; „Geh zurück …“ steht sie auf, geht zur Tür und über die Schwelle hinaus
    Q.cam_keys(rig, [(0, seat, look(seat, HUTD["world"](0, -2.5, 1.0))), (ev("ismail_e8") + 0.6, None, look(seat, isz)),
                     (ev("jemand_e8") - 0.3, None, look(seat, (isz[0], isz[1], isz[2] + 0.1))),
                     (ls("f2") + 0.5, None, look(seat, (isz[0] - 0.2, isz[1], isz[2] - 0.2))),
                     (tu - 0.3, seat, look(seat, isz)), (tu + 0.6, seat, look(seat, (isz[0], isz[1] , isz[2] - 0.9))),
                     (tu + 1.6, stand, look(stand, (isz[0], isz[1], isz[2] - 0.3))), (tf - 0.1, door, look(door, th)),
                     (D - 0.05, out1, look(out1, away))])
    Q.handheld(shake, 0, D, amp=0.35, walk_from=tu + 1.6, walk_to=D, walk_amp=0.8)
    return L


def shot_besuch2():
    """Morgen, Ich-Sicht der zweiten Frau: sie kocht Fleisch vor dem Haus; „… dann kommt Ibrahim wieder“: ein Licht kommt den Weg herab."""
    L, spots, vl = KW.settle_world("morning", t1=D + 1, people=8)
    make_hut()
    fp = HUTD["world"](-1.6, -KW.HUT_D / 2 - 1.2)
    F = KW.cook_fire("hfire", fp, energy=35.0, pot=True)
    for k in range(6):  # Fleisch im Topf
        Q.ball(f"potmeat{k}", (fp[0] + 0.07 * math.cos(k), fp[1] + 0.07 * math.sin(k), fp[2] + 0.555), (0.05, 0.04, 0.03), KW.M["meat"], seg=10)
    G = KW.goat("tied", HUTD["world"](1.9, -KW.HUT_D / 2 - 0.6), yaw=0.8, seed=2)
    KW.goat_graze(G, 0, D)
    rig, shake, cam, H = wife_cam(wife=WIFE2)
    crouch = (fp[0] + 0.55 * math.cos(HUTD["yaw"] + 0.3), fp[1] + 0.55 * math.sin(HUTD["yaw"] + 0.3), fp[2] + 0.95)
    crouch = HUTD["world"](-1.3, -KW.HUT_D / 2 - 0.45, 0.95)
    pose(H, 0, "lap")
    start = (-4.6, 14.0)
    Ib = prophet("ibrahim", (start[0], start[1], gz(*start)))
    MK.glide(Ib, [start, (0.5, 8.4), (3.5, 6.6)], ev("ibrahim_e9") - 1.6, speed=1.25)
    pot = (fp[0], fp[1], fp[2] + 0.5)
    Q.cam_keys(rig, [(0, crouch, look(crouch, pot)), (ev("ibrahim_e9") - 0.6, None, look(crouch, (pot[0], pot[1], pot[2] + 0.05))),
                     (ev("ibrahim_e9") + 0.6, None, look(crouch, (start[0] + 2.0, start[1] - 2.5, 1.7))),
                     (D, None, look(crouch, (2.6, 7.2, 1.3)))])
    Q.handheld(shake, 0, D, amp=0.3)
    return L


def wife2_scene():
    """Zweite Frau steht draußen vor der Tür, Ibrahim (Licht) vor ihr; Feuer mit Topf, Ziege.
    Zwischen ihnen auf einer Matte: Holztablett mit Schale Fleisch, Wasserkrug und Becher (sie bewirtet den Gast)."""
    L, spots, vl = KW.settle_world("morning", t1=D + 1, people=8, life_kids=False)
    make_hut()
    fp = HUTD["world"](-1.6, -KW.HUT_D / 2 - 1.2)
    KW.cook_fire("hfire", fp, energy=35.0, pot=True)
    G = KW.goat("tied", HUTD["world"](1.9, -KW.HUT_D / 2 - 0.6), yaw=0.8, seed=2)
    KW.goat_graze(G, 0, D)
    me = HUTD["world"](0.0, -KW.HUT_D / 2 - 0.55, EYE - 0.07)
    ib = HUTD["world"](0.15, -KW.HUT_D / 2 - 3.3)
    Ib = prophet("ibrahim", ib)
    MK.hold_at(Ib, 0)
    # Tablett auf einer Matte vor ihr (Welt), Schale + Krug + Becher
    tc = HUTD["world"](0.05, -KW.HUT_D / 2 - 1.45)
    z = gz(tc[0], tc[1])
    root = Q.empty("tray", (tc[0], tc[1], z), rot=(0, 0, HUTD["yaw"]))
    MK.rug("tray_mat", (0, 0, 0), (1.3, 0.9), rot=0.0, mat=MK.M["blanket_r"]).parent = root
    Q.cyl("tray_wood", (0, 0, 0.045), 0.42, 0.03, MK.M["wood"], seg=40, parent=root)
    Q.torus("tray_rim", (0, 0, 0.06), 0.42, 0.012, MK.M["wood"], parent=root, seg=40, rseg=6)
    KW.bowl("bowl", (-0.13, 0.04, 0.06), parent=root, seed=3, r=0.15)
    KW.jug("tjug", (0.2, 0.12, 0.06), parent=root, scale=0.62)
    KW.cup("cup", (0.17, -0.16, 0.06), parent=root)
    spots_ = {"bowl": HUTD["world"](-0.08, -KW.HUT_D / 2 - 1.41, 0.12), "cup": HUTD["world"](0.22, -KW.HUT_D / 2 - 1.27, 0.12),
              "tray": HUTD["world"](0.05, -KW.HUT_D / 2 - 1.45, 0.1)}
    spots_ = {k: (v[0], v[1], gz(v[0], v[1]) + 0.12) for k, v in spots_.items()}
    return L, me, ib, Ib, spots_


def shot_tuer2():
    """Sie empfängt ihn draußen: „Uns geht es gut …“ – „Was esst ihr?“ – „Fleisch.“ (Blick zur Schale) – „… trinkt ihr?“ – „Wasser.“
    (Blick zu Krug und Becher) – „O Allah, segne ihnen das Fleisch und das Wasser“: goldene Lichtpunkte steigen vom Tablett auf."""
    L, me, ib, Ib, sp = wife2_scene()
    rig, shake, cam, H = wife_cam(wife=WIFE2)
    pose(H, 0, "hidden")
    ibz = (ib[0], ib[1], gz(ib[0], ib[1]) + 1.25)
    tb = ev("fleisch_f4")
    tw = ev("wasser_f5")
    tsg = ev("segne_q5")
    glow_pulse(Ib, tsg, peak=1.8)
    Q.cam_keys(rig, [(0, me, look(me, ibz)), (ls("q3") + 0.3, None, look(me, (ibz[0], ibz[1], ibz[2] - 0.15))),
                     (tb - 0.2, None, look(me, sp["bowl"])), (le("q4") - 0.2, None, look(me, (sp["bowl"][0], sp["bowl"][1], sp["bowl"][2] + 0.05))),
                     (tw - 0.1, None, look(me, sp["cup"])), (tsg - 0.5, None, look(me, (ibz[0], ibz[1], ibz[2] - 0.2))),
                     (tsg + 1.4, None, look(me, (ibz[0], ibz[1], ibz[2] - 0.5))), (D, None, look(me, sp["tray"]))])
    Q.handheld(shake, 0, D, amp=0.3)
    motes_burst("bless", sp["tray"], tsg + 0.2, n=70, radius=0.4, rise_h=1.3, dur=D - tsg + 4.0, seed=4)
    return L


def shot_segen():
    """Nah: Tablett mit Fleisch und Wasser, goldene Lichtpunkte (Segen). Dann „Grüß deinen Mann … die Schwelle … festhalten“:
    Blick zu Ibrahim, dann zum Haus, auf die Schwelle."""
    L, me, ib, Ib, sp = wife2_scene()
    rig, shake, cam, H = wife_cam(wife=WIFE2)
    pose(H, 0, "hidden")
    motes_burst("bless", sp["tray"], 0.0, n=100, radius=0.4, rise_h=1.2, dur=9.0, seed=5)
    ibz = (ib[0], ib[1], gz(ib[0], ib[1]) + 1.25)
    tq7 = ls("q7")
    tsw = ev("schwelle_q7")
    th = threshold_pt()
    tr = sp["tray"]
    Q.cam_keys(rig, [(0, me, look(me, tr)), (4.2, None, look(me, (tr[0], tr[1], tr[2] + 0.15))),
                     (tq7 - 0.4, None, look(me, (ibz[0], ibz[1], ibz[2] - 0.6))), (tq7 + 0.6, None, look(me, ibz)),
                     (tsw - 0.7, None, look(me, (ibz[0], ibz[1], ibz[2] - 0.2))), (tsw + 0.5, None, look(me, th)),
                     (D, None, look(me, (th[0], th[1], th[2] - 0.02)))])
    Q.handheld(shake, 0, D, amp=0.3)
    glow_pulse(Ib, ev("festhalten_q7"), peak=1.6)
    return L


def shot_abend2():
    """Abend: Ismail (Licht) an der Tür, Lampe drinnen. „… und die Schwelle … bist du. Behalte dich.“ – Blick auf die Schwelle, dann zu ihm."""
    L, spots, vl = KW.settle_world("dusk", stars=1.8, t1=D + 1, people=6, goats=False)
    make_hut(lamp=True)
    Q.flicker(HUTD["lamp"]["light"], 0, D, 30.0)
    rig, shake, cam, H = wife_cam(wife=WIFE2)
    stand = HUTD["world"](0.1, -0.35, EYE - 0.05)
    fr = HUTD["world"](0.1, -KW.HUT_D / 2 - 1.3)
    st = HUTD["world"](2.6, -KW.HUT_D / 2 - 4.0)
    Is = prophet("ismail", (st[0], st[1], gz(st[0], st[1])), strength=0.85, day=False)
    MK.glide(Is, [(st[0], st[1]), (fr[0], fr[1])], 0.0, speed=1.35)
    pose(H, 0, "lap")
    isz = (fr[0], fr[1], gz(fr[0], fr[1]) + 1.3)
    tsw = ev("schwelle_q8")
    th = threshold_pt()
    glow_pulse(Is, ev("dich_q8") - 0.3, peak=1.9)
    Q.cam_keys(rig, [(0, stand, look(stand, (isz[0] + 1.0, isz[1] - 1.5, isz[2]))), (2.4, None, look(stand, isz)),
                     (tsw - 0.3, None, look(stand, (isz[0], isz[1], isz[2] - 0.2))), (tsw + 0.6, None, look(stand, th)),
                     (ev("dich_q8") - 1.2, None, look(stand, (th[0], th[1], th[2] + 0.05))), (ev("dich_q8") - 0.2, None, look(stand, isz)),
                     (D, None, look(stand, (isz[0], isz[1], isz[2] + 0.1)))])
    Q.handheld(shake, 0, D, amp=0.3)
    return L


ISP = (TREE.x + 0.9, TREE.y + 0.9)          # Ismail sitzt unter dem Baum
MEET_S = (ISP[0], ISP[1] + 1.0)               # hier steht Ismail beim Gespräch
MEET_I = (ISP[0] - 0.15, ISP[1] + 1.95)       # hier steht Ibrahim
MEET = ((MEET_S[0] + MEET_I[0]) / 2, (MEET_S[1] + MEET_I[1]) / 2)


def tree_scene(mode="day"):
    L, spots, vl = KW.settle_world(mode, t1=D + 1, people=10, extra_keep=[(TREE.x, TREE.y, 6.0)],
                                   tent_avoid=[(ISP[0] + 6.0, ISP[1] + 2.4, 5.0), (ISP[0] + 3.5, ISP[1] + 1.5, 4.0)])
    make_hut()
    isp = ISP
    cz = gz(*isp)
    MK.rug("arug", (isp[0] + 0.75, isp[1] - 0.2, cz), (1.0, 1.2), rot=0.3, mat=MK.M["blanket_b"])
    for k in range(7):
        KW.arrow(f"arr{k}", (isp[0] + 0.5 + 0.07 * k, isp[1] - 0.45 + 0.03 * k, cz + 0.035), rot=(0, 0, 0.2 + 0.05 * k), done=k < 5)
    KW.bow("abow", (TREE.x + 0.35, TREE.y + 0.35, cz + 0.62), rot=(math.radians(80), 0, math.radians(30)))
    rnd = random.Random(3)
    for k in range(30):  # Holzspäne
        Q.ball(f"shav{k}", (isp[0] + 0.45 + rnd.uniform(-0.3, 0.3), isp[1] + 0.3 + rnd.uniform(-0.3, 0.3), cz + 0.01),
               (0.012, 0.004, 0.003), KW.M["shaft"], seg=6).rotation_euler = (0, 0, rnd.uniform(0, 6.28))
    return L, isp


def shot_baum():
    """Ich-Sicht eines Jungen der Dschurhum: Ismail (Licht, sitzend) unter dem großen Baum nahe Zamzam, Pfeile auf der Decke.
    „… seinen Vater sieht“: Ibrahim (Licht) kommt; Ismail steht auf (Säule wächst); sie begrüßen sich (Lichter nah, leuchten auf)."""
    L, isp = tree_scene("day")
    Is = prophet("ismail", (isp[0], isp[1], gz(*isp)), height=2.15, strength=0.85)
    rise(Is, 0, 0.1, 1.3, 1.3)
    tst = ev("steht_e13")
    rise(Is, tst - 0.2, tst + 0.9, 1.3, 2.15)
    tv = ev("vater_e13")
    tb = ev("begrüßen_e13")
    t_go = 5.0
    dvec = Vector((-0.3, 1.0)).normalized() * (1.25 * (tb - 0.3 - t_go))
    start = (MEET_I[0] + dvec.x, MEET_I[1] + dvec.y)
    Ib = prophet("ibrahim", (start[0], start[1], gz(*start)))
    MK.hold_at(Ib, 0, start)
    MK.glide(Ib, [start, MEET_I], t_go, speed=1.25)
    MK.hold_at(Is, tst + 0.5, isp)
    MK.glide(Is, [isp, MEET_S], tst + 0.5, speed=0.85)
    meet = MEET

    def ib_at(t):  # wo Ibrahims Licht zur Zeit t ist (für den Blick)
        u = min(1.0, max(0.0, (t - t_go) * 1.25 / max(1e-6, dvec.length)))
        x, y = start[0] + (MEET_I[0] - start[0]) * u, start[1] + (MEET_I[1] - start[1]) * u
        return (x, y, gz(x, y) + 1.2)
    glow_pulse(Is, tb, peak=2.0)
    glow_pulse(Ib, tb, peak=2.0)
    rig, shake, cam = Q.pov_camera(lens=17)
    c0 = P(isp[0] + 6.8, isp[1] + 2.6, 1.35)
    c1 = P(isp[0] + 2.4, isp[1] + 0.9, 1.3)
    c2 = P(isp[0] + 4.6, isp[1] + 2.8, 1.4)
    arrows = (isp[0] + 0.75, isp[1] - 0.25, gz(*isp) + 0.05)
    mz = (meet[0], meet[1], gz(*meet) + 1.1)
    Q.cam_keys(rig, [(0, c0, look(c0, (TREE.x, TREE.y, 3.0))), (ev("ismail_e12") - 0.4, None, look(c0, (isp[0], isp[1], gz(*isp) + 0.7))),
                     (ev("zamzam_e12") - 0.4, None, look(c0, (SP.x, SP.y, 0.6))), (ev("pfeile_e12") - 0.6, c1, look(c1, arrows)),
                     (tv - 0.6, None, look(c1, (isp[0], isp[1], gz(*isp) + 0.6))), (tv + 0.5, None, look(c1, ib_at(tv + 0.5))),
                     (tst + 0.2, None, look(c1, (isp[0], isp[1], gz(*isp) + 1.1))), (tb - 0.3, c2, look(c2, mz)), (D, None, look(c2, mz))])
    Q.handheld(shake, 0, D, amp=0.5, walk_from=ev("pfeile_e12") - 2.0, walk_to=ev("pfeile_e12") - 0.6, walk_amp=0.6)
    return L


def shot_befehl():
    """Die beiden Lichter stehen sich unter dem Baum gegenüber (Gespräch). „… hier ein Haus zu bauen“: Blick wendet sich zum Hügel."""
    L, isp = tree_scene("day")
    meet = MEET
    Ib = prophet("ibrahim", (MEET_I[0], MEET_I[1], gz(*MEET_I)))
    Is = prophet("ismail", (MEET_S[0], MEET_S[1], gz(*MEET_S)), height=2.15, strength=0.85)
    MK.hold_at(Ib, 0)
    MK.hold_at(Is, 0)
    for q_, H_ in (("q9", Ib), ("q10", Is), ("q11", Ib), ("q12", Is), ("q13", Ib)):
        glow_pulse(H_, ls(q_) + 0.1, peak=1.35)
    th = ev("haus_q13")
    rig, shake, cam = Q.pov_camera(lens=17)
    mz = (meet[0], meet[1], gz(*meet) + 1.15)
    a0, a1 = 0.15, -0.35
    c = lambda a, r=4.6: (meet[0] + r * math.cos(a), meet[1] + r * math.sin(a), gz(*meet) + 1.35)  # noqa: E731
    hill = (HILL.x, HILL.y, 1.3)
    Q.cam_keys(rig, [(0, c(a0), look(c(a0), mz)), (th - 0.4, c(a1, 4.2), look(c(a1, 4.2), mz)), (D, c(a1 + 0.05, 4.1), look(c(a1 + 0.05, 4.1),
                     (mz[0] + (hill[0] - mz[0]) * 0.35, mz[1] + (hill[1] - mz[1]) * 0.35, 1.1)))])
    Q.handheld(shake, 0, D, amp=0.45)
    return L


def shot_huegel():
    """Blick zum Hügel. „Genau dort, wo der Engel es versprochen hatte“: goldene Umrisse eines Hauses (wie in Folge 2)."""
    L, isp = tree_scene("day")
    meet = MEET
    Ib = prophet("ibrahim", (MEET_I[0], MEET_I[1], gz(*MEET_I)))
    Is = prophet("ismail", (MEET_S[0], MEET_S[1], gz(*MEET_S)), height=2.15, strength=0.85)
    MK.hold_at(Ib, 0)
    MK.hold_at(Is, 0)
    MK.kaaba_ghost(ev("engel_e14") + 0.1, loc=HILL, size=(KW.KA_W + KW.KA_T, KW.KA_D + KW.KA_T, 4.6))
    rig, shake, cam = Q.pov_camera(lens=17)
    c = (meet[0] + 4.1 * math.cos(-0.3), meet[1] + 4.1 * math.sin(-0.3), gz(*meet) + 1.35)
    hill = (HILL.x, HILL.y, 1.6)
    mz = (meet[0], meet[1], gz(*meet) + 1.15)
    c2 = (c[0] - 0.6, c[1] - 1.4, c[2])
    Q.cam_keys(rig, [(0, c, look(c, (mz[0] + (hill[0] - mz[0]) * 0.35, mz[1] + (hill[1] - mz[1]) * 0.35, 1.1))),
                     (ev("hügel_e14") + 0.4, None, look(c, hill)), (D, c2, look(c2, (hill[0], hill[1], 2.6)))])
    Q.handheld(shake, 0, D, amp=0.45, walk_from=ev("hügel_e14"), walk_to=D, walk_amp=0.5)
    return L


def build_scene(mode="day", complete=False):
    L = MK.light(mode, stars=0.0)
    KW.mats()
    MK.valley(keep=[(KW.GRAVE.x, KW.GRAVE.y, 3.0), (SP.x, SP.y, 4.0), (HILL.x, HILL.y, 10.0)])
    KW.well()
    KW.grave()
    spots = KW.tents(12, seed=21, fire_lights=mode in ("dusk", "golden"))
    KW.villagers(spots, D + 1, n=6)
    # Steinhaufen (Ismail bringt Steine von hier)
    pile = Vector((HILL.x + 8.0, HILL.y - 3.0, 0))
    rnd = random.Random(2)
    for k in range(26):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(0, 1.3)
        x, y = pile.x + r * math.cos(a), pile.y + r * math.sin(a)
        Q.box(f"pile{k}", (x, y, gz(x, y) + 0.12 + 0.18 * (r < 0.6)), (rnd.uniform(0.4, 0.7), 0.6, 0.28), KW.M["granite"] if k % 2 else KW.M["granite2"],
              rot=(rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), rnd.uniform(0, 3.1)), bevel=0.03, jitter=0.03, seed=k)
    return L, pile


def shot_bau():
    """Der Bau: Ismail (Licht) bringt Steine, Ibrahim (Licht) setzt sie – Lage für Lage, im Zeitraffer wachsen die Mauern.
    „Da bringt Ismail einen großen Stein“: der Maqam-Stein; „… stellt sich darauf“: Ibrahims Licht steht höher und baut weiter."""
    L, pile = build_scene("day")
    tm = ev("mauern_e16")
    ts = ev("stein_e16")
    td = ev("darauf_e16")
    n_ch = 12

    def t_of(c, k, n):
        if c == 0:
            return 0.4 + k * 0.42          # erste Lage: Stück für Stück (e15)
        if c == 1:
            return 5.5 + k * 0.03
        if c <= 9:
            return tm + 0.3 + (c - 2 + k / n) * (ts - 1.6 - tm) / 8.0
        return td + 0.7 + (c - 10 + k / n) * (D - 0.2 - td - 0.7) / 5.0
    KW.walls(t_of=t_of)
    # Lichter: Ibrahim baut entlang der Mauer (Umfang), Ismail pendelt mit Steinen zwischen Haufen und Mauer
    Ib = prophet("ibrahim", (0, 0, 0))
    Is = prophet("ismail", (pile.x, pile.y, gz(pile.x, pile.y)), height=2.15, strength=0.85)
    carried = Q.box("carry", (0, -0.55, 1.05), (0.5, 0.36, 0.26), KW.M["granite2"], parent=Is["root"], bevel=0.03, jitter=0.02, seed=4)
    zfun = lambda x, y: KW.hillock_z(x, y)  # noqa: E731
    U_ST = 2.73
    sx, sy = KW.side_point(U_ST, out=0.5)
    for f in range(1, Q.T(D) + 2, 2):
        t = (f - 1) / Q.FPS
        if t < tm:
            u = 0.13 * (t / tm)
        elif t < ts - 1.6:
            u = 0.13 + (t - tm) / (ts - 1.6 - tm) * (U_ST - 0.13)
        else:
            u = U_ST
        x, y = KW.side_point(u, out=0.75 if t < td - 0.3 else 0.5)
        if t >= td - 0.3:
            x, y = sx, sy
        add = smooth(td - 0.3, td + 0.5, t) * 0.48
        Ib["root"].location = (x, y, zfun(x, y) + add)
        Ib["root"].keyframe_insert("location", frame=f)
    # Ismail: Hin und Her (echte Zeit bis tm, dann schneller im Zeitraffer) – IMMER außen um die Mauern herum (nie hindurch)
    OUT_W = 1.5
    a = (pile.x - 0.8, pile.y - 0.6)
    u_pile = min((k_ / 400.0 for k_ in range(400)), key=lambda u: math.dist(KW.side_point(u, out=OUT_W), a))

    def around(u0, u1, out=OUT_W):
        """Punkte entlang des Umfangs von u0 nach u1 (kürzerer Weg)."""
        du = ((u1 - u0 + 0.5) % 1.0) - 0.5
        n = max(1, int(abs(du) * 40))
        return [KW.side_point(u0 + du * j / n, out=out) for j in range(n + 1)]
    t = 0.0
    k = 0
    while t < D:
        spd = 1.3 if t < tm else 4.5
        u_tgt = (0.06 + 0.04 * k) if t < tm else 0.13 + (t - tm) / max(1.0, ts - 1.6 - tm) * 2.6
        if tm < t < td + 0.7 and t > ts - 2.0:
            u_tgt = U_ST + 0.05
        u_tgt %= 1.0
        wx, wy = KW.side_point(u_tgt, out=0.6)
        go = [a] + around(u_pile, u_tgt) + [(wx, wy)]
        t = MK.glide(Is, go, t, speed=spd)
        t = MK.glide(Is, list(reversed(go)), t + 0.25, speed=spd) + 0.2
        k += 1
    # Maqam-Stein: Ismail bringt ihn (erscheint), Ibrahim steht darauf
    St = KW.maqam_stone("maqam", (sx, sy, KW.hillock_z(sx, sy) - 0.02), t_on=ts + 0.2)
    # Sonne wandert im Zeitraffer (Schatten ziehen)
    sun = bpy.data.objects.get("sun")
    if sun:
        r0 = sun.rotation_euler.copy()
        sun.keyframe_insert("rotation_euler", frame=max(1, Q.T(tm)))
        sun.rotation_euler = (r0.x + math.radians(8), r0.y, r0.z + math.radians(-35))
        sun.keyframe_insert("rotation_euler", frame=Q.T(D))
    rig, shake, cam = Q.pov_camera(lens=17)
    c0 = P(HILL.x + 9.5, HILL.y + 9.0, 1.4)
    c1 = P(HILL.x + 11.0, HILL.y + 5.5, 1.4)
    tgt0 = (HILL.x + 2.2, HILL.y + 2.0, 1.0)
    tgt1 = (HILL.x, HILL.y, 2.6)
    st = (sx, sy, KW.hillock_z(sx, sy) + 1.0)
    Q.cam_keys(rig, [(0, c0, look(c0, (pile.x - 0.4, pile.y - 0.3, 0.9))), (ev("ibrahim_e15") - 0.3, None, look(c0, tgt0)),
                     (tm, None, look(c0, (HILL.x + 0.5, HILL.y + 0.5, 1.6))), (ts - 0.8, c1, look(c1, tgt1)),
                     (ts + 0.4, None, look(c1, st)), (td + 1.0, None, look(c1, (st[0], st[1], st[2] + 0.6))), (D, None, look(c1, tgt1))])
    Q.handheld(shake, 0, D, amp=0.45, walk_from=tm, walk_to=ts - 0.8, walk_amp=0.5)
    return L


def shot_gebet():
    """Goldene Stunde: die Mauern stehen. Ibrahim und Ismail (Licht) gehen um das Haus und beten (Koran 2:127). Kamera steigt."""
    L, pile = build_scene("golden")
    KW.walls(built_to=KW.N_COURSES)
    sx, sy = KW.side_point(2.73, out=0.5)
    KW.maqam_stone("maqam", (sx, sy, KW.hillock_z(sx, sy) - 0.02))
    Ib = prophet("ibrahim", (0, 0, 0))
    Is = prophet("ismail", (0, 0, 0), height=2.15, strength=0.85)
    for f in range(1, Q.T(D) + 2, 2):
        t = (f - 1) / Q.FPS
        for H_, du in ((Ib, 0.0), (Is, -0.045)):
            x, y = KW.side_point(0.05 + du + t * 0.012, out=1.0)
            H_["root"].location = (x, y, KW.hillock_z(x, y))
            H_["root"].keyframe_insert("location", frame=f)
    glow_pulse(Ib, ls("q14") + 0.2, peak=1.7)
    glow_pulse(Is, ls("q15") + 0.2, peak=1.7)
    MD.dust("gdust", (HILL.x, HILL.y, 3.0), (14, 14, 6), n=500, seed=3, dur=D + 1, col=(1.0, 0.8, 0.5), strength=0.8)
    rig, shake, cam = Q.pov_camera(lens=17)
    c0 = P(HILL.x + 10.5, HILL.y + 7.0, 1.4)
    c1 = (HILL.x + 13.0, HILL.y - 7.0, gz(0, 0) + 9.0)
    Q.cam_keys(rig, [(0, c0, look(c0, (HILL.x, HILL.y, 2.6))), (D, c1, look(c1, (HILL.x, HILL.y, 1.8)))], interp="BEZIER")
    Q.handheld(shake, 0, D, amp=0.3)
    return L


# ---------------------------------------------------------------- heute
def today_world(t1, gap=None):
    Q.world_sky("night")
    KW.mataf()
    KW.kaaba_today()
    KW.maqam_today()
    rings = []
    for k, (r0, r1, n, sp) in enumerate(((8.5, 14, 1100, 7.0), (14, 21, 1500, 5.2), (21, 30, 1700, 3.8), (30, 42, 1700, 2.6))):
        g = gap if (gap and r0 >= 14 and r0 < 30) else None
        if g:
            sp = 0.6   # langsam, damit die Lücke (Betende) an ihrem Platz bleibt
        objs = KW.crowd_ring(f"cr{k}", r0, r1, n, seed=k, gap=g)
        KW.circle_crowd(objs, t1, sp)
        rings += objs
    return dict(mist_col=(0.05, 0.06, 0.1), mist_amt=0.15)


def shot_heute():
    """Nacht, heute: die Kaaba, rundherum gehen Pilger (gegen den Uhrzeigersinn). Blick vom oberen Umgang."""
    cfg = today_world(D + 1)
    rig, shake, cam = Q.pov_camera(lens=20)
    c0 = (40.0, -36.0, 15.5)
    c1 = (36.0, -39.5, 15.0)
    Q.cam_keys(rig, [(0, c0, look(c0, (0, 0, 6.0))), (D, c1, look(c1, (0, 0, 6.5)))], interp="BEZIER")
    Q.handheld(shake, 0, D, amp=0.25)
    return cfg


def shot_maqam():
    """Zum Maqam Ibrahim: goldene Glocke vor der Kaaba, Pilger gehen vorbei. „… die Abdrücke von zwei Füßen“: Blick durch das Glas."""
    cfg = today_world(D + 1, gap=(-90.0, 24.0))
    KW.tawaf_walkers(26, 9.5, 15.6, D + 1, seed=2, a_range=(-math.pi * 0.85, -math.pi * 0.15))
    rig, shake, cam = Q.pov_camera(lens=17)
    m = KW.MAQAM_T
    c0 = (m.x + 4.0, m.y - 7.5, 1.6)
    c1 = (m.x + 1.6, m.y - 2.6, 1.65)
    c2 = (m.x + 0.75, m.y - 1.15, 2.05)
    tm = ev("maqam_e19")
    tf = ls("e20")
    Q.cam_keys(rig, [(0, c0, look(c0, (0, 0, 8.0))), (tm - 1.5, None, look(c0, (0, 0, 5.0))), (tm + 0.6, c1, look(c1, (m.x, m.y, 1.4))),
                     (tf + 1.2, None, look(c1, (m.x, m.y, 1.1))), (tf + 3.0, c2, look(c2, (m.x, m.y, 1.05))), (D, None, look(c2, (m.x, m.y, 1.05)))])
    Q.handheld(shake, 0, D, amp=0.3, walk_from=0, walk_to=tf + 3.0, walk_amp=0.6)
    return cfg


def shot_ende():
    """Pilger beten hinter dem Maqam (Reihen, Blick zur Kaaba); Kamera steigt auf: der ganze Platz, Pilger umrunden die Kaaba."""
    cfg = today_world(D + 1, gap=(-90.0, 24.0))
    KW.tawaf_walkers(18, 9.5, 15.6, D + 1, seed=5, a_range=(-math.pi * 0.8, -math.pi * 0.2))
    m = KW.MAQAM_T
    rnd = random.Random(4)
    k = 0
    for row in range(4):
        for j in range(11):
            x = m.x - 5.0 + j * 1.0 + rnd.uniform(-0.1, 0.1)
            y = m.y - 2.6 - row * 1.25
            if abs(x - m.x) < 1.3 and row == 0:
                continue
            woman = row >= 2 and j % 3 == 0
            Pp = MK.pilgrim(f"pr{k}", (x, y, 0), yaw=Q.face_yaw((x, y), (0, 0)), seed=700 + k, woman=woman)
            for s_ in ("L", "R"):
                Q.arm_pose(Pp, 0, s_, -40, -100, sh_y=(20 if s_ == "L" else -20))
            Pp["head"].rotation_euler = (math.radians(14), 0, 0)
            k += 1
    rig, shake, cam = Q.pov_camera(lens=17)
    c0 = (m.x + 0.6, m.y - 7.8, 1.6)
    c1 = (m.x + 9.0, m.y - 24.0, 26.0)
    Q.cam_keys(rig, [(0, c0, look(c0, (m.x, m.y, 1.4))), (3.2, None, look(c0, (0, 0, 5.0))), (D, c1, look(c1, (0, 0, 2.0)))], interp="BEZIER")
    Q.handheld(shake, 0, D, amp=0.25)
    return cfg


SHOTS = {"zelte": shot_zelte, "ismail": shot_ismail, "grab": shot_grab, "ankunft": shot_ankunft, "tuer1": shot_tuer1, "abend1": shot_abend1,
         "besuch2": shot_besuch2, "tuer2": shot_tuer2, "segen": shot_segen, "abend2": shot_abend2, "baum": shot_baum, "befehl": shot_befehl,
         "huegel": shot_huegel, "bau": shot_bau, "gebet": shot_gebet, "heute": shot_heute, "maqam": shot_maqam, "ende": shot_ende}

def join_noshadow(prefixes=("peb", "sb", "tree_far"), small_rocks=0.55):
    """Kleinkram (Kiesel, Büsche, ferne Bäume, kleine Steine) wirft keinen Schatten und wird zu EINEM Objekt verschmolzen:
    auf dem Rechner ohne Grafikkarte kostet jedes Dreieck im Schatten-Durchgang (je Sample) Zeit."""
    objs = []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.animation_data or (o.parent and o.parent.animation_data):
            continue
        top = o
        while top.parent is not None:
            top = top.parent
        if top.get("person") or top.animation_data:
            continue
        nm = o.name
        if nm.startswith(prefixes) or (nm.startswith("rk") and max(o.scale) < small_rocks):
            objs.append(o)
    if len(objs) < 2:
        return
    for o in bpy.data.objects:
        o.select_set(False)
    with bpy.context.temp_override(selected_objects=objs, selected_editable_objects=objs, active_object=objs[0], object=objs[0]):
        bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
        bpy.ops.object.make_single_user(object=True, obdata=True)
        bpy.ops.object.convert(target="MESH")
        bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active or objs[0]
    o.name = "noshadow_static"
    o.visible_shadow = False
    print("join_noshadow:", len(objs))


Q.reset()
cfg = SHOTS[SHOT]()
MK.no_glow_shadows()
if os.environ.get("NOSH", "1") == "1":
    join_noshadow()
if os.environ.get("JOIN", "1") == "1":
    MD.join_static(keep=("ibrahim", "ismail", "ka_", "maqam", "kaaba_ghost", "ghost", "cm", "vl", "man", "pl", "pcm", "kid",
                         "bride", "bmother", "wellw", "tied", "pov", "mend", "spoon", "bowl", "cup", "bless", "potmeat", "cr", "tw", "pr",
                         "hut_hinge", "hut_lamp", "carry", "gdust", "noshadow"))
SHADOW_HI = set()
TODAY = SHOT in ("heute", "maqam", "ende")
Q.render_setup(pct=PCT, samples=SAMPLES, mist_col=cfg["mist_col"], mist_amt=cfg["mist_amt"], shadow_res=1.0 if SHOT in SHADOW_HI else 0.5,
               sky_sep=not TODAY)
sc = bpy.context.scene
if os.environ.get("LIST"):
    for o in bpy.data.objects:
        if o.name.startswith(os.environ["LIST"]):
            print("OBJ", o.name, o.type, tuple(round(v, 3) for v in o.matrix_world.translation), o.parent.name if o.parent else None)
    sys.exit(0)
for o in bpy.data.objects:
    if o.type == "CAMERA":
        o.data.clip_end = 900
if os.environ.get("NOCOMP"):
    sc.render.use_compositing = False
if os.environ.get("BENCH_SHADOW"):
    sc.eevee.shadow_resolution_scale = float(os.environ["BENCH_SHADOW"])
if os.environ.get("BENCH_DETAIL"):  # Rauschen mit weniger Oktaven (schneller)
    cap = float(os.environ["BENCH_DETAIL"])
    for m in bpy.data.materials:
        if m.node_tree:
            for n in m.node_tree.nodes:
                if n.type == "TEX_NOISE":
                    n.inputs["Detail"].default_value = min(n.inputs["Detail"].default_value, cap)
sc.frame_start, sc.frame_end = 1, SEG[SHOT]["frames"]
if os.environ.get("FRAMES"):
    sc.frame_start, sc.frame_end = map(int, os.environ["FRAMES"].split("-"))
import time as _time
print("SETUP_DONE", _time.time())
if os.environ.get("KIDS_CHECK"):  # Test: in welchen Bildern sind rennende Kinder zu sehen?
    from bpy_extras.object_utils import world_to_camera_view
    kids = [o for o in bpy.data.objects if o.name.startswith("kid") and o.name.endswith("_root")]
    camo = sc.camera
    vis = []
    for f in range(1, SEG[SHOT]["frames"] + 1, 2):
        sc.frame_set(f)
        for o in kids:
            for dz in (0.3, 0.9):
                co = o.matrix_world.translation + Vector((0, 0, dz))
                v = world_to_camera_view(sc, camo, co)
                if -0.05 < v.x < 1.05 and -0.05 < v.y < 1.05 and 0 < v.z < 70:
                    vis.append((f, o.name, round(v.z, 1)))
                    break
    fr = sorted(set(f for f, _, _ in vis))
    print("KIDS_VISIBLE", SHOT, len(fr), (fr[0], fr[-1]) if fr else None, sorted(set(n for _, n, _ in vis)), min((d for _, _, d in vis), default=None))
    sys.exit(0)
if os.environ.get("TRIS"):
    import re as _re
    dg = bpy.context.evaluated_depsgraph_get()
    cnt = {}
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        k = _re.split(r"[_.0-9]", o.name)[0]
        ev_ = o.evaluated_get(dg)
        n = sum(len(pg.vertices) - 2 for pg in ev_.data.polygons)
        cnt[k] = cnt.get(k, 0) + n
    for k, v in sorted(cnt.items(), key=lambda x: -x[1])[:25]:
        print("TRIS", k, v)
    print("TRIS_TOTAL", sum(cnt.values()))
    sys.exit(0)
if os.environ.get("BENCH"):
    print("OBJECTS", len(bpy.data.objects), "MESH", sum(1 for o in bpy.data.objects if o.type == "MESH"),
          "LIGHTS", sum(1 for o in bpy.data.objects if o.type == "LIGHT"),
          "ANIM", sum(1 for o in bpy.data.objects if o.animation_data))
    for f in (100, 101, 102):
        t0 = _time.time(); sc.frame_set(f); print("FRAMESET", f, round(_time.time() - t0, 2))
    sc.render.resolution_percentage = int(os.environ.get("BENCH_PCT", "10"))
    for f in (100, 101, 102):
        sc.frame_set(f)
        t0 = _time.time(); sc.render.filepath = os.path.join(OUT, f"b{f}.png"); bpy.ops.render.render(write_still=True)
        print("RENDER10", f, round(_time.time() - t0, 2))
    sc.render.use_compositing = False
    for f in (103, 104):
        sc.frame_set(f)
        t0 = _time.time(); bpy.ops.render.render(write_still=False)
        print("RENDER_NOCOMP", f, round(_time.time() - t0, 2))
    sc.render.use_compositing = True
    for m in bpy.data.materials:
        if m.node_tree:
            for n in m.node_tree.nodes:
                if n.type == "TEX_NOISE":
                    n.inputs["Detail"].default_value = min(n.inputs["Detail"].default_value, 2.0)
    for f in (105, 106):
        sc.frame_set(f)
        t0 = _time.time(); bpy.ops.render.render(write_still=False)
        print("RENDER_DETAIL2", f, round(_time.time() - t0, 2))
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
