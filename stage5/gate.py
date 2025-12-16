# stage5/gate.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class GateRoute(str, Enum):
    STRUCTURED = "STRUCTURED"    # Fast path -> direct compute (if fields present)
    PATTERNABLE = "PATTERNABLE"  # Deterministic parse -> extract then compute
    UNTRUSTED = "UNTRUSTED"      # STOP


@dataclass(frozen=True)
class GateDecision:
    route: GateRoute
    guard_code: Optional[str] = None
    guard_state: Optional[str] = None
    guard_action: Optional[str] = None  # "STOP" | "ASK" | "TOOL" etc.
    reason: Optional[str] = None


class Stage5Gate:
    """
    O(1) heuristics only. No inference.
    - STRUCTURED: already has fields required for direct compute
    - PATTERNABLE: raw text contains recognizable pattern for extraction
    - UNTRUSTED: missing/ambiguous/unsupported -> STOP
    """

    def __init__(self) -> None:
        pass

    def decide(self, problem_data: Dict[str, Any]) -> GateDecision:
        # 1) Structured path: caller already provided parsed fields
        if self._is_already_structured(problem_data):
            return GateDecision(route=GateRoute.STRUCTURED)

        # 2) Patternable path: raw text present and matches known patterns
        raw = self._get_raw(problem_data)
        if raw is not None and self._is_patternable(raw):
            return GateDecision(route=GateRoute.PATTERNABLE)

        # 3) Otherwise STOP (untrusted / insufficient observation)
        return GateDecision(
            route=GateRoute.UNTRUSTED,
            guard_code="OBS_UNTRUSTED",
            guard_state="OBS_UNTRUSTED",
            guard_action="STOP",
            reason="Input is neither structured nor patternable with deterministic rules.",
        )

    def _get_raw(self, problem_data: Dict[str, Any]) -> Optional[str]:
        # Try multiple keys: "raw", "problem", "text"
        for key in ("raw", "problem", "text"):
            val = problem_data.get(key)
            if isinstance(val, str) and val.strip():
                return val
        return None

    def _is_already_structured(self, problem_data: Dict[str, Any]) -> bool:
        """
        Check if problem_data contains pre-extracted structured fields.
        Currently only supports "kind" contract (legacy Stage-0 format).
        """
        kind = problem_data.get("kind")
        if kind == "nCk_times_nCk":
            return all(isinstance(problem_data.get(k), int) for k in ("n1", "k1", "n2", "k2"))
        return False

    def _is_patternable(self, raw: str) -> bool:
        """
        Deterministic pattern checks only.
        Keep this fast and conservative.
        Returns True if ANY pattern matches.
        """
        s = raw.lower()

        # Pattern 1: Combinatorics
        if ("committee" in s or "choose" in s or "ways" in s) and ("men" in s and "women" in s):
            return True

        # Pattern 2: Algebra (x² + y²)
        if ("x^2" in s or "x²" in s or "x**2" in s) and ("xy" in s or "x*y" in s):
            return True

        # Pattern 3: Number Theory (divisors)
        if ("divisor" in s or "factor" in s) and "sum" in s:
            return True

        # Pattern 4: Geometry (circle, radius, tangent)
        if "circle" in s and "radius" in s and "tangent" in s:
            return True

        # Pattern 5: Probability (dice)
        if ("dice" in s or "die" in s) and ("sum" in s or "probability" in s):
            return True

        # Pattern 6: Calculus (f(x), extrema)
        if "f(x)" in s and ("extrem" in s or "maximum" in s or "minimum" in s):
            return True

        return False
