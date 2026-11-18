"""The launcher icon: what the tree shows, and that it can never break a session."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import icon
from icon import Course

ASSET = Path(__file__).resolve().parent / "assets" / "openstudy.svg"


def _svg(courses):
    return icon.render(ASSET.read_text(encoding="utf-8"), courses)


def _count(svg, pattern):
    return len(re.findall(pattern, svg))


def test_every_output_is_valid_svg():
    for n in (0, 1, 2, 7, 12, 40):
        ET.fromstring(_svg([Course(9, 0)] * n))


def test_one_main_branch_per_course_and_a_capped_number():
    def mains(n):
        # the main branches are the paths with stroke-width group 6.5, one per course plus the trunk
        group = re.search(r'<g fill="none" stroke-width="7".*?</g>', _svg([Course()] * n)).group(0)
        return group.count("<path") - 1
    assert [mains(n) for n in (0, 1, 5)] == [0, 1, 5]
    assert mains(50) == icon.MAX_COURSES


def test_more_done_means_more_twigs_with_a_ceiling():
    assert [icon.twigs_for(d) for d in (0, 1, 4, 9, 16, 1000)] == [0, 1, 2, 3, 3, icon.MAX_TWIGS]
    few = _svg([Course(1)])
    many = _svg([Course(100)])
    twig = rf'r="{icon.TWIG_R}"'
    assert _count(few, twig) == 1
    assert _count(_svg([Course(1000)]), twig) == _count(many, twig) == icon.MAX_TWIGS
    assert many.count("<path") > few.count("<path")


def test_idle_course_loses_its_colour():
    assert icon.STALE in _svg([Course(5, icon.STALE_DAYS)])
    assert icon.STALE not in _svg([Course(5, icon.STALE_DAYS - 1)])
    assert icon.STALE not in _svg([Course(5, None)])


def test_nothing_leaves_the_glass():
    svg = _svg([Course(50, 0)] * icon.MAX_COURSES)
    twigs = re.findall(rf'<circle cx="([\d.]+)" cy="([\d.]+)" r="{re.escape(str(icon.TWIG_R))}"', svg)
    assert twigs
    for x, y in twigs:
        assert abs(float(x) - icon.CX) < icon._wall(float(y)), (x, y)


def test_write_is_atomic_and_idempotent(tmp_path):
    target = tmp_path / "sub" / "icon.svg"
    assert icon.write_icon(ASSET, target, [Course(4, 1)]) is True
    assert icon.write_icon(ASSET, target, [Course(4, 1)]) is False
    assert icon.write_icon(ASSET, target, [Course(4, 1), Course(1, 1)]) is True
    assert not list(target.parent.glob("*.tmp"))


def test_template_without_markers_is_refused():
    try:
        icon.render("<svg/>", [])
    except ValueError:
        return
    raise AssertionError("expected ValueError")
