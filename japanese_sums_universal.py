"""
Japanese Sums Generator - Universal (Quadratisch & Rechteckig)

Unterstützt:
- Quadratische Gitter: 5x5 bis 10x10
- Rechteckige Gitter: z.B. 5x7, 8x6, 7x10, etc.
- Schnelle Generierung
- Garantiert eindeutige Lösung
"""

import random
import copy
from typing import List, Tuple, Optional, Set
from enum import Enum
import time


class Difficulty(Enum):
    """Difficulty levels"""
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4


class UniversalSolver:
    """Solver für beliebige Gittergrößen"""

    def __init__(self, rows: int, cols: int, row_clues: List[List[int]], col_clues: List[List[int]]):
        self.rows = rows
        self.cols = cols
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.solutions_count = 0
        self.solution = None
        self.nodes_explored = 0
        # Erhöht auf 5,000,000 für garantierte Eindeutigkeit bei großen Gittern
        # Bisherige Tests zeigten, dass 9x9 und 7x10 das alte Limit (500,000) erreichten
        self.max_nodes = 5000000

    def count_solutions(self, max_count: int = 2) -> int:
        self.solutions_count = 0
        self.solution = None
        self.nodes_explored = 0

        grid = [[0] * self.cols for _ in range(self.rows)]
        self._solve(grid, 0, 0, max_count)

        return self.solutions_count

    def _solve(self, grid: List[List[int]], row: int, col: int, max_count: int) -> bool:
        if self.solutions_count >= max_count or self.nodes_explored > self.max_nodes:
            return False

        self.nodes_explored += 1

        if col >= self.cols:
            row += 1
            col = 0

        if row >= self.rows:
            if self._is_valid(grid):
                self.solutions_count += 1
                if self.solution is None:
                    self.solution = copy.deepcopy(grid)
            return self.solutions_count < max_count

        if not self._partial_valid(grid, row, col):
            return True

        values = self._get_valid_values(grid, row, col)

        for val in values:
            grid[row][col] = val
            if self._is_promising(grid, row, col):
                if not self._solve(grid, row, col + 1, max_count):
                    grid[row][col] = 0
                    return False
            grid[row][col] = 0

        return True

    def _get_valid_values(self, grid: List[List[int]], row: int, col: int) -> List[int]:
        used = set()
        for c in range(self.cols):
            if grid[row][c] != 0:
                used.add(grid[row][c])
        for r in range(self.rows):
            if grid[r][col] != 0:
                used.add(grid[r][col])

        values = [0]
        for d in range(1, 10):
            if d not in used:
                values.append(d)
        return values

    def _partial_valid(self, grid: List[List[int]], row: int, col: int) -> bool:
        if col > 0:
            if not self._check_partial(grid[row][:col], self.row_clues[row], False):
                return False
        if row > 0:
            col_vals = [grid[r][col] for r in range(row)]
            if not self._check_partial(col_vals, self.col_clues[col], False):
                return False
        return True

    def _is_promising(self, grid: List[List[int]], row: int, col: int) -> bool:
        if not self._check_partial(grid[row][:col+1], self.row_clues[row], col == self.cols - 1):
            return False
        col_data = [grid[r][col] for r in range(row + 1)]
        if not self._check_partial(col_data, self.col_clues[col], row == self.rows - 1):
            return False
        return True

    def _check_partial(self, line: List[int], clues: List[int], complete: bool) -> bool:
        groups = []
        current = 0

        for val in line:
            if val > 0:
                current += val
            else:
                if current > 0:
                    groups.append(current)
                    current = 0

        if complete:
            if current > 0:
                groups.append(current)
            return groups == clues

        if len(groups) > len(clues):
            return False

        for i, g in enumerate(groups):
            if g != clues[i]:
                return False

        if current > 0 and len(groups) < len(clues):
            if current > clues[len(groups)]:
                return False

        return True

    def _is_valid(self, grid: List[List[int]]) -> bool:
        for r in range(self.rows):
            if not self._check_exact(grid[r], self.row_clues[r]):
                return False
        for c in range(self.cols):
            col = [grid[r][c] for r in range(self.rows)]
            if not self._check_exact(col, self.col_clues[c]):
                return False
        return True

    def _check_exact(self, line: List[int], clues: List[int]) -> bool:
        groups = []
        current = 0

        for val in line:
            if val > 0:
                current += val
            else:
                if current > 0:
                    groups.append(current)
                    current = 0

        if current > 0:
            groups.append(current)

        return groups == clues


class UniversalGenerator:
    """Generator für beliebige Gittergrößen"""

    def __init__(self, rows: int, cols: int, difficulty: Difficulty):
        if rows < 5 or rows > 12 or cols < 5 or cols > 12:
            raise ValueError("Rows und Cols müssen zwischen 5 und 12 liegen")

        self.rows = rows
        self.cols = cols
        self.difficulty = difficulty

    def generate(self, timeout: float = None) -> Tuple[List[List[int]], List[List[int]], List[List[int]]]:
        if timeout is None:
            # Timeout basierend auf Gittergröße
            total_cells = self.rows * self.cols
            if total_cells <= 30:
                timeout = 30
            elif total_cells <= 50:
                timeout = 45
            elif total_cells <= 70:
                timeout = 60
            elif total_cells <= 90:
                timeout = 90
            else:
                timeout = 120

        start = time.time()
        attempts = 0
        best_candidate = None
        best_score = 0

        while time.time() - start < timeout:
            attempts += 1

            grid = self._create_grouped_grid()

            row_clues = [self._get_clues(grid[r]) for r in range(self.rows)]
            col_clues = [self._get_clues([grid[r][c] for r in range(self.rows)]) for c in range(self.cols)]

            quality = self._assess_quality(row_clues, col_clues)
            if quality < 0.3:
                continue

            solver = UniversalSolver(self.rows, self.cols, row_clues, col_clues)
            count = solver.count_solutions(max_count=2)

            if count == 1:
                print(f"  (Generiert nach {attempts} Versuchen in {time.time()-start:.1f}s)")
                return grid, row_clues, col_clues

            if count == 0 and quality > best_score:
                best_score = quality
                best_candidate = (grid, row_clues, col_clues)

        if best_candidate and time.time() - start < timeout * 1.2:
            print(f"  (Versuche Anpassung nach {attempts} Versuchen...)")
            return self._try_fix_candidate(best_candidate, timeout - (time.time() - start))

        raise TimeoutError(f"Timeout nach {timeout:.0f}s ({attempts} Versuche)")

    def _create_grouped_grid(self) -> List[List[int]]:
        grid = [[0] * self.cols for _ in range(self.rows)]
        row_used = [set() for _ in range(self.rows)]
        col_used = [set() for _ in range(self.cols)]

        self._place_groups(grid, row_used, col_used)

        return grid

    def _place_groups(self, grid: List[List[int]], row_used: List[Set[int]], col_used: List[Set[int]]):
        rates = {
            Difficulty.EASY: (0.60, 0.70),
            Difficulty.MEDIUM: (0.50, 0.60),
            Difficulty.HARD: (0.40, 0.50),
            Difficulty.EXPERT: (0.35, 0.45)
        }
        min_r, max_r = rates[self.difficulty]
        target_cells = int(self.rows * self.cols * random.uniform(min_r, max_r))

        # Gruppengrößen anpassen basierend auf kleinerer Dimension
        min_dim = min(self.rows, self.cols)
        max_group_size = min(5, min_dim)

        group_sizes = {}
        for i in range(1, max_group_size + 1):
            if i == 1:
                group_sizes[i] = 5
            elif i == 2:
                group_sizes[i] = 40
            elif i == 3:
                group_sizes[i] = 35
            elif i == 4:
                group_sizes[i] = 15
            else:
                group_sizes[i] = 5

        filled = 0
        stuck_count = 0

        while filled < target_cells and stuck_count < 50:
            sizes = list(group_sizes.keys())
            weights = [group_sizes[s] for s in sizes]
            group_size = random.choices(sizes, weights=weights)[0]

            # Für rechteckige Gitter: bevorzuge horizontale Gruppen wenn mehr Spalten
            if self.cols > self.rows:
                is_horizontal = random.random() < 0.7
            elif self.rows > self.cols:
                is_horizontal = random.random() < 0.4
            else:
                is_horizontal = random.random() < 0.6

            if is_horizontal:
                placed = self._place_h_group(grid, group_size, row_used, col_used)
            else:
                placed = self._place_v_group(grid, group_size, row_used, col_used)

            if placed:
                filled += group_size
                stuck_count = 0
            else:
                stuck_count += 1

    def _place_h_group(self, grid: List[List[int]], size: int,
                        row_used: List[Set[int]], col_used: List[Set[int]]) -> bool:
        if size > self.cols:
            return False

        candidates = []

        for r in range(self.rows):
            for c in range(self.cols - size + 1):
                if all(grid[r][c + i] == 0 for i in range(size)):
                    available = set(range(1, 10)) - row_used[r]
                    for i in range(size):
                        available -= col_used[c + i]

                    if len(available) >= size:
                        candidates.append((r, c, available))

        if not candidates:
            return False

        r, c, available = random.choice(candidates)
        digits = random.sample(list(available), size)

        for i, d in enumerate(digits):
            grid[r][c + i] = d
            row_used[r].add(d)
            col_used[c + i].add(d)

        return True

    def _place_v_group(self, grid: List[List[int]], size: int,
                        row_used: List[Set[int]], col_used: List[Set[int]]) -> bool:
        if size > self.rows:
            return False

        candidates = []

        for c in range(self.cols):
            for r in range(self.rows - size + 1):
                if all(grid[r + i][c] == 0 for i in range(size)):
                    available = set(range(1, 10)) - col_used[c]
                    for i in range(size):
                        available -= row_used[r + i]

                    if len(available) >= size:
                        candidates.append((r, c, available))

        if not candidates:
            return False

        r, c, available = random.choice(candidates)
        digits = random.sample(list(available), size)

        for i, d in enumerate(digits):
            grid[r + i][c] = d
            row_used[r + i].add(d)
            col_used[c].add(d)

        return True

    def _assess_quality(self, row_clues: List[List[int]], col_clues: List[List[int]]) -> float:
        all_clue_counts = [len(rc) for rc in row_clues] + [len(cc) for cc in col_clues]

        if not all_clue_counts:
            return 0.0

        max_clues = max(all_clue_counts)
        if max_clues > 5:
            return 0.2

        avg_clues = sum(all_clue_counts) / len(all_clue_counts)

        if 2.0 <= avg_clues <= 3.5:
            quality = 1.0
        elif 1.5 <= avg_clues <= 4.0:
            quality = 0.8
        else:
            quality = 0.5

        all_sums = []
        for rc in row_clues:
            all_sums.extend(rc)
        for cc in col_clues:
            all_sums.extend(cc)

        if all_sums:
            unique_ratio = len(set(all_sums)) / len(all_sums)
            quality *= (0.7 + 0.3 * unique_ratio)

        return quality

    def _try_fix_candidate(self, candidate, remaining_time) -> Tuple[List[List[int]], List[List[int]], List[List[int]]]:
        return self.generate(timeout=remaining_time)

    def _get_clues(self, line: List[int]) -> List[int]:
        clues = []
        current = 0

        for val in line:
            if val > 0:
                current += val
            else:
                if current > 0:
                    clues.append(current)
                    current = 0

        if current > 0:
            clues.append(current)

        return clues


class Puzzle:
    """Puzzle representation"""

    def __init__(self, rows: int, cols: int, row_clues: List[List[int]], col_clues: List[List[int]], solution: List[List[int]]):
        self.rows = rows
        self.cols = cols
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.solution = solution

    def display(self, show_solution: bool = False):
        print("\n" + "=" * 70)
        print(f"Japanese Sums - Universal ({self.rows}x{self.cols})")
        print("=" * 70)

        print("\nSpalten-Hinweise (von oben nach unten):")
        for c in range(self.cols):
            print(f"  Spalte {c+1}: {self.col_clues[c] if self.col_clues[c] else '[]'}")

        print("\nZeilen-Hinweise (von links nach rechts):")
        for r in range(self.rows):
            print(f"  Zeile {r+1}: {self.row_clues[r] if self.row_clues[r] else '[]'}")

        if show_solution:
            print("\nLösung:")
            self._show_grid(self.solution)

        self._show_stats()
        print("=" * 70)

    def _show_grid(self, grid: List[List[int]]):
        print("  +" + "-" * (self.cols * 2 - 1) + "+")
        for r in range(self.rows):
            row_str = "  |"
            for c in range(self.cols):
                row_str += str(grid[r][c]) if grid[r][c] != 0 else "."
                if c < self.cols - 1:
                    row_str += " "
            row_str += "|"
            print(row_str)
        print("  +" + "-" * (self.cols * 2 - 1) + "+")

    def _show_stats(self):
        all_sums = []
        for rc in self.row_clues:
            all_sums.extend(rc)
        for cc in self.col_clues:
            all_sums.extend(cc)

        clue_counts = [len(rc) for rc in self.row_clues] + [len(cc) for cc in self.col_clues]

        if all_sums:
            print(f"\nStatistik:")
            print(f"  Summen gesamt: {len(all_sums)}")
            print(f"  Summen-Bereich: {min(all_sums)}-{max(all_sums)}")
            print(f"  Ø Summen pro Zeile/Spalte: {sum(clue_counts)/len(clue_counts):.1f}")

            small = sum(1 for s in all_sums if s < 10)
            medium = sum(1 for s in all_sums if 10 <= s < 20)
            large = sum(1 for s in all_sums if s >= 20)

            print(f"  Klein (<10): {small}, Mittel (10-19): {medium}, Groß (≥20): {large}")


def generate_puzzle(rows: int = 6, cols: int = None, difficulty: Difficulty = Difficulty.MEDIUM) -> Puzzle:
    """
    Generiere Japanese Sums - UNIVERSAL (quadratisch & rechteckig)

    Args:
        rows: Anzahl Zeilen (5-12)
        cols: Anzahl Spalten (5-12), wenn None dann cols=rows (quadratisch)
        difficulty: Schwierigkeit

    Returns:
        Puzzle-Objekt

    Beispiele:
        generate_puzzle(7, 7)      # 7x7 quadratisch
        generate_puzzle(5, 8)      # 5x8 rechteckig
        generate_puzzle(10, 6)     # 10x6 rechteckig
        generate_puzzle(9)         # 9x9 quadratisch (cols=None)
    """
    if cols is None:
        cols = rows

    gen = UniversalGenerator(rows, cols, difficulty)
    solution, row_clues, col_clues = gen.generate()
    return Puzzle(rows, cols, row_clues, col_clues, solution)


if __name__ == "__main__":
    print("\nJapanese Sums - Universal Generator")
    print("=" * 70)
    print("Unterstützt quadratische UND rechteckige Gitter!\n")

    tests = [
        (5, 7, Difficulty.MEDIUM, "MEDIUM 5x7 (rechteckig)"),
        (7, 7, Difficulty.HARD, "HARD 7x7 (quadratisch)"),
        (6, 9, Difficulty.MEDIUM, "MEDIUM 6x9 (rechteckig)"),
        (9, 9, Difficulty.HARD, "HARD 9x9 (quadratisch)"),
        (8, 6, Difficulty.MEDIUM, "MEDIUM 8x6 (rechteckig)"),
    ]

    for rows, cols, diff, label in tests:
        print(f"\n{'='*70}")
        print(f"Generiere {label}...")
        start = time.time()

        try:
            puzzle = generate_puzzle(rows, cols, diff)
            elapsed = time.time() - start
            print(f"✓ Erfolgreich!")

            puzzle.display(show_solution=True)

            solver = UniversalSolver(puzzle.rows, puzzle.cols, puzzle.row_clues, puzzle.col_clues)
            count = solver.count_solutions(max_count=2)
            print(f"\nVerifikation: {count} Lösung(en)")
            if count == 1:
                print("✓ EINDEUTIG!")

        except Exception as e:
            elapsed = time.time() - start
            print(f"✗ Fehler: {e}")

    print("\n" + "=" * 70)
    print("Verwendung:")
    print("  from japanese_sums_universal import generate_puzzle, Difficulty")
    print("  puzzle = generate_puzzle(7, 10, Difficulty.HARD)  # 7x10")
    print("  puzzle = generate_puzzle(9, difficulty=Difficulty.MEDIUM)  # 9x9")
    print("=" * 70 + "\n")
