"""CLI interativo pra testar o agent no terminal."""

from __future__ import annotations

import uuid

import click

from iris_langgraph.graph import build_graph
from iris_langgraph.state import initial_state


@click.command()
@click.option("--conversation-id", default=None, help="ID da conversa. Default: aleatório.")
def main(conversation_id: str | None) -> None:
    """Inicia uma sessão interativa com o agent SDR no terminal."""
    conv_id = conversation_id or str(uuid.uuid4())[:8]
    print(f"Sessão iniciada (conversation_id={conv_id}). Digite 'sair' pra encerrar.\n")

    app = build_graph()
    state = None

    first_message = input("Você: ").strip()
    if not first_message:
        return

    state = initial_state(conv_id, first_message)

    # Loop: roda o grafo até bater num END, mostra última resposta, pega próxima input
    while True:
        result = app.invoke(state)
        print(f"Aria: {result.get('last_agent_response', '(sem resposta)')}\n")

        if result.get("next_action") == "end":
            print(f"--- FIM ---")
            print(f"Label: {result.get('label')}")
            print(f"Score: {result.get('score')}")
            if result.get("disqualified_reason"):
                print(f"Motivo: {result['disqualified_reason']}")
            break

        user_input = input("Você: ").strip()
        if not user_input or user_input.lower() == "sair":
            break

        # Atualiza state com nova mensagem do usuário
        state = {**result, "last_user_message": user_input}
        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]


if __name__ == "__main__":
    main()
