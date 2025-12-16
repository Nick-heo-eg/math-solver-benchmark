# echo_engine/stage5/pipeline.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .gate import GateRoute, Stage5Gate
from .extractor import Stage5Extractor
from .verifier import Stage5Verifier
from .explainer import Stage5Explainer


@dataclass(frozen=True)
class Stage5Response:
    ok: bool
    answer: Optional[int] = None
    text: str = ""
    guard_code: Optional[str] = None
    guard_state: Optional[str] = None
    guard_action: Optional[str] = None
    route: Optional[str] = None
    reason: Optional[str] = None


class Stage5Pipeline:
    """
    Deterministic pipeline.
    - No loops
    - No LLM calls
    - STOP is a state (guard_code propagates)
    """

    def __init__(self) -> None:
        self.gate = Stage5Gate()
        self.extractor = Stage5Extractor()
        self.verifier = Stage5Verifier()
        self.explainer = Stage5Explainer()

    def solve(self, problem_data: Dict[str, Any]) -> Stage5Response:
        decision = self.gate.decide(problem_data)

        if decision.route == GateRoute.UNTRUSTED:
            return Stage5Response(
                ok=False,
                answer=None,
                text="",
                guard_code=decision.guard_code,
                guard_state=decision.guard_state,
                guard_action=decision.guard_action,
                route=decision.route.value,
                reason=decision.reason,
            )

        # STRUCTURED -> Stage-0 compute
        if decision.route == GateRoute.STRUCTURED:
            kind = problem_data["kind"]
            if kind != "nCk_times_nCk":
                return Stage5Response(
                    ok=False,
                    text="",
                    guard_code="UNSUPPORTED_KIND",
                    guard_state="UNSUPPORTED_KIND",
                    guard_action="STOP",
                    route=decision.route.value,
                    reason=f"Unsupported kind: {kind}",
                )

            n1, k1, n2, k2 = problem_data["n1"], problem_data["k1"], problem_data["n2"], problem_data["k2"]
            answer = self._compute_stage0_nCk_times_nCk(n1, k1, n2, k2)

            vr = self.verifier.verify_nCk_times_nCk(n1, k1, n2, k2, answer)
            if not vr.ok:
                return Stage5Response(
                    ok=False,
                    answer=None,
                    text="",
                    guard_code=vr.guard_code,
                    guard_state=vr.guard_state,
                    guard_action=vr.guard_action,
                    route=decision.route.value,
                    reason=vr.reason,
                )

            explained = self.explainer.explain_nCk_times_nCk(n1, k1, n2, k2, answer)
            return Stage5Response(ok=True, answer=answer, text=explained.text, route=decision.route.value)

        # PATTERNABLE -> Stage-3 extract then Stage-0 compute
        raw = problem_data.get("raw", "")
        extracted = self.extractor.extract(raw)
        if extracted is None:
            return Stage5Response(
                ok=False,
                text="",
                guard_code="EXTRACT_FAIL",
                guard_state="EXTRACT_FAIL",
                guard_action="STOP",
                route=decision.route.value,
                reason="Deterministic extraction failed.",
            )

        answer = self._compute_stage0_nCk_times_nCk(extracted.n1, extracted.k1, extracted.n2, extracted.k2)
        vr = self.verifier.verify_nCk_times_nCk(extracted.n1, extracted.k1, extracted.n2, extracted.k2, answer)
        if not vr.ok:
            return Stage5Response(
                ok=False,
                answer=None,
                text="",
                guard_code=vr.guard_code,
                guard_state=vr.guard_state,
                guard_action=vr.guard_action,
                route=decision.route.value,
                reason=vr.reason,
            )

        explained = self.explainer.explain_nCk_times_nCk(extracted.n1, extracted.k1, extracted.n2, extracted.k2, answer)
        return Stage5Response(ok=True, answer=answer, text=explained.text, route=decision.route.value)

    def _compute_stage0_nCk_times_nCk(self, n1: int, k1: int, n2: int, k2: int) -> int:
        # Pure computation (Stage-0 equivalent)
        from math import comb
        return comb(n1, k1) * comb(n2, k2)
