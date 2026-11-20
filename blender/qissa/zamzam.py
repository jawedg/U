# QISSAH Folge 2 – „Der Ursprung von Zamzam“: alle Einstellungen in Blender (Ich-Sicht Hadschar, Tal von Mekka; Mas'a heute).
# Aufruf:  blender -b --factory-startup --python blender/qissa/zamzam.py -- <einstellung> <ausgabe_ordner> [prozent] [samples] [standbild-zeiten]
# Längen und Ereignisse: src/qissa_zamzam/timeline.json (scripts/build_qissa_zamzam.py).
# Regeln: Ibrahim und Ismail (Propheten) und der Engel NUR als Licht; Menschen ohne Gesicht; Hadschar mit Licht über dem Kopf.
import bpy, sys, os, math, json, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import lib as Q
import medina as MD
import mekka as MK

TL = json.load(open(os.path.join(ROOT, "src", "qissa_zamzam", "timeline.json"), encoding="utf-8"))
SEG = {s["id"]: s for s in TL["segments"]}
LINE = {l["id"]: l for l in TL["lines"]}
EV = TL["events"]
Q.FPS = TL.get("render_fps", 30)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SHOT = argv[0] if argv else "tal"
OUT = argv[1] if len(argv) > 1 else "/tmp/zamzam"
PCT = int(argv[2]) if len(argv) > 2 else 50
SAMPLES = int(argv[3]) if len(argv) > 3 else 8
STILLS = [float(x) for x in argv[4].split(",")] if len(argv) > 4 and argv[4] else None

S0 = SEG[SHOT]["start"]
D = SEG[SHOT]["dur"]
EYE = 1.55
gz = MK.ground_z


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


def path_point(pts, s):
    """Punkt bei Weglänge s auf dem Polygonzug pts (vor dem Anfang: rückwärts verlängert)."""
    pts = [Vector((p[0], p[1])) for p in pts]
    if s <= 0:
        d = (pts[1] - pts[0]).normalized()
        return pts[0] + d * s
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        L_ = (b - a).length
        if s <= acc + L_:
            return a + (b - a) * ((s - acc) / L_)
        acc += L_
    return pts[-1]


def carried_bundle(cam):
    """Baby-Bündel in den Armen (Kind der Kamera): quer vor der Brust, Kopfende (Licht) links oben, Oberseite zur Kamera."""
    from mathutils import Matrix
    y = Vector((1.0, -0.12, 0.25)).normalized()      # Fußende nach rechts (Kopf = -Y nach links)
    z = Vector((0.0, 0.55, 0.83)).normalized()       # Oberseite schaut nach oben/zur Kamera
    y = (y - y.dot(z) * z).normalized()
    x = y.cross(z)
    rot = Matrix((x, y, z)).transposed().to_euler()
    B = MK.bundle("baby_c", (0.07, -0.46, -0.62), parent=cam, rot=tuple(rot), light=0.8, scale=0.64)
    return B


# ============================================================ Einstellungen
def shot_tal():
    """Ankunft im leeren Tal: Ich-Sicht (Hadschar) mit dem Baby im Arm, Ibrahims Licht geht voraus zur Akazie."""
    L = MK.light("day")
    MK.valley(keep=[(-1.0, 0.0, 3.0)])
    MK.waterskin("skin", (BABY.x + 0.75, BABY.y - 0.55, gz(BABY.x, BABY.y) + 0.02), full=True, rot=1.2)
    MK.dates_bag("dates", (BABY.x - 0.85, BABY.y - 0.45, gz(BABY.x, BABY.y) + 0.02))
    rig, shake, cam = Q.pov_camera(lens=17)
    H = MK.pov_arms(cam)
    MK.pose_hands(H, 0, "carry")
    MK.hand_bob(H, 0, 15.5, amp=0.012, hz=1.8)
    carried_bundle(cam)
    Ib = MK.prophet_light("ibrahim", (-2.0, 5.2, gz(-2.0, 5.2)))
    t_arr = MK.glide(Ib, [(-2.0, 5.2), (2.5, -3.0), (7.2, -9.4)], 0.0, speed=1.18)
    MK.hold_at(Ib, D)
    Q.animate_motes(Ib, 1, Q.T(D))
    A, B = Vector((-3.5, 7.6)), Vector((3.3, -8.0))
    keys = []
    for k in range(9):
        u = k / 8
        e = u * u * (3 - 2 * u) * 0.25 + u * 0.75
        p = A + (B - A) * e
        keys.append((15.2 * u, P(p.x, p.y), None))
    keys.append((D, P(B.x + 0.1, B.y - 0.15), None))
    Q.cam_keys(rig, keys, loc_interp="BEZIER")

    def at(t):
        u = min(1.0, t / 15.2)
        e = u * u * (3 - 2 * u) * 0.25 + u * 0.75
        p = A + (B - A) * e
        return P(p.x, p.y)

    def ib(t):
        return MK.path_pos if False else None
    skin_pt = (BABY.x + 0.75, BABY.y - 0.55, 0.1)
    rot = [(0.0, look(at(0), (90, 5, 18))), (2.8, look(at(2.8), (60, -60, 14))), (5.2, look(at(5.2), (10, -40, 3))),
           (7.4, look(at(7.4), (at(7.4)[0] + 0.6, at(7.4)[1] - 3.2, gz(0, 0) - 0.2))),
           (9.6, look(at(9.6), (1.0, -1.5, 1.4))), (ev("baby_e2") - 0.9, look(at(ev("baby_e2") - 0.9), (5.5, -7.0, 1.3))),
           (ev("baby_e2") - 0.1, (Q.yaw_to(at(ev("baby_e2")), (5.5, -7.0)) + 4, -46, 0)),
           (ev("baby_e2") + 1.3, (Q.yaw_to(at(ev("baby_e2") + 1.3), (5.5, -7.0)) + 4, -48, 0)), (15.6, look(at(15.6), (7.2, -9.4, 1.2))),
           (16.9, look(at(16.9), (BABY.x - 0.85, BABY.y - 0.45, 0.1))), (18.4, look(at(18.4), skin_pt)), (D, look(at(D), skin_pt))]
    Q.cam_keys(rig, [(t, None, a) for t, a in rot])
    Q.handheld(shake, 0, D, amp=0.6, walk_from=0, walk_to=15.2, walk_amp=0.55)
    return L


BABY = MK.BABY


def shot_abschied():
    """Ibrahim dreht sich um und geht (Licht entfernt sich nach Norden), Hadschar legt das Baby ab und läuft ihm nach."""
    L = MK.light("day")
    MK.valley()
    Bb, ws, db = MK.camp_under_tree(full_skin=True)
    rig, shake, cam = Q.pov_camera(lens=17)
    H = MK.pov_arms(cam)
    MK.pose_hands(H, 0, "low")
    MK.pose_hands(H, 1.2, "low")
    MK.pose_hands(H, 2.2, "hidden")
    path = [(6.4, -9.0), (2.5, 0.0), (-3.0, 10.0), (-8.5, 22.0), (-12.0, 34.0), (-16.0, 50.0), (-18.0, 64.0), (MK.PASS.x, MK.PASS.y)]
    Ib = MK.prophet_light("ibrahim", (6.4, -9.0, gz(6.4, -9.0)))
    tg = ev("geht_e3") - 0.3
    sp = 1.6
    MK.hold_at(Ib, 0)
    MK.hold_at(Ib, tg)
    MK.glide(Ib, path, tg, speed=sp)
    Q.animate_motes(Ib, 1, Q.T(D))
    stand = Vector((4.3, -11.0))
    keys, rots = [], []
    for k in range(0, int(D * 10) + 1):
        t = k / 10
        sL = max(0.0, sp * (t - tg))
        s_cam = min(sL - 2.1, 2.5 * (t - 5.0) - 1.4) if t > 5.0 else -1.4
        pp = path_point(path, s_cam)
        w = smooth(4.6, 7.2, t)
        pos = stand.lerp(pp, w)
        eye = 0.85 + (EYE - 0.85) * smooth(1.6, 2.9, t)
        cpos = (pos.x, pos.y, gz(pos.x, pos.y) + eye)
        lp = path_point(path, sL)
        tgt = (lp.x, lp.y, gz(lp.x, lp.y) + 1.3)
        # Blick ruhig vom Baby hoch zum Licht (Nutzer: Kopf schwang bei 0:36 plötzlich nach links)
        bt = (BABY.x, BABY.y, gz(BABY.x, BABY.y) + 0.1)
        wb = smooth(1.3, 3.7, t)
        tgt = tuple(bt[i] + (tgt[i] - bt[i]) * wb for i in range(3))
        keys.append((t, cpos, None))
        if k % 3 == 0:
            rots.append((t, look(cpos, tgt)))
    Q.cam_keys(rig, keys, loc_interp="LINEAR")
    Q.cam_keys(rig, [(t, None, a) for t, a in rots])
    MK.pose_hands(H, ls("q1") - 0.4, "hidden", only="R")
    MK.pose_hands(H, ls("q1") + 0.3, "reach", only="R")
    MK.pose_hands(H, le("q1") - 1.5, "reach", only="R")
    MK.pose_hands(H, le("q1") + 0.2, "hidden", only="R")
    Q.handheld(shake, 0, D, amp=0.9, walk_from=5.0, walk_to=D, walk_amp=1.6)
    return L


def shot_frage():
    """„Hat Allah dir das befohlen?“ – „Ja.“ Das Licht bleibt kurz stehen, leuchtet auf und geht weiter zum Pass."""
    L = MK.light("day")
    MK.valley()
    rig, shake, cam = Q.pov_camera(lens=17)
    H = MK.pov_arms(cam)
    MK.pose_hands(H, 0, "hidden")
    path = [(-4.6, 13.2), (-8.5, 22.0), (-12.0, 34.0), (-16.0, 50.0), (-18.0, 64.0), (MK.PASS.x, MK.PASS.y)]
    Ib = MK.prophet_light("ibrahim", (-4.6, 13.2, gz(-4.6, 13.2)))
    Q.animate_motes(Ib, 1, Q.T(D))
    t_stop, t_go = ls("q2") + 2.4, ls("q3") + 0.9
    v1, v2 = 1.05, 1.45
    s_stop = v1 * t_stop

    def sL(t):
        if t <= t_stop:
            return v1 * t
        if t <= t_go:
            return s_stop
        return s_stop + v2 * (t - t_go)
    for k in range(0, int(D * 10) + 1, 2):
        t = k / 10
        pp = path_point(path, sL(t))
        Ib["root"].location = (pp.x, pp.y, gz(pp.x, pp.y))
        Ib["root"].keyframe_insert("location", frame=Q.T(t))
    MK.pulse(Ib["parts"][2].active_material, ev("ja_e5"), 25.0, 70.0, up=0.3, down=1.6)
    MK.pulse(Ib["parts"][1].active_material, ev("ja_e5"), 9.0, 22.0, up=0.3, down=1.6)
    t_halt = ls("q3")
    keys, rots = [], []
    for k in range(0, int(D * 10) + 1):
        t = k / 10
        gap = 2.7 - 0.9 * smooth(ls("q2") - 0.5, t_stop, t)
        sc = sL(min(t, t_halt)) - gap if t <= t_halt else sL(t_halt) - gap
        pp = path_point(path, sc)
        side = Vector((0.55, 0.0))
        cpos = (pp.x + side.x, pp.y, gz(pp.x, pp.y) + EYE)
        lp = path_point(path, sL(t))
        tgt = (lp.x, lp.y, gz(lp.x, lp.y) + 1.3)
        keys.append((t, cpos, None))
        if k % 3 == 0:
            a = look(cpos, tgt)
            back = look(cpos, (MK.TREE.x, MK.TREE.y, 2.0))
            w = smooth(D - 1.6, D, t)
            a = (a[0] + ((back[0] - a[0] + 180) % 360 - 180) * w, a[1] * (1 - w) + back[1] * w, 0)
            rots.append((t, a))
    Q.cam_keys(rig, keys, loc_interp="LINEAR")
    Q.cam_keys(rig, [(t, None, a) for t, a in rots])
    MK.pose_hands(H, ls("q2") - 0.3, "hidden", only="R")
    MK.pose_hands(H, ls("q2") + 0.3, "reach", only="R")
    MK.pose_hands(H, ls("q2") + 2.6, "reach", only="R")
    MK.pose_hands(H, ls("q2") + 3.4, "hidden", only="R")
    Q.handheld(shake, 0, D, amp=0.7, walk_from=0, walk_to=t_halt, walk_amp=0.8)
    return L


def shot_durst():
    """Mittagshitze: der Wasserschlauch ist leer, die Sonne brennt durch die Akazie, das Baby (Licht) windet sich."""
    L = MK.light("noon")
    MK.valley()
    Bb, ws, db = MK.camp_under_tree(full_skin=False)
    MK.wiggle(Bb["root"], 0, D, amp=7.0, hz=1.6, seed=2)
    MK.pulse(Bb["core"].active_material, ev("baby_e6") - 0.2, 11.2, 18.0, up=0.4, down=2.5)
    rig, shake, cam = Q.pov_camera(lens=17)
    H = MK.pov_arms(cam)
    cpos = P(4.15, -11.35, 0.92)
    skin = (BABY.x + 0.75, BABY.y - 0.55, gz(BABY.x, BABY.y) + 0.06)
    baby = (BABY.x, BABY.y, gz(BABY.x, BABY.y) + 0.1)
    sd = MK.sun_dir(MK.LIGHT["noon"][0])
    sunpt = tuple(Vector(cpos) + sd * 10)
    Q.cam_keys(rig, [(0, cpos, None), (D, (cpos[0] + 0.25, cpos[1] - 0.45, cpos[2] - 0.1), None)])
    Q.cam_keys(rig, [(0, None, look(cpos, (skin[0] - 0.5, skin[1] + 0.2, skin[2]))), (ev("wasser_e6") + 0.2, None, look(cpos, skin)),
                     (ev("sonne_e6") - 0.35, None, look(cpos, skin)), (ev("sonne_e6") + 0.55, None, look(cpos, sunpt)),
                     (ev("baby_e6") - 0.6, None, look(cpos, sunpt)), (ev("baby_e6") + 0.4, None, look(cpos, baby)),
                     (D, None, look((cpos[0] + 0.25, cpos[1] - 0.45, cpos[2] - 0.1), baby))])
    MK.pose_hands(H, 0, "hidden")
    MK.pose_hands(H, ev("wasser_e6") - 0.2, "hidden", only="R")
    MK.pose_hands(H, ev("wasser_e6") + 0.4, "low", only="R")
    MK.pose_hands(H, ev("sonne_e6") - 0.2, "low", only="R")
    MK.pose_hands(H, ev("sonne_e6") + 0.4, "hidden", only="R")
    Q.handheld(shake, 0, D, amp=0.55)
    return L


def shot_safa():
    """Sie kann nicht mehr hinsehen: Blick zurück zum Baum, dann den Hügel Safa hinauf – oben: niemand im Tal."""
    L = MK.light("noon")
    MK.valley()
    MK.camp_under_tree(full_skin=False)
    rig, shake, cam = Q.pov_camera(lens=17)
    H = MK.pov_arms(cam)
    MK.pose_hands(H, 0, "hidden")
    start = Vector((-31.5, 11.5))
    top = MK.hill_top(MK.SAFA, MK.SAFA_H)
    t_run, t_top = 1.9, 5.1
    keys = []
    for k in range(0, int(D * 10) + 1):
        t = k / 10
        u = smooth(t_run, t_top, t) * 0.4 + max(0.0, min(1.0, (t - t_run) / (t_top - t_run))) * 0.6
        x = start.x + (top.x + 1.2 - start.x) * u
        y = start.y + (top.y - 1.0 - start.y) * u
        base = max(gz(x, y), MK.hill_z(MK.SAFA, 12.0, MK.SAFA_H, x, y) + 0.1)
        keys.append((t, (x, y, base + EYE), None))
    Q.cam_keys(rig, keys, loc_interp="LINEAR")
    tree = (MK.TREE.x, MK.TREE.y, 1.0)
    pt = keys[-1][1]
    Q.cam_keys(rig, [(0, None, look(keys[0][1], tree)), (1.3, None, look(keys[0][1], tree)),
                     (t_run + 0.5, None, (Q.yaw_to(keys[10][1], (top.x, top.y)) + 12, 16, 0)),
                     (t_top - 0.3, None, (Q.yaw_to(keys[40][1], (top.x, top.y)) - 14, 12, 0)),
                     (t_top + 0.5, None, look(pt, (0, 40, 0)) ), (ev("niemand_e7") - 0.3, None, look(pt, (20, -20, 0))),
                     (D, None, look(pt, (35, 10, 0)))])
    Q.handheld(shake, 0, D, amp=1.0, walk_from=t_run, walk_to=t_top, walk_amp=2.4)
    return L


def shot_marwa():
    """Hinüber zur Marwa, hinauf – wieder niemand."""
    L = MK.light("noon")
    MK.valley()
    MK.camp_under_tree(full_skin=False)
    rig, shake, cam = Q.pov_camera(lens=17)
    H = MK.pov_arms(cam)
    MK.pose_hands(H, 0, "hidden")
    start = Vector((27.0, 18.5))
    top = MK.hill_top(MK.MARWA, MK.MARWA_H)
    t_top = 3.5
    keys = []
    for k in range(0, int(D * 10) + 1):
        t = k / 10
        u = min(1.0, t / t_top) ** 1.08
        x = start.x + (top.x - 1.0 - start.x) * u
        y = start.y + (top.y - 0.4 - start.y) * u
        base = max(gz(x, y), MK.hill_z(MK.MARWA, 11.0, MK.MARWA_H, x, y) + 0.1)
        keys.append((t, (x, y, base + EYE), None))
    Q.cam_keys(rig, keys, loc_interp="LINEAR")
    pt = keys[-1][1]
    Q.cam_keys(rig, [(0, None, (Q.yaw_to(keys[0][1], (top.x, top.y)), 10, 0)), (t_top - 0.4, None, (Q.yaw_to(keys[30][1], (top.x, top.y)) + 10, 8, 0)),
                     (t_top + 0.4, None, look(pt, (10, 50, 0))), (ev("niemand_e8") - 0.2, None, look(pt, (-10, -10, 0))),
                     (D, None, look(pt, (-30, 0, 0)))])
    Q.handheld(shake, 0, D, amp=1.1, walk_from=0, walk_to=t_top, walk_amp=2.6)
    return L


def shot_stimme():
    """Beim siebten Mal, oben auf der Marwa, erschöpft – eine Stimme. Unten beim Baum leuchtet ein Licht auf."""
    L = MK.light("golden")
    MK.valley()
    MK.camp_under_tree(full_skin=False)
    A = MK.angel("engel", (SP.x - 0.7, SP.y - 0.35, gz(SP.x, SP.y)))
    MK.angel_anim(A, ev("stimme_e10") - 0.1, D)
    rig, shake, cam = Q.pov_camera(lens=17)
    top = MK.hill_top(MK.MARWA, MK.MARWA_H)
    pos = (top.x - 1.4, top.y - 0.6, top.z + 1.35)
    pos2 = (top.x - 1.6, top.y - 0.8, top.z + EYE)
    Q.cam_keys(rig, [(0, pos, None), (ev("stimme_e10"), pos, None), (D, pos2, None)])
    tree = (MK.TREE.x, MK.TREE.y, 1.5)
    Q.cam_keys(rig, [(0, None, (Q.yaw_to(pos, (top.x - 6, top.y - 2)), -48, 0)), (ev("stimme_e10") - 0.3, None, (Q.yaw_to(pos, (top.x - 6, top.y - 2)), -40, 0)),
                     (ev("stimme_e10") + 0.6, None, look(pos, tree)), (D, None, look(pos2, tree))])
    Q.handheld(shake, 0, D, amp=0.9, walk_from=0, walk_to=D, walk_amp=0.7)
    return L


SP = MK.SPRING


def shot_quelle():
    """Der Engel (Licht) beim Baby, scharrt im Boden – Wasser bricht hervor."""
    L = MK.light("golden")
    MK.valley()
    Bb, ws, db = MK.camp_under_tree(full_skin=False)
    A = MK.angel("engel", (SP.x - 0.7, SP.y - 0.35, gz(SP.x, SP.y)))
    MK.angel_anim(A, -2.0, D)
    tb = ev("wasser_e11") - 0.1
    S = MK.spring(tb, D)
    # Scharren: Licht am Boden glüht auf + Funken
    glow = Q.ball("dig_glow", (SP.x, SP.y, gz(SP.x, SP.y) + 0.02), (0.5, 0.5, 0.06),
                  Q.glow_mat("dig_m", (1.0, 0.92, 0.7), 6.0, 0.7, fresnel=True), seg=24)
    t_dig = ev("engel_e11") + 1.6
    for t, s in ((0, 0.001), (t_dig - 0.1, 0.001), (t_dig + 0.5, 1.0), (tb, 1.3), (tb + 0.6, 0.001)):
        glow.scale = (s, s, s)
        glow.keyframe_insert("scale", frame=max(1, Q.T(t)))
    rig, shake, cam = Q.pov_camera(lens=17)
    p0, p1 = P(11.5, -3.2), P(7.6, -8.4)
    Q.cam_keys(rig, [(0, p0, None), (4.6, p1, None), (tb, p1, None), (tb + 0.25, (p1[0] + 0.15, p1[1] + 0.25, p1[2]), None),
                     (D, (p1[0] - 0.2, p1[1] - 0.3, p1[2]), None)], loc_interp="BEZIER")
    baby = (BABY.x, BABY.y, gz(BABY.x, BABY.y) + 0.1)
    Q.cam_keys(rig, [(0, None, look(p0, (SP.x, SP.y, 1.4))), (ev("baby_e11") + 0.3, None, look(p0, baby)),
                     (ev("engel_e11") + 0.2, None, look(p1, (SP.x - 0.5, SP.y, 2.0))), (t_dig, None, look(p1, (SP.x, SP.y, 0.3))),
                     (tb + 0.4, None, look(p1, (SP.x, SP.y, 0.9))), (D, None, look(p1, (SP.x, SP.y, 0.5)))])
    Q.handheld(shake, 0, D, amp=0.8, walk_from=0, walk_to=4.6, walk_amp=1.0)
    H = MK.pov_arms(cam)
    MK.pose_hands(H, 0, "hidden")
    return L


def shot_wall():
    """Hadschar schiebt mit beiden Händen Sand zu einem Wall um das Wasser; das Wasser sprudelt (Zitat des Propheten ﷺ)."""
    L = MK.light("golden")
    MK.valley()
    Bb, ws, db = MK.camp_under_tree(full_skin=False)
    A = MK.angel("engel", (SP.x - 0.7, SP.y - 0.35, gz(SP.x, SP.y)))
    MK.angel_anim(A, -5.0, D)
    w0, w1 = 0.5, max(3.2, ev("wall_e12") + 1.7)
    S = MK.spring(None, D, wall_t0=w0, wall_t1=w1)
    rig, shake, cam = Q.pov_camera(lens=17)
    H = MK.pov_arms(cam)
    c0 = (SP.x + 0.15, SP.y + 1.05, gz(SP.x, SP.y) + 0.95)
    c1 = (SP.x + 0.6, SP.y + 2.1, gz(SP.x, SP.y) + 1.5)
    Q.cam_keys(rig, [(0, c0, None), (w1 + 0.6, c0, None), (D, c1, None)], loc_interp="BEZIER")
    spc = (SP.x, SP.y, gz(SP.x, SP.y))
    Q.cam_keys(rig, [(0, None, look(c0, spc)), (w1 + 0.6, None, look(c0, spc)), (D - 3.0, None, look(c1, (spc[0] - 0.3, spc[1] - 0.4, 0.3))),
                     (D, None, look(c1, (spc[0] - 0.4, spc[1] - 0.6, 0.4)))])
    MK.pose_hands(H, 0, "hidden")
    t = w0 - 0.2
    k = 0
    while t < w1:
        MK.pose_hands(H, t, "dig" if k % 2 == 0 else "dig_in")
        t += 0.42
        k += 1
    MK.pose_hands(H, w1 + 0.4, "low")
    MK.pose_hands(H, w1 + 1.3, "hidden")
    Q.handheld(shake, 0, D, amp=0.5)
    return L


def shot_engel():
    """„Habt keine Angst. Hier wird das Haus Allahs stehen …“ – auf dem Hügelchen erscheinen goldene Umrisse."""
    L = MK.light("golden")
    MK.valley()
    Bb, ws, db = MK.camp_under_tree(full_skin=False)
    A = MK.angel("engel", (SP.x - 0.7, SP.y - 0.35, gz(SP.x, SP.y)))
    MK.angel_anim(A, -8.0, D)
    MK.spring(None, D, wall_t0=-3.0, wall_t1=-1.0)
    MK.kaaba_ghost(ev("haus_q5") - 0.2)
    rig, shake, cam = Q.pov_camera(lens=17)
    c0 = P(SP.x + 2.4, SP.y + 3.2)
    c1 = P(SP.x + 3.4, SP.y + 4.4)
    Q.cam_keys(rig, [(0, c0, None), (D, c1, None)], loc_interp="BEZIER")
    ang = (SP.x - 0.7, SP.y - 0.35, 2.4)
    hk = (MK.HILLOCK.x, MK.HILLOCK.y, 3.0)
    Q.cam_keys(rig, [(0, None, look(c0, (ang[0], ang[1], 1.2))), (ev("engel_e13") + 0.8, None, look(c0, ang)),
                     (ev("haus_q5") - 0.4, None, look(c0, ang)), (ev("haus_q5") + 1.4, None, look(c0, hk)),
                     (D - 2.0, None, look(c1, hk)), (D, None, look(c1, (hk[0] + 3.0, hk[1] + 2.0, 2.6)))])
    Q.handheld(shake, 0, D, amp=0.5)
    H = MK.pov_arms(cam)
    MK.pose_hands(H, 0, "hidden")
    return L


def shot_karawane():
    """Ich-Sicht auf einem Kamel: eine Karawane zieht am Tal vorbei; Vögel kreisen über der Stelle mit der Quelle."""
    L = MK.light("morning")
    MK.valley()
    MK.camp_under_tree(full_skin=False)
    MK.spring(None, D, wall_t0=-3.0, wall_t1=-1.0)
    MK.birds_circle((SP.x, SP.y), 11.0, 30.0, 8, D, seed=3, scale=5.0)
    route = [(-112.0, -40.0), (-80.0, -36.0), (-50.0, -30.0)]
    me = MK.camel("me", (route[0][0], route[0][1], gz(*route[0])), seed=1)
    MK.camel_walk(me, route, 0.0, speed=1.3)
    rig, shake, cam = Q.pov_camera(lens=17)
    rig.parent = me["body"]
    rig.location = (0, 0.12, 1.45)
    others = []
    for i, (dx, dy, sp_) in enumerate(((1.0, 6.0, 1.3), (-1.4, 13.0, 1.3), (3.4, -1.2, 1.3))):
        C = MK.camel(f"c{i}", (route[0][0] + dy, route[0][1] + dx, 0), seed=10 + i)
        rt = [(x + dy, y + dx) for x, y in route]
        MK.camel_walk(C, rt, 0.0, speed=sp_)
        R = MK.rider(f"r{i}", C, seed=40 + i, head="turban" if i != 2 else "scarf",
                     cloak=(0.3, 0.24, 0.18) if i == 2 else None, robe=(0.62, 0.52, 0.4) if i == 2 else None)
        others.append((C, R))
    young, old = others[0][1], others[2][1]
    sky = (SP.x, SP.y, 30.0)
    camw = lambda: rig.matrix_world.translation  # noqa: E731
    # Der Junge vorn dreht sich um und zeigt in den Himmel (k1), der Alte neben dir schaut zu dir (k2)
    Q.head_to(young, 0, (0, -100, 1.6))
    Q.head_to(young, ls("k1") - 0.2, (0, -100, 1.6))
    young["root"].rotation_euler = (0, 0, 0)
    Q.arm_pose(young, ls("k1") - 0.1, "R", 28, -50)
    Q.arm_pose(young, ls("k1") + 0.6, "R", -120, -10, sh_y=-20)
    Q.arm_pose(young, le("k1") + 0.6, "R", -120, -10, sh_y=-20)
    Q.arm_pose(young, le("k1") + 1.4, "R", 28, -50)
    old["head"].rotation_euler = (0, 0, 0)
    old["head"].keyframe_insert("rotation_euler", frame=1)
    old["head"].keyframe_insert("rotation_euler", frame=Q.T(ls("k2") - 0.3))
    old["head"].rotation_euler = (math.radians(-5), 0, math.radians(72))
    old["head"].keyframe_insert("rotation_euler", frame=Q.T(ls("k2") + 0.4))
    old["head"].keyframe_insert("rotation_euler", frame=Q.T(le("k2") - 0.2))
    old["head"].rotation_euler = (math.radians(15), 0, math.radians(15))
    old["head"].keyframe_insert("rotation_euler", frame=Q.T(le("k2") + 0.5))
    # Kamera (relativ zum Kamel: Blick nach vorn = yaw 180)
    yaw_sky = 180 + 8
    Q.cam_keys(rig, [(0, None, (180 - 10, -14, 0)), (ls("e14") + 2.5, None, (180 + 4, -9, 0)), (ls("k1") + 0.3, None, (180 + 2, -4, 0)),
                     (ev("vögel_k1") - 0.2, None, (180 + 4, 2, 0)), (ev("vögel_k1") + 0.9, None, (yaw_sky, 15, 0)),
                     (ls("k2") + 0.1, None, (yaw_sky + 4, 14, 0)), (ls("k2") + 0.9, None, (180 + 104, -3, 0)),
                     (le("k2") - 0.2, None, (180 + 98, -3, 0)), (D, None, (yaw_sky + 2, 13, 0))])
    Q.handheld(shake, 0, D, amp=0.6)
    return L


def shot_finden():
    """Die Späher finden eine Mutter, ein Baby und eine Quelle; „… wird Mekka“: Zelte entstehen rings um die Quelle."""
    L = MK.light("morning")
    MK.valley()
    MK.spring(None, D, wall_t0=-3.0, wall_t1=-1.0)
    MK.birds_circle((SP.x, SP.y), 10.0, 40.0, 6, D, seed=5, scale=3.0)
    hp = (SP.x - 1.2, SP.y - 0.9)
    Hd = Q.person("hadschar", (hp[0], hp[1], gz(*hp)), yaw=Q.face_yaw(hp, (-14, -9)), sit=True, glow=True, seed=7, head="khimar",
                  robe=(0.2, 0.14, 0.11), wrap=(0.13, 0.1, 0.1), skin=(0.4, 0.27, 0.18))
    Q.idle(Hd, 0, D, seed=3, look=[(0, 0, 0)])
    B = MK.bundle("baby_lap", (0, -0.24, 0.02), parent=Hd["hips"], rot=(0, 0, math.radians(90)), light=0.9)
    for s_ in ("L", "R"):
        Q.arm_pose(Hd, 0, s_, -18, -78, sh_y=10 if s_ == "L" else -10)
    MK.rug("rug2", (hp[0], hp[1], gz(*hp)), (1.6, 1.1), rot=0.3)
    MK.waterskin("skin", (hp[0] + 0.9, hp[1] - 0.4, gz(*hp) + 0.02), full=True, rot=0.8)
    rig, shake, cam = Q.pov_camera(lens=17)
    p0, p1 = P(-15.5, -7.0), P(-4.6, -10.8)
    hp3 = (hp[0], hp[1], gz(*hp) + 0.75)
    tr = ev("bleiben_e16") + 0.8
    up = (-20.0, 4.0, gz(0, 0) + 8.5)
    Q.cam_keys(rig, [(0, p0, None), (ev("mutter_e15") - 0.3, p1, None), (tr, (p1[0] - 0.3, p1[1] + 0.2, p1[2]), None), (D, up, None)],
               loc_interp="BEZIER")
    Q.cam_keys(rig, [(0, None, look(p0, (SP.x, SP.y, 9.0))), (ev("späher_e15") + 1.2, None, look(p0, (SP.x, SP.y, 1.0))),
                     (ev("mutter_e15") - 0.1, None, look(p1, hp3)), (ev("baby_e15") + 0.1, None, look(p1, (hp[0], hp[1], gz(*hp) + 0.35))),
                     (ev("quelle_e15") + 0.2, None, look(p1, (SP.x, SP.y, 0.1))), (tr, None, look(p1, hp3)),
                     (D, None, look(up, (SP.x + 2.0, SP.y - 2.0, 0.0)))])
    Q.handheld(shake, 0, D, amp=0.6, walk_from=0, walk_to=ev("mutter_e15") - 0.3, walk_amp=0.9)
    # sie nickt (lässt sie bleiben) und zeigt einladend
    Q.head_to(Hd, ev("bleiben_e16") - 0.6, (p1[0], p1[1], 1.5))
    Hd["head"].rotation_euler.x += math.radians(-14)
    Hd["head"].keyframe_insert("rotation_euler", frame=Q.T(ev("bleiben_e16") + 0.1))
    Q.head_to(Hd, ev("bleiben_e16") + 0.6, (p1[0], p1[1], 1.5))
    Q.arm_pose(Hd, ev("bleiben_e16") - 0.3, "R", -18, -78, sh_y=-10)
    Q.arm_pose(Hd, ev("bleiben_e16") + 0.5, "R", -55, -20, sh_y=-40)
    Q.arm_pose(Hd, ev("bleiben_e16") + 1.8, "R", -18, -78, sh_y=-10)
    # Späher (zwei Männer) gehen mit
    s1 = Q.person("spaeher1", (-14.0, -5.4, 0), seed=51, head="turban")
    Q.walk(s1, [(-14.0, -5.4), (-6.0, -8.0), (-3.5, -9.0)], 0.2, speed=1.25)
    # „… wird Mekka“: Zelte, Kamele, Feuer, Leute erscheinen nach und nach rings um die Quelle
    rnd = random.Random(9)
    tm = ev("mekka_e16") - 2.4
    spots = []
    for i in range(26):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(12, 42)
        x, y = SP.x + r * math.cos(a), SP.y + r * 0.8 * math.sin(a)
        if (x - MK.HILLOCK.x) ** 2 + (y - MK.HILLOCK.y) ** 2 < 70 or (x - p1[0]) ** 2 + (y - p1[1]) ** 2 < 30:
            continue
        spots.append((x, y, a))
    for k, (x, y, a) in enumerate(spots):
        t_ = tm + 3.2 * k / max(1, len(spots)) + rnd.uniform(0, 0.4)
        T_ = MK.tent(f"tent{k}", (x, y, gz(x, y)), yaw=a + math.pi / 2, w=rnd.uniform(3.2, 5.0), d=rnd.uniform(2.2, 3.0),
                     mat=MK.M["tent2"] if k % 3 else MK.M["tent"], seed=k)
        MK.pop_in(T_, t_)
        if k % 3 == 0:
            F = MK.campfire(f"fire{k}", (x + 2.5 * math.cos(a), y + 2.5 * math.sin(a), gz(x, y)))
            MK.pop_in(F["root"], t_ + 0.2)
        if k % 4 == 1:
            C = MK.camel(f"cm{k}", (x - 2.4 * math.sin(a), y + 2.4 * math.cos(a), gz(x, y)), yaw=a, seed=k, load=False, sit=True)
            MK.pop_in(C["root"], t_ + 0.3)
        if k % 2 == 0:
            Pp = Q.person(f"camp{k}", (x + 1.5 * math.cos(a + 0.6), y + 1.5 * math.sin(a + 0.6), gz(x, y)), yaw=a, seed=300 + k,
                          head=rnd.choice(["turban", "scarf", "khimar"]))
            MK.pop_in(Pp["root"], t_ + 0.25)
    return L


def shot_heute():
    """Mas'a heute: Pilger in Weiß laufen zwischen Safa und Marwa; im Bereich des Tals (grüne Lichter) eilen sie."""
    MK.mats()
    Q.world_sky("dawn", amb=((0.9, 0.85, 0.78), 0.5))
    HL = MK.masaa()
    W = HL["width"]
    rig, shake, cam = Q.pov_camera(lens=17)
    x0 = -22.5
    sp = 1.25
    c = lambda t: (x0 + sp * min(t, 12.0), 2.6, EYE + 0.05)  # noqa: E731
    Q.cam_keys(rig, [(0, c(0), None), (12.0, c(12.0), None), (D, (c(12.0)[0] + 0.6, 2.2, EYE + 0.05), None)], loc_interp="LINEAR")
    zz = (-3.0, -W / 2 + 0.8, 0.9)
    Q.cam_keys(rig, [(0, None, (-90 + 4, -2, 0)), (4.0, None, (-90 - 6, 1, 0)), (6.5, None, (-90 + 8, 6, 0)), (9.5, None, (-90 - 4, 2, 0)),
                     (ev("zamzam_e18") - 0.2, None, (-90 - 2, 0, 0)), (ev("zamzam_e18") + 1.2, None, look(c(ev("zamzam_e18") + 1.2), zz)),
                     (D, None, look((c(12.0)[0] + 0.6, 2.2, EYE), zz))])
    Q.handheld(shake, 0, D, amp=0.7, walk_from=0, walk_to=12.6, walk_amp=0.7)
    rnd = random.Random(12)
    gx0, gx1 = HL["green"]
    k = 0
    cam_x = lambda t: x0 + sp * min(t, 12.0)  # noqa: E731
    # Spur mit dir (Richtung Marwa, +x): y 0.6 … 8.6; Gegenspur (-x): y -0.6 … -8.6. Dicht wie beim echten Sa'i.
    for lane, dirx, n in ((1, 1, 44), (-1, -1, 30)):
        for i in range(n):
            for _try in range(20):
                y = lane * rnd.uniform(0.7, 8.6)
                x = rnd.uniform(x0 - 4, x0 + 34) if lane == 1 else rnd.uniform(x0 + 2, x0 + 52)
                if lane == 1 and abs(y - 2.6) < 0.8 and x0 - 3 < x < x0 + 22:
                    continue  # Weg vor der Kamera frei
                break
            y = MK.clear_cols(y)
            woman = rnd.random() < 0.3
            Pp = MK.pilgrim(f"pg{k}", (x, y, 0), yaw=(-math.pi / 2 if dirx > 0 else math.pi / 2), seed=500 + k, woman=woman)
            spd = rnd.uniform(1.05, 1.35) if lane == 1 else rnd.uniform(1.0, 1.3)
            if lane == 1 and not woman and rnd.random() < 0.85:
                # geht normal, im grünen Bereich (Talboden) eilt er im Laufschritt
                t_a = max(0.0, (gx0 - x) / spd)
                xa = max(x, gx0)
                if x < gx0:
                    Q.walk(Pp, [(x, y), (gx0, y)], 0.0, speed=spd)
                t_b = Q.walk(Pp, [(xa, y), (min(gx1, xa + 14), y)], t_a, speed=2.4, run=True)
                if t_b < D:
                    Q.walk(Pp, [(min(gx1, xa + 14), y), (min(gx1, xa + 14) + spd * (D - t_b) + 1, y)], t_b, speed=spd)
            else:
                Q.walk(Pp, [(x, y), (x + dirx * spd * (D + 1), y)], 0.0, speed=spd)
            k += 1
    MK.far_crowd("far_a", 16, 85, 0.8, 8.6, 260, seed=1)
    MK.far_crowd("far_b", 34, 85, -8.6, -0.8, 220, seed=2)
    MK.far_crowd("far_c", -85, -30, -8.6, -0.8, 160, seed=3)
    return dict(mist_col=(0.88, 0.86, 0.8), mist_amt=0.25)


def shot_ende():
    """Abenddämmerung im Tal: Hadschar sitzt mit dem Baby (Licht) an der Quelle – die Kamera steigt langsam auf."""
    L = MK.light("dusk", stars=2.2)
    MK.valley()
    MK.spring(None, D, wall_t0=-3.0, wall_t1=-1.0)
    hp = (SP.x - 1.2, SP.y - 0.9)
    Hd = Q.person("hadschar", (hp[0], hp[1], gz(*hp)), yaw=Q.face_yaw(hp, (SP.x, SP.y)), sit=True, glow=True, seed=7, head="khimar",
                  robe=(0.2, 0.14, 0.11), wrap=(0.13, 0.1, 0.1), skin=(0.4, 0.27, 0.18))
    Q.idle(Hd, 0, D, seed=3, look=[(0, 0, -12)])
    MK.bundle("baby_lap", (0, -0.24, 0.02), parent=Hd["hips"], rot=(0, 0, math.radians(90)), light=1.1)
    for s_ in ("L", "R"):
        Q.arm_pose(Hd, 0, s_, -18, -78, sh_y=10 if s_ == "L" else -10)
    MK.rug("rug2", (hp[0], hp[1], gz(*hp)), (1.6, 1.1), rot=0.3)
    Q.point("spring_glow", (SP.x, SP.y, 0.6), 18, color=(0.7, 0.85, 1.0), radius=0.4)
    rig, shake, cam = Q.pov_camera(lens=17)
    p0 = (hp[0] + 1.9, hp[1] + 2.4, gz(*hp) + 1.2)
    p1 = (hp[0] + 9.0, hp[1] + 14.0, gz(*hp) + 9.5)
    tgt = (hp[0] + 0.6, hp[1] + 0.3, 0.5)
    Q.cam_keys(rig, [(0, p0, look(p0, tgt)), (D, p1, look(p1, (hp[0] - 2.0, hp[1] - 6.0, 2.0)))], interp="BEZIER")
    Q.handheld(shake, 0, D, amp=0.25)
    return L


SHOTS = {"tal": shot_tal, "abschied": shot_abschied, "frage": shot_frage, "durst": shot_durst, "safa": shot_safa, "marwa": shot_marwa,
         "stimme": shot_stimme, "quelle": shot_quelle, "wall": shot_wall, "engel": shot_engel, "karawane": shot_karawane,
         "finden": shot_finden, "heute": shot_heute, "ende": shot_ende}

Q.reset()
cfg = SHOTS[SHOT]()
MK.no_glow_shadows()
if os.environ.get("JOIN", "1") == "1":
    MD.join_static(keep=("baby", "skin", "dates", "spring", "engel", "ibrahim", "kaaba_ghost", "dig_glow", "bird", "tent", "fire", "cm",
                         "camp", "me_", "c0", "c1", "c2", "r0", "r1", "r2", "pg", "far_", "hadschar", "spaeher", "rug2", "burst"))
# Schattenauflösung: die zuerst gerenderten Einstellungen mit 1.0, der Rest mit 0.5 (12 % schneller, kaum sichtbar – 4-CPU-Rechner)
SHADOW_HI = {"tal", "frage", "wall", "finden", "heute"}
Q.render_setup(pct=PCT, samples=SAMPLES, mist_col=cfg["mist_col"], mist_amt=cfg["mist_amt"], shadow_res=1.0 if SHOT in SHADOW_HI else 0.5,
               sky_sep=SHOT != "heute")
sc = bpy.context.scene
if os.environ.get("LIST"):  # Test: Objekte mit Präfix auflisten
    for o in bpy.data.objects:
        if o.name.startswith(os.environ["LIST"]):
            print("OBJ", o.name, o.type, tuple(round(v, 3) for v in o.matrix_world.translation), o.parent.name if o.parent else None,
                  [m.name for m in o.data.materials] if o.type == "MESH" else "")
    sys.exit(0)
for o in bpy.data.objects:  # Kamera reicht weit (Berge)
    if o.type == "CAMERA":
        o.data.clip_end = 900
if os.environ.get("NOCOMP"):
    sc.render.use_compositing = False
sc.frame_start, sc.frame_end = 1, SEG[SHOT]["frames"]
if os.environ.get("FRAMES"):
    sc.frame_start, sc.frame_end = map(int, os.environ["FRAMES"].split("-"))
if os.environ.get("BENCH_DETAIL"):  # Test: Rauschen mit weniger Oktaven (schneller)
    cap = float(os.environ["BENCH_DETAIL"])
    for m in bpy.data.materials:
        if m.node_tree:
            for n in m.node_tree.nodes:
                if n.type == "TEX_NOISE":
                    n.inputs["Detail"].default_value = min(n.inputs["Detail"].default_value, cap)
if os.environ.get("BENCH_SHADOW"):
    sc.eevee.shadow_resolution_scale = float(os.environ["BENCH_SHADOW"])
import time as _time
print("SETUP_DONE", _time.time())
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
