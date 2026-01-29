from src.app.retrieval.rag_chain import rag_chain

def main():
    questions = [
        "How many annual leaves can I take?",
        "What is work from home policy?",
        "Who is the CEO of this company?",
        "What is the sick leave policy?"
    ]
    
    for question in questions:
        print(f"\n{'='*60}")
        print(f"❓ Question: {question}")
        print('='*60)
        
        result = rag_chain.query(question)
        
        print(f"\n💬 Answer: {result.answer}")
        
        print(f"\n📊 Guardrail Results:")
        print(f"   Confidence: {result.confidence_level}")
        print(f"   Citations Valid: {result.citations_valid}")
        print(f"   Grounded: {result.is_grounded}")
        print(f"   Should Answer: {result.should_answer}")
        
        if result.warnings:
            print(f"\n⚠️ Warnings:")
            for w in result.warnings:
                print(f"   {w}")
        
        if result.sources:
            print(f"\n📚 Sources:")
            for s in result.sources:
                print(f"   [{s['id']}] {s['source']} (score: {s['score']})")
        
        if result.latency:
            print(f"\n⚡ Latency: {result.latency}s")

if __name__ == "__main__":
    main()