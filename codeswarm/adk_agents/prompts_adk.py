import json
import os

# Determine the absolute path to the 'prompts' directory
# Assuming prompts_adk.py is in codeswarm/adk_agents/
# and prompts/ is in codeswarm/prompts/
PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'prompts')

def _load_json_prompt_as_string(filename: str) -> str:
    """Loads a JSON file and returns its content as a JSON string."""
    path = os.path.join(PROMPTS_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            prompt_data = json.load(f)
        return json.dumps(prompt_data)  # Serialize the Python dict to a JSON string
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found: {path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from {path}: {e}")

def get_admin_instruction_string() -> str:
    return _load_json_prompt_as_string("admin_prompt.json")

def get_dev_instruction_string(dev_id: int) -> str:
    base_json_string = _load_json_prompt_as_string("dev_prompt.json")
    # If your dev_prompt.json uses a placeholder like "#ID#", replace it.
    # For this, you'd load, modify the dict, then dumps:
    # path = os.path.join(PROMPTS_DIR, "dev_prompt.json")
    # with open(path, 'r', encoding='utf-8') as f:
    #     prompt_data = json.load(f)
    # if "agentProfile" in prompt_data and "name" in prompt_data["agentProfile"]:
    #      prompt_data["agentProfile"]["name"] = prompt_data["agentProfile"]["name"].replace("#ID#", str(dev_id))
    # return json.dumps(prompt_data)
    # For simplicity, if dev_prompt.json doesn't need dynamic ID in the JSON structure itself,
    # but the LLM should be aware of its ID, ensure the input to the agent includes the ID.
    # The example dev_prompt.json below doesn't use #ID#.
    return base_json_string # Or modified string if placeholders are used

def get_revisor_instruction_string(revisor_id: int) -> str:
    base_json_string = _load_json_prompt_as_string("revisor_prompt.json")
    # Similar placeholder replacement logic if needed for revisor_id
    return base_json_string

# You would then create dev_prompt.json and revisor_prompt.json
# in codeswarm/prompts/ with similar JSON structures.
