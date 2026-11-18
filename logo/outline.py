#!/usr/bin/env python3
"""Arabisches Wort richtig verbunden (HarfBuzz) als Umriss-Kurven für Blender (Blender selbst kann Arabisch nicht verbinden).
  python3 logo/outline.py /home/user/fonts_ttf/Amiri-Bold-ar.ttf "قصة" logo/qissah_ar_outline.json
Ausgabe: Konturen als kubische Bézier-Segmente in Schrift-Einheiten (Überlappungen per skia-pathops vereinigt).
Benötigt: pip install fonttools brotli uharfbuzz skia-pathops (die Woff2-Schrift vorher nach TTF wandeln)."""
import json
import sys

import pathops
import uharfbuzz as hb
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

font_path, text, out = sys.argv[1], sys.argv[2], sys.argv[3]
blob = hb.Blob.from_file_path(font_path)
face = hb.Face(blob)
font = hb.Font(face)
buf = hb.Buffer()
buf.add_str(text)
buf.guess_segment_properties()
hb.shape(font, buf, {"liga": True, "kern": True})

tt = TTFont(font_path)
gs = tt.getGlyphSet()
order = tt.getGlyphOrder()
upm = tt["head"].unitsPerEm


class PathPen(BasePen):  # Glyphenumriss (verschoben) in einen pathops-Pfad schreiben
    def __init__(self, gs, path, dx, dy):
        super().__init__(gs)
        self.p, self.dx, self.dy = path, dx, dy

    def _t(self, pt):
        return (pt[0] + self.dx, pt[1] + self.dy)

    def _moveTo(self, pt):
        self.p.moveTo(*self._t(pt))

    def _lineTo(self, pt):
        self.p.lineTo(*self._t(pt))

    def _curveToOne(self, a, b, c):
        self.p.cubicTo(*self._t(a), *self._t(b), *self._t(c))

    def _qCurveToOne(self, a, b):
        self.p.quadTo(*self._t(a), *self._t(b))

    def _closePath(self):
        self.p.close()


path = pathops.Path()
x = 0
for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
    name = order[info.codepoint]
    gs[name].draw(PathPen(gs, path, x + pos.x_offset, pos.y_offset))
    x += pos.x_advance
path.simplify(fix_winding=True)  # Überlappungen vereinigen, Richtungen korrigieren

contours, cur, start = [], None, None
for verb, pts in path.segments:
    if verb == "moveTo":
        cur, start = {"start": list(pts[0]), "segs": []}, pts[0]
        contours.append(cur)
        last = pts[0]
    elif verb == "lineTo":
        a = pts[0]
        cur["segs"].append([[last[0] + (a[0] - last[0]) / 3, last[1] + (a[1] - last[1]) / 3],
                            [last[0] + 2 * (a[0] - last[0]) / 3, last[1] + 2 * (a[1] - last[1]) / 3], list(a)])
        last = a
    elif verb == "qCurveTo":  # mehrere Kontrollpunkte möglich (TrueType: Zwischenpunkte liegen mittig zwischen ihnen)
        offs, end = pts[:-1], pts[-1]
        for k, q in enumerate(offs):
            a = end if k == len(offs) - 1 else ((q[0] + offs[k + 1][0]) / 2, (q[1] + offs[k + 1][1]) / 2)
            cur["segs"].append([[last[0] + 2 / 3 * (q[0] - last[0]), last[1] + 2 / 3 * (q[1] - last[1])],
                                [a[0] + 2 / 3 * (q[0] - a[0]), a[1] + 2 / 3 * (q[1] - a[1])], list(a)])
            last = a
    elif verb == "curveTo":
        cur["segs"].append([list(pts[0]), list(pts[1]), list(pts[2])])
        last = pts[2]
    elif verb == "closePath":
        if cur["segs"] and (abs(last[0] - start[0]) > 1e-3 or abs(last[1] - start[1]) > 1e-3):
            a = start
            cur["segs"].append([[last[0] + (a[0] - last[0]) / 3, last[1] + (a[1] - last[1]) / 3],
                                [last[0] + 2 * (a[0] - last[0]) / 3, last[1] + 2 * (a[1] - last[1]) / 3], list(a)])
xs = [p[0] for c in contours for s in c["segs"] for p in s]
ys = [p[1] for c in contours for s in c["segs"] for p in s]
json.dump({"upm": upm, "bbox": [min(xs), min(ys), max(xs), max(ys)], "contours": contours}, open(out, "w"))
print(f"✓ {len(contours)} Konturen, Breite {max(xs) - min(xs):.0f} / {upm} Einheiten -> {out}")
