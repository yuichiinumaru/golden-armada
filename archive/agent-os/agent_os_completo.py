#!/usr/bin/env python3
"""
AGENT OS COMPLETO - Script para carregar todos os agentes gerados e iniciar o Agent OS

Este script carrega todos os agentes da pasta 01-generated-agents e inicia
um Agent OS completo com todos eles disponíveis.
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path
from typing import List, Any
from dotenv import load_dotenv

# Importações do Agno
from agno.os import AgentOS
from agno.models.google import Gemini

load_dotenv()

logger = logging.getLogger("agent_os_completo")

def setup_logging(verbose: bool = False):
    """Configura logging para o Agent OS completo."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("agent_os_completo.log", encoding="utf-8")
        ]
    )

async def load_agent_from_file(file_path: Path) -> Any:
    """
    Carrega dinamicamente um agente de um arquivo Python.
    
    Args:
        file_path: Caminho para o arquivo do agente
        
    Returns:
        Instância do agente do Agno ou None se falhar
    """
    try:
        import importlib.util
        
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
        
        # Encontrar a classe do agente
        agent_class_name = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                attr_name.endswith("Agent") and 
                attr_name != "Agent"):
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
            logger.info(f"✅ Carregado: {agent_class_name}")
            return agent_instance.agent
        else:
            logger.error(f"❌ Agente não configurado: {agent_class_name}")
            return None
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar {file_path.name}: {e}")
        return None

async def load_all_agents(agents_dir: Path, max_agents: int = None, verbose: bool = False) -> List[Any]:
    """
    Carrega todos os agentes de um diretório.
    
    Args:
        agents_dir: Diretório contendo os agentes
        max_agents: Número máximo de agentes para carregar (None = todos)
        verbose: Se deve mostrar logs detalhados
        
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
    
    # Limitar número de agentes se especificado
    if max_agents:
        agent_files = agent_files[:max_agents]
        logger.info(f"🔢 Limitando a {max_agents} agentes para teste")
    
    loaded_agents = []
    failed_count = 0
    
    # Mostrar progresso
    total_files = len(agent_files)
    logger.info(f"📥 Carregando {total_files} agentes...")
    
    for i, agent_file in enumerate(agent_files, 1):
        if verbose or i % 10 == 0 or i == total_files:
            logger.info(f"📥 [{i}/{total_files}] Carregando: {agent_file.name}")
        
        agent_instance = await load_agent_from_file(agent_file)
        if agent_instance:
            loaded_agents.append(agent_instance)
        else:
            failed_count += 1
    
    logger.info(f"✅ Carregados {len(loaded_agents)} agentes com sucesso")
    if failed_count > 0:
        logger.warning(f"⚠️  {failed_count} agentes falharam ao carregar")
    
    return loaded_agents

def create_agent_os(agents: List[Any], description: str = None) -> AgentOS:
    """
    Cria uma instância do Agent OS com os agentes carregados.
    
    Args:
        agents: Lista de instâncias de agentes
        description: Descrição personalizada do Agent OS
        
    Returns:
        Instância do Agent OS configurada
    """
    if description is None:
        description = f"AgentMaker OS Completo - {len(agents)} agentes especializados"
    
    logger.info(f"🏗️  Criando Agent OS com {len(agents)} agentes")
    
    # Criar Agent OS
    agent_os = AgentOS(
        description=description,
        agents=agents
    )
    
    logger.info("✅ Agent OS criado com sucesso")
    return agent_os

async def start_server(agent_os: AgentOS, port: int = 8000, verbose: bool = False):
    """
    Inicia o servidor Agent OS.
    
    Args:
        agent_os: Instância do Agent OS
        port: Porta para o servidor
        verbose: Se deve mostrar logs detalhados
    """
    logger.info(f"🌐 Iniciando servidor Agent OS na porta {port}...")
    logger.info(f"📡 Acesse: http://localhost:{port}")
    logger.info(f"📚 Documentação: http://localhost:{port}/docs")
    logger.info(f"🤖 Agentes: http://localhost:{port}/agents")
    logger.info(f"🔧 Configuração: http://localhost:{port}/config")
    logger.info("🛑 Use Ctrl+C para parar")
    
    try:
        # Obter app FastAPI
        app = agent_os.get_app()
        
        if verbose:
            logger.info(f"📋 App FastAPI: {app}")
            logger.info(f"📋 Rotas disponíveis: {len(app.routes)}")
            
            # Mostrar algumas rotas importantes
            important_routes = ["/docs", "/agents", "/config", "/openapi.json"]
            for route in app.routes:
                if hasattr(route, 'path') and route.path in important_routes:
                    logger.info(f"  📍 {route.methods} {route.path}")
        
        # Iniciar servidor
        import uvicorn
        config = uvicorn.Config(
            app, 
            host="0.0.0.0", 
            port=port, 
            log_level="info" if verbose else "warning"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        if verbose:
            import traceback
            logger.error(traceback.format_exc())

async def main():
    parser = argparse.ArgumentParser(description="Agent OS Completo com todos os agentes gerados")
    parser.add_argument("--agents-dir", "-a", default="../01-agents", 
                       help="Diretório contendo os agentes gerados")
    parser.add_argument("--max-agents", type=int, 
                       help="Número máximo de agentes para carregar (padrão: todos)")
    parser.add_argument("--port", type=int, default=8000,
                       help="Porta para o servidor (padrão: 8000)")
    parser.add_argument("--description", 
                       help="Descrição personalizada para o Agent OS")
    parser.add_argument("--verbose", action="store_true", 
                       help="Logging verboso")
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging(args.verbose)
    
    logger.info("🚀 AGENT OS COMPLETO - Iniciando...")
    logger.info(f"📁 Diretório de agentes: {args.agents_dir}")
    logger.info(f"🌐 Porta do servidor: {args.port}")
    if args.max_agents:
        logger.info(f"🔢 Limite de agentes: {args.max_agents}")
    else:
        logger.info("🔢 Carregando TODOS os agentes")
    
    # Verificar se o diretório existe
    agents_dir = Path(args.agents_dir)
    if not agents_dir.exists():
        logger.error(f"❌ Diretório não encontrado: {agents_dir}")
        return 1
    
    # Verificar variáveis de ambiente necessárias
    if not os.environ.get("GOOGLE_API_KEY"):
        logger.error("❌ GOOGLE_API_KEY não configurada")
        logger.error("💡 Execute: python setup_env.py create")
        return 1
    
    try:
        # Carregar agentes
        agents = await load_all_agents(agents_dir, args.max_agents, args.verbose)
        
        if not agents:
            logger.error("❌ Nenhum agente foi carregado com sucesso")
            return 1
        
        # Criar Agent OS
        agent_os = create_agent_os(agents, args.description)
        
        # Iniciar servidor
        await start_server(agent_os, args.port, args.verbose)
        
        logger.info("✅ Agent OS executado com sucesso!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro durante a execução: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
