"""CRM adapter — abstração sobre Monday/HubSpot/Pipedrive."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class CRMLead:
    """Representa um lead criado no CRM."""

    conversation_id: str
    name: str | None
    label: str  # HOT/WARM/COLD
    score: int
    monthly_investment: float | None
    notes: str = ""
    extras: dict = field(default_factory=dict)


class CRMAdapter(Protocol):
    """Interface pra criar/atualizar lead no CRM."""

    def upsert_lead(self, lead: CRMLead) -> str:
        """Cria ou atualiza lead. Retorna o ID externo."""
        ...

    def add_note(self, lead_id: str, note: str) -> None:
        """Adiciona nota ao lead existente."""
        ...


class MockCRM:
    """Mock que armazena leads em dict pra inspeção em testes."""

    def __init__(self):
        self.leads: dict[str, CRMLead] = {}
        self.notes: dict[str, list[str]] = {}

    def upsert_lead(self, lead: CRMLead) -> str:
        self.leads[lead.conversation_id] = lead
        return lead.conversation_id

    def add_note(self, lead_id: str, note: str) -> None:
        self.notes.setdefault(lead_id, []).append(note)
