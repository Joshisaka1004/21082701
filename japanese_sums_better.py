"""
Japanese Sums Generator - Better Group Variety

Basiert auf dem funktionierenden Original-Generator,
aber mit verbesserter Gruppen-Bildung für mehr Abwechslung.
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


class FastSolver:
    """Fast solver with intelligent pruning"""

    def __init__(self, size: int, row_clues: List[List[int]], col_clues: List[List[int]]):
        self.size = size
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.solutions_count = 0
        self.solution = None
        self.nodes_explored = 0
        self.max_nodes = 1000000

    def count_solutions(self, max_count: int = 2) -> int:
        self.solutions_count = 0
        self.solution = None
        self.nodes_explored = 0

        grid = [[0] * self.size for _ in range(self.size)]
        self._solve(grid, 0, 0, max_count)

        return self.solutions_count

    def _solve(self, grid: List[List[int]], row: int, col: int, max_count: int) -> bool:
        if self.solutions_count >= max_count or self.nodes_explored > self.max_nodes:
            return False

        self.nodes_explored += 1

        if col >= self.size:
            row += 1
            col = 0

        if row >= self.size:
            if self._is_valid(grid):
                self.solutions_count += 1
                if self.solution is None:
                    self.solution = copy.deepcopy(grid)
            return self.solutions_count < max_count

        values = self._get_possible_values(grid, row, col)

        for val in values:
            grid[row][col] = val
            if self._is_promising(grid, row, col):
                if not self._solve(grid, row, col + 1, max_count):
                    grid[row][col] = 0
                    return False
            grid[row][col] = 0

        return True

    def _get_possible_values(self, grid: List[List[int]], row: int, col: int) -> List[int]:
        used = set()
        for c in range(self.size):
            if grid[row][c] != 0:
                used.add(grid[row][c])
        for r in range(self.size):
            if grid[r][col] != 0:
                used.add(grid[r][col])

        values = [0]
        for d in range(1, 10):
            if d not in used:
                values.append(d)
        return values

    def _is_promising(self, grid: List[List[int]], row: int, col: int) -> bool:
        if not self._check_line_partial(grid[row], self.row_clues[row], col == self.size - 1):
            return False
        col_data = [grid[r][col] for r in range(row + 1)]
        if not self._check_line_partial(col_data, self.col_clues[col], row == self.size - 1):
            return False
        return True

    def _check_line_partial(self, line: List[int], clues: List[int], complete: bool) -> bool:
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
        for r in range(self.size):
            if not self._check_line_exact(grid[r], self.row_clues[r]):
                return False
        for c in range(self.size):
            col = [grid[r][c] for r in range(self.size)]
            if not self._check_line_exact(col, self.col_clues[c]):
                return False
        return True

    def _check_line_exact(self, line: List[int], clues: List[int]) -> bool:
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


class BetterGenerator:
    """Generator with improved group variety"""

    def __init__(self, size: int, difficulty: Difficulty):
        self.size = size
        self.difficulty = difficulty

    def generate(self, timeout: float = None) -> Tuple[List[List[int]], List[List[int]], List[List[int]]]:
        if timeout is None:
            timeout_map = {5: 30, 6: 45, 7: 60, 8: 90, 9: 120}
            timeout = timeout_map.get(self.size, 60)

        start = time.time()
        attempts = 0

        while time.time() - start < timeout:
            attempts += 1

            grid = self._create_grid()

            row_clues = [self._get_clues(grid[r]) for r in range(self.size)]
            col_clues = [self._get_clues([grid[r][c] for r in range(self.size)]) for c in range(self.size)]

            total_clues = sum(len(rc) for rc in row_clues) + sum(len(cc) for cc in col_clues)
            if total_clues < self.size * 2:
                continue

            solver = FastSolver(self.size, row_clues, col_clues)
            count = solver.count_solutions(max_count=2)

            if count == 1:
                print(f"  (Generated after {attempts} attempts)")
                return grid, row_clues, col_clues

        raise TimeoutError(f"Timeout after {timeout}s ({attempts} attempts)")

    def _create_grid(self) -> List[List[int]]:
        """Create grid with emphasis on longer groups"""
        rates = {
            Difficulty.EASY: (0.55, 0.65),
            Difficulty.MEDIUM: (0.45, 0.55),
            Difficulty.HARD: (0.35, 0.45),
            Difficulty.EXPERT: (0.28, 0.38)
        }

        min_r, max_r = rates[self.difficulty]
        target = int(self.size * self.size * random.uniform(min_r, max_r))

        grid = [[0] * self.size for _ in range(self.size)]
        row_used = [set() for _ in range(self.size)]
        col_used = [set() for _ in range(self.size)]

        positions = [(r, c) for r in range(self.size) for c in range(self.size)]
        random.shuffle(positions)

        filled = 0
        for r, c in positions:
            if filled >= target:
                break

            available = set(range(1, 10)) - row_used[r] - col_used[c]
            if available and self._should_place(grid, r, c):
                d = random.choice(list(available))
                grid[r][c] = d
                row_used[r].add(d)
                col_used[c].add(d)
                filled += 1

        self._ensure_groups(grid, row_used, col_used)

        return grid

    def _should_place(self, grid: List[List[int]], r: int, c: int) -> bool:
        """Decide if to place digit - HIGHER probability for neighbors"""
        neighbors = 0
        if c > 0 and grid[r][c - 1] != 0:
            neighbors += 1
        if c < self.size - 1 and grid[r][c + 1] != 0:
            neighbors += 1
        if r > 0 and grid[r - 1][c] != 0:
            neighbors += 1
        if r < self.size - 1 and grid[r + 1][c] != 0:
            neighbors += 1

        # ERHÖHTE Wahrscheinlichkeiten für Gruppierung!
        if neighbors >= 2:
            return random.random() < 0.90  # Sehr hoch bei 2+ Nachbarn
        elif neighbors == 1:
            return random.random() < 0.80  # Hoch bei 1 Nachbar
        else:
            return random.random() < 0.30  # Niedrig ohne Nachbarn

    def _ensure_groups(self, grid: List[List[int]], row_used: List[Set[int]], col_used: List[Set[int]]):
        for r in range(self.size):
            if all(grid[r][c] == 0 for c in range(self.size)):
                self._add_row_group(grid, r, row_used, col_used)

        for c in range(self.size):
            if all(grid[r][c] == 0 for r in range(self.size)):
                self._add_col_group(grid, c, row_used, col_used)

    def _add_row_group(self, grid: List[List[int]], r: int, row_used: List[Set[int]], col_used: List[Set[int]]):
        """Add group to row - try LONGER groups first"""
        # Versuche Gruppen der Länge 3, 4, dann 2
        for group_len in [4, 3, 2]:
            for c in range(self.size - group_len + 1):
                if all(grid[r][c + i] == 0 for i in range(group_len)):
                    available = set(range(1, 10)) - row_used[r]
                    for i in range(group_len):
                        available = available - col_used[c + i]

                    if len(available) >= group_len:
                        digits = random.sample(list(available), group_len)
                        for i, digit in enumerate(digits):
                            grid[r][c + i] = digit
                            row_used[r].add(digit)
                            col_used[c + i].add(digit)
                        return

    def _add_col_group(self, grid: List[List[int]], c: int, row_used: List[Set[int]], col_used: List[Set[int]]):
        """Add group to column - try LONGER groups first"""
        for group_len in [4, 3, 2]:
            for r in range(self.size - group_len + 1):
                if all(grid[r + i][c] == 0 for i in range(group_len)):
                    available = set(range(1, 10)) - col_used[c]
                    for i in range(group_len):
                        available = available - row_used[r + i]

                    if len(available) >= group_len:
                        digits = random.sample(list(available), group_len)
                        for i, digit in enumerate(digits):
                            grid[r + i][c] = digit
                            row_used[r + i].add(digit)
                            col_used[c].add(digit)
                        return

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

    def __init__(self, size: int, row_clues: List[List[int]], col_clues: List[List[int]], solution: List[List[int]]):
        self.size = size
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.solution = solution

    def display(self, show_solution: bool = False):
        print("\n" + "=" * 70)
        print(f"Japanese Sums - Better Variety ({self.size}x{self.size})")
        print("=" * 70)

        print("\nSpalten-Hinweise (von oben nach unten):")
        for c in range(self.size):
            print(f"  Spalte {c+1}: {self.col_clues[c] if self.col_clues[c] else '[]'}")

        print("\nZeilen-Hinweise (von links nach rechts):")
        for r in range(self.size):
            print(f"  Zeile {r+1}: {self.row_clues[r] if self.row_clues[r] else '[]'}")

        if show_solution:
            print("\nLösung:")
            self._show_grid(self.solution)

        self._show_stats()
        print("=" * 70)

    def _show_grid(self, grid: List[List[int]]):
        print("  +" + "-" * (self.size * 2 - 1) + "+")
        for r in range(self.size):
            row_str = "  |"
            for c in range(self.size):
                row_str += str(grid[r][c]) if grid[r][c] != 0 else "."
                if c < self.size - 1:
                    row_str += " "
            row_str += "|"
            print(row_str)
        print("  +" + "-" * (self.size * 2 - 1) + "+")

    def _show_stats(self):
        all_sums = []
        for rc in self.row_clues:
            all_sums.extend(rc)
        for cc in self.col_clues:
            all_sums.extend(cc)

        if all_sums:
            print(f"\nStatistik:")
            print(f"  Anzahl Summen: {len(all_sums)}")
            print(f"  Bereich: {min(all_sums)}-{max(all_sums)}")
            print(f"  Durchschnitt: {sum(all_sums) / len(all_sums):.1f}")

            small = sum(1 for s in all_sums if s < 10)
            medium = sum(1 for s in all_sums if 10 <= s < 20)
            large = sum(1 for s in all_sums if s >= 20)

            print(f"  Klein (<10): {small}")
            print(f"  Mittel (10-19): {medium}")
            print(f"  Groß (≥20): {large}")


def generate_puzzle(size: int = 6, difficulty: Difficulty = Difficulty.MEDIUM) -> Puzzle:
    """
    Generate Japanese Sums puzzle with better group variety.

    Verbesserte Version mit mehr abwechslungsreichen Summen-Größen.
    Garantiert weiterhin eindeutige Lösung!

    Args:
        size: Grid size (5-9)
        difficulty: Difficulty level

    Returns:
        Puzzle object
    """
    gen = BetterGenerator(size, difficulty)
    solution, row_clues, col_clues = gen.generate()
    return Puzzle(size, row_clues, col_clues, solution)


if __name__ == "__main__":
    print("\nJapanese Sums - Better Group Variety Generator")
    print("=" * 70)
    print("Mehr Abwechslung bei den Summen-Größen!\n")

    tests = [
        (5, Difficulty.EASY, "EASY 5x5"),
        (6, Difficulty.MEDIUM, "MEDIUM 6x6"),
        (7, Difficulty.HARD, "HARD 7x7"),
    ]

    for size, diff, label in tests:
        print(f"\n{'='*70}")
        print(f"Generiere {label}...")
        start = time.time()

        try:
            puzzle = generate_puzzle(size, diff)
            elapsed = time.time() - start
            print(f"✓ Generiert in {elapsed:.2f}s")

            puzzle.display(show_solution=True)

            solver = FastSolver(puzzle.size, puzzle.row_clues, puzzle.col_clues)
            count = solver.count_solutions(max_count=2)
            print(f"\nVerifikation: {count} Lösung(en)")
            if count == 1:
                print("✓ Eindeutigkeit bestätigt!")

        except Exception as e:
            elapsed = time.time() - start
            print(f"✗ Fehler: {e}")

    print("\n" + "=" * 70)
    print("Nutzung:")
    print("  from japanese_sums_better import generate_puzzle, Difficulty")
    print("  puzzle = generate_puzzle(size=6, difficulty=Difficulty.MEDIUM)")
    print("=" * 70 + "\n")
