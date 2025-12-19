# agno agi v2 how to add mcp  
  
To add Model Context Protocol (MCP) support in Agno AGI v2, you should use the `MCPTools` integration and pass an active MCP server to your agent. Below is a concise step-by-step guide for Python, following the official documentation and recent usage patterns:[1][2]

### 1. Import and Install Requirements
Make sure you have the Agno library installed, and that you have an MCP server available (it can be local or remote).

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
```

### 2. Configure and Connect MCPTools

You can connect to an MCP server using either the URL (for a remote MCP server) or the command (to spawn a local MCP server process).

**Via URL (Remote MCP server):**
```python
mcp_tools = MCPTools(url="https://your-mcp-server.com")
await mcp_tools.connect()
```

**Via command (Local MCP server process):**
```python
mcp_tools = MCPTools(command="uvx mcp-server-git")
await mcp_tools.connect()
```

### 3. Add MCPTools to Your Agent

Pass the `mcp_tools` instance to your agent as a tool on initialization.

```python
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[mcp_tools]
)
response = await agent.aprint_response("Test MCP integration", stream=True)
```

### 4. Automatic Connection Management

If you don't manually call `connect()`, Agno will manage the connection automatically (connection is established and closed on each agent execution).

```python
mcp_tools = MCPTools(url="https://your-mcp-server.com")
agent = Agent(model=OpenAIChat(id="gpt-4o"), tools=[mcp_tools])
# No explicit .connect() needed, handled by Agent
```

### 5. Close the MCP Connection

Always close the MCP connection after use if you managed it manually.

```python
await mcp_tools.close()
```

### 6. Example: Full Async Usage

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools

async def run():
    mcp_tools = MCPTools(command="uvx mcp-server-git")
    await mcp_tools.connect()
    try:
        agent = Agent(model=OpenAIChat(id="gpt-4o"), tools=[mcp_tools])
        await agent.aprint_response("Test query", stream=True)
    finally:
        await mcp_tools.close()
```
This sample integrates the MCP layer, enabling your agent to interact with any connected MCP tool/service. For advanced use (like multiple servers, connection refresh, etc.), see `refresh_connection` or the latest Agno documentation.[2][1]

If you need real multi-tool or multi-server workflows, refer to latest agent multi-tool docs or examples provided in the Agno "cookbook" repository.[3]  
  
# Citations:  
[1] [Model Context Protocol (MCP) - Agno](https://docs.agno.com/concepts/tools/mcp/overview)  
[2] [Model Context Protocol (MCP) - Agno](https://docs-v1.agno.com/tools/mcp/mcp)  
[3] [Agno's Universal Agent Interface (UAgI) Powered by MCP - LinkedIn](https://www.linkedin.com/pulse/agnos-universal-agent-interface-uagi-powered-mcp-allyson-barros-yga9f)  
[4] [agno-agi/agno: Multi-agent framework, runtime and control ... - GitHub](https://github.com/agno-agi/agno)  
[5] [L-23 Using MCP Servers with Agno: From Local Setup to ... - YouTube](https://www.youtube.com/watch?v=3WCD0ziGC5g)  
[6] [Connect to MCP Servers with Agno AI Agent, MCP Tools ... - YouTube](https://www.youtube.com/watch?v=77SIxH9G_1M)  
[7] [MCP Server](https://docs.agentops.ai/v2/usage/mcp-server)  
[8] [How to use Agent in playground UI with MCP tools in it #2825 - GitHub](https://github.com/agno-agi/agno/issues/2825)  
[9] [AGI Memory MCP Server: The Ultimate Guide to ...](https://skywork.ai/skypage/en/agi-memory-mcp-server-ai-consciousness/1978998690775605248)  
[10] [SSE MCP Server Agent - Agno | MCP Tutorial - Part 3 - YouTube](https://www.youtube.com/watch?v=StXHQ3z5cvA)  
[11] [Multi-tool agent with SurrealMCP and Agno - SurrealDB](https://surrealdb.com/blog/multi-tool-agent-with-surrealmcp-and-agno)  
[12] [Introducing Agno v2.0](https://www.agno.com/blog/introducing-agno-v2)  
[13] [Agno Playground Unavailable? Here's How to Unlock Its True Power](https://skywork.ai/skypage/en/Agno%20Playground%20Unavailable%3F%20Here%E2%80%99s%20How%20to%20Unlock%20Its%20True%20Power/1976191631378935808)  
[14] [Building Dissi with Agno and MCP - DEV Community](https://dev.to/k0msenapati/building-dissi-with-agno-and-mcp-4044)  
[15] [is there any way to use SSE to connect to MCP servers in ...](https://github.com/agno-agi/agno/issues/2706)  
[16] [Building an AI Agent with Agno: A Step-by-Step Guide](https://ai.plainenglish.io/building-an-ai-agent-with-agno-a-step-by-step-guide-13542b2a5fb6)  
[17] [MCP tools - Agent Development Kit - Google](https://google.github.io/adk-docs/tools-custom/mcp-tools/)  
[18] [Custom Tools, Prebuilt Toolkits, and MCP Servers](https://www.youtube.com/watch?v=cbZPhgr5qiA)  
---  


# how to make THESE, in agno?

---

Baseado na análise dos arquivos do espaço "AI AGENT PROMPTS", identifiquei diversas ferramentas e técnicas avançadas de engenharia de prompts discutidas. Vou criar uma lista abrangente de questões de nível HARD para um processo seletivo de Engenheiro de IA, com suas respectivas respostas.
Lista de Questões Avançadas - Processo Seletivo Engenheiro de IA
Questão 1: Arquitetura de Agent Loops
Pergunta: Explique detalhadamente como funciona um "agent loop" no contexto de agentes autônomos de IA. Descreva as 6 etapas fundamentais do ciclo e como você implementaria um mecanismo de fallback para evitar loops infinitos em casos de falha recorrente.
Resposta Esperada: Um agent loop é um ciclo iterativo que permite que agentes de IA executem tarefas complexas de forma autônoma. As 6 etapas são:
Analyze Events: O agente analisa o estado atual através do event stream, focando em mensagens recentes do usuário e resultados de execução anteriores
Select Tools: Escolha da ferramenta apropriada baseada no estado atual, planejamento de tarefas e conhecimento disponível
Wait for Execution: A ação selecionada é executada pelo ambiente sandbox com novas observações adicionadas ao event stream
Iterate: Executar apenas uma chamada de ferramenta por iteração, repetindo pacientemente até completar a tarefa
Submit Results: Enviar resultados ao usuário via message tools, incluindo deliverables e arquivos relacionados
Enter Standby: Entrar em estado idle quando todas as tarefas estiverem completas
Mecanismos de Fallback:
Limite máximo de 3 tentativas para corrigir o mesmo erro no mesmo arquivo
Contador de iterações globais (máximo de 16 tool calls conforme observado em alguns sistemas)
Sistema de validação pré-execução verificando se os parâmetros das ferramentas estão corretos
Estratégia de fallback para métodos alternativos após falhas consecutivas
Checkpoint system após cada 3-5 tool calls para avaliar progresso
Sistema de "progress delta updates" para evitar repetição desnecessária

Questão 2: Tool Calling Etiquette e Best Practices
Pergunta: No contexto de sistemas agentic AI, quais são as regras críticas de "tool calling etiquette" que devem ser seguidas? Cite pelo menos 5 princípios fundamentais e explique por que cada um é importante para a experiência do usuário.
Resposta Esperada:
Nunca mencionar nomes de ferramentas ao usuário: Em vez de dizer "usarei o runinterminal tool", dizer "executarei o comando no terminal". Importante porque o usuário não precisa saber detalhes de implementação.
Explicar o "porquê" antes de chamar cada ferramenta: Antes de cada tool call, explicar ao usuário por que você está chamando aquela ferramenta. Promove transparência e confiança.
Aderir estritamente aos schemas JSON/XML: Sempre seguir o schema de tool call exatamente como especificado. Previne erros de execução e comportamentos inesperados.
Não solicitar permissão antes de usar ferramentas: O usuário espera ação imediata. Perguntar cria fricção desnecessária na experiência.
Usar message tools apropriadamente: Dividir entre "notify" (não-bloqueante) e "ask" (bloqueante). Minimizar disrupção do usuário enquanto mantém comunicação.
Executar tool calls em paralelo quando possível: Para operações independentes, executar simultaneamente para melhorar performance. Exceção: semanticsearch nunca em paralelo.
Não fabricar ferramentas não-existentes: Verificar cuidadosamente as ferramentas disponíveis e não inventar ferramentas que não foram fornecidas explicitamente.

Questão 3: File Editing Strategies
Pergunta: Compare e contraste três abordagens diferentes para edição de arquivos em sistemas agentic: (1) line-based search and replace, (2) string replacement, e (3) insert edit. Quando cada abordagem deve ser utilizada? Forneça exemplos práticos.
Resposta Esperada:
1. Line-Based Search and Replace (Abordagem Preferencial)
Quando usar: Para modificar código existente, especialmente seções maiores (>6 linhas)
Vantagens:
Validação explícita usando números de linha
Uso de ellipsis (...) para reduzir tokens
Maior precisão com validação de conteúdo
Exemplo:
filepath: src/components/TaskList.tsx
search: "const handleTaskComplete = (taskId) => {\n  setTasks(...)\n  ... existing code ...\n  onTaskUpdate?.(updatedTasks)\n}"
firstreplacedline: 15
lastreplacedline: 28
replace: "const handleTaskComplete = useCallback((taskId: string) => {\n  // New implementation with analytics\n  ...\n})"

2. String Replacement (replacestringinfile)
Quando usar: Mudanças menores e precisas onde você tem uma string única para substituir
Vantagens:
Simples e direto para pequenas mudanças
Não requer contagem de linhas
Desvantagens: Requer contexto único (3-5 linhas antes/depois)
Exemplo: Trocar um import específico ou renomear uma variável
3. Insert Edit (último recurso)
Quando usar: APENAS quando replacestringinfile falhou ou o usuário solicitou explicitamente
Vantagens: Ferramenta "inteligente" que entende contexto
Formato: Usar comentários como "...existing code..." para representar regiões inalteradas
Exemplo:
class Person {
  ...existing code...
  age: number;  // Nova propriedade inserida
  ...existing code...
  getAge() { return this.age; }  // Novo método
}

Regra de Ouro: Sempre começar com line-based search and replace, usar string replacement para casos simples, e inserteditintofile apenas como último recurso.

Questão 4: Sandbox Environment Awareness
Pergunta: Por que é crucial que um agente AI tenha "environment awareness"? Descreva os componentes essenciais de informação sobre ambiente que devem ser fornecidos ao agente e dê exemplos de como essa informação influencia as decisões do agente.
Resposta Esperada:
Componentes Essenciais de Environment Awareness:
Sistema Operacional:
Exemplo: "OS is Linux 5.15.0 Ubuntu 22.04"
Impacto: Determina comandos shell apropriados (apt vs brew, bash vs powershell)
Shell Padrão:
Exemplo: "Default shell is powershell.exe Windows PowerShell v5.1"
Impacto: Sintaxe de comandos (& vs &&, path separators)
Runtime Environment:
Python version (3.10.12), Node.js (20.18.0)
Impacto: Disponibilidade de features, compatibilidade de código
Sandbox Constraints (WebContainer example):
No pip support, no native binaries
Python limited to standard library only
No Git available
Impacto: Determina quais bibliotecas podem ser usadas, workflow alternatives
Diretório de Trabalho:
Current Working Directory
Home Directory
Impacto: Paths absolutos vs relativos
User Privileges:
sudo availability
Impacto: Operações que requerem elevação
Data/Timestamp Atual:
Exemplo: "Current date: 2025-11-12"
Impacto: Buscas web, timestamps, logs
Exemplos Práticos de Influência:
# SEM environment awareness (INCORRETO)
# Assumindo Linux quando o usuário está no Windows
agent.run_command("apt-get install package")

# COM environment awareness (CORRETO)
if os_info.platform == "Windows":
    agent.run_command("choco install package")
elif os_info.platform == "Linux":
    agent.run_command("apt-get install package")

WebContainer Constraints:
# INCORRETO - tentando usar pip em WebContainer
agent.run_command("pip install pandas")

# CORRETO - usando apenas stdlib
import json  # stdlib only
import statistics  # stdlib only


Questão 5: Prompting Patterns para Deep Research
Pergunta: Baseado no framework "Deep Research Planner", descreva as 4 fases obrigatórias de planejamento para pesquisas acadêmicas profundas. Para cada fase, especifique os outputs esperados e os checkpoints de validação.
Resposta Esperada:
Fase 1: Requirement Deconstruction & Scope Definition
Actions: 1.1. Restate query palavra-por-palavra para confirmar 1.2. Semantic Dissection: Decompor em , , , , , , 1.3. Metacognitive Analysis: Listar assumptions e internal clarifications 1.4. Define Preliminary Scope: 3-7 key themes/pillars 1.5. Assess Scope Sufficiency para profundidade acadêmica
Checklist:
Query restated accurately
Semantic dissection completa (incluindo NFRs)
Assumptions e clarifications logged em 'thought trace'
Preliminary scope de key themes definido
Scope assessed para depth/word count

Fase 2: Source Analysis & Synthesis Strategy
Actions: 2.1. Rigorous Assessment de cada fonte:
Relevance to scope topics
Recency (comparado com data atual)
Authority/Bias
Key information/data provided
Overlap/contradictions com outras fontes
Grounding quality (primary vs secondary)
2.2. Gap Analysis: Identificar gaps de informação 2.3. Define Synthesis Strategy:
Prioritization rules
Conflict resolution method
Bias mitigation plan
Checklist:
Todas fontes rigorosamente assessed (relevance, bias, grounding)
Information gaps claramente identificados
Clear synthesis strategy definida
Proactive, actionable bias mitigation plan

Fase 3: Detailed Outline Generation
Actions: 3.1. Explore Outline Structures: Considerar 2-3 high-level structures (chronological, thematic, problem-solution) 3.2. Develop Detailed Hierarchical Execution Outline:
# Title refletindo core theme
Opening summary paragraph key points
Pelo menos 5 informative ## Body Sections
Detailed ### Subsections com:
subsection_title
content_notes
sources (indexes)
synthesis_note
reasoning_tool_assignment (causal chains, counterfactual, etc.)
word_est
3.3. Review Outline Format & Modularity contra <report_format>
Checklist:
Outline structure selecionada em 'thought trace'
Title e summary outlined
Mínimo 5 ## sections definidas
### subsections detalhadamente planejadas
Subsections complexas assignadas com reasoning tools
## Conclusion points planejados
Outline validado para format e modularity

Fase 4: Final Plan Review & Adversarial Self-Critique (SASC)
Actions: 4.1. Execute Mandatory SASC usando 3 personas:
Skeptical Academic Reviewer: Lógica rigorosa? Scope superficial? Synthesis academically sound?
Bias Hunter: Bias mitigation adequado? Espaço para counter-arguments?
User Requirement Advocate: 100% coverage de query aspects? Atende core goal?
4.2. Implement Feedback Loop:
Se qualquer persona encontrar falhas críticas: "validation failed"
Retornar à fase relevante, corrigir, e re-executar
4.3. Generate Final Plan Validation Output:
plan_status: "Validated"
plan_quality_score: "10/10"
execution_confidence_score: 0.0-1.0
justification
remaining_risks
Checklist:
SASC executado por todas 3 personas
Feedback loop completado
Final plan validation output gerado (Status: Validated, 10/10)

Questão 6: Chain-of-Thought vs. Agentic Reasoning
Pergunta: Explique a diferença fundamental entre "Chain-of-Thought" prompting tradicional e "Agentic Reasoning" com tool use. Como o conceito de "thinking tags" ou "planning phases" se encaixa em ambas abordagens?
Resposta Esperada:
Chain-of-Thought (CoT) Prompting:
Natureza: Raciocínio interno, texto-para-texto
Execução: O modelo "pensa em voz alta" antes de dar resposta final
Ferramentas: Nenhuma - todo o raciocínio é simulado internalmente
Formato: "Let's think step by step..." seguido de raciocínio em linguagem natural
Limitações:
Não pode verificar fatos externos
Não pode executar código real
Propenso a alucinações em cálculos complexos
Agentic Reasoning com Tool Use:
Natureza: Raciocínio distribuído entre modelo e ambiente externo
Execução: O agente alterna entre pensar e agir (tool calls)
Ferramentas: Múltiplas - search, code execution, file operations, browser, etc.
Formato: Ciclo de action → observation → reflection → next action
Vantagens:
Verificação factual através de search
Cálculos precisos via code execution
Interação com sistemas reais
Thinking Tags / Planning Phases:
No CoT:
<thinking>
Para resolver X, preciso:
1. Entender o contexto de Y
2. Calcular Z usando fórmula W
3. Considerar edge cases...
</thinking>

<answer>
A resposta é...

Citations:
[1] [dontriskit-awesome-ai-system-prompts-8a5edab282632443.txt](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_c7aa070f-c6d1-4c79-8289-f22a9956256d/da091de2-3939-4400-a76b-bed1896ab870/dontriskit-awesome-ai-system-prompts-8a5edab282632443.txt)  
[2] [bigboyslave-agents-prompts-8a5edab282632443.txt](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_c7aa070f-c6d1-4c79-8289-f22a9956256d/4fd0cedd-9030-41bc-a34a-615b602c01ff/bigboyslave-agents-prompts-8a5edab282632443.txt)  
[3] [x1xhlol-system-prompts-and-models-of-ai-tools-8a5edab282632443.txt](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_c7aa070f-c6d1-4c79-8289-f22a9956256d/73f02051-8d51-44c0-b7bb-638c5a4a6856/x1xhlol-system-prompts-and-models-of-ai-tools-8a5edab282632443.txt)  
[4] [agents.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_c7aa070f-c6d1-4c79-8289-f22a9956256d/233f8ecb-7042-4165-aa57-e4b87aeda102/agents.md)  
[5] [kshiteej006-system-prompts-and-models-of-ai-tools-8a5edab282632443.txt](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_c7aa070f-c6d1-4c79-8289-f22a9956256d/4b619864-7e19-4085-8220-86a772a16ac0/kshiteej006-system-prompts-and-models-of-ai-tools-8a5edab282632443.txt)  
  
Perfect! I've created a comprehensive guide implementing all the advanced AI agent patterns from your AI AGENT PROMPTS documents into Agno AGI v2. Here's what I've built for you:

## Implementing Advanced AI Agent Patterns in Agno AGI v2



This complete guide covers all six advanced topics you requested, with production-ready code examples for each:

### 📋 **1. Agent Loop Architecture (6-Stage Cycle)**
- Complete event monitoring implementation using Agno's `RunEvent` system
- 6-stage loop: ANALYZE → SELECT → EXECUTE → ITERATE → SUBMIT → STANDBY
- Checkpoint system creating snapshots every 5 tool calls
- Fallback mechanisms with error tracking and retry limits
- Global iteration limits (16 calls max, as per your notes)

### 🛠️ **2. Tool Calling Etiquette (7 Critical Principles)**
- Never mention tool names to users
- Explain rationale before each tool call
- Strict schema adherence validation
- No permission-asking (users expect action)
- Message tool strategy (notify vs. ask)
- Parallel execution optimization (except semantic_search)
- No tool fabrication detection

### 📝 **3. File Editing Strategies**
Three approaches in order of preference:
1. **Line-based search & replace** (for >6 lines) - PREFERRED with line number validation
2. **String replacement** (for small, unique changes) - Requires 3-5 context lines
3. **Insert edit** (last resort) - Uses context markers for insertion

### 🔧 **4. Sandbox Environment Awareness**
- Automatic OS/shell detection (Windows PowerShell vs. Linux bash)
- Python version and runtime detection
- Constraint identification (pip availability, git, native binaries)
- WebContainer-specific limitations (stdlib-only)
- Environment-aware tool adaptation
- Directory and permissions context

### 🔬 **5. Deep Research Planner (4 Phases)**
- **Phase 1**: Requirement deconstruction with semantic dissection (7 elements)
- **Phase 2**: Source analysis with 6-dimensional evaluation + gap analysis
- **Phase 3**: Hierarchical outline generation with reasoning tools assignment
- **Phase 4**: Adversarial self-critique (SASC) using 3 personas + feedback loops

### 🧠 **6. Chain-of-Thought vs. Agentic Reasoning**
- Internal reasoning (CoT) with `<thinking>` tags
- External verification (Agentic) with tool use
- Comparison of limitations and strengths
- Hybrid approach combining both patterns
- Planning phase orchestration

### 🏆 **7. Complete Multi-Agent Research System**
- Full Team-based workflow with 4 specialized agents
- Coordinator orchestrating the 4-phase process
- Information flow management between agents
- Validation and feedback loop handling

The guide includes best practices checklists for all patterns and is ready for production use with your Agno agents in Brazil!  
  
# Citations:  
[1] [Basic Agent Events Handling - Agno](https://docs.agno.com/examples/concepts/agent/events/basic_agent_events)  
[2] [Building an autonomous analytics agent with Agno and ...](https://www.tinybird.co/blog/building-an-analytics-agent-with-agno-and-tinybird)  
[3] [Search & Retrieval - Agno](https://docs.agno.com/concepts/knowledge/core-concepts/search-retrieval)  
[4] [Streaming structured output in Agent Teams · Issue #2812](https://github.com/agno-agi/agno/issues/2812)  
[5] [AI Agent Tool Calling Best Practices Webinar](https://www.youtube.com/watch?v=LU4XdfywiuQ)  
[6] [Getting Started with Agno Agents, uv, and a Dash of RAG Magic](https://www.bitdoze.com/agno-get-start/)  
[7] [Build Your Own AI Stock Portfolio Agent with Agno + AG-UI](https://webflow.copilotkit.ai/blog/build-your-own-ai-stock-portfolio-agent-with-agno-ag-ui)  
[8] [Creating your own tools - Agno](https://docs.agno.com/concepts/tools/custom-tools)  
[9] [TIL you can use "find and replace" built in with anki editor ...](https://www.reddit.com/r/Anki/comments/u64mre/til_you_can_use_find_and_replace_built_in_with/)  
[10] [Process Automation With Agno Multi-Agent Workflows](https://www.youtube.com/watch?v=I0mPWhZPaiI)  
[11] [Discovering and masking environmental features in ...](https://www.diva-portal.org/smash/get/diva2:1662757/FULLTEXT01.pdf)  
[12] [[Feature Request] Deep Research · Issue #2115 · agno-agi ...](https://github.com/agno-agi/agno/issues/2115)  
[13] [Handling "Agent stopped due to iteration limit or time ...](https://www.linkedin.com/pulse/handling-agent-stopped-due-iteration-limit-time-loops-rany-dqkgc)  
[14] [How Autonomous Agents Are Transforming Environmental ...](https://smythos.com/managers/ops/autonomous-agents-in-environmental-monitoring/)  
[15] [Building AI Agents and Teams for Deep Research](https://www.youtube.com/watch?v=lB2b0SPbOEc)  
[16] [Loop agents - Agent Development Kit - Google](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/)  
[17] [An Introduction to AI Agents](https://www.getzep.com/ai-agents/introduction-to-ai-agents/)  
[18] [Building Your AI Research Squad with Agno, Streamlit, and uv](https://www.bitdoze.com/agno-squad/)  
[19] [Introducing Agno - Ashpreet Bedi](https://www.ashpreetbedi.com/articles/introducing-agno)  
[20] [AgentScope 1.0: A Developer-Centric Framework for ...](https://arxiv.org/html/2508.16279v1)  
[21] [Running Agents - Agno](https://docs.agno.com/concepts/agents/running-agents)  
[22] [Enhanced Structured Output Support in Agent Class](https://github.com/agno-agi/agno/issues/2963)  
[23] [Agents - Docs by LangChain](https://docs.langchain.com/oss/python/langchain/agents)  
[24] [Agent Loop and how to get notified of tool calls and results ...](https://learn.microsoft.com/en-ie/answers/questions/2288230/agent-loop-and-how-to-get-notified-of-tool-calls-a)  
[25] [How to Keep LLM Outputs Predictable Using Pydantic ...](https://www.freecodecamp.org/news/how-to-keep-llm-outputs-predictable-using-pydantic-validation/)  
[26] [Orchestrator-Worker Agents: A Practical Comparison of ...](https://arize.com/blog/orchestrator-worker-agents-a-practical-comparison-of-common-agent-frameworks/)  
[27] [How to build an analytics agent with Agno and Tinybird](https://www.tinybird.co/blog/how-to-build-an-analytics-agent-with-agno-and-tinybird-step-by-step)  
[28] [How to get structured output from LLMs with AGNO and ...](https://www.linkedin.com/posts/veerakumar-murugesan-78030025a_ai-llms-pydantic-activity-7307484099298897920-QkNv)  
[29] [langgraph/how-tos/react-agent-from-scratch/ #1657](https://github.com/langchain-ai/langgraph/discussions/1657)  
[30] [[Bug] Team Leader unable to detect Agent response #3370](https://github.com/agno-agi/agno/issues/3370)