# openstudy — an AI exam-prep tutor for any model

A stdlib-only launcher that starts an AI coding agent inside an exam-prep folder,
so that folder's `CLAUDE.md` drives the study loop: open your reference sheets and
the newest problem set, then feed you one bite-sized exercise at a time,
personalised from your actual mistakes. The launcher encodes no study procedure:
about 2000 lines that pick a folder, pick a model and send a "let's study"
trigger, so you improve the loop by editing a workspace's `CLAUDE.md`, not this
code. Tested on Linux with KDE.

**Start with `openstudy`.** It runs the session in [opencode](https://opencode.ai),
which works with almost any model provider, so you choose what the tutor costs:

- **Free:** opencode offers free models of its own. Their names end in `-free`
  (`opencode models` lists the current ones), and the menu offers them directly.
- **Local:** a model on your own machine through LM Studio, Ollama or any
  OpenAI-compatible server, configured once in opencode.
- **Paid:** Claude, GPT, Gemini and the others, with your own API key or
  subscription (`opencode auth`).

Out of the box `openstudy` uses the model already set in your opencode config, so
a working opencode is a working tutor. Switch models in the menu at any time.

**`studyclaude`** is the same tool running in [Claude Code](https://claude.com/claude-code)
instead. Use it if you have a Claude subscription and want your claude.ai
connectors (Google Calendar) without extra setup; it runs Claude models only.

Both commands are one program (`main.py --engine opencode|claude`) with the same
Lern-Loop, menu and courses. The courses, the default course, the exam file and the
Quickie streak are shared; model, effort and working medium are kept per engine.
openstudy used to be its own repo (archived since the merge on 2026-10-31);
studyclaude was formerly **lernclaude** (renamed 2026-10-18).

> **The tool speaks German** — prompts, workspace template, menu. The loop itself
> is language-agnostic: [docs/workspace.md](docs/workspace.md#using-it-in-another-language).

## Requirements

- [opencode](https://opencode.ai) on your `PATH` (or in `~/.opencode/bin`) for `openstudy`;
  optionally [Claude Code](https://claude.com/claude-code) for `studyclaude`
- Python 3.9+, **standard library only** (`requirements.txt` is empty)
- `konsole` (KDE) for the windowed launch; without it, it runs in your terminal

## Install

```bash
curl -fsSL https://opencode.ai/install | bash   # opencode, if you don't have it
git clone https://github.com/AutomatedAlchemy/studyclaude.git
cd studyclaude
python3 main.py           # menu (openstudy); first entry is "neuen Kurs anlegen"
python3 main.py --install # desktop icons + the `openstudy` and `studyclaude` aliases
python3 main.py --engine claude   # the same with Claude Code
```

Without `--engine`, the launcher runs opencode. It uses Claude Code only when
opencode is not installed and Claude Code is; `STUDY_ENGINE` sets the default
explicitly.

*neuen Kurs anlegen* starts an agent session that searches your filesystem with
you, agrees on a course folder, scaffolds and registers it, then reads your
material and fills in exam date, topic map and starting points. `--install` needs
[`cli-tools-kit`](https://github.com/Probst1nator/cli-tools-kit); without it it
says what is missing, and the tool still runs by path.

## Models

| Engine | Choices | Default |
|---|---|---|
| `openstudy` | `opencode-Standard` (whatever your opencode config uses), Opus / Sonnet / Fable, every free model, and with `O` every model `opencode models` lists | opencode-Standard |
| `studyclaude` | Opus / Sonnet / Fable | Opus |

`o` cycles through the short list, `O` opens the full one, and `--set-model` takes
the same names or any `provider/model` id, e.g.
`openstudy --set-model opencode/<name>-free`. Effort (`e`, `--set-effort`) applies
to the Claude models; with any other model opencode uses the model's own setting.
Claude Opus at `medium` effort is the deliberate choice for `studyclaude`: the loop
is interactive tutoring, where latency is felt more than reasoning depth helps.

Differences of the opencode engine: opencode has no `--append-system-prompt`, so the
launcher writes the prompt to `$XDG_RUNTIME_DIR/study/prompt-<hash>.md` and passes it,
with the course's `CLAUDE.md`, as `instructions`; subagents run on the session's model.
The **Tutor Board** is registered for you in every session of both tools
(`https://board.probable.work/mcp`, override with `STUDY_BOARD_MCP_URL`); nothing is
written to your opencode or Claude Code config. The engine signs in by itself with a
redirect to your computer, so the board's sign-in page needs one click on **Allow** when
your browser is signed in to the board, and takes a board link otherwise. `studyclaude`
hides a claude.ai connector for the board in its sessions, so the tools do not show twice. Google Calendar is not connected (Claude Code gets it
as a claude.ai connector; opencode needs its own MCP entry).

### First start: log in to the Tutor Board

The board needs a Tutor Board account (see [Media](#media)). On the first `openstudy`
start, type `/mcps` in the session, choose `tutor-board` and log in with the link from
your board's share menu. Without a board account, use the Xournal++ medium; it works
without any of this. `opencode mcp list` and `opencode mcp auth` do not show the entry,
because they ask opencode's shared background service, which does not see the
launcher's config; log in through `/mcps`.

## Usage

The examples say `openstudy`; every one works the same with `studyclaude`.

A bare `openstudy` opens a curses picker of your registered courses, exam banner
above, progress note per row. The top row is the Begleiter, the default persona.
`↑`/`↓` move · `Enter` starts · `Space` marks courses for the
Gärtner · `g` Gärtner · `m` medium · `o`/`O` model · `e` effort · `d`
default · `x` removes the course from the menu, and on request moves its folder
into `_archiv/` beside it · `q` quits. Untouched for ten seconds it autostarts your default.

| Launch | What it does |
|---|---|
| `openstudy <workspace>` | Run that course's Lern-Loop; `--menu` forces the menu instead |
| `openstudy --begleiter` | Begleiter (the default): one session over all courses checks the timetable for the current time and helps with what is due — a lecture running now, starting soon or just ended, a deadline, or a Häppchen in free time |
| `openstudy --quickie` | One short, winnable Häppchen (about 5 min); counts a daily streak |
| `openstudy --gaertner [PFAD…]` | Gärtner: a maintenance session, no studying. You tell it in chat which courses to clean up, merge or revise; the paths are its focus |
| `openstudy --wochenvorbereitung woche\|morgen\|beginn` | Unattended: builds and updates the appointment tabs of the week from the timetable and the synced material, no chat; for timers, with `--dry-run` to inspect ([docs/modes.md § Wochenvorbereitung](docs/modes.md#wochenvorbereitung)) |

Mechanics of the three modes, the streak and the dossiers: [docs/modes.md](docs/modes.md).
The Begleiter reads who you are and where your timetable lives from a tab
„Profil“ on one of your Tutor Boards (any board, found by the tab name); without it, it asks you in chat
([docs/modes.md § Begleiter](docs/modes.md#begleiter)).
To steer which course the Begleiter and the Quickie pick on which weekday, put a
plain-text rule into `data/wochenplan.md` ([docs/modes.md § Wochenplan](docs/modes.md#wochenplan)).
Other flags: `--list` (`*` marks the default), `--set-default`, `--mode-done`, `--set-medium`,
`--set-model`, `--set-effort`, `--add` (guided onboarding), `--register`,
`--unregister`, `--print-prompt`, `--dry-run`, `--install [ws]`, `--remove [ws]`.

**Starting on login:** no flag. Tick **Auto-Start** in the
`cli-tools-kit` installer (pre-ticked for `openstudy` via `default_autostart`); it symlinks the
icon into `~/.config/autostart` and clears it on removal. What starts is the menu
with its countdown, so you can always get out.

## Media

Sessions work either in **Xournal++ + Firefox** (the default: exercise PDF in the
browser, calculations on a separate `.xopp` sheet) or on a **Tutor Board** (a web
whiteboard, one tab per exercise, needs an account on the author's invite-only
service). Switch with `m`, `openstudy --set-medium xournalpp|board` or
`STUDY_MEDIUM`; verbal mid-session switch and per-course pin in
[docs/workspace.md](docs/workspace.md#the-medium-switch). How many sketches and
clips a course gets is one Eckdaten row in its `CLAUDE.md`, see
[docs/workspace.md](docs/workspace.md#visuals-per-course).

**Tutor Board** lives at <https://board.probable.work>. An agent connects as an
MCP (Model Context Protocol) connector, `https://board.probable.work/mcp`, with
OAuth 2.1 + PKCE (Proof Key for Code Exchange); live docs at
<https://board.probable.work/setup.md> and <https://board.probable.work/agent.md>.
This tool ships no MCP client and no credentials — those come from your own
Claude Code or opencode MCP config.

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
| `STUDY_ENGINE` | Default engine when `--engine` is not given (`opencode` \| `claude`; unset: opencode, or claude when only Claude Code is installed) |
| `STUDY_REGISTRY` | Path to the registry (default: `./data/registry.json`) |
| `STUDY_DEFAULT_WORKSPACE` | Override the registered default for one launch |
| `STUDY_ROOT` | The study root on this host: the course list lives in `<root>/.study/` and onboarding starts searching there (else `host.json`, else `$HOME` for onboarding only) |
| `STUDY_CONFIG_DIR` | Where `host.json` lives (default `~/.config/study`) |
| `STUDY_EXAMS` | Markdown file with your exam-date table (banner off when unset; registry key `exams_file` does the same) |
| `STUDY_MEDIUM` | Override the working medium for one launch (`xournalpp` \| `board`) |
| `STUDY_FEED_DIR` | Scroller feed folder that takes quiz cards from every course (rule off when unset or missing; registry key `feed_dir`, set with `--set-feed`; contract in `docs/feed_lernkarten.md`) |
| `STUDY_BOARD_MCP_URL` | Tutor Board MCP URL that both tools register (default `https://board.probable.work/mcp`) |

**Where things live.** The course list is `<study root>/.study/courses.json`, next to your
courses (versioned, one entry per course with a stable `id`, paths relative to the root).
The study root is per host: `STUDY_ROOT`, else `study --set-root DIR` (stored in
`~/.config/study/host.json`, `%APPDATA%\study\host.json` on Windows). Put the root in a synced
folder and the list is the same on every machine. Everything else (default course, model,
effort, medium, exam file, Quickie streak) is in the gitignored `data/registry.json`; model,
effort and medium are stored per engine under `engines.<engine>`, and the default is a course
`id`.

Courses are added and removed as operations under a lock, so two menus open at once do not
undo each other. A Syncthing conflict copy of the list (`courses.sync-conflict-*.json`) is
shown in the menu header and by `--list`; it is not merged. If the list cannot be read, the
menu opens empty, course changes are refused and nothing is overwritten.

**Syncing the list.** The atomic write leaves a short-lived `.study/courses.json.<pid>.tmp`
beside the list, so the sync tool should ignore it on every host (the lock file is per host and
lives in the config dir, not beside the list). For Syncthing, add to the folder's `.stignore`
(per host, not synced): `(?d)**/.study/*.tmp`. A registry on another host finds the list through
its `root_hint`; without one (a fresh host) the menu header says to run `study --set-root`.

The first start migrates the older layouts once: a registry with top-level
`model`/`effort`/`medium` (studyclaude), the old openstudy registry,
`~/.config/study-courses.json`, and the course list in the registry. The root is guessed from
your courses (their common folder) and printed. The registry is copied to
`registry.json.pre-courses` first. After that, a course you remove stays removed.

Model and effort picks ([Models](#models)) are used as chosen and persist in the
registry, per engine. Under `studyclaude`, subagents a session starts (explainer
clips, the Blatt-Finder mapping) run on Sonnet, or Haiku for simple work, never on
Opus; under `openstudy` they run on the session's model.

A workspace itself is a normal folder with your material plus a `CLAUDE.md`.
Onboarding stamps a minimal skeleton (`CLAUDE.md`, `todo.md`, `fehlermuster.md`,
`Personalisierte_Übungen/`) and never overwrites an existing file. Layout, the
overview contract and adding a course: [docs/workspace.md](docs/workspace.md).

## Tests and license

```bash
python3 -m pytest -q          # offline: no network, no launch
```

MIT — see [LICENSE](LICENSE).
