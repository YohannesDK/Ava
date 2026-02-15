import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

def load_config():
    load_dotenv(ENV_FILE)

def get_ollama_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def get_default_model() -> str:
    return os.getenv("OLLAMA_MODEL", "llama3")
