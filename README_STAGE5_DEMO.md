# Stage-5 Math Solver: Quick Start Guide

## What is Stage-5?

**Deterministic math solver with NO LLMs, NO loops, NO retries.**

- **Gate**: Routes input to STRUCTURED/PATTERNABLE/UNTRUSTED paths
- **Extractor**: Regex-based parser (no AI)
- **Verifier**: Multi-check validation without retry
- **Explainer**: Natural language output generation

**Key principle**: Input determines output. Same input = same output, always.

---

## Quick Start

### 1. Run the demo

```bash
python math_experiments/scripts/run_stage5_loopless.py
```

**Output:**
```
=== Problem #1 ===
{"kind": "nCk_times_nCk", "n1": 6, "k1": 3, "n2": 4, "k2": 2}
Route: STRUCTURED → PASS | Answer = 120
Choose 3 from 6 and 2 from 4, independently.
Total ways = C(6,3) × C(4,2) = 120.

=== Problem #2 ===
{"raw": "There are 6 men and 4 women. How many committees of 5 can be formed with 3 men and 2 women?"}
Route: PATTERNABLE → PASS | Answer = 120
Choose 3 from 6 and 2 from 4, independently.
Total ways = C(6,3) × C(4,2) = 120.

=== Problem #3 ===
{"raw": "Solve it"}
Route: UNTRUSTED → STOP (OBS_UNTRUSTED)
Reason: Input is neither structured nor patternable with deterministic rules.
```

---

## Try Your Own Inputs

### Option A: Python REPL

```python
from echo_engine.stage5 import Stage5Pipeline

p = Stage5Pipeline()

# Test different values
result = p.solve({"kind": "nCk_times_nCk", "n1": 10, "k1": 5, "n2": 8, "k2": 3})
print(f"Answer: {result.answer}")  # C(10,5) × C(8,3) = 14112

# Test natural language input
result = p.solve({
    "raw": "There are 10 men and 8 women. How many committees of 8 can be formed with 5 men and 3 women?"
})
print(f"Answer: {result.answer}")  # Same: 14112
```

### Option B: Modify the demo script

Edit `math_experiments/scripts/run_stage5_loopless.py`:

```python
def _sample_problems() -> List[Dict[str, Any]]:
    # Add your own test cases here
    test1 = {"kind": "nCk_times_nCk", "n1": 20, "k1": 10, "n2": 15, "k2": 5}
    test2 = {"raw": "100 men and 50 women committee..."}
    return [test1, test2]
```

---

## Compare with LLM-based solvers

### Stage-5 (This implementation)

```python
from echo_engine.stage5 import Stage5Pipeline
import time

p = Stage5Pipeline()

start = time.time()
result = p.solve({"kind": "nCk_times_nCk", "n1": 6, "k1": 3, "n2": 4, "k2": 2})
elapsed = time.time() - start

print(f"Answer: {result.answer}")
print(f"Time: {elapsed*1000:.3f}ms")
print(f"Correct: {result.ok}")
```

**Output:**
```
Answer: 120
Time: 0.234ms
Correct: True
```

### LLM-based solver (for comparison)

```python
import anthropic
import time

client = anthropic.Anthropic()

start = time.time()
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=512,
    messages=[{
        "role": "user",
        "content": "Choose 3 from 6 men and 2 from 4 women. How many committees?"
    }]
)
elapsed = time.time() - start

print(f"Answer: {response.content[0].text}")
print(f"Time: {elapsed*1000:.1f}ms")
```

**Typical output:**
```
Answer: To solve this, we use combinations...
        C(6,3) × C(4,2) = 20 × 6 = 120
Time: 1847.3ms
```

### Comparison Table

| Method | Time | Deterministic | Cost | Input Variation |
|--------|------|---------------|------|-----------------|
| **Stage-5** | ~0.2ms | ✅ Yes | $0 | Change n1,k1,n2,k2 freely |
| **Claude Sonnet** | ~1800ms | ❌ No | $0.003/query | Must re-prompt |
| **GPT-4** | ~2500ms | ❌ No | $0.015/query | Must re-prompt |
| **Local LLM (phi3)** | ~90000ms | ❌ No | $0 | 90s timeout issues |

---

## Why Stage-5 is faster

### LLM approach (slow)
```
User input → Tokenize → Neural network inference (1000+ matrix ops)
→ Generate tokens sequentially → Parse text output
```

### Stage-5 approach (fast)
```
User input → Regex match (O(n)) → Math formula (O(1)) → Return int
```

**No neural network. No token generation. Pure computation.**

---

## What Stage-5 can solve

✅ **Supported**: Combination problems (nCk × nCk)
- Structured input: `{"kind": "nCk_times_nCk", "n1": 6, "k1": 3, "n2": 4, "k2": 2}`
- Natural language: `"X men and Y women, committee of Z with A men and B women"`

❌ **Not supported** (returns STOP):
- Ambiguous input: `"Solve it"`
- Other problem types: Algebra, geometry, calculus (not implemented yet)

**This is by design.** Stage-5 returns STOP instead of guessing wrong answers.

---

## Extend to new problem types

Want to add support for quadratic equations?

1. **Add to Gate** (`echo_engine/stage5/gate.py`):
```python
def _is_quadratic(self, raw: str) -> bool:
    return "x^2" in raw or "quadratic" in raw
```

2. **Add to Extractor** (`echo_engine/stage5/extractor.py`):
```python
_re_quadratic = re.compile(r"x\^2\s*\+\s*(\d+)x\s*\+\s*(\d+)")
```

3. **Add to Verifier** (`echo_engine/stage5/verifier.py`):
```python
def verify_quadratic(self, a, b, c, roots):
    # Check discriminant, substitute roots back
```

4. **Add to Pipeline** (`echo_engine/stage5/pipeline.py`):
```python
if decision.route == GateRoute.QUADRATIC:
    return self._solve_quadratic(extracted)
```

---

## Philosophy: Judgment before execution

Stage-5 implements **temporal priority**:

1. **Judge** input trustworthiness (Gate)
2. **Extract** observable facts (Extractor)
3. **Verify** computation correctness (Verifier)
4. **Explain** result to human (Explainer)

**If any step fails → STOP immediately with guard_code.**

No loops. No retries. No "maybe this will work" attempts.

---

## References

- **Full implementation**: `echo_engine/stage5/`
- **Design document**: `STAGE5_LOOPLESS_UNIVERSAL_JUDGMENT.md`
- **Unit tests**: `tests/unit/test_stage5_*.py`

**System philosophy**: `SYSTEM_ESSENCE.md`
> "판단을 미래에 두고, 관측을 현재에 묶어, 그 사이의 마찰을 듣는 시스템이다."
