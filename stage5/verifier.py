# stage5/verifier.py
from __future__ import annotations

from dataclasses import dataclass
from math import comb, isclose
from typing import Callable, List, Optional, Union, Tuple

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


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    guard_code: Optional[str] = None
    guard_state: Optional[str] = None
    guard_action: Optional[str] = None
    reason: Optional[str] = None


class Stage5Verifier:
    """
    Loopless 'self-correction': not retrying generation,
    but performing multiple independent deterministic checks.

    Rule: ALL checks must PASS.
    """

    def verify(
        self,
        extracted: Extracted,
        answer: Union[int, float, str, List[Tuple[str, float, float]]]
    ) -> VerifyResult:
        """Dispatch to appropriate verifier based on pattern kind"""
        if extracted.kind == PatternKind.COMBINATORICS:
            return self._verify_combinatorics(extracted, answer)
        elif extracted.kind == PatternKind.ALGEBRA:
            return self._verify_algebra(extracted, answer)
        elif extracted.kind == PatternKind.NUMBER_THEORY:
            return self._verify_number_theory(extracted, answer)
        elif extracted.kind == PatternKind.GEOMETRY:
            return self._verify_geometry(extracted, answer)
        elif extracted.kind == PatternKind.PROBABILITY:
            return self._verify_probability(extracted, answer)
        elif extracted.kind == PatternKind.CALCULUS:
            return self._verify_calculus(extracted, answer)
        else:
            return VerifyResult(
                ok=False,
                guard_code="UNSUPPORTED_KIND",
                guard_state="UNSUPPORTED_KIND",
                guard_action="STOP",
                reason=f"Unsupported pattern kind: {extracted.kind}"
            )

    def _verify_combinatorics(self, ex: CombinatoricsExtracted, answer: int) -> VerifyResult:
        """Verify combinatorics answer"""
        # Recompute
        expected = sum(comb(ex.n1, k1) * comb(ex.n2, k2) for k1, k2 in ex.cases)

        checks: List[Callable[[], bool]] = [
            lambda: answer == expected,
            lambda: answer > 0,  # combinatorics result must be positive
            lambda: all(answer % comb(ex.n1, k1) == 0 for k1, _ in ex.cases),  # divisibility check
        ]

        return self._run_checks(checks)

    def _verify_algebra(self, ex: AlgebraExtracted, answer: int) -> VerifyResult:
        """Verify algebra answer"""
        expected = ex.x2_plus_y2 + 2 * ex.xy

        checks: List[Callable[[], bool]] = [
            lambda: answer == expected,
            lambda: answer > 0,  # (x+y)² must be non-negative
        ]

        return self._run_checks(checks)

    def _verify_number_theory(self, ex: NumberTheoryExtracted, answer: int) -> VerifyResult:
        """Verify number theory answer (divisor sum)"""
        # Recompute divisor sum
        divisors = self._get_divisors(ex.number)
        expected = sum(divisors)

        checks: List[Callable[[], bool]] = [
            lambda: answer == expected,
            lambda: answer >= ex.number + 1,  # σ(n) >= n + 1 for n > 1
            lambda: answer > ex.number,  # σ(n) > n always
        ]

        return self._run_checks(checks)

    def _verify_geometry(self, ex: GeometryExtracted, answer: float) -> VerifyResult:
        """Verify geometry answer"""
        from math import sqrt
        expected = sqrt(ex.radius**2 + ex.tangent**2)

        checks: List[Callable[[], bool]] = [
            lambda: isclose(answer, expected, rel_tol=1e-9),
            lambda: answer > ex.radius,  # OP > radius
            lambda: answer > ex.tangent,  # OP > tangent
        ]

        return self._run_checks(checks)

    def _verify_probability(self, ex: ProbabilityExtracted, answer: float) -> VerifyResult:
        """Verify probability answer"""
        checks: List[Callable[[], bool]] = [
            lambda: 0 <= answer <= 1,  # probability must be in [0, 1]
            lambda: answer > 0,  # should be positive for reasonable target sums
        ]

        return self._run_checks(checks)

    def _verify_calculus(
        self,
        ex: CalculusExtracted,
        answer: List[Tuple[str, float, float]]
    ) -> VerifyResult:
        """Verify calculus answer (extrema)"""
        if not isinstance(answer, list):
            return VerifyResult(
                ok=False,
                guard_code="VERIFY_FAIL",
                guard_state="VERIFY_FAIL",
                guard_action="STOP",
                reason="Calculus answer must be a list of extrema"
            )

        # Basic sanity checks
        checks: List[Callable[[], bool]] = [
            lambda: len(answer) <= 2,  # cubic has at most 2 extrema
            lambda: all(t[0] in ("max", "min") for t in answer),  # valid types
        ]

        return self._run_checks(checks)

    # Helper methods

    def _run_checks(self, checks: List[Callable[[], bool]]) -> VerifyResult:
        """Run all checks, return FAIL on first failure"""
        for idx, chk in enumerate(checks):
            try:
                if not chk():
                    return VerifyResult(
                        ok=False,
                        guard_code="VERIFY_FAIL",
                        guard_state="VERIFY_FAIL",
                        guard_action="STOP",
                        reason=f"Verifier check {idx} failed.",
                    )
            except Exception as e:
                return VerifyResult(
                    ok=False,
                    guard_code="VERIFY_ERROR",
                    guard_state="VERIFY_ERROR",
                    guard_action="STOP",
                    reason=f"Verifier exception: {e!r}",
                )

        return VerifyResult(ok=True)

    def _get_divisors(self, n: int) -> List[int]:
        """Get all divisors of n"""
        divisors = []
        for i in range(1, int(n**0.5) + 1):
            if n % i == 0:
                divisors.append(i)
                if i != n // i:
                    divisors.append(n // i)
        return sorted(divisors)
