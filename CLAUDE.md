# study (studyclaude + openstudy) — maintainer notes

Merged on 2026-10-31 from two repos: studyclaude (this one, with the history) and openstudy
(its opencode fork, created the same day by `git archive` at studyclaude 74b699b, then
archived). One `main.py`; `ENGINE` (`claude` | `opencode`, set by `--engine` or
`STUDY_ENGINE`) changes only `_backend_launch`, `_opening_args`, the subagent sentence in
`_prompt_common`, `_launch_env`, the names (`_command_name`) and which `engines.<engine>`
settings apply. The installer advertises two entries (`studyclaude`, `openstudy`), each
with `args` `--engine X`; `--install` / `--remove` handle both, because the kit no longer
passes an entry's args to the lifecycle commands (cli-tools-kit 602af85).

Facts tested 2026-10-31 on opencode v2.1.2: `instructions` in `OPENCODE_CONFIG_CONTENT`
loads both files (needs `--standalone`); CLAUDE.md in cwd is NOT loaded; the TUI has
`--prompt`. Tutor Board under opencode (2026-11-01): `_backend_launch` puts `mcp.servers.tutor-board`
(`type remote`, `url`; no `enabled`, the schema has only `disabled`; OAuth stays on) into
`OPENCODE_CONFIG_CONTENT`. The session server sees it (`needs_auth` until the user logs in
with `/mcps`); `opencode mcp list/auth` do NOT, they ask the shared background service. So
there is no launcher-side login step, only the hint text (`_board_login_hint`, in the
Begleiter opening and `_board_engine_rule`). Unknown: whether the `/mcps` login persists
across `--standalone` starts. The opencode wait mechanics (wait_url + background shell) are
in `_board_engine_rule`, not in `board.md`, whose test forbids "curl".
Not tested: the interactive TUI with `--prompt` and `-m …#effort` together.

**openstudy is the default (user, 2026-10-31)**, because opencode reaches any provider,
free and local models included. Without `--engine` and `STUDY_ENGINE`, `_initial_engine`
picks opencode, claude only on a host with Claude Code and no opencode; only the
openstudy entry has `default_autostart`. The README leads with openstudy. Models per
engine: claude takes the Anthropic aliases; opencode also takes `standard`
(`OPENCODE_STANDARD`, its default: the launch sets no model, so the user's opencode
config decides) and any `provider/model` id. `_available_models` adds the `*-free` ids
from `opencode models` to the `o` cycle, `full=True` (the `O` menu) every id. Effort
goes into the config as `variant` only for the Anthropic aliases, whose variants are
known.

Env: `STUDY_*` first, then `STUDYCLAUDE_*`, then `OPENSTUDY_*` (`_env`), for one release.
The sections below were written for studyclaude and still say Claude Code, `--append-system-prompt`
and `claude` where the opencode engine differs; read them for design, not for launch mechanics.
The old `tier.py` (Claude subscription tier lookup) is unused since 2026-09-16.

---

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

The FAU variant (branch `fau`, GitHub `studyclaude-fau`: the fauclaude backend
and the `fau:` models) was removed on 2026-10-29 (user): too specific. Its last
state is the local tag `archiv/fau`. The checkout sits on `main`.

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

The path itself is configuration (`STUDY_EXAMS`, or `exams_file` in the
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
(same boundary as `templates/media/board.md`). Without a board tool (Xournal++
users) or without the tab, the session says so in one sentence and asks
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
tuned for a quick win; after the correction the next Quickie is built ahead and
reached by a „Weiter → QKnn“ button, with no question. It carries
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

## Eigener Modus: the session asks, the launcher saves

A saved mode (`saved_modes` in the registry: name, text, course or None, plus the daily
fields) is created in a session, not typed into the menu (user, 2026-11-20). The mode row
and `s` return `("mode_new", (course, revise))`; `_launch_mode_builder` starts a session
whose opening (`_mode_builder_head`) is the interview: ask one open question as plain chat
text, with an example or two of an answer, and wait; then make proposals where the answer
leaves the direction open, follow up on what a later session could not decide itself,
write a name and an instruction for a session that does not know the conversation, get
the OK, save. The proposals and the answers offered with each follow-up come from what
the opening carries (dossiers, exams, medium, existing modes). The order is the user's
(2026-11-20): a bare open question was too little, proposals or a pick-list before they
had written anything were wrong; they speak first, in free text, and step 1 forbids the
question tool for that reason.
The session saves with `--save-mode NAME [--replaces OLD] [WORKSPACE]`, the instruction on
stdin (`_save_mode_cli`), because a multi-line text in an argv breaks on quoting. A same
name or `--replaces` replaces the mode in place and keeps its daily state. The builder gets
the same context as a custom session (time, exams, dossiers; one dossier for a course
mode), so it can run the new mode in the same session.

A registry written by the version published before 2026-11-20 holds `custom_modes` (the
last eight Aufträge as plain texts, shown as `↳` rows). `_saved_modes` reads them as modes
named after their first words while the registry has no `saved_modes`; the first change
writes `saved_modes` and the old key is not read again.

What the interview asks is in `_mode_builder_head` only. `s` on a `↳` row starts it with
`revise`: same steps, opening with what the mode does now and the question what should
change. The menu
has no editor for a mode's text any more, because the instructions are multi-line and
`_text_input` is one line; for the same reason `p` on a `↳` row adds one line for that
start instead of editing the text. `p` elsewhere is the one-off Auftrag (`--auftrag`).
`--dry-run` prints the launch for `--new-mode` and `--auftrag` (`_show_launch`).

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
`STUDY_MEDIUM` override, default `xournalpp`) and the *mechanics*
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
<https://board.probable.work/agent.md> — not to the template.

## Visuals: level in the course, forms in the medium

Added 2026-10-29 (user) after a transcript count: of 25 content tabs since
1 October, 4 got a clip without being asked, and no session ever said why it
skipped one. The old clip rule sat near the end of `board.md`, fired only
"after each new Häppchen tab" (the Begleiter's lecture tabs never counted),
knew only the narrated manim clip, and came after "hand over, then wait", so
the session went into `wait_url` and never came back to it.

The split follows the Kursübersicht:

- **Level** is the course's: the Eckdaten row `| **Visualisierung** | viel |
  mittel | wenig | keine; Ausnahmen |` in its CLAUDE.md. `course_visual_level`
  parses it, same fail-into-silence contract as `course_overview`; the
  template placeholder starts with « and does not match. The dossier says
  `Visualisierung: <Stufe>` or `Visualisierung: fehlt`.
- **Meaning and form** are the medium's: `board.md` §„Bild zu jedem
  Inhalts-Tab“ (a table level → sketch / clip, the build order, the `Bild: …`
  line in todo.md) and §„Clip“ (the manim mechanics); `xournalpp.md` has one
  bullet (a TikZ sketch in the PDF). The section sits right after „Blöcke
  bauen“ on purpose: deciding the picture is part of building the tab.
- **Presence** is the launcher's: `_visual_brief` asks the session to propose a
  level, ask once and write the row. It goes into `opening_message` only while
  the row is missing, always into `opening_message_begleiter`, never into the
  Quickie. The 10 existing courses were not edited by hand.

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

## Quiz cards for the scroller feed: a folder setting, one rule in the prompt

The scroller app Nachschub takes
quiz cards from every course. The feed folder comes from `STUDY_FEED_DIR` or the
registry key `feed_dir` (`--set-feed DIR`, `none` turns it off). When it is set and
exists on the host, `_prompt_common` adds a `<feed_lernkarten>` block: on arrival,
book the answers from `<feed>/lernkarten_antworten/<Kurs>.jsonl`. Live sessions write no
cards since 2026-11-26 (user): the unattended Wochenvorbereitung runs write them. The
card format is one card of the Tutor Board `cards` block plus `id`, `muster`,
`thema`, `hinweis`. Format, answer file, counting rule and the Nachschub side are in
`docs/feed_lernkarten.md`, which both sides follow. Counting rule chosen by the user:
a wrong answer is a Beleg, a right one may count as the §3b repair check, and
`Fortschritt:` never moves.

Comments and lecture prep (2026-11-12): the phone can comment on a card; the Nachschub job
writes it to `<feed>/lernkarten_kommentare/<Kurs>.jsonl`, and the brief tells the session to read
it after the answers (`Feed-Kommentare: gelesen bis …` in `todo.md`): feedback, never a Beleg.
The evening job also writes lecture-prep cards to `<feed>/lernkarten/VL-<Name>/` (`muster: null`,
`zweck: "vorbereitung"`, expire after the lecture). No study course is named `VL-*`, so no
session reads their answers or comments, and the "no card on material not yet taught" rule is
for session-written cards only. Both parts are in `docs/feed_lernkarten.md`.

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

Two places, by what they are:

- **The course list** is `<root>/.study/courses.json` (`courses.py`): beside the courses,
  versioned (`{"version": 1, "courses": [{"id", "name", "path", ...}]}`), `path` relative to
  the root or absolute, ids derived from the stored path (so two hosts that import the same
  list agree) and kept for good once written. The root is per host: `STUDY_ROOT`, else
  `~/.config/study/host.json` (`STUDY_CONFIG_DIR` moves it). Reason (user, 2026-10-31): the
  list must mean the same on every machine and travel with sync, which a per-host file in
  `~/.config` or a file beside the tool could not do for the two engines and for Windows.
- **Everything else** (`default`, `exams_file`, `quickies`, `meta`, and per engine under
  `engines.<engine>` `model`/`effort`/`medium`) is `data/registry.json`, anchored to
  `SCRIPT_DIR`. Gitignored runtime state.

Rules to keep:
- **Changes to the list are operations**: `courses.apply` locks (`fcntl`), re-reads, applies
  add/remove and writes. `_save_registry` turns what differs from the snapshot taken at load
  (`_courses_loaded`) into those operations; it never writes the whole list back. A stale
  menu therefore cannot bring back a course another process removed. After a write the
  caller's snapshot is updated, so saving one dict twice works.
- **In memory** `data["workspaces"]` is absolute paths and `data["default"]` a path or a mode
  sentinel, so every caller is unchanged; on disk `default` is a course id. Compare paths with
  `course_list.same_path`, never with `==`.
- **Never overwrite what cannot be read**: an unreadable registry is copied to
  `registry.json.unreadable` and not saved over; an unreadable or newer-version list raises
  `CoursesError` on any change (settings still save); a missing root raises `RootNotSet`,
  which names `STUDY_ROOT` and `--set-root`.
- **Migration runs once** (`"migrated"` for the settings and old sources, the empty
  `workspaces` plus the existing file for the list). The list's first move guesses the root
  from the common folder of the old courses and copies the registry to
  `registry.json.pre-courses`. Adding is idempotent, so a crash in between only repeats it.
- Sync conflict copies are reported (`_conflict_banner_lines`), not merged: a union cannot tell
  "removed on one host" from "never there".
- Locking uses `fcntl`; on Windows the lock is skipped (the launchers do not run there yet).
- The `STUDY_REGISTRY` override lets tests redirect the registry; every test also sets
  `STUDY_ROOT` and `STUDY_CONFIG_DIR` to `tmp_path`, so none reads the user's real list.

## One engine, many icons

The engine is global (this one `main.py`) so loop improvements propagate to every
subject. The entry points are specific: `--install <ws> --name X` generates a thin
per-workspace `.desktop` icon whose `Exec` passes that workspace. Each exam gets a
one-click resume icon that doubles as a passive deadline nudge, with no code
duplication.

## Model and effort

Launches use the registry keys `model` and `effort` directly, defaulting to
**opus** at **medium** effort (`DEFAULT_MODEL` / `DEFAULT_EFFORT` in `main.py`) for
claude and to `standard` for opencode (`_default_model`, see the top of this file).
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

The `o` cycle lists the Anthropic models (`_ANTHROPIC_MODELS`; under opencode also
`standard` and the free models), and `_available_models` appends whatever the
registry currently holds so a pinned value stays visible. `_current_model` accepts
only a name `_known_model` knows for the engine: a registry written by an older
build may still carry a model this one does not know, and that value falls back to
`_default_model()` instead of reaching a launch.

## Commits

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
| `wochenvorbereitung.py` | Wochenvorbereitung logic (config, timetable, state, phases, prompt, result schema, cards, tool lists); pure, stdlib |
| `templates/systemd/*` | timer and service templates for the four phases; not installed by the launcher |
| `test_wochenvorbereitung.py` | offline tests for that mode |
| `test_studyclaude.py` | offline tests — behaviour only, no network, no launch |
| `requirements.txt` | empty by design; stdlib only |

## Wochenvorbereitung: unattended, script collects, model reads, script writes

`--wochenvorbereitung {woche,morgen,beginn}` (docs/modes.md) builds the appointment tabs
without a person. Invariants:

- **The model never writes files.** It gets Read, Glob, Grep and named board tools and returns one
  JSON. The script validates it (`validate_result`) and writes state, cards and the `todo.md` line.
  An invalid result writes nothing.
- **The script selects the board, not the model.** `create_tab` takes no board and `select_board`
  is denied, so `_select_board` (main.py) calls `select_board` over HTTP with the run's bearer
  before the engine starts and fails the group unless the answer names the board. The board is
  stored on the run's link, so the run needs a link of its own. Found on the first real run
  (2026-11-23): without this the tab for "Spielplatz" landed on the board the user had open.
- **One source for the tool lists.** `BOARD_ALLOWED` / `BOARD_DENIED` in `wochenvorbereitung.py` feed
  claude's allow-list and opencode's deny-list; a test compares them. A new board tool belongs in
  one of the two tuples. Untested: whether opencode's `permission` block also covers MCP tools
  (named `<server>_<tool>` here); until that is probed, an unattended run under opencode is not
  trusted.
- **feedkit adapter.** With `wochenvorbereitung.feedkit` set, `week_appointments` takes appointments,
  `VL-` feed names, topics and slide picks from the evening job's `prep/schedule.py` / `material.py` (imported by file
  location in `_import_feedkit`: `sys.path` restored, feedkit modules dropped from `sys.modules`, no bytecode written into
  the feedkit). Its state is read, never written. The own timetable parser fills in what it lacks or has disabled; any adapter
  error falls back to the parser with a note (dry run and log). Slide text goes to `cache_dir`, outside every synced folder.
  A failed run sends one message through `<feedkit>/news/outbox.py` (`notify(text)`, loaded by file location, no secrets
  in the text); without a feedkit it stays a log line. Verified against the real outbox: `notify(text, outbox=None, host=None, now=None)`.
  The own timetable parser supplies only courses the feedkit does not know or has disabled (title and registry `key`); an enabled
  course the feedkit skips on a day (its `dates`) stays out. Registry `slots`, `extras` and `exceptions` still force appointments.
- **Reading the board: the run never reads tab content** (finding of 2026-11-19, tutor-board README and
  `server/mcp.ts`). `read_board` by a second agent drains the tab's event queue (README:653, 918), moves the user's
  submissions from `pending` to `seen` (README:2815-2827, `mcp.ts` `read_board` description) and drops the held wakes
  on that tab (README:1112); `get_canvas`, `read_chat` and `wait_url` are as bad or worse. A later agent write then
  turns every `seen` submission into `answered` (`boards.ts` `markAnswered`, l.3135; `pending` stays `pending`).
  `list_tabs` consumes nothing and shows `submissions_you_have_not_read`, `submissions_read_but_unanswered`,
  `pending_events`, `answers_the_board_did_not_mark` per tab, but not widget values typed without a submit. So
  `read_board` and `get_canvas` are in `BOARD_DENIED`, and the script decides from its state file: replacing blocks
  (`update_block`) is allowed only on a tab this tool built (`von_uns`), before the appointment starts, never handed
  over (`uebergeben`), and only on the block ids it recorded (`bloecke`) (`_in_place`). Everything else is
  `append_blocks` ("Neu seit ..."), and a tab whose `list_tabs` row shows waiting input is skipped
  (`aktion: uebersprungen`). Residual risk: a widget value typed before the start without a submit is not visible and
  could be replaced in an in-place update. Nothing sets `uebergeben` yet; a session that hands a tab over should set it
  in the state file.
- **Review cards:** `validate_card` follows the importer's rules (`cardlib.validate_card`: widgets, options, answer,
  limits) plus the evening job's check for markup and links; the files go to `<feed>/lernkarten/<course folder>/`
  (never `VL-*`; the importer wants `[A-Za-z0-9_][A-Za-z0-9_.-]{0,39}`, so a folder name with spaces is skipped with a
  log line) with `muster: null` and a file-level `expires_at`. The importer accepts the extra card field `zweck` (it
  validates known fields only and copies the card whole), so `zweck: "wiederholung"` stays.
- **Prompt:** the unattended prompt is a short orientation, the sections "Struktur", "Blöcke bauen" and "Bild zu jedem
  Inhalts-Tab" of `templates/media/board.md` (chosen by heading, paragraphs about waiting and hand-over dropped) and the
  unattended rules. It does not carry the interactive orientation of `_prompt_common()`.
- **Keys by folder name.** `METADATA.md` is read per material folder; `course_title` can be wrong.
- **No personal paths.** All of them come from the registry key `wochenvorbereitung`; the board link
  from an env file (mode 600), read at run time, never printed. The bearer is in a mode-600 file in a private
  temp dir for a claude run (`--mcp-config <path>`, removed in a `finally`), in the env of an opencode run; never in an argv.
- **Week preview:** `woche` renders one PNG (Pillow, lazy import) into `cache_dir`, copies it to `<feed>/pngs/` and
  appends one line to `.parts/wochenvorschau.jsonl`. It never runs `merge_check`: the feed's daily merge picks it up.
  Switch `vorschau` (default on); skipped in a dry run.
- **`abend`, the Nachbereitung (2026-11-23, user):** appends to the appointment's tab, by default daily at 20:15
  (set the timer after the feed job that exports the day's answers, if one runs). It needs evidence of what was covered, collected by the script: `notes_of_day` (files in the
  material folder changed that day that are not in `file_history`), new StudOn files, `session_lines` (lines of the
  course's `todo.md` with that date, without the tool's own `[wv:…]` / `[nb:…]` lines and the status lines). No
  evidence, no model run; the phase then stays open on the day itself and closes the evening after. The prepared topic
  alone is no evidence (two of three topics were guesses on the first day). `render_xopp` draws a Xournal++ file with
  Pillow (strokes, pasted images, typed text) into `cache_dir`, because the model cannot read gzip and a timer has
  no display for `xournalpp --create-pdf`. The state keeps the preparation's `thema`, `vorschau` and
  `bloecke`; the Nachbereitung has its own key `nachbereitung`. Cards go to `<stamp>-nb-<slug>.json`, numbered from 3
  (the preparation has 1 and 2), and expire `NACH_CARD_DAYS` after the appointment. A model skip on the day itself
  (input waiting) does not close the phase. The same no-read rule holds: reviewing stays with the sessions.
- **Day without appointments (`morgen`, registry switch `frei`, default off):** `plan_free_day` builds one
  Wiederholungs-Tab when a course with a `termin:` entry has session lines of the day before. The stand-in
  `free_day_appointment` gives it an id (`<date>_0000_wiederholung-<course>`), a state file and a card file. Activity
  is read from `todo.md`, not from the board: `list_boards` only has `last_opened_days_ago`, and the run's own
  `select_board` may count as opening. `open_free_tab` blocks a new tab while an earlier one of the last
  `FREE_OPEN_DAYS` days is named in no session line (one Häppchen at a time, without reading a tab). The evening run
  does nothing on such a day: there is no lecture material and it may not read what was handed in.
- **Feed games (`morgen`, registry switch `spiele`, default off; 2026-11-23, user):** per appointment of the day 3 to
  5 cards in the field `spiele`: the four games and the word puzzle of docs/feed_lernkarten.md plus quiz cards. A plan
  that runs anyway (build, update, free day) carries `games`; an appointment with a tab and nothing new gets a run of
  its own, mode `karten`, with no bearer, no MCP server and only Read, Glob, Grep (`_backend_headless(bearer=None)`).
  The morning after, an appointment whose state has `nachbereitung` gets games on that topic (`games == "nach"`), with
  the same evidence the evening run had. `validate_card(card, GAME_WIDGETS)` checks the contract (`_game_errors`);
  `valid_games` drops a bad card instead of failing the result, because by then the model may have built a tab, and an
  invalid result would lose its state. Only a `karten` run that brings no usable card counts as failed. Files:
  `<stamp>-sp-<slug>.json` (numbers from 5, expires with the appointment) and `<stamp>-ns-<slug>.json` (from 10, stays
  `NACH_CARD_DAYS`), `zweck: "spiel"`, `muster: null`, table `CARD_KINDS`. The state key `spiele` (`vor`, `nach`) makes
  each happen once. No feed folder switches the games off for the run. The script cannot check that a game's answer is
  right, only that it fits the lists.
- Not built yet: the evening job reading `woche-<KW>.json`, timer installation, PDF text cache.

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
