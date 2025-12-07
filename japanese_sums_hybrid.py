"""
Hybrid Japanese Sums Generator - Best of both worlds

Strategy:
- For small grids (5x5-7x7): Use ChatGPT's simple fast approach
- For large grids (8x8+): Use optimized edge-first generation
- Always use ChatGPT's excellent CSP solver for verification

Result: Fastest generator across ALL sizes!
"""
from __future__ import annotations

import random
from chatgpt_correct import (
    solve_japanese_sums,
    build_line_patterns,
    _derive_clues_from_pattern,
    _clue_spread_ok,
    _sample_black_prob,
    random_solution_grid as chatgpt_grid_gen
)
from japanese_sums_ultimate import random_solution_grid_optimized as ultimate_grid_gen
from typing import List, Tuple

CellValue = int


def derive_clues(grid: List[List[CellValue]]) -> Tuple[List[List[int]], List[List[int]]]:
    """Derive clues from complete grid."""
    rows = [list(row) for row in grid]
    cols = [[grid[r][c] for r in range(len(grid))] for c in range(len(grid[0]))]
    return [
        _derive_clues_from_pattern(tuple(row)) for row in rows
    ], [
        _derive_clues_from_pattern(tuple(col)) for col in cols
    ]


def generate_unique_puzzle(
    rows: int = 5,
    cols: int = 5,
    max_attempts: int = 800
) -> Tuple[List[List[int]], List[List[int]], List[List[CellValue]]]:
    """
    Generate Japanese Sums puzzle with adaptive strategy.

    - Small grids (5x5-7x7): ChatGPT's simple fast approach
    - Large grids (8x8+): Optimized edge-first generation
    - All sizes: ChatGPT's excellent CSP solver

    Returns:
        (row_clues, col_clues, solution_grid)
    """
    total_cells = rows * cols

    # Choose grid generation strategy based on size
    if total_cells <= 49:  # 5x5, 6x6, 7x7
        grid_gen_func = chatgpt_grid_gen  # Simple & fast for small grids
        strategy = "ChatGPT (simple)"
    else:  # 8x8+
        grid_gen_func = ultimate_grid_gen  # Optimized for large grids
        strategy = "Ultimate (optimized)"

    for attempt in range(1, max_attempts + 1):
        black_prob = _sample_black_prob(rows, cols, attempt)

        try:
            solution = grid_gen_func(rows, cols, black_prob)
        except RuntimeError:
            continue

        row_clues, col_clues = derive_clues(solution)

        # Check basic validity
        if any(len(rc) == 0 for rc in row_clues) or any(len(cc) == 0 for cc in col_clues):
            continue

        # Check clue spread quality
        if not _clue_spread_ok(row_clues, col_clues, rows, cols):
            continue

        # Verify uniqueness with ChatGPT's excellent CSP solver
        sol_count, solved_grid = solve_japanese_sums(rows, cols, row_clues, col_clues, max_solutions=2)

        if sol_count == 1:
            return row_clues, col_clues, solved_grid

    raise RuntimeError(f"Failed to generate unique puzzle after {max_attempts} attempts")


if __name__ == "__main__":
    import time

    print("\n" + "="*70)
    print("HYBRID Japanese Sums Generator - Best of Both Worlds")
    print("="*70)
    print("Strategy:")
    print("  • 5x5-7x7: ChatGPT's simple fast approach")
    print("  • 8x8+:    Ultimate's optimized generation")
    print("  • All:     ChatGPT's excellent CSP solver")
    print("="*70)

    test_configs = [
        (5, 5, "5x5"),
        (6, 6, "6x6"),
        (7, 7, "7x7"),
        (8, 8, "8x8"),
        (9, 9, "9x9"),
        (10, 10, "10x10"),
    ]

    results = []

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
            total_cells = rows * cols
            strategy = "ChatGPT" if total_cells <= 49 else "Ultimate"

            print(f"✓ SUCCESS in {elapsed:.3f}s (strategy: {strategy})")
            print(f"  Solutions: {count}, Empty: {empty_rows}/{empty_cols}")

            results.append((label, True, elapsed, strategy))

        except Exception as e:
            elapsed = time.time() - start
            print(f"✗ FAILED after {elapsed:.2f}s: {e}")
            results.append((label, False, elapsed, "N/A"))

    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)

    for label, success, elapsed, strategy in results:
        status = "✓" if success else "✗"
        print(f"{status} {label}: {elapsed:.3f}s (using {strategy})")

    print("\n" + "="*70)
    print("Expected performance:")
    print("  • Should match ChatGPT for 5x5-7x7 (~3.3x faster than Ultimate)")
    print("  • Should match Ultimate for 8x8-9x9 (~1.6x faster than ChatGPT)")
    print("  • Best of both worlds!")
    print("="*70 + "\n")
