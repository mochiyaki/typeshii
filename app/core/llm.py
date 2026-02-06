"""
LLM Client - Abstraction layer for Grok (xAI) API.
Designed for easy provider swapping if needed.
"""
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import get_settings

settings = get_settings()


class LLMClient:
    """Async LLM client for Grok API with OpenAI-compatible interface."""
    
    def __init__(self):
        self.api_key = settings.grok_api_key
        self.base_url = settings.grok_base_url
        self.model = settings.grok_model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Send a chat completion request to Grok API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt to prepend
            
        Returns:
            The assistant's response text
        """
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def structured_output(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.3,
    ) -> str:
        """
        Get structured output for agent tasks.
        Uses lower temperature for more consistent output.
        """
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=4096,
        )


# Singleton instance
llm_client = LLMClient()


def get_llm_client() -> LLMClient:
    """Get LLM client instance for dependency injection."""
    return llm_client
