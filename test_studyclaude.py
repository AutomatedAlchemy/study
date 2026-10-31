"""Offline tests for studyclaude — no konsole/claude launch, no network.

Every test asserts a behaviour that would break something real: the registry
state machine, the CLI routing, the launch argv, the parsers that read foreign
files, and the SSoT boundary. Wording of prompts is deliberately not pinned.

Loads main.py under a unique module name (repo runs pytest in prepend-import
mode with no __init__.py, so a bare `import main` would collide with siblings).
"""
import curses
import datetime
import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
MAIN = HERE / "main.py"
TEMPLATE = (HERE / "templates" / "LERNLOOP_TEMPLATE.md").read_text(encoding="utf-8")


def _load():
    spec = importlib.util.spec_from_file_location("studyclaude_main", MAIN)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m = _load()


@pytest.fixture(autouse=True)
def spawns(monkeypatch, tmp_path):
    """No test may open a real konsole or exec a real claude. execvpe is
    recorded (tests inspect the argv); a Popen fails the test unless it opted
    in with ``spawns["allow_popen"] = True``. Also isolates the registry."""
    rec = {"exec": [], "popen": [], "cwd": None}
    monkeypatch.setenv("STUDYCLAUDE_REGISTRY", str(tmp_path / "registry.json"))
    monkeypatch.delenv("STUDYCLAUDE_DEFAULT_WORKSPACE", raising=False)
    monkeypatch.delenv("STUDYCLAUDE_MEDIUM", raising=False)
    monkeypatch.delenv("STUDYCLAUDE_EXAMS", raising=False)
    monkeypatch.setenv("CLAUDE_TIER_OVERRIDE", "max")
    monkeypatch.setattr(m.os, "chdir", lambda d: rec.update(cwd=d))
    monkeypatch.setattr(m.os, "execvpe", lambda prog, argv, env: rec["exec"].append(argv))
    monkeypatch.setattr(m.subprocess, "Popen", lambda cmd, **k: rec["popen"].append(cmd))
    yield rec
    assert not rec["popen"] or rec.get("allow_popen"), f"real spawn attempted: {rec['popen']}"


def _courses(tmp_path, *names):
    out = []
    for n in names:
        ws = tmp_path / n; ws.mkdir()
        out.append(str(ws))
    return out


# ---- guards --------------------------------------------------------------

def test_no_personal_paths_and_no_builtin_default():
    """A fresh clone must not know anyone's study folders."""
    src = MAIN.read_text(encoding="utf-8")
    for leaked in ("Klausurvorbereitung", "/home/prob", "Synced/OneDrive"):
        assert leaked not in src, f"personal path leaked into main.py: {leaked}"
    assert m._resolve_workspace(None) is None
    data = m._ensure_default(m._load_registry())
    assert data["workspaces"] == [] and data["default"] is None
    assert m._menu_rows([]) == [m._ADD_SENTINEL]


def test_board_template_carries_no_mcp_manual():
    """The board template says what the loop wants on the board, never how the
    MCP tools behave: the server sends that itself on every connection, and a
    copy here can only be older. See CLAUDE.md § The medium switch."""
    text = (HERE / "templates" / "media" / "board.md").read_text(encoding="utf-8")
    for manual in (
        "kinds",                          # wake-kind lists (0.22.0 removed the parameter)
        "curl",                           # how wait_url / request_upload are driven
        "await_event",                    # the fallback tool's name and cost
        "submissions_you_have_not_read",  # list_tabs field names
        "Großbuchstaben",                 # label rendering (fixed in the web app)
        "kontoweit",                      # select_board semantics, stated by the server
        "nimmt keine PDFs",               # upload rules, stated by request_upload
    ):
        assert manual not in text, f"MCP usage leaked into media/board.md: {manual}"
    assert "Bedienung des Boards" in text


def test_advertise_answers_before_heavy_imports(monkeypatch, capsys):
    """The installer polls --advertise with a 5s timeout; it is answered at
    import time, before argparse, and must be the installer's JSON shape."""
    monkeypatch.setattr(sys, "argv", ["studyclaude", "--advertise"])
    with pytest.raises(SystemExit) as e:
        _load()
    assert e.value.code == 0
    meta = json.loads(capsys.readouterr().out)[0]
    assert meta["alias"] == "studyclaude" and meta["capability"] == "agent"
    assert "skill_name" not in meta   # an agent you talk to, not a skill


# ---- registry ------------------------------------------------------------

def test_registry_state_machine(tmp_path, monkeypatch):
    a, b = _courses(tmp_path, "A", "B")
    m._register_workspace(a)
    assert m._load_registry()["default"] is None            # registering never claims it
    assert m._ensure_default(m._load_registry())["default"] == m._BEGLEITER_SENTINEL
    m._register_workspace(b); m._register_workspace(b)
    assert m._load_registry()["workspaces"].count(b) == 1   # idempotent
    data = m._load_registry(); data["default"] = None
    assert m._ensure_default(data)["default"] == m._BEGLEITER_SENTINEL   # unset → Begleiter
    m._set_default(b)
    assert m._load_registry()["default"] == b
    for literal, sentinel in (("quickie", m._QUICKIE_SENTINEL),
                              ("begleiter", m._BEGLEITER_SENTINEL)):
        m._set_default(literal)
        data = m._load_registry()
        assert data["default"] == sentinel and sentinel not in data["workspaces"]
        assert m._resolve_workspace(None) == a               # scripts never see a sentinel
    monkeypatch.setenv("STUDYCLAUDE_DEFAULT_WORKSPACE", b)
    assert m._resolve_workspace(None) == b                   # env wins
    monkeypatch.delenv("STUDYCLAUDE_DEFAULT_WORKSPACE")
    m._set_default(a)
    assert m._unregister_workspace(a) and not m._unregister_workspace(a)
    assert m._ensure_default(m._load_registry())["default"] == m._BEGLEITER_SENTINEL   # falls back
    assert m._menu_rows([a, b]) == [m._BEGLEITER_SENTINEL, m._QUICKIE_SENTINEL,
                                    a, b, m._ADD_SENTINEL]
    # a default that is neither a course nor a known sentinel (retired sentinel
    # from another host, unregistered course) counts as unset — in the menu and
    # for scripts
    for retired in ("__RETIRED__", "__TUTOR__", "__META__"):
        assert (m._ensure_default({"workspaces": [b], "default": retired})["default"]
                == m._BEGLEITER_SENTINEL)
        data = m._load_registry(); data["default"] = retired; m._save_registry(data)
        assert m._resolve_workspace(None) == b
    assert "unverändert" in m._set_default("tutor")          # never registers <cwd>/tutor
    assert m._load_registry()["workspaces"] == [b]


def test_archive_moves_the_course_beside_it_and_never_overwrites(tmp_path):
    kurs = tmp_path / "Kurse" / "Analysis"
    (kurs / "sub").mkdir(parents=True)
    (kurs / "todo.md").write_text("x", encoding="utf-8")
    dest = m._archive_workspace(str(kurs))
    assert dest == tmp_path / "Kurse" / "_archiv" / "Analysis"
    assert (dest / "todo.md").is_file() and not kurs.exists()
    kurs.mkdir()                                   # same name again: gets a date suffix
    assert m._archive_target(str(kurs), "2026-09-23").name == "Analysis-2026-09-23"
    (tmp_path / "Kurse" / "_archiv" / "Analysis-2026-09-23").mkdir()
    assert m._archive_target(str(kurs), "2026-09-23").name == "Analysis-2026-09-23-2"
    inner = kurs / "Teil"                          # a registered course inside blocks the move
    inner.mkdir()
    with pytest.raises(OSError):
        m._archive_workspace(str(kurs), [str(kurs), str(inner)])
    assert kurs.is_dir()
    with pytest.raises(OSError):
        m._archive_workspace(str(tmp_path / "fehlt"))

def test_medium_choice_precedence(monkeypatch):
    assert m._current_medium() == "xournalpp"
    m._set_medium("board")
    assert m._current_medium() == "board"                    # registry
    monkeypatch.setenv("STUDYCLAUDE_MEDIUM", "xournalpp")
    assert m._current_medium() == "xournalpp"                # env wins
    monkeypatch.setenv("STUDYCLAUDE_MEDIUM", "garbage")
    assert m._current_medium() == "xournalpp"                # junk falls back
    for medium in m._MEDIA:
        assert (HERE / "templates" / "media" / f"{medium}.md").is_file()


def test_model_picker_and_registry_tolerance():
    assert m._current_model() == m.DEFAULT_MODEL             # fresh registry
    m._set_model("sonnet")
    assert m._current_model() == "sonnet"
    assert m._model_label("opus") == "Opus"
    models = m._available_models()
    assert set(m._ANTHROPIC_MODELS) <= set(models)
    assert "auto" not in models                              # removed 2026-09-16
    # a model this build does not know (an old registry) falls back, never crashes
    m._set_model("deepseek-ai/DeepSeek-V4-Flash-0731")
    assert m._current_model() == m.DEFAULT_MODEL
    assert m._backend_cmd() == ["claude"]


def test_quickie_streak_arithmetic():
    data = {"workspaces": []}
    assert m._record_quickie(data, "2026-08-24") == (1, 1)
    assert m._record_quickie(data, "2026-08-24") == (1, 2)   # same day: no streak bump
    assert m._record_quickie(data, "2026-08-25") == (2, 3)
    assert m._quickie_stats(data, "2026-08-26") == (2, 3)    # yesterday still counts
    assert m._quickie_stats(data, "2026-08-28") == (0, 3)    # lapsed
    assert m._record_quickie(data, "2026-08-28") == (1, 4)   # restarts
    assert m._quickie_stats({"quickies": {"last": "garbage"}}) == (0, 0)


# ---- CLI routing and launching ------------------------------------------

def test_cli_routes(tmp_path, monkeypatch, spawns):
    a, b = _courses(tmp_path, "A", "B")
    m._register_workspace(a); m._register_workspace(b)
    called = []
    for name in ("run_menu", "launch", "do_add", "_launch_quickie",
                 "_launch_gaertner", "_launch_begleiter"):
        monkeypatch.setattr(m, name, lambda *x, _n=name, **k: called.append(_n) or 0)
    cases = {
        (): "run_menu",
        (a,): "launch",
        ("--add",): "do_add",
        ("--begleiter",): "_launch_begleiter",
        ("--print-prompt", "--begleiter"): None,
        ("--quickie",): "_launch_quickie",
        ("--print-prompt", "--quickie"): None,
        ("--gaertner",): "_launch_gaertner",
        ("--gaertner", a): "_launch_gaertner",
        ("--print-prompt", "--gaertner"): None,
        ("--dry-run",): None,           # inspection flags: no menu, no launch
        ("--print-prompt",): None,
        ("--register", str(tmp_path / "Neu")): None,
    }
    for argv, expect in cases.items():
        called.clear()
        monkeypatch.setattr(sys, "argv", ["studyclaude", *argv])
        assert m.main() == 0, argv
        assert called == ([expect] if expect else []), argv
    assert (tmp_path / "Neu" / "CLAUDE.md").is_file()       # --register scaffolded
    assert str(tmp_path / "Neu") in m._load_registry()["workspaces"]


def test_launches_exec_one_interactive_session(tmp_path, monkeypatch, spawns):
    """Course and Quickie both exec ONE interactive claude (no -p)
    on the tier model at medium effort, in the right directory — and an
    inline launch never falls through into the konsole spawn (it once opened
    three real windows from this suite)."""
    a, b = _courses(tmp_path, "Physik", "Spanisch")
    m.launch(a, inline=True)
    data = {"workspaces": [a]}
    m._launch_quickie(data, inline=True)
    data["workspaces"].append(b)
    m._launch_quickie(data, inline=True)
    assert len(spawns["exec"]) == 3
    for argv in spawns["exec"]:
        assert argv[0] == "claude" and "-p" not in argv
        assert argv[argv.index("--model") + 1] == "opus"
        assert argv[argv.index("--effort") + 1] == "medium"
    assert m._load_registry()["quickies"]["total"] == 2      # launches are counted
    m._set_model("sonnet")                                   # the pin is what launches
    argv = m._build_argv(a)
    assert argv[argv.index("--model") + 1] == "sonnet"
    m._set_model(m.DEFAULT_MODEL)
    # cwd: course → itself; multi-course quickie / Begleiter → common root; sole quickie → course
    spawns["exec"].clear()
    cwds = []
    for call in (lambda: m.launch(a, inline=True),
                 lambda: m._launch_quickie({"workspaces": [a, b]}, inline=True),
                 lambda: m._launch_quickie({"workspaces": [a]}, inline=True),
                 lambda: m._launch_begleiter({"workspaces": [a, b]}, inline=True)):
        call(); cwds.append(spawns["cwd"])
    assert cwds == [a, str(tmp_path), a, str(tmp_path)]
    assert "-p" not in spawns["exec"][-1]
    # the desktop-icon route (inline=False) spawns konsole with the same argv
    spawns["allow_popen"] = True
    m.launch(a)
    assert spawns["popen"][-1][:2] == ["konsole", "--workdir"] and "claude" in spawns["popen"][-1]


def test_gaertner_sees_every_course_and_keeps_no_state(tmp_path, spawns):
    """The Gärtner starts at the common root with every course's dossier, names
    the focus, and neither registers a focus path nor counts anything."""
    a, b, loose = _courses(tmp_path, "Physik", "Spanisch", "Alt")
    m._register_workspace(a); m._register_workspace(b)
    m._launch_gaertner(m._load_registry(), [b, loose], inline=True)
    assert len(spawns["exec"]) == 1 and spawns["cwd"] == str(tmp_path)
    opening = spawns["exec"][0][-1]
    assert "-p" not in spawns["exec"][0] and a in opening and loose in opening
    assert opening.index(b) < opening.index("<dossiers>")      # b is named as the focus
    assert m.opening_message_gaertner([a, b], []).count(a) == 1  # no focus, no focus list
    reg = m._load_registry()
    assert loose not in reg["workspaces"] and "quickies" not in reg


# ---- prompts: orient, never re-encode the procedure ----------------------

def test_prompts_orient_without_reencoding_the_procedure(tmp_path, monkeypatch):
    """The SSoT boundary: every prompt points at the workspace CLAUDE.md and
    carries the launcher-owned bits (date, active medium's mechanics — only
    that one's), but no sheet names and no Häppchen file list."""
    a, b = _courses(tmp_path, "Physik", "Spanisch")
    Path(a, "todo.md").write_text("Fortschritt: 2/30 Häppchen\n", encoding="utf-8")
    monkeypatch.setenv("STUDYCLAUDE_MEDIUM", "board")
    texts = {
        "course": m._assemble_prompt(a) + m.opening_message(a),
        "quickie": m._assemble_quickie_prompt([a, b]) + m.opening_message_quickie([a, b], 3, 7),
        "quickie-solo": m._assemble_quickie_prompt([a]) + m.opening_message_quickie([a], 0, 1),
        "gaertner": m._assemble_gaertner_prompt() + m.opening_message_gaertner([a, b], [b]),
        "begleiter": m._assemble_begleiter_prompt() + m.opening_message_begleiter([a, b]),
    }
    for name, text in texts.items():
        assert "CLAUDE.md" in text and "Heute:" in text, name
        assert "Bedienung des Boards" in text and ".xopp" not in text, name   # active medium only
        for forbidden in ("cheatsheet", "basics.pdf", "haeppchen_"):
            assert forbidden not in text, (name, forbidden)
        assert "Fortschritt: x/y Häppchen" in text, name    # the menu reads that line
        assert "model: sonnet" in text and "model: opus" not in text, name   # subagents
    # the Kursübersicht: the launcher only says "build it first" and names the
    # template the section is copied from — the content stays in the course CLAUDE.md
    template_path = str(m.TEMPLATE_DIR / "LERNLOOP_TEMPLATE.md")
    assert "Kursübersicht" in texts["course"] and template_path in texts["course"]
    assert "Kursübersicht" in texts["begleiter"] and "Übersicht: fehlt" in texts["begleiter"]
    assert template_path not in texts["quickie"]              # never the Quickie's job
    Path(a, "todo.md").write_text("Fortschritt: 2/30 Häppchen\nÜbersicht: bestätigt 2026-09-02\n",
                                  encoding="utf-8")
    assert template_path not in m.opening_message(a)         # confirmed: no nudge
    assert "Übersicht: bestätigt 2026-09-02" in m.opening_message_begleiter([a, b])
    assert "Kursübersicht" in m.opening_message_onboard()
    assert "Bedienung des Boards" in m._assemble_onboard_prompt()   # builds it in the medium
    # the Blatt-Finder: the launcher names the tool, the step itself is the
    # course CLAUDE.md's and the tool's --help
    finder = m.TEMPLATE_DIR / "tools" / "blatt_finder.py"
    assert finder.is_file() and "blatt_finder.py" in TEMPLATE
    assert str(finder) in texts["course"] and str(finder) in texts["begleiter"]
    assert str(finder) not in texts["quickie"]
    # the Visualisierung row: the launcher asks for it while it is missing,
    # what a level means is the medium file's (here the board's)
    assert "„Visualisierung“" in texts["course"] and "„Visualisierung“" in texts["begleiter"]
    for name in ("course", "begleiter"):                     # the pointer in _LOOP_BRIEF
        assert "entscheidest du beim Bauen" in texts[name], name
    assert "„Visualisierung“" not in texts["quickie"]
    assert "Visualisierung: fehlt" in texts["begleiter"]
    assert "Bild zu jedem Inhalts-Tab" in texts["course"]
    Path(a, "CLAUDE.md").write_text("| **Visualisierung** | viel |\n", encoding="utf-8")
    assert "„Visualisierung“" not in m.opening_message(a)    # set: no nudge …
    assert "entscheidest du beim Bauen" in m.opening_message(a)   # … but the pointer stays
    assert a in texts["course"]
    assert (a in texts["begleiter"] and b in texts["begleiter"]
            and "2/30" in texts["begleiter"])                # dossiers
    assert a in texts["quickie"] and b in texts["quickie"]
    assert b not in texts["quickie-solo"]                    # one course: no pick
    assert a in texts["gaertner"] and "2/30" in texts["gaertner"]         # every dossier
    assert "--unregister" in texts["gaertner"] and "registry.json" not in texts["gaertner"]
    monkeypatch.setenv("STUDYCLAUDE_MEDIUM", "xournalpp")
    assert ".xopp" in m._assemble_prompt(a) and "get_canvas" not in m._assemble_prompt(a)


def test_blatt_finder_marks_exactly_the_mapped_spans(tmp_path):
    """The finder's promise: a question highlights the mapped text and nothing
    else, a snippet that cuts a formula or left the sheet is refused, and the
    page builds without KaTeX."""
    spec = importlib.util.spec_from_file_location(
        "studyclaude_blatt_finder", HERE / "templates" / "tools" / "blatt_finder.py")
    bf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bf)
    sheet = tmp_path / "blatt.md"
    sheet.write_text("**Leitung**\n- Ohm $U = RI$; Leistung $P = UI$ ==nicht $I^2$ vergessen==\n"
                     "- Drude: freies Elektronengas\n", encoding="utf-8")
    lines = sheet.read_text(encoding="utf-8").split("\n")
    data = [
        {"nr": 1, "frage": "Ohmsches Gesetz?", "abdeckung": "voll", "hinweis": "U = RI ablesen.",
         "treffer": [{"zeile": 2, "text": "Ohm $U = RI$"}]},
        {"nr": 2, "frage": "Postulate?", "abdeckung": "keine", "hinweis": "Steht nicht drauf.", "treffer": []},
    ]
    assert bf.check(lines, data) == []
    cut = [dict(data[0], treffer=[{"zeile": 2, "text": "Ohm $U = R"}])]
    gone = [dict(data[0], treffer=[{"zeile": 3, "text": "Ohm $U = RI$"}])]
    assert "zerschneidet" in bf.check(lines, cut)[0]
    assert "enthält nicht" in bf.check(lines, gone)[0]          # strict: the named line
    out = tmp_path / "finder.html"
    stats = bf.build(str(sheet), gone + data[1:], str(out), "Test", katex_dir=False)
    assert stats["voll"] == 1 and stats["keine"] == 1           # build follows a moved line
    page = out.read_text(encoding="utf-8")
    q = json.loads(page.split("const Q = ", 1)[1].split(";\n", 1)[0])
    assert len(q[0]["segs"]) == 1 and q[1]["segs"] == []
    marked = page.split(f'data-s="{q[0]["segs"][0]}">', 1)[1].split("</span>", 1)[0]
    assert marked.startswith("Ohm ") and "Leistung" not in marked
    with pytest.raises(SystemExit):                              # snippet left the sheet
        bf.build(str(sheet), [dict(data[0], treffer=[{"zeile": 2, "text": "Hall"}])], str(out), katex_dir=False)


def test_catchall_rule_only_with_a_marked_registered_course(tmp_path):
    """The maths-gap rule reaches every session once a registered course
    carries the inbox file — found through the registry, never by a path."""
    a, b = _courses(tmp_path, "Physik", "Mathe")
    for ws in (a, b):
        m._register_workspace(ws)
    assert "<mathe_luecken>" not in m._prompt_common()          # nobody marked
    Path(b, m.CATCHALL_INBOX).write_text("# Lücken-Eingang\n", encoding="utf-8")
    assert m._catchall_workspace() == b
    for text in (m._assemble_prompt(a), m._assemble_begleiter_prompt(), m._assemble_gaertner_prompt()):
        assert "<mathe_luecken>" in text and str(Path(b, m.CATCHALL_INBOX)) in text
    m._unregister_workspace(b)
    assert "<mathe_luecken>" not in m._prompt_common()          # unregistered: silent


def test_scaffold_never_overwrites_and_teaches_the_conventions(tmp_path):
    ws = tmp_path / "NeuesFach"; ws.mkdir()
    (ws / "todo.md").write_text("KEEP ME", encoding="utf-8")
    m._scaffold_workspace(str(ws))
    assert (ws / "CLAUDE.md").is_file() and (ws / "fehlermuster.md").is_file()
    assert (ws / "Personalisierte_Übungen").is_dir()
    assert (ws / "todo.md").read_text(encoding="utf-8") == "KEEP ME"
    fresh = tmp_path / "Leer"; fresh.mkdir()
    m._scaffold_workspace(str(fresh))
    assert "Fortschritt: 0/?" in (fresh / "todo.md").read_text(encoding="utf-8")
    assert m.course_overview(str(fresh)) is None              # placeholder does not count
    assert "Fortschritt: x/y Häppchen" in TEMPLATE
    assert "Kursübersicht" in TEMPLATE and "Übersicht: bestätigt" in TEMPLATE
    # the medium is the launcher's: the template points at the system prompt
    # and carries no per-medium mechanics
    assert "Systemprompt" in TEMPLATE
    assert "get_canvas" not in TEMPLATE and "xournalpp <datei>" not in TEMPLATE


def test_course_overview_parses_never_judges(tmp_path):
    """The Übersicht line is bookkeeping the workspace session writes once the
    user has confirmed the overview in the medium; the launcher reads it and
    fails into silence like the Fortschritt line."""
    (a,) = _courses(tmp_path, "Physik")
    todo = Path(a, "todo.md")
    assert m.course_overview(str(tmp_path / "weg")) is None   # no file
    todo.write_text("Fortschritt: 1/9 Häppchen\n", encoding="utf-8")
    assert m.course_overview(a) is None                       # no line
    todo.write_text("Übersicht: fehlt  *(…)*\n", encoding="utf-8")
    assert m.course_overview(a) is None                       # the scaffolded placeholder
    assert m._overview_suffix(a) == "   · ohne Übersicht"
    assert "Übersicht: fehlt" in m._course_dossier(a)
    todo.write_text("Übersicht: gebaut 2026-01-04, Bestätigung ausstehend (Board x, Tab 0)\n", encoding="utf-8")
    assert m.course_overview(a) is None and m.course_overview_built(a)   # built ≠ confirmed
    assert m._overview_suffix(a) == "   · Übersicht unbestätigt"
    assert "Kursübersicht" in m.opening_message(a)              # still nudged: confirm, not build
    todo.write_text("**Uebersicht: bestätigt 2026-01-05**\n", encoding="utf-8")
    assert m.course_overview(a) == "2026-01-05"
    assert m._overview_suffix(a) == ""
    assert "Übersicht: bestätigt 2026-01-05" in m._course_dossier(a)


def test_visual_level_parses_never_judges(tmp_path):
    """The Visualisierung row is the course's; the launcher reads the level
    from the Eckdaten table and fails into silence. The stamped placeholder
    and a prose mention do not count."""
    (a,) = _courses(tmp_path, "Physik")
    claude = Path(a, "CLAUDE.md")
    assert m.course_visual_level(str(tmp_path / "weg")) is None   # no file
    m._scaffold_workspace(str(tmp_path / "Neu"))
    assert m.course_visual_level(str(tmp_path / "Neu")) is None   # template placeholder
    claude.write_text("Visualisierung: viel wäre schön\n", encoding="utf-8")
    assert m.course_visual_level(a) is None                       # prose, not the row
    assert "Visualisierung: fehlt" in m._course_dossier(a)
    claude.write_text("| **Fach** | Physik |\n| **Visualisierung** | Mittel; Optik viel |\n",
                      encoding="utf-8")
    assert m.course_visual_level(a) == "mittel"
    assert "Visualisierung: mittel" in m._course_dossier(a)


# ---- parsers of files the launcher does not own --------------------------

def test_course_progress_parses_or_stays_silent(tmp_path):
    ws = tmp_path / "Kurs"; ws.mkdir()
    todo = ws / "todo.md"
    todo.write_text("# todo\n\n**Fortschritt:** 7/24 Häppchen (Stand 2026-08-20)\n", encoding="utf-8")
    assert m.course_progress(str(ws)) == (7, 24)
    assert "7/24 Häppchen" in m._progress_suffix(str(ws))
    todo.write_text("Fortschritt: 20/20 Häppchen\n", encoding="utf-8")
    assert "bereit" in m._progress_suffix(str(ws))
    todo.write_text("Fortschritt: 0/? Häppchen\n", encoding="utf-8")   # scaffold placeholder
    assert m.course_progress(str(ws)) is None and m._progress_suffix(str(ws)) == ""
    assert m.course_progress(str(tmp_path / "missing")) is None


def test_course_progress_takes_the_last_line_and_ignores_prose(tmp_path):
    """Both todo.md shapes are legal: one maintained line, or a per-session log
    that appends one. The last line wins — the first one is the course's opening
    number. A prose mention inside a bullet is not a bookkeeping line."""
    ws = tmp_path / "Kurs"; ws.mkdir()
    todo = ws / "todo.md"
    todo.write_text(
        "# todo\n\n## Stand 2026-08-01\n**Fortschritt: 11/25 Häppchen**\n\n"
        "## Stand 2026-09-07\n- Levels unverändert, Fortschritt bleibt 22/28.\n"
        "**Fortschritt: 23/29 Häppchen**\n",
        encoding="utf-8")
    assert m.course_progress(str(ws)) == (23, 29)
    # the indented prose line alone is no bookkeeping line at all
    todo.write_text("# todo\n- kein Häppchen, Fortschritt bleibt 6/26.\n", encoding="utf-8")
    assert m.course_progress(str(ws)) is None


def test_dossier_extracts_facts_and_drops_missing_pieces(tmp_path):
    ws = tmp_path / "Physik"; ws.mkdir()
    (ws / "CLAUDE.md").write_text(
        "## Themenkarte\n\n| # | Thema | Falle |\n|---|---|---|\n"
        "| 1 | Coulomb | Vorzeichen |\n| 2 | Gauß | Symmetrie |\n\n## Sonst\n",
        encoding="utf-8")
    (ws / "todo.md").write_text(
        "# todo\nFortschritt: 2/26 Häppchen\n\n## Stand\n"
        "- 2026-08-13 — Workspace angelegt.\n- 2026-08-20 — **H01** neu ausgeliefert.\n"
        "- Altklausur 27.07.10 durchgesehen\n",   # dotted date without a 4-digit year: not a log line
        encoding="utf-8")
    (ws / "fehlermuster.md").write_text(
        "# Fehlermuster\n\n> Nach JEDEM Review …\n\n- Vorzeichen bei Feldrichtung vergessen\n",
        encoding="utf-8")
    ex = ws / "Personalisierte_Übungen"; ex.mkdir()
    for name in ("haeppchen_01.tex", "haeppchen_01.pdf", "haeppchen_01_reviewt.png",
                 "haeppchen_02.tex", "rechenblatt_01.xopp"):
        (ex / name).touch()
    assert m._themenkarte_size(str(ws)) == 2
    assert m._haeppchen_counts(str(ws)) == (2, 1)
    assert m._top_fehlermuster(str(ws)) == "Vorzeichen bei Feldrichtung vergessen"
    # the ranked shape: the first body row of the Aktive-Muster table wins, header
    # and separator rows are skipped, and the scaffolded empty table yields None
    (ws / "fehlermuster.md").write_text(
        "# Fehlermuster\n\n## Aktive Muster\n\n| # | Muster | Belege | Stand |\n|---|---|---|---|\n"
        "| 6 | Präfix in die falsche Richtung | 9 | offen |\n| 1 | SI vor dem Einsetzen | 1 | repariert |\n\n"
        "## Belege\n\n- irgendein alter Bullet\n", encoding="utf-8")
    assert m._top_fehlermuster(str(ws)) == "Präfix in die falsche Richtung"
    (ws / "fehlermuster.md").write_text(
        "# Fehlermuster\n\n## Aktive Muster\n\n| # | Muster | Belege | Stand |\n|---|---|---|---|\n\n## Belege\n",
        encoding="utf-8")
    assert m._top_fehlermuster(str(ws)) is None
    (ws / "fehlermuster.md").write_text(
        "# Fehlermuster\n\n> Nach JEDEM Review …\n\n- Vorzeichen bei Feldrichtung vergessen\n",
        encoding="utf-8")
    assert "H01 neu ausgeliefert" in m._todo_stand(str(ws))
    dossier = m._course_dossier(str(ws))
    for expected in ("2/26 Häppchen", "2 Themen", "2 Häppchen, 1 reviewt", "Vorzeichen", "H01"):
        assert expected in dossier
    bare = tmp_path / "Leer"; bare.mkdir()
    dossier = m._course_dossier(str(bare))
    assert "unbekannt" in dossier
    for absent in ("Themenkarte", "Übungsdateien", "Top-Fehlermuster", "Zuletzt"):
        assert absent not in dossier


_EXAM_TABLE = """# Prüfungen

| Prüf-Nr | Fach | Form | ECTS | Termin | Prüfer |
|---|---|---|---:|---|---|
| 57561 | ML in Materialwissenschaften | **schriftlich** — Mail 23.07. | 7,5 | **Fr 31.07. 09:00** (90 min) | Pelz |
| 57121 | Math für Data Science 2 | Klausur | 8 | ~~Mo 20.07.~~ **nicht bestanden** | Kronz |
| 50641 | Math. Grundlagen ML | mündlich | 5 | **abgelegt Fr 24.07. — bestanden 1,7** | Pelz |
| 12345 | Lineare Algebra I | Klausur | 2,5 | **Mi 16.09. 09:00** | Musterfrau |
| 23456 | Thermodynamik | Klausur | 5 | **Fr 25.09.** | Mustermann |
| 34567 | Analysis | Klausur | 5 | **Mo 12.01. 08:00** | Mustermann |

| Modul-Nr | Modul | ECTS | Note |
|---|---|---:|---|
| 65711 | Mathematik für Data Science 1 | 10 | 3,0 |
"""


def test_wochenplan_reaches_the_course_pick(tmp_path):
    """No wochenplan.md next to the registry means no block; with one, the
    multi-course Quickie gets it verbatim with today's weekday."""
    a, b = str(tmp_path / "A"), str(tmp_path / "B")
    for ws in (a, b):
        Path(ws).mkdir()
    assert m._wochenplan_block() == ""
    (tmp_path / "wochenplan.md").write_text("Mo–Fr: A\nSa–So: B\n", encoding="utf-8")
    block = m._wochenplan_block(now=datetime.datetime(2026, 10, 3, 7, 0))
    assert block.startswith("Heute ist Samstag, 03.10.2026.")
    assert "<wochenplan>\nMo–Fr: A\nSa–So: B\n</wochenplan>" in block
    assert "<wochenplan>" in m.opening_message_quickie([a, b], 1, 2)
    assert "<wochenplan>" not in m.opening_message_quickie([a], 1, 2)  # one course: no pick


def test_begleiter_starts_from_the_clock_and_the_profile_tab(tmp_path):
    """The Begleiter's opening carries the launch time in German whatever the
    locale, points at the profile tab on the board (the profile is never in
    the repo), sees every dossier, and gets the Wochenplan for free time only —
    the course pick is one of its options, not its first job."""
    a, b = _courses(tmp_path, "Physik", "Spanisch")
    now = datetime.datetime(2026, 10, 19, 14, 5)
    text = m.opening_message_begleiter([a, b], now=now)
    assert "Montag, 19.10.2026, 14:05 Uhr" in text
    assert f"Tab „{m.PROFILE_TAB}“ auf einem meiner Boards" in text
    assert a in text and b in text and "<dossiers>" in text
    assert "<wochenplan>" not in text
    (tmp_path / "wochenplan.md").write_text("Mo–Fr: Physik\n", encoding="utf-8")
    text = m.opening_message_begleiter([a, b], now=now)
    assert "<wochenplan>\nMo–Fr: Physik\n</wochenplan>" in text
    assert "Wähle den Kurs nach meinem Wochenplan" not in text
    assert "`date`" in m._assemble_begleiter_prompt()      # the opening's time goes stale


def test_exam_table_parsing(tmp_path, monkeypatch):
    """Future rows only, soonest first, weekday re-derived, bare dates roll
    into next year, settled rows (~~, abgelegt) and tables without a date
    column are ignored — and no configured file means no banner, no error."""
    assert m.upcoming_exams() == []
    assert "keine Klausurtabelle konfiguriert" in m._exam_prompt_lines()
    f = tmp_path / "Pruefungen.md"
    f.write_text(_EXAM_TABLE, encoding="utf-8")
    monkeypatch.setenv("STUDYCLAUDE_EXAMS", str(f))
    rows = m.upcoming_exams(now=datetime.datetime(2026, 8, 13, 10, 0))
    assert [r[2] for r in rows] == ["Lineare Algebra I", "Thermodynamik", "Analysis"]
    assert rows[0][:2] == (34, "Mi 16.09. 09:00")
    assert rows[1][1] == "Fr 25.09."                          # no time in the cell
    assert rows[2][1] == "Di 12.01. 08:00" and rows[2][0] > 100   # January = next year
    f.write_text("| Fach | Termin |\n|---|---|\n| X | garbage |\n", encoding="utf-8")
    assert m.upcoming_exams() == []                           # fail into silence
    assert m._exam_prompt_lines() == f"- kein kommender Termin mit Datum in {f}"


class MockCursesScreen:
    """Mock curses standard screen for simulating terminal input and rendering."""

    def __init__(
        self,
        simulated_key_sequence: list[int],
        simulated_terminal_dimensions: tuple[int, int] = (24, 80),
    ) -> None:
        """Initialize mock curses screen with simulated input keys and geometry.

        Args:
            simulated_key_sequence: Queue of key codes to return on getch() calls.
            simulated_terminal_dimensions: Simulated (height, width) screen dimensions.
        """
        self._key_sequence: list[int] = list(simulated_key_sequence)
        self._terminal_dimensions: tuple[int, int] = simulated_terminal_dimensions
        self.rendered_lines: list[tuple[int, int, str, int]] = []
        self.erased: bool = False
        self.refreshed: bool = False
        self.timeout_delay: int | None = None

    def erase(self) -> None:
        """Simulate screen erase."""
        self.erased = True

    def refresh(self) -> None:
        """Simulate screen refresh."""
        self.refreshed = True

    def getmaxyx(self) -> tuple[int, int]:
        """Simulate returning terminal dimensions.

        Returns:
            Tuple of (height, width).
        """
        return self._terminal_dimensions

    def addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        """Record rendered text line.

        Args:
            y: Vertical row coordinate.
            x: Horizontal column coordinate.
            text: Text to display.
            attr: Display attributes bitmask.
        """
        self.rendered_lines.append((y, x, text, attr))

    def getch(self) -> int:
        """Return next key code from the simulated queue.

        Returns:
            Integer key code, or -1 if queue is exhausted.
        """
        if self._key_sequence:
            return self._key_sequence.pop(0)
        return -1

    def timeout(self, delay: int) -> None:
        """Record timeout setting.

        Args:
            delay: Delay in milliseconds, or -1 for blocking.
        """
        self.timeout_delay = delay


def test_model_selection_menu_navigation_and_selection():
    """Verify navigating down to next model and selecting with Enter key."""
    palette: dict[str, int] = {"title": 0, "path": 0, "foot": 0, "tutor": 0, "star": 0}
    models: list[str] = ["opus", "sonnet", "fable"]
    # Start at 'opus', press KEY_DOWN, then Enter (10)
    screen = MockCursesScreen([curses.KEY_DOWN, 10])
    selected_model = m._model_selection_menu(screen, palette, models, "opus")
    assert selected_model == "sonnet"


def test_model_selection_menu_wraps_around_with_up_arrow():
    """Verify up arrow from top of list wraps around to the last model."""
    palette: dict[str, int] = {"title": 0, "path": 0, "foot": 0, "tutor": 0, "star": 0}
    models: list[str] = ["opus", "sonnet", "fable"]
    # Start at 'opus' (index 0), press KEY_UP, then Enter (13)
    screen = MockCursesScreen([curses.KEY_UP, 13])
    selected_model = m._model_selection_menu(screen, palette, models, "opus")
    assert selected_model == "fable"


def test_model_selection_menu_cancellation_preserves_current_model():
    """Verify cancellation via Esc, Backspace, Left arrow, or q preserves current model."""
    palette: dict[str, int] = {"title": 0, "path": 0, "foot": 0, "tutor": 0, "star": 0}
    models: list[str] = ["opus", "sonnet", "fable"]

    # Cancel with Escape (27)
    esc_screen = MockCursesScreen([curses.KEY_DOWN, 27])
    assert m._model_selection_menu(esc_screen, palette, models, "opus") == "opus"

    # Cancel with Backspace (127)
    bs_screen = MockCursesScreen([curses.KEY_DOWN, 127])
    assert m._model_selection_menu(bs_screen, palette, models, "opus") == "opus"

    # Cancel with Left Arrow (curses.KEY_LEFT)
    left_screen = MockCursesScreen([curses.KEY_DOWN, curses.KEY_LEFT])
    assert m._model_selection_menu(left_screen, palette, models, "opus") == "opus"

    # Cancel with 'q'
    q_screen = MockCursesScreen([curses.KEY_DOWN, ord("q")])
    assert m._model_selection_menu(q_screen, palette, models, "opus") == "opus"


def test_model_selection_menu_empty_list():
    """Verify empty model list returns current model immediately."""
    palette: dict[str, int] = {"title": 0, "path": 0, "foot": 0, "tutor": 0, "star": 0}
    screen = MockCursesScreen([10])
    assert m._model_selection_menu(screen, palette, [], "opus") == "opus"


def test_model_selection_menu_scrolling_on_compact_terminal():
    """Verify scrolling logic and indicators on a terminal smaller than model count."""
    palette: dict[str, int] = {"title": 0, "path": 0, "foot": 0, "tutor": 0, "star": 0}
    models: list[str] = [f"model_{idx}" for idx in range(20)]
    # Start at model_15 on a 10-line terminal, press Enter
    screen = MockCursesScreen([10], simulated_terminal_dimensions=(10, 80))
    selected = m._model_selection_menu(screen, palette, models, "model_15")
    assert selected == "model_15"
    # Upper scroll indicator should have been drawn
    has_upper_indicator = any("weitere Modelle oben" in text for _, _, text, _ in screen.rendered_lines)
    assert has_upper_indicator



def test_menu_countdown_survives_a_window_resize(monkeypatch, tmp_path):
    """A resize (Konsole maximising right after the autostart) is no keypress:
    the countdown still starts the default. Before the fix it read the `q`."""
    import collections
    monkeypatch.setattr(curses, "curs_set", lambda _: None)
    monkeypatch.setattr(m, "_init_colors", lambda: collections.defaultdict(int))
    monkeypatch.setattr(m, "_available_models", lambda: ["opus"])
    monkeypatch.setattr(m, "_exam_banner_lines", lambda: [])
    clock = iter([0.0, 0.0])
    monkeypatch.setattr(m.time, "monotonic", lambda: next(clock, 11.0))
    data = {"workspaces": [str(tmp_path)], "default": m._BEGLEITER_SENTINEL}
    screen = MockCursesScreen([curses.KEY_RESIZE, ord("q")])
    assert m._menu_loop(screen, data) == ("begleiter", None)


# --- the course list is shared with the sibling tool ---------------------------

def test_courses_are_shared_through_one_file(tmp_path, monkeypatch):
    import json, main
    monkeypatch.delenv("STUDYCLAUDE_REGISTRY", raising=False)
    monkeypatch.setenv("STUDY_COURSES", str(tmp_path / "courses.json"))
    monkeypatch.setattr(main, "SCRIPT_DIR", tmp_path / "tool")
    (tmp_path / "tool" / "data").mkdir(parents=True)
    legacy = tmp_path / "tool" / "data" / "registry.json"
    legacy.write_text(json.dumps({"workspaces": ["/a"], "model": "x"}), encoding="utf-8")
    assert main._load_registry()["workspaces"] == ["/a"]          # migrated
    (tmp_path / "courses.json").write_text(
        json.dumps({"workspaces": ["/a", "/b"]}), encoding="utf-8")  # the sibling added one
    assert main._load_registry()["workspaces"] == ["/a", "/b"]
    data = main._load_registry()
    data["workspaces"].remove("/a")
    main._save_registry(data)
    assert json.loads((tmp_path / "courses.json").read_text())["workspaces"] == ["/b"]
    own = json.loads(legacy.read_text())
    assert own["workspaces"] == [] and own["model"] == "x"        # settings stay local
    assert main._load_registry()["workspaces"] == ["/b"]          # no resurrection
