# stage5/explainer.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Union, List, Tuple

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
class Explained:
    text: str


class Stage5Explainer:
    """
    Only for PASS results. STOP must remain silent (empty text).
    """

    def explain(
        self,
        extracted: Extracted,
        answer: Union[int, float, str, List[Tuple[str, float, float]]]
    ) -> Explained:
        """Dispatch to appropriate explainer based on pattern kind"""
        if extracted.kind == PatternKind.COMBINATORICS:
            return self._explain_combinatorics(extracted, answer)
        elif extracted.kind == PatternKind.ALGEBRA:
            return self._explain_algebra(extracted, answer)
        elif extracted.kind == PatternKind.NUMBER_THEORY:
            return self._explain_number_theory(extracted, answer)
        elif extracted.kind == PatternKind.GEOMETRY:
            return self._explain_geometry(extracted, answer)
        elif extracted.kind == PatternKind.PROBABILITY:
            return self._explain_probability(extracted, answer)
        elif extracted.kind == PatternKind.CALCULUS:
            return self._explain_calculus(extracted, answer)
        else:
            return Explained(text="")

    def _explain_combinatorics(self, ex: CombinatoricsExtracted, answer: int) -> Explained:
        """Explain combinatorics solution"""
        case_explanations = []
        for k1, k2 in ex.cases:
            from math import comb
            val = comb(ex.n1, k1) * comb(ex.n2, k2)
            case_explanations.append(f"  Case ({k1} men, {k2} women): C({ex.n1},{k1}) × C({ex.n2},{k2}) = {val}")

        text = "Combinatorics (Committee Selection):\n"
        text += "\n".join(case_explanations)
        text += f"\nTotal = {answer}"
        return Explained(text=text)

    def _explain_algebra(self, ex: AlgebraExtracted, answer: int) -> Explained:
        """Explain algebra solution"""
        text = f"Algebra:\n"
        text += f"  Given: x² + y² = {ex.x2_plus_y2}, xy = {ex.xy}\n"
        text += f"  Formula: (x + y)² = x² + 2xy + y²\n"
        text += f"  (x + y)² = {ex.x2_plus_y2} + 2×{ex.xy} = {answer}"
        return Explained(text=text)

    def _explain_number_theory(self, ex: NumberTheoryExtracted, answer: int) -> Explained:
        """Explain number theory solution"""
        text = f"Number Theory (Divisor Sum):\n"
        text += f"  Number: {ex.number}\n"
        text += f"  Sum of all divisors: σ({ex.number}) = {answer}"
        return Explained(text=text)

    def _explain_geometry(self, ex: GeometryExtracted, answer: float) -> Explained:
        """Explain geometry solution"""
        text = f"Geometry (Pythagorean Theorem):\n"
        text += f"  Radius: {ex.radius}, Tangent: {ex.tangent}\n"
        text += f"  OP² = {ex.radius}² + {ex.tangent}² = {ex.radius**2} + {ex.tangent**2}\n"
        text += f"  OP = √{ex.radius**2 + ex.tangent**2} = {answer}"
        return Explained(text=text)

    def _explain_probability(self, ex: ProbabilityExtracted, answer: float) -> Explained:
        """Explain probability solution"""
        total = 6 ** ex.num_dice
        favorable = int(answer * total)
        text = f"Probability (Dice Sum):\n"
        text += f"  {ex.num_dice} dice, target sum = {ex.target_sum}\n"
        text += f"  Favorable outcomes: {favorable}\n"
        text += f"  Total outcomes: {total}\n"
        text += f"  Probability: {favorable}/{total} = {answer:.6f}"
        return Explained(text=text)

    def _explain_calculus(
        self,
        ex: CalculusExtracted,
        answer: List[Tuple[str, float, float]]
    ) -> Explained:
        """Explain calculus solution"""
        a, b, c, d = ex.coefficients
        text = f"Calculus (Local Extrema):\n"
        text += f"  f(x) = {a}x³ + {b}x² + {c}x + {d}\n"
        text += f"  f'(x) = {3*a}x² + {2*b}x + {c}\n"
        text += f"  Critical points found:\n"

        for typ, x, f_val in answer:
            text += f"    {typ.capitalize()} at x={x:.2f}, f(x)={f_val:.2f}\n"

        return Explained(text=text)
