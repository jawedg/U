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


class SPath:
    """v2 (Nutzer: schneller Ritt ruckelte): weiche Kurve (Catmull-Rom) durch die Wegpunkte statt Ecken, gleichmäßig abgetastet;
    über die Enden hinaus geradeaus verlängert. tangent() schaut ±2,5 m voraus/zurück -> Richtung ändert sich weich."""

    def __init__(self, path):
        P_ = [Vector((p[0], p[1], 0.0)) for p in path]
        if len(P_) == 1:
            P_.append(P_[0] + Vector((0, 0.01, 0)))
        ext = [P_[0] * 2 - P_[1]] + P_ + [P_[-1] * 2 - P_[-2]]
        pts = []
        for i in range(1, len(ext) - 2):
            p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
            n = max(2, int((p2 - p1).length / 0.25))
            for k in range(n):
                u = k / n
                pts.append(0.5 * (2 * p1 + (p2 - p0) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (3 * p1 - p0 - 3 * p2 + p3) * u ** 3))
        pts.append(P_[-1].copy())
        self.p = pts
        self.c = [0.0]
        for a, b in zip(pts, pts[1:]):
            self.c.append(self.c[-1] + (b - a).length)
        self.total = self.c[-1]

    def at(self, d):
        import bisect
        p = self.p
        if d <= 0:
            return p[0] + (p[1] - p[0]).normalized() * d
        if d >= self.total:
            return p[-1] + (p[-1] - p[-2]).normalized() * (d - self.total)
        i = min(len(p) - 2, bisect.bisect_right(self.c, d) - 1)
        L_ = self.c[i + 1] - self.c[i]
        return p[i] + (p[i + 1] - p[i]) * ((d - self.c[i]) / L_ if L_ > 1e-9 else 0.0)

    def tangent(self, d, look=2.5):
        return (self.at(d + look) - self.at(d - look)).normalized()


def smoothstep(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


class Gait:
    """Tempo-Verlauf eines Pferdes: steht bis t0 (bei accel > 0), läuft in accel s weich auf speed an, ab t_stop in decel s weich aus.
    d(t) = Weg, ph(t) = Schrittphase (Galoppsprünge), amp(t) = Stärke der Galoppbewegung (0 = steht)."""

    def __init__(self, t0, speed, accel=0.0, t_stop=None, decel=1.2, stride=3.4, t_end=60.0):
        self.t0, self.speed, self.accel, self.t_stop, self.decel, self.stride = t0, speed, accel, t_stop, decel, stride
        self.dt = 1.0 / 240
        self.tmin = min(0.0, t0) - 1.0
        n = int((t_end - self.tmin) / self.dt) + 2
        self.ts, self.ds, self.phs, self.vs = [], [], [], []
        d = ph = 0.0
        for k in range(n):
            t = self.tmin + k * self.dt
            v = self.vel(t)
            self.ts.append(t)
            self.ds.append(d)
            self.phs.append(ph)
            self.vs.append(v)
            a = min(1.0, v / (0.7 * speed)) if speed > 0 else 0.0
            d += v * self.dt
            ph += v / (stride * (0.5 + 0.5 * a)) * self.dt if v > 0 else 0.0
        i0 = min(range(n), key=lambda k: abs(self.ts[k] - t0))
        off = self.ds[i0]
        self.ds = [x - off for x in self.ds]   # d(t0) = 0

    def vel(self, t):
        if t < self.t0:
            v = 0.0 if self.accel > 0 else self.speed
        else:
            v = self.speed * (smoothstep((t - self.t0) / self.accel) if self.accel > 0 else 1.0)
        if self.t_stop is not None and t > self.t_stop:
            v *= 1.0 - smoothstep((t - self.t_stop) / self.decel)
        return v

    def _i(self, arr, t):
        x = (t - self.tmin) / self.dt
        k = max(0, min(len(arr) - 2, int(x)))
        u = max(0.0, min(1.0, x - k))
        return arr[k] + (arr[k + 1] - arr[k]) * u

    def d(self, t):
        return self._i(self.ds, t)

    def ph(self, t):
        return self._i(self.phs, t)

    def v(self, t):
        return self._i(self.vs, t)

    def amp(self, t):
        return min(1.0, self.v(t) / (0.7 * self.speed)) if self.speed > 0 else 0.0


def _ground(pos, dv, zf=None):
    """Bodenhöhe unter dem Pferd (Mittel aus Vorder- und Hinterhufen) + Hangneigung in Grad (vorn höher = positiv)."""
    zf = zf or gz
    b, f_ = pos - dv * 0.55, pos + dv * 0.55
    zb, zfr = zf(b.x, b.y), zf(f_.x, f_.y)
    return (zb + zfr) / 2, math.degrees(math.atan2(zfr - zb, 1.1))


def _unwrap(a, prev):
    if prev is None:
        return a
    while a - prev > math.pi:
        a -= 2 * math.pi
    while a - prev < -math.pi:
        a += 2 * math.pi
    return a


def horse_go(C, sp, G, t0, t1, trot=False, zf=None, idle_seed=0, d0=0.0):
    """Pferd auf weicher Kurve mit Tempo-Verlauf G: steht (lebendig: Kopf, Schweif, Atmen) -> läuft weich an -> Galopp.
    Beine im Viertakt mit Stärke amp (steht = Beine gerade). Ersetzt BW.horse_run (konstantes Tempo, Ecken, Beine hingen vorher fest)."""
    root, body, neck = C["root"], C["body"], C["neck"]
    prev = None
    rnd = random.Random(idle_seed)
    i1, i2, i3 = rnd.uniform(0, 6), rnd.uniform(0, 6), rnd.uniform(0, 6)
    for f in range(max(1, Q.T(t0)), Q.T(t1) + 1):
        t = (f - 1) / Q.FPS
        d, a, cyc = G.d(t) + d0, G.amp(t), G.ph(t)
        ph = 2 * math.pi * cyc
        pos, dv = sp.at(d), sp.tangent(d)
        z, slope = _ground(pos, dv, zf)
        root.location = (pos.x, pos.y, z)
        root.keyframe_insert("location", frame=f)
        yaw = _unwrap(math.atan2(dv.x, -dv.y), prev)
        prev = yaw
        root.rotation_euler = (0, 0, yaw)
        root.keyframe_insert("rotation_euler", index=2, frame=f)
        am = a * (0.5 if trot else 1.0)
        idle = 1.0 - a
        breathe = 0.006 * math.sin(t * 2.2 + i1) * idle
        body.location = (0, 0, 1.18 + (0.05 if trot else 0.09) * am * math.sin(2 * ph if trot else ph) + breathe)
        body.rotation_euler = (math.radians(-slope + 5 * am * math.sin(ph + 0.8)), 0, 0)
        body.keyframe_insert("location", frame=f)
        body.keyframe_insert("rotation_euler", frame=f)
        n_idle = (7 * math.sin(t * 0.7 + i2) + 4 * math.sin(t * 1.9 + i3)) * idle
        neck.rotation_euler = (math.radians(n_idle - 8 * am * math.sin(ph + 0.3) + 7 * a), 0,
                               math.radians(9 * math.sin(t * 0.45 + i1) * idle))
        neck.keyframe_insert("rotation_euler", frame=f)
        C["tail"].rotation_euler = (math.radians(12 * idle + 35 * am + 8 * math.sin(ph * 2) * a), 0,
                                    math.radians(6 * math.sin(ph) * a + 11 * math.sin(t * 2.3 + i2) * idle))
        C["tail"].keyframe_insert("rotation_euler", frame=f)
        for k, e in enumerate(C.get("mane", ())):   # Mähne flattert mit dem Galopp, weht im Stand leicht
            u = k / 12
            e.rotation_euler = (math.radians(-35 + 10 * u - 18 * a + 9 * a * math.sin(ph * 2 - k * 0.55) + 2.5 * idle * math.sin(t * 1.7 + k)),
                                math.radians(28 + 10 * a * math.sin(ph - k * 0.4)), 0)
            e.keyframe_insert("rotation_euler", frame=f)
        for nm, off in BW.GALLOP.items():
            if trot:
                off = {"BL": 0.0, "FR": 0.0, "BR": 0.5, "FL": 0.5}[nm]
            u = (cyc + off) % 1.0
            if u < 0.4:
                sw, kb = 1.0 - 2.0 * u / 0.4, 0.0
            else:
                v_ = (u - 0.4) / 0.6
                sw, kb = -1.0 + 2.0 * v_, math.sin(math.pi * v_)
            front = nm[0] == "F"
            C[f"leg.{nm}"].rotation_euler = (math.radians(-(32 if front else 28) * am * sw), 0, 0)
            C[f"leg.{nm}"].keyframe_insert("rotation_euler", frame=f)
            C[f"knee.{nm}"].rotation_euler = (math.radians((70 if front else -55) * am * kb), 0, 0)
            C[f"knee.{nm}"].keyframe_insert("rotation_euler", frame=f)


RIDE_H = 1.18 + 0.36 + 0.9   # Augenhöhe im Sattel über dem Boden


def ride(C, rig, path, t0, t1, speed, stride=3.4, yaw_off=None, pitch=0.0, trot=False, cam_from=None, run=True, accel=0.0,
         t_stop=None, decel=1.2, horse_from=None):
    """Pferd + Kamera im Sattel auf derselben weichen Kurve/demselben Tempo. Kamera: halbes Wippen, wenig Nicken/Rollen (Nutzer:
    schneller Ritt zu hektisch). Rückgabe: (SPath, Gait)."""
    sp = SPath(path)
    G = Gait(t0, speed, accel=accel, t_stop=t_stop, decel=decel, stride=stride, t_end=t1 + 2.0)
    if run:
        horse_go(C, sp, G, horse_from if horse_from is not None else min(t0, cam_from if cam_from is not None else t0), t1, trot=trot)
    prev = None
    for f in range(max(1, Q.T(cam_from if cam_from is not None else t0)), Q.T(t1) + 1):
        t = (f - 1) / Q.FPS
        d, a = G.d(t), G.amp(t)
        ph = 2 * math.pi * G.ph(t)
        pos, dv = sp.at(d), sp.tangent(d)
        z, slope = _ground(pos, dv)
        am = a * (0.5 if trot else 1.0)
        p = pos + dv * (-0.08)
        rig.location = (p.x, p.y, z + RIDE_H + 0.045 * am * math.sin(2 * ph if trot else ph))
        rig.keyframe_insert("location", frame=f)
        yw = _unwrap(math.atan2(-dv.x, dv.y) + math.radians(yaw_off(t) if yaw_off else 0.0), prev)
        prev = yw
        pt = pitch + slope * 0.6 - 1.5 * am * math.sin(ph + 0.8)
        rig.rotation_euler = (math.radians(pt), math.radians(0.6 * am * math.sin(ph * 0.5)), yw)
        rig.keyframe_insert("rotation_euler", frame=f)
    return sp, G


def rein_mesh():
    me = bpy.data.meshes.get("rein_seg")
    if me:
        return me
    import bmesh
    bm = bmesh.new()
    n = 6
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        r = 0.0055
        vs = [bm.verts.new((r * math.cos(a0), 0.0, r * math.sin(a0) * 0.6)), bm.verts.new((r * math.cos(a1), 0.0, r * math.sin(a1) * 0.6)),
              bm.verts.new((r * math.cos(a1), 1.0, r * math.sin(a1) * 0.6)), bm.verts.new((r * math.cos(a0), 1.0, r * math.sin(a0) * 0.6))]
        bm.faces.new(vs)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    me = bpy.data.meshes.new("rein_seg")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(MK.M["leather"])
    return me


def reins(Hh, C, off=()):
    """v2 (Nutzer: „das Seil hängt in der Luft“): Zügel als zwei Lederstücke je Seite, per Constraint immer von der Faust zum Gebissring
    am Pferdemaul gespannt, in der Mitte leicht durchhängend. off = [(t_aus, t_an), …]: Zügel losgelassen (unsichtbar)."""
    hs = bpy.data.objects[f"{C['name']}_hs"]
    me = rein_mesh()
    segs = []
    for nm, sx in (("L", 1), ("R", -1)):   # Pferd lokal +X = links des Reiters
        a = Q.empty(f"pov_reina.{nm}", (0, 0.09, -0.03), Hh[nm])
        b = Q.empty(f"pov_reinb.{nm}", (0.068 * sx, -0.24, -0.035), hs)
        m = Q.empty(f"pov_reinm.{nm}", (0, 0, 0))
        c1 = m.constraints.new("COPY_LOCATION")
        c1.target = a
        c2 = m.constraints.new("COPY_LOCATION")
        c2.target = b
        c2.influence = 0.5
        ms = Q.empty(f"pov_reinms.{nm}", (0, 0, -0.09), m)
        s1 = bpy.data.objects.new(f"pov_rein1.{nm}", me)
        Q.link(s1)
        s1.parent = Hh[nm]
        s1.location = (0, 0.09, -0.03)
        st = s1.constraints.new("STRETCH_TO")
        st.target, st.rest_length, st.volume = ms, 1.0, "NO_VOLUME"
        s2 = bpy.data.objects.new(f"pov_rein2.{nm}", me)
        Q.link(s2)
        cl = s2.constraints.new("COPY_LOCATION")
        cl.target = ms
        st2 = s2.constraints.new("STRETCH_TO")
        st2.target, st2.rest_length, st2.volume = b, 1.0, "NO_VOLUME"
        for s_ in (s1, s2):
            s_.visible_shadow = False
            segs.append(s_)
    for item in off:
        t_off, t_on = item[0], item[1]
        sides = item[2] if len(item) > 2 else "LR"
        for s_ in segs:
            if s_.name[-1] not in sides:
                continue
            s_.hide_render = False
            s_.keyframe_insert("hide_render", frame=max(1, Q.T(t_off) - 1))
            s_.hide_render = True
            s_.keyframe_insert("hide_render", frame=max(1, Q.T(t_off)))
            if t_on is not None:
                s_.keyframe_insert("hide_render", frame=max(1, Q.T(t_on) - 1))
                s_.hide_render = False
                s_.keyframe_insert("hide_render", frame=max(1, Q.T(t_on)))
    return segs


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
    "brace": {"L": ((-0.17, -0.12, -0.5), (-25, 0, -12)), "R": ((0.17, -0.12, -0.5), (-25, 0, 12))},
    "brace_hit": {"L": ((-0.2, -0.22, -0.4), (-55, 0, -20)), "R": ((0.2, -0.22, -0.4), (-55, 0, 20))},
    "push": {"L": ((-0.22, -0.42, -0.3), (-80, 0, -25)), "R": ((0.22, -0.42, -0.3), (-80, 0, 25))},
    # Lospfeile (v2): rechte Hand greift in den Köcher links unten, zieht das Bündel heraus, hält es hoch; links zieht einen Pfeil
    "grab_q": {"R": ((-0.12, -0.36, -0.42), (-70, 10, 60))},
    "bundle": {"R": ((0.06, -0.14, -0.46), (-20, 0, 15))},
    "shake_a": {"R": ((0.07, -0.12, -0.45), (-14, 0, 5))},
    "shake_b": {"R": ((0.05, -0.15, -0.47), (-26, 0, 25))},
    "draw_l": {"L": ((-0.1, -0.3, -0.48), (-70, 0, -30))},
    "away_r": {"R": ((0.26, -0.5, -0.35), (-80, 0, 20))},
}


def fists(Hh, reins=False):
    """Ich-Hände als Fäuste (Finger eingerollt). Zügel jetzt per reins() (am Pferdemaul befestigt)."""
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
    Q.limb(f"{name}_manes", (0, 0.12, 0.04), (0, -0.2, 0.66), 0.035, 0.024, mh, parent=C["neck"], seg=10)
    Q.ball(f"{name}_forelock", (0, -0.3, 0.7), (0.04, 0.05, 0.05), mh, parent=C["neck"], seg=10)
    # v2: Mähne aus Haarbüscheln, die beim Galopp flattern (Nutzer: Pferd zu steif) – aus dem Sattel gut zu sehen
    a0, a2 = Vector((0, 0.12, 0.04)), Vector((0, -0.2, 0.66))
    tufts = []
    rnd = random.Random(7)
    for k in range(13):
        u = k / 12
        e = Q.empty(f"{name}_tuft{k}", tuple(a0 + (a2 - a0) * u + Vector((0, 0.02, 0.02))), C["neck"],
                    rot=(math.radians(-35 + 10 * u), math.radians(28), 0))
        Q.ball(f"{name}_tuftm{k}", (0, 0.06, -0.01), (0.018, 0.075 + 0.02 * rnd.random(), 0.05), mh, parent=e, seg=8)
        tufts.append(e)
    C["mane"] = tufts
    return C


def fall_off(rig, shake, t, start, dv, side=1, back=0.0, lie_look=None, dur=0.62, fwd=2.4, out=0.9, Hh=None, yaw0=None):
    """v2 (Nutzer: Sturz sah komisch aus): ich werde über die Schulter des Pferdes nach vorn geworfen – kurz hoch, dann kippt der Blick
    nach unten auf den heranrasenden Sand, Hände fangen den Sturz ab, Aufprall mit Rolle zur Seite, Blick liegt flach über dem Boden.
    Rückgabe: Liegeposition (Kamera knapp über dem Sand)."""
    sv = Vector((dv.y, -dv.x, 0)) * side
    s0 = Vector(start)
    land = s0 + dv * (fwd - back) + sv * out
    land.z = gz(land.x, land.y) + 0.28
    yw = yaw0 if yaw0 is not None else math.degrees(math.atan2(-dv.x, dv.y))
    up = s0 + dv * 0.5 + Vector((0, 0, 0.16))
    air = s0 + dv * (fwd * 0.65 - back) + sv * out * 0.4
    air.z = gz(air.x, air.y) + 1.05
    slide = land + dv * 0.35 + sv * 0.15
    slide.z = gz(slide.x, slide.y) + 0.26
    ck(rig, [(t, tuple(s0), (yw, -6, 0)), (t + dur * 0.22, tuple(up), (yw - 4 * side, -28, 6 * side)),
             (t + dur * 0.6, tuple(air), (yw - 10 * side, -68, 18 * side)), (t + dur, tuple(land), (yw - 22 * side, -30, 55 * side)),
             (t + dur + 0.3, tuple(slide), (yw - 30 * side, -8, 78 * side)), (t + dur + 1.1, None, (yw - 34 * side, -4, 82 * side))])
    if Hh is not None:   # Hände: loslassen, nach vorn strecken (abfangen), dann weg
        pose(Hh, t + 0.05, "reins")
        pose(Hh, t + dur * 0.5, "brace")
        pose(Hh, t + dur + 0.05, "brace_hit")
        pose(Hh, t + dur + 0.35, "hidden")
    return slide


def stumble(C, t, down=1.0, up=None):
    """Pferd stolpert: Vorderbeine knicken ein, Brust nach vorn unten (und steht wieder auf, wenn up gesetzt)."""
    body = C["body"]
    seq = [(t + 0.3, 24 * down, -0.42 * down, -45, 95, -22, -40), (t + 0.9, 20 * down, -0.38 * down, -40, 90, -18, -35)]
    if up:
        seq += [(up - 0.5, 16, -0.3, -20, 60, -25, -45), (up, 8, -0.1, -10, 30, -8, -12), (up + 0.6, 0, 0.0, 0, 0, 0, 0)]
    for tt, pt, dz, hip, knee, bh, bk in seq:
        body.rotation_euler = (math.radians(pt), 0, 0)
        body.location = (0, 0, 1.18 + dz)
        body.keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
        body.keyframe_insert("location", frame=max(1, Q.T(tt)))
        for nm, hp, kn in (("FL", hip, knee), ("FR", hip * 0.85, knee * 0.9), ("BL", bh, bk), ("BR", bh * 0.9, bk * 0.9)):
            C[f"leg.{nm}"].rotation_euler = (math.radians(hp), 0, 0)
            C[f"knee.{nm}"].rotation_euler = (math.radians(kn), 0, 0)
            C[f"leg.{nm}"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
            C[f"knee.{nm}"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
    for tt, a in ((t + 0.1, -25), (t + 0.5, 30), (t + 1.2, 10), ((up or t + 2) - 0.3, -20), ((up or t + 2) + 0.4, 0)):
        C["neck"].rotation_euler = (math.radians(a), 0, 0)
        C["neck"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))


def horse_idle(C, t0, t1, seed=0, legs=True):
    """Stehendes Pferd, lebendig (Nutzer: Pferd „hängt“/zu steif): Beine gerade, atmet, Kopf hebt/senkt sich (schnuppert am Boden),
    schaut umher, schlägt mit dem Schweif, scharrt ab und zu mit einem Vorderhuf, verlagert das Gewicht."""
    rnd = random.Random(seed)
    nk, body, tl = C["neck"], C["body"], C["tail"]
    if legs:
        for nm in ("FL", "FR", "BL", "BR"):
            for j in ("leg", "knee"):
                C[f"{j}.{nm}"].rotation_euler = (0, 0, 0)
                C[f"{j}.{nm}"].keyframe_insert("rotation_euler", frame=max(1, Q.T(t0)))
    t = t0
    while t < t1:   # Kopf: umherschauen / tief zum Boden (schnuppern) / hoch (lauschen)
        kind = rnd.random()
        if kind < 0.25:
            ang = (rnd.uniform(26, 38), rnd.uniform(-10, 10))
        elif kind < 0.45:
            ang = (rnd.uniform(-14, -8), rnd.uniform(-18, 18))
        else:
            ang = (rnd.uniform(-4, 12), rnd.uniform(-16, 16))
        nk.rotation_euler = (math.radians(ang[0]), 0, math.radians(ang[1]))
        nk.keyframe_insert("rotation_euler", frame=max(1, Q.T(t)))
        t += rnd.uniform(1.1, 2.2)
    for f in range(max(1, Q.T(t0)), Q.T(t1) + 1, 3):
        tt = (f - 1) / Q.FPS
        tl.rotation_euler = (math.radians(12 + 4 * math.sin(tt * 1.3)), 0, math.radians(14 * math.sin(tt * 2.6 + seed) * (0.5 + 0.5 * math.sin(tt * 0.4))))
        tl.keyframe_insert("rotation_euler", frame=f)
        body.location = (0, 0, 1.18 + 0.007 * math.sin(tt * 2.1 + seed))
        body.rotation_euler = (math.radians(0.6 * math.sin(tt * 0.5 + seed)), math.radians(1.2 * math.sin(tt * 0.33 + seed)), 0)
        body.keyframe_insert("location", frame=f)
        body.keyframe_insert("rotation_euler", frame=f)
    if legs:   # ab und zu scharrt ein Vorderhuf
        t = t0 + rnd.uniform(0.8, 2.0)
        while t < t1 - 0.8:
            nm = rnd.choice(("FL", "FR"))
            for tt, hip, kn in ((t, 0, 0), (t + 0.18, -14, 70), (t + 0.36, 6, 15), (t + 0.55, 0, 0)):
                C[f"leg.{nm}"].rotation_euler = (math.radians(hip), 0, 0)
                C[f"knee.{nm}"].rotation_euler = (math.radians(kn), 0, 0)
                C[f"leg.{nm}"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
                C[f"knee.{nm}"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tt)))
            t += rnd.uniform(2.5, 4.5)


def sand_ring(name, loc, t, r=0.5, yaw=0.0):
    """v2: Sandwall um die eingesunkenen Vorderbeine (wächst beim Einsinken aus dem Boden, kein dunkles Loch mehr)."""
    o = sand_heap(name, loc, r * 1.25, r * 0.95, 0.22, seed=3, yaw=yaw)
    o["person"] = 1   # animiert -> nicht mit join_static verschmelzen
    o.scale = (0.4, 0.4, 0.001)
    o.keyframe_insert("scale", frame=1)
    o.keyframe_insert("scale", frame=max(1, Q.T(t)))
    o.scale = (0.9, 0.9, 0.8)
    o.keyframe_insert("scale", frame=max(1, Q.T(t + 0.25)))
    o.scale = (1.0, 1.0, 1.0)
    o.keyframe_insert("scale", frame=max(1, Q.T(t + 1.2)))
    return o


def smoke_dust(prefix, loc, cam, t0, dur=6.0, n=16, seed=0, rise=1.4, alpha=0.6, spread=0.6, size=(1.6, 2.2)):
    """Staub steigt auf wie Rauch: viele Karten, die nach oben treiben und gross werden."""
    rnd = random.Random(seed)
    for k in range(n):
        a0 = t0 + k * 0.08 + rnd.uniform(0, 0.2)
        p = (loc[0] + rnd.uniform(-spread, spread), loc[1] + rnd.uniform(-spread, spread), loc[2] + rnd.uniform(0.1, 0.9))
        BW.dust_card(f"{prefix}{k}", p, (size[0] * rnd.uniform(0.75, 1.25), size[1] * rnd.uniform(0.75, 1.25)), cam, a0,
                     a0 + dur * rnd.uniform(0.8, 1.1), alpha * rnd.uniform(0.75, 1.0),
                     grow=rnd.uniform(2.2, 3.2), drift=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rise * rnd.uniform(0.7, 1.3)),
                     fade_in=0.3, fade_out=2.2, col=(0.95, 0.84, 0.7))


def smoke_mat():
    """Wie BW.dust_mat, aber feinere, kontrastreichere Fetzen (Staubsäule sah als weiche Wolke wie ein Fleck aus)."""
    if "h_smoke" in bpy.data.materials:
        return bpy.data.materials["h_smoke"]
    m = BW.dust_mat().copy()
    m.name = "h_smoke"
    for nd in m.node_tree.nodes:
        if nd.type == "TEX_NOISE":
            nd.inputs["Scale"].default_value = 3.4
            nd.inputs["Detail"].default_value = 6.0
        elif nd.type == "MAP_RANGE":
            nd.inputs["From Min"].default_value = 0.42
            nd.inputs["From Max"].default_value = 0.66
    return m


def smoke_column(prefix, base, cam, t0, t_emit=2.4, n=30, seed=0, height=5.5, wind=(0.0, 0.0)):
    """Staubsäule wie Rauch (v2-QA): schmale Karten steigen nacheinander vom Boden auf, werden oben breiter, der Wind
    versetzt sie leicht – statt weniger riesiger Karten, die zu einem verschwommenen Fleck verschmolzen."""
    rnd = random.Random(seed)
    mat = smoke_mat()
    for k in range(n):
        a0 = t0 + t_emit * k / n + rnd.uniform(0, 0.1)
        life = rnd.uniform(2.4, 3.4)
        p = (base[0] + rnd.uniform(-0.3, 0.3), base[1] + rnd.uniform(-0.3, 0.3), base[2] + rnd.uniform(0.15, 0.8))
        w = rnd.uniform(0.6, 1.4)
        o = BW.dust_card(f"{prefix}{k}", p, (rnd.uniform(0.65, 0.95), rnd.uniform(0.85, 1.25)), cam, a0, a0 + life,
                         rnd.uniform(0.65, 0.9), grow=rnd.uniform(2.0, 2.8),
                         drift=(wind[0] * w, wind[1] * w, height / life * rnd.uniform(0.7, 1.1)), fade_in=0.25, fade_out=1.4,
                         col=(0.9, 0.78, 0.64))
        o.data.materials[0] = mat


def _sand_mat():
    return MK.M["sand"]   # gleiche Farbe wie der Boden (v2-Test: eigener Sand war zu hell)


def sand_heap(name, center, rx, ry, h, seed=0, yaw=0.0, mat=None):
    """Aufgeworfener Sandwall (Ring mit unregelmäßiger Höhe, innen tiefer) – Mesh-Objekt, Ursprung am Boden."""
    import bmesh
    from mathutils import noise as _nz
    bm = bmesh.new()
    nr, na = 7, 40
    grid = []
    for i in range(nr + 1):
        u = i / nr   # 0 = Mitte, 1 = Rand aussen
        row = []
        for j in range(na):
            a = 2 * math.pi * j / na
            rr = 0.25 + 0.95 * u
            x, y = rx * rr * math.cos(a), ry * rr * math.sin(a)
            n_ = _nz.noise(Vector((x * 3.0 + seed, y * 3.0, 0.5)))
            prof = math.sin(math.pi * min(1.0, u * 1.25)) if u > 0.08 else -0.4   # Wall: aussen hoch, innen Mulde
            z = h * (prof * (0.8 + 0.4 * n_)) - (0.05 if u < 0.3 else 0.0)
            row.append(bm.verts.new((x, y, max(-0.12, z) if u < 0.999 else -0.03)))
        grid.append(row)
    for i in range(nr):
        for j in range(na):
            bm.faces.new((grid[i][j], grid[i][(j + 1) % na], grid[i + 1][(j + 1) % na], grid[i + 1][j]))
    bm.faces.new(list(reversed(grid[0])))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat or _sand_mat())
    o = bpy.data.objects.new(name, me)
    Q.link(o)
    o.location = center
    o.rotation_euler = (0, 0, yaw)
    return o


def sand_spray(prefix, src, dirv, t, n=36, seed=0, speed=(1.5, 3.4), up=(1.6, 3.6), size=(0.012, 0.035)):
    """Sandbrocken fliegen weg (ballistisch, je Bild ein Schlüssel) und bleiben liegen."""
    rnd = random.Random(seed)
    m = _sand_mat()
    for k in range(n):
        a = math.atan2(dirv.y, dirv.x) + rnd.uniform(-1.2, 1.2)
        v = rnd.uniform(*speed)
        vx, vy, vz = math.cos(a) * v, math.sin(a) * v, rnd.uniform(*up)
        s = rnd.uniform(*size)
        o = Q.ball(f"{prefix}{k}", (0, 0, 0), (s, s * rnd.uniform(0.5, 0.9), s * rnd.uniform(0.4, 0.7)), m, seg=5)
        o.rotation_euler = (rnd.uniform(0, 3), rnd.uniform(0, 3), rnd.uniform(0, 3))
        o.visible_shadow = False
        p0 = Vector(src) + Vector((rnd.uniform(-0.15, 0.15), rnd.uniform(-0.15, 0.15), 0.05))
        t0 = t + rnd.uniform(0.0, 0.18)
        o.scale = (0.001, 0.001, 0.001)
        o.location = p0
        o.keyframe_insert("scale", frame=1)
        o.keyframe_insert("location", frame=1)
        o.keyframe_insert("scale", frame=max(1, Q.T(t0) - 1))
        o.keyframe_insert("location", frame=max(1, Q.T(t0) - 1))
        o.scale = (1, 1, 1)
        landed = False
        for f in range(Q.T(t0), Q.T(t0 + 1.6)):
            tt = (f - Q.T(t0)) / Q.FPS
            x, y = p0.x + vx * tt, p0.y + vy * tt
            z = p0.z + vz * tt - 4.9 * tt * tt
            zg = gz(x, y) + s * 0.5
            if z <= zg and tt > 0.05:
                z = zg
                landed = True
            o.location = (x, y, z)
            o.keyframe_insert("location", frame=f)
            o.keyframe_insert("scale", frame=f)
            if landed:
                break


def sand_drip(prefix, C, legs, t0, t1, seed=0, every=0.05):
    """Sand rieselt von den herausgezogenen Beinen (kleine Brocken fallen von den Knien/Hufen)."""
    rnd = random.Random(seed)
    m = _sand_mat()
    k = 0
    t = t0
    pts = {}
    while t < t1:
        nm = rnd.choice(legs)
        Q.sc.frame_set(Q.T(t))
        src = C[f"knee.{nm}"].matrix_world @ Vector((0, rnd.uniform(-0.05, 0.05), rnd.uniform(-0.45, -0.05)))
        s = rnd.uniform(0.015, 0.035)
        o = Q.ball(f"{prefix}{k}", (0, 0, 0), (s, s, s), m, seg=5)
        o.visible_shadow = False
        o.scale = (0.001, 0.001, 0.001)
        o.location = src
        o.keyframe_insert("scale", frame=max(1, Q.T(t) - 1))
        o.scale = (1, 1, 1)
        for f in range(Q.T(t), Q.T(t + 0.7)):
            tt = (f - Q.T(t)) / Q.FPS
            z = max(gz(src.x, src.y), src.z - 4.9 * tt * tt)
            o.location = (src.x, src.y, z)
            o.keyframe_insert("location", frame=f)
            o.keyframe_insert("scale", frame=f)
        t += every * rnd.uniform(0.6, 1.4)
        k += 1
    Q.sc.frame_set(1)


def set_z(P_, t0, t1):
    """walk() hält z konstant: z je Schlüsselbild aus dem Gelände nachziehen."""
    fcs = Q.fcurves(P_["root"])
    xs = [f for f in fcs if f.data_path == "location" and f.array_index == 0]
    ys = [f for f in fcs if f.data_path == "location" and f.array_index == 1]
    if not xs or not ys:
        return
    r = P_["root"]
    for fr in range(Q.T(t0), Q.T(t1) + 1):   # v2: JE BILD (vorher jedes 3. -> z sprang hin und her, der Läufer „hing“)
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
    # v2 (Nutzer: Abu Bakr kam „durch eine schwarze Wand“): echte Türnische ins Haus schneiden (Boolean), innen ein warmes Licht –
    # er steht im Halbdunkel des Flurs und tritt heraus (vorher: schwarzes Kästchen auf massiver Wand)
    hb = bpy.data.objects["hAB_body"]
    dh_ = bpy.data.objects.get("hAB_dhole")
    if dh_:
        bpy.data.objects.remove(dh_)
    cut = Q.box("hAB_cut", (door.x + 0.85, door.y, 0.92), (2.1, 0.93, 2.04), MK.M["sand"])   # ragt über Wand/Boden hinaus
    mo = hb.modifiers.new("door_cut", "BOOLEAN")
    mo.operation, mo.solver, mo.object = "DIFFERENCE", "EXACT", cut
    with bpy.context.temp_override(object=hb, active_object=hb, selected_objects=[hb], selected_editable_objects=[hb]):
        bpy.ops.object.modifier_apply(modifier=mo.name)
    bpy.data.objects.remove(cut)
    Q.box("hAB_back", (door.x + 1.92, door.y, 0.97), (0.04, 0.95, 1.94), MD.M["wood_dark"])   # Rückwand: Vorhang/Tür ins Haus
    Q.box("hAB_mat", (door.x + 1.0, door.y, 0.01), (1.6, 0.8, 0.02), MK.M["blanket_r"])
    li = bpy.data.lights.new("hAB_lamp", "POINT")
    li.energy, li.color, li.shadow_soft_size = 18.0, (1.0, 0.72, 0.45), 0.3
    lo = bpy.data.objects.new("hAB_lamp", li)
    Q.link(lo)
    lo.location = (door.x + 1.4, door.y + 0.25, 1.75)
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
    AB["root"].location = (door.x + 1.25, door.y, 0)
    Q.walk(AB, [(door.x + 1.25, door.y), (door.x - 0.55, door.y - 0.1)], t_open + 0.2, speed=0.85)
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


def fitted_web(name, Cv, seed=2, rings=15, spokes=12):
    """v2 (Nutzer: Netz „durch die Wand“): Öffnung im Fels per Strahlen vermessen, Netz genau IN der Öffnung aufspannen –
    jede Speiche endet am Felsrand bzw. am Sandboden. Rückgabe: (Wurzel, Mitte Welt, Abstand Felsfläche lokal-y)."""
    import bmesh
    from mathutils.bvhtree import BVHTree
    rnd = random.Random(seed)
    root, rock = Cv["root"], Cv["rock"]
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    bvh = BVHTree.FromObject(rock, dg)
    Mr, Ri = rock.matrix_world.copy(), root.matrix_world.copy()
    Mi = Mr.inverted()

    def cast(o_l, d_l, maxd=4.0):
        o_w = Ri @ Vector(o_l)
        d_w = (Ri.to_3x3() @ Vector(d_l)).normalized()
        o_r = Mi @ o_w
        d_r = (Mi.to_3x3() @ d_w).normalized()
        hit = bvh.ray_cast(o_r, d_r, 50.0)
        if hit[0] is None:
            return None
        dist = ((Mr @ hit[0]) - o_w).length
        return dist if dist <= maxd else None
    ys = []
    for j in range(20):
        a = 2 * math.pi * j / 20
        for rr in (1.0, 1.25):
            x, z = rr * math.cos(a), 0.45 + rr * 0.8 * math.sin(a)
            if z < 0.08:
                continue
            dd = cast((x, -9.0, z), (0, 1, 0), 9.0)
            if dd:
                ys.append(-9.0 + dd)
    ys.sort()
    y_face = ys[len(ys) // 2] if ys else -3.6
    y_w = y_face + 0.22
    up = cast((0, y_w, 0.45), (0, 0, 1), 3.0)
    top = 0.45 + up if up else 1.1
    zc = (top + 0.03) / 2
    angs = sorted((2 * math.pi * k / spokes + rnd.uniform(-0.18, 0.18)) for k in range(spokes))
    lens = []
    for a in angs:
        r = cast((0, y_w, zc), (math.cos(a), 0, math.sin(a)), 2.5) or 0.7
        if math.sin(a) < -0.05:
            r = min(r, (zc - 0.03) / -math.sin(a))
        lens.append(max(0.12, min(r, 1.4)))
    m = bpy.data.materials.new(f"{name}_silk")
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.92, 0.92, 0.9, 1)
    b.inputs["Roughness"].default_value = 0.25
    b.inputs["Emission Color"].default_value = (1.0, 0.97, 0.9, 1)
    b.inputs["Emission Strength"].default_value = 0.8
    c_w = Ri @ Vector((0, y_w, zc))
    wr = Q.empty(name, tuple(c_w), rot=(0, 0, root.rotation_euler.z))
    bm = bmesh.new()
    th = 0.0014

    def strand(p0, p1, w=th):
        d = p1 - p0
        if d.length < 1e-4:
            return
        ax = d.normalized()
        upv = Vector((0, 1, 0)) if abs(ax.y) < 0.9 else Vector((1, 0, 0))
        s1 = ax.cross(upv).normalized() * w
        s2 = ax.cross(s1).normalized() * w
        vs = [bm.verts.new(p + o) for p in (p0, p1) for o in (s1, s2, -s1, -s2)]
        for i in range(4):
            bm.faces.new((vs[i], vs[(i + 1) % 4], vs[4 + (i + 1) % 4], vs[4 + i]))
    ends = [Vector((L * 1.01 * math.cos(a), 0, L * 1.01 * math.sin(a))) for a, L in zip(angs, lens)]
    hub = Vector((0, 0, 0))
    for e in ends:
        strand(hub, e)
    n = rings * spokes
    prev = None
    for i in range(n + 1):
        k = i % spokes
        u = 0.94 - i / n * 0.84
        p_ = ends[k] * u
        if prev is not None:
            mid = (prev + p_) * 0.5 + Vector((0, 0.002 * rnd.uniform(-1, 1), -0.006 * u))
            strand(prev, mid, th * 0.8)
            strand(mid, p_, th * 0.8)
        prev = p_
    for k in range(spokes):   # Randfaden entlang des Felsrandes
        strand(ends[k] * 0.98, ends[(k + 1) % spokes] * 0.98, th * 0.9)
    me = bpy.data.meshes.new(f"{name}_me")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(m)
    o = bpy.data.objects.new(f"{name}_web", me)
    Q.link(o)
    o.parent = wr
    o.visible_shadow = False
    ms = Q.pbr(f"{name}_sp_m", (0.03, 0.025, 0.02), 0.4)
    sp = Q.empty(f"{name}_spider", (0.04, -0.004, 0.05), wr)
    Q.ball(f"{name}_sp_b", (0, 0, 0), (0.012, 0.009, 0.016), ms, parent=sp, seg=10)
    Q.ball(f"{name}_sp_h", (0, 0, 0.017), 0.007, ms, parent=sp, seg=8)
    for s_ in (-1, 1):
        for j in range(4):
            a = math.radians(-50 + j * 33)
            Q.limb(f"{name}_sp_l{j}{s_}", (0, 0, 0.008), (s_ * 0.03 * math.cos(a), -0.002, 0.03 * math.sin(a) + 0.008), 0.0012, 0.0008,
                   ms, parent=sp, seg=4)
    wr["person"] = 1
    print("WEB", name, "Felsfläche y", round(y_face, 2), "Mitte z", round(zc, 2), "Speichen", [round(L, 2) for L in lens])
    return wr, c_w, y_face


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
    WEB, web_c, y_face = fitted_web("web", C)
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
    """Vor der Höhle: die Verfolger kommen den Hang herauf, einer beugt sich zur Öffnung – darin ein unberührtes Spinnennetz.
    „Wäre er hier drin …“ – sie gehen weiter, bergab. v2 (Nutzer: Netz „durch die Wand“, Männer kaum zu sehen): Netz genau in der
    vermessenen Öffnung; die Männer stehen groß und hell im Bild (Kamera hinter ihnen, über die Schulter), am Ende bleibt das Netz."""
    cs, C = cave_setup(day=True)
    cfg = MK.light("day")
    WEB, web_c, y_face = fitted_web("web", C)
    for o in list(bpy.data.objects):   # Felsbrocken direkt vor dem Eingang weg (standen Kamera und Männern im Weg)
        if o.name.startswith("crk"):
            lp = o.location
            if abs(lp.x) < 2.2 and lp.y < -3.8:
                bpy.data.objects.remove(o)
    tv = ls("v1")
    tn = ev("spinnennetz_c5", ls("c5") + 2.2)
    te = ev("entfernen_c6", ls("c6") + 0.8)
    yf = y_face

    def at(x, y):
        p_ = cv((x, y, 0), cs)
        return (p_[0], p_[1])
    # dunkles Höhleninneres hinter dem Netz (sonst hellgrau: EEVEE hat innen kein echtes Dunkel) -> Netz leuchtet vor Schwarz
    dm = Q.pbr("cave_dark", (0.006, 0.005, 0.004), 1.0)
    dk = Q.box("cave_dark", cv((0.0, yf + 0.5, 0.5), cs), (3.0, 0.05, 2.0), dm)
    dk.rotation_euler = (0, 0, math.pi)
    dk.visible_shadow = False
    spots = [(-0.42, yf - 0.8), (0.78, yf - 1.35), (-0.95, yf - 1.9)]
    starts = [(-0.6, yf - 3.7), (1.0, yf - 4.3), (-1.3, yf - 4.9)]
    sp = pursuers("vf", [(*at(*st_), 0.0) for st_ in starts], seed=7, weapon=None)
    for k, Pp in enumerate(sp):
        a_, b_ = at(*starts[k]), at(*spots[k])
        Pp["root"].rotation_euler.z = Q.face_yaw(a_, b_)
        t_arr = Q.walk(Pp, [a_, b_], 0.0 + 0.2 * k, speed=1.15)
        set_z(Pp, 0.0, t_arr + 0.1)
        Pp["root"].keyframe_insert("rotation_euler", frame=max(1, Q.T(t_arr)))
        Pp["root"].rotation_euler.z = Q.face_yaw(b_, at(0.0, yf))
        Pp["root"].keyframe_insert("rotation_euler", frame=max(1, Q.T(t_arr + 0.5)))
    # A beugt sich zur Öffnung, zeigt aufs Netz, richtet sich auf, winkt ab, dreht sich zu B
    A = sp[0]
    tb = tn - 0.6
    A["chest"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tb - 0.4)))
    A["chest"].rotation_euler = (math.radians(34), 0, math.radians(-8))
    A["chest"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tb + 0.3)))
    Q.arm_pose(A, tb, "R", -10, -10)
    Q.arm_pose(A, tb + 0.6, "R", -75, -15)
    A["chest"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tv - 0.2)))
    A["chest"].rotation_euler = (0, 0, math.radians(25))
    A["chest"].keyframe_insert("rotation_euler", frame=max(1, Q.T(tv + 0.5)))
    Q.arm_pose(A, tv + 0.2, "R", -45, -60)
    Q.arm_pose(A, tv + 0.8, "R", -30, 20)
    Q.arm_pose(A, tv + 1.6, "R", -10, -10)
    Q.head_to(sp[1], tv + 0.3, tuple(Vector(cv((-0.55, yf - 1.05, 1.5), cs))))
    # weg, bergab an der Kamera vorbei
    down = [(-2.4, yf - 15.0), (2.2, yf - 15.5), (0.6, yf - 16.5)]
    for k, Pp in enumerate(sp):
        a_, b_ = at(*spots[k]), at(*down[k])
        t0_ = te - 1.4 + 0.3 * k
        Pp["root"].keyframe_insert("rotation_euler", frame=max(1, Q.T(t0_ - 0.4)))
        Pp["root"].rotation_euler.z = Q.face_yaw(a_, b_)
        Pp["root"].keyframe_insert("rotation_euler", frame=max(1, Q.T(t0_)))
        t_arr = Q.walk(Pp, [a_, b_], t0_, speed=1.4)
        set_z(Pp, t0_, min(t_arr, D + 0.5))
    rig, shake, cam = Q.pov_camera(lens=19)
    web = tuple(web_c)
    def G(x, y, h):
        p_ = cv((x, y, 0), cs)
        return (p_[0], p_[1], gz(p_[0], p_[1]) + h)
    c0 = G(0.3, yf - 6.3, 1.65)
    c1 = G(0.3, yf - 3.0, 1.5)
    c2 = G(0.08, yf - 1.25, 0.85)
    mid = G(-0.2, yf - 0.9, 1.15)
    ck(rig, [(0, c0, look(c0, G(0.0, yf - 1.0, 0.9))), (tv - 0.3, c1, look(c1, web)), (tv + 1.2, None, look(c1, mid)),
             (te - 0.6, None, look(c1, web)), (D, c2, look(c2, web))])
    Q.handheld(shake, 0, D, amp=0.4)
    cfg["mist_amt"] = 0.14
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
    """Hinter dem Zelt, heimlich: Ich gehe mit gesenktem Speer zum Pferd hinter dem Hügel, steige auf – und galoppiere los.
    v2: Pferd steht lebendig (Beine gerade statt im Galoppsprung erstarrt), läuft weich an; Zügel am Maul; ruhigere Kamera."""
    hx, hy = TENT.x + 14.0, TENT.y - 10.0
    run = [(hx, hy), (hx - 10.0, hy - 22.0), (hx - 30.0, hy - 70.0), (hx - 52.0, hy - 120.0)]
    HW.coast_world(keep=[(TENT.x, TENT.y, 12.0), (hx, hy, 6.0)] + line_keep(run, 5.0))
    cfg = MK.light("day")
    tz = gz(TENT.x, TENT.y)
    HW.bedouin_tent("tent", (TENT.x, TENT.y, tz), yaw=-math.pi / 2)
    MK.rock_hill("huegel", Vector((hx + 3.0, hy + 6.0, gz(hx + 3, hy + 6))), 6.0, 2.4, seed=4)
    Hs = suraqa_horse("sh", (hx, hy, gz(hx, hy)), yaw=Q.face_yaw((hx, hy), run[1]))
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
    Q.handheld(shake, 0, tm, amp=0.5, walk_from=0.0, walk_to=tm - 0.2, walk_amp=0.8)
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
    ck(rig, [(ta, w1, look(w1, (hx, hy, 1.3)))])
    # Pferd steht bis zum Losreiten (lebendig), dann weicher Anlauf; Kamera ab dem Schnitt im Sattel
    ride(Hs, rig, run, tg - 0.1, D + 0.5, speed=10.0, cam_from=tb_, accel=1.5, horse_from=0.0, pitch=-3.0)
    reins(Hh, Hs, off=[(0.0, tb_)])
    ride_dust(Hs, cam, tg + 0.4, D + 0.5)
    Q.handheld(shake, tm + 0.01, D + 0.5, amp=0.35, hits=[(tg + 0.1, 0.5)])
    for ob in [rig, Hh["L"], Hh["R"]]:   # Schlüssel vor dem Schnitt CONSTANT -> Sprung genau zwischen fcut-1 und fcut
        for fc in Q.fcurves(ob):
            for kp in fc.keyframe_points:
                if int(round(kp.co.x)) == fcut - 1:
                    kp.interpolation = "CONSTANT"
    cfg["mist_amt"] = 0.18
    cfg["mblur"] = 0.5
    return cfg


def far_caravan(y, t1, speed=1.5, off=24.0, seed=0, day=True, guide=True):
    return caravan(cx(y, off), y, 0.0, t1, speed=speed, heading=-3, seed=seed, day=day, guide=guide)


def shot_jagd():
    """(Quelle für den Einstieg) Galopp an der Küste entlang, weit vorn die Kamele. v2: weich, Zügel am Maul, Bewegungsunschärfe."""
    y0 = -200.0
    pth = coast_path(y0, y0 + 110, 30.0)
    HW.coast_world(keep=line_keep(pth, 5.0) + line_keep(coast_path(-80, 60, 24.0), 4.0))
    cfg = MK.light("morning")
    far_caravan(-40.0, D + 1, speed=1.5)
    Hs = suraqa_horse("sh", (pth[0][0], pth[0][1], gz(*pth[0])))
    rig, shake, cam = Q.pov_camera(lens=17)
    Hh = pov_rider(cam, spear_=False)
    pose(Hh, 0, "reins")
    ride(Hs, rig, pth, 0.0, D + 0.5, speed=10.5, yaw_off=lambda t: 5 * math.sin(t * 0.6))
    reins(Hh, Hs)
    ride_dust(Hs, cam, 0.0, D + 0.5)
    Q.handheld(shake, 0, D + 0.5, amp=0.35)
    cfg["mist_amt"] = 0.2
    cfg["mblur"] = 0.5
    return cfg


def slide_root(C, sp, G, t0, t1):
    """Nach dem Ende von horse_go: Pferd rutscht mit dem Tempo-Verlauf G noch weiter (nur Ort/Richtung)."""
    root = C["root"]
    prev = root.rotation_euler.z
    for f in range(Q.T(t0) + 1, Q.T(t1) + 1):
        t = (f - 1) / Q.FPS
        d = G.d(t)
        pos, dv = sp.at(d), sp.tangent(d)
        z, _ = _ground(pos, dv)
        root.location = (pos.x, pos.y, z)
        root.keyframe_insert("location", frame=f)
        yaw = _unwrap(math.atan2(dv.x, -dv.y), prev)
        prev = yaw
        root.rotation_euler = (0, 0, yaw)
        root.keyframe_insert("rotation_euler", index=2, frame=f)


def cam_state(rig, t):
    """Ort + Gierwinkel (Grad) der Kamera bei t (aus den Schlüsseln)."""
    Q.sc.frame_set(Q.T(t))
    return rig.location.copy(), math.degrees(rig.rotation_euler.z)


def shot_ritt():
    """Ich galoppiere den Spuren nach – dann stolpert das Pferd, ich stürze in den Sand.
    v2: weicher Galopp, Pferd rutscht beim Stolpern weiter, Sturz nach vorn über die Schulter (Hände fangen ab)."""
    y0 = -130.0
    ts = ev("stolpert_s6", ls("s6") + 1.6)
    sp_ = 10.0
    pth = coast_path(y0, y0 + sp_ * ts + 30, 30.0, n=4)
    HW.coast_world(keep=line_keep(coast_path(y0, y0 + 80, 30.0), 6.0))
    cfg = MK.light("day")
    far_caravan(-20.0, D + 1, speed=1.5)
    Hs = suraqa_horse("sh", (pth[0][0], pth[0][1], gz(*pth[0])))
    rig, shake, cam = Q.pov_camera(lens=17)
    Hh = pov_rider(cam, spear_=False)
    pose(Hh, 0, "reins")
    spath, G = ride(Hs, rig, pth, 0.0, ts, speed=sp_, t_stop=ts - 0.05, decel=0.32)
    slide_root(Hs, spath, G, ts, ts + 0.6)
    stumble(Hs, ts, up=ts + 2.6)
    horse_idle(Hs, ts + 3.4, D + 0.5, seed=2)
    loc0, yw0 = cam_state(rig, ts)
    d_end = G.d(ts + 0.6)
    pos = spath.at(d_end)
    dv = spath.tangent(G.d(ts))
    land = fall_off(rig, shake, ts, tuple(loc0), dv, side=1, Hh=Hh, yaw0=yw0, fwd=3.6, out=2.4)
    reins(Hh, Hs, off=[(ts + 0.12, None)])
    sitp = (land.x, land.y, gz(land.x, land.y) + 0.95)
    hz = (pos.x, pos.y, gz(pos.x, pos.y) + 1.2)
    pose(Hh, ts + 1.9, "push")
    pose(Hh, ts + 2.5, "hidden")
    ck(rig, [(ts + 1.7, None, None), (ts + 2.5, sitp, look(sitp, hz)), (D, sitp, look(sitp, (pos.x, pos.y, gz(pos.x, pos.y) + 1.5)))])
    ride_dust(Hs, cam, 0.0, ts + 0.5)
    hf = spath.at(G.d(ts) + 0.6)
    sand_spray("fsp", (hf.x, hf.y, gz(hf.x, hf.y)), dv, ts + 0.15, n=30, seed=4, speed=(1.0, 2.6), up=(1.0, 2.4))
    smoke_dust("stum", (hf.x, hf.y, gz(hf.x, hf.y)), cam, ts + 0.1, dur=3.0, n=8, rise=0.6, alpha=0.6, spread=0.5, size=(1.6, 1.1))
    lz = (land.x + dv.x * 1.6, land.y + dv.y * 1.6, gz(land.x, land.y))
    smoke_dust("fall_puff", lz, cam, ts + 0.62, dur=2.4, n=5, rise=0.4, alpha=0.4, spread=0.4, size=(1.2, 0.8))
    Q.handheld(shake, 0, D, amp=0.35, hits=[(ts + 0.05, 0.5), (ts + 0.62, 1.4)])
    cfg["mist_amt"] = 0.2
    cfg["mblur"] = 0.5
    return cfg


def _mat(X, Y, Z, p):
    from mathutils import Matrix
    M = Matrix.Identity(4)
    for i in range(3):
        M[i][0], M[i][1], M[i][2], M[i][3] = X[i], Y[i], Z[i], p[i]
    return M


def _hand_world(H, W, f):
    """Hand H (Kind der Kamera) per Schlüssel so stellen, dass ihre Weltmatrix in Bild f genau W ist."""
    Q.sc.frame_set(f)
    par = H.parent
    basis = (par.matrix_world @ H.matrix_parent_inverse).inverted() @ W
    loc, rot, _ = basis.decompose()
    H.location = loc
    H.rotation_euler = rot.to_euler("XYZ", H.rotation_euler)
    H.keyframe_insert("location", frame=f)
    H.keyframe_insert("rotation_euler", frame=f)


def _vis(objs, keys):
    """keys = [(bild, sichtbar)], harte Wechsel."""
    for o in objs:
        for ch in [o] + list(o.children_recursive):
            for f, on in keys:
                ch.hide_render = not on
                ch.keyframe_insert("hide_render", frame=max(1, f))


def azlam_bundle(name, parent, loc, rot):
    """Drei Lospfeile (ohne Spitze/Federn), einer mit dunklem Band („Nein“). Rückgabe: (Bündel-Empty, [Pfeile])."""
    b = Q.empty(name, loc, parent, rot=rot)
    arr = []
    for k in range(3):
        a = KW.arrow(f"{name}_a{k}", (0.011 * (k - 1), 0.0, 0.004 * (k % 2)), parent=b, rot=(0, math.radians(7 * (k - 1)), 0), length=0.5, done=False)
        arr.append(a)
    Q.box(f"{name}_band", (0, 0.17, 0), (0.016, 0.045, 0.016), MK.M["blanket_b"], parent=arr[1])
    return b, arr


def shot_lose():
    """Im Sand sitzend: der Köcher liegt neben mir. Die rechte Hand greift hinein, zieht die Lospfeile heraus, schüttelt sie;
    die linke zieht einen Pfeil – das Band heisst „Nein“. Ich werfe ihn weg und stehe auf.
    v2 (Nutzer: Pfeil erschien plötzlich rechts): Übergabe genau dort, wo die Hand das Bündel greift (Weltmatrix wird angeglichen)."""
    y0 = -60.0
    x0 = cx(y0, 30.0)
    HW.coast_world(keep=[(x0, y0, 8.0)])
    cfg = MK.light("day")
    Hs = suraqa_horse("sh", (x0 + 2.4, y0 + 3.2, gz(x0 + 2.4, y0 + 3.2)), yaw=Q.face_yaw((x0 + 2.4, y0 + 3.2), (x0 - 4, y0 + 30)))
    horse_idle(Hs, 0, D, seed=3)
    far_caravan(70.0, D + 1, speed=1.5)
    rig, shake, cam = Q.pov_camera(lens=18)
    Hh = MK.pov_arms(cam, skin=(0.4, 0.26, 0.17), sleeve=(0.42, 0.32, 0.22))
    fists(Hh)
    tp = ev("lospfeile_s7", ls("s7") + 0.6)
    tn = ev("nein_s7", ls("s7") + 4.0)
    tw = ev("weiter_s7", le("s7") - 0.6)
    sit = (x0, y0, gz(x0, y0) + 0.95)
    stand = (x0 + 0.6, y0 + 1.0, gz(x0, y0) + EYE)
    hy = Q.yaw_to(sit, (x0 + 2.4, y0 + 3.2))
    yq = hy - 38   # Blick links unten zum Köcher
    bh, arh = azlam_bundle("bh", Hh["R"], (0.0, 0.085, -0.012), (0, 0, math.radians(90)))
    la = KW.arrow("al_l", (0.0, 0.085, -0.012), parent=Hh["L"], rot=(0, 0, math.radians(-90)), length=0.5, done=False)
    Q.box("al_l_band", (0, 0.17, 0), (0.016, 0.045, 0.016), MK.M["blanket_b"], parent=la)
    # Kamera: sitzt, schaut zum Köcher, dann auf die Hand mit dem Bündel, dann steht auf
    tgr = tp - 0.15
    ck(rig, [(0, sit, (yq + 6, -40, 0)), (tgr + 0.6, None, (yq + 18, -24, 0)), (tn - 1.1, None, (yq + 24, -18, 0)),
             (tn + 1.4, None, (yq + 28, -16, 0)), (tw - 0.3, sit, (hy - 5, -12, 0)), (D, stand, (hy, -8, 0))])
    Q.handheld(shake, 0, D, amp=0.3)
    # rechte Hand greift in den Köcher: NATÜRLICHE Handhaltung festlegen (Handrücken oben, Finger von der rechten Schulter zum
    # Köcher), Bündel + Köcher danach ausrichten -> die Übergabe Köcher -> Hand ist unsichtbar (v2: Pfeil „erschien“ vorher plötzlich)
    pose(Hh, 0, "hidden")
    pose(Hh, tgr - 0.55, "hidden", only="R")
    fg = Q.T(tgr)
    Q.sc.frame_set(fg)
    Cw = cam.matrix_world.copy()
    cR, cU, cF = (Cw.to_3x3() @ Vector(v) for v in ((1, 0, 0), (0, 1, 0), (0, 0, -1)))
    cp = Cw.translation.copy()
    S = cp + cR * 0.22 - cU * 0.3
    fl, rl = Vector((cF.x, cF.y, 0)).normalized(), Vector((cR.x, cR.y, 0)).normalized()
    G0 = Vector((cp.x, cp.y, 0)) + fl * 0.58 - rl * 0.08
    G0.z = gz(G0.x, G0.y) + 0.05
    Yh = (G0 - S).normalized()
    Zh = (Vector((0, 0, 1)) - Yh * Yh.z).normalized()
    Xh = Yh.cross(Zh)
    M_R = _mat(Xh, Yh, Zh, G0 - Yh * 0.085 + Zh * 0.012)
    _hand_world(Hh["R"], M_R, fg)
    _hand_world(Hh["R"], M_R, fg + 4)
    bpy.context.view_layer.update()
    Wb = M_R @ bh.matrix_local
    bq, arq = azlam_bundle("bq", None, (0, 0, 0), (0, 0, 0))
    bq.matrix_world = Wb
    A = (Wb.to_3x3() @ Vector((0, 1, 0))).normalized()
    Zq = (Vector((0, 0, 1)) - A * A.z).normalized()
    quiv = Q.empty("quiver")
    quiv.matrix_world = _mat(A.cross(Zq), A, Zq, Wb.translation - A * 0.21)
    quiv["person"] = 1
    Q.cyl("quiver_c", (0, 0, 0), 0.045, 0.38, MK.M["leather"], seg=14, rot=(math.pi / 2, 0, 0), parent=quiv)
    Q.torus("quiver_r", (0, 0.19, 0), 0.046, 0.007, BW.M["tack"], parent=quiv).rotation_euler = (math.pi / 2, 0, 0)
    Q.box("quiver_strap", (0.0, -0.05, -0.04), (0.03, 0.3, 0.006), BW.M["tack"], parent=quiv)
    pose(Hh, tgr + 0.75, "bundle", only="R")
    for k, nm in enumerate(("shake_a", "shake_b", "shake_a", "shake_b", "bundle")):
        pose(Hh, tgr + 1.0 + 0.14 * k, nm, only="R")
    _vis([bq], [(1, True), (fg, True), (fg + 1, False)])
    _vis([bh], [(1, False), (fg, False), (fg + 1, True)])
    # linke Hand: greift das Ende des Pfeils mit Band (Hand natürlich von links, Handrücken oben), zieht ihn heraus
    td = tn - 0.85
    fd = Q.T(td)
    pose(Hh, td - 0.6, "hidden", only="L")
    pose(Hh, td - 0.25, "draw_l", only="L")
    pose(Hh, td - 0.5, "bundle", only="R")
    pose(Hh, td + 0.3, "bundle", only="R")
    pose(Hh, td + 0.6, "bundle", only="R")
    Q.sc.frame_set(fd)
    Cw = cam.matrix_world.copy()
    cR, cU = Cw.to_3x3() @ Vector((1, 0, 0)), Cw.to_3x3() @ Vector((0, 1, 0))
    W_a = arh[1].matrix_world.copy()
    A = (W_a.to_3x3() @ Vector((0, 1, 0))).normalized()
    c_ = W_a.translation.copy()
    e1, e2 = c_ + A * 0.19, c_ - A * 0.19
    grab = e1 if e1.dot(cR) < e2.dot(cR) else e2
    Xh = A.copy()
    Zh = (cU - A * cU.dot(A)).normalized()
    Yh = Zh.cross(Xh)
    if Yh.dot(cR) < 0:
        Xh = -A
        Yh = Zh.cross(Xh)
    M_L = _mat(Xh, Yh, Zh, grab - Yh * 0.085 + Zh * 0.012)
    _hand_world(Hh["L"], M_L, fd)
    _hand_world(Hh["L"], M_L, fd + 3)
    la.matrix_parent_inverse.identity()
    la.matrix_basis = M_L.inverted() @ W_a
    _vis([arh[1]], [(1, True), (fd, True), (fd + 1, False)])
    _vis([la], [(1, False), (fd, False), (fd + 1, True)])
    hand_pose(Hh, td + 0.55, "L", (-0.12, -0.02, -0.44), (-10, 0, -60))   # Pfeil hoch: das Band ist zu sehen
    hand_pose(Hh, tn + 0.5, "L", (-0.1, 0.0, -0.42), (-6, 0, -75))
    hand_pose(Hh, tn + 1.05, "L", (-0.2, 0.05, -0.38), (-30, 0, -40))   # ausholen
    hand_pose(Hh, tn + 1.3, "L", (-0.75, -0.25, -0.2), (-60, 0, -10))   # wegwerfen (aus dem Bild)
    pose(Hh, tn + 1.6, "hidden", only="L")
    pose(Hh, tn + 1.5, "away_r", only="R")
    pose(Hh, tn + 1.9, "hidden", only="R")
    _vis([la], [(Q.T(tn + 1.32), False)])
    Q.sc.frame_set(1)
    cfg["mist_amt"] = 0.2
    return cfg


def shot_nah():
    """Wieder im Galopp: vorn die Kamele, immer näher. Das Licht reitet ruhig, ohne sich umzudrehen; Abu Bakr dreht sich immer wieder um."""
    y0 = 20.0
    sp_ = 9.0
    pth = coast_path(y0, y0 + sp_ * (D + 1), 27.0, n=6)
    HW.coast_world(keep=line_keep(pth, 6.0) + line_keep(coast_path(100, 150, 23.0), 5.0))
    cfg = MK.light("day")
    CV = caravan(cx(118.0, 23.0), 118.0, 0.0, D + 1, speed=1.7, heading=-3)
    turn_back(CV["ab"], [(0.5, 0), (1.2, 150), (2.2, 150), (2.9, 0), (4.0, 0), (4.6, -150), (5.6, -150), (6.2, 0), (D - 1.0, 0),
                          (D - 0.5, 150)])
    Hs = suraqa_horse("sh", (pth[0][0], pth[0][1], gz(*pth[0])))
    rig, shake, cam = Q.pov_camera(lens=17)
    Hh = pov_rider(cam, spear_=False)
    pose(Hh, 0, "reins")
    ride(Hs, rig, pth, 0.0, D + 0.5, speed=sp_, yaw_off=lambda t: -3 * math.sin(t * 0.6))
    reins(Hh, Hs)
    ride_dust(Hs, cam, 0.0, D + 0.5)
    Q.handheld(shake, 0, D + 0.5, amp=0.35)
    cfg["mist_amt"] = 0.18
    cfg["mblur"] = 0.5
    return cfg


def key_pose(C, t, body=None, legs=None, neck=None):
    """Pferd-Pose zu Zeit t. body = (nicken°, z, y); legs = {"FL": (hüfte°, knie°), …}; neck = (nicken°, drehen°)."""
    f = max(1, Q.T(t))
    if body is not None:
        C["body"].rotation_euler = (math.radians(body[0]), 0, 0)
        C["body"].location = (0, body[2] if len(body) > 2 else 0.0, 1.18 + body[1])
        C["body"].keyframe_insert("rotation_euler", frame=f)
        C["body"].keyframe_insert("location", frame=f)
    for nm, (hp, kn) in (legs or {}).items():
        C[f"leg.{nm}"].rotation_euler = (math.radians(hp), 0, 0)
        C[f"knee.{nm}"].rotation_euler = (math.radians(kn), 0, 0)
        C[f"leg.{nm}"].keyframe_insert("rotation_euler", frame=f)
        C[f"knee.{nm}"].keyframe_insert("rotation_euler", frame=f)
    if neck is not None:
        C["neck"].rotation_euler = (math.radians(neck[0]), 0, math.radians(neck[1]))
        C["neck"].keyframe_insert("rotation_euler", frame=f)


def shot_versinken():
    """Die Vorderbeine des Pferdes versinken bis zu den Knien – ich falle. Das Pferd kämpft sich heraus, Staub steigt auf wie Rauch.
    v2 (Nutzer): Sandwall um die VORDERbeine (vorher dunkles Loch an den Hinterbeinen), Sand spritzt, rieselt von den Beinen,
    Pferd kämpft lebendig (Kopf, Beine abwechselnd), steigt heraus, schüttelt sich; dichter, gut sichtbarer Staub; besserer Sturz."""
    y0 = 150.0
    sp_ = 9.0
    tv = ev("versinken_s9", ls("s9") + 0.3)
    pth = coast_path(y0, y0 + sp_ * tv + 30, 27.0, n=3)
    HW.coast_world(keep=line_keep(coast_path(y0, y0 + 80, 27.0), 7.0) + line_keep(coast_path(170, 230, 23.0), 5.0))
    cfg = MK.light("day")
    CV = caravan(cx(188.0, 23.0), 188.0, 0.0, D + 1, speed=1.6, heading=-3)
    turn_back(CV["ab"], [(0.2, 0), (0.6, 150), (3.0, 150), (3.8, 0)])
    Hs = suraqa_horse("sh", (pth[0][0], pth[0][1], gz(*pth[0])))
    rig, shake, cam = Q.pov_camera(lens=17)
    Hh = pov_rider(cam, spear_=False)
    pose(Hh, 0, "reins")
    spath, G = ride(Hs, rig, pth, 0.0, tv, speed=sp_, t_stop=tv - 0.04, decel=0.3)
    slide_root(Hs, spath, G, tv, tv + 0.5)
    loc0, yw0 = cam_state(rig, tv)
    dv = spath.tangent(G.d(tv))
    pos = spath.at(G.d(tv + 0.5))
    yaw_h = math.atan2(dv.x, -dv.y)
    tm = ev("mühsam_s10", ls("s10") + 1.2)
    ts = ev("staub_s10", ls("s10") + 3.6)
    # --- Pferd: einsinken, kämpfen (Kopf wirft sich, Vorderbeine abwechselnd), heraus, schütteln
    key_pose(Hs, tv - 0.04, body=(0, 0.0), neck=(0, 0))
    key_pose(Hs, tv + 0.22, body=(21, -0.52), legs={"FL": (14, 0), "FR": (10, 0), "BL": (-18, -30), "BR": (-14, -25)}, neck=(-22, 6))
    key_pose(Hs, tv + 0.6, body=(19, -0.58), neck=(12, -10))
    t = tv + 1.0
    k = 0
    while t < tm - 0.3:   # erste Versuche
        key_pose(Hs, t, body=(18 + 2 * (k % 2), -0.58 + 0.04 * (k % 2)), neck=((-18, 15)[k % 2], (14, -12)[k % 2]))
        t += 0.55
        k += 1
    seq = [(tm - 0.2, (17, -0.56), {"FL": (-25, 55), "FR": (12, 0), "BL": (-24, -40), "BR": (-20, -36)}, (-24, 10)),
           (tm + 0.25, (8, -0.38), {"FL": (-40, 85), "FR": (14, 0)}, (-30, -8)),
           (tm + 0.6, (16, -0.55), {"FL": (10, 5), "FR": (-28, 60)}, (16, 12)),
           (tm + 1.0, (6, -0.36), {"FL": (14, 0), "FR": (-42, 88)}, (-26, -14)),
           (tm + 1.4, (15, -0.52), {"FL": (-20, 40), "FR": (8, 5)}, (10, 18)),
           (ts - 0.45, (12, -0.45), {"FL": (5, 0), "FR": (5, 0), "BL": (-30, -50), "BR": (-30, -50)}, (-10, 0)),
           (ts - 0.05, (-26, 0.22, 0.25), {"FL": (-58, 95), "FR": (-52, 100), "BL": (-8, -12), "BR": (-6, -10)}, (-30, 0)),
           (ts + 0.4, (-30, 0.3, 0.3), {"FL": (-62, 105), "FR": (-66, 98)}, (-28, 6)),
           (ts + 0.95, (-4, 0.02, 0.4), {"FL": (8, 10), "FR": (4, 12), "BL": (2, 0), "BR": (0, 0)}, (-6, 0)),
           (ts + 1.3, (0, 0.0, 0.4), {"FL": (0, 0), "FR": (0, 0), "BL": (0, 0), "BR": (0, 0)}, (4, 0))]
    for tt, bd, lg, nk in seq:
        key_pose(Hs, tt, body=bd, legs=lg, neck=nk)
    for j, tt in enumerate((ts + 1.5, ts + 1.62, ts + 1.74, ts + 1.86, ts + 1.98, ts + 2.15)):   # schüttelt sich
        key_pose(Hs, tt, neck=(6, (22, -22)[j % 2] if j < 5 else 0))
    horse_idle(Hs, ts + 2.4, D + 0.5, seed=5, legs=False)
    # Pferd macht nach dem Herauskommen einen Schritt zurück (Körper y), Wurzel bleibt
    # --- Sand: Wall um die Vorderbeine, Spritzer, Rieseln, Staub
    fpos = pos + dv * 0.5
    fz = gz(fpos.x, fpos.y)
    sand_ring("sring", (fpos.x, fpos.y, fz), tv + 0.08, r=0.48, yaw=yaw_h)
    sand_spray("ssp", (fpos.x, fpos.y, fz), dv, tv + 0.1, n=40, seed=1)
    sand_spray("ssp2", (fpos.x, fpos.y, fz), dv, tm + 0.25, n=16, seed=2, speed=(0.6, 1.6), up=(1.0, 2.2))
    sand_spray("ssp3", (fpos.x, fpos.y, fz), -dv, ts - 0.05, n=34, seed=3, speed=(0.8, 2.4), up=(1.6, 3.4))
    sand_drip("sdr", Hs, ("FL", "FR"), ts - 0.05, ts + 1.4, seed=4)
    for k_, t_ in enumerate((tv + 0.1, tm + 0.25, tm + 1.0)):
        smoke_dust(f"sink{k_}", (fpos.x, fpos.y, fz), cam, t_, dur=2.6, n=7, rise=0.6, alpha=0.75, spread=0.45, size=(1.5, 1.1), seed=k_)
    # --- ich: Sturz nach vorn links, liege, richte mich auf, schaue zum Pferd, dann dem Staub nach oben
    land = fall_off(rig, shake, tv, tuple(loc0), dv, side=-1, fwd=3.8, out=2.8, Hh=Hh, yaw0=yw0)
    # Staubsäule (v2-QA): schmal, steigt wie Rauch am Pferd hoch, Wind von links; Pferd bleibt im Bild
    dl = Vector((pos.x - land.x, pos.y - land.y, 0)).normalized()
    smoke_dust("smoke_g", (fpos.x, fpos.y, fz), cam, ts - 0.1, dur=2.4, n=6, rise=0.4, alpha=0.6, spread=0.5, size=(1.2, 0.8), seed=9)
    smoke_column("scol", (fpos.x, fpos.y, fz), cam, ts - 0.2, seed=11, wind=(dl.y * 0.45, -dl.x * 0.45))
    reins(Hh, Hs, off=[(tv + 0.1, None)])
    hd = (pos.x, pos.y, gz(pos.x, pos.y) + 0.8)
    up = (land.x, land.y, gz(land.x, land.y) + 0.95)
    pose(Hh, tv + 1.8, "push")
    pose(Hh, tv + 2.45, "hidden")
    ck(rig, [(tv + 2.55, up, look(up, hd)), (ts - 0.2, None, look(up, hd)),
             (ts + 0.6, None, look(up, (pos.x, pos.y, gz(pos.x, pos.y) + 1.5))),
             (D, None, look(up, (pos.x, pos.y, gz(pos.x, pos.y) + 2.6)))])
    Q.handheld(shake, 0, D, amp=0.4, hits=[(tv + 0.05, 0.6), (tv + 0.62, 1.4), (tm + 0.3, 0.25), (ts, 0.35)])
    Q.sc.frame_set(1)
    cfg["mist_amt"] = 0.2
    cfg["mblur"] = 0.5
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
        # v2: weich anhalten (Beine gerade statt im Trab erstarrt), wenden, zurück
        p1 = SPath([(x, y), (x, y + 60.0)])
        G1 = Gait(0.0, 4.0, t_stop=tn - 1.0, decel=1.0, stride=1.6, t_end=tn + 1.0)
        horse_go(Hh_, p1, G1, 0.0, tn + 0.6, trot=True, idle_seed=k)
        st_ = p1.at(G1.d(tn + 0.6))
        back = (st_.x + 1.0, st_.y - 20.0)
        p2 = SPath([(st_.x, st_.y - 3.0), (st_.x, st_.y), (st_.x + 1.8, st_.y + 1.6), (st_.x + 3.0, st_.y - 0.5), back])
        G2 = Gait(tn + 0.6 + 0.15 * k, 5.0, accel=0.8, stride=2.0, t_end=D + 1.0)
        horse_go(Hh_, p2, G2, tn + 0.6 + 1 / Q.FPS, D + 0.5, trot=True, idle_seed=k, d0=p2.c[min(range(len(p2.p)), key=lambda i: (p2.p[i] - Vector((st_.x, st_.y, 0))).length)])
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
    ride(Hs, rig, pth, 0.0, D + 0.5, speed=sp, stride=1.6, trot=True, pitch=-4.0, t_stop=tn_ - 0.4, decel=1.0)
    reins(Hh, Hs, off=[(tz - 0.4, tn + 1.0, "R")])
    Q.handheld(shake, 0, D + 0.5, amp=0.35)
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
if cfg.get("mblur") and os.environ.get("MBLUR", "1") == "1":   # v2: Bewegungsunschärfe beim schnellen Ritt (flüssiger)
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
