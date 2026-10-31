"""The course list: a versioned file beside the courses, edited by operations.

Layout::

    <root>/.study/courses.json   {"version": 1, "courses": [{"id", "name", "path", ...}]}
    <config>/host.json           {"root": "<where the study material lives on this host>"}

``root`` is per host (``STUDY_ROOT`` overrides it), so the list can sit in a synced
folder and mean the same on every machine: ``path`` is relative to the root, or
absolute for a course outside it. Changes are ``add`` / ``remove`` operations that
lock, re-read, apply and write, so two running menus cannot bring back a course the
other one removed. Unknown fields are kept on every course and at the top level.

A Syncthing conflict copy (``courses.sync-conflict-*.json``) is reported, never merged:
a union cannot tell "removed on one host" from "never there".

Stdlib only; locking uses ``fcntl`` (POSIX). Where it is missing (Windows) the lock is
skipped, which leaves the read-apply-write window open but nothing else.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
from typing import Iterator, Optional

try:  # POSIX
    import fcntl
except ImportError:  # pragma: no cover - Windows
    fcntl = None  # type: ignore[assignment]

VERSION = 1
DIR_NAME = ".study"
FILE_NAME = "courses.json"
CONFLICT_GLOB = "courses.sync-conflict-*.json"
ROOT_SETTING = "STUDY_ROOT"


class CoursesError(OSError):
    """The course list cannot be read or changed; nothing was written."""


class RootNotSet(CoursesError):
    """No study root on this host."""

    def __init__(self) -> None:
        super().__init__(
            f"{ROOT_SETTING} ist nicht gesetzt: der Ordner, unter dem dein Lernmaterial "
            f"liegt. Setze die Umgebungsvariable {ROOT_SETTING} oder führe "
            "`study --set-root ORDNER` aus.")


# --- paths ----------------------------------------------------------------------

def norm(path: "str | os.PathLike") -> str:
    """The form two paths are compared in: expanded, normalised, case-folded on Windows."""
    return os.path.normcase(os.path.normpath(os.path.expanduser(str(path))))


def same_path(a: "str | os.PathLike", b: "str | os.PathLike") -> bool:
    return norm(a) == norm(b)


def config_dir() -> Path:
    """Per-host settings: ``STUDY_CONFIG_DIR``, else ``%APPDATA%\\study`` / ``~/.config/study``."""
    override = os.environ.get("STUDY_CONFIG_DIR")
    if override:
        return Path(os.path.expanduser(override))
    if os.name == "nt":  # pragma: no cover - Windows
        return Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming") / "study"
    return Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "study"


def host_file() -> Path:
    return config_dir() / "host.json"


def read_root(env_value: Optional[str] = None) -> Optional[str]:
    """The study root: the environment (passed in), else ``host.json``, else None."""
    if env_value:
        return os.path.expanduser(env_value)
    try:
        value = json.loads(host_file().read_text(encoding="utf-8")).get("root")
    except (OSError, ValueError, AttributeError):
        return None
    return os.path.expanduser(value) if isinstance(value, str) and value else None


def write_root(root: "str | os.PathLike") -> str:
    path = host_file()
    try:
        current = json.loads(path.read_text(encoding="utf-8"))
        current = current if isinstance(current, dict) else {}
    except (OSError, ValueError):
        current = {}
    current["root"] = str(Path(os.path.expanduser(str(root))).resolve())
    _atomic_write(path, current)
    return current["root"]


def common_root(paths: "list[str]") -> Optional[str]:
    """The deepest folder that holds every path: where a root is guessed from, once."""
    parents = [Path(os.path.expanduser(p)).resolve() for p in paths]
    if not parents:
        return None
    try:
        common = os.path.commonpath([str(p) for p in parents])
    except ValueError:  # different drives
        return None
    common_path = Path(common)
    if len(parents) == 1:
        common_path = parents[0].parent
    return None if common_path == Path(common_path.anchor) else str(common_path)


def file_path(root: "str | os.PathLike") -> Path:
    return Path(os.path.expanduser(str(root))) / DIR_NAME / FILE_NAME


def conflict_copies(root: "str | os.PathLike") -> "list[Path]":
    """Sync conflict copies of the list, newest name last. Reported, never merged."""
    folder = file_path(root).parent
    return sorted(folder.glob(CONFLICT_GLOB)) if folder.is_dir() else []


# --- entries --------------------------------------------------------------------

def stored_path(root: "str | os.PathLike", path: "str | os.PathLike") -> str:
    """``path`` relative to the root when it is inside it (with ``/``), else absolute."""
    absolute = Path(os.path.expanduser(str(path))).resolve()
    base = Path(os.path.expanduser(str(root))).resolve()
    try:
        return absolute.relative_to(base).as_posix()
    except ValueError:
        return str(absolute)


def resolve_path(root: "str | os.PathLike", stored: str) -> str:
    """The absolute path of a stored one: relative ones hang off the root."""
    p = Path(os.path.expanduser(stored))
    if p.is_absolute():
        return str(p)
    return str(Path(os.path.expanduser(str(root))).resolve() / p)


def make_id(stored: str) -> str:
    """Derived from the stored path, so two hosts that import the same list agree.
    Kept for good once written: moving the folder later does not change it."""
    return "c" + hashlib.sha1(norm(stored).replace("\\", "/").encode("utf-8")).hexdigest()[:8]


def make_course(root: "str | os.PathLike", path: "str | os.PathLike", name: Optional[str] = None) -> dict:
    stored = stored_path(root, path)
    return {"id": make_id(stored), "name": name or Path(stored).name, "path": stored}


# --- file -----------------------------------------------------------------------

def _atomic_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _read(path: Path) -> dict:
    """The document; an empty one when the file does not exist yet. Raises
    ``CoursesError`` for a file that exists but is not a version this code understands."""
    if not path.exists():
        return {"version": VERSION, "courses": []}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CoursesError(f"Kursliste nicht lesbar ({path}): {exc}") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("courses"), list):
        raise CoursesError(f"Kursliste nicht lesbar ({path}): kein gültiges Format")
    version = doc.get("version")
    if version != VERSION:
        raise CoursesError(
            f"Kursliste {path} hat Version {version!r}, dieses Programm kennt {VERSION}.")
    return doc


def _usable(entry: object) -> bool:
    """Entries this code can act on. Others stay in the file untouched."""
    return isinstance(entry, dict) and isinstance(entry.get("path"), str)


@contextlib.contextmanager
def _locked(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fcntl is None:  # pragma: no cover - Windows
        yield
        return
    with open(path.with_name(path.name + ".lock"), "a+") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def read_courses(root: "str | os.PathLike") -> "list[dict]":
    return [c for c in _read(file_path(root))["courses"] if _usable(c)]


def apply(root: "str | os.PathLike", add: "list[dict] | None" = None,
          remove: "list[str] | None" = None) -> "list[dict]":
    """Lock, re-read, apply ``add`` (course dicts) and ``remove`` (ids), write.

    Adding a path that is already there (same file, however it is written) does
    nothing; removing an id that is gone does nothing. Returns the new list.
    """
    path = file_path(root)
    with _locked(path):
        doc = _read(path)
        before = list(doc["courses"])
        courses = list(before)
        gone = set(remove or [])
        if gone:
            courses = [c for c in courses if not (isinstance(c, dict) and c.get("id") in gone)]
        for new in add or []:
            target = norm(resolve_path(root, new["path"]))
            if not any(_usable(c) and (norm(resolve_path(root, c["path"])) == target
                                       or c.get("id") == new["id"]) for c in courses):
                courses.append(new)
        if courses != before or not path.exists():
            doc["courses"] = courses
            _atomic_write(path, doc)
        return [c for c in courses if _usable(c)]
