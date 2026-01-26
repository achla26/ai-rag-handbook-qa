from src.app.core.embeddings import embedding_service

def main():
    # Single text embed
    text = "What is the leave policy for employees?"
    embedding = embedding_service.embed_query(text)
    
    print(f"Text: {text}")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    
    # Similarity test
    text1 = "How many leaves can I take?"
    text2 = "What is the vacation policy?"
    text3 = "What is the office address?"
    
    sim1 = embedding_service.similarity(text1, text2)
    sim2 = embedding_service.similarity(text1, text3)
    
    print(f"\n Similarity Tests:")
    print(f"'{text1}' vs '{text2}' = {sim1:.4f}")  # Should be HIGH
    print(f"'{text1}' vs '{text3}' = {sim2:.4f}")  # Should be LOW

if __name__ == "__main__":
    main()