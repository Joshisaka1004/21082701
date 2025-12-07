"""
Test the solver speed directly
"""

from japanese_sums_guaranteed import AdvancedSolver
import time


# Simple 5x5 test case
print("\n" + "="*70)
print("TEST 1: Simple 5x5 with 1 solution")
print("="*70)

row_clues = [[8], [3, 5], [12], [7], [9]]
col_clues = [[11], [7], [6], [8], [12]]

start = time.time()
solver = AdvancedSolver(5, 5, row_clues, col_clues)
count = solver.count_solutions(max_count=2)
elapsed = time.time() - start

print(f"Solutions: {count}")
print(f"Time: {elapsed:.3f}s")

if solver.solution:
    print("Solution found:")
    for row in solver.solution:
        print("  " + " ".join(str(x) if x > 0 else "." for x in row))


# Test with a more complex case
print("\n" + "="*70)
print("TEST 2: More complex 6x6")
print("="*70)

row_clues = [[9, 6], [12], [8, 4], [15], [7], [10, 5]]
col_clues = [[14], [11, 3], [9], [13], [6, 8], [12]]

start = time.time()
solver = AdvancedSolver(6, 6, row_clues, col_clues)

# Use timeout approach
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Solver took too long")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout

try:
    count = solver.count_solutions(max_count=2)
    elapsed = time.time() - start
    signal.alarm(0)  # Cancel alarm

    print(f"Solutions: {count}")
    print(f"Time: {elapsed:.3f}s")

    if solver.solution:
        print("Solution found:")
        for row in solver.solution:
            print("  " + " ".join(str(x) if x > 0 else "." for x in row))

except TimeoutError:
    elapsed = time.time() - start
    signal.alarm(0)
    print(f"✗ TIMEOUT after {elapsed:.1f}s!")
    print("The solver is too slow for this configuration!")


# Test with a sparse puzzle (should be fast)
print("\n" + "="*70)
print("TEST 3: Sparse 7x7 (high fill rate)")
print("="*70)

# Create a simple sparse puzzle manually
row_clues = [[15], [8, 7], [12], [6, 9], [10], [14], [11, 4]]
col_clues = [[13], [9, 5], [11], [7, 8], [12], [10], [13, 6]]

start = time.time()
solver = AdvancedSolver(7, 7, row_clues, col_clues)

signal.alarm(30)
try:
    count = solver.count_solutions(max_count=2)
    elapsed = time.time() - start
    signal.alarm(0)

    print(f"Solutions: {count}")
    print(f"Time: {elapsed:.3f}s")

except TimeoutError:
    elapsed = time.time() - start
    signal.alarm(0)
    print(f"✗ TIMEOUT after {elapsed:.1f}s!")


print("\n" + "="*70)
print("CONCLUSION:")
print("="*70)
print("If any test times out, ChatGPT's 'no limit' solver is NOT viable")
print("because it's too slow for practical use!")
print("="*70 + "\n")
