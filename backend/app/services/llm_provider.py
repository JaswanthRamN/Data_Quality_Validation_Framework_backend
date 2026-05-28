"""
Multi-provider LLM abstraction layer.

Set AI_PROVIDER in .env to one of:
  gemini       — Google Gemini 1.5 Flash (free: 1,500 req/day)
  groq         — Groq Llama 3 (free: generous daily quota, very fast)
  openai       — OpenAI GPT-4o-mini (paid but ~$0.01 per 10 analyses)
  huggingface  — HuggingFace Inference API (free tier, Mistral/Llama)
  ollama       — Local Ollama (completely free, requires local install)
  anthropic    — Anthropic Claude (original, kept for completeness)
  none         — TF-IDF keyword fallback only (no AI features)
"""

import json
import logging
import re
from abc import ABC, abstractmethod

from app.config import settings

logger = logging.getLogger(__name__)


def _strip_json_fences(text: str) -> str:
    """Remove markdown code fences that some models wrap around JSON."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _parse_with_retry(text: str) -> dict:
    """
    Try to parse JSON; if it fails on first attempt, find the first '{' and retry.
    Some models add prose before/after the JSON object.
    """
    try:
        return json.loads(_strip_json_fences(text))
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        raise


# ── Abstract base ─────────────────────────────────────────────────────────────

class LLMProvider(ABC):
    """Minimal interface — send a prompt, get a text response."""

    @abstractmethod
    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        pass

    def complete_json(self, prompt: str, max_tokens: int = 2048) -> dict:
        """Complete and parse JSON response, with retry on parse error."""
        raw = self.complete(prompt, max_tokens)
        try:
            return _parse_with_retry(raw)
        except json.JSONDecodeError:
            # Retry once with explicit instruction
            retry_prompt = prompt + "\n\nIMPORTANT: Respond ONLY with raw valid JSON. No text before or after."
            raw2 = self.complete(retry_prompt, max_tokens)
            return _parse_with_retry(raw2)


# ── Google Gemini (free: 1,500 req/day on gemini-1.5-flash) ──────────────────

class GeminiProvider(LLMProvider):
    """
    Google Gemini via google-generativeai SDK.
    Free API key: https://ai.google.dev
    Default model: gemini-1.5-flash (fast + free tier)
    """

    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            generation_config={"response_mime_type": "application/json"},
        )

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        response = self.model.generate_content(prompt)
        return response.text


# ── Groq (free: ~14,400 req/day on llama-3.1-8b-instant) ─────────────────────

class GroqProvider(LLMProvider):
    """
    Groq cloud inference via groq SDK (OpenAI-compatible).
    Free API key: https://console.groq.com
    Default model: llama-3.3-70b-versatile (quality) or llama-3.1-8b-instant (speed)
    """

    def __init__(self):
        from groq import Groq
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return response.choices[0].message.content


# ── OpenAI (pay-as-you-go, gpt-4o-mini is ~$0.15/1M tokens) ─────────────────

class OpenAIProvider(LLMProvider):
    """
    OpenAI via openai SDK.
    Default model: gpt-4o-mini (~$0.01 per 10 job analyses)
    """

    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content


# ── HuggingFace Inference API (free tier) ─────────────────────────────────────

class HuggingFaceProvider(LLMProvider):
    """
    HuggingFace serverless Inference API.
    Free token: https://huggingface.co/settings/tokens
    Default model: mistralai/Mistral-7B-Instruct-v0.3
    """

    def __init__(self):
        from huggingface_hub import InferenceClient
        self.client = InferenceClient(
            model=settings.HUGGINGFACE_MODEL,
            token=settings.HUGGINGFACE_API_KEY,
        )

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        response = self.client.text_generation(
            prompt,
            max_new_tokens=max_tokens,
            temperature=0.2,
            return_full_text=False,
        )
        return response


# ── Ollama (local, completely free) ──────────────────────────────────────────

class OllamaProvider(LLMProvider):
    """
    Local Ollama instance — zero cost, runs on your machine.
    Install: https://ollama.ai  then: ollama pull llama3.2
    Default model: llama3.2
    """

    def __init__(self):
        import httpx
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self._client = httpx.Client(timeout=120.0)

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        response = self._client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": max_tokens, "temperature": 0.2},
            },
        )
        response.raise_for_status()
        return response.json()["response"]


# ── Anthropic Claude (original) ───────────────────────────────────────────────

class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude via anthropic SDK.
    Default model: claude-sonnet-4-6
    """

    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-6"

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text


# ── Factory ───────────────────────────────────────────────────────────────────

_PROVIDER_MAP = {
    "gemini": GeminiProvider,
    "groq": GroqProvider,
    "openai": OpenAIProvider,
    "huggingface": HuggingFaceProvider,
    "ollama": OllamaProvider,
    "anthropic": AnthropicProvider,
}

_REQUIRED_KEYS = {
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "openai": "OPENAI_API_KEY",
    "huggingface": "HUGGINGFACE_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "ollama": None,  # no key needed
    "none": None,
}


def get_llm_provider() -> LLMProvider | None:
    """
    Factory — returns the configured LLM provider or None (TF-IDF fallback).
    Checks that the required API key is set before instantiating.
    """
    provider_name = settings.AI_PROVIDER.lower().strip()

    if provider_name == "none" or not provider_name:
        logger.info("AI_PROVIDER=none — using TF-IDF keyword fallback only")
        return None

    if provider_name not in _PROVIDER_MAP:
        logger.warning(
            f"Unknown AI_PROVIDER '{provider_name}'. "
            f"Valid options: {list(_PROVIDER_MAP.keys())}. Using TF-IDF fallback."
        )
        return None

    # Check the required API key exists (except Ollama)
    key_field = _REQUIRED_KEYS.get(provider_name)
    if key_field:
        key_value = getattr(settings, key_field, "")
        if not key_value:
            logger.warning(
                f"AI_PROVIDER={provider_name} but {key_field} is empty. "
                f"Using TF-IDF fallback. Set {key_field} in your .env to enable AI analysis."
            )
            return None

    try:
        provider = _PROVIDER_MAP[provider_name]()
        logger.info(f"LLM provider initialized: {provider_name}")
        return provider
    except ImportError as e:
        logger.error(
            f"Cannot import package for provider '{provider_name}': {e}. "
            f"Run: pip install {_get_install_hint(provider_name)}"
        )
        return None
    except Exception as e:
        logger.error(f"Failed to initialize '{provider_name}' provider: {e}")
        return None


def _get_install_hint(provider: str) -> str:
    hints = {
        "gemini": "google-generativeai",
        "groq": "groq",
        "openai": "openai",
        "huggingface": "huggingface_hub",
        "ollama": "httpx",
    }
    return hints.get(provider, "")
