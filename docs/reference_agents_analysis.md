# Análise de Agentes de Referência (`reference-agno-agents/`)

**Data:** 19/12/2025
**Escopo:** Análise do diretório `reference-agno-agents/`, focando em padrões arquiteturais e agentes reutilizáveis.

## 1. Descobertas Principais

### 1.1. O Padrão `KhalaBaseAgent`
A joia da coroa deste diretório é o `app/templates/base_agent.py` definindo `KhalaBaseAgent`.
*   **Integração Profunda:** Ele conecta nativamente o agente ao `KhalaClient` (em `app/lib/khala_client.py`).
*   **Ciclo de Memória:** Implementa métodos `recall()` (antes de chat) e `remember()` (depois de chat) automáticos.
*   **Recomendação:** Devemos adaptar este template para ser a classe base de todos os agentes no `codeswarm`, substituindo ou enriquecendo a atual implementação em `codeswarm/agents.py`.

### 1.2. `SecurityAboyeur` (O Porteiro)
Localizado em `app/agents/security_aboyeur.py`.
*   **Função:** Atua como um firewall cognitivo.
*   **Capabilities:** Detecta "Prompt Injection", sanitiza inputs e classifica a intenção do usuário (CONSULTING vs OPERATIONS) antes de rotear para outros agentes.
*   **Recomendação:** Implementar uma versão deste agente como o ponto de entrada único do `AgentOS`.

### 1.3. `AgentEngineer` (O Especialista em Ferramentas)
Localizado em `app/agents/agent_engineer.py`.
*   **Função:** Analisa o prompt de sistema de *outro* agente e decide dinamicamente quais ferramentas (MCP ou Nativas) ele precisa.
*   **Recomendação:** Extremamente útil para o nosso `PlannerAgent`. Em vez de hardcodar ferramentas, o Planner poderia consultar o AgentEngineer para "equipar" os workers dinamicamente.

### 1.4. Outros Agentes Notáveis
*   **DeepReasoner:** Implementa "Chain of Thought" explícita. Útil para tarefas de arquitetura complexa.
*   **KnowledgeSynthesizer:** Similar ao nosso KnowledgeAgent, mas vale comparar a implementação de síntese.
*   **Orchestrator:** Vale estudar como ele gerencia o hand-off entre agentes versus a nossa `TaskTree`.

## 2. Lista de Oportunidades de Integração

Aqui está a lista do que podemos usar/adaptar diretamente:

| Componente | Origem (`reference-agno-agents`) | Destino (`codeswarm`) | Ação Recomendada |
| :--- | :--- | :--- | :--- |
| **Khala Client** | `app/lib/khala_client.py` | `codeswarm/khala_integration.py` | **Portar Completo.** Esta lib já tem a lógica de retry, conexão segura e métodos de graph/vector prontos. |
| **Base Agent** | `app/templates/base_agent.py` | `codeswarm/agents.py` | **Adaptar.** Criar `class SwarmAgent(KhalaBaseAgent)` que herda as capacidades de memória automática. |
| **Security Guard** | `app/agents/security_aboyeur.py` | `agno-agents/000-gatekeeper_agent.py` | **Criar Novo.** Adicionar camada de segurança na entrada do sistema. |
| **Tool Selector** | `app/agents/agent_engineer.py` | `codeswarm/core/tool_registry.py` | **Inspirar.** Criar lógica para seleção dinâmica de ferramentas baseada em descrição da tarefa. |
| **Reasoning** | `app/agents/deepreasoner.py` | `prompts/core_reasoning.json` | **Extrair Prompt.** Usar a técnica de `<thought>` tags no system prompt dos nossos arquitetos. |

## 3. Conclusão
O diretório de referência contém componentes maduros que preenchem lacunas importantes no `codeswarm`, especificamente na **gestão automática de memória** e **segurança**. A prioridade deve ser portar a infraestrutura de conexão (`KhalaClient` e `KhalaBaseAgent`) para que todos os nossos agentes ganhem "memória persistente" de graça.
