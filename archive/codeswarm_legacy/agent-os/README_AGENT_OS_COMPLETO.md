# Agent OS Completo - Guia de Uso

Este diretório contém scripts para iniciar um Agent OS completo com todos os agentes gerados pelo `agentmaker2.py`.

## 🚀 Scripts Disponíveis

### **`agent_os_completo.py`** - Script Principal
Carrega todos os agentes da pasta `01-generated-agents` e inicia o Agent OS.

```bash
# Carregar TODOS os agentes (padrão)
python agent_os_completo.py

# Carregar apenas 10 agentes para teste
python agent_os_completo.py --max-agents 10

# Usar porta diferente
python agent_os_completo.py --port 8001

# Logging verboso
python agent_os_completo.py --verbose
```

### **`lancar_agent_os.py`** - Script de Conveniência
Script simplificado para facilitar o uso.

```bash
# Iniciar com todos os agentes
python lancar_agent_os.py --modo todos

# Teste rápido com 10 agentes
python lancar_agent_os.py --modo teste --max-agents 10

# Verificar se está rodando
python lancar_agent_os.py --modo status

# Parar servidor
python lancar_agent_os.py --modo parar
```

### **`teste_rapido_agent_os.py`** - Teste de Funcionamento
Verifica se o Agent OS está funcionando corretamente.

```bash
python teste_rapido_agent_os.py
```

## 📊 Status Atual

✅ **198 agentes carregados** com sucesso  
✅ **Servidor rodando** na porta 8000  
✅ **API funcionando** com 52 rotas  
✅ **Documentação disponível** em `/docs`  

## 🔗 URLs Disponíveis

- **Documentação**: http://localhost:8000/docs
- **Configuração**: http://localhost:8000/config  
- **Agentes**: http://localhost:8000/agents
- **OpenAPI**: http://localhost:8000/openapi.json

## 🎯 Uso Rápido

### 1. **Iniciar com Todos os Agentes**
```bash
python lancar_agent_os.py --modo todos
```

### 2. **Teste Rápido**
```bash
python lancar_agent_os.py --modo teste --max-agents 5
```

### 3. **Verificar Status**
```bash
python lancar_agent_os.py --modo status
```

### 4. **Parar Servidor**
```bash
python lancar_agent_os.py --modo parar
```

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

## 📈 Performance

### Tempo de Carregamento
- **10 agentes**: ~30 segundos
- **50 agentes**: ~2 minutos  
- **198 agentes**: ~5 minutos

### Uso de Recursos
- **Memória**: ~2-3GB para todos os agentes
- **CPU**: Moderado durante carregamento
- **Rede**: Conexão com Gemini API

## 🎮 Integração com Agent UI

### Conectar ao Agent OS
1. **Acesse**: `os.agno.com`
2. **Clique**: "Add new OS" → "Local"
3. **Configure**:
   - **URL**: `http://localhost:8000`
   - **Nome**: "AgentMaker OS Completo"
   - **Tags**: `complete`, `all-agents`
4. **Conecte**: Clique em "CONNECT"

### Testar Conexão
```bash
# Verificar se está funcionando
python teste_rapido_agent_os.py

# Testar endpoint específico
curl http://localhost:8000/agents | jq length
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
tail -20 agent_os_completo.log

# Testar com menos agentes
python agent_os_completo.py --max-agents 5 --verbose
```

### Erro de memória
```bash
# Usar menos agentes
python agent_os_completo.py --max-agents 50

# Ou aumentar swap/memória do sistema
```

## 📋 Logs e Debug

### Arquivos de Log
- **`agent_os_completo.log`** - Log principal do Agent OS
- **`test_agent_os.log`** - Log do script de teste original

### Debug Verboso
```bash
python agent_os_completo.py --verbose
```

### Monitorar Carregamento
```bash
# Em outro terminal
tail -f agent_os_completo.log | grep "Carregado"
```

## 🎉 Resultado Final

Com todos os agentes carregados, você terá:

- ✅ **198 agentes especializados** disponíveis
- ✅ **API REST completa** para interação
- ✅ **Documentação automática** em `/docs`
- ✅ **Integração com Agent UI** do Agno
- ✅ **Sistema escalável** e robusto

---

**💡 Dica**: Comece sempre com `--modo teste` para verificar se tudo está funcionando antes de carregar todos os agentes!
