# echo_engine/stage5/explainer.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Explained:
    text: str


class Stage5Explainer:
    """
    Only for PASS results. STOP must remain silent (empty text).
    """

    def explain_nCk_times_nCk(self, n1: int, k1: int, n2: int, k2: int, answer: int) -> Explained:
        return Explained(
            text=(
                f"Choose {k1} from {n1} and {k2} from {n2}, independently.\n"
                f"Total ways = C({n1},{k1}) × C({n2},{k2}) = {answer}."
            )
        )
