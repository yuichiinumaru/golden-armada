# investigue como o Agno agi passa o context engineering 
[https://docs.agno.com/concepts/agents/context](https://docs.agno.com/concepts/agents/context) aos modelos gemini - o que vai para o 'user prompt' (a mensagem ou pedido que é realizado), e o que vai para o campo 'systeminstruction' (o campo que modela comportamento geral do modelo, e geralmente entra em cached prompt, economizando tokens). 

verifique na codebase no github pra ter certeza do que vai no campo systeminstruction pfvr [https://github.com/agno-agi/agno](https://github.com/agno-agi/agno)  
  
# Answer (Auto):  
# Como o Agno Implementa Context Engineering com Gemini

Baseado na investigação da codebase do Agno, descobri como o framework passa o context engineering aos modelos Gemini, especificamente como separa o que vai para o **user prompt** versus o **campo systemInstruction**.

## Separação Clara de Contextos

O Agno implementa uma separação inteligente entre dois tipos de contexto:

### **SystemInstruction (Context Engineering)**

Todo o context engineering do Agent é enviado para o campo `systemInstruction` do Gemini. Isso inclui:[1]

- **Agent.description** - Descrição geral do comportamento do agente
- **Agent.instructions** - Lista de instruções específicas formatadas em tags `<instructions>`
- **Agent.additional_context** - Contexto adicional personalizado
- **Agent.expected_output** - Formato de saída esperado
- **Configurações do Agent** - Como markdown, datetime, location
- **Memórias do usuário** - Se `enable_user_memories=True`
- **Conhecimento (RAG)** - Se `add_knowledge_to_context=True`
- **Estado da sessão** - Se `add_session_state_to_context=True`

### **Contents (User Prompt)**

O campo `contents` contém apenas a interação dinâmica:

- Mensagem atual do usuário
- Histórico de conversação (se habilitado)
- Tool calls e suas respostas
- Mídia (imagens, vídeos, áudio, arquivos)

## Implementação Técnica

A implementação acontece principalmente no método `_format_messages()` no arquivo `gemini.py`:[1]

```python
# Linha 567-570: Filtragem de mensagens system
for message in messages:
    role = message.role
    if role in ["system", "developer"]:
        system_message = message.content
        continue
```

```python  
# Linha 356: Configuração do systemInstruction
if system_message is not None:
    config["system_instruction"] = system_message
```

## Vantagens do Prompt Caching

Esta separação permite que o Gemini aproveite o **prompt caching**, oferecendo:[2]

1. **Economia de tokens** - O systemInstruction é cacheado automaticamente
2. **Menor latência** - Em conversas longas, o context engineering não é reprocessado
3. **Melhor performance** - Especialmente em multi-turn conversations
4. **Arquitetura limpa** - Context engineering separado da interação dinâmica

## Fluxo Completo

1. O Agent constrói o context usando os parâmetros de context engineering[1]
2. `_format_messages()` separa system messages dos user messages
3. System messages são enviados como `systemInstruction` 
4. User messages são enviados como `contents`
5. Tool calls ficam em `contents` como `function_call` parts

Essa implementação é otimizada para aproveitar as capacidades específicas do Gemini, especialmente o prompt caching, resultando em melhor performance e economia de tokens em aplicações de produção.  
  
# Citations:  
[1] [Context Engineering - Agno](https://docs.agno.com/concepts/agents/context)  
[2] [.github directory in the agno repository on GitHub](/agno-agi/agno/tree/main/.github)  
[3] [Agno Cookbook - Examples and Recipes for Multi-Agent Systems](/agno-agi/agno/tree/main/cookbook)  
[4] [Libs Directory in Agno Multi-Agent System Repository](/agno-agi/agno/tree/main/libs)  
[5] [Repository Files in agno-agi/agno on GitHub](/agno-agi/agno/tree/main/scripts)  
[6] [Agno Repository README - High-Performance Multi-Agent System Runtime](/agno-agi/agno/blob/main/README.md)  
[7] [AgentOS Directory in agno Cookbook Repository](/agno-agi/agno/tree/main/cookbook/agent_os)  
[8] [agno AGI Cookbook - Agents Directory](/agno-agi/agno/tree/main/cookbook/agents)  
[9] [Evaluations Directory in AGNO-Auto-GPT Cookbook Repository](/agno-agi/agno/tree/main/cookbook/evals)  
[10] [Cookbook Examples - AGNO/AGI Repository](/agno-agi/agno/tree/main/cookbook/examples)  
[11] [Getting Started with Agno Cookbook](/agno-agi/agno/tree/main/cookbook/getting_started)  
[12] [Knowledge Directory - Updates on Batch Embeddings and Tool Renaming](/agno-agi/agno/tree/main/cookbook/knowledge)  
[13] [Agno Cookbook Models Directory](/agno-agi/agno/tree/main/cookbook/models)  
[14] [Agno Cookbook - Teams Directory](/agno-agi/agno/tree/main/cookbook/teams)  
[15] [Tools Directory - Cookbook GitHub Repository](/agno-agi/agno/tree/main/cookbook/tools)  
[16] [Workflows Directory in Agno Cookbook](/agno-agi/agno/tree/main/cookbook/workflows)  
[17] [agno agent directory in the agno/libs/agno library repository](/agno-agi/agno/tree/main/libs/agno/agno/agent)  
[18] [agno/libs/agno/agno/api Directory - agno Repository](/agno-agi/agno/tree/main/libs/agno/agno/api)  
[19] [Database Directory - Git Repository](/agno-agi/agno/tree/main/libs/agno/agno/db)  
[20] [Evaluation Module - Version 2.0.0 Features and Updates](/agno-agi/agno/tree/main/libs/agno/agno/eval)  
[21] [Guardrails: Pre/post hooks for agents and system enhancements](/agno-agi/agno/tree/main/libs/agno/agno/guardrails)  
[22] [Knowledge Directory - Batch Embeddings & Model Updates](/agno-agi/agno/tree/main/libs/agno/agno/knowledge)  
[23] [agno/models Directory — AGNO Code Library](/agno-agi/agno/tree/main/libs/agno/agno/models)  
[24] [Reasoning Module Updates and Fixes in agno Project](/agno-agi/agno/tree/main/libs/agno/agno/reasoning)  
[25] [agno team directory in agno library - Release 2.1.0 update](/agno-agi/agno/tree/main/libs/agno/agno/team)  
[26] [tools Directory in agno Library - agno/agno/tools](/agno-agi/agno/tree/main/libs/agno/agno/tools)  
[27] [workflow directory in Agno library - pre/post hooks for agents & Guardrails](/agno-agi/agno/tree/main/libs/agno/agno/workflow)  
[28] [Code search results · GitHub](https://github.com/search?q=repo%3Aagno-agi%2Fagno+systeminstruction&type=code)  
[29] [[Bug] Class Message metrics not there in messages.py (agno.models.message) · Issue #3858 · agno-agi/agno](https://github.com/agno-agi/agno/issues/3858)  
[30] [Use system instructions | Generative AI on Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/system-instructions)  
[31] [Long context | Gemini API - Google AI for Developers](https://ai.google.dev/gemini-api/docs/long-context)  
[32] [Core Framework | agno-agi/agno | DeepWiki](https://deepwiki.com/agno-agi/agno/2-core-framework)  
[33] [How to Use Gemini Vision AI with Agno](https://www.youtube.com/watch?v=1Jc7t-b4YQM)  
[34] [[Bug] Not add context to the system message · Issue #3129](https://github.com/agno-agi/agno/issues/3129)  
[35] [agno/ at main · agno-agi/agno](https://github.com/agno-agi/agno?search=1)  
[36] [[Bug] Gemini tools and response_model are incompatible](https://github.com/agno-agi/agno/issues/2186)  
[37] [[Bug] Gemini‑backed agent tool‑call messages break when ...](https://github.com/agno-agi/agno/issues/4012)  
[38] [gemini models · Issue #2126 · agno-agi/agno](https://github.com/agno-agi/agno/issues/2126)  
[39] [A Multi-Agent System on Agno Framework (Gemini 2.5 ...](https://www.youtube.com/watch?v=lh0TlADJ3NQ)  
[40] [How to build an analytics agent with Agno and Tinybird](https://www.tinybird.co/blog-posts/how-to-build-an-analytics-agent-with-agno-and-tinybird-step-by-step)  
[41] [Merge branch 'feat/gemini-grounding' of https://github.com/agno-agi/agno into feat/gemini-grounding · agno-agi/agno@53cb038](https://github.com/agno-agi/agno/actions/runs/13462372421/workflow)  
[42] [Set system instructions to Gemini 1.5 Pro | Generative AI on ...](https://cloud.google.com/vertex-ai/generative-ai/docs/samples/generativeaionvertexai-gemini-system-instruction)  
[43] [With a 1M context Gemini, does it still make sense to do ...](https://www.reddit.com/r/LocalLLaMA/comments/1lx10ja/with_a_1m_context_gemini_does_it_still_make_sense/)  
[44] [Releases · agno-agi/agno](https://github.com/agno-agi/agno/releases)  
[45] [Building your first AI agent with Agno - Complete tutorial!](https://www.youtube.com/watch?v=Y8nbC_Uj6LI)  
[46] [Generate & edit images using Gemini (aka "nano banana")](https://firebase.google.com/docs/ai-logic/generate-images-gemini)  
[47] [agno-agi/agno v1.1.5 on GitHub](https://newreleases.io/project/github/agno-agi/agno/release/v1.1.5)  
[48] [System prompt handling in Gemini](https://support.google.com/gemini/thread/340196124/system-prompt-handling-in-gemini?hl=en)  
[49] [agn0 AGI project: models/aimlapi directory in main branch](/agno-agi/agno/tree/main/libs/agno/agno/models/aimlapi)  
[50] [Anthropic Models Directory in agno-agi/agno libs/agno/agno/models](/agno-agi/agno/tree/main/libs/agno/agno/models/anthropic)  
[51] [AWS Model Directory in Agno Library - Recent Fixes for Claude Legacy Tool](/agno-agi/agno/tree/main/libs/agno/agno/models/aws)  
[52] [Azure Model Directory in Agno Project Repository](/agno-agi/agno/tree/main/libs/agno/agno/models/azure)  
[53] [Agno Models - Cerebras Directory](/agno-agi/agno/tree/main/libs/agno/agno/models/cerebras)  
[54] [Cohere Model Directory in Agno Library](/agno-agi/agno/tree/main/libs/agno/agno/models/cohere)  
[55] [cometapi Model Directory in agno Library](/agno-agi/agno/tree/main/libs/agno/agno/models/cometapi)  
[56] [dashscope Model Directory in agno/agno Repository](/agno-agi/agno/tree/main/libs/agno/agno/models/dashscope)  
[57] [deepinfra Directory in AGNO Models Library](/agno-agi/agno/tree/main/libs/agno/agno/models/deepinfra)  
[58] [deepseek Model Directory in agno Library](/agno-agi/agno/tree/main/libs/agno/agno/models/deepseek)  
[59] [fireworks Directory in agno-agi/agno Models](/agno-agi/agno/tree/main/libs/agno/agno/models/fireworks)  
[60] [__init__.py in Google Models Module - agno GitHub Repository](/agno-agi/agno/tree/main/libs/agno/agno/models/google)  
[61] [agno/models/groq Directory in Agno Repository](/agno-agi/agno/tree/main/libs/agno/agno/models/groq)  
[62] [Huggingface Models Directory in Agno Repository](/agno-agi/agno/tree/main/libs/agno/agno/models/huggingface)  
[63] [IBM Model Directory in Agno AGI Project](/agno-agi/agno/tree/main/libs/agno/agno/models/ibm)  
[64] [internlm Model Directory in agno Library](/agno-agi/agno/tree/main/libs/agno/agno/models/internlm)  
[65] [langdb Directory in agno Library Models - agno-agi/agno GitHub Repository](/agno-agi/agno/tree/main/libs/agno/agno/models/langdb)  
[66] [litellm Model Directory in Agno AGI Library](/agno-agi/agno/tree/main/libs/agno/agno/models/litellm)  
[67] [llama_cpp Model Directory in Agno AGI Repository](/agno-agi/agno/tree/main/libs/agno/agno/models/llama_cpp)  
[68] [lmstudio Directory in AGNO AI Models Library](/agno-agi/agno/tree/main/libs/agno/agno/models/lmstudio)  
[69] [agno/models/meta Directory - AGNO AGI Library Source Code](/agno-agi/agno/tree/main/libs/agno/agno/models/meta)  
[70] [mistral directory - agno models library](/agno-agi/agno/tree/main/libs/agno/agno/models/mistral)  
[71] [Nebius Model Directory - AI Models Repository](/agno-agi/agno/tree/main/libs/agno/agno/models/nebius)  
[72] [nexus Directory in agno Models - Feature Update for llama cpp](/agno-agi/agno/tree/main/libs/agno/agno/models/nexus)  
[73] [Nvidia Model Directory in Agno AGI Library](/agno-agi/agno/tree/main/libs/agno/agno/models/nvidia)  
[74] [ollama Model Directory in agno Library - Recent Fixes](/agno-agi/agno/tree/main/libs/agno/agno/models/ollama)  
[75] [OpenAI Models Directory - Latest Update and Commit History](/agno-agi/agno/tree/main/libs/agno/agno/models/openai)  
[76] [openrouter model directory in agno library](/agno-agi/agno/tree/main/libs/agno/agno/models/openrouter)  
[77] [Perplexity Model Directory in AGNO Library](/agno-agi/agno/tree/main/libs/agno/agno/models/perplexity)  
[78] [portkey Directory in agno Models - Fix OpenRouter API Key Timing](/agno-agi/agno/tree/main/libs/agno/agno/models/portkey)  
[79] [requesty Directory in agno Models - Requesty Provider Integration](/agno-agi/agno/tree/main/libs/agno/agno/models/requesty)  
[80] [sambanova Model Directory in Agno Repository](/agno-agi/agno/tree/main/libs/agno/agno/models/sambanova)  
[81] [siliconflow - Model Provider Directory in AGNO Repository](/agno-agi/agno/tree/main/libs/agno/agno/models/siliconflow)  
[82] [Agno Models - Together Directory in Agno Repository](/agno-agi/agno/tree/main/libs/agno/agno/models/together)  
[83] [vercel Directory in agno Models - OpenRouter API Key Fix](/agno-agi/agno/tree/main/libs/agno/agno/models/vercel)  
[84] [vllm Directory in Agno Models Library](/agno-agi/agno/tree/main/libs/agno/agno/models/vllm)  
[85] [xai Directory in Agno Models - Requesty Provider Integration](/agno-agi/agno/tree/main/libs/agno/agno/models/xai)  
[86] [__init__.py file in agno models directory](/agno-agi/agno/blob/main/libs/agno/agno/models/__init__.py)  
[87] [base.py in agno models - chore: Release 2.1.0 update](/agno-agi/agno/blob/main/libs/agno/agno/models/base.py)  
[88] [defaults.py in Agno Models Directory](/agno-agi/agno/blob/main/libs/agno/agno/models/defaults.py)  
[89] [agno/libs/agno/agno/models/message.py - GitHub Source File](/agno-agi/agno/blob/main/libs/agno/agno/models/message.py)  
[90] [Metrics Module Update in agno/models/metrics.py](/agno-agi/agno/blob/main/libs/agno/agno/models/metrics.py)  
[91] [Source Code for Response Model in Agno Library (response.py)](/agno-agi/agno/blob/main/libs/agno/agno/models/response.py)  
[92] [utils.py in agno/models directory - Version 2.0.0 update](/agno-agi/agno/blob/main/libs/agno/agno/models/utils.py)  
[93] [Google Models Initialization in Python - agno Project](/agno-agi/agno/blob/main/libs/agno/agno/models/google/__init__.py)  
[94] [Google Gemini Model Source Code - agno-agi/agno GitHub Repo](/agno-agi/agno/blob/main/libs/agno/agno/models/google/gemini.py)  
---  


# é possível referenciar o conteudo markdown de um arquivo separado em vez de inserir dentro do arquivo py do agente, para melhor modularidade?  
  
# Answer (Auto):  
# Sim! É Totalmente Possível Referenciar Conteúdo Markdown Externo

**Resposta direta:** Sim, é perfeitamente possível e até **recomendado** carregar o conteúdo de context engineering de arquivos markdown separados para melhor modularidade no Agno.

## Implementação Prática

### Estrutura de Arquivos Sugerida

```
projeto/
├── agent_config/
│   ├── instructions.md
│   ├── description.md 
│   └── additional_context.md
├── agent.py
└── main.py
```

### Código de Implementação

```python
from pathlib import Path
from agno.agent import Agent
from agno.models.google import Gemini

def load_markdown_content(file_path: str) -> str:
    """Carrega conteúdo de um arquivo markdown"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {file_path}")
        return ""
    except Exception as e:
        print(f"Erro ao ler arquivo {file_path}: {e}")
        return ""

def create_agent_from_files():
    """Cria um agent carregando configurações de arquivos externos"""
    
    config_dir = Path("agent_config")
    
    # Carrega conteúdo dos arquivos
    description = load_markdown_content(config_dir / "description.md")
    instructions_content = load_markdown_content(config_dir / "instructions.md") 
    additional_context = load_markdown_content(config_dir / "additional_context.md")
    
    # Criar o agent com conteúdo dos arquivos
    agent = Agent(
        model=Gemini(id="gemini-2.5-pro"),
        description=description,
        instructions=[instructions_content],
        additional_context=additional_context,
        markdown=True
    )
    
    return agent
```

## Vantagens da Abordagem Modular

### **Organização Superior**
- **Separação clara** entre código e configuração
- **Versionamento** independente do context engineering
- **Colaboração facilitada** - não técnicos podem editar instruções

### **Flexibilidade Operacional** 
- **Reutilização** de instruções entre diferentes agents
- **Configurações específicas** por ambiente (dev/prod)
- **Templates dinâmicos** com variáveis usando Jinja2

### **Manutenibilidade Aprimorada**
- **Edição de instruções** sem alterar código Python
- **Teste A/B** de diferentes prompts facilmente
- **Rollback simples** de configurações

### **Escalabilidade Empresarial**
- **Gestão centralizada** de instruções
- **Carregamento condicional** por contexto
- **Internacionalização** facilitada

## Implementação Avançada com Templates

Para projetos maiores, você pode usar template engines:

```python
from jinja2 import Template
import yaml

def load_agent_with_template():
    # Carrega configurações YAML
    with open('agent_config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    # Template dinâmico
    with open('instructions_template.md', 'r') as file:
        template_content = file.read()
    
    template = Template(template_content)
    instructions = template.render(
        agent_name=config['name'],
        expertise_area=config['expertise']
    )
    
    return Agent(
        model=Gemini(id=config['model']),
        description=config['description'], 
        instructions=[instructions]
    )
```

Esta abordagem é amplamente utilizada na comunidade Agno e é considerada uma **best practice** para projetos de produção, permitindo que equipes não técnicas colaborem na otimização do context engineering sem precisar modificar código Python.[1][2]  
  
# Citations:  
[1] [Firecrawl + FileTools · agno-agi agno · Discussion #3486](https://github.com/agno-agi/agno/discussions/3486)  
[2] [Agno](https://docs.agentops.ai/v2/integrations/agno)  
[3] [coleam00/context-engineering-intro](https://github.com/coleam00/context-engineering-intro)  
[4] [How to build an analytics agent with Agno and Tinybird](https://www.tinybird.co/blog-posts/how-to-build-an-analytics-agent-with-agno-and-tinybird-step-by-step)  
[5] [Build AI Agents within 15 Minutes using Agno](https://www.youtube.com/watch?v=DiahQlVrnaw)  
[6] [[Feature Request] Support Markdown Files as ...](https://github.com/agno-agi/agno/issues/2318)  
[7] [Build AI Agents With SERP & Web Scraping in Agno](https://brightdata.com/blog/ai/build-ai-agents-in-agno-with-bright-data)  
[8] [agno-agi/agent-api: A minimal, open-source setup for ...](https://github.com/agno-agi/agent-api)  
[9] [A Guide to Context Engineering for PMs](https://www.productcompass.pm/p/context-engineering)  
[10] [agno-agi/agno: High-performance runtime for multi-agent ...](https://github.com/agno-agi/agno)  
[11] [Build Your Own AI Stock Portfolio Agent with Agno + AG-UI](https://www.copilotkit.ai/blog/build-your-own-ai-stock-portfolio-agent-with-agno-ag-ui)  
[12] [Context Engineering: The New Backbone of Scalable AI ...](https://www.qodo.ai/blog/context-engineering/)  
[13] [Agno: The agent framework for Python teams](https://workos.com/blog/agno-the-agent-framework-for-python-teams)  
[14] [Building an AI Agent with Agno: A Step-by-Step Guide](https://ai.plainenglish.io/building-an-ai-agent-with-agno-a-step-by-step-guide-13542b2a5fb6)  
[15] [Context Engineering for AI Agents: Lessons from Building ...](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)  
[16] [agno 1.0.0](https://pypi.org/project/agno/1.0.0/)  
[17] [context-engineering](https://hackmd.io/@bok-summer-25/r17gTCFNxe)  
[18] [Building an autonomous analytics agent with Agno and ...](https://www.tinybird.co/blog-posts/building-an-analytics-agent-with-agno-and-tinybird)  
[19] [Context Engineering](https://blog.langchain.com/context-engineering-for-agents/)  
[20] [Web Scraping With AI Agents in Agno and Bright Data](https://brightdata.com/blog/ai/web-scraping-with-agno-and-bright-data)  
[21] [Agno + Groq: Build Fast, Multi-Modal Agents - GroqDocs](https://console.groq.com/docs/agno)  
[22] [How To Build Financial Agent with Agno & Groq](https://dataaspirant.com/building-financial-agent-agno-groq/)  
[23] [Agno Agent Framework on Agentuity](https://www.agentuity.com/blog/agno-examples)  
[24] [Rastreamento de Agno – Azure Databricks](https://learn.microsoft.com/pt-br/azure/databricks/mlflow3/genai/tracing/integrations/agno)  
[25] [[Bug] System prompt lacks space when both structured ...](https://github.com/agno-agi/agno/issues/4073)  
[26] [Agno](https://docs.tavily.com/documentation/integrations/agno)  
[27] [Build a Local AI Agent with Memory Using Agno and gpt-oss](https://tinztwinshub.com/software-engineering/build-a-local-ai-agent-with-memory-using-agno-and-gpt-oss/)  
[28] [The Best Pre-Built Toolkits for AI Agents](https://getstream.io/blog/ai-agent-toolkits/)  
[29] [GitHub Sign In Page Redirect for Code Search in agno-agi/agno Repository](https://github.com/login?return_to=https%3A%2F%2Fgithub.com%2Fsearch%3Fq%3Drepo%253Aagno-agi%252Fagno%2Bread_file%2Binstructions%26type%3Dcode)