# echo_engine/stage5/gate.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class GateRoute(str, Enum):
    STRUCTURED = "STRUCTURED"    # Fast path -> Stage-0
    PATTERNABLE = "PATTERNABLE"  # Deterministic parse -> Stage-3
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
    - STRUCTURED: already has fields required for Stage-0 compute
    - PATTERNABLE: raw text contains recognizable pattern for Stage-3 extraction
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
        raw = problem_data.get("raw")
        return raw if isinstance(raw, str) and raw.strip() else None

    def _is_already_structured(self, problem_data: Dict[str, Any]) -> bool:
        """
        Example structured contract (customize to your existing Stage-0 schema):
          { "kind": "nCk_times_nCk", "n1": 6, "k1": 3, "n2": 4, "k2": 2 }
        """
        kind = problem_data.get("kind")
        if kind == "nCk_times_nCk":
            return all(isinstance(problem_data.get(k), int) for k in ("n1", "k1", "n2", "k2"))
        return False

    def _is_patternable(self, raw: str) -> bool:
        """
        Deterministic pattern checks only.
        Keep this fast and conservative.
        """
        s = raw.lower()
        # Example: committee / combinations pattern
        if ("committee" in s or "choose" in s) and ("men" in s and "women" in s):
            return True
        return False
