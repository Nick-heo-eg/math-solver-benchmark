# stage5/extractor.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict
from enum import Enum


class PatternKind(str, Enum):
    COMBINATORICS = "combinatorics"
    ALGEBRA = "algebra"
    NUMBER_THEORY = "number_theory"
    GEOMETRY = "geometry"
    PROBABILITY = "probability"
    CALCULUS = "calculus"


@dataclass(frozen=True)
class Extracted:
    """Base class for all extracted patterns"""
    kind: PatternKind


@dataclass(frozen=True)
class CombinatoricsExtracted(Extracted):
    n1: int
    k1: int
    n2: int
    k2: int
    cases: List[Tuple[int, int]]


@dataclass(frozen=True)
class AlgebraExtracted(Extracted):
    x2_plus_y2: int
    xy: int


@dataclass(frozen=True)
class NumberTheoryExtracted(Extracted):
    number: int


@dataclass(frozen=True)
class GeometryExtracted(Extracted):
    radius: float
    tangent: float


@dataclass(frozen=True)
class ProbabilityExtracted(Extracted):
    num_dice: int
    target_sum: int


@dataclass(frozen=True)
class CalculusExtracted(Extracted):
    coefficients: List[float]  # [a_n, a_(n-1), ..., a_1, a_0]


class Stage5Extractor:
    """
    Deterministic pattern extraction only.
    No reasoning, no guessing, only regex/DFA rules.
    """

    def extract(self, raw: str) -> Optional[Extracted]:
        """Try all patterns in order, return first match"""
        # Order matters: more specific patterns first
        patterns = [
            self._try_combinatorics,
            self._try_algebra,
            self._try_number_theory,
            self._try_geometry,
            self._try_probability,
            self._try_calculus,
        ]

        for pattern_fn in patterns:
            result = pattern_fn(raw)
            if result is not None:
                return result

        return None

    def _try_combinatorics(self, raw: str) -> Optional[CombinatoricsExtracted]:
        """
        Pattern: "A committee of 5 people from 6 men and 4 women.
                  Must contain at least 3 men and at least 1 woman."

        Extracts: n1=6, n2=4, committee_size=5, min_men=3, min_women=1
        Cases: [(3,2), (4,1)]
        """
        s = raw.lower()

        # Must have committee/choose keywords AND men/women
        if not (("committee" in s or "choose" in s or "ways" in s) and
                ("men" in s and "women" in s)):
            return None

        # Extract numbers: "6 men", "4 women", "committee of 5", "3 men", "1 woman"
        m = re.search(r"(\d+)\s+men.*?(\d+)\s+women", s)
        if not m:
            return None

        total_men = int(m.group(1))
        total_women = int(m.group(2))

        # Committee size
        size_match = re.search(r"committee\s+of\s+(\d+)|(\d+)\s+people", s)
        if not size_match:
            return None
        committee_size = int(size_match.group(1) or size_match.group(2))

        # Constraints: "at least 3 men", "at least 1 woman"
        min_men_match = re.search(r"at\s+least\s+(\d+)\s+men", s)
        min_women_match = re.search(r"at\s+least\s+(\d+)\s+wom[ae]n", s)

        if not (min_men_match and min_women_match):
            return None

        min_men = int(min_men_match.group(1))
        min_women = int(min_women_match.group(1))

        # Generate valid cases
        cases = []
        for num_men in range(min_men, min(total_men, committee_size) + 1):
            num_women = committee_size - num_men
            if min_women <= num_women <= total_women:
                cases.append((num_men, num_women))

        if not cases:
            return None

        return CombinatoricsExtracted(
            kind=PatternKind.COMBINATORICS,
            n1=total_men,
            k1=0,  # placeholder, actual values in cases
            n2=total_women,
            k2=0,  # placeholder
            cases=cases
        )

    def _try_algebra(self, raw: str) -> Optional[AlgebraExtracted]:
        """
        Pattern: "If x^2 + y^2 = 25 and xy = 12, find (x + y)^2"

        Extracts: x2_plus_y2=25, xy=12
        """
        s = raw.lower()

        # Must mention x^2 + y^2 and xy
        if not ("x^2" in s or "x²" in s or "x**2" in s):
            return None
        if "xy" not in s and "x*y" not in s:
            return None

        # Extract x^2 + y^2 = value
        x2_y2_match = re.search(r"(?:x\^2|x²|x\*\*2)\s*\+\s*(?:y\^2|y²|y\*\*2)\s*=\s*(\d+)", s)
        if not x2_y2_match:
            return None
        x2_plus_y2 = int(x2_y2_match.group(1))

        # Extract xy = value
        xy_match = re.search(r"xy\s*=\s*(\d+)|x\s*\*\s*y\s*=\s*(\d+)", s)
        if not xy_match:
            return None
        xy = int(xy_match.group(1) or xy_match.group(2))

        # Must ask for (x + y)^2
        if "(x + y)^2" not in s and "(x+y)^2" not in s and "(x + y)²" not in s:
            return None

        return AlgebraExtracted(
            kind=PatternKind.ALGEBRA,
            x2_plus_y2=x2_plus_y2,
            xy=xy
        )

    def _try_number_theory(self, raw: str) -> Optional[NumberTheoryExtracted]:
        """
        Pattern: "Find the sum of all positive divisors of 360"

        Extracts: number=360
        """
        s = raw.lower()

        # Must mention divisors/factors and sum
        if not (("divisor" in s or "factor" in s) and "sum" in s):
            return None

        # Extract number
        num_match = re.search(r"divisors?\s+of\s+(\d+)|factors?\s+of\s+(\d+)", s)
        if not num_match:
            return None

        number = int(num_match.group(1) or num_match.group(2))

        return NumberTheoryExtracted(
            kind=PatternKind.NUMBER_THEORY,
            number=number
        )

    def _try_geometry(self, raw: str) -> Optional[GeometryExtracted]:
        """
        Pattern: "Circle with radius 10, tangent from P has length 24. Find distance OP."

        Extracts: radius=10, tangent=24
        """
        s = raw.lower()

        # Must mention circle, radius, and tangent
        if not ("circle" in s and "radius" in s and "tangent" in s):
            return None

        # Extract radius
        radius_match = re.search(r"radius\s+(?:is\s+)?(\d+)", s)
        if not radius_match:
            return None
        radius = float(radius_match.group(1))

        # Extract tangent length
        tangent_match = re.search(r"tangent.*?(?:length\s+)?(?:is\s+)?(\d+)", s)
        if not tangent_match:
            return None
        tangent = float(tangent_match.group(1))

        return GeometryExtracted(
            kind=PatternKind.GEOMETRY,
            radius=radius,
            tangent=tangent
        )

    def _try_probability(self, raw: str) -> Optional[ProbabilityExtracted]:
        """
        Pattern: "Three dice are rolled. Probability that sum is exactly 10?"

        Extracts: num_dice=3, target_sum=10
        """
        s = raw.lower()

        # Must mention dice and probability/sum
        if not ("dice" in s or "die" in s):
            return None

        # Extract number of dice
        num_dice_match = re.search(r"(one|two|three|four|five|six|1|2|3|4|5|6)\s+dic[e]", s)
        if not num_dice_match:
            return None

        word_to_num = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
        dice_str = num_dice_match.group(1)
        num_dice = word_to_num.get(dice_str, int(dice_str) if dice_str.isdigit() else None)

        if num_dice is None:
            return None

        # Extract target sum
        sum_match = re.search(r"sum\s+(?:is\s+)?(?:exactly\s+)?(\d+)", s)
        if not sum_match:
            return None
        target_sum = int(sum_match.group(1))

        return ProbabilityExtracted(
            kind=PatternKind.PROBABILITY,
            num_dice=num_dice,
            target_sum=target_sum
        )

    def _try_calculus(self, raw: str) -> Optional[CalculusExtracted]:
        """
        Pattern: "f(x) = x^3 - 6x^2 + 9x + 1, find local extrema"

        Extracts: coefficients=[1, -6, 9, 1]
        """
        s = raw.lower()

        # Must mention f(x) and extrema/maximum/minimum
        if "f(x)" not in s:
            return None
        if not ("extrem" in s or "maximum" in s or "minimum" in s):
            return None

        # Extract polynomial: f(x) = ax^3 + bx^2 + cx + d
        # Simplified: only cubic for now
        poly_match = re.search(
            r"f\(x\)\s*=\s*([+-]?\d*)\s*x\^3\s*([+-]\s*\d+)\s*x\^2\s*([+-]\s*\d+)\s*x\s*([+-]\s*\d+)",
            s.replace(" ", "")
        )

        if not poly_match:
            return None

        # Parse coefficients
        a_str = poly_match.group(1) or "1"
        a = int(a_str) if a_str not in ("", "+", "-") else (1 if a_str != "-" else -1)

        b = int(poly_match.group(2).replace(" ", ""))
        c = int(poly_match.group(3).replace(" ", ""))
        d = int(poly_match.group(4).replace(" ", ""))

        return CalculusExtracted(
            kind=PatternKind.CALCULUS,
            coefficients=[float(a), float(b), float(c), float(d)]
        )
