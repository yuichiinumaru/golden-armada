import argparse
import asyncio
import os
import traceback
import json
from google.genai.types import Content, Part
from .adk_config import (
    GEMINI_API_KEY,
    DEFAULT_PROJECT_PATH, DEFAULT_GOAL, DEFAULT_PAIRS, DEFAULT_ROUNDS
)
from .workflow import create_codeswarm_workflow
from .adk_core.adk_setup import get_runner
from google.adk.sessions import InMemorySessionService

MAIN_USER_ID = "codeswarm_orchestrator"

def parse_cli_args_and_setup_paths(args_list=None) -> (argparse.Namespace, str, str):
    parser = argparse.ArgumentParser(
        description="CodeSwarm: ADK Multi-Agent Coding Project",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-P", "--path",
        type=str,
        help="Caminho absoluto para uma pasta de projeto existente onde os agentes irão trabalhar (target_project_path).",
        default=DEFAULT_PROJECT_PATH,
        required=False
    )
    parser.add_argument(
        "-g", "--goal",
        type=str,
        help="Objetivo do projeto (linguagem natural).",
        default=DEFAULT_GOAL,
        required=False
    )
    parser.add_argument(
        "-x", "--pairs",
        type=int,
        default=int(DEFAULT_PAIRS),
        help="Número de pares Dev/Revisor."
    )
    parser.add_argument(
        "-r", "--rounds",
        type=int,
        default=int(DEFAULT_ROUNDS),
        help="Número de rodadas para executar."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Ativa o modo de depuração com logs detalhados."
    )
    parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="ID da sessão ADK a ser carregada (se não fornecido, cria nova)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override do modelo Gemini para todos os agentes (opcional)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Note: Session resumption not available with InMemorySessionService."
    )
    parser.add_argument(
        "--list-sessions",
        action="store_true",
        help="Shows current session information (sessions are not persisted with InMemorySessionService)."
    )
    args = parser.parse_args(args_list)

    if not args.path:
        print("Erro: O caminho do projeto (target_project_path) é obrigatório. Defina via CLI (--path) ou DEFAULT_PROJECT_PATH no .env.")
        # Consider raising an exception or sys.exit(1) for script usage
        raise ValueError("Project path is required.")
    if not args.goal:
        print("Erro: O objetivo do projeto (goal) é obrigatório. Defina via CLI (--goal) ou DEFAULT_GOAL no .env.")
        raise ValueError("Project goal is required.")

    target_project_path = os.path.abspath(args.path)
    if not os.path.isdir(target_project_path):
        try:
            os.makedirs(target_project_path, exist_ok=True)
            print(f"Diretório do projeto '{target_project_path}' não existia e foi criado.")
        except OSError as e:
            print(f"Erro: O caminho do projeto '{target_project_path}' não existe e não pôde ser criado: {e}")
            raise # Re-raise after printing
            
    project_goal = args.goal
    return args, target_project_path, project_goal

async def main_async(args_list=None):
    try:
        args, target_project_path, project_goal = parse_cli_args_and_setup_paths(args_list)
    except ValueError as e:
        print(f"Erro na configuração inicial: {e}")
        return

    if not GEMINI_API_KEY:
        print("Erro: GEMINI_API_KEY não encontrada. Configure no .env ou ambiente.")
        return

    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="codeswarm", user_id=MAIN_USER_ID)
    print(f"[Sessão] Nova sessão criada: {session.id}")

    workflow = create_codeswarm_workflow(pairs=args.pairs, model_override=args.model)
    
    runner = get_runner(
        agent_instance=workflow,
        session_service_instance=session_service,
        app_name="codeswarm"
    )

    initial_state = {
        "overall_project_goal": project_goal,
        "target_project_path": target_project_path,
        "rounds": args.rounds,
        "pairs": args.pairs,
        "debug_mode": args.debug,
        "summaries": []
    }

    # Update the session with the initial state
    session.state.update(initial_state)

    message_for_agent = Content(parts=[Part(text=json.dumps(initial_state))])

    async for event in runner.run_async(
        user_id=MAIN_USER_ID,
        session_id=session.id,
        new_message=message_for_agent
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_part = event.content.parts[-1]
                if final_part.text:
                    print(f"Workflow finalizou com a seguinte mensagem: {final_part.text}")
                else:
                    print("Workflow finalizou.")
            else:
                print("Workflow finalizou.")

if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except Exception as e:
        print(f"Erro fatal na execução do script: {e}")
        traceback.print_exc()
