# Análise do Código Fonte do Codeswarm

**Data:** 19/12/2025
**Escopo:** Análise do diretório `codeswarm/`, incluindo arquivos core e agentes em `agno-agents/`.

## 1. Estrutura do Projeto
O diretório `codeswarm/` contém a implementação principal do sistema.
*   **Core:** `agent_os.py`, `agents.py`, `main.py`, `models.py`.
*   **Agentes:** `agno-agents/` contendo dezenas de implementações individuais de agentes (ex: `001-accessibility_tester_agent.py`, `014-backend_developer_agent.py`).
*   **Ferramentas e Integrações:** `tools.py`, `mcp_tools.py`, `khala_integration.py`.
*   **Prompts:** `prompts/` contendo definições JSON dos personas.

## 2. Arquitetura Core (`agent_os.py`)
A classe `AgentOS` é o orquestrador central.
*   **Inicialização:** Configura o ambiente, ferramentas de memória (`khala_integration`) e inicializa os agentes principais (`admin`, `planner`, `knowledge`).
*   **TaskTree:** Utiliza uma estrutura de árvore (`structures.py`) para gerenciar a decomposição de tarefas.
*   **Fluxo:** Embora o código lido mostre a inicialização, a orquestração depende fortemente da interação entre o `planner_agent` e a execução das tarefas definidas na árvore.

## 3. Implementação dos Agentes (`agno-agents/*.py`)
A análise de arquivos como `001-accessibility_tester_agent.py` e `014-backend_developer_agent.py` revela um padrão consistente:
*   **Framework Agno:** Todos herdam ou utilizam `agno.agent.Agent`.
*   **Modelos:** Configurados para usar `agno.models.google.Gemini`.
*   **System Prompts:** Carregados de arquivos JSON satélites (ex: `*_sysp.json`).
*   **Cognee:** Suporte opcional à biblioteca `cognee` para gestão de memória/grafo.
*   **Execução Standalone:** Cada arquivo de agente possui um bloco `if __name__ == "__main__":` que permite execução isolada via linha de comando, útil para testes e debugging.

## 4. Gestão de Prompts (`prompts/*.json`)
Os prompts são definidos em JSON, o que facilita a modificação sem alterar o código Python.
*   **Estrutura:**
    *   `agentProfile`: Nome e Role.
    *   `coreDirectives` (ou `explicit_processing_instruction` no `dev_prompt`): Instruções detalhadas de comportamento.
    *   `tools`: Lista de ferramentas permitidas.
*   **DevPrompt:** É extremamente detalhado, com instruções sobre "Iterative Critique-Refinement Cycle" e especificações estritas de output JSON.

## 5. Integrações e Ferramentas
*   **Khala:** `khala_integration.py` expõe ferramentas para interação com o banco de memória.
*   **MCP:** `mcp_tools.py` sugere a camada de compatibilidade com o Model Context Protocol, permitindo que ferramentas sejam servidas e consumidas de forma padronizada.
*   **Segurança:** `utils/security.py` implementa verificação de caminhos (`safe_paths`) para evitar que agentes acessem ou modifiquem arquivos fora do diretório do projeto alvo.

## 6. Conclusão da Análise de Código
O código reflete uma arquitetura modular e escalável. A separação entre a definição do agente (código Python) e seu comportamento (JSON prompts) é uma prática robusta. A existência de dezenas de agentes especializados em `agno-agents/` confirma a estratégia de "Swarm Intelligence", onde a complexidade é distribuída entre muitos especialistas ao invés de poucos generalistas.
