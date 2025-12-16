# stage5/pipeline.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Union, List, Tuple

from .gate import GateRoute, Stage5Gate
from .extractor import Stage5Extractor, Extracted
from .solver import Stage5Solver
from .verifier import Stage5Verifier
from .explainer import Stage5Explainer


@dataclass(frozen=True)
class Stage5Response:
    ok: bool
    answer: Optional[Union[int, float, str]] = None
    text: str = ""
    guard_code: Optional[str] = None
    guard_state: Optional[str] = None
    guard_action: Optional[str] = None
    route: Optional[str] = None
    reason: Optional[str] = None


class Stage5Pipeline:
    """
    Deterministic pipeline for 6 math problem patterns.
    - No loops
    - No LLM calls
    - STOP is a state (guard_code propagates)
    """

    def __init__(self) -> None:
        self.gate = Stage5Gate()
        self.extractor = Stage5Extractor()
        self.solver = Stage5Solver()
        self.verifier = Stage5Verifier()
        self.explainer = Stage5Explainer()

    def solve(self, problem_data: Dict[str, Any]) -> Stage5Response:
        """
        Main entry point. Supports:
        1. STRUCTURED path: pre-extracted fields (legacy)
        2. PATTERNABLE path: raw text extraction

        Returns Stage5Response with answer or STOP guard.
        """
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

        # STRUCTURED path (legacy nCk_times_nCk format)
        if decision.route == GateRoute.STRUCTURED:
            return self._handle_structured(problem_data, decision)

        # PATTERNABLE path (raw text → extract → solve)
        return self._handle_patternable(problem_data, decision)

    def _handle_structured(
        self,
        problem_data: Dict[str, Any],
        decision
    ) -> Stage5Response:
        """Handle pre-structured input (legacy)"""
        kind = problem_data.get("kind")
        if kind != "nCk_times_nCk":
            return Stage5Response(
                ok=False,
                text="",
                guard_code="UNSUPPORTED_KIND",
                guard_state="UNSUPPORTED_KIND",
                guard_action="STOP",
                route=decision.route.value,
                reason=f"Unsupported structured kind: {kind}",
            )

        # Legacy compute for nCk_times_nCk
        from math import comb
        n1, k1, n2, k2 = problem_data["n1"], problem_data["k1"], problem_data["n2"], problem_data["k2"]
        answer = comb(n1, k1) * comb(n2, k2)

        # Verification not needed for STRUCTURED path (trusted input)
        text = f"Structured compute: C({n1},{k1}) × C({n2},{k2}) = {answer}"
        return Stage5Response(ok=True, answer=answer, text=text, route=decision.route.value)

    def _handle_patternable(
        self,
        problem_data: Dict[str, Any],
        decision
    ) -> Stage5Response:
        """Handle raw text extraction and solving"""
        # Get raw text
        raw = None
        for key in ("raw", "problem", "text"):
            val = problem_data.get(key)
            if isinstance(val, str) and val.strip():
                raw = val
                break

        if raw is None:
            return Stage5Response(
                ok=False,
                text="",
                guard_code="NO_RAW_TEXT",
                guard_state="NO_RAW_TEXT",
                guard_action="STOP",
                route=decision.route.value,
                reason="No raw text found in input",
            )

        # Extract pattern
        extracted = self.extractor.extract(raw)
        if extracted is None:
            return Stage5Response(
                ok=False,
                text="",
                guard_code="EXTRACT_FAIL",
                guard_state="EXTRACT_FAIL",
                guard_action="STOP",
                route=decision.route.value,
                reason="Deterministic extraction failed - pattern not recognized",
            )

        # Solve using extracted values
        try:
            answer = self.solver.solve(extracted)
        except Exception as e:
            return Stage5Response(
                ok=False,
                text="",
                guard_code="SOLVER_ERROR",
                guard_state="SOLVER_ERROR",
                guard_action="STOP",
                route=decision.route.value,
                reason=f"Solver exception: {e!r}",
            )

        # Verify answer
        verify_result = self.verifier.verify(extracted, answer)
        if not verify_result.ok:
            return Stage5Response(
                ok=False,
                answer=None,
                text="",
                guard_code=verify_result.guard_code,
                guard_state=verify_result.guard_state,
                guard_action=verify_result.guard_action,
                route=decision.route.value,
                reason=verify_result.reason,
            )

        # Generate explanation
        explained = self.explainer.explain(extracted, answer)

        # Format answer for response
        answer_str = self._format_answer(answer)

        return Stage5Response(
            ok=True,
            answer=answer_str,
            text=explained.text,
            route=decision.route.value
        )

    def _format_answer(self, answer: Union[int, float, str, List[Tuple[str, float, float]]]) -> str:
        """Format answer for consistent output"""
        if isinstance(answer, list):
            # Calculus extrema
            parts = []
            for typ, x, f_val in answer:
                parts.append(f"{typ} at x={x:.2f} (f={f_val:.2f})")
            return ", ".join(parts)
        elif isinstance(answer, float):
            # Check if it's close to an integer
            if abs(answer - round(answer)) < 1e-9:
                return str(int(round(answer)))
            else:
                return f"{answer:.6f}".rstrip('0').rstrip('.')
        else:
            return str(answer)
