# Workspaces, the overview contract, media

Each subject gets a **workspace** — a normal directory holding your lecture
PDFs, past papers, and problem sets, plus a `CLAUDE.md` describing how you want
to study *that* subject. `studyclaude <workspace>` starts Claude with its working
directory set there, so Claude Code loads that `CLAUDE.md` automatically and
follows it. Improve the loop by editing a workspace's `CLAUDE.md`, not the
launcher code.

## Vocabulary

The German terms are load-bearing, so they're worth knowing:

| Term | Means |
|---|---|
| **Lern-Loop** | The study procedure defined in a workspace's `CLAUDE.md` |
| **Lern-Set** | The files opened at the start of a session — reference sheets, newest problem set |
| **Häppchen** | Literally "small bite" — one exercise-sized chunk of work |
| **Fehlermuster** | Error patterns: a ranked table of the mistakes still open, plus the log of evidence behind each; used to target the next Häppchen |
| **Themenkarte** | Topic map: the exam's topics and the typical trap in each |

## Layout

Onboarding stamps a minimal skeleton and never overwrites an existing file:

| Path | Role |
|---|---|
| `CLAUDE.md` | The Lern-Loop procedure and exam facts. Stamped from [`templates/LERNLOOP_TEMPLATE.md`](../templates/LERNLOOP_TEMPLATE.md). |
| `todo.md` | Where you left off — subject, exam date, active files, plus the two bookkeeping lines the menu reads (`Fortschritt: x/y Häppchen`, `Übersicht: bestätigt YYYY-MM-DD`) |
| `fehlermuster.md` | Error patterns: ranked `## Aktive Muster` table on top (the menu's dossier reads its first row), chronological `## Belege` log below |
| `Personalisierte_Übungen/` | Generated exercises land here |

Everything else is created on demand, when a workflow is first used.

## The Blatt-Finder

When an exam allows a self-written sheet and there is a pool of questions (a
question catalogue, the lecture goals, old exam tasks), the session builds
`Klausur_mitnehmen/blatt_finder.html` once the sheet has a first complete
version: the questions on the left, the sheet on the right. Clicking a question
highlights exactly the text on the sheet that helps answer it and says whether
the sheet covers the question fully, partly or not at all. Clicking a passage
of the sheet lists the questions that use it. The page is one self-contained
file and works offline.

The mapping is done by subagents and checked mechanically: every snippet must
occur verbatim on the sheet. [`templates/tools/blatt_finder.py`](../templates/tools/blatt_finder.py)
validates and builds; its `--help` is the full procedure and data format. It
needs `node` with KaTeX only to render formulas (`--katex DIR`), and falls back
to the formula source without it.

## Adding a course

`--add` is interactive by design. Rather than prompting you to type an absolute
path, it starts a Claude session that searches your filesystem with you, agrees
on a location, and then calls `--register` itself.

A fresh clone has nothing registered, so the menu shows only "add a course" —
there is no built-in default folder.

## The course overview (the contract)

Every course gets an overview before its first Häppchen: what the exam asks,
every topic of the Themenkarte explained from scratch, every material in the
course folder named and explained, and an agreement on what is in and what is
out. You read it on your own, then confirm it — that confirmation is the
contract between you and the tutor about what the course covers. It lives in
the working medium (on the board it is Tab 0, with the material attached so you
can open it from there), not in a file: the learner only ever sees the medium.

The launcher owns none of the content. It reads one bookkeeping line the
session writes to the course's `todo.md` once you have confirmed
(`Übersicht: bestätigt 2026-09-02`), shows `· ohne Übersicht` on the menu row
until then (`· Übersicht unbestätigt` once the line says it is built and only
the confirmation is missing), and tells a normal launch or the Begleiter to
build the overview first, or to ask for the confirmation if it is already
built. Courses created before this existed pick it up the same way on their
next launch; the session copies the `Kursübersicht` section from the template
into the course `CLAUDE.md` if it is missing. The Quickie never builds one.
Changing the Themenkarte means the overview is redone and confirmed again.

## The medium switch

Sessions work in one of two media: **Xournal++ + Firefox** (exercise PDF in the
browser, calculations on a separate `.xopp` sheet) or a **Tutor Board** (a web
whiteboard with one tab per exercise; it needs an account on the author's
service, see the README). The active medium is a single launcher-level switch —
toggle it with `m` in the menu, `studyclaude --set-medium xournalpp|board`, or
`STUDYCLAUDE_MEDIUM` — not a per-course fact.

The mechanics of each medium live in `templates/media/<name>.md` and ride into
every session via the system prompt; course workspaces carry no medium
instructions at all, so improving how a medium works is one edit for all
subjects. Mid-session you can still switch verbally ("lass uns aufs Board") —
the session carries on and reminds you to flip the menu switch for next time. A
course whose own `CLAUDE.md` pins a fixed medium overrides the switch.

## Visuals per course

How many sketches and explainer clips a session makes depends on the subject.
Each course says it in one Eckdaten row of its `CLAUDE.md`:
`| **Visualisierung** | viel | mittel | wenig | keine; exceptions per topic |`.
Without the row, `mittel` applies, and the next session proposes a level and
asks you once. The medium file says what a level means there (on the board: a
still sketch in the tab, a narrated manim clip for ideas with motion). The
session decides while it builds each tab, before it hands the tab over, and
writes the decision into `todo.md` as a `Bild: …` line, including the reason
when there is no picture. Say "mehr Bilder" or "weniger" to change the level.

## Using it in another language

Nothing structural is German; the strings are. To translate, edit the four
prompt builders in `main.py` — `_assemble_prompt`, `opening_message`,
`opening_message_onboard` — and
[`templates/LERNLOOP_TEMPLATE.md`](../templates/LERNLOOP_TEMPLATE.md). That's
the whole surface. The launcher, registry, and menu need no changes.

One instruction is worth keeping whatever the language: the prompt tells Claude
to explain **without LaTeX**, in Unicode notation (`√`, `x²`, `∫`, `≤`, `λ`). A
terminal can't render `\frac`, and unrendered LaTeX is genuinely hard to read
mid-exercise. LaTeX belongs in the `.tex` files the exercises produce, not in
the chat.
