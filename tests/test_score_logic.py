"""Tests da regra de qualificação por investimento."""

import pytest

from sdr_agent_langgraph.nodes.score import score_node
from sdr_agent_langgraph.state import initial_state


def _state_with(**kwargs):
    """Helper: state inicial mais overrides."""
    s = initial_state("test", "")
    s.update(kwargs)
    return s


@pytest.mark.parametrize(
    "investment,expected_label,expected_score,expected_action",
    [
        (5000, "HOT", 30, "schedule"),
        (3000, "HOT", 30, "schedule"),
        (2999, "WARM", 20, "schedule"),
        (1500, "WARM", 20, "schedule"),
        (1499, "COLD", -30, "disqualify"),
        (500, "COLD", -30, "disqualify"),
    ],
)
def test_score_by_investment(investment, expected_label, expected_score, expected_action):
    state = _state_with(has_paid_traffic=True, monthly_investment=investment)
    result = score_node(state)
    assert result["label"] == expected_label
    assert result["score"] == expected_score
    assert result["next_action"] == expected_action


def test_score_no_traffic_willing():
    state = _state_with(has_paid_traffic=False, willing_to_invest=True)
    result = score_node(state)
    assert result["label"] == "WARM"
    assert result["score"] == 15
    assert result["next_action"] == "schedule"


def test_score_no_traffic_not_willing():
    state = _state_with(has_paid_traffic=False, willing_to_invest=False)
    result = score_node(state)
    assert result["label"] == "COLD"
    assert result["disqualified_reason"] == "budget_not_available"
    assert result["next_action"] == "disqualify"


def test_score_disqualified_below_minimum_has_reason():
    state = _state_with(has_paid_traffic=True, monthly_investment=800)
    result = score_node(state)
    assert result["disqualified_reason"] == "budget_below_minimum"
