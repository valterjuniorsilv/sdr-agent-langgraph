"""Monta o StateGraph do LangGraph.

Arquitetura: agent multi-turno. Cada invoke processa UMA mensagem do usuário,
roda UM node, gera UMA resposta e encerra. O `next_action` no state guia
qual node deve rodar no próximo invoke.

Fluxo:
    1. invoke(state) -> entrypoint `router`
    2. router decide via conditional_edges qual node executar
    3. node faz trabalho, retorna {next_action: "...", last_agent_response: "..."}
    4. node -> END
    5. CLI/webhook captura `last_agent_response` e devolve pro usuário
    6. Usuário responde -> novo invoke com state atualizado
"""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from sdr_agent_langgraph.edges.routing import route_next
from sdr_agent_langgraph.nodes import (
    ask_investment_node,
    ask_traffic_node,
    ask_willing_invest_node,
    disqualify_node,
    greeting_node,
    role_node,
    schedule_node,
    score_node,
    spin_implication_node,
    spin_problem_node,
    spin_situation_node,
)
from sdr_agent_langgraph.state import AgentState


def _router_node(state: AgentState) -> dict:
    """Node passthrough — decisão real fica nos conditional edges."""
    return {}


def build_graph():
    """Constrói e compila o StateGraph completo do agent SDR."""
    builder = StateGraph(AgentState)

    builder.add_node("router", _router_node)
    builder.add_node("greeting", greeting_node)
    builder.add_node("role", role_node)
    builder.add_node("spin_situation", spin_situation_node)
    builder.add_node("spin_problem", spin_problem_node)
    builder.add_node("spin_implication", spin_implication_node)
    builder.add_node("ask_traffic", ask_traffic_node)
    builder.add_node("ask_investment", ask_investment_node)
    builder.add_node("ask_willing_invest", ask_willing_invest_node)
    builder.add_node("score", score_node)
    builder.add_node("schedule", schedule_node)
    builder.add_node("disqualify", disqualify_node)

    builder.set_entry_point("router")

    # Router decide o node baseado em state.next_action (ou greeting se primeira vez)
    builder.add_conditional_edges(
        "router",
        _route_from_router,
        {
            "greeting": "greeting",
            "role": "role",
            "spin_situation": "spin_situation",
            "spin_problem": "spin_problem",
            "spin_implication": "spin_implication",
            "ask_traffic": "ask_traffic",
            "ask_investment": "ask_investment",
            "ask_willing_invest": "ask_willing_invest",
            "score": "score",
            "schedule": "schedule",
            "disqualify": "disqualify",
        },
    )

    # ask_investment e ask_willing_invest podem cair direto em score
    # (porque eles só extraem dado e setam next_action="score")
    # Pra evitar 2 turnos pro mesmo input, conectamos ao score quando next_action=="score"
    builder.add_conditional_edges(
        "ask_investment",
        lambda s: "score" if s.get("next_action") == "score" else "__end__",
        {"score": "score", "__end__": END},
    )
    builder.add_conditional_edges(
        "ask_willing_invest",
        lambda s: "score" if s.get("next_action") == "score" else "__end__",
        {"score": "score", "__end__": END},
    )

    # score sempre roteia pra schedule ou disqualify
    builder.add_conditional_edges(
        "score",
        lambda s: s.get("next_action", "disqualify"),
        {"schedule": "schedule", "disqualify": "disqualify"},
    )

    # Todos os outros vão pra END (encerram este turno, aguardam próximo input do usuário)
    for terminal in [
        "greeting",
        "role",
        "spin_situation",
        "spin_problem",
        "spin_implication",
        "ask_traffic",
        "schedule",
        "disqualify",
    ]:
        builder.add_edge(terminal, END)

    return builder.compile()


def _route_from_router(state: AgentState) -> str:
    """Router de entrada: se conversa nova, vai pra greeting; senão usa next_action."""
    # Conversa nova = sem resposta do assistant ainda
    has_assistant_msg = any(m.get("role") == "assistant" for m in state.get("messages", []))
    if not has_assistant_msg:
        return "greeting"

    action = state.get("next_action", "end")
    mapping = {
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
    }
    return mapping.get(action, "disqualify")  # default seguro
