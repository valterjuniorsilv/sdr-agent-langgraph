"""State definition do agent SDR.

State é a memória compartilhada entre todos os nodes do grafo.
Cada node lê o state e retorna updates parciais que o LangGraph faz merge.
"""

from typing import Literal, TypedDict


class AgentState(TypedDict, total=False):
    """Estado do agent SDR durante a conversa.

    Campos opcionais (total=False) porque o state cresce ao longo da conversa.
    """

    # Identificação da conversa
    conversation_id: str
    contact_name: str | None
    contact_role: Literal["dentist", "manager", "other", None]

    # Histórico de mensagens (lista de dicts {role, content})
    messages: list[dict[str, str]]

    # Última mensagem recebida (input)
    last_user_message: str

    # Última resposta do agent (output deste turno)
    last_agent_response: str

    # Respostas do SPIN
    spin_situation: str | None  # S — situação atual da agenda
    spin_problem: str | None  # P — principal problema percebido
    spin_implication: str | None  # I — implicação se nada mudar

    # Investimento em tráfego
    has_paid_traffic: bool | None
    monthly_investment: float | None  # R$/mês
    willing_to_invest: bool | None  # se não roda ads, está disposto a investir 1500+

    # Score e classificação
    score: int  # somatório
    label: Literal["HOT", "WARM", "COLD", "UNKNOWN"]
    disqualified_reason: str | None

    # Próximo passo
    next_action: Literal[
        "ask_role",
        "ask_spin_situation",
        "ask_spin_problem",
        "ask_spin_implication",
        "ask_traffic",
        "ask_investment",
        "ask_willing_invest",
        "schedule",
        "disqualify",
        "end",
    ]

    # Agendamento (se HOT/WARM)
    scheduled_at: str | None  # ISO 8601


def initial_state(conversation_id: str, user_message: str) -> AgentState:
    """Cria state inicial pra uma nova conversa."""
    return AgentState(
        conversation_id=conversation_id,
        contact_name=None,
        contact_role=None,
        messages=[{"role": "user", "content": user_message}],
        last_user_message=user_message,
        last_agent_response="",
        spin_situation=None,
        spin_problem=None,
        spin_implication=None,
        has_paid_traffic=None,
        monthly_investment=None,
        willing_to_invest=None,
        score=0,
        label="UNKNOWN",
        disqualified_reason=None,
        next_action="ask_role",
        scheduled_at=None,
    )
