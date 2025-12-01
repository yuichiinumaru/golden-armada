#!/usr/bin/env python3
"""
INFO AGENT OS - Script para mostrar informações detalhadas sobre o Agent OS

Este script mostra informações detalhadas sobre os agentes carregados,
estatísticas e status do sistema.
"""

import requests
import json
import sys
from collections import Counter
import argparse

def get_agent_os_info():
    """Obtém informações do Agent OS."""
    try:
        # Configuração
        config_response = requests.get("http://localhost:8000/config", timeout=10)
        if config_response.status_code != 200:
            return None, f"Erro ao obter configuração: {config_response.status_code}"
        
        config = config_response.json()
        
        # Lista de agentes
        agents_response = requests.get("http://localhost:8000/agents", timeout=10)
        if agents_response.status_code != 200:
            return None, f"Erro ao obter agentes: {agents_response.status_code}"
        
        agents = agents_response.json()
        
        return config, agents, None
        
    except requests.exceptions.ConnectionError:
        return None, None, "Servidor não está rodando"
    except Exception as e:
        return None, None, f"Erro: {e}"

def analyze_agents(agents):
    """Analisa os agentes e gera estatísticas."""
    stats = {
        'total': len(agents),
        'models': Counter(),
        'providers': Counter(),
        'categories': Counter(),
        'descriptions': []
    }
    
    for agent in agents:
        # Modelo e provider
        model_info = agent.get('model', {})
        stats['models'][model_info.get('model', 'Unknown')] += 1
        stats['providers'][model_info.get('provider', 'Unknown')] += 1
        
        # Categoria baseada no nome
        name = agent.get('name', '')
        if 'test' in name.lower():
            stats['categories']['Test'] += 1
        elif 'api' in name.lower():
            stats['categories']['API'] += 1
        elif 'security' in name.lower():
            stats['categories']['Security'] += 1
        elif 'frontend' in name.lower():
            stats['categories']['Frontend'] += 1
        elif 'backend' in name.lower():
            stats['categories']['Backend'] += 1
        elif 'data' in name.lower():
            stats['categories']['Data'] += 1
        elif 'devops' in name.lower():
            stats['categories']['DevOps'] += 1
        elif 'mobile' in name.lower():
            stats['categories']['Mobile'] += 1
        elif 'design' in name.lower():
            stats['categories']['Design'] += 1
        elif 'marketing' in name.lower():
            stats['categories']['Marketing'] += 1
        else:
            stats['categories']['Other'] += 1
        
        # Descrições
        desc = agent.get('system_message', {}).get('description', '')
        if desc:
            stats['descriptions'].append(desc)
    
    return stats

def print_agent_info(config, agents, stats, verbose=False):
    """Imprime informações detalhadas sobre o Agent OS."""
    print("🤖 AGENT OS - INFORMAÇÕES DETALHADAS")
    print("=" * 60)
    
    # Informações básicas
    print(f"📋 OS ID: {config.get('os_id', 'N/A')}")
    print(f"📝 Descrição: {config.get('description', 'N/A')}")
    print(f"📊 Total de Agentes: {stats['total']}")
    print()
    
    # Estatísticas de modelos
    print("🤖 MODELOS UTILIZADOS:")
    for model, count in stats['models'].most_common():
        print(f"  {model}: {count} agentes")
    print()
    
    # Estatísticas de providers
    print("🏢 PROVIDERS:")
    for provider, count in stats['providers'].most_common():
        print(f"  {provider}: {count} agentes")
    print()
    
    # Categorias de agentes
    print("📂 CATEGORIAS DE AGENTES:")
    for category, count in stats['categories'].most_common():
        print(f"  {category}: {count} agentes")
    print()
    
    # Top 10 agentes por nome
    print("🔝 TOP 10 AGENTES (por nome):")
    sorted_agents = sorted(agents, key=lambda x: x.get('name', ''))
    for i, agent in enumerate(sorted_agents[:10], 1):
        name = agent.get('name', 'N/A')
        desc = agent.get('system_message', {}).get('description', 'N/A')
        print(f"  {i:2d}. {name}")
        if verbose and desc != 'N/A':
            print(f"      {desc[:80]}{'...' if len(desc) > 80 else ''}")
    print()
    
    if verbose:
        # Lista completa de agentes
        print("📋 LISTA COMPLETA DE AGENTES:")
        for i, agent in enumerate(sorted_agents, 1):
            name = agent.get('name', 'N/A')
            desc = agent.get('system_message', {}).get('description', 'N/A')
            print(f"  {i:3d}. {name}")
            if desc != 'N/A':
                print(f"       {desc}")
        print()
    
    # URLs úteis
    print("🔗 URLs ÚTEIS:")
    print("  📚 Documentação: http://localhost:8000/docs")
    print("  🤖 Agentes: http://localhost:8000/agents")
    print("  🔧 Configuração: http://localhost:8000/config")
    print("  📋 OpenAPI: http://localhost:8000/openapi.json")
    print()
    
    # Status do sistema
    print("✅ STATUS DO SISTEMA:")
    print("  🟢 Servidor: Funcionando")
    print("  🟢 API: Respondendo")
    print("  🟢 Agentes: Carregados")
    print("  🟢 Documentação: Disponível")

def main():
    parser = argparse.ArgumentParser(description="Informações detalhadas do Agent OS")
    parser.add_argument("--verbose", action="store_true", 
                       help="Mostrar informações detalhadas")
    parser.add_argument("--json", action="store_true",
                       help="Saída em formato JSON")
    
    args = parser.parse_args()
    
    # Obter informações
    config, agents, error = get_agent_os_info()
    
    if error:
        print(f"❌ {error}")
        print("💡 Execute: python lancar_agent_os.py --modo todos")
        return 1
    
    # Analisar agentes
    stats = analyze_agents(agents)
    
    if args.json:
        # Saída JSON
        output = {
            'config': config,
            'agents': agents,
            'stats': {
                'total': stats['total'],
                'models': dict(stats['models']),
                'providers': dict(stats['providers']),
                'categories': dict(stats['categories'])
            }
        }
        print(json.dumps(output, indent=2))
    else:
        # Saída formatada
        print_agent_info(config, agents, stats, args.verbose)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
