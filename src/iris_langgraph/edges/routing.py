"""Roteamento condicional baseado no campo `next_action` do state."""

from __future__ import annotations

from typing import Literal

from iris_langgraph.state import AgentState

NodeName = Literal[
    "greeting",
    "role",
    "spin_situation",
    "spin_problem",
    "spin_implication",
    "ask_traffic",
    "ask_investment",
    "ask_willing_invest",
    "score",
    "schedule",
    "disqualify",
    "__end__",
]


_ACTION_TO_NODE: dict[str, NodeName] = {
    "ask_role": "role",
    "ask_spin_situation": "spin_situation",
    "ask_spin_problem": "spin_problem",
    "ask_spin_implication": "spin_implication",
    "ask_traffic": "ask_traffic",
    "ask_investment": "ask_investment",
    "ask_willing_invest": "ask_willing_invest",
    "score": "score",
    "schedule": "schedule",
    "disqualify": "disqualify",
    "end": "__end__",
}


def route_next(state: AgentState) -> NodeName:
    """Mapeia `next_action` pro próximo node. Default: encerra."""
    action = state.get("next_action", "end")
    return _ACTION_TO_NODE.get(action, "__end__")
