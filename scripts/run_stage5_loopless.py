#!/usr/bin/env python3
"""
Stage-5: Loopless Universal Judgment Demo

Demonstrates deterministic Gate → Extractor → Verifier → Explainer flow
without loops, LLMs, or retries.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from stage5 import Stage5Pipeline


class Stage5Demo:
    def __init__(self) -> None:
        self.pipeline = Stage5Pipeline()

    def run_batch(self, problems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for problem in problems:
            res = self.pipeline.solve(problem)
            results.append({
                "input": problem,
                "ok": res.ok,
                "route": res.route,
                "answer": res.answer,
                "text": res.text,
                "guard_code": res.guard_code,
                "guard_state": res.guard_state,
                "guard_action": res.guard_action,
                "reason": res.reason,
            })
        return results

    def print_summary(self, results: List[Dict[str, Any]]) -> None:
        for idx, res in enumerate(results, 1):
            print(f"\n=== Problem #{idx} ===")
            print(json.dumps(res["input"], ensure_ascii=False, indent=2))
            if res["ok"]:
                print(f"Route: {res['route']} → PASS | Answer = {res['answer']}")
                print(res["text"])
            else:
                print(f"Route: {res['route']} → STOP ({res['guard_code']})")
                if res["reason"]:
                    print(f"Reason: {res['reason']}")


def _sample_problems() -> List[Dict[str, Any]]:
    structured = {"kind": "nCk_times_nCk", "n1": 6, "k1": 3, "n2": 4, "k2": 2}
    patternable = {
        "raw": "There are 6 men and 4 women. How many committees of 5 can be formed with 3 men and 2 women?"
    }
    untrusted = {"raw": "Solve it"}
    return [structured, patternable, untrusted]


if __name__ == "__main__":
    demo = Stage5Demo()
    results = demo.run_batch(_sample_problems())
    demo.print_summary(results)
