from src.app.guardrails.confidence import confidence_scorer

def main():
    # Test 1: High confidence
    print("Test 1: High Confidence")
    print("-" * 40)
    sources1 = [
        {"id": 1, "source": "policy.md", "score": 0.85},
        {"id": 2, "source": "policy.md", "score": 0.72}
    ]
    result1 = confidence_scorer.assess(sources1)
    print(f"Sources: {sources1}")
    print(f"Level: {result1.confidence_level}")
    print(f"Should Answer: {result1.should_answer}")
    print(f"Reason: {result1.reason}")
    
    # Test 2: Medium confidence
    print("\nTest 2: Medium Confidence")
    print("-" * 40)
    sources2 = [
        {"id": 1, "source": "policy.md", "score": 0.45},
        {"id": 2, "source": "policy.md", "score": 0.38}
    ]
    result2 = confidence_scorer.assess(sources2)
    print(f"Sources: {sources2}")
    print(f"Level: {result2.confidence_level}")
    print(f"Should Answer: {result2.should_answer}")
    print(f"Reason: {result2.reason}")
    
    # Test 3: Low confidence (should abstain)
    print("\nTest 3: Low Confidence (Abstain)")
    print("-" * 40)
    sources3 = [
        {"id": 1, "source": "policy.md", "score": 0.15},
        {"id": 2, "source": "policy.md", "score": 0.10}
    ]
    result3 = confidence_scorer.assess(sources3)
    print(f"Sources: {sources3}")
    print(f"Level: {result3.confidence_level}")
    print(f"Should Answer: {result3.should_answer}")
    print(f"Reason: {result3.reason}")
    
    # Test 4: No sources
    print("\nTest 4: No Sources")
    print("-" * 40)
    sources4 = []
    result4 = confidence_scorer.assess(sources4)
    print(f"Sources: {sources4}")
    print(f"Level: {result4.confidence_level}")
    print(f"Should Answer: {result4.should_answer}")
    print(f"Reason: {result4.reason}")

if __name__ == "__main__":
    main()