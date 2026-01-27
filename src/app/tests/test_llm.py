from src.app.core.llm import llm_client
from src.utils.logger import logger 

def main():
    # Health check
    logger.info("Health Check...")
    health = llm_client.health_check()
    logger.info(f"Status: {health}")

    if health["status"] != "healthy":
        logger.error("LLM not working!")
        return

    # Simple generation
    logger.info("\n Simple Generation...")

    response = llm_client.generate(
        prompt="What is RAG in AI? Answer in 2 lines.",
        system_prompt="You are a helpful AI assistant."
    )

    print(f"Response: {response['content']}")
    print(f"Tokens used: {response['usage']}")
    print(f"Latency: {response['latency_seconds']}s")

    # Streaming test
    print("\n Streaming Test...")
    print("Response: ", end="")

    for chunk in llm_client.generate_stream("Count 1 to 5"):
        print(chunk, end="", flush=True)
    print("\nDone!")

if __name__ == "__main__":
    main()