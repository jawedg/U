# Besetzung im Ink-Pop-Stil (gemeinsam für alle Szenen).
import figure as F

CAST = {
    "sota": dict(skin=(0.88, 0.66, 0.48), hair=(0.07, 0.07, 0.09), jacket=(0.13, 0.17, 0.31), pants=(0.3, 0.32, 0.38), hair_style="block"),
    "me": dict(skin=(0.93, 0.74, 0.58), hair=(0.1, 0.08, 0.07), jacket=(0.14, 0.18, 0.3), pants=(0.3, 0.32, 0.38), hair_style="short"),
    "yui": dict(skin=(0.95, 0.78, 0.64), hair=(0.12, 0.08, 0.07), jacket=(0.15, 0.19, 0.33), pants=(0.2, 0.22, 0.32), hair_style="long",
                lower="skirt", socks=(0.12, 0.13, 0.2), height=1.6, build=0.9, iris=(0.3, 0.18, 0.1), zipper=False),
    "oma": dict(skin=(0.9, 0.72, 0.58), hair=(0.82, 0.82, 0.84), jacket=(0.52, 0.36, 0.48), pants=(0.32, 0.28, 0.3), hair_style="bun",
                height=1.5, build=1.05, glasses=True, iris=(0.25, 0.18, 0.12), zipper=False, shoes=(0.4, 0.3, 0.25)),
    "tanaka": dict(skin=(0.84, 0.62, 0.45), hair=(0.12, 0.12, 0.13), jacket=(0.32, 0.4, 0.3), pants=(0.25, 0.25, 0.27), hair_style="short",
                   height=1.68, build=1.22, iris=(0.25, 0.15, 0.08), shoes=(0.2, 0.2, 0.2)),
    "fahrer": dict(skin=(0.85, 0.64, 0.48), hair=(0.15, 0.15, 0.16), jacket=(0.2, 0.26, 0.42), pants=(0.2, 0.24, 0.38), hair_style="cap",
                   height=1.7, build=1.08, cap=(0.2, 0.26, 0.42), shoes=(0.15, 0.15, 0.15)),
}


def make(name, **over):
    kw = dict(CAST[name])
    kw.update(over)
    return F.make_figure(name, **kw)
