# Arbeitsmedium-Mechanik: Tutor Board

**Voraussetzung:** Das Board braucht ein Tutor-Board-Konto (Einladung nötig,
beta.probable.work). Die MCP-Verbindung wird außerhalb von studyclaude
konfiguriert.

**Bedienung des Boards:** den Tool-Beschreibungen und den Server-Instructions des
Tutor-Board-MCP folgen. Diese Datei sagt nur, was der Lern-Loop auf dem Board haben
will. Bei Widerspruch gewinnt der Server; eine Eigenheit des Servers wird dort
beschrieben oder behoben, nicht hier umschifft.

## Ankommen (in dieser Reihenfolge, ohne nachzufragen)

1. Ein Kurs = ein Board, benannt nach dem Kurs. Gibt es keins, eines anlegen.
   **Nie auf dem Board eines anderen Kurses bauen.** Mehrere Lern-Sessions laufen
   oft parallel auf demselben Konto: vor jedem schreibenden Call prüfen, dass das
   gewählte Board noch das eigene ist.
2. Den User aufs Board holen: erst über das Board selbst einladen, und nur wenn
   niemand zuschaut, Firefox auf die konkrete Board-URL öffnen, nicht auf die
   Startseite.
3. Ankunftsbericht lesen: gibt es ungelesene Abgaben, **zuerst reviewen**, bevor
   irgendetwas Neues entsteht. Ein bereits ausgegebenes, aber ungerechnetes
   Häppchen wird **wieder vorgelegt, nicht ersetzt**.

## Struktur (verbindlich)

- **Tab 0 = „Übersicht"** — die Kursübersicht (§Kursübersicht der Kurs-CLAUDE.md),
  siehe den Abschnitt unten. Fehlt der Tab, **jetzt** anlegen und an Position 0 holen.
- **Angepinnt: „Fortschritt"** — kurzer Spiegel von `todo.md`/`fehlermuster.md`,
  nicht deren Ersatz, siehe §„Fortschritt". Angepinnte Tabs stehen rechts in der
  Leiste und bleiben sichtbar, wie lang die Leiste auch wird. Fehlt der Tab, **jetzt**
  mit `create_tab(pinned: true, select: false)` anlegen.
- **Angepinnt: „Hilfsmittel"** — nur wenn die Klausur Hilfsmittel erlaubt, siehe
  §„Hilfsmittel".
- **Sonst wird nichts angepinnt.** Häppchen und Quiz nie.
- **Jeder weitere Tab = genau EIN Häppchen.** Titel kurz und referenzierbar
  (`H03 …`); der ganze Satz gehört in die Tab-Beschreibung.
- **Quiz-Häppchen** als eigener Tab (`Q01 <Thema>`), eine Frage pro Block,
  geantwortet wird im selben Tab.

## Blöcke bauen

- **Formeln in `markdown`-Blöcke**, dort rendert LaTeX.
- **Antwortformat vor Freitext-Mathe bevorzugen**: Zahlenfelder mit vorgedruckter
  Form, oder `radio`. Exponenten zu tippen frisst mehr Zeit als das Rechnen, und
  ein Radio hat kein leeres Feld, in dem man sich verstecken kann.
- **Antworten in Textfeldern, den Canvas nur für echte 2D-Antworten** (Skizzen,
  Richtungsfelder, Schaltbilder), nie für Formeln oder Rechenwege.
- **Wunde Stellen in Einzelfelder zerlegen** (Vorzeichen, Vorfaktor, Exponent
  getrennt) und in jedem Schritt den Wert neu hinschreiben, statt auf die Zeile
  darüber zu verweisen — sonst wird die Zahl von oben durchgereicht.
- **Jede Aufgabe endet mit einem `submit`-Knopf mit Antwortschlüssel**, sobald die
  Antworten objektiv prüfbar sind. Der Schlüssel ist Teil der Aufgabe: vor dem
  `select_tab` jeden Eintrag selbst nachrechnen und die Zuordnung Feld → Wert
  prüfen. Ein falscher Schlüssel markiert eine richtige Abgabe als falsch und
  verfälscht das Fehlermuster. Gleichwertige Schreibweisen als Liste angeben.
- **Unter jeder Aufgabe ein Korrektur-Platzhalter** (Nutzervorgabe 23.09.2026):
  direkt nach ihrem letzten Block (Knopf oder Eingabefeld), vor der nächsten
  Aufgabe, ein Markdown-Block mit der Id `<aufgabe>_korrektur`, der bis zum
  Review nur „—“ enthält. Neue Blöcke landen immer am Tabende;
  nur ein Platzhalter, der schon beim Bauen an seiner Stelle steht, bringt die
  Korrektur später direkt unter die Aufgabe. Das gilt für jede Aufgabe, auch ohne
  Schlüssel und auch in Tabs mit nur einer Aufgabe.

## Bild zu jedem Inhalts-Tab (Nutzervorgabe 17.09. und 29.10.2026)

Gilt für jeden Tab mit Lernstoff: Häppchen, Quiz, Begleitung, Vor- und
Nachbereitung einer Veranstaltung. Nicht für Übersicht, Fortschritt, Hilfsmittel
und Plan-Tabs. Entschieden wird beim Bauen des Tabs, nicht danach.

**Die Stufe** steht in den Eckdaten der Kurs-CLAUDE.md, Zeile `Visualisierung`.
Fehlt die Zeile, gilt `mittel`. Ausnahmen je Thema in derselben Zeile gehen vor.

| Stufe | Skizze | Clip |
|---|---|---|
| viel | in jedem Inhalts-Tab | zu jeder neuen Idee, in der sich etwas bewegt oder verändert |
| mittel | wo das Thema eine Kurve, ein Diagramm, eine Geometrie oder eine Struktur hat | zu einem neuen Konzept mit Bewegung |
| wenig | nur wo die Prüfung ein Diagramm zeichnen oder ablesen lässt | nur auf Wunsch |
| keine | nur auf Wunsch | nur auf Wunsch |

Sagt der User „mehr Bilder“ oder „weniger“, wird die Zeile in den Eckdaten
geändert.

**Zwei Formen:**
- **Skizze**: ein stehendes Bild im Tab (Kurve, Diagramm, Strukturbild,
  Strahlengang), selbst gebaut, klein neben dem Block, zu dem es gehört. Sie zeigt
  nie, was die Aufgabe zeichnen oder ablesen lässt, sonst misst das Review nichts;
  diese Skizze kommt erst mit der Korrektur.
- **Clip**: ein vertontes Erklärvideo, Mechanik in §„Clip“.

**Reihenfolge:** Tab samt Skizze bauen, im Fortschritt eintragen, Clip anstoßen,
die `Bild:`-Zeile buchen (unten), übergeben (§„Häppchen übergeben“), warten.
Der Clip zum aktuellen Tab ist kein
Vorbauen: er wird gestartet, bevor der Wait beginnt, und läuft im Hintergrund.
Der User wartet nie auf einen Render. Ist der Clip fertig, hängt ihn der
Hauptkontext als Video-Block unten an denselben Tab.

**Entscheidung buchen:** in `todo.md` beim Eintrag des Tabs eine Zeile
`Bild: Skizze`, `Bild: Clip`, `Bild: Skizze + Clip` oder
`Bild: keins (<Grund in wenigen Wörtern>)`. Ein Tab ohne diese Zeile ist nicht
fertig gebaut. Gehört der Tab zu keinem Kurs (eine Veranstaltung ohne Kursordner),
gilt `mittel` und die Zeile entfällt; dafür wird keine Datei angelegt. (Bis 29.10.2026 bekamen 4 von 25 Inhalts-Tabs einen Clip, und
keine Session hat je gesagt, warum sie keinen gebaut hat.)

## Kursübersicht (Tab 0)

Tab 0 ist der eine Übersichts-Tab des Kurses — der Vertrag aus §Kursübersicht der
Kurs-CLAUDE.md. Der Fortschritt steht im angepinnten Tab „Fortschritt". Reihenfolge
der Blöcke:

1. **Prüfung** — Eckdaten, Format, Bestehen.
2. **Themen erklärt** — je Thema Idee, Prüfungsanforderung, Notation, Falle,
   Material, höchstens 6 Sätze. Formeln in `markdown`-Blöcke.
3. **Materialien** — jede Datei mit Pfad und einem Halbsatz beschrieben. Fotos
   als Bild-Block, einzelne PDF-Seiten nur situativ im Häppchen, das sie braucht
   (als PNG gerendert), nie ganze Skripte.
4. **Vereinbarung** — drin / nicht drin / offene Fragen. Darunter genau EIN
   `submit`-Knopf („Gelesen & einverstanden"); sonst **keine Eingabefelder** im Tab.

Bestätigung: auf den Klick warten (§„Auf den User warten"); sagt der User es
im Chat, gilt das genauso. Danach in `todo.md`
`Übersicht: bestätigt YYYY-MM-DD` eintragen und erst dann das erste Häppchen.

**Tab 0 wird immer an Ort und Stelle geändert**, auch beim Umbau: Blöcke mit
`update_block` ersetzen, mit `append_blocks` ergänzen, mit `remove_block`
entfernen. Kein `show_board`/`clear_board` für eine Änderung an einem Tab — das
setzt das ganze Board zurück. `clear_board` nur für ein leeres oder für ein
falsch aufgebautes Board.

Nachziehen bei einem Board, dessen Tab 0 bisher nur der Fortschrittsspiegel war:
die fehlenden Blöcke ergänzen und in die Reihenfolge oben bringen. Trägt Tab 0 noch
eine Themenkarte mit Fortschritt, wandert sie in den Tab „Fortschritt" und wird aus
Tab 0 mit `remove_block` entfernt.

## Fortschritt (angepinnt)

So kurz, dass er ohne Scrollen passt. Genau diese Blöcke, sonst nichts:

1. Eine Tabelle `Thema | Stand | Häppchen`: je Zeile der Themenkarte eine Ampel
   (🔴/🟡/🟢) und die zugehörigen Häppchen als Kürzel (`H03`). Die Legende passt
   in eine Zeile darunter.
2. Die höchstens drei obersten offenen Muster aus `fehlermuster.md`, je eine Zeile.
3. Die Zeile `Fortschritt: x/y Häppchen`.

Keine Eingabefelder, keine Erklärungen, keine Bilder. Nach jedem Review und beim
Anlegen eines Häppchens per `update_block` nachziehen, ohne `select_tab`.

## Hilfsmittel (angepinnt)

Der Tab zeigt genau das, was in der Klausur auf dem Tisch liegt, damit mit
denselben Hilfsmitteln geübt wird. Ob es ihn gibt, sagt das Feld `Hilfsmittel` der
Eckdaten:

- **Eigenes Blatt erlaubt** (z.B. handschriftliche A4-Seiten): der Tab spiegelt das
  Mitnehm-Blatt des Kurses (Ort laut Kurs-CLAUDE.md). Die Datei bleibt die Quelle;
  eine Änderung kommt erst in die Datei, dann auf den Tab.
- **Ausgeteilte Unterlage** (Formelsammlung, Periodensystem, Tabelle): der Tab
  enthält genau diese, als Bild oder Markdown.
- **Keine Hilfsmittel**: kein Tab. Ein ständig sichtbarer Spickzettel würde das
  Üben von „welche Formel wann" aushebeln.
- **Noch offen**: kein Tab, bis es feststeht.

Keine Eingabefelder. Änderungen an Ort und Stelle per `update_block`/`append_blocks`,
ohne `select_tab`. Eine Korrektur darf auf den Tab verweisen („steht in
*Hilfsmittel*"), statt die Formel zu wiederholen.

## Häppchen übergeben und einsammeln

- **Ein Häppchen zur Zeit.** Das nächste wird erst gebaut, wenn das aktuelle
  abgegeben und reviewt ist; Wartezeit wird nicht mit Vorbauen gefüllt (das Bild
  zum aktuellen Tab ist kein Vorbauen, §„Bild zu jedem Inhalts-Tab“). Liegt ein
  Tab ungerechnet, wird er wieder vorgelegt (§Ankommen), nicht durch einen neuen
  ersetzt. (EP2 2026: drei offene Tabs nebeneinander, eines davon drei Tage
  ungerechnet; User: „räum die Tabs mal auf".)
- Bauen immer mit `create_tab(select: false)`, samt Bild und `Bild:`-Zeile
  (§„Bild zu jedem Inhalts-Tab“), und im Fortschritt eintragen. Wann
  der User auf den neuen Tab kommt, hängt davon ab, wo er gerade ist:
  - **Erstes Häppchen der Session** (er kommt gerade an): danach `select_tab`.
  - **Häppchen nach einem Review:** kein `select_tab`. Er liest gerade die
    Korrektur, und der Wechsel nähme sie ihm weg (User 24.10.2026: „du bewegst
    mich immer zum nächsten tab bevor ich mir deine korrektur anschauen
    konnte"). Am Ende des korrigierten Tabs steht genau EIN `submit`-Knopf
    „Weiter → H03"; erst sein Klick löst `select_tab` aus. Wechselt er selbst,
    gilt das genauso.
- Danach auf die Abgabe warten, siehe §„Auf den User warten". Der Clip zum Tab
  ist zu diesem Zeitpunkt schon angestoßen.

## Auf den User warten

Gilt für jeden Wait: Übersichts-Bestätigung, Häppchen-Abgabe, „Noch eins?".

- Warten, wie der MCP es beschreibt (bevorzugt der Weg, der keine Modellaufrufe
  kostet). Nach dem Aufwachen sagt das Ereignis, ob der User geklickt oder
  geschrieben hat; entsprechend Board oder Chat lesen.
- **Den Wait als Monitor führen, nicht als Hintergrund-Shell.** Claude Code
  räumt Hintergrund-Shells ab, sobald der Kernel Speicherdruck meldet
  („stopped because the system is running low on memory"), und das trifft auf
  diesem Host auch bei mehreren freien GB zu. Monitore sind davon ausgenommen.
  `persistent` setzen, damit auch das Zeitlimit des Monitors nicht dazwischen
  kommt. Vom Stream nur die Ereigniszeile durchlassen und die Zeilen wegfiltern,
  die bloß die Verbindung offen halten — kommt jede davon als Meldung an, stoppt
  der Monitor wegen zu vieler Meldungen.
- **Wird der Wait trotzdem beendet, ohne gefeuert zu haben**: einmal das Board
  lesen — oft liegt die Abgabe längst vor; sonst den Wait höchstens **zweimal**
  neu starten; danach dem User in einem Satz sagen, dass er sich nach dem Abgeben
  kurz melden soll. Keine dritte Runde.
- Stirbt der Wait wiederholt, den Wait im Modellkontext nehmen, den der MCP als
  Rückfallebene anbietet — nicht als Standard.

## Review

- Abgaben samt Score vom Board lesen. Trägt der Tab eine Zeichnung, sie holen —
  **nie über eine ungesehene Zeichnung raten**.
- Die Korrektur **am selben Tab, direkt unter der Aufgabe** zeigen, nicht nur im
  Chat und nie gesammelt am Tabende: Zitat → warum falsch → was stattdessen,
  **je Fehler höchstens fünf Sätze**. Jede Aufgabe bekommt ihre eigene Korrektur,
  eine richtig gelöste ein kurzes „✓“. Sie kommt per `update_block` in den
  Platzhalter `<aufgabe>_korrektur`; der `submit`-Knopf der Aufgabe darf
  stattdessen ersetzt werden, er steht an derselben Stelle (Nutzervorgabe
  19.09. und 23.09.2026). Die Eingaben des Users bleiben stehen.
- Ältere Tabs ohne Platzhalter: die Korrektur in den `submit`-Knopf der Aufgabe
  setzen. Hat die Aufgabe keinen, die Korrektur vor den Text des Blocks setzen,
  mit dem die nächste Aufgabe beginnt, abgesetzt durch eine Linie. Nur bei der
  letzten Aufgabe darf sie angehängt werden, denn das Tabende ist dort direkt
  unter der Aufgabe.
- Ist der Score falsch, weil der Schlüssel falsch war, das auf dem Board
  richtigstellen und dem User sagen.
- Danach den Tab „Fortschritt" per `update_block` nachziehen (Ampeln,
  Häppchen, offene Muster, `Fortschritt:`-Zeile), bei erlaubten Hilfsmitteln auch
  den Tab „Hilfsmittel". Fertig reviewte Tabs **bleiben auf der
  Leiste**, samt Korrektur: der User will sie weiter sehen. Archivieren nur auf
  ausdrückliche Bitte; der Eintrag im Fortschritt bleibt in jedem Fall.

## Clip

Wann ein Tab einen Clip bekommt, sagt §„Bild zu jedem Inhalts-Tab“. Ein Clip
trägt eine Idee, in der sich etwas bewegt: eine Funktion, die sich verändert, eine
Ableitung als Tangente, ein Vektor, der sich dreht, eine Konvergenz, eine Skizze,
die entsteht.

- **Per Sonnet-Subagent, nicht im eigenen Kontext** (Token-Sparsamkeit; Nutzervorgabe 08.10.2026: Subagenten nie auf Opus): `Agent` mit
  `model: sonnet`, Auftrag = Skill `manim-kit` laden, eine Szene, 15–25 s, eine Idee,
  **1080p bei 60 fps** (`-q h`, manim-kit-Standard; Nutzervorgabe 18.09.2026, nie Draft-Qualität), unter 8 MB je Clip (längere Videos als Einzelclips, nicht herunterkomprimieren), die Standard-Tonspur/Musik des manim-kit **nicht** abbestellen;
  Rückgabe **nur** der mp4-Pfad (oder
  `RENDER FAILED: <Grund>`).
- **Immer mit Voiceover** (Nutzervorgabe 18.09.2026): der Clip wird als `VoiceoverScene`
  gebaut (`manim-kit new NAME --template narrated`), jede Animation in einem
  `with self.voiceover(...)`-Block, der die Idee in ein bis zwei Sätzen sagt — nicht die
  Beschriftung vorlesen, sondern erklären, was gerade passiert. Stimme:
  **`kokoro-v1:af_sarah`** (offline, kostenlos, englisch). Eine offline-deutsche Stimme
  gibt es in dieser Version nicht; die bezahlte `gemini-flash-tts:Aoede:de` hat der User
  am 18.09. abgelehnt („Englisch, kostenlos"). Vor dem ersten Clip je Host einmal
  `manim-kit voice setup` (354 MB Modell). Die Musik mischt manim-kit bei Narration
  automatisch unter die Stimme — nichts extra einstellen. Der Hauptkontext lädt das mp4 hoch
  und hängt es als Video-Block unten an denselben Tab.
- **Fail into silence:** scheitert der Render, bleibt es beim Textblock; kein Hinweis an
  den User, keine zweite Runde, in `todo.md` `Bild: Clip gescheitert`. `manim-kit
  doctor` einmal pro Host.
- **Nie in die Übersicht und nie in angepinnte Tabs.** Ein Clip an einer Korrektur (wiederkehrendes, geometrisches
  Fehlermuster) bleibt zusätzlich erlaubt, gleiche Mechanik.

## „Noch eins?“ (Quickie)

Gilt nur im Quickie-Modus. Im Lern-Loop ist das nächste Häppchen beim Klick schon
gebaut, der Knopf heißt dort „Weiter → Hxx" (§„Häppchen übergeben").

Die Frage nach dem nächsten Quickie gehört **aufs Board, nicht ins Terminal** —
der User schaut ohnehin dorthin, und ein Klick ist billiger als eine getippte
Antwort.

- Ans Ende des Häppchen-Tabs, unter die letzte Aufgabe und ihre Korrektur, genau EINEN
  `submit`-Knopf („Noch eins?“). Kein Gegenstück zum Ablehnen — wer aufhören
  will, klickt einfach nicht oder sagt es im Chat; ein „für heute reicht's“-Knopf
  macht das Aufhören zur angebotenen Option und arbeitet gegen die Gewohnheit.
- Danach auf den Klick warten (§„Auf den User warten"). Kommt der Klick, folgt
  das nächste Häppchen als neuer Tab; bleibt er aus oder sagt der User ab, ein
  Satz Abschied.
- Antwortet er stattdessen im Chat, gilt das genauso — den Knopf dann nicht
  wiederholen.
