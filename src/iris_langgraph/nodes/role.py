"""Node: role — pergunta/identifica papel do contato (decisor ou não)."""

from __future__ import annotations

import re

from iris_langgraph.state import AgentState

# Patterns flexíveis pra detectar dentista (com ou sem artigo)
DENTIST_PATTERNS = [
    r"\bsou\s+(o\s+|a\s+)?dr\.?\b",
    r"\bsou\s+(o\s+|a\s+)?dra\.?\b",
    r"\bsou\s+(o\s+|a\s+)?dentista\b",
    r"\bsou\s+(o\s+|a\s+)?dono\b",
    r"\bowner\b",
    r"\bdecisor\b",
    r"\bdoutor\b",
    r"\bsim\b",  # "sou o decisor?" -> "sim"
]

MANAGER_PATTERNS = [
    r"\bgerente\b",
    r"\bsecret[áa]ria\b",
    r"\bassistente\b",
    r"\brecepcionista\b",
]


def _detect_role(msg: str) -> str | None:
    """Retorna 'dentist', 'manager' ou None."""
    if not msg:
        return None
    msg_lower = msg.lower()
    for pattern in MANAGER_PATTERNS:
        if re.search(pattern, msg_lower):
            return "manager"
    for pattern in DENTIST_PATTERNS:
        if re.search(pattern, msg_lower):
            return "dentist"
    return None


def role_node(state: AgentState) -> dict:
    """Identifica se o contato é decisor.

    Após 2 tentativas sem detecção, default = "dentist" + segue (permissivo).
    """
    msg = state.get("last_user_message", "")
    role = _detect_role(msg)
    attempts = state.get("messages", []).count({}) + sum(
        1 for m in state.get("messages", []) if "é o decisor" in m.get("content", "")
    )

    if role == "dentist":
        response = (
            "Perfeito, doutor(a). Pra começar: hoje, os pacientes novos "
            "vêm mais de indicação ou você já roda tráfego pago?"
        )
        next_action = "ask_traffic"
        detected = "dentist"
    elif role == "manager":
        response = (
            "Entendi. Preciso falar diretamente com o decisor da clínica "
            "pra avançar. Você consegue me passar o contato direto?"
        )
        next_action = "end"
        detected = "manager"
    elif attempts >= 1:
        # Já tentou perguntar 1x e não conseguiu — assume dentist (default permissivo)
        response = (
            "Beleza. Pra começar então: hoje, os pacientes novos "
            "vêm mais de indicação ou você já roda tráfego pago?"
        )
        next_action = "ask_traffic"
        detected = "dentist"
    else:
        response = "Antes da gente seguir, você é o decisor da operação?"
        next_action = "ask_role"
        detected = None

    return {
        "contact_role": detected,
        "last_agent_response": response,
        "messages": state.get("messages", []) + [{"role": "assistant", "content": response}],
        "next_action": next_action,
    }
