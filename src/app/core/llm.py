from groq import Groq
from typing import List, Dict, Optional, Generator 
import time

from src.config.settings import settings
from src.utils.logger import logger 


class LLMClient:
    """Groq LLM client with retry logic and streaming support."""
    
    def __init__(self):
        if settings.groq_api_key is None:
            raise ValueError("GROQ_API_KEY is required for LLM functionality")
        self.client = Groq(
            api_key=settings.groq_api_key.get_secret_value()
        )
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """generate Single response."""
        
        messages = []
                
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            latency = time.time() - start_time
            
            return {
                "content": response.choices[0].message.content,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "latency_seconds": round(latency, 3)
            }
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Streaming response for real-time UI."""
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Stream failed: {e}")
            raise
    
    def health_check(self) -> Dict:
        """Quick LLM health check."""
        try:
            response = self.generate(
                prompt="Say 'OK' only.",
                max_tokens=5
            )
            return {
                "status": "healthy",
                "model": self.model,
                "latency": response["latency_seconds"]
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Singleton
llm_client = LLMClient()