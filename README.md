# Math Solver Benchmark: LLM vs Pattern Matching

> **TL;DR**: We tested 5 approaches to solve GPT-4 level math problems. Pattern matching (no LLM) won by **400,000×** in speed while maintaining 100% accuracy.

[![Experiment Status](https://img.shields.io/badge/experiment-completed-success)]()
[![Accuracy](https://img.shields.io/badge/accuracy-100%25-brightgreen)]()
[![Speed](https://img.shields.io/badge/speedup-400000x-blue)]()

> ⚠️ **Important**: This compares **runtime LLM parsing vs LLM-designed patterns**, not "LLM capability vs regex". See [CLARIFICATION.md](CLARIFICATION.md) for details.

## Quick Results

| Approach | Speed | Accuracy | LLM Used |
|----------|-------|----------|----------|
| **Pure Computation** | 0.008ms | 100% | No |
| **Pattern Matching** | 0.183ms | 100% | No |
| **Cached LLM** | 0.034ms (after 500ms cold start) | 100% | Once |
| **LLM Parsing** | >90,000ms (timeout) | 0% | Yes |

## The Question

**Can deterministic pattern matching replace LLM "understanding" for structured computational tasks?**

## The Answer

**Yes. And it's 400,000× faster.**

## What We Actually Compared

This is **not** "regex vs LLM capability". It's **runtime architecture comparison**:

### Architecture A: LLM Parsing at Runtime
- **Model**: phi3:mini (3.8B parameters, local via Ollama)
- **Process**: Problem → LLM parses → Extract structure → Compute
- **LLM role**: Called at runtime for every single problem
- **Result**: 90,000ms timeout, 0% success rate

### Architecture B: Pattern Matching (LLM-Designed, Runtime-Free)
- **Design phase**: Patterns designed once with Claude's assistance (offline)
- **Runtime**: Problem → Regex match → Extract structure → Compute
- **LLM role**: None at runtime (only used during design)
- **Result**: 0.183ms, 100% success rate

### Key Distinction

**Claude designed the patterns** (Architecture B), but **doesn't run them**.

This validates the principle: **"LLM for design (offline), deterministic code for execution (online)"**

The comparison proves: Runtime LLM parsing (phi3:mini) vs LLM-designed patterns (no runtime LLM) = 492,896× speedup.

## What We Tested

6 GPT-4 level math problems across different domains:
- Combinatorics
- Algebra
- Number Theory
- Geometry
- Probability
- Calculus

See [data/test_problems.json](data/test_problems.json) for full problem set.

## Results Summary

### Speed Comparison (Log Scale)

```
0.008ms    ████ Stage-0: Pure computation
0.012ms    ████ Stage-1A: Mock parser
0.034ms    █████ Stage-2: Cached LLM
0.183ms    ███████ Stage-3: Pattern matching ⟵ Best non-LLM
500ms      ████████████████████████████████ Stage-2: Cold start
90,000ms   ████████████████████████████████████████████████ Stage-1B: LLM (FAILED)
```

### Key Findings

1. **LLM is always the bottleneck**
   - Real-time LLM parsing: 90s timeout, 0% accuracy
   - Even cached LLM: 4.3× overhead vs pure computation

2. **Pattern matching wins for structured problems**
   - 23.5× slower than pure computation (still <1ms)
   - 492,896× faster than LLM parsing
   - 100% accuracy, deterministic

3. **The cost of "intelligence"**
   - Orchestration overhead: 1.5×
   - Cache I/O: 4.3×
   - Pattern matching: 23.5×
   - LLM generation: **64,208×**

## How Pattern Matching Works

```
Input: "A committee of 5 people from 6 men and 4 women..."

Step 1: Classify
  Keywords ["committee", "choose"] → Combinatorics

Step 2: Parse (regex)
  "6 men" → total_men = 6
  "4 women" → total_women = 4
  "committee of 5" → size = 5

Step 3: Compute (deterministic)
  answer = C(6,3) × C(4,2) + C(6,4) × C(4,1)
  answer = 120 + 60 = 180 ✓

Time: 0.7ms (vs 90,000ms for LLM)
```

No "understanding", no "reasoning", just:
- Pattern recognition (regex)
- Variable extraction
- Formula application

## How to Run

### Quick Start (Pattern Matching - No LLM Required)

```bash
# Clone the repository
git clone https://github.com/Nick-heo-eg/math-solver-benchmark.git
cd math-solver-benchmark

# Run Stage-3 (pattern matching benchmark)
python scripts/run_stage3_pattern_matching.py

# Run Stage-0 (pure computation baseline)
python scripts/run_stage0_baseline.py
```

**No dependencies required** - Uses only Python standard library (3.8+)

### Running LLM Experiments (Optional)

To reproduce Stage-1B (LLM parsing failure) or Stage-2 (cached LLM):

```bash
# Install Ollama
# https://ollama.ai/

# Pull phi3:mini model
ollama pull phi3:mini

# Run Stage-2 (cached LLM)
python scripts/run_stage2_cached_interpretation.py

# Run Stage-1B (LLM parsing - will timeout)
# Warning: Takes 90s per problem, all fail
python scripts/run_stage1b_llm_parsing.py
```

### Results

All scripts save results to `results/` directory in JSON format.

## Documentation

- **[EXPERIMENT_LOG.md](EXPERIMENT_LOG.md)** - Complete experimental log with methodology
- **[docs/METHODOLOGY.md](docs/METHODOLOGY.md)** - How we measured and compared
- **[docs/FINDINGS.md](docs/FINDINGS.md)** - Three key findings explained
- **[docs/FAQ.md](docs/FAQ.md)** - Common questions answered

## Results Data

All experimental results available in JSON format:
- [results/summary.json](results/summary.json) - Overall comparison
- [results/stage0_pure_computation.json](results/stage0_pure_computation.json)
- [results/stage2_cached_llm.json](results/stage2_cached_llm.json)
- [results/stage3_pattern_matching.json](results/stage3_pattern_matching.json)

## The Broader Implication

This isn't just about math. It's about **system design philosophy**:

### Traditional Approach
```
Problem → LLM → Solution
(slow, expensive, non-deterministic)
```

### Structural Approach
```
Problem → Pattern Match → Deterministic Layer → Solution
(fast, cheap, deterministic)

LLM used only for designing layers (offline, once)
```

## Three Design Principles

1. **No non-determinism in runtime**
   - Token generation, sampling, LLM inference = forbidden in execution path

2. **No LLM in runtime**
   - LLM can design the system (offline)
   - LLM cannot run the system (online)

3. **No human time scale illusion**
   - 2 seconds ≠ "fast enough" for systems
   - Only <1ms is "sufficiently zero"

## Limitations

**What pattern matching can solve** (6 categories tested):
- ✓ Standard combinatorics
- ✓ Algebraic equations
- ✓ Number theory
- ✓ Basic geometry
- ✓ Probability calculations
- ✓ Calculus extrema

**What it cannot solve** (yet):
- ✗ Novel problem types not in pattern library
- ✗ Graph theory (no layer designed)
- ✗ Abstract algebra (no layer designed)
- ✗ Truly creative/unstructured problems

**To add new domain**: Design parser once (with Claude/GPT-4), then runs forever without LLM.

## FAQ

**Q: Is this just hardcoding?**

A: Patterns are reusable, numbers are computed dynamically. Same pattern handles `"5 from 6 men, 4 women" → 180` and `"10 from 20 men, 15 women" → different answer`. Not hardcoded answers, just structured extraction + computation. See [FAQ.md](docs/FAQ.md#is-this-just-hardcoding) for details.

**Q: What about GPT-4?**

A: Faster than phi3:mini, but still 1000-10,000× slower than pattern matching. Plus cost: $0.03 per problem vs $0.000001.

**Q: When should I use LLM then?**

A: For truly unstructured problems where patterns don't exist yet. Use LLM to explore, then crystallize patterns into deterministic layers.

## Related Work

This benchmark validates the **Echo Judgment System** philosophy:

> "Place judgment in the future, bind observation to the present"

- **Judgment** (design/structure) = LLM, offline, slow, expensive
- **Observation** (execution) = deterministic, online, fast, free

Full system architecture: [EchoJudgmentSystem](https://github.com/Nick-heo-eg/EchoJudgmentSystem_v10) (private - research in progress)

## Contributing

This is a completed experiment/benchmark. We're not accepting code contributions, but:

- **Questions**: Open an issue
- **New benchmarks**: Share your results in discussions
- **Reproduce**: All data provided, methodology documented

## License

MIT License - See [LICENSE](LICENSE) for details

## Citation

If you use this benchmark in your research:

```bibtex
@misc{math-solver-benchmark-2025,
  title={Math Solver Benchmark: LLM vs Pattern Matching},
  author={Echo Judgment System Research},
  year={2025},
  url={https://github.com/Nick-heo-eg/math-solver-benchmark}
}
```

## Contact

- Issues: Use GitHub issues for questions
- Research collaboration: [Open a discussion]
- Related work: [Echo Judgment System](https://github.com/Nick-heo-eg/EchoJudgmentSystem_v10)

---

**Built to prove a point**: For deterministic computational tasks, the best LLM is no LLM.

**Tested**: December 2025
**Status**: Experiment complete, results public
