# Kollisions-Prüfung für das Flug-Video (Nutzer: „keine Köpfe, Hände, Körper durch Sitze, Bildschirme, Wände“).
# Aufruf (nach dem Szenenaufbau von flug.py, ohne Verschmelzen):
#   JOIN=0 DBGPY=blender/qissa/flug_check.py blender -b --factory-startup --python blender/qissa/flug.py -- <einstellung> /tmp/x 50 2
# Prüft je CHECK_STEP Bilder (Standard 6), ob Punkte von Kopf/Armen/Händen/Körper der Menschen IN Sitzen, Bildschirmen,
# Wänden, Service-Leisten, Gepäckfächern oder der Decke stecken (Tiefe > CHECK_TOL, Standard 1 cm).
import bpy, os, collections
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree

STEP = int(os.environ.get("CHECK_STEP", "6"))
TOL = float(os.environ.get("CHECK_TOL", "0.01"))
sc = bpy.context.scene

STATIC_PREFIX = ("seat", "ife", "wall", "psu", "binbody", "bindoor", "ceil", "bulk", "floor")
PERSON_PREFIX = ("pax", "nb_", "stw_", "pov_", "st")


def part_kind(n):
    n = n.lower()
    if "khimar" in n:
        return "Tuch"
    if any(k in n for k in ("skull", "hair", "_cap", "visor", "nose", "chin", "ear", "eye", "brow", "lip", "mouth", "lid", "iris", "scarf")):
        return "Kopf"
    if any(k in n for k in ("palm", "thumb", "pov_f", "pov_ft", "pov_th", "pov_wr")):
        return "Hand"
    if any(k in n for k in ("_fa.", "_elm.", "_ua.", "_shm.")):
        return "Arm"
    if any(k in n for k in ("torso", "lap", "knee", "neckm")):
        return "Körper"
    return None


def owner(n):
    for p in ("pov",):
        if n.startswith(p):
            return "ich"
    return n.split("_")[0]


def static_tree():
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys, pobj = [], [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith(STATIC_PREFIX) or o.hide_render:
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = o.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in me.vertices]
        for p in me.polygons:
            polys.append([base + i for i in p.vertices])
            pobj.append(o.name)
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys), pobj


def own_seat(person):   # pax0D -> seat0D
    if person == "nb":
        return "seat0C"
    if person == "ich":
        return "seat0A"
    return "seat" + person[3:] if person.startswith("pax") else None


VIEW_ONLY = os.environ.get("CHECK_ALL", "0") != "1"   # nur Punkte zählen, die die Kamera in dem Bild sieht


hits = collections.defaultdict(lambda: [0, 0.0, None, None])   # (person, kind, obj) -> [frames, max depth, first frame, worst frame]
parts = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(PERSON_PREFIX) and part_kind(o.name)]
print("CHECK Teile:", len(parts))
t0 = None
for f in range(sc.frame_start, sc.frame_end + 1, STEP):
    sc.frame_set(f)
    tree, pobj = static_tree()   # Gepäckfach-Klappen bewegen sich -> je Bild neu
    dg = bpy.context.evaluated_depsgraph_get()
    cam = sc.camera
    seen = set()
    for o in parts:
        if o.hide_render or not o.visible_get():
            continue
        ev = o.evaluated_get(dg)
        mw = o.matrix_world
        me = ev.data
        kind = part_kind(o.name)
        who = owner(o.name)
        nv = len(me.vertices)
        step = max(1, nv // 60)
        for i in range(0, nv, step):
            p = mw @ me.vertices[i].co
            if VIEW_ONLY:
                cv = world_to_camera_view(sc, cam, p)
                if not (0.0 <= cv.x <= 1.0 and 0.0 <= cv.y <= 1.0 and cv.z > 0.0):
                    continue
            loc, nrm, idx, dist = tree.find_nearest(p, 0.3)
            if loc is None:
                continue
            depth = -(p - loc).dot(nrm)
            if depth <= TOL:
                continue
            ob = pobj[idx]
            if kind in ("Körper", "Tuch") and ob == own_seat(who):
                continue   # sitzen = Rücken/Gesäß/Kopftuch am eigenen Sitz ist normal
            key = (who, kind, ob)
            h = hits[key]
            if (key, f) not in seen:
                seen.add((key, f))
                h[0] += 1
                if h[2] is None:
                    h[2] = f
            if depth > h[1]:
                h[1] = depth
                h[3] = f
fps = sc.render.fps
print("CHECK Ergebnis (Person, Teil, Objekt: Bilder, max. Tiefe, erstes/schlimmstes Bild):")
for (who, kind, ob), (n, dmax, f1, fw) in sorted(hits.items(), key=lambda x: -x[1][1]):
    print(f"CHECK {who:8s} {kind:6s} in {ob:14s} {n:3d}× bis {dmax * 100:4.1f} cm  ab Bild {f1} (t={(f1 - 1) / fps:.2f}s), schlimmst {fw}")
print("CHECK Summe:", len(hits), "Treffer-Gruppen")
