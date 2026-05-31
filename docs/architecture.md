# Arquitetura — sdr-agent-langgraph

## Princípio único: cada invoke = 1 turno

Diferente de um chatbot LangChain "chain" (que executa do início ao fim em uma única chamada), aqui cada `app.invoke(state)` processa **um turno** da conversa:

1. Recebe `state` (com `last_user_message`)
2. Router decide qual node executar baseado em `next_action`
3. Node executa, gera `last_agent_response`, atualiza `next_action`
4. Grafo encerra (END)
5. Caller (CLI ou webhook) devolve `last_agent_response` pro usuário
6. Quando usuário responde, novo `invoke` com state atualizado

Esse padrão evita recursion limit e mapeia 1:1 com o ciclo natural de uma conversa WhatsApp.

## Por que não usar LangGraph `interrupt()`

LangGraph oferece `interrupt()` pra pausar execução e aguardar input humano. É elegante mas requer checkpointer persistente (SQLite/Postgres) e adiciona complexidade pra deploy em ambiente sem state local (serverless).

A abordagem "1 invoke = 1 turno" funciona em qualquer runtime, persiste state externamente (Redis/Postgres) e é mais simples de raciocinar.

## State design

`AgentState` é um `TypedDict` com `total=False` porque o state CRESCE ao longo da conversa:

- Início: só `conversation_id`, `last_user_message`, `next_action="ask_role"`
- Meio: + `contact_role`, `spin_situation`, `has_paid_traffic`, etc.
- Fim: + `score`, `label`, `disqualified_reason` ou `scheduled_at`

LangGraph faz merge automático: cada node retorna apenas as chaves que mudou.

## Roteamento

O nó `router` é passthrough — não faz nada além de existir como entrypoint estável. A decisão real fica nos `add_conditional_edges`, que mapeiam `state.next_action` pra um destino:

```python
"ask_role" -> role
"ask_spin_situation" -> spin_situation
...
```

**Detalhe importante:** `ask_investment` e `ask_willing_invest` têm conditional edge **direta pro `score`** quando conseguem extrair dado da resposta. Isso evita 2 turnos pro mesmo input (usuário diz "5000" → captura valor → roda score → roteia pra schedule, tudo em 1 invoke).

## Adapter pattern

Cada integração externa (LLM, messaging, CRM, calendar) é definida como `Protocol`:

```python
class MessagingAdapter(Protocol):
    def send(self, conversation_id: str, text: str) -> None: ...
```

E tem implementações:
- `MockMessaging` — armazena em memória, usado em testes
- `EvolutionMessaging` — produção real (esqueleto incluído)

Os nodes recebem adapters via dependency injection (no graph compile ou via state). Isso permite testes 100% determinísticos sem queimar API.

## Por que sanitizado

O agent original é parte da operação comercial Olympus (clínicas odontológicas). Aqui ele foi **genérico**:

- Persona "Aria" (não "Iris")
- Nicho não-especificado (não menciona dentista/clínica)
- Sem integração com Evolution prod / Monday real
- Sem prompts específicos da operação

Isso permite que outros desenvolvedores adaptem pra outros nichos sem precisar remover branding.

## Quando NÃO usar este padrão

- **Workflows simples sem branching:** use chain do LangChain ou Zapier/Make
- **Integrações múltiplas como produto principal:** n8n entrega melhor
- **Equipe não-dev edita o fluxo:** n8n permite, LangGraph não
- **Stateless puro (sem memória):** overkill, use chamada direta ao LLM
