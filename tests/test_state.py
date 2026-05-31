"""Tests do state inicial."""

from sdr_agent_langgraph.state import initial_state


def test_initial_state_creates_defaults():
    state = initial_state("conv-1", "oi")
    assert state["conversation_id"] == "conv-1"
    assert state["last_user_message"] == "oi"
    assert state["label"] == "UNKNOWN"
    assert state["score"] == 0
    assert state["next_action"] == "ask_role"
    assert state["messages"] == [{"role": "user", "content": "oi"}]
