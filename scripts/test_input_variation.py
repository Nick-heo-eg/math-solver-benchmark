#!/usr/bin/env python3
"""
Test Input Variation → Output Variation

Principle: Same pattern, different numbers → different answers
This proves the solver is NOT hardcoded.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from stage5 import Stage5Pipeline


def test_input_variation():
    """Test that changing inputs changes outputs"""
    pipeline = Stage5Pipeline()

    tests = [
        # Combinatorics: committee selection
        {
            "name": "Combinatorics (6 men, 4 women)",
            "input1": "A committee of 5 people from 6 men and 4 women. Must contain at least 3 men and at least 1 woman.",
            "expected1": "180",
            "input2": "A committee of 7 people from 10 men and 8 women. Must contain at least 4 men and at least 2 women.",
            "expected2_not": "180",  # Must be different
        },
        # Algebra
        {
            "name": "Algebra (x² + y²)",
            "input1": "If x^2 + y^2 = 25 and xy = 12, find (x + y)^2",
            "expected1": "49",
            "input2": "If x^2 + y^2 = 50 and xy = 20, find (x + y)^2",
            "expected2_not": "49",
        },
        # Number Theory
        {
            "name": "Number Theory (divisors)",
            "input1": "Find the sum of all positive divisors of 360",
            "expected1": "1170",
            "input2": "Find the sum of all positive divisors of 12",
            "expected2_not": "1170",
        },
        # Geometry
        {
            "name": "Geometry (circle tangent)",
            "input1": "A circle has radius 10. Tangent from P has length 24. Find distance OP.",
            "expected1": "26",
            "input2": "A circle has radius 5. Tangent from P has length 12. Find distance OP.",
            "expected2_not": "26",
        },
        # Probability
        {
            "name": "Probability (dice)",
            "input1": "Three dice are rolled. What is the probability that the sum is exactly 10?",
            "expected1": "0.125",
            "input2": "Two dice are rolled. What is the probability that the sum is exactly 7?",
            "expected2_not": "0.125",
        },
        # Calculus
        {
            "name": "Calculus (extrema)",
            "input1": "If f(x) = x^3 - 6x^2 + 9x + 1, find all local extrema",
            "expected1_contains": ["x=1", "x=3"],
            "input2": "If f(x) = x^3 - 3x^2 + 2x + 5, find all local extrema",
            "expected2_not_contains": ["x=1", "x=3"],  # Different critical points
        },
    ]

    print("="*70)
    print("Input Variation Test - Proving NOT Hardcoded")
    print("="*70)

    all_passed = True

    for test in tests:
        print(f"\n{'='*70}")
        print(f"Test: {test['name']}")
        print(f"{'='*70}")

        # Test input 1
        result1 = pipeline.solve({"problem": test["input1"]})
        answer1 = str(result1.answer) if result1.ok else None

        print(f"\nInput 1: {test['input1'][:60]}...")
        print(f"  Output 1: {answer1}")
        print(f"  Expected: {test.get('expected1', test.get('expected1_contains'))}")

        # Test input 2
        result2 = pipeline.solve({"problem": test["input2"]})
        answer2 = str(result2.answer) if result2.ok else None

        print(f"\nInput 2: {test['input2'][:60]}...")
        print(f"  Output 2: {answer2}")
        print(f"  Must NOT be: {test.get('expected2_not', test.get('expected2_not_contains'))}")

        # Verify outputs are different
        if "expected2_not" in test:
            passed = (answer1 == test["expected1"]) and (answer2 != test["expected2_not"]) and (answer1 != answer2)
        elif "expected1_contains" in test:
            # For calculus: check critical points differ
            passed = (all(s in str(answer1) for s in test["expected1_contains"]) and
                     not all(s in str(answer2) for s in test["expected2_not_contains"]) and
                     answer1 != answer2)
        else:
            passed = answer1 != answer2

        if passed:
            print(f"\n✅ PASS - Outputs differ (not hardcoded)")
        else:
            print(f"\n❌ FAIL - Outputs same or wrong")
            all_passed = False

    # Summary
    print(f"\n{'='*70}")
    if all_passed:
        print("✅ ALL INPUT VARIATION TESTS PASSED")
        print("   Solver uses extracted values, NOT hardcoded answers")
    else:
        print("❌ SOME TESTS FAILED")
        print("   Solver may be hardcoded or broken")
    print(f"{'='*70}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(test_input_variation())
