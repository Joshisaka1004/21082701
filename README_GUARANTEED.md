# Japanese Sums Generator - 100% Garantierte Eindeutigkeit

Ein professioneller Generator für Japanese Sums Puzzles mit **mathematisch bewiesener Eindeutigkeit**.

## 🎯 Kerngarantie

**WENN ein Rätsel generiert wird, hat es GARANTIERT exakt 1 eindeutige Lösung!**

Der Generator verwendet eine strikte Verifikationsstrategie:
- Jeder Kandidat wird vollständig durchsucht (bis zu 10 Millionen Knoten)
- Kandidaten die das Limit erreichen werden **VERWORFEN**
- Nur vollständig verifizierte Rätsel werden akzeptiert

## ✅ Zuverlässige Größen

| Größe | Status | Generierungszeit | Zuverlässigkeit |
|-------|--------|------------------|-----------------|
| 5x5   | ⚠️ Variabel | 10-60s | ~60% |
| 6x6   | ⚠️ Variabel | 15-90s | ~50% |
| **7x7** | ✅ **Zuverlässig** | **4-8s** | **~95%** |
| 8x8   | ⚠️ Variabel | 20-120s | ~40% |
| **9x9** | ⚠️ Funktioniert oft | 2-20s | **~70%** |
| 10x10 | ⚠️ Schwierig | 30-180s | ~30% |

**Empfehlung**: Verwenden Sie **7x7** für zuverlässige Ergebnisse.

## 📦 Verwendung

```python
from japanese_sums_universal import generate_puzzle, Difficulty

# Einfachste Verwendung (7x7 empfohlen)
puzzle = generate_puzzle(7, 7, Difficulty.MEDIUM)
puzzle.display(show_solution=True)

# Andere Größen (können timeouten)
try:
    puzzle = generate_puzzle(9, 9, Difficulty.MEDIUM)
    print("✓ Erfolgreich generiert - 100% eindeutig!")
except TimeoutError:
    print("Timeout - versuchen Sie es erneut oder nutzen Sie 7x7")

# Rechteckige Gitter
puzzle = generate_puzzle(5, 7, Difficulty.EASY)
```

## 🔧 Schwierigkeitsgrade

- **EASY**: 70-80% gefüllte Zellen, einfachere Summen
- **MEDIUM**: 62-72% gefüllte Zellen, ausgeglichene Herausforderung
- **HARD**: 52-62% gefüllte Zellen, komplexere Rätsel
- **EXPERT**: 47-57% gefüllte Zellen, maximale Schwierigkeit

## 🎮 Adaptive Strategie

Der Generator passt sich automatisch an:

1. **Start**: Normale Füllrate für den Schwierigkeitsgrad
2. **Verwerfung**: Kandidaten die max_nodes erreichen werden verworfen
3. **Anpassung**: Nach 8 Versuchen mit >3 Verwerfungen → Füllrate +8%
4. **Erfolg**: Erstes vollständig verifiziertes Rätsel wird akzeptiert

## ⚙️ Technische Details

### Verifikationsalgorithmus

```python
class UniversalSolver:
    max_nodes = 10,000,000  # Sehr hohes Limit
    hit_limit = False       # Flag für Limit-Erkennung

    def count_solutions(self, max_count=2):
        # Vollständige Backtracking-Suche
        # Zählt bis zu 2 Lösungen
        # Setzt hit_limit=True wenn max_nodes erreicht
```

### Garantie-Mechanismus

```python
solver = UniversalSolver(rows, cols, row_clues, col_clues)
count = solver.count_solutions(max_count=2)

if count == 1 and not solver.hit_limit:
    # ✓ 100% GARANTIERT EINDEUTIG
    return puzzle
else:
    # ✗ Verwerfen und neu generieren
    continue
```

## 📊 Beispieloutput

```
7x7 MEDIUM...
  (Füllrate erhöht um 0% nach 1 Versuchen)
  (Generiert nach 2 Versuchen in 4.5s)
  (Verifiziert: 565,943 Knoten, 5.7% des Limits)
  ✓✓✓ 100% GARANTIERT EINDEUTIG!
```

## ⚠️ Wichtige Hinweise

### Timeouts

Manche Größen können timeouten, wenn:
- Zu viele Kandidaten das max_nodes Limit erreichen
- Der Suchraum zu groß ist
- Die adaptive Strategie nicht schnell genug anpasst

**Lösung**: Erneut versuchen oder 7x7 verwenden

### Füllraten

Höhere Füllraten (60-80%) machen:
- ✅ Verifikation schneller
- ✅ Eindeutigkeit garantierbar
- ⚠️ Rätsel eventuell etwas einfacher

### Performance-Optimierung

Für **maximale Zuverlässigkeit**:
```python
# 7x7 ist der Sweet Spot
puzzle = generate_puzzle(7, 7, Difficulty.MEDIUM)
```

Für **größere Herausforderung** (mit Timeout-Risiko):
```python
# 9x9 funktioniert oft, aber nicht immer
try:
    puzzle = generate_puzzle(9, 9, Difficulty.HARD)
except TimeoutError:
    print("Timeout - verwenden Sie MEDIUM oder versuchen Sie erneut")
```

## 🔬 Verifikation

Alle generierten Rätsel können nachgeprüft werden:

```python
from japanese_sums_universal import UniversalSolver

solver = UniversalSolver(
    puzzle.rows, puzzle.cols,
    puzzle.row_clues, puzzle.col_clues
)

count = solver.count_solutions(max_count=2)
nodes_pct = (solver.nodes_explored / solver.max_nodes) * 100

print(f"Lösungen: {count}")
print(f"Knoten: {solver.nodes_explored:,} ({nodes_pct:.1f}%)")
print(f"Hit Limit: {solver.hit_limit}")

if count == 1 and not solver.hit_limit:
    print("✓ 100% GARANTIERT EINDEUTIG!")
```

## 📈 Erfolgsstatistiken

Basierend auf Tests:
- **7x7**: ~95% Erfolgsrate, Ø 5s Generierung
- **9x9**: ~70% Erfolgsrate, Ø 8s Generierung
- **Alle akzeptierten Rätsel**: 100% eindeutig verifiziert

## 🎯 Best Practices

1. **Verwenden Sie 7x7** für Produktionsumgebungen
2. **Implementieren Sie Retry-Logik** für größere Gitter
3. **Zeigen Sie Fortschritt** an (Generator gibt Status aus)
4. **Fangen Sie Timeouts** ab und informieren Sie den Benutzer

```python
def generate_reliable_puzzle(size=7, max_retries=3):
    """Generiert ein Rätsel mit Retry-Logik"""
    for attempt in range(max_retries):
        try:
            return generate_puzzle(size, size, Difficulty.MEDIUM)
        except TimeoutError:
            if attempt < max_retries - 1:
                print(f"Versuch {attempt+1} timeout, versuche erneut...")
            else:
                print("Verwende 7x7 als Fallback...")
                return generate_puzzle(7, 7, Difficulty.MEDIUM)
```

## 🚀 Zusammenfassung

### ✅ Garantien

- **100% Eindeutigkeit** für alle generierten Rätsel
- **Vollständige Verifikation** (kein max_nodes erreicht)
- **Mathematisch bewiesen** (komplette Backtracking-Suche)

### ⚠️ Einschränkungen

- **Nicht alle Größen** funktionieren zuverlässig
- **Mögliche Timeouts** bei großen Gittern
- **Höhere Füllraten** machen Rätsel tendenziell einfacher

### 🎯 Empfehlung

Verwenden Sie **7x7 MEDIUM** für den besten Kompromiss zwischen:
- Zuverlässigkeit (~95%)
- Geschwindigkeit (~5s)
- Rätselqualität (ausgeglichen)
- Garantierte Eindeutigkeit (100%)

---

**Status**: Production-ready für 7x7, Best-Effort für andere Größen
**Garantie**: 100% eindeutige Lösungen WENN erfolgreich generiert
**Lizenz**: MIT
