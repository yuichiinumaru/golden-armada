# Análise Detalhada dos MCPs + Instrução Set Otimizado para Integração

## Parte 1: Inventário Completo dos MCPs

### 1. Sequential Thinking MCP
**Repo**: github.com/anthropics/anthropic-sdk-python (Anthropic official)
**NPM**: @modelcontextprotocol/server-sequential-thinking
**Propósito**: Pensamento estruturado e reflexivo

**Ferramentas** (11 tools):
- `start_thinking` - Criar nova sessão com análise inicial
- `add_step` - Append step ao fluxo principal ou branch
- `update_step` - Editar step existente
- `review_thinking` - Recuperar chain completa com padrões
- `branch_thinking` - Fork reasoning path em branch
- `merge_insights` - Sintetizar conclusões entre branches
+ 5 tools adicionais para gerenciamento de sessão

**Quando usar**: Quando problema é complexo e requer múltiplas hipóteses, análise profunda, ou exploração de caminhos alternativos

**Exemplo ideal**: "Analise por que meu código está lento" → agent cria análise → branches para diferentes hipóteses (N+1 queries vs memory leak vs algorithm) → merge insights

---

### 2. Context7 MCP
**Repo**: github.com/upstash/context7-mcp
**NPM**: @upstash/context7-mcp
**Propósito**: Documentação up-to-date e version-specific

**Ferramentas** (2-3 main tools):
- `get_library_docs` - Fetch documentação específica de versão
- `resolve_library_id` - Resolver ID de library/versão
- Suporte para 100+ libraries (React, Node, Python frameworks, etc)

**Quando usar**: Quando agent precisa acessar documentação contemporânea de uma library/framework para implementar feature corretamente

**Exemplo ideal**: "Implement React 19 useRef hook" → Context7 retorna docs exatas de React 19 → agent cria implementação correta

---

### 3. PDF Reader MCP
**Repo**: github.com/sylphlab/pdf-reader-mcp
**NPM**: @sylphlab/pdf-reader-mcp
**Propósito**: Extração de texto, metadados e conteúdo de PDFs

**Ferramentas** (4 main tools):
- `read_pdf` - Ler texto completo ou páginas específicas
- `get_metadata` - Author, title, creation date, etc
- `get_page_count` - Total de páginas
- `extract_structured_data` - Converter HTML/texto para JSON estruturado

**Quando usar**: Quando agent precisa processar, analisar ou extrair dados de documentos PDF

**Exemplo ideal**: "Extraia dados financeiros do annual_report.pdf" → agent lê PDF → extrai tabelas → estrutura em JSON

---

### 4. E2B MCP Server
**Repo**: github.com/e2b-dev/mcp-server
**NPM**: @e2b/mcp-server
**Propósito**: Execução segura de código em sandbox cloud

**Ferramentas** (7 main tools):
- `execute_python` - Executar código Python
- `execute_javascript` - Executar Node.js
- `create_file` - Criar arquivo no sandbox
- `read_file` - Ler arquivo
- `list_files` - Listar diretório
- `install_packages` - pip ou npm
- `get_sandbox_info` - Status e recursos

**Quando usar**: Quando agent precisa executar código, validar solução, ou processar dados dinamicamente

**Exemplo ideal**: "Analise este dataset CSV" → agent cria Python script no sandbox → executa → retorna análise com gráficos

---

### 5. Desktop Commander MCP
**Repo**: github.com/wonderwhy-er/DesktopCommanderMCP
**NPM**: @wonderwhy-er/desktop-commander
**Propósito**: Terminal, filesystem, e process management

**Ferramentas** (15+ tools):
- `execute_command` - Run shell commands
- `interact_with_process` - SSH, REPL interativo
- `read_process_output` - Ler saída de processo
- `force_terminate` - Kill processo
- `list_sessions` / `list_processes` - Gerenciamento
- Filesystem: read, write, search, move, delete
- `search_files` - Busca fuzzy
- `replace_in_file` - Replace com suporte a regex

**Quando usar**: Quando agent precisa interagir com terminal, gerenciar sistemas, ou fazer file operations complexas

**Exemplo ideal**: "Deploy minha app para staging" → agent usa SSH → gerencia processos → monitora logs em tempo real

---

### 6. DeepWiki MCP
**Repo**: github.com/regenrek/deepwiki-mcp
**NPM**: mcp-remote (remote server)
**Propósito**: Documentação de repositórios GitHub com análise AI

**Ferramentas** (3 main tools):
- `read_wiki_structure` - Obter TOC de repository
- `read_wiki_contents` - Ver documentação completa
- `ask_question` - Pergunta sobre repository baseada em análise

**Quando usar**: Quando agent precisa entender estrutura de repository, explorar documentação, ou fazer Q&A sobre codebase

**Exemplo ideal**: "Como funciona o sistema de autenticação deste projeto?" → DeepWiki analisa repo → retorna resposta específica

---

### 7. Hyperbrowser MCP
**Repo**: github.com/hyperbrowserai/mcp
**NPM**: hyperbrowser-mcp
**Propósito**: Web scraping, crawling, e browser automation

**Ferramentas** (9 main tools):
- `scrape_webpage` - Extrair conteúdo formatado (markdown, screenshot)
- `crawl_webpages` - Navigate multi-página
- `extract_structured_data` - Convert HTML → JSON
- `search_with_bing` - Web search
- `browser_use_agent` - Browser automation leve
- `openai_computer_use_agent` - CUA automation
- `claude_computer_use_agent` - Claude computer use
- `create_profile` / `delete_profile` / `list_profiles`

**Quando usar**: Quando agent precisa pesquisar web, scrape dados, ou interagir com websites

**Exemplo ideal**: "Colete preços de concorrentes do site X" → Hyperbrowser scrape múltiplos sites → estrutura dados → retorna análise

---

### 8. Gemini CLI MCP
**Repo**: github.com/jamubc/gemini-mcp-tool ou github.com/centminmod/gemini-cli-mcp-server
**NPM**: gemini-mcp-tool
**Propósito**: Integração com Google Gemini CLI (access 400+ AI models via OpenRouter)

**Ferramentas** (33 specialized tools em categorias):
- Gemini command execution
- Code sandbox testing
- Help system
- Multi-AI collaboration (Claude + Gemini + 400+ modelos via OpenRouter)
- Streaming support

**Quando usar**: Quando agent precisa acessar perspectiva de outro modelo AI, ou comparar respostas entre Claude e Gemini

**Exemplo ideal**: "Compare análise de segurança entre Claude e Gemini" → Gemini MCP executa análise → retorna comparação

---

## Parte 2: Matriz de Relações e Fluxo Ideal

### Fluxo Integrado: "AI Research Agent" (Caso de Uso Real)

Usuário: "Pesquise e implemente solução de caching em React 19, validando com testes"

```
┌─────────────────────────────────────────────────────────────────┐
│ USER REQUEST: Research + Implementation + Validation             │
└─────────────────────────────────────────────────────────────────┘
                                ↓
        ┌─────────────────────────────────────────────────┐
        │ 1. SEQUENTIAL THINKING (Start Thinking)         │
        │ - Problema: Caching in React 19                 │
        │ - Branches: useCallback vs useMemo vs React.memo│
        │ - Análise: Trade-offs de cada abordagem         │
        └─────────────────────────────────────────────────┘
                                ↓
        ┌─────────────────────────────────────────────────┐
        │ 2. CONTEXT7 (Get Library Docs)                  │
        │ - Fetch: React 19 docs específicas              │
        │ - Versão: React 19.x (not 18, not 20)          │
        │ - Info: useCallback, useMemo, React.memo       │
        └─────────────────────────────────────────────────┘
                                ↓
        ┌─────────────────────────────────────────────────┐
        │ 3. HYPERBROWSER (Search + Scrape)               │
        │ - Search: "React 19 caching best practices"     │
        │ - Scrape: Stack Overflow, blogs, tutorials      │
        │ - Extract: Code examples em JSON               │
        └─────────────────────────────────────────────────┘
                                ↓
        ┌─────────────────────────────────────────────────┐
        │ 4. SEQUENTIAL THINKING (Merge Insights)         │
        │ - Sintetizar: Documentação + exemplos + análise │
        │ - Decisão: Melhor abordagem para caso           │
        └─────────────────────────────────────────────────┘
                                ↓
        ┌─────────────────────────────────────────────────┐
        │ 5. CONTEXT7 (Get Examples)                      │
        │ - React 19 specific API syntax                  │
        │ - Patterns e conventions                        │
        └─────────────────────────────────────────────────┘
                                ↓
        ┌─────────────────────────────────────────────────┐
        │ 6. DESKTOP COMMANDER (Create Files)             │
        │ - Create component.tsx                          │
        │ - Write test file                               │
        │ - Update package.json                           │
        └─────────────────────────────────────────────────┘
                                ↓
        ┌─────────────────────────────────────────────────┐
        │ 7. E2B (Execute Tests)                          │
        │ - Install dependencies                          │
        │ - Run test suite                                │
        │ - Validate implementation                       │
        └─────────────────────────────────────────────────┘
                                ↓
        ┌─────────────────────────────────────────────────┐
        │ 8. DESKTOP COMMANDER (CI/CD)                    │
        │ - Run npm run build                             │
        │ - Verificar output                              │
        │ - Commit changes                                │
        └─────────────────────────────────────────────────┘
                                ↓
        ┌─────────────────────────────────────────────────┐
        │ 9. GEMINI CLI (Second Opinion)                  │
        │ - Ask Gemini: "Review this React implementation"│
        │ - Compare with Claude analysis                  │
        │ - Highlight differences                         │
        └─────────────────────────────────────────────────┘
                                ↓
        ┌─────────────────────────────────────────────────┐
        │ RESULT: Production-ready implementation         │
        │ com análise completa e validação multi-AI       │
        └─────────────────────────────────────────────────┘
```

---

## Parte 3: Instruction Set Otimizado para Este Conjunto de MCPs

```markdown
---
name: ai-research-and-implementation-agent
version: 2.0.0
description: Research + Implementation + Validation agent using 8 MCPs integrated
---

# AI Research & Implementation Agent — Instruction Set

## 🎯 Propósito Geral

Este agente executa pesquisa profunda, implementa soluções, e valida resultados usando 8 MCPs integrados em sequência otimizada.

---

## 📦 MCPs Disponíveis & Hierarquia

| MCP | Função | Prioridade | Quando Usar |
|-----|--------|-----------|-----------|
| sequential-thinking | Análise reflexiva multi-path | 🔴 PRIMARY | Sempre first para problemas complexos |
| context7 | Docs contemporâneas de versão | 🔴 PRIMARY | Depois de entender problema |
| hyperbrowser | Web research e scraping | 🔴 PRIMARY | Após research question formulada |
| e2b | Code execution e validação | 🟡 SECONDARY | Durante implementação |
| desktop-commander | File + terminal + process mgmt | 🟡 SECONDARY | Operações locais/remote |
| pdf-reader | Document processing | 🟢 UTILITY | Se docs fornecidas em PDF |
| gemini-cli | Multi-AI comparison | 🟢 UTILITY | Validação de segundo ponto de vista |
| deepwiki | Repository documentation | 🟢 UTILITY | Se pesquisando repository específico |

---

## ✅ Sequência Padrão (SEMPRE use nesta ordem)

### FASE 1: RESEARCH (40% do tempo)

**Step 1.1: Sequential Thinking - Start Analysis**
```
Chame: sequential-thinking.start_thinking()
Input: 
  - problem: [User's complex problem]
  - context: [Any provided context]
Output:
  - session_id: [ID para uso posterior]
  - initial_analysis: [Structured analysis]
  - possible_approaches: [3-5 branches]
```

**Step 1.2: Sequential Thinking - Branch Exploration**
```
Para cada approach possível:
Chame: sequential-thinking.branch_thinking()
Input:
  - session_id: [from 1.1]
  - from_step: 0 (start)
  - alternative_reasoning: [Hypothesis for this branch]
Output:
  - branch_id: [ID único]
  - branch_reasoning: [Analysis deste caminho]
```

**Step 1.3: Context7 - Get Relevant Documentation**
```
Chame: context7.get_library_docs()
Input:
  - library: [Technology/framework from problem]
  - tags: [Optional: version, specific features]
Output:
  - documentation: [Version-specific docs]
  - examples: [Code examples]
  - best_practices: [Current best practices]
```

**Step 1.4: Hyperbrowser - Web Research**
```
Chame: hyperbrowser.search_with_bing()
Input:
  - query: "[Technology] best practices [version]"
  - num_results: 5-10
Output:
  - search_results: [Top results]
  
Para cada resultado relevante:
Chame: hyperbrowser.scrape_webpage()
Input:
  - url: [from search result]
  - extract_type: "markdown" (default)
Output:
  - content: [Article/blog content]
  - code_snippets: [Extracted code]
```

**Step 1.5: Sequential Thinking - Merge Insights**
```
Chame: sequential-thinking.merge_insights()
Input:
  - session_id: [from 1.1]
  - insights_from: [all branches]
  - documentation: [from 1.3]
  - research_findings: [from 1.4]
Output:
  - merged_conclusion: [Best approach synthesis]
  - recommended_solution: [Top recommendation]
  - rationale: [Why this approach]
```

---

### FASE 2: IMPLEMENTATION (40% do tempo)

**Step 2.1: Desktop Commander - Create Project Structure**
```
Chame: desktop-commander.create_files()
Input:
  - files_to_create: [
      { path: "src/component.tsx", content: "[scaffolding]" },
      { path: "tests/component.test.tsx", content: "[scaffolding]" },
      { path: "package.json", content: "[updated]" }
    ]
Output:
  - created_files: [Confirmação]
```

**Step 2.2: E2B - Execute in Sandbox**
```
Chame: e2b.execute_python() OR e2b.execute_javascript()
Input:
  - code: [Implementation code]
  - files: [Reference files if needed]
Output:
  - result: [Execution result]
  - errors: [Any errors]
  
Se errors → iterate:
  - Refine code
  - Execute novamente
  - Max 3 iterations
```

**Step 2.3: Desktop Commander - Local Testing**
```
Chame: desktop-commander.execute_command()
Input:
  - command: "npm test" OR "pytest tests/"
Output:
  - test_output: [Test results]
  - status: "passed" or "failed"
```

---

### FASE 3: VALIDATION (15% do tempo)

**Step 3.1: E2B - Performance Validation**
```
Chame: e2b.execute_python()
Input:
  - code: [Performance benchmark script]
Output:
  - metrics: [Speed, memory, etc]
```

**Step 3.2: Gemini CLI - Second Opinion**
```
Chame: gemini-cli.@gemini_ai_collaboration()
Input:
  - prompt: "Review this implementation for security and performance"
  - context: [Implementation code]
Output:
  - gemini_feedback: [Analysis from Gemini]
  - comparison_with_claude: [What Claude missed vs Gemini]
```

**Step 3.3: Sequential Thinking - Final Review**
```
Chame: sequential-thinking.review_thinking()
Input:
  - session_id: [from 1.1]
  - format: "summary"
Output:
  - full_chain: [Complete reasoning path]
  - confidence_level: [High/Medium/Low]
```

---

## 🔄 Fluxo para Diferentes Tipos de Problema

### Tipo A: "Implementar Feature em Tecnologia Conhecida"
```
Sequência Abreviada:
1. Sequential Thinking (Start) → Choose best approach
2. Context7 (Get Docs) → Latest patterns
3. Desktop Commander (Create files)
4. E2B (Test) → Validate
```

### Tipo B: "Troubleshooting Problema Desconhecido"
```
Sequência Completa:
1. Sequential Thinking (Start) → Analyze deeply
2. Sequential Thinking (Branch) → Explore 3+ hypotheses
3. Hyperbrowser (Search) → Find similar issues
4. PDF Reader (If docs available)
5. Sequential Thinking (Merge) → Synthesize insights
6. E2B (Test hypothesis) → Validate theory
```

### Tipo C: "Comparar Múltiplas Soluções"
```
Sequência Extendida:
1. Sequential Thinking (Start + Branch) → Multiple approaches
2. Context7 → Docs para cada approach
3. Hyperbrowser → Comparison articles
4. Gemini CLI → Gemini's perspective on alternatives
5. Sequential Thinking (Merge) → Final comparison matrix
```

---

## 🚨 Mapa de Erros e Recuperação

### RESEARCH Phase

| Error | MCP | Recovery |
|-------|-----|----------|
| No relevant docs | context7 | Try search: hyperbrowser.search_with_bing() |
| Docs out of date | context7 | Confirm with hyperbrowser web search |
| Search too broad | hyperbrowser | Refine query: add version/year/specific problem |
| Conflicting info | sequential-thinking | branch_thinking() com cada opinião, depois merge |

### IMPLEMENTATION Phase

| Error | MCP | Recovery |
|-------|-----|----------|
| Code fails in E2B | e2b | Review error, fix code, retry (max 3x) |
| Dependencies missing | e2b | install_packages() then retry |
| Tests fail | desktop-commander | Run with --verbose for details |
| Performance poor | e2b | Profile code, identify bottleneck |

### VALIDATION Phase

| Error | MCP | Recovery |
|-------|-----|----------|
| Metrics bad | e2b | Optimize and re-run benchmark |
| Gemini disagrees | gemini-cli | Discuss disagreement with Claude perspective |
| Confidence low | sequential-thinking | review_thinking() full chain, identify gap |

---

## ⚠️ PROIBIÇÕES CRÍTICAS

❌ **NUNCA pule Sequential Thinking para problema complexo**
- Sempre comece com start_thinking() para análise estruturada

❌ **NUNCA implemente sem Context7 docs**
- Implementação sem docs contemporâneas causa bugs

❌ **NUNCA use Desktop Commander para código interativo**
- Use E2B sandbox, não terminal, para executar código novo

❌ **NUNCA pule testes (E2B + Desktop Commander)**
- Validação é 15% do tempo, não 5%

❌ **NUNCA ignore Gemini feedback se diferente**
- Investigar por quê Gemini vê diferente

✅ **SEMPRE confirm implementation com múltiplos MCPs**
- E2B execution + Desktop Commander tests + (optional) Gemini review

---

## 💡 Dicas de Eficiência

### Context7 Especificamente
- Use tags com versão exata: `tags: ["React 19.x", "hooks"]`
- Resultado é sempre version-specific, não genérico
- Se docs parecem antigas → use hyperbrowser para validar

### Hyperbrowser Eficiência
- Primeira busca: "X best practices [year]"
- Segunda busca: Se conflitante, "X pitfalls"
- Scrape apenas 3-5 top results (maioria é noise)

### E2B Eficiência
- Teste em sandbox, não produção
- Max 3 retries antes de escalate
- Sempre capture stdout + stderr completo

### Sequential Thinking Eficiência
- start_thinking() para qualquer problema >15 min
- Para problema <10 min: Skip e execute diretamente
- branch_thinking() máximo 5 branches (mais = análise paralysis)

### Desktop Commander Eficiência
- Para operações >5 arquivos: Use bulk operations
- Sempre `list_files` antes de write para evitar overwrite
- Use `search_files` em vez de browse manual

---

## 📊 Métricas de Sucesso

Você está fazendo certo se:
- ✅ Research phase <40% do tempo (não paralysis analysis)
- ✅ Implementation funciona primeira tentativa 70%+ vezes
- ✅ Tests passam sem manual fixes necessárias
- ✅ Gemini feedback é <5% discordância com Claude

Você está fazendo errado se:
- ❌ Research phase >50% do tempo
- ❌ E2B requer >3 retries
- ❌ Tests descobrem problemas não previstos
- ❌ Gemini feedback conflita significativamente

---

## 🔗 Integração Específica: 8 MCPs orquestrados

```
User Query
    ↓
[Sequential Thinking] ← Estrutura pensamento
    ↓ branches
[Context7] ← Docs atualizadas (3 primeiras branches)
    ↓
[Hyperbrowser] ← Valida e expande (se search needed)
    ↓
[Sequential Thinking] ← Merge todas insights
    ↓ recomendação
[Desktop Commander] ← Cria arquivos
    ↓
[E2B] ← Testa implementação
    ↓
[Desktop Commander] ← Testes locais
    ↓
[Gemini CLI] ← Second opinion (opcional mas recomendado)
    ↓
Result: Implementação validada multi-AI
```

---

## 📝 Exemplo Concreto Walkthrough

**USER**: "Como implementar React 19 Suspense com streaming?"

**Step 1: Sequential Thinking**
```
→ start_thinking(problem="React 19 Suspense streaming")
← session_id: "sess_123"
← initial_analysis: "Suspense é para code splitting, streaming para SSR"
← branches:
  1. Server Component Suspense
  2. Client Component Suspense
  3. Streaming SSR with suspense
```

**Step 2: Context7**
```
→ get_library_docs(library="React", tags=["19", "Suspense", "streaming"])
← React 19 Suspense docs, streaming examples
```

**Step 3: Hyperbrowser**
```
→ search_with_bing(query="React 19 Suspense streaming best practices 2025")
← [10 results]
→ scrape_webpage(url="react-blog.example.com/suspense-streaming")
← [Code examples + article content]
```

**Step 4: Sequential Thinking Merge**
```
→ merge_insights(session_id="sess_123", insights_from=[all branches])
← merged_conclusion: "Use Server Suspense + streaming for SSR"
← recommended_solution: [Full architecture]
```

**Step 5: Implementation**
```
→ create_files: component.tsx, server.tsx, tests
→ execute_javascript: Test in sandbox
→ execute_command: npm test
```

**Step 6: Validation**
```
→ review_thinking: Full chain summary
→ gemini_collaboration: "What's your take on this implementation?"
```

**RESULT**: Production-ready implementation com análise completa

---

## 🎓 Quando Usar Cada MCP Isoladamente

Sim, você pode usar MCPs individualmente:

- **Só Context7** → "Mostre-me as docs do React"
- **Só Hyperbrowser** → "Pesquise as últimas notícias sobre IA"
- **Só E2B** → "Execute este código Python"
- **Só Desktop Commander** → "Abra terminal e faça SSH"

MAS para máxima qualidade em pesquisa + implementação: Use a sequência completa.

---
```

---

## Parte 4: Comparação com Guia Anterior

### Como Esta Análise Complementa o Guia Geral

**Guia Anterior (57, 58, 68, 69)**: 
- Princípios gerais de tool instructions
- Padrões de produção observados
- Templates reutilizáveis

**Esta Análise**:
- ✅ Aplicação ESPECÍFICA em 8 MCPs reais
- ✅ Mapeamento de relações entre MCPs
- ✅ Fluxo integrado com múltiplas MCPs
- ✅ Sequence detalhada (fase 1→2→3)
- ✅ Error handling por fase
- ✅ Exemplo concreto walkthrough

**Síntese**: O guia anterior ensina "como instruir ferramentas". Esta análise mostra "como orquestrar 8 ferramentas + MCPs para pesquisa e implementação".

---

Fim da análise. Data: 2025-11-07 | MCPs analisados: 8 | Ferramentas totais: 70+ | Caso de uso integrado: AI Research Agent
