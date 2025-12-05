"""
Example usage of the Japanese Sums Puzzle Generator
"""

from japanese_sums_generator import generate_puzzle, Difficulty, FastSolver


def example_1_basic():
    """Basic puzzle generation"""
    print("\n" + "="*70)
    print("Example 1: Einfache Rätsel-Generierung")
    print("="*70)

    puzzle = generate_puzzle(size=5, difficulty=Difficulty.EASY)
    puzzle.display(show_solution=True)


def example_2_different_difficulties():
    """Generate puzzles of different difficulties"""
    print("\n" + "="*70)
    print("Example 2: Verschiedene Schwierigkeitsgrade")
    print("="*70)

    for diff in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
        print(f"\n{diff.name}:")
        puzzle = generate_puzzle(size=6, difficulty=diff)
        puzzle.display(show_solution=False)


def example_3_different_sizes():
    """Generate puzzles of different sizes"""
    print("\n" + "="*70)
    print("Example 3: Verschiedene Größen")
    print("="*70)

    for size in [5, 6, 7]:
        print(f"\n{size}x{size}:")
        puzzle = generate_puzzle(size=size, difficulty=Difficulty.MEDIUM)
        puzzle.display(show_solution=True)


def example_4_verify_solution():
    """Verify that a puzzle has a unique solution"""
    print("\n" + "="*70)
    print("Example 4: Lösung verifizieren")
    print("="*70)

    puzzle = generate_puzzle(size=6, difficulty=Difficulty.MEDIUM)
    puzzle.display(show_solution=True)

    # Verify uniqueness
    solver = FastSolver(puzzle.size, puzzle.row_clues, puzzle.col_clues)
    count = solver.count_solutions(max_count=2)

    print(f"\nAnzahl der Lösungen: {count}")
    if count == 1:
        print("✓ Das Rätsel hat eine eindeutige Lösung!")
    elif count == 0:
        print("✗ Keine Lösung gefunden!")
    else:
        print("✗ Mehrere Lösungen gefunden!")


def example_5_solve_manually():
    """Demonstrate how to solve a given puzzle"""
    print("\n" + "="*70)
    print("Example 5: Manuelles Rätsel lösen")
    print("="*70)

    # Define a puzzle manually
    size = 5
    row_clues = [
        [2],      # Row 1
        [5],      # Row 2
        [7, 5],   # Row 3
        [2, 7, 3], # Row 4
        [4]       # Row 5
    ]
    col_clues = [
        [14],     # Col 1
        [2],      # Col 2
        [7],      # Col 3
        [4],      # Col 4
        [8]       # Col 5
    ]

    print("Rätsel-Hinweise:")
    print(f"Zeilen: {row_clues}")
    print(f"Spalten: {col_clues}")

    # Solve it
    solver = FastSolver(size, row_clues, col_clues)
    count = solver.count_solutions(max_count=1)

    if count > 0 and solver.solution:
        print("\nGefundene Lösung:")
        print("  +---------+")
        for r in range(size):
            row_str = "  |"
            for c in range(size):
                val = solver.solution[r][c]
                row_str += str(val) if val != 0 else "."
                if c < size - 1:
                    row_str += " "
            row_str += "|"
            print(row_str)
        print("  +---------+")
    else:
        print("\nKeine Lösung gefunden!")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("Japanese Sums Generator - Beispiele")
    print("="*70)

    # Run individual examples
    example_1_basic()

    # Uncomment to run other examples:
    # example_2_different_difficulties()
    # example_3_different_sizes()
    # example_4_verify_solution()
    # example_5_solve_manually()

    print("\n" + "="*70)
    print("Fertig!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
