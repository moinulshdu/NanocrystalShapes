"""
Renderer for nanocrystal shapes.

Pure Python + Pillow. Orthographic camera, translucent faces, thin edges and
lit tubes/arrows, painter's algorithm with supersampling for anti-aliasing.
Translucent surfaces are composited as whole layers, so curved meshes show no
seams.

The tetrahedron's default settings reproduce the original reference picture
(294 x 252 px frame).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict

from PIL import Image, ImageDraw

from . import geometry as G
from .geometry import add, sub, mul, dot, cross, norm, lerp

# --------------------------------------------------------------------------
# shapes and their parameters
# --------------------------------------------------------------------------

# key: (label, low, high, step, display format)
PARAM_SPECS = {
    "t": ("Truncation t", 0.0, 0.49, 0.005, "{:.3f}"),
    "aspect": ("Aspect ratio", 0.05, 10.0, 0.01, "{:.2f}"),
    "wall": ("Inner / outer diameter", 0.10, 0.95, 0.01, "{:.2f}"),
    "sides": ("Number of sides", 3, 8, 1, "{:.0f}"),
    "cap": ("End rounding", 0.0, 1.0, 0.01, "{:.2f}"),
}

# Each shape: label, builder, default parameters, optional label/range
# overrides, default view (azimuth, elevation), and whether it has twin planes.
SHAPES = {
    "tetrahedron": dict(label="Tetrahedron", build=G.tetra_shape, params={"t": 0.20},
                        view=(-136.145, 9.846)),
    "cube": dict(label="Cube", build=G.cube_shape, params={"t": 0.0}, view=(-124.0, 24.0),
                 ranges={"t": (0.0, 0.5)}),
    "octahedron": dict(label="Octahedron", build=G.octa_shape, params={"t": 0.20}, view=(-150.0, 25.0)),
    "cuboctahedron": dict(label="Cuboctahedron", build=G.cubocta_shape, params={"t": 0.0},
                          view=(-122.0, 20.0)),
    "icosahedron": dict(label="Icosahedron", build=G.icosa_shape, params={"t": 0.0},
                        view=(-118.0, 14.0)),
    "decahedron": dict(label="Decahedron", build=G.decahedron_shape,
                       params={"aspect": round(G.DECA_IDEAL_ASPECT, 3), "t": 0.0},
                       view=(-95.0, 25.0), labels={"aspect": "Length / width"},
                       ranges={"aspect": (0.3, 4.0)}, twins=True),
    "bipyramid": dict(label="Bipyramid", build=G.bipyramid_shape,
                      params={"sides": 5, "aspect": 2.5, "t": 0.0}, view=(-68.0, 18.0),
                      labels={"aspect": "Length / width"}, ranges={"aspect": (0.5, 8.0)}, twins=True),
    "triangular_plate": dict(label="Triangular plate", build=G.plate_shape(3, 1.0),
                             params={"aspect": 0.12, "t": 0.0}, view=(-100.0, 34.0),
                             labels={"aspect": "Thickness / edge", "t": "Corner truncation t"},
                             ranges={"aspect": (0.02, 1.0), "t": (0.0, 0.5)}),
    "hexagonal_plate": dict(label="Hexagonal plate", build=G.plate_shape(6, 1.0),
                            params={"aspect": 0.25, "t": 0.0}, view=(-100.0, 34.0),
                            labels={"aspect": "Thickness / edge", "t": "Corner truncation t"},
                            ranges={"aspect": (0.02, 2.0), "t": (0.0, 0.5)}),
    "sphere": dict(label="Sphere", build=G.sphere_shape, params={}, view=(-136.145, 9.846)),
    "rod": dict(label="Rod", build=G.rod_shape, params={"aspect": 3.0, "cap": 1.0}, view=(-62.0, 20.0),
                labels={"aspect": "Length / diameter"}, ranges={"aspect": (1.0, 10.0)}),
    "tube": dict(label="Tube", build=G.tube_shape, params={"aspect": 3.0, "wall": 0.6}, view=(-62.0, 22.0),
                 labels={"aspect": "Length / diameter"}, ranges={"aspect": (0.2, 10.0)}),
    "tetrapod": dict(label="Tetrapod", build=G.tetrapod_shape, params={"aspect": 2.0, "cap": 1.0},
                     view=(-136.145, 14.0), labels={"aspect": "Arm length / diameter"},
                     ranges={"aspect": (0.6, 6.0)}),
}


def param_spec(shape, key):
    lab, lo, hi, step, fmt = PARAM_SPECS[key]
    sp = SHAPES[shape]
    lab = sp.get("labels", {}).get(key, lab)
    lo, hi = sp.get("ranges", {}).get(key, (lo, hi))
    return lab, lo, hi, step, fmt


def has_twins(shape, params):
    if not SHAPES[shape].get("twins"):
        return False
    if shape == "bipyramid":
        return int(round(params.get("sides", 5))) == 5
    return True


# --------------------------------------------------------------------------
# settings
# --------------------------------------------------------------------------

REF_SIZE = (294, 252)          # size of the reference picture in pixels
REF_SCALE = 227.8              # pixels per unit edge length in the reference
REF_CENTER = (107.675, 151.35)  # where the centroid lands in the reference


@dataclass
class Settings:
    shape: str = "tetrahedron"
    params: dict = field(default_factory=dict)   # shape -> {parameter: value}
    azimuth: float = -136.145       # degrees
    elevation: float = 9.846        # degrees
    zoom: float = 1.0
    face_color: tuple = (0, 255, 255)
    face_opacity: float = 0.383
    back_face_shade: float = 1.0
    edge_color: tuple = (0, 0, 255)
    corner_color: tuple = (0, 0, 0)
    radius_color: tuple = (255, 0, 0)
    arrow_color: tuple = (255, 128, 0)
    twin_color: tuple = (230, 0, 230)
    twin_opacity: float = 0.32
    edge_width: float = 2.2                # px in the 294-px reference frame
    corner_width: float = 2.2
    radius_tube: float = 0.0115            # world units
    arrow_tube: float = 0.0235
    arrow_head_len: float = 0.12
    arrow_head_radius: float = 0.036
    arrow_tip_gap: float = 0.03
    radius_scale: float = 1.0              # thickness multiplier for radii / axes
    arrow_scale: float = 1.0               # thickness multiplier for edge arrows
    show_faces: bool = True
    show_edges: bool = True
    show_corners: bool = True
    show_radii: bool = True
    show_arrows: bool = True
    show_back_arrow: bool = True           # arrows lying behind the faces
    show_twins: bool = True
    lighting: bool = True
    background: tuple = (255, 255, 255)

    # -- per-shape parameters
    def shape_params(self, shape=None):
        shape = shape or self.shape
        p = dict(SHAPES[shape]["params"])
        p.update({k: v for k, v in self.params.get(shape, {}).items() if k in p})
        return p

    def set_param(self, key, value, shape=None):
        shape = shape or self.shape
        self.params.setdefault(shape, {})[key] = value

    def to_dict(self):
        d = asdict(self)
        for k, v in d.items():
            if isinstance(v, tuple):
                d[k] = list(v)
        return d

    @classmethod
    def from_dict(cls, d):
        s = cls()
        for k, v in (d or {}).items():
            if not hasattr(s, k):
                continue
            cur = getattr(s, k)
            try:
                if k == "shape":
                    if v not in SHAPES:
                        continue
                elif k == "params":
                    v = {sh: {pk: float(pv) for pk, pv in dict(vals).items()}
                         for sh, vals in dict(v).items() if sh in SHAPES}
                elif isinstance(cur, tuple):
                    v = tuple(int(x) for x in v)
                elif isinstance(cur, bool):
                    v = bool(v)
                elif isinstance(cur, float):
                    v = float(v)
            except (TypeError, ValueError):
                continue
            setattr(s, k, v)
        return s


# --------------------------------------------------------------------------
# lighting (view space: x right, y up, z towards the viewer)
# --------------------------------------------------------------------------

AMBIENT = (0.4, 0.2, 0.2)
LIGHTS = [((0.0, 0.18, 0.5), norm((1.5, -0.5, 2.0))),
          ((0.18, 0.5, 0.18), norm((1.5, 1.5, 3.0))),
          ((0.5, 0.18, 0.0), norm((-0.5, 1.5, 2.0))),
          ((0.0, 0.18, 0.5), norm((-0.5, -0.5, 2.0)))]

# Lights for the translucent faces, fitted to the reference picture's face colours.
FACE_AMBIENT = (0.281, 0.281, 0.228)
FACE_WEIGHTS = [(0.447, 0.447, 0.708), (0.317, 0.317, 0.099),
                (0.272, 0.272, 0.161), (-0.380, -0.380, -0.172)]


def shade_face(base, n_view, enabled=True):
    if not enabled:
        return tuple(int(c) for c in base)
    k = list(FACE_AMBIENT)
    for (_, d), w in zip(LIGHTS, FACE_WEIGHTS):
        s = dot(n_view, d)
        if s > 0:
            for i in range(3):
                k[i] += w[i] * s
    return tuple(max(0, min(255, int(round(base[i] * k[i])))) for i in range(3))


def shade(base, n_view, enabled=True):
    if not enabled:
        return tuple(int(c) for c in base)
    k = list(AMBIENT)
    for col, d in LIGHTS:
        s = dot(n_view, d)
        if s > 0:
            k[0] += col[0] * s
            k[1] += col[1] * s
            k[2] += col[2] * s
    return tuple(max(0, min(255, int(round(base[i] * k[i])))) for i in range(3))


# --------------------------------------------------------------------------
# camera
# --------------------------------------------------------------------------


class Camera:
    def __init__(self, az_deg, el_deg, scale, offset):
        az, el = math.radians(az_deg), math.radians(el_deg)
        self.cam = (math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))
        self.fwd = mul(self.cam, -1.0)
        r = cross(self.fwd, (0.0, 0.0, 1.0))
        if dot(r, r) < 1e-12:
            r = (-math.sin(az), math.cos(az), 0.0)
        self.right = norm(r)
        self.up = cross(self.right, self.fwd)
        self.scale = scale
        self.ox, self.oy = offset

    def project(self, p):
        return (self.ox + self.scale * dot(p, self.right),
                self.oy - self.scale * dot(p, self.up))

    def depth(self, p):
        return dot(p, self.fwd)

    def to_view(self, n):
        return (dot(n, self.right), dot(n, self.up), dot(n, self.cam))


# --------------------------------------------------------------------------
# shape cache and classification
# --------------------------------------------------------------------------

BACK, MIDDLE, FRONT, MISS = 0, 1, 2, 3
_CACHE = {}


def _key(s):
    return (s.shape, tuple(sorted((k, round(float(v), 6)) for k, v in s.shape_params().items())))


def get_shape(s):
    k = _key(s)
    sh = _CACHE.get(k)
    if sh is None:
        sh = SHAPES[s.shape]["build"](s.shape_params())
        if len(_CACHE) > 40:
            _CACHE.clear()
        _CACHE[k] = sh
    return sh


def classify(planes, p, fwd, eps=0.012, miss=FRONT):
    """Where point p lies along the view ray relative to a convex body.
    `miss` is returned when the ray does not meet the body at all."""
    lo, hi = -1e9, 1e9
    for n, c in planes:
        nd = dot(n, fwd)
        npv = dot(n, p) - c
        if abs(nd) < 1e-12:
            if npv > 0:
                return miss
            continue
        lam = -npv / nd
        if nd > 0:
            hi = min(hi, lam)
        else:
            lo = max(lo, lam)
    if lo > hi:
        return miss
    if 0.0 <= lo + eps:
        return FRONT
    if 0.0 > hi + eps:
        return BACK
    return MIDDLE


# --------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------


@dataclass
class Prim:
    depth: float
    prio: int
    pts: list
    color: tuple
    alpha: float = 1.0
    kind: str = "poly"      # poly | line
    width: float = 1.0      # px (reference frame)


@dataclass
class Layer:
    """Facets drawn opaque into one layer, then composited with `alpha`."""
    depth: float
    prims: list
    alpha: float
    prio: int = 0


def tube_prims(cls, cam, p0, p1, radius, color, segs=14, sides=28, prio=3, head=None, lighting=True):
    """Lit cylinder from p0 to p1 (optionally ending in a cone `head`=(len, r))."""
    out = []
    axis = sub(p1, p0)
    L = math.sqrt(dot(axis, axis))
    if L < 1e-9:
        return out
    d = mul(axis, 1.0 / L)
    tmp = (0.0, 0.0, 1.0) if abs(d[2]) < 0.9 else (1.0, 0.0, 0.0)
    u = norm(cross(d, tmp))
    v = cross(d, u)
    shaft_end = L
    if head:
        hl, hr = head
        hl = min(hl, L * 0.8)
        shaft_end = L - hl
    ring = [(math.cos(2 * math.pi * k / sides), math.sin(2 * math.pi * k / sides)) for k in range(sides)]

    def circ(center, r, k):
        c, s_ = ring[k % sides]
        return add(center, add(mul(u, r * c), mul(v, r * s_)))

    fwd = cam.fwd
    for sgi in range(segs):
        a = shaft_end * sgi / segs
        b = shaft_end * (sgi + 1) / segs
        ca, cb = add(p0, mul(d, a)), add(p0, mul(d, b))
        mid = add(p0, mul(d, (a + b) / 2))
        for k in range(sides):
            ang = 2 * math.pi * (k + 0.5) / sides
            n = add(mul(u, math.cos(ang)), mul(v, math.sin(ang)))
            if dot(n, fwd) >= 0.02:
                continue
            pts = [circ(ca, radius, k), circ(ca, radius, k + 1), circ(cb, radius, k + 1), circ(cb, radius, k)]
            col = shade(color, cam.to_view(n), lighting)
            surf = add(mid, mul(n, radius))
            out.append((cls(surf, 0.003), Prim(cam.depth(surf), prio, pts, col)))
    if head:
        hl, hr = head
        hl = min(hl, L * 0.8)
        base_c = add(p0, mul(d, L - hl))
        tip = p1
        cat = cls(lerp(base_c, tip, 0.4), 0.012)
        slope = hr / hl
        for k in range(sides):
            ang = 2 * math.pi * (k + 0.5) / sides
            radial = add(mul(u, math.cos(ang)), mul(v, math.sin(ang)))
            n = norm(add(radial, mul(d, slope)))
            if dot(n, fwd) >= 0.0:
                continue
            pts = [circ(base_c, hr, k), circ(base_c, hr, k + 1), tip]
            col = shade(color, cam.to_view(n), lighting)
            surf = add(lerp(base_c, tip, 0.33), mul(radial, hr * 0.67))
            out.append((cls(surf, 0.003), Prim(cam.depth(surf), prio + 1, pts, col)))
        nb = mul(d, -1.0)
        if dot(nb, fwd) < 0:
            pts = [circ(base_c, hr, k) for k in range(sides)]
            col = shade(color, cam.to_view(nb), lighting)
            out.append((cat, Prim(cam.depth(base_c), prio + 1, pts, col)))
    return out


def sphere_prims(cls, cam, c, r, color, prio=3, nlat=10, nlon=20, lighting=True):
    out = []
    for i in range(nlat):
        th0 = math.pi * i / nlat - math.pi / 2
        th1 = math.pi * (i + 1) / nlat - math.pi / 2
        for j in range(nlon):
            ph0 = 2 * math.pi * j / nlon
            ph1 = 2 * math.pi * (j + 1) / nlon

            def P(th, ph):
                return (math.cos(th) * math.cos(ph), math.cos(th) * math.sin(ph), math.sin(th))
            nm = norm(P((th0 + th1) / 2, (ph0 + ph1) / 2))
            if dot(nm, cam.fwd) >= 0.02:
                continue
            pts = [add(c, mul(P(th0, ph0), r)), add(c, mul(P(th0, ph1), r)),
                   add(c, mul(P(th1, ph1), r)), add(c, mul(P(th1, ph0), r))]
            col = shade(color, cam.to_view(nm), lighting)
            surf = add(c, mul(nm, r))
            out.append((cls(surf, 0.003), Prim(cam.depth(surf), prio, pts, col)))
    return out


def line_prims(cls, cam, p0, p1, color, width, prio=1, segs=10, bias=0.0):
    out = []
    for k in range(segs):
        a = lerp(p0, p1, k / segs)
        b = lerp(p0, p1, (k + 1) / segs)
        m = lerp(a, b, 0.5)
        out.append((cls(m, 0.012), Prim(cam.depth(m) + bias, prio, [a, b], color, 1.0, "line", width)))
    return out


def contour_segments(sh, fwd):
    """Smooth outline of curved surfaces: where the interpolated vertex
    normal turns from facing the viewer to facing away."""
    segs = []
    for srf in sh.surfaces:
        if srf.kind != "smooth":
            continue
        for f in srf.facets:
            g = [dot(n, fwd) for n in f.vn]
            if (g[0] > 0) == (g[1] > 0) == (g[2] > 0):
                continue
            pts = []
            for i in range(3):
                j = (i + 1) % 3
                if (g[i] > 0) != (g[j] > 0):
                    s = g[i] / (g[i] - g[j])
                    pts.append(lerp(f.pts[i], f.pts[j], s))
            if len(pts) == 2:
                segs.append((pts[0], pts[1]))
    return segs


# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------


def _bbox(cam, V):
    xs, ys = [], []
    for p in V:
        x, y = cam.project(p)
        xs.append(x)
        ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


_FIT = {}


def shape_fit(s, sh):
    """(relative scale, target bbox centre in reference px). The tetrahedron
    gives the reference; other shapes are scaled, at their default view, to
    fill the same box."""
    k = _key(s)
    if k not in _FIT:
        tv = SHAPES["tetrahedron"]["view"]
        cam = Camera(tv[0], tv[1], 1.0, (0.0, 0.0))
        tx0, ty0, tx1, ty1 = _bbox(cam, G.tetra_vertices())
        tcen = (REF_CENTER[0] + REF_SCALE * (tx0 + tx1) / 2, REF_CENTER[1] + REF_SCALE * (ty0 + ty1) / 2)
        if s.shape == "tetrahedron":
            rel = 1.0
        else:
            view = SHAPES[s.shape]["view"]
            cam = Camera(view[0], view[1], 1.0, (0.0, 0.0))
            x0, y0, x1, y1 = _bbox(cam, sh.fit_points)
            rel = min((tx1 - tx0) / max(x1 - x0, 1e-9), (ty1 - ty0) / max(y1 - y0, 1e-9))
        # arrows start at the corner furthest left in the default view
        start = None
        if sh.is_polyhedron:
            view = SHAPES[s.shape]["view"]
            cam = Camera(view[0], view[1], 1.0, (0.0, 0.0))
            start = min(range(len(sh.V)), key=lambda i: (round(cam.project(sh.V[i])[0], 6), -cam.depth(sh.V[i])))
        if len(_FIT) > 80:
            _FIT.clear()
        _FIT[k] = (rel, tcen, start)
    return _FIT[k]


def _layout(s, sh, size):
    W, H = size
    k = min(W / REF_SIZE[0], H / REF_SIZE[1])
    rel, tcen, _ = shape_fit(s, sh)
    scale = REF_SCALE * rel * k * s.zoom
    cam = Camera(s.azimuth, s.elevation, 1.0, (0.0, 0.0))
    x0, y0, x1, y1 = _bbox(cam, sh.fit_points)
    bc = ((x0 + x1) / 2, (y0 + y1) / 2)
    fx = (W - REF_SIZE[0] * k) / 2
    fy = (H - REF_SIZE[1] * k) / 2
    return scale, (fx + tcen[0] * k - scale * bc[0], fy + tcen[1] * k - scale * bc[1])


# --------------------------------------------------------------------------
# scene -> ordered draw list
# --------------------------------------------------------------------------


def build_draw_list(s: Settings, cam: Camera, sh=None):
    sh = sh or get_shape(s)
    params = s.shape_params()
    rel, _, start = shape_fit(s, sh)
    g = 1.0 / rel                     # keep tubes the same thickness on screen
    fwd = cam.fwd
    center = (0.0, 0.0, 0.0)

    if sh.convex:
        planes = sh.class_planes

        def cls(p, eps=0.012):
            return classify(planes, p, fwd, eps)
    else:
        def cls(p, eps=0.012):
            return None

    items = []    # (category, Prim)
    ga = g * s.arrow_scale
    lb = 1.5 * s.arrow_tube * ga if (s.show_arrows and sh.is_polyhedron) else 0.0

    if s.show_edges:
        for p, q in sh.poly_edges:
            items += line_prims(cls, cam, p, q, s.edge_color, s.edge_width, prio=1, bias=lb)
        for p, q in sh.rims:
            items += line_prims(cls, cam, p, q, s.edge_color, s.edge_width, prio=1, segs=1)
        for p, q in contour_segments(sh, fwd):
            m = lerp(p, q, 0.5)
            cat = FRONT if sh.convex else None
            items.append((cat, Prim(cam.depth(m), 1, [p, q], s.edge_color, 1.0, "line", s.edge_width)))
    if s.show_corners and sh.corner_lines:
        for p, q in sh.corner_lines:
            items += line_prims(cls, cam, p, q, s.corner_color, s.corner_width, prio=0, segs=3, bias=lb)
    if s.show_radii:
        for vtx in sh.radius_points:
            items += tube_prims(cls, cam, center, vtx, s.radius_tube * g * s.radius_scale, s.radius_color,
                                segs=12, sides=16, prio=2, lighting=s.lighting)
    if s.show_arrows and sh.is_polyhedron and start is not None:
        head = (s.arrow_head_len * g * (0.5 + 0.5 * s.arrow_scale), s.arrow_head_radius * ga)
        V = sh.V
        Lv = V[start]
        for j in sh.adj[start]:
            tgt = V[j]
            if not s.show_back_arrow and classify(sh.class_planes, lerp(Lv, tgt, 0.5), fwd) != FRONT:
                continue
            dv = norm(sub(tgt, Lv))
            tgt = sub(tgt, mul(dv, s.arrow_tip_gap * g))
            items += tube_prims(cls, cam, Lv, tgt, s.arrow_tube * ga, s.arrow_color, head=head,
                                prio=3, lighting=s.lighting)
        items += sphere_prims(cls, cam, Lv, s.arrow_tube * ga * 1.02, s.arrow_color, lighting=s.lighting)
    if s.show_twins and sh.twin_polys and has_twins(s.shape, params):
        for poly in sh.twin_polys:
            col = tuple(s.twin_color)     # flat colour: twin planes are seen edge-on a lot
            items.append((MIDDLE, Prim(cam.depth(G.centroid(poly)), 1, poly, col, s.twin_opacity)))

    # faces, grouped into layers
    groups = {}
    if s.show_faces:
        for f in sh.facets:
            away = dot(f.n, fwd) > 0
            nv = cam.to_view(f.n)
            if nv[2] < 0:
                nv = mul(nv, -1)
            col = shade_face(s.face_color, nv, s.lighting)
            if away and s.back_face_shade != 1.0:
                col = tuple(max(0, min(255, int(round(c * s.back_face_shade)))) for c in col)
            gk = (0 if sh.convex else f.surf, away)
            groups.setdefault(gk, []).append(Prim(cam.depth(f.c), 0, f.pts, col))

    def srt(lst):
        return sorted(lst, key=lambda p: (-p.depth, p.prio))

    def layer(prims):
        prims = srt(prims)
        dep = sum(p.depth for p in prims) / len(prims)
        return Layer(dep, prims, s.face_opacity)

    if sh.convex:
        ordered = srt([p for c, p in items if c == BACK])
        if (0, True) in groups:
            ordered.append(layer(groups[(0, True)]))
        ordered += srt([p for c, p in items if c == MIDDLE])
        if (0, False) in groups:
            ordered.append(layer(groups[(0, False)]))
        ordered += srt([p for c, p in items if c == FRONT])
        return ordered
    # non-convex shapes (tube, tetrapod): layers are sorted far to near; every
    # line or tube piece goes right after the last layer that lies behind it.
    # Whether a surface lies in front of or behind a point is decided against
    # that surface's own convex hull.
    keys = sorted(groups, key=lambda k: -sum(p.depth for p in groups[k]) / len(groups[k]))
    layers = [layer(groups[k]) for k in keys]
    slots = [[] for _ in range(len(layers) + 1)]
    for _, pr in items:
        m = lerp(pr.pts[0], pr.pts[-1], 0.5) if pr.kind == "line" else G.centroid(pr.pts)
        behind = {}     # layer -> True (behind the point) / False (in front)
        for si, srf in enumerate(sh.surfaces):
            c = classify(srf.hull, m, fwd, 0.006, miss=MISS)
            if c == MISS:
                continue
            if c == FRONT:
                behind[(si, True)] = behind[(si, False)] = True
            elif c == BACK:
                behind[(si, True)] = behind[(si, False)] = False
            elif srf.kind == "flat":
                behind[(si, True)] = behind[(si, False)] = True
            else:
                behind[(si, True)] = not srf.inward      # facets facing away
                behind[(si, False)] = srf.inward
        lo_pos, hi_pos = 0, len(keys)
        for i, k in enumerate(keys):
            b = behind.get(k)
            if b is True:
                lo_pos = i + 1
            elif b is False and hi_pos == len(keys):
                hi_pos = i
        slots[min(lo_pos, hi_pos)].append(pr)
    ordered = srt(slots[0])
    for i, lay in enumerate(layers):
        ordered.append(lay)
        ordered += srt(slots[i + 1])
    return ordered


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------


def _draw_layer(img, cam, lay):
    polys = [[cam.project(q) for q in pr.pts] for pr in lay.prims]
    xs = [x for poly in polys for x, _ in poly]
    ys = [y for poly in polys for _, y in poly]
    W, H = img.size
    x0, y0 = max(0, int(min(xs)) - 2), max(0, int(min(ys)) - 2)
    x1, y1 = min(W, int(max(xs)) + 3), min(H, int(max(ys)) + 3)
    if x1 <= x0 or y1 <= y0:
        return
    col = Image.new("RGB", (x1 - x0, y1 - y0))
    mask = Image.new("L", (x1 - x0, y1 - y0), 0)
    dc, dm = ImageDraw.Draw(col), ImageDraw.Draw(mask)
    a = int(round(255 * lay.alpha))
    for poly, pr in zip(polys, lay.prims):
        sh_ = [(x - x0, y - y0) for x, y in poly]
        dc.polygon(sh_, fill=pr.color)
        dm.polygon(sh_, fill=a)
    img.paste(col, (x0, y0), mask)


def checkerboard(size, cell=10, c1=(255, 255, 255), c2=(214, 214, 214)):
    """Grey/white checkerboard, the usual sign of a transparent background."""
    W, H = size
    img = Image.new("RGB", (W, H), c1)
    d = ImageDraw.Draw(img)
    for y in range(0, H, cell):
        for x in range((y // cell) % 2 * cell, W, 2 * cell):
            d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=c2)
    return img


def render(s: Settings, size=REF_SIZE, supersample=4, background=None, checker=False):
    """Render to an RGB image of `size` on the given background colour, or on a
    checkerboard (preview of a transparent background)."""
    W, H = size
    ss = max(1, int(supersample))
    bg = tuple(background if background is not None else s.background)
    sh = get_shape(s)
    scale, off = _layout(s, sh, (W * ss, H * ss))
    cam = Camera(s.azimuth, s.elevation, scale, off)
    if checker:
        img = checkerboard((W * ss, H * ss), 10 * ss)
    else:
        img = Image.new("RGB", (W * ss, H * ss), bg)
    dr = ImageDraw.Draw(img, "RGBA")
    px = min(W / REF_SIZE[0], H / REF_SIZE[1]) * ss * s.zoom
    for p in build_draw_list(s, cam, sh):
        if isinstance(p, Layer):
            _draw_layer(img, cam, p)
            dr = ImageDraw.Draw(img, "RGBA")
            continue
        pts2 = [cam.project(q) for q in p.pts]
        if p.kind == "line":
            w = max(1, int(round(p.width * px)))
            col = p.color + (255,)
            dr.line(pts2, fill=col, width=w)
            r = max(0.5, (w - 1) / 2.0)     # round joints, same width as the line
            for (x, y) in pts2:
                dr.ellipse([x - r, y - r, x + r, y + r], fill=col)
        else:
            dr.polygon(pts2, fill=p.color + (int(round(255 * p.alpha)),))
    if ss > 1:
        img = img.resize((W, H), Image.LANCZOS)
    return img


def render_rgba(s: Settings, size=REF_SIZE, supersample=4):
    """Render with a transparent background (alpha recovered from a render on
    white and one on black)."""
    w = render(s, size, supersample, (255, 255, 255))
    b = render(s, size, supersample, (0, 0, 0))
    try:
        import numpy as np
        Wa = np.asarray(w, dtype=np.float32)
        Ba = np.asarray(b, dtype=np.float32)
        a = np.clip(255.0 - (Wa - Ba).mean(axis=2), 0, 255)
        safe = np.where(a > 0.5, a, 1.0)
        rgb = np.clip(Ba * (255.0 / safe)[..., None] + 0.5, 0, 255)
        rgb[a <= 0.5] = 0
        return Image.fromarray(np.dstack([rgb, a + 0.5]).astype(np.uint8), "RGBA")
    except ImportError:
        pass
    wp, bp = w.load(), b.load()
    out = Image.new("RGBA", size)
    op = out.load()
    for y in range(size[1]):
        for x in range(size[0]):
            r1, g1, b1 = wp[x, y]
            r0, g0, b0 = bp[x, y]
            a = max(0.0, min(255.0, 255 - ((r1 - r0) + (g1 - g0) + (b1 - b0)) / 3.0))
            if a < 0.5:
                op[x, y] = (0, 0, 0, 0)
            else:
                f = 255.0 / a
                op[x, y] = (min(255, int(r0 * f + 0.5)), min(255, int(g0 * f + 0.5)),
                            min(255, int(b0 * f + 0.5)), int(a + 0.5))
    return out
