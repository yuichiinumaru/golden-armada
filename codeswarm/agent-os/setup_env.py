#!/usr/bin/env python3
"""
SETUP ENV - Script para configurar variáveis de ambiente

Este script ajuda a configurar as variáveis de ambiente necessárias
para executar os testes do Agent OS.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Cria arquivo .env com configurações padrão."""
    env_content = """# Configuração de ambiente para AgentMaker
GOOGLE_API_KEY=AIzaSyCAviZwQ84pzpzW7QH6GjGyDuz6qXiCUrs
GEMINI_MODEL=gemini-2.5-pro
GEMINI_TEMPERATURE=0.5
"""
    
    env_file = Path(".env")
    
    if env_file.exists():
        print(f"⚠️  Arquivo .env já existe em {env_file.absolute()}")
        response = input("Deseja sobrescrever? (y/N): ").lower()
        if response != 'y':
            print("❌ Operação cancelada")
            return False
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ Arquivo .env criado em {env_file.absolute()}")
        print("🔑 API Key configurada: AIzaSyCAviZwQ84pzpzW7QH6GjGyDuz6qXiCUrs")
        print("🤖 Modelo: gemini-2.5-pro")
        print("🌡️  Temperatura: 0.5")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .env: {e}")
        return False

def check_env_file():
    """Verifica se o arquivo .env existe e está configurado corretamente."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "GOOGLE_API_KEY=" in content:
            print("✅ Arquivo .env encontrado e configurado")
            return True
        else:
            print("⚠️  Arquivo .env existe mas não contém GOOGLE_API_KEY")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao ler arquivo .env: {e}")
        return False

def show_env_status():
    """Mostra o status atual das variáveis de ambiente."""
    print("🔍 Status das variáveis de ambiente:")
    print("-" * 50)
    
    google_key = os.environ.get("GOOGLE_API_KEY")
    gemini_model = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")
    gemini_temp = os.environ.get("GEMINI_TEMPERATURE", "0.5")
    
    if google_key:
        # Mostrar apenas os primeiros e últimos caracteres da key
        masked_key = f"{google_key[:10]}...{google_key[-10:]}" if len(google_key) > 20 else google_key
        print(f"✅ GOOGLE_API_KEY: {masked_key}")
    else:
        print("❌ GOOGLE_API_KEY: não configurada")
    
    print(f"🤖 GEMINI_MODEL: {gemini_model}")
    print(f"🌡️  GEMINI_TEMPERATURE: {gemini_temp}")

def main():
    print("🔧 SETUP ENV - Configuração de Ambiente")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "create":
            success = create_env_file()
            if success:
                print("\n💡 Agora você pode executar:")
                print("   python test_agent_os.py --test-mode basic --max-agents 5")
            return 0 if success else 1
            
        elif command == "check":
            success = check_env_file()
            return 0 if success else 1
            
        elif command == "status":
            show_env_status()
            return 0
            
        else:
            print(f"❌ Comando desconhecido: {command}")
            return 1
    
    # Modo interativo
    print("Escolha uma opção:")
    print("1. Criar arquivo .env")
    print("2. Verificar arquivo .env")
    print("3. Mostrar status das variáveis")
    print("4. Sair")
    
    try:
        choice = input("\nDigite sua escolha (1-4): ").strip()
        
        if choice == "1":
            success = create_env_file()
            if success:
                print("\n💡 Agora você pode executar:")
                print("   python test_agent_os.py --test-mode basic --max-agents 5")
            return 0 if success else 1
            
        elif choice == "2":
            success = check_env_file()
            return 0 if success else 1
            
        elif choice == "3":
            show_env_status()
            return 0
            
        elif choice == "4":
            print("👋 Até logo!")
            return 0
            
        else:
            print("❌ Opção inválida")
            return 1
            
    except KeyboardInterrupt:
        print("\n👋 Operação cancelada pelo usuário")
        return 0
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
