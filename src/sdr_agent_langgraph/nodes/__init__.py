"""Nodes do grafo SDR.

Cada node é uma função que recebe state e retorna updates parciais.
LangGraph faz merge automático dos updates no state global.
"""

from sdr_agent_langgraph.nodes.greeting import greeting_node
from sdr_agent_langgraph.nodes.role import role_node
from sdr_agent_langgraph.nodes.spin import spin_situation_node, spin_problem_node, spin_implication_node
from sdr_agent_langgraph.nodes.investment import (
    ask_traffic_node,
    ask_investment_node,
    ask_willing_invest_node,
)
from sdr_agent_langgraph.nodes.score import score_node
from sdr_agent_langgraph.nodes.schedule import schedule_node
from sdr_agent_langgraph.nodes.disqualify import disqualify_node

__all__ = [
    "greeting_node",
    "role_node",
    "spin_situation_node",
    "spin_problem_node",
    "spin_implication_node",
    "ask_traffic_node",
    "ask_investment_node",
    "ask_willing_invest_node",
    "score_node",
    "schedule_node",
    "disqualify_node",
]
