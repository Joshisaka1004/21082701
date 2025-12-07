"""
Direct benchmark comparison: ChatGPT vs Ultimate Generator
"""

import time
from chatgpt_correct import generate_unique_puzzle as generate_chatgpt
from japanese_sums_ultimate import generate_unique_puzzle as generate_ultimate, solve_japanese_sums


def benchmark_generator(name, gen_func, rows, cols, iterations=3):
    """Benchmark a generator function."""
    times = []
    success_count = 0

    for i in range(iterations):
        start = time.time()
        try:
            row_clues, col_clues, solution = gen_func(rows, cols, max_attempts=800)
            elapsed = time.time() - start

            # Verify uniqueness
            count, _ = solve_japanese_sums(rows, cols, row_clues, col_clues, max_solutions=2)

            if count == 1:
                times.append(elapsed)
                success_count += 1
            else:
                print(f"  {name} attempt {i+1}: FAILED (not unique)")

        except Exception as e:
            elapsed = time.time() - start
            print(f"  {name} attempt {i+1}: ERROR after {elapsed:.2f}s: {e}")

    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        return success_count, avg_time, min_time, max_time
    else:
        return 0, 0.0, 0.0, 0.0


def main():
    print("\n" + "="*70)
    print("BENCHMARK: ChatGPT vs Ultimate Generator")
    print("="*70)

    test_sizes = [
        (5, 5, "5x5"),
        (6, 6, "6x6"),
        (7, 7, "7x7"),
        (8, 8, "8x8"),
        (9, 9, "9x9"),
    ]

    results = []

    for rows, cols, label in test_sizes:
        print(f"\n{label}:")
        print("-" * 70)

        # Test ChatGPT
        print("ChatGPT:")
        chatgpt_success, chatgpt_avg, chatgpt_min, chatgpt_max = benchmark_generator(
            "ChatGPT", generate_chatgpt, rows, cols, iterations=3
        )

        # Test Ultimate
        print("Ultimate:")
        ultimate_success, ultimate_avg, ultimate_min, ultimate_max = benchmark_generator(
            "Ultimate", generate_ultimate, rows, cols, iterations=3
        )

        results.append({
            'label': label,
            'chatgpt': (chatgpt_success, chatgpt_avg, chatgpt_min, chatgpt_max),
            'ultimate': (ultimate_success, ultimate_avg, ultimate_min, ultimate_max)
        })

        # Print comparison
        if chatgpt_success > 0 and ultimate_success > 0:
            speedup = chatgpt_avg / ultimate_avg if ultimate_avg > 0 else 0
            if speedup > 1:
                print(f"→ Ultimate is {speedup:.2f}x FASTER")
            elif speedup < 1:
                print(f"→ ChatGPT is {1/speedup:.2f}x FASTER")
            else:
                print(f"→ TIED")

    # Summary table
    print("\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    print(f"{'Size':<8} {'ChatGPT Avg':<15} {'Ultimate Avg':<15} {'Winner':<15}")
    print("-" * 70)

    for res in results:
        label = res['label']
        chatgpt_success, chatgpt_avg, _, _ = res['chatgpt']
        ultimate_success, ultimate_avg, _, _ = res['ultimate']

        chatgpt_str = f"{chatgpt_avg:.3f}s" if chatgpt_success > 0 else "FAILED"
        ultimate_str = f"{ultimate_avg:.3f}s" if ultimate_success > 0 else "FAILED"

        if chatgpt_success > 0 and ultimate_success > 0:
            if ultimate_avg < chatgpt_avg:
                winner = f"Ultimate ({chatgpt_avg/ultimate_avg:.1f}x)"
            elif chatgpt_avg < ultimate_avg:
                winner = f"ChatGPT ({ultimate_avg/chatgpt_avg:.1f}x)"
            else:
                winner = "Tied"
        elif chatgpt_success > 0:
            winner = "ChatGPT"
        elif ultimate_success > 0:
            winner = "Ultimate"
        else:
            winner = "Both failed"

        print(f"{label:<8} {chatgpt_str:<15} {ultimate_str:<15} {winner:<15}")

    print("="*70 + "\n")


if __name__ == "__main__":
    main()
