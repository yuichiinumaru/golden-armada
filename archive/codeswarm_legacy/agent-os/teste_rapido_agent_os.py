#!/usr/bin/env python3
"""
TESTE RÁPIDO AGENT OS - Script para testar rapidamente se o Agent OS está funcionando
"""

import requests
import time
import sys

def test_agent_os():
    """Testa se o Agent OS está funcionando."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testando Agent OS...")
    print(f"📡 URL base: {base_url}")
    
    # Testar endpoints principais
    endpoints = [
        ("/config", "Configuração do OS"),
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
                if endpoint == "/agents":
                    agents = response.json()
                    print(f"   📊 {len(agents)} agentes encontrados")
                    for agent in agents[:3]:  # Mostrar apenas os primeiros 3
                        print(f"   - {agent.get('name', 'N/A')}: {agent.get('description', 'N/A')}")
                elif endpoint == "/config":
                    config = response.json()
                    print(f"   📋 OS ID: {config.get('os_id', 'N/A')[:8]}...")
                    print(f"   📝 Descrição: {config.get('description', 'N/A')}")
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
    
    print(f"\n🎉 Agent OS está funcionando perfeitamente!")
    print(f"📚 Acesse a documentação: {base_url}/docs")
    print(f"🔧 Configuração: {base_url}/config")
    print(f"🤖 Agentes: {base_url}/agents")
    
    return True

def main():
    print("🚀 TESTE RÁPIDO AGENT OS")
    print("=" * 50)
    
    # Aguardar um pouco para o servidor inicializar
    print("⏳ Aguardando servidor inicializar...")
    time.sleep(2)
    
    success = test_agent_os()
    
    if success:
        print("\n✅ Todos os testes passaram!")
        print("💡 Você pode agora conectar o Agent UI ao Agent OS")
        return 0
    else:
        print("\n❌ Alguns testes falharam")
        print("💡 Verifique se o servidor está rodando")
        return 1

if __name__ == "__main__":
    sys.exit(main())
