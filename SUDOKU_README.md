# Sudoku Generator für Pythonista (iPad)

Ein leistungsstarker Sudoku-Generator, der speziell für Pythonista auf dem iPad entwickelt wurde.

## Features

✨ **Einzigartige Lösungen**: Jedes generierte Sudoku hat garantiert genau eine Lösung
🔄 **Symmetrische Anordnung**: Optional symmetrische Platzierung der Hinweise
🎯 **Präzise Clue-Kontrolle**: Genaue Angabe der gewünschten Anzahl an Hinweisen (z.B. 20-24)
💾 **Mehrfache Export-Formate**: Text, PNG-Bild und PDF
🔁 **Interaktive Nutzung**: Erzeuge mehrere Rätsel nacheinander
📱 **iPad-optimiert**: Speziell für Pythonista entwickelt

## Verfügbare Versionen

### 1. sudoku_generator.py (Basis-Version)
- Grundlegende Sudoku-Generierung
- Text-Export
- Alle Kernfunktionen
- Keine zusätzlichen Abhängigkeiten

### 2. sudoku_generator_advanced.py (Erweiterte Version)
- Alle Features der Basis-Version
- PNG-Bildexport (benötigt Pillow)
- PDF-Export (benötigt reportlab)
- Verbesserte Formatierung

## Installation

### Für Pythonista auf dem iPad:

1. **Basis-Version** (keine Abhängigkeiten):
   ```python
   # Einfach sudoku_generator.py in Pythonista öffnen und ausführen
   ```

2. **Erweiterte Version** (mit Bild/PDF-Export):

   Installiere die Abhängigkeiten in Pythonista:
   ```python
   import pip
   pip.main(['install', 'Pillow'])
   pip.main(['install', 'reportlab'])
   ```

   Oder verwende das StaSh-Terminal in Pythonista:
   ```bash
   pip install Pillow reportlab
   ```

## Verwendung

### Schnellstart

```python
python sudoku_generator.py
```

oder für die erweiterte Version:

```python
python sudoku_generator_advanced.py
```

### Interaktive Eingaben

Das Programm führt Sie durch folgende Schritte:

1. **Symmetrie**: Möchten Sie symmetrische Clue-Anordnung? (j/n)
2. **Anzahl Hinweise**: Wie viele Hinweise? (z.B. "20-24" oder "30")
3. **Lösung anzeigen**: Möchten Sie die Lösung sehen? (j/n)
4. **Speichern**: Möchten Sie das Rätsel speichern? (j/n)
5. **Dateiformat**: Wählen Sie Text, PNG oder PDF
6. **Neues Rätsel**: Möchten Sie ein weiteres Rätsel erstellen? (j/n)

### Beispiel-Sitzung

```
==================================================
    SUDOKU GENERATOR für Pythonista
==================================================

Möchten Sie eine symmetrische Anordnung der Hinweise? (j/n): j
Wie viele Hinweise möchten Sie? (z.B. 20-24 oder 25): 22-25

Generiere Sudoku mit 22-25 Hinweisen...
(mit symmetrischer Anordnung)
✓ Sudoku erfolgreich generiert mit 24 Hinweisen!

IHR SUDOKU RÄTSEL
=====================================
 .  .  3  |  .  .  .  |  7  .  .
 .  5  .  |  .  8  .  |  .  3  .
 8  .  .  |  .  .  .  |  .  .  1
-------------------------------------
 .  .  .  |  3  .  6  |  .  .  .
 .  8  .  |  .  .  .  |  .  1  .
 .  .  .  |  2  .  4  |  .  .  .
-------------------------------------
 7  .  .  |  .  .  .  |  .  .  9
 .  1  .  |  .  4  .  |  .  6  .
 .  .  9  |  .  .  .  |  2  .  .

Möchten Sie die Lösung sehen? (j/n): j

LÖSUNG
=====================================
 2  6  3  |  9  1  5  |  7  4  8
 1  5  7  |  6  8  2  |  9  3  4
 8  9  4  |  7  3  6  |  5  2  1
-------------------------------------
 4  2  1  |  3  9  6  |  8  7  5
 9  8  5  |  4  7  3  |  6  1  2
 6  7  3  |  2  5  4  |  1  9  8
-------------------------------------
 7  3  2  |  1  6  8  |  4  5  9
 5  1  8  |  9  4  7  |  3  6  2
 3  4  9  |  5  2  1  |  2  8  7

Möchten Sie das Rätsel speichern? (j/n): j

Wählen Sie das Dateiformat:
  1 - Text-Datei (.txt)
  2 - PNG-Bild (.png)
  3 - PDF (.pdf)
Ihre Wahl (1-3): 2

✓ Sudoku gespeichert als: sudoku_20231126_143022.png

Möchten Sie ein neues Rätsel erstellen? (j/n): n

Vielen Dank für die Nutzung des Sudoku Generators!
Auf Wiedersehen!
```

## Programmier-Schnittstelle

Sie können den Generator auch programmatisch verwenden:

```python
from sudoku_generator import SudokuGenerator

# Erstelle Generator-Instanz
generator = SudokuGenerator()

# Generiere ein Sudoku mit 25-30 Hinweisen, symmetrisch
success = generator.generate_puzzle(
    min_clues=25,
    max_clues=30,
    symmetric=True
)

if success:
    # Zeige das Rätsel
    generator.print_grid(generator.grid, "Mein Sudoku")

    # Zeige die Lösung
    generator.print_grid(generator.solution, "Lösung")

    # Hole Anzahl der Hinweise
    clue_count = generator.get_clue_count()
    print(f"Anzahl Hinweise: {clue_count}")
```

### Erweiterte Verwendung mit Export

```python
from sudoku_generator_advanced import SudokuGenerator, SudokuExporter

generator = SudokuGenerator()
generator.generate_puzzle(min_clues=22, max_clues=24, symmetric=True)

# Exportiere als PNG mit Lösung
SudokuExporter.save_as_image(
    generator,
    include_solution=True,
    filename="mein_sudoku.png"
)

# Exportiere als PDF ohne Lösung
SudokuExporter.save_as_pdf(
    generator,
    include_solution=False,
    filename="mein_sudoku.pdf"
)
```

## Technische Details

### Algorithmen

- **Generierung**: Verwendet einen optimierten Backtracking-Algorithmus
- **Eindeutigkeit**: Jedes Rätsel wird auf Eindeutigkeit geprüft
- **Symmetrie**: Point-Symmetrie um die Mitte des Grids
- **Schwierigkeit**: Kontrolle über Schwierigkeit durch Anzahl der Hinweise

### Hinweis-Anzahl und Schwierigkeit

| Hinweise | Schwierigkeit |
|----------|---------------|
| 40-50    | Sehr leicht   |
| 30-39    | Leicht        |
| 25-29    | Mittel        |
| 22-24    | Schwer        |
| 17-21    | Sehr schwer   |

**Minimum**: 17 Hinweise (mathematisches Minimum für eindeutige Lösung)

### Symmetrie-Typen

Aktuell unterstützt: **Point-Symmetrie** (180° Rotation)
- Wenn eine Zahl bei (i,j) vorhanden ist, ist auch bei (8-i, 8-j) eine Zahl

## Dateiformat-Spezifikationen

### Text (.txt)
- Einfaches ASCII-Format
- Grid mit Linien zur Visualisierung
- Optional mit Lösung
- Kompatibel mit allen Texteditoren

### PNG-Bild (.png)
- Hochauflösendes Raster-Bild
- Professionelles Layout
- Rätsel und optional Lösung nebeneinander
- Zeitstempel inklusive
- Ideal zum Teilen und Drucken

### PDF (.pdf)
- Vektorbasiertes Format
- Skalierbar ohne Qualitätsverlust
- Separate Seiten für Rätsel und Lösung
- Ideal zum Drucken auf A4

## Tipps für Pythonista auf dem iPad

1. **Speicherort**: Dateien werden im aktuellen Pythonista-Arbeitsverzeichnis gespeichert
2. **Dateien teilen**: Nutzen Sie die Share-Funktion in Pythonista
3. **Batch-Generierung**: Erstellen Sie ein Skript für mehrere Rätsel
4. **Performance**: Die Generierung kann 5-30 Sekunden dauern, abhängig von den Einstellungen

## Fehlerbehebung

### "PIL nicht verfügbar"
```python
# In Pythonista:
import pip
pip.main(['install', 'Pillow'])
```

### "reportlab nicht verfügbar"
```python
# In Pythonista:
import pip
pip.main(['install', 'reportlab'])
```

### Generierung dauert zu lange
- Erhöhen Sie die maximale Anzahl der Hinweise
- Deaktivieren Sie die Symmetrie
- Bei sehr wenigen Hinweisen (<20) kann es länger dauern

### Keine Lösung gefunden
- Probieren Sie andere Einstellungen
- Das Programm versucht bis zu 50 Mal, ein gültiges Rätsel zu erzeugen
- Bei extremen Einstellungen (z.B. genau 17 symmetrische Hinweise) kann dies schwierig sein

## Lizenz

Dieses Projekt ist Open Source und kann frei verwendet werden.

## Autor

Entwickelt für Pythonista auf dem iPad.

## Changelog

### Version 2.0 (Advanced)
- PDF-Export hinzugefügt
- PNG-Bildexport hinzugefügt
- Verbesserte Benutzeroberfläche
- Zeitstempel in Dateien

### Version 1.0 (Basis)
- Initiale Version
- Grundlegende Sudoku-Generierung
- Text-Export
- Symmetrie-Unterstützung
- Eindeutigkeitsprüfung
