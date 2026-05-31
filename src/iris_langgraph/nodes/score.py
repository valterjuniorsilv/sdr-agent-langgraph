"""Node: score — calcula score e label baseado no investimento (regra Iris canônica)."""

from __future__ import annotations

import os

from iris_langgraph.state import AgentState


def score_node(state: AgentState) -> dict:
    """Aplica a tabela de qualificação Iris:

    | Investimento                        | Score | Label |
    | >= R$3000/mês                       | +30   | HOT   |
    | R$1500-2999/mês                     | +20   | WARM  |
    | Só indicação + disposto >= R$1500   | +15   | WARM  |
    | R$1-1499 (já investe)               | -30   | COLD  |
    | Só indicação + NÃO disposto         |  0    | COLD  |
    """
    min_invest = float(os.environ.get("MIN_INVESTMENT", "1500"))
    hot_threshold = float(os.environ.get("HOT_THRESHOLD", "3000"))

    has_traffic = state.get("has_paid_traffic")
    investment = state.get("monthly_investment")
    willing = state.get("willing_to_invest")

    score = 0
    label = "COLD"
    disqualified_reason = None
    next_action = "disqualify"

    if has_traffic and investment is not None:
        if investment >= hot_threshold:
            score = 30
            label = "HOT"
            next_action = "schedule"
        elif investment >= min_invest:
            score = 20
            label = "WARM"
            next_action = "schedule"
        else:
            score = -30
            label = "COLD"
            disqualified_reason = "budget_below_minimum"
            next_action = "disqualify"
    elif has_traffic is False:
        if willing is True:
            score = 15
            label = "WARM"
            next_action = "schedule"
        else:
            score = 0
            label = "COLD"
            disqualified_reason = "budget_not_available"
            next_action = "disqualify"

    return {
        "score": score,
        "label": label,
        "disqualified_reason": disqualified_reason,
        "next_action": next_action,
    }
