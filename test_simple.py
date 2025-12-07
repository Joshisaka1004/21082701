"""
Simple focused test of ChatGPT's generator
"""

from japanese_sums_guaranteed import generate_puzzle, Difficulty, AdvancedSolver
import time


print("\n" + "="*70)
print("SIMPLE TEST - 7x7 MEDIUM")
print("="*70)

start = time.time()
try:
    puzzle = generate_puzzle(7, 7, Difficulty.MEDIUM)
    elapsed = time.time() - start

    print(f"\n✓ Generated in {elapsed:.1f}s")

    # Verify
    solver = AdvancedSolver(
        puzzle.rows, puzzle.cols,
        puzzle.row_clues, puzzle.col_clues
    )

    verify_start = time.time()
    count = solver.count_solutions(max_count=2)
    verify_time = time.time() - verify_start

    # Check empty lines
    empty_rows = sum(1 for rc in puzzle.row_clues if len(rc) == 0)
    empty_cols = sum(1 for cc in puzzle.col_clues if len(cc) == 0)

    # Metrics
    total_clues = sum(len(rc) for rc in puzzle.row_clues) + \
                 sum(len(cc) for cc in puzzle.col_clues)
    avg_clues = total_clues / (puzzle.rows + puzzle.cols)

    print(f"\nVerification:")
    print(f"  Solutions: {count}")
    print(f"  Verification time: {verify_time:.1f}s")
    print(f"  Empty rows: {empty_rows}, Empty cols: {empty_cols}")
    print(f"  Total clues: {total_clues} (avg {avg_clues:.1f} per line)")

    print(f"\nRow clues: {puzzle.row_clues}")
    print(f"Col clues: {puzzle.col_clues}")

    print(f"\nSolution:")
    for row in puzzle.solution:
        print("  " + " ".join(str(x) if x > 0 else "." for x in row))

    if count == 1 and empty_rows == 0 and empty_cols == 0:
        print(f"\n✓✓✓ SUCCESS - 100% unique, no empty lines!")
    else:
        print(f"\n✗✗✗ PROBLEM!")

except TimeoutError as e:
    elapsed = time.time() - start
    print(f"\n✗ TIMEOUT after {elapsed:.1f}s: {e}")
except Exception as e:
    elapsed = time.time() - start
    import traceback
    print(f"\n✗ ERROR after {elapsed:.1f}s:")
    traceback.print_exc()

print("\n" + "="*70)
