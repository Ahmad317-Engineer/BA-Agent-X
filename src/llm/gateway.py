"""
LLM Gateway - Abstract interface for multiple LLM providers
"""

from abc import ABC, abstractmethod
from typing import Optional, Generator
import requests
import json

class BaseLLM(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def stream(self, prompt: str, system: Optional[str] = None) -> Generator[str, None, None]:
        """Stream response from LLM"""
        pass

class OllamaLLM(BaseLLM):
    """Ollama local LLM implementation"""
    
    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system or "You are a senior Business Analyst.",
                    "stream": False,
                    "options": {"temperature": 0.2}
                },
                timeout=30
            )
            return response.json().get("response", "Error: No response")
        except Exception as e:
            print(f"Ollama error: {e}")
            return f"Error: Could not connect to Ollama. Is it running? {e}"
    
    def stream(self, prompt: str, system: Optional[str] = None) -> Generator[str, None, None]:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system or "You are a senior Business Analyst.",
                    "stream": True,
                    "options": {"temperature": 0.2}
                },
                stream=True,
                timeout=30
            )
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    yield data.get("response", "")
        except Exception as e:
            yield f"Error: {e}"

class OpenRouterLLM(BaseLLM):
    """OpenRouter API implementation (cloud fallback)"""
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system or "You are a senior Business Analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                },
                timeout=30
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"OpenRouter error: {e}"
    
    def stream(self, prompt: str, system: Optional[str] = None) -> Generator[str, None, None]:
        # Simplified streaming for OpenRouter
        yield self.generate(prompt, system)

class MockLLM(BaseLLM):
    """Mock LLM for development without API keys"""
    
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        return f"""
        [MOCK LLM RESPONSE]
        
        Prompt: {prompt[:100]}...
        
        As a Business Analyst, I would analyze this request by:
        1. Understanding the business need
        2. Identifying stakeholders
        3. Defining success criteria
        4. Outlining implementation approach
        
        (This is a mock response. Configure Ollama or OpenRouter for real AI.)
        """
    
    def stream(self, prompt: str, system: Optional[str] = None) -> Generator[str, None, None]:
        yield self.generate(prompt, system)

def get_llm(provider: str = "mock", **kwargs):
    """Factory method to get LLM instance"""
    if provider == "ollama":
        return OllamaLLM(**kwargs)
    elif provider == "openrouter":
        return OpenRouterLLM(**kwargs)
    else:
        return MockLLM(**kwargs)

# Test the LLM gateway
if __name__ == "__main__":
    print("Testing LLM Gateway...")
    llm = get_llm("mock")
    response = llm.generate("What is a user story?")
    print(response[:200])
