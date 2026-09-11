"""
Direct side-by-side comparison: ChatGPT vs Claude
"""

import time
import signal


def timeout_handler(signum, frame):
    raise TimeoutError("Timeout!")


print("\n" + "="*70)
print("DIRECT COMPARISON: ChatGPT vs Claude")
print("="*70)

# Test configuration
TEST_SIZE = 7
TEST_DIFFICULTY = "MEDIUM"

print(f"\nTest: {TEST_SIZE}x{TEST_SIZE} {TEST_DIFFICULTY}")
print("="*70)


# ============================================================================
# TEST 1: Claude's Generator (japanese_sums_pro.py)
# ============================================================================

print("\n[1] Claude's Generator (japanese_sums_pro.py)")
print("-" * 70)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout

try:
    from japanese_sums_pro import generate_puzzle as generate_claude
    from japanese_sums_pro import Difficulty as DiffClaude, ProSolver as SolverClaude

    diff_claude = DiffClaude.MEDIUM

    start = time.time()
    puzzle_claude = generate_claude(TEST_SIZE, TEST_SIZE, diff_claude)
    gen_time = time.time() - start

    signal.alarm(0)  # Cancel timeout

    # Verify
    solver = SolverClaude(
        puzzle_claude.rows, puzzle_claude.cols,
        puzzle_claude.row_clues, puzzle_claude.col_clues
    )
    count = solver.count_solutions(max_count=2)

    # Check empty lines
    empty_rows = sum(1 for rc in puzzle_claude.row_clues if len(rc) == 0)
    empty_cols = sum(1 for cc in puzzle_claude.col_clues if len(cc) == 0)

    total_clues = sum(len(rc) for rc in puzzle_claude.row_clues) + \
                 sum(len(cc) for cc in puzzle_claude.col_clues)

    print(f"✓ SUCCESS!")
    print(f"  Generation time: {gen_time:.2f}s")
    print(f"  Solutions: {count}")
    print(f"  Nodes explored: {solver.nodes_explored:,}")
    print(f"  Hit limit: {solver.hit_limit}")
    print(f"  Empty rows: {empty_rows}, Empty cols: {empty_cols}")
    print(f"  Total clues: {total_clues}")
    print(f"  Row clues: {puzzle_claude.row_clues[:2]}...")
    print(f"  Col clues: {puzzle_claude.col_clues[:2]}...")

    claude_success = True
    claude_time = gen_time

except TimeoutError:
    signal.alarm(0)
    print(f"✗ TIMEOUT after 30s")
    claude_success = False
    claude_time = 30.0

except Exception as e:
    signal.alarm(0)
    print(f"✗ ERROR: {e}")
    claude_success = False
    claude_time = 30.0


# ============================================================================
# TEST 2: ChatGPT's Generator (japanese_sums_guaranteed.py)
# ============================================================================

print("\n[2] ChatGPT's Generator (japanese_sums_guaranteed.py)")
print("-" * 70)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout

try:
    from japanese_sums_guaranteed import generate_puzzle as generate_chatgpt
    from japanese_sums_guaranteed import Difficulty as DiffChatGPT, AdvancedSolver

    diff_chatgpt = DiffChatGPT.MEDIUM

    start = time.time()
    puzzle_chatgpt = generate_chatgpt(TEST_SIZE, TEST_SIZE, diff_chatgpt)
    gen_time = time.time() - start

    signal.alarm(0)  # Cancel timeout

    # Verify
    solver = AdvancedSolver(
        puzzle_chatgpt.rows, puzzle_chatgpt.cols,
        puzzle_chatgpt.row_clues, puzzle_chatgpt.col_clues
    )
    count = solver.count_solutions(max_count=2)

    # Check empty lines
    empty_rows = sum(1 for rc in puzzle_chatgpt.row_clues if len(rc) == 0)
    empty_cols = sum(1 for cc in puzzle_chatgpt.col_clues if len(cc) == 0)

    total_clues = sum(len(rc) for rc in puzzle_chatgpt.row_clues) + \
                 sum(len(cc) for cc in puzzle_chatgpt.col_clues)

    print(f"✓ SUCCESS!")
    print(f"  Generation time: {gen_time:.2f}s")
    print(f"  Solutions: {count}")
    print(f"  Empty rows: {empty_rows}, Empty cols: {empty_cols}")
    print(f"  Total clues: {total_clues}")
    print(f"  Row clues: {puzzle_chatgpt.row_clues[:2]}...")
    print(f"  Col clues: {puzzle_chatgpt.col_clues[:2]}...")

    chatgpt_success = True
    chatgpt_time = gen_time

except TimeoutError:
    signal.alarm(0)
    print(f"✗ TIMEOUT after 30s")
    print(f"  The generator got stuck during verification!")
    chatgpt_success = False
    chatgpt_time = 30.0

except Exception as e:
    signal.alarm(0)
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    chatgpt_success = False
    chatgpt_time = 30.0


# ============================================================================
# COMPARISON SUMMARY
# ============================================================================

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"\nClaude's Generator:")
if claude_success:
    print(f"  ✓ SUCCESS in {claude_time:.2f}s")
else:
    print(f"  ✗ FAILED (timeout or error)")

print(f"\nChatGPT's Generator:")
if chatgpt_success:
    print(f"  ✓ SUCCESS in {chatgpt_time:.2f}s")
else:
    print(f"  ✗ FAILED (timeout or error)")

print(f"\n" + "="*70)

if claude_success and not chatgpt_success:
    print("VERDICT: Claude's generator is SUPERIOR")
    print("ChatGPT's 'toller Code' DOES NOT WORK!")
elif chatgpt_success and not claude_success:
    print("VERDICT: ChatGPT's generator is superior")
elif claude_success and chatgpt_success:
    if claude_time < chatgpt_time:
        speedup = chatgpt_time / claude_time
        print(f"VERDICT: Claude's generator is FASTER ({speedup:.1f}x speedup)")
    else:
        speedup = claude_time / chatgpt_time
        print(f"VERDICT: ChatGPT's generator is faster ({speedup:.1f}x speedup)")
else:
    print("VERDICT: Both generators failed!")

print("="*70 + "\n")
