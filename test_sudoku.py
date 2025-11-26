"""
Test-Skript für den Sudoku Generator
Testet alle Kernfunktionen ohne Benutzerinteraktion
"""

import sys
from sudoku_generator import SudokuGenerator

def test_sudoku_generation():
    """Testet die Basis-Generierung"""
    print("=" * 60)
    print("TEST 1: Basis-Generierung")
    print("=" * 60)

    generator = SudokuGenerator()

    # Test 1: Einfache Generierung
    print("\n1. Generiere Sudoku mit 25-30 Hinweisen (nicht symmetrisch)...")
    success = generator.generate_puzzle(min_clues=25, max_clues=30, symmetric=False)

    if success:
        clue_count = generator.get_clue_count()
        print(f"✓ Erfolgreich generiert mit {clue_count} Hinweisen")
        generator.print_grid(generator.grid, "Generiertes Rätsel")

        # Verifiziere, dass die Lösung gültig ist
        if verify_solution(generator.solution):
            print("✓ Lösung ist gültig")
        else:
            print("✗ FEHLER: Lösung ist ungültig!")
            return False
    else:
        print("✗ FEHLER: Generierung fehlgeschlagen")
        return False

    return True


def test_symmetric_generation():
    """Testet symmetrische Generierung"""
    print("\n" + "=" * 60)
    print("TEST 2: Symmetrische Generierung")
    print("=" * 60)

    generator = SudokuGenerator()

    print("\n2. Generiere symmetrisches Sudoku mit 26-30 Hinweisen...")
    success = generator.generate_puzzle(min_clues=26, max_clues=30, symmetric=True)

    if success:
        clue_count = generator.get_clue_count()
        print(f"✓ Erfolgreich generiert mit {clue_count} Hinweisen")
        generator.print_grid(generator.grid, "Symmetrisches Rätsel")

        # Verifiziere Symmetrie
        if verify_symmetry(generator.grid):
            print("✓ Grid ist symmetrisch")
        else:
            print("✗ FEHLER: Grid ist nicht symmetrisch!")
            return False

        # Verifiziere Lösung
        if verify_solution(generator.solution):
            print("✓ Lösung ist gültig")
        else:
            print("✗ FEHLER: Lösung ist ungültig!")
            return False
    else:
        print("✗ FEHLER: Symmetrische Generierung fehlgeschlagen")
        return False

    return True


def test_unique_solution():
    """Testet, ob die Lösung eindeutig ist"""
    print("\n" + "=" * 60)
    print("TEST 3: Eindeutigkeitsprüfung")
    print("=" * 60)

    generator = SudokuGenerator()

    print("\n3. Generiere Sudoku und prüfe Eindeutigkeit...")
    success = generator.generate_puzzle(min_clues=30, max_clues=35, symmetric=False)

    if success:
        clue_count = generator.get_clue_count()
        print(f"✓ Erfolgreich generiert mit {clue_count} Hinweisen")

        # Kopiere das Rätsel und zähle Lösungen
        import copy
        test_grid = copy.deepcopy(generator.grid)
        num_solutions = generator.count_solutions(test_grid)

        if num_solutions == 1:
            print(f"✓ Das Rätsel hat genau 1 eindeutige Lösung")
        else:
            print(f"✗ FEHLER: Das Rätsel hat {num_solutions} Lösungen!")
            return False
    else:
        print("✗ FEHLER: Generierung fehlgeschlagen")
        return False

    return True


def test_clue_count_range():
    """Testet, ob die Clue-Anzahl im gewünschten Bereich liegt"""
    print("\n" + "=" * 60)
    print("TEST 4: Clue-Anzahl Bereich")
    print("=" * 60)

    generator = SudokuGenerator()

    min_clues = 24
    max_clues = 26

    print(f"\n4. Generiere Sudoku mit {min_clues}-{max_clues} Hinweisen...")
    success = generator.generate_puzzle(min_clues=min_clues, max_clues=max_clues, symmetric=False)

    if success:
        clue_count = generator.get_clue_count()
        print(f"✓ Erfolgreich generiert mit {clue_count} Hinweisen")

        if min_clues <= clue_count <= max_clues:
            print(f"✓ Clue-Anzahl liegt im gewünschten Bereich ({min_clues}-{max_clues})")
        else:
            print(f"✗ FEHLER: Clue-Anzahl {clue_count} außerhalb des Bereichs {min_clues}-{max_clues}!")
            return False
    else:
        print("✗ FEHLER: Generierung fehlgeschlagen")
        return False

    return True


def verify_solution(solution):
    """Verifiziert, ob eine Lösung gültig ist"""
    # Prüfe jede Zeile
    for row in solution:
        if sorted(row) != list(range(1, 10)):
            return False

    # Prüfe jede Spalte
    for col in range(9):
        column = [solution[row][col] for row in range(9)]
        if sorted(column) != list(range(1, 10)):
            return False

    # Prüfe jede 3x3 Box
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            box = []
            for i in range(box_row, box_row + 3):
                for j in range(box_col, box_col + 3):
                    box.append(solution[i][j])
            if sorted(box) != list(range(1, 10)):
                return False

    return True


def verify_symmetry(grid):
    """Verifiziert, ob ein Grid point-symmetrisch ist"""
    for i in range(9):
        for j in range(9):
            # Wenn eine Zelle gefüllt ist...
            if grid[i][j] != 0:
                # ...muss die symmetrische Zelle auch gefüllt sein
                sym_i, sym_j = 8 - i, 8 - j
                if grid[sym_i][sym_j] == 0:
                    return False
            # Wenn eine Zelle leer ist...
            else:
                # ...muss die symmetrische Zelle auch leer sein
                sym_i, sym_j = 8 - i, 8 - j
                if grid[sym_i][sym_j] != 0:
                    return False

    return True


def run_all_tests():
    """Führt alle Tests aus"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "SUDOKU GENERATOR TEST SUITE" + " " * 20 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    tests = [
        ("Basis-Generierung", test_sudoku_generation),
        ("Symmetrische Generierung", test_symmetric_generation),
        ("Eindeutigkeitsprüfung", test_unique_solution),
        ("Clue-Anzahl Bereich", test_clue_count_range),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ FEHLER in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Zusammenfassung
    print("\n" + "=" * 60)
    print("TEST ZUSAMMENFASSUNG")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ BESTANDEN" if result else "✗ FEHLGESCHLAGEN"
        print(f"{test_name:.<40} {status}")

    print("=" * 60)
    print(f"Ergebnis: {passed}/{total} Tests bestanden")
    print("=" * 60)

    if passed == total:
        print("\n🎉 Alle Tests erfolgreich bestanden!")
        return True
    else:
        print(f"\n⚠️  {total - passed} Test(s) fehlgeschlagen!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
