# QISSAH Folge 4 – „Die Schlacht von Badr“: alle Einstellungen in Blender (Ich-Sicht eines Muslims aus Medina). Aufruf:
#   blender -b --factory-startup --python blender/qissa/badr.py -- <einstellung> <ausgabe_ordner> [prozent] [samples] [standbild-zeiten]
# Längen und Ereignisse: src/qissa_badr/timeline.json (scripts/build_qissa_badr.py).
# Regeln: der Prophet ﷺ NUR als Licht, die Engel NUR als Licht-Streifen; Menschen ohne Gesicht; kein Blut (Hiebe treffen nur
# Schild/Schwert, der stürzende Gegner fällt in den Staub, Schnitt).
import bpy, sys, os, math, json, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import lib as Q
import medina as MD
import mekka as MK
import kaaba_world as KW
import badr_world as BW

TL = json.load(open(os.environ.get("TL_FILE") or os.path.join(ROOT, "src", "qissa_badr", "timeline.json"), encoding="utf-8"))
SEG = {s["id"]: s for s in TL["segments"]}
LINE = {l["id"]: l for l in TL["lines"]}
EV = TL["events"]
Q.FPS = TL.get("render_fps", 30)
MK.PEB_SUB = 1
MK.N_SHRUBS = 90
MK.FAR_LEAVES = 700
MK.SHRUB_SUB = 0


def _fast_templates():
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
SHOT = argv[0] if argv else "rat"
OUT = argv[1] if len(argv) > 1 else "/tmp/badr"
PCT = int(argv[2]) if len(argv) > 2 else 50
SAMPLES = int(argv[3]) if len(argv) > 3 else 8
STILLS = [float(x) for x in argv[4].split(",")] if len(argv) > 4 and argv[4] else None

S0 = SEG[SHOT]["start"]
D = SEG[SHOT]["dur"]
EYE = 1.62
gz = MK.ground_z
ARISH, TREE, WELLS = BW.ARISH, BW.TREE, BW.WELLS


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


def ck(rig, keys, **kw):
    """Q.cam_keys, aber Gier-Winkel ohne Sprung über ±180° (sonst dreht die Kamera den langen Weg herum)."""
    out, prev = [], None
    for t, pos, ang in keys:
        if ang is not None:
            yw = ang[0]
            if prev is not None:
                while yw - prev > 180:
                    yw -= 360
                while yw - prev < -180:
                    yw += 360
            prev = yw
            ang = (yw, ang[1], ang[2])
        out.append((t, pos, ang))
    Q.cam_keys(rig, out, **kw)


def lerp3(a, b, u):
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))


def prophet(name, loc, height=2.2, strength=0.9, day=True):
    """Der Prophet ﷺ: nur als Licht-Säule."""
    H = Q.holy_light(name, loc, height=height, strength=strength)
    if day:
        H["light"].data.energy = 22.0
        em = next(n for n in H["parts"][3].active_material.node_tree.nodes if n.type == "EMISSION")
        em.inputs["Strength"].default_value = 0.6
    Q.animate_motes(H, 1, Q.T(D) + 2)
    return H


def scale_h(H, t, h):
    r = H["root"]
    r.scale = (1, 1, h / H["height"])
    r.keyframe_insert("scale", frame=max(1, Q.T(t)))


def glow_pulse(H, t, peak=2.0):
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


def companions(spots, seed=0, prefix="c", side="m", weapon=None, idle=True):
    """spots: [(x, y, blickziel(x, y)), ...] -> stehende Gefährten (manche mit Schwert an der Seite / Speer)."""
    rnd = random.Random(seed)
    out = []
    for i, (x, y, tgt) in enumerate(spots):
        w = weapon if weapon is not None else rnd.choice(["none", "none", "none", "sword"])
        Pp = BW.warrior(f"{prefix}{i}", (x, y, gz(x, y)), yaw=Q.face_yaw((x, y), tgt), side=side, seed=rnd.randint(0, 9999), weapon=w,
                        shield_=(w == "sword" and rnd.random() < 0.5))
        if w == "spear":
            Q.arm_pose(Pp, 0, "R", -18, -70)
        if idle:
            Q.idle(Pp, 0, D, seed=i + seed)
        out.append(Pp)
    return out


def walkers_column(prefix, path, n, t0, speed, seed=0, spacing=2.2, side="m"):
    """Leute gehen hintereinander einen Weg entlang."""
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        off = k * spacing
        P_ = BW.warrior(f"{prefix}{k}", (path[0][0], path[0][1], gz(*path[0])), side=side, seed=rnd.randint(0, 9999),
                        weapon=rnd.choice(["none", "spear", "sword", "none"]), shield_=False)
        Q.walk(P_, [(x + rnd.uniform(-0.4, 0.4), y) for x, y in path], t0 - off / speed, speed=speed * rnd.uniform(0.95, 1.05))
        out.append(P_)
    return out


def set_z_ground(P_, t0, t1):
    """Figuren beim Gehen auf die Geländehöhe setzen (walk() setzt z konstant)."""
    r = P_["root"]
    for f in range(Q.T(t0), Q.T(t1) + 1, 3):
        Q.sc.frame_set(f)
        x, y = r.location.x, r.location.y
        r.location.z = gz(x, y)
        r.keyframe_insert("location", index=2, frame=f)


def ground_walk(P_, path, t0, speed, run=False):
    pts = [(x, y) for x, y in path]
    t1 = Q.walk(P_, pts, t0, speed=speed, run=run)
    # z an jedem Schlüsselbild aus dem Gelände
    for fc in Q.fcurves(P_["root"]):
        if fc.data_path == "location" and fc.array_index == 2:
            xs = [f for f in Q.fcurves(P_["root"]) if f.data_path == "location" and f.array_index == 0][0]
            ys = [f for f in Q.fcurves(P_["root"]) if f.data_path == "location" and f.array_index == 1][0]
            for kp in fc.keyframe_points:
                fr = kp.co.x
                kp.co.y = gz(xs.evaluate(fr), ys.evaluate(fr))
    return t1


def camel_group(prefix, loc, yaw, seed=0, light=False):
    """Ein Kamel, drei Männer: einer reitet, zwei gehen nebenher (Ahmad 3901). light=True: einer der drei ist der Prophet ﷺ (Licht)."""
    C = MK.camel(f"{prefix}_cam", loc, yaw=yaw, seed=seed)
    R = MK.rider(f"{prefix}_rid", C, seed=seed + 1, head="turban")
    return C, R


# ============================================================ Einstellungen
def shot_medina():
    """Medina in der Dämmerung, Ramadan: zarte Mondsichel; im Hof der Moschee sitzen die Ausgewanderten mit wenig Habe."""
    cfg = MK.light("golden")
    BW.mats()
    I = MD.town(night=True)
    rig, shake, cam = Q.pov_camera(lens=17)
    BW.crescent("moon_c", (-160.0, 260.0, 62.0), size=5.5, face=cam, strength=9.0)
    rnd = random.Random(3)
    sit = [(-9.5, 12.6), (-8.2, 13.1), (-6.4, 12.4), (-3.1, 13.4), (-1.8, 12.9), (2.4, 12.6), (3.8, 13.3), (6.6, 12.8), (8.4, 13.5),
           (10.6, 12.7), (-11.6, 14.6), (0.6, 15.2), (5.2, 15.6), (-5.2, 15.4)]
    ppl = []
    for k, (x, y) in enumerate(sit):
        Pp = Q.person(f"suf{k}", (x, y, 0), yaw=Q.face_yaw((x, y), (x * 0.6, 0)), sit=True, seed=500 + k,
                      head=rnd.choice(["turban", "scarf", "cap"]), robe=rnd.choice([(0.55, 0.45, 0.34), (0.42, 0.36, 0.3), (0.66, 0.58, 0.46)]))
        Q.idle(Pp, 0, D, seed=k)
        ppl.append(Pp)
        if k % 3 == 0:
            MK.dates_bag(f"bund{k}", (x + 0.45, y + 0.25, 0.0))
        if k % 4 == 1:
            KW.bowl(f"bowl{k}", (x - 0.35, y - 0.45, 0.02), meat=False)
    for k, (x, y) in enumerate(((-4.0, 2.0), (5.0, -1.0), (2.5, 6.0))):
        Pp = Q.person(f"st{k}", (x, y, 0), yaw=rnd.uniform(-3, 3), seed=560 + k, head="turban")
        Q.idle(Pp, 0, D, seed=k + 20)
    w = Q.person("wlk", (12.0, -4.0, 0), seed=571, head="scarf")
    Q.walk(w, [(12.0, -4.0), (6.0, 6.0), (4.0, 11.0)], 0.5, speed=1.0)
    for k, (x, y) in enumerate(((-7.0, 11.4), (4.5, 11.6), (10.0, 11.5))):
        Lp = Q.oil_lamp(f"floor{k}", (x, y, 0.03), energy=0.0)
        Lp["light"].data.energy = 18
        Q.flicker(Lp["light"], 0, D, 18, seed=k)
    c0 = (0.3, 1.5, EYE)
    c1 = (0.5, 7.0, EYE)
    c2 = (0.8, 8.6, EYE)
    tb = ev("besitz_e2") if "besitz_e2" in EV else ls("e2") + 3.0
    ck(rig, [(0, c0, (16, 7, 0)), (2.6, None, (14, 4, 0)), (ls("e2") - 0.2, c1, (8, -6, 0)), (tb - 0.6, None, (-10, -12, 0)),
             (D, c2, (-2, -10, 0))])
    Q.handheld(shake, 0, D, amp=0.6, walk_from=0, walk_to=D, walk_amp=0.6)
    cfg["mist_amt"] = 0.18
    return cfg


def path_keep(pts, r=6.0, step=3.0):
    out = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(bx - ax, by - ay) / step))
        out += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n, r) for k in range(n + 1)]
    return out


def column_world(mode="day", keep=()):
    cfg = BW.daylight(mode)
    BW.valley(tree=True, wells=True, arish_=False, palms=True, field=False, keep=keep)
    cfg["mist_amt"] = 0.22
    return cfg


def shot_kolonne():
    """Einstieg: Ich gehe in der langen Reihe der Muslime – wenige Kamele, je drei Männer: einer reitet, zwei gehen. Ein Pferd."""
    cfg = column_world("day", keep=path_keep([(37.0, 196.0), (33.0, 172.0), (30.0, 152.0), (27.0, 118.0)], r=7.0))
    t1 = D + 1
    rnd = random.Random(7)
    path = [(36.0, 190.0), (33.0, 172.0), (30.0, 152.0), (27.0, 132.0)]
    sp = 1.25
    # Kamele mit je einem Reiter + zwei Gehenden (vor der Kamera, versetzt)
    groups = []
    for k, off in enumerate((-7.0, -16.0, -26.0, -37.0, -50.0)):
        y0 = 184.0 + off
        x0 = 35.0 - (184.0 - y0) * 0.15 + (0.9 if k % 2 else -0.6)
        C = MK.camel(f"cm{k}", (x0, y0, gz(x0, y0)), yaw=math.pi, seed=20 + k)
        R = MK.rider(f"rd{k}", C, seed=40 + k, head=rnd.choice(["turban", "scarf"]))
        MK.camel_walk(C, [(x0, y0), (x0 - 2.0, y0 - sp * t1)], 0.0, speed=sp)
        for s_ in (-1, 1):
            Wk = BW.warrior(f"wk{k}{'ab'[s_ > 0]}", (x0 + 1.0 * s_, y0 + 0.4, gz(x0, y0)), side="m", seed=60 + k * 2 + (s_ > 0),
                            weapon=rnd.choice(["sword", "spear", "none"]), shield_=False)
            ground_walk(Wk, [(x0 + 1.0 * s_, y0 + 0.4), (x0 + 1.0 * s_ - 2.0, y0 + 0.4 - sp * t1)], 0.0, sp)
        groups.append(C)
    # der Prophet ﷺ (Licht) vorne neben einem Kamel – auch er geht abwechselnd zu Fuß
    lx, ly = 33.6, 120.0
    Hl = prophet("nur", (lx, ly, gz(lx, ly)), height=2.2, strength=0.85)
    BW.move(Hl["root"], [(0, (lx, ly, gz(lx, ly))), (t1, (lx - 2.0, ly - sp * t1, gz(lx - 2.0, ly - sp * t1)))])
    C = MK.camel("cmN", (lx + 1.3, ly + 0.5, gz(lx, ly)), yaw=math.pi, seed=31)
    MK.camel_walk(C, [(lx + 1.3, ly + 0.5), (lx - 0.7, ly + 0.5 - sp * t1)], 0.0, speed=sp)
    # einziger Reiter (al-Miqdad): Pferd im Schritt links
    Hx = BW.horse("hm", (29.5, 178.0, gz(29.5, 178.0)), yaw=math.pi, seed=3, colour=0)
    BW.mounted("hmr", Hx, side="m", seed=81, weapon="spear")
    BW.horse_run(Hx, [(29.5, 178.0), (27.5, 178.0 - 1.4 * t1)], 0.0, speed=1.4, stride=1.6, trot=True)
    # weitere Gehende vor und hinter der Kamera
    walkers_column("fw", [(34.5, 150.0), (31.5, 150.0 - sp * t1)], 10, 0.0, sp, seed=5, spacing=2.6)
    BW.far_army("col_far", 24.0, 40.0, 60.0, 118.0, 60, n_camel=10, side="m", seed=2, banners=1, facing=math.pi)
    rig, shake, cam = Q.pov_camera(lens=17)
    c0 = P(35.2, 187.0)
    c1 = P(33.2, 187.0 - sp * D)
    ck(rig, [(0, c0, (178, -4, 0)), (2.4, None, (196, -6, 0)), (4.6, None, (166, -5, 0)), (D, c1, (178, -3, 0))],
               loc_interp="LINEAR")
    Q.handheld(shake, 0, D, amp=0.7, walk_from=0, walk_to=D, walk_amp=0.8)
    BW.dust_cloud("cdust", (32, 160), (8, 30), 8, cam, 0.0, D, seed=1, size=(7, 3), alpha=0.25)
    return cfg


def shot_auszug():
    """Von der Anhöhe: unten in der Ebene zieht die reiche Karawane der Quraisch vorbei. Dann Blick nach vorn: das Licht an der Spitze."""
    cfg = column_world("day", keep=path_keep([(46.0, 176.0), (40.0, 168.0), (37.0, 130.0)], r=6.0) +
                       path_keep([(100.0, 96.0), (-40.0, 96.0)], r=5.0))
    t1 = D + 1
    rnd = random.Random(11)
    # Karawane: lange Reihe beladener Kamele, wenige Treiber, Staub
    for k in range(22):
        x0 = 95.0 - k * 4.6
        y0 = 96.0 + 1.2 * math.sin(k * 0.7)
        C = MK.camel(f"kv{k}", (x0, y0, gz(x0, y0)), yaw=-math.pi / 2, seed=100 + k, load=True)
        MK.camel_walk(C, [(x0, y0), (x0 - 1.4 * t1, y0)], 0.0, speed=1.4)
        if k % 5 == 0:
            MK.rider(f"kvr{k}", C, seed=120 + k, head="scarf", robe=rnd.choice(BW.QROBES))
    BW.far_army("kv_far", -60.0, -10.0, 92.0, 100.0, 4, n_camel=14, side="q", seed=4, banners=0)
    rig, shake, cam = Q.pov_camera(lens=17)
    BW.dust_cloud("kvd", (40, 100), (60, 4), 12, cam, 0.0, D, seed=2, size=(9, 3.5), alpha=0.3, drift=(-1.0, 0, 0.2))
    # unsere Kolonne auf dem Weg (links unten) + das Licht vorne
    sp = 1.2
    walkers_column("aw", [(40.0, 168.0), (36.0, 168.0 - sp * t1)], 8, 0.0, sp, seed=9, spacing=2.4)
    for k in range(3):
        x0, y0 = 38.5 - k * 0.4, 158.0 - k * 9.0
        C = MK.camel(f"ac{k}", (x0, y0, gz(x0, y0)), yaw=math.pi, seed=140 + k)
        MK.rider(f"ar{k}", C, seed=150 + k, head="turban")
        MK.camel_walk(C, [(x0, y0), (x0 - 1.5, y0 - sp * t1)], 0.0, speed=sp)
    lx, ly = 37.0, 136.0
    Hl = prophet("nur", (lx, ly, gz(lx, ly)), height=2.2, strength=0.9)
    BW.move(Hl["root"], [(0, (lx, ly, gz(lx, ly))), (t1, (lx - 1.6, ly - sp * t1, gz(lx - 1.6, ly - sp * t1)))])
    c0 = P(45.5, 171.0)
    c1 = P(44.5, 168.5)
    tk = ev("karawane_e3")
    tp = ev("prophet_e3")
    car = (40.0, 98.0, 1.5)
    ck(rig, [(0, c0, look(c0, (38, 150, 1.5))), (tk - 0.2, None, look(c0, car)), (tp - 0.5, None, look(c0, (20, 98, 1.0))),
                     (tp + 0.9, c1, look(c1, (lx, ly - 4, 1.8))), (D, None, look(c1, (lx - 1.5, ly - 10, 1.6)))])
    Q.handheld(shake, 0, D, amp=0.5, walk_from=tp, walk_to=D, walk_amp=0.5)
    return cfg


def shot_heer():
    """Späher-Blick von einem Hügel: die Karawane verschwindet nach Westen. Dann: durch den Pass im Süden kommt das Heer aus Mekka."""
    cfg = BW.daylight("day")
    BW.valley(tree=True, wells=True, arish_=False, field=False)
    t1 = D + 1
    rig, shake, cam = Q.pov_camera(lens=17)
    # Karawane weit im Westen (zieht weg)
    kv = BW.far_army("kv", -330.0, -250.0, -95.0, -85.0, 6, n_camel=26, side="q", seed=7, banners=0)
    BW.move(kv, [(0, (0, 0, 0)), (t1, (-1.6 * t1, 0, 0))])
    BW.dust_cloud("kvd", (-270, -90), (45, 6), 10, cam, 0.0, t1, seed=3, size=(26, 10), alpha=0.5, drift=(-1.5, 0, 0.3))
    # Heer: viele Reiter, Kamele, Fußvolk, Fahnen – kommt aus dem Pass nach Norden
    for k, (x0, x1, y0, y1, nm, nh, nc) in enumerate(((-60, -10, -260, -205, 160, 26, 30), (-55, -15, -205, -175, 120, 18, 10),
                                                      (-50, -20, -320, -260, 200, 20, 40))):
        A = BW.far_army(f"army{k}", x0, x1, y0, y1, nm, n_horse=nh, n_camel=nc, side="q", seed=10 + k, banners=5, facing=0.0)
        BW.move(A, [(0, (0, 0, 0)), (t1, (0, 1.6 * t1, 0))])
        BW.far_wobble(A, t1, amp=0.04)
    rnd = random.Random(5)
    for k in range(9):  # vorderste Reiter als echte Pferde (näher)
        x, y = -68.0 + k * 2.6 + rnd.uniform(-1, 1), -186.0 - rnd.uniform(0, 8)
        Hh = BW.horse(f"hq{k}", (x, y, gz(x, y)), yaw=0.0, seed=200 + k)
        BW.mounted(f"hqr{k}", Hh, side="q", seed=220 + k, weapon=rnd.choice(["spear", "sword"]), helmet=True)
        BW.horse_run(Hh, [(x, y), (x + rnd.uniform(-2, 2), y + 2.6 * t1)], 0.0, speed=2.6, stride=1.9, trot=True)
    for k in range(3):
        x, y = -62.0 + k * 8.0, -192.0
        BW.banner(f"hb{k}", (x, y, gz(x, y)), [BW.M["flag_r"], BW.M["flag_k"], BW.M["flag_y"]][k], pole_h=4.4, size=(1.5, 1.0), wind=1.4)
    BW.dust_cloud("ad", (-35, -215), (35, 40), 18, cam, 0.0, t1, seed=4, size=(18, 8), alpha=0.4, drift=(0.4, 1.4, 0.4))
    c0 = (-92.0, -152.0, gz(-92.0, -152.0) + 4.2)
    MK._inst("rock3", "rk_view", (-92.0, -151.6, gz(-92.0, -152.0) - 0.4), rot=(0.1, 0.05, 0.6), scale=(2.6, 2.4, 2.4))
    te = ev("heer_e4")
    ck(rig, [(0, c0, look(c0, (-300, -92, 2))), (max(0.6, te - 1.3), None, look(c0, (-290, -96, 2))),
                     (te - 0.3, None, look(c0, (-40, -205, 4))), (D, None, look(c0, (-35, -190, 4)))])
    Q.handheld(shake, 0, D, amp=0.45)
    cfg["mist_amt"] = 0.42
    return cfg


def camp_world(mode, t1, dust=0.0, stars=0.0, tree=True):
    cfg = BW.daylight(mode, dust=dust, stars=stars) if mode != "night" else BW.night()
    BW.valley(tree=tree)
    rnd = random.Random(12)
    for k, (x, y) in enumerate(((14, 50), (18, 46), (11, 55), (20, 53), (-2, 54), (25, 44), (8, 60), (-6, 58))):
        C = MK.camel(f"kc{k}", (x, y, gz(x, y)), yaw=rnd.uniform(0, 6.28), seed=300 + k, sit=True, load=(k % 2 == 0))
    for k, (x, y) in enumerate(((16.5, 41.0), (12.0, 43.5))):
        MK.dates_bag(f"db{k}", (x, y, gz(x, y)))
        MK.waterskin(f"ws{k}", (x + 0.6, y + 0.2, gz(x, y)), rot=rnd.uniform(0, 3))
    BW.banner("liwa", (-1.5, 33.5, gz(-1.5, 33.5)), BW.M["flag_w"], pole_h=3.4, size=(1.0, 0.7))
    BW.banner("raya", (6.5, 31.5, gz(6.5, 31.5)), BW.M["flag_k"], pole_h=3.4, size=(1.0, 0.7))
    return cfg


def shot_rat():
    """Später Nachmittag bei den Brunnen: die Gefährten stehen um das Licht. Al-Miqdad tritt vor und spricht."""
    cfg = camp_world("golden", D + 1)
    lp = Vector((3.0, 37.2, 0.0))
    H = prophet("nur", (lp.x, lp.y, gz(lp.x, lp.y)), height=2.2, strength=0.9)
    rnd = random.Random(21)
    R_ = 5.2
    a_cam, a_mq = math.radians(-128), math.radians(-52)
    spots = []
    for k in range(19):
        a = math.radians(-200 + k * 220 / 18)
        if abs(a - a_cam) < math.radians(9) or abs(a - a_mq) < math.radians(7):
            continue
        r = R_ + rnd.uniform(-0.25, 0.35) + (1.0 if k % 4 == 0 else 0)
        x, y = lp.x + r * math.cos(a), lp.y + r * math.sin(a)
        spots.append((x, y, (lp.x, lp.y)))
    for k in range(8):  # zweite Reihe dahinter
        a = math.radians(-190 + k * 200 / 7 + 8)
        x, y = lp.x + (R_ + 1.6) * math.cos(a), lp.y + (R_ + 1.6) * math.sin(a)
        if abs(a - a_cam) < math.radians(14):
            continue
        spots.append((x, y, (lp.x, lp.y)))
    ppl = companions(spots, seed=4, prefix="gf", weapon=None)
    for Pp in ppl:
        sp_ = bpy.data.objects.get(f"{Pp['name']}_sp")
    mq0 = Vector((lp.x + R_ * math.cos(a_mq), lp.y + R_ * math.sin(a_mq), 0))
    Mq = BW.warrior("miqdad", (mq0.x, mq0.y, gz(mq0.x, mq0.y)), yaw=Q.face_yaw(mq0.xy, lp.xy), side="m", seed=901, weapon="sword",
                    shield_=False, glow=True, cloak=(0.36, 0.28, 0.2))
    tm = ev("miqdad_e5")
    mq1 = lp + (mq0 - lp) * 0.7
    Q.walk(Mq, [mq0.xy, mq1.xy], tm - 0.4, speed=0.9)
    Q.idle(Mq, 0, D, seed=3)
    q0 = ls("q1")
    for t, sh, el in ((q0 + 0.2, -40, -60), (ev("kämpfen_q1") - 0.1 if "kämpfen_q1" in EV else q0 + 3.2, -95, -40),
                      ((ev("rechts_q1") if "rechts_q1" in EV else q0 + 4.5) - 0.1, -55, -30), (le("q1") + 0.3, -10, -20)):
        Q.arm_pose(Mq, t, "R", sh, el)
    if "links_q1" in EV:
        Q.arm_pose(Mq, ev("links_q1") - 0.1, "L", -55, -30)
        Q.arm_pose(Mq, le("q1") + 0.3, "L", -8, -15)
    for k, Pp in enumerate(ppl):  # alle schauen zu al-Miqdad, wenn er spricht
        Q.head_to(Pp, tm + 0.2 + 0.05 * k, (mq1.x, mq1.y, gz(mq1.x, mq1.y) + 1.6))
        Q.head_to(Pp, le("q1") + 0.3, (lp.x, lp.y, gz(lp.x, lp.y) + 1.5))
    glow_pulse(H, le("q1") - 0.5, peak=1.6)
    rig, shake, cam = Q.pov_camera(lens=17)
    c0 = P(lp.x + (R_ + 0.1) * math.cos(a_cam), lp.y + (R_ + 0.1) * math.sin(a_cam))
    lpz = (lp.x, lp.y, gz(lp.x, lp.y) + 1.4)
    ck(rig, [(0, c0, look(c0, (lp.x + 1.5, lp.y - 1.0, 1.5 + gz(lp.x, lp.y)))), (ls("e5") + 1.6, None, look(c0, lpz)),
                     (tm - 0.2, None, look(c0, (mq1.x, mq1.y, gz(mq1.x, mq1.y) + 1.5))),
                     (le("q1"), None, look(c0, (mq1.x - 0.3, mq1.y + 0.5, gz(mq1.x, mq1.y) + 1.55))), (D, None, look(c0, lpz))])
    Q.handheld(shake, 0, D, amp=0.4)
    return cfg


def shot_regen():
    """Nacht vor der Schlacht: Regen. Ich liege am Boden, ringsum Schlafende; der Sand wird dunkel und fest. Augen fallen zu."""
    cfg = BW.night(overcast=True, moon=2.6)
    BW.valley()
    rnd = random.Random(31)
    c = Vector((4.0, 44.0, 0))
    spots = [(0.2, 1.6, 1.57), (1.0, 3.0, 1.45), (-0.9, 4.4, 1.7), (0.6, 5.9, 1.5), (-0.3, 7.4, 1.62), (1.4, 8.9, 1.4), (-1.2, 10.3, 1.75),
             (2.8, 2.2, 0.2), (3.4, 5.2, 0.1), (-2.6, 2.4, 3.0), (-3.0, 6.0, 2.9)]
    for k, (dx, dy, yw) in enumerate(spots):
        BW.sleeper(f"sl{k}", (c.x + dx, c.y + dy), yw, seed=600 + k, side=rnd.choice((-1, 1)))
    for k, (x, y) in enumerate(((12, 52), (16, 47), (-4, 58))):
        MK.camel(f"nc{k}", (x, y, gz(x, y)), yaw=rnd.uniform(0, 6.28), seed=330 + k, sit=True, load=False)
    rig, shake, cam = Q.pov_camera(lens=17)
    c0 = (c.x - 0.4, c.y - 1.2, gz(c.x, c.y) + 0.34)
    BW.rain("rain", (c.x, c.y + 6, 0), c0, size=(22.0, 24.0, 12.0), n=1500, speed=9.5, t1=D + 1, seed=2, alpha=0.32)
    BW.wet_ground(ls("e6") + 2.0, ls("e6") + 6.5, amount=0.55)
    ts = ev("schlafen_e6") if "schlafen_e6" in EV else le("e6") - 1.0
    ck(rig, [(0, c0, (6, 2, -10)), (ls("e6") + 2.5, None, (2, 0, -12)), (ts - 1.0, None, (-4, 3, -14)), (D, None, (-6, 5, -16))])
    Q.handheld(shake, 0, D, amp=0.15)
    vs = Q.sc.view_settings
    vs.exposure = 0.0
    vs.keyframe_insert("exposure", frame=max(1, Q.T(ts - 0.6)))
    vs.exposure = -4.0
    vs.keyframe_insert("exposure", frame=Q.T(D))
    return cfg


def shot_baum():
    """Alle schlafen. Nur einer ist wach: unter dem Baum betet das Licht und neigt sich nieder, bis zum Morgen."""
    cfg = BW.night(moon=0.6)
    BW.valley()
    rnd = random.Random(41)
    for k in range(22):
        x, y = rnd.uniform(-8, 22), rnd.uniform(36, 56)
        if (Vector((x, y)) - TREE.xy).length < 4 or any((Vector((x, y)) - w.xy).length < 2.2 for w in WELLS):
            continue
        BW.sleeper(f"sl{k}", (x, y), rnd.uniform(0, 6.28), seed=640 + k, side=rnd.choice((-1, 1)))
    lp = Vector((TREE.x - 0.4, TREE.y - 1.6, 0))
    H = prophet("nur", (lp.x, lp.y, gz(lp.x, lp.y)), height=2.2, strength=1.0, day=False)
    # Gebet: stehen – sich verneigen – niederwerfen – sitzen (die Säule wird niedriger/höher)
    t = 0.0
    seq = [(0.0, 2.2), (1.6, 2.2), (2.1, 1.5), (3.2, 1.5), (3.7, 2.2), (4.4, 2.2), (5.0, 0.75), (6.6, 0.75), (7.1, 1.25), (8.2, 1.25),
           (8.7, 0.75), (D, 0.75)]
    for tt, h in seq:
        scale_h(H, tt, h)
    if "weint_e7" in EV:
        glow_pulse(H, ev("weint_e7"), peak=1.5)
    rig, shake, cam = Q.pov_camera(lens=17)
    c0 = (4.0, 34.0, gz(4.0, 34.0) + 3.2)
    c1 = (lp.x - 6.0, lp.y - 7.0, gz(lp.x, lp.y) + 2.0)
    tgt0 = (12.0, 50.0, 0.5)
    lpz = (lp.x, lp.y, gz(lp.x, lp.y) + 1.0)
    tw = ev("wach_e7") if "wach_e7" in EV else ls("e7") + 1.0
    ck(rig, [(0, c0, look(c0, tgt0)), (tw - 0.2, None, look(c0, (14.0, 54.0, 0.5))), (D, c1, look(c1, lpz))], interp="BEZIER")
    Q.handheld(shake, 0, D, amp=0.12)
    # erstes Morgenlicht: Horizont wird heller (Welt-Stärke)
    bg = Q.sc.world.node_tree.nodes.get("Background")
    if bg:
        s = bg.inputs["Strength"]
        s.keyframe_insert("default_value", frame=max(1, Q.T(ls("e7") + 3.0)))
        s.default_value = s.default_value * 1.5
        s.keyframe_insert("default_value", frame=Q.T(D))
    return cfg


def battle_lines(t1, q_front=True, q_far=True, m_rows=True, cam=None, q_y=BW.LINE_Q, avoid=()):
    """Morgens: beide Heere stehen sich gegenüber (Muslime im Norden, Quraisch im Süden)."""
    rnd = random.Random(51)
    out = {"m": [], "q": [], "qh": []}
    if m_rows:
        for k in range(26):
            x = -15.0 + k * 1.2 + rnd.uniform(-0.15, 0.15)
            if abs(x - 0.4) < 0.9:
                continue
            Pp = BW.warrior(f"mr{k}", (x, BW.LINE_M + rnd.uniform(-0.2, 0.2), gz(x, BW.LINE_M)), yaw=Q.face_yaw((x, 0), (x, -10)), side="m",
                            seed=700 + k, weapon=rnd.choice(["sword", "spear", "sword", "bow"]))
            Q.idle(Pp, 0, t1, seed=k)
            out["m"].append(Pp)
        BW.far_army("mrow", -60.0, 60.0, BW.LINE_M + 1.5, BW.LINE_M + 7.0, 200, side="m", seed=9, banners=2, facing=math.pi,
                    avoid=list(avoid) + [(0.0, BW.LINE_M, 18.0)])
    if q_front:
        for k in range(12):
            x = -26.0 + k * 4.6 + rnd.uniform(-1, 1)
            y = q_y + rnd.uniform(-1.5, 1.5)
            Hh = BW.horse(f"qh{k}", (x, y, gz(x, y)), yaw=math.pi, seed=800 + k)
            BW.mounted(f"qhr{k}", Hh, side="q", seed=820 + k, weapon=rnd.choice(["spear", "sword"]), helmet=True, mail=True)
            out["qh"].append(Hh)
        for k in range(22):
            x = -30.0 + k * 2.8 + rnd.uniform(-0.6, 0.6)
            y = q_y + 3.5 + rnd.uniform(-0.6, 0.6)
            Pp = BW.warrior(f"qi{k}", (x, y, gz(x, y)), yaw=math.pi, side="q", seed=850 + k, weapon=rnd.choice(["sword", "spear"]))
            Q.idle(Pp, 0, t1, seed=k + 9)
            out["q"].append(Pp)
        for k in range(5):
            x = -24.0 + k * 12.0
            BW.banner(f"qb{k}", (x, q_y - 1.0, gz(x, q_y - 1.0)), [BW.M["flag_r"], BW.M["flag_k"], BW.M["flag_y"]][k % 3], pole_h=4.3,
                      size=(1.4, 0.95), wind=1.2)
    if q_far:
        BW.far_army("qrow", -90.0, 90.0, q_y - 18.0, q_y - 4.0, 700, n_horse=60, n_camel=30, side="q", seed=11, banners=7)
    return out


def shot_reihen():
    """Morgen: ich stehe in der vordersten Reihe. Gegenüber das große Heer. Dann Blick zurück: auf der Anhöhe das Licht, Hände erhoben."""
    cfg = BW.daylight("morning", dust=0.15)
    BW.valley()
    battle_lines(D + 1)
    rnd = random.Random(52)
    for k in range(16):  # zweite und dritte Reihe hinter mir (echte Figuren, die Kamera dreht sich zu ihnen um)
        x = -9.0 + (k % 8) * 2.3 + rnd.uniform(-0.3, 0.3)
        y = BW.LINE_M + 1.6 + (k // 8) * 1.5
        Pp = BW.warrior(f"mb{k}", (x, y, gz(x, y)), yaw=Q.face_yaw((x, y), (x, -10)), side="m", seed=760 + k,
                        weapon=rnd.choice(["sword", "spear", "none"]))
        Q.idle(Pp, 0, D, seed=k + 3)
    lp = Vector((ARISH.x, ARISH.y + 0.3, 0))
    H = prophet("nur", (lp.x, lp.y, gz(lp.x, lp.y)), height=2.2, strength=0.95)
    ab = BW.warrior("abubakr", (lp.x + 0.6, lp.y + 1.3, gz(lp.x, lp.y)), yaw=Q.face_yaw((lp.x + 0.6, lp.y + 1.3), (lp.x, lp.y - 3)), side="m",
                    seed=911, weapon="none", shield_=False, glow=True, cloak=(0.82, 0.78, 0.68))
    Q.idle(ab, 0, D, seed=4)
    th = ev("hände_e8") if "hände_e8" in EV else le("e8") - 0.6
    glow_pulse(H, th, peak=2.2)
    rig, shake, cam = Q.pov_camera(lens=21)
    c0 = P(0.4, BW.LINE_M - 0.2)
    tq = ev("qibla_e8") if "qibla_e8" in EV else ls("e8") + 2.6
    lpz = (lp.x, lp.y, gz(lp.x, lp.y) + 1.5)
    ck(rig, [(0, c0, look(c0, (-6.0, BW.LINE_Q, 2.0))), (tq - 1.6, None, look(c0, (6.0, BW.LINE_Q, 2.0))),
                     (tq + 0.2, None, look(c0, lpz)), (D, None, look(c0, (lp.x + 0.3, lp.y, gz(lp.x, lp.y) + 1.7)))])
    Q.handheld(shake, 0, D, amp=0.5)
    return cfg


def shot_gebet():
    """Am Schattendach: das Licht betet zur Qibla. Der Umhang fällt; Abu Bakr legt ihn zurück und hält ihn von hinten."""
    cfg = BW.daylight("morning", dust=0.1)
    BW.valley()
    battle_lines(D + 1, q_front=False, m_rows=False)
    BW.far_army("mrow2", -50.0, 50.0, BW.LINE_M - 2.0, BW.LINE_M + 6.0, 320, side="m", seed=19, banners=2, facing=math.pi)
    ag = ARISH
    lp = Vector((ag.x, ag.y + 0.2, 0))
    zg = gz(lp.x, lp.y)
    H = prophet("nur", (lp.x, lp.y, zg), height=2.2, strength=0.95)
    # Licht leuchtet bei den Worten des Bittgebets auf
    for k_ in ("versprochen_q2", "schar_q2", "untergeht_q2"):
        if k_ in EV:
            glow_pulse(H, ev(k_), peak=1.5)
    # Umhang: fällt aus dem Licht zu Boden (vor dem Licht), Abu Bakr hebt ihn auf und legt ihn zurück
    tu = ev("umhang_e9") if "umhang_e9" in EV else ls("e9") + 1.5
    tz = ev("zurück_e9") if "zurück_e9" in EV else le("e9") - 1.0
    mc = Q.pbr("cloak_n", (0.18, 0.2, 0.14), 0.95, var=0.1, scale=5, bump=0.1, bscale=30)
    cl = Q.loft("umhang", [(-0.5, 0.26, 0.08, 0, 0.0), (-0.2, 0.3, 0.1, 0, 0.0), (0.15, 0.33, 0.09, 0, 0.01), (0.3, 0.22, 0.06)], mc,
                seg=28, folds=(6, 0.18, 0.05, 3))
    gfloor = (lp.x + 0.1, lp.y - 0.75, zg + 0.06)
    keys = [(0.0, (lp.x, lp.y, zg + 1.35), (0, 0, 0), 0.001), (tu - 0.25, (lp.x, lp.y, zg + 1.35), (0, 0, 0), 0.001),
            (tu, (lp.x, lp.y - 0.2, zg + 1.3), (0.2, 0, 0), 1.0), (tu + 0.45, (lp.x + 0.05, lp.y - 0.55, zg + 0.6), (0.9, 0.2, 0.3), 1.0),
            (tu + 0.8, gfloor, (1.5, 0.1, 0.5), 1.0)]
    ab0 = Vector((lp.x + 0.9, lp.y + 0.9, 0))
    abp = Vector((lp.x + 0.75, lp.y - 0.85, 0))
    abm = Vector((lp.x + 0.9, lp.y - 0.1, 0))
    abb = Vector((lp.x + 0.1, lp.y + 0.55, 0))
    t_w0 = tu + 0.9
    t_arr = t_w0 + (ab0.xy - abp.xy).length / 1.1
    t_pick = t_arr + 0.3
    keys += [(t_pick - 0.2, gfloor, (1.5, 0.1, 0.5), 1.0), (t_pick + 0.4, (abp.x - 0.3, abp.y + 0.1, zg + 1.0), (0.6, 0, 0.3), 1.0),
             (t_pick + 1.6, (lp.x, lp.y, zg + 1.35), (0.15, 0, 0), 0.9), (t_pick + 2.0, (lp.x, lp.y, zg + 1.35), (0, 0, 0), 0.001)]
    for t, p, r, s_ in keys:
        cl.location = p
        cl.rotation_euler = r
        cl.scale = (s_, s_, s_)
        for dp in ("location", "rotation_euler", "scale"):
            cl.keyframe_insert(dp, frame=max(1, Q.T(t)))
    ab = BW.warrior("abubakr", (ab0.x, ab0.y, zg), yaw=Q.face_yaw(ab0.xy, (lp.x, lp.y - 2)), side="m", seed=911, weapon="none",
                    shield_=False, glow=True, cloak=(0.82, 0.78, 0.68))
    Q.idle(ab, 0, D, seed=4)
    Q.hold(ab, 0.0, t_w0)
    Q.walk(ab, [ab0.xy, abp.xy], t_w0, speed=1.1)
    Q.hold(ab, t_arr, t_pick + 1.8)
    ch = ab["chest"]
    for t, bx in ((t_pick - 0.5, 0.0), (t_pick - 0.1, 0.75), (t_pick + 0.4, 0.0)):
        ch.rotation_euler = (bx, 0, 0)
        ch.keyframe_insert("rotation_euler", frame=Q.T(t))
    Q.arm_pose(ab, t_pick - 0.1, "L", -70, -10)
    Q.arm_pose(ab, t_pick - 0.1, "R", -70, -10)
    Q.arm_pose(ab, t_pick + 1.4, "L", -110, -30)
    Q.arm_pose(ab, t_pick + 1.4, "R", -110, -30)
    Q.arm_pose(ab, t_pick + 2.0, "L", -10, -15)
    Q.arm_pose(ab, t_pick + 2.0, "R", -10, -15)
    t_w2 = t_pick + 1.9
    t_end2 = Q.walk(ab, [abp.xy, abm.xy, abb.xy], t_w2, speed=1.0)
    Q.hold(ab, t_end2, D)
    rr = ab["root"]
    rr.rotation_euler = (0, 0, Q.face_yaw(abb.xy, lp.xy))
    rr.keyframe_insert("rotation_euler", index=2, frame=Q.T(t_end2 + 0.3))
    Q.arm_pose(ab, t_end2 + 0.4, "L", -75, -35, sh_y=-25)
    Q.arm_pose(ab, t_end2 + 0.4, "R", -75, -35, sh_y=25)
    # Wächter am Schattendach
    for k, (dx, dy) in enumerate(((3.4, 1.8), (-3.0, -1.2))):
        g = BW.warrior(f"wache{k}", (lp.x + dx, lp.y + dy, gz(lp.x + dx, lp.y + dy)), yaw=Q.face_yaw((lp.x + dx, lp.y + dy), (lp.x + dx, 0)),
                       side="m", seed=930 + k, weapon="sword", shield_=True, mail=True, helmet=(k == 0))
        Q.idle(g, 0, D, seed=k + 30)
    rig, shake, cam = Q.pov_camera(lens=17)
    c0 = P(lp.x + 5.4, lp.y - 4.4, 1.75)
    c1 = P(lp.x + 4.3, lp.y - 3.5, 1.72)
    lpz = (lp.x, lp.y, zg + 1.3)
    ck(rig, [(0, c0, look(c0, (lp.x - 0.3, lp.y, zg + 1.6))), (tu - 0.4, None, look(c0, lpz)),
                     (tu + 0.6, None, look(c0, (lp.x, lp.y - 0.4, zg + 0.6))), (t_w0 + 0.4, c1, look(c1, (lp.x + 0.5, lp.y - 0.3, zg + 0.9))),
                     (t_pick + 1.6, None, look(c1, (lp.x, lp.y, zg + 1.3))), (t_end2 + 0.6, None, look(c1, (lp.x, lp.y + 0.3, zg + 1.45))), (D, None, look(c1, (lp.x, lp.y + 0.3, zg + 1.5)))])
    Q.handheld(shake, 0, D, amp=0.35)
    return cfg


def shot_engel():
    """Blick in den Himmel über dem Schlachtfeld: Lichtstreifen kommen herab, einer nach dem anderen."""
    cfg = BW.daylight("morning", dust=0.25)
    BW.valley()
    battle_lines(D + 1, q_front=False)
    rnd = random.Random(61)
    t0 = max(0.4, ls("e10") + 1.2)
    k = 0
    for wave in range(9):
        for j in range(5):
            ts = t0 + wave * 0.55 + j * 0.11 + rnd.uniform(0, 0.08)
            if ts > D - 0.3:
                continue
            x0 = -90.0 + j * 45.0 + rnd.uniform(-12, 12)
            p0 = (x0, -120.0 + rnd.uniform(-30, 30), 230.0 + rnd.uniform(-30, 30))
            p1 = (x0 * 0.35 + rnd.uniform(-8, 8), -40.0 + rnd.uniform(-12, 12), 3.0)
            BW.light_rider(f"lr{k}", p0, p1, ts, rnd.uniform(2.2, 2.8), length=rnd.uniform(16, 24), width=rnd.uniform(1.0, 1.5),
                           strength=1.0, lamp=1500.0)
            k += 1
    for j, ts in enumerate((ls("e10") + 2.2, ls("e10") + 3.6)):
        BW.light_rider(f"lrn{j}", (6.0 - 12 * j, 60.0, 30.0), (-4.0 + 8 * j, -40.0, 2.0), ts, 1.2, length=9.0, width=0.6, lamp=900.0)
    rig, shake, cam = Q.pov_camera(lens=17)
    c0 = P(1.2, BW.LINE_M - 0.3)
    ck(rig, [(0, c0, (176, 4, 0)), (ls("e10") + 1.0, None, (172, 22, 0)), (D * 0.7, None, (168, 26, 0)), (D, None, (176, 12, 0))])
    Q.handheld(shake, 0, D, amp=0.4)
    return cfg


def pov_fighter(cam, sword_=False, shield_=True):
    """Eigene Hände (Ich-Sicht) mit Schwert rechts und Schild links (unten am Bildrand)."""
    Hh = MK.pov_arms(cam, skin=(0.42, 0.28, 0.19), sleeve=(0.72, 0.66, 0.55))
    if sword_:
        BW.sword("pov_sword", Hh["R"], rot=(math.radians(-90), 0, 0), loc=(0, 0.05, -0.02))
    if shield_:
        BW.shield("pov_shield", Hh["L"], loc=(0.0, 0.06, 0.05), r=0.27)
    return Hh


POV_REST = {"R": ((0.26, -0.4, -0.48), (-62, 12, 28)), "L": ((-0.36, -0.5, -0.5), (-80, -15, -40))}
POV_BLOCK = {"L": ((-0.08, -0.1, -0.5), (-12, -6, -8))}


def hand_pose(Hh, t, side, loc, rot):
    w = Hh[side]
    w.location = loc
    w.rotation_euler = [math.radians(a) for a in rot]
    w.keyframe_insert("location", frame=max(1, Q.T(t)))
    w.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))


def shot_sturm():
    """Der Zusammenprall: das Heer der Quraisch stürmt heran (Reiter, Fußvolk, Staub), wir rennen los. Schnitt vor dem Aufprall."""
    cfg = BW.daylight("morning", dust=0.35)
    BW.valley()
    rnd = random.Random(71)
    t1 = D + 1
    rig, shake, cam = Q.pov_camera(lens=17)
    for k in range(10):  # Reiter galoppieren heran
        x = -22.0 + k * 4.6 + rnd.uniform(-1, 1)
        y = -33.0 - rnd.uniform(0, 6)
        Hh = BW.horse(f"sh{k}", (x, y, gz(x, y)), yaw=math.pi, seed=1000 + k)
        R = BW.mounted(f"shr{k}", Hh, side="q", seed=1020 + k, weapon=rnd.choice(["sword", "spear"]), helmet=True, mail=True)
        Q.arm_pose(R, 0, "R", -150, -40)
        BW.horse_run(Hh, [(x, y), (x + rnd.uniform(-2, 2), y + 8.0 * t1)], 0.0, speed=8.0, stride=2.8)
        BW.hoof_dust(f"hd{k}_", Hh, 0.0, D, cam, every=0.3, alpha=0.32, seed=k)
    for k in range(18):  # Fußvolk rennt heran
        x = -24.0 + k * 2.8 + rnd.uniform(-0.6, 0.6)
        y = -21.0 - rnd.uniform(0, 5)
        Pp = BW.warrior(f"sq{k}", (x, y, gz(x, y)), yaw=math.pi, side="q", seed=1050 + k, weapon=rnd.choice(["sword", "spear"]))
        Q.arm_pose(Pp, 0, "R", -140 if k % 2 else -40, -40)
        Q.arm_pose(Pp, 0, "L", -60, -60)
        ground_walk(Pp, [(x, y), (x, y + 5.0 * t1)], 0.0, 5.0, run=True)
    for k in range(10):  # Muslime neben mir rennen los
        x = -7.0 + k * 1.5 + rnd.uniform(-0.2, 0.2)
        if abs(x) < 1.0:
            continue
        y = BW.LINE_M + rnd.uniform(-1.0, 1.5)
        Pp = BW.warrior(f"sm{k}", (x, y, gz(x, y)), yaw=0.0, side="m", seed=1080 + k, weapon="sword")
        Q.arm_pose(Pp, 0, "R", -150, -40)
        ground_walk(Pp, [(x, y), (x, y - 4.6 * t1)], 0.25 + rnd.uniform(0, 0.3), 4.6, run=True)
    A = BW.far_army("qfar", -80.0, 80.0, -58.0, -40.0, 500, n_horse=40, side="q", seed=13, banners=6)
    BW.move(A, [(0, (0, 0, 0)), (t1, (0, 5.0 * t1, 0))])
    BW.dust_cloud("sd", (0, -40), (60, 10), 22, cam, 0.0, t1, seed=5, size=(14, 7), alpha=0.45, drift=(0.3, 3.0, 0.4))
    Hh = pov_fighter(cam, shield_=False)
    hand_pose(Hh, 0, "R", (0.3, -0.9, -0.3), (-80, 0, 10))
    hand_pose(Hh, 0, "L", (-0.3, -0.9, -0.3), (-80, 0, -10))
    c0 = P(0.3, BW.LINE_M - 0.2)
    c1 = P(0.3, BW.LINE_M - 0.2 - 4.4 * (D - 0.5))
    ck(rig, [(0, c0, (180, 0, 0)), (0.5, c0, (180, 1, 0)), (D, c1, (180, -2, 0))], loc_interp="BEZIER")
    Q.handheld(shake, 0, D, amp=1.4, walk_from=0.5, walk_to=D, walk_amp=1.8)
    return cfg


def shot_kampf():
    """Mitten im Kampf, dichter Staub im Gegenlicht: Silhouetten, ein Gegner schlägt zu – mein Schild fängt den Hieb (Funken);
    ein Pferd bäumt sich auf, Klingen kreuzen sich. Nur Schild und Klinge werden getroffen."""
    cfg = BW.daylight("morning", dust=0.85)
    BW.valley()
    rnd = random.Random(81)
    t1 = D + 1
    sd = MK.sun_dir(MK.LIGHT["morning"][0])
    fwd = Vector((sd.x, sd.y, 0)).normalized()   # Blick zur Sonne: Gegenlicht
    side = Vector((fwd.y, -fwd.x, 0))
    c = Vector((0.0, -14.0, 0))

    def at(f, s):
        p = c + fwd * f + side * s
        return (p.x, p.y)
    rig, shake, cam = Q.pov_camera(lens=17)
    # Kampfpaare im Staub
    pairs = [(5.0, -3.0), (8.0, 2.5), (11.0, -6.0), (13.0, 5.0), (6.5, 6.5), (16.0, 0.0)]
    for k, (f, s) in enumerate(pairs):
        pa = at(f, s - 0.75)
        pb = at(f + 0.3, s + 0.75)
        A = BW.warrior(f"da{k}", (pa[0], pa[1], gz(*pa)), yaw=Q.face_yaw(pa, pb), side="m", seed=1200 + k, weapon="sword")
        B = BW.warrior(f"db{k}", (pb[0], pb[1], gz(*pb)), yaw=Q.face_yaw(pb, pa), side="q", seed=1220 + k, weapon="sword")
        BW.duel(A, B, 0.0, t1, seed=k, period=1.0 + 0.2 * (k % 3))
        Q.idle(A, 0, t1, seed=k)
        Q.idle(B, 0, t1, seed=k + 50)
    # Gegner stürmt auf mich zu und schlägt zu (3,4–4,0 s): mein Schild fängt den Hieb
    e0 = at(8.0, 1.2)
    e1 = at(2.1, 0.3)
    En = BW.warrior("enemy", (e0[0], e0[1], gz(*e0)), yaw=Q.face_yaw(e0, at(0, 0)), side="q", seed=1300, weapon="sword", helmet=True, mail=True)
    BW.guard_pose(En, 0.0)
    ground_walk(En, [e0, e1], 2.4, 5.5, run=True)
    Q.arm_pose(En, 3.3, "R", -170, -60, sh_y=8)
    Q.arm_pose(En, 3.85, "R", -60, -10, sh_y=4)
    Q.arm_pose(En, 4.5, "R", -140, -40, sh_y=8)
    # Pferd bäumt sich auf (rechts, ~5,2 s)
    hp = at(5.0, 3.6)
    Hr = BW.horse("hr", (hp[0], hp[1], gz(*hp)), yaw=Q.face_yaw(hp, at(5.0, -2)), seed=1310, colour=2)
    Rr = BW.mounted("hrr", Hr, side="q", seed=1311, weapon="sword", helmet=True)
    Q.arm_pose(Rr, 4.8, "R", -165, -40)
    Q.arm_pose(Rr, 5.7, "R", -60, -10)
    BW.horse_rear(Hr, 5.15, dur=1.5)
    # Klingen kreuzen sich vorn (Funken)
    fa = at(3.2, 1.9)
    fb = at(3.4, 3.0)
    A = BW.warrior("fa", (fa[0], fa[1], gz(*fa)), yaw=Q.face_yaw(fa, fb), side="m", seed=1320, weapon="sword")
    B = BW.warrior("fb", (fb[0], fb[1], gz(*fb)), yaw=Q.face_yaw(fb, fa), side="q", seed=1321, weapon="sword")
    BW.guard_pose(A, 0)
    BW.guard_pose(B, 0)
    for t_ in (5.6, 6.3):
        BW.strike(A, t_)
        BW.block(B, t_)
    mid = Vector(((fa[0] + fb[0]) / 2, (fa[1] + fb[1]) / 2, gz(*fa) + 1.55))
    BW.sparks("spk_a", mid, 5.6, seed=1)
    BW.sparks("spk_b", mid, 6.3, seed=2)
    # Staub: Karten im Gegenlicht
    for k in range(26):
        f, s = rnd.uniform(2.0, 22.0), rnd.uniform(-10.0, 10.0)
        p = at(f, s)
        pz = gz(*p) + rnd.uniform(0.8, 2.4)
        a0 = rnd.uniform(-1.0, D * 0.7)
        BW.dust_card(f"kd{k}", (p[0], p[1], pz), (rnd.uniform(4, 8), rnd.uniform(2.5, 4.5)), cam, a0, a0 + rnd.uniform(2.5, 4.5),
                     rnd.uniform(0.35, 0.6), grow=1.6, drift=(rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), 0.35), fade_in=0.6, fade_out=1.2)
    BW.far_army("kfar", -70.0, 70.0, -40.0, -20.0, 300, n_horse=30, side="q", seed=15, banners=5)
    # Ich: Schwert + Schild; Schild hoch beim Hieb, Ruck
    Hh = pov_fighter(cam)
    hand_pose(Hh, 0, "R", (0.3, -0.9, -0.3), (-80, 0, 10))
    hand_pose(Hh, 0, "L", *POV_REST["L"])
    hand_pose(Hh, 3.45, "L", *POV_REST["L"])
    hand_pose(Hh, 3.72, "L", *POV_BLOCK["L"])
    hand_pose(Hh, 3.95, "L", (-0.1, -0.13, -0.44), (-16, -8, -12))
    hand_pose(Hh, 4.7, "L", *POV_REST["L"])
    imp = 3.88
    # Funken am Rand meines Schildes (Welt-Position zur Zeit des Treffers)
    c0 = P(*at(-0.6, 0.0))
    cm = P(*at(0.6, 0.15))
    yaw0 = Q.yaw_to(c0, (*at(10, 0), 0))
    ck(rig, [(0, c0, (yaw0 + 8, 2, 0)), (2.3, None, (yaw0 - 4, 3, 0)), (3.2, cm, (yaw0 - 2, 4, 0)), (imp, None, (yaw0 - 3, 7, -4)),
                     (imp + 0.25, None, (yaw0 - 1, 2, 2)), (4.8, None, (yaw0 - 26, 6, 0)), (D, None, (yaw0 - 18, 3, 0))])
    Q.handheld(shake, 0, D, amp=1.2, walk_from=0, walk_to=3.2, walk_amp=1.0)
    Q.sc.frame_set(Q.T(imp))
    sp = (cam.matrix_world @ Vector((-0.06, 0.1, -0.62)))
    Q.sc.frame_set(1)
    BW.sparks("spk_s", sp, imp, n=34, seed=3, lamp=260.0)
    return cfg


def shot_jagd():
    """Ich jage einem Gegner nach durch den Staub. Über mir: ein Lichtstreif + Peitschenknall. Der Gegner stürzt. Ich drehe um
    und gehe zum Licht auf der Anhöhe, um es zu erzählen."""
    cfg = BW.daylight("morning", dust=0.75)
    BW.valley()
    rnd = random.Random(91)
    t1 = D + 1
    rig, shake, cam = Q.pov_camera(lens=17)
    tp = ev("peitschenknall_e13") if "peitschenknall_e13" in EV else ls("e13") + 3.5
    tf = ev("stürzt_e14") if "stürzt_e14" in EV else ls("e14") + 0.6
    te = ev("erzählt_e14") if "erzählt_e14" in EV else ls("e14") + 2.0
    sp = 4.2
    y_stop = 2.0 - sp * (tf - 0.3)
    en_path = [(3.0, -2.0), (3.6, -2.0 - 5.0 * t1)]
    En = BW.warrior("flee", (3.0, -2.0, gz(3.0, -2.0)), yaw=0.0, side="q", seed=1400, weapon="none", shield_=False, helmet=True, mail=True)
    # Flucht: läuft bis zum Sturz, dann liegt er (kein Blut)
    yf = -2.0 - 4.4 * tf
    ground_walk(En, [(3.0, -2.0), (3.4, yf)], 0.0, 4.4, run=True)
    Q.head_to(En, 1.4, (3.0, 4.0, 1.6))
    Q.head_to(En, 2.2, (3.4, -40.0, 1.6))
    BW.fall_back(En, tf, dur=0.65)
    # andere Kämpfe im Staub ringsum
    for k, (x, y) in enumerate(((-6, -10), (11, -16), (-9, -26), (13, -34), (-4, -40), (9, -48))):
        A = BW.warrior(f"ja{k}", (x, y, gz(x, y)), yaw=Q.face_yaw((x, y), (x + 1.4, y)), side="m", seed=1410 + k, weapon="sword")
        B = BW.warrior(f"jb{k}", (x + 1.5, y, gz(x + 1.5, y)), yaw=Q.face_yaw((x + 1.5, y), (x, y)), side="q", seed=1430 + k, weapon="sword")
        BW.duel(A, B, 0.0, t1, seed=k)
    for k in range(4):  # fliehende Reiter
        x, y = rnd.uniform(-20, 20), -30.0 - k * 6
        Hh = BW.horse(f"jh{k}", (x, y, gz(x, y)), yaw=0.0, seed=1450 + k)
        BW.mounted(f"jhr{k}", Hh, side="q", seed=1460 + k, weapon="none", shield_=False)
        BW.horse_run(Hh, [(x, y), (x + rnd.uniform(-6, 6), y - 8.0 * t1)], rnd.uniform(0, 2), speed=8.0)
    # Licht-Streif über mir (Peitschenknall) + kurzer Lichtblitz
    BW.light_rider("lr_whip", (0.0, 12.0, 9.0), (6.0, -60.0, 4.0), tp - 0.15, 0.75, length=8.0, width=0.6, lamp=1200.0)
    # Staub
    for k in range(30):
        x, y = rnd.uniform(-14, 18), rnd.uniform(-60, 0)
        a0 = rnd.uniform(-1.0, D * 0.6)
        BW.dust_card(f"jd{k}", (x, y, gz(x, y) + rnd.uniform(0.8, 2.2)), (rnd.uniform(5, 9), rnd.uniform(2.5, 4)), cam, a0, a0 + rnd.uniform(3, 5),
                     rnd.uniform(0.3, 0.5), grow=1.6, drift=(rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), 0.3))
    BW.dust_card("fall_puff", (3.4, yf + 1.0, gz(3.4, yf) + 0.6), (4.2, 2.6), cam, tf + 0.12, tf + 3.2, 0.9, grow=2.0, drift=(0.2, 0, 0.3),
                 fade_in=0.25, fade_out=1.4)
    BW.dust_card("fall_puff2", (2.6, yf + 1.6, gz(3.4, yf) + 0.9), (3.6, 2.2), cam, tf + 0.2, tf + 3.0, 0.7, grow=2.2, drift=(-0.2, 0, 0.3),
                 fade_in=0.3, fade_out=1.4)
    # das Licht auf der Anhöhe (weit hinten), Gefährten davor
    lp = Vector((ARISH.x, ARISH.y + 0.3, 0))
    H = prophet("nur", (lp.x, lp.y, gz(lp.x, lp.y)), height=2.2, strength=1.0)
    Hh = pov_fighter(cam, shield_=False)
    hand_pose(Hh, 0, "R", (0.3, -0.9, -0.3), (-80, 0, 10))
    hand_pose(Hh, 0, "L", (-0.3, -0.9, -0.3), (-80, 0, -10))
    c0 = P(3.0, 1.6)
    cs = P(3.2, yf + 4.6)
    ck(rig, [(0, c0, (182, -2, 0)), (tp - 0.3, None, (182, 0, 0)), (tp + 0.1, None, (184, 14, 0)), (tp + 0.7, None, (182, 2, 0)),
                     (tf - 0.3, None, None), (tf + 0.4, cs, (182, 0, 0)), (tf + 0.9, None, (170, 1, 0)),
                     (tf + 2.4, None, (look(cs, (lp.x, lp.y, gz(lp.x, lp.y) + 1.4))[0], -1, 0)),
                     (D, P(2.6, yf + 6.4), (look(cs, (lp.x, lp.y, gz(lp.x, lp.y) + 1.4))[0], 0, 0))])
    # Position bis zum Sturz linear (Rennen), danach ruhig
    r = rig
    for fc in Q.fcurves(r):
        if fc.data_path == "location":
            for kp in fc.keyframe_points:
                if kp.co.x <= Q.T(tf + 0.4):
                    kp.interpolation = "LINEAR"
    Q.handheld(shake, 0, D, amp=1.0, walk_from=0, walk_to=tf + 0.3, walk_amp=1.8)
    return cfg


def shot_ende():
    """Der Staub legt sich: in der Ferne fliehen die Quraisch. Vorn liegt eine Fahne im Sand. Gefangene sitzen in einer Reihe."""
    cfg = BW.daylight("day", dust=0.3)
    BW.valley()
    rnd = random.Random(101)
    t1 = D + 1
    rig, shake, cam = Q.pov_camera(lens=17)
    A = BW.far_army("flee_far", -90.0, 90.0, -120.0, -80.0, 260, n_horse=40, n_camel=20, side="q", seed=17, banners=2)
    BW.move(A, [(0, (0, 0, 0)), (t1, (0, -5.0 * t1, 0))])
    for k in range(6):
        x, y = rnd.uniform(-40, 40), rnd.uniform(-75, -55)
        Hh = BW.horse(f"eh{k}", (x, y, gz(x, y)), yaw=0.0, seed=1500 + k)
        BW.mounted(f"ehr{k}", Hh, side="q", seed=1510 + k, weapon="none", shield_=False)
        BW.horse_run(Hh, [(x, y), (x + rnd.uniform(-6, 6), y - 8.0 * t1)], 0.0, speed=8.0)
    BW.dust_cloud("ed", (0, -95), (70, 15), 14, cam, 0.0, t1, seed=6, size=(18, 7), alpha=0.35, drift=(0.2, -2.0, 0.3))
    # Fahne im Sand, Schild, Schwert
    fl = BW.banner("fallen", (-1.2, -21.0, gz(-1.2, -21.0) + 0.06), BW.M["flag_r"], pole_h=3.2, size=(1.1, 0.8),
                   rot=(math.radians(88), 0, math.radians(30)), wind=0.15)
    shd = Q.empty("shd_r", (1.8, -19.6, gz(1.8, -19.6) + 0.05), rot=(math.radians(-90), 0, 0.4))
    BW.shield("lost_shield", shd, loc=(0, 0, 0))
    sw = Q.empty("sw_r", (0.6, -18.4, gz(0.6, -18.4) + 0.02), rot=(0, 0, 0.8))
    BW.sword("lost_sword", sw, rot=(math.radians(90), 0, 0), loc=(0, 0, 0))
    # Gefangene sitzen in einer Reihe (Hände hinter dem Rücken), zwei Wächter
    gx, gy = 7.0, -15.0
    for k in range(7):
        x, y = gx + k * 0.95, gy - k * 0.25
        Pp = BW.warrior(f"cap{k}", (x, y, gz(x, y)), yaw=Q.face_yaw((x, y), (x - 6, y + 4)), side="q", seed=1550 + k, weapon="none",
                        shield_=False, sit=True, helmet=False, mail=False)
        Q.arm_pose(Pp, 0, "L", 40, -35, sh_y=15)
        Q.arm_pose(Pp, 0, "R", 40, -35, sh_y=-15)
        Pp["head"].rotation_euler = (math.radians(18), 0, 0)
    for k, (x, y) in enumerate(((gx - 1.4, gy + 1.6), (gx + 7.6, gy - 0.3))):
        g = BW.warrior(f"gw{k}", (x, y, gz(x, y)), yaw=Q.face_yaw((x, y), (gx + 3, gy)), side="m", seed=1570 + k, weapon="spear", shield_=False)
        Q.arm_pose(g, 0, "R", -18, -70)
        Q.idle(g, 0, D, seed=k)
    for k in range(5):  # Muslime gehen über das Feld
        x, y = rnd.uniform(-12, 12), rnd.uniform(-35, -25)
        Pp = BW.warrior(f"ew{k}", (x, y, gz(x, y)), side="m", seed=1580 + k, weapon="sword", shield_=rnd.random() < 0.5)
        ground_walk(Pp, [(x, y), (x + rnd.uniform(-3, 3), y + 6)], rnd.uniform(0, 2), 1.0)
    c0 = P(-3.5, -12.5)
    c1 = P(-2.5, -14.0)
    tg = ev("gefangen_e15") if "gefangen_e15" in EV else le("e15") - 1.4
    ck(rig, [(0, c0, look(c0, (-2, -90, 3))), (ls("e15") + 1.8, None, look(c0, (6, -90, 3))), (tg - 1.0, None, look(c0, (0.2, -21, 0.4))),
                     (tg + 0.4, c1, look(c1, (gx + 3.0, gy, 0.9))), (D, None, look(c1, (gx + 3.4, gy - 0.4, 0.8)))])
    Q.handheld(shake, 0, D, amp=0.4, walk_from=tg - 0.6, walk_to=tg + 0.6, walk_amp=0.5)
    return cfg


def shot_abend():
    """Sonnenuntergang: die Muslime beten in Reihen zur Qibla (Süden), vorne das Licht. Die Kamera steigt auf: das ganze Tal."""
    cfg = BW.daylight("golden")
    BW.valley()
    rnd = random.Random(111)
    lp = Vector((0.0, 12.0, 0))
    H = prophet("nur", (lp.x, lp.y, gz(lp.x, lp.y)), height=2.2, strength=0.95)
    rows = []
    for r_ in range(4):
        for k in range(24):
            x = -13.6 + k * 1.18 + rnd.uniform(-0.05, 0.05)
            y = lp.y + 2.2 + r_ * 1.4
            Pp = BW.warrior(f"pr{r_}_{k}", (x, y, gz(x, y)), yaw=Q.face_yaw((x, y), (x, y - 5)), side="m", seed=1600 + r_ * 40 + k,
                            weapon="none", shield_=False, helmet=False)
            for s_ in ("L", "R"):
                Q.arm_pose(Pp, 0, s_, -40, -100, sh_y=(20 if s_ == "L" else -20))
            Pp["head"].rotation_euler = (math.radians(12), 0, 0)
            rows.append(Pp)
    BW.far_army("prfar", -70.0, -19.0, lp.y + 2.0, lp.y + 7.0, 110, side="m", seed=23, banners=0, spears=False)
    BW.far_army("prfar2", 19.0, 70.0, lp.y + 2.0, lp.y + 7.0, 110, side="m", seed=24, banners=0, spears=False)
    # Verneigung (Ruku): bei „geholfen“ – Oberkörper neigt sich, Hände auf die Knie
    tr = ev("geholfen_e16") if "geholfen_e16" in EV else ls("e16") + 2.4
    for Pp in rows:
        ch = Pp["chest"]
        for t, bx in ((tr - 0.4, 0.0), (tr + 0.4, 1.25), (tr + 2.6, 1.25), (tr + 3.3, 0.0)):
            ch.rotation_euler = (bx, 0, 0)
            ch.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))
        for s_ in ("L", "R"):
            Q.arm_pose(Pp, tr - 0.4, s_, -40, -100, sh_y=(20 if s_ == "L" else -20))
            Q.arm_pose(Pp, tr + 0.4, s_, -60, 0, sh_y=(8 if s_ == "L" else -8))
            Q.arm_pose(Pp, tr + 2.6, s_, -60, 0, sh_y=(8 if s_ == "L" else -8))
            Q.arm_pose(Pp, tr + 3.3, s_, -40, -100, sh_y=(20 if s_ == "L" else -20))
    scale_h(H, tr - 0.4, 2.2)
    scale_h(H, tr + 0.4, 1.45)
    scale_h(H, tr + 2.6, 1.45)
    scale_h(H, tr + 3.3, 2.2)
    rig, shake, cam = Q.pov_camera(lens=17)
    c0 = P(9.0, lp.y + 10.5)
    c1 = (30.0, lp.y + 40.0, gz(0, 0) + 30.0)
    tk = ls("e17")
    ck(rig, [(0, c0, look(c0, (0, lp.y + 1, 1.2))), (tk - 1.0, P(7.0, lp.y + 12.0), look(P(7.0, lp.y + 12.0), (0, lp.y + 1, 1.0))),
                     (D, c1, look(c1, (-10, -60, 0.0)))], interp="BEZIER")
    Q.handheld(shake, 0, D, amp=0.25)
    return cfg


SHOTS = {"medina": shot_medina, "kolonne": shot_kolonne, "auszug": shot_auszug, "heer": shot_heer, "rat": shot_rat, "regen": shot_regen,
         "baum": shot_baum, "reihen": shot_reihen, "gebet": shot_gebet, "engel": shot_engel, "sturm": shot_sturm, "kampf": shot_kampf,
         "jagd": shot_jagd, "ende": shot_ende, "abend": shot_abend}


def join_noshadow(prefixes=("peb", "sb", "tree_far"), small_rocks=0.55):
    """Kleinkram ohne Schatten zu EINEM Objekt (jedes Dreieck kostet je Sample)."""
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
for o in bpy.data.objects:  # Gelände wirft keinen Schatten auf sich selbst (sonst großes Vieleck-Muster bei tiefer Sonne)
    if o.name.startswith("terrain"):
        o.visible_shadow = False
if os.environ.get("NOSH", "1") == "1":
    join_noshadow()
if os.environ.get("JOIN", "1") == "1":
    MD.join_static(keep=("noshadow", "umhang", "lr", "spk", "rain", "moon_c", "terrain"))
if os.environ.get("TERR_FLAT"):
    mflat = Q.pbr("flat_test", (0.6, 0.5, 0.4), 0.9)
    for o in bpy.data.objects:
        if o.name.startswith("terrain"):
            o.data.materials[0] = mflat
if os.environ.get("TERR_NOSH"):
    for o in bpy.data.objects:
        if o.name.startswith("terrain"):
            o.visible_shadow = False
Q.render_setup(pct=PCT, samples=SAMPLES, mist_col=cfg["mist_col"], mist_amt=cfg["mist_amt"], shadow_res=0.5, sky_sep=True)
sc = bpy.context.scene
for o in bpy.data.objects:
    if o.type == "CAMERA":
        o.data.clip_end = 1200
if os.environ.get("NOCOMP"):
    sc.render.use_compositing = False
sc.frame_start, sc.frame_end = 1, SEG[SHOT]["frames"]
if os.environ.get("FRAMES"):
    sc.frame_start, sc.frame_end = map(int, os.environ["FRAMES"].split("-"))
import time as _time
print("SETUP_DONE", _time.time())
if os.environ.get("PRINT"):
    sc.frame_set(int(os.environ.get("PFRAME", "30")))
    cams = [o for o in bpy.data.objects if o.type == "CAMERA"]
    for c_ in cams:
        fw = c_.matrix_world.to_3x3() @ Vector((0, 0, -1))
        print("CAM", tuple(round(v, 2) for v in c_.matrix_world.translation), "fwd", tuple(round(v, 2) for v in fw))
    for o in bpy.data.objects:
        if o.name.startswith(tuple(os.environ["PRINT"].split(","))) and (o.parent is None or o.type == "MESH"):
            bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
            print("OBJ", o.name, o.type, "min", tuple(round(min(v[i] for v in bb), 1) for i in range(3)),
                  "max", tuple(round(max(v[i] for v in bb), 1) for i in range(3)))
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
