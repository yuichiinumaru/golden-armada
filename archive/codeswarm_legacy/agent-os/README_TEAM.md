# Agent Team Creator - Guia Completo

Este diretório contém scripts para criar e gerenciar Teams com todos os agentes do AgentMaker.

## 🚀 Scripts Disponíveis

### **`agent_team_creator.py`** - Script Principal
Cria um Team com todos os agentes da pasta `01-generated-agents`.

```bash
# Criar Team com TODOS os agentes (198 agentes)
python agent_team_creator.py

# Criar Team com apenas 10 agentes para teste
python agent_team_creator.py --max-agents 10

# Usar porta diferente
python agent_team_creator.py --port 8001

# Logging verboso
python agent_team_creator.py --verbose
```

### **`lancar_agent_team.py`** - Script de Conveniência
Script simplificado para facilitar o uso.

```bash
# Criar Team com todos os agentes
python lancar_agent_team.py --modo team

# Teste rápido com 10 agentes
python lancar_agent_team.py --modo teste --max-agents 10

# Verificar se está rodando
python lancar_agent_team.py --modo status

# Parar servidor
python lancar_agent_team.py --modo parar
```

### **`teste_team.py`** - Teste de Funcionamento
Verifica se o Team foi criado corretamente.

```bash
python teste_team.py
```

## 📊 Status Atual

✅ **198 agentes organizados** em 1 Team  
✅ **Servidor funcionando** na porta 8000  
✅ **API funcionando** com endpoints de Teams  
✅ **Documentação disponível** em `/docs`  

## 🔗 URLs Disponíveis

- **Documentação**: http://localhost:8000/docs
- **Teams**: http://localhost:8000/teams
- **Configuração**: http://localhost:8000/config
- **OpenAPI**: http://localhost:8000/openapi.json

## 🎯 Uso Rápido

### **1. Configurar Ambiente**
```bash
cd 00-agent-os
python setup_env.py create
```

### **2. Criar Team Completo**
```bash
# Com todos os agentes (198 agentes)
python lancar_agent_team.py --modo team

# Teste rápido com 10 agentes
python lancar_agent_team.py --modo teste --max-agents 10
```

### **3. Verificar Status**
```bash
python lancar_agent_team.py --modo status
python teste_team.py
```

### **4. Testar Funcionamento**
```bash
python teste_team.py
```

## 🎮 Integração com Agent UI

### Conectar ao Agent OS
1. **Acesse**: `os.agno.com`
2. **Clique**: "Add new OS" → "Local"
3. **Configure**:
   - **URL**: `http://localhost:8000`
   - **Nome**: "AgentMaker Team OS"
   - **Tags**: `team`, `collaborative`, `all-agents`
4. **Conecte**: Clique em "CONNECT"

### Testar Conexão
```bash
# Verificar se está funcionando
python teste_team.py

# Testar endpoint específico
curl http://localhost:8000/teams | jq length
```

## 🔍 Diferenças: Agent OS vs Team

### **Agent OS Individual**
- ✅ **198 agentes** disponíveis individualmente
- ✅ **API REST** para cada agente
- ✅ **Documentação** em `/docs`
- ✅ **Agentes**: http://localhost:8000/agents

### **Agent Team**
- ✅ **1 Team** com 198 agentes colaborativos
- ✅ **Trabalho conjunto** coordenado
- ✅ **Distribuição de tarefas** automática
- ✅ **Teams**: http://localhost:8000/teams

## 📈 Performance

### Tempo de Carregamento
- **10 agentes**: ~30 segundos
- **50 agentes**: ~2 minutos  
- **198 agentes**: ~5 minutos

### Uso de Recursos
- **Memória**: ~2-3GB para operação completa
- **CPU**: Moderado durante carregamento
- **Rede**: Conexão com Gemini API

## 🔧 Configuração

### Pré-requisitos
```bash
# 1. Configurar API key
python setup_env.py create

# 2. Instalar dependências (já instaladas)
conda run -n 12 pip install agno google-genai python-dotenv mcp
```

### Variáveis de Ambiente
```bash
# Arquivo .env (criado automaticamente)
GOOGLE_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.5-pro
GEMINI_TEMPERATURE=0.5
```

## 🎯 Comandos Úteis

### **Da Pasta Raiz (Recomendado)**
```bash
# Usar script de conveniência
python agent_os.py team        # Team completo
python agent_os.py team-teste  # Teste rápido
python agent_os.py status      # Verificar status
python agent_os.py parar       # Parar servidor
```

### **Da Pasta 00-agent-os**
```bash
# Executar diretamente
python lancar_agent_team.py --modo team
python lancar_agent_team.py --modo teste --max-agents 10
python teste_team.py
```

## 🔍 Troubleshooting

### Servidor não inicia
```bash
# Verificar API key
python setup_env.py check

# Verificar dependências
conda run -n 12 python -c "import agno; print('OK')"
```

### Poucos agentes carregados
```bash
# Verificar logs
tail -20 agent_team_creator.log

# Testar com menos agentes
python agent_team_creator.py --max-agents 5 --verbose
```

### Erro de porta
```bash
# Verificar porta em uso
lsof -i :8000

# Usar porta diferente
python agent_team_creator.py --port 8001
```

## 📋 Logs e Debug

### Arquivos de Log
- **`agent_team_creator.log`** - Log principal do Team Creator

### Debug Verboso
```bash
python agent_team_creator.py --verbose
```

### Monitorar Carregamento
```bash
# Em outro terminal
tail -f agent_team_creator.log | grep "Carregado"
```

## 🎉 Resultado Final

Com o Team criado, você terá:

- ✅ **198 agentes especializados** trabalhando em conjunto
- ✅ **Coordenação automática** de tarefas
- ✅ **API REST completa** para interação com o Team
- ✅ **Documentação automática** em `/docs`
- ✅ **Integração com Agent UI** do Agno
- ✅ **Sistema escalável** e robusto

---

**💡 Dica**: Comece sempre com `--modo teste` para verificar se tudo está funcionando antes de criar o Team completo!
