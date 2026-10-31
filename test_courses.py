"""The course list file (courses.py) and its use by main.py.

Covers the format, the per-host root, operations under a lock (including two
processes at once), migration from every older layout, and the failure modes:
no root, an unreadable list, a sync conflict copy.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import courses as cl  # noqa: E402


@pytest.fixture(autouse=True)
def host(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDY_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.delenv("STUDY_ROOT", raising=False)
    return tmp_path


def _course(root, name):
    p = Path(root) / name
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


# --- format -----------------------------------------------------------------------

def test_a_course_inside_the_root_is_stored_relative(tmp_path):
    root = tmp_path / "Studium"
    entry = cl.make_course(root, _course(root, "Lernloops/AMW_I"))
    assert entry["path"] == "Lernloops/AMW_I" and entry["name"] == "AMW_I"
    assert cl.resolve_path(root, entry["path"]) == str((root / "Lernloops/AMW_I").resolve())


def test_a_course_outside_the_root_is_stored_absolute(tmp_path):
    root = tmp_path / "Studium"; root.mkdir()
    other = _course(tmp_path / "elsewhere", "X")
    entry = cl.make_course(root, other)
    assert entry["path"] == str(Path(other).resolve())
    assert cl.resolve_path(root, entry["path"]) == entry["path"]


def test_ids_are_stable_across_hosts_and_kept_after_a_move(tmp_path):
    a = cl.make_course(tmp_path / "r1", _course(tmp_path / "r1", "Chemie"))
    b = cl.make_course(tmp_path / "r2", _course(tmp_path / "r2", "Chemie"))
    assert a["id"] == b["id"] and a["id"].startswith("c")
    cl.apply(tmp_path / "r1", add=[a])
    doc = json.loads(cl.file_path(tmp_path / "r1").read_text())
    doc["courses"][0]["path"] = "Chemie_neu"            # the folder was renamed by hand
    cl.file_path(tmp_path / "r1").write_text(json.dumps(doc))
    assert cl.read_courses(tmp_path / "r1")[0]["id"] == a["id"]


def test_the_file_is_versioned(tmp_path):
    cl.apply(tmp_path, add=[cl.make_course(tmp_path, _course(tmp_path, "A"))])
    doc = json.loads(cl.file_path(tmp_path).read_text())
    assert doc["version"] == 1 and doc["courses"][0]["path"] == "A"


def test_unknown_fields_survive_on_every_course_and_at_the_top(tmp_path):
    root = tmp_path
    a = cl.make_course(root, _course(root, "A")); b = cl.make_course(root, _course(root, "B"))
    cl.apply(root, add=[a, b])
    doc = json.loads(cl.file_path(root).read_text())
    doc["future"] = {"x": 1}
    doc["courses"][0]["exam"] = "2027-02-01"
    doc["courses"].append({"id": "cweird", "note": "no path, not ours"})
    cl.file_path(root).write_text(json.dumps(doc))
    cl.apply(root, remove=[b["id"]])
    after = json.loads(cl.file_path(root).read_text())
    assert after["future"] == {"x": 1}
    assert after["courses"][0]["exam"] == "2027-02-01"
    assert {"id": "cweird", "note": "no path, not ours"} in after["courses"]
    assert [c["id"] for c in cl.read_courses(root)] == [a["id"]]


def test_a_newer_version_is_refused_and_left_alone(tmp_path):
    path = cl.file_path(tmp_path); path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"version": 2, "courses": []}))
    with pytest.raises(cl.CoursesError, match="Version"):
        cl.apply(tmp_path, add=[cl.make_course(tmp_path, _course(tmp_path, "A"))])
    assert json.loads(path.read_text())["version"] == 2


def test_an_unreadable_list_is_never_overwritten(tmp_path):
    path = cl.file_path(tmp_path); path.parent.mkdir(parents=True)
    path.write_text('{"version": 1, "courses": [{"id"')                 # half-synced
    with pytest.raises(cl.CoursesError, match="nicht lesbar"):
        cl.apply(tmp_path, add=[cl.make_course(tmp_path, _course(tmp_path, "A"))])
    assert path.read_text() == '{"version": 1, "courses": [{"id"'


# --- operations -------------------------------------------------------------------

def test_adding_the_same_course_twice_is_a_no_op_however_it_is_spelled(tmp_path):
    root = tmp_path
    a = _course(root, "A")
    cl.apply(root, add=[cl.make_course(root, a)])
    cl.apply(root, add=[cl.make_course(root, str(Path(a) / ".." / "A"))])
    cl.apply(root, add=[{"id": "other", "name": "A", "path": "A"}])
    assert len(cl.read_courses(root)) == 1


def test_removing_a_gone_id_does_nothing(tmp_path):
    cl.apply(tmp_path, add=[cl.make_course(tmp_path, _course(tmp_path, "A"))])
    assert len(cl.apply(tmp_path, remove=["nope"])) == 1


def test_path_comparison_ignores_spelling():
    assert cl.same_path("/a/b/../b", "/a/b")
    assert cl.same_path("/a//b", "/a/b/")
    assert not cl.same_path("/a/b", "/a/c")


_WORKER = '''
import sys
sys.path.insert(0, {here!r})
import courses as cl
root, tag, mode = sys.argv[1:4]
for i in range(30):
    if mode == "add":
        cl.apply(root, add=[{{"id": f"{{tag}}{{i}}", "name": "x", "path": f"{{tag}}/{{i}}"}}])
    else:
        cl.apply(root, remove=[f"gone{{i}}"])
'''


def test_two_processes_editing_at_once_lose_nothing(tmp_path):
    root = tmp_path / "root"; root.mkdir()
    script = tmp_path / "worker.py"
    script.write_text(_WORKER.format(here=str(HERE)))
    procs = [subprocess.Popen([sys.executable, str(script), str(root), tag, "add"]) for tag in "abcd"]
    assert all(p.wait(timeout=120) == 0 for p in procs)
    ids = {c["id"] for c in cl.read_courses(root)}
    assert ids == {f"{tag}{i}" for tag in "abcd" for i in range(30)}


def test_a_removal_is_not_undone_by_a_process_that_only_adds(tmp_path):
    root = tmp_path / "root"; root.mkdir()
    cl.apply(root, add=[{"id": f"gone{i}", "name": "g", "path": f"g/{i}"} for i in range(30)])
    script = tmp_path / "worker.py"
    script.write_text(_WORKER.format(here=str(HERE)))
    procs = [subprocess.Popen([sys.executable, str(script), str(root), "n", "add"]),
             subprocess.Popen([sys.executable, str(script), str(root), "n", "remove"])]
    assert all(p.wait(timeout=120) == 0 for p in procs)
    ids = {c["id"] for c in cl.read_courses(root)}
    assert ids == {f"n{i}" for i in range(30)}


# --- root -------------------------------------------------------------------------

def test_the_root_comes_from_the_environment_then_from_host_json(tmp_path):
    assert cl.read_root(None) is None
    assert cl.write_root(tmp_path / "A") == str((tmp_path / "A").resolve())
    assert cl.read_root(None) == str((tmp_path / "A").resolve())
    assert cl.read_root(str(tmp_path / "B")) == str(tmp_path / "B")


def test_the_missing_root_error_names_the_setting():
    err = cl.RootNotSet()
    assert "STUDY_ROOT" in str(err) and "--set-root" in str(err)


def test_a_root_is_guessed_from_existing_courses(tmp_path):
    a = _course(tmp_path / "Studium", "Sprachen/Spanisch")
    b = _course(tmp_path / "Studium", "Lernloops/Chemie")
    assert cl.common_root([a, b]) == str((tmp_path / "Studium").resolve())
    assert cl.common_root([a]) == str((tmp_path / "Studium" / "Sprachen").resolve())
    assert cl.common_root([]) is None
    assert cl.common_root(["/x/a", "/y/b"]) is None


# --- conflict copies --------------------------------------------------------------

def test_conflict_copies_are_listed_not_merged(tmp_path):
    root = tmp_path
    cl.apply(root, add=[cl.make_course(root, _course(root, "A"))])
    folder = cl.file_path(root).parent
    (folder / "courses.sync-conflict-20261031-181500-ABCDEFG.json").write_text(
        json.dumps({"version": 1, "courses": [{"id": "x", "name": "x", "path": "X"}]}))
    assert [p.name for p in cl.conflict_copies(root)] == [
        "courses.sync-conflict-20261031-181500-ABCDEFG.json"]
    assert [c["path"] for c in cl.read_courses(root)] == ["A"]
