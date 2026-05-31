"""Node: role — pergunta/identifica papel do contato (decisor ou não)."""

from __future__ import annotations

from iris_langgraph.state import AgentState


def role_node(state: AgentState) -> dict:
    """Identifica se o contato é decisor. Lógica simplificada: keyword match.

    Em produção, substitua por classificação via LLM.
    """
    msg = state.get("last_user_message", "").lower()
    role = None
    if any(k in msg for k in ["sou o dr", "sou a dra", "sou dentista", "dono", "owner"]):
        role = "dentist"
    elif any(k in msg for k in ["gerente", "secretária", "secretaria", "assistente"]):
        role = "manager"
    elif msg:
        role = "other"

    if role == "dentist":
        response = (
            "Perfeito, doutor(a). Pra começar: hoje, os pacientes novos "
            "vêm mais de indicação ou você já roda tráfego pago?"
        )
        next_action = "ask_traffic"
    elif role == "manager":
        response = (
            "Entendi. Preciso falar diretamente com o decisor da clínica "
            "pra avançar. Você consegue me passar o contato direto?"
        )
        next_action = "end"
    else:
        response = "Antes da gente seguir, você é o decisor da operação?"
        next_action = "ask_role"

    return {
        "contact_role": role,
        "last_agent_response": response,
        "messages": state.get("messages", []) + [{"role": "assistant", "content": response}],
        "next_action": next_action,
    }
