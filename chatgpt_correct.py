"""
Unified Japanese Sums generator (sizes 5x5 through 13x13 and rectangles) with export options.

This variant biases clue generation toward a wider mix of small, medium, and
large sums while keeping uniqueness checks intact.
"""
from __future__ import annotations

import os
import random
import unicodedata
from copy import deepcopy
from functools import lru_cache
from itertools import combinations, permutations
from typing import List, Sequence, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:  # Pillow might be unavailable in some environments
    Image = None  # type: ignore
    ImageDraw = None  # type: ignore
    ImageFont = None  # type: ignore


Digit = int
CellValue = int  # 0 for black, 1-9 for digits
Pattern = Tuple[CellValue, ...]


# ----------------------------- Solver utilities -----------------------------

def _min_cells_for_groups(groups_remaining: int) -> int:
    if groups_remaining <= 0:
        return 0
    return groups_remaining + (groups_remaining - 1)


@lru_cache(maxsize=None)
def _digit_sequences_for_sum_cached(target: int, length: int, used_tuple: Tuple[int, ...]) -> List[Tuple[Digit, ...]]:
    """Return ordered digit tuples of given length that sum to target without reusing used digits."""
    candidates: List[Tuple[Digit, ...]] = []
    used = set(used_tuple)
    available = [d for d in range(1, 10) if d not in used]
    for combo in combinations(available, length):
        if sum(combo) != target:
            continue
        for perm in permutations(combo):
            candidates.append(perm)
    return candidates


def _digit_sequences_for_sum(target: int, length: int, used: set[int]) -> List[Tuple[Digit, ...]]:
    return _digit_sequences_for_sum_cached(target, length, tuple(sorted(used)))


@lru_cache(maxsize=None)
def _build_line_patterns_cached(size: int, clues_key: Tuple[int, ...]) -> List[Pattern]:
    clues = list(clues_key)
    results: List[Pattern] = []

    def backtrack(clue_idx: int, pos: int, used: set[int], current: List[CellValue]) -> None:
        if clue_idx == len(clues):
            if len(current) < size:
                current.extend([0] * (size - len(current)))
            results.append(tuple(current))
            for _ in range(size - pos):
                current.pop()
            return

        remaining_groups = len(clues) - clue_idx
        min_needed = _min_cells_for_groups(remaining_groups)
        max_lead = size - pos - min_needed
        for lead in range(max_lead + 1):
            current.extend([0] * lead)
            pos_after_lead = pos + lead
            remaining_slots = size - pos_after_lead
            min_after_group = _min_cells_for_groups(remaining_groups - 1)
            for length in range(1, remaining_slots - min_after_group + 1):
                for digits in _digit_sequences_for_sum(clues[clue_idx], length, used):
                    used.update(digits)
                    current.extend(digits)
                    new_pos = pos_after_lead + length
                    if clue_idx < len(clues) - 1:
                        if new_pos >= size:
                            current[:] = current[:pos_after_lead]
                            used.difference_update(digits)
                            continue
                        current.append(0)
                        backtrack(clue_idx + 1, new_pos + 1, used, current)
                        current.pop()
                    else:
                        backtrack(clue_idx + 1, new_pos, used, current)
                    current[:] = current[:pos_after_lead]
                    used.difference_update(digits)
            current[:] = current[:pos]

    backtrack(0, 0, set(), [])
    return results


def build_line_patterns(size: int, clues: Sequence[int]) -> List[Pattern]:
    """Generate all row/column patterns matching the clue list."""
    return list(_build_line_patterns_cached(size, tuple(clues)))


def _derive_clues_from_pattern(pattern: Sequence[CellValue]) -> List[int]:
    clues = []
    acc = 0
    for val in pattern + (0,):
        if val == 0:
            if acc:
                clues.append(acc)
            acc = 0
        else:
            acc += val
    return clues


def solve_japanese_sums(
    rows: int, cols: int, row_clues: List[List[int]], col_clues: List[List[int]], max_solutions: int = 2
) -> Tuple[int, List[List[CellValue]] | None]:
    """Return (solution_count, solution_grid_or_None). Stops after max_solutions."""
    row_domains = [build_line_patterns(cols, clues) for clues in row_clues]
    col_domains = [build_line_patterns(rows, clues) for clues in col_clues]

    if any(not opts for opts in row_domains) or any(not opts for opts in col_domains):
        return 0, None

    def propagate(r_dom: List[List[Pattern]], c_dom: List[List[Pattern]]) -> bool:
        changed = True
        while changed:
            changed = False
            for r in range(rows):
                for c in range(cols):
                    row_vals = {p[c] for p in r_dom[r]}
                    col_vals = {p[r] for p in c_dom[c]}
                    allowed = row_vals & col_vals
                    if not allowed:
                        return False
                    new_r = [p for p in r_dom[r] if p[c] in allowed]
                    if len(new_r) != len(r_dom[r]):
                        r_dom[r] = new_r
                        changed = True
                    new_c = [p for p in c_dom[c] if p[r] in allowed]
                    if len(new_c) != len(c_dom[c]):
                        c_dom[c] = new_c
                        changed = True
            if any(len(opts) == 0 for opts in r_dom) or any(len(opts) == 0 for opts in c_dom):
                return False
        return True

    def search(r_dom: List[List[Pattern]], c_dom: List[List[Pattern]], solutions: List[List[List[CellValue]]]) -> None:
        if len(solutions) >= max_solutions:
            return
        if not propagate(r_dom, c_dom):
            return
        if all(len(opts) == 1 for opts in r_dom) and all(len(opts) == 1 for opts in c_dom):
            grid = [list(opts[0]) for opts in r_dom]
            solutions.append(grid)
            return
        candidates = [(len(r_dom[i]), ('r', i)) for i in range(rows) if len(r_dom[i]) > 1] + [
            (len(c_dom[j]), ('c', j)) for j in range(cols) if len(c_dom[j]) > 1
        ]
        candidates.sort()
        _, (axis, idx) = candidates[0]
        patterns = r_dom[idx] if axis == 'r' else c_dom[idx]
        for pat in patterns:
            new_r = deepcopy(r_dom)
            new_c = deepcopy(c_dom)
            if axis == 'r':
                new_r[idx] = [pat]
            else:
                new_c[idx] = [pat]
            search(new_r, new_c, solutions)
            if len(solutions) >= max_solutions:
                return

    collected: List[List[List[CellValue]]] = []
    search(row_domains, col_domains, collected)
    return len(collected), (collected[0] if collected else None)


# --------------------------- Puzzle construction ---------------------------

def random_solution_grid(rows: int, cols: int, black_prob: float) -> List[List[CellValue]]:
    """Create a random fully-specified grid with blacks and digits obeying row/column uniqueness."""
    grid = [[None for _ in range(cols)] for _ in range(rows)]

    def backtrack(pos: int) -> bool:
        if pos == rows * cols:
            return True
        r, c = divmod(pos, cols)
        if random.random() < black_prob:
            grid[r][c] = 0
            if backtrack(pos + 1):
                return True
            grid[r][c] = None
        used_row = {grid[r][k] for k in range(cols) if isinstance(grid[r][k], int) and grid[r][k] != 0}
        used_col = {grid[k][c] for k in range(rows) if isinstance(grid[k][c], int) and grid[k][c] != 0}
        candidates = [d for d in range(1, 10) if d not in used_row and d not in used_col]
        random.shuffle(candidates)
        for d in candidates:
            grid[r][c] = d
            if backtrack(pos + 1):
                return True
        grid[r][c] = None
        return False

    for _ in range(150):
        if backtrack(0):
            row_ok = all(any(cell == 0 for cell in row) and any(cell != 0 for cell in row) for row in grid)
            col_ok = all(any(grid[r][c] == 0 for r in range(rows)) and any(grid[r][c] != 0 for r in range(rows)) for c in range(cols))
            max_row_whites = max(sum(1 for cell in row if cell != 0) for row in grid)
            max_col_whites = max(sum(1 for r in range(rows) if grid[r][c] != 0) for c in range(cols))
            if row_ok and col_ok and max_row_whites <= 9 and max_col_whites <= 9:
                return grid
        grid = [[None for _ in range(cols)] for _ in range(rows)]
    raise RuntimeError("Failed to build random solution grid")


def _sample_black_prob(rows: int, cols: int, attempt: int) -> float:
    """Vary black density to encourage a mix of clue sizes."""
    longest = max(rows, cols)
    band = attempt % 3
    if band == 0:
        low = 0.18 + 0.01 * max(0, longest - 5)
        high = 0.32 + 0.01 * max(0, longest - 5)
    elif band == 1:
        low = 0.26 + 0.012 * max(0, longest - 5)
        high = 0.44 + 0.014 * max(0, longest - 5)
    else:
        low = 0.34 + 0.015 * max(0, longest - 5)
        high = 0.52 + 0.02 * max(0, longest - 5)
    return random.uniform(min(low, 0.6), min(high, 0.7))


def _clue_spread_ok(row_clues: List[List[int]], col_clues: List[List[int]], rows: int, cols: int) -> bool:
    flat = [v for sub in row_clues + col_clues for v in sub]
    if not flat:
        return False
    small = sum(1 for v in flat if v <= 10)
    medium = sum(1 for v in flat if 11 <= v <= 17)
    large = sum(1 for v in flat if v >= 18)
    total = len(flat)
    medium_large = medium + large
    if total < 4:
        return True
    min_ml = max(2, total // 6)
    if medium_large < min_ml:
        return False
    if small / total > 0.8:
        return False
    if max(rows, cols) >= 9 and large == 0:
        return False
    return True


def derive_clues(grid: List[List[CellValue]]) -> Tuple[List[List[int]], List[List[int]]]:
    rows = [list(row) for row in grid]
    cols = [[grid[r][c] for r in range(len(grid))] for c in range(len(grid[0]))]
    return [
        _derive_clues_from_pattern(tuple(row)) for row in rows
    ], [
        _derive_clues_from_pattern(tuple(col)) for col in cols
    ]


def generate_unique_puzzle(rows: int = 5, cols: int = 5, max_attempts: int = 800) -> Tuple[List[List[int]], List[List[int]], List[List[CellValue]]]:
    """Generate a Japanese Sums puzzle (row clues, col clues, solution grid)."""
    for attempt in range(1, max_attempts + 1):
        black_prob = _sample_black_prob(rows, cols, attempt)
        try:
            solution = random_solution_grid(rows, cols, black_prob)
        except RuntimeError:
            continue
        row_clues, col_clues = derive_clues(solution)
        if any(len(rc) == 0 for rc in row_clues) or any(len(cc) == 0 for cc in col_clues):
            continue
        if not _clue_spread_ok(row_clues, col_clues, rows, cols):
            continue
        sol_count, solved_grid = solve_japanese_sums(rows, cols, row_clues, col_clues, max_solutions=2)
        if sol_count == 1:
            return row_clues, col_clues, solved_grid
    raise RuntimeError("Failed to generate a unique puzzle after multiple attempts")


if __name__ == "__main__":
    import time

    print("\n" + "="*70)
    print("TEST: ChatGPT's KORREKTER Code")
    print("="*70)

    test_configs = [
        (5, 5, "5x5"),
        (6, 6, "6x6"),
        (7, 7, "7x7"),
        (8, 8, "8x8"),
        (9, 9, "9x9"),
    ]

    for rows, cols, label in test_configs:
        print(f"\nGeneriere {label}...")
        start = time.time()
        try:
            row_clues, col_clues, solution = generate_unique_puzzle(rows, cols, max_attempts=800)
            elapsed = time.time() - start

            # Verify
            count, _ = solve_japanese_sums(rows, cols, row_clues, col_clues, max_solutions=2)

            empty_rows = sum(1 for rc in row_clues if len(rc) == 0)
            empty_cols = sum(1 for cc in col_clues if len(cc) == 0)

            print(f"✓ SUCCESS in {elapsed:.2f}s")
            print(f"  Solutions: {count}")
            print(f"  Empty rows/cols: {empty_rows}/{empty_cols}")
            print(f"  Row clues: {row_clues[:2]}...")
            print(f"  Col clues: {col_clues[:2]}...")

        except Exception as e:
            elapsed = time.time() - start
            print(f"✗ FAILED after {elapsed:.2f}s: {e}")
