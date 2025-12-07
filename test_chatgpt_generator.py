"""
Comprehensive test suite for ChatGPT's Japanese Sums Generator
"""

from japanese_sums_guaranteed import generate_puzzle, Difficulty, AdvancedSolver
import time


def test_single_size(rows, cols, difficulty):
    """Test a single configuration"""
    print(f"\n{'='*70}")
    print(f"Testing {rows}x{cols} {difficulty.name}")
    print(f"{'='*70}")

    start = time.time()
    try:
        puzzle = generate_puzzle(rows, cols, difficulty)
        elapsed = time.time() - start

        # Verify uniqueness
        solver = AdvancedSolver(
            puzzle.rows, puzzle.cols,
            puzzle.row_clues, puzzle.col_clues
        )
        count = solver.count_solutions(max_count=2)

        # Check for empty rows/columns
        empty_rows = sum(1 for rc in puzzle.row_clues if len(rc) == 0)
        empty_cols = sum(1 for cc in puzzle.col_clues if len(cc) == 0)

        # Calculate metrics
        total_clues = sum(len(rc) for rc in puzzle.row_clues) + \
                     sum(len(cc) for cc in puzzle.col_clues)
        avg_clues = total_clues / (puzzle.rows + puzzle.cols)

        print(f"✓ SUCCESS in {elapsed:.1f}s")
        print(f"  Solutions: {count}")
        print(f"  Total clues: {total_clues} (avg {avg_clues:.1f} per line)")
        print(f"  Empty rows: {empty_rows}, Empty cols: {empty_cols}")
        print(f"  Row clues: {puzzle.row_clues[:3]}...")
        print(f"  Col clues: {puzzle.col_clues[:3]}...")

        if count == 1 and empty_rows == 0 and empty_cols == 0:
            print(f"  ✓✓✓ PERFECT - 100% guaranteed unique, no empty lines!")
            return True
        else:
            print(f"  ✗✗✗ PROBLEM - count={count}, empty_rows={empty_rows}, empty_cols={empty_cols}")
            return False

    except TimeoutError as e:
        elapsed = time.time() - start
        print(f"✗ TIMEOUT after {elapsed:.1f}s: {e}")
        return False
    except Exception as e:
        elapsed = time.time() - start
        print(f"✗ ERROR after {elapsed:.1f}s: {e}")
        return False


def test_comprehensive():
    """Run comprehensive tests"""
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST SUITE - ChatGPT's Generator")
    print("="*70)

    results = []

    # Test configurations
    configs = [
        # Square grids
        (5, 5, Difficulty.EASY, "5x5 EASY"),
        (5, 5, Difficulty.MEDIUM, "5x5 MEDIUM"),
        (6, 6, Difficulty.MEDIUM, "6x6 MEDIUM"),
        (7, 7, Difficulty.MEDIUM, "7x7 MEDIUM"),
        (8, 8, Difficulty.MEDIUM, "8x8 MEDIUM"),
        (9, 9, Difficulty.MEDIUM, "9x9 MEDIUM"),
        (10, 10, Difficulty.MEDIUM, "10x10 MEDIUM"),

        # Rectangular grids
        (5, 7, Difficulty.MEDIUM, "5x7 MEDIUM"),
        (6, 8, Difficulty.MEDIUM, "6x8 MEDIUM"),
        (7, 5, Difficulty.MEDIUM, "7x5 MEDIUM"),

        # Different difficulties on 7x7
        (7, 7, Difficulty.EASY, "7x7 EASY"),
        (7, 7, Difficulty.HARD, "7x7 HARD"),
        (7, 7, Difficulty.EXPERT, "7x7 EXPERT"),
    ]

    for rows, cols, diff, label in configs:
        success = test_single_size(rows, cols, diff)
        results.append((label, success))

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    successes = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nTotal: {successes}/{total} ({successes/total*100:.1f}% success rate)\n")

    for label, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {label}")

    print("\n" + "="*70)


def test_batch_reliability():
    """Test reliability by generating multiple puzzles of same size"""
    print("\n" + "="*70)
    print("RELIABILITY TEST - Generate 5x 7x7 MEDIUM")
    print("="*70)

    successes = 0
    total = 5
    times = []

    for i in range(total):
        print(f"\nAttempt {i+1}/{total}:")
        start = time.time()
        try:
            puzzle = generate_puzzle(7, 7, Difficulty.MEDIUM)
            elapsed = time.time() - start
            times.append(elapsed)

            solver = AdvancedSolver(
                puzzle.rows, puzzle.cols,
                puzzle.row_clues, puzzle.col_clues
            )
            count = solver.count_solutions(max_count=2)

            if count == 1:
                print(f"  ✓ Success in {elapsed:.1f}s")
                successes += 1
            else:
                print(f"  ✗ Failed - {count} solutions")
        except Exception as e:
            elapsed = time.time() - start
            print(f"  ✗ Error after {elapsed:.1f}s: {e}")

    print(f"\nReliability: {successes}/{total} ({successes/total*100:.0f}%)")
    if times:
        print(f"Average time: {sum(times)/len(times):.1f}s")
        print(f"Min/Max time: {min(times):.1f}s / {max(times):.1f}s")


if __name__ == "__main__":
    # Run comprehensive test
    test_comprehensive()

    # Run reliability test
    test_batch_reliability()

    print("\n" + "="*70)
    print("Testing complete!")
    print("="*70 + "\n")
