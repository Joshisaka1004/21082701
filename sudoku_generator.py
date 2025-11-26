"""
Sudoku Generator für Pythonista (iPad)
Erzeugt Sudoku-Rätsel mit einzigartiger Lösung und optionaler Symmetrie
"""

import random
import copy
from typing import List, Tuple, Optional

class SudokuGenerator:
    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]

    def is_valid(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        """Prüft, ob eine Zahl an einer Position gültig ist"""
        # Prüfe Zeile
        if num in grid[row]:
            return False

        # Prüfe Spalte
        if num in [grid[i][col] for i in range(9)]:
            return False

        # Prüfe 3x3 Box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if grid[i][j] == num:
                    return False

        return True

    def solve(self, grid: List[List[int]]) -> bool:
        """Löst ein Sudoku mit Backtracking"""
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_valid(grid, row, col, num):
                            grid[row][col] = num
                            if self.solve(grid):
                                return True
                            grid[row][col] = 0
                    return False
        return True

    def count_solutions(self, grid: List[List[int]], count: int = 0) -> int:
        """Zählt die Anzahl möglicher Lösungen (stoppt bei 2)"""
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_valid(grid, row, col, num):
                            grid[row][col] = num
                            count = self.count_solutions(grid, count)
                            if count > 1:
                                grid[row][col] = 0
                                return count
                            grid[row][col] = 0
                    return count
        return count + 1

    def generate_complete_grid(self) -> None:
        """Erzeugt ein vollständig gefülltes, gültiges Sudoku"""
        # Fülle diagonal 3x3 Boxen (diese beeinflussen sich nicht gegenseitig)
        for box in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            idx = 0
            for i in range(box, box + 3):
                for j in range(box, box + 3):
                    self.grid[i][j] = nums[idx]
                    idx += 1

        # Löse den Rest
        self.solve(self.grid)
        self.solution = copy.deepcopy(self.grid)

    def get_symmetric_cells(self) -> List[Tuple[int, int]]:
        """Gibt alle Zellenpositionen in symmetrischer Reihenfolge zurück"""
        cells = []
        for i in range(9):
            for j in range(9):
                cells.append((i, j))

        # Gruppiere symmetrische Paare
        symmetric_pairs = []
        used = set()

        for i in range(9):
            for j in range(9):
                if (i, j) not in used:
                    sym_i, sym_j = 8 - i, 8 - j
                    if (i, j) == (sym_i, sym_j):
                        # Zentrale Zelle
                        symmetric_pairs.append([(i, j)])
                    else:
                        symmetric_pairs.append([(i, j), (sym_i, sym_j)])
                    used.add((i, j))
                    used.add((sym_i, sym_j))

        random.shuffle(symmetric_pairs)
        return symmetric_pairs

    def remove_numbers(self, min_clues: int, max_clues: int, symmetric: bool = False) -> bool:
        """
        Entfernt Zahlen aus dem Rätsel bis zur gewünschten Anzahl
        Stellt sicher, dass es nur eine eindeutige Lösung gibt
        """
        self.grid = copy.deepcopy(self.solution)

        if symmetric:
            cell_groups = self.get_symmetric_cells()
        else:
            # Alle Zellen in zufälliger Reihenfolge
            cells = [(i, j) for i in range(9) for j in range(9)]
            random.shuffle(cells)
            cell_groups = [[(i, j)] for i, j in cells]

        current_clues = 81

        for group in cell_groups:
            # Stoppe wenn wir im Zielbereich sind
            if current_clues <= max_clues:
                # Wenn wir schon im erlaubten Bereich sind, akzeptiere das
                if current_clues >= min_clues:
                    break

            # Speichere Werte
            saved_values = [(i, j, self.grid[i][j]) for i, j in group]

            # Entferne temporär
            for i, j, _ in saved_values:
                self.grid[i][j] = 0

            # Prüfe, ob es noch eindeutig lösbar ist
            test_grid = copy.deepcopy(self.grid)
            num_solutions = self.count_solutions(test_grid)

            if num_solutions == 1:
                # Erfolgreich entfernt
                current_clues -= len(group)
            else:
                # Wiederherstellen
                for i, j, val in saved_values:
                    self.grid[i][j] = val

        # Erfolgreich wenn wir im gewünschten Bereich sind
        return min_clues <= current_clues <= max_clues

    def generate_puzzle(self, min_clues: int, max_clues: int, symmetric: bool = False, max_attempts: int = 100) -> bool:
        """
        Generiert ein Sudoku-Rätsel mit der gewünschten Anzahl an Hinweisen
        """
        for attempt in range(max_attempts):
            self.generate_complete_grid()

            if self.remove_numbers(min_clues, max_clues, symmetric):
                return True

        return False

    def print_grid(self, grid: List[List[int]], title: str = "") -> None:
        """Zeigt das Sudoku-Grid formatiert an"""
        if title:
            print(f"\n{title}")
            print("=" * 37)

        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("-" * 37)

            row_str = ""
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    row_str += " | "

                if grid[i][j] == 0:
                    row_str += " . "
                else:
                    row_str += f" {grid[i][j]} "

            print(row_str)
        print()

    def get_clue_count(self) -> int:
        """Gibt die Anzahl der Hinweise im aktuellen Rätsel zurück"""
        return sum(1 for row in self.grid for cell in row if cell != 0)


def get_yes_no_input(prompt: str) -> bool:
    """Hilfsfunktion für Ja/Nein-Eingaben"""
    while True:
        response = input(f"{prompt} (j/n): ").strip().lower()
        if response in ['j', 'ja', 'y', 'yes']:
            return True
        elif response in ['n', 'nein', 'no']:
            return False
        else:
            print("Bitte 'j' für Ja oder 'n' für Nein eingeben.")


def get_clue_range() -> Tuple[int, int]:
    """Fragt nach der gewünschten Anzahl an Hinweisen"""
    while True:
        try:
            range_input = input("Wie viele Hinweise möchten Sie? (z.B. 20-24 oder 25): ").strip()

            if '-' in range_input:
                parts = range_input.split('-')
                min_clues = int(parts[0].strip())
                max_clues = int(parts[1].strip())
            else:
                min_clues = max_clues = int(range_input)

            if min_clues < 17:
                print("Warnung: Weniger als 17 Hinweise können zu mehreren Lösungen führen.")
                print("Minimum wird auf 17 gesetzt.")
                min_clues = 17

            if max_clues > 81:
                print("Maximum kann nicht mehr als 81 sein.")
                max_clues = 81

            if min_clues > max_clues:
                print("Der Minimalwert muss kleiner oder gleich dem Maximalwert sein.")
                continue

            return min_clues, max_clues

        except ValueError:
            print("Ungültige Eingabe. Bitte eine Zahl oder einen Bereich (z.B. 20-24) eingeben.")


def save_to_file(generator: SudokuGenerator, show_solution: bool) -> None:
    """Speichert das Sudoku als Text-Datei"""
    try:
        filename = f"sudoku_{random.randint(1000, 9999)}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("SUDOKU RÄTSEL\n")
            f.write("=" * 37 + "\n\n")
            f.write(f"Anzahl der Hinweise: {generator.get_clue_count()}\n\n")

            # Rätsel
            for i in range(9):
                if i % 3 == 0 and i != 0:
                    f.write("-" * 37 + "\n")

                row_str = ""
                for j in range(9):
                    if j % 3 == 0 and j != 0:
                        row_str += " | "

                    if generator.grid[i][j] == 0:
                        row_str += " . "
                    else:
                        row_str += f" {generator.grid[i][j]} "

                f.write(row_str + "\n")

            if show_solution:
                f.write("\n\n")
                f.write("LÖSUNG\n")
                f.write("=" * 37 + "\n\n")

                for i in range(9):
                    if i % 3 == 0 and i != 0:
                        f.write("-" * 37 + "\n")

                    row_str = ""
                    for j in range(9):
                        if j % 3 == 0 and j != 0:
                            row_str += " | "
                        row_str += f" {generator.solution[i][j]} "

                    f.write(row_str + "\n")

        print(f"\n✓ Sudoku gespeichert in: {filename}")

    except Exception as e:
        print(f"\n✗ Fehler beim Speichern: {e}")


def main():
    """Hauptfunktion für die interaktive Nutzung"""
    print("=" * 50)
    print("    SUDOKU GENERATOR für Pythonista")
    print("=" * 50)

    while True:
        print("\n")

        # Benutzereinstellungen abfragen
        symmetric = get_yes_no_input("Möchten Sie eine symmetrische Anordnung der Hinweise?")
        min_clues, max_clues = get_clue_range()

        print(f"\nGeneriere Sudoku mit {min_clues}-{max_clues} Hinweisen...")
        if symmetric:
            print("(mit symmetrischer Anordnung)")

        # Sudoku generieren
        generator = SudokuGenerator()
        success = generator.generate_puzzle(min_clues, max_clues, symmetric)

        if success:
            actual_clues = generator.get_clue_count()
            print(f"✓ Sudoku erfolgreich generiert mit {actual_clues} Hinweisen!")

            # Rätsel anzeigen
            generator.print_grid(generator.grid, "IHR SUDOKU RÄTSEL")

            # Lösung anzeigen?
            show_solution = get_yes_no_input("Möchten Sie die Lösung sehen?")
            if show_solution:
                generator.print_grid(generator.solution, "LÖSUNG")

            # Speichern?
            save_file = get_yes_no_input("Möchten Sie das Rätsel speichern?")
            if save_file:
                save_to_file(generator, show_solution)
        else:
            print("✗ Konnte kein Sudoku mit den gewünschten Eigenschaften generieren.")
            print("  Versuchen Sie es mit anderen Einstellungen.")

        # Neues Rätsel?
        print("\n")
        if not get_yes_no_input("Möchten Sie ein neues Rätsel erstellen?"):
            print("\nVielen Dank für die Nutzung des Sudoku Generators!")
            print("Auf Wiedersehen!")
            break


if __name__ == "__main__":
    main()
