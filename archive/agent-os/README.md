# 00-agent-os - Agent OS Completo

Esta pasta contém todos os scripts e ferramentas para criar e gerenciar um Agent OS completo com todos os agentes gerados pelo `agentmaker2.py`.

## 📁 Arquivos Organizados

### **🚀 Scripts Principais**
- **`agent_os_completo.py`** - Script principal para carregar todos os agentes
- **`agent_team_creator.py`** - Script para criar Team com todos os agentes
- **`lancar_agent_os.py`** - Script de conveniência com modos simplificados
- **`lancar_agent_team.py`** - Script de conveniência para Teams
- **`simple_agent_os.py`** - Script simplificado para testes básicos

### **🧪 Scripts de Teste**
- **`test_agent_os.py`** - Script de teste para agentes folderless
- **`test_agent_os_folder.py`** - Script de teste para agentes em diretórios
- **`teste_rapido_agent_os.py`** - Teste rápido de funcionamento
- **`teste_team.py`** - Teste de funcionamento do Team

### **🔧 Scripts de Utilitários**
- **`setup_env.py`** - Configuração de variáveis de ambiente
- **`info_agent_os.py`** - Informações detalhadas sobre o Agent OS
- **`exemplo_uso_agent_os.py`** - Exemplos de uso dos scripts

### **📚 Documentação**
- **`README_AGENT_OS_COMPLETO.md`** - Guia completo do Agent OS
- **`README_TEST_AGENT_OS.md`** - Guia de testes do Agent OS

### **📋 Logs**
- **`*.log`** - Arquivos de log dos diferentes scripts

## 🚀 Uso Rápido

### **1. Configurar Ambiente**
```bash
cd 00-agent-os
python setup_env.py create
```

### **2. Iniciar Agent OS Completo**
```bash
# Com todos os agentes (198 agentes)
python lancar_agent_os.py --modo todos

# Teste rápido com 10 agentes
python lancar_agent_os.py --modo teste --max-agents 10
```

### **3. Criar Team com Agentes**
```bash
# Team com todos os agentes (198 agentes)
python lancar_agent_team.py --modo team

# Teste rápido com Team
python lancar_agent_team.py --modo teste --max-agents 10
```

### **4. Verificar Status**
```bash
python lancar_agent_os.py --modo status
python info_agent_os.py
python teste_team.py
```

### **5. Testar Funcionamento**
```bash
python teste_rapido_agent_os.py
python teste_team.py
```

## 📊 Status Atual

✅ **198 agentes carregados** com sucesso  
✅ **1 Team criado** com todos os agentes  
✅ **Servidor funcionando** na porta 8000  
✅ **API funcionando** com endpoints de Teams  
✅ **Documentação disponível** em `/docs`  

## 🔗 URLs Disponíveis

- **Documentação**: http://localhost:8000/docs
- **Teams**: http://localhost:8000/teams
- **Agentes**: http://localhost:8000/agents
- **Configuração**: http://localhost:8000/config
- **OpenAPI**: http://localhost:8000/openapi.json

## 🎯 Próximos Passos

1. **Conectar Agent UI**: Acesse `os.agno.com` e conecte `http://localhost:8000`
2. **Testar Agentes**: Use a documentação em `/docs` para testar diferentes agentes
3. **Testar Team**: Use `/teams` para trabalho colaborativo
4. **Integrar Aplicações**: Use a API REST para integrar com outras aplicações

## 📈 Performance

- **Carregamento**: ~5 minutos para todos os agentes
- **Memória**: ~2-3GB para operação completa
- **Resposta**: <2s para consultas simples

---

**💡 Dica**: Comece sempre com `--modo teste` para verificar se tudo está funcionando!
