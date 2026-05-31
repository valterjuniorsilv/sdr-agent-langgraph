"""Node: schedule — convida lead qualificado pra reunião."""

from __future__ import annotations

from sdr_agent_langgraph.state import AgentState


def schedule_node(state: AgentState) -> dict:
    """Oferece agenda. Mensagem varia por label (HOT vs WARM)."""
    label = state.get("label")
    if label == "HOT":
        response = (
            "Show. Acho que faz total sentido a gente conversar 20 minutos pra eu te "
            "mostrar como funciona. Qual horário fica melhor pra você: amanhã 14h ou 16h?"
        )
    else:  # WARM
        response = (
            "Beleza. Vou te mandar uma call de 20 minutos só pra te dar contexto educacional "
            "do que faz sentido pro seu cenário. Amanhã 14h ou quinta 10h?"
        )

    return {
        "last_agent_response": response,
        "messages": state.get("messages", []) + [{"role": "assistant", "content": response}],
        "next_action": "end",
    }
