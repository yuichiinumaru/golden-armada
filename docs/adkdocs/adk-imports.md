## **Imports Comuns do Google ADK (Agent Development Kit)**

Aqui estão os imports mais comuns do ADK, organizados por módulo:

### **google.adk.agents**

Módulo para definir e gerir diferentes tipos de agentes.

* from google.adk.agents import Agent \- Classe base para a criação de todos os tipos de agentes.  
* from google.adk.agents import LlmAgent \- Agente especializado que utiliza um Modelo de Linguagem Grande (LLM) para processamento e resposta.  
* from google.adk.agents import WorkflowAgent \- Agente que orquestra um fluxo de trabalho, gerindo a execução de outros agentes ou ferramentas.  
* from google.adk.agents import SequentialAgent \- Um tipo de WorkflowAgent que executa os seus componentes (agentes/ferramentas filho) em sequência.  
* from google.adk.agents import LoopAgent \- Um tipo de WorkflowAgent que executa um componente filho repetidamente, seja um número fixo de vezes ou até uma condição ser satisfeita.  
* from google.adk.agents import ParallelAgent \- Um tipo de WorkflowAgent que executa os seus componentes filho em paralelo.  
* from google.adk.agents import RouterAgent \- Agente que encaminha dinamicamente os eventos para diferentes agentes ou ferramentas com base em condições ou no conteúdo do evento.  
* from google.adk.agents import AgentInput \- Representa o objeto de dados de entrada esperado por um agente.  
* from google.adk.agents import AgentOutput \- Representa o objeto de dados de saída produzido por um agente.

### **google.adk.events**

Módulo para definir e manusear eventos que fluem através do sistema de agentes.

* from google.adk.events import Event \- Classe base para todos os eventos, representando uma unidade de dados ou sinal no sistema.  
* from google.adk.events import UserEvent \- Um evento que se origina de uma entrada ou interação do utilizador.  
* from google.adk.events import AgentEvent \- Um evento que é gerado por um agente.  
* from google.adk.events import StatusUpdateEvent \- Evento usado para comunicar alterações de estado ou progresso de um agente ou processo.  
* from google.adk.events import ErrorEvent \- Evento usado para sinalizar e transportar informações sobre erros ocorridos.

### **google.adk.tools**

Módulo para criar e gerir ferramentas que os agentes podem utilizar para interagir com o mundo exterior ou realizar tarefas específicas.

* from google.adk.tools import Tool \- Classe base para a criação de todas as ferramentas.  
* from google.adk.tools import FunctionTool \- Uma ferramenta que encapsula uma função Python, tornando-a executável por um agente.  
* from google.adk.tools import tool \- Decorador para converter facilmente uma função Python numa FunctionTool.  
* from google.adk.tools import ToolInput \- Representa o objeto de dados de entrada esperado por uma ferramenta.  
* from google.adk.tools import ToolOutput \- Representa o objeto de dados de saída produzido por uma ferramenta.

### **google.adk.sessions**

Módulo para gerir o estado e a memória das interações com os agentes.

* from google.adk.sessions import Session \- Gere o ciclo de vida e o estado de uma conversação ou interação com um agente.  
* from google.adk.sessions import SessionState \- Enumeração ou classe que representa os vários estados possíveis de uma sessão.  
* from google.adk.sessions import InMemorySessionStore \- Implementação de um armazenamento de sessão que guarda os dados em memória, útil para desenvolvimento e testes.  
* from google.adk.sessions.memory import Memory \- Componente dentro de uma sessão para gerir a memória de curto e longo prazo do agente.

### **google.adk.runtime**

Módulo responsável pela execução dos agentes e pela gestão do fluxo de eventos.

* from google.adk.runtime import Runtime \- Classe principal que gere a execução de um ou mais agentes.  
* from google.adk.runtime import RunConfig \- Objeto de configuração que define como um agente ou sistema de agentes deve ser executado.  
* from google.adk.runtime import execute\_agent \- Função utilitária para executar um único agente com uma dada entrada e sessão.

### **google.adk.callbacks**

Módulo para implementar callbacks que podem ser acionados em diferentes pontos do ciclo de vida da execução de um agente.

* from google.adk.callbacks import Callback \- Interface ou classe base para criar callbacks personalizados.  
* from google.adk.callbacks import PrintCallback \- Um callback simples que imprime informações sobre eventos ou o estado do agente na consola.  
* from google.adk.callbacks import StreamingCallback \- Callback especificamente desenhado para manusear respostas de streaming de agentes ou ferramentas.

### **google.adk.models**

Módulo para interagir com modelos de linguagem grandes (LLMs) ou outros modelos de IA.

* from google.adk.models import Model \- Classe base abstrata para representar um modelo de IA.  
* from google.adk.models import LlmModel \- Classe base para modelos de linguagem grandes.  
* from google.adk.models import GeminiModel \- Implementação específica para interagir com os modelos Gemini do Google.  
* from google.adk.models import VertexAIModel \- Implementação para interagir com modelos hospedados na Vertex AI do Google Cloud.

### **google.adk.streaming**

Módulo para funcionalidades relacionadas com o processamento de streams de dados.

* from google.adk.streaming import StreamEvent \- Tipo de evento específico para transportar chunks de dados em operações de streaming.  
* from google.adk.streaming import console\_display\_stream \- Função utilitária para exibir o conteúdo de um stream de eventos na consola.

### **google.adk.context**

Módulo para gerir informações contextuais durante a execução.

* from google.adk.context import Context \- Mantém e fornece acesso a dados contextuais relevantes durante o processamento de um agente.

## **Imports Comuns do A2A (Agents-to-Agents) Python SDK**

O A2A Python SDK permite construir agentes que aderem à especificação A2A, facilitando a interoperabilidade. Muitos agentes A2A podem ser construídos utilizando componentes do ADK.

### **a2a.web.server**

Módulo para criar servidores A2A que expõem agentes através de uma API HTTP.

* from a2a.web.server import A2AServer \- Classe para configurar e executar um servidor web compatível com A2A, geralmente baseado em FastAPI.  
* from a2a.web.server import AgentConfig \- Objeto de configuração para definir como um agente específico é exposto pelo A2AServer.

### **a2a.web.client**

Módulo para criar clientes que interagem com servidores A2A. (Inferido, estrutura comum de SDKs)

* from a2a.client import A2AClient \- Cliente síncrono para enviar pedidos a um agente A2A.  
* from a2a.client import AsyncA2AClient \- Cliente assíncrono para enviar pedidos a um agente A2A.

### **a2a.types (ou a2a.web.types conforme exemplos da documentação)**

Módulo que define as estruturas de dados (tipos Pydantic) usadas na comunicação A2A.

* from a2a.types import InteractionRequest \- Modelo de dados para um pedido de interação enviado a um agente A2A.  
* from a2a.types import InteractionResponse \- Modelo de dados para a resposta de um agente A2A a um InteractionRequest.  
* from a2a.types import StreamEvent \- Modelo de dados para um evento individual num stream de resposta A2A.  
* from a2a.types import Error \- Modelo de dados para representar erros de acordo com a especificação A2A.  
* from a2a.types import AgentSkillCard \- Descreve as "skills" (capacidades) de um agente, os seus metadados e como interagir com elas.  
* from a2a.types import SkillInput \- Descreve o esquema de entrada para uma skill específica de um agente A2A.  
* from a2a.types import SkillOutput \- Descreve o esquema de saída para uma skill específica de um agente A2A.  
* from a2a.types import SkillSignature \- Define a assinatura completa de uma skill, incluindo os seus esquemas de entrada e saída.

### **Outros imports comuns em exemplos A2A/ADK (Python Standard Library e Pydantic)**

Frequentemente usados em conjunto com ADK e A2A para tipagem e modelagem de dados.

* from typing import List, Dict, Any, Optional, Union, Callable \- Módulo de tipagem padrão do Python para anotações de tipo.  
* from pydantic import BaseModel, Field \- Biblioteca para validação de dados e gestão de configurações, frequentemente usada para definir AgentInput, AgentOutput, e tipos A2A.

Esta lista cobre os imports mais proeminentes e essenciais que provavelmente encontrará ao trabalhar com a documentação do ADK e A2A. A disponibilidade exata e os caminhos podem variar ligeiramente dependendo da versão específica dos SDKs. Recomenda-se sempre consultar a documentação da API mais recente para a versão que está a utilizar.