"""Calendar adapter — abstração sobre Google Calendar / Cal.com."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class CalendarSlot:
    """Slot agendado."""

    conversation_id: str
    start_at: datetime
    meeting_url: str | None = None


class CalendarAdapter(Protocol):
    """Interface pra criar reunião."""

    def schedule(self, conversation_id: str, start_at: datetime) -> CalendarSlot:
        """Cria reunião e devolve slot com URL."""
        ...


class MockCalendar:
    """Mock que retorna slot com URL falsa pra testes."""

    def __init__(self):
        self.scheduled: list[CalendarSlot] = []

    def schedule(self, conversation_id: str, start_at: datetime) -> CalendarSlot:
        slot = CalendarSlot(
            conversation_id=conversation_id,
            start_at=start_at,
            meeting_url=f"https://meet.example.com/{conversation_id}",
        )
        self.scheduled.append(slot)
        return slot
