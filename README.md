# Math Solver Benchmark: Pattern Matching Implementation

⚠️ **Archived Repository**

This repository is archived and no longer actively maintained.

It is preserved as an experimental or evidentiary reference.

It is not part of the current active specification layer.

**For the conceptual entry point of the execution-boundary ecosystem:**
→ [https://github.com/Nick-heo-eg/execution-boundary](https://github.com/Nick-heo-eg/execution-boundary)

---

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
```

---

## Purpose

This repository demonstrates:

- Pattern-based problem decomposition
- Deterministic execution paths
- Test coverage for specific domains

It does not attempt to:
- Generalize to arbitrary math problems
- Use LLMs for reasoning
- Provide interactive solving

---

## Architecture

```
Input Problem
     ↓
Pattern Matcher (identify problem type)
     ↓
Specialized Solver (one per pattern)
     ↓
Verified Output
```

---

## Why This Repository Is Archived

This experiment validated pattern-based solving for specific problem types.

The approach is deterministic and testable, but not generalizable.

Work has shifted toward broader structural definitions rather than domain-specific implementations.

---

## License

MIT License
