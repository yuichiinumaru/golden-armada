#!/usr/bin/env python3
"""
TEST AGENT OS - Script para testar Agent OS com agentes gerados pelo agentmaker2.py

Este script carrega dinamicamente todos os agentes gerados e cria um Agent OS
para testar a integração completa.
"""

import os
import sys
import importlib
import importlib.util
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Importações do Agno
from agno.os import AgentOS
from agno.db.sqlite import SqliteDb
from agno.db.postgres import PostgresDb

load_dotenv()

logger = logging.getLogger("test_agent_os")

def setup_logging(verbose: bool = False):
    """Configura logging para o teste."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("test_agent_os.log", encoding="utf-8")
        ]
    )

async def load_agent_from_file(file_path: Path) -> Any:
    """
    Carrega dinamicamente um agente de um arquivo Python.
    
    Args:
        file_path: Caminho para o arquivo do agente
        
    Returns:
        Instância da classe do agente ou None se falhar
    """
    try:
        # Extrair nome do módulo do arquivo
        module_name = file_path.stem
        
        # Carregar o módulo dinamicamente
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            logger.error(f"Não foi possível criar spec para {file_path}")
            return None
            
        module = importlib.util.module_from_spec(spec)
        if module is None:
            logger.error(f"Não foi possível criar módulo para {file_path}")
            return None
            
        # Executar o módulo
        spec.loader.exec_module(module)
        
        # Encontrar a classe do agente (assumindo que segue o padrão do template)
        agent_class_name = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                attr_name.endswith("Agent") and 
                attr_name != "Agent"):  # Evitar conflito com a classe Agent do Agno
                agent_class_name = attr_name
                break
        
        if not agent_class_name:
            logger.error(f"Não foi possível encontrar classe do agente em {file_path}")
            return None
        
        # Instanciar o agente
        agent_class = getattr(module, agent_class_name)
        agent_instance = agent_class()
        
        # Configurar o agente (chamar setup_agent)
        await agent_instance.setup_agent()
        
        # Extrair o agente real do Agno
        if hasattr(agent_instance, 'agent') and agent_instance.agent:
            logger.info(f"✅ Carregado agente: {agent_class_name} de {file_path.name}")
            return agent_instance.agent
        else:
            logger.error(f"❌ Agente não configurado corretamente: {agent_class_name}")
            return None
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar {file_path}: {e}")
        return None

def extract_agent_info(agent_instance: Any) -> Dict[str, str]:
    """
    Extrai informações do agente para configuração do Agent OS.
    
    Args:
        agent_instance: Instância do agente carregado
        
    Returns:
        Dicionário com informações do agente
    """
    try:
        # Tentar extrair informações do agente
        agent_name = getattr(agent_instance, 'agent', {}).get('name', 'Unknown Agent')
        agent_description = getattr(agent_instance, 'agent', {}).get('description', 'No description')
        
        return {
            'name': agent_name,
            'description': agent_description,
            'class_name': agent_instance.__class__.__name__
        }
    except Exception as e:
        logger.warning(f"Erro ao extrair informações do agente: {e}")
        return {
            'name': agent_instance.__class__.__name__,
            'description': 'Agent loaded from file',
            'class_name': agent_instance.__class__.__name__
        }

async def load_all_agents(agents_dir: Path, max_agents: int = None) -> List[Any]:
    """
    Carrega todos os agentes de um diretório.
    
    Args:
        agents_dir: Diretório contendo os agentes
        max_agents: Número máximo de agentes para carregar (para teste)
        
    Returns:
        Lista de instâncias de agentes carregados
    """
    logger.info(f"🔍 Procurando agentes em: {agents_dir}")
    
    # Encontrar todos os arquivos Python de agentes
    agent_files = list(agents_dir.glob("*_agent.py"))
    
    if not agent_files:
        logger.error(f"Nenhum arquivo de agente encontrado em {agents_dir}")
        return []
    
    logger.info(f"📁 Encontrados {len(agent_files)} arquivos de agentes")
    
    # Limitar número de agentes para teste se especificado
    if max_agents:
        agent_files = agent_files[:max_agents]
        logger.info(f"🔢 Limitando a {max_agents} agentes para teste")
    
    loaded_agents = []
    failed_count = 0
    
    for i, agent_file in enumerate(agent_files, 1):
        logger.info(f"📥 Carregando agente {i}/{len(agent_files)}: {agent_file.name}")
        
        agent_instance = await load_agent_from_file(agent_file)
        if agent_instance:
            loaded_agents.append(agent_instance)
        else:
            failed_count += 1
    
    logger.info(f"✅ Carregados {len(loaded_agents)} agentes com sucesso")
    if failed_count > 0:
        logger.warning(f"⚠️  {failed_count} agentes falharam ao carregar")
    
    return loaded_agents

def create_agent_os(agents: List[Any], db_config: Dict[str, Any] = None) -> AgentOS:
    """
    Cria uma instância do Agent OS com os agentes carregados.
    
    Args:
        agents: Lista de instâncias de agentes
        db_config: Configuração do banco de dados
        
    Returns:
        Instância do Agent OS configurada
    """
    logger.info(f"🏗️  Criando Agent OS com {len(agents)} agentes")
    
    # Configurar banco de dados se especificado
    db = None
    if db_config and db_config.get('enabled', False):
        db_type = db_config.get('type', 'sqlite')
        
        if db_type == 'sqlite':
            db_path = db_config.get('path', 'agent_os_test.db')
            db = SqliteDb(db_file=db_path)
            logger.info(f"💾 Configurado banco SQLite: {db_path}")
            
        elif db_type == 'postgres':
            db_url = db_config.get('url')
            if db_url:
                db = PostgresDb(db_url)
                logger.info("💾 Configurado banco PostgreSQL")
            else:
                logger.error("URL do PostgreSQL não especificada")
    
    # Criar Agent OS
    agent_os = AgentOS(
        description="AgentMaker Test OS - Sistema de teste com agentes gerados",
        agents=agents
    )
    
    logger.info("✅ Agent OS criado com sucesso")
    return agent_os

def test_agent_os(agent_os: AgentOS, test_mode: str = "basic"):
    """
    Executa testes básicos no Agent OS.
    
    Args:
        agent_os: Instância do Agent OS
        test_mode: Modo de teste ('basic', 'interactive', 'api')
    """
    logger.info(f"🧪 Iniciando testes em modo: {test_mode}")
    
    if test_mode == "basic":
        # Teste básico - verificar se o Agent OS foi criado corretamente
        logger.info("✅ Teste básico: Agent OS criado com sucesso")
        logger.info(f"📊 Número de agentes: {len(agent_os.agents) if hasattr(agent_os, 'agents') else 'N/A'}")
        
    elif test_mode == "interactive":
        # Modo interativo - iniciar servidor para teste manual
        logger.info("🚀 Iniciando servidor Agent OS para teste interativo...")
        logger.info("📡 Acesse: http://localhost:8000")
        logger.info("🛑 Use Ctrl+C para parar")
        
        try:
            app = agent_os.get_app()
            logger.info(f"📋 App FastAPI criada: {app}")
            logger.info(f"📋 Rotas disponíveis: {len(app.routes)}")
            
            # Mostrar algumas rotas
            for i, route in enumerate(app.routes[:5]):
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    logger.info(f"  {i+1}. {route.methods} {route.path}")
            
            logger.info("🌐 Iniciando servidor na porta 8000...")
            
            # Usar uvicorn diretamente para evitar problemas com reload
            import uvicorn
            config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
            server = uvicorn.Server(config)
            await server.serve()
        except KeyboardInterrupt:
            logger.info("🛑 Servidor interrompido pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar servidor: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    elif test_mode == "api":
        # Teste de API - verificar endpoints
        logger.info("🔌 Testando endpoints da API...")
        app = agent_os.get_app()
        
        # Listar rotas disponíveis
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append(f"{route.methods} {route.path}")
        
        logger.info(f"📋 Rotas disponíveis: {len(routes)}")
        for route in routes[:10]:  # Mostrar apenas as primeiras 10
            logger.info(f"  {route}")
        
        if len(routes) > 10:
            logger.info(f"  ... e mais {len(routes) - 10} rotas")

async def main():
    parser = argparse.ArgumentParser(description="Teste Agent OS com agentes gerados pelo agentmaker2.py")
    parser.add_argument("--agents-dir", "-a", default="../01-agents", 
                       help="Diretório contendo os agentes gerados")
    parser.add_argument("--max-agents", type=int, 
                       help="Número máximo de agentes para carregar (para teste)")
    parser.add_argument("--test-mode", choices=["basic", "interactive", "api"], 
                       default="basic", help="Modo de teste")
    parser.add_argument("--db-type", choices=["sqlite", "postgres", "none"], 
                       default="sqlite", help="Tipo de banco de dados")
    parser.add_argument("--db-path", default="agent_os_test.db", 
                       help="Caminho do banco SQLite")
    parser.add_argument("--db-url", 
                       help="URL do banco PostgreSQL")
    parser.add_argument("--verbose", action="store_true", 
                       help="Logging verboso")
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging(args.verbose)
    
    logger.info("🚀 Iniciando teste do Agent OS")
    logger.info(f"📁 Diretório de agentes: {args.agents_dir}")
    logger.info(f"🧪 Modo de teste: {args.test_mode}")
    
    # Verificar se o diretório existe
    agents_dir = Path(args.agents_dir)
    if not agents_dir.exists():
        logger.error(f"❌ Diretório não encontrado: {agents_dir}")
        return 1
    
    # Verificar variáveis de ambiente necessárias
    if not os.environ.get("GOOGLE_API_KEY"):
        logger.error("❌ GOOGLE_API_KEY não configurada")
        logger.error("💡 Dica: Crie um arquivo .env com GOOGLE_API_KEY=sua_chave")
        logger.error("💡 Ou execute: python setup_env.py")
        return 1
    
    try:
        # Carregar agentes
        agents = await load_all_agents(agents_dir, args.max_agents)
        
        if not agents:
            logger.error("❌ Nenhum agente foi carregado com sucesso")
            return 1
        
        # Configurar banco de dados
        db_config = None
        if args.db_type != "none":
            db_config = {
                'enabled': True,
                'type': args.db_type,
                'path': args.db_path,
                'url': args.db_url
            }
        
        # Criar Agent OS
        agent_os = create_agent_os(agents, db_config)
        
        # Executar testes
        test_agent_os(agent_os, args.test_mode)
        
        logger.info("✅ Teste concluído com sucesso!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))
