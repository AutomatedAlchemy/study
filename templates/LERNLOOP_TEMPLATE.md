# CLAUDE.md — Lern-Loop-Workspace: «FACH»

> Generalisiertes Lern-Loop-Muster (Prototyp: Math DS 2). Diese Datei wurde von
> der Kurs-Anlage in den Materialordner gestempelt. Die anlegende Claude-Instanz
> füllt die «Platzhalter» aus dem vorhandenen Material aus.
> Gestartet wird der Loop über `studyclaude «dieser Ordner»` (eigenes Desktop-Icon möglich).

## Eckdaten (beim Anlegen ausfüllen)

| | |
|---|---|
| **Fach** | «FACH» |
| **Klausur** | «Datum, Uhrzeit, Ort» |
| **Modus** | «Rechnen \| Freitext \| Multiple Choice \| mündlich»; hat die Prüfung Teile mit verschiedenem Format, das Format je Teil |
| **Bestehen ab** | «z.B. 50 %» |
| **Hilfsmittel** | «z.B. 5 handschriftliche A4-Seiten \| keine \| Formelsammlung» |
| **Visualisierung** | «viel \| mittel \| wenig \| keine»; Ausnahmen je Thema in einem Halbsatz, z.B. „Phasendiagramme viel, Stöchiometrie keine“ |

**Visualisierung** sagt, wie viel Anschauung das Fach trägt. Die anlegende Session
schlägt die Stufe aus der Themenkarte vor und lässt sie bestätigen; das Feld
blockiert nicht. Was eine Stufe im aktiven Medium heißt, steht im Systemprompt.
Sagt der User „mehr Bilder“ oder „weniger“, wird die Zeile geändert.

**Unbekannte Eckdaten blockieren.** Ist ein Feld beim Anlegen unbekannt (vor allem
Hilfsmittel, Datum, Bestehensgrenze), steht es in der Vereinbarung als offene Frage
**mit Frist**: spätestens nach drei Tagen geklärt, über Kursseite und Ankündigungen,
den Abgleich mit der Prüfungsdatei, die das Startmenü für seine Klausurzeile liest,
sonst über eine Frage an den Prüfer. Nicht „vorsichtshalber ohne üben" (EP2 2026:
vier Wochen mit falschem Datum und unbekannten Hilfsmitteln, obwohl die
Prüfungsdatei beides richtig hatte). Sobald ein handschriftliches Blatt erlaubt ist,
wird `Klausur_mitnehmen/` **am selben Tag** angelegt und ab dem nächsten Review
mitgeführt, nicht in der letzten Woche.

## Themenkarte (beim Anlegen aus dem Material füllen)

Der Klausur-Bauplan: die Themen + je Thema die typische Falle. Bewusst ein
Abschnitt in dieser Datei und keine eigene Datei — so lädt Claude ihn
automatisch mit. Die Häppchen rotieren durch diese Themen.

**Herleitung, in dieser Reihenfolge:** zuerst die **Altklausuren** (jede Aufgabe
jeder Altklausur bekommt eine Zeile, in der sie steht), dann die **Tutorien /
Übungsblätter**, zuletzt die **Vorlesungen**. Die Tutorien decken nicht alles ab,
was die Klausur fragt: in Experimentalphysik II (2026) fehlten Optik und
Thermodynamik in allen Tutorien, waren aber in beiden Altklausuren der
zweitgrößte Block und wurden nie geübt. Jede Zeile nennt ihre Quelle. Fehlen
Altklausuren, steht das als offene Frage in der Vereinbarung, und die Karte gilt
als vorläufig.

**Deckungsprobe** (beim Anlegen und bei jeder neu gefundenen Altklausur): jede
Aufgabe jeder Altklausur lässt sich einer Zeile zuordnen, sonst kommt eine Zeile
dazu. Das Ergebnis steht in der Vereinbarung.

Die Spalte **Klausurbeleg** sagt, ob eine Altklausur die Zeile abfragt (✓) oder
nicht (—). Nach ihr wird gekürzt, wenn die Zeit nicht reicht (§Die drei
Kern-Dateien, `Budget:`-Zeile).

| # | Thema | Typische Falle | Quelle | Klausurbeleg |
|---|-------|----------------|--------|--------------|
| 1 | «…» | «…» | «Altklausur SS25 Nr. 6 · Tut. 3 · VL 5» | «✓» |
| 2 | «…» | «…» | «…» | «—» |

## Kursübersicht (beim Anlegen bauen, vom User bestätigen)

Der Vertrag zwischen Tutor und Lerner darüber, was Kurs und Prüfung umfassen.
Beim Anlegen aus dem Material gebaut, vom User allein gelesen und bestätigt;
nach jeder Änderung der Themenkarte nachgezogen und neu bestätigt. Ohne
bestätigte Übersicht kein Häppchen.

Inhalt, in dieser Reihenfolge — kein Vorwissen voraussetzen, der User soll sie
ohne Rückfrage lesen und verstehen können. Dabei knapp bleiben: je Thema
höchstens 6 Sätze, je Material ein Halbsatz.

1. **Prüfung** — die Eckdaten von oben, dazu Aufgabenformat (Rechnen, Ankreuzen,
   Herleiten, mündlich), Gewichtung und was „bestanden" konkret heißt.
2. **Themen** — je Zeile der Themenkarte: die Idee in eigenen Worten, was die
   Prüfung dazu verlangt (Aufgabentyp, Tiefe), die Notation ausgeschrieben, die
   typische Falle, und welches Material das Thema abdeckt.
3. **Materialien** — jede Datei und jeder Ordner im Kurs-Ordner und jede Quelle
   (Folien, Übungsblätter, Altklausuren, Skript, Bücher): was es ist, wofür es
   taugt, wie der Loop es nutzt, und **ob die Session es gelesen hat** (gelesen /
   überflogen / ungelesen; Scans ohne Textebene zählen erst als gelesen, wenn sie
   visuell durchgesehen wurden). Ungelesenes Material ist eine Lücke der
   Themenkarte und steht als solche in der Vereinbarung. Der Lerner soll jedes
   Material von der Übersicht aus erreichen können.
4. **Vereinbarung** — was drin ist, was ausdrücklich nicht, das Ergebnis der
   Deckungsprobe (§Themenkarte), offene Fragen an den User. Der User bestätigt;
   erst dann gilt sie.

Ort: im Arbeitsmedium (Mechanik im Systemprompt), nicht als Datei — der Lerner
sieht nur das Medium. Buchung: genau eine Zeile `Übersicht: bestätigt YYYY-MM-DD`
in `todo.md` (bis dahin `Übersicht: fehlt`); das `studyclaude`-Startmenü liest genau
diese Zeile. Bei Neubestätigung das Datum ersetzen.

## Die drei Kern-Dateien

- **`CLAUDE.md`** (diese Datei) = *wie* + Eckdaten + Themenkarte. Zuerst lesen.
- **`todo.md`** = *wo stehen wir* — Re-Entry-Punkt: Klausurdatum, Stand, aktive Dateien.
  Enthält die Zeile `Fortschritt: x/y Häppchen` am Zeilenanfang (`**…**` erlaubt) —
  x = reviewte Häppchen, y = aktuelle Schätzung, wie viele Häppchen es insgesamt bis zur
  Klausurbereitschaft braucht. y ist eine lebende Schätzung (nach jedem Review neu bewerten,
  gern anhand der Themenkarte). Das `studyclaude`-Startmenü liest die **letzte** solche Zeile:
  du kannst die eine Zeile oben pflegen oder pro Sitzung eine neue anhängen. Im Fließtext
  erwähnte Zahlen gehören eingerückt, nie an den Zeilenanfang.
  Zweite Pflichtzeile: `Übersicht: bestätigt YYYY-MM-DD` (siehe §Kursübersicht).
  Dritte Zeile, nach jedem Review nachgezogen: `Budget: T Tage · h Häppchen/Tag ·
  n Themen offen`. Reicht T·h nicht für eine Runde über die offenen Themen, schlägt
  die Session **von sich aus** einen gekürzten Pfad vor (welche Zeilen der Themenkarte
  gestrichen werden) und lässt ihn bestätigen. Behalten wird in dieser Reihenfolge:
  Zeilen mit Klausurbeleg, dann Zeilen mit Beleg aus Übungsblatt, Fragensammlung
  oder Skriptkern, der Rest ist Reserve. Nicht warten, bis der User „zu viele Themen" sagt (EP2 2026: 36 Themen,
  ein Häppchen alle drei Tage, zweimal erst auf Beschwerde gekürzt).
- **`fehlermuster.md`** = *was ich falsch mache*, der personalisierte Kern. Zwei Teile:
  oben die **Rangliste** `## Aktive Muster`, eine Tabelle `# | Muster | Belege | Stand`
  (Belege als Zahl, Stand offen / repariert), nach jedem Review umsortiert, das
  dominante Muster in Zeile 1 (das Startmenü liest genau diese Zeile). Darunter das
  **Beleg-Log** `## Belege`, chronologisch angehängt: je Review User-Zitat → warum
  falsch → was stattdessen, mit der Nummer des Musters. Ein Muster hat **eine**
  Nummer; ein weiterer Beleg ist ein neuer Log-Eintrag unter derselben Nummer plus
  ein Zähler in der Tabelle, keine Nummern 6b…6g. (EP2 2026: 37 KB reines Log, zwei
  Muster „4", Muster 17 hinter 19; eine Rangliste gab es nie.)
- **`Personalisierte_Übungen/`** — die Häppchen (Aufgabenquelle, z.B.
  `haeppchen_NN.tex` → `.pdf`), die Rechenblätter des Users und die Artefakte der
  Reviews. Welche Form Rechenblatt und Review-Artefakt haben, bestimmt das
  Arbeitsmedium (Systemprompt).

**Schreibrechte.** Die Session schreibt `todo.md`, `fehlermuster.md`,
`Personalisierte_Übungen/` und die situativen Dateien des nächsten Abschnitts. In
dieser `CLAUDE.md` ändert sie nur die Eckdaten, die Themenkarte und
§Kursübersicht, und das als einzelne Änderungen — die Datei wird nie neu
geschrieben. Kursmaterial (Folien, Übungsblätter, Altklausuren, Skripte) wird nie
geändert, verschoben oder gelöscht.

## Situative Dateien — nur anlegen, wenn gebraucht

- **`notebooklm_lernpausen.md`** (nur wenn du Lernpausen-Videos willst) — EIN
  kompaktes NotebookLM-Doc: (A) Fehlermuster, (B) Themen im Schnelldurchlauf. Kein
  LaTeX, Unicode. Dynamisch, nicht kumulativ.
- **`Klausur_mitnehmen/`** (nur falls Hilfsmittel erlaubt, dann ab dem Tag, an dem
  das feststeht) — Mitnehm-Blätter; Patch-SSoT `cheatsheet_personalisierung.md`
  (Fehlermuster → Blatt-Änderungen), nach jedem Review geprüft.
- **`Klausur_mitnehmen/blatt_finder.html`** (nur falls ein eigenes Blatt erlaubt ist
  und es einen Fragenpool gibt: Fragenkatalog, Lernziele der Folien,
  Altklausur-Aufgaben) — der Blatt-Finder: eine Seite mit dem Mitnehm-Blatt und allen
  Fragen des Pools. Ein Klick auf eine Frage markiert auf dem Blatt genau die Stellen,
  die bei der Antwort helfen, und sagt, ob das Blatt die Frage voll, teilweise oder gar
  nicht abdeckt. Standardschritt der Vorbereitung: bauen, sobald das Blatt eine erste
  vollständige Fassung hat, ohne nachzufragen und neben dem Lernen (die Zuordnung
  machen Subagenten). Danach dem User die Seite im Browser öffnen und die Zahlen
  nennen. Die Fragen mit „teilweise“ und „keine“ zeigen, was aufs Blatt fehlt oder
  auswendig sitzen muss; ergänzt wird das Blatt nur nach dem Ja des Users. Nach jeder
  Änderung am Blatt neu bauen. Werkzeug, Vorgehen und Datenformat: `blatt_finder.py
  --help`, der Pfad steht in der Startnachricht der Session. Fragen und Zuordnung
  liegen als `blatt_finder_map.json` daneben.

## Lern-Loop (der Kern)

**0. Arbeitsmedium** — kommt vom Launcher, nicht aus dieser Datei: der Umschalter
im `studyclaude`-Startmenü (`m`) bestimmt Xournal++ oder Tutor Board, und die Mechanik
des aktiven Mediums steht im Systemprompt der Session. **Nicht erfragen.** Der
User darf **mitten im Lernen wechseln** („lass uns aufs Board", „zurück zu
Xournal") — dann ab dem nächsten Häppchen im neuen Medium weiterarbeiten und ihn
erinnern, fürs nächste Mal den Schalter im Menü umzulegen.

**0b. Kursübersicht** — ohne bestätigte Übersicht (§Kursübersicht, Zeile in
`todo.md`) kein Häppchen: erst bauen bzw. nachziehen, bestätigen lassen, buchen.

**1. Lern-Set öffnen** — auf „lass uns lernen" das Arbeitsfenster des aktiven
Mediums öffnen (wie im Systemprompt beschrieben, ohne nachzufragen) plus
Referenz-/Mitnehm-Blätter und die zuletzt geänderte Übung.

**2. Häppchen-Prinzip** — personalisierte Übungen als **kleine 5–10-min-Einzelaufgaben**,
die durch die Themen der Themenkarte oben **rotieren** — NICHT große Multi-Aufgaben-Blätter
(die wirken erschlagend und verhindern den Einstieg). Verbindliche Design-Regeln:
- **Knapp:** EINE Aufgabe, max. ~2 Teilaufgaben, wenig Fließtext. Zwei Themen ⇒ zwei Häppchen.
- **Lösungsfrei:** das Blatt trägt NUR Aufgabe + ggf. EINEN Hinweis — NIE die Lösung/
  Musterkette. Sonst misst das Review nichts.
- **Drei Stufen, in dieser Reihenfolge: G → S → K.** Die ersten Häppchen eines Kurses
  sind **Grundlagen-Drills (G)**: Lehrtext in zwei Sätzen plus 8–10 Einzeiler zu
  Einheiten, Präfixen, Zehnerpotenzen, Formel umstellen, „welche Formel wann". Ziel
  unter 5 min; **flüssig** heißt zwei Runden in Folge mit höchstens einem Fehler,
  sonst eine neue Runde mit neuen Zahlen. Dann **geführte Klausurtypen (S)**: jede
  Aufgabe in 4–5 einzeln geprüften Feldern (SI-Zeile → Formel → Zwischenwert →
  Endwert). Erst dann **Klausurformat (K)**: die Aufgabe wörtlich wie in Klausur oder
  Übungsblatt. Nicht zu K springen, solange G nicht sitzt. Eine Klausuraufgabe mit
  0 von 5 misst nur, dass Grundlagen fehlen (EP2 2026: die Fehler saßen in Präfixen
  und „mal statt geteilt", nicht in der Physik; eine 5-min-Aufgabe dauerte 30 min).
- **Rechnen, nicht Theorie, wo die Prüfung rechnet:** G-Drills wie S- und K-Aufgaben
  sind dann Rechenaufgaben, Theorie/Definitionen nur als fertige Merksätze aufs
  Cheatsheet. Fragt die Prüfung Wissen ab, folgt das Häppchen ihrem Format
  (§Format folgt der Prüfung).
- **Distraktoren und Hinweise aus `fehlermuster.md`**, bei jedem Häppchen: der falsche
  Weg, den der User wirklich geht, ist die beste Falle.
- **„Nennen Sie n" heißt alle n.** Im Review zählt Vollzähligkeit; eine fehlende
  Nennung ist ein Fehler, auch wenn der Rest stimmt.
- **Konzeptlücken erst prüfen:** bei neuen Themen nicht Bekanntheit voraussetzen — 1–2-
  Satz-Konzeptintro, Notation ausschreiben (z.B. ⟨a,b⟩ = a₁b₁+a₂b₂).
- **Bild beim Bauen entscheiden:** zu jedem Häppchen nach der Eckdaten-Zeile
  `Visualisierung`, wie im Systemprompt beschrieben, und die Entscheidung in
  `todo.md` beim Häppchen als Zeile `Bild: …` buchen, bei keinem Bild mit Grund.
- **Ablauf:** eine Mini-Aufgabe → User löst sie mit Zwischenschritten im aktiven Medium →
  gibt ab (wie, steht im Systemprompt) → gezieltes Review → nächstes Häppchen (nächster Typ).
- **Neues Häppchen sofort selbst öffnen**, nicht nachfragen — im aktiven Medium,
  wie im Systemprompt beschrieben.

**2b. Quiz-Häppchen — Wissensabfragen laufen IM Loop, nie extern.** Externe
Quiz-Generatoren (NotebookLM & Co.) sieht der Tutor nie: Antworten und bewiesenes
Wissen gehen für Fehlermuster + Fortschritt verloren. Wissensabfragen daher als
eigenes Häppchen hier im Loop:
- **Format zuerst prüfen — Choice-Framing ist nicht automatisch richtig.** Gut für
  Single/Multiple Choice: Erkennen und Unterscheiden (Definitionen, Notation, „welche
  Aussage gilt"), schnelle Konzept-Checks vor einem neuen Thema, Faktenwissen im
  mündlich-Modus. Falsch für alles mit Rechenweg/Herleitung — dort misst MC nur
  Ausschlussdenken; das bleibt ein Rechen-Häppchen. Im Zweifel offene Frage statt
  Optionen. Stellt die Prüfung selbst Multiple Choice, ist MC das richtige Format
  (§Format folgt der Prüfung).
- **Umsetzung im aktiven Medium** (s. Systemprompt): AskUserQuestion-Runden im Chat
  bzw. ein eigener Quiz-Tab auf dem Board. Distraktoren aus `fehlermuster.md` (§2).
- **Nachbereitung wie jedes Review:** falsche Antworten → `fehlermuster.md` (Zitat →
  warum falsch → was stattdessen); ein Quiz zählt als Häppchen in der
  `Fortschritt:`-Zeile.

**3. Review-Regel (verbindlich): Fehler SICHTBAR am Blatt des Users zeigen**, nicht nur
loggen — wie, steht in der Medium-Mechanik im Systemprompt (annotiertes PNG bzw.
Korrektur am Board-Tab direkt unter der jeweiligen Aufgabe). Zusätzlich im Chat explizit durchgehen (Zitat → warum falsch →
was stattdessen). Erst danach das nächste Häppchen. Fragt der User eine Diagnose
nach, die Diagnose prüfen statt verteidigen: war sie falsch, am Blatt und in
`fehlermuster.md` mit Datum richtigstellen (EP2 2026, Muster 17b: ein selbst
hergeleiteter Faktor ½ war als Fehler gewertet worden). Jedes Review auch in
`fehlermuster.md` (Rangliste umsortieren, Beleg anhängen; + ggf. situative Docs,
falls angelegt), und die Zeile
`Fortschritt: x/y Häppchen` in `todo.md` mitziehen (x hochzählen, y neu schätzen).

**3b. Wiederholungs-Häppchen** — ein Muster in `fehlermuster.md` gilt erst als
repariert, wenn ein späteres Häppchen es ohne Hinweis abfragt und der User es richtig
macht. Dafür regelmäßig ein gemischtes Häppchen nur aus Posten, die schon einmal falsch
waren, ohne neuen Stoff; spätestens in der letzten Woche vor der Klausur. Es zählt als
Häppchen, Review wie üblich. (Datenerfassung 2026: Schluss-Drill „was fehlte" am Klausurmorgen,
fünf Runden über alle vier Teile.)

**Format folgt der Prüfung** — das Häppchen übt in dem Format, in dem die Prüfung
fragt. Hat die Prüfung Teile mit verschiedenem Format, gilt das je Teil (Eckdaten).
- **Rechnen/Herleiten** → der Häppchen-Rechen-Loop wie oben.
- **Freitext/Stichworte** → die Frage im Klausurwortlaut, die Antwort in Stichworten
  wie in der Klausur; Review gegen eine Modellantwort mit Quellbeleg.
- **Multiple Choice** → Drills im Originalstil, je Frage mit der Angabe „genau eine"
  oder „mehrere richtige Antworten". Das Ankreuzen wird mitgeübt: die Angabe zuerst
  lesen, nie eine Frage ohne Kreuz lassen, bei „mehrere" jedes weitere Kreuz nur mit
  einem Grund. Zu jedem Kreuz ein Begründungsfeld für einen Halbsatz; das Review liest
  die Begründung mit (Datenerfassung 2026: mit ausgefüllter Begründung 1/1 richtig, ohne 0/5).
- **mündlich** → Laut-erklären-Loop: Begründungen laut formulieren, auf Schlüsselwörter
  bestehen. Rechnen üben hilft dort wenig.

## Terminal-Regel

Chat-Erklärungen **OHNE LaTeX** — kein `$...$`, kein `\frac`. Unicode-Notation
(√, x², ∫, ≤, λ, x_1, Brüche als (a+b)/c). LaTeX gehört nur in die `.tex`-Häppchen.

## Building the LaTeX (falls Häppchen als PDF)

`pdflatex -interaction=nonstopmode haeppchen_NN.tex`. `.aux`/`.log` sind Wegwerf-
Nebenprodukte. Nach dem Klausurdatum wird dieser Workspace vom User archiviert;
die Session ändert daran nichts.
