"""
Sudoku Generator für Pythonista (iPad) - ERWEITERTE VERSION
Erzeugt Sudoku-Rätsel mit einzigartiger Lösung und Export zu PDF/Bild
"""

import random
import copy
from typing import List, Tuple, Optional
from datetime import datetime

# Für Bildexport
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Hinweis: PIL nicht verfügbar. Bildexport deaktiviert.")

# Für PDF-Export
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Hinweis: reportlab nicht verfügbar. PDF-Export deaktiviert.")


class SudokuGenerator:
    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]

    def is_valid(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        """Prüft, ob eine Zahl an einer Position gültig ist"""
        if num in grid[row]:
            return False

        if num in [grid[i][col] for i in range(9)]:
            return False

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
        for box in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            idx = 0
            for i in range(box, box + 3):
                for j in range(box, box + 3):
                    self.grid[i][j] = nums[idx]
                    idx += 1

        self.solve(self.grid)
        self.solution = copy.deepcopy(self.grid)

    def get_symmetric_cells(self) -> List[Tuple[int, int]]:
        """Gibt alle Zellenpositionen in symmetrischer Reihenfolge zurück"""
        symmetric_pairs = []
        used = set()

        for i in range(9):
            for j in range(9):
                if (i, j) not in used:
                    sym_i, sym_j = 8 - i, 8 - j
                    if (i, j) == (sym_i, sym_j):
                        symmetric_pairs.append([(i, j)])
                    else:
                        symmetric_pairs.append([(i, j), (sym_i, sym_j)])
                    used.add((i, j))
                    used.add((sym_i, sym_j))

        random.shuffle(symmetric_pairs)
        return symmetric_pairs

    def remove_numbers(self, min_clues: int, max_clues: int, symmetric: bool = False) -> bool:
        """Entfernt Zahlen aus dem Rätsel bis zur gewünschten Anzahl"""
        self.grid = copy.deepcopy(self.solution)

        if symmetric:
            cell_groups = self.get_symmetric_cells()
        else:
            cells = [(i, j) for i in range(9) for j in range(9)]
            random.shuffle(cells)
            cell_groups = [[(i, j)] for i, j in cells]

        current_clues = 81

        for group in cell_groups:
            # Stoppe wenn wir im Zielbereich sind
            if current_clues <= max_clues:
                if current_clues >= min_clues:
                    break

            saved_values = [(i, j, self.grid[i][j]) for i, j in group]

            for i, j, _ in saved_values:
                self.grid[i][j] = 0

            test_grid = copy.deepcopy(self.grid)
            num_solutions = self.count_solutions(test_grid)

            if num_solutions == 1:
                current_clues -= len(group)
            else:
                for i, j, val in saved_values:
                    self.grid[i][j] = val

        return min_clues <= current_clues <= max_clues

    def generate_puzzle(self, min_clues: int, max_clues: int, symmetric: bool = False, max_attempts: int = 100) -> bool:
        """Generiert ein Sudoku-Rätsel mit der gewünschten Anzahl an Hinweisen"""
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


class SudokuExporter:
    """Exportiert Sudoku-Rätsel als Bild oder PDF"""

    @staticmethod
    def draw_sudoku_grid(draw, grid: List[List[int]], offset_x: int, offset_y: int,
                         cell_size: int, font_size: int, is_solution: bool = False):
        """Zeichnet ein Sudoku-Grid auf ein Image"""
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()

        # Zeichne Grid
        for i in range(10):
            line_width = 3 if i % 3 == 0 else 1

            # Horizontale Linien
            y = offset_y + i * cell_size
            draw.line([(offset_x, y), (offset_x + 9 * cell_size, y)],
                      fill='black', width=line_width)

            # Vertikale Linien
            x = offset_x + i * cell_size
            draw.line([(x, offset_y), (x, offset_y + 9 * cell_size)],
                      fill='black', width=line_width)

        # Zeichne Zahlen
        for i in range(9):
            for j in range(9):
                if grid[i][j] != 0:
                    num_str = str(grid[i][j])
                    x = offset_x + j * cell_size + cell_size // 2
                    y = offset_y + i * cell_size + cell_size // 2

                    # Zentriere Text
                    bbox = draw.textbbox((0, 0), num_str, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]

                    text_x = x - text_width // 2
                    text_y = y - text_height // 2

                    color = 'blue' if is_solution else 'black'
                    draw.text((text_x, text_y), num_str, fill=color, font=font)

    @staticmethod
    def save_as_image(generator: SudokuGenerator, include_solution: bool = False,
                      filename: Optional[str] = None) -> Optional[str]:
        """Speichert Sudoku als PNG-Bild"""
        if not PIL_AVAILABLE:
            print("PIL ist nicht verfügbar. Bildexport nicht möglich.")
            return None

        try:
            cell_size = 60
            margin = 50
            title_height = 80

            if include_solution:
                img_width = 2 * (9 * cell_size) + 3 * margin
                img_height = 9 * cell_size + 2 * margin + title_height
            else:
                img_width = 9 * cell_size + 2 * margin
                img_height = 9 * cell_size + 2 * margin + title_height

            # Erstelle Bild
            img = Image.new('RGB', (img_width, img_height), 'white')
            draw = ImageDraw.Draw(img)

            # Titel-Font
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
                info_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
            except:
                title_font = ImageFont.load_default()
                info_font = ImageFont.load_default()

            # Titel
            title = "SUDOKU RÄTSEL"
            bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = bbox[2] - bbox[0]
            draw.text(((img_width - title_width) // 2, 20), title,
                      fill='black', font=title_font)

            # Info
            info = f"Hinweise: {generator.get_clue_count()} | Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            draw.text((margin, 60), info, fill='gray', font=info_font)

            # Zeichne Rätsel
            SudokuExporter.draw_sudoku_grid(draw, generator.grid, margin,
                                           margin + title_height, cell_size, 32)

            # Zeichne Lösung (falls gewünscht)
            if include_solution:
                solution_x = 2 * margin + 9 * cell_size

                # "LÖSUNG" Label
                solution_label = "LÖSUNG"
                bbox = draw.textbbox((0, 0), solution_label, font=info_font)
                label_width = bbox[2] - bbox[0]
                draw.text((solution_x + (9 * cell_size - label_width) // 2, margin + title_height - 30),
                         solution_label, fill='blue', font=info_font)

                SudokuExporter.draw_sudoku_grid(draw, generator.solution, solution_x,
                                               margin + title_height, cell_size, 32, is_solution=True)

            # Speichern
            if filename is None:
                filename = f"sudoku_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            img.save(filename, 'PNG')
            return filename

        except Exception as e:
            print(f"Fehler beim Erstellen des Bildes: {e}")
            return None

    @staticmethod
    def save_as_pdf(generator: SudokuGenerator, include_solution: bool = False,
                    filename: Optional[str] = None) -> Optional[str]:
        """Speichert Sudoku als PDF"""
        if not REPORTLAB_AVAILABLE:
            print("reportlab ist nicht verfügbar. PDF-Export nicht möglich.")
            return None

        try:
            if filename is None:
                filename = f"sudoku_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4

            # Titel
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(width / 2, height - 40, "SUDOKU RÄTSEL")

            # Info
            c.setFont("Helvetica", 12)
            info_text = f"Hinweise: {generator.get_clue_count()} | Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            c.drawCentredString(width / 2, height - 60, info_text)

            # Rätsel zeichnen
            cell_size = 20 * mm
            start_x = (width - 9 * cell_size) / 2
            start_y = height - 100 - 9 * cell_size

            SudokuExporter._draw_pdf_grid(c, generator.grid, start_x, start_y, cell_size, False)

            # Lösung (falls gewünscht)
            if include_solution:
                c.showPage()
                c.setFont("Helvetica-Bold", 24)
                c.drawCentredString(width / 2, height - 40, "LÖSUNG")

                SudokuExporter._draw_pdf_grid(c, generator.solution, start_x, start_y, cell_size, True)

            c.save()
            return filename

        except Exception as e:
            print(f"Fehler beim Erstellen des PDFs: {e}")
            return None

    @staticmethod
    def _draw_pdf_grid(c, grid: List[List[int]], start_x: float, start_y: float,
                       cell_size: float, is_solution: bool):
        """Hilfsfunktion zum Zeichnen eines Grids im PDF"""
        # Grid-Linien
        for i in range(10):
            line_width = 2 if i % 3 == 0 else 0.5
            c.setLineWidth(line_width)

            # Horizontale Linien
            y = start_y + i * cell_size
            c.line(start_x, y, start_x + 9 * cell_size, y)

            # Vertikale Linien
            x = start_x + i * cell_size
            c.line(x, start_y, x, start_y + 9 * cell_size)

        # Zahlen
        c.setFont("Helvetica", 16)
        for i in range(9):
            for j in range(9):
                if grid[i][j] != 0:
                    x = start_x + j * cell_size + cell_size / 2
                    y = start_y + (8 - i) * cell_size + cell_size / 2 - 5

                    c.drawCentredString(x, y, str(grid[i][j]))


def save_as_text(generator: SudokuGenerator, include_solution: bool = False,
                 filename: Optional[str] = None) -> Optional[str]:
    """Speichert das Sudoku als Text-Datei"""
    try:
        if filename is None:
            filename = f"sudoku_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 50 + "\n")
            f.write("SUDOKU RÄTSEL\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Hinweise: {generator.get_clue_count()}\n")
            f.write(f"Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")

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

            if include_solution:
                f.write("\n\n")
                f.write("=" * 50 + "\n")
                f.write("LÖSUNG\n")
                f.write("=" * 50 + "\n\n")

                for i in range(9):
                    if i % 3 == 0 and i != 0:
                        f.write("-" * 37 + "\n")

                    row_str = ""
                    for j in range(9):
                        if j % 3 == 0 and j != 0:
                            row_str += " | "
                        row_str += f" {generator.solution[i][j]} "

                    f.write(row_str + "\n")

        return filename

    except Exception as e:
        print(f"Fehler beim Speichern: {e}")
        return None


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


def main():
    """Hauptfunktion für die interaktive Nutzung"""
    print("=" * 60)
    print("    SUDOKU GENERATOR für Pythonista (ERWEITERT)")
    print("=" * 60)
    print()
    print("Verfügbare Export-Formate:")
    print(f"  - Text-Datei: Ja")
    print(f"  - PNG-Bild: {'Ja' if PIL_AVAILABLE else 'Nein (PIL fehlt)'}")
    print(f"  - PDF: {'Ja' if REPORTLAB_AVAILABLE else 'Nein (reportlab fehlt)'}")
    print()

    while True:
        print("\n" + "=" * 60)

        # Benutzereinstellungen abfragen
        symmetric = get_yes_no_input("Möchten Sie eine symmetrische Anordnung der Hinweise?")
        min_clues, max_clues = get_clue_range()

        print(f"\n⏳ Generiere Sudoku mit {min_clues}-{max_clues} Hinweisen...")
        if symmetric:
            print("   (mit symmetrischer Anordnung)")

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
                print("\nWählen Sie das Dateiformat:")
                print("  1 - Text-Datei (.txt)")
                if PIL_AVAILABLE:
                    print("  2 - PNG-Bild (.png)")
                if REPORTLAB_AVAILABLE:
                    print("  3 - PDF (.pdf)")

                format_choice = input("Ihre Wahl (1-3): ").strip()

                saved_file = None

                if format_choice == "1":
                    saved_file = save_as_text(generator, show_solution)
                elif format_choice == "2" and PIL_AVAILABLE:
                    saved_file = SudokuExporter.save_as_image(generator, show_solution)
                elif format_choice == "3" and REPORTLAB_AVAILABLE:
                    saved_file = SudokuExporter.save_as_pdf(generator, show_solution)
                else:
                    print("Ungültige Wahl. Speichere als Text-Datei...")
                    saved_file = save_as_text(generator, show_solution)

                if saved_file:
                    print(f"\n✓ Sudoku gespeichert als: {saved_file}")
                else:
                    print("\n✗ Fehler beim Speichern der Datei.")
        else:
            print("✗ Konnte kein Sudoku mit den gewünschten Eigenschaften generieren.")
            print("  Versuchen Sie es mit anderen Einstellungen.")

        # Neues Rätsel?
        print("\n" + "=" * 60)
        if not get_yes_no_input("Möchten Sie ein neues Rätsel erstellen?"):
            print("\n" + "=" * 60)
            print("Vielen Dank für die Nutzung des Sudoku Generators!")
            print("Auf Wiedersehen!")
            print("=" * 60)
            break


if __name__ == "__main__":
    main()
