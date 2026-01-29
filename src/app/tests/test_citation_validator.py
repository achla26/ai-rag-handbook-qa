from src.app.guardrails.citation_validator import citation_validator

def main():
    # Test Case 1: Valid citations
    print("Test 1: Valid Citations")
    print("-" * 40)
    answer1 = "You get 24 days of leave [Source 1]. WFH is allowed 2 days [Source 2]."
    sources1 = [{"id": 1, "source": "policy.md"}, {"id": 2, "source": "policy.md"}]
    
    result1 = citation_validator.validate(answer1, sources1)
    print(f"Answer: {answer1}")
    print(f"Result: {result1.details}")
    print(f"Valid: {result1.is_valid}")
    
    # Test Case 2: Invalid citation
    print("\nTest 2: Invalid Citation")
    print("-" * 40)
    answer2 = "The CEO is John [Source 5]."  # Source 5 doesn't exist
    sources2 = [{"id": 1, "source": "policy.md"}]
    
    result2 = citation_validator.validate(answer2, sources2)
    print(f"Answer: {answer2}")
    print(f"Result: {result2.details}")
    print(f"Valid: {result2.is_valid}")
    
    # Test Case 3: No citations
    print("\nTest 3: No Citations")
    print("-" * 40)
    answer3 = "You get 24 days of leave."  # No citation
    sources3 = [{"id": 1, "source": "policy.md"}]
    
    result3 = citation_validator.validate(answer3, sources3)
    print(f"Answer: {answer3}")
    print(f"Result: {result3.details}")
    print(f"Valid: {result3.is_valid}")

if __name__ == "__main__":
    main()