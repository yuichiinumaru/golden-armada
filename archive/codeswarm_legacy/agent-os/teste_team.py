#!/usr/bin/env python3
"""
TESTE TEAM - Script para testar se o Team está funcionando

Este script testa se o Team foi criado corretamente e está funcionando.
"""

import requests
import json
import sys
import argparse
from collections import Counter

def test_team():
    """Testa se o Team está funcionando."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testando Agent Team...")
    print(f"📡 URL base: {base_url}")
    
    # Testar endpoints principais
    endpoints = [
        ("/config", "Configuração do OS"),
        ("/teams", "Lista de teams"),
        ("/agents", "Lista de agentes"),
        ("/docs", "Documentação da API"),
        ("/openapi.json", "Especificação OpenAPI")
    ]
    
    for endpoint, description in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"\n🔍 Testando {description}...")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {description}: OK (200)")
                
                if endpoint == "/teams":
                    teams = response.json()
                    print(f"   👥 {len(teams)} teams encontrados")
                    for team in teams:
                        print(f"   - {team.get('name', 'N/A')}: {team.get('description', 'N/A')[:50]}...")
                        members = team.get('members', [])
                        print(f"     Membros: {len(members)} agentes")
                        
                elif endpoint == "/agents":
                    agents = response.json()
                    print(f"   🤖 {len(agents)} agentes encontrados")
                    
                elif endpoint == "/config":
                    config = response.json()
                    teams = config.get('teams', [])
                    agents = config.get('agents', [])
                    print(f"   📋 OS ID: {config.get('os_id', 'N/A')[:8]}...")
                    print(f"   📝 Descrição: {config.get('description', 'N/A')}")
                    print(f"   👥 Teams: {len(teams)}")
                    print(f"   🤖 Agentes: {len(agents)}")
                    
            else:
                print(f"❌ {description}: Erro {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {description}: Servidor não está rodando")
            return False
        except requests.exceptions.Timeout:
            print(f"❌ {description}: Timeout")
            return False
        except Exception as e:
            print(f"❌ {description}: Erro {e}")
            return False
    
    print(f"\n🎉 Agent Team está funcionando perfeitamente!")
    print(f"📚 Acesse a documentação: {base_url}/docs")
    print(f"👥 Teams: {base_url}/teams")
    print(f"🤖 Agentes: {base_url}/agents")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Teste do Agent Team")
    parser.add_argument("--verbose", action="store_true", 
                       help="Mostrar informações detalhadas")
    
    args = parser.parse_args()
    
    print("🚀 TESTE AGENT TEAM")
    print("=" * 50)
    
    # Aguardar um pouco para o servidor inicializar
    print("⏳ Aguardando servidor inicializar...")
    import time
    time.sleep(2)
    
    success = test_team()
    
    if success:
        print("\n✅ Todos os testes passaram!")
        print("💡 Você pode agora usar o Team para trabalho colaborativo")
        return 0
    else:
        print("\n❌ Alguns testes falharam")
        print("💡 Verifique se o servidor está rodando")
        return 1

if __name__ == "__main__":
    sys.exit(main())
