"""
Beispiele für den Japanese Sums Generator mit 100% Eindeutigkeitsgarantie
"""

from japanese_sums_universal import generate_puzzle, Difficulty, UniversalSolver
import time


def example_basic():
    """Einfachstes Beispiel - 7x7 (empfohlen)"""
    print("\n" + "=" * 70)
    print("BEISPIEL 1: Einfache Generierung (7x7 - empfohlen)")
    print("=" * 70)

    puzzle = generate_puzzle(7, 7, Difficulty.MEDIUM)
    puzzle.display(show_solution=True)


def example_with_verification():
    """Generierung mit expliziter Verifikation"""
    print("\n" + "=" * 70)
    print("BEISPIEL 2: Mit Verifikation")
    print("=" * 70)

    puzzle = generate_puzzle(7, 7, Difficulty.MEDIUM)

    # Explizite Verifikation
    solver = UniversalSolver(
        puzzle.rows, puzzle.cols,
        puzzle.row_clues, puzzle.col_clues
    )

    count = solver.count_solutions(max_count=2)
    nodes = solver.nodes_explored
    limit = solver.max_nodes
    hit_limit = solver.hit_limit

    print(f"\nVerifikation:")
    print(f"  Lösungen gefunden: {count}")
    print(f"  Knoten durchsucht: {nodes:,}")
    print(f"  Limit erreicht: {hit_limit}")
    print(f"  Prozent des Limits: {nodes/limit*100:.2f}%")

    if count == 1 and not hit_limit:
        print(f"\n✓✓✓ 100% GARANTIERT EINDEUTIG!")

    puzzle.display(show_solution=False)


def example_with_retry():
    """Generierung mit Retry-Logik für größere Gitter"""
    print("\n" + "=" * 70)
    print("BEISPIEL 3: Mit Retry-Logik (9x9)")
    print("=" * 70)

    def generate_with_retry(rows, cols, difficulty, max_retries=3):
        """Generiert mit Retry-Logik"""
        for attempt in range(max_retries):
            try:
                print(f"\nVersuch {attempt + 1}/{max_retries}...")
                return generate_puzzle(rows, cols, difficulty)
            except TimeoutError as e:
                print(f"  Timeout: {e}")
                if attempt < max_retries - 1:
                    print(f"  Versuche erneut...")
                else:
                    print(f"  Fallback auf 7x7...")
                    return generate_puzzle(7, 7, difficulty)

    puzzle = generate_with_retry(9, 9, Difficulty.MEDIUM, max_retries=2)
    puzzle.display(show_solution=True)


def example_all_difficulties():
    """Zeigt alle Schwierigkeitsgrade"""
    print("\n" + "=" * 70)
    print("BEISPIEL 4: Alle Schwierigkeitsgrade (7x7)")
    print("=" * 70)

    difficulties = [
        (Difficulty.EASY, "EASY (70-80% gefüllt)"),
        (Difficulty.MEDIUM, "MEDIUM (62-72% gefüllt)"),
        (Difficulty.HARD, "HARD (52-62% gefüllt)"),
    ]

    for diff, label in difficulties:
        print(f"\n{label}:")
        print("-" * 70)

        start = time.time()
        puzzle = generate_puzzle(7, 7, diff)
        elapsed = time.time() - start

        total_clues = sum(len(rc) for rc in puzzle.row_clues) + \
                     sum(len(cc) for cc in puzzle.col_clues)
        avg_clues = total_clues / (puzzle.rows + puzzle.cols)

        print(f"Generiert in {elapsed:.1f}s")
        print(f"Hinweise: {total_clues} (Ø {avg_clues:.1f} pro Linie)")
        print(f"Zeilen-Hinweise: {puzzle.row_clues[:3]}...")
        print(f"Spalten-Hinweise: {puzzle.col_clues[:3]}...")


def example_rectangular():
    """Rechteckige Gitter"""
    print("\n" + "=" * 70)
    print("BEISPIEL 5: Rechteckige Gitter")
    print("=" * 70)

    configs = [
        (5, 7, Difficulty.EASY, "5x7 EASY"),
        (8, 6, Difficulty.MEDIUM, "8x6 MEDIUM"),
    ]

    for rows, cols, diff, label in configs:
        print(f"\n{label}:")
        print("-" * 70)

        try:
            puzzle = generate_puzzle(rows, cols, diff)
            total_clues = sum(len(rc) for rc in puzzle.row_clues) + \
                         sum(len(cc) for cc in puzzle.col_clues)
            print(f"✓ Erfolgreich! Hinweise: {total_clues}")
            print(f"  Zeilen-Hinweise: {puzzle.row_clues}")
            print(f"  Spalten-Hinweise: {puzzle.col_clues}")
        except TimeoutError:
            print(f"✗ Timeout - versuchen Sie erneut")


def example_production_ready():
    """Production-ready Implementierung"""
    print("\n" + "=" * 70)
    print("BEISPIEL 6: Production-Ready Generator")
    print("=" * 70)

    class ProductionGenerator:
        """Production-ready Generator mit allen Best Practices"""

        def __init__(self):
            self.default_size = 7  # Zuverlässigste Größe
            self.max_retries = 3

        def generate(self, size=None, difficulty=Difficulty.MEDIUM):
            """Generiert ein Rätsel mit allen Sicherheitsvorkehrungen"""
            if size is None:
                size = self.default_size

            # Warne bei problematischen Größen
            if size not in [7, 9]:
                print(f"⚠ Warnung: {size}x{size} ist nicht optimal. 7x7 empfohlen.")

            # Retry-Logik
            for attempt in range(self.max_retries):
                try:
                    print(f"Generiere {size}x{size} {difficulty.value}...")
                    start = time.time()

                    puzzle = generate_puzzle(size, size, difficulty)

                    elapsed = time.time() - start
                    print(f"✓ Erfolgreich in {elapsed:.1f}s - 100% garantiert eindeutig!")

                    return puzzle

                except TimeoutError:
                    if attempt < self.max_retries - 1:
                        print(f"Timeout. Versuch {attempt + 2}/{self.max_retries}...")
                    else:
                        print(f"Fallback auf {self.default_size}x{self.default_size}...")
                        return generate_puzzle(
                            self.default_size,
                            self.default_size,
                            difficulty
                        )

        def generate_batch(self, count=5, size=7, difficulty=Difficulty.MEDIUM):
            """Generiert mehrere Rätsel"""
            puzzles = []
            print(f"\nGeneriere {count} Rätsel ({size}x{size} {difficulty.value})...")

            for i in range(count):
                print(f"\nRätsel {i+1}/{count}:")
                puzzle = self.generate(size, difficulty)
                puzzles.append(puzzle)

            print(f"\n✓ {len(puzzles)} Rätsel erfolgreich generiert!")
            return puzzles

    # Verwendung
    gen = ProductionGenerator()

    # Einzelnes Rätsel
    puzzle = gen.generate(size=7, difficulty=Difficulty.MEDIUM)
    puzzle.display(show_solution=False)

    # Batch-Generierung
    # puzzles = gen.generate_batch(count=3, size=7, difficulty=Difficulty.MEDIUM)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("JAPANESE SUMS - 100% GARANTIERTE EINDEUTIGKEIT")
    print("Beispiele und Best Practices")
    print("=" * 70)

    # Wähle Beispiele zum Ausführen
    examples = [
        ("Einfache Generierung (7x7)", example_basic),
        ("Mit Verifikation", example_with_verification),
        ("Mit Retry-Logik (9x9)", example_with_retry),
        ("Alle Schwierigkeitsgrade", example_all_difficulties),
        ("Rechteckige Gitter", example_rectangular),
        ("Production-Ready", example_production_ready),
    ]

    print("\nVerfügbare Beispiele:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nWähle ein Beispiel (1-6) oder 0 für alle:")
    try:
        choice = input("> ").strip()

        if choice == "0":
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"\n✗ Fehler in {name}: {e}")
        else:
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                examples[idx][1]()
            else:
                print("Ungültige Wahl. Führe Beispiel 1 aus...")
                example_basic()

    except (ValueError, KeyboardInterrupt):
        print("\nFühre Standard-Beispiel aus...")
        example_basic()

    print("\n" + "=" * 70)
    print("Weitere Informationen: siehe README_GUARANTEED.md")
    print("=" * 70 + "\n")
