import os
from dotenv import load_dotenv

# Load environment variables from .env in the project root
# prioritize .env in the same directory as this script, then one level up
dotenv_path_script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
dotenv_path_parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')

if os.path.exists(dotenv_path_script_dir):
    load_dotenv(dotenv_path_script_dir)
    print(f"AGNO_CONFIG: Loaded .env from {dotenv_path_script_dir}")
elif os.path.exists(dotenv_path_parent_dir):
    load_dotenv(dotenv_path_parent_dir)
    print(f"AGNO_CONFIG: Loaded .env from {dotenv_path_parent_dir}")
else:
    print("AGNO_CONFIG_WARNING: .env file not found in script directory or parent directory. Using environment variables or defaults.")


# Model and API key configuration
ADMIN_MODEL_STR = os.getenv("ADMIN_MODEL_TYPE", "gemini-2.5-flash")
DEV_MODEL_STR = os.getenv("DEV_MODEL_TYPE", "gemini-2.5-flash")
REVISOR_MODEL_STR = os.getenv("REVISOR_MODEL_TYPE", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model temperature settings
ADMIN_MODEL_TEMPERATURE = float(os.getenv("ADMIN_MODEL_TEMPERATURE", "0.2"))
DEV_MODEL_TEMPERATURE = float(os.getenv("DEV_MODEL_TEMPERATURE", "0.3"))
REVISOR_MODEL_TEMPERATURE = float(os.getenv("REVISOR_MODEL_TEMPERATURE", "0.3"))

# Agno uses GOOGLE_API_KEY for Gemini models
if GEMINI_API_KEY and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
    print(f"AGNO_CONFIG: GOOGLE_API_KEY set from GEMINI_API_KEY.")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("AGNO_CONFIG_ERROR: GOOGLE_API_KEY is not set. Please ensure it's in your .env file or environment variables.")

# Default operational parameters
DEFAULT_PROJECT_PATH = os.getenv("DEFAULT_PROJECT_PATH", "./generated_code")
DEFAULT_GOAL = os.getenv("DEFAULT_GOAL", "Develop a simple Python script.")
DEFAULT_PAIRS = os.getenv("DEFAULT_PAIRS", "1")
DEFAULT_ROUNDS = os.getenv("DEFAULT_ROUNDS", "1")

print(f"AGNO_CONFIG: Admin Model: {ADMIN_MODEL_STR}, Temp: {ADMIN_MODEL_TEMPERATURE}")
print(f"AGNO_CONFIG: Dev Model: {DEV_MODEL_STR}, Temp: {DEV_MODEL_TEMPERATURE}")
print(f"AGNO_CONFIG: Revisor Model: {REVISOR_MODEL_STR}, Temp: {REVISOR_MODEL_TEMPERATURE}")
