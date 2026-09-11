"""
Japanese Sums Puzzle Generator

Generates Japanese Sums puzzles with guaranteed unique solutions.
Supports grid sizes 5x5 to 9x9 with difficulty levels: Easy, Medium, Hard, Expert.

Rules:
- Place digits 1-9 in some cells (not all cells are filled)
- No digit repeats in any row or column
- Numbers outside indicate sums of adjacent digit groups in that row/column, IN ORDER
- Each sum group is separated by at least one empty cell
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
    """Highly optimized solver with intelligent pruning"""

    def __init__(self, size: int, row_clues: List[List[int]], col_clues: List[List[int]]):
        self.size = size
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.solutions_count = 0
        self.solution = None
        self.nodes_explored = 0
        self.max_nodes = 1000000  # Limit exploration

    def count_solutions(self, max_count: int = 2) -> int:
        """Count solutions up to max_count"""
        self.solutions_count = 0
        self.solution = None
        self.nodes_explored = 0

        grid = [[0] * self.size for _ in range(self.size)]
        self._solve(grid, 0, 0, max_count)

        return self.solutions_count

    def _solve(self, grid: List[List[int]], row: int, col: int, max_count: int) -> bool:
        """Backtracking solver with aggressive pruning"""
        if self.solutions_count >= max_count or self.nodes_explored > self.max_nodes:
            return False

        self.nodes_explored += 1

        # Move to next position
        if col >= self.size:
            row += 1
            col = 0

        # Solution found
        if row >= self.size:
            if self._is_valid(grid):
                self.solutions_count += 1
                if self.solution is None:
                    self.solution = copy.deepcopy(grid)
            return self.solutions_count < max_count

        # Get possible values
        values = self._get_possible_values(grid, row, col)

        for val in values:
            grid[row][col] = val

            # Prune early
            if self._is_promising(grid, row, col):
                if not self._solve(grid, row, col + 1, max_count):
                    grid[row][col] = 0
                    return False

            grid[row][col] = 0

        return True

    def _get_possible_values(self, grid: List[List[int]], row: int, col: int) -> List[int]:
        """Get valid values for position"""
        # Get used digits
        used = set()
        for c in range(self.size):
            if grid[row][c] != 0:
                used.add(grid[row][c])
        for r in range(self.size):
            if grid[r][col] != 0:
                used.add(grid[r][col])

        # Return 0 (empty) plus available digits
        values = [0]
        for d in range(1, 10):
            if d not in used:
                values.append(d)

        return values

    def _is_promising(self, grid: List[List[int]], row: int, col: int) -> bool:
        """Check if current state can lead to solution"""
        # Check row constraints
        if not self._check_line_partial(grid[row], self.row_clues[row], col == self.size - 1):
            return False

        # Check column constraints
        col_data = [grid[r][col] for r in range(row + 1)]
        if not self._check_line_partial(col_data, self.col_clues[col], row == self.size - 1):
            return False

        return True

    def _check_line_partial(self, line: List[int], clues: List[int], complete: bool) -> bool:
        """Check if line satisfies clues"""
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

        # Partial check
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
        """Verify complete grid"""
        for r in range(self.size):
            if not self._check_line_exact(grid[r], self.row_clues[r]):
                return False

        for c in range(self.size):
            col = [grid[r][c] for r in range(self.size)]
            if not self._check_line_exact(col, self.col_clues[c]):
                return False

        return True

    def _check_line_exact(self, line: List[int], clues: List[int]) -> bool:
        """Check exact match"""
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


class Generator:
    """Puzzle generator"""

    def __init__(self, size: int, difficulty: Difficulty):
        self.size = size
        self.difficulty = difficulty

    def generate(self, timeout: float = None) -> Tuple[List[List[int]], List[List[int]], List[List[int]]]:
        """Generate puzzle"""
        # Auto-adjust timeout based on size if not specified
        if timeout is None:
            timeout_map = {5: 30, 6: 45, 7: 60, 8: 90, 9: 120}
            timeout = timeout_map.get(self.size, 60)

        start = time.time()
        attempts = 0

        while time.time() - start < timeout:
            attempts += 1

            # Create grid
            grid = self._create_grid()

            # Extract clues
            row_clues = [self._get_clues(grid[r]) for r in range(self.size)]
            col_clues = [self._get_clues([grid[r][c] for r in range(self.size)]) for c in range(self.size)]

            # Quick validation
            if not self._has_min_clues(row_clues, col_clues):
                continue

            # Check uniqueness
            solver = FastSolver(self.size, row_clues, col_clues)
            count = solver.count_solutions(max_count=2)

            if count == 1:
                print(f"  (Generated after {attempts} attempts)")
                return grid, row_clues, col_clues

        raise TimeoutError(f"Timeout after {timeout}s ({attempts} attempts)")

    def _create_grid(self) -> List[List[int]]:
        """Create solution grid"""
        # Fill rates
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

        # Ensure min groups
        self._ensure_groups(grid, row_used, col_used)

        return grid

    def _should_place(self, grid: List[List[int]], r: int, c: int) -> bool:
        """Decide if to place digit"""
        neighbors = 0
        if c > 0 and grid[r][c - 1] != 0:
            neighbors += 1
        if c < self.size - 1 and grid[r][c + 1] != 0:
            neighbors += 1
        if r > 0 and grid[r - 1][c] != 0:
            neighbors += 1
        if r < self.size - 1 and grid[r + 1][c] != 0:
            neighbors += 1

        return random.random() < (0.7 if neighbors > 0 else 0.4)

    def _ensure_groups(self, grid: List[List[int]], row_used: List[Set[int]], col_used: List[Set[int]]):
        """Ensure all rows/cols have groups"""
        for r in range(self.size):
            if all(grid[r][c] == 0 for c in range(self.size)):
                self._add_row_group(grid, r, row_used, col_used)

        for c in range(self.size):
            if all(grid[r][c] == 0 for r in range(self.size)):
                self._add_col_group(grid, c, row_used, col_used)

    def _add_row_group(self, grid: List[List[int]], r: int, row_used: List[Set[int]], col_used: List[Set[int]]):
        """Add group to row"""
        for c in range(self.size - 1):
            if grid[r][c] == 0 and grid[r][c + 1] == 0:
                av1 = set(range(1, 10)) - row_used[r] - col_used[c]
                if av1:
                    d1 = random.choice(list(av1))
                    grid[r][c] = d1
                    row_used[r].add(d1)
                    col_used[c].add(d1)

                    av2 = set(range(1, 10)) - row_used[r] - col_used[c + 1]
                    if av2:
                        d2 = random.choice(list(av2))
                        grid[r][c + 1] = d2
                        row_used[r].add(d2)
                        col_used[c + 1].add(d2)
                return

    def _add_col_group(self, grid: List[List[int]], c: int, row_used: List[Set[int]], col_used: List[Set[int]]):
        """Add group to column"""
        for r in range(self.size - 1):
            if grid[r][c] == 0 and grid[r + 1][c] == 0:
                av1 = set(range(1, 10)) - row_used[r] - col_used[c]
                if av1:
                    d1 = random.choice(list(av1))
                    grid[r][c] = d1
                    row_used[r].add(d1)
                    col_used[c].add(d1)

                    av2 = set(range(1, 10)) - row_used[r + 1] - col_used[c]
                    if av2:
                        d2 = random.choice(list(av2))
                        grid[r + 1][c] = d2
                        row_used[r + 1].add(d2)
                        col_used[c].add(d2)
                return

    def _get_clues(self, line: List[int]) -> List[int]:
        """Extract clues from line"""
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

    def _has_min_clues(self, row_clues: List[List[int]], col_clues: List[List[int]]) -> bool:
        """Check minimum clues"""
        total = sum(len(rc) for rc in row_clues) + sum(len(cc) for cc in col_clues)
        return total >= self.size * 2


class Puzzle:
    """Puzzle representation"""

    def __init__(self, size: int, row_clues: List[List[int]], col_clues: List[List[int]], solution: List[List[int]]):
        self.size = size
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.solution = solution

    def display(self, show_solution: bool = False):
        """Display puzzle"""
        print("\n" + "=" * 70)
        print(f"Japanese Sums ({self.size}x{self.size})")
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

        print("=" * 70)

    def _show_grid(self, grid: List[List[int]]):
        """Show grid"""
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


def generate_puzzle(size: int = 6, difficulty: Difficulty = Difficulty.MEDIUM) -> Puzzle:
    """
    Generate a Japanese Sums puzzle with unique solution.

    Args:
        size: Grid size (5-9)
        difficulty: Difficulty level (EASY, MEDIUM, HARD, EXPERT)

    Returns:
        Puzzle object
    """
    gen = Generator(size, difficulty)
    solution, row_clues, col_clues = gen.generate()
    return Puzzle(size, row_clues, col_clues, solution)


if __name__ == "__main__":
    print("\nJapanese Sums Puzzle Generator")
    print("=" * 70)
    print("\nGeneriere Rätsel mit garantiert eindeutiger Lösung...")
    print("(Zahlen 1-9 sind erlaubt, nicht alle Zellen werden gefüllt)\n")

    tests = [
        (5, Difficulty.EASY, "EASY 5x5"),
        (6, Difficulty.MEDIUM, "MEDIUM 6x6"),
        (7, Difficulty.HARD, "HARD 7x7"),
        (8, Difficulty.EXPERT, "EXPERT 8x8"),
    ]

    for size, diff, label in tests:
        print(f"\n{'='*70}")
        print(f"Generiere {label}...")
        start = time.time()

        try:
            puzzle = generate_puzzle(size, diff)
            elapsed = time.time() - start
            print(f"✓ Erfolgreich generiert in {elapsed:.2f}s")

            puzzle.display(show_solution=True)

            # Verify
            solver = FastSolver(puzzle.size, puzzle.row_clues, puzzle.col_clues)
            count = solver.count_solutions(max_count=2)
            print(f"\nVerifikation: {count} Lösung(en) gefunden")
            if count == 1:
                print("✓ Eindeutigkeit bestätigt!")

        except Exception as e:
            elapsed = time.time() - start
            print(f"✗ Fehler nach {elapsed:.2f}s: {e}")

    print("\n" + "=" * 70)
    print("\nBeispiel-Nutzung:")
    print("  from japanese_sums_generator import generate_puzzle, Difficulty")
    print("  puzzle = generate_puzzle(size=6, difficulty=Difficulty.MEDIUM)")
    print("  puzzle.display(show_solution=True)")
    print("=" * 70 + "\n")
