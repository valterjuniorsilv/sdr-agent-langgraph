"""Nodes do SPIN simplificado: Situation, Problem, Implication.

Em produção: cada node poderia usar LLM pra extrair dados estruturados da resposta.
Aqui: armazenamos a resposta literal e avançamos.
"""

from __future__ import annotations

from iris_langgraph.state import AgentState


def spin_situation_node(state: AgentState) -> dict:
    """Captura situação atual e pergunta o problema."""
    response = (
        "Entendi. Hoje, quando você olha o mês, qual é o maior gargalo da agenda? "
        "Falta paciente novo, falta gente confirmar, ou os horários sobram?"
    )
    return {
        "spin_situation": state.get("last_user_message"),
        "last_agent_response": response,
        "messages": state.get("messages", []) + [{"role": "assistant", "content": response}],
        "next_action": "ask_spin_problem",
    }


def spin_problem_node(state: AgentState) -> dict:
    """Captura o problema e pergunta a implicação."""
    response = (
        "Faz sentido. E se isso continuar assim nos próximos 3 meses, "
        "o que você acha que muda no faturamento da clínica?"
    )
    return {
        "spin_problem": state.get("last_user_message"),
        "last_agent_response": response,
        "messages": state.get("messages", []) + [{"role": "assistant", "content": response}],
        "next_action": "ask_spin_implication",
    }


def spin_implication_node(state: AgentState) -> dict:
    """Captura a implicação e segue pra qualificação por investimento."""
    response = (
        "Beleza. Última pergunta antes de eu te montar o cenário: "
        "vocês já investem em anúncio hoje?"
    )
    return {
        "spin_implication": state.get("last_user_message"),
        "last_agent_response": response,
        "messages": state.get("messages", []) + [{"role": "assistant", "content": response}],
        "next_action": "ask_traffic",
    }
