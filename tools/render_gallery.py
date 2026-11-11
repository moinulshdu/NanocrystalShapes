"""Regenerates the pictures used in README.md (docs/images/).

    python tools/render_gallery.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from nanoshapes import renderer as R  # noqa: E402

OUT = os.path.join(ROOT, "docs", "images")
SCALE = 2          # each tile is 2 x the 294 x 252 reference frame
LABEL_H = 44


def font(size):
    try:
        return ImageFont.load_default(size=size)       # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def sheet(cases, cols, path):
    W, H = R.REF_SIZE[0] * SCALE, R.REF_SIZE[1] * SCALE
    rows = (len(cases) + cols - 1) // cols
    out = Image.new("RGB", (W * cols, (H + LABEL_H) * rows), "white")
    d = ImageDraw.Draw(out)
    f = font(22)
    for i, (shape, params, label, opts) in enumerate(cases):
        s = R.Settings(shape=shape)
        s.azimuth, s.elevation = R.SHAPES[shape]["view"]
        for k, v in params.items():
            s.set_param(k, v)
        for k, v in opts.items():
            setattr(s, k, v)
        x, y = (i % cols) * W, (i // cols) * (H + LABEL_H)
        out.paste(R.render(s, (W, H), 3), (x, y + LABEL_H))
        tw = d.textlength(label, font=f)
        d.text((x + (W - tw) / 2, y + 12), label, fill=(40, 40, 40), font=f)
    out.save(path, optimize=True)
    print("wrote", os.path.relpath(path, ROOT))


def main():
    os.makedirs(OUT, exist_ok=True)
    sheet([(k, {}, v["label"], {}) for k, v in R.SHAPES.items()] + [("tetrahedron", {"t": 1 / 3},
           "Truncated tetrahedron", {})], 4, os.path.join(OUT, "shapes-gallery.png"))
    clean = {"show_arrows": False, "show_radii": False}
    sheet([
        ("cube", {"t": 0.293}, "Cube, t = 0.293", clean),
        ("cube", {"t": 0.5}, "Cube, t = 0.5", clean),
        ("octahedron", {"t": 1 / 3}, "Octahedron, t = 1/3", clean),
        ("icosahedron", {"t": 1 / 3}, "Icosahedron, t = 1/3", clean),
        ("decahedron", {"aspect": 1.2, "t": 0.1}, "Decahedron, L/W 1.2, t = 0.1", clean),
        ("bipyramid", {"aspect": 4.0, "t": 0.08}, "Bipyramid, L/W 4, t = 0.08", clean),
        ("triangular_plate", {"t": 1 / 3}, "Triangular plate, t = 1/3", clean),
        ("hexagonal_plate", {"t": 0.2}, "Hexagonal plate, t = 0.2", clean),
        ("rod", {"aspect": 5.0, "cap": 0.0}, "Rod 5:1, flat ends", clean),
        ("tube", {"aspect": 1.0, "wall": 0.85}, "Tube, thin wall", clean),
        ("tetrapod", {"aspect": 3.5, "cap": 0.4}, "Tetrapod, long arms", clean),
        ("bipyramid", {"sides": 6, "aspect": 2.5}, "6-sided bipyramid", clean),
    ], 4, os.path.join(OUT, "parameter-examples.png"))


if __name__ == "__main__":
    main()
