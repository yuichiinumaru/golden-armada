# Quick Reference: 8 MCPs + Integrated Instruction Set

## Tabela Rápida de MCPs

| MCP | Tools | Use When | Setup |
|-----|-------|----------|-------|
| **sequential-thinking** | 11 | Problema complexo, múltiplas hipóteses | `npx @modelcontextprotocol/server-sequential-thinking` |
| **context7** | 2-3 | Docs de versão específica | `npx @upstash/context7-mcp` + API key |
| **pdf-reader** | 4 | Processar PDF, extrair dados | `npx @sylphlab/pdf-reader-mcp` |
| **e2b** | 7 | Executar código, sandbox | `npx @e2b/mcp-server` + API key |
| **desktop-commander** | 15+ | Terminal, files, SSH, process | `npx @wonderwhy-er/desktop-commander@latest` |
| **deepwiki** | 3 | Docs de repo GitHub, Q&A | `mcp-remote https://mcp.deepwiki.com/mcp` |
| **hyperbrowser** | 9 | Web scraping, search, automation | `npx hyperbrowser-mcp` + API key |
| **gemini-cli** | 33 | Multi-AI comparison, 400+ models | `npx gemini-mcp-tool` |

---

## Casos de Uso Padrão

### Caso 1: "Pesquisar + Implementar + Validar" (Recomendado para estas MCPs)
```
Fluxo: Sequential ➜ Context7 ➜ Hyperbrowser ➜ E2B ➜ Desktop ➜ Gemini
Tempo: 1-2 horas
Output: Production-ready code + análise multi-AI
```

### Caso 2: "Só Implementar Código Rápido"
```
Fluxo: Context7 ➜ Desktop Commander ➜ E2B
Tempo: 10-30 min
Output: Código testado
```

### Caso 3: "Pesquisar só (sem implementação)"
```
Fluxo: Hyperbrowser ➜ Sequential Thinking
Tempo: 15-45 min
Output: Análise + recomendações
```

### Caso 4: "Troubleshooting Profundo"
```
Fluxo: Sequential ➜ Hyperbrowser ➜ E2B (teste hipótese)
Tempo: 30-90 min
Output: Root cause + solução validada
```

---

## Arquitetura Integrada (Visual)

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER QUERY                               │
│                  (Pesquisa + Implementação)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
    ╔═════════════╗                  ╔═════════════════╗
    │ Sequential  │                  │   Context7      │
    │ Thinking    │◄─────────────────│   (Get Docs)    │
    │             │ (branches)       │                 │
    │ (Analysis & │                  ╚═════════════════╝
    │  hypotheses)│
    ╚═════╤═══╤═╤╝
          │   │ │
    ┌─────┘   │ └──────────┐
    │         │            │
    ▼         ▼            ▼
 ┌─────┐  ┌──────────┐  ┌──────────┐
 │Merge│  │Hyperbrowser  │DeepWiki
 │     │  │(Search+Scrape)        │
 └─────┘  │          │  │
    │     └──────────┘  └──────────┘
    │
    └─────────────────────┬─────────────────────┐
                          │                     │
                    ┌─────▼────┐         ┌─────▼──────┐
                    │Desktop   │         │ E2B        │
                    │Commander │         │ (Execute   │
                    │(Files)   │         │  & Test)   │
                    └─────┬────┘         └─────┬──────┘
                          │                     │
                    ┌─────▼─────────────────────▼──────┐
                    │   Validation & Testing            │
                    │   - Tests passed?                 │
                    │   - Performance OK?               │
                    │   - All edge cases?               │
                    └─────┬──────────────────────────────┘
                          │
                    ┌─────▼──────────────┐
                    │ Gemini CLI         │
                    │ (Second Opinion)   │
                    │ (Optional)         │
                    └─────┬──────────────┘
                          │
                    ┌─────▼──────────────────────┐
                    │  FINAL RESULT              │
                    │  Validated + Multi-AI      │
                    │  Analyzed Implementation   │
                    └────────────────────────────┘
```

---

## Prioridades por Tipo de Problema

### "Implementar Feature Conhecida" (Tempo: 10-30 min)
```
Priority: Context7 > Desktop > E2B
Sequence: 
  1. Context7: Get docs
  2. Desktop: Create files
  3. E2B: Test
Salte: Sequential, Hyperbrowser, Gemini
```

### "Implementar Feature Desconhecida" (Tempo: 1-2h)
```
Priority: Sequential > Context7 > Hyperbrowser > E2B > Gemini
Sequence:
  1. Sequential: Analyze + branch
  2. Context7: Get docs
  3. Hyperbrowser: Research
  4. Sequential: Merge insights
  5. Desktop + E2B: Implement + test
  6. Gemini: (Optional) Review
Salte: DeepWiki, PDF
```

### "Troubleshooting Bug" (Tempo: 30-90 min)
```
Priority: Sequential > Hyperbrowser > E2B > Desktop
Sequence:
  1. Sequential: Branch hypotheses
  2. Hyperbrowser: Similar issues
  3. E2B: Test each hypothesis
  4. Sequential: Synthesize solution
  5. Desktop: Implement fix
Salte: Context7 (unless bug is version-specific)
```

### "Comparar Alternativas" (Tempo: 45 min-2h)
```
Priority: Sequential > Context7 > Hyperbrowser > Gemini
Sequence:
  1. Sequential: Branch alternatives (max 5)
  2. Context7: Docs for each
  3. Hyperbrowser: Articles comparing
  4. Sequential: Merge comparison
  5. Gemini: What does Gemini think?
Salte: E2B (unless benchmarking needed)
```

---

## Error Handling Flowchart

```
┌─────────────┐
│ Error in    │
│ Phase X?    │
└────┬────────┘
     │
     ├─→ RESEARCH Phase Error
     │   ├─ "No docs found"? → Try Hyperbrowser
     │   ├─ "Results conflict"? → Sequential.branch_thinking()
     │   └─ "Search too broad"? → Refine query
     │
     ├─→ IMPLEMENTATION Phase Error
     │   ├─ "Code fails"? → E2B retry (max 3x)
     │   ├─ "Missing deps"? → E2B.install_packages()
     │   ├─ "Tests fail"? → Desktop --verbose
     │   └─ "After 3 retries" → Escalate
     │
     └─→ VALIDATION Phase Error
         ├─ "Perf bad"? → Profile + optimize
         ├─ "Gemini disagrees"? → Investigate why
         └─ "Low confidence"? → Sequential.review_thinking()
```

---

## Command Cheat Sheet

### Install All 8 MCPs

```bash
# Sequential Thinking
npx -y @modelcontextprotocol/server-sequential-thinking

# Context7 (requires API key)
export CONTEXT7_API_KEY="your_key"
npx -y @upstash/context7-mcp

# PDF Reader
npx -y @sylphlab/pdf-reader-mcp

# E2B (requires API key)
export E2B_API_KEY="your_key"
npx -y @e2b/mcp-server

# Desktop Commander
npx -y @wonderwhy-er/desktop-commander@latest

# DeepWiki
npx -y mcp-remote https://mcp.deepwiki.com/mcp

# Hyperbrowser (requires API key)
export HYPERBROWSER_API_KEY="your_key"
npx -y hyperbrowser-mcp

# Gemini CLI
npx -y gemini-mcp-tool
```

### Test MCP Connection

```bash
# Inspect any MCP
npx -y @modelcontextprotocol/inspector npx @modelcontextprotocol/server-sequential-thinking
```

---

## Instruction Set Template (Minimalista)

Se você quer começar AGORA sem ler tudo:

```markdown
---
name: research-implementation-agent
description: Research + implement + validate using 8 MCPs
---

# Quick Instruction Set

## Sequence (ALWAYS in this order)

1. **Sequential Thinking** (if complex problem)
   - start_thinking → branch_thinking → merge_insights

2. **Context7** (always)
   - get_library_docs for technology

3. **Hyperbrowser** (if research needed)
   - search + scrape top 3-5 results

4. **Desktop Commander** (when implementing)
   - create_files + execute_command

5. **E2B** (always test)
   - execute_python/javascript + validate

6. **Gemini CLI** (optional)
   - Ask for second opinion

## Error Recovery

- Research phase: Retry search with refined query
- Implementation phase: E2B retry max 3x then escalate
- Validation phase: Profile and optimize

## Metrics

Success = 
- Tests pass first try 70%+
- Implementation under 1h
- No manual fixes needed

---
```

---

## Próximos Passos

1. ✅ Você tem **guia teórico** (57, 58)
2. ✅ Você tem **padrões de produção** (68, 69)
3. ✅ Você tem **8 MCPs análise** (100)
4. ✅ Você tem **quick reference** (este documento)

**Agora**:
- [ ] Pick a use case (pesquisa simples? implementação? troubleshooting?)
- [ ] Copy instruction set relevante
- [ ] Setup os 3-5 MCPs que precisa
- [ ] Test com agente real
- [ ] Refine based on results

---

## Support Matrix

| Pergunta | Resposta | Arquivo |
|----------|----------|---------|
| Como instruir ferramentas em geral? | Guia completo + princípios | 57 |
| Templates prontos | YAML, JSON, Markdown | 58, 69 |
| Padrões de repos reais | 15+ repos, 610+ agentes | 68 |
| Análise dos 8 MCPs? | Inventário completo + workflow | 100 |
| Começar agora? | Quick reference | este doc |

---

Fim. Ready to implement? Pick your use case e go! 🚀
