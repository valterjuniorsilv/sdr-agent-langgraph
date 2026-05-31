"""Tests do parser de valor monetário."""

import pytest

from sdr_agent_langgraph.nodes.investment import _parse_value


@pytest.mark.parametrize(
    "text,expected",
    [
        ("1500", 1500),
        ("R$ 1500", 1500),
        ("r$1500", 1500),
        ("3000 reais", 3000),
        ("3k", 3000),
        ("1.5k", 1500),
        ("dois mil", 2000),
        ("mil", 1000),
        ("nada", None),
    ],
)
def test_parse_value(text, expected):
    assert _parse_value(text) == expected
