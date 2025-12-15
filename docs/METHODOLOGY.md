# Methodology

## Experimental Design

### Objective

Measure the performance difference between LLM-based and pattern-based approaches for solving structured mathematical problems.

### Test Set

**6 problems** across 6 mathematical domains:
- Combinatorics (committees, arrangements)
- Algebra (equations, identities)
- Number Theory (divisors, factorization)
- Geometry (circles, triangles, distance)
- Probability (dice, events)
- Calculus (extrema, derivatives)

**Difficulty**: GPT-4 level (challenging for humans, solvable by advanced LLMs)

**Problem format**: Natural language text → Numerical answer

See [../data/test_problems.json](../data/test_problems.json) for complete problem set.

---

## Stages Tested

### Stage-0: Pure Computation (Baseline)
**Input**: Pre-structured data (JSON with extracted variables)
**Process**: Direct computation only
**Output**: Answer

**Purpose**: Establish theoretical minimum (no parsing overhead)

**Example**:
```
Input: {"total_men": 6, "total_women": 4, "size": 5}
Computation: C(6,3)*C(4,2) + C(6,4)*C(4,1)
Output: "180"
```

---

### Stage-1A: Mock Hybrid
**Input**: Raw problem text
**Process**: Mock parser (instant, pre-defined structures) → Compute
**Output**: Answer

**Purpose**: Test hybrid architecture overhead with zero LLM delay

---

### Stage-1B: LLM Parsing
**Input**: Raw problem text
**Process**: LLM (phi3:mini) parses → Compute
**Output**: Answer (if successful)

**LLM Configuration**:
- Model: `phi3:mini` (3.8B parameters, local via Ollama)
- Timeout: 90 seconds per problem
- Temperature: 0 (deterministic)

**Purpose**: Test real-world LLM performance in runtime

---

### Stage-2: Cached LLM
**Input**: Raw problem text
**Process**:
- First run: LLM parses → cache structure → compute
- Later runs: Load from cache → compute

**Cache Implementation**:
- Key: SHA256 hash of problem text
- Storage: Persistent JSON files
- Hit rate: 100% for repeated problems

**Purpose**: Test whether caching can amortize LLM cost

---

### Stage-3: Pattern Matching
**Input**: Raw problem text
**Process**: Pattern classify → Regex parse → Compute
**Output**: Answer

**Pattern Matching**:
- Classification: Keyword scoring (e.g., "committee" → combinatorics)
- Parsing: Domain-specific regex (e.g., `r'(\d+)\s+men'` → extract 6)
- Computation: Same deterministic engine as all stages

**Purpose**: Prove that structured problems don't need LLM at all

---

## Measurement Protocol

### Time Measurement

**What we measured**:
- Parse time (pattern matching or LLM)
- Compute time (deterministic calculation)
- Total time (parse + compute)

**How we measured**:
```python
start = time.time()
# ... operation ...
elapsed = time.time() - start
```

**Precision**: Microsecond (µs) resolution

**Iterations**:
- Stage-0, 1A, 1B, 3: Single run per problem (deterministic)
- Stage-2: 3 iterations (cold start + 2 warm cache)

### Accuracy Measurement

**Definition**: Computed answer matches expected answer

**Comparison method**:
1. Exact string match (case-insensitive)
2. Substring match (for complex answers)
3. Numerical tolerance (±0.001 for floats)

**Scoring**: Binary (correct/incorrect per problem)

---

## Experimental Conditions

### Hardware
- CPU: [Not disclosed for security]
- RAM: Sufficient for all operations
- Storage: SSD (for cache I/O)

**Note**: All stages ran on same hardware, same conditions.

### Software
- Python 3.8+
- Ollama (for phi3:mini)
- Standard libraries only (math, re, time, json)

### Controlled Variables
- Same computation engine for all stages
- Same problem set for all stages
- Same timeout (90s) for LLM stages
- Sequential execution (no parallelism)

---

## Data Collection

### Per-Problem Data
```json
{
  "problem_id": "prob_001",
  "difficulty": "hard",
  "category": "combinatorics",
  "parse_time_seconds": 0.000679,
  "compute_time_seconds": 0.000025,
  "total_time_seconds": 0.000706,
  "computed_answer": "180",
  "correct_answer": "180",
  "is_correct": true,
  "error": null
}
```

### Aggregate Metrics
- Total problems tested
- Accuracy rate (%)
- Average time (ms)
- Min/max time
- Standard deviation
- Success/failure count

---

## Threat to Validity

### Internal Validity

**Potential confounds**:
1. **System load**: Ran sequentially to minimize interference
2. **Cache warming**: Stage-2 intentionally tests cold vs warm
3. **LLM variability**: Used temperature=0 for determinism

**Mitigation**: Controlled environment, deterministic where possible

### External Validity

**Generalization limits**:
1. **Problem scope**: Only 6 categories tested
2. **Problem difficulty**: GPT-4 level, not trivial or extreme
3. **LLM choice**: phi3:mini (3.8B), not GPT-4 (trillion+)

**Claim**: Results hold for "structured mathematical problems solvable by deterministic rules"

**Does NOT claim**: Pattern matching beats LLM for all tasks

### Construct Validity

**Are we measuring what we claim?**
- ✓ Speed: Direct time measurement
- ✓ Accuracy: Binary correct/incorrect
- ✗ "Intelligence": Not measured, not claimed

**We measure**: Operational performance (time/accuracy)
**We don't measure**: Reasoning quality, generalization, understanding

---

## Reproducibility

### What's Provided
✓ Test problems (data/test_problems.json)
✓ Results (results/*.json)
✓ Methodology (this document)
✓ Experimental log (EXPERIMENT_LOG.md)

### What's NOT Provided
✗ Exact implementation code (security)
✗ Intermediate cache files
✗ Internal system architecture

### How to Reproduce (Conceptually)

**Stage-0**: Write direct computation functions for 6 problems
**Stage-3**: Write regex parsers + classification rules, then compute
**Stage-2**: Add caching layer (SHA256 key, JSON storage) to Stage-3
**Stage-1B**: Use Ollama + phi3:mini with 90s timeout

**Expected results**: Should match our findings within ±20% for timing, 100% for accuracy trends

---

## Statistical Significance

**Sample size**: N=6 (problems)

**Statistical tests**: None (deterministic, not probabilistic)

**Claim strength**: Proof of concept, not statistical inference

**Confidence**: High for tested domain, unknown for untested domains

---

## Ethical Considerations

### Disclosure
- No cherry-picking: All 6 problems reported
- Failure cases documented (Stage-1B: 0% success)
- Limitations acknowledged

### Bias
- **Pro-pattern bias**: Researchers designed both LLM and pattern approaches
- **Mitigation**: Used standard LLM (phi3:mini), didn't optimize for failure

### Intent
- Goal: Prove pattern matching viable, not "LLMs are useless"
- Context: Structured computational tasks only
- Application: System design guidance, not blanket rejection of LLMs

---

## Conclusion

This benchmark demonstrates:
1. **For structured problems**: Pattern matching ≈ 500,000× faster than LLM
2. **For cached execution**: LLM viable if problems repeat (4.3× overhead)
3. **For novel problems**: LLM fails at runtime (90s timeout)

**Validity**: High for tested domain, requires replication for other domains

**Implication**: System architects should consider deterministic layers for structured tasks instead of defaulting to LLM.
