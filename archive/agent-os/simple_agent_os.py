#!/usr/bin/env python3
"""
TESTE SIMPLES AGENT OS - Script simplificado para testar o Agent OS

Este script testa o Agent OS de forma mais direta, sem reload automático.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Importações do Agno
from agno.os import AgentOS
from agno.agent import Agent
from agno.models.google import Gemini

load_dotenv()

logger = logging.getLogger("simple_agent_os")

def setup_logging():
    """Configura logging simples."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("simple_agent_os.log", encoding="utf-8")
        ]
    )

async def create_simple_agent(name: str, description: str, instructions: str) -> Agent:
    """Cria um agente simples do Agno."""
    model = Gemini(
        id="gemini-2.5-pro",
        api_key=os.environ.get("GOOGLE_API_KEY"),
        temperature=0.5
    )
    
    agent = Agent(
        model=model,
        name=name,
        description=description,
        instructions=[instructions],
        markdown=True
    )
    
    return agent

async def main():
    setup_logging()
    
    logger.info("🚀 Criando Agent OS simples...")
    
    # Verificar API key
    if not os.environ.get("GOOGLE_API_KEY"):
        logger.error("❌ GOOGLE_API_KEY não configurada")
        return 1
    
    try:
        # Criar alguns agentes simples
        logger.info("📝 Criando agentes...")
        
        agent1 = await create_simple_agent(
            name="TestAgent1",
            description="Agente de teste 1",
            instructions="Você é um agente de teste especializado em responder perguntas básicas."
        )
        
        agent2 = await create_simple_agent(
            name="TestAgent2", 
            description="Agente de teste 2",
            instructions="Você é um agente de teste especializado em análise de dados."
        )
        
        logger.info("✅ Agentes criados com sucesso")
        
        # Criar Agent OS
        logger.info("🏗️  Criando Agent OS...")
        agent_os = AgentOS(
            description="Agent OS Simples para Teste",
            agents=[agent1, agent2]
        )
        
        logger.info("✅ Agent OS criado com sucesso")
        
        # Obter app FastAPI
        app = agent_os.get_app()
        logger.info(f"📋 App FastAPI: {app}")
        logger.info(f"📋 Rotas: {len(app.routes)}")
        
        # Mostrar algumas rotas
        for i, route in enumerate(app.routes[:10]):
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                logger.info(f"  {i+1}. {route.methods} {route.path}")
        
        # Iniciar servidor
        logger.info("🌐 Iniciando servidor na porta 8000...")
        logger.info("📡 Acesse: http://localhost:8000")
        logger.info("📚 Documentação: http://localhost:8000/docs")
        logger.info("🛑 Use Ctrl+C para parar")
        
        # Usar uvicorn diretamente
        import uvicorn
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("🛑 Servidor interrompido pelo usuário")
        return 0
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
