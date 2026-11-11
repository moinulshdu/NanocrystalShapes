"""
Geometry of the nanocrystal shapes.

Polyhedra (tetrahedron, cube, octahedron, cuboctahedron, icosahedron,
decahedron, bipyramid, triangular and hexagonal plates) are built as the
intersection of half-spaces: the faces of the base solid plus one cutting
plane per corner. Truncation t cuts every corner at a fraction t of the
edges that meet there, exactly as in the original tetrahedron figure.

Curved shapes (sphere, rod, tube, tetrapod) are triangle meshes with smooth
vertex normals, so their outlines can be drawn as smooth contours.

Every solid is centred on the origin.
"""
from __future__ import annotations

import math

# --------------------------------------------------------------------------
# vectors
# --------------------------------------------------------------------------


def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    n = math.sqrt(dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n) if n > 1e-15 else (0.0, 0.0, 0.0)


def lerp(a, b, s): return add(a, mul(sub(b, a), s))


def centroid(pts):
    c = (0.0, 0.0, 0.0)
    for p in pts:
        c = add(c, p)
    return mul(c, 1.0 / len(pts))


def basis(d):
    """Two unit vectors perpendicular to unit vector d (u x v = d)."""
    tmp = (0.0, 0.0, 1.0) if abs(d[2]) < 0.9 else (1.0, 0.0, 0.0)
    u = norm(cross(tmp, d))
    v = cross(d, u)
    return u, v


def rot_y90(p):
    """Rotate so that the z axis becomes the x axis."""
    return (p[2], p[1], -p[0])


PHI = (1 + 5 ** 0.5) / 2


# --------------------------------------------------------------------------
# containers
# --------------------------------------------------------------------------


class Facet:
    __slots__ = ("pts", "n", "vn", "surf", "c")

    def __init__(self, pts, n, surf, vn=None):
        self.pts = pts      # 3D points (counter-clockwise seen from outside)
        self.n = n          # outward unit normal
        self.vn = vn        # vertex normals (smooth surfaces only)
        self.surf = surf    # index of the surface it belongs to
        self.c = centroid(pts)


class Surface:
    """kind: 'poly'   - flat polygon faces; every edge is drawn
             'smooth' - curved; its outline (contour) is drawn
             'flat'   - flat cap made of several triangles; no lines drawn
       rims: draw the open boundary of this surface (e.g. ends of a tube)."""

    def __init__(self, kind, rims=False, inward=False):
        self.kind = kind
        self.rims = rims
        self.inward = inward        # normals point into the hollow (tube bore)
        self.facets = []
        self.hull = []              # circumscribing planes (non-convex shapes)


class Shape:
    def __init__(self):
        self.surfaces = []
        self.convex = True
        self.class_planes = []      # n.p <= d, describing a convex shape
        self.V = None               # corners of the uncut polyhedron
        self.adj = None             # neighbouring corners
        self.poly_edges = []        # edges of the (truncated) polyhedron
        self.corner_lines = []      # vertex -> cut point (the tL pieces)
        self.radius_points = []     # lines from the centre to these points
        self.twin_polys = []        # internal twin planes
        self.rims = []              # boundary lines of curved surfaces
        self.fit_points = []        # used to size the shape in the frame
        self.is_polyhedron = False

    @property
    def facets(self):
        for s in self.surfaces:
            for f in s.facets:
                yield f

    def finish(self):
        """Collect rims of curved surfaces."""
        for si, srf in enumerate(self.surfaces):
            if not srf.rims:
                continue
            count = {}
            for f in srf.facets:
                k = len(f.pts)
                for i in range(k):
                    p, q = f.pts[i], f.pts[(i + 1) % k]
                    key = _ekey(p, q)
                    if key in count:
                        count[key][1] += 1
                    else:
                        count[key] = [(p, q), 1]
            self.rims += [pq for pq, c in count.values() if c == 1]
        if not self.fit_points:
            uniq = {}
            for f in self.facets:
                for q in f.pts:
                    uniq.setdefault(_pkey(q), q)
            self.fit_points = list(uniq.values())
        if not self.convex:
            for srf in self.surfaces:
                uniq = {}
                for f in srf.facets:
                    for q in f.pts:
                        uniq.setdefault(_pkey(q), q)
                srf.hull = support_planes(list(uniq.values()), 90)
        return self


def _pkey(p):
    return (round(p[0], 6), round(p[1], 6), round(p[2], 6))


def _ekey(p, q):
    a, b = _pkey(p), _pkey(q)
    return (a, b) if a <= b else (b, a)


# --------------------------------------------------------------------------
# half-space polyhedra
# --------------------------------------------------------------------------


def hull_planes(V):
    """Face planes (outward n, d) of the convex hull of points V (centred)."""
    c = centroid(V)
    planes = []
    n = len(V)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                m = cross(sub(V[j], V[i]), sub(V[k], V[i]))
                if dot(m, m) < 1e-14:
                    continue
                m = norm(m)
                d = dot(m, V[i])
                if dot(m, c) > d:
                    m, d = mul(m, -1.0), -d
                if all(dot(m, p) <= d + 1e-7 for p in V):
                    if not any(abs(d - d2) < 1e-6 and dot(m, m2) > 1 - 1e-9 for m2, d2 in planes):
                        planes.append((m, d))
    return planes


def clip_polygon(poly, m, e, eps=1e-9):
    """Keep the part of polygon `poly` with m.p <= e."""
    out = []
    k = len(poly)
    for i in range(k):
        P, Q = poly[i], poly[(i + 1) % k]
        fp, fq = dot(m, P) - e, dot(m, Q) - e
        if fp <= eps:
            out.append(P)
        if (fp <= eps) != (fq <= eps):
            s = fp / (fp - fq)
            out.append(lerp(P, Q, s))
    return out


def _clean(poly):
    out = []
    for p in poly:
        if not out or math.dist(p, out[-1]) > 1e-7:
            out.append(p)
    while len(out) > 1 and math.dist(out[0], out[-1]) <= 1e-7:
        out.pop()
    return out


def _area(poly, n):
    a = (0.0, 0.0, 0.0)
    for i in range(len(poly)):
        a = add(a, cross(poly[i], poly[(i + 1) % len(poly)]))
    return 0.5 * abs(dot(a, n))


def plane_polygon(n, d, planes, skip=None, size=20.0):
    """Polygon of plane n.p = d cut by all half-spaces in `planes`."""
    u, v = basis(n)
    c0 = mul(n, d)
    poly = [add(c0, add(mul(u, x * size), mul(v, y * size))) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for k, (m, e) in enumerate(planes):
        if k == skip:
            continue
        poly = clip_polygon(poly, m, e)
        if len(poly) < 3:
            return []
    poly = _clean(poly)
    if len(poly) < 3 or _area(poly, n) < 1e-9:
        return []
    return poly


def polyhedron(V, t, cut_mode="radial", twin_axis=None, twin_vertices=(), radius_points=None):
    """Truncated convex polyhedron. cut_mode 'radial' cuts each corner
    perpendicular to its direction from the centre; 'horizontal' cuts plates
    with vertical planes (in-plane corner truncation)."""
    sh = Shape()
    sh.is_polyhedron = True
    sh.V = list(V)
    faces = hull_planes(V)
    n = len(V)
    on = [{k for k, (m, d) in enumerate(faces) if abs(dot(m, V[i]) - d) < 1e-6} for i in range(n)]
    sh.adj = [[j for j in range(n) if j != i and len(on[i] & on[j]) >= 2] for i in range(n)]

    planes = list(faces)
    cuts = {}
    if t > 1e-4:
        for i in range(n):
            if cut_mode == "horizontal":
                nn = norm((V[i][0], V[i][1], 0.0))
            else:
                nn = norm(V[i])
            nb = [j for j in sh.adj[i] if dot(nn, sub(V[j], V[i])) < -1e-9]
            if not nb:
                continue
            d = sum(dot(nn, lerp(V[i], V[j], t)) for j in nb) / len(nb)
            cuts[i] = (nn, d)
            planes.append((nn, d))
    sh.class_planes = planes

    srf = Surface("poly")
    for k, (m, d) in enumerate(planes):
        p = plane_polygon(m, d, planes, skip=k)
        if p:
            srf.facets.append(Facet(p, m, 0))
    sh.surfaces.append(srf)

    seen = set()
    for f in srf.facets:
        for i in range(len(f.pts)):
            p, q = f.pts[i], f.pts[(i + 1) % len(f.pts)]
            key = _ekey(p, q)
            if key not in seen:
                seen.add(key)
                sh.poly_edges.append((p, q))

    for i, (nn, d) in cuts.items():
        for j in sh.adj[i]:
            den = dot(nn, sub(V[j], V[i]))
            if den < -1e-9:
                s = max(0.0, min(1.0, (d - dot(nn, V[i])) / den))
                sh.corner_lines.append((V[i], lerp(V[i], V[j], s)))

    if twin_axis is not None:
        a = norm(twin_axis)
        for e in twin_vertices:
            ep = norm(sub(e, mul(a, dot(a, e))))
            m = norm(cross(a, ep))
            poly = plane_polygon(m, 0.0, planes + [(mul(ep, -1.0), 0.0)])
            if poly:
                sh.twin_polys.append(poly)

    sh.radius_points = list(radius_points) if radius_points is not None else list(V)
    sh.fit_points = list(V)
    return sh.finish()


# --------------------------------------------------------------------------
# base solids (edge length 1 unless stated)
# --------------------------------------------------------------------------


def tetra_vertices():
    """Apex A, then the base vertices L (left/back), F (front), R (right)."""
    h = math.sqrt(2.0 / 3.0)
    r = 1.0 / math.sqrt(3.0)
    base = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), -h / 4)
            for a in (90.0, 210.0, 330.0)]
    return [(0.0, 0.0, 3 * h / 4)] + base


OCTA_TWIST = 20.0


def octa_vertices():
    a = 1.0 / math.sqrt(2.0)
    rot = math.radians(OCTA_TWIST)
    eq = [(a * math.cos(rot + k * math.pi / 2), a * math.sin(rot + k * math.pi / 2), 0.0) for k in range(4)]
    return [(0.0, 0.0, a)] + eq + [(0.0, 0.0, -a)]


def cube_vertices():
    return [(x * 0.5, y * 0.5, z * 0.5) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]


def cubocta_vertices():
    s = 1.0 / math.sqrt(2.0)
    out = []
    for a in (-1, 1):
        for b in (-1, 1):
            out += [(a * s, b * s, 0.0), (a * s, 0.0, b * s), (0.0, a * s, b * s)]
    return out


def icosa_vertices():
    out = []
    for a in (-1, 1):
        for b in (-1, 1):
            out += [(0.0, a * 0.5, b * PHI / 2), (a * 0.5, b * PHI / 2, 0.0), (b * PHI / 2, 0.0, a * 0.5)]
    return out


def ngon(n, R, z, phase=90.0):
    return [(R * math.cos(math.radians(phase + 360.0 * k / n)),
             R * math.sin(math.radians(phase + 360.0 * k / n)), z) for k in range(n)]


# --------------------------------------------------------------------------
# meshes
# --------------------------------------------------------------------------


def revolve(sh, profile, center, d, nseg, kind="smooth", rims=False, inward=False):
    """Surface of revolution about axis d through `center`.
    profile: list of (x, rho, nx, nrho) - position along the axis, radius and
    the (unnormalised) normal in the meridian plane."""
    u, v = basis(d)
    rings, nrings = [], []
    for x, rho, nx, nr in profile:
        ring, nring = [], []
        nl = math.hypot(nx, nr) or 1.0
        for j in range(nseg):
            ph = 2 * math.pi * j / nseg
            radial = add(mul(u, math.cos(ph)), mul(v, math.sin(ph)))
            ring.append(add(center, add(mul(d, x), mul(radial, rho))))
            nn = add(mul(d, nx / nl), mul(radial, nr / nl))
            nring.append(mul(nn, -1.0) if inward else nn)
        rings.append(ring)
        nrings.append(nring)
    srf = Surface(kind, rims, inward)
    si = len(sh.surfaces)
    for i in range(len(rings) - 1):
        for j in range(nseg):
            j2 = (j + 1) % nseg
            quad = [(rings[i][j], nrings[i][j]), (rings[i][j2], nrings[i][j2]),
                    (rings[i + 1][j2], nrings[i + 1][j2]), (rings[i + 1][j], nrings[i + 1][j])]
            for tri in ((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3])):
                pts = [p for p, _ in tri]
                m = cross(sub(pts[1], pts[0]), sub(pts[2], pts[0]))
                if dot(m, m) < 1e-16:
                    continue
                m = norm(m)
                avg = add(add(tri[0][1], tri[1][1]), tri[2][1])
                if dot(m, avg) < 0:
                    pts = [pts[0], pts[2], pts[1]]
                    vns = [tri[0][1], tri[2][1], tri[1][1]]
                    m = mul(m, -1.0)
                else:
                    vns = [q for _, q in tri]
                srf.facets.append(Facet(pts, m, si, vns))
    sh.surfaces.append(srf)
    return rings


def disc(sh, ring_outer, ring_inner, n_out):
    """Flat cap (disc or annulus) between rings, facing n_out."""
    srf = Surface("flat")
    si = len(sh.surfaces)
    k = len(ring_outer)
    if ring_inner is None:
        c = centroid(ring_outer)
        for j in range(k):
            pts = [c, ring_outer[j], ring_outer[(j + 1) % k]]
            m = norm(cross(sub(pts[1], pts[0]), sub(pts[2], pts[0])))
            if dot(m, n_out) < 0:
                pts = [pts[0], pts[2], pts[1]]
            srf.facets.append(Facet(pts, n_out, si))
    else:
        for j in range(k):
            j2 = (j + 1) % k
            pts = [ring_outer[j], ring_outer[j2], ring_inner[j2], ring_inner[j]]
            m = norm(cross(sub(pts[1], pts[0]), sub(pts[2], pts[0])))
            if dot(m, n_out) < 0:
                pts = pts[::-1]
            srf.facets.append(Facet(pts, n_out, si))
    sh.surfaces.append(srf)


def capsule_profile(x0, x1, r, cap, nseg_cap=14, nseg_body=6):
    """Profile of a rod from x0 to x1 with radius r whose ends are rounded by
    `cap` (0 flat ... 1 hemispherical). Returns (profile, flat_ends)."""
    L = x1 - x0
    a = min(cap * r, L / 2.0)
    if a < 1e-3:
        prof = [(x0 + L * i / nseg_body, r, 0.0, 1.0) for i in range(nseg_body + 1)]
        return prof, True
    prof = []
    for i in range(nseg_cap + 1):          # left cap, -90 .. 0 deg
        th = -math.pi / 2 + (math.pi / 2) * i / nseg_cap
        prof.append((x0 + a + a * math.sin(th), r * math.cos(th), math.sin(th) / a, math.cos(th) / r))
    body = (x1 - a) - (x0 + a)
    if body > 1e-6:
        for i in range(1, nseg_body + 1):
            prof.append((x0 + a + body * i / nseg_body, r, 0.0, 1.0))
    for i in range(1, nseg_cap + 1):       # right cap, 0 .. 90 deg
        th = (math.pi / 2) * i / nseg_cap
        prof.append((x1 - a + a * math.sin(th), r * math.cos(th), math.sin(th) / a, math.cos(th) / r))
    return prof, False


def support_planes(points, ndir=160):
    """Circumscribing planes of the convex hull of `points` (Fibonacci directions)."""
    planes = []
    ga = math.pi * (3 - math.sqrt(5))
    try:
        import numpy as np
        P = np.asarray(points, dtype=float)
    except ImportError:
        P = None
    for i in range(ndir):
        z = 1 - 2 * (i + 0.5) / ndir
        r = math.sqrt(max(0.0, 1 - z * z))
        n = (r * math.cos(ga * i), r * math.sin(ga * i), z)
        if P is not None:
            d = float((P @ np.asarray(n)).max())
        else:
            d = max(dot(n, p) for p in points)
        planes.append((n, d))
    return planes


def capsule(sh, p0, p1, r, cap, nseg=64):
    d = norm(sub(p1, p0))
    L = math.dist(p0, p1)
    prof, flat = capsule_profile(0.0, L, r, cap)
    rings = revolve(sh, prof, p0, d, nseg, "smooth", rims=flat)
    if flat:
        disc(sh, rings[0], None, mul(d, -1.0))
        disc(sh, rings[-1], None, d)


def sphere_shape(p):
    sh = Shape()
    r = 0.5
    nlat = 40
    prof = []
    for i in range(nlat + 1):
        th = -math.pi / 2 + math.pi * i / nlat
        prof.append((r * math.sin(th), r * math.cos(th), math.sin(th), math.cos(th)))
    revolve(sh, prof, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 80)
    sh.radius_points = [mul(norm((-0.55, 0.75, -0.35)), r)]
    sh.finish()
    sh.class_planes = support_planes(sh.fit_points)
    return sh


def rod_shape(p):
    sh = Shape()
    D = 1.0
    L = max(p["aspect"], 1.0) * D
    a = (-L / 2, 0.0, 0.0)
    b = (L / 2, 0.0, 0.0)
    capsule(sh, a, b, D / 2, p["cap"])
    sh.radius_points = [a, b]
    sh.finish()
    sh.class_planes = support_planes(sh.fit_points)
    return sh


def tube_shape(p):
    sh = Shape()
    sh.convex = False
    R = 0.5
    r = R * min(max(p["wall"], 0.05), 0.97)
    L = max(p["aspect"], 0.2) * 2 * R
    d = (1.0, 0.0, 0.0)
    c = (-L / 2, 0.0, 0.0)
    nb = 6
    outer = revolve(sh, [(L * i / nb, R, 0.0, 1.0) for i in range(nb + 1)], c, d, 64, "smooth", rims=True)
    inner = revolve(sh, [(L * i / nb, r, 0.0, 1.0) for i in range(nb + 1)], c, d, 64, "smooth",
                    rims=True, inward=True)
    disc(sh, outer[0], inner[0], (-1.0, 0.0, 0.0))
    disc(sh, outer[-1], inner[-1], (1.0, 0.0, 0.0))
    sh.radius_points = [(-L / 2, 0.0, 0.0), (L / 2, 0.0, 0.0)]
    return sh.finish()


def tetrapod_shape(p):
    sh = Shape()
    sh.convex = False
    D = 1.0
    Larm = max(p["aspect"], 0.6) * D
    dirs = [norm(v) for v in tetra_vertices()]
    tips = []
    for dv in dirs:
        tip = mul(dv, Larm)
        tips.append(tip)
        # each arm starts a little behind the centre so the core is closed
        start = mul(dv, -D * 0.25)
        capsule(sh, start, tip, D / 2, p["cap"], nseg=56)
    sh.radius_points = tips
    return sh.finish()


# --------------------------------------------------------------------------
# polyhedral shape builders
# --------------------------------------------------------------------------


def tetra_shape(p):
    return polyhedron(tetra_vertices(), p["t"])


def octa_shape(p):
    return polyhedron(octa_vertices(), p["t"])


def cube_shape(p):
    return polyhedron(cube_vertices(), p["t"])


def cubocta_shape(p):
    return polyhedron(cubocta_vertices(), p["t"])


def icosa_shape(p):
    return polyhedron(icosa_vertices(), p["t"])


DECA_IDEAL_ASPECT = 1.0 / math.sqrt(3.0)   # five regular tetrahedra: axis 1, width sqrt(3)


def decahedron_shape(p):
    """Five tetrahedra sharing the vertical 5-fold axis. aspect = length of the
    5-fold axis / width across the equator; 1/sqrt(3) = 0.577 is the ideal
    decahedron made of five regular tetrahedra (edge 1)."""
    R = math.sqrt(3.0) / 2.0
    h = max(p.get("aspect", DECA_IDEAL_ASPECT), 0.05) * R    # half-length of the axis
    eq = ngon(5, R, 0.0, phase=-90.0)
    V = [(0.0, 0.0, h)] + eq + [(0.0, 0.0, -h)]
    return polyhedron(V, p["t"], twin_axis=(0.0, 0.0, 1.0), twin_vertices=eq)


def bipyramid_shape(p):
    """n-sided bipyramid lying along x; aspect = length / width."""
    n = int(round(p["sides"]))
    R = 0.5
    h = max(p["aspect"], 0.3) * R
    eq = ngon(n, R, 0.0, phase=90.0)
    V = [(0.0, 0.0, h)] + eq + [(0.0, 0.0, -h)]
    V = [rot_y90(v) for v in V]
    eq = [rot_y90(v) for v in eq]
    twin = (1.0, 0.0, 0.0) if n == 5 else None
    return polyhedron(V, p["t"], twin_axis=twin, twin_vertices=eq)


def plate_shape(n, edge):
    def build(p):
        R = edge / (2 * math.sin(math.pi / n))
        h = max(p["aspect"], 0.01) * edge
        top = ngon(n, R, h / 2, phase=90.0)
        bot = ngon(n, R, -h / 2, phase=90.0)
        mid = ngon(n, R, 0.0, phase=90.0)
        return polyhedron(top + bot, p["t"], cut_mode="horizontal", radius_points=mid)
    return build
