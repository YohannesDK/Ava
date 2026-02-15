import json
from typing import Optional, Any
from .config import get_ollama_url, get_default_model

class OllamaClient:
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, system_prompt: Optional[str] = None):
        self.base_url = base_url or get_ollama_url()
        self.model = model or get_default_model()
        self.system_prompt = system_prompt or ""
    
    def generate(self, prompt: str, context: Optional[list[dict]] = None) -> str:
        import requests
        
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": prompt})
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={"model": self.model, "messages": messages, "stream": False},
            timeout=120
        )
        response.raise_for_status()
        
        return response.json()["message"]["content"]
    
    def chat(self, messages: list[dict]) -> str:
        import requests
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={"model": self.model, "messages": messages, "stream": False},
            timeout=120
        )
        response.raise_for_status()
        
        return response.json()["message"]["content"]
