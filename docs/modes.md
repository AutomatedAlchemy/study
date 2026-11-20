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
right, and asks „Noch eins?“ the way the active medium does it (a button on the
board, a line in the chat) — with the next Quickie already in mind. If you
stop, it says goodbye in a sentence; no lecture. A Quickie still counts in the
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
the mode into the menu. Enter starts a session in which the tutor asks what you want to do in
this mode and how it should run. It follows up on what is still open (goal, one course or all,
the steps, the duration, the medium, what should exist at the end), then shows you a short name
and a written-out instruction. After your OK it saves both itself with
`studyclaude --save-mode NAME` (the instruction on stdin) as a named mode (`saved_modes` in the
registry) and offers to start it right away. The session starts at the courses' common root,
like the Begleiter. `s` on a course row does the same inside that course and binds the mode to
it, `s` on any other row is the same as the mode row. From the shell, use
`--new-mode [WORKSPACE]`.

Saved modes show up as `↳ Name` rows under the mode row, with the course name when they have
one. Enter starts one: the session gets the instruction as its `<auftrag>`, plus the time, the
exams and every dossier. `p` starts it once with an edited text, `s` changes its text or name
by hand, and `x` removes it. A mode with the same name is replaced, so the interview can also
revise an existing mode: it sees the modes you already have. A mode whose course is no longer
registered runs across all courses.

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

`studyclaude --wochenvorbereitung {woche,morgen,beginn}` bereitet die Termin-Tabs der
Woche ohne Aufsicht vor. Es ist kein Menümodus: Timer rufen es auf einem Rechner auf, der
das Board und die Kursordner erreicht (Vorlagen in `templates/systemd/`, nicht
installiert). Die Logik steht in `wochenvorbereitung.py`, der Start der Engine in
`_backend_headless` (`main.py`).

| Phase | Wann | Was |
|---|---|---|
| `woche` | Samstag 07:00 | Tabs für alle Termine der kommenden Woche (Mo bis Fr) bauen, `woche-<KW>.json` schreiben |
| `morgen` | Mo bis Fr 06:30 | Termine von heute: neue Dateien im Materialordner? Dann Tab nachziehen |
| `beginn` | Mo bis Fr alle 5 Minuten | Termine, deren Beginn 5 bis 20 Minuten zurückliegt: bei +5, +10, +15 prüfen, bei +20 schließen |

Neu heißt: ein `file_history`-Zeitstempel in der `METADATA.md` des Materialordners liegt nach
dem gespeicherten. Der Schlüssel ist der Ordnername, nie `course_title`. Ist nichts neu, läuft
kein Modell. Ist `last_fetched` zu alt (nicht heute, bzw. nicht vor Beginn −5 Minuten), steht
„StudOn heute nicht synchronisiert“ als Ergebniszeile im Zustand.

- **Zustand:** je Termin `<state_dir>/termine/<YYYY-MM-DD>_<HHMM>_<slug>.json`, dazu
  `<state_dir>/woche-<KW>.json`. Der Zustand ersetzt das Herleiten aus `todo.md`.
- **Konfiguration:** Registry-Schlüssel `wochenvorbereitung`, gesetzt mit
  `--set-wochenvorbereitung KEY VALUE` (`material_root`, `timetable`, `state_dir`, `env_file`,
  `engine`, `model`, `skip`, `extras`, `exceptions`, `termin:<Titel>` mit
  `Kursordner;Materialordner;Board;VL-Name`). Die Stundenplandatei ist eine Markdown-Tabelle
  `| Tag | Zeit | Veranstaltung | Typ | Gebäude | Dozent | Zeitraum |`.
- **Board-Link:** steht in einer Env-Datei (Modus 600, Pfad `env_file`, Variable `BOARD_LINK`).
  Der Lauf tauscht ihn mit `POST /agent/token` gegen einen Bearer. Die Datei fehlt oder ist für
  andere lesbar: Abbruch mit Code 2.
- **Werkzeuge:** claude bekommt eine Allow-Liste (`dontAsk`), opencode eine Deny-Liste (`--auto`).
  Beide kommen aus einer Quelle (`BOARD_ALLOWED` / `BOARD_DENIED`). Erlaubt sind Read, Glob, Grep
  und `list_boards`, `list_tabs`, `create_tab`, `update_tab`,
  `append_blocks`, `update_block`. Nie `select_tab`, `clear_board`, `show_board`, `select_board`.
- **Regeln für Tab-Änderungen:** Der Lauf liest nie den Inhalt eines Tabs, weil `read_board` dem User Abgaben und Klicks
  wegnehmen würde (Begründung in `CLAUDE.md`). Er sieht nur `list_tabs` (Titel, Fenster, Zähler). Ein Tab mit wartender Eingabe
  wird übersprungen. Sonst wird angehängt („Neu seit …“). In Ort und Stelle ändert er nur Blöcke eines Tabs, den er selbst
  gebaut hat, vor Beginn des Termins und nur an den im Zustand gemerkten Block-Ids.
- **Woche:** `woche` nimmt ab Samstag die nächste Woche, Mo bis Fr die laufende, dann nur Termine, die noch nicht begonnen
  haben. `--woche JJJJ-Www` erzwingt eine Woche. Wiederkehrende Termine, die weder feedkit noch die Stundenplandatei kennen,
  stehen in der Registry-Liste `slots` (Setter: `--set-wochenvorbereitung slots '<JSON-Liste>'`, je Eintrag `weekday`, `start`,
  `end`, `title`, optional `from`, `to`).
- **Feed:** Der Lauf liest die letzten 7 Tage aus `lernkarten_antworten/VL-<Name>.jsonl` (falsche erste Antworten) und
  `lernkarten_kommentare/VL-<Name>.jsonl` und gibt sie als Datenblock `<feed_rueckmeldung>` weiter. Er bucht nichts daraus.
  Er schreibt je Termin 1 bis 2 Wiederholungskarten, `woche-<KW>.json` nach `<Feed>/wochenvorbereitung/` und ein
  Vorschaubild (Schalter `vorschau`, Vorgabe an); der tägliche Merge des Feeds nimmt den Part auf, unser Code startet ihn nicht.
- **Fehler:** Ein gescheiterter Lauf schickt höchstens eine Nachricht über `<feedkit>/news/outbox.py`, ohne Geheimnisse.
- **Ergebnis:** ein JSON je Lauf (Tab-Id, Thema, Schlüssel, `Bild:`, 1 bis 2 Wiederholungskarten,
  ein Satz Vorschau). Ein ungültiges Ergebnis zählt als gescheiterter Lauf, es wird nichts
  geschrieben.
- **Prüfen:** `--wochenvorbereitung woche --dry-run` druckt Terminliste, Prompt, Befehl (Bearer als
  `<bearer>`) und Werkzeugliste und schreibt nichts. `--termin ID` erzwingt einen Termin.

- **Quelle der Termine (feedkit):** Ist `feedkit` gesetzt (Ordner des Abend-Jobs, nur auf dem Rechner, auf dem er liegt)
  und vorhanden, liefert dessen `prep/schedule.py` die Termine samt `VL-`-Feedname, Thema und gewählten Folien
  (`material.pick_material`). Die eigene Stundenplandatei ergänzt, was dort fehlt oder abgeschaltet ist (gleiches Datum,
  gleicher Beginn, gleicher normierter Titel zählt als derselbe Termin). Der Folientext (`job.read_text`) kommt in ein
  Cache-Verzeichnis außerhalb von `~/Synced` (`cache_dir`, Vorgabe `~/.cache/study/wochenvorbereitung`) und wird erst bei einem
  echten Lauf geschrieben. Der Zustand des Abend-Jobs wird nur gelesen. Der eigene Parser liefert nur Kurse, die der feedkit nicht kennt oder abgeschaltet hat; ein aktiver Kurs, den der feedkit an einem Tag auslässt (`dates`), bleibt draußen. `slots`, `extras` und `exceptions` der Registry erzwingen Termine trotzdem. `notify(text, outbox=None, host=None, now=None)` ist gegen das echte Outbox geprüft. Fällt der Adapter aus, nimmt der Lauf den eigenen
  Parser und meldet das im Dry-Run (`Hinweis:`) und im Log. Ein Eintrag in `termine` kann mit einem fünften Teil
  (`...;feed;KOR`) an einen feedkit-Schlüssel gebunden werden; dann zählt dessen Feedname.

Noch nicht gebaut: Änderungen im Abend-Job (liest die Terminliste noch nicht), ein Installer für die Timer.

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
