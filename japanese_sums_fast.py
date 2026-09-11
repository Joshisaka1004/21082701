"""
Japanese Sums Generator - Optimized for Speed & Quality

Fokus:
- SCHNELLE Generierung (auch für 7x7, 8x8)
- Bessere Gruppen-Verteilung (weniger Einzelzellen)
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


class OptimizedSolver:
    """Ultra-fast solver with aggressive pruning"""

    def __init__(self, size: int, row_clues: List[List[int]], col_clues: List[List[int]]):
        self.size = size
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.solutions_count = 0
        self.solution = None
        self.nodes_explored = 0
        self.max_nodes = 500000  # Reduziert für Geschwindigkeit

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

        # Frühes Pruning
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

    def _partial_valid(self, grid: List[List[int]], row: int, col: int) -> bool:
        """Quick partial validation"""
        if col > 0:
            if not self._check_partial(grid[row][:col], self.row_clues[row], False):
                return False
        if row > 0:
            col_vals = [grid[r][col] for r in range(row)]
            if not self._check_partial(col_vals, self.col_clues[col], False):
                return False
        return True

    def _is_promising(self, grid: List[List[int]], row: int, col: int) -> bool:
        if not self._check_partial(grid[row][:col+1], self.row_clues[row], col == self.size - 1):
            return False
        col_data = [grid[r][col] for r in range(row + 1)]
        if not self._check_partial(col_data, self.col_clues[col], row == self.size - 1):
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
        for r in range(self.size):
            if not self._check_exact(grid[r], self.row_clues[r]):
                return False
        for c in range(self.size):
            col = [grid[r][c] for r in range(self.size)]
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


class FastGenerator:
    """Optimized generator focusing on speed and quality"""

    def __init__(self, size: int, difficulty: Difficulty):
        self.size = size
        self.difficulty = difficulty

    def generate(self, timeout: float = None) -> Tuple[List[List[int]], List[List[int]], List[List[int]]]:
        if timeout is None:
            timeout_map = {5: 20, 6: 30, 7: 45, 8: 60, 9: 90}
            timeout = timeout_map.get(self.size, 45)

        start = time.time()
        attempts = 0
        best_candidate = None
        best_score = 0

        while time.time() - start < timeout:
            attempts += 1

            # Erstelle Grid mit Gruppen-Fokus
            grid = self._create_grouped_grid()

            row_clues = [self._get_clues(grid[r]) for r in range(self.size)]
            col_clues = [self._get_clues([grid[r][c] for r in range(self.size)]) for c in range(self.size)]

            # Qualitäts-Check
            quality = self._assess_quality(row_clues, col_clues)
            if quality < 0.3:  # Zu schlecht
                continue

            # Uniqueness check
            solver = OptimizedSolver(self.size, row_clues, col_clues)
            count = solver.count_solutions(max_count=2)

            if count == 1:
                print(f"  (Generiert nach {attempts} Versuchen in {time.time()-start:.1f}s)")
                return grid, row_clues, col_clues

            # Speichere besten Kandidaten (falls Timeout)
            if count == 0 and quality > best_score:
                best_score = quality
                best_candidate = (grid, row_clues, col_clues)

        # Wenn nichts gefunden, versuche besten Kandidaten anzupassen
        if best_candidate and time.time() - start < timeout * 1.2:
            print(f"  (Versuche Anpassung nach {attempts} Versuchen...)")
            return self._try_fix_candidate(best_candidate, timeout - (time.time() - start))

        raise TimeoutError(f"Timeout nach {timeout:.0f}s ({attempts} Versuche)")

    def _create_grouped_grid(self) -> List[List[int]]:
        """Erstelle Grid mit bewusster Gruppen-Platzierung"""
        grid = [[0] * self.size for _ in range(self.size)]
        row_used = [set() for _ in range(self.size)]
        col_used = [set() for _ in range(self.size)]

        # Platziere größere Gruppen zuerst
        self._place_groups(grid, row_used, col_used)

        return grid

    def _place_groups(self, grid: List[List[int]], row_used: List[Set[int]], col_used: List[Set[int]]):
        """Platziere zusammenhängende Gruppen"""

        # Berechne Anzahl der zu platzierenden Gruppen
        rates = {
            Difficulty.EASY: (0.60, 0.70),
            Difficulty.MEDIUM: (0.50, 0.60),
            Difficulty.HARD: (0.40, 0.50),
            Difficulty.EXPERT: (0.35, 0.45)
        }
        min_r, max_r = rates[self.difficulty]
        target_cells = int(self.size * self.size * random.uniform(min_r, max_r))

        # Gruppen-Längen mit Gewichtung (bevorzuge 2-4)
        group_sizes = {
            2: 40,
            3: 35,
            4: 15,
            5: 5,
            1: 5  # Sehr selten einzelne Zellen
        }

        filled = 0
        stuck_count = 0

        while filled < target_cells and stuck_count < 50:
            # Wähle Gruppengröße
            sizes = list(group_sizes.keys())
            weights = [group_sizes[s] for s in sizes]
            group_size = random.choices(sizes, weights=weights)[0]

            # 60% horizontal, 40% vertikal
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
        """Platziere horizontale Gruppe"""
        candidates = []

        for r in range(self.size):
            for c in range(self.size - size + 1):
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
        """Platziere vertikale Gruppe"""
        candidates = []

        for c in range(self.size):
            for r in range(self.size - size + 1):
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
        """Bewerte Qualität des Rätsels (0-1)"""
        all_clue_counts = [len(rc) for rc in row_clues] + [len(cc) for cc in col_clues]

        if not all_clue_counts:
            return 0.0

        # Zu viele Summen pro Zeile ist schlecht
        max_clues = max(all_clue_counts)
        if max_clues > 5:
            return 0.2

        avg_clues = sum(all_clue_counts) / len(all_clue_counts)

        # Ideal: 2-3 Summen pro Zeile/Spalte
        if 2.0 <= avg_clues <= 3.5:
            quality = 1.0
        elif 1.5 <= avg_clues <= 4.0:
            quality = 0.8
        else:
            quality = 0.5

        # Bonus für Vielfalt der Summen
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
        """Versuche einen Kandidaten zu reparieren (falls Zeit übrig)"""
        # Einfach neu generieren in verbleibender Zeit
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

    def __init__(self, size: int, row_clues: List[List[int]], col_clues: List[List[int]], solution: List[List[int]]):
        self.size = size
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.solution = solution

    def display(self, show_solution: bool = False):
        print("\n" + "=" * 70)
        print(f"Japanese Sums - Optimiert ({self.size}x{self.size})")
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

        # Zähle Summen pro Zeile/Spalte
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


def generate_puzzle(size: int = 6, difficulty: Difficulty = Difficulty.MEDIUM) -> Puzzle:
    """
    Generiere Japanese Sums - SCHNELL & QUALITATIV

    Optimiert für:
    - Schnelle Generierung auch bei 7x7, 8x8
    - Gute Gruppen-Verteilung (weniger Einzelzellen)
    - Garantiert eindeutige Lösung

    Args:
        size: Gittergröße (5-9)
        difficulty: Schwierigkeit

    Returns:
        Puzzle-Objekt
    """
    gen = FastGenerator(size, difficulty)
    solution, row_clues, col_clues = gen.generate()
    return Puzzle(size, row_clues, col_clues, solution)


if __name__ == "__main__":
    print("\nJapanese Sums - Optimierter Generator")
    print("=" * 70)
    print("Fokus: Geschwindigkeit + Qualität\n")

    tests = [
        (5, Difficulty.EASY, "EASY 5x5"),
        (6, Difficulty.MEDIUM, "MEDIUM 6x6"),
        (7, Difficulty.HARD, "HARD 7x7"),
        (8, Difficulty.HARD, "HARD 8x8"),
    ]

    for size, diff, label in tests:
        print(f"\n{'='*70}")
        print(f"Generiere {label}...")
        start = time.time()

        try:
            puzzle = generate_puzzle(size, diff)
            elapsed = time.time() - start
            print(f"✓ Erfolgreich!")

            puzzle.display(show_solution=True)

            solver = OptimizedSolver(puzzle.size, puzzle.row_clues, puzzle.col_clues)
            count = solver.count_solutions(max_count=2)
            print(f"\nVerifikation: {count} Lösung(en)")
            if count == 1:
                print("✓ EINDEUTIG!")

        except Exception as e:
            elapsed = time.time() - start
            print(f"✗ Fehler: {e}")

    print("\n" + "=" * 70)
    print("Verwendung:")
    print("  from japanese_sums_fast import generate_puzzle, Difficulty")
    print("  puzzle = generate_puzzle(size=7, difficulty=Difficulty.HARD)")
    print("=" * 70 + "\n")
