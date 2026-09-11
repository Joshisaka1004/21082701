"""
Japanese Skylines - Japanese Sums x Skyscrapers (Produkt-Variante)
===================================================================

Ein Japanese-Sums-Raetsel, bei dem ein Teil der Hinweise durch Skyline-
Hinweise ERSETZT ist. Der Anteil ist einstellbar; bewaehrt sind 20 bis 40
Prozent. Welche Linie welchen Typ traegt, wechselt von Raetsel zu Raetsel -
Zeilen wie Spalten koennen beides sein.

  * JAPANESE SUMS (die Mehrheit der Linien): die Summe jeder
    zusammenhaengenden Zifferngruppe, in der Reihenfolge der Linie.

  * SKYLINE (der kleinere Teil, markiert mit ^): fuer jede Gruppe das
    PRODUKT der Haeuser, die man von links bzw. von oben sieht. Die
    klassische Skyscrapers-Variante nennt die Anzahl sichtbarer Haeuser,
    die Summen-Variante ihre Summe - hier ist es ihr Produkt.

REGELN
------
1. Jede Zelle ist schwarz (leer) oder traegt eine Ziffer von 1 bis 9.
2. In jeder Zeile und jeder Spalte kommt jede Ziffer hoechstens einmal vor.
3. Jede Zeile und jede Spalte enthaelt mindestens eine Ziffer.
4. Zwei Gruppen sind durch mindestens ein schwarzes Feld getrennt. Jede
   Hinweisliste nennt ihre Gruppen in der Reihenfolge der Linie.
5. SUMMEN-Hinweis: die Summe der Ziffern der Gruppe.
6. SKYLINE-Hinweis: das Produkt der sichtbaren Haeuser der Gruppe. Innerhalb
   einer Gruppe ist ein Haus sichtbar, wenn alle Haeuser davor IN DERSELBEN
   GRUPPE niedriger sind. Das erste Haus jeder Gruppe ist immer sichtbar;
   ein schwarzes Feld beginnt die Sicht neu.

BEISPIELE fuer dieselbe Linie  3 # 5 1 7  mit Gruppen [3] und [5,1,7]

   als Summen-Linie:    3 und 13, denn 5 + 1 + 7 = 13
   als Skyline-Linie:   3 und 35, denn man sieht die 5, dann verdeckt sie
                        die 1, dann ragt die 7 heraus: 5 * 7 = 35

NUETZLICHE DEDUKTIONSREGELN
---------------------------
* Die sichtbaren Haeuser einer Spaltengruppe bilden eine streng aufsteigende
  Folge. Ein Spalten-Hinweis ist also stets ein Produkt lauter verschiedener
  Ziffern - 16 oder 25 kann kein Hinweis sein.
* Ein Spalten-Hinweis von 5 oder 7 heisst: diese Ziffer steht ganz oben in
  ihrer Gruppe, alles darunter in der Gruppe ist kleiner.
* Ein Spalten-Hinweis 1 heisst: die Gruppe beginnt mit einer 1 und faellt
  danach nur noch ab - eine 1 ganz oben verdeckt nichts, also besteht die
  Gruppe aus genau dieser 1.
* Ein grosser Spalten-Hinweis wie 504 = 7*8*9 erzwingt mindestens drei
  Zellen mit stark steigenden Werten.
* Eine Zeilengruppe mit Summe s und Laenge L braucht L verschiedene Ziffern:
  Summe 6 auf drei Zellen geht nur als 1+2+3.

Jedes erzeugte Raetsel hat garantiert genau eine Loesung.
"""
from __future__ import annotations

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
    """Spalten-Hinweis: Produkt der in jeder Gruppe sichtbaren Haeuser."""
    clue = []
    for group in _groups(line):
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
    """Alle Linien der Laenge `size` mit diesen Gruppen-Sichtprodukten."""
    return _build_patterns(size, clue, by_product=True)


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

    left = []
    for kind, clue in row_clues:
        text = " ".join(map(str, clue)) or "-"
        left.append(("^ " if kind == SKY else "  ") + text)
    label_width = max(len(s) for s in left)

    columns = [[str(v) for v in clue] for _, clue in col_clues]
    marks = ["^" if kind == SKY else "" for kind, _ in col_clues]
    depth = max(len(c) for c in columns) + 1  # eine Zeile fuer die Marker
    cell_width = max(3, max((len(s) for c in columns for s in c), default=1))

    pad = " " * (label_width + 1)
    border = pad + "+" + "+".join("-" * cell_width for _ in range(cols)) + "+"

    out = [pad + " " + " ".join(m.center(cell_width) for m in marks)]
    for level in range(depth - 1):
        line = []
        for c in columns:
            # Hinweise nach unten ausrichten, damit sie am Gitter kleben
            offset = level - (depth - 1 - len(c))
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
        out.append(f"{left[r]:>{label_width}} |" + "|".join(cells) + "|")
        out.append(border)

    sky_count = sum(1 for kind, _ in list(row_clues) + list(col_clues) if kind == SKY)
    out.append("")
    out.append("  ^ = Produkt der sichtbaren Haeuser jeder Gruppe (Skyline)")
    out.append("  sonst = Summe jeder Gruppe (Japanese Sums)")
    out.append(f"  {sky_count} von {rows + cols} Linien sind Skyline-Linien")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Kommandozeile
# ---------------------------------------------------------------------------

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

        if not input("\nNoch eins? (j/n): ").strip().lower().startswith("j"):
            break
        size = _parse_size(input("Groesse (leer = gleich bleiben): "), size)


if __name__ == "__main__":
    main()
