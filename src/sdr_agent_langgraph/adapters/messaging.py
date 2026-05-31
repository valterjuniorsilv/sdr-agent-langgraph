"""Messaging adapter — abstração sobre WhatsApp (Evolution API, Twilio, etc.)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class SentMessage:
    """Representa uma mensagem enviada (pra testes)."""

    conversation_id: str
    text: str


class MessagingAdapter(Protocol):
    """Interface pra envio de mensagem."""

    def send(self, conversation_id: str, text: str) -> None:
        """Envia texto pro contato identificado por conversation_id."""
        ...


class MockMessaging:
    """Mock que armazena mensagens em memória pra inspecionar em testes."""

    def __init__(self):
        self.sent: list[SentMessage] = []

    def send(self, conversation_id: str, text: str) -> None:
        self.sent.append(SentMessage(conversation_id=conversation_id, text=text))


# Implementação real (Evolution API) — esqueleto pra Valter completar quando integrar
class EvolutionMessaging:
    """Wrapper sobre Evolution API. Requer EVOLUTION_API_URL + EVOLUTION_API_KEY."""

    def __init__(self, base_url: str, api_key: str, instance: str):
        import httpx

        self.client = httpx.Client(base_url=base_url, headers={"apikey": api_key})
        self.instance = instance

    def send(self, conversation_id: str, text: str) -> None:
        # conversation_id = phone number (ex: 554499...)
        response = self.client.post(
            f"/message/sendText/{self.instance}",
            json={"number": conversation_id, "text": text},
        )
        response.raise_for_status()
