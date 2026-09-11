# Japanese Sums Puzzle Generator

Ein Python-Generator für Japanese Sums Rätsel mit garantiert eindeutiger Lösung.

## Was ist Japanese Sums?

Japanese Sums ist ein Logikrätsel mit folgenden Regeln:

1. **Platziere Zahlen 1-9** in einige Zellen des Gitters (nicht alle Zellen werden gefüllt)
2. **Keine Wiederholungen**: Keine Zahl darf in einer Zeile oder Spalte mehrfach vorkommen
3. **Summen-Hinweise**: Die Zahlen außerhalb des Gitters zeigen die Summen von benachbarten Zahlengruppen in dieser Zeile/Spalte **in der angegebenen Reihenfolge**
4. **Trennungen**: Jede Summengruppe ist durch mindestens eine leere Zelle getrennt

**Wichtig:** Japanese Sums ist komplett anders als Kakuro!

## Features

- ✅ Generiert Rätsel von 5x5 bis 9x9
- ✅ 4 Schwierigkeitsstufen: Easy, Medium, Hard, Expert
- ✅ **Garantiert eindeutige Lösung** für jedes Rätsel
- ✅ Verwendet Zahlen 1-9 (nicht begrenzt auf 1-N)
- ✅ Schneller Solver mit intelligenter Beschneidung
- ✅ Generierung in vernünftiger Zeit (<5s für 5x5 bis 7x7)

## Installation

Keine externe Abhängigkeiten erforderlich! Nur Python 3.7+.

```bash
# Einfach die Datei herunterladen
# Keine pip install notwendig
```

## Schnellstart

### Beispiel 1: Einfaches Rätsel generieren

```python
from japanese_sums_generator import generate_puzzle, Difficulty

# Generiere ein MEDIUM 6x6 Rätsel
puzzle = generate_puzzle(size=6, difficulty=Difficulty.MEDIUM)

# Zeige das Rätsel mit Lösung an
puzzle.display(show_solution=True)
```

### Beispiel 2: Verschiedene Schwierigkeitsgrade

```python
from japanese_sums_generator import generate_puzzle, Difficulty

# EASY - Mehr gefüllte Zellen (55-65%)
easy_puzzle = generate_puzzle(size=5, difficulty=Difficulty.EASY)

# MEDIUM - Mittlere Füllung (45-55%)
medium_puzzle = generate_puzzle(size=6, difficulty=Difficulty.MEDIUM)

# HARD - Weniger Füllung (35-45%)
hard_puzzle = generate_puzzle(size=7, difficulty=Difficulty.HARD)

# EXPERT - Sehr wenig Füllung (28-38%)
expert_puzzle = generate_puzzle(size=8, difficulty=Difficulty.EXPERT)
```

### Beispiel 3: Lösung verifizieren

```python
from japanese_sums_generator import generate_puzzle, FastSolver, Difficulty

# Generiere Rätsel
puzzle = generate_puzzle(size=6, difficulty=Difficulty.MEDIUM)

# Verifiziere Eindeutigkeit
solver = FastSolver(puzzle.size, puzzle.row_clues, puzzle.col_clues)
num_solutions = solver.count_solutions(max_count=2)

print(f"Anzahl Lösungen: {num_solutions}")
if num_solutions == 1:
    print("✓ Eindeutige Lösung!")
```

### Beispiel 4: Manuelles Rätsel lösen

```python
from japanese_sums_generator import FastSolver

# Definiere ein Rätsel
size = 5
row_clues = [[2], [5], [7, 5], [2, 7, 3], [4]]
col_clues = [[14], [2], [7], [4], [8]]

# Löse es
solver = FastSolver(size, row_clues, col_clues)
count = solver.count_solutions(max_count=1)

if count > 0:
    print("Lösung gefunden!")
    # Zugriff auf die Lösung über solver.solution
```

## Ausgabeformat

Beispiel-Ausgabe eines 5x5 EASY Rätsels:

```
======================================================================
Japanese Sums (5x5)
======================================================================

Spalten-Hinweise (von oben nach unten):
  Spalte 1: [14]
  Spalte 2: [2]
  Spalte 3: [7]
  Spalte 4: [4]
  Spalte 5: [8]

Zeilen-Hinweise (von links nach rechts):
  Zeile 1: [2]
  Zeile 2: [5]
  Zeile 3: [7, 5]
  Zeile 4: [2, 7, 3]
  Zeile 5: [4]

Lösung:
  +---------+
  |. 2 . . .|
  |5 . . . .|
  |7 . . 4 1|
  |2 . 7 . 3|
  |. . . . 4|
  +---------+
```

Legende:
- `.` = leere Zelle
- Zahlen = gefüllte Zellen

## Performance

Generierungszeiten (auf durchschnittlicher Hardware):

| Größe | Schwierigkeit | Typische Zeit |
|-------|---------------|---------------|
| 5x5   | EASY          | ~1-2s         |
| 6x6   | MEDIUM        | ~1-3s         |
| 7x7   | HARD          | ~2-5s         |
| 8x8   | EXPERT        | ~10-30s       |
| 9x9   | EXPERT        | ~30-60s       |

**Hinweis:** Größere Rätsel (8x8, 9x9) können länger dauern, da die Unique-Solution-Verifikation aufwendiger ist.

## API-Referenz

### `generate_puzzle(size, difficulty)`

Generiert ein neues Japanese Sums Rätsel.

**Parameter:**
- `size` (int): Größe des Gitters (5-9)
- `difficulty` (Difficulty): Schwierigkeitsstufe

**Returns:** `Puzzle` Objekt

### `Puzzle` Klasse

**Attribute:**
- `size`: Gittergröße
- `row_clues`: Liste der Zeilen-Hinweise
- `col_clues`: Liste der Spalten-Hinweise
- `solution`: Lösungsgitter

**Methoden:**
- `display(show_solution=False)`: Zeigt das Rätsel an

### `FastSolver` Klasse

**Methoden:**
- `count_solutions(max_count=2)`: Zählt Lösungen bis max_count
- `has_unique_solution()`: Prüft auf eindeutige Lösung

## Technische Details

### Algorithmus

1. **Generierung:**
   - Erstellt ein zufälliges Gitter mit kontrollierten Füllungsraten
   - Stellt sicher, dass jede Zeile/Spalte mindestens eine Gruppe hat
   - Extrahiert Summen-Hinweise aus dem Lösungsgitter

2. **Unique-Solution-Verifikation:**
   - Verwendet Backtracking mit aggressiver Beschneidung
   - Prüft partielle Constraints bei jedem Schritt
   - Stoppt nach Finden von 2 Lösungen (Effizienz)

3. **Optimierungen:**
   - Early pruning durch partielle Constraint-Checks
   - Limit auf Suchknoten (1M) um Timeout zu vermeiden
   - Intelligente Platzierungsstrategien für Gruppierung

### Unterschied zu Kakuro

- **Kakuro**: Alle Zellen in einem Bereich werden gefüllt, Summen haben feste Längen
- **Japanese Sums**: Nicht alle Zellen werden gefüllt, Gruppen haben variable Längen, Trennungen durch leere Zellen

## Beispiel-Skripte

```bash
# Hauptgenerator ausführen (zeigt mehrere Beispiele)
python japanese_sums_generator.py

# Beispielsammlung ausführen
python example_usage.py
```

## Troubleshooting

**Problem:** "Timeout after 30.0s"
- Größere Rätsel (8x8, 9x9) brauchen manchmal länger
- Versuchen Sie es erneut oder reduzieren Sie die Größe

**Problem:** "Failed to generate valid puzzle"
- Sehr selten bei kleineren Größen
- Generierung erneut versuchen

## Lizenz

Dieses Projekt ist frei verfügbar für persönliche und kommerzielle Nutzung.

## Autor

Erstellt am 2025-12-05

## Weiterführende Informationen

- [Logic Masters Deutschland - Japanese Sums](https://logic-masters.de/Raetselportal/Raetsel/zeigen.php?chlang=en&id=000594)
- [The Art of Puzzles - Japanese Sums](https://www.gmpuzzles.com/blog/category/numberplacement/japanese-sums/)
