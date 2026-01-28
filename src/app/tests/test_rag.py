from src.app.retrieval.rag_chain import rag_chain

def main():
    questions = [
        "How many annual leaves can I take?",
        "What is the work from home policy?",
        "Who is the CEO of the company?"  # Should say "I don't know"
    ]
    
    for question in questions:
        print(f"\n❓ Question: {question}")
        print("=" * 60)
        
        result = rag_chain.query(question)
        
        print(f" Answer: {result['answer']}")
        print(f"\n Sources used:")
        for src in result["sources"]:
            print(f"   [{src['id']}] {src['source']} (score: {src['score']})")
        
        if result.get("latency"):
            print(f"\n⚡ Latency: {result['latency']}s")

if __name__ == "__main__":
    main()

 