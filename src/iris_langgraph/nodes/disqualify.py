"""Node: disqualify — encerra com simpatia leads que não cabem no piso."""

from __future__ import annotations

from iris_langgraph.state import AgentState


def disqualify_node(state: AgentState) -> dict:
    """Mensagem de descarte por motivo (budget_below_minimum, budget_not_available)."""
    reason = state.get("disqualified_reason")

    if reason == "budget_below_minimum":
        response = (
            "Olha, sendo honesto: pra esse modelo funcionar bem, a faixa de R$1500/mês "
            "é o mínimo. Abaixo disso a gente não consegue gerar volume nem calibrar. "
            "Quando o orçamento abrir, manda mensagem aqui que retomamos. Tudo bem?"
        )
    else:  # budget_not_available
        response = (
            "Tranquilo. Quando o momento for melhor pra investir em aquisição "
            "estruturada, manda mensagem aqui. Sucesso na clínica."
        )

    return {
        "last_agent_response": response,
        "messages": state.get("messages", []) + [{"role": "assistant", "content": response}],
        "next_action": "end",
    }
