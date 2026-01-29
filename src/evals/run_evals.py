import json
import time
from typing import Dict, List, Any
from dataclasses import dataclass
import sys
sys.path.append(".")

from src.app.retrieval.rag_chain import rag_chain
from src.utils.logger import logger

@dataclass
class EvalResult:
    """Single evaluation result."""
    test_id: int
    question: str
    expected: str
    actual: str
    passed: bool
    has_citation: bool
    confidence: str
    latency: float


def load_test_cases(path: str = "src/evals/test_cases.json") -> List[Dict]:
    """Load test cases from JSON."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(e)


def check_answer(expected: str, actual: str) -> bool:
    """Check if expected answer is in actual response."""
    expected_lower = expected.lower()
    actual_lower = actual.lower()
    
    # Abstain test
    if expected_lower == "not_found":
        abstain_phrases = [
            "don't have enough information",
            "i don't know",
            "cannot answer",
            "no information"
        ]
        return any(phrase in actual_lower for phrase in abstain_phrases)
    
    # Check each key word present
    key_words = expected_lower.replace(",", "").split()
    matches = sum(1 for word in key_words if word in actual_lower)
    
    # 70% words match = pass
    return matches >= len(key_words) * 0.7


def run_evaluation() -> Dict[str, Any]:
    """Run all test cases and compute metrics."""
    
    test_cases = load_test_cases()
    results: List[EvalResult] = []
    
    print("🧪 Running Evaluations...")
    print("=" * 60)
    
    total_latency = 0
    
    for tc in test_cases:
        start = time.time()
        response = rag_chain.query(tc["question"])
        latency = time.time() - start
        total_latency += latency
        
        passed = check_answer(tc["expected_answer"], response.answer)
        has_citation = "[Source" in response.answer or not response.should_answer
        
        result = EvalResult(
            test_id=tc["id"],
            question=tc["question"],
            expected=tc["expected_answer"],
            actual=response.answer[:100] + "..." if len(response.answer) > 100 else response.answer,
            passed=passed,
            has_citation=has_citation,
            confidence=response.confidence_level,
            latency=round(latency, 3)
        )
        results.append(result)
        
        status = "✅" if passed else "❌"
        print(f"{status} Test {tc['id']}: {tc['question'][:40]}...")
    
    # Compute metrics
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    cited = sum(1 for r in results if r.has_citation)
    avg_latency = total_latency / total
    
    metrics = {
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": round(passed / total * 100, 1),
        "citation_rate": round(cited / total * 100, 1),
        "avg_latency_seconds": round(avg_latency, 3),
        "p95_latency": round(sorted([r.latency for r in results])[int(total * 0.95)], 3)
    }
    
    print("\n" + "=" * 60)
    print("📊 EVALUATION RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{total} ({metrics['accuracy']}%)")
    print(f"📝 Citation Rate: {metrics['citation_rate']}%")
    print(f"⚡ Avg Latency: {metrics['avg_latency_seconds']}s")
    print(f"⚡ P95 Latency: {metrics['p95_latency']}s")
    
    # Failed tests detail
    failed_tests = [r for r in results if not r.passed]
    if failed_tests:
        print("\n❌ Failed Tests:")
        for r in failed_tests:
            print(f"   Test {r.test_id}: Expected '{r.expected}' in '{r.actual}'")
    
    return {
        "metrics": metrics,
        "results": [vars(r) for r in results]
    }


if __name__ == "__main__":
    evaluation = run_evaluation()
    
    # Save results
    with open("src/evals/results.json", "w") as f:
        json.dump(evaluation, f, indent=2)
    
    print("\n💾 Results saved to evals/results.json")