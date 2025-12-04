import os
from dotenv import load_dotenv

# Load environment variables from .env in the project root
# prioritize .env in the same directory as this script, then one level up
dotenv_path_script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
dotenv_path_parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')

if os.path.exists(dotenv_path_script_dir):
    load_dotenv(dotenv_path_script_dir)
elif os.path.exists(dotenv_path_parent_dir):
    load_dotenv(dotenv_path_parent_dir)


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

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Default operational parameters
DEFAULT_PROJECT_PATH = os.getenv("DEFAULT_PROJECT_PATH", "./generated_code")
DEFAULT_GOAL = os.getenv("DEFAULT_GOAL", "Develop a simple Python script.")
DEFAULT_PAIRS = os.getenv("DEFAULT_PAIRS", "1")
DEFAULT_ROUNDS = os.getenv("DEFAULT_ROUNDS", "1")

