# Pattern Contract - Stage5 General Solver

> **작성일**: 2025-12-16
> **목적**: Parser가 추출하는 변수와 Solver가 사용하는 변수의 계약 명시

---

## 원칙

1. **Parser가 추출한 모든 변수는 Solver에서 사용되어야 함**
2. **Solver는 Parser가 추출하지 않은 값을 사용할 수 없음**
3. **입력 변화 시 출력 반드시 변화** (하드코딩 금지)

---

## Pattern 1: Combinatorics (nCk × nCk)

### 문제 예시
```
A committee of 5 people from 6 men and 4 women.
Must contain at least 3 men and at least 1 woman.
```

### Parser 출력 (Extractor)
```python
@dataclass
class CombinatoricsExtracted:
    n1: int  # total men (6)
    k1: int  # men to choose (3 or 4)
    n2: int  # total women (4)
    k2: int  # women to choose (2 or 1)
    cases: List[Tuple[int, int]]  # [(3,2), (4,1)]
```

### Solver 계산
```python
answer = sum(comb(n1, k1_i) * comb(n2, k2_i) for k1_i, k2_i in cases)
```

### 입력 변화 예시
- 입력: "6 men, 4 women, committee of 5, 3 men 2 women" → 출력: 120
- 입력: "10 men, 8 women, committee of 7, 4 men 3 women" → 출력: 11760 (변화 확인)

---

## Pattern 2: Algebra (x² + y² and xy given)

### 문제 예시
```
If x² + y² = 25 and xy = 12, find (x + y)²
```

### Parser 출력
```python
@dataclass
class AlgebraExtracted:
    x2_plus_y2: int  # 25
    xy: int          # 12
    target: str      # "(x + y)^2"
```

### Solver 계산
```python
# (x + y)² = x² + 2xy + y²
answer = x2_plus_y2 + 2 * xy
```

### 입력 변화 예시
- 입력: "x² + y² = 25, xy = 12" → 출력: 49
- 입력: "x² + y² = 50, xy = 20" → 출력: 90 (변화 확인)

---

## Pattern 3: Number Theory (Divisor Sum)

### 문제 예시
```
Find the sum of all positive divisors of 360
```

### Parser 출력
```python
@dataclass
class NumberTheoryExtracted:
    number: int  # 360
    operation: str  # "divisor_sum"
```

### Solver 계산
```python
# Prime factorization: 360 = 2³ × 3² × 5¹
# σ(n) = Π[(p^(k+1) - 1) / (p - 1)]
def prime_factorization(n: int) -> Dict[int, int]:
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = 1
    return factors

factors = prime_factorization(number)
answer = 1
for prime, exp in factors.items():
    answer *= (prime**(exp + 1) - 1) // (prime - 1)
```

### 입력 변화 예시
- 입력: "divisors of 360" → 출력: 1170
- 입력: "divisors of 12" → 출력: 28 (변화 확인)

---

## Pattern 4: Geometry (Pythagorean Theorem)

### 문제 예시
```
Circle with radius 10, tangent from P has length 24.
Find distance OP.
```

### Parser 출력
```python
@dataclass
class GeometryExtracted:
    radius: float    # 10
    tangent: float   # 24
    target: str      # "OP"
```

### Solver 계산
```python
# OP² = radius² + tangent²
import math
answer = math.sqrt(radius**2 + tangent**2)
```

### 입력 변화 예시
- 입력: "radius 10, tangent 24" → 출력: 26
- 입력: "radius 5, tangent 12" → 출력: 13 (변화 확인)

---

## Pattern 5: Probability (Dice Sum)

### 문제 예시
```
Three dice are rolled. Probability that sum is exactly 10?
```

### Parser 출력
```python
@dataclass
class ProbabilityExtracted:
    num_dice: int     # 3
    target_sum: int   # 10
```

### Solver 계산
```python
# Brute force enumeration
def count_dice_sum(num_dice: int, target_sum: int) -> int:
    count = 0
    for outcome in itertools.product(range(1, 7), repeat=num_dice):
        if sum(outcome) == target_sum:
            count += 1
    return count

total_outcomes = 6 ** num_dice
favorable = count_dice_sum(num_dice, target_sum)
answer = favorable / total_outcomes
```

### 입력 변화 예시
- 입력: "3 dice, sum = 10" → 출력: 0.125 (27/216)
- 입력: "2 dice, sum = 7" → 출력: 0.167 (6/36) (변화 확인)

---

## Pattern 6: Calculus (Local Extrema)

### 문제 예시
```
f(x) = x³ - 6x² + 9x + 1
Find all local extrema
```

### Parser 출력
```python
@dataclass
class CalculusExtracted:
    coefficients: List[float]  # [1, -6, 9, 1] for x³ - 6x² + 9x + 1
    degree: int                # 3
```

### Solver 계산
```python
import numpy as np

# f'(x) = 3x² - 12x + 9
derivative = np.polyder(coefficients)

# Find critical points: f'(x) = 0
critical_points = np.roots(derivative)

# f''(x) for second derivative test
second_derivative = np.polyder(derivative)

extrema = []
for x in critical_points:
    f_val = np.polyval(coefficients, x)
    f_double_prime = np.polyval(second_derivative, x)

    if f_double_prime < 0:
        extrema.append(("max", x, f_val))
    elif f_double_prime > 0:
        extrema.append(("min", x, f_val))

answer = extrema  # [("max", 1, 5), ("min", 3, 1)]
```

### 입력 변화 예시
- 입력: "x³ - 6x² + 9x + 1" → 출력: max at (1, 5), min at (3, 1)
- 입력: "x³ - 3x + 2" → 출력: max at (-1, 4), min at (1, 0) (변화 확인)

---

## 계약 검증 규칙

### Parser → Solver 계약
1. **Parser가 추출한 모든 필드는 Solver에서 사용**
2. **Solver는 Parser 출력 외 값을 사용 금지**
3. **Parser 실패 시 STOP (하드코딩 대체 금지)**

### 입력 변화 검증
1. **각 패턴마다 최소 2개 서로 다른 입력 테스트**
2. **입력 변경 시 출력 반드시 변경**
3. **같은 패턴, 다른 숫자 → 다른 답**

---

## 금지 사항

❌ **Parser 출력 무시하고 하드코딩**
```python
# 금지
def solve(extracted):
    return 180  # 항상 같은 값
```

❌ **Parser 없이 직접 계산**
```python
# 금지
def solve(raw_text):
    return comb(6, 3) * comb(4, 2)  # 6, 3, 4, 2가 어디서 왔는지 불명
```

❌ **Parser 실패 시 기본값 사용**
```python
# 금지
extracted = extractor.extract(raw) or DEFAULT_VALUES
```

✅ **올바른 구조**
```python
extracted = extractor.extract(raw)
if extracted is None:
    return STOP("EXTRACT_FAIL")

answer = solver.compute(extracted)  # extracted 값만 사용
```

---

**최종 원칙**: Parser가 못 뽑으면 못 푼다. 하지만 못 푸는 척하지 않는다.
