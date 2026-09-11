# Was ich aus ChatGPT's Code lernen kann

## Kernkonzepte von ChatGPT's überlegenem Ansatz

### 1. **Forward Construction statt Backward Search**

**ChatGPT**:
```python
def generate_unique_puzzle():
    solution = random_solution_grid(rows, cols, black_prob)  # 1. Vollständiges Raster
    row_clues, col_clues = derive_clues(solution)            # 2. Clues ableiten
    sol_count = solve_japanese_sums(...)                      # 3. Verifizieren
    if sol_count == 1: return puzzle
```

**Mein Ansatz (alt)**:
```python
def generate():
    grid = place_groups_partially()  # 1. Partielle Platzierung
    clues = extract_clues()          # 2. Clues extrahieren
    count = backtrack_solve()        # 3. Langsam verifizieren
```

**Learning**: Forward Construction ist VIEL effizienter, weil:
- Man startet mit einem garantiert gültigen Raster
- Keine ungültigen Zwischenzustände
- Einfachere Clue-Extraktion

### 2. **CSP-Solver mit Pattern-Domains**

**ChatGPT's Brillanz**:
```python
@lru_cache(maxsize=None)
def _build_line_patterns_cached(size: int, clues: Tuple[int, ...]) -> List[Pattern]:
    """Generiert ALLE möglichen Zeilen/Spalten-Muster für gegebene Clues"""
    # Beispiel: clues=[3, 7] in size=7
    # Patterns: (1,2,0,4,3), (2,1,0,3,4), (3,0,4,3,0), ...
    # ALLE werden vorberechnet und gecached!
```

**Vorteile**:
- Patterns werden nur 1x berechnet, dann cached
- Arc Consistency kann direkt auf Patterns arbeiten
- Massive Beschleunigung durch Vorberechnung

**Mein Ansatz**: Berechne mögliche Werte on-the-fly → langsam!

### 3. **Arc Consistency mit aggressiver Constraint Propagation**

```python
def propagate(r_dom, c_dom):
    while changed:
        for r, c in all_cells:
            row_vals = {p[c] for p in r_dom[r]}  # Mögliche Werte aus Zeilen-Patterns
            col_vals = {p[r] for p in c_dom[c]}  # Mögliche Werte aus Spalten-Patterns
            allowed = row_vals & col_vals        # Schnittmenge = EINZIGE gültige Werte

            # Reduziere Domains basierend auf allowed
            r_dom[r] = [p for p in r_dom[r] if p[c] in allowed]
            c_dom[c] = [p for p in c_dom[c] if p[r] in allowed]
```

**Learning**:
- Domains werden iterativ reduziert bis Fixpunkt
- Oft wird Lösung OHNE Suche gefunden (alle Domains = 1 Pattern)
- Wenn Suche nötig, ist Suchraum bereits winzig klein

### 4. **Most Constrained Variable (MCV) Heuristik**

```python
candidates = [
    (len(r_dom[i]), ('r', i)) for i in range(rows) if len(r_dom[i]) > 1
]
candidates.sort()  # Sortiere nach Anzahl Möglichkeiten
_, (axis, idx) = candidates[0]  # Wähle Variable mit WENIGSTEN Möglichkeiten
```

**Learning**:
- Wähle immer die "am meisten eingeschränkte" Variable zuerst
- Minimiert Branching-Faktor
- Findet Widersprüche früher

### 5. **Adaptive Black Probability**

```python
def _sample_black_prob(rows, cols, attempt):
    band = attempt % 3
    if band == 0:   # Versuche 1, 4, 7, 10, ...
        return random.uniform(0.18, 0.32)  # Weniger Schwarzfelder
    elif band == 1: # Versuche 2, 5, 8, 11, ...
        return random.uniform(0.26, 0.44)  # Mittlere Schwarzfelder
    else:           # Versuche 3, 6, 9, 12, ...
        return random.uniform(0.34, 0.52)  # Mehr Schwarzfelder
```

**Learning**:
- Variiere Strategie basierend auf Attempt-Nummer
- Erzeugt Mix aus verschiedenen Puzzle-Charakteristiken
- Verhindert "stuck in local optimum"

### 6. **Quality Checks auf Clue-Verteilung**

```python
def _clue_spread_ok(row_clues, col_clues):
    small = sum(1 for v in flat if v <= 10)
    medium = sum(1 for v in flat if 11 <= v <= 17)
    large = sum(1 for v in flat if v >= 18)

    # Fordere Mix aus kleinen, mittleren und großen Summen
    if medium + large < total // 6: return False
    if small / total > 0.8: return False
    if max(rows, cols) >= 9 and large == 0: return False
```

**Learning**:
- Quality ist nicht nur "unique solution"
- Clue-Verteilung wichtig für interessante Rätsel
- Automatische Ablehnung von "langweiligen" Rätseln

## Mögliche Verbesserungen über ChatGPT hinaus

### Idee 1: **Parallele Multi-Candidate Generation**

```python
from multiprocessing import Pool

def generate_parallel(rows, cols, num_workers=4):
    with Pool(num_workers) as pool:
        # Generiere 4 Kandidaten parallel
        results = pool.starmap(generate_single_attempt, [(rows, cols)] * 4)
        # Wähle besten Kandidaten (z.B. nach Quality-Score)
        return max(results, key=lambda p: quality_score(p))
```

**Vorteil**: 4x Speedup auf 4-Core System!

### Idee 2: **Learned Heuristics**

```python
class LearnedGenerator:
    def __init__(self):
        self.success_stats = {}  # black_prob → success_rate

    def sample_black_prob(self, rows, cols):
        # Statt fixed bands, lerne welche Werte gut funktionieren
        if (rows, cols) in self.success_stats:
            # Sample bevorzugt aus erfolgreichen Bereichen
            return weighted_sample(self.success_stats[(rows, cols)])
        return default_sample()

    def record_result(self, rows, cols, black_prob, success):
        # Lerne aus jedem Versuch
        self.success_stats[(rows, cols)][black_prob] += 1 if success else -1
```

**Vorteil**: Wird besser je mehr Rätsel generiert werden!

### Idee 3: **Constraint-basierte Grid-Generation**

Statt random backtracking:
```python
def random_solution_grid_csp(rows, cols, black_prob):
    # Nutze CSP-Solver schon für Grid-Generation!
    domains = [[set(range(10)) for _ in range(cols)] for _ in range(rows)]

    # Wende Constraints direkt an
    for r in range(rows):
        for c in range(cols):
            if random.random() < black_prob:
                domains[r][c] = {0}
            else:
                # Entferne bereits verwendete Werte
                used_row = get_used_in_row(r)
                used_col = get_used_in_col(c)
                domains[r][c] -= used_row | used_col

    # Arc Consistency für Grid-Generation
    propagate_grid_constraints(domains)
    # MCV-basierte Wertauswahl
    return solve_with_mcv(domains)
```

**Vorteil**: Schnellere Grid-Generation durch intelligente Constraint-Nutzung!

### Idee 4: **Pattern-Cache Optimierung**

```python
# Statt Dict, nutze komprimierten Trie
class PatternCache:
    def __init__(self):
        self.trie = {}
        self.compressed_patterns = {}

    def get_patterns(self, size, clues):
        key = (size, tuple(clues))
        if key in self.compressed_patterns:
            # Dekomprimiere patterns
            return decompress(self.compressed_patterns[key])

        patterns = _build_line_patterns(size, clues)
        # Komprimiere und speichere
        self.compressed_patterns[key] = compress(patterns)
        return patterns
```

**Vorteil**: Weniger Memory, mehr Patterns können gecached werden!

### Idee 5: **Hybrid Forward-Backward Approach**

```python
def generate_hybrid(rows, cols):
    # Phase 1: Forward - generiere vollständiges Raster
    solution = random_solution_grid(rows, cols, black_prob)
    row_clues, col_clues = derive_clues(solution)

    # Phase 2: Backward - entferne Constraints iterativ
    # Versuche Clues zu minimieren während Eindeutigkeit erhalten bleibt
    for r in range(rows):
        for clue_idx in range(len(row_clues[r])):
            # Versuche diesen Clue zu entfernen
            test_clues = row_clues[:r] + [row_clues[r][:clue_idx] + row_clues[r][clue_idx+1:]] + row_clues[r+1:]
            if solve_count(test_clues, col_clues) == 1:
                row_clues = test_clues  # Clue war redundant!

    return minimized_puzzle
```

**Vorteil**: Minimale Anzahl Clues = schwierigere, elegantere Rätsel!

## Konkreter Plan für verbesserten Generator

### japanese_sums_ultimate.py - Kombination aller Best Practices:

1. ✓ Forward Construction (von ChatGPT)
2. ✓ CSP-Solver mit Pattern-Domains (von ChatGPT)
3. ✓ Arc Consistency (von ChatGPT)
4. ✓ MCV Heuristik (von ChatGPT)
5. ✓ Adaptive Strategies (von ChatGPT)
6. **NEU**: Parallele Generation
7. **NEU**: Constraint-basierte Grid-Generation
8. **NEU**: Optimierter Pattern-Cache
9. **NEU**: Optional: Clue Minimization

**Erwartete Performance**:
- 5x5-7x7: < 0.05s (schneller als ChatGPT)
- 8x8-9x9: < 0.5s (schneller als ChatGPT)
- 10x10-13x13: < 5s (gleich oder schneller als ChatGPT)

## Nächste Schritte

1. Implementiere `japanese_sums_ultimate.py` mit allen Verbesserungen
2. Benchmark gegen ChatGPT's Implementation
3. Wenn schneller: Das wäre der ultimative Generator!
4. Wenn langsamer: Lerne warum und iteriere
