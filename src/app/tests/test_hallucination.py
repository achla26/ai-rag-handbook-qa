from src.app.guardrails.hallucination import hallucination_detector

def main():
    context = """
    All employees are entitled to 24 days of annual leave per year.
    Employees can work from home up to 2 days per week.
    Medical certificate required for leave exceeding 2 days.
    """
    
    # Test 1: Grounded answer
    print("Test 1: Grounded Answer")
    print("-" * 40)
    answer1 = "You get 24 days of annual leave [Source 1]. WFH is allowed 2 days per week [Source 1]."
    
    result1 = hallucination_detector.check(answer1, context)
    print(f"Answer: {answer1}")
    print(f"Grounded: {result1.is_grounded}")
    print(f"Score: {result1.groundedness_score}")
    print(f"Details: {result1.details}")
    
    # Test 2: Hallucinated answer
    print("\nTest 2: Hallucinated Answer")
    print("-" * 40)
    answer2 = "You get 24 days leave [Source 1]. The CEO gives bonus every month. Salary is 10 LPA."
    
    result2 = hallucination_detector.check(answer2, context)
    print(f"Answer: {answer2}")
    print(f"Grounded: {result2.is_grounded}")
    print(f"Score: {result2.groundedness_score}")
    print(f"Details: {result2.details}")
    
    if result2.flagged_sentences:
        print(f"Flagged:")
        for s in result2.flagged_sentences:
            print(f"   ❌ {s}")
    
    # Test 3: Refusal answer
    print("\nTest 3: Refusal Answer")
    print("-" * 40)
    answer3 = "I don't have enough information to answer this question."
    
    result3 = hallucination_detector.check(answer3, context)
    print(f"Answer: {answer3}")
    print(f"Details: {result3.details}")

if __name__ == "__main__":
    main()
    