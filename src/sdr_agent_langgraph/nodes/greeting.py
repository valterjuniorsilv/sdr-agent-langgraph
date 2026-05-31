"""Node: greeting — primeira resposta + extrai nome se mencionado."""

from __future__ import annotations

from sdr_agent_langgraph.state import AgentState


def greeting_node(state: AgentState) -> dict:
    """Cumprimenta e abre a conversa pedindo identificação informal."""
    response = (
        "Oi, tudo bem? Sou a Aria, consultora da agência. "
        "Vi que você mostrou interesse — posso te fazer 2-3 perguntas rápidas "
        "pra entender se faz sentido a gente conversar?"
    )
    return {
        "last_agent_response": response,
        "messages": state.get("messages", []) + [{"role": "assistant", "content": response}],
        "next_action": "ask_role",
    }
