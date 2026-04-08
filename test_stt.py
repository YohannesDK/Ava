# test_stt.py
from src.core.config import load_config
from src.voice.stt import WhisperSTT

load_config()

stt = WhisperSTT(model_size="small")

print("Press Enter to start recording, then Enter again to stop...")
input()
print("Recording... press Enter to stop")
text = stt.transcribe_from_mic()
print(f"Result: '{text}'")
