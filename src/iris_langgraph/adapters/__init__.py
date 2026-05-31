"""Adapters pra integrações externas (LLM, messaging, CRM, calendar).

Cada adapter tem uma interface (Protocol) + 1 implementação Mock + 1 real.
Mock permite testar sem queimar API. Real implementa quando for pra produção.
"""

from iris_langgraph.adapters.llm import LLMAdapter, MockLLM, AnthropicLLM
from iris_langgraph.adapters.messaging import MessagingAdapter, MockMessaging
from iris_langgraph.adapters.crm import CRMAdapter, MockCRM
from iris_langgraph.adapters.calendar import CalendarAdapter, MockCalendar

__all__ = [
    "LLMAdapter",
    "MockLLM",
    "AnthropicLLM",
    "MessagingAdapter",
    "MockMessaging",
    "CRMAdapter",
    "MockCRM",
    "CalendarAdapter",
    "MockCalendar",
]
