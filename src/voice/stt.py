from typing import Optional
import numpy as np


class WhisperSTT:
    def __init__(self, model_size: str = "small"):
        self.model_size = model_size
        self.model = None
    
    def _get_device(self) -> str:
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
        except ImportError:
            pass
        return "cpu"
    
    def _get_compute_type(self) -> str:
        if self._get_device() == "cuda":
            return "float16"
        return "int8"
    
    def init_model(self):
        if self.model is None:
            from faster_whisper import WhisperModel
            device = self._get_device()
            compute_type = self._get_compute_type()
            print(f"Loading Whisper {self.model_size} on {device}...", flush=True)
            self.model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=compute_type
            )
            print("Whisper model loaded.", flush=True)
    
    def transcribe(self, audio_data: np.ndarray) -> str:
        if self.model is None:
            self.init_model()
        
        segments, info = self.model.transcribe(
            audio_data,
            language="en",
            beam_size=5,
            vad_filter=True
        )
        
        text = " ".join([segment.text for segment in segments])
        return text.strip()
    
    def transcribe_from_mic(self, sample_rate: int = 16000) -> Optional[str]:
        import sounddevice as sd
        
        print("Recording... (press Enter to stop)", flush=True)
        
        recording = []
        
        def callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}", flush=True)
            recording.append(indata.copy())
        
        try:
            with sd.InputStream(
                samplerate=sample_rate,
                channels=1,
                dtype='float32',
                callback=callback
            ):
                input()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Error: {e}", flush=True)
            from src.core.logger import log_error
            log_error(e, "STT")
            return None
        
        if not recording:
            return None
        
        audio = np.concatenate(recording, axis=0)
        audio = audio.flatten()
        
        if len(audio) < sample_rate * 0.5:
            print("Audio too short. Try again.", flush=True)
            return None
        
        return self.transcribe(audio)


_stt_instance: Optional[WhisperSTT] = None


def init_whisper(model_size: str = "small") -> WhisperSTT:
    global _stt_instance
    _stt_instance = WhisperSTT(model_size)
    return _stt_instance


def get_whisper() -> WhisperSTT:
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = init_whisper()
    return _stt_instance


def transcribe(audio_data: np.ndarray) -> str:
    return get_whisper().transcribe(audio_data)


def transcribe_from_mic(sample_rate: int = 16000) -> Optional[str]:
    return get_whisper().transcribe_from_mic(sample_rate)
