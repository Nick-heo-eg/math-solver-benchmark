# echo_engine/stage5/verifier.py
from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Callable, List, Optional


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

    def verify_nCk_times_nCk(self, n1: int, k1: int, n2: int, k2: int, answer: int) -> VerifyResult:
        checks: List[Callable[[], bool]] = [
            lambda: answer == self._calc_direct(n1, k1, n2, k2),
            lambda: answer % comb(n1, k1) == 0,  # structural divisibility check
            lambda: answer % comb(n2, k2) == 0,
        ]

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

    def _calc_direct(self, n1: int, k1: int, n2: int, k2: int) -> int:
        return comb(n1, k1) * comb(n2, k2)
