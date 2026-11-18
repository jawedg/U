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
Q.FPS = TL.get("render_fps", 24)  # Blender-Bilder pro Sekunde (Video: 60 fps, dazwischen interpoliert)

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
    """Nachts durch die Gasse; der junge Mann (Ich-Sicht) bleibt beim Mann an der Tür stehen und fragt ihn (d1),
    der schaut hoch, antwortet (n1) und zeigt Richtung Moschee; dann geht es weiter."""
    L = night()
    I = MD.town(night=True)
    rig, shake, cam = Q.pov_camera()
    H = Q.pov_hands(cam)
    Q.flicker(H["lamp"]["light"], 0, D, 9.0, seed=1)
    for k, nl in enumerate(I["niche_lamps"]):
        Q.flicker(nl["light"], 0, D, 35.0, seed=10 + k)
    man = (1.75, -32.6)                       # sitzt an seiner Tür (Ostseite)
    t_ask, t_ans, t_end = ls("d1"), ls("n1"), le("n1")
    t_stop = max(2.0, t_ask - 0.45)
    stop = (-0.15, -34.9, 1.62)
    y0 = -40.2
    keys = []
    for k in range(0, 9):  # langsam gehen bis vor den Mann
        u = k / 8
        keys.append((t_stop * u, (0.3 + (stop[0] - 0.3) * u, y0 + (stop[1] - y0) * u, 1.62), None))
    keys.append((t_end - 0.15, stop, None))
    keys.append((D, (0.0, stop[1] + 0.5, 1.62), None))  # „Lauf lieber!“ -> weiter
    Q.cam_keys(rig, keys, loc_interp="BEZIER")
    face_man = Q.yaw_to(stop, man)
    look_down = Q.pitch_to(stop, (man[0], man[1], 1.05))
    Q.cam_keys(rig, [(0, None, (4, -3, 0)), (1.8, None, (14, -2, 0)), (min(4.2, t_stop - 2.0), None, (-12, -4, 0)),
                     (t_stop - 0.8, None, (-6, -3, 0)), (t_ask + 0.2, None, (face_man, look_down, 0)),
                     (t_end - 0.3, None, (face_man * 0.85, look_down + 1, 0)), (D, None, (face_man * 0.35, -2, 0))])
    Q.handheld(shake, 0, D, amp=0.8, walk_from=0, walk_to=t_stop)
    # Leute: einer geht vorn zur Moschee, einer sitzt an seiner Tür (antwortet), einer steht im Eingang
    a = Q.person("vor", (-0.5, -29.0, 0), seed=21, head="turban")
    Q.walk(a, [(-0.5, -29.0), (-0.3, -22.0), (0.0, -15.0)], 0.0, speed=1.15)
    b = Q.person("sitz", (*man, 0), yaw=-math.pi / 2, sit=True, seed=22, head="scarf")
    Q.idle(b, 0, D, seed=3)
    for k in range(3):  # schaut vor sich hin, dann zu dir hoch, während du fragst und er antwortet
        Q.head_to(b, k * 2.0, (man[0] - 3, man[1] + (k - 1) * 2.5, 1.0))
    Q.head_to(b, t_ask + 0.35, stop)
    Q.head_to(b, t_ans + 0.8, stop)
    Q.head_to(b, t_end - 0.7, (0.0, -15.0, 1.6))          # „Lauf lieber!“ – Blick Richtung Moschee
    Q.head_to(b, D, (0.0, -15.0, 1.6))
    Q.arm_pose(b, t_end - 1.3, "R", -10, -20)
    Q.arm_pose(b, t_end - 0.6, "R", -70, -10, sh_y=-30)    # zeigt die Gasse hinauf zur Moschee
    Q.arm_pose(b, D, "R", -70, -10, sh_y=-30)
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
                     (le("m2") + 0.1, None, (a1 * 0.7, -3, 0)), (D, None, (10, 3, 0))])
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
    # wer schlägt was vor (Glocke links, Horn rechts, Feuer links hinten) – ruhige, weiche Bewegungen (Nutzer: vorher zu hektisch)
    who = {"glocke_d4": 1, "horn_d4": 6, "feuer_d4": 2}
    for ev, idx in who.items():
        t = lt(EV[ev])
        P, p = sah[idx]
        Q.head_to(P, t - 1.0, (*light_pt[:2], 1.0))
        Q.head_to(P, t, (C.x, C.y - 1.2, 0.9))           # dreht sich langsam zur Runde
        Q.arm_pose(P, t - 0.9, "R", 28, -50)
        Q.arm_pose(P, t + 0.2, "R", -30, -60)              # Hand hebt sich beim Vorschlag
        Q.arm_pose(P, t + 2.0, "R", 28, -50)
        Q.head_to(P, t + 2.6, (*light_pt[:2], 1.0))      # und langsam zurück zum Licht
    # nur zwei andere schauen beim ersten Vorschlag langsam hin und später zurück
    t1 = lt(EV["glocke_d4"])
    for j in (3, 7):
        Pj, pj = sah[j]
        Q.head_to(Pj, t1 - 0.2, (*light_pt[:2], 1.0))
        Q.head_to(Pj, t1 + 0.9, (sah[1][1][0], sah[1][1][1], 0.9))
        Q.head_to(Pj, t1 + 3.4, (*light_pt[:2], 1.0))
    # Kamera: kein Hin-und-her-Schwenken mehr, nur eine langsame, kleine Bewegung
    te = lt(EV["feuer_d4"])
    cam_rot = [(0, (0, -4, 0)), (ls("d3") + 2.0, (0, -3, 0)), (t1 - 0.5, (6, -5, 0)), (te + 1.0, (-5, -5, 0)),
               (max(te + 2.5, ls("d5") + 0.8), (0, -3, 0)), (D, (0, -1, 0))]
    Q.cam_keys(rig, [(0, pov, None), (D, (0.0, pov[1] + 0.45, 0.98), None)], loc_interp="BEZIER")
    Q.cam_keys(rig, [(t, None, a) for t, a in cam_rot])
    Q.handheld(shake, 0, D, amp=0.55)
    Q.point("fill", (0, C.y - 4, 2.5), 8, color=(0.8, 0.7, 0.6))
    return L


def shot_traum():
    Q.world_sky("dreamnight", amb=((0.32, 0.34, 0.58), 0.4))
    MD.mats()
    X0 = Vector((3000, 0, 0))
    rq = random.Random(9)
    # Traum-Wüste: weite Dünen (Gitter mit sanftem Relief), golden schimmernd
    import bmesh
    bm = bmesh.new()
    n, size = 90, 160.0
    vs = []
    for j in range(n + 1):
        row = []
        for i in range(n + 1):
            x, y = -size / 2 + size * i / n, -size / 2 + size * j / n
            r = math.hypot(x, y)
            z = (0.0 if r < 7 else min(1.0, (r - 7) / 10)) * (1.4 * math.sin(x * 0.11 + 0.7 * math.sin(y * 0.07)) +
                                                                 0.8 * math.sin(y * 0.16 + x * 0.05) + 0.3 * math.sin(x * 0.4 + y * 0.3))
            row.append(bm.verts.new((X0.x + x, X0.y + y, z - 0.03)))
        vs.append(row)
    for j in range(n):
        for i in range(n):
            bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
    me = bpy.data.meshes.new("dream_dunes")
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    me.materials.append(Q.pbr("dream_sand", (0.5, 0.39, 0.27), 0.6, var=0.25, scale=0.08, bump=0.25, bscale=3, emit=(1.0, 0.78, 0.48), es=0.03))
    Q.link(bpy.data.objects.new("dream_dunes", me))
    # Medina als Traumbild ringsum im Dunst: Häuser + Palmen
    for i in range(16):
        a_ = 2 * math.pi * i / 16 + rq.uniform(-0.12, 0.12)
        r = rq.uniform(17, 30)
        w, d_ = rq.uniform(4, 8), rq.uniform(4, 7)
        MD.house(f"dh{i}", X0.x + r * math.cos(a_) - w / 2, X0.y + r * math.sin(a_) - d_ / 2, w, d_, rq.choice([3.0, 3.4, 5.6]),
                 seed=300 + i, lit=True, windows=2)
    for i in range(12):
        a_ = 2 * math.pi * i / 12 + 0.26
        r = rq.uniform(12, 24)
        MD.palm(f"dp{i}", (X0.x + r * math.cos(a_), X0.y + r * math.sin(a_), 0), h=rq.uniform(7, 10.5), seed=400 + i)
    # leuchtende Wolkenbänke am Horizont und darüber
    for i in range(22):
        a_ = rq.uniform(0, 2 * math.pi)
        r = rq.uniform(40, 75)
        z = rq.uniform(-1, 6) if i < 14 else rq.uniform(20, 32)
        sc_ = (rq.uniform(9, 18), rq.uniform(5, 9), rq.uniform(1.6, 3.2))
        Q.ball(f"cloud{i}", (X0.x + r * math.cos(a_), X0.y + r * math.sin(a_), z), sc_,
               Q.glow_mat(f"cloud_m{i}", (0.6, 0.62, 0.85) if i >= 14 else (0.9, 0.7, 0.5), rq.uniform(0.25, 0.45), alpha=0.4, fresnel=True),
               seg=20)
    # großer Mond (Sichel) im Dunst
    mo = Q.ball("dream_moon", (X0.x - 60, X0.y + 70, 34), 5.0, Q.glow_mat("moon_m", (1.0, 0.93, 0.78), 9.0), seg=32)
    Q.ball("dream_moon_cut", (X0.x - 57.6, X0.y + 68.0, 35.4), 4.7, Q.glow_mat("moon_cut", (0.012, 0.016, 0.045), 1.0), seg=32)
    # schwebende Lichtpunkte im ganzen Raum + Staub, der im Kreis mitwirbelt
    mq = Q.glow_mat("dream_mote", (1.0, 0.86, 0.55), 14.0)
    for i in range(120):
        a_ = rq.uniform(0, 2 * math.pi)
        r = rq.choice([rq.uniform(1.0, 3.0), rq.uniform(8.5, 16.0)])
        o = Q.ball(f"dm{i}", X0 + Vector((r * math.cos(a_), r * math.sin(a_), rq.uniform(0.2, 5.5))), rq.uniform(0.008, 0.022), mq, seg=8)
        o.keyframe_insert("location", frame=1)
        o.location.z += rq.uniform(0.4, 1.4)
        o.location.x += rq.uniform(-0.4, 0.4)
        o.keyframe_insert("location", frame=Q.T(D))
    for k_, (rad, hz, turns, cnt) in enumerate(((2.0, 0.6, 1.0, 260), (2.6, 1.5, 0.7, 200), (1.4, 2.5, 1.3, 140))):
        piv = Q.empty(f"swirl{k_}", tuple(X0))
        bm = bmesh.new()
        for _ in range(cnt):
            a_ = rq.uniform(0, 2 * math.pi)
            rr = rad + rq.uniform(-0.3, 0.3)
            g = bmesh.ops.create_icosphere(bm, subdivisions=0, radius=rq.uniform(0.004, 0.01))
            off = Vector((rr * math.cos(a_), rr * math.sin(a_), hz + rq.uniform(-0.5, 0.5)))
            for v in g["verts"]:
                v.co += off
        me = bpy.data.meshes.new(f"swirl_me{k_}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(Q.glow_mat(f"swirl_m{k_}", (1.0, 0.82, 0.5), 10.0))
        so = bpy.data.objects.new(f"swirl_o{k_}", me)
        Q.link(so)
        so.parent = piv
        piv.rotation_euler = (0, 0, 0)
        piv.keyframe_insert("rotation_euler", frame=1)
        piv.rotation_euler = (0, 0, 2 * math.pi * turns * (1 if k_ != 1 else -1))
        piv.keyframe_insert("rotation_euler", frame=Q.T(D) + 1)
        Q.set_interp(piv, "LINEAR")
    # tiefer Bodennebel (weiche, leuchtende Schwaden)
    for i in range(10):
        a_ = rq.uniform(0, 2 * math.pi)
        r = rq.uniform(4, 14)
        Q.ball(f"fog{i}", (X0.x + r * math.cos(a_), X0.y + r * math.sin(a_), 0.15), (rq.uniform(3, 6), rq.uniform(2, 4), 0.35),
               Q.glow_mat(f"fog_m{i}", (1.0, 0.85, 0.62), 0.5, alpha=0.35, fresnel=True), seg=16)
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
    # leuchtende Fußspuren, wo der Mann im Kreis geht (erscheinen Schritt für Schritt, verglimmen langsam)
    mfp = Q.glow_mat("footprint", (1.0, 0.72, 0.32), 4.0)
    nst = 22
    for k_ in range(nst):
        u = (k_ + 0.5) / nst
        a_ = -math.pi / 2 + 1.5 * math.pi * u
        side = 0.13 if k_ % 2 else -0.13
        px = X0.x + (r + side) * math.cos(a_)
        py = X0.y + (r + side) * math.sin(a_)
        fp = Q.ball(f"fp{k_}", (px, py, 0.012), (0.15, 0.065, 0.008), mfp, seg=10)
        fp.rotation_euler = (0, 0, a_ + math.pi / 2)
        tk = 0.3 + (end_t - 0.3) * u
        fp.scale = (0.001, 0.001, 0.001)
        fp.keyframe_insert("scale", frame=max(1, Q.T(tk - 0.05)))
        fp.scale = (1, 1, 1)
        fp.keyframe_insert("scale", frame=Q.T(tk) + 1)
        fp.keyframe_insert("scale", frame=Q.T(tk + 3.5) + 1)
        fp.scale = (0.6, 0.6, 0.6)
        fp.keyframe_insert("scale", frame=Q.T(min(D, tk + 7.0)) + 1)
    Q.point("dream_key", tuple(X0 + Vector((-3, -4, 5))), 260, color=(1.0, 0.85, 0.65), radius=1.0)
    Q.point("dream_rim", tuple(X0 + Vector((2, 4, 3))), 200, color=(1.0, 0.75, 0.45), radius=1.0)
    Q.point("dream_back", tuple(X0 + Vector((0, 9, 2))), 300, color=(1.0, 0.7, 0.4), radius=2.0)
    Q.point("dream_top", tuple(X0 + Vector((0, 0, 6.5))), 520, color=(1.0, 0.82, 0.55), radius=1.5)
    bpy.context.scene.world.mist_settings.start = 6.0
    bpy.context.scene.world.mist_settings.depth = 55.0
    # Kamera: beginnt hoch und weit (die ganze Traumwelt), sinkt im Bogen herab, endet nah über Abdullahs Schulter
    rig, shake, cam = Q.pov_camera(lens=18)
    keys = []
    for k_ in range(13):
        u = k_ / 12
        e = 1 - (1 - u) ** 2.2  # schnell heran, dann langsam
        a_ = math.radians(-135 + 95 * e)
        rr = 7.6 - 4.0 * e
        p = (X0.x + rr * math.cos(a_), X0.y + rr * math.sin(a_), 3.4 - 1.65 * e)
        tgt = (X0.x + 0.3 * math.sin(u * 3), X0.y, 1.25 + 0.2 * (1 - e))
        keys.append((D * u, p, (Q.yaw_to(p, tgt[:2]), Q.pitch_to(p, tgt), 0)))
    Q.cam_keys(rig, keys, interp="BEZIER")
    Q.handheld(shake, 0, D, amp=0.18)
    return dict(mist_col=(0.06, 0.07, 0.15), mist_amt=0.55)


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
    t2 = Q.walk(bil, [bil_p0, (3.05, 10.25), bil_p1], tb - 0.2, speed=1.0)  # vor der Säulenreihe (y=11) entlang, nicht hindurch
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
    # die Mutter kommt aus einer ECHTEN Haustür (Westseite der Gasse), die Tür geht dabei auf (vorher: kam aus der Wand)
    best = None
    for nm, (dr, x0_, y0_, w_, d_) in I["doors"].items():
        if dr is None or x0_ > 0:
            continue
        hx, hy = dr.location.x, dr.location.y + 0.475
        dist = abs(hy + 26.0) + abs(hx + 2.0)
        if best is None or dist < best[0]:
            best = (dist, dr, hx, hy)
    _, hinge, hx, hy = best
    hinge.rotation_euler = (0, 0, 0)
    hinge.keyframe_insert("rotation_euler", frame=Q.T(0.15))
    hinge.rotation_euler = (0, 0, math.radians(-100))
    hinge.keyframe_insert("rotation_euler", frame=Q.T(0.9))
    b = Q.person("tuer1", (hx - 0.45, hy, 0), yaw=Q.face_yaw((hx, hy), (hx + 2, hy)), seed=102, head="scarf")
    t2 = Q.walk(b, [(hx - 0.45, hy), (hx + 0.55, hy - 0.1), (hx + 1.2, hy - 0.4)], 0.45, speed=0.9)
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
if os.environ.get("JOIN", "1") == "1":
    MD.join_static()
Q.render_setup(pct=PCT, samples=SAMPLES, mist_col=cfg["mist_col"], mist_amt=cfg["mist_amt"])
sc = bpy.context.scene
if os.environ.get("NOCOMP"):  # Test: ohne Compositor (Dunst/Leuchten)
    sc.render.use_compositing = False
sc.frame_start, sc.frame_end = 1, SEG[SHOT]["frames"]
if os.environ.get("FRAMES"):  # Test: nur Bilder a-b
    sc.frame_start, sc.frame_end = map(int, os.environ["FRAMES"].split("-"))
os.makedirs(OUT, exist_ok=True)
if os.environ.get("MID") == "1":
    # Echte Zwischenbilder für 60 fps: Bild k+0,5 (gleiche Animation, Blender wertet den Zwischenzeitpunkt aus).
    # Mehrere Prozesse teilen sich die Arbeit über Platzhalter-Dateien (O_EXCL). Datei k = Zeitpunkt zwischen Bild k und k+1.
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
