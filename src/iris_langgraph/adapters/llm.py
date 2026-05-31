"""LLM adapter — wrapper sobre Claude com mock pra testes."""

from __future__ import annotations

import os
from typing import Protocol


class LLMAdapter(Protocol):
    """Interface pra qualquer LLM."""

    def complete(self, prompt: str, max_tokens: int = 200) -> str:
        """Recebe prompt, retorna texto da resposta."""
        ...


class MockLLM:
    """LLM determinístico pra testes. Retorna respostas pré-programadas baseadas em keywords."""

    def __init__(self, responses: dict[str, str] | None = None):
        self.responses = responses or {}
        self.default = "Entendi. Pode me contar mais?"
        self.calls: list[str] = []

    def complete(self, prompt: str, max_tokens: int = 200) -> str:
        self.calls.append(prompt)
        prompt_lower = prompt.lower()
        for keyword, response in self.responses.items():
            if keyword.lower() in prompt_lower:
                return response
        return self.default


class AnthropicLLM:
    """LLM real via Anthropic SDK. Importa lazy pra mock funcionar sem o SDK instalado."""

    def __init__(self, model: str | None = None, api_key: str | None = None):
        from anthropic import Anthropic

        self.client = Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])
        self.model = model or os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

    def complete(self, prompt: str, max_tokens: int = 200) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        # extrai texto do primeiro bloco
        return message.content[0].text if message.content else ""
