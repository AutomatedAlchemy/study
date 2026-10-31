#!/usr/bin/env python3
r"""Blatt-Finder: eine HTML-Seite, die das Mitnehm-Blatt einer Klausur zeigt und zu jeder
Frage des Fragenpools genau die Stellen markiert, die bei der Antwort helfen.

Wann: die Klausur erlaubt ein eigenes Blatt, das Blatt hat eine erste vollständige
Fassung, und es gibt einen Fragenpool (Fragenkatalog, Lernziele der Folien,
Altklausur-Aufgaben). Nach jeder Änderung am Blatt neu bauen.

Vorgehen
1. Blatt als Markdown, eine Datei, dieselbe, aus der das Blatt entsteht. Erkannt werden:
   Überschrift (Zeile nur aus **Titel** oder "# Titel"), Stichpunkt ("- "), Formel
   ($...$), **fett**, ==Falle== (rot). $\colorbox{#d9d9d9}{Text \(Formel\)}$ gilt als
   "neu seit der Abschrift" und wird grau hinterlegt.
2. fragen.json: Liste von {nr, frage, titel, typ, gruppe}. frage wörtlich aus dem Pool,
   titel in wenigen Wörtern, typ R/Z/E (Rechnen/Zeichnen/Erklären, darf fehlen),
   gruppe = Abschnitt des Pools (Vorlesung, Kapitel; darf fehlen).
3. Zuordnung durch Subagenten (unter Claude Code mit model sonnet), je 30 bis 40 Fragen einer. Jeder bekommt das Blatt mit
   Zeilennummern, seine Fragen und dieses Format und schreibt eine Datei map_<von>_<bis>.json:
   Liste von {nr, abdeckung, hinweis, treffer: [{zeile, text}]}.
   - abdeckung: "voll" (das Blatt reicht für die Antwort), "teilweise" (es hilft, ein Teil
     muss aus dem Kopf kommen), "keine" (nichts auf dem Blatt, treffer leer).
   - hinweis: ein bis zwei Sätze, wie die Stellen zur Antwort führen und was fehlt.
     Bei Rechenfragen mit dem erwarteten Ergebnis.
   - treffer: zeile = Zeilennummer im Blatt (ab 1), text = wörtlicher Ausschnitt dieser
     Zeile. Er muss in der Zeile genau einmal vorkommen, darf keine Formel zerschneiden
     und muss ** und == paarweise enthalten. So kurz wie möglich: die Formel, die
     Konstante, das Stichwort, nicht die ganze Zeile.
   Der Subagent prüft seine Datei selbst, bis keine Fehler bleiben:
       blatt_finder.py check BLATT.md map_001_035.json
4. Bauen:
       blatt_finder.py build BLATT.md map_*.json --fragen fragen.json -o blatt_finder.html --titel "Blatt-Finder <Fach>"
   Formeln rendert KaTeX beim Bauen zu MathML, die Seite braucht danach kein Netz.
   KaTeX: --katex DIR oder KATEX_DIR zeigt auf einen Ordner mit node_modules/katex
   (einmal "npm install katex" in einem Arbeitsordner). Ohne KaTeX bleibt der
   Formel-Quelltext stehen.
5. Seite im Browser öffnen (…/blatt_finder.html#<nr> wählt eine Frage vor) und zwei, drei
   Fragen ansehen: stimmen die markierten Stellen?
6. Dem User die Zahlen nennen (voll/teilweise/keine) und die Fragen ohne Treffer. Sie
   zeigen, was aufs Blatt fehlt oder auswendig sitzen muss. Das Blatt nur nach seinem
   Ja ergänzen.
Nach einer Änderung am Blatt: build erneut. Zeilen dürfen sich verschoben haben, der
Ausschnitt wird dann im ganzen Blatt gesucht. Steht er nicht mehr da, bricht der Bau ab
und nennt die Frage; dann den Eintrag in der Zuordnung anpassen.
"""
import argparse, html, json, os, re, subprocess, sys

ABDECKUNG = ("voll", "teilweise", "keine")
NEU = r"\colorbox{#d9d9d9}{"
HEAD = re.compile(r"\*\*([^*]+)\*\*|#{1,6}\s+(.+)")
MATH_SPAN = re.compile(r"\$\$.+?\$\$|\$[^\n$]+?\$")


def heading(line):
    m = HEAD.fullmatch(line.strip())
    return (m.group(1) or m.group(2)) if m else None


def locate(lines, z, s, strict):
    """(zeile, a, b) des Ausschnitts s. strict: nur in Zeile z; sonst bei Bedarf im ganzen Blatt."""
    if not isinstance(z, int) or not 1 <= z <= len(lines):
        raise ValueError(f"Zeile {z} gibt es nicht")
    line = lines[z - 1]
    c = line.count(s) if s else 0
    if c != 1:
        if strict or c > 1:
            raise ValueError(f"Zeile {z} " + ("enthält nicht: " if c == 0 else "mehrfach (Ausschnitt verlängern): ") + repr(s))
        hits = [i for i, l in enumerate(lines, 1) if s and l.count(s) == 1]
        if len(hits) != 1:
            raise ValueError(f"Ausschnitt steht nicht mehr eindeutig im Blatt: {s!r}")
        z, line = hits[0], lines[hits[0] - 1]
    a = line.index(s)
    b = a + len(s)
    for m in MATH_SPAN.finditer(line):
        if m.start() < a < m.end() or m.start() < b < m.end():
            raise ValueError(f"Zeile {z} zerschneidet Formel {m.group(0)!r} mit {s!r}")
    for d in ("**", "=="):
        if s.count(d) % 2:
            raise ValueError(f"Zeile {z}: ungerade Zahl von {d} in {s!r}")
    return z, a, b


def check(lines, data, strict=True, need_frage=False):
    """Fehlerliste (leer = in Ordnung)."""
    err, seen = [], set()
    for d in data:
        nr = d.get("nr")
        if nr in seen:
            err.append(f"{nr}: Nummer doppelt")
        seen.add(nr)
        if d.get("abdeckung") not in ABDECKUNG:
            err.append(f"{nr}: abdeckung muss voll, teilweise oder keine sein")
        if not str(d.get("hinweis") or "").strip():
            err.append(f"{nr}: hinweis fehlt")
        if need_frage and not str(d.get("frage") or "").strip():
            err.append(f"{nr}: frage fehlt (--fragen angeben)")
        treffer = d.get("treffer") or []
        if d.get("abdeckung") in ("voll", "teilweise") and not treffer:
            err.append(f"{nr}: abdeckung {d['abdeckung']}, aber keine Treffer")
        for t in treffer:
            try:
                locate(lines, t.get("zeile"), t.get("text", ""), strict)
            except ValueError as e:
                err.append(f"{nr}: {e}")
    return err


def load(maps, fragen=None):
    """Zuordnungsdateien einlesen und über nr mit den Fragen zusammenführen."""
    base = {}
    if fragen:
        for q in json.load(open(fragen, encoding="utf-8")):
            base[q["nr"]] = dict(q)
    for p in maps:
        for d in json.load(open(p, encoding="utf-8")):
            if d["nr"] in base and "abdeckung" in base[d["nr"]]:
                sys.exit(f"{p}: Frage {d['nr']} ist schon zugeordnet")
            base.setdefault(d["nr"], {}).update(d)
    missing = [nr for nr, q in base.items() if "abdeckung" not in q]
    if missing:
        sys.exit(f"Fragen ohne Zuordnung: {missing}")
    return list(base.values())


def katex_render(exprs, katex_dir):
    """MathML je Formel, oder None, wenn node oder KaTeX fehlen."""
    js = r"""
const katex = require('katex'); let s=''; process.stdin.on('data',d=>s+=d);
process.stdin.on('end',()=>{ const a=JSON.parse(s);
  console.log(JSON.stringify(a.map(t=>katex.renderToString(t,{output:'mathml',throwOnError:true,strict:'ignore'})))); });"""
    env = dict(os.environ)
    if katex_dir:
        env["NODE_PATH"] = os.path.join(katex_dir, "node_modules")
    try:
        r = subprocess.run(["node", "-e", js], input=json.dumps(exprs), capture_output=True, text=True, env=env)
    except OSError:
        return None
    if r.returncode:
        if "Cannot find module" in r.stderr:
            return None
        sys.exit("KaTeX: " + r.stderr[-800:])
    return json.loads(r.stdout)


# ---------- Blatt in Einheiten zerlegen ----------
def units(line):
    """Liste von Einheiten [kind, start, end, src, bold, mark]. kind: text | math | delim."""
    out, i, bold, mark = [], 0, False, False
    while i < len(line):
        if line[i] == "$":
            d = "$$" if line.startswith("$$", i) else "$"
            j = line.find(d, i + len(d))
            if j < 0:
                raise ValueError("Formel nicht geschlossen: " + line[i:i + 40])
            out.append(["math", i, j + len(d), line[i + len(d):j], bold, mark])
            i = j + len(d)
        elif line.startswith("**", i):
            bold = not bold
            out.append(["delim", i, i + 2, "", bold, mark])
            i += 2
        elif line.startswith("==", i):
            mark = not mark
            out.append(["delim", i, i + 2, "", bold, mark])
            i += 2
        else:
            out.append(["text", i, i + 1, line[i], bold, mark])
            i += 1
    if bold or mark:
        raise ValueError("** oder == nicht geschlossen: " + line[:60])
    return out


def unit_html(u, math):
    """math: {LaTeX: Platzhalterindex}, wird hier gefüllt."""
    def m(tex):
        math.setdefault(tex, len(math))
        return f"\x00M{math[tex]}\x00"
    kind, _, _, src, _, _ = u
    if kind == "text":
        return html.escape(src)
    if kind == "delim":
        return ""
    if src.startswith(NEU) and src.endswith("}"):  # grau hinterlegt = neu auf dem Blatt
        inner, parts, pos = src[len(NEU):-1], [], 0
        for g in re.finditer(r"\\\((.+?)\\\)", inner):
            parts.append(html.escape(inner[pos:g.start()]))
            parts.append(m(g.group(1)))
            pos = g.end()
        parts.append(html.escape(inner[pos:]))
        return '<span class="neu">' + "".join(parts) + "</span>"
    return m(src)


def build_sheet(lines, cuts, math):
    """cuts: {zeilennr: sortierte Schnittpunkte}. Gibt (html, {(zeile, a, b): segment-id})."""
    out, seg_of, sid, in_ul = [], {}, 0, False
    for nr, line in enumerate(lines, 1):
        if not line.strip():
            continue
        head = heading(line)
        bullet = line.startswith(("- ", "* "))
        if in_ul and not bullet:
            out.append("</ul>")
            in_ul = False
        if head:
            out.append(f"<h3>{html.escape(head)}</h3>")
            continue
        us = units(line)
        if bullet:
            us = us[2:]  # das Aufzählungszeichen nicht anzeigen
            if not in_ul:
                out.append("<ul>")
                in_ul = True
        cp = cuts.get(nr, [])
        # Einheiten zu Segmenten gruppieren: Wechsel an jedem Schnittpunkt
        segs, cur = [], []
        for u in us:
            if cur and any(cur[-1][2] <= p <= u[1] for p in cp):
                segs.append(cur)
                cur = []
            cur.append(u)
        if cur:
            segs.append(cur)
        buf = []
        for seg in segs:
            inner, run, state = [], [], None

            def flush():
                if not run:
                    return
                h = "".join(run)
                if state[1]:
                    h = f'<mark class="falle">{h}</mark>'
                if state[0]:
                    h = f"<b>{h}</b>"
                inner.append(h)
            for u in seg:
                if u[0] == "delim":
                    continue
                st = (u[4], u[5])
                if st != state:
                    flush()
                    run, state = [], st
                run.append(unit_html(u, math))
            flush()
            if not inner:
                continue
            seg_of[(nr, seg[0][1], seg[-1][2])] = sid
            buf.append(f'<span class="s" data-s="{sid}">{"".join(inner)}</span>')
            sid += 1
        out.append(("<li>" if bullet else "<p>") + "".join(buf) + ("</li>" if bullet else "</p>"))
    if in_ul:
        out.append("</ul>")
    return "\n".join(out), seg_of


def build(sheet_path, data, out_path, title="Blatt-Finder", katex_dir=None):
    """Schreibt die Seite. Gibt die Kennzahlen zurück. katex_dir=False: kein KaTeX versuchen."""
    lines = open(sheet_path, encoding="utf-8").read().split("\n")
    err = check(lines, data, strict=False, need_frage=True)
    if err:
        sys.exit("\n".join(["Zuordnung passt nicht zum Blatt:"] + err))
    cuts, iv = {}, {}
    for q in data:
        for t in q.get("treffer") or []:
            if heading(lines[t["zeile"] - 1]) and lines[t["zeile"] - 1].count(t["text"]) == 1:
                continue  # Überschrift: nichts zu markieren
            z, a, b = locate(lines, t["zeile"], t["text"], strict=False)
            cuts.setdefault(z, set()).update((a, b))
            iv.setdefault(q["nr"], []).append((z, a, b))
    math = {}
    sheet, seg_of = build_sheet(lines, {z: sorted(c) for z, c in cuts.items()}, math)
    rendered = [] if not math else None if katex_dir is False else katex_render(list(math), katex_dir)
    if rendered is None:
        if katex_dir is not False:
            print("Hinweis: KaTeX nicht gefunden, Formeln bleiben als Quelltext stehen (--katex DIR).", file=sys.stderr)
        rendered = [f'<code class="tex">{html.escape(t)}</code>' for t in math]
    sheet = re.sub("\x00M(\\d+)\x00", lambda m: rendered[int(m.group(1))], sheet)
    qs = []
    for q in data:
        segs = sorted({sid for (z, s0, s1), sid in seg_of.items()
                       for (qz, a, b) in iv.get(q["nr"], []) if qz == z and a <= s0 and s1 <= b})
        frage = str(q["frage"])
        qs.append({"nr": str(q["nr"]), "titel": str(q.get("titel") or frage[:60]), "frage": frage,
                   "typ": str(q.get("typ") or ""), "gruppe": str(q.get("gruppe") or q.get("lecture") or ""),
                   "abd": q["abdeckung"], "hinweis": str(q["hinweis"]), "segs": segs})
    page = (TEMPLATE.replace("<!--TITLE-->", html.escape(title))
            .replace("/*DATA*/", json.dumps(qs, ensure_ascii=False).replace("</", "<\\/"))
            .replace("<!--SHEET-->", sheet))
    open(out_path, "w", encoding="utf-8").write(page)
    stats = {k: sum(1 for q in qs if q["abd"] == k) for k in ABDECKUNG}
    stats.update(fragen=len(qs), segmente=len(seg_of), formeln=len(math))
    return stats


TEMPLATE = r"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><!--TITLE--></title>
<style>
:root { --bg:#eceff2; --panel:#fff; --ink:#17212b; --muted:#647383; --line:#d3dae0; --accent:#1d5fa6;
  --hl:#ffe14d; --voll:#2b8454; --teil:#b98311; --keine:#8a96a1; }
* { box-sizing:border-box; }
html, body { height:100%; margin:0; }
body { background:var(--bg); color:var(--ink); font:15px/1.4 system-ui, "Segoe UI", Roboto, sans-serif;
  display:grid; grid-template-columns:minmax(280px, 380px) 1fr; }
aside { background:var(--panel); border-right:1px solid var(--line); display:flex; flex-direction:column; height:100vh; }
.tools { padding:12px; border-bottom:1px solid var(--line); }
.tools input[type=search] { width:100%; padding:8px 10px; font:inherit; border:1px solid var(--line); border-radius:6px; }
.chips { display:flex; gap:6px; flex-wrap:wrap; margin-top:8px; }
.chips button { font:inherit; font-size:13px; padding:3px 9px; border:1px solid var(--line); border-radius:999px;
  background:#fff; color:var(--ink); cursor:pointer; }
.chips button[aria-pressed=true] { background:var(--accent); border-color:var(--accent); color:#fff; }
#count { font-size:12px; color:var(--muted); margin-top:6px; }
#list { overflow:auto; flex:1; }
#list h2 { font-size:12px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); margin:0;
  padding:10px 12px 4px; background:var(--panel); position:sticky; top:0; }
.q { display:grid; grid-template-columns:34px 1fr auto; gap:6px; align-items:baseline; width:100%; text-align:left;
  font:inherit; background:none; border:0; border-left:4px solid transparent; padding:6px 12px 6px 8px; cursor:pointer; color:inherit; }
.q:hover { background:#f2f5f7; }
.q[aria-current=true] { background:#e4eef9; border-left-color:var(--accent); }
.q .nr { font-variant-numeric:tabular-nums; color:var(--muted); text-align:right; }
.q .typ { font-size:11px; color:var(--muted); }
.dot { display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:5px; }
.voll { background:var(--voll); } .teilweise { background:var(--teil); } .keine { background:var(--keine); }
main { height:100vh; overflow:auto; }
#frage { position:sticky; top:0; z-index:2; background:var(--panel); border-bottom:1px solid var(--line); padding:12px 20px; }
#frage .kopf { font-size:13px; color:var(--muted); display:flex; gap:12px; flex-wrap:wrap; align-items:center; }
#frage .text { font-size:16px; margin:4px 0 6px; max-width:90ch; }
#frage .hinweis { font-size:14px; max-width:90ch; padding:6px 10px; border-left:4px solid var(--line); background:#f6f8fa; }
#frage .hinweis.voll { background:#e8f4ed; border-color:var(--voll); }
#frage .hinweis.teilweise { background:#fbf3df; border-color:var(--teil); }
#frage .hinweis.keine { background:#eef1f4; border-color:var(--keine); }
.badge { color:#fff; border-radius:4px; padding:1px 7px; font-size:12px; }
label.opt { font-size:13px; color:var(--muted); cursor:pointer; }
#blatt { background:#fff; color:#111; margin:18px auto 60px; padding:14px 18px; max-width:1100px; width:calc(100% - 36px);
  box-shadow:0 1px 3px rgba(0,0,0,.15); column-count:2; column-gap:22px;
  font:14.5px/1.42 "Latin Modern Roman", "CMU Serif", Georgia, "Times New Roman", serif; }
#blatt h3 { font-size:1em; margin:.7em 0 .15em; break-after:avoid; border-bottom:1px solid #999; }
#blatt h3:first-child { margin-top:0; }
#blatt p { margin:.15em 0; }
#blatt ul { margin:.1em 0; padding-left:1.1em; }
#blatt li { margin:.14em 0; }
#blatt mark.falle { background:none; color:#a31515; font-weight:700; }
#blatt .neu { background:#d9d9d9; border-radius:2px; padding:0 2px; }
#blatt math { font-size:1.02em; }
#blatt code.tex { font-size:.85em; }
.s { border-radius:2px; transition:background .12s, opacity .12s; }
body.sel.dim #blatt .s:not(.hl) { opacity:.38; }
#blatt .s.hl { background:var(--hl); box-shadow:0 0 0 2px var(--hl); }
#blatt .s.hl .neu { background:#e3c93e; }
#blatt .s.used { cursor:pointer; }
#blatt .s.used:hover { outline:1px dashed var(--accent); }
.leer { padding:30px 20px; color:var(--muted); }
@media (max-width:900px) { body { grid-template-columns:1fr; } aside { height:45vh; } main { height:55vh; } #blatt { column-count:1; } }
@media print { aside, #frage { display:none; } body { display:block; } main { height:auto; overflow:visible; } }
</style>
</head>
<body class="dim">
<aside>
  <div class="tools">
    <input type="search" id="suche" placeholder="Frage suchen (Nummer oder Wort)" autocomplete="off">
    <div class="chips" id="chips">
      <button data-f="alle" aria-pressed="true">alle</button>
      <button data-f="voll"><span class="dot voll"></span>steht drauf</button>
      <button data-f="teilweise"><span class="dot teilweise"></span>teilweise</button>
      <button data-f="keine"><span class="dot keine"></span>nicht drauf</button>
    </div>
    <div id="count"></div>
  </div>
  <div id="list"></div>
</aside>
<main id="main">
  <div id="frage"><div class="leer">Links eine Frage anklicken. Auf dem Blatt werden die Stellen gelb markiert, die bei der Antwort helfen.
  Ein Klick auf eine Stelle des Blatts zeigt umgekehrt alle Fragen, die sie brauchen. Pfeiltasten ↑ ↓ wechseln die Frage.</div></div>
  <div id="blatt"><!--SHEET--></div>
</main>
<script>
const Q = /*DATA*/;
const LABEL = {voll:"steht auf dem Blatt", teilweise:"teilweise auf dem Blatt", keine:"nicht auf dem Blatt"};
const TYP = {R:"Rechnen", Z:"Zeichnen", E:"Erklären"};
const KEY = "blattfinder:" + location.pathname;
const $ = s => document.querySelector(s);
const list = $("#list"), frage = $("#frage"), blatt = $("#blatt"), main = $("#main");
let filter = "alle", segFilter = null, current = null, shown = [];
const esc = s => s.replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

const typen = [...new Set(Q.map(q => q.typ).filter(Boolean))];
if (typen.length > 1) typen.forEach(t => { const b = document.createElement("button"); b.dataset.f = "typ:" + t;
  b.textContent = TYP[t] || t; $("#chips").appendChild(b); });

const used = new Map();
Q.forEach(q => q.segs.forEach(s => { if (!used.has(s)) used.set(s, []); used.get(s).push(q.nr); }));
blatt.querySelectorAll(".s").forEach(el => { if (used.has(+el.dataset.s)) { el.classList.add("used");
  el.title = "gebraucht von Frage " + used.get(+el.dataset.s).join(", "); } });

function render() {
  const t = $("#suche").value.trim().toLowerCase();
  shown = Q.filter(q => (filter === "alle" || q.abd === filter || "typ:" + q.typ === filter)
    && (segFilter === null || q.segs.includes(segFilter))
    && (!t || q.nr.toLowerCase() === t || (q.nr + " " + q.titel + " " + q.frage).toLowerCase().includes(t)));
  let h = "", grp = null;
  for (const q of shown) {
    if (q.gruppe !== grp) { grp = q.gruppe; if (grp) h += "<h2>" + esc(grp) + "</h2>"; }
    h += '<button class="q" data-nr="' + esc(q.nr) + '"' + (q.nr === current ? ' aria-current="true"' : "") + '><span class="nr">' + esc(q.nr) +
      '</span><span><span class="dot ' + q.abd + '" title="' + LABEL[q.abd] + '"></span>' + esc(q.titel) + '</span><span class="typ">' + esc(q.typ) + "</span></button>";
  }
  list.innerHTML = h || '<div class="leer">Keine Frage passt.</div>';
  $("#count").innerHTML = shown.length + " von " + Q.length + " Fragen" +
    (segFilter !== null ? ' zu dieser Blatt-Stelle <a href="#" id="segoff">(alle zeigen)</a>' : "");
}

function select(nr, scroll) {
  const q = Q.find(x => x.nr === nr); if (!q) return;
  current = nr;
  try { localStorage.setItem(KEY, nr); } catch (e) {}
  document.body.classList.add("sel");
  frage.innerHTML = '<div class="kopf"><b>Frage ' + esc(q.nr) + "</b>" + (q.typ ? "<span>" + esc(TYP[q.typ] || q.typ) + "</span>" : "") +
    '<span class="badge ' + q.abd + '">' + LABEL[q.abd] +
    "</span><span>" + q.segs.length + ' Stelle' + (q.segs.length === 1 ? "" : "n") + ' markiert</span>' +
    '<label class="opt"><input type="checkbox" id="dim"' + (document.body.classList.contains("dim") ? " checked" : "") + "> Rest abblenden</label></div>" +
    '<div class="text">' + esc(q.frage) + '</div><div class="hinweis ' + q.abd + '">' + esc(q.hinweis) + "</div>";
  const set = new Set(q.segs);
  let first = null;
  blatt.querySelectorAll(".s").forEach(el => { const on = set.has(+el.dataset.s); el.classList.toggle("hl", on); if (on && !first) first = el; });
  list.querySelectorAll(".q").forEach(b => b.toggleAttribute("aria-current", false));
  const btn = [...list.querySelectorAll(".q")].find(b => b.dataset.nr === nr);
  if (btn) { btn.setAttribute("aria-current", "true"); if (scroll) btn.scrollIntoView({block:"nearest"}); }
  if (first) { const top = first.getBoundingClientRect().top - main.getBoundingClientRect().top + main.scrollTop;
    main.scrollTo({top: Math.max(0, top - frage.offsetHeight - 60), behavior:"smooth"}); }
}

list.addEventListener("click", e => { const b = e.target.closest(".q"); if (b) select(b.dataset.nr, false); });
$("#suche").addEventListener("input", render);
$("#chips").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; filter = b.dataset.f;
  document.querySelectorAll("#chips button").forEach(x => x.setAttribute("aria-pressed", x === b)); render(); });
document.addEventListener("change", e => { if (e.target.id === "dim") document.body.classList.toggle("dim", e.target.checked); });
document.addEventListener("click", e => { if (e.target.id === "segoff") { e.preventDefault(); segFilter = null; render(); } });
blatt.addEventListener("click", e => { const s = e.target.closest(".s.used"); if (!s) return; segFilter = +s.dataset.s; render();
  if (shown.length) select(shown[0].nr, true); });
document.addEventListener("keydown", e => { if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
  if (e.target.tagName === "INPUT" && e.target.type !== "search") return; e.preventDefault();
  const i = shown.findIndex(q => q.nr === current), j = e.key === "ArrowDown" ? i + 1 : i - 1;
  if (shown[j]) select(shown[j].nr, true); else if (i < 0 && shown.length) select(shown[0].nr, true); });
render();
try { const n = decodeURIComponent(location.hash.slice(1)) || localStorage.getItem(KEY); if (n) select(n, true); } catch (e) {}
</script>
</body>
</html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(prog="blatt_finder.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Zuordnungsdateien gegen das Blatt prüfen")
    c.add_argument("blatt")
    c.add_argument("zuordnung", nargs="+")
    b = sub.add_parser("build", help="die Seite bauen")
    b.add_argument("blatt")
    b.add_argument("zuordnung", nargs="+")
    b.add_argument("--fragen", help="fragen.json, wenn die Zuordnung die Fragen nicht selbst enthält")
    b.add_argument("-o", "--out", help="Zieldatei (Standard: blatt_finder.html neben dem Blatt)")
    b.add_argument("--titel", default="Blatt-Finder")
    b.add_argument("--katex", default=os.environ.get("KATEX_DIR"), help="Ordner mit node_modules/katex")
    a = ap.parse_args(argv)
    if a.cmd == "check":
        lines = open(a.blatt, encoding="utf-8").read().split("\n")
        bad = 0
        for p in a.zuordnung:
            data = json.load(open(p, encoding="utf-8"))
            err = check(lines, data)
            for e in err:
                print(f"FEHLER {p}: {e}")
            print(f"{p}: {len(data)} Fragen, {sum(len(d.get('treffer') or []) for d in data)} Treffer, {len(err)} Fehler")
            bad += len(err)
        return 1 if bad else 0
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.blatt)), "blatt_finder.html")
    s = build(a.blatt, load(a.zuordnung, a.fragen), out, a.titel, a.katex)
    print(f"{out}: {s['fragen']} Fragen, {s['segmente']} Segmente, {s['formeln']} Formeln; "
          f"voll {s['voll']}, teilweise {s['teilweise']}, keine {s['keine']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
