"""Nodes de qualificação por investimento — regra de negócio do filtro.

Replica a regra Iris: piso R$1500/mês. Acima de R$3000 = HOT.
"""

from __future__ import annotations

import re

from iris_langgraph.state import AgentState


def _parse_value(text: str) -> float | None:
    """Extrai valor R$ da mensagem. Aceita '1500', '1.5k', 'R$ 2000', 'dois mil'."""
    if not text:
        return None
    text_lower = text.lower().strip()

    # Tenta extensos primeiro (mais específicos antes), pra evitar "mil" matchar "dois mil"
    extensos = [
        ("cinco mil", 5000.0),
        ("quatro mil", 4000.0),
        ("três mil", 3000.0),
        ("tres mil", 3000.0),
        ("dois mil", 2000.0),
        ("mil e quinhentos", 1500.0),
        ("dez mil", 10000.0),
        ("mil", 1000.0),
    ]
    for word, val in extensos:
        if word in text_lower:
            return val

    # Tenta números com k/mil sufixo: "1.5k", "3k", "2 mil"
    match_k = re.search(r"(\d+(?:[.,]\d+)?)\s*(k|mil)\b", text_lower)
    if match_k:
        num_str = match_k.group(1).replace(",", ".")
        return float(num_str) * 1000

    # Tenta número puro: "1500", "R$ 2000", "3000 reais"
    match_num = re.search(r"r?\$?\s*(\d{3,})\b", text_lower)
    if match_num:
        return float(match_num.group(1))

    return None


def ask_traffic_node(state: AgentState) -> dict:
    """Decide se o lead já investe em tráfego baseado na última resposta."""
    msg = state.get("last_user_message", "").lower()
    has_traffic = any(k in msg for k in ["sim", "já", "rodo", "rodando", "invisto", "tenho"])
    no_traffic = any(k in msg for k in ["não", "nao", "indicação", "indicacao", "boca a boca"])

    if has_traffic and not no_traffic:
        response = (
            "Beleza. Pra eu te montar o cenário certo, quanto você investe por mês mais ou menos?"
        )
        next_action = "ask_investment"
        has_paid_traffic = True
    elif no_traffic:
        response = (
            "Entendi. Pra esse modelo de aquisição que a gente usa funcionar, "
            "o piso é R$1500/mês em mídia. Você teria espaço pra começar nessa faixa?"
        )
        next_action = "ask_willing_invest"
        has_paid_traffic = False
    else:
        response = "Só pra confirmar: vocês investem em anúncio hoje ou ainda não?"
        next_action = "ask_traffic"
        has_paid_traffic = None

    return {
        "has_paid_traffic": has_paid_traffic,
        "last_agent_response": response,
        "messages": state.get("messages", []) + [{"role": "assistant", "content": response}],
        "next_action": next_action,
    }


def ask_investment_node(state: AgentState) -> dict:
    """Captura o valor mensal investido. Decide próximo passo baseado no piso."""
    value = _parse_value(state.get("last_user_message", ""))

    if value is None:
        response = "Me ajuda: dá um número aproximado mesmo, tipo 1500, 3000, 5000."
        return {
            "last_agent_response": response,
            "messages": state.get("messages", [])
            + [{"role": "assistant", "content": response}],
            "next_action": "ask_investment",
        }

    return {
        "monthly_investment": value,
        "next_action": "score",
    }


def ask_willing_invest_node(state: AgentState) -> dict:
    """Captura se o lead que NÃO roda ads está disposto a investir 1500+."""
    msg = state.get("last_user_message", "").lower()
    willing = any(k in msg for k in ["sim", "consigo", "posso", "tenho", "claro", "tranquilo"])
    not_willing = any(
        k in msg
        for k in ["não", "nao", "agora não", "ainda não", "muito alto", "fora", "não consigo"]
    )

    if willing and not not_willing:
        willing_to_invest = True
    elif not_willing:
        willing_to_invest = False
    else:
        response = "Só pra confirmar: dá pra começar com R$1500/mês ou agora não rola?"
        return {
            "last_agent_response": response,
            "messages": state.get("messages", [])
            + [{"role": "assistant", "content": response}],
            "next_action": "ask_willing_invest",
        }

    return {
        "willing_to_invest": willing_to_invest,
        "next_action": "score",
    }
