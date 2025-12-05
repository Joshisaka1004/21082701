"""
Quick test to verify uniqueness for smaller puzzles
"""

from japanese_sums_generator import generate_puzzle, FastSolver, Difficulty


def quick_test():
    print("\n" + "="*70)
    print("Quick Uniqueness Test - 10 random puzzles")
    print("="*70)

    tests = [
        (5, Difficulty.EASY),
        (5, Difficulty.EASY),
        (5, Difficulty.EASY),
        (5, Difficulty.MEDIUM),
        (5, Difficulty.MEDIUM),
        (6, Difficulty.EASY),
        (6, Difficulty.EASY),
        (6, Difficulty.MEDIUM),
        (7, Difficulty.EASY),
        (7, Difficulty.EASY),
    ]

    failed = 0
    for i, (size, diff) in enumerate(tests):
        print(f"\n{i+1}. {diff.name} {size}x{size}...", end=" ")

        try:
            # Generate
            puzzle = generate_puzzle(size=size, difficulty=diff)

            # Verify by counting ALL possible solutions (not just 2)
            solver = FastSolver(puzzle.size, puzzle.row_clues, puzzle.col_clues)
            solver.max_solutions = 10  # Look for up to 10 solutions
            solver.max_nodes = 5000000  # Increase search limit
            count = solver.count_solutions(max_count=10)

            if count == 1:
                print(f"✓ UNIQUE ({solver.nodes_explored} nodes)")
            else:
                print(f"✗ FAILED - {count} solutions found!")
                failed += 1

                # Show the puzzle
                puzzle.display(show_solution=True)

        except Exception as e:
            print(f"✗ Error: {e}")
            failed += 1

    print("\n" + "="*70)
    if failed == 0:
        print("✓✓✓ ALL 10 PUZZLES HAVE UNIQUE SOLUTIONS! ✓✓✓")
    else:
        print(f"✗✗✗ {failed} puzzles failed! ✗✗✗")
    print("="*70 + "\n")


if __name__ == "__main__":
    quick_test()
