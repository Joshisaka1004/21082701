"""
Japanese Skylines - Japanese Sums x Skyscrapers (Produkt-Variante)
===================================================================

Ein Japanese-Sums-Raetsel, bei dem ein Teil der Hinweise durch Skyline-
Hinweise ERSETZT ist. Alle vier Seiten des Gitters tragen Hinweise, und die
Seite verraet den Typ:

  * LINKS und OBEN stehen JAPANESE-SUMS-Hinweise: die Summe jeder
    zusammenhaengenden Zifferngruppe, gelesen von links bzw. von oben.

  * RECHTS und UNTEN stehen SKYLINE-Hinweise: fuer jede Gruppe das PRODUKT
    der Haeuser, die man VON DORT sieht, also von rechts bzw. von unten. Die
    klassische Skyscrapers-Variante nennt die Anzahl sichtbarer Haeuser,
    die Summen-Variante ihre Summe - hier ist es ihr Produkt.

Jede Linie traegt genau einen Hinweis, entweder links/oben oder rechts/unten.
Der Anteil der Skyline-Linien ist einstellbar; bewaehrt sind 20 bis 40
Prozent. Welche Linie welchen Typ bekommt, wechselt von Raetsel zu Raetsel.

Warum die Seiten so verteilt sind: eine Gruppensumme ist von beiden Seiten
dieselbe Zahl, ein Summen-Hinweis rechts waere also nur die umgedrehte Liste
des linken - ohne neuen Inhalt. Sichtprodukte dagegen haengen an der
Blickrichtung und sind auf der Gegenseite echte Zusatzinformation.

REGELN
------
1. Jede Zelle ist schwarz (leer) oder traegt eine Ziffer von 1 bis 9.
2. In jeder Zeile und jeder Spalte kommt jede Ziffer hoechstens einmal vor.
3. Jede Zeile und jede Spalte enthaelt mindestens eine Ziffer.
4. Zwei Gruppen sind durch mindestens ein schwarzes Feld getrennt. Jede
   Hinweisliste nennt ihre Gruppen in der Reihenfolge, in der man sie von
   der Seite des Hinweises aus antrifft.
5. SUMMEN-Hinweis (links/oben): die Summe der Ziffern der Gruppe.
6. SKYLINE-Hinweis (rechts/unten): das Produkt der sichtbaren Haeuser der
   Gruppe. Innerhalb einer Gruppe ist ein Haus sichtbar, wenn alle Haeuser
   davor IN DERSELBEN GRUPPE niedriger sind. Das erste Haus jeder Gruppe ist
   immer sichtbar; ein schwarzes Feld beginnt die Sicht neu.

BEISPIEL fuer dieselbe Zeile  3 # 5 1 7  mit Gruppen [3] und [5,1,7]

   als Summen-Zeile, links:    3 und 13, denn 5 + 1 + 7 = 13
   als Skyline-Zeile, rechts:  7 und 3 - von rechts trifft man zuerst die
                               Gruppe [5,1,7]. Dort steht die 7 vorn und
                               verdeckt 1 und 5, bleibt also allein sichtbar.
                               Dann folgt die 3.

NUETZLICHE DEDUKTIONSREGELN
---------------------------
* Die sichtbaren Haeuser einer Gruppe bilden eine streng aufsteigende Folge.
  Ein Skyline-Hinweis ist also stets ein Produkt lauter verschiedener
  Ziffern - 16 oder 25 kann kein Hinweis sein.
* Ein Skyline-Hinweis von 5 oder 7 heisst: diese Ziffer steht am aeusseren
  Ende ihrer Gruppe, alles dahinter in der Gruppe ist kleiner.
* Ein Skyline-Hinweis 1 heisst: die Gruppe beginnt von dieser Seite mit
  einer 1. Eine 1 verdeckt nichts, also besteht die Gruppe aus genau ihr.
* Ein grosser Skyline-Hinweis wie 504 = 7*8*9 erzwingt mindestens drei
  Zellen mit stark steigenden Werten.
* Eine Gruppe mit Summe s auf L Zellen braucht L verschiedene Ziffern:
  Summe 6 auf drei Zellen geht nur als 1+2+3.
* Summe und Sichtprodukt beschreiben dieselbe Gruppe von zwei Seiten - wer
  eine Gruppe aus einer Richtung festgelegt hat, kennt sie ganz.

Jedes erzeugte Raetsel hat garantiert genau eine Loesung.
"""
from __future__ import annotations

import os
import random
import time
from copy import deepcopy
from functools import lru_cache
from typing import List, Optional, Sequence, Tuple

CellValue = int  # 0 = schwarzes Feld, 1-9 = Haushoehe
Pattern = Tuple[CellValue, ...]
Clue = Tuple[int, ...]  # ein Wert je Gruppe, in Reihenfolge der Linie

SUM = "sum"  # Gruppensummen (Japanese Sums)
SKY = "sky"  # Produkt der sichtbaren Haeuser je Gruppe (Skyline)

LineClue = Tuple[str, Clue]  # (Hinweistyp, Werte) fuer eine Zeile/Spalte


# ---------------------------------------------------------------------------
# Hinweise aus einer fertigen Linie ablesen
# ---------------------------------------------------------------------------

def _groups(line: Sequence[CellValue]) -> List[List[int]]:
    """Zerlegt eine Linie in ihre zusammenhaengenden Zifferngruppen."""
    found: List[List[int]] = []
    run: List[int] = []
    for value in list(line) + [0]:
        if value:
            run.append(value)
        elif run:
            found.append(run)
            run = []
    return found


def group_sums(line: Sequence[CellValue]) -> Clue:
    """Zeilen-Hinweis: Summe jeder Gruppe."""
    return tuple(sum(g) for g in _groups(line))


def group_products(line: Sequence[CellValue]) -> Clue:
    """
    Skyline-Hinweis, VON HINTEN gelesen: Produkt der in jeder Gruppe
    sichtbaren Haeuser, mit Blick von rechts bzw. von unten. Die Gruppen
    erscheinen in der Reihenfolge, in der man sie von dort aus antrifft.
    """
    clue = []
    for group in _groups(list(line)[::-1]):
        product, highest = 1, 0
        for value in group:
            if value > highest:
                product *= value
                highest = value
        clue.append(product)
    return tuple(clue)


# ---------------------------------------------------------------------------
# Bausteine: passende Ziffernfolgen fuer eine einzelne Gruppe
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _runs_by_sum(target: int, length: int, used: int) -> Tuple[Tuple[int, ...], ...]:
    """Geordnete Folgen aus `length` verschiedenen Ziffern mit Summe `target`."""
    results: List[Tuple[int, ...]] = []
    current: List[int] = []

    def build(remaining: int, slots: int, taken: int) -> None:
        if slots == 0:
            if remaining == 0:
                results.append(tuple(current))
            return
        if not (slots <= remaining <= 9 * slots):
            return
        for digit in range(1, 10):
            bit = 1 << digit
            if taken & bit or digit > remaining:
                continue
            current.append(digit)
            build(remaining - digit, slots - 1, taken | bit)
            current.pop()

    build(target, length, used)
    return tuple(results)


@lru_cache(maxsize=None)
def _runs_by_product(target: int, length: int, used: int) -> Tuple[Tuple[int, ...], ...]:
    """
    Geordnete Folgen aus `length` verschiedenen Ziffern, deren sichtbare
    Haeuser sich zu `target` multiplizieren.
    """
    results: List[Tuple[int, ...]] = []
    current: List[int] = []

    def build(slots: int, taken: int, highest: int, product: int) -> None:
        if slots == 0:
            if product == target:
                results.append(tuple(current))
            return
        for digit in range(1, 10):
            bit = 1 << digit
            if taken & bit:
                continue
            if digit > highest:
                grown = product * digit
                if target % grown:  # Zielprodukt waere nicht mehr erreichbar
                    continue
                new_highest = digit
            else:
                grown, new_highest = product, highest
            current.append(digit)
            build(slots - 1, taken | bit, new_highest, grown)
            current.pop()

    build(length, used, 0, 1)
    return tuple(results)


# ---------------------------------------------------------------------------
# Pattern-Erzeugung: alle Linien, die zu einer Hinweisliste passen
# ---------------------------------------------------------------------------

def _build_patterns(size: int, clue: Clue, by_product: bool) -> Tuple[Pattern, ...]:
    runs = _runs_by_product if by_product else _runs_by_sum
    results: List[Pattern] = []
    line: List[CellValue] = [0] * size

    def place(index: int, start: int, used: int) -> None:
        if index == len(clue):
            results.append(tuple(line))
            return
        # Fuer jede weitere Gruppe mindestens eine Zelle plus ein Trennfeld
        reserve = 2 * (len(clue) - index - 1)
        for begin in range(start, size - reserve):
            for length in range(1, size - begin - reserve + 1):
                for combo in runs(clue[index], length, used):
                    taken = used
                    for offset, digit in enumerate(combo):
                        line[begin + offset] = digit
                        taken |= 1 << digit
                    place(index + 1, begin + length + 1, taken)
                    for offset in range(length):
                        line[begin + offset] = 0

    place(0, 0, 0)
    return tuple(results)


@lru_cache(maxsize=None)
def patterns_for_sums(size: int, clue: Clue) -> Tuple[Pattern, ...]:
    """Alle Linien der Laenge `size` mit diesen Gruppensummen."""
    return _build_patterns(size, clue, by_product=False)


@lru_cache(maxsize=None)
def patterns_for_products(size: int, clue: Clue) -> Tuple[Pattern, ...]:
    """
    Alle Linien der Laenge `size`, deren Sichtprodukte VON HINTEN gelesen
    diesem Hinweis entsprechen. Gebaut wird vorwaerts, dann gespiegelt: eine
    Linie, die von links `clue` ergibt, ergibt umgedreht von rechts dasselbe.
    """
    return tuple(p[::-1] for p in _build_patterns(size, clue, by_product=True))


def patterns_for(size: int, line: LineClue) -> Tuple[Pattern, ...]:
    """Alle Linien, die zu diesem Hinweis passen - je nach Hinweistyp."""
    kind, clue = line
    if kind == SKY:
        return patterns_for_products(size, clue)
    return patterns_for_sums(size, clue)


# ---------------------------------------------------------------------------
# Solver: CSP ueber Zeilen- und Spalten-Pattern mit Arc Consistency
# ---------------------------------------------------------------------------

def solve(
    rows: int,
    cols: int,
    row_clues: Sequence[LineClue],
    col_clues: Sequence[LineClue],
    max_solutions: int = 2,
) -> Tuple[int, Optional[List[List[CellValue]]]]:
    """Zaehlt Loesungen bis `max_solutions` und liefert die erste gefundene."""
    row_domains = [list(patterns_for(cols, c)) for c in row_clues]
    col_domains = [list(patterns_for(rows, c)) for c in col_clues]

    if any(not d for d in row_domains) or any(not d for d in col_domains):
        return 0, None

    def propagate(r_dom: List[List[Pattern]], c_dom: List[List[Pattern]]) -> bool:
        changed = True
        while changed:
            changed = False
            for r in range(rows):
                for c in range(cols):
                    allowed = {p[c] for p in r_dom[r]} & {p[r] for p in c_dom[c]}
                    if not allowed:
                        return False
                    kept = [p for p in r_dom[r] if p[c] in allowed]
                    if len(kept) != len(r_dom[r]):
                        if not kept:
                            return False
                        r_dom[r] = kept
                        changed = True
                    kept = [p for p in c_dom[c] if p[r] in allowed]
                    if len(kept) != len(c_dom[c]):
                        if not kept:
                            return False
                        c_dom[c] = kept
                        changed = True
        return True

    solutions: List[List[List[CellValue]]] = []

    def search(r_dom: List[List[Pattern]], c_dom: List[List[Pattern]]) -> None:
        if len(solutions) >= max_solutions:
            return
        if not propagate(r_dom, c_dom):
            return
        if all(len(d) == 1 for d in r_dom) and all(len(d) == 1 for d in c_dom):
            solutions.append([list(d[0]) for d in r_dom])
            return

        # Most Constrained Variable: Linie mit den wenigsten Optionen zuerst
        options = [(len(r_dom[i]), 'r', i) for i in range(rows) if len(r_dom[i]) > 1]
        options += [(len(c_dom[j]), 'c', j) for j in range(cols) if len(c_dom[j]) > 1]
        if not options:
            return
        _, axis, idx = min(options)

        for pattern in (r_dom[idx] if axis == 'r' else c_dom[idx]):
            next_r, next_c = deepcopy(r_dom), deepcopy(c_dom)
            if axis == 'r':
                next_r[idx] = [pattern]
            else:
                next_c[idx] = [pattern]
            search(next_r, next_c)
            if len(solutions) >= max_solutions:
                return

    search(row_domains, col_domains)
    return len(solutions), (solutions[0] if solutions else None)


# ---------------------------------------------------------------------------
# Gitter-Erzeugung
# ---------------------------------------------------------------------------

def random_grid(rows: int, cols: int, black_prob: float) -> Optional[List[List[CellValue]]]:
    """Zufaelliges gueltiges Gitter, oder None wenn es nicht gelingt."""
    grid = [[0] * cols for _ in range(rows)]
    row_used: List[set] = [set() for _ in range(rows)]
    col_used: List[set] = [set() for _ in range(cols)]

    cells = [(r, c) for r in range(rows) for c in range(cols)]
    random.shuffle(cells)

    for r, c in cells:
        if random.random() < black_prob:
            continue
        choices = [d for d in range(1, 10)
                   if d not in row_used[r] and d not in col_used[c]]
        if not choices:
            continue
        digit = random.choice(choices)
        grid[r][c] = digit
        row_used[r].add(digit)
        col_used[c].add(digit)

    # Leere Zeilen und Spalten nachtraeglich besetzen
    for r in range(rows):
        if row_used[r]:
            continue
        spots = [c for c in range(cols) if len(col_used[c]) < 9]
        if not spots:
            return None
        c = random.choice(spots)
        digit = random.choice([d for d in range(1, 10) if d not in col_used[c]])
        grid[r][c] = digit
        row_used[r].add(digit)
        col_used[c].add(digit)

    for c in range(cols):
        if col_used[c]:
            continue
        spots = [r for r in range(rows) if len(row_used[r]) < 9]
        if not spots:
            return None
        r = random.choice(spots)
        digit = random.choice([d for d in range(1, 10) if d not in row_used[r]])
        grid[r][c] = digit
        row_used[r].add(digit)
        col_used[c].add(digit)

    return grid


def line_clue(line: Sequence[CellValue], kind: str) -> LineClue:
    """Hinweis einer Linie im gewuenschten Typ."""
    return (kind, group_products(line) if kind == SKY else group_sums(line))


def derive_clues(
    grid: Sequence[Sequence[CellValue]],
    sky_rows: Sequence[int] = (),
    sky_cols: Sequence[int] = (),
) -> Tuple[List[LineClue], List[LineClue]]:
    """
    Hinweise ablesen. Die in `sky_rows`/`sky_cols` genannten Linien bekommen
    Skyline-Produkte, alle uebrigen Japanese-Sums-Summen.
    """
    rows, cols = len(grid), len(grid[0])
    sky_r, sky_c = set(sky_rows), set(sky_cols)
    row_clues = [line_clue(grid[r], SKY if r in sky_r else SUM)
                 for r in range(rows)]
    col_clues = [line_clue([grid[r][c] for r in range(rows)],
                           SKY if c in sky_c else SUM)
                 for c in range(cols)]
    return row_clues, col_clues


def _quality_ok(row_clues: Sequence[LineClue], col_clues: Sequence[LineClue]) -> bool:
    """Sorgt fuer abwechslungsreiche Hinweise statt lauter Kleinkram."""
    every = list(row_clues) + list(col_clues)
    sums = [v for kind, clue in every if kind == SUM for v in clue]
    products = [v for kind, clue in every if kind == SKY for v in clue]
    if not sums or not products:
        return False
    # Nicht zu viele Gruppen in einer Linie
    if any(len(clue) > 4 for _, clue in every):
        return False
    # Nicht ueberwiegend einstellige Gruppensummen
    if sum(1 for v in sums if v < 10) / len(sums) > 0.6:
        return False
    # Wenigstens ein Teil der Sichtprodukte soll zweistellig sein
    if sum(1 for v in products if v >= 12) < max(1, len(products) // 4):
        return False
    return True


def _black_probability(rows: int, cols: int, attempt: int) -> float:
    """Wechselnde Dichte schwarzer Felder, damit die Raetsel variieren."""
    base = 0.28 + 0.015 * max(0, max(rows, cols) - 5)
    spread = (0.00, 0.07, 0.14)[attempt % 3]
    return min(0.58, random.uniform(base + spread, base + spread + 0.08))


# ---------------------------------------------------------------------------
# Raetsel-Erzeugung
# ---------------------------------------------------------------------------

def _pick_sky_lines(rows: int, cols: int, sky_ratio: float) -> Tuple[List[int], List[int]]:
    """
    Waehlt zufaellig, welche Linien einen Skyline-Hinweis bekommen. Gezaehlt
    wird ueber Zeilen und Spalten gemeinsam, damit der Anteil stimmt.
    """
    total = rows + cols
    count = max(1, min(total - 1, round(total * sky_ratio)))
    chosen = random.sample(range(total), count)
    return ([i for i in chosen if i < rows],
            [i - rows for i in chosen if i >= rows])


def generate_puzzle(
    rows: int = 6,
    cols: Optional[int] = None,
    sky_ratio: float = 0.3,
    max_attempts: int = 3000,
    time_limit: float = 120.0,
) -> Tuple[List[LineClue], List[LineClue], List[List[CellValue]]]:
    """
    Erzeugt ein Raetsel mit garantiert eindeutiger Loesung.

    `sky_ratio` ist der Anteil der Linien mit Skyline-Hinweis; der Rest
    bekommt Japanese-Sums-Summen. Sinnvoll sind etwa 0.2 bis 0.4 - je mehr
    Skyline, desto weniger Substanz tragen die Hinweise insgesamt.

    Rueckgabe: (Zeilen-Hinweise, Spalten-Hinweise, Loesung)
    """
    if cols is None:
        cols = rows
    if not (4 <= rows <= 13 and 4 <= cols <= 13):
        raise ValueError("Groesse muss zwischen 4 und 13 liegen")
    if not 0.0 < sky_ratio < 1.0:
        raise ValueError("sky_ratio muss zwischen 0 und 1 liegen")

    started = time.time()
    attempt = 0

    while attempt < max_attempts and time.time() - started <= time_limit:
        attempt += 1

        grid = random_grid(rows, cols, _black_probability(rows, cols, attempt))
        if grid is None:
            continue

        sky_rows, sky_cols = _pick_sky_lines(rows, cols, sky_ratio)
        row_clues, col_clues = derive_clues(grid, sky_rows, sky_cols)
        if not _quality_ok(row_clues, col_clues):
            continue

        count, solution = solve(rows, cols, row_clues, col_clues, max_solutions=2)
        if count == 1:
            return row_clues, col_clues, solution

    raise RuntimeError(
        f"Kein eindeutiges Raetsel gefunden ({attempt} Versuche, "
        f"{time.time() - started:.1f}s)"
    )


# ---------------------------------------------------------------------------
# Darstellung
# ---------------------------------------------------------------------------

def render(
    row_clues: Sequence[LineClue],
    col_clues: Sequence[LineClue],
    grid: Optional[Sequence[Sequence[CellValue]]] = None,
) -> str:
    """
    Zeichnet das Raetsel. Ein vorangestelltes ^ markiert eine Linie mit
    Skyline-Hinweis; alle uebrigen tragen Gruppensummen.
    """
    rows, cols = len(row_clues), len(col_clues)

    # Summen-Zeilen beschriften links, Skyline-Zeilen rechts
    left, right = [], []
    for kind, clue in row_clues:
        text = " ".join(map(str, clue))
        left.append("" if kind == SKY else text)
        right.append(text if kind == SKY else "")
    left_width = max(len(s) for s in left)

    # Summen-Spalten beschriften oben, Skyline-Spalten unten
    above, below = [], []
    for kind, clue in col_clues:
        text = [str(v) for v in clue]
        above.append([] if kind == SKY else text)
        below.append(text if kind == SKY else [])
    high = max((len(c) for c in above), default=0)
    deep = max((len(c) for c in below), default=0)
    cell_width = max(3, max((len(s) for c in above + below for s in c), default=1))

    pad = " " * (left_width + 1)
    border = pad + "+" + "+".join("-" * cell_width for _ in range(cols)) + "+"

    out = []
    for level in range(high):
        line = []
        for c in above:
            # nach unten ausrichten, damit die Hinweise am Gitter kleben
            offset = level - (high - len(c))
            line.append((c[offset] if offset >= 0 else "").center(cell_width))
        out.append(pad + " " + " ".join(line))

    out.append(border)
    for r in range(rows):
        cells = []
        for c in range(cols):
            if grid is None:
                cells.append(" " * cell_width)
            else:
                value = grid[r][c]
                cells.append(("#" if value == 0 else str(value)).center(cell_width))
        tail = f" {right[r]}" if right[r] else ""
        out.append(f"{left[r]:>{left_width}} |" + "|".join(cells) + "|" + tail)
        out.append(border)

    for level in range(deep):
        line = []
        for c in below:
            line.append((c[level] if level < len(c) else "").center(cell_width))
        out.append(pad + " " + " ".join(line))

    sky = sum(1 for kind, _ in list(row_clues) + list(col_clues) if kind == SKY)
    out.append("")
    out.append("  links und oben  = Summe jeder Gruppe")
    out.append("  rechts und unten = Produkt der von dort sichtbaren Haeuser")
    out.append(f"  {sky} von {rows + cols} Linien sind Skyline-Linien")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# PNG-Ausgabe (benoetigt Pillow)
# ---------------------------------------------------------------------------

_INK = (20, 20, 20)
_SKY_INK = (12, 90, 160)
_BLACK_CELL = (44, 48, 54)
_GRID = (60, 60, 60)


def _font(size: int):
    """Laedt eine TrueType-Schrift, mit Rueckfall auf Pillows Standard."""
    from PIL import ImageFont
    for name in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                 "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
                 "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _centered(draw, text: str, box: Tuple[int, int, int, int], font, fill) -> None:
    """Schreibt `text` mittig in das Rechteck (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    draw.text((((x0 + x1) - (right + left)) // 2,
               ((y0 + y1) - (bottom + top)) // 2), text, font=font, fill=fill)


def save_image(
    path: str,
    row_clues: Sequence[LineClue],
    col_clues: Sequence[LineClue],
    grid: Optional[Sequence[Sequence[CellValue]]] = None,
    title: str = "",
    cell: int = 62,
) -> str:
    """
    Speichert das Raetsel als Bild. Das Format ergibt sich aus der Endung von
    `path` - .png und .pdf sind beide moeglich. Ohne `grid` entsteht das leere
    Raetsel, mit `grid` die Loesung. Skyline-Linien bekommen einen blauen
    Hinweisstreifen.
    """
    from PIL import Image, ImageDraw

    rows, cols = len(row_clues), len(col_clues)
    clue_font = _font(int(cell * 0.42))
    digit_font = _font(int(cell * 0.52))
    title_font = _font(int(cell * 0.38))
    note_font = _font(int(cell * 0.26))

    # Summen stehen links und oben, Skyline-Produkte rechts und unten
    def depth(clues, kind) -> int:
        return max((len(clue) for k, clue in clues if k == kind), default=0)

    deep_left = depth(row_clues, SUM)
    deep_right = depth(row_clues, SKY)
    deep_top = depth(col_clues, SUM)
    deep_bottom = depth(col_clues, SKY)

    # Hinweisfeld so breit machen, dass auch dreistellige Zahlen hineinpassen
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    def text_width(text: str, font) -> int:
        box = probe.textbbox((0, 0), text, font=font)
        return box[2] - box[0]

    widest = max(text_width(str(v), clue_font)
                 for _, clue in list(row_clues) + list(col_clues) for v in clue)
    slot = max(int(cell * 0.55), widest + int(cell * 0.26))

    note = ("links und oben: Summe je Gruppe        "
            "rechts und unten: Produkt der von dort sichtbaren Haeuser")
    note_width = text_width(note, note_font)

    margin = int(cell * 0.55)
    head = int(cell * 0.95) if title else margin
    grid_x = margin + deep_left * slot
    grid_y = head + deep_top * slot
    width = max(grid_x + cols * cell + deep_right * slot + margin,
                margin + note_width + margin)
    height = (grid_y + rows * cell + deep_bottom * slot
              + margin + int(cell * 0.85))

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    if title:
        _centered(draw, title, (margin, int(cell * 0.12), width - margin,
                                head - int(cell * 0.18)), title_font, _INK)

    # Hinweise wachsen vom Gitter nach aussen, damit sie daran kleben
    grid_right = grid_x + cols * cell
    grid_bottom = grid_y + rows * cell

    for r, (kind, clue) in enumerate(row_clues):
        y = grid_y + r * cell
        if kind == SKY:  # rechts, erste Gruppe von rechts zuerst
            for i, value in enumerate(clue):
                x = grid_right + i * slot
                _centered(draw, str(value), (x, y, x + slot, y + cell),
                          clue_font, _SKY_INK)
        else:  # links, letzte Gruppe naeher am Gitter
            for i, value in enumerate(reversed(clue)):
                x = grid_x - (i + 1) * slot
                _centered(draw, str(value), (x, y, x + slot, y + cell),
                          clue_font, _INK)

    for c, (kind, clue) in enumerate(col_clues):
        x = grid_x + c * cell
        if kind == SKY:  # unten, erste Gruppe von unten zuerst
            for i, value in enumerate(clue):
                y = grid_bottom + i * slot
                _centered(draw, str(value), (x, y, x + cell, y + slot),
                          clue_font, _SKY_INK)
        else:  # oben, letzte Gruppe naeher am Gitter
            for i, value in enumerate(reversed(clue)):
                y = grid_y - (i + 1) * slot
                _centered(draw, str(value), (x, y, x + cell, y + slot),
                          clue_font, _INK)

    # Zellen
    for r in range(rows):
        for c in range(cols):
            x = grid_x + c * cell
            y = grid_y + r * cell
            if grid is not None:
                value = grid[r][c]
                if value == 0:
                    draw.rectangle([x, y, x + cell, y + cell], fill=_BLACK_CELL)
                else:
                    _centered(draw, str(value), (x, y, x + cell, y + cell),
                              digit_font, _INK)

    # Gitterlinien
    for r in range(rows + 1):
        y = grid_y + r * cell
        draw.line([(grid_x, y), (grid_x + cols * cell, y)], fill=_GRID, width=2)
    for c in range(cols + 1):
        x = grid_x + c * cell
        draw.line([(x, grid_y), (x, grid_y + rows * cell)], fill=_GRID, width=2)
    draw.rectangle([grid_x, grid_y, grid_x + cols * cell, grid_y + rows * cell],
                   outline=_INK, width=4)

    # Legende, farblich passend zu den Hinweisen selbst
    note_y = grid_bottom + deep_bottom * slot + int(cell * 0.26)
    head_note, _, sky_note = note.partition("rechts und unten")
    draw.text((margin, note_y), head_note, font=note_font, fill=_INK)
    draw.text((margin + text_width(head_note, note_font), note_y),
              "rechts und unten" + sky_note, font=note_font, fill=_SKY_INK)

    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    image.save(path, resolution=150.0) if path.lower().endswith(".pdf") \
        else image.save(path)
    return os.path.abspath(path)


# Frueherer Name, damit bestehender Code weiterlaeuft
save_png = save_image


# ---------------------------------------------------------------------------
# Kommandozeile
# ---------------------------------------------------------------------------

def _export_dialog(
    row_clues: Sequence[LineClue],
    col_clues: Sequence[LineClue],
    solution: Sequence[Sequence[CellValue]],
    rows: int,
    cols: int,
) -> None:
    """Fragt ab, was wohin gespeichert werden soll, und legt die Dateien an."""
    what = input("\nSpeichern? (r=Raetsel, l=Loesung, b=beides, n=nichts): ")
    what = what.strip().lower()
    if what not in ("r", "l", "b"):
        return

    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("  Dafuer wird Pillow gebraucht:  pip install Pillow")
        return

    kind = input("Format? (p=PNG, d=PDF, b=beides): ").strip().lower()
    endings = {"p": (".png",), "d": (".pdf",), "b": (".png", ".pdf")}.get(kind)
    if endings is None:
        print("  Format nicht erkannt, verwende PNG.")
        endings = (".png",)

    folder = input("Ordner (leer = aktueller Ordner): ").strip()
    folder = os.path.expanduser(folder) if folder else os.getcwd()

    default_stem = f"skyline_{rows}x{cols}"
    stem = input(f"Dateiname ohne Endung (Standard {default_stem}): ").strip()
    stem = stem or default_stem

    head = f"Japanese Skylines  {rows}x{cols}"
    jobs = []
    if what in ("r", "b"):
        jobs.append(("raetsel", None, head))
    if what in ("l", "b"):
        jobs.append(("loesung", solution, head + "  -  Loesung"))

    for label, grid, title in jobs:
        for ending in endings:
            path = os.path.join(folder, f"{stem}_{label}{ending}")
            try:
                written = save_image(path, row_clues, col_clues, grid, title)
                print(f"  gespeichert: {written}")
            except OSError as exc:
                print(f"  konnte {path} nicht schreiben: {exc}")


def _parse_size(text: str, fallback: Tuple[int, int]) -> Tuple[int, int]:
    text = text.strip().lower().replace(" ", "")
    if not text:
        return fallback
    try:
        if "x" in text:
            a, _, b = text.partition("x")
            rows = int(a) if a else fallback[0]
            cols = int(b) if b else rows
        else:
            rows = cols = int(text)
    except ValueError:
        return fallback
    return (rows, cols) if 4 <= rows <= 11 and 4 <= cols <= 11 else fallback


def main() -> None:
    print(__doc__.strip())
    print()

    size = _parse_size(input("Groesse (z.B. 6 oder 5x7, Standard 6x6): "), (6, 6))

    try:
        entered = input("Anteil Skyline-Linien in Prozent (Standard 30): ").strip()
        ratio = int(entered) / 100 if entered else 0.30
        if not 0.0 < ratio < 1.0:
            raise ValueError
    except ValueError:
        print("Nicht lesbar, verwende 30%.")
        ratio = 0.30

    while True:
        rows, cols = size
        print(f"\nErzeuge {rows}x{cols} mit {ratio:.0%} Skyline-Linien ...")
        started = time.time()
        try:
            row_clues, col_clues, solution = generate_puzzle(rows, cols, ratio)
        except RuntimeError as exc:
            print(f"  {exc}")
            return
        print(f"  fertig in {time.time() - started:.2f}s\n")

        print(render(row_clues, col_clues))

        if input("\nLoesung zeigen? (j/n): ").strip().lower().startswith("j"):
            print()
            print(render(row_clues, col_clues, solution))

        _export_dialog(row_clues, col_clues, solution, rows, cols)

        if not input("\nNoch eins? (j/n): ").strip().lower().startswith("j"):
            break
        size = _parse_size(input("Groesse (leer = gleich bleiben): "), size)


if __name__ == "__main__":
    main()
