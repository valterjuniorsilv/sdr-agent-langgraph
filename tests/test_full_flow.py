"""Tests do fluxo end-to-end do grafo."""

from iris_langgraph.graph import build_graph
from iris_langgraph.state import initial_state


def _run_one_turn(app, state):
    """Roda 1 ciclo do grafo (executa até bater END condicional ou retornar)."""
    return app.invoke(state)


def test_hot_lead_full_flow():
    """Dentista com R$5k/mês -> HOT -> schedule."""
    app = build_graph()

    # Turno 1: greeting
    state = initial_state("c1", "oi")
    state = _run_one_turn(app, state)
    assert "Aria" in state["last_agent_response"]

    # Turno 2: identifica como dentista
    state = {**state, "last_user_message": "sou o Dr. Silva"}
    state["messages"] = state.get("messages", []) + [
        {"role": "user", "content": "sou o Dr. Silva"}
    ]
    state = _run_one_turn(app, state)
    assert state["contact_role"] == "dentist"
    assert state["next_action"] == "ask_traffic"

    # Turno 3: confirma que já roda tráfego
    state = {**state, "last_user_message": "sim, já invisto"}
    state = _run_one_turn(app, state)
    assert state["has_paid_traffic"] is True
    assert state["next_action"] == "ask_investment"

    # Turno 4: declara valor (acima do threshold HOT)
    state = {**state, "last_user_message": "5000"}
    state = _run_one_turn(app, state)
    # score_node roda em seguida via roteamento, mas como ask_investment não emite resposta
    # quando o valor é parseado, o grafo segue direto pra score -> schedule
    assert state["label"] == "HOT"
    assert state["score"] == 30


def test_cold_lead_below_minimum():
    """Dentista com R$800/mês -> COLD -> disqualify."""
    app = build_graph()

    state = initial_state("c2", "oi")
    state = _run_one_turn(app, state)

    state = {**state, "last_user_message": "sou dentista"}
    state = _run_one_turn(app, state)

    state = {**state, "last_user_message": "sim"}
    state = _run_one_turn(app, state)

    state = {**state, "last_user_message": "800"}
    state = _run_one_turn(app, state)

    assert state["label"] == "COLD"
    assert state["disqualified_reason"] == "budget_below_minimum"


def test_warm_lead_no_traffic_willing():
    """Dentista sem tráfego mas disposto -> WARM."""
    app = build_graph()

    state = initial_state("c3", "oi")
    state = _run_one_turn(app, state)

    state = {**state, "last_user_message": "sou o dr"}
    state = _run_one_turn(app, state)

    state = {**state, "last_user_message": "não, só indicação"}
    state = _run_one_turn(app, state)
    assert state["has_paid_traffic"] is False
    assert state["next_action"] == "ask_willing_invest"

    state = {**state, "last_user_message": "consigo sim, tranquilo"}
    state = _run_one_turn(app, state)
    assert state["label"] == "WARM"
    assert state["score"] == 15
