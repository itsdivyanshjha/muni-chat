"""OpenRouter client for LLM interactions."""

import httpx
import json
from typing import Dict, Any, List, Optional
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class OpenRouterError(Exception):
    """Exception raised when OpenRouter API calls fail."""
    pass


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.model_slug = settings.model_slug
        self.base_url = "https://openrouter.ai/api/v1"
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://municipal-ai-insights.com",
                "X-Title": "Municipal AI Insights"
            }
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Send a chat completion request to OpenRouter."""
        
        # Log the request for debugging
        logger.info(f"OpenRouter request - Model: {self.model_slug}")
        logger.info(f"OpenRouter request - Messages count: {len(messages)}")
        logger.info(f"OpenRouter request - Tools: {'Yes' if tools else 'No'}")
        
        payload = {
            "model": self.model_slug,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice
        
        try:
            logger.info("Sending request to OpenRouter...")
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            logger.info(f"OpenRouter response status: {response.status_code}")
            
            # Log response content for debugging
            if response.status_code != 200:
                error_content = response.text
                logger.error(f"OpenRouter error response: {error_content}")
                raise OpenRouterError(f"HTTP {response.status_code}: {error_content}")
            
            result = response.json()
            logger.info("OpenRouter response received successfully")
            
            if "error" in result:
                logger.error(f"OpenRouter API error: {result['error']}")
                raise OpenRouterError(f"OpenRouter API error: {result['error']}")
            
            return result
            
        except httpx.HTTPStatusError as e:
            error_text = e.response.text if hasattr(e, 'response') else str(e)
            logger.error(f"HTTP error calling OpenRouter: Status {e.response.status_code}, Body: {error_text}")
            raise OpenRouterError(f"HTTP error {e.response.status_code}: {error_text}")
        except httpx.RequestError as e:
            logger.error(f"Request error calling OpenRouter: {e}")
            raise OpenRouterError(f"Request error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error calling OpenRouter: {e}")
            raise OpenRouterError(f"Unexpected error: {e}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
