# studyclaude — maintainer notes

User-facing docs are in [`README.md`](README.md). This file holds the design
decisions and invariants an agent working on the code needs.

Extracted from the author's `tools` monorepo (2026-08-10) into a standalone MIT
repo, following the same path `bloggen` took. It has **no** dependency on
`_shared` any more: the tier logic was vendored into `tier.py`, and the installer
import falls back gracefully when `cli_tools_kit` is absent.

Renamed from **lernclaude** on 2026-10-18 (user). The alias `lernen` became
`studyclaude`, the variables `LERNCLAUDE_*` became `STUDYCLAUDE_*`, and the
GitHub repos `AutomatedAlchemy/lernclaude` and `lernclaude-fau` became
`studyclaude` and `studyclaude-fau`. There is no fallback for the old names.
The German terms inside the tool (Lern-Loop, Häppchen, „lass uns lernen“) stay.

## The SSoT boundary (the load-bearing invariant)

The study procedure — *which* sheets to open, the Häppchen rotation, the topic
order — lives canonically in each **workspace's** `CLAUDE.md`. This launcher must
never re-encode it.

`test_studyclaude.py` enforces this: the prompt-assembly tests assert that concrete
take-in-sheet filenames never appear in the assembled prompt. If you find yourself
adding a file list to `_assemble_prompt`, the change belongs in the workspace
template instead.

The mechanism is just Claude Code's own behaviour: we launch with the working
directory set to the workspace, so `<workspace>/CLAUDE.md` and its parents load
automatically. The launcher only orients the session — today's date, the workspace
path, a pointer to the procedure.

## No hardcoded personal paths

There is deliberately no built-in default workspace. `_resolve_workspace(None)`
returns `None` on a fresh install, and the caller routes that to the menu.

`test_no_personal_paths_and_no_builtin_default` greps `main.py` for personal path
fragments and fails if any reappear. That test earned its keep during extraction —
it caught the onboarding prompt still naming the author's study folders after the
constants had been cleaned up.

## The exam banner reads a file it does not own

The menu header (`upcoming_exams` → `_exam_banner_lines`) parses a *foreign*
markdown file — for the author, a life-admin SSoT that gets edited by hand for
its own reasons. Two consequences the code must keep honouring:

- **Never write to it, never require a shape.** The parser skips any table that
  lacks a date *and* a label header, so an unrelated table in the same file (a
  Notenübersicht, say) is silently ignored rather than mis-read.
- **Fail into silence, not into an error.** Missing path, unreadable file,
  garbage dates — every path returns `[]` and the menu just has no banner. This
  is a launcher; it must not refuse to open a course because a notes file moved.

The path itself is configuration (`STUDYCLAUDE_EXAMS`, or `exams_file` in the
registry), never a constant — `test_no_personal_paths_and_no_builtin_default` greps
`main.py` for personal path fragments and this feature is exactly the kind that
would tempt one back in.

Rows the user has already dealt with are filtered by `_DONE_MARKERS` (`~~`,
`abgelegt`, `bestanden`, `Rücktritt`, …) rather than by a status column, because
the source table records outcomes inline in the date cell.

## Course progress: parse, never judge

The menu's `· x/y Häppchen` per course comes from one line the *workspace
session* maintains in that course's `todo.md` (`Fortschritt: 7/24 Häppchen`).
The split honours the SSoT boundary: how many Häppchen remain until
"klausurbereit" is a tutoring judgment, so the workspace owns the number and
re-estimates `y` after every review; the launcher (`course_progress`) only
parses and displays it. Same failure contract as the exam banner: missing file,
missing line, the scaffolded `0/?` placeholder — all return `None` and the row
just has no suffix. The convention is taught in three places that must stay in
sync: the template (todo.md bullet + review step), the scaffolded `todo.md`
skeleton, and `opening_message` (so pre-existing workspaces adopt it without
manual edits).

**The last matching line wins, and the match is anchored to a line start.** Two
todo.md shapes grew in the wild and both are legal: one line kept up to date at
the top, or a per-session log that appends a fresh one. Reading the first match
showed a course's opening number for weeks (Ableitungen sat at `11/25` in the
menu while its log said `23/28`). Anchoring keeps a prose mention inside an
indented bullet — "Fortschritt bleibt 6/26", Experimentalphysik_II — from being
read as the bookkeeping line. `test_course_progress_takes_the_last_line_and_
ignores_prose` pins both halves. The Übersicht parsers stay first-match on
purpose: confirmation is a latch, any occurrence means confirmed.

## Kursübersicht: presence in the launcher, content in the template, look in the medium

Every course gets an overview before its first Häppchen — the contract between
tutor and learner about what the exam, the topics and the materials cover. It
is board-native by design: the learner only sees the working medium, never the
files on the studyclaude host, so the overview is a medium object (board: Tab 0
with the materials attached via `upload_asset`; xournalpp: a reading PDF), not
a markdown file. The split follows the Fortschritt pattern:

- **Content** is `templates/LERNLOOP_TEMPLATE.md` §Kursübersicht (Prüfung →
  Themen → Materialien → Vereinbarung) and, once stamped, the course CLAUDE.md.
  It must not migrate into `main.py` — `test_prompts_orient_without_reencoding_
  the_procedure` only allows the section name and the template path there.
- **Look** is `templates/media/<name>.md` (block order, the single
  „Gelesen & einverstanden" submit, `wait_url`, the backfill of an old Tab 0).
- **Presence** is the launcher's: `course_overview` parses one line the session
  writes to `todo.md` after the user confirmed (`Übersicht: bestätigt
  YYYY-MM-DD`), same fail-into-silence contract as `course_progress`; the
  scaffolded `Übersicht: fehlt` placeholder deliberately does not match. The
  in-between line `Übersicht: gebaut …, Bestätigung ausstehend` (written when
  the overview was built outside a tutoring session) is recognised by
  `course_overview_built`: still unconfirmed, but the row says
  `· Übersicht unbestätigt` and the brief tells the session to ask for the
  confirmation instead of building again.
  Consumers: `_overview_suffix` (menu row `· ohne Übersicht`, `--list`), the
  dossier line, and `_overview_brief` — appended to `opening_message`
  only while the line is missing, always to `opening_message_begleiter` (the
  course is chosen inside the session), never to the Quickie.

Backfill for pre-existing courses is the same mechanism: the brief tells the
session to copy the §Kursübersicht section from the template into a course
CLAUDE.md that lacks it, build the overview, get it confirmed, write the line.
Nothing in the seven existing workspaces was edited by hand.

## Dossiers: facts for the sessions that work across courses

The Begleiter, the multi-course Quickie and the Gärtner start at
`_tutor_workdir` (the courses' common root, `$HOME` fallback), so no course
CLAUDE.md auto-loads; the session reads the chosen course's CLAUDE.md itself,
and its system prompt says so. Their opening carries `_course_dossier` per
course plus `_exam_prompt_lines`. The dossier is everything *mechanically*
extractable from the files every course is guaranteed to have: the Fortschritt
line and file mtimes, the Themenkarte row count (CLAUDE.md), created/reviewed
Häppchen counted from the exercise folder, the top row of the `## Aktive Muster`
table in fehlermuster.md (or the first entry of an older log-only file; dominant
by convention), and the newest dated todo.md line (dotted dates need a 4-digit
year — "27.07.10" is an old exam's filename). Deliberately NO file excerpts:
the session has tools and reads the candidates' todo.md itself (inline excerpts
were only ever needed by the removed tool-less `claude -p` pass, and had
ballooned the opening to ~15k chars; facts keep it ~4k). Each extractor fails
into silence — a missing piece drops its line. The openings wrap what they
inject in `<klausuren>` and `<dossiers>` and say in one line that the tags hold
data, not instructions: the exam labels and the todo.md excerpts come from
hand-edited files the launcher does not own. Which course comes first is the
model's judgment, not a launcher-side heuristic (SSoT boundary).

Tutors Choice (`--tutor`, a pick-the-course-then-tutor-it session) and the
Meta-Häppchen (`--meta`, one Häppchen in a target course shaped by source
courses) were removed on 2026-10-19 (user). The Begleiter covers the course
pick. A `__TUTOR__` or `__META__` default left in a synced registry counts as
unset (`_ensure_default`, `_default_workspace`), `--set-default tutor|meta`
answers "unverändert" instead of registering `<cwd>/tutor` as a course, and a
leftover registry key `meta` is ignored.

**Wochenplan.** An optional free-text `wochenplan.md` next to the registry
(`data/`, personal, gitignored) says which courses fit which weekdays.
`_wochenplan_block` passes it verbatim in `<wochenplan>` tags, with today's
weekday, into the multi-course Quickie pick; the Begleiter gets the bare text
(see below). No file or an empty file adds nothing. The launcher never parses
the plan; the Gärtner keeps it current when courses are added or removed.

Registration never claims the default — an unset default resolves in
`_ensure_default` to the Begleiter as soon as there is one course.
`_default_workspace()` (scripts, `--dry-run`/`--print-prompt`) returns only a
registered course, never a sentinel; otherwise it falls back to the first
course. The palette key `C["tutor"]` (always-bold magenta) kept its name from
the retired row; it colours the switch values and the model-menu cursor.

## Begleiter: the clock first, the profile on the board

The default persona (user, 2026-10-18). `_launch_begleiter` runs one session at
`_tutor_workdir`, like the Gärtner, so it can work in whichever course the hour
asks for. The opening (`opening_message_begleiter`) carries the launch time
(`_now_line`, German weekday from `_WEEKDAYS_LONG_DE`, never `%A`, which follows
the locale), the exams, the Wochenplan as text for free time (`_wochenplan_text`,
without the "Wähle den Kurs" sentence: the pick is one of its options, not its
first job), every dossier, and the loop, finder and overview briefs for when it
becomes a Häppchen. The system prompt tells it to run `date` before any statement
about time, because the opening's time is stale minutes after launch.

What is due now is the model's judgment. The launcher neither reads the
timetable nor maps a lecture to a course: timetables come in too many shapes (a
calendar, a campo export, a board tab), and which course bundles which lecture
is a fact of the course, not of this tool.

**The profile is on the board, not in the repo.** Who the user is and where the
timetable and the semester material are is a tab `PROFILE_TAB` („Profil“) on any
of the user's boards (since 21.10.2026 no fixed board name; usually the semester
overview board), found by the tab name. The repo is public and
`test_no_personal_paths_and_no_builtin_default` keeps personal data out of
`main.py`; the board is the user's own and reaches every agent on the account.
The prompt names only the board and the tab, never how the MCP tools work
(same boundary as `templates/media/board.md`). Without a board tool (fauclaude,
Xournal++ users) or without the tab, the session says so in one sentence and asks
in chat. The board with the profile is no course board; course work goes on the
course's own board, as the medium file says.

It is a row and a sentinel (`_BEGLEITER_SENTINEL`, in `_SENTINELS`): a valid
default (`d`, `--set-default begleiter`), shown with ≥1 course, no registry
state of its own. Added after the 2026-10-02 freeze of v1.0.

## Quickie: the habit entry, not a second loop

The menu's second row (`_QUICKIE_SENTINEL`, shown with ≥1 course) and `--quickie`
route to `_launch_quickie`: one interactive session like a course launch
(tier model, `_exec_or_konsole`, dossiers when there are several courses, the
course's own CLAUDE.md read for the mechanics), but the brief
(`opening_message_quickie`) is scaled down to ONE five-minute Häppchen and
tuned for a quick win and a one-line „Noch eins?“. It carries
`upcoming_exams()` (shared `_exam_prompt_lines`) — with
several courses the deadlines steer the pick, with one they steer the topic. The point is the habit —
lowering the threshold to start and making a second round the easy next step —
so the brief forbids preamble, long analysis and closing lectures. It still
respects the SSoT boundary: no file lists, the course CLAUDE.md owns the
mechanics; the Quickie only says "scale it to one Häppchen". With one course
the session starts inside it (CLAUDE.md auto-loads); with several it starts at
the common root like the Begleiter.

The streak (`registry["quickies"]`: `last`, `streak`, `total`) is launcher
state, written by `_record_quickie` at launch time — a launch counts, whether
or not a Häppchen got finished; judging that would put a tutoring decision in
the launcher. `_quickie_stats` reports the streak only while it is alive (last
Quickie today or yesterday), and both are pure functions of a `today` string so
the tests never depend on the clock. The row suffix (`_quickie_suffix`) and the
opening's counter line are the only consumers. The sentinel is a valid
`default` (`d`, `--set-default quickie`) and never leaks out of
`_default_workspace`. `_SENTINELS` is the single list of menu sentinels.

## Gärtner: maintenance by chat, plan before change

`g` in the menu (and `--gaertner [PFAD…]`) routes to `_launch_gaertner`: one
session at `_tutor_workdir`, same launch mechanics as the Begleiter, but no study
brief. The user says in chat which courses to clean up, merge or revise; which
course needs what is theirs to say, so the opening only carries every dossier,
the exams and the focus (the courses checked in the multiselect when `g` was
pressed, or the CLI paths) and asks. The system prompt holds the rules the
user chose on 2026-09-22: a plan and an OK before anything that moves, deletes
or merges files or changes the course list; the list changes only through
`--register` / `--unregister` (the registry file is never edited by the
session); `_archiv/` over deletion. It also tells the session which lines the
menu parses, so a merge leaves one valid `Fortschritt:` line and resets the
overview to `Übersicht: fehlt`.

It is a key, not a row: no sentinel, not a valid default, no registry state,
no streak. A CLI focus path that is not registered is shown but not
registered, because registering is itself a change that needs the plan.

The multiselect exists for the focus and is menu state only (`multi`,
`checked` in `_menu_loop`): Space opens it with the cursor row checked, Space
toggles, `g` returns `("gaertner", checked)`, Enter/Esc/`q` leave it. Inside
the mode the other keys (`d`, `x`, the switches) are ignored on purpose, and
the sentinel rows are greyed out and unselectable. `curses.set_escdelay(25)`
makes Esc immediate; it is wrapped in try because it is Python ≥ 3.9 only.
Until 2026-10-19 the same multiselect also picked the Meta-Häppchen's target
and sources.

## The medium switch: choice in the launcher, mechanics in launcher templates

The working medium (Xournal++ vs Tutor Board) is deliberately NOT part of the
SSoT in the course docs — it is cross-course infrastructure. Two launcher-owned
pieces: the *choice* (registry key `medium`, menu key `m`, `--set-medium`,
`STUDYCLAUDE_MEDIUM` override, default `xournalpp`) and the *mechanics*
(`templates/media/<name>.md`, appended to the system prompt by
`_assemble_prompt` — only the active medium's file, fail-into-silence when
missing). `_prompt_common` emits three tagged parts — `<orientierung>`,
`<heute>` and `<medium_mechanik name="…">` — so the session can tell the
launcher's orientation from the medium file it carries. Every launch gets it,
onboarding included: onboarding builds the first Kursübersicht in the medium
(`_assemble_onboard_prompt`; until 2026-10-08 it had its own prompt without
the medium). Course CLAUDE.mds and the workspace template carry no medium
machinery; they point at "Systemprompt" (the last asserts of
`test_scaffold_never_overwrites_and_teaches_the_conventions` pin this). Escape hatches the prompt grants: mid-session verbal
switching (next Häppchen in the new medium), and a course CLAUDE.md may pin a
fixed medium, which then wins — the board-native language courses rely on that.

**A medium file carries what the loop wants from the medium, never how the medium's
tools work.** For the Tutor Board the MCP server sends its own instructions and
tool descriptions on every connection, and those are maintained with the server.
Any copy of them in `templates/media/board.md` is older than the server by
construction and wins over it in practice, because it sits in the system prompt
as an order. That is how a `kinds:["click","submit"]` line from an August
workaround made a session deaf to the board chat on 2026-09-05, and earlier a
"`select_board` does not exist" note made sessions build blindly.
`test_board_template_carries_no_mcp_manual` pins the boundary: a server fact that
seems missing is added to the server's descriptions — the Tutor Board server is
a private repo of the author, agent docs at
<https://beta.probable.work/agent.md> — not to the template.

## Catch-all for maths gaps: a marker file, one rule in the prompt

One course may collect the maths gaps the other courses find. It marks itself
with `luecken_eingang.md` (`CATCHALL_INBOX`); `_catchall_workspace` takes the
first registered course that has it, so the path comes from the registry and
`test_no_personal_paths_and_no_builtin_default` stays green. `_prompt_common`
then adds a `<mathe_luecken>` block to every session: book a pure calculation
gap there as an appended line, format per the file's header. The launcher owns
only that routing sentence. How the catch-all works through its inbox is its
own CLAUDE.md's business, like any other procedure. Added 2026-09-24 so the
rule lives in one place instead of a copied paragraph in every course.

## Blatt-Finder: a tool in `templates/tools/`, three places that name it

`templates/tools/blatt_finder.py` builds a page that shows a course's take-in
sheet beside its question pool and highlights, per question, the sheet text that
helps answer it (first built 2026-10-01 for Funktionsmaterialien, made the
standard preparation step the same day). The split follows the Kursübersicht:

- **When** is the template's §Situative Dateien entry (own sheet allowed, a
  question pool exists, sheet has a first complete version; rebuild after
  every sheet change).
- **How** is the tool's own docstring, printed by `--help`: sheet format,
  `fragen.json`, the per-subagent mapping files, `check`, `build`. Keep the
  procedure there and nowhere else — the template and the launcher only point.
- **Where** is `_finder_brief`, appended to `opening_message` and
  `opening_message_begleiter`. A stamped course CLAUDE.md cannot know this repo's
  path, so the launcher names it. The same sentence is the backfill for older
  courses whose CLAUDE.md lacks the entry. Never the Quickie's.

The tool is stdlib Python. KaTeX (via `node`) is optional and only renders the
formulas; without it the page keeps the formula source. `check` is strict about
the line number (subagents must cite the right line), `build` searches the whole
sheet when a line moved and aborts when a snippet is gone.
`test_blatt_finder_marks_exactly_the_mapped_spans` pins both.

## Autostart belongs to the installer, not to this file

Login autostart is cli-tools-kit's, and the whole implementation here is one
`--advertise` field: `default_autostart: True`, which pre-ticks the installer's
Auto-Start checkbox. Do not add a flag, a registry key or a `.desktop` writer
for it — that was tried on 2026-09-14 and reverted the same day.

The kit's contract for an `Icon` tool (`gui_installer.enable_autostart`) is a
**symlink** at `~/.config/autostart/<desktop_file>` pointing at the installed
`~/.local/share/applications/<desktop_file>`. One file, one name, and the
installer's remove path calls `disable_autostart` for you. A hand-written second
`.desktop` is a parallel mechanism the installer cannot see, toggle or clean up
— the same wart the umbrella CLAUDE.md records for studon-client's `~/.bashrc`
function, which is not a precedent to copy.

Because the symlink runs the icon's argument-less `Exec`, login gets `main()` →
`run_menu()`: the konsole re-exec for the missing TTY, the 10s countdown to the
default, any key to cancel. That is the point — an autostart that dropped
straight into a session would hand a fresh login a Claude process with no way
out, so nothing here should ever point autostart at `--quickie` or a course.

## Removing a course: unregister, optionally archive

`x` in the menu asks first. `j` only unregisters and leaves the folder alone.
`a` also moves the folder to `<parent>/_archiv/<name>` (`_archive_workspace`),
with a date suffix when that name is taken, so nothing is ever overwritten.
The move comes first and the course is unregistered only if it worked. A failed
move stays in the dialog with the error. The move is refused when another
registered course lies inside the folder. `--unregister` stays registry-only,
because the Gärtner prompt relies on "trägt nur aus, löscht nichts".

## Tool-local state

The registry lives at `data/registry.json`, anchored to `SCRIPT_DIR` — **not**
`~/.config`. Rationale: this is run from a checkout that is shared or replicated
across several machines, and per-host config silently diverges (a course list once
showed three courses on one host and one on another). Keeping it beside the tool
makes the course list travel with the checkout.

Consequences to preserve:
- The path takes a `STUDYCLAUDE_REGISTRY` override so tests can redirect it to
  `tmp_path`. Every registry test relies on this.
- It is gitignored. It's mutable runtime state; tracking it would leave
  `git status` permanently dirty and invite merge conflicts.
- Because the file is shared, `default` is shared too. Two machines writing it in
  the same sync window can produce a `*.sync-conflict-*` copy — harmless, delete
  the loser.

## One engine, many icons

The engine is global (this one `main.py`) so loop improvements propagate to every
subject. The entry points are specific: `--install <ws> --name X` generates a thin
per-workspace `.desktop` icon whose `Exec` passes that workspace. Each exam gets a
one-click resume icon that doubles as a passive deadline nudge, with no code
duplication.

## Model and effort

Launches use the registry keys `model` and `effort` directly, defaulting to
**opus** at **medium** effort (`DEFAULT_MODEL` / `DEFAULT_EFFORT` in `main.py`).
Medium is a deliberate ceiling, not an oversight: this is interactive tutoring,
where latency is felt more than extra depth helps.

Subagents never run on Opus (user, 2026-10-08). `_prompt_common` tells every
session to pass `model: sonnet`, or `model: haiku` for simple work, on each
Agent call. The two places that start subagents by design name the model
themselves: the explainer clip in `templates/media/board.md` and step 3 of
`blatt_finder.py --help`. An explicit model is needed because a subagent
without one inherits the session's model, which defaults to opus.

The pick is used exactly as set — there is no tier detection and no clamp
(user, 2026-09-16). `auto`, the `STUDYCLAUDE_MODEL` / `STUDYCLAUDE_EFFORT`
overrides and the tier lookup they fed were all removed then; `tier.py` is
retained but no longer imported. They are launcher-level switches shaped exactly like the medium
switch (menu keys `m` / `o` / `e`, `--set-medium` / `--set-model` /
`--set-effort`, env override on top),
and `_select_model` / `_select_effort` are the model readers. An explicit pick
bypasses `tier_effort` on purpose: choosing `high` in the menu on a Max host must
give high, or the switch would be a lie. The menu label for the medium row reads
"Userspace"; the registry key, the templates and the code all still say `medium`.

The `o` cycle lists the Anthropic models (`_ANTHROPIC_MODELS`), and
`_available_models` appends whatever the registry currently holds so a pinned
value stays visible. `_current_model` accepts only a known name: a registry
written by an older build may still carry a model this one does not know, and
that value falls back to `DEFAULT_MODEL` instead of reaching a launch.

## Commits

- **Pick the branch before the first edit.** The checkout sits on `fau`, but
  only the FAU layer belongs there: the fauclaude backend, the `fau:` models,
  FAU names and URLs. Everything else goes on `main`, the public base version.
  On 2026-09-22 two sessions committed general work on `fau` because this rule
  was missing here, and it had to be ported by hand.
- **Commit general work on `main` without switching the shared checkout:**
  `git worktree add <scratch>/wt main`, edit, test and commit there, then
  `git worktree remove`. Bring it into `fau` with `git merge main` in the
  checkout. Merge, never rebase: `fau` is published on `fau/main`, and a rebase
  rewrites those commits.
- **A general change that calls FAU-layer code** (`_backend_for_model`,
  `_discover_fau_models`, the fauclaude test) is split: the general part on
  `main`, the FAU addition as its own commit on `fau` after the merge.
- **Check before you report:** `git log --oneline --no-merges main..fau` lists
  only FAU-layer commits.
- **German summaries, as they are now**, and one concern per commit. Commit by
  pathspec (`git commit -m "…" -- a b`) so an unrelated dirty file does not ride
  along; `git add` only new paths.
- **Check `git status` before your first edit.** A dirty tree is someone else's
  unfinished work. Commit it as its own commit first, then start yours — once the
  edits are mixed the two can no longer be separated by pathspec.
- **Tests pass before the commit.** `python3 -m pytest -q` green, and docs go in
  the same commit as the code they describe (README + this file + the mode
  tables). Never commit `data/registry.json`: it is gitignored, mutable per-host
  state.
- **Never push or open a PR on your own.** Publishing is the maintainer's call;
  say the work is committed, name the SHA, and stop.
- **Never rewrite at or below the published branch.** Pushed is permanent; fix
  forward with a normal commit.

## Layout

| File | Role |
|------|------|
| `main.py` | launcher, menu, registry, install/remove |
| `tier.py` | vendored subscription-tier → model/effort mapping; **vendored, unused** — no longer imported |
| `templates/LERNLOOP_TEMPLATE.md` | the Lern-Loop procedure stamped into new workspaces |
| `templates/media/*.md` | per-medium mechanics, appended to the system prompt |
| `templates/tools/blatt_finder.py` | Blatt-Finder: validates a question→sheet mapping and builds the page; `--help` is the procedure |
| `test_studyclaude.py` | offline tests — behaviour only, no network, no launch |
| `requirements.txt` | empty by design; stdlib only |

## Gotchas

- **`--advertise` must answer before any heavy import.** The installer times out
  after 5 s. The check sits above the `import argparse` block on purpose — don't
  move it.
- **`SCRIPT_DIR` is spliced onto `sys.path` at module level** so a sibling import
  resolves both when `main.py` is run directly and when the tests load it by file
  location. Nothing imports `tier` any more, but the splice is what makes that
  pattern work; keep it if a sibling module comes back.
- **`.desktop` files hold absolute paths.** Moving or renaming this directory means
  `--remove` then `--install` from the new location.
- **The nvm PATH fix in `_launch_env()` is not optional.** A `.desktop` launch
  inherits the graphical session's PATH, which lacks the nvm bin dir where `claude`
  and `node` live — without it the icon opens a konsole that immediately closes.
- **Permission mode is left at Claude Code's default.** The session's work — read
  files, open PDFs — is read-only or user-approved.

## Tests

```bash
python3 -m pytest -q     # offline
```

Tests load `main.py` under a unique module name via `importlib` rather than
`import main`, a habit from the monorepo where sibling tools would collide in
`sys.modules`. Harmless here; keep it if this ever gets vendored back.
