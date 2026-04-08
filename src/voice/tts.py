from pathlib import Path
from typing import Optional
import threading
import subprocess
import tempfile
import wave
import json
import os
import sys


class PiperTTS:
    def __init__(self, model_path: Path, config_path: Path):
        self.model_path = model_path
        self.config_path = config_path
        self.piper_path = self._find_piper()
        self.sample_rate = self._get_sample_rate()

    def _get_sample_rate(self) -> int:
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config.get('audio', {}).get('sample_rate', 22050)
        except Exception:
            return 22050

    def _find_piper(self) -> str:
        venv_bin = os.path.dirname(sys.executable)
        for name in ["piper", "piper.exe"]:
            path = os.path.join(venv_bin, name)
            if os.path.exists(path):
                return path
        for path in ["/usr/bin/piper", "/usr/local/bin/piper", os.path.expanduser("~/.local/bin/piper")]:
            if os.path.exists(path):
                return path
        return "piper"

    def _raw_to_wav(self, raw_audio: bytes, path: str):
        with wave.open(path, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            wav.writeframes(raw_audio)

    def _get_players(self, wav_path: str) -> list:
        players = []

        # WSL2 / Windows
        try:
            win_path = subprocess.check_output(["wslpath", "-w", wav_path], text=True).strip()
            players.append(["powershell.exe", "-c", f'(New-Object Media.SoundPlayer "{win_path}").PlaySync()'])
        except Exception:
            pass

        # Linux native
        players += [
            ["aplay", wav_path],
            ["paplay", wav_path],
            ["pw-play", wav_path],
            ["ffplay", "-nodisp", "-autoexit", wav_path],
            ["mpv", "--no-video", wav_path],
        ]

        # macOS
        players.append(["afplay", wav_path])

        return players

    def _play_wav(self, wav_path: str):
        for cmd in self._get_players(wav_path):
            try:
                subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                return
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        print("No audio backend found", flush=True)

    def speak(self, text: str, blocking: bool = False):
        if not text:
            return

        def _speak():
            try:
                process = subprocess.Popen(
                    [self.piper_path,
                     "--model", str(self.model_path),
                     "--config", str(self.config_path),
                     "--output-raw",
                     "--length-scale", "1.0"],
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

                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    tmp_path = f.name

                try:
                    self._raw_to_wav(raw_audio, tmp_path)
                    self._play_wav(tmp_path)
                finally:
                    os.unlink(tmp_path)

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
