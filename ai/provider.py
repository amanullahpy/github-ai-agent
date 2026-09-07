import time
import json
import logging
import requests
from typing import Dict, Any, Optional, Tuple
from config import Config
from .cache import AICache
from .prompts import SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)

GEMINI_CANDIDATE_MODELS = [
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
]


class AIProvider:
    def __init__(self, cache: Optional[AICache] = None):
        self.cache = cache or AICache()
        self.api_key = Config.AI_API_KEY
        self.provider = Config.AI_PROVIDER.lower()
        self.model = Config.AI_MODEL or "gemini-2.5-flash"

    def test_connection(self) -> Dict[str, Any]:
        """
        Tests the AI model connectivity and measures latency.
        """
        if not self.api_key:
            return {
                "success": False,
                "provider": self.provider,
                "model": self.model,
                "latency_ms": 0,
                "error": "No AI_API_KEY configured in .env",
                "output": "Running in heuristic fallback mode.",
            }

        start_time = time.time()
        test_prompt = "Say 'GitHub AI Agent connection verified!' in 6 words or less."

        try:
            if "gemini" in self.provider:
                result, used_model = self._call_gemini_with_fallback(test_prompt)
            else:
                result = self._call_openai_compatible(test_prompt)
                used_model = self.model

            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "success": True,
                "provider": self.provider,
                "model": used_model,
                "latency_ms": elapsed_ms,
                "output": result.strip(),
                "error": None,
            }
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "provider": self.provider,
                "model": self.model,
                "latency_ms": elapsed_ms,
                "error": str(e),
                "output": "Failed to connect to AI provider.",
            }

    def generate(
        self,
        prompt: str,
        operation: str = "general_analysis",
        context: Optional[Dict[str, Any]] = None,
        repository_id: Optional[int] = None
    ) -> str:
        ctx = context or {}
        input_hash = self.cache.compute_input_hash(operation, prompt, ctx)

        if not self.api_key:
            logger.info("No AI_API_KEY provided; using deterministic heuristic analysis.")
            return self._heuristic_fallback(operation, ctx)

        try:
            if "gemini" in self.provider:
                result, used_model = self._call_gemini_with_fallback(prompt)
            else:
                result = self._call_openai_compatible(prompt)
                used_model = self.model

            in_tokens = len(prompt) // 4
            out_tokens = len(result) // 4

            self.cache.record_usage(
                operation=operation,
                model=used_model,
                input_hash=input_hash,
                input_tokens=in_tokens,
                output_tokens=out_tokens,
                estimated_cost=0.0001,
                repository_id=repository_id,
                success=True,
            )
            return result
        except Exception as e:
            logger.error(f"AI generation error: {e}. Falling back to heuristics.")
            self.cache.record_usage(
                operation=operation,
                model=self.model,
                input_hash=input_hash,
                repository_id=repository_id,
                success=False,
            )
            return self._heuristic_fallback(operation, ctx)

    def _call_gemini_with_fallback(self, prompt: str) -> Tuple[str, str]:
        models_to_try = [self.model] + [m for m in GEMINI_CANDIDATE_MODELS if m != self.model]

        last_err = None
        for m in models_to_try:
            try:
                url = f"{Config.AI_BASE_URL}/models/{m}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": f"{SYSTEM_INSTRUCTION}\n\n{prompt}"}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 2048,
                    }
                }
                res = requests.post(url, json=payload, timeout=30)
                if res.status_code == 404:
                    # Model not supported on this endpoint/key, try next candidate
                    continue
                res.raise_for_status()
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        self.model = m  # Remember working model
                        return parts[0].get("text", ""), m
            except Exception as e:
                last_err = e

        if last_err:
            raise last_err
        raise RuntimeError("All Gemini model candidates failed or returned 404.")

    def _call_openai_compatible(self, prompt: str) -> str:
        url = f"{Config.AI_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        res = requests.post(url, json=payload, headers=headers, timeout=30)
        res.raise_for_status()
        data = res.json()
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return ""

    def _heuristic_fallback(self, operation: str, context: Dict[str, Any]) -> str:
        if operation == "readme_analysis":
            has_install = "installation" in str(context.get("readme_lower", ""))
            has_usage = "usage" in str(context.get("readme_lower", ""))
            missing = []
            if not has_install:
                missing.append("Installation instructions")
            if not has_usage:
                missing.append("Usage instructions")
            return f"Heuristic Analysis: Missing sections: {', '.join(missing) if missing else 'None'}"
        return "Deterministic analysis complete."
