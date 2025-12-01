# Teste Agent OS - Guia de Uso

Este diretório contém scripts para testar a integração do Agent OS com agentes gerados pelo `agentmaker2.py`.

## 📁 Arquivos

- **`test_agent_os.py`** - Script para testar agentes no modo **folderless** (todos os agentes em um diretório)
- **`test_agent_os_folder.py`** - Script para testar agentes no modo **folder-based** (cada agente em seu diretório)
- **`exemplo_uso_agent_os.py`** - Script demonstrativo com exemplos de uso

## 🚀 Uso Rápido

### Pré-requisitos
```bash
# 1. Configure a API key
echo "GOOGLE_API_KEY=sua_chave_aqui" > .env

# 2. Instale dependências
pip install agno python-dotenv

# 3. Gere agentes (se ainda não fez)
python scripts/agentmaker2.py -f docs/prompts -o 01-generated-agents --folderless
```

### Teste Básico
```bash
# Teste com agentes folderless (5 agentes)
python test_agent_os.py --max-agents 5 --test-mode basic --verbose

# Teste com agentes em diretórios (3 agentes)
python test_agent_os_folder.py --max-agents 3 --test-mode basic --verbose
```

### Servidor Interativo
```bash
# Iniciar servidor para teste manual
python test_agent_os.py --test-mode interactive

# Acesse: http://localhost:8000
# Use Ctrl+C para parar
```

## 🔧 Opções Disponíveis

### Modos de Teste
- **`basic`** - Teste básico de criação do Agent OS
- **`interactive`** - Inicia servidor para teste manual
- **`api`** - Testa endpoints da API

### Configuração de Banco
- **`sqlite`** - Banco SQLite local (padrão)
- **`postgres`** - Banco PostgreSQL
- **`none`** - Sem banco de dados

### Outras Opções
- **`--max-agents N`** - Limita número de agentes para teste
- **`--agents-dir PATH`** - Especifica diretório de agentes
- **`--verbose`** - Logging detalhado

## 📋 Exemplos Completos

### 1. Teste Básico com SQLite
```bash
python test_agent_os.py \
  --max-agents 10 \
  --test-mode basic \
  --db-type sqlite \
  --db-path agentos_test.db \
  --verbose
```

### 2. Servidor Interativo com PostgreSQL
```bash
python test_agent_os.py \
  --test-mode interactive \
  --db-type postgres \
  --db-url "postgresql://user:pass@localhost/agentos" \
  --max-agents 20
```

### 3. Teste de API sem Banco
```bash
python test_agent_os_folder.py \
  --test-mode api \
  --db-type none \
  --max-agents 5 \
  --verbose
```

### 4. Teste com Diretório Personalizado
```bash
python test_agent_os.py \
  --agents-dir ./meus-agentes \
  --test-mode interactive \
  --max-agents 15
```

## 🔍 Troubleshooting

### Erro: "GOOGLE_API_KEY não configurada"
```bash
# Verifique se o arquivo .env existe e contém a chave
cat .env | grep GOOGLE_API_KEY
```

### Erro: "Nenhum agente foi carregado"
```bash
# Verifique se os agentes foram gerados
ls -la 01-generated-agents/

# Ou gere novos agentes
python scripts/agentmaker2.py -f docs/prompts -o 01-generated-agents --folderless
```

### Erro: "Módulo não encontrado"
```bash
# Instale as dependências do Agno
pip install agno

# Ou reinstale tudo
pip install -r requirements.txt
```

### Servidor não inicia
```bash
# Verifique se a porta 8000 está livre
lsof -i :8000

# Use uma porta diferente (se necessário)
# (Modifique o script para usar porta diferente)
```

## 📊 Logs e Debug

### Logs Automáticos
- **`test_agent_os.log`** - Log do script folderless
- **`test_agent_os_folder.log`** - Log do script folder-based

### Debug Verboso
```bash
python test_agent_os.py --verbose --test-mode basic
```

### Verificar Agentes Carregados
```bash
python test_agent_os.py --max-agents 5 --test-mode basic --verbose | grep "Carregado agente"
```

## 🎯 Próximos Passos

1. **Teste Básico**: Execute com poucos agentes primeiro
2. **Teste Interativo**: Use o servidor para testar manualmente
3. **Integração**: Conecte ao painel do Agno em `os.agno.com`
4. **Produção**: Configure banco PostgreSQL para persistência

## 🔗 Integração com Agent OS

Após testar localmente, conecte ao Agent OS:

1. Execute o servidor: `python test_agent_os.py --test-mode interactive`
2. Acesse `os.agno.com` e faça login
3. Clique em "Add new OS" → "Local"
4. Configure:
   - **URL**: `http://localhost:8000`
   - **Nome**: "AgentMaker Test OS"
   - **Tags**: `test`, `development`
5. Clique em "CONNECT"

## 📈 Monitoramento

### Métricas Importantes
- **Tempo de carregamento** dos agentes
- **Uso de memória** por agente
- **Taxa de sucesso** no carregamento
- **Performance** da API

### Logs de Performance
```bash
# Monitorar uso de memória
python test_agent_os.py --verbose --max-agents 50 --test-mode basic

# Verificar logs de erro
tail -f test_agent_os.log | grep ERROR
```

---

**💡 Dica**: Comece sempre com `--max-agents 5` para testes rápidos, depois aumente gradualmente!
