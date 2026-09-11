"""
Japanese Sums Universal Generator - Usage Examples

Demonstrates how to generate puzzles for:
- Large square grids (9x9, 10x10)
- Rectangular grids (5x7, 8x6, 7x10, etc.)
"""

from japanese_sums_universal import generate_puzzle, Difficulty
import time


def main():
    print("\n" + "=" * 70)
    print("Japanese Sums Universal Generator - Examples")
    print("=" * 70)

    examples = [
        # Square grids
        (9, 9, Difficulty.MEDIUM, "9x9 MEDIUM (square)"),
        (10, 10, Difficulty.HARD, "10x10 HARD (square)"),

        # Rectangular grids - horizontal
        (5, 7, Difficulty.EASY, "5x7 EASY (horizontal)"),
        (6, 8, Difficulty.MEDIUM, "6x8 MEDIUM (horizontal)"),

        # Rectangular grids - vertical
        (8, 6, Difficulty.MEDIUM, "8x6 MEDIUM (vertical)"),
        (10, 7, Difficulty.HARD, "10x7 HARD (vertical)"),
    ]

    for rows, cols, diff, label in examples:
        print(f"\n{'=' * 70}")
        print(f"Generiere {label}...")

        start = time.time()
        try:
            puzzle = generate_puzzle(rows, cols, diff)
            elapsed = time.time() - start

            print(f"✓ Erfolgreich generiert in {elapsed:.2f}s")
            puzzle.display(show_solution=True)

        except TimeoutError as e:
            elapsed = time.time() - start
            print(f"✗ Timeout: {e}")
        except Exception as e:
            elapsed = time.time() - start
            print(f"✗ Fehler: {e}")

    print("\n" + "=" * 70)
    print("Fertig!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
