import argparse
import asyncio
import os
import traceback
import json # Added for JSON parsing
import inspect # Added to resolve NameError
from .adk_models import AdminTaskOutput # Added for Pydantic model validation 
# import google.generativeai as genai # Commented out: ADK handles API key via env var GOOGLE_API_KEY
import google.adk.events
print(f"--- Diagnostic: dir(google.adk.events) ---")
print(dir(google.adk.events))
if hasattr(google.adk.events, '__file__'):
    print(f"google.adk.events path: {google.adk.events.__file__}")
    # Optionally, list the contents of the events directory
    import os
    events_package_path = os.path.dirname(google.adk.events.__file__)
    print(f"Contents of google.adk.events directory ({events_package_path}): {os.listdir(events_package_path)}")
print(f"--- End Diagnostic ---")
from google.adk.events import Event
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.agents.callback_context import CallbackContext
# from google.generativeai.types import Content, Part # Commented out: ADK's Event.Content should be used, or types from google.genai if new SDK is directly used.
# If google-genai is installed and needed for Content/Part, the import would be:
from google.genai.types import Content, Part # Assuming google-genai is now the primary SDK

from .adk_config import (
    ADMIN_MODEL_STR, DEV_MODEL_STR, REVISOR_MODEL_STR, GEMINI_API_KEY,
    DEFAULT_PROJECT_PATH, DEFAULT_GOAL, DEFAULT_PAIRS, DEFAULT_ROUNDS
)
from .adk_agents import create_admin_llm_agent
from .adk_agents.dev_agent import create_dev_llm_agent
from .adk_agents.revisor_agent import create_revisor_llm_agent
from .adk_core.adk_setup import get_runner
# As definições de ferramentas não são usadas diretamente neste arquivo, mas são importantes para os agentes
# from adk_core.tool_definitions import admin_tools_adk, dev_tools_adk, revisor_tools_adk

# Define a constant for the main user ID to be used throughout
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

async def initialize_session_and_load_state(session_service, target_project_path, initial_user_id="codeswarm_orchestrator"):
    session = await session_service.create_session(app_name="codeswarm", user_id=initial_user_id)
    print(f"[Sessão] Nova sessão criada: {session.id}")
    # if args.debug: print(f"DEBUG: session_service instance in main_async (after create): {id(session_service)}")
    # if args.debug: print(f"DEBUG: Created session object: {session}")

    state_file_path = os.path.join(target_project_path, "codeswarm_state.json")
    if os.path.exists(state_file_path):
        try:
            with open(state_file_path, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            if not hasattr(session, 'state') or session.state is None:
                 print("[Aviso de Estado] session.state não está inicializado. Verifique a implementação de Session.")
            elif isinstance(session.state, dict):
                 session.state["summaries"] = state_data.get("summaries", [])
                 print(f"[Estado] Sumários anteriores carregados de {state_file_path}")
            else:
                print(f"[Aviso de Estado] session.state não é um dicionário. Tipo: {type(session.state)}")
        except Exception as e:
            print(f"[Estado] Falha ao carregar estado anterior: {e}")
    return session

def initialize_agents(args, admin_model_override, dev_model_override, revisor_model_override):
    try:
        admin_agent_instance = create_admin_llm_agent(model_override=admin_model_override)
        dev_agent_instances = [create_dev_llm_agent(i+1, model_override=dev_model_override) for i in range(args.pairs)]
        revisor_agent_instances = [create_revisor_llm_agent(i+1, model_override=revisor_model_override) for i in range(args.pairs)]
        # dev_revisor_pairs logic was commented out, so not including it here.
        return admin_agent_instance, dev_agent_instances, revisor_agent_instances
    except Exception as e:
        print(f"Erro durante a inicialização do agente: {e}")
        traceback.print_exc()
        raise # Re-raise after printing

async def run_admin_task_assignment_phase(admin_agent_instance, project_goal, target_project_path, current_round, previous_summaries, execute_agent_fn, debug_mode):
    print("[Orchestrator] Executando AdminAgent para atribuição de tarefas...")
    admin_task_input_dict = {
        "overall_project_goal": project_goal,
        "target_project_path": target_project_path,
        "round": current_round, # Corrected: pass current_round directly
        "previous_summaries": previous_summaries,
        "current_phase": "task_assignment"
    }
    admin_task_assignment_result = await execute_agent_fn(
        admin_agent_instance,
        admin_task_input_dict,
        "admin_task_assigner"
    )

    if debug_mode: print(f"[AdminAgent Task Assignment Output] {admin_task_assignment_result}")

    parsed_admin_output = None
    if admin_task_assignment_result and isinstance(admin_task_assignment_result, dict):
        # Simplified parsing logic assuming 'output_model' handles structure
        # Direct use of output_model means the result should already be the Pydantic object or a dict that can be validated
        # For CodeSwarm, agents return dicts that include status, and if successful, the Pydantic model's content might be nested.
        # The execute_agent_and_get_result function already tries to parse JSON from text.
        # If AdminAgent uses output_model=AdminTaskOutput, the result from execute_agent_and_get_result should be that model directly (or its dict form).
        try:
            # Assuming admin_task_assignment_result *is* the Pydantic model or its dict representation
            if isinstance(admin_task_assignment_result, AdminTaskOutput):
                 parsed_admin_output = admin_task_assignment_result
            else: # If it's a dict from JSON
                 parsed_admin_output = AdminTaskOutput.model_validate(admin_task_assignment_result)
            if debug_mode: print(f"[AdminAgent] Output parseado (AdminTaskOutput): {parsed_admin_output}")
        except Exception as e_parse:
            print(f"[AdminAgent ERRO] Falha ao validar resultado como AdminTaskOutput: {e_parse}. Resultado: {admin_task_assignment_result}")
            # Fallback to old parsing logic if direct validation fails (e.g. if result is nested)
            if 'admin_structured_output' in admin_task_assignment_result and admin_task_assignment_result['admin_structured_output']:
                content_to_parse = admin_task_assignment_result['admin_structured_output']
                # ... (rest of old parsing logic can be here if needed as deeper fallback) ...
            elif 'output_text' in admin_task_assignment_result and admin_task_assignment_result['output_text']:
                raw_text = admin_task_assignment_result['output_text']
                task_json_str = raw_text
                if raw_text.strip().startswith("```json"): task_json_str = raw_text.strip()[7:-3].strip()
                elif raw_text.strip().startswith("```") and raw_text.strip().endswith("```"): task_json_str = raw_text.strip()[3:-3].strip()
                try:
                    parsed_admin_output = AdminTaskOutput.model_validate_json(task_json_str)
                except Exception as e_text_json:
                    print(f"[AdminAgent ERRO] Falha ao parsear 'output_text' como AdminTaskOutput: {e_text_json}. Conteúdo: {task_json_str}")

    if parsed_admin_output and hasattr(parsed_admin_output, 'tasks') and isinstance(parsed_admin_output.tasks, list):
        task_list = [task.model_dump() for task in parsed_admin_output.tasks] # Convert Pydantic tasks to dicts for downstream
        if debug_mode: print(f"[AdminAgent] Tarefas atribuídas: {task_list}")
        return task_list
    else:
        error_message = f"AdminAgent não retornou uma lista de tarefas válida. Resultado: {admin_task_assignment_result}, Parseado: {parsed_admin_output}"
        print(f"[AdminAgent ERRO - Atribuição de Tarefas] {error_message}")
        return []

async def process_task_with_dev_revisor_loop(task_details_dict: dict, round_context: dict) -> dict:
    """
    Manages the iterative Dev-Revisor loop for a single task.
    """
    dev_id = task_details_dict.get("dev_id")
    revisor_id = task_details_dict.get("revisor_id")
    target_project_path = round_context["target_project_path"]
    execute_agent_fn = round_context["execute_agent_fn"]
    dev_agent_instances = round_context["dev_agent_instances"]
    revisor_agent_instances = round_context["revisor_agent_instances"]
    debug_mode = round_context["debug_mode"]

    if not dev_id or not (0 < dev_id <= len(dev_agent_instances)):
        msg = f"Tarefa com dev_id inválido ou ausente: {dev_id}."
        print(f"[Orchestrator ERRO] {msg}")
        return {"dev_id": dev_id, "revisor_id": revisor_id, "status": "error", "message": msg, "dev_result": None, "revisor_result": None, "attempts": 0, "approved": False}

    if not revisor_id or not (0 < revisor_id <= len(revisor_agent_instances)):
        msg = f"Tarefa com revisor_id inválido ou ausente: {revisor_id}."
        print(f"[Orchestrator ERRO] {msg}")
        return {"dev_id": dev_id, "revisor_id": revisor_id, "status": "error", "message": msg, "dev_result": None, "revisor_result": None, "attempts": 0, "approved": False}

    original_relative_path = task_details_dict.get("file_to_edit_or_create")
    if not original_relative_path:
        msg = f"Tarefa para DevAgent {dev_id} não contém 'file_to_edit_or_create'."
        print(f"[Orchestrator ERRO] {msg}")
        return {"dev_id": dev_id, "revisor_id": revisor_id, "status": "error", "message": msg, "dev_result": None, "revisor_result": None, "attempts": 0, "approved": False}

    absolute_file_path = os.path.normpath(os.path.join(target_project_path, original_relative_path))
    if not os.path.abspath(absolute_file_path).startswith(os.path.abspath(target_project_path)):
        msg = f"Caminho construído para DevAgent {dev_id} ('{absolute_file_path}') está fora do projeto alvo ('{target_project_path}')."
        print(f"[Orchestrator ERRO - Segurança] {msg}")
        return {"dev_id": dev_id, "revisor_id": revisor_id, "status": "error", "message": msg, "dev_result": None, "revisor_result": None, "attempts": 0, "approved": False}

    dev_agent_instance = dev_agent_instances[dev_id - 1]
    revisor_agent_instance = revisor_agent_instances[revisor_id - 1]

    current_dev_task_description = task_details_dict.get("dev_task_description")
    previous_revision_feedback = ""
    dev_result = None
    revisor_result = None
    approved = False

    MAX_DEV_REVISOR_CYCLES = 3
    for attempt in range(1, MAX_DEV_REVISOR_CYCLES + 1):
        print(f"[Orchestrator] Ciclo Dev-Revisor {attempt}/{MAX_DEV_REVISOR_CYCLES} para tarefa '{task_details_dict.get('task_id', 'N/A')}' (Dev {dev_id}, Revisor {revisor_id})")

        # --- DevAgent Phase ---
        current_dev_task_input = {
            "task_id": task_details_dict.get("task_id", f"task_unidentified_{dev_id}"),
            "dev_task_description": current_dev_task_description,
            "file_to_edit_or_create": absolute_file_path,
            "target_project_path": target_project_path,
            "previous_revision_feedback": previous_revision_feedback # Pass feedback from previous Revisor iteration
        }
        if debug_mode: print(f"[Orchestrator] DevAgent {dev_id} Input (Attempt {attempt}): {current_dev_task_input}")

        dev_result = await execute_agent_fn(dev_agent_instance, current_dev_task_input, agent_identifier_for_logging=f"DevAgent_{dev_id}_Attempt_{attempt}")
        if debug_mode: print(f"[DevAgent {dev_id} Output (Attempt {attempt})] {dev_result}")

        if not dev_result or dev_result.get("status") != "success": # Assuming DevAgentOutput has a 'status' field
            print(f"[Orchestrator] DevAgent {dev_id} falhou ou não reportou sucesso na tentativa {attempt}. Interrompendo ciclo para esta tarefa.")
            break

        # --- RevisorAgent Phase ---
        revisor_input_dict = {
            "file_to_review": absolute_file_path, # Path comes from original admin task, confirmed by Dev
            "focus_areas": task_details_dict.get("revisor_focus_areas", "Revisão geral"),
            "target_project_path": target_project_path,
            "dev_task_description": task_details_dict.get("dev_task_description") # For context
        }
        if debug_mode: print(f"[Orchestrator] RevisorAgent {revisor_id} Input (Attempt {attempt}): {revisor_input_dict}")

        revisor_result = await execute_agent_fn(revisor_agent_instance, revisor_input_dict, agent_identifier_for_logging=f"RevisorAgent_{revisor_id}_Attempt_{attempt}")
        if debug_mode: print(f"[RevisorAgent {revisor_id} Output (Attempt {attempt})] {revisor_result}")

        if not revisor_result or revisor_result.get("status") not in ["success", "requires_changes"]: # Revisor output Pydantic model should define this
            print(f"[Orchestrator] RevisorAgent {revisor_id} falhou ou retornou status inesperado na tentativa {attempt}. Interrompendo ciclo.")
            break

        # Assuming RevisorAgentOutput Pydantic model has an 'approved' boolean field
        # and 'review_comments' string field, accessed via the parsed 'revisor_result' dict.
        if isinstance(revisor_result, dict) and revisor_result.get("approved") == True: # Check for explicit True
            print(f"[Orchestrator] Tarefa '{task_details_dict.get('task_id', 'N/A')}' aprovada pelo Revisor {revisor_id} na tentativa {attempt}.")
            approved = True
            break # Exit loop if approved

        previous_revision_feedback = revisor_result.get("review_comments", "")
        if not previous_revision_feedback and not approved : # If not approved and no comments, something is wrong or it's an implicit approval not caught
             print(f"[Orchestrator AVISO] Revisor {revisor_id} não aprovou mas não forneceu comentários. Assumindo que mudanças são necessárias mas não especificadas.")
             previous_revision_feedback = "Revisor não aprovou o código, mas não forneceu comentários específicos. Por favor, revise cuidadosamente."


        if attempt == MAX_DEV_REVISOR_CYCLES:
            print(f"[Orchestrator] Máximo de ciclos Dev-Revisor ({MAX_DEV_REVISOR_CYCLES}) atingido para a tarefa '{task_details_dict.get('task_id', 'N/A')}'.")

    return {
        "dev_id": dev_id,
        "revisor_id": revisor_id,
        "task_details_original": task_details_dict, # Keep original task for reference
        "final_dev_result": dev_result,
        "final_revisor_result": revisor_result,
        "attempts": attempt,
        "approved": approved
    }

async def run_admin_logging_phase(admin_agent_instance, round_dev_revisor_outputs, target_project_path, current_round, execute_agent_fn, debug_mode):
    admin_logging_input_dict = {
        "dev_outputs": dev_outputs,
        "revisor_feedback": revisor_feedback,
        "target_project_path": target_project_path,
        "round": current_round, # Corrected: pass current_round
        "current_phase": "logging_and_updates"
    }

    print("[Orchestrator] Executando AdminAgent para logging e atualizações...")
    admin_log_result = await execute_agent_fn(admin_agent_instance, admin_logging_input_dict, agent_identifier_for_logging="admin_logger")

    if debug_mode: print(f"[AdminAgent Logging/Update Output] {admin_log_result}")
    if not admin_log_result or admin_log_result.get("status") != "success": # Assuming AdminLogOutput has a status
         print(f"[AdminAgent ERRO - Logging/Update] {admin_log_result.get('message', 'Sem mensagem ou resultado inválido') if isinstance(admin_log_result, dict) else 'Resultado inválido'}")
    return admin_log_result

def save_round_state(session, state_file_path, current_round_summary, target_project_path): # target_project_path passed for consistency, though state_file_path is already absolute
    if isinstance(session.state, dict):
        session.state["summaries"] = session.state.get("summaries", [])
        session.state["summaries"].append(current_round_summary)
    else:
        print("[Aviso de Estado] Não foi possível salvar sumários pois session.state não é um dicionário.")

    print(f"[Memória] Round {current_round_summary.get('round', 'N/A')} completed - session state updated automatically.")

    try:
        with open(state_file_path, "w", encoding="utf-8") as f:
            # Ensure data_to_save has a fallback if session.state is not a dict
            summaries_to_save = session.state.get("summaries", [current_round_summary]) if isinstance(session.state, dict) else [current_round_summary]
            data_to_save = {"summaries": summaries_to_save}
            json.dump(data_to_save, f, indent=2)
        print(f"[Estado] Sumários salvos em {state_file_path}")
        print(f"[Sessão] Round {current_round_summary.get('round', 'N/A')} state saved locally. Session ID: {session.id}")
    except Exception as e:
        print(f"[Estado] Falha ao salvar estado: {e}")


async def main_async(args_list=None): # Allow passing args for testing
    try:
        args, target_project_path, project_goal = parse_cli_args_and_setup_paths(args_list)
    except ValueError as e:
        print(f"Erro na configuração inicial: {e}")
        return

    if not GEMINI_API_KEY:
        print("Erro: GEMINI_API_KEY não encontrada. Configure no .env ou ambiente.")
        return

    session_service = InMemorySessionService()
    if args.debug: print(f"DEBUG: session_service instance in main_async: {id(session_service)}")

    session = await initialize_session_and_load_state(session_service, target_project_path, MAIN_USER_ID)

    if args.list_sessions: # Should be checked after session initialization if it needs session info
        print("Note: Using InMemorySessionService - sessions are not persisted across runs without explicit save/load.")
        print(f"Current session ID: {session.id}")
        return

    admin_model_override = args.model if args.model else ADMIN_MODEL_STR
    dev_model_override = args.model if args.model else DEV_MODEL_STR
    revisor_model_override = args.model if args.model else REVISOR_MODEL_STR

    try:
        admin_agent_instance, dev_agent_instances, revisor_agent_instances = initialize_agents(
            args, admin_model_override, dev_model_override, revisor_model_override
        )
    except Exception: # initialize_agents already prints traceback
        return

    state_file_path = os.path.join(target_project_path, "codeswarm_state.json") # Define here as it's used by save_round_state

    # --- Função auxiliar para executar agente e processar eventos (mantida aqui por enquanto) ---
    # Note: This function captures 'session_service', 'args', 'session' and 'MAIN_USER_ID' from the main_async scope.
    # If this were moved outside main_async, these would need to be passed as arguments.
    async def execute_agent_and_get_result(current_agent_instance, agent_input_dict, agent_identifier_for_logging="agent_user"):
        # nonlocal session_service # No longer needed if session_service is passed or accessed differently
        if args.debug: print(f"DEBUG: session_service instance at start of execute_agent_and_get_result: {id(session_service)}")
        
        current_runner = get_runner( 
            agent_instance=current_agent_instance,
            session_service_instance=session_service, 
            app_name="codeswarm"
        )
        if args.debug: print(f"DEBUG: session_service instance in current_runner: {id(current_runner.session_service)}")

        agent_name = getattr(current_agent_instance, 'name', agent_identifier_for_logging) # Use agent_identifier if name not present
        # Security check for dangerous tools
        if agent_name.startswith("DevAgentADK") or agent_name == "AdminAgentADK" or agent_identifier_for_logging == "admin_logger":
            dangerous_tools = ["execute_python_code", "execute_shell_command"]
            tool_call_detected_in_input = any(dt in json.dumps(agent_input_dict).lower() for dt in dangerous_tools)
            tool_is_dangerous_itself = False
            if hasattr(current_agent_instance, 'tools'):
                for tool in current_agent_instance.tools:
                    if getattr(tool._func, '__name__', '') in dangerous_tools:
                        tool_is_dangerous_itself = True
                        break
            
            if tool_call_detected_in_input or tool_is_dangerous_itself:
                confirm_msg = f"[Segurança] O Agente '{agent_name}' (Task: {agent_input_dict.get('current_phase', 'N/A')}) pode usar/solicitar uma ferramenta perigosa. Permitir? [y/N]: "
                if os.getenv("CODESWARM_AUTO_APPROVE_DANGEROUS_TOOLS", "false").lower() == "true":
                    print(f"{confirm_msg}Aprovado automaticamente via CODESWARM_AUTO_APPROVE_DANGEROUS_TOOLS.")
                    confirm = 'y'
                else:
                    confirm = input(confirm_msg).strip().lower()

                if confirm != 'y':
                    print("Execução negada pelo usuário.")
                    return {"status": "error", "message": "Execução de ferramenta perigosa negada."}

        input_json_str = json.dumps(agent_input_dict)
        message_for_agent = Content(parts=[Part(text=input_json_str)])
        final_agent_output = None

        if args.debug: print(f"DEBUG: Chamando run_async para {agent_name} com user_id={MAIN_USER_ID}, session_id={session.id}")

        try:
            async for event in current_runner.run_async(
                user_id=MAIN_USER_ID,
                session_id=session.id, 
                new_message=message_for_agent
            ):
                log_parts = [f"Evento ({agent_name}): Author='{event.author}'"]
                text_content, func_calls, func_responses = [], [], []
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text: text_content.append(part.text[:100] + "...")
                        if hasattr(part, 'function_call') and part.function_call: fc = part.function_call; func_calls.append(f"{{'name': '{fc.name}', 'args': {fc.args}}}")
                if hasattr(event, 'get_function_calls') and event.get_function_calls(): func_calls.extend([f"{{'name': '{c.name}', 'args': {c.args}}}" for c in event.get_function_calls()])
                if hasattr(event, 'get_function_responses') and event.get_function_responses(): func_responses.extend([f"{{'name': '{r.name}', 'response': {r.response}}}" for r in event.get_function_responses()])
                if text_content: log_parts.append(f"Content(text)='{' '.join(text_content)}'")
                if func_calls: log_parts.append(f"FunctionCalls=[{', '.join(func_calls)}]")
                if func_responses: log_parts.append(f"FunctionResponses=[{', '.join(func_responses)}]")
                if args.debug: print(", ".join(log_parts))
                
                if event.is_final_response():
                    if args.debug: print(f"DEBUG Final Event ({agent_name}): {event}")
                    if event.content and event.content.parts:
                        final_part = event.content.parts[-1]
                        if final_part.text:
                            try:
                                final_agent_output = json.loads(final_part.text)
                            except json.JSONDecodeError:
                                final_agent_output = {"output_text": final_part.text}
                        elif final_part.function_call:
                            fc = final_part.function_call
                            final_agent_output = {"function_call": {"name": fc.name, "args": dict(fc.args) if hasattr(fc.args, 'items') else fc.args}}
                    elif event.actions and event.actions.state_delta: # If agent used output_model and it changed state
                        final_agent_output = {"status": "success_state_updated", "delta": event.actions.state_delta, "message": "Agente concluiu com atualização de estado (output_model)."}


            if final_agent_output is None: # Fallback if no final_response event yielded processable data
                print(f"[{agent_name} AVISO] Nenhum resultado final processável dos eventos. Verifique se o agente usa output_model ou produz texto JSON.")
                return {"status": "error", "message": "Nenhum resultado final processável do agente."}
            return final_agent_output
        except Exception as e_run:
            print(f"[{agent_name} Exceção durante run_async] {e_run}")
            traceback.print_exc()
            return {"status": "error", "message": str(e_run)}

    # --- Main round orchestration function ---
    async def execute_round(round_context: dict) -> dict:
        current_round_num = round_context["current_round_num"]
        print(f"\n=== EXECUTING ROUND {current_round_num} via execute_round ===")

        # Extract necessary components from context
        admin_agent_instance = round_context["admin_agent_instance"]
        dev_agent_instances = round_context["dev_agent_instances"]
        revisor_agent_instances = round_context["revisor_agent_instances"]
        project_goal = round_context["project_goal"]
        target_project_path = round_context["target_project_path"]
        session_summaries = round_context["session_summaries"]
        execute_agent_fn = round_context["execute_agent_fn"]
        debug_mode = round_context["debug_mode"]

        task_list = await run_admin_task_assignment_phase(
            admin_agent_instance, project_goal, target_project_path,
            current_round_num, session_summaries,
            execute_agent_fn, debug_mode
        )
        round_context["task_list"] = task_list # Save admin assigned tasks to context
        if not task_list:
            print(f"[Orchestrator] Fim da Rodada {current_round_num} (via execute_round) devido à ausência de tarefas do AdminAgent.")
            round_context["status"] = "aborted_no_tasks"
            # Initialize other outputs as empty to avoid issues in summary
            round_context["dev_revisor_cycle_outputs"] = []
            round_context["admin_logging_result"] = {}
            return round_context

        # Initialize lists to store final outputs from the Dev-Revisor loops for each task
        dev_revisor_cycle_outputs = []

        for task_detail in task_list:
            task_result_summary = await process_task_with_dev_revisor_loop(task_detail, round_context)
            dev_revisor_cycle_outputs.append(task_result_summary)
        
        round_context["dev_revisor_cycle_outputs"] = dev_revisor_cycle_outputs

        # Adapt input for admin logging phase if necessary, e.g., extract final dev/revisor outputs
        # For now, pass the detailed cycle outputs. Admin prompt might need adjustment.
        final_dev_outputs_for_logging = [item.get("final_dev_result") for item in dev_revisor_cycle_outputs if item.get("final_dev_result")]
        final_revisor_feedback_for_logging = [item.get("final_revisor_result") for item in dev_revisor_cycle_outputs if item.get("final_revisor_result")]

        admin_log_result = await run_admin_logging_phase(
            admin_agent_instance, final_dev_outputs_for_logging, final_revisor_feedback_for_logging, target_project_path,
            current_round_num, execute_agent_fn, debug_mode
        )
        round_context["admin_logging_result"] = admin_log_result # Save admin log result to context
        round_context["status"] = "completed"
        return round_context

    # --- Main execution loop ---
    for current_round_num in range(1, args.rounds + 1):
        # Prepare context for the round
        current_round_context = {
            "current_round_num": current_round_num,
            "args": args, # Pass full args if specific flags needed by phases
            "target_project_path": target_project_path,
            "project_goal": project_goal,
            "session": session, # Pass the main session object
            "admin_agent_instance": admin_agent_instance,
            "dev_agent_instances": dev_agent_instances,
            "revisor_agent_instances": revisor_agent_instances,
            "execute_agent_fn": execute_agent_and_get_result, # Pass the agent executor
            "session_summaries": session.state.get("summaries", []), # Get latest summaries
            "debug_mode": args.debug
        }
        
        round_results_context = await execute_round(current_round_context)

        if round_results_context.get("status") == "aborted_no_tasks":
            break # Exit main loop if admin provided no tasks

        current_round_summary_data = {
            "round": current_round_num,
            "tasks_assigned": round_results_context.get("task_list", []), # From Admin phase
            "dev_revisor_cycle_outputs": round_results_context.get("dev_revisor_cycle_outputs", []), # Detailed outputs from Dev/Revisor loops
            "admin_logging_result": round_results_context.get("admin_logging_result", {})
        }
        save_round_state(session, state_file_path, current_round_summary_data, target_project_path)

    print("\nTodas as rodadas completas. Verifique os artefatos no diretório do projeto e os logs em docs/.")

if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except Exception as e: # Catch-all for any synchronous error during setup not caught by main_async's try-except
        print(f"Erro fatal na execução do script: {e}")
        traceback.print_exc()
