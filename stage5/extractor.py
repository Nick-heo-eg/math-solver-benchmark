# echo_engine/stage5/extractor.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Extracted:
    """
    Parsed observation for Stage-3/Stage-0 compute.
    """
    kind: str
    n1: int
    k1: int
    n2: int
    k2: int


class Stage5Extractor:
    """
    Observation-only extractor: regex/DFA rules only.
    No reasoning, no 'guessing'.
    """

    # Example regex for: "6 men and 4 women ... committee of 5 ... 3 men and 2 women"
    _re_mw = re.compile(
        r"(?P<m>\d+)\s+men.*?(?P<w>\d+)\s+women.*?(committee|committees|group|groups)\s+of\s+(?P<size>\d+).*?"
        r"(?P<km>\d+)\s+men.*?(?P<kw>\d+)\s+women",
        re.IGNORECASE | re.DOTALL,
    )

    def extract(self, raw: str) -> Optional[Extracted]:
        m = self._re_mw.search(raw)
        if not m:
            return None

        men = int(m.group("m"))
        women = int(m.group("w"))
        km = int(m.group("km"))
        kw = int(m.group("kw"))

        # Deterministic sanity: require km+kw = committee size if provided, else just accept km/kw.
        size = int(m.group("size"))
        if km + kw != size:
            return None

        return Extracted(kind="nCk_times_nCk", n1=men, k1=km, n2=women, k2=kw)
