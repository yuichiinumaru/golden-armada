import argparse
import asyncio
import os
import traceback
import json
import inspect
import re
from .adk_models import AdminTaskOutput
from pathlib import Path
import google.adk.events
# print(f"--- Diagnostic: dir(google.adk.events) ---")
# print(dir(google.adk.events))
# if hasattr(google.adk.events, '__file__'):
#     print(f"google.adk.events path: {google.adk.events.__file__}")
#     events_package_path = os.path.dirname(google.adk.events.__file__)
#     print(f"Contents of google.adk.events directory ({events_package_path}): {os.listdir(events_package_path)}")
print(f"--- End Diagnostic ---")

from google.adk.events import Event, EventActions
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from .adk_config import (
    ADMIN_MODEL_STR, DEV_MODEL_STR, REVISOR_MODEL_STR, GEMINI_API_KEY,
    DEFAULT_PROJECT_PATH, DEFAULT_GOAL, DEFAULT_PAIRS, DEFAULT_ROUNDS
)
from .adk_agents import create_admin_llm_agent, load_instruction_from_file
from .adk_agents.dev_agent import create_dev_llm_agent
from .adk_agents.revisor_agent import create_revisor_llm_agent
from .adk_core.adk_setup import get_runner
from .adk_core.tool_logic import (
    write_file as tool_write_file,
    read_file as tool_read_file,
    execute_python_code as tool_execute_python_code,
    execute_shell_command as tool_execute_shell_command
)

async def _execute_python_tool_directly(script_path: str, target_project_path: str, args_obj) -> dict:
    print(f"[Orchestrator] Attempting to execute Python script: {script_path}")
    full_script_path = os.path.normpath(os.path.join(target_project_path, script_path))
    if not os.path.exists(full_script_path):
        print(f"[Orchestrator ERRO] Script file not found for execution: {full_script_path}")
        return {"status": "error", "message": f"Script file {script_path} not found at {full_script_path}."}

    read_result = tool_read_file(full_script_path)
    if read_result.get("status") != "success":
        print(f"[Orchestrator ERRO] Could not read script file {full_script_path}: {read_result.get('message')}")
        return {"status": "error", "message": f"Could not read script {script_path}: {read_result.get('message')}"}
    script_content = read_result.get("content", "")

    confirm_message = f"[Segurança ORQUESTRADOR] Executar o script '{script_path}' com o seguinte conteúdo?\n--- SCRIPT CODE ---\n{script_content}\n--- END SCRIPT CODE ---\nPermitir execução? [y/N]: "
    confirm = 'n'
    if args_obj.debug:
        print(confirm_message + " (Auto-confirmado 'y' em modo debug)")
        confirm = 'y'
    else:
        confirm = input(confirm_message).strip().lower()

    if confirm == 'y':
        print(f"[Orchestrator] Executing script content from: {script_path}")
        result = tool_execute_python_code(code=script_content)
        print(f"[Orchestrator] Result of executing {script_path}: {result.get('stdout', result.get('stderr', 'No output'))}")
        return result
    else:
        print(f"[Orchestrator] Execução do script {script_path} negada pelo usuário.")
        return {"status": "skipped", "message": "Execução negada pelo usuário."}

async def _execute_shell_tool_directly(command: str, args_obj) -> dict:
    print(f"[Orchestrator] Attempting to execute shell command: {command}")
    confirm_message = f"[Segurança ORQUESTRADOR] Executar o comando shell: '{command}'? Permitir? [y/N]: "
    confirm = 'n'
    if args_obj.debug:
        print(confirm_message + " (Auto-confirmado 'y' em modo debug)")
        confirm = 'y'
    else:
        confirm = input(confirm_message).strip().lower()

    if confirm == 'y':
        print(f"[Orchestrator] Executing command: {command}")
        result = tool_execute_shell_command(command=command)
        print(f"[Orchestrator] Result of command {command}: {result.get('stdout', result.get('stderr', 'No output'))}")
        return result
    else:
        print(f"[Orchestrator] Execução do comando '{command}' negada pelo usuário.")
        return {"status": "skipped", "message": "Execução negada pelo usuário."}

async def main_async():
    parser = argparse.ArgumentParser(description="CodeSwarm", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-P", "--path", type=str, default=DEFAULT_PROJECT_PATH)
    parser.add_argument("-g", "--goal", type=str, default=DEFAULT_GOAL)
    parser.add_argument("-x", "--pairs", type=int, default=int(DEFAULT_PAIRS))
    parser.add_argument("-r", "--rounds", type=int, default=int(DEFAULT_ROUNDS))
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--model", type=str, default=None)
    args = parser.parse_args()

    target_project_path = os.path.abspath(args.path)
    os.makedirs(target_project_path, exist_ok=True)
    project_logs_path = Path(target_project_path) / "project_logs"
    project_logs_path.mkdir(parents=True, exist_ok=True)
    (project_logs_path / "changelog.log").touch(exist_ok=True)
    (project_logs_path / "tasklist.md").touch(exist_ok=True)
    print(f"[Orchestrator] Logs directory '{project_logs_path}' ensured.")
    project_goal = args.goal
    os.environ["TARGET_PROJECT_PATH_FOR_TOOLS"] = target_project_path
    if not GEMINI_API_KEY: print("Erro: GEMINI_API_KEY not found."); return

    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="codeswarm", user_id="codeswarm_orchestrator")
    print(f"[Sessão] Nova sessão criada: {session.id}")
    MAIN_USER_ID = "codeswarm_orchestrator"
    admin_model, dev_model, revisor_model = (args.model or ADMIN_MODEL_STR, args.model or DEV_MODEL_STR, args.model or REVISOR_MODEL_STR)

    try:
        admin_interpreter_agent = create_admin_llm_agent(model_override=admin_model, instruction_override=load_instruction_from_file("admin_interpret_goal_prompt.json"), tools_override=[])
        admin_formatter_agent = create_admin_llm_agent(model_override=admin_model, instruction_override=load_instruction_from_file("admin_task_assignment_prompt.json"), tools_override=[])
        admin_logger_agent = create_admin_llm_agent(model_override=admin_model, instruction_override=load_instruction_from_file("admin_logger_prompt.json"))
        if args.pairs > 0:
            dev_agent_instances = [create_dev_llm_agent(i+1, model_override=dev_model) for i in range(args.pairs)]
            revisor_agent_instances = [create_revisor_llm_agent(i+1, model_override=revisor_model) for i in range(args.pairs)]
        else:
            dev_agent_instances = []
            revisor_agent_instances = []
            print("[Orchestrator] Advertência: Nenhuma dupla Dev/Revisor foi instanciada.")
    except Exception as e: print(f"Erro durante a inicialização do agente: {e}"); traceback.print_exc(); return

    async def execute_agent_and_get_result(current_agent_instance, agent_input_dict, agent_identifier_for_logging="agent_user"):
        nonlocal session_service, session, args
        agent_name_for_log = getattr(current_agent_instance, 'name', current_agent_instance.__class__.__name__)
        current_runner = get_runner(agent_instance=current_agent_instance, session_service_instance=session_service, app_name="codeswarm")
        input_json_str = json.dumps(agent_input_dict)
        message_for_agent = Content(parts=[Part(text=input_json_str)])
        final_agent_output = None
        if args.debug: print(f"DEBUG: [{agent_identifier_for_logging}] Input: {input_json_str[:500]}...")

        async for event in current_runner.run_async(user_id=MAIN_USER_ID, session_id=session.id, new_message=message_for_agent):
            if args.debug:
                log_parts_evt = [f"DEBUG Event ({agent_name_for_log}): Author='{event.author}'"]
                if event.content and event.content.parts: log_parts_evt.append(f"Parts={event.content.parts}")
                if event.actions: log_parts_evt.append(f"Actions={event.actions}")
                print(", ".join(log_parts_evt))

            if event.is_final_response():
                if args.debug: print(f"DEBUG Final Event ({agent_name_for_log}): Author: {event.author}, Content: {event.content}, Actions: {event.actions}")
                
                if hasattr(event, 'get_function_calls') and event.get_function_calls():
                    calls = event.get_function_calls()
                    if calls: final_agent_output = {"function_call_ADK_parsed": {"name": calls[0].name, "args": dict(calls[0].args) if hasattr(calls[0].args, 'items') else calls[0].args}}; break
                if hasattr(event, 'get_function_responses') and event.get_function_responses():
                    responses = event.get_function_responses()
                    if responses: final_agent_output = {"function_response": {"name": responses[0].name, "response": dict(responses[0].response) if hasattr(responses[0].response, 'items') else responses[0].response}}; break
                
                if event.content and event.content.parts:
                    final_part_text = event.content.parts[-1].text
                    if final_part_text:
                        thought_prefix = ""
                        json_str_to_parse = final_part_text
                        match = re.search(r"(.*?)(```json\s*(\{.*?\})\s*```)", final_part_text, re.DOTALL | re.IGNORECASE)
                        if match:
                            thought_prefix = match.group(1).strip()
                            json_str_to_parse = match.group(3)
                            if args.debug: print(f"DEBUG: Extracted JSON block. Thought: '{thought_prefix}'. JSON: '{json_str_to_parse}'")

                        try:
                            parsed_json = json.loads(json_str_to_parse)
                            if isinstance(parsed_json, dict) and "function_call" in parsed_json:
                                final_agent_output = {"function_call_text_parsed": parsed_json["function_call"]}
                                if thought_prefix: final_agent_output["thought"] = thought_prefix
                            else:
                                final_agent_output = parsed_json
                                if thought_prefix and isinstance(final_agent_output, dict): final_agent_output["thought"] = thought_prefix
                        except json.JSONDecodeError:
                            if args.debug: print(f"DEBUG: No JSON object in final_part_text after regex, using as output_text. Text: {final_part_text}")
                            final_agent_output = {"output_text": final_part_text}
                
                if final_agent_output is None and event.actions and event.actions.state_delta:
                    final_agent_output = {"status": "state_updated", "delta": event.actions.state_delta}
                break

        if final_agent_output is None: return {"status": "error", "message": "No final output from agent."}
        return final_agent_output

    all_dev_outputs_for_round = []
    all_revisor_feedback_for_round = []

    for current_round in range(args.rounds):
        print(f"\n=== ROUND {current_round + 1} ===")
        if isinstance(session.state, dict):
            state_changes_for_interpreter = {"current_project_goal": project_goal, "current_target_path": target_project_path}
            await session_service.append_event(session, Event(author="orchestrator", actions=EventActions(state_delta=state_changes_for_interpreter)))
            session = await session_service.get_session(session_id=session.id, user_id=MAIN_USER_ID, app_name="codeswarm")
        
        print("[Orchestrator] Executing AdminInterpreterAgent...")
        nl_tasks_result = await execute_agent_and_get_result(admin_interpreter_agent, {}, "admin_interpreter")
        natural_language_text = nl_tasks_result.get("output_text", "") if isinstance(nl_tasks_result, dict) else str(nl_tasks_result)
        if args.debug: print(f"[AdminInterpreterAgent Output] '{natural_language_text}'")

        print("[Orchestrator] Executing AdminFormatterAgent to get action list...")
        formatter_input_dict = {"natural_language_tasks": natural_language_text, "target_project_path": target_project_path}
        action_list_result = await execute_agent_and_get_result(admin_formatter_agent, formatter_input_dict, "admin_formatter")

        processed_action_list = []
        if isinstance(action_list_result, list): processed_action_list = action_list_result
        elif isinstance(action_list_result, dict):
            if "tasks" in action_list_result and isinstance(action_list_result["tasks"],list) :
                 processed_action_list = action_list_result["tasks"]
            elif "output_text" in action_list_result:
                try:
                    parsed_text = json.loads(action_list_result["output_text"].strip().lstrip("```json").rstrip("```").strip())
                    if isinstance(parsed_text, list): processed_action_list = parsed_text
                    elif isinstance(parsed_text, dict) and "tasks" in parsed_text and isinstance(parsed_text["tasks"],list):
                        processed_action_list = parsed_text["tasks"]
                except Exception as e_parse: print(f"[Orchestrator ERRO] Parsing AdminFormatter output_text: {e_parse}")
        if not isinstance(processed_action_list, list): print(f"[Orchestrator ERRO] AdminFormatter did not produce a list. Got: {action_list_result}"); processed_action_list = []
        if args.debug: print(f"[Orchestrator] Action List: {processed_action_list}")
        if not processed_action_list: print("[Orchestrator AVISO] No actions produced by AdminFormatterAgent for this round.")

        current_dev_agent = dev_agent_instances[0] if args.pairs == 1 and dev_agent_instances else None
        current_revisor_agent = revisor_agent_instances[0] if args.pairs == 1 and revisor_agent_instances else None

        for task_index, task_data in enumerate(processed_action_list):
            action = task_data.get("action")
            print(f"\n[Orchestrator] Processing Action {task_index + 1}/{len(processed_action_list)}: {action}")

            if action == "create_or_update_file":
                if not current_dev_agent: print("[Orchestrator ERRO] No DevAgent for create_or_update_file."); continue
                file_path_from_admin = task_data.get("file_path", "")
                dev_instructions = task_data.get("instructions_for_dev", "")
                dev_input = {"task_description_from_input": dev_instructions, "file_path_from_input": file_path_from_admin}
                print(f"[Orchestrator] Calling DevAgent for: {file_path_from_admin}")
                dev_agent_response = await execute_agent_and_get_result(current_dev_agent, dev_input, f"DevAgent_Action_{task_index+1}")
                
                actual_tool_result = None
                write_success = False
                dev_agent_final_comment = dev_agent_response.get("output_text", dev_agent_response.get("thought",""))

                if isinstance(dev_agent_response, dict):
                    parsed_tool_call = dev_agent_response.get("function_call_text_parsed")
                    if parsed_tool_call and parsed_tool_call.get("name") == "write_file":
                        tool_args = parsed_tool_call.get("args", {})
                        target_file_path_for_tool = tool_args.get("file_path", file_path_from_admin)
                        content_to_write = tool_args.get("content", "")

                        print(f"[Orchestrator] DevAgent requested write_file for '{target_file_path_for_tool}'. Executing directly.")
                        actual_tool_result = tool_write_file(file_path=target_file_path_for_tool, content=content_to_write)

                        if actual_tool_result.get("status") == "success":
                            write_success = True
                            print(f"[Orchestrator] Successfully executed write_file for {target_file_path_for_tool}")
                        else:
                            print(f"[Orchestrator ERRO] Failed to execute write_file for {target_file_path_for_tool}: {actual_tool_result.get('message')}")
                    elif dev_agent_response.get("status") == "success":
                         write_success = True; actual_tool_result = dev_agent_response
                         dev_agent_final_comment = dev_agent_response.get("message", dev_agent_final_comment)
                    else:
                        print(f"[Orchestrator AVISO] DevAgent did not request 'write_file' or report direct success for task {file_path_from_admin}. Response: {dev_agent_response}")
                        actual_tool_result = dev_agent_response

                all_dev_outputs_for_round.append({"action_task": task_data, "dev_agent_response": dev_agent_response, "actual_tool_result": actual_tool_result or {}, "dev_agent_final_comment": dev_agent_final_comment})

                if current_revisor_agent and write_success:
                    revisor_file_path_relative = file_path_from_admin
                    if isinstance(session.state, dict):
                        revisor_state_delta = {"revisor_target_file_abs_path": os.path.join(target_project_path, revisor_file_path_relative), "revisor_task_description": dev_instructions, "revisor_focus_areas_str": task_data.get("revisor_focus_areas", f"Review content of {revisor_file_path_relative} based on dev instructions.")}
                        await session_service.append_event(session, Event(author="orchestrator", actions=EventActions(state_delta=revisor_state_delta)))
                        session = await session_service.get_session(session_id=session.id, user_id=MAIN_USER_ID, app_name="codeswarm")
                    print(f"[Orchestrator] Calling RevisorAgent for: {revisor_file_path_relative}")
                    revisor_result = await execute_agent_and_get_result(current_revisor_agent, {}, f"Revisor_Action_{task_index+1}")
                    all_revisor_feedback_for_round.append({"action_task": task_data, "revisor_result": revisor_result})
                elif current_revisor_agent:
                    print(f"[Orchestrator] Skipping Revisor for {file_path_from_admin} due to Dev/write_file non-success.")
                    all_revisor_feedback_for_round.append({"action_task": task_data, "revisor_result": {"status": "skipped", "message": "Skipped due to Dev/write_file failure or non-action."}})
            
            elif action == "execute_python_script":
                script_path_relative = task_data.get("script_path")
                if script_path_relative:
                    exec_result = await _execute_python_tool_directly(script_path_relative, target_project_path, args)
                    all_dev_outputs_for_round.append({"action_task": task_data, "execution_result": exec_result, "dev_agent_final_comment": f"Orchestrator executed {script_path_relative}."})
                else:
                    print("[Orchestrator ERRO] 'script_path' missing for execute_python_script action.")
                    all_dev_outputs_for_round.append({"action_task": task_data, "execution_result": {"status": "error", "message": "script_path missing"}, "dev_agent_final_comment": "Error: script_path missing."})
            
            elif action == "execute_shell_command":
                command = task_data.get("command")
                if command:
                    exec_result = await _execute_shell_tool_directly(command, args)
                    all_dev_outputs_for_round.append({"action_task": task_data, "execution_result": exec_result, "dev_agent_final_comment": f"Orchestrator executed shell command: {command}."})
                else:
                    print("[Orchestrator ERRO] 'command' missing for execute_shell_command action.")
                    all_dev_outputs_for_round.append({"action_task": task_data, "execution_result": {"status": "error", "message": "command missing"}, "dev_agent_final_comment": "Error: command missing."})
            else:
                print(f"[Orchestrator AVISO] Unknown action type: {action}")
                all_dev_outputs_for_round.append({"action_task": task_data, "execution_result": {"status": "error", "message": f"Unknown action: {action}"}, "dev_agent_final_comment": f"Error: Unknown action {action}."})

        if isinstance(session.state, dict):
            await session_service.append_event(session, Event(author="orchestrator", actions=EventActions(state_delta={"round": current_round + 1, "target_project_path": target_project_path})))
            session = await session_service.get_session(session_id=session.id, user_id=MAIN_USER_ID, app_name="codeswarm")
        
        admin_logging_input_dict = {"dev_outputs": all_dev_outputs_for_round, "revisor_feedback": all_revisor_feedback_for_round, "target_project_path": target_project_path, "round": current_round + 1}
        print("[Orchestrator] Executing AdminLoggerAgent...")
        admin_log_result = await execute_agent_and_get_result(admin_logger_agent, admin_logging_input_dict, "admin_logger")
        
        # Attempt to execute write_file if AdminLoggerAgent requests it for changelog
        if isinstance(admin_log_result, dict):
            log_parsed_call = admin_log_result.get("function_call_text_parsed")
            if log_parsed_call and log_parsed_call.get("name") == "write_file":
                log_tool_args = log_parsed_call.get("args", {})
                log_file_path = log_tool_args.get("file_path")
                log_content = log_tool_args.get("content")
                # Ensure it's trying to write to a .log file within project_logs for safety
                if log_file_path and log_content and log_file_path.startswith(str(project_logs_path)) and log_file_path.endswith(".log"):
                    print(f"[Orchestrator] AdminLoggerAgent requested write_file for '{log_file_path}'. Executing directly.")
                    log_write_result = tool_write_file(file_path=log_file_path, content=log_content) # Uses absolute path from agent
                    if log_write_result.get("status") != "success":
                        print(f"[AdminAgent ERRO - Logging/Update] Failed to execute write_file for changelog: {log_write_result.get('message')}")
                else:
                    print(f"[AdminAgent ERRO - Logging/Update] AdminLoggerAgent requested write_file to non-log or outside project_logs: {log_file_path}")
            elif not (admin_log_result.get("status") == "success"): # If it wasn't a write_file call, and not a direct success status
                 print(f"[AdminAgent ERRO - Logging/Update] Logging agent did not report success or valid write_file call. Result: {admin_log_result}")

        all_dev_outputs_for_round.clear(); all_revisor_feedback_for_round.clear()
    print("\nTodas as rodadas completas.")

if __name__ == "__main__":
    asyncio.run(main_async())
