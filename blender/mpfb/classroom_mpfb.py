# Klassenzimmer aus blender/pov/classroom.py, aber mit echten MPFB-Menschen (Haut, Haare, Kleidung, Skelett, Mimik).
# Aufruf: blender -b --python classroom_mpfb.py -- <ausgabe_präfix> <prozent>
import bpy, sys, os, math, random

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOM = os.path.join(HERE, "..", "pov", "classroom.py")
g = {"__file__": ROOM, "__name__": "__room__"}
exec(compile(open(ROOM).read(), ROOM, "exec"), g)
T = g["T"]
sc = bpy.context.scene

# Klotz-Figuren entfernen (Schüler s*, Lehrerin)
def kill(o):
    for c in list(o.children):
        kill(c)
    bpy.data.objects.remove(o, do_unlink=True)

for o in [o for o in bpy.data.objects if o.type == "EMPTY" and o.parent is None and (o.name.startswith("s") and o.name[1:].isdigit() or o.name == "teacher")]:
    kill(o)

import people as P

random.seed(5)
CAST = [
    # x, y, Geschlecht, Haut, Haare, Kleidung, Nachbar?
    (2.27, -1.75, 1.0, "young_caucasian_male", "short02", ("male_casualsuit02", "shoes02"), True),
    (2.27, -0.35, 0.0, "young_caucasian_female", "ponytail01", ("female_casualsuit01", "shoes03"), False),
    (2.93, -0.35, 1.0, "young_african_male", "short04", ("male_casualsuit05", "shoes01"), False),
    (0.33, -1.75, 0.0, "young_asian_female", "bob02", ("female_sportsuit01", "shoes03"), False),
    (-0.33, -0.35, 1.0, "young_caucasian_male", "short03", ("male_casualsuit01", "shoes02"), False),
    (0.33, -0.35, 0.0, "young_african_female", "braid01", ("female_casualsuit02", "shoes03"), False),
    (2.27, 1.05, 1.0, "young_asian_male", "short01", ("male_casualsuit03", "shoes01"), False),
    (2.93, 1.05, 0.0, "young_caucasian_female", "long01", ("female_casualsuit01", "shoes03"), False),
]
people = []
for i, (x, y, gen, skin, hair, clothes, nb) in enumerate(CAST):
    p = P.make_person(f"st{i}", gender=gen, age=random.uniform(0.38, 0.45), muscle=random.uniform(0.4, 0.6), weight=random.uniform(0.4, 0.6),
                      skin=skin, hair=hair, clothes=clothes, eyebrows=random.choice(["eyebrow001", "eyebrow003", "eyebrow007"]))
    p["rig"].location = (x, y, -0.33)
    p["rig"].rotation_euler = (0, 0, math.pi)
    P.seated(p, 1)
    p["nb"] = nb
    people.append(p)

# Lehrerin an der Tafel (schaut zur Klasse = −y, Standard der MPFB-Figur)
teacher = P.make_person("teacher", gender=0.0, age=0.62, skin="middleage_caucasian_female", hair="bob01", clothes=("female_elegantsuit01", "shoes03"))
teacher["rig"].location = (1.2, 3.35, 0)
for s in ("L", "R"):
    P.rot(teacher, f"upperarm01.{s}", 1, y=(48 if s == "L" else -48))
    P.rot(teacher, f"lowerarm01.{s}", 1, x=15)

END = 5.6
F1 = T(END) + 2
for i, p in enumerate(people):
    P.idle(p, 1, F1, seed=i)
    P.set_face(p, 1, "neutral")
    d = random.uniform(0.0, 0.5)
    if p["nb"]:
        # Sitznachbar: dreht sich zu dir, Angst im Gesicht
        P.rot(p, "spine03", 1, x=6)
        P.rot(p, "spine03", T(2.3), x=6)
        P.rot(p, "spine03", T(2.9), x=4, y=-18)
        P.rot(p, "neck01", T(2.3))
        P.rot(p, "neck01", T(2.85), y=-28, x=-4)
        P.rot(p, "neck01", T(4.2), y=-28, x=-4)
        P.rot(p, "neck01", T(4.9), y=-12, x=2)
        P.set_face(p, T(2.35), "neutral")
        P.set_face(p, T(2.9), "fear", 1.0)
        P.set_face(p, T(4.0), "fear", 0.9)
        P.set_face(p, T(5.0), "fear", 0.75)
        P.blink(p, T(3.6))
    else:
        # schauen erschrocken zum Lautsprecher (rechts vorne)
        P.rot(p, "neck01", T(2.6 + d))
        P.rot(p, "neck01", T(3.2 + d), y=-35, x=-6)
        P.rot(p, "neck01", T(END), y=-38, x=-6)
        P.set_face(p, T(2.6 + d), "neutral")
        P.set_face(p, T(3.2 + d), "surprise", 0.9)
        P.set_face(p, T(4.6 + d), "fear", 0.8)
        P.blink(p, T(1.2 + d * 2))
        P.blink(p, T(4.2 + d))
P.idle(teacher, 1, F1, seed=42)
P.set_face(teacher, 1, "neutral")
P.rot(teacher, "neck01", T(2.6))
P.rot(teacher, "neck01", T(3.1), y=35)
P.set_face(teacher, T(2.6), "neutral")
P.set_face(teacher, T(3.2), "worried", 1.0)
P.blink(teacher, T(1.5))

sc.frame_end = T(END)
