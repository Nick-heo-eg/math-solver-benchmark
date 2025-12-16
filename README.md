# Math Solver Benchmark: Pattern Matching Implementation

> **Status**: 6/6 patterns implemented and verified (2025-12-16)

[![Tests](https://img.shields.io/badge/tests-6/6_passing-success)]()
[![Patterns](https://img.shields.io/badge/patterns-6_implemented-blue)]()

## What This Is

A **deterministic pattern matching solver** for 6 specific math problem types:

1. **Combinatorics** - Committee selection (nCk × nCk)
2. **Algebra** - (x+y)² given x²+y² and xy
3. **Number Theory** - Divisor sum
4. **Geometry** - Pythagorean theorem (circle tangent)
5. **Probability** - Dice sum probability
6. **Calculus** - Local extrema of cubic polynomials

**Not a general math solver**. Only these 6 specific patterns are supported.

---

## Test Results

```bash
$ python scripts/test_all_problems.py

Results: 6/6 passed

By category:
  ✅ algebra: 1/1
  ✅ calculus: 1/1
  ✅ combinatorics: 1/1
  ✅ geometry: 1/1
  ✅ number_theory: 1/1
  ✅ probability: 1/1
```

**Input Variation Test**:
```bash
$ python scripts/test_input_variation.py

✅ ALL INPUT VARIATION TESTS PASSED
   Solver uses extracted values, NOT hardcoded answers
```

---

## How It Works

```
Input Text → Pattern Matching (regex) → Extract Variables → Compute → Verify → Output
```

### Example: Combinatorics

**Input**:
```
"A committee of 5 people from 6 men and 4 women.
 Must contain at least 3 men and at least 1 woman."
```

**Processing**:
1. **Gate**: Detects "committee", "men", "women" keywords → PATTERNABLE
2. **Extractor**: Regex extracts `n1=6, n2=4, cases=[(3,2), (4,1)]`
3. **Solver**: Computes `C(6,3)×C(4,2) + C(6,4)×C(4,1) = 120 + 60 = 180`
4. **Verifier**: Confirms answer matches recomputation
5. **Explainer**: Generates step-by-step explanation

**Output**: `180`

**Different Input**:
```
"A committee of 7 people from 10 men and 8 women.
 Must contain at least 4 men and at least 2 women."
```

**Output**: `Different answer` (proves not hardcoded)

---

## Supported Patterns

### 1. Combinatorics

**Pattern**: Committee selection with constraints

**Example**: "6 men, 4 women, committee of 5, at least 3 men and 1 woman"

**Extractor**: Regex for numbers, keywords ("committee", "men", "women", "at least")

**Solver**: `sum(C(n1, k1_i) × C(n2, k2_i) for each valid case)`

---

### 2. Algebra

**Pattern**: Find (x+y)² given x²+y² and xy

**Example**: "If x² + y² = 25 and xy = 12, find (x + y)²"

**Extractor**: Regex for `x²+y²=value` and `xy=value`

**Solver**: `(x+y)² = x²+y² + 2xy`

---

### 3. Number Theory

**Pattern**: Sum of divisors

**Example**: "Find the sum of all positive divisors of 360"

**Extractor**: Regex for "divisors of N"

**Solver**: Prime factorization → σ(n) formula

---

### 4. Geometry

**Pattern**: Circle tangent distance (Pythagorean theorem)

**Example**: "Circle radius 10, tangent length 24, find distance OP"

**Extractor**: Regex for "radius N" and "tangent N"

**Solver**: `OP = √(radius² + tangent²)`

---

### 5. Probability

**Pattern**: Dice sum probability

**Example**: "Three dice rolled, probability sum = 10"

**Extractor**: Regex for "N dice" and "sum = M"

**Solver**: Brute force enumeration of all outcomes

---

### 6. Calculus

**Pattern**: Local extrema of cubic polynomials

**Example**: "f(x) = x³ - 6x² + 9x + 1, find local extrema"

**Extractor**: Regex for polynomial coefficients

**Solver**: f'(x)=0 → critical points, f''(x) → classify max/min

---

## What's NOT Supported

- **Problem variations not matching regex**: Slightly different wording may fail
- **Other problem types**: Graph theory, linear algebra, differential equations, etc.
- **Novel patterns**: Only the 6 patterns above are implemented
- **Natural language understanding**: Pure regex matching, no LLM

**If input doesn't match a pattern → STOP (no answer)**

---

## Usage

### Test All Patterns

```bash
python scripts/test_all_problems.py
```

Tests 6 problems from `data/test_problems.json`.

### Test Input Variation

```bash
python scripts/test_input_variation.py
```

Proves solver uses extracted values (not hardcoded).

### Use as Library

```python
from stage5 import Stage5Pipeline

pipeline = Stage5Pipeline()

# Option 1: Raw text
result = pipeline.solve({
    "problem": "Find sum of divisors of 360"
})

print(result.answer)  # "1170"
print(result.text)    # Explanation

# Option 2: Pre-extracted (structured)
result = pipeline.solve({
    "kind": "nCk_times_nCk",
    "n1": 6, "k1": 3, "n2": 4, "k2": 2
})

print(result.answer)  # "120"
```

---

## Technical Details

### Contract: Parser → Solver

**Rule**: Solver ONLY uses values extracted by Parser

**Example** (Algebra):
- Parser extracts: `x2_plus_y2=25, xy=12`
- Solver computes: `25 + 2×12 = 49`
- Solver NEVER uses hardcoded values

See `PATTERN_CONTRACT.md` for full specification.

### Verification

Every answer is verified by:
1. **Recomputation**: Compute again using extracted values
2. **Sanity checks**: Domain-specific validation (e.g., probability ∈ [0,1])
3. **Structural checks**: Answer type and range validation

If verification fails → STOP (no answer returned)

---

## Limitations

### What This Proves

✅ **Pattern matching works for structured problems**
- 6/6 test cases pass
- Input variation → output variation (not hardcoded)
- Sub-millisecond latency
- No LLM required at runtime

### What This Does NOT Prove

❌ **Not a general solver**
- Only 6 specific patterns
- Regex requires exact keyword matches
- Cannot handle problem variations beyond implemented patterns

❌ **Not better than LLMs at understanding**
- LLMs can solve novel problems
- This cannot (pattern library is fixed)

❌ **Not "100% accuracy" claim**
- 100% on these 6 test cases
- Unknown accuracy on unseen problems (likely 0% if pattern doesn't match)

---

## Architecture

```
stage5/
├── gate.py         # Route decision (STRUCTURED/PATTERNABLE/UNTRUSTED)
├── extractor.py    # 6 regex patterns for variable extraction
├── solver.py       # 6 deterministic compute functions
├── verifier.py     # 6 verification functions
├── explainer.py    # 6 explanation generators
└── pipeline.py     # Orchestration (no loops, no LLM)
```

**Principle**: Gate → Extract → Solve → Verify → Explain

**STOP conditions**:
- Pattern not recognized
- Extraction failed
- Verification failed
- Solver exception

---

## Dependencies

**None**. Uses only Python standard library (3.8+):
- `re` - Regex matching
- `math` - comb(), sqrt()
- `itertools` - Probability enumeration

---

## Test Files

- `data/test_problems.json` - 6 test problems (1 per category)
- `scripts/test_all_problems.py` - Verify all 6 pass
- `scripts/test_input_variation.py` - Prove not hardcoded
- `PATTERN_CONTRACT.md` - Parser-Solver contract specification

---

## Comparison to README Claims (Before Fix)

### Before (Overclaimed)

- ❌ "100% accuracy" (on what dataset?)
- ❌ "GPT-4 level problems" (only 6 specific patterns)
- ❌ "Pattern matching > LLM understanding" (not a fair comparison)
- ❌ Implied generalization (was 1 pattern, claimed 6 categories)

### After (Honest)

- ✅ "6/6 patterns implemented" (specific count)
- ✅ "Only these 6 patterns supported" (clear limitation)
- ✅ "100% on test set" (dataset specified: 6 problems)
- ✅ Input variation test proves not hardcoded

---

## Philosophical Note

**This is a structural prototype, not a product.**

**Purpose**: Demonstrate that **for known, structured problem types**:
- Deterministic extraction + computation is sufficient
- LLM not needed at runtime
- Sub-millisecond latency achievable

**Not claiming**: Pattern matching replaces LLMs for general math.

**Claiming**: For these 6 patterns, deterministic code works.

---

## Related Work

This validates part of the **Echo Judgment System** philosophy:

> "LLM for design (offline), deterministic code for execution (online)"

- **Design phase**: Patterns designed once (with human/LLM assistance)
- **Runtime**: Pure regex + computation (no LLM)

Full system: [EchoJudgmentSystem](https://github.com/Nick-heo-eg/EchoJudgmentSystem_v10)

---

## License

MIT License

---

## Honesty Statement

**What changed** (2025-12-16):
- README previously claimed 6 categories support with 1 pattern implemented
- Code now implements all 6 patterns matching README claims
- All test cases pass (6/6)
- Input variation test added to prove not hardcoded
- Removed unsupported claims ("100% accuracy", "GPT-4 level")
- Added explicit limitations section

**Principle**: Cannot claim to solve what hasn't been implemented.

---

**Last verified**: 2025-12-16
**Test status**: 6/6 passing, input variation verified
