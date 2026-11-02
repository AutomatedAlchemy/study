"""The launcher icon: an hourglass with a circuit tree that grows with the courses.

One main branch per course; every course grows small twigs the more Häppchen it has
(``int(sqrt(done))``, at most five, so the first ones come fast and the last ones slowly).
A course nobody touched for a while keeps its branch but loses its colour.

The frame, glass and sand come from ``assets/openstudy.svg``; the tree sits between the
``<!--tree-->`` and ``<!--/tree-->`` markers there and is swapped for the generated one.
Stdlib only.
"""

from __future__ import annotations

import math
import os
import re
from pathlib import Path
from typing import Iterable, NamedTuple

CX, BASE, TOP = 256, 396, 288
GOLD, YELLOW, PINK, CREAM = "#ffb347", "#ffd166", "#ff4f8b", "#fff3d6"
STALE = "#9a7a8c"
STALE_DAYS = 14
MAX_COURSES = 12
MAX_TWIGS = 4
_COLOURS = (PINK, YELLOW, PINK, YELLOW)

_MARKED = re.compile(r"<!--tree-->.*?<!--/tree-->", re.DOTALL)


class Course(NamedTuple):
    done: int = 0                   # Häppchen done in this course
    idle_days: "int | None" = None  # days since the course was last touched


def _wall(y: float) -> float:
    """Half the width of the lower glass bulb at height y (the outline in the SVG)."""
    best = 0.0
    for i in range(201):
        t = i / 200
        by = (1 - t) ** 2 * 250 + 2 * t * (1 - t) * 290 + t * t * 396
        bx = (1 - t) ** 2 * 248 + 2 * t * (1 - t) * 164 + t * t * 164
        if by <= y:
            best = CX - bx
    return best


def twigs_for(done: int) -> int:
    return min(MAX_TWIGS, int(math.sqrt(max(0, done))))


def _point(pts, f):
    """The point at fraction f of the way along a polyline."""
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    want = sum(seg) * f
    for (a, b), n in zip(zip(pts, pts[1:]), seg):
        if want <= n or n == 0:
            k = want / n if n else 0
            return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
        want -= n
    return pts[-1]


def _fmt(pts) -> str:
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def tree_svg(courses: "Iterable[Course]") -> str:
    """The SVG fragment for the tree of these courses (no courses: a sprout)."""
    courses = list(courses)[:MAX_COURSES]
    n = len(courses)
    levels = max(1, math.ceil(n / 2))
    span = 84.0
    gap = min(22.0, span / levels)
    lines, twig_lines, nodes = [], [], []

    top = BASE - 12 - gap * (levels - 1) - (gap / 2 if n > 1 else 0) - 20
    top = max(TOP, min(top, 350))
    lines.append(f'<path d="M{CX} {BASE} V{top:.1f}" stroke="{GOLD}"/>')
    nodes.append(f'<circle cx="{CX}" cy="{top:.1f}" r="{10 if n else 7}" fill="{CREAM}"/>')

    for i, course in enumerate(courses):
        side = -1 if i % 2 == 0 else 1
        level = i // 2
        y = BASE - 12 - level * gap - (gap / 2 if side == 1 else 0)
        rise = max(11 - level, 5)
        slope = (0.55, 0.8, 0.45, 0.7, 0.6)[i % 5]
        reach = 58 - level * 6 + (3 if side == 1 else 0) - (i * 7) % 5
        while reach > 14 and _wall(y - reach * slope - rise) - reach < 24:
            reach -= 2
        ex, ey = CX + side * reach, y - reach * slope
        pts = [(CX, y), (ex, ey), (ex, ey - rise)]
        stale = course.idle_days is not None and course.idle_days >= STALE_DAYS
        colour = STALE if stale else _COLOURS[i % len(_COLOURS)]
        lines.append(f'<path d="{_fmt(pts)}" stroke="{colour}"/>')
        nodes.append(f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="6" fill="{colour}"/>')
        k = twigs_for(course.done)
        for j in range(k):
            px, py = _point(pts, (j + 1) / (k + 1) * 0.92)
            steep = j % 2 == 0   # alternate steep and flat twigs, always away from the trunk
            dx, dy = side * (7 if steep else 11), -(11 if steep else 7)
            tx, ty = px + dx, py + dy
            if _wall(ty) - abs(tx - CX) < 12:
                continue
            twig_lines.append(f'<path d="M{px:.1f} {py:.1f} L{tx:.1f} {ty:.1f}" stroke="{colour}"/>')
            nodes.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="3.4" fill="{colour}"/>')

    return ("<!--tree-->"
            '<g fill="none" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round">'
            + "".join(lines) + "</g>"
            '<g fill="none" stroke-width="4" stroke-linecap="round">' + "".join(twig_lines) + "</g>"
            + "".join(nodes) + "<!--/tree-->")


def render(template: str, courses: "Iterable[Course]") -> str:
    """The template SVG with its marked tree replaced by the one for ``courses``."""
    if not _MARKED.search(template):
        raise ValueError("template has no <!--tree--> markers")
    return _MARKED.sub(lambda _m: tree_svg(courses), template, count=1)


def write_icon(template_path: "str | Path", target: "str | Path",
               courses: "Iterable[Course]") -> bool:
    """Write the icon; True when the file changed. Never leaves a half-written file."""
    svg = render(Path(template_path).read_text(encoding="utf-8"), courses)
    target = Path(target)
    try:
        if target.read_text(encoding="utf-8") == svg:
            return False
    except OSError:
        pass
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + f".{os.getpid()}.tmp")
    tmp.write_text(svg, encoding="utf-8")
    os.replace(tmp, target)
    return True
