# Launch modes in detail

The menu and the flags in the [README](../README.md) start four kinds of session.
A plain course launch just runs that workspace's Lern-Loop. The other three are
described here.

## Begleiter

The Begleiter is the default persona and the menu's top row as soon as one
course is registered. Picking it (or running `studyclaude --begleiter`) launches
one session at the courses' common parent folder, like the Gärtner, with every
course's dossier, your upcoming exams, the Wochenplan and the current time. It
works from the clock:

1. It reads your profile: the tab „Profil“ on one of your Tutor Boards, found by name.
   The profile says who you are (programme, semester), where your timetable is
   (a calendar, a file, another board's tab) and where the semester's material
   lies. It is free text. The repo holds no personal data, so the profile lives
   on your board. Without a board, or without the tab, the session asks you for
   these facts in chat and offers to create the tab.
2. It checks the timetable the profile names: what runs now, what just ended,
   what comes later today, and deadlines until tomorrow.
3. It picks what is due: following a lecture that is running, preparing one that
   starts within the hour, reviewing one that just ended, a deadline, or — in free
   time — a course by Wochenplan, exams and dossiers, and the next Häppchen from
   its Lern-Loop.
4. It tells you in at most three lines what is on now, what comes later and what
   it suggests, and then starts.

It is the automatic default whenever you never chose one, and `d` on its row or
`studyclaude --set-default begleiter` sets it explicitly. The tab „Profil“ may sit on
any of your boards (found by name); Häppchen go on each course's own board.

## Dossiers

The sessions that work across courses (Begleiter, a Quickie with several
courses, Gärtner) get a compact, mechanically extracted dossier per course in
their opening message: progress line, overview status, days since last
activity, Themenkarte size, created/reviewed Häppchen counts, the dominant
Fehlermuster, the newest todo.md entry. They read a course's files themselves
once they have picked it. (Scripted flags like `--dry-run` need a concrete
folder; with a mode as the default they fall back to the first course.)

## Quickie

The menu's second row (shown as soon as one course exists) is **⚡ Quickie**
— one short Häppchen, about five minutes, nothing else. It is the low-threshold
entry for days when a full session feels like too much: pick it (or run
`studyclaude --quickie`) and the session greets you in one sentence, picks a course
in half a sentence when there are several (no file reading first — the dossiers
suffice), and opens one small, self-contained, deliberately *winnable* task in
the active medium, following that course's `CLAUDE.md` mechanics scaled down to
a single Häppchen. After your answer it corrects briefly, names what you got
right, and builds the next Quickie at once without asking: on the board it sits
behind a „Weiter → QKnn“ button, in the chat it starts in the chat. If you
stop (you say so in the chat), it says goodbye in a sentence; no lecture. A Quickie still counts in the
`Fortschritt:` line and is noted with date and topic in `todo.md`.

The launcher keeps a streak in the registry (`quickies`: last date, days in a
row, total) and shows it on the row — `· Serie: 3 Tage` while the streak is
alive (a Quickie today or yesterday), `· 12 Quickies, zuletzt 11.10.` otherwise. The session gets
the numbers to mention in its greeting. A launch counts as a Quickie; the
launcher never judges whether you finished. `studyclaude --set-default quickie`
(or `d` on the row) makes it the 10s autostart target.

The Quickie never builds a course overview.

## Eigener Modus

The third mode row, **✎ Eigener Modus anlegen**, creates a mode of your own. You do not type
the mode into the menu. Enter starts a session in which the tutor first asks, as plain chat
text, what you want to do in this mode and how a session should run, with an example or two of
an answer. You write freely. Only then does it make proposals where your answer leaves the
direction open (drawn from your courses and their state, the coming exams, the medium, the
modes you already have) and follow up on what is still open (goal, one course or all, the
steps, the duration, the medium, what should exist at the end), each follow-up with a few
answers to pick from. Then it shows you a short name and a written-out instruction. After your
OK it saves both itself with
`studyclaude --save-mode NAME` (the instruction on stdin) as a named mode (`saved_modes` in the
registry) and offers to start it right away. The session starts at the courses' common root,
like the Begleiter. `s` on a course row does the same inside that course and binds the mode to
it, `s` on any other row is the same as the mode row. From the shell, use
`--new-mode [WORKSPACE]`.

Saved modes show up as `↳ Name` rows under the mode row, with the course name when they have
one. Enter starts one: the session gets the instruction as its `<auftrag>`, plus the time, the
exams and every dossier. `p` starts it once with one added line („heute nur 20 min“), and `x`
removes it. `s` on a `↳` row starts the same interview to revise that mode: the tutor says what
the mode does now, asks what should change, and saves the result in place, under the old or a new name
(`--save-mode NAME --replaces OLD`). A mode whose course is no longer registered runs across
all courses.

For a one-off session without a saved mode, press `p` and type one line, for example
„Nachbereitung der Vorlesung von heute“ or „30 min Klausursimulation Chemie“. On a course row
it runs inside that course, with its CLAUDE.md loaded, otherwise across all courses. The text
is not kept. From the shell, use `--auftrag "TEXT" [WORKSPACE]`.

`d` on a `↳` row makes the mode daily. A daily mode that has not been reported done today
is the menu's default instead of the stored one: the cursor starts on it, the row says
`★ startet heute zuerst`, and the 10s autostart runs it. Done is not the same as launched,
because a launch can be cut off. The session reports it itself: a daily mode's Auftrag ends
with the instruction to run `studyclaude --mode-done NAME` once everything for the day is
prepared, or when there is nothing to prepare. That writes today's date into the mode
(`done`), and the stored default (the Begleiter, unless changed) is back until midnight. A
daily mode started again on the same day is told to check what exists and build only what
is missing. For 60 minutes after a launch the menu does not autostart the mode again (the
row says `läuft seit HH:MM`), so a second menu does not start a second run beside the first;
Enter on the row still starts it. Starting it with an edited text (`p`) is a one-off and gets no such instruction.

## Wochenplan

The Begleiter (in free time) and the Quickie pick a course on their own. To steer that pick by
weekday, write a plain-text rule into `data/wochenplan.md`, next to the registry
(with `STUDY_REGISTRY` set, next to that file). For example: "Monday to
Friday the university courses, on weekends the languages; an exam within 7 days
always comes first." Copy
[`templates/wochenplan.example.md`](../templates/wochenplan.example.md) as a
starting point and name courses by their folder name.

The launcher does not parse the rule. It passes the text, together with today's
weekday and date, into the opening message, and the session applies it when it
picks. Without the file, or with an empty one, nothing changes. The file is
personal and gitignored, like the registry. A Quickie with only one course
registered has no pick to make and ignores it.

## Gärtner

The Gärtner is a maintenance session, not a study session: no Häppchen, no
tutoring. Press `g` in the menu (or run `studyclaude --gaertner`) and tell it in chat
what to do with your courses — clean one up, merge two into one, revise a
course's `CLAUDE.md` against the current template. It gets every course's
dossier and your upcoming exams, greets you, names up to three things it notices
(two courses on the same subject, a long-idle course, a missing overview) and
asks what you want to tackle. It starts at the courses' common parent folder.

`Space` in the menu opens a multiselect with the course under the cursor
checked; `Space` toggles a course, `Enter` or `Esc` goes back. Courses checked
when you press `g` are named as the focus; the others are there for comparison
and change only when you say so.
From a script, `studyclaude --gaertner PFAD…` sets the focus; a path that is not
registered is shown but not registered.

Before anything that moves, deletes or merges files, or changes the course list,
it shows a short plan and waits for your OK. It changes the course list only
through `studyclaude --register` / `--unregister`, never by editing the registry file,
and moves what should go into `_archiv/` inside the course instead of deleting
it, unless you ask for deletion. After a merge it re-estimates the `Fortschritt:`
line and sets `Übersicht: fehlt`, so the next study session builds a new overview.
The Gärtner keeps no state and does not count towards the Quickie streak.

## Wochenvorbereitung

`studyclaude --wochenvorbereitung {woche,morgen,beginn,abend}` prepares the appointment tabs of
the week on the Tutor Board without supervision. It is not a menu mode. Timers call it on
a machine that reaches the board and the course folders. Unit templates are in
`templates/systemd/`; copy and enable them yourself, there is no installer for them.
When a feed job imports the cards, let it start the `woche` and `morgen` services
(`systemctl --user start study-wochenvorbereitung-morgen.service`) before its import and
leave those two timers off. Then the cards of the day reach the feed before the first
appointment. The author's feed does this at 05:00.

| Phase | When | What |
|---|---|---|
| `woche` | Saturday 07:00 | Build a tab for every appointment of the coming week (Mon to Fri) |
| `morgen` | daily 05:30 | Today's appointments: new files in the material folder? Then extend the tab. On a day without appointments: one Wiederholungs-Tab, see below |
| `beginn` | Mon to Fri, every 5 minutes | Appointments that began 5 to 20 minutes ago: check at +5, +10, +15, close at +20 |
| `abend` | daily 20:15 | Nachbereitung: for each appointment of today that has ended, append what was covered and 4 to 6 questions to its tab |

A file counts as new when its `file_history` timestamp in the material folder's
`METADATA.md` is later than the stored one. When nothing is new, no model runs. When the
material was not synchronised today, the run records that instead of a result.

- **Nachbereitung (`abend`):** it runs for an appointment only when something says what was
  covered: a file you changed in the material folder that day (a Xournal++ file, a photo, a
  PDF), new files from StudOn, or a line with that day's date that a session wrote into the
  course's `todo.md`. A Xournal++ file is rendered to images first, so the handwriting can be
  read. Without any of these nothing is appended, and the next evening tries once more. It
  appends to the appointment's tab (block ids `nb_…`), never reads your submissions and never
  reviews them. It writes 1 to 2 cards that stay in the feed for 7 days and one line
  `Nachbereitung …` into `todo.md`. The timer runs after the feed's evening job, so today's
  answers are exported already. On a day without appointments it does nothing.
- **Day without appointments (`morgen`, switch `frei`):** when the day before has a session
  line in the `todo.md` of a course that has an entry under `termin:`, the run builds one
  Wiederholungs-Tab on that course's board: 5 to 7 tasks on the top Fehlermuster and on what
  those lines name, no window, no new material. The course with the most lines gets it. No
  new tab while an earlier one of the last 7 days is not named in any session line. Off by
  default: `--set-wochenvorbereitung frei on`.
- **Feed games (`morgen`, switch `spiele`):** with the flashcard feed set up, the morning run
  also writes 3 to 5 cards per appointment of the day: matching, ordering, sorting, a cloze
  text, a word puzzle and quiz questions on what the slides say you should know before the
  lecture. They expire when the appointment ends. The morning after a Nachbereitung it writes
  the same kind of cards on what was covered; those stay 7 days. A run that only writes these
  cards gets no board access at all. Nothing is booked from them (`muster: null`). Off by
  default: `--set-wochenvorbereitung spiele on`.
- **Configuration:** registry key `wochenvorbereitung`, set with
  `--set-wochenvorbereitung KEY VALUE`. Keys: `material_root`, `timetable`, `state_dir`,
  `cache_dir`, `env_file`, `engine`, `model`, `skip`, `extras`, `exceptions`, `slots`, `frei`, `spiele`, and
  `termin:<title>` with the value `course folder;material folder;board;lecture name`.
- **Timetable:** a Markdown table
  `| Tag | Zeit | Veranstaltung | Typ | Gebäude | Dozent | Zeitraum |`. Recurring
  appointments that are not in it go into `slots`
  (`--set-wochenvorbereitung slots '<JSON list>'`, each entry with `weekday`, `start`,
  `end`, `title`, optional `from`, `to`).
- **Week:** from Saturday on, `woche` takes the next week. Monday to Friday it takes the
  current week and only appointments that have not begun. `--woche YYYY-Www` forces a week.
- **Board link:** in an env file (mode 600, path `env_file`, variable `BOARD_LINK`). When
  the file is missing or readable by others, the run stops with exit code 2.
- **Board:** the script selects the appointment's board with the run's own link before
  the model starts, and the run fails if the board does not confirm it. The model has no
  tool to change the board. Give the run a link of its own: a link shared with another
  agent shares the selected board with it.
- **Tools:** the session may read files (Read, Glob, Grep) and call `list_boards`,
  `list_tabs`, `create_tab`, `update_tab`, `append_blocks` and `update_block`. It never
  switches the tab or board you are looking at and never clears a board.
- **Changes to tabs:** the run never reads a tab's content, so your submissions and clicks
  stay unread for your next session. A tab with input waiting is skipped. Otherwise new
  material is appended ("Neu seit …"). It edits blocks in place only in a tab it built
  itself, and only before the appointment begins.
- **Feed:** with the flashcard feed set up ([feed_lernkarten.md](feed_lernkarten.md)), the
  run reads the last 7 days of wrong first answers and comments for the lecture and writes
  1 to 2 review cards per appointment.
- **State:** one JSON file per appointment and one per week under `state_dir`.
- **Errors:** a run with an invalid result counts as failed and writes nothing.
- **Check:** `--wochenvorbereitung woche --dry-run` prints the appointment list, the
  prompt, the command and the tool list and writes nothing. `--termin ID` forces one
  appointment.

## The progress line

Each course row in the menu shows its progress, e.g. `· 7/24 Häppchen` (and
`✓ bereit` once the target is reached), and `· ohne Übersicht` while the course
has no confirmed overview yet. The numbers come from a single line the study
session itself maintains in the workspace's `todo.md`:

```
Fortschritt: 7/24 Häppchen
```

`x` counts reviewed Häppchen; `y` is the session's *living estimate* of how many
it will take until you are exam-ready, re-judged after every review. The
launcher only reads the line — the judgment stays in the workspace. No line, no
display.
