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

async def main_async():
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
    args = parser.parse_args()

    if not args.path:
        print("Erro: O caminho do projeto (target_project_path) é obrigatório. Defina via CLI (--path) ou DEFAULT_PROJECT_PATH no .env.")
        return
    if not args.goal:
        print("Erro: O objetivo do projeto (goal) é obrigatório. Defina via CLI (--goal) ou DEFAULT_GOAL no .env.")
        return

    target_project_path = os.path.abspath(args.path)
    if not os.path.isdir(target_project_path):
        try:
            os.makedirs(target_project_path, exist_ok=True)
            print(f"Diretório do projeto '{target_project_path}' não existia e foi criado.")
        except OSError as e:
            print(f"Erro: O caminho do projeto '{target_project_path}' não existe e não pôde ser criado: {e}")
            return
            
    project_goal = args.goal

    if not GEMINI_API_KEY: # Check if the key is missing
        print("Erro: GEMINI_API_KEY não encontrada no ambiente ou arquivo .env. Esta chave é configurada como GOOGLE_API_KEY para o ADK.")
        return
    # else: # Commented out direct configuration of google.generativeai
        # genai.configure(api_key=GEMINI_API_KEY) # ADK uses GOOGLE_API_KEY from environment
        # print("Chave GEMINI_API_KEY (configurada como GOOGLE_API_KEY) carregada e pronta para uso pelo ADK.")

    # --- Session service setup ---
    session_service = InMemorySessionService()
    if args.debug: print(f"DEBUG: session_service instance in main_async (before create): {id(session_service)}")

    # --- Session creation ---
    session = await session_service.create_session(app_name="codeswarm", user_id="codeswarm_orchestrator")
    print(f"[Sessão] Nova sessão criada: {session.id}")
    if args.debug: print(f"DEBUG: session_service instance in main_async (after create): {id(session_service)}")
    if args.debug: print(f"DEBUG: Created session object: {session}")

    # Define a constant for the main user ID to be used throughout
    MAIN_USER_ID = "codeswarm_orchestrator"

    if args.list_sessions:
        print("Note: Using InMemorySessionService - sessions are not persisted.")
        print(f"Current session: {session.id}")
        return

    # --- Model override logic ---
    model_str = args.model if args.model else None
    admin_model = model_str if model_str else ADMIN_MODEL_STR
    dev_model = model_str if model_str else DEV_MODEL_STR
    revisor_model = model_str if model_str else REVISOR_MODEL_STR

    # --- Note: CallbackManager is no longer part of ADK API ---
    # Logging will be handled differently in the current ADK version

    # --- Agent initialization ---
    try:
        admin_agent_instance = create_admin_llm_agent(model_override=admin_model)
        dev_agent_instances = [create_dev_llm_agent(i+1, model_override=dev_model) for i in range(args.pairs)]
        revisor_agent_instances = [create_revisor_llm_agent(i+1, model_override=revisor_model) for i in range(args.pairs)]
        dev_revisor_pairs = []
        for i in range(args.pairs):
            def run_dev(task_input, dev_agent=dev_agent_instances[i]):
                return dev_agent.run(input_text=task_input)
            def run_revisor(dev_output, revisor_agent=revisor_agent_instances[i]):
                return revisor_agent.run(input_text=dev_output.output_text)
            # Note: SequentialAgent usage needs to be updated for current ADK API
            # seq = SequentialAgent(chain=[run_dev, run_revisor])
            # dev_revisor_pairs.append(seq)
    except Exception as e:
        print(f"Erro durante a inicialização do agente: {e}")
        traceback.print_exc()
        return

    # --- Arquivo de estado/memória intermediário ---
    state_file_path = os.path.join(target_project_path, "codeswarm_state.json")
    if os.path.exists(state_file_path):
        try:
            with open(state_file_path, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            # O estado da sessão ADK é um dicionário.
            if not hasattr(session, 'state') or session.state is None:
                 # session.state = {} # Inicialize se não existir (depende da implementação de Session)
                 print("[Aviso de Estado] session.state não está inicializado. Verifique a implementação de Session.")
            elif isinstance(session.state, dict):
                 session.state["summaries"] = state_data.get("summaries", [])
                 print(f"[Estado] Sumários anteriores carregados de {state_file_path}")
            else:
                print(f"[Aviso de Estado] session.state não é um dicionário. Tipo: {type(session.state)}")

        except Exception as e:
            print(f"[Estado] Falha ao carregar estado anterior: {e}")

    # --- Note: ChatMessageHistory is no longer part of ADK API ---
    # Memory management is handled differently in the current ADK version
    print("[Memória] Using ADK's built-in session state for memory management.")

    # --- Função auxiliar para executar agente e processar eventos ---
    async def execute_agent_and_get_result(current_agent_instance, agent_input_dict, agent_identifier_for_logging="agent_user"):
        nonlocal session_service 
        if args.debug: print(f"DEBUG: session_service instance at start of execute_agent_and_get_result: {id(session_service)}")
        
        current_runner = get_runner( 
            agent_instance=current_agent_instance,
            session_service_instance=session_service, 
            app_name="codeswarm"
        )
        if args.debug: print(f"DEBUG: session_service instance in current_runner: {id(current_runner.session_service)}")

        # Refined security check for dangerous tool calls
        agent_name = getattr(current_agent_instance, 'name', '')
        if agent_name.startswith("DevAgentADK") or agent_name == "AdminAgentADK":
            # Heuristic: check for explicit tool call requests in the input dict
            dangerous_tools = ["execute_python_code", "execute_shell_command"]
            # Check for explicit tool call keys or values
            tool_call_detected = False
            # Simplified check - assuming agent_input_dict itself might contain the direct request or its string form
            input_str_for_check = json.dumps(agent_input_dict).lower()
            if any(dt in input_str_for_check for dt in dangerous_tools):
                tool_call_detected = True
            
            if tool_call_detected: # Check if a dangerous tool call is likely
                tool_calls_in_event_history = False
                # Check current agent's tools for dangerous ones
                if hasattr(current_agent_instance, 'tools'):
                    for tool in current_agent_instance.tools:
                        if getattr(tool._func, '__name__', '') in dangerous_tools: # Access internal _func name
                            tool_call_detected = True
                            break
                
                if tool_call_detected:
                    confirm = input(f"[Segurança] O Agente '{agent_name}' pode tentar usar uma ferramenta perigosa ({', '.join(dangerous_tools)}). Permitir? [y/N]: ").strip().lower()
                    if confirm != 'y':
                        print("Execução negada pelo usuário.")
                        return {"status": "error", "message": "Execução de ferramenta perigosa negada pelo usuário."}

        # Prepara a mensagem para o agente
        input_json_str = json.dumps(agent_input_dict)
        message_for_agent = Content(parts=[Part(text=input_json_str)])

        final_agent_output = None
        if args.debug: print(f"DEBUG: Assinatura de current_runner.run_async: {inspect.signature(current_runner.run_async)}")
        # Use MAIN_USER_ID for run_async, agent_identifier_for_logging is for logs only
        if args.debug: print(f"DEBUG: Chamando run_async para {current_agent_instance.__class__.__name__} (logging as {agent_identifier_for_logging}) com user_id={MAIN_USER_ID}, session_id={session.id}, new_message (json)='{input_json_str[:200]}...'")

        try:
            # Use MAIN_USER_ID for run_async
            if args.debug: print(f"DEBUG: Attempting run_async with session_id={session.id}, user_id={MAIN_USER_ID}")
            # You can also try to explicitly get the session here to see if it's found by the service
            try:
                retrieved_session_before_run = await session_service.get_session(
                    session_id=session.id, 
                    user_id=MAIN_USER_ID,
                    app_name="codeswarm"  # Added app_name
                ) 
                if args.debug: print(f"DEBUG: Successfully retrieved session {retrieved_session_before_run.id} manually before run_async using user_id='{MAIN_USER_ID}'.")
            except Exception as e_get:
                if args.debug: print(f"DEBUG: FAILED to retrieve session manually before run_async using user_id='{MAIN_USER_ID}': {e_get}")

            async for event in current_runner.run_async(
                user_id=MAIN_USER_ID,  # Corrected: Use the main session user_id
                session_id=session.id, 
                new_message=message_for_agent
            ):
                agent_name_for_log = current_agent_instance.__class__.__name__
                log_parts = [f"Evento ({agent_name_for_log}): Author='{event.author}'"] # DEBUG prefix removed, will be conditional below
                
                text_content = []
                func_calls = []
                func_responses = []

                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_content.append(part.text[:100] + "...")
                        if hasattr(part, 'function_call') and part.function_call:
                            fc = part.function_call
                            func_calls.append(f"{{'name': '{fc.name}', 'args': {fc.args}}} (from part)")
                
                if hasattr(event, 'get_function_calls') and event.get_function_calls():
                    calls = event.get_function_calls()
                    func_calls.extend([f"{{'name': '{call.name}', 'args': {call.args}}} (from get_function_calls)" for call in calls])
                
                if hasattr(event, 'get_function_responses') and event.get_function_responses():
                    responses = event.get_function_responses()
                    func_responses.extend([f"{{'name': '{resp.name}', 'response': {resp.response}}} " for resp in responses])

                if text_content: log_parts.append(f"Content(text)='{' '.join(text_content)}'")
                if func_calls: log_parts.append(f"FunctionCalls=[{', '.join(func_calls)}]")
                if func_responses: log_parts.append(f"FunctionResponses=[{', '.join(func_responses)}]")
                if event.actions: log_parts.append(f"Actions={event.actions}")
                
                if args.debug: print(", ".join(log_parts))
                
                # Lógica para identificar se o evento é final e contém a resposta do agente
                # ADK's is_final_response() é o indicador primário.
                if event.is_final_response():
                    if args.debug: print(f"DEBUG Final Event ({agent_name_for_log}): Author: {event.author}, Content: {event.content}, Actions: {event.actions}")
                    if event.content and event.content.parts:
                        # A resposta final pode ser texto ou uma chamada de função.
                        # O ADK geralmente coloca a resposta final do LLM (texto ou função) na última parte do último evento.
                        final_part = event.content.parts[-1] # Considerar a última parte
                        if final_part.text:
                            try:
                                # Tentar decodificar como JSON se for a convenção esperada
                                final_agent_output = json.loads(final_part.text)
                                if args.debug: print(f"DEBUG: Saída final do agente (JSON decodificado de texto): {final_agent_output}")
                            except json.JSONDecodeError:
                                # Se não for JSON, tratar como texto simples
                                final_agent_output = {"output_text": final_part.text} # Ou apenas a string, dependendo do que se espera
                                if args.debug: print(f"DEBUG: Saída final do agente (texto direto): {final_part.text}")
                        elif final_part.function_call:
                            fc = final_part.function_call
                            final_agent_output = {"function_call": {"name": fc.name, "args": dict(fc.args) if hasattr(fc.args, 'items') else fc.args}}
                            if args.debug: print(f"DEBUG: Saída final do agente (FunctionCall): {final_agent_output}")
                        # Se houver múltiplos parts, pode ser necessário concatenar textos ou processar de forma mais complexa.
                        # Para este exemplo, focamos na última parte do evento final.
                    
                    # Se a resposta final for apenas uma ação (ex: state_delta) sem conteúdo explícito
                    if final_agent_output is None and event.actions and event.actions.state_delta:
                         final_agent_output = {"status": "state_updated", "delta": event.actions.state_delta, "message": "Ação de atualização de estado concluída."}
                         if args.debug: print(f"DEBUG: Saída final do agente (State Delta Action): {final_agent_output}")

            if final_agent_output is None:
                print(f"[{agent_name_for_log} AVISO] Nenhum resultado final (is_final_response=True com dados processáveis) foi obtido dos eventos do agente.")
                # Tenta pegar o último texto de qualquer evento do agente, se disponível, como fallback
                last_text_from_agent = ""
                async for evt_fallback in current_runner.run_async(user_id=MAIN_USER_ID, session_id=session.id, new_message=message_for_agent): # Re-iterar pode não ser ideal, mas para fallback
                    if evt_fallback.author == current_agent_instance.name and evt_fallback.content and evt_fallback.content.parts:
                        for p in evt_fallback.content.parts:
                            if p.text: last_text_from_agent = p.text # Pega o último texto
                if last_text_from_agent:
                    print(f"[{agent_name_for_log} FALLBACK] Usando último texto do agente como saída: {last_text_from_agent}")
                    final_agent_output = {"output_text": last_text_from_agent, "status": "fallback_text"}
                else:
                    return {"status": "error", "message": "Nenhum resultado final do agente e nenhum texto de fallback."}
            
            return final_agent_output

        except Exception as e_agent_run:
            print(f"[{current_agent_instance.__class__.__name__} Exceção durante run_async] {e_agent_run}")
            traceback.print_exc()
            return {"status": "error", "message": str(e_agent_run)}


    # --- Main execution loop ---
    for current_round in range(args.rounds):
        print(f"\n=== ROUND {current_round + 1} ===")
        round_dev_outputs = []
        round_revisor_feedback = []

        # 1. AdminAgent - Task Assignment
        print("[Orchestrator] Executando AdminAgent para atribuição de tarefas...")
        admin_task_input_dict = {
            "overall_project_goal": project_goal,
            "target_project_path": target_project_path,
            "round": current_round + 1,
            "previous_summaries": session.state.get("summaries", []),
            "current_phase": "task_assignment"
        }
        admin_task_assignment_result = await execute_agent_and_get_result(
            admin_agent_instance,
            admin_task_input_dict,
            "admin_task_assigner"
        )
        
        if args.debug: print(f"[AdminAgent Task Assignment Output] {admin_task_assignment_result}")

        # Como output_model foi removido do LlmAgent, precisamos parsear manualmente.
        # A saída esperada está em admin_task_assignment_result['admin_structured_output'] (se output_key funcionou)
        # ou em admin_task_assignment_result['output_text'] (se o LLM apenas retornou texto).
        parsed_admin_output = None
        if admin_task_assignment_result and isinstance(admin_task_assignment_result, dict):
            if 'admin_structured_output' in admin_task_assignment_result and admin_task_assignment_result['admin_structured_output']:
                # Idealmente, 'admin_structured_output' contém o JSON como string ou já como dict
                content_to_parse = admin_task_assignment_result['admin_structured_output']
                if isinstance(content_to_parse, str):
                    try:
                        # Tentar remover ```json ... ``` se presente
                        if content_to_parse.strip().startswith("```json"):
                            content_to_parse = content_to_parse.strip()[7:-3].strip()
                        elif content_to_parse.strip().startswith("```") and content_to_parse.strip().endswith("```"):
                            content_to_parse = content_to_parse.strip()[3:-3].strip()
                        parsed_admin_output = AdminTaskOutput.model_validate_json(content_to_parse)
                        if args.debug: print(f"[AdminAgent] Output parseado de 'admin_structured_output' (string JSON): {parsed_admin_output}")
                    except Exception as e_json_str:
                        print(f"[AdminAgent ERRO] Falha ao parsear 'admin_structured_output' (string) como AdminTaskOutput: {e_json_str}. Conteúdo: {content_to_parse}")
                elif isinstance(content_to_parse, dict): # Se já for um dict
                    try:
                        parsed_admin_output = AdminTaskOutput.model_validate(content_to_parse)
                        if args.debug: print(f"[AdminAgent] Output parseado de 'admin_structured_output' (dict): {parsed_admin_output}")
                    except Exception as e_dict:
                        print(f"[AdminAgent ERRO] Falha ao validar 'admin_structured_output' (dict) como AdminTaskOutput: {e_dict}. Conteúdo: {content_to_parse}")
                else:
                    print(f"[AdminAgent AVISO] 'admin_structured_output' não é string nem dict: {type(content_to_parse)}. Conteúdo: {content_to_parse}")

            elif 'output_text' in admin_task_assignment_result and admin_task_assignment_result['output_text']:
                # Fallback para 'output_text' se 'admin_structured_output' não funcionou
                raw_text = admin_task_assignment_result['output_text']
                if args.debug: print(f"[AdminAgent AVISO] Tentando parsear 'output_text' como AdminTaskOutput. Conteúdo: {raw_text}")
                task_json_str = None
                if raw_text.strip().startswith("```json"):
                    task_json_str = raw_text.strip()[7:-3].strip()
                elif raw_text.strip().startswith("```") and raw_text.strip().endswith("```"):
                    task_json_str = raw_text.strip()[3:-3].strip()
                else:
                    task_json_str = raw_text # Assumir que é JSON direto
                
                if task_json_str:
                    try:
                        parsed_admin_output = AdminTaskOutput.model_validate_json(task_json_str)
                        if args.debug: print(f"[AdminAgent] Output parseado de 'output_text': {parsed_admin_output}")
                    except Exception as e_text_json:
                        print(f"[AdminAgent ERRO] Falha ao parsear 'output_text' como AdminTaskOutput: {e_text_json}. Conteúdo: {task_json_str}")
            else:
                print(f"[AdminAgent ERRO] Nem 'admin_structured_output' nem 'output_text' utilizáveis no resultado do AdminAgent: {admin_task_assignment_result}")

        if parsed_admin_output and hasattr(parsed_admin_output, 'tasks') and isinstance(parsed_admin_output.tasks, list):
            task_list = [task.model_dump() for task in parsed_admin_output.tasks]
            if args.debug: print(f"[AdminAgent] Tarefas atribuídas (parseadas manualmente): {task_list}")
        else:
            error_message = f"AdminAgent não retornou uma lista de tarefas válida após o parsing manual. Resultado do agente: {admin_task_assignment_result}, Output parseado: {parsed_admin_output}"
            print(f"[AdminAgent ERRO - Atribuição de Tarefas] {error_message}")
            continue

        if not task_list: # Checagem final se a task_list está vazia
            print(f"[AdminAgent ERRO - Atribuição de Tarefas] Nenhuma tarefa válida foi processada.")
            continue

        # 2. Devs codificam
        dev_outputs = []
        for i, task_details in enumerate(task_list):
            dev_id = task_details.get("dev_id")
            if not dev_id:
                print(f"[Orchestrator ERRO] Tarefa para DevAgent {dev_id} não contém 'dev_id'.")
                # Store error for this dev task
                dev_outputs.append({
                    "dev_id": dev_id,
                    "task_details": task_details, # include original task for logging
                    "result": {"status": "error", "message": "Tarefa do AdminAgent não especificou 'dev_id'."}
                })
                continue

            original_relative_path = task_details.get("file_to_edit_or_create")

            if not original_relative_path:
                print(f"[Orchestrator ERRO] Tarefa para DevAgent {dev_id} não contém 'file_to_edit_or_create'.")
                # Store error for this dev task
                dev_outputs.append({
                    "dev_id": dev_id,
                    "task_details": task_details, # include original task for logging
                    "result": {"status": "error", "message": "Tarefa do AdminAgent não especificou 'file_to_edit_or_create'."}
                })
                continue

            # Construct the full absolute path safely
            # os.path.normpath is used to clean up the path (e.g., remove trailing slashes or resolve '..')
            # os.path.join is crucial for platform-independent path construction.
            absolute_file_path = os.path.normpath(os.path.join(target_project_path, original_relative_path))

            # Security check: Ensure the constructed path is still within the target_project_path
            # This prevents directory traversal issues if original_relative_path contains '..' excessively
            if not os.path.abspath(absolute_file_path).startswith(os.path.abspath(target_project_path)):
                print(f"[Orchestrator ERRO - Segurança] Caminho construído para DevAgent {dev_id} ('{absolute_file_path}') está fora do diretório de projeto alvo ('{target_project_path}').")
                dev_outputs.append({
                    "dev_id": dev_id,
                    "task_details": task_details,
                    "result": {"status": "error", "message": f"Tentativa de acesso a caminho fora do projeto alvo: {original_relative_path}"}
                })
                continue
            
            # Update the task_details with the new absolute path to be passed to DevAgent
            # Or, if DevAgent expects 'file_to_edit_or_create' directly in its input, prepare it here.
            current_dev_task_input = {
                "task_id": task_details.get("task_id", f"task_{i+1}"), # Assuming task_id might exist or generate one
                "dev_task_description": task_details.get("dev_task_description"),
                "file_to_edit_or_create": absolute_file_path, # Pass the corrected, absolute path
                "target_project_path": target_project_path # DevAgent prompt might still want this for context
            }
            if args.debug:
                print(f"[Orchestrator] DevAgent {dev_id} Input: {current_dev_task_input}")

            # Execute DevAgent with current_dev_task_input
            print(f"[Orchestrator] Executando DevAgent {dev_id}...")
            dev_result = await execute_agent_and_get_result(dev_agent_instances[dev_id-1], current_dev_task_input, agent_identifier_for_logging=f"DevAgent_{dev_id}")
            dev_outputs.append({"dev_id": dev_id, "result": dev_result})
            if args.debug: print(f"[DevAgent {dev_id} Output] {dev_result}")

        # 3. Revisores revisam
        revisor_feedback = []
        for i, revisor_agent_instance_loop in enumerate(revisor_agent_instances):
            revisor_id_to_match = i + 1
            
            # Find the original task assigned by Admin for this revisor_id
            original_task_for_revisor = next((t for t in task_list if t.get("revisor_id") == revisor_id_to_match), None)

            if not original_task_for_revisor:
                if args.debug: print(f"[RevisorAgent {revisor_id_to_match}] No original task found with revisor_id {revisor_id_to_match}.")
                continue

            # Find the corresponding dev_id from the original task
            dev_id_for_this_revisor_task = original_task_for_revisor.get("dev_id")
            if not dev_id_for_this_revisor_task:
                if args.debug: print(f"[RevisorAgent {revisor_id_to_match}] Original task for revisor_id {revisor_id_to_match} does not specify a dev_id.")
                continue
                
            # Find the output of the DevAgent that handled this task
            dev_output_for_review = next((d_out for d_out in dev_outputs if d_out.get("dev_id") == dev_id_for_this_revisor_task), None)

            if not dev_output_for_review:
                if args.debug: print(f"[RevisorAgent {revisor_id_to_match}] No DevAgent output found for dev_id {dev_id_for_this_revisor_task}.")
                continue

            # Check if the DevAgent was successful before attempting revision
            dev_result_data = dev_output_for_review.get("result", {})
            # Assuming dev_result_data is a dictionary like {'status': 'success', 'message': '...'}
            # or {'output_text': '{"status": "success", ...}'}
            
            dev_status_is_success = False
            if isinstance(dev_result_data, dict) and dev_result_data.get("status") == "success":
                dev_status_is_success = True
            elif isinstance(dev_result_data, dict) and 'output_text' in dev_result_data:
                try:
                    # Dev output might be a JSON string within output_text
                    inner_dev_json = json.loads(dev_result_data['output_text'])
                    if isinstance(inner_dev_json, dict) and inner_dev_json.get("status") == "success":
                        dev_status_is_success = True
                except json.JSONDecodeError:
                    # If not JSON, and no explicit status, assume failure for safety unless prompt guarantees success output structure
                    if args.debug: print(f"[RevisorAgent {revisor_id_to_match}] DevAgent output_text for dev_id {dev_id_for_this_revisor_task} is not a success JSON.")
                except Exception: # Catch any other parsing errors
                    if args.debug: print(f"[RevisorAgent {revisor_id_to_match}] Error parsing DevAgent output_text for dev_id {dev_id_for_this_revisor_task}.")


            if not dev_status_is_success:
                print(f"[RevisorAgent {revisor_id_to_match}] Skipping revision for dev_id {dev_id_for_this_revisor_task} as DevAgent did not report success. Dev output: {dev_result_data}")
                revisor_feedback.append({
                    "revisor_id": revisor_id_to_match,
                    "result": {"status": "skipped", "message": f"Revision skipped for dev_id {dev_id_for_this_revisor_task} due to DevAgent failure or non-success status."}
                })
                continue
            
            file_to_review_path = original_task_for_revisor.get("file_to_edit_or_create") # Path comes from original admin task
            if not file_to_review_path: # Should have been caught earlier by Dev path checks
                print(f"[RevisorAgent {i+1}] ERRO: Tarefa de revisão (baseada na tarefa do Admin para dev {dev_id_for_this_revisor_task}) sem 'file_to_edit_or_create'.")
                continue

            revisor_input_dict = {
                "file_to_review": file_to_review_path,
                "focus_areas": original_task_for_revisor.get("revisor_focus_areas", "Revisão geral"),
                "target_project_path": target_project_path,
                "dev_task_description": original_task_for_revisor.get("dev_task_description") # For context
            }
            
            print(f"[Orchestrator] Executando RevisorAgent {revisor_id_to_match} for dev_id {dev_id_for_this_revisor_task} on file {file_to_review_path}...")
            revisor_result = await execute_agent_and_get_result(revisor_agent_instance_loop, revisor_input_dict, agent_identifier_for_logging=f"RevisorAgent_{revisor_id_to_match}")
            revisor_feedback.append({"revisor_id": revisor_id_to_match, "result": revisor_result})
            if args.debug: print(f"[RevisorAgent {revisor_id_to_match} Output] {revisor_result}")

        # 4. Admin registra/atualiza
        admin_logging_input_dict = {
            "dev_outputs": dev_outputs,
            "revisor_feedback": revisor_feedback,
            "target_project_path": target_project_path,
            "round": current_round + 1,
            "current_phase": "logging_and_updates"
        }
        
        print("[Orchestrator] Executando AdminAgent para logging e atualizações...")
        admin_log_result = await execute_agent_and_get_result(admin_agent_instance, admin_logging_input_dict, agent_identifier_for_logging="admin_logger")
        
        if args.debug: print(f"[AdminAgent Logging/Update Output] {admin_log_result}")
        if not admin_log_result or admin_log_result.get("status") != "success":
             print(f"[AdminAgent ERRO - Logging/Update] {admin_log_result.get('message', 'Sem mensagem ou resultado inválido')}")
        
        # Atualiza o estado da sessão
        current_summaries = {
            "round": current_round + 1,
            "dev_outputs": dev_outputs,
            "revisor_feedback": revisor_feedback,
            "admin_task_assignment_result": admin_task_assignment_result, # Log do resultado da atribuição
            "admin_logging_result": admin_log_result # Log do resultado do logging
        }
        if isinstance(session.state, dict):
            session.state["summaries"] = session.state.get("summaries", []) # Garante que é uma lista
            session.state["summaries"].append(current_summaries) # Adiciona o sumário da rodada atual
        else:
            print("[Aviso de Estado] Não foi possível salvar sumários pois session.state não é um dicionário.")

        # --- Note: Memory management updated for current ADK API ---
        # Session state is automatically managed by ADK's session service
        print(f"[Memória] Round {current_round + 1} completed - session state updated automatically.")

        try:
            with open(state_file_path, "w", encoding="utf-8") as f:
                data_to_save = {"summaries": session.state.get("summaries", [current_summaries]) if isinstance(session.state, dict) else [current_summaries]}
                json.dump(data_to_save, f, indent=2)
            print(f"[Estado] Sumários salvos em {state_file_path}")
            # Note: InMemorySessionService doesn't persist sessions
            print(f"[Sessão] Round {current_round + 1} state saved locally. Session ID: {session.id}")
        except Exception as e:
            print(f"[Estado] Falha ao salvar estado: {e}")

    print("\nTodas as rodadas completas. Veja project_logs/ para changelog e atualizações da lista de tarefas.")

if __name__ == "__main__":
    asyncio.run(main_async())
