# QISSAH Folge 5 – „Die Hidschra – der Jäger in der Wüste“: alle Einstellungen in Blender. Aufruf:
#   blender -b --factory-startup --python blender/qissa/hijra.py -- <einstellung> <ausgabe_ordner> [prozent] [samples] [standbild-zeiten]
# Längen und Ereignisse: src/qissa_hijra/timeline.json (scripts/build_qissa_hijra.py).
# Regeln: der Prophet ﷺ NUR als Licht; Menschen ohne Gesicht; Abu Bakr (und Amir ibn Fuhaira) mit Licht über dem Kopf.
# Suraqa ist die Kamera (Ich-Sicht) – er wird nie gezeigt. Keine Koran-Rezitation im Bild/Ton.
import bpy, sys, os, math, json, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import lib as Q
import mekka as MK
import hijra_world as HW
import medina as MD
import kaaba_world as KW
import badr_world as BW

TL = json.load(open(os.environ.get("TL_FILE") or os.path.join(ROOT, "src", "qissa_hijra", "timeline.json"), encoding="utf-8"))
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
SHOT = argv[0] if argv else "stamm"
OUT = argv[1] if len(argv) > 1 else "/tmp/hijra"
PCT = int(argv[2]) if len(argv) > 2 else 50
SAMPLES = int(argv[3]) if len(argv) > 3 else 8
STILLS = [float(x) for x in argv[4].split(",")] if len(argv) > 4 and argv[4] else None

S0 = SEG[SHOT]["start"]
D = SEG[SHOT]["dur"]
EYE = 1.62
gz = HW.gz


def lt(t_abs):
    return t_abs - S0


def ls(i):
    return lt(LINE[i]["start"])


def le(i):
    return lt(LINE[i]["start"] + LINE[i]["dur"])


def ev(k, alt=None):
    if k in EV:
        return lt(EV[k])
    return alt


def P(x, y, eye=EYE):
    return (x, y, gz(x, y) + eye)


def look(src, dst):
    return (Q.yaw_to(src, dst), Q.pitch_to(src, dst), 0)


def ck(rig, keys, **kw):
    """Q.cam_keys, aber Gier-Winkel ohne Sprung über ±180°."""
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


def light_rider(C, day=True, strength=0.8):
    """Das Licht (der Prophet ﷺ) sitzt auf dem Kamel – kleinere Licht-Säule auf dem Sattel."""
    H = prophet(f"{C['name']}_nur", (0, 0, 0), height=1.45, strength=strength, day=day)
    H["root"].parent = C["body"]
    H["root"].location = (0, 0.05, 0.42)
    H["parts"][3].hide_render = True   # kein Boden-Schein in der Luft
    return H


def abu_bakr_rider(C, name="abubakr", seed=901, glow=True, robe=(0.86, 0.82, 0.72)):
    R = MK.rider(name, C, seed=seed, head="turban", glow=glow, robe=robe, wrap=(0.92, 0.9, 0.84))
    return R


def turn_back(R, keys):
    """Reiter dreht Oberkörper + Kopf nach hinten. keys = [(t, grad)] (0 = nach vorn, ± nach hinten links/rechts)."""
    for t, a in keys:
        R["chest"].rotation_euler = (0, 0, math.radians(a * 0.4))
        R["chest"].keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))
        R["head"].rotation_euler = (math.radians(-4 if a else 0), 0, math.radians(a * 0.6))
        R["head"].keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))


def caravan(x0, y0, t0, t1, speed=1.5, heading=0.0, stop=None, day=True, seed=0, guide=True, z_of=None):
    """Kamel 1: das Licht (der Prophet ﷺ); Kamel 2: Abu Bakr (+ Amir ibn Fuhaira hinten); Kamel 3: der Führer.
    heading = Richtung in Grad (0 = Norden +Y). stop = Zeit, ab der sie stehen bleiben."""
    hd = math.radians(heading)
    fv = Vector((-math.sin(hd), math.cos(hd), 0))
    sv = Vector((fv.y, -fv.x, 0))
    yaw = math.atan2(fv.x, -fv.y)
    out = {}
    t_end = stop if stop is not None else t1
    for k, (back, side) in enumerate(((0.0, 0.0), (5.2, 0.6), (10.6, -0.4))):
        if k == 2 and not guide:
            continue
        p = Vector((x0, y0, 0)) - fv * back + sv * side
        C = MK.camel(f"cv{k}", (p.x, p.y, gz(p.x, p.y)), yaw=yaw, seed=50 + k + seed, load=True)
        if t_end - t0 > 0.05:
            q = p + fv * speed * (t_end - t0)
            MK.camel_walk(C, [(p.x, p.y), (q.x, q.y)], t0, speed=speed, z_of=z_of)
        out[k] = C
    out["light"] = light_rider(out[0], day=day)
    out["ab"] = abu_bakr_rider(out[1])
    am = MK.rider("amir", out[1], seed=903, head="scarf", glow=True, robe=(0.62, 0.55, 0.44))
    am["root"].location = (0, 0.75, 0.42)
    out["amir"] = am
    if guide:
        out["guide"] = MK.rider("guide", out[2], seed=905, head="scarf", robe=(0.3, 0.24, 0.18))
    return out


# ---------------------------------------------------------------- Reiten (Ich-Sicht im Sattel)
def path_eval(path, d):
    pts = [Vector((p[0], p[1], 0)) for p in path]
    segs = list(zip(pts, pts[1:]))
    total = sum((b - a).length for a, b in segs)
    d = max(0.0, min(total, d))
    acc = 0.0
    for a, b in segs:
        L_ = (b - a).length
        if d <= acc + L_:
            return a + (b - a) * ((d - acc) / L_), (b - a).normalized(), total
        acc += L_
    return pts[-1], (segs[-1][1] - segs[-1][0]).normalized(), total


def path_len(path):
    return path_eval(path, 0)[2]


def ride(C, rig, path, t0, t1, speed, stride=2.8, yaw_off=None, pitch=0.0, trot=False, cam_from=None, run=True):
    """Pferd läuft path entlang (BW.horse_run); die Kamera sitzt im Sattel (Schlüssel je Bild von cam_from bis t1)."""
    if run:
        BW.horse_run(C, path, t0, speed=speed, stride=stride, trot=trot)
    amp = 0.5 if trot else 1.0
    for f in range(Q.T(cam_from if cam_from is not None else t0), Q.T(t1) + 1):
        t = (f - 1) / Q.FPS
        d = max(0.0, (t - t0) * speed)
        pos, dv, total = path_eval(path, d)
        moving = d < total
        ph = 2 * math.pi * d / stride
        bob = ((0.05 if trot else 0.09) * math.sin(2 * ph if trot else ph)) if moving else 0.0
        p = pos + dv * (-0.08)
        rig.location = (p.x, p.y, gz(pos.x, pos.y) + 1.18 + 0.36 + 0.9 + bob)
        rig.keyframe_insert("location", frame=f)
        yw = math.degrees(math.atan2(-dv.x, dv.y)) + (yaw_off(t) if yaw_off else 0.0)
        pt = pitch - (3.5 * amp * math.sin(ph + 0.8) if moving else 0.0)
        rig.rotation_euler = (math.radians(pt), math.radians(1.2 * math.sin(ph * 0.5) if moving else 0.0), math.radians(yw))
        rig.keyframe_insert("rotation_euler", frame=f)
    return t0 + path_len(path) / speed


RIDE_HANDS = {"L": ((-0.11, -0.43, -0.5), (-60, -6, -14)), "R": ((0.13, -0.42, -0.5), (-60, 6, 14))}


def hand_pose(Hh, t, side, loc, rot):
    w = Hh[side]
    w.location = loc
    w.rotation_euler = [math.radians(a) for a in rot]
    w.keyframe_insert("location", frame=max(1, Q.T(t)))
    w.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))


def pose(Hh, t, name, only=None):
    for side, (loc, rot) in POSES[name].items():
        if only and side != only:
            continue
        hand_pose(Hh, t, side, loc, rot)


POSES = {
    "reins": RIDE_HANDS,
    "hidden": {"L": ((-0.2, -0.95, -0.3), (-80, 0, -10)), "R": ((0.2, -0.95, -0.3), (-80, 0, 10))},
    "raise": {"R": ((0.13, 0.02, -0.62), (8, 0, -10))},
    "wave_a": {"R": ((0.15, 0.0, -0.6), (8, 0, -28))},
    "wave_b": {"R": ((0.1, 0.0, -0.6), (8, 0, 10))},
    "dismiss": {"R": ((0.18, -0.2, -0.46), (-40, 0, 40))},
    "dismiss2": {"R": ((0.26, -0.16, -0.42), (-30, 20, -10))},
    "offer": {"L": ((-0.07, -0.2, -0.48), (-80, 0, -10)), "R": ((0.07, -0.2, -0.48), (-80, 0, 10))},
    "low": {"L": ((-0.2, -0.5, -0.36), (-80, 0, -10)), "R": ((0.2, -0.5, -0.36), (-80, 0, 10))},
    "spear_low": {"R": ((0.2, -0.42, -0.36), (-95, 0, 8))},
    "arrows": {"L": ((-0.06, -0.2, -0.42), (-55, 0, -20)), "R": ((0.09, -0.22, -0.44), (-60, 0, 25))},
    "pull": {"R": ((0.14, -0.1, -0.5), (-25, 0, 10))},
    "look_arrow": {"R": ((0.05, -0.08, -0.4), (-15, 0, 80))},
    "throw": {"R": ((0.34, -0.3, -0.38), (-80, 0, 40))},
}


def fists(Hh, reins=True):
    """Ich-Hände als Fäuste (Finger eingerollt) + Zügel nach vorn."""
    ms = bpy.data.materials.get("pov_skin_h")
    for nm in ("L", "R"):
        for o in list(Hh[nm].children):
            if o.name.startswith(("pov_f", "pov_ft", "pov_th")):
                o.hide_render = True
        Q.ball(f"pov_fist.{nm}", (0, 0.085, -0.012), (0.042, 0.032, 0.03), ms, parent=Hh[nm], seg=16)
        Q.ball(f"pov_thumbk.{nm}", ((-0.03 if nm == "R" else 0.03), 0.07, 0.012), (0.014, 0.024, 0.013), ms, parent=Hh[nm], seg=10)
        if reins:
            Q.limb(f"pov_rein.{nm}", (0, 0.09, -0.03), ((0.08 if nm == "L" else -0.08), 0.75, -0.42), 0.006, 0.006, MK.M["leather"],
                   parent=Hh[nm], seg=6)


def pov_rider(cam, spear_=True):
    Hh = MK.pov_arms(cam, skin=(0.4, 0.26, 0.17), sleeve=(0.42, 0.32, 0.22))
    fists(Hh)
    if spear_:
        s = Q.empty("pov_spear_r", (0, 0.06, -0.01), Hh["R"], rot=(math.radians(-14), 0, math.radians(150)))
        BW.spear("pov_spear", s, length=2.4)
    return Hh


def suraqa_horse(name="sh", loc=(0, 0, 0), yaw=0.0):
    """Suraqas Pferd (Fuchs, ohne Sattel); Mähne als weicher Kamm statt Klötzchen (sieht man aus dem Sattel)."""
    C = BW.horse(name, loc, yaw=yaw, seed=11, colour=0, saddle=False)
    for k in range(9):
        o = bpy.data.objects.get(f"{name}_mane{k}")
        if o:
            bpy.data.objects.remove(o)
    mh = Q.pbr(f"{name}_manem", (0.07, 0.04, 0.025), 0.8, var=0.25, scale=30, bump=0.3, bscale=120)
    Q.limb(f"{name}_manes", (0, 0.12, 0.04), (0, -0.2, 0.66), 0.05, 0.032, mh, parent=C["neck"], seg=10)
    Q.ball(f"{name}_forelock", (0, -0.3, 0.7), (0.04, 0.05, 0.05), mh, parent=C["neck"], seg=10)
    return C


def fall_off(rig, shake, t, start, dv, side=1, back=0.0, lie_look=None, dur=0.55, fwd=2.6, out=2.0):
    """Kamera fällt vom Pferd: kippt zur Seite, schlägt im Sand auf (Ruck). Rückgabe: Liegeposition."""
    sv = Vector((dv.y, -dv.x, 0)) * side
    land = Vector(start) + dv * (fwd - back) + sv * out
    land.z = gz(land.x, land.y) + 0.32
    yw = math.degrees(math.atan2(-dv.x, dv.y))
    ck(rig, [(t, start, (yw, -10, 0)), (t + dur * 0.45, lerp3(start, tuple(land), 0.55), (yw - 20 * side, -35, -30 * side)),
             (t + dur, tuple(land), (yw - 35 * side, -14, -38 * side))])
    return land


def stumble(C, t, down=1.0, up=None):
    """Pferd stolpert: Vorderbeine knicken ein, Brust nach vorn unten (und steht wieder auf, wenn up gesetzt)."""
    body = C["body"]
    seq = [(t - 0.05, 0, 0.0, 0, 0), (t + 0.3, 24 * down, -0.42 * down, -45, 95), (t + 0.9, 20 * down, -0.38 * down, -40, 90)]
    if up:
        seq += [(up, 8, -0.1, -10, 30), (up + 0.6, 0, 0.0, 0, 0)]
    for tt, pt, dz, hip, knee in seq:
        body.rotation_euler = (math.radians(pt), 0, 0)
        body.location = (0, 0, 1.18 + dz)
        body.keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
        body.keyframe_insert("location", frame=max(1, Q.T(tt)))
        for nm in ("FL", "FR"):
            C[f"leg.{nm}"].rotation_euler = (math.radians(hip), 0, 0)
            C[f"knee.{nm}"].rotation_euler = (math.radians(knee), 0, 0)
            C[f"leg.{nm}"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
            C[f"knee.{nm}"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))


def horse_idle(C, t0, t1, seed=0):
    rnd = random.Random(seed)
    nk = C["neck"]
    t = t0
    while t < t1:
        nk.rotation_euler = (math.radians(rnd.uniform(-10, 14)), 0, math.radians(rnd.uniform(-12, 12)))
        nk.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))
        t += rnd.uniform(0.9, 1.8)
    tl = C["tail"]
    for f in range(Q.T(t0), Q.T(t1) + 1, 6):
        tt = (f - 1) / Q.FPS
        tl.rotation_euler = (math.radians(12 + 4 * math.sin(tt * 1.3)), 0, math.radians(10 * math.sin(tt * 2.1 + seed)))
        tl.keyframe_insert("rotation_euler", frame=f)


def sand_ring(name, loc, t, r=0.5):
    """Sandwulst um die eingesunkenen Beine (erscheint beim Einsinken)."""
    root = Q.empty(name, loc)
    for k in range(10):
        a = k * 0.63
        Q.ball(f"{name}_{k}", (r * 1.2 * math.cos(a), r * math.sin(a), 0.0), (0.34, 0.26, 0.09), MK.M["sand"], parent=root, seg=10)
    Q.cyl(f"{name}_pit", (0, 0, 0.012), r * 0.9, 0.01, Q.pbr(f"{name}_pm", (0.25, 0.19, 0.13), 1.0, var=0.2), parent=root, seg=20)
    root.scale = (0.001, 0.001, 0.001)
    root.keyframe_insert("scale", frame=1)
    root.keyframe_insert("scale", frame=max(1, Q.T(t)))
    root.scale = (1, 1, 1)
    root.keyframe_insert("scale", frame=max(1, Q.T(t + 0.35)))
    return root


def smoke_dust(prefix, loc, cam, t0, dur=6.0, n=16, seed=0, rise=1.4, alpha=0.6):
    """Staub steigt auf wie Rauch: viele Karten, die nach oben treiben und gross werden."""
    rnd = random.Random(seed)
    for k in range(n):
        a0 = t0 + k * 0.12 + rnd.uniform(0, 0.2)
        p = (loc[0] + rnd.uniform(-0.6, 0.6), loc[1] + rnd.uniform(-0.6, 0.6), loc[2] + rnd.uniform(0.2, 1.0))
        BW.dust_card(f"{prefix}{k}", p, (rnd.uniform(1.2, 2.0), rnd.uniform(1.6, 2.6)), cam, a0, a0 + dur * rnd.uniform(0.8, 1.1), alpha,
                     grow=rnd.uniform(2.0, 2.8), drift=(rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), rise * rnd.uniform(0.8, 1.2)),
                     fade_in=0.35, fade_out=1.8, col=(1.05, 0.95, 0.85))


def set_z(P_, t0, t1):
    """walk() hält z konstant: z je Schlüsselbild aus dem Gelände nachziehen."""
    fcs = Q.fcurves(P_["root"])
    xs = [f for f in fcs if f.data_path == "location" and f.array_index == 0]
    ys = [f for f in fcs if f.data_path == "location" and f.array_index == 1]
    if not xs or not ys:
        return
    r = P_["root"]
    for fr in range(Q.T(t0), Q.T(t1) + 1, 3):
        r.location.z = gz(xs[0].evaluate(fr), ys[0].evaluate(fr))
        r.keyframe_insert("location", index=2, frame=fr)


def pursuers(prefix, spots, seed=0, weapon=None):
    rnd = random.Random(seed)
    out = []
    for k, (x, y, yaw) in enumerate(spots):
        w = weapon or rnd.choice(["sword", "spear", "none"])
        Pp = BW.warrior(f"{prefix}{k}", (x, y, gz(x, y)), yaw=yaw, side="q", seed=rnd.randint(0, 9999), weapon=w, shield_=False)
        if w == "spear":
            Q.arm_pose(Pp, 0, "R", -18, -70)
        out.append(Pp)
    return out


# ============================================================ Mekka
def shot_mekka():
    """Nacht in Mekka: Männer der Quraisch beraten am Feuer in einem Hof. Bei „töten“ steht einer auf und zieht das Schwert."""
    sq = Vector((26.0, 18.0, 0))
    HW.mecca_town(night=True, keep=[(sq.x, sq.y, 13.0)])
    cfg = BW.night(moon=0.45)
    rnd = random.Random(3)
    fire = MK.campfire("fire", (sq.x, sq.y, 0.0), energy=260.0)
    Q.flicker(fire["light"], 0, D, 260, amt=0.25, seed=1)
    men = []
    for k in range(9):
        if k == 5:
            men.append(None)
            continue
        a = 2 * math.pi * k / 9 + 0.3
        x, y = sq.x + 2.6 * math.cos(a), sq.y + 2.6 * math.sin(a)
        Pp = BW.warrior(f"qm{k}", (x, y, 0), yaw=Q.face_yaw((x, y), (sq.x, sq.y)), side="q", seed=300 + k, weapon="none",
                        shield_=False, sit=k not in (2, 6), helmet=False, mail=False)
        Q.idle(Pp, 0, D, seed=k)
        men.append(Pp)
    for k, (x, y) in enumerate(((sq.x + 4.6, sq.y + 2.0), (sq.x - 4.4, sq.y + 3.0), (sq.x + 1.0, sq.y + 4.8))):
        Pp = BW.warrior(f"qs{k}", (x, y, 0), yaw=Q.face_yaw((x, y), (sq.x, sq.y)), side="q", seed=330 + k, weapon="spear", shield_=False)
        Q.arm_pose(Pp, 0, "R", -18, -70)
        Q.idle(Pp, 0, D, seed=k + 10)
    # der Sprecher gestikuliert; bei „töten“ zieht einer sein Schwert
    sp = men[2]
    for k, tt in enumerate((0.8, 2.0, 3.2, 4.4)):
        Q.arm_pose(sp, tt, "R", -70 if k % 2 else -40, -60)
    tk = ev("töten_m1", D * 0.6)
    ax = men[6]
    BW.sword("qsw", ax["hand.R"])
    Q.arm_pose(ax, tk - 0.3, "R", -20, -20)
    Q.arm_pose(ax, tk + 0.25, "R", -150, -30)
    for k in range(6):
        L = Q.oil_lamp(f"wl{k}", (sq.x + 6.5 * math.cos(k), sq.y + 6.5 * math.sin(k), 1.7), energy=0.0)
        L["light"].data.energy = 16
    rig, shake, cam = Q.pov_camera(lens=20)
    c0 = (sq.x - 7.0, sq.y - 5.0, 1.9)
    c1 = (sq.x - 4.4, sq.y - 3.2, 1.75)
    tgt = (sq.x, sq.y, 0.9)
    ck(rig, [(0, c0, look(c0, tgt)), (tk - 0.4, lerp3(c0, c1, 0.7), look(lerp3(c0, c1, 0.7), (sq.x + 0.6, sq.y + 1.5, 1.0))),
             (D, c1, look(c1, (sq.x + 1.6, sq.y + 2.2, 1.6)))])
    Q.handheld(shake, 0, D, amp=0.5, hits=[(tk + 0.25, 0.5)])
    cfg["mist_amt"] = 0.35
    return cfg


def abu_bakr_house():
    """Abu Bakrs Haus (Tür nach Westen) an einem kleinen Platz; Rückgabe: Tür-Scharnier, Türmitte."""
    x0, y0 = 40.0, -46.0
    hinge = MD.house("hAB", x0, y0, 7.0, 7.0, 3.4, door_side="W", door_at=0.5, seed=31, lit=False, windows=2)
    return hinge, Vector((x0, y0 + 3.5, 0))


def shot_haus():
    """Mittagshitze, leere Gasse: das Licht kommt zu Abu Bakrs Tür. Die Tür geht auf, Abu Bakr (Licht über dem Kopf) tritt heraus."""
    door = Vector((40.0, -42.5, 0))
    HW.mecca_town(night=False, keep=[(door.x - 4.0, door.y, 10.0), (door.x + 3.5, door.y, 5.0), (door.x - 2.0, door.y + 8.0, 7.0)])
    cfg = MK.light("noon")
    hinge, dp = abu_bakr_house()
    t_open = ls("m2") + 1.0
    hinge.keyframe_insert("rotation_euler", frame=max(1, Q.T(t_open - 0.1)))
    hinge.rotation_euler = (0, 0, math.radians(-100))
    hinge.keyframe_insert("rotation_euler", frame=max(1, Q.T(t_open + 0.9)))
    # das Licht kommt von Norden die Gasse herunter zur Tür
    lx = door.x - 1.5
    H = prophet("nur", (lx, door.y + 7.5, 0.0), height=2.2, strength=0.9)
    te = MK.glide(H, [(lx, door.y + 7.5), (lx, door.y + 1.1)], 0.0, speed=2.4)
    MK.hold_at(H, D)
    AB = Q.person("abubakr", (door.x + 0.6, door.y, 0), yaw=Q.face_yaw((door.x, door.y), (lx, door.y)), robe=(0.86, 0.82, 0.72),
                  wrap=(0.92, 0.9, 0.84), head="turban", glow=True, seed=901)
    Q.walk(AB, [(door.x + 0.6, door.y), (door.x - 0.55, door.y - 0.1)], t_open + 0.5, speed=0.8)
    Q.idle(AB, t_open + 2.0, D, seed=3)
    tq2 = ls("q2")
    Q.arm_pose(AB, tq2 - 0.2, "R", -10, -10)
    Q.arm_pose(AB, tq2 + 0.4, "R", -45, -70)
    Q.arm_pose(AB, tq2 + 1.6, "R", -10, -10)
    glow_pulse(H, ls("q1"), 1.7)
    glow_pulse(H, ls("q3"), 2.2)
    # Leben: Katze? nein – Hitze: ein Hund schläft im Schatten nicht; nur Wäsche/Krüge (props)
    for k, (x, y) in enumerate(((door.x - 6.8, door.y + 3.0), (door.x - 7.0, door.y - 2.6))):
        KW.jug(f"jug{k}", (x, y, 0), scale=1.2)
    rig, shake, cam = Q.pov_camera(lens=19)
    c0 = (door.x - 6.2, door.y - 1.6, 1.62)
    c1 = (door.x - 5.4, door.y - 1.0, 1.62)
    ck(rig, [(0, c0, look(c0, (lx, door.y + 6.0, 1.4))), (t_open - 0.4, None, look(c0, (lx + 0.6, door.y + 1.5, 1.4))),
             (ls("q1"), lerp3(c0, c1, 0.6), look(lerp3(c0, c1, 0.6), (door.x - 0.8, door.y + 0.2, 1.4))),
             (D, c1, look(c1, (door.x - 0.9, door.y, 1.35)))])
    Q.handheld(shake, 0, D, amp=0.45)
    cfg["mist_amt"] = 0.16
    return cfg


def shot_auszug():
    """Nacht: das Licht und Abu Bakr gehen aus der Stadt – nicht nach Norden, sondern nach Süden zum dunklen Berg."""
    cs = HW.cave_spot()
    path = [(10.0, -44.0), (10.5, -60.0), (11.0, -80.0), (13.0, -100.0), (14.0, -118.0)]
    HW.mecca_town(night=True, keep=[(x, y, 12.0) for x, y in path] + [(9.0, -36.0, 12.0)])
    cfg = BW.night(moon=0.6)
    rh = random.Random(4)
    yy = -32.0
    while yy > -70.0:
        d_ = rh.uniform(5.0, 8.0)
        for side in (-1, 1):
            w_ = rh.uniform(5.0, 7.0)
            x0 = 10.2 + side * rh.uniform(2.4, 3.0) - (w_ if side < 0 else 0)
            MD.house(f"ga{int(-yy)}{side}", x0, yy - d_, w_, d_, rh.choice([3.0, 3.3, 5.4]), seed=rh.randint(0, 999), lit=True,
                     door_side=("E" if side < 0 else "W") if rh.random() < 0.5 else None)
        yy -= d_ + rh.uniform(0.2, 1.2)
    t0 = 0.0
    H = prophet("nur", (path[0][0], path[0][1], gz(*path[0])), height=2.1, strength=0.75, day=False)
    MK.glide(H, path, t0 + 0.4, speed=1.05)
    AB = Q.person("abubakr", (path[0][0] + 1.0, path[0][1] + 1.6, 0), robe=(0.62, 0.58, 0.5), head="turban", glow=True, seed=901)
    Q.walk(AB, [(x + 1.0, y + 1.6) for x, y in path], t0 + 0.4, speed=1.05)
    # der Berg Thaur im Süden: kleiner Lichtschein an der Stelle der Höhle (wird erst später erzählt)
    rig, shake, cam = Q.pov_camera(lens=19)
    c0 = (9.6, -34.0, 1.62)
    c1 = (10.4, -46.0, 1.62)
    tsd = ev("süden_m3", D * 0.5)
    th = ev("höhle_m3", D * 0.8)
    mtn = (cs.x, cs.y, cs.z + 6.0)
    ck(rig, [(0, c0, look(c0, (10.0, -50.0, 1.2))), (tsd - 0.8, lerp3(c0, c1, 0.5), look(lerp3(c0, c1, 0.5), (11.0, -70.0, 1.5))),
             (tsd + 0.6, None, look(lerp3(c0, c1, 0.6), (cs.x, cs.y, cs.z * 0.6))), (D, c1, look(c1, mtn))])
    Q.handheld(shake, 0, D, amp=0.5, walk_from=0, walk_to=D, walk_amp=0.5)
    cfg["mist_amt"] = 0.3
    return cfg


# ============================================================ Höhle im Berg Thaur
def cave_setup(day=True):
    cs = HW.cave_spot()
    HW.mecca_town(night=not day, keep=[(cs.x, cs.y, 10.0)], kaaba=True)
    C = HW.cave("cave", (cs.x, cs.y, cs.z), yaw=math.pi)   # Öffnung nach Norden (Blick über das Tal)
    return cs, C


def cv(local, cs):
    """Höhlen-Koordinaten (Öffnung bei lokal -Y) -> Welt (Höhle um 180° gedreht)."""
    return (cs.x - local[0], cs.y - local[1], cs.z + local[2])


def shot_hoehle():
    """Nacht am Berg Thaur: in der kleinen Felsöffnung ein warmer Schein. Sterne."""
    cs, C = cave_setup(day=False)
    cfg = BW.night(moon=1.1)
    H = prophet("nur", cv((0.3, 0.6, 0.0), cs), height=1.4, strength=0.8, day=False)
    rig, shake, cam = Q.pov_camera(lens=22)
    ent = cv((0, -3.6, 0.6), cs)
    c0 = cv((-4.0, -16.0, 1.3), cs)
    c1 = cv((-3.0, -13.0, 1.4), cs)
    ck(rig, [(0, c0, look(c0, ent)), (D, c1, look(c1, ent))])
    Q.handheld(shake, 0, D, amp=0.35)
    cfg["mist_amt"] = 0.25
    return cfg


def shot_versteck():
    """In der Höhle: Abu Bakr (Licht über dem Kopf) und das Licht sitzen im Dunkeln. Draussen Schritte – die Füsse der Verfolger
    erscheinen in der Öffnung. Abu Bakr flüstert; das Licht bleibt ruhig und leuchtet warm auf."""
    cs, C = cave_setup(day=True)
    cfg = MK.light("day")
    for n_ in Q.sc.world.node_tree.nodes:   # in der Höhle: weniger Himmelslicht (sonst wirkt das Innere hell und milchig)
        if n_.type == "BACKGROUND":
            n_.inputs["Strength"].default_value *= 0.35
    H = prophet("nur", cv((0.55, -1.0, 0.0), cs), height=1.3, strength=0.4, day=False)
    H["light"].data.energy = 16.0
    AB = Q.person("abubakr", cv((-0.45, -0.55, 0.0), cs), yaw=0.0, robe=(0.78, 0.74, 0.64), head="turban", glow=True, seed=901, sit=True)
    AB["root"].rotation_euler.z = Q.face_yaw(cv((-0.45, -0.55, 0), cs), cv((0, -3.6, 0), cs))
    AB["halo"][2].data.energy = 4.0
    Q.idle(AB, 0, D, seed=4)
    WEB = HW.spider_web("web", cv((0.0, -3.62, 0.48), cs), math.pi, r=0.52)
    # Verfolger draussen: gehen zur Öffnung, stehen, gehen umher
    tsc = ev("schritte_c2", ls("c2") + 0.6)
    ent_out = [cv((x, -4.9, 0), cs) for x in (-1.2, 0.4, 1.5)]
    rnd = random.Random(5)
    ps = []
    for k, e in enumerate(ent_out):
        st = (e[0] + 5.0 * (1 if k % 2 else -1), e[1] + rnd.uniform(-1.5, 1.5))
        Pp = BW.warrior(f"vf{k}", (st[0], st[1], gz(*st)), side="q", seed=700 + k, weapon=["sword", "spear", "none"][k], shield_=False)
        Q.walk(Pp, [st, (e[0], e[1])], tsc - 0.6 + k * 0.5, speed=1.2)
        ps.append(Pp)
    tq4 = ls("q4")
    tq5 = ls("q5")
    Q.walk(ps[1], [(ent_out[1][0], ent_out[1][1]), (ent_out[1][0] + 0.8, ent_out[1][1] - 0.4)], tq4 + 0.8, speed=0.6)
    Q.walk(ps[2], [(ent_out[2][0], ent_out[2][1]), (ent_out[2][0] - 0.6, ent_out[2][1] - 1.2)], tq5 + 0.5, speed=0.7)
    # Abu Bakr schaut nach oben zur Öffnung, beugt sich zum Licht (flüstert)
    AB["head"].rotation_euler = (math.radians(-8), 0, 0)
    AB["head"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tsc)))
    AB["head"].rotation_euler = (math.radians(18), 0, 0)
    AB["head"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tsc + 0.8)))
    AB["chest"].rotation_euler = (0, 0, 0)
    AB["chest"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tq4 - 0.6)))
    AB["chest"].rotation_euler = (math.radians(10), 0, math.radians(-35))
    AB["chest"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tq4)))
    glow_pulse(H, tq5, 1.9)
    rig, shake, cam = Q.pov_camera(lens=18)
    c0 = cv((0.0, 1.45, 0.82), cs)
    c1 = cv((-0.05, 0.95, 0.78), cs)
    ent = cv((0.0, -3.5, 0.55), cs)
    ck(rig, [(0, c0, look(c0, ent)), (tq4, lerp3(c0, c1, 0.5), look(lerp3(c0, c1, 0.5), cv((-0.3, -1.6, 0.6), cs))),
             (tq5 - 0.2, None, look(lerp3(c0, c1, 0.6), cv((0.3, -1.5, 0.6), cs))), (D, c1, look(c1, ent))])
    Q.handheld(shake, 0, D, amp=0.35)
    cfg["mist_amt"] = 0.05
    return cfg


def shot_netz():
    """Ich bin einer der Verfolger: vor der Öffnung ein Spinnennetz, unberührt. „Wäre er hier drin …“ – wir gehen weiter, bergab."""
    cs, C = cave_setup(day=True)
    cfg = MK.light("day")
    WEB = HW.spider_web("web", cv((0.0, -3.62, 0.48), cs), math.pi, r=0.52)
    tv = ls("v1")
    te = ev("entfernen_c6", ls("c6") + 0.8)
    sp = pursuers("vf", [(cv((-1.4, -5.2, 0), cs)[0], cv((-1.4, -5.2, 0), cs)[1], math.pi),
                         (cv((1.5, -5.6, 0), cs)[0], cv((1.5, -5.6, 0), cs)[1], math.pi * 0.8),
                         (cv((0.4, -6.8, 0), cs)[0], cv((0.4, -6.8, 0), cs)[1], math.pi)], seed=7)
    # der Sprecher beugt sich zum Netz, zeigt darauf, winkt ab
    A = sp[0]
    A["root"].rotation_euler.z = Q.face_yaw(cv((-1.4, -5.2, 0), cs), cv((0, -3.6, 0), cs))
    A["chest"].keyframe_insert("rotation_euler", frame=1)
    A["chest"].rotation_euler = (math.radians(28), 0, 0)
    A["chest"].keyframe_insert("rotation_euler", frame=max(1, Q.T(0.8)))
    Q.arm_pose(A, 0.9, "R", -70, -10)
    Q.arm_pose(A, tv + 0.5, "R", -40, -60)
    A["chest"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tv + 0.6)))
    A["chest"].rotation_euler = (0, 0, 0)
    A["chest"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tv + 1.3)))
    Q.arm_pose(A, tv + 1.4, "R", -10, -10)
    down = [cv((x, -16.0, 0), cs) for x in (-2.0, 1.0, 3.0)]
    for k, Pp in enumerate(sp):
        st = Pp["root"].location.copy()
        Q.walk(Pp, [(st.x, st.y), (down[k][0], down[k][1])], te - 1.2 + 0.3 * k, speed=1.3)
    rig, shake, cam = Q.pov_camera(lens=19)
    web = cv((0.0, -3.62, 0.48), cs)
    c0 = cv((0.35, -5.15, 1.15), cs)
    c1 = cv((0.25, -4.75, 0.95), cs)
    c2 = cv((0.6, -8.5, 1.6), cs)
    ck(rig, [(0, c0, look(c0, web)), (tv - 0.3, c1, look(c1, web)), (te - 1.0, None, look(c1, cv((-0.4, -5.6, 1.4), cs))),
             (te + 0.2, None, look(c1, cv((0.5, -14.0, 1.0), cs))), (D, c2, look(c2, cv((0.4, -18.0, 0.8), cs)))])
    Q.handheld(shake, 0, D, amp=0.45, walk_from=te - 0.4, walk_to=D, walk_amp=0.6)
    cfg["mist_amt"] = 0.16
    return cfg


# ============================================================ Küste – Ritt und Jagd (Suraqa = Kamera)
def cx(y, off=24.0):
    return HW.shore(y) + off


def line_keep(pts, r=5.0, step=3.0):
    out = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(bx - ax, by - ay) / step))
        out += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n, r) for k in range(n + 1)]
    return out


def coast_path(y0, y1, off=24.0, n=8):
    return [(cx(y0 + (y1 - y0) * k / n, off), y0 + (y1 - y0) * k / n) for k in range(n + 1)]


def ride_dust(C, cam, t0, t1, seed=0):
    BW.hoof_dust(f"hd{C['name']}_", C, t0, t1, cam, every=0.22, alpha=0.32, seed=seed)


def shot_kueste():
    """Morgens an der Küste: drei Kamele ziehen am Wasser entlang nach Norden – vorn das Licht."""
    y0 = 40.0
    HW.coast_world(keep=line_keep(coast_path(y0 - 20, y0 + 20, 22.0), 4.0))
    cfg = MK.light("morning")
    CV = caravan(cx(y0 - 6, 22.0), y0 - 6, 0.0, D + 1, speed=1.5, heading=-4)
    rig, shake, cam = Q.pov_camera(lens=19)
    c0 = (cx(y0 + 6, 31.0), y0 + 6, gz(cx(y0 + 6, 31.0), y0 + 6) + 1.9)
    c1 = (cx(y0 + 7, 30.5), y0 + 7.5, gz(cx(y0 + 7, 30.5), y0 + 7.5) + 1.9)
    ck(rig, [(0, c0, look(c0, (cx(y0 - 4, 22.0), y0 - 4, 1.6))), (D, c1, look(c1, (cx(y0 + 1, 22.0), y0 + 1, 1.8)))])
    Q.handheld(shake, 0, D, amp=0.35)
    cfg["mist_amt"] = 0.2
    return cfg


TENT = Vector((70.0, 120.0, 0.0))


def shot_stamm():
    """Ich sitze im Zelt meines Stammes (Blick nach Westen zum Meer). Ein Mann kommt herein, zeigt zur Küste. Ich winke ab."""
    HW.coast_world(keep=[(TENT.x, TENT.y, 12.0)] + line_keep([(TENT.x - 4, TENT.y), (TENT.x - 30, TENT.y - 6)], 4.0))
    cfg = MK.light("day")
    tz = gz(TENT.x, TENT.y)
    T_ = HW.bedouin_tent("tent", (TENT.x, TENT.y, tz), yaw=-math.pi / 2)   # vorn (lokal -Y) nach Westen
    rnd = random.Random(9)
    fx, fy = TENT.x - 1.3, TENT.y + 0.2
    men = []
    for k, a in enumerate((70, 115, 160, 205, 250, 295)):
        r = 1.55 if k % 2 else 1.75
        x, y = fx + r * math.cos(math.radians(a)), fy + r * math.sin(math.radians(a))
        Pp = Q.person(f"tm{k}", (x, y, tz), yaw=Q.face_yaw((x, y), (fx, fy)), sit=True, seed=800 + k,
                      head=rnd.choice(["scarf", "turban"]), robe=rnd.choice(BW.QROBES))
        Q.arm_pose(Pp, 0, "L", 16, -62, sh_y=10)
        Q.arm_pose(Pp, 0, "R", 16, -62, sh_y=-10)
        Q.idle(Pp, 0, D, seed=k)
        men.append(Pp)
    HW.embers("glut", (fx, fy, tz), energy=25.0)
    for k, (x, y) in enumerate(((TENT.x + 1.8, TENT.y - 3.4), (TENT.x + 1.9, TENT.y + 3.2))):
        Q.ball(f"saddle{k}", (x, y, tz + 0.25), (0.45, 0.3, 0.25), MK.M["wood"], seg=12)
    # der Mann kommt von draussen (Westen) gelaufen
    tv2 = ls("v2")
    Mn = Q.person("bote", (TENT.x - 26.0, TENT.y - 5.0, gz(TENT.x - 26, TENT.y - 5)), seed=820, head="scarf", robe=(0.45, 0.32, 0.2))
    t_in = Q.walk(Mn, [(TENT.x - 26.0, TENT.y - 5.0), (TENT.x - 7.0, TENT.y - 1.4), (TENT.x - 3.4, TENT.y - 1.0)], ls("s2") + 0.8, speed=3.6, run=True)
    set_z(Mn, ls("s2") + 0.8, t_in + 0.1)
    Q.arm_pose(Mn, tv2 + 0.2, "R", -95, -5)    # zeigt zur Küste
    Q.arm_pose(Mn, tv2 + 1.6, "R", -60, -20)
    Mn["root"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tv2 + 0.1)))
    Mn["root"].rotation_euler.z = Q.face_yaw((TENT.x - 3.4, TENT.y - 1.0), (TENT.x - 40, TENT.y - 4))
    Mn["root"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tv2 + 0.6)))
    Mn["root"].rotation_euler.z = Q.face_yaw((TENT.x - 3.4, TENT.y - 1.0), (TENT.x + 0.7, TENT.y + 0.5))
    Mn["root"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tv2 + 1.8)))
    for Pp in men:
        Q.head_to(Pp, tv2 - 0.3, (TENT.x - 3.4, TENT.y - 1.0, tz + 1.4))
    rig, shake, cam = Q.pov_camera(lens=18)
    Hh = MK.pov_arms(cam, skin=(0.4, 0.26, 0.17), sleeve=(0.42, 0.32, 0.22))
    pose(Hh, 0, "hidden")
    tv3 = ls("v3")
    pose(Hh, tv3 - 0.5, "hidden", only="R")
    pose(Hh, tv3 - 0.1, "dismiss", only="R")
    pose(Hh, tv3 + 0.35, "dismiss2", only="R")
    pose(Hh, tv3 + 1.0, "hidden", only="R")
    me = (TENT.x + 0.7, TENT.y + 0.5, tz + 1.0)
    ck(rig, [(0, me, look(me, (TENT.x - 20, TENT.y - 2, tz + 0.2))), (tv2 - 0.6, None, look(me, (TENT.x - 3, TENT.y - 0.6, tz + 1.3))),
             (tv2 + 0.7, None, look(me, (TENT.x - 30, TENT.y - 6, tz + 0.6))), (tv3 - 0.4, None, look(me, (TENT.x - 3, TENT.y - 0.5, tz + 1.2))),
             (D, None, look(me, (TENT.x - 2.8, TENT.y - 0.8, tz + 1.1)))])
    Q.handheld(shake, 0, D, amp=0.3)
    cfg["mist_amt"] = 0.18
    return cfg


def shot_pferd():
    """Hinter dem Zelt, heimlich: Ich gehe mit gesenktem Speer zum Pferd hinter dem Hügel, steige auf – und galoppiere los."""
    hx, hy = TENT.x + 14.0, TENT.y - 10.0
    run = [(hx, hy), (hx - 10.0, hy - 22.0), (hx - 30.0, hy - 70.0)]
    HW.coast_world(keep=[(TENT.x, TENT.y, 12.0), (hx, hy, 6.0)] + line_keep(run, 5.0))
    cfg = MK.light("day")
    tz = gz(TENT.x, TENT.y)
    HW.bedouin_tent("tent", (TENT.x, TENT.y, tz), yaw=-math.pi / 2)
    # kleiner Hügel, hinter dem das Pferd wartet
    MK.rock_hill("huegel", Vector((hx + 3.0, hy + 6.0, gz(hx + 3, hy + 6))), 6.0, 2.4, seed=4)
    Hs = suraqa_horse("sh", (hx, hy, gz(hx, hy)), yaw=Q.face_yaw((hx, hy), run[1]))
    horse_idle(Hs, 0, D, seed=1)
    tg = ev("galoppiert_s5", ls("s5") + 0.3)
    tm = tg - 1.6
    rig, shake, cam = Q.pov_camera(lens=18)
    Hh = pov_rider(cam, spear_=True)
    pose(Hh, 0, "hidden", only="L")
    pose(Hh, 0, "spear_low", only="R")
    st = (TENT.x + 3.6, TENT.y + 1.2)
    w0 = (st[0], st[1], gz(*st) + EYE)
    w1 = (hx - 1.6, hy + 1.4, gz(hx - 1.6, hy + 1.4) + EYE)
    ck(rig, [(0, w0, look(w0, (hx, hy, 1.0))), (tm - 0.2, w1, look(w1, (hx, hy, 1.3)))], loc_interp="LINEAR")
    Q.handheld(shake, 0, tm, amp=0.6, walk_from=0.0, walk_to=tm - 0.2, walk_amp=0.9)
    # aufsteigen: harter Schnitt in den Sattel (eine Kamerafahrt dorthin ging mitten durch den Pferdekörper)
    fcut = Q.T(tm + 0.25)
    ta, tb_ = (fcut - 2) / Q.FPS, (fcut - 1) / Q.FPS   # zwei aufeinanderfolgende Bilder: vor / nach dem Schnitt
    pose(Hh, ta, "spear_low", only="R")
    pose(Hh, ta, "hidden", only="L")
    pose(Hh, tb_, "reins")
    for o in [bpy.data.objects["pov_spear_r"]] + list(bpy.data.objects["pov_spear_r"].children_recursive):
        o.keyframe_insert("hide_render", frame=fcut - 1)
        o.hide_render = True
        o.keyframe_insert("hide_render", frame=fcut)
    pv = Vector(run[1]) - Vector((hx, hy))
    pv.normalize()
    seat = (hx + pv.x * 0.1, hy + pv.y * 0.1, gz(hx, hy) + 2.3)
    ck(rig, [(ta, w1, look(w1, (hx, hy, 1.3)))])
    # Sattel-Gierwinkel genau wie in ride() (NICHT entfaltet: sonst -360° Unterschied -> Kamera drehte sich einmal im Kreis)
    Q.cam_keys(rig, [(tb_, seat, (math.degrees(math.atan2(-pv.x, pv.y)), -6, 0))])
    cut_objs = [rig, Hh["L"], Hh["R"]]
    ride(Hs, rig, run, tg, D + 0.5, speed=10.5, cam_from=tg)
    ride_dust(Hs, cam, tg, D + 0.5)
    Q.handheld(shake, tm + 0.01, D + 0.5, amp=0.9, hits=[(tg + 0.1, 0.7)])
    for ob in cut_objs:   # Schlüssel vor dem Schnitt CONSTANT -> Sprung genau zwischen fcut-1 und fcut
        for fc in Q.fcurves(ob):
            for kp in fc.keyframe_points:
                if int(round(kp.co.x)) == fcut - 1:
                    kp.interpolation = "CONSTANT"
    cfg["mist_amt"] = 0.18
    return cfg


def far_caravan(y, t1, speed=1.5, off=24.0, seed=0, day=True, guide=True):
    return caravan(cx(y, off), y, 0.0, t1, speed=speed, heading=-3, seed=seed, day=day, guide=guide)


def shot_jagd():
    """(Quelle für den Einstieg) Galopp an der Küste entlang, Speer in der Hand, weit vorn die Kamele."""
    y0 = -200.0
    pth = coast_path(y0, y0 + 110, 30.0)
    HW.coast_world(keep=line_keep(pth, 5.0) + line_keep(coast_path(-80, 60, 24.0), 4.0))
    cfg = MK.light("morning")
    far_caravan(-40.0, D + 1, speed=1.5)
    Hs = suraqa_horse("sh", (pth[0][0], pth[0][1], gz(*pth[0])))
    rig, shake, cam = Q.pov_camera(lens=17)
    Hh = pov_rider(cam, spear_=False)
    pose(Hh, 0, "reins")
    ride(Hs, rig, pth, 0.0, D + 0.5, speed=11.5, yaw_off=lambda t: 6 * math.sin(t * 0.7))
    ride_dust(Hs, cam, 0.0, D + 0.5)
    Q.handheld(shake, 0, D + 0.5, amp=0.9)
    cfg["mist_amt"] = 0.2
    return cfg


def shot_ritt():
    """Ich galoppiere den Spuren nach – dann stolpert das Pferd, ich stürze in den Sand."""
    y0 = -130.0
    ts = ev("stolpert_s6", ls("s6") + 1.6)
    sp = 11.0
    pth = coast_path(y0, y0 + sp * ts, 30.0, n=4)
    HW.coast_world(keep=line_keep(coast_path(y0, y0 + 80, 30.0), 6.0))
    cfg = MK.light("day")
    far_caravan(-20.0, D + 1, speed=1.5)
    Hs = suraqa_horse("sh", (pth[0][0], pth[0][1], gz(*pth[0])))
    rig, shake, cam = Q.pov_camera(lens=17)
    Hh = pov_rider(cam, spear_=False)
    pose(Hh, 0, "reins")
    ride(Hs, rig, pth, 0.0, ts, speed=sp)
    stumble(Hs, ts, up=ts + 2.4)
    horse_idle(Hs, ts + 3.2, D + 0.5, seed=2)
    pos, dv, _ = path_eval(pth, 1e9)
    start = (rig.location.x, rig.location.y, rig.location.z)
    pose(Hh, ts, "reins")
    pose(Hh, ts + 0.3, "hidden")
    land = fall_off(rig, shake, ts, start, dv, side=1)
    sitp = (land.x, land.y, gz(land.x, land.y) + 0.95)
    hz = (pos.x, pos.y, gz(pos.x, pos.y) + 1.2)
    ck(rig, [(ts + 1.0, None, None), (ts + 1.9, sitp, look(sitp, hz)), (D, sitp, look(sitp, (pos.x, pos.y, gz(pos.x, pos.y) + 1.5)))])
    ride_dust(Hs, cam, 0.0, ts)
    BW.dust_card("fall_puff", (land.x + dv.x * 1.6, land.y + dv.y * 1.6, land.z + 0.2), (2.0, 1.2), cam, ts + 0.5, ts + 3.0, 0.42,
                 grow=2.0, drift=(0, 0, 0.25), fade_in=0.15, fade_out=1.4)
    Q.handheld(shake, 0, D, amp=0.9, hits=[(ts + 0.05, 0.6), (ts + 0.55, 1.6)])
    cfg["mist_amt"] = 0.2
    return cfg


def shot_lose():
    """Im Sand sitzend ziehe ich die Lospfeile aus dem Köcher: Soll ich ihnen schaden? – Nein. Ich werfe den Pfeil weg, stehe auf."""
    y0 = -60.0
    x0 = cx(y0, 30.0)
    HW.coast_world(keep=[(x0, y0, 8.0)])
    cfg = MK.light("day")
    Hs = suraqa_horse("sh", (x0 + 2.4, y0 + 3.2, gz(x0 + 2.4, y0 + 3.2)), yaw=Q.face_yaw((x0 + 2.4, y0 + 3.2), (x0 - 4, y0 + 30)))
    horse_idle(Hs, 0, D, seed=3)
    far_caravan(70.0, D + 1, speed=1.5)
    rig, shake, cam = Q.pov_camera(lens=18)
    Hh = MK.pov_arms(cam, skin=(0.4, 0.26, 0.17), sleeve=(0.42, 0.32, 0.22))
    # Köcher + drei Lospfeile in der linken Hand (einer mit dunklem Band = „Nein“)
    q = Q.empty("quiver", (0.0, 0.02, -0.02), Hh["L"], rot=(math.radians(-10), 0, math.radians(8)))
    Q.cyl("quiver_c", (0, -0.12, 0), 0.04, 0.32, MK.M["leather"], seg=12, rot=(math.pi / 2, 0, 0), parent=q)
    arrows = []
    for k in range(3):
        a = KW.arrow(f"azlam{k}", (0.012 * (k - 1), 0.12, 0.0), parent=q, rot=(0, math.radians(8 * (k - 1)), 0), length=0.5, done=False)
        arrows.append(a)
    Q.box("band", (0, 0.06, 0), (0.016, 0.04, 0.016), MK.M["blanket_b"], parent=arrows[1])
    tp = ev("lospfeile_s7", ls("s7") + 0.6)
    tn = ev("nein_s7", ls("s7") + 4.0)
    tw = ev("weiter_s7", le("s7") - 0.6)
    pose(Hh, 0, "hidden")
    pose(Hh, max(0.1, tp - 0.6), "arrows")
    pose(Hh, tp + 1.4, "pull", only="R")
    pose(Hh, tn - 0.4, "look_arrow", only="R")
    # Pfeil wandert in die rechte Hand (Elternwechsel per Sichtbarkeit: zweiter Pfeil in der Hand erscheint)
    held = KW.arrow("azlam_held", (0.0, 0.08, 0.0), parent=Hh["R"], rot=(0, 0, 0), length=0.5, done=False)
    Q.box("band_h", (0, 0.06, 0), (0.016, 0.04, 0.016), MK.M["blanket_b"], parent=held)
    for o, on_t, off_t in ((arrows[1], 0.0, tp + 1.35), (held, tp + 1.35, tn + 1.6)):
        for ch in [o] + list(o.children_recursive):
            ch.hide_render = on_t > 0.0
            ch.keyframe_insert("hide_render", frame=1)
            ch.hide_render = False
            ch.keyframe_insert("hide_render", frame=max(1, Q.T(on_t)))
            ch.hide_render = True
            ch.keyframe_insert("hide_render", frame=max(1, Q.T(off_t)))
    pose(Hh, tn + 1.2, "throw", only="R")
    pose(Hh, tn + 1.8, "hidden", only="R")
    pose(Hh, tw - 0.6, "hidden", only="L")
    sit = (x0, y0, gz(x0, y0) + 0.95)
    stand = (x0 + 0.6, y0 + 1.0, gz(x0, y0) + EYE)
    hy = Q.yaw_to(sit, (x0 + 2.4, y0 + 3.2))
    ck(rig, [(0, sit, (hy - 30, -32, 0)), (tp + 0.4, None, (hy - 25, -40, 0)), (tn + 1.4, None, (hy - 20, -30, 0)),
             (tw - 0.3, sit, (hy - 5, -12, 0)), (D, stand, (hy, -8, 0))])
    Q.handheld(shake, 0, D, amp=0.45)
    cfg["mist_amt"] = 0.2
    return cfg


def shot_nah():
    """Wieder im Galopp: vorn die Kamele, immer näher. Das Licht reitet ruhig, ohne sich umzudrehen; Abu Bakr dreht sich immer wieder um."""
    y0 = 20.0
    sp = 9.5
    pth = coast_path(y0, y0 + sp * (D + 1), 27.0, n=6)
    HW.coast_world(keep=line_keep(pth, 6.0) + line_keep(coast_path(100, 150, 23.0), 5.0))
    cfg = MK.light("day")
    CV = caravan(cx(118.0, 23.0), 118.0, 0.0, D + 1, speed=1.7, heading=-3)
    tu = ev("umzudrehen_s8", ls("s8") + 5.0)
    turn_back(CV["ab"], [(0.5, 0), (1.2, 150), (2.2, 150), (2.9, 0), (4.0, 0), (4.6, -150), (5.6, -150), (6.2, 0), (D - 1.0, 0),
                          (D - 0.5, 150)])
    Hs = suraqa_horse("sh", (pth[0][0], pth[0][1], gz(*pth[0])))
    rig, shake, cam = Q.pov_camera(lens=17)
    Hh = pov_rider(cam, spear_=False)
    pose(Hh, 0, "reins")
    ride(Hs, rig, pth, 0.0, D + 0.5, speed=sp, yaw_off=lambda t: -3 * math.sin(t * 0.6))
    ride_dust(Hs, cam, 0.0, D + 0.5)
    Q.handheld(shake, 0, D + 0.5, amp=0.85)
    cfg["mist_amt"] = 0.18
    return cfg


def shot_versinken():
    """Die Vorderbeine des Pferdes versinken bis zu den Knien – ich falle. Das Pferd kämpft sich heraus, Staub steigt auf wie Rauch."""
    y0 = 150.0
    sp = 9.0
    tv = ev("versinken_s9", ls("s9") + 0.3)
    pth = coast_path(y0, y0 + sp * tv, 27.0, n=3)
    HW.coast_world(keep=line_keep(coast_path(y0, y0 + 80, 27.0), 7.0) + line_keep(coast_path(170, 230, 23.0), 5.0))
    cfg = MK.light("day")
    CV = caravan(cx(188.0, 23.0), 188.0, 0.0, D + 1, speed=1.6, heading=-3)
    turn_back(CV["ab"], [(0.2, 0), (0.6, 150), (3.0, 150), (3.8, 0)])
    Hs = suraqa_horse("sh", (pth[0][0], pth[0][1], gz(*pth[0])))
    rig, shake, cam = Q.pov_camera(lens=17)
    Hh = pov_rider(cam, spear_=False)
    pose(Hh, 0, "reins")
    ride(Hs, rig, pth, 0.0, tv, speed=sp)
    pos, dv, _ = path_eval(pth, 1e9)
    # Einsinken: Brust nach vorn unten, Vorderbeine im Sand; dann Kampf, dann heraus
    body = Hs["body"]
    tm = ev("mühsam_s10", ls("s10") + 1.2)
    ts = ev("staub_s10", ls("s10") + 3.6)
    for tt, pt, dz in ((tv - 0.04, 0, 0.0), (tv + 0.25, 20, -0.62), (tv + 1.2, 18, -0.6), (tm - 0.2, 19, -0.62), (tm + 0.3, 2, -0.35),
                       (tm + 0.7, 18, -0.58), (tm + 1.2, -14, -0.05), (ts - 0.2, -30, 0.25), (ts + 0.6, -8, 0.05), (ts + 1.2, 0, 0.0)):
        body.rotation_euler = (math.radians(pt), 0, 0)
        body.location = (0, 0, 1.18 + dz)
        body.keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
        body.keyframe_insert("location", frame=max(1, Q.T(tt)))
    for tt, hip, knee in ((tv - 0.04, 0, 0), (tv + 0.25, 12, 0), (tm + 0.3, -50, 80), (tm + 0.7, 12, 0), (tm + 1.2, -60, 90),
                          (ts + 0.6, -20, 30), (ts + 1.2, 0, 0)):
        for nm in ("FL", "FR"):
            Hs[f"leg.{nm}"].rotation_euler = (math.radians(hip), 0, 0)
            Hs[f"knee.{nm}"].rotation_euler = (math.radians(knee), 0, 0)
            Hs[f"leg.{nm}"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
            Hs[f"knee.{nm}"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
    for tt, a in ((tv, 0), (tv + 0.3, 30), (tm, -15), (tm + 0.6, 35), (ts, -40), (ts + 1.0, 0)):
        Hs["neck"].rotation_euler = (math.radians(a), 0, 0)
        Hs["neck"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
    hp = pos + dv * (-0.52)
    sand_ring("sring", (pos.x - dv.x * 0.6, pos.y - dv.y * 0.6, gz(pos.x, pos.y)), tv + 0.1, r=0.42)
    start = (rig.location.x, rig.location.y, rig.location.z)
    pose(Hh, tv + 0.2, "hidden")
    land = fall_off(rig, shake, tv, start, dv, side=-1, fwd=3.6, out=3.2)
    hd = (pos.x - dv.x * 0.5, pos.y - dv.y * 0.5, gz(pos.x, pos.y) + 0.7)
    up = (land.x, land.y, gz(land.x, land.y) + 0.95)
    ck(rig, [(tv + 1.1, None, look(tuple(land), hd)), (tm - 0.3, up, look(up, hd)),
             (ts + 0.3, None, look(up, (pos.x, pos.y, gz(pos.x, pos.y) + 3.0))), (D, None, look(up, (pos.x, pos.y, gz(pos.x, pos.y) + 9.0)))])
    for k, t_ in enumerate((tv + 0.1, tm + 0.3, tm + 1.2)):
        BW.dust_card(f"sink{k}", (pos.x - dv.x * 0.6, pos.y - dv.y * 0.6, gz(pos.x, pos.y) + 0.5), (2.0, 1.2), cam, t_, t_ + 2.0, 0.6,
                     grow=2.2, drift=(0, 0, 0.3), fade_in=0.12, fade_out=1.2)
    smoke_dust("smoke", (pos.x, pos.y, gz(pos.x, pos.y)), cam, ts - 0.1, dur=7.0, n=16, rise=1.8, alpha=0.45)
    Q.handheld(shake, 0, D, amp=0.8, hits=[(tv + 0.05, 0.8), (tv + 0.55, 1.6), (tm + 0.3, 0.3), (ts, 0.4)])
    cfg["mist_amt"] = 0.2
    return cfg


def shot_ruf():
    """Ich stehe auf, das Pferd hinter mir, vorn ziehen sie weiter. Ich hebe die Hand und rufe: „Ihr seid sicher vor mir!“ – sie halten an."""
    y0 = 160.0
    x0 = cx(y0, 27.0)
    HW.coast_world(keep=[(x0, y0, 8.0)] + line_keep(coast_path(185, 230, 23.0), 5.0))
    cfg = MK.light("day")
    tr = ev("sicher_v4", ls("v4") + 0.3)
    CV = caravan(cx(181.0, 23.0), 181.0, 0.0, D + 1, speed=1.5, heading=-3, stop=tr + 0.8)
    turn_back(CV["ab"], [(tr + 0.2, 0), (tr + 0.9, 150)])
    for k in (0, 1, 2):
        C = CV[k]
        C["root"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tr + 1.2)))
        C["root"].rotation_euler.z += math.radians(25 if k else 15)
        C["root"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tr + 2.4)))
    Hs = suraqa_horse("sh", (x0 + 1.2, y0 - 2.4, gz(x0 + 1.2, y0 - 2.4)), yaw=Q.face_yaw((x0, y0), (x0 + 3, y0 + 10)))
    horse_idle(Hs, 0, D, seed=4)
    for k in range(4):
        BW.dust_card(f"rest{k}", (x0 + 1.0 + k * 0.6, y0 - 3 + k, gz(x0, y0) + 2 + k), (3.0, 3.6), Q.sc.camera or Hs["root"], 0.0, 4.0 + k,
                     0.3, grow=2.0, drift=(0.2, 0, 0.8), fade_in=0.01, fade_out=3.0)
    rig, shake, cam = Q.pov_camera(lens=18)
    for o in bpy.data.objects:
        if o.name.startswith("rest"):
            o.constraints[0].target = cam
    Hh = MK.pov_arms(cam, skin=(0.4, 0.26, 0.17), sleeve=(0.42, 0.32, 0.22))
    pose(Hh, 0, "hidden")
    pose(Hh, tr - 0.5, "hidden", only="R")
    pose(Hh, tr - 0.1, "raise")
    pose(Hh, tr + 1.6, "raise")
    pose(Hh, tr + 2.3, "hidden", only="R")
    c0 = (x0, y0, gz(x0, y0) + EYE)
    c1 = (x0 - 0.3, y0 + 1.2, gz(x0, y0) + EYE)
    tgt = (cx(188.0, 23.0), 188.0, gz(cx(188.0, 23.0), 188.0) + 1.8)
    ck(rig, [(0, c0, look(c0, tgt)), (tr - 0.4, lerp3(c0, c1, 0.6), look(lerp3(c0, c1, 0.6), tgt)), (D, c1, look(c1, tgt))])
    Q.handheld(shake, 0, D, amp=0.55, walk_from=0.2, walk_to=tr - 0.4, walk_amp=0.5, hits=[(tr, 0.25)])
    cfg["mist_amt"] = 0.18
    return cfg


def shot_treffen():
    """Ich gehe zu ihnen. Das Licht auf dem Kamel, Abu Bakr, Amir, der Führer. Ich biete Proviant an – sie nehmen nichts."""
    y0 = 200.0
    x0 = cx(y0, 23.0)
    HW.coast_world(keep=[(x0, y0, 10.0)])
    cfg = MK.light("day")
    CV = caravan(x0, y0, 0.0, 0.0, speed=1.0, heading=-3, stop=0.0)
    for k, (dx, dy, rz) in ((0, (0.0, 0.0, -8)), (1, (3.3, 1.2, -28)), (2, (-3.4, 2.2, 22))):
        C = CV[k]
        C["root"].location = (x0 + dx, y0 + dy, gz(x0 + dx, y0 + dy))
        C["root"].rotation_euler.z = math.radians(rz)
    tq = ls("q6")
    tk = ev("kopfgeld_w1", ls("w1") + 1.6)
    glow_pulse(CV["light"], tq, 1.9)
    turn_back(CV["ab"], [(0.0, 0)])
    AB = CV["ab"]
    Q.arm_pose(AB, tk + 1.6, "R", -10, -10)
    Q.arm_pose(AB, tk + 2.2, "R", -60, -50)      # Hand hoch: „nein, danke“
    Q.arm_pose(AB, tk + 3.4, "R", -10, -10)
    rig, shake, cam = Q.pov_camera(lens=18)
    Hh = MK.pov_arms(cam, skin=(0.4, 0.26, 0.17), sleeve=(0.42, 0.32, 0.22))
    bag = Q.empty("bagp", (0.06, 0.1, 0.06), Hh["L"])
    Q.ball("pouch", (0, 0, 0), (0.07, 0.06, 0.085), MK.M["leather"], parent=bag, seg=16)
    Q.cyl("pouch_neck", (0, 0, 0.08), 0.025, 0.04, MK.M["leather"], parent=bag, seg=10)
    Q.torus("pouch_tie", (0, 0, 0.075), 0.028, 0.006, MK.M["rope"], parent=bag, seg=16)
    pose(Hh, 0, "hidden")
    pose(Hh, tk + 0.6, "hidden")
    pose(Hh, tk + 1.2, "offer")
    pose(Hh, tk + 3.2, "offer")
    pose(Hh, tk + 3.8, "hidden")
    Hs = suraqa_horse("sh", (x0 - 4.0, y0 - 9.0, gz(x0 - 4, y0 - 9)), yaw=Q.face_yaw((x0 - 4, y0 - 9), (x0, y0)))
    horse_idle(Hs, 0, D, seed=5)
    c0 = (x0 - 2.0, y0 - 10.0, gz(x0, y0) + EYE)
    c1 = (x0 - 0.6, y0 - 4.4, gz(x0, y0) + EYE)
    lightpos = (x0, y0, gz(x0, y0) + 2.6)
    abpos = (x0 + 3.3, y0 + 1.2, gz(x0, y0) + 2.5)
    ck(rig, [(0, c0, look(c0, lightpos)), (tk + 0.4, c1, look(c1, lerp3(lightpos, abpos, 0.5))),
             (tk + 2.0, None, look(c1, abpos)), (tq - 0.5, None, look(c1, lightpos)), (D, None, look(c1, (x0, y0, gz(x0, y0) + 2.4)))])
    Q.handheld(shake, 0, D, amp=0.45, walk_from=0, walk_to=tk + 0.4, walk_amp=0.7)
    cfg["mist_amt"] = 0.18
    return cfg


def shot_rueckweg():
    """Auf dem Rückweg (Abendlicht) kommen mir Reiter entgegen. Ich winke ab: „Hier ist niemand.“ – sie kehren um."""
    y0 = 140.0
    sp = 4.2
    tn_ = ev("niemand_v5", ls("v5") + 0.3)
    pth = coast_path(y0, y0 - sp * (tn_ + 0.2), 30.0, n=3)
    HW.coast_world(keep=line_keep(pth, 6.0) + line_keep(coast_path(y0 - 60, y0 - 20, 30.0), 6.0))
    cfg = MK.light("golden")
    tz = ev("zurück_w2", le("w2") - 0.6)
    tn = ev("niemand_v5", ls("v5") + 0.3)
    others = []
    for k in range(3):
        x, y = cx(y0 - 46.0 - k * 3.0, 30.0 + (k - 1) * 2.6), y0 - 46.0 - k * 3.0
        Hh_ = BW.horse(f"oh{k}", (x, y, gz(x, y)), yaw=math.pi, seed=60 + k)
        BW.mounted(f"ohr{k}", Hh_, side="q", seed=70 + k, weapon=["spear", "sword", "spear"][k], shield_=False)
        stop = (x, y + 4.0 * (tn - 0.3))
        BW.horse_run(Hh_, [(x, y), stop], 0.0, speed=4.0, stride=1.6, trot=True)
        back = (stop[0] + 1.0, stop[1] - 20.0)
        BW.horse_run(Hh_, [stop, (stop[0] + 2.5, stop[1] + 0.5), back], tn + 0.6, speed=5.0, stride=2.0, trot=True)
        others.append(Hh_)
    Hs = suraqa_horse("sh", (pth[0][0], pth[0][1], gz(*pth[0])))
    rig, shake, cam = Q.pov_camera(lens=18)
    Hh = pov_rider(cam, spear_=False)
    pose(Hh, 0, "reins")
    pose(Hh, tz - 0.4, "reins", only="R")
    pose(Hh, tz, "wave_a")
    pose(Hh, tz + 0.35, "wave_b")
    pose(Hh, tn, "wave_a")
    pose(Hh, tn + 0.35, "wave_b")
    pose(Hh, tn + 1.0, "reins", only="R")
    ride(Hs, rig, pth, 0.0, D + 0.5, speed=sp, stride=1.6, trot=True, pitch=-4.0)
    Q.handheld(shake, 0, D + 0.5, amp=0.6)
    cfg["mist_amt"] = 0.2
    return cfg


def shot_abend():
    """Abend: Ich stehe auf einer Düne. Die Sonne sinkt ins Meer; weit im Norden ziehen drei kleine Gestalten davon."""
    y0 = 150.0
    x0 = cx(y0, 70.0)
    HW.coast_world(keep=[(x0, y0, 8.0)])
    cfg = MK.light("golden")
    CV = caravan(cx(235.0, 24.0), 235.0, 0.0, D + 1, speed=1.4, heading=-3)
    Hs = suraqa_horse("sh", (x0 + 1.8, y0 - 1.2, gz(x0 + 1.8, y0 - 1.2)), yaw=Q.face_yaw((x0, y0), (x0 - 10, y0 + 6)))
    horse_idle(Hs, 0, D, seed=6)
    rig, shake, cam = Q.pov_camera(lens=19)
    c0 = (x0, y0, gz(x0, y0) + EYE)
    car = (cx(240.0, 24.0), 240.0, gz(cx(240.0, 24.0), 240.0) + 1.6)
    sun_dir = (x0 - 0.849 * 400.0, y0 - 0.451 * 400.0, gz(x0, y0) + 0.29 * 400.0)
    tm = ls("w4")
    ck(rig, [(0, c0, look(c0, car)), (tm - 0.6, None, look(c0, lerp3(car, sun_dir, 0.25))), (D, None, look(c0, lerp3(car, sun_dir, 0.6)))])
    Q.handheld(shake, 0, D, amp=0.3)
    cfg["mist_amt"] = 0.25
    return cfg


# ============================================================ Medina
def shot_medina():
    """Medina am Morgen: Leute stehen auf dem schwarzen Lavafeld und warten. Aus dem Süden kommen die Kamele – vorn das Licht."""
    keep = [(0.0, -6.0, 6.0)] + line_keep([(2.0, -60.0), (1.0, -14.0)], 5.0)
    HW.medina_world(keep=keep)
    cfg = MK.light("morning")
    rnd = random.Random(31)
    tm = ev("medina_w5", ls("w5") + 1.8)
    ppl = []
    for k in range(26):
        x = rnd.uniform(-14, 14)
        y = rnd.uniform(-14, -4)
        if abs(x) < 2.2 and y > -9:
            continue
        Pp = Q.person(f"md{k}", (x, y, gz(x, y)), yaw=Q.face_yaw((x, y), (1.5, -50)), seed=1000 + k, head=rnd.choice(["turban", "scarf", "cap"]),
                      height=rnd.choice([1.0, 1.0, 1.0, 0.75]))
        Q.idle(Pp, 0, D, seed=k)
        if k % 2 == 0:
            Q.arm_pose(Pp, tm - 0.2 + rnd.uniform(0, 0.6), "R", -10, -10)
            Q.arm_pose(Pp, tm + 0.4 + rnd.uniform(0, 0.6), "R", -160, -10)
        ppl.append(Pp)
    for k, (x, y) in enumerate(((-9.0, -16.0), (-12.5, -22.0), (-8.0, -30.0), (10.5, -18.0), (13.0, -27.0), (-15.0, -12.0), (16.0, -11.0),
                                (-11.0, -40.0), (12.0, -38.0))):
        MD.palm(f"palmn{k}", (x, y, gz(x, y)), h=rnd.uniform(6.5, 9.5), lean=(rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05)), seed=700 + k)
    CV = caravan(2.0, -42.0, 0.0, D + 1, speed=1.3, heading=0)
    rig, shake, cam = Q.pov_camera(lens=18)
    c0 = (0.6, -2.5, gz(0.6, -2.5) + EYE)
    c1 = (0.9, -5.0, gz(0.9, -5.0) + EYE)
    ck(rig, [(0, c0, look(c0, (1.5, -40.0, 1.8))), (D, c1, look(c1, (1.8, -34.0, 2.2)))])
    Q.handheld(shake, 0, D, amp=0.4, walk_from=0, walk_to=D, walk_amp=0.4)
    cfg["mist_amt"] = 0.18
    return cfg


SHOTS = {"mekka": shot_mekka, "haus": shot_haus, "auszug": shot_auszug, "hoehle": shot_hoehle, "versteck": shot_versteck, "netz": shot_netz,
         "kueste": shot_kueste, "stamm": shot_stamm, "pferd": shot_pferd, "jagd": shot_jagd, "ritt": shot_ritt, "lose": shot_lose,
         "nah": shot_nah, "versinken": shot_versinken, "ruf": shot_ruf, "treffen": shot_treffen, "rueckweg": shot_rueckweg,
         "abend": shot_abend, "medina": shot_medina}


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
    # eigenes Verschmelzen (Operator-Join mischte bei geteilten Netzen die Lagen durcheinander): jedes Objekt in Weltlage übernehmen
    import bmesh as _bm
    dg = bpy.context.evaluated_depsgraph_get()
    bm = _bm.new()
    mats = []
    for o in objs:
        eo = o.evaluated_get(dg)
        me = eo.to_mesh()
        me.transform(o.matrix_world)
        remap = []
        for m in (o.data.materials if o.data else []):
            if m not in mats:
                mats.append(m)
            remap.append(mats.index(m))
        n0 = len(bm.faces)
        bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        for f in bm.faces[n0:]:
            f.material_index = remap[f.material_index] if f.material_index < len(remap) else 0
        eo.to_mesh_clear()
    nm = bpy.data.meshes.new("noshadow_static")
    bm.to_mesh(nm)
    bm.free()
    for m in mats:
        nm.materials.append(m)
    for o in objs:
        bpy.data.objects.remove(o)
    o = bpy.data.objects.new("noshadow_static", nm)
    Q.link(o)
    o.visible_shadow = False
    print("join_noshadow:", len(objs))


Q.reset()
cfg = SHOTS[SHOT]()
bpy.context.view_layer.update()   # Welt-Matrizen aktuell, sonst landen Kinder beim Verschmelzen an falscher Stelle
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
if os.environ.get("CAMDBG"):
    camo = sc.camera
    for t_ in map(float, os.environ["CAMDBG"].split(",")):
        sc.frame_set(Q.T(t_))
        fw = camo.matrix_world.to_3x3() @ Vector((0, 0, -1))
        extra = ""
        for nm in os.environ.get("OBJS", "").split(","):
            o = bpy.data.objects.get(nm)
            if o:
                extra += f" {nm}={tuple(round(v, 1) for v in o.matrix_world.translation)}"
        print("CAMDBG", t_, tuple(round(v, 2) for v in camo.matrix_world.translation), "fwd", tuple(round(v, 2) for v in fw), extra)
    sys.exit(0)
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
