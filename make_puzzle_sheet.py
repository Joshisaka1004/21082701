"""
Erzeugt einen Satz Japanese-Skylines-Raetsel als PNG.

Raetsel und Loesungen landen getrennt im Ordner `puzzles/`.
Aufruf:  python make_puzzle_sheet.py
"""
from __future__ import annotations

import os
import random
import time

from japanese_skylines import generate_puzzle, solve, save_image, SKY

# (Zeilen, Spalten, Skyline-Anteil, Stufenname)
SHEET = [
    (5, 5, 0.20, "Einsteiger"),
    (6, 6, 0.25, "Leicht"),
    (7, 7, 0.30, "Mittel"),
    (8, 8, 0.25, "Mittel"),
    (9, 9, 0.30, "Schwer"),
    (11, 11, 0.25, "Experte"),
]

OUT = "puzzles"


def build(out_dir: str = OUT, sheet=SHEET, seed: int | None = None,
          ending: str = ".png"):
    """
    Erzeugt alle Raetsel des Satzes und gibt die Dateipfade zurueck.
    `ending` waehlt das Format - ".png" oder ".pdf".
    """
    if seed is not None:
        random.seed(seed)
    os.makedirs(out_dir, exist_ok=True)

    puzzles, solutions = [], []

    for number, (rows, cols, ratio, level) in enumerate(sheet, start=1):
        started = time.time()
        row_clues, col_clues, grid = generate_puzzle(
            rows, cols, ratio, time_limit=180
        )
        elapsed = time.time() - started

        # Eindeutigkeit unabhaengig nachpruefen, bevor irgendetwas gespeichert wird
        count, _ = solve(rows, cols, row_clues, col_clues, max_solutions=2)
        if count != 1:
            raise RuntimeError(f"Raetsel {number} hat {count} Loesungen")

        sky = sum(1 for kind, _ in list(row_clues) + list(col_clues) if kind == SKY)
        stem = f"{number}_{rows}x{cols}_{level.lower()}"
        head = f"Japanese Skylines  {rows}x{cols}  -  {level}"

        puzzles.append(save_image(
            os.path.join(out_dir, f"raetsel_{stem}{ending}"),
            row_clues, col_clues, None, head,
        ))
        solutions.append(save_image(
            os.path.join(out_dir, f"loesung_{stem}{ending}"),
            row_clues, col_clues, grid, head + "  -  Loesung",
        ))

        print(f"  {number}. {rows}x{cols} {level:<11} "
              f"{sky}/{rows + cols} Skyline-Linien, {elapsed:5.1f}s")

    return puzzles, solutions


if __name__ == "__main__":
    print(f"Erzeuge {len(SHEET)} Raetsel ...")
    made, solved = build()
    print(f"\n{len(made)} Raetsel und {len(solved)} Loesungen in '{OUT}/'")
