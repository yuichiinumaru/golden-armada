#!/usr/bin/env python3
"""
EXEMPLO DE USO - Scripts de teste do Agent OS

Este script demonstra como usar os scripts de teste do Agent OS
com diferentes configurações e modos.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Executa um comando e mostra o resultado."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Comando: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.stdout:
            print("📤 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  STDERR:")
            print(result.stderr)
        
        print(f"📊 Código de saída: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Comando executado com sucesso!")
        else:
            print("❌ Comando falhou!")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏱️  Comando expirou após 5 minutos")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False

def main():
    print("🧪 EXEMPLOS DE USO - Teste Agent OS")
    print("=" * 60)
    
    # Verificar se os scripts existem
    scripts = {
        "test_agent_os.py": "Script para agentes folderless",
        "test_agent_os_folder.py": "Script para agentes em diretórios"
    }
    
    for script, description in scripts.items():
        if not Path(script).exists():
            print(f"❌ Script não encontrado: {script}")
            return 1
        else:
            print(f"✅ {script} - {description}")
    
    print("\n" + "="*60)
    print("📋 EXEMPLOS DE COMANDOS")
    print("="*60)
    
    examples = [
        {
            "cmd": ["python", "test_agent_os.py", "--help"],
            "desc": "Mostrar ajuda do script folderless"
        },
        {
            "cmd": ["python", "test_agent_os_folder.py", "--help"],
            "desc": "Mostrar ajuda do script folder-based"
        },
        {
            "cmd": ["python", "test_agent_os.py", "--max-agents", "5", "--test-mode", "basic", "--verbose"],
            "desc": "Teste básico com 5 agentes (modo folderless)"
        },
        {
            "cmd": ["python", "test_agent_os_folder.py", "--max-agents", "3", "--test-mode", "api", "--verbose"],
            "desc": "Teste de API com 3 agentes (modo folder-based)"
        },
        {
            "cmd": ["python", "test_agent_os.py", "--test-mode", "interactive", "--db-type", "sqlite"],
            "desc": "Servidor interativo com banco SQLite (modo folderless)"
        },
        {
            "cmd": ["python", "test_agent_os_folder.py", "--test-mode", "interactive", "--db-type", "none"],
            "desc": "Servidor interativo sem banco (modo folder-based)"
        }
    ]
    
    print("\n🔧 COMANDOS DISPONÍVEIS:")
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['desc']}")
        print(f"   {' '.join(example['cmd'])}")
    
    print("\n" + "="*60)
    print("🎯 EXECUTANDO EXEMPLOS")
    print("="*60)
    
    # Executar alguns exemplos básicos
    basic_examples = [
        {
            "cmd": ["python", "test_agent_os.py", "--help"],
            "desc": "Ajuda do script folderless"
        },
        {
            "cmd": ["python", "test_agent_os_folder.py", "--help"],
            "desc": "Ajuda do script folder-based"
        }
    ]
    
    for example in basic_examples:
        success = run_command(example["cmd"], example["desc"])
        if not success:
            print(f"⚠️  Exemplo falhou: {example['desc']}")
    
    print("\n" + "="*60)
    print("📖 INSTRUÇÕES DE USO")
    print("="*60)
    
    instructions = """
🔑 PRÉ-REQUISITOS:
1. Configure GOOGLE_API_KEY no arquivo .env
2. Instale as dependências: pip install agno python-dotenv
3. Certifique-se de que os agentes foram gerados pelo agentmaker2.py

🚀 USO BÁSICO:
# Teste básico com agentes folderless
python test_agent_os.py --max-agents 5 --test-mode basic

# Teste básico com agentes em diretórios
python test_agent_os_folder.py --max-agents 5 --test-mode basic

🌐 SERVIDOR INTERATIVO:
# Iniciar servidor para teste manual
python test_agent_os.py --test-mode interactive

# Acesse: http://localhost:8000
# Use Ctrl+C para parar

🔌 TESTE DE API:
# Verificar endpoints disponíveis
python test_agent_os.py --test-mode api

💾 CONFIGURAÇÃO DE BANCO:
# Com SQLite (padrão)
python test_agent_os.py --db-type sqlite --db-path meu_banco.db

# Com PostgreSQL
python test_agent_os.py --db-type postgres --db-url "postgresql://user:pass@localhost/db"

# Sem banco de dados
python test_agent_os.py --db-type none

🔍 LOGGING VERBOSO:
# Para debug detalhado
python test_agent_os.py --verbose

📁 DIRETÓRIOS PERSONALIZADOS:
# Especificar diretório de agentes
python test_agent_os.py --agents-dir ./meus-agentes
python test_agent_os_folder.py --agents-dir ./meus-agentes-dir
"""
    
    print(instructions)
    
    print("\n" + "="*60)
    print("✅ Exemplos concluídos!")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
