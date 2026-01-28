from src.app.retrieval.retriever import retriever

def main():
    # Test queries
    queries = [
        "How many annual leaves can I take?",
        "What is work from home policy?",
        "Tell me about sick leave"
    ]
    
    for query in queries:
        print(f"\n Query: {query}")
        print("-" * 50)
        
        result = retriever.retrieve_with_context(query, top_k=3)
        
        if result["sources"]:
            for src in result["sources"]:
                print(f"Source {src['id']}: {src['source']} (score: {src['score']})")
        else:
            print("No relevant chunks found!")

if __name__ == "__main__":
    main()