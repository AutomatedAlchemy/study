# study (studyclaude / openstudy)

A stdlib-only launcher that starts [Claude Code](https://claude.com/claude-code)
or [opencode](https://opencode.ai) inside an exam-prep folder, so that folder's `CLAUDE.md` drives the study loop:
open your reference sheets and the newest problem set, then feed you one
bite-sized exercise at a time, personalised from your actual mistakes. The
launcher encodes no study procedure: about 2000 lines that pick a folder, pick a
model and send a "let's study" trigger, so you improve the loop by editing a
workspace's `CLAUDE.md`, not this code. Tested on Linux with KDE.

**One tool, two commands.** `studyclaude` runs the session in Claude Code, `openstudy` in
opencode (`main.py --engine claude|opencode`). The Lern-Loop, menu and courses are the
same; only the launch and these settings differ per engine: model, effort and working
medium. The courses, the default course, the exam file and the Quickie streak are
shared. openstudy used to be its own repo (now archived); studyclaude was formerly
**lernclaude** (renamed 2026-10-18).

Differences when the engine is opencode: no `--append-system-prompt`, so the launcher
writes the prompt to `$XDG_RUNTIME_DIR/study/prompt-<hash>.md` and passes it, with the
course's `CLAUDE.md`, as `instructions`; the **Tutor Board and Google Calendar are not
connected** (Claude Code gets them as claude.ai connectors, opencode needs its own MCP
entry), so use the Xournal++ medium there; subagents run on the session's model.

> **The tool speaks German** — prompts, workspace template, menu. The loop itself
> is language-agnostic: [docs/workspace.md](docs/workspace.md#using-it-in-another-language).

## Requirements

- [Claude Code](https://claude.com/claude-code) (for `studyclaude`) and/or [opencode](https://opencode.ai) (for `openstudy`) on your `PATH`
- Python 3.9+, **standard library only** (`requirements.txt` is empty)
- `konsole` (KDE) for the windowed launch; without it, it runs in your terminal

## Install

```bash
git clone https://github.com/AutomatedAlchemy/studyclaude.git
cd studyclaude
python3 main.py          # menu; first entry is "neuen Kurs anlegen"
python3 main.py --install # desktop icons + the `studyclaude` and `openstudy` aliases
python3 main.py --engine opencode   # run with opencode instead of Claude Code
```

*neuen Kurs anlegen* starts a Claude session that searches your filesystem with
you, agrees on a course folder, scaffolds and registers it, then reads your
material and fills in exam date, topic map and starting points. `--install` needs
[`cli-tools-kit`](https://github.com/Probst1nator/cli-tools-kit); without it it
says what is missing, and the tool still runs by path.

## Usage

A bare `studyclaude` opens a curses picker of your registered courses, exam banner
above, progress note per row. The top row is the Begleiter, the default persona.
`↑`/`↓` move · `Enter` starts · `Space` marks courses for the
Gärtner · `g` Gärtner · `m` medium · `o` model · `e` effort · `d`
default · `x` removes the course from the menu, and on request moves its folder
into `_archiv/` beside it · `q` quits. Untouched for ten seconds it autostarts your default.

| Launch | What it does |
|---|---|
| `studyclaude <workspace>` | Run that course's Lern-Loop; `--menu` forces the menu instead |
| `studyclaude --begleiter` | Begleiter (the default): one session over all courses checks the timetable for the current time and helps with what is due — a lecture running now, starting soon or just ended, a deadline, or a Häppchen in free time |
| `studyclaude --quickie` | One short, winnable Häppchen (about 5 min); counts a daily streak |
| `studyclaude --gaertner [PFAD…]` | Gärtner: a maintenance session, no studying. You tell it in chat which courses to clean up, merge or revise; the paths are its focus |

Mechanics of the three modes, the streak and the dossiers: [docs/modes.md](docs/modes.md).
The Begleiter reads who you are and where your timetable lives from a tab
„Profil“ on one of your Tutor Boards (any board, found by the tab name); without it, it asks you in chat
([docs/modes.md § Begleiter](docs/modes.md#begleiter)).
To steer which course the Begleiter and the Quickie pick on which weekday, put a
plain-text rule into `data/wochenplan.md` ([docs/modes.md § Wochenplan](docs/modes.md#wochenplan)).
Other flags: `--list` (`*` marks the default), `--set-default`, `--set-medium`,
`--set-model`, `--set-effort`, `--add` (guided onboarding), `--register`,
`--unregister`, `--print-prompt`, `--dry-run`, `--install [ws]`, `--remove [ws]`.

**Starting on login:** no `studyclaude` flag. Tick **Auto-Start** in the
`cli-tools-kit` installer (pre-ticked via `default_autostart`); it symlinks the
icon into `~/.config/autostart` and clears it on removal. What starts is the menu
with its countdown, so you can always get out.

## Media

Sessions work either in **Xournal++ + Firefox** (the default: exercise PDF in the
browser, calculations on a separate `.xopp` sheet) or on a **Tutor Board** (a web
whiteboard, one tab per exercise, needs an account on the author's invite-only
service). Switch with `m`, `studyclaude --set-medium xournalpp|board` or
`STUDY_MEDIUM`; verbal mid-session switch and per-course pin in
[docs/workspace.md](docs/workspace.md#the-medium-switch). How many sketches and
clips a course gets is one Eckdaten row in its `CLAUDE.md`, see
[docs/workspace.md](docs/workspace.md#visuals-per-course).

**Tutor Board** lives at <https://beta.probable.work>. An agent connects as an
MCP (Model Context Protocol) connector, `https://beta.probable.work/mcp`, with
OAuth 2.1 + PKCE (Proof Key for Code Exchange); live docs at
<https://beta.probable.work/setup.md> and <https://beta.probable.work/agent.md>.
studyclaude ships no MCP client and no credentials — those come from your own
Claude Code MCP config.

## The Blatt-Finder

For exams that allow a self-written sheet, the session builds a page that shows
the sheet next to every question of the catalogue and highlights the text that
answers the selected question. See
[`docs/workspace.md`](docs/workspace.md#the-blatt-finder).

## The exam banner

Set `STUDY_EXAMS` (or the registry key `"exams_file"`) to a markdown file of
exam dates and the menu lists the upcoming ones above the courses: soonest first,
days left, red inside three days, yellow inside ten. Unset, no banner. It reads
every table with **both** a date column (`Termin`, `Datum`, `Date`, `When`) and a
label column (`Fach`, `Kurs`, `Modul`, `Prüfung`, `Klausur`, `Subject`, `Course`,
`Exam`), so existing notes work as-is:

```markdown
| Prüf-Nr | Fach                  | ECTS | Termin              |
|---------|-----------------------|-----:|---------------------|
| 12345   | Lineare Algebra I     |  2,5 | **Mi 16.09. 09:00** |
| 23456   | Thermodynamik         |    5 | **Fr 25.09.**       |
```

The time is optional and a bare `12.01.` means the *next* 12 January. Rows past,
struck through (`~~…~~`) or marked `abgelegt` / `bestanden` / `Rücktritt` /
`entfällt` / `verschoben` / `TBD` drop out.

## A catch-all course for maths gaps

Put a file `luecken_eingang.md` into one registered course and that course
collects maths gaps from all others: every session's system prompt then tells it
to append a line there when a review finds a pure calculation error (powers,
units, fractions, signs …) rather than a subject error. The file's header states
the line format; the course's own `CLAUDE.md` says how it works through the
inbox. No file, no rule.

## Configuration

All optional.

Every variable is read as `STUDY_<NAME>`; the old `STUDYCLAUDE_<NAME>` and
`OPENSTUDY_<NAME>` still work as fallbacks for one release (`STUDY_*` wins).

| Variable | Effect |
|---|---|
| `STUDY_ENGINE` | Default engine when `--engine` is not given (`claude` \| `opencode`) |
| `STUDY_REGISTRY` | Path to the registry (default: `./data/registry.json`) |
| `STUDY_DEFAULT_WORKSPACE` | Override the registered default for one launch |
| `STUDY_ROOT` | Where guided onboarding starts searching (default: `$HOME`) |
| `STUDY_EXAMS` | Markdown file with your exam-date table (banner off when unset; registry key `exams_file` does the same) |
| `STUDY_MEDIUM` | Override the working medium for one launch (`xournalpp` \| `board`) |

Courses and settings live in the gitignored `data/registry.json`, in the tool's own
directory rather than `~/.config`, so a synced or shared checkout carries the same
course list on every machine. Model, effort and medium are stored per engine under
`engines.<engine>`. The first start migrates the two old layouts once: a registry with
top-level `model`/`effort`/`medium` (studyclaude), the old openstudy registry and
`~/.config/study-courses.json`. After that, a course you remove stays removed.

Sessions launch on **Opus at `medium` effort**. Medium is deliberate: the loop is
interactive tutoring, where latency is felt more than reasoning depth helps. `o`
(cycle) or `O` (interactive menu) and `e` in the menu (or `--set-model` /
`--set-effort`) change model (Opus | Sonnet | Fable) and effort (low | medium |
high | xhigh | max); the pick is used as chosen and persists in the registry.

Subagents a session starts (explainer clips, the Blatt-Finder mapping) run on
Sonnet, or Haiku for simple work, never on Opus.

A workspace itself is a normal folder with your material plus a `CLAUDE.md`.
Onboarding stamps a minimal skeleton (`CLAUDE.md`, `todo.md`, `fehlermuster.md`,
`Personalisierte_Übungen/`) and never overwrites an existing file. Layout, the
overview contract and adding a course: [docs/workspace.md](docs/workspace.md).

## Tests and license

```bash
python3 -m pytest -q          # offline: no network, no launch
```

MIT — see [LICENSE](LICENSE).
