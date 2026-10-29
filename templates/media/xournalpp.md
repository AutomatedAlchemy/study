# Arbeitsmedium-Mechanik: Xournal++ + Firefox

- Die Aufgabe liegt als `.tex` → PDF, in **Firefox** geöffnet. Gerechnet wird in
  einem **eigenen** `.xopp`-Rechenblatt (`xournalpp <datei> &`) in
  `Personalisierte_Übungen/` — das letzte fortsetzen oder, wenn keins existiert
  oder das letzte voll ist, ein neues leeres anlegen. Zwei Fenster nebeneinander.
- ⛔ **Nie in das Häppchen-PDF hineinschreiben.** Das PDF ist die Aufgabe
  (lesen), das `.xopp` ist der Rechenweg (schreiben). Eine Annotationsschicht
  über dem Aufgaben-PDF ist ausdrücklich **kein** Modus.
- **Lern-Set öffnen** („lass uns lernen"): Referenz-/Mitnehm-Blätter + die
  zuletzt geänderte Übung in Firefox + das aktuelle `.xopp` in Xournal++.
- **Kursübersicht** (§Kursübersicht der Kurs-CLAUDE.md): ein aufgabenfreies
  Lesedokument `kursuebersicht.tex` → PDF im Kurs-Ordner, sofort in Firefox
  öffnen; die Bestätigung kommt im Chat, dann die Zeile in `todo.md`.
- **Bild im Häppchen:** beim Bauen eine Skizze (TikZ/pgfplots) ins PDF setzen,
  nach der Eckdaten-Zeile `Visualisierung` der Kurs-CLAUDE.md (fehlt sie: `mittel`).
  `viel` = in jedem Häppchen, `mittel` = wo das Thema eine Kurve, ein Diagramm,
  eine Geometrie oder eine Struktur hat, `wenig` = nur wo die Prüfung ein Diagramm
  zeichnen oder ablesen lässt, `keine` = nur auf Wunsch. Nie das, was die Aufgabe
  zeichnen lässt. In `todo.md` beim Häppchen `Bild: Skizze` oder
  `Bild: keins (<Grund>)`.
- **Neues Häppchen:** das PDF sofort selbst in Firefox öffnen, nicht nachfragen.
- **Abgabe:** der User sagt Bescheid, wenn er fertig ist; gelesen wird das
  gespeicherte `.xopp` (bei Papier das Foto/der Scan).
- **Review, Export:** das neueste `.xopp` zu PNG machen —
  `xournalpp --create-img=<out.png> <datei.xopp>` (mehrseitig: eine Datei je Seite).
- **Review, Annotieren:** Fehlerstellen rot einkreisen/nummerieren, Legende
  (rot = Fehler mit Korrektur, grün = neu Gemeistertes) in den Freiraum darunter
  — mit Python/Pillow (`PIL.ImageDraw`) oder `convert`. Als
  `haeppchen_NN_reviewt.png` in `Personalisierte_Übungen/` speichern und
  **sofort in Firefox öffnen**.
- **Quiz-Häppchen:** per AskUserQuestion-Tool im Chat (1–4 Fragen pro Runde,
  je max. 4 Optionen).
- **Papier-Variante auf Zuruf** („ich rechne auf Papier"): PDF gedruckt oder in
  Firefox, gerechnet auf Papier, Review über Foto/Scan → annotiertes PNG.
