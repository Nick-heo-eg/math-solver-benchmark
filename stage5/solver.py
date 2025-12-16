# stage5/solver.py
from __future__ import annotations

import itertools
from math import comb, sqrt
from typing import Union, List, Tuple, Dict

from .extractor import (
    Extracted,
    CombinatoricsExtracted,
    AlgebraExtracted,
    NumberTheoryExtracted,
    GeometryExtracted,
    ProbabilityExtracted,
    CalculusExtracted,
    PatternKind
)


class Stage5Solver:
    """
    Deterministic computation only.
    Uses ONLY values extracted by Parser.
    No hardcoding, no external data sources.
    """

    def solve(self, extracted: Extracted) -> Union[int, float, str, List[Tuple[str, float, float]]]:
        """Dispatch to appropriate solver based on pattern kind"""
        if extracted.kind == PatternKind.COMBINATORICS:
            return self._solve_combinatorics(extracted)
        elif extracted.kind == PatternKind.ALGEBRA:
            return self._solve_algebra(extracted)
        elif extracted.kind == PatternKind.NUMBER_THEORY:
            return self._solve_number_theory(extracted)
        elif extracted.kind == PatternKind.GEOMETRY:
            return self._solve_geometry(extracted)
        elif extracted.kind == PatternKind.PROBABILITY:
            return self._solve_probability(extracted)
        elif extracted.kind == PatternKind.CALCULUS:
            return self._solve_calculus(extracted)
        else:
            raise ValueError(f"Unsupported pattern kind: {extracted.kind}")

    def _solve_combinatorics(self, ex: CombinatoricsExtracted) -> int:
        """
        Contract: Uses ex.n1, ex.n2, ex.cases
        Formula: sum(C(n1, k1_i) × C(n2, k2_i) for each case)
        """
        total = 0
        for k1, k2 in ex.cases:
            total += comb(ex.n1, k1) * comb(ex.n2, k2)
        return total

    def _solve_algebra(self, ex: AlgebraExtracted) -> int:
        """
        Contract: Uses ex.x2_plus_y2, ex.xy
        Formula: (x + y)² = x² + 2xy + y²
        """
        return ex.x2_plus_y2 + 2 * ex.xy

    def _solve_number_theory(self, ex: NumberTheoryExtracted) -> int:
        """
        Contract: Uses ex.number
        Formula: σ(n) = Π[(p^(k+1) - 1) / (p - 1)] for prime factorization
        """
        factors = self._prime_factorization(ex.number)
        sigma = 1
        for prime, exp in factors.items():
            sigma *= (prime ** (exp + 1) - 1) // (prime - 1)
        return sigma

    def _solve_geometry(self, ex: GeometryExtracted) -> float:
        """
        Contract: Uses ex.radius, ex.tangent
        Formula: OP² = radius² + tangent² (Pythagorean theorem)
        """
        return sqrt(ex.radius ** 2 + ex.tangent ** 2)

    def _solve_probability(self, ex: ProbabilityExtracted) -> float:
        """
        Contract: Uses ex.num_dice, ex.target_sum
        Method: Brute force enumeration of all outcomes
        """
        total_outcomes = 6 ** ex.num_dice
        favorable = self._count_dice_sum(ex.num_dice, ex.target_sum)
        return favorable / total_outcomes

    def _solve_calculus(self, ex: CalculusExtracted) -> List[Tuple[str, float, float]]:
        """
        Contract: Uses ex.coefficients
        Method: Find critical points via derivative, classify via second derivative test
        Returns: [(type, x, f(x))] where type in ("max", "min")
        """
        # f(x) coefficients: [a, b, c, d] for ax³ + bx² + cx + d
        a, b, c, d = ex.coefficients

        # f'(x) = 3ax² + 2bx + c
        # Solve 3ax² + 2bx + c = 0 using quadratic formula
        A = 3 * a
        B = 2 * b
        C = c

        discriminant = B**2 - 4*A*C
        if discriminant < 0:
            return []  # No real critical points

        x1 = (-B + sqrt(discriminant)) / (2 * A)
        x2 = (-B - sqrt(discriminant)) / (2 * A)

        extrema = []
        for x in [x1, x2]:
            # f''(x) = 6ax + 2b
            f_double_prime = 6 * a * x + 2 * b

            # f(x) value
            f_val = a * x**3 + b * x**2 + c * x + d

            if f_double_prime < 0:
                extrema.append(("max", round(x, 6), round(f_val, 6)))
            elif f_double_prime > 0:
                extrema.append(("min", round(x, 6), round(f_val, 6)))

        return sorted(extrema, key=lambda t: t[1])  # sort by x value

    # Helper methods

    def _prime_factorization(self, n: int) -> Dict[int, int]:
        """Return prime factorization as {prime: exponent}"""
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

    def _count_dice_sum(self, num_dice: int, target_sum: int) -> int:
        """Count how many ways to get target_sum with num_dice dice"""
        count = 0
        for outcome in itertools.product(range(1, 7), repeat=num_dice):
            if sum(outcome) == target_sum:
                count += 1
        return count
