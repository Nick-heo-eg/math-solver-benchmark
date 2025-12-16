#!/usr/bin/env python3
"""
Classifier Validation Test: 20 Diverse Math Problems

Tests the ProblemClassifier with:
1. Problems similar to benchmark (should work)
2. Edge cases (paraphrasing, multi-domain)
3. Problems outside 6 categories (should fail)
4. Adversarial cases (keyword pollution)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from run_stage3_pattern_matching import ProblemClassifier


# Test cases with expected behavior
TEST_CASES = [
    # ===== SIMILAR TO BENCHMARK (Should Work) =====
    {
        "id": "test_001",
        "problem": "How many ways can we select 3 students from a class of 10?",
        "expected": "combinatorics",
        "should_work": True,
        "reason": "Clear 'select' and 'how many ways' keywords"
    },
    {
        "id": "test_002",
        "problem": "Solve for x: x^2 - 5x + 6 = 0",
        "expected": "algebra",
        "should_work": True,
        "reason": "Contains x^2"
    },
    {
        "id": "test_003",
        "problem": "Find all prime factors of 360",
        "expected": "number_theory",
        "should_work": True,
        "reason": "Contains 'prime'"
    },
    {
        "id": "test_004",
        "problem": "A circle has radius 5. Find the distance from center to point (3,4)",
        "expected": "geometry",
        "should_work": True,
        "reason": "Contains 'circle', 'radius', 'distance'"
    },
    {
        "id": "test_005",
        "problem": "What is the probability of rolling a sum of 7 with two dice?",
        "expected": "probability",
        "should_work": True,
        "reason": "Contains 'probability', 'dice'"
    },
    {
        "id": "test_006",
        "problem": "Find the derivative of f(x) = x^3 + 2x",
        "expected": "calculus",
        "should_work": True,
        "reason": "Contains 'derivative', 'f(x)'"
    },

    # ===== PARAPHRASING (May Fail) =====
    {
        "id": "test_007",
        "problem": "In how many distinct arrangements can 5 books be placed on a shelf?",
        "expected": "combinatorics",
        "should_work": False,
        "reason": "Missing 'ways'/'select'/'choose' - uses 'arrangements'"
    },
    {
        "id": "test_008",
        "problem": "Count the number of 4-person teams from 12 people",
        "expected": "combinatorics",
        "should_work": False,
        "reason": "Missing keywords - uses 'count' instead of 'how many ways'"
    },

    # ===== MULTI-DOMAIN (Will Misclassify) =====
    {
        "id": "test_009",
        "problem": "What is the probability of selecting a committee with at least 2 women from 5 men and 4 women?",
        "expected": "probability+combinatorics",
        "should_work": False,
        "reason": "Both probability AND combinatorics - classifier forces single label"
    },
    {
        "id": "test_010",
        "problem": "Find the maximum area of a rectangle inscribed in a circle of radius r",
        "expected": "calculus+geometry",
        "should_work": False,
        "reason": "Optimization (calculus) of geometric object"
    },
    {
        "id": "test_011",
        "problem": "Calculate the expected value of the sum of two dice",
        "expected": "probability+algebra",
        "should_work": False,
        "reason": "Expected value (probability) involves algebraic computation"
    },

    # ===== OUTSIDE 6 CATEGORIES (Will Return Random) =====
    {
        "id": "test_012",
        "problem": "Prove that the square root of 2 is irrational",
        "expected": "UNKNOWN (proof/logic)",
        "should_work": False,
        "reason": "Number theory proof - no matching keywords"
    },
    {
        "id": "test_013",
        "problem": "Show that every tree with n vertices has n-1 edges",
        "expected": "UNKNOWN (graph theory)",
        "should_work": False,
        "reason": "Graph theory - not in 6 categories"
    },
    {
        "id": "test_014",
        "problem": "Find the determinant of the 3x3 matrix [[1,2,3],[4,5,6],[7,8,9]]",
        "expected": "UNKNOWN (linear algebra)",
        "should_work": False,
        "reason": "Linear algebra - not in 6 categories"
    },

    # ===== ADVERSARIAL (Keyword Pollution) =====
    {
        "id": "test_015",
        "problem": "A geometry student uses dice to randomly select which circle to study. If x^2 + y^2 = 25...",
        "expected": "geometry (or algebra)",
        "should_work": False,
        "reason": "Contains 'geometry', 'dice', 'circle', 'x^2', 'y^2' - keyword pollution"
    },
    {
        "id": "test_016",
        "problem": "In a probability class, students choose committees. Find the derivative of the function f(x) = x^2",
        "expected": "calculus",
        "should_work": False,
        "reason": "Contains probability, choose, derivative, f(x), x^2 - massive pollution"
    },

    # ===== AMBIGUOUS WORDING =====
    {
        "id": "test_017",
        "problem": "If a circle has equation x^2 + y^2 = 16, what is its radius?",
        "expected": "geometry",
        "should_work": False,
        "reason": "Both 'circle' (geometry) and 'x^2 + y^2' (algebra)"
    },
    {
        "id": "test_018",
        "problem": "A prime number p satisfies p^2 < 100. List all such primes.",
        "expected": "number_theory",
        "should_work": True,
        "reason": "Contains 'prime' - but also has p^2 which might match algebra pattern"
    },

    # ===== CORRECT BUT DIFFERENT NOTATION =====
    {
        "id": "test_019",
        "problem": "Find f'(x) where f(x) = sin(x)",
        "expected": "calculus",
        "should_work": False,
        "reason": "Uses f'(x) instead of 'derivative' - pattern might miss"
    },
    {
        "id": "test_020",
        "problem": "Compute C(10,3)",
        "expected": "combinatorics",
        "should_work": False,
        "reason": "Uses notation C(n,k) instead of words - no keyword match"
    },
]


def run_validation():
    classifier = ProblemClassifier()

    results = {
        "total": len(TEST_CASES),
        "correct": 0,
        "expected_failures": 0,
        "unexpected_failures": 0,
        "unexpected_successes": 0,
        "details": []
    }

    print("=" * 80)
    print("CLASSIFIER VALIDATION TEST")
    print("=" * 80)
    print(f"Testing {len(TEST_CASES)} diverse math problems\n")

    for i, test in enumerate(TEST_CASES, 1):
        problem_text = test["problem"]
        expected = test["expected"]
        should_work = test["should_work"]

        # Classify
        classification_result = classifier.classify(problem_text)
        result = classification_result['category'] if classification_result['category'] else 'UNKNOWN'
        confidence = classification_result['confidence']

        # Check correctness
        is_correct = expected in result or result in expected

        # Categorize result
        if should_work and is_correct:
            status = "✓ PASS (Expected Success)"
            results["correct"] += 1
        elif should_work and not is_correct:
            status = "✗ FAIL (Unexpected Failure)"
            results["unexpected_failures"] += 1
        elif not should_work and not is_correct:
            status = "○ EXPECTED FAIL"
            results["expected_failures"] += 1
        else:  # not should_work and is_correct
            status = "◉ UNEXPECTED SUCCESS"
            results["unexpected_successes"] += 1

        # Store details
        results["details"].append({
            "id": test["id"],
            "result": result,
            "expected": expected,
            "status": status,
            "reason": test["reason"]
        })

        # Print
        print(f"[{i:02d}/{len(TEST_CASES)}] {test['id']}")
        print(f"  Problem: {problem_text[:60]}...")
        print(f"  Expected: {expected}")
        print(f"  Got: {result} (confidence: {confidence})")
        if classification_result['is_tie']:
            print(f"  Warning: Tie detected among categories")
        print(f"  Status: {status}")
        print(f"  Reason: {test['reason']}")
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {results['total']}")
    print(f"Expected Successes: {results['correct']}/{sum(1 for t in TEST_CASES if t['should_work'])}")
    print(f"Expected Failures: {results['expected_failures']}/{sum(1 for t in TEST_CASES if not t['should_work'])}")
    print(f"Unexpected Failures: {results['unexpected_failures']} ⚠️")
    print(f"Unexpected Successes: {results['unexpected_successes']}")
    print()

    # Detailed failure analysis
    if results["unexpected_failures"] > 0:
        print("=" * 80)
        print("UNEXPECTED FAILURES (Should work but didn't)")
        print("=" * 80)
        for detail in results["details"]:
            if "Unexpected Failure" in detail["status"]:
                print(f"{detail['id']}: Expected {detail['expected']}, got {detail['result']}")
                print(f"  Reason: {detail['reason']}")
                print()

    # Analysis of expected failures
    print("=" * 80)
    print("EXPECTED FAILURE ANALYSIS")
    print("=" * 80)
    print("These are limitations we already know about:")
    print()

    categories = {
        "Paraphrasing": [],
        "Multi-domain": [],
        "Outside categories": [],
        "Adversarial": [],
        "Notation": []
    }

    for detail in results["details"]:
        if "EXPECTED FAIL" in detail["status"]:
            if "paraphras" in detail["reason"].lower() or "missing" in detail["reason"].lower():
                categories["Paraphrasing"].append(detail)
            elif "both" in detail["reason"].lower() or "and" in detail["reason"].lower():
                categories["Multi-domain"].append(detail)
            elif "unknown" in detail["expected"].lower() or "not in 6" in detail["reason"].lower():
                categories["Outside categories"].append(detail)
            elif "pollution" in detail["reason"].lower():
                categories["Adversarial"].append(detail)
            elif "notation" in detail["reason"].lower() or "uses" in detail["reason"].lower():
                categories["Notation"].append(detail)

    for cat_name, items in categories.items():
        if items:
            print(f"\n{cat_name} ({len(items)} cases):")
            for item in items:
                print(f"  - {item['id']}: {item['reason']}")

    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)

    accuracy_on_designed = results['correct'] / sum(1 for t in TEST_CASES if t['should_work']) * 100
    print(f"Accuracy on problems it was designed for: {accuracy_on_designed:.1f}%")

    if results["unexpected_failures"] == 0:
        print("✓ No unexpected failures - classifier behaves as designed")
    else:
        print(f"⚠️ {results['unexpected_failures']} unexpected failures - classifier has bugs")

    print(f"\nExpected failure rate: {results['expected_failures']}/{results['total']} ({results['expected_failures']/results['total']*100:.1f}%)")
    print("This confirms the classifier is limited to specific patterns, as documented.")

    return results


if __name__ == "__main__":
    results = run_validation()
