import json
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings


class LlmClient:
    """OpenAI-compatible Qwen client with deterministic fallback support."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        self.api_key = api_key or settings.dashscope_api_key
        self.base_url = (base_url or settings.dashscope_base_url).rstrip("/")
        self.model = model or settings.dashscope_model
        self.timeout_seconds = timeout_seconds or settings.ai_timeout_seconds

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def complete_json(self, system_prompt: str, user_prompt: str, schema_name: str) -> Dict[str, Any]:
        if not self.is_configured():
            return {}

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        if isinstance(content, dict):
            return content
        if isinstance(content, str):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {}
        return {}
