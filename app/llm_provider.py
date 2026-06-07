from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from .config import settings


class LlmProviderError(RuntimeError):
    pass


def load_provider_config(path: Path | None = None) -> dict[str, Any] | None:
    config_path = path or settings.llm_provider_config
    if not config_path.exists():
        return None
    data = json.loads(config_path.read_text(encoding="utf-8"))
    if not data.get("base_url") or not data.get("api_key") or not data.get("model"):
        raise LlmProviderError("llm provider config is incomplete")
    return data


def extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise LlmProviderError("model did not return a JSON object")
    return json.loads(text[start : end + 1])


def complete_json(system_prompt: str, user_prompt: str, *, timeout: float | None = None) -> tuple[dict[str, Any], str]:
    config = load_provider_config()
    if not config:
        raise LlmProviderError("llm provider config is missing")
    base_url = str(config["base_url"]).rstrip("/")
    model = str(config["model"])
    provider_id = str(config.get("provider_id") or "custom-provider")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {config['api_key']}", "Content-Type": "application/json"}
    try:
        with httpx.Client(timeout=timeout or settings.llm_timeout_seconds) as client:
            response = client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        raise LlmProviderError(str(exc)) from exc
    content = data["choices"][0]["message"]["content"]
    return extract_json_object(content), provider_id
