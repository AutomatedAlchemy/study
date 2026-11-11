# Lernkarten im Scroller-Feed

Vertrag zwischen den Lern-Sessions von studyclaude (schreiben Karten, lesen Antworten) und
GifScroll (ein täglicher Job nimmt Karten auf, die App auf dem Handy fragt ab und
exportiert Antworten). Angelegt 2026-11-09 nach Wahl des Users: Transport über den
Feed-Ordner (offline), Zählregel „Beleg + Reparatur-Probe“.

Der Feed-Ordner ist der, den `--set-feed` (oder `STUDY_FEED_DIR`) nennt. Er wird zwischen
den Rechnern der Lern-Sessions, dem Rechner des Jobs und dem Handy synchronisiert. Ist er
gesetzt und auf dem Host vorhanden, bekommt jede Session den Block `<feed_lernkarten>`,
der auf diese Datei verweist.

## Ablage

| Was | Wo | Wer schreibt |
|---|---|---|
| Karten | `<Feed>/lernkarten/<Kurs>/<YYYYMMDD-HHMM>-<slug>.json` | Lern-Session, eine neue Datei je Review |
| Antworten | `<Feed>/lernkarten_antworten/<Kurs>.jsonl` | nur der GifScroll-Job, nur anhängen |

`<Kurs>` ist der Name des Kursordners (`AMW_I`, `Mathe-Handwerk`). Eine Kartendatei wird
nach dem Schreiben nie geändert und nie ergänzt. Mehrere Sessions laufen parallel auf
verschiedenen Rechnern, und eine gemeinsame Datei würde Sync-Konflikte erzeugen.

## Kartendatei

Jede Karte ist eine Karte des `cards`-Blocks des Tutor Boards (Felder `front`, `back`,
`input`, `answer`, siehe `services/tutor-board/README.md` § cards) plus vier Zusatzfelder.
Ohne die Zusatzfelder geht dieselbe Karte unverändert in einen Kartenstapel auf dem Board.

```json
{
  "kurs": "AMW_I",
  "created_at": "2026-11-09T16:40:00+01:00",
  "quelle": "Review Q01 vom 2026-10-19",
  "cards": [
    {
      "id": "AMW_I-20261109-1640-1",
      "muster": 1,
      "thema": "P8",
      "hinweis": false,
      "front": "Flory-Huggins, $\\chi_{crit} = 2/N$: welches System entmischt schon bei der kleinsten Abstoßung?",
      "input": {"widget": "radio", "options": ["zwei kleine Moleküle, N = 1", "zwei Polymere, N = 1000", "beide gleich"]},
      "answer": "zwei Polymere, N = 1000",
      "back": "$\\chi_{crit} = 2/N$ ist für N = 1000 nur 0,002, für N = 1 aber 2. Die Mischungsentropie pro Gitterplatz sinkt mit 1/N, deshalb reicht bei Polymeren schon eine winzige Abstoßung."
    },
    {
      "id": "AMW_I-20261109-1640-2",
      "muster": 1,
      "thema": "P8",
      "hinweis": false,
      "front": "Symmetrischer Blend mit $N = 500$. $\\chi_{crit} = {?}$",
      "input": {"widget": "number"},
      "answer": 0.004,
      "back": "$\\chi_{crit} = 2/N = 2/500 = 0{,}004$."
    }
  ]
}
```

| Feld | Regel |
|---|---|
| `id` | `<Kurs>-<YYYYMMDD-HHMM>-<n>`, eindeutig |
| `muster` | Nummer aus `## Aktive Muster` in `fehlermuster.md` des Kurses, oder `null` |
| `thema` | Kürzel der Themenkarte (`P8`, `H03`) |
| `hinweis` | `true`, wenn die Vorderseite auf die Antwort hinführt. So eine Karte zählt nie als Reparatur-Probe |
| `front` | Markdown + KaTeX, höchstens etwa 300 Zeichen, höchstens eine abgesetzte Formel. Muss ohne Scrollen auf einen Handybildschirm passen. Bei `word` darf es das Wort nicht enthalten |
| `input.widget` | `radio`, `select`, `number` oder `word` (Worträtsel, Regeln unten). `text` vorerst nicht, weil Freitext auf dem Handy nicht zuverlässig bewertet wird |
| `answer` | bei `radio`/`select` der genaue Optionstext, bei `number` eine Zahl, bei `word` das gesuchte Wort. Eine Liste heißt: jede davon gilt (nicht bei `word`) |
| `back` | die Erklärung nach dem Antworten, höchstens 3 Sätze |

### Worträtsel (`input.widget: "word"`)

Der Nutzer rät das Wort in mehreren Versuchen und bekommt nach jedem Versuch eine
Rückmeldung je Buchstabe. `front` ist der Hinweis, `answer` das Wort, `back` die Erklärung.
Das Wort steht weder in `front` noch sonst auf der Vorderseite.

```json
{"id": "AMW_I-20261111-0900-1", "muster": 3, "thema": "P8", "hinweis": false,
 "front": "Anderer Name für einen Stoff, der sich im Blend nicht mischt: 8 Buchstaben.",
 "input": {"widget": "word", "tries": 6}, "answer": "ENTMISCHT", "back": "…"}
```

- Alphabet: A–Z sowie Ä Ö Ü. Kein ß (als SS schreiben), keine Ziffern, kein Bindestrich.
  Gespeichert wird in Großbuchstaben, NFC-normalisiert. Groß- und Kleinschreibung der Eingabe
  ist egal.
- Länge des Wortes: 3 bis 12 Buchstaben.
- `input.tries`: Zahl der Versuche, 1 bis 10, optional, Vorgabe 6.
- Kein Wörterbuch. Jede Buchstabenfolge der richtigen Länge gilt als Versuch.
- Rückmeldung je Buchstabe in zwei Durchgängen: zuerst die exakten Treffer, danach „kommt
  vor“ nur, solange der Buchstabe im Wort noch übrig ist.
- `options` und `scale` sind bei `word` nicht erlaubt.

Für die Session, die schreibt:
- 1 bis 2 Karten je Review, nur zu einem Fehler, der in diesem Review als Beleg gebucht wurde.
- Ein Distraktor ist der falsche Weg, den der User wirklich gegangen ist (Zitat aus dem Beleg).
- Jeden Schlüssel vorher selbst nachrechnen, wie beim Board.
- Keine Karte zu Stoff, der noch nicht in einem Häppchen dran war.

## Antwortdatei

Eine JSON-Zeile je Antwort, angehängt vom GifScroll-Job:

```json
{"card": "AMW_I-20261109-1640-2", "kurs": "AMW_I", "muster": 1, "answered_at": "2026-11-10T08:12:33+01:00", "value": "0,04", "correct": false, "first": true}
```

Bei einer `word`-Karte ist `value` die Liste der Versuche in der Reihenfolge, in der sie
abgegeben wurden. `correct: true` heißt gelöst. Das neue Feld `tries` ist die Zahl der
abgegebenen Versuche (bei anderen Karten fehlt es):

```json
{"card": "AMW_I-20261111-0900-1", "kurs": "AMW_I", "muster": 3, "answered_at": "2026-11-11T08:12:33+01:00", "value": ["POLYMER", "ENTMISCHT"], "correct": true, "tries": 2, "first": true}
```

Nur Zeilen mit `"first": true` zählen. Eine zweite Antwort auf dieselbe Karte ist geraten
oder abgeschrieben, denn nach der ersten Antwort zeigt die App die Rückseite.

## Was die Lern-Session mit Antworten macht

Beim Ankommen im Kurs, vor dem ersten Häppchen:

1. `<Feed>/lernkarten_antworten/<Kurs>.jsonl` lesen, falls vorhanden. Nur Zeilen mit
   `answered_at` nach der Zeile `Feed-Antworten: gelesen bis <Zeitstempel>` in `todo.md`.
   Fehlt die Zeile, alle.
2. **Falsche Antwort**: ein Beleg unter `muster` in `fehlermuster.md` (Zähler +1, Log-Eintrag
   „Feed-Karte <id>: <Vorderseite kurz> → <value> statt <answer>“). Steht das Muster auf
   „repariert“, geht es zurück auf „offen“.
3. **Richtige Antwort**: zählt als Reparatur-Probe nach §3b der Kurs-CLAUDE.md, wenn alle
   drei Bedingungen gelten: `hinweis` ist `false`, die Eingabe ist `number` oder ein
   `radio`/`select` mit mindestens 3 Optionen, und das Muster hat keinen Beleg nach
   `created_at` der Karte. Dann `Stand` auf „repariert“ und ein Log-Eintrag „repariert per
   Feed-Karte <id>“. Sonst nichts buchen.
   **Worträtsel**: Ein nicht gelöstes Wort (`correct: false`) auf einer Karte mit `muster`
   zählt als ein Beleg, wie eine falsche Karte. Ein gelöstes Wort bucht nichts, auch keine
   Reparatur-Probe, denn die Buchstaben-Rückmeldung hilft beim Lösen.
   **Spaßkarten** (`purpose: "fun"`, ohne `kurs` und `muster`) werden nie gebucht.
4. `Fortschritt: x/y Häppchen` bleibt unverändert. Feed-Karten sind keine Häppchen.
5. In `todo.md` die Zeile `Feed-Antworten: gelesen bis <answered_at der neuesten Zeile>`
   setzen, am Zeilenanfang. Es gibt nur eine solche Zeile.

## Was GifScroll damit macht (seit GifScroll 0.10)

- **Aufnehmen**: Der Job liest neue Dateien unter `<Feed>/lernkarten/` und legt je Karte ein
  Manifest-Item an: `purpose: "quiz"`, `kind: "card"`, `id` = Karten-id, `tags` = `[<Kurs>,
  <thema>]`, die Karte selbst im Feld `card`. Die Kartendateien bleiben unverändert. Der Job
  braucht dafür keinen Zugriff auf die Kursordner. Die Synchronisation muss beide Ordner
  durchlassen: `lernkarten/` zum Job, `lernkarten_antworten/` zurück zu den Lern-Sessions.
- **Zeigen**: Die App rendert `front` (Markdown + KaTeX) und das Eingabefeld. Die Antwort
  prüft sie selbst gegen `answer`: Radio und Auswahl als genauer Text, Zahlen mit Komma
  oder Punkt und 1 % relativer Toleranz, ein Wort als gelöst nach den Regeln des Worträtsels. Danach zeigt sie ✓ oder ✗, die richtige Antwort und
  `back`. Vor der Eingabe ist nichts davon zu sehen.
- **Protokollieren**: jede Antwort als neue Zeilenart in `gifscroll-events.tsv` (Karten-id,
  eingegebener Wert, richtig/falsch, erste Antwort ja/nein).
- **Exportieren**: Der Job hängt die Antworten an `<Feed>/lernkarten_antworten/<Kurs>.jsonl` an.
- **Wiedervorlage** (Vorschlag): Eine falsch beantwortete Karte kommt frühestens am
  nächsten Tag wieder. Eine richtig beantwortete muss nicht wiederkommen.
