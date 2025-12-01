#!/usr/bin/env python3
"""
LANÇAR AGENT OS - Script de conveniência para iniciar o Agent OS completo

Este script facilita o uso do Agent OS completo com diferentes opções.
"""

import subprocess
import sys
import argparse
import time
import os
from pathlib import Path

def get_python_command():
    """Detecta se deve usar conda run ou python diretamente."""
    # Verificar se estamos no ambiente conda 12
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env == "12":
        return "python"
    else:
        return "conda run -n 12 python"

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

def check_server():
    """Verifica se o servidor está rodando."""
    import requests
    try:
        response = requests.get("http://localhost:8000/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            agent_count = len(config.get('agents', []))
            print(f"✅ Servidor rodando com {agent_count} agentes")
            return True
    except:
        pass
    
    print("❌ Servidor não está rodando")
    return False

def main():
    parser = argparse.ArgumentParser(description="Lançar Agent OS Completo")
    parser.add_argument("--modo", choices=["todos", "teste", "status", "parar"], 
                       default="todos", help="Modo de operação")
    parser.add_argument("--agents-dir", "-a", 
                       help="Diretório contendo os agentes gerados")
    parser.add_argument("--max-agents", type=int, 
                       help="Número máximo de agentes (modo teste)")
    parser.add_argument("--port", type=int, default=8000,
                       help="Porta do servidor")
    parser.add_argument("--verbose", action="store_true",
                       help="Logging verboso")
    
    args = parser.parse_args()
    
    print("🚀 LANÇAR AGENT OS COMPLETO")
    print("=" * 60)
    
    if args.modo == "status":
        print("🔍 Verificando status do servidor...")
        if check_server():
            print("💡 Servidor está funcionando!")
            print("📚 Acesse: http://localhost:8000/docs")
        else:
            print("💡 Execute: python lancar_agent_os.py --modo todos")
        return 0
    
    elif args.modo == "parar":
        print("🛑 Parando servidor...")
        result = subprocess.run(["pkill", "-f", "agent_os_completo.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Servidor parado com sucesso!")
        else:
            print("⚠️  Nenhum servidor encontrado para parar")
        return 0
    
    elif args.modo == "teste":
        if not args.max_agents:
            args.max_agents = 10
        
        print(f"🧪 Modo teste com {args.max_agents} agentes...")
        python_cmd = get_python_command().split()
        cmd = python_cmd + [
            "agent_os_completo.py",
            "--max-agents", str(args.max_agents),
            "--port", str(args.port)
        ]
        
        if args.agents_dir:
            # Se executando da pasta raiz, ajustar caminho
            if not args.agents_dir.startswith('../'):
                args.agents_dir = f"../{args.agents_dir}"
            cmd.extend(["--agents-dir", args.agents_dir])
        
        if args.verbose:
            cmd.append("--verbose")
        
        print("💡 Este é um teste rápido. Para usar todos os agentes, use --modo todos")
        print("🛑 Use Ctrl+C para parar o servidor")
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n🛑 Servidor interrompido pelo usuário")
        
        return 0
    
    elif args.modo == "todos":
        print("🚀 Iniciando Agent OS com TODOS os agentes...")
        print("⚠️  Isso pode demorar alguns minutos para carregar todos os agentes")
        
        python_cmd = get_python_command().split()
        cmd = python_cmd + [
            "agent_os_completo.py",
            "--port", str(args.port)
        ]
        
        if args.agents_dir:
            # Se executando da pasta raiz, ajustar caminho
            if not args.agents_dir.startswith('../'):
                args.agents_dir = f"../{args.agents_dir}"
            cmd.extend(["--agents-dir", args.agents_dir])
        
        if args.verbose:
            cmd.append("--verbose")
        
        print("💡 Aguarde o carregamento completo...")
        print("🛑 Use Ctrl+C para parar o servidor")
        print("📚 Após carregar, acesse: http://localhost:8000/docs")
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n🛑 Servidor interrompido pelo usuário")
        
        return 0
    
    else:
        print(f"❌ Modo desconhecido: {args.modo}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
