"""Builds nanoshapes/icon.png and icon.ico with the app's own renderer."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402
from nanoshapes import renderer as R  # noqa: E402

N = 1024
OUT = os.path.join(os.path.dirname(HERE), "nanoshapes")

# background tile: rounded square, vertical gradient
tile = Image.new("RGBA", (N, N), (0, 0, 0, 0))
grad = Image.new("RGB", (N, N))
gd = ImageDraw.Draw(grad)
top, bot = (24, 52, 110), (8, 20, 48)
for y in range(N):
    f = y / (N - 1)
    gd.line([(0, y), (N, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * f) for i in range(3)))
mask = Image.new("L", (N, N), 0)
ImageDraw.Draw(mask).rounded_rectangle([40, 40, N - 40, N - 40], radius=200, fill=255)
tile.paste(grad, (0, 0), mask)

# crystal: truncated octahedron
s = R.Settings(shape="octahedron")
s.set_param("t", 1 / 3)
s.azimuth, s.elevation = -150.0, 25.0
s.show_radii = s.show_arrows = s.show_corners = False
s.face_color = (40, 230, 255)
s.face_opacity = 0.55
s.edge_color = (235, 250, 255)
s.edge_width = 3.2
crystal = R.render_rgba(s, (1176, 1008), 3)
crystal = crystal.crop(crystal.getbbox())
k = 0.74 * N / max(crystal.size)
crystal = crystal.resize((int(crystal.width * k), int(crystal.height * k)), Image.LANCZOS)

# soft glow behind it
glow = Image.new("RGBA", (N, N), (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse([N * 0.2, N * 0.2, N * 0.8, N * 0.8], fill=(60, 200, 255, 90))
glow = glow.filter(ImageFilter.GaussianBlur(N * 0.08))
glow.putalpha(Image.composite(glow.getchannel("A"), Image.new("L", (N, N), 0), mask))
tile.alpha_composite(glow)
tile.alpha_composite(crystal, ((N - crystal.width) // 2, (N - crystal.height) // 2))

tile.resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "icon.png"))
tile.save(os.path.join(OUT, "icon.ico"), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("icon written")
