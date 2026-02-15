import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
PERSONALITY_FILE = PROJECT_ROOT.parent / "config" / "personality.yaml"

def load_config():
    load_dotenv(ENV_FILE)

def get_ollama_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def get_default_model() -> str:
    return os.getenv("OLLAMA_MODEL", "llama3")

def _load_personality_config():
    with open(PERSONALITY_FILE, "r") as f:
        return yaml.safe_load(f)

def get_available_personalities() -> list[str]:
    config = _load_personality_config()
    return list(config.get("personalities", {}).keys())

def get_default_personality() -> str:
    config = _load_personality_config()
    return config.get("default", "jarvis")

def get_personality_system_prompt(personality: str) -> str:
    config = _load_personality_config()
    personalities = config.get("personalities", {})
    if personality in personalities:
        return personalities[personality].get("system_prompt", "")
    return ""
