"""LLM Provider abstraction.

Supports multiple LLM providers with a common interface.
Configurable via environment variables:
  LLM_PROVIDER: "openai" | "ollama" (default: "openai")
  LLM_MODEL: model name (default: "gpt-4o-mini")
  LLM_API_KEY: API key for cloud providers
  LLM_BASE_URL: custom base URL (optional)
"""
import logging
import os
from abc import ABC, abstractmethod

logger = logging.getLogger("skillbridge")


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate a response from the LLM."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and available."""
        ...


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def generate(self, system_prompt: str, user_message: str) -> str:
        import httpx

        url = (self.base_url or "https://api.openai.com/v1") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "max_tokens": 1500,
            "temperature": 0.7,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.TimeoutException:
            logger.error("LLM request timed out")
            raise
        except httpx.HTTPStatusError as e:
            logger.error("LLM API error: %s", e.response.status_code)
            raise
        except Exception as e:
            logger.error("LLM request failed: %s", e)
            raise

    def is_available(self) -> bool:
        return bool(self.api_key)


class OllamaProvider(LLMProvider):
    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate(self, system_prompt: str, user_message: str) -> str:
        import httpx

        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["message"]["content"]
        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            raise
        except Exception as e:
            logger.error("Ollama request failed: %s", e)
            raise

    def is_available(self) -> bool:
        import httpx

        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False


class FallbackProvider(LLMProvider):
    def __init__(self, primary: LLMProvider, fallback_message: str | None = None):
        self.primary = primary
        self.fallback_message = fallback_message or (
            "I'm the SkillBridge AI Career Assistant. The LLM service is currently unavailable. "
            "I can still help you understand your SkillBridge data. Please try again later, "
            "or ask a question and I'll do my best to guide you based on your data."
        )

    def generate(self, system_prompt: str, user_message: str) -> str:
        if self.primary.is_available():
            try:
                return self.primary.generate(system_prompt, user_message)
            except Exception as e:
                logger.warning("Primary LLM provider failed, using fallback: %s", e)
        return self.fallback_message

    def is_available(self) -> bool:
        return True


def get_llm_provider() -> LLMProvider:
    provider_name = os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    api_key = os.getenv("LLM_API_KEY", "")
    base_url = os.getenv("LLM_BASE_URL")

    if provider_name == "ollama":
        ollama_url = base_url or "http://localhost:11434"
        provider = OllamaProvider(model=model, base_url=ollama_url)
    else:
        provider = OpenAIProvider(api_key=api_key, model=model, base_url=base_url)

    return FallbackProvider(primary=provider)
