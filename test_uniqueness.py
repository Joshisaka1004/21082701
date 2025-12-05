"""
Test script to verify uniqueness of solutions
"""

from japanese_sums_generator import generate_puzzle, FastSolver, Difficulty
import time


def test_uniqueness(size, difficulty, num_tests=5):
    """Generate multiple puzzles and verify they all have unique solutions"""
    print(f"\n{'='*70}")
    print(f"Testing {difficulty.name} {size}x{size} puzzles")
    print(f"{'='*70}")

    for i in range(num_tests):
        print(f"\nTest {i+1}/{num_tests}:")

        try:
            # Generate puzzle
            start = time.time()
            puzzle = generate_puzzle(size=size, difficulty=difficulty)
            gen_time = time.time() - start

            print(f"  Generated in {gen_time:.2f}s")

            # Verify with solver
            start = time.time()
            solver = FastSolver(puzzle.size, puzzle.row_clues, puzzle.col_clues)

            # Count up to 3 solutions to be really sure
            count = solver.count_solutions(max_count=3)
            verify_time = time.time() - start

            print(f"  Verified in {verify_time:.2f}s")
            print(f"  Solutions found: {count}")

            if count == 1:
                print(f"  ✓ UNIQUE solution verified!")

                # Double-check: the found solution should match the original
                if solver.solution:
                    matches = True
                    for r in range(size):
                        for c in range(size):
                            if solver.solution[r][c] != puzzle.solution[r][c]:
                                matches = False
                                break

                    if matches:
                        print(f"  ✓ Solution matches original!")
                    else:
                        print(f"  ✗ WARNING: Solution doesn't match original!")
                        return False

            elif count == 0:
                print(f"  ✗ ERROR: No solution found!")
                return False
            else:
                print(f"  ✗ ERROR: Multiple solutions found ({count})!")
                print(f"\n  Puzzle clues:")
                print(f"  Row clues: {puzzle.row_clues}")
                print(f"  Col clues: {puzzle.col_clues}")
                puzzle.display(show_solution=True)
                return False

        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False

    print(f"\n{'='*70}")
    print(f"✓ All {num_tests} tests PASSED!")
    print(f"{'='*70}")
    return True


def main():
    print("\n" + "="*70)
    print("Japanese Sums - Uniqueness Verification Tests")
    print("="*70)
    print("\nTesting that all generated puzzles have exactly one solution...")

    # Test different sizes and difficulties
    test_cases = [
        (5, Difficulty.EASY, 3),
        (6, Difficulty.MEDIUM, 3),
        (7, Difficulty.HARD, 2),
    ]

    all_passed = True

    for size, diff, num_tests in test_cases:
        if not test_uniqueness(size, diff, num_tests):
            all_passed = False
            print(f"\n✗ FAILED for {diff.name} {size}x{size}")
            break

    print("\n" + "="*70)
    if all_passed:
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("All generated puzzles have exactly ONE unique solution!")
    else:
        print("✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("There may be an issue with uniqueness verification!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
