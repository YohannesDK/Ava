from pathlib import Path
from typing import Optional
import threading
import subprocess
import os


class PiperTTS:
    def __init__(self, model_path: Path, config_path: Path):
        self.model_path = model_path
        self.config_path = config_path
        self.piper_path = self._find_piper()
        self.sample_rate = self._get_sample_rate()
    
    def _get_sample_rate(self) -> int:
        try:
            import json
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config.get('audio', {}).get('sample_rate', 22050)
        except Exception:
            return 22050
    
    def _find_piper(self) -> Optional[str]:
        import sys
        venv_piper = os.path.join(os.path.dirname(sys.executable), "piper")
        if os.path.exists(venv_piper):
            return venv_piper
        
        import sys
        venv_bin = os.path.dirname(sys.executable)
        for name in ["piper", "piper.exe"]:
            path = os.path.join(venv_bin, name)
            if os.path.exists(path):
                return path
        
        common_paths = [
            "/usr/bin/piper",
            "/usr/local/bin/piper",
            os.path.expanduser("~/.local/bin/piper"),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return "piper"
    
    def speak(self, text: str, blocking: bool = False):
        if not text:
            return
        
        def _speak():
            try:
                import pygame
                import numpy as np
                
                pygame.mixer.init(frequency=self.sample_rate)
                
                piper_cmd = self._find_piper()
                print(f"Using piper: {piper_cmd}", flush=True)
                
                process = subprocess.Popen(
                    [piper_cmd, 
                     "--model", str(self.model_path), 
                     "--config", str(self.config_path),
                     "--output-raw"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                raw_audio, stderr = process.communicate(input=text.encode("utf-8"))
                
                if stderr:
                    print(f"Piper stderr: {stderr.decode('utf-8', errors='replace')}", flush=True)
                
                if not raw_audio:
                    print("TTS Error: No audio data returned", flush=True)
                    return
                
                audio = np.frombuffer(raw_audio, dtype=np.int16)
                
                if audio.ndim == 1:
                    audio = np.column_stack((audio, audio))
                
                print(f"Playing audio: {len(audio)} samples at {self.sample_rate}Hz", flush=True)
                
                sound = pygame.sndarray.make_sound(audio)
                pygame.mixer.Sound.play(sound)
                while pygame.mixer.get_busy():
                    pygame.time.wait(100)
                print("Audio playback complete", flush=True)
                
            except Exception as e:
                print(f"TTS Error: {e}", flush=True)
                from src.core.logger import log_error
                log_error(e, "TTS")
        
        if blocking:
            _speak()
        else:
            thread = threading.Thread(target=_speak, daemon=True)
            thread.start()
    
    def speak_and_wait(self, text: str):
        self.speak(text, blocking=True)


import io


_tts_instance: Optional[PiperTTS] = None


def init_piper(voice_name: str = "en_GB-aru-medium") -> PiperTTS:
    from src.core.config import get_voice_path
    
    global _tts_instance
    
    model_path, config_path = get_voice_path(voice_name)
    
    if not model_path.exists():
        raise FileNotFoundError(f"Voice model not found: {model_path}")
    if not config_path.exists():
        raise FileNotFoundError(f"Voice config not found: {config_path}")
    
    _tts_instance = PiperTTS(model_path, config_path)
    return _tts_instance


def get_tts() -> PiperTTS:
    global _tts_instance
    if _tts_instance is None:
        from src.core.config import get_default_voice
        _tts_instance = init_piper(get_default_voice())
    return _tts_instance


def speak(text: str, blocking: bool = False):
    get_tts().speak(text, blocking)


def speak_and_wait(text: str):
    get_tts().speak_and_wait(text)
