from typing import Optional
import numpy as np
import os
import sys


class WhisperSTT:
    def __init__(self, model_size: str = "small"):
        self.model_size = model_size
        self.model = None
        self.is_wsl = self._detect_wsl()

    def _detect_wsl(self) -> bool:
        try:
            with open("/proc/version") as f:
                return "microsoft" in f.read().lower()
        except Exception:
            return False

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
        if self.is_wsl:
            return self._transcribe_from_mic_wsl(sample_rate)
        else:
            return self._transcribe_from_mic_native(sample_rate)

    def _transcribe_from_mic_wsl(self, sample_rate: int = 16000) -> Optional[str]:
        import tempfile
        import subprocess
        import wave
        import scipy.signal

        # Save to Windows temp dir instead of WSL tmp
        win_tmp = subprocess.check_output(
            ["powershell.exe", "-c", "$env:TEMP"],
            text=True
        ).strip()
        win_wav_path = win_tmp + "\\ava_recording.wav"

        # Convert back to Linux path for reading
        linux_wav_path = subprocess.check_output(
            ["wslpath", "-u", win_wav_path], text=True
        ).strip()

        try:
            print("Recording... (press Enter to stop)", flush=True)

            ps_script = (
                "Add-Type -TypeDefinition @'\n"
                "using System;\n"
                "using System.Runtime.InteropServices;\n"
                "public class WaveRecorder {\n"
                "    [DllImport(\"winmm.dll\")]\n"
                "    public static extern int mciSendString(string cmd, System.Text.StringBuilder ret, int size, IntPtr handle);\n"
                "}\n"
                "'@\n"
                "[WaveRecorder]::mciSendString(\"open new Type waveaudio Alias recsound\", $null, 0, [IntPtr]::Zero)\n"
                "[WaveRecorder]::mciSendString(\"set recsound time format ms\", $null, 0, [IntPtr]::Zero)\n"
                "[WaveRecorder]::mciSendString(\"set recsound bitspersample 16\", $null, 0, [IntPtr]::Zero)\n"
                "[WaveRecorder]::mciSendString(\"set recsound samplespersec 48000\", $null, 0, [IntPtr]::Zero)\n"
                "[WaveRecorder]::mciSendString(\"set recsound channels 4\", $null, 0, [IntPtr]::Zero)\n"
                "[WaveRecorder]::mciSendString(\"set recsound alignment 8\", $null, 0, [IntPtr]::Zero)\n"
                "[WaveRecorder]::mciSendString(\"set recsound bytespersec 384000\", $null, 0, [IntPtr]::Zero)\n"
                "[WaveRecorder]::mciSendString(\"record recsound\", $null, 0, [IntPtr]::Zero)\n"
                "Read-Host\n"
                "[WaveRecorder]::mciSendString(\"stop recsound\", $null, 0, [IntPtr]::Zero)\n"
                "Start-Sleep -Milliseconds 500\n"
                f"[WaveRecorder]::mciSendString('save recsound \"{win_wav_path}\"', $null, 0, [IntPtr]::Zero)\n"
                "Start-Sleep -Milliseconds 200\n"
                "[WaveRecorder]::mciSendString(\"close recsound\", $null, 0, [IntPtr]::Zero)\n"
                "Start-Sleep -Milliseconds 200\n"
            )

            process = subprocess.Popen(
                ["powershell.exe", "-c", ps_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            input()
            stdout, stderr = process.communicate(input=b"\n")
            process.wait()

            print(f"PowerShell stdout: {stdout.decode('utf-8', errors='replace')}", flush=True)
            print(f"PowerShell stderr: {stderr.decode('utf-8', errors='replace')}", flush=True)
            print(f"File exists: {os.path.exists(linux_wav_path)}", flush=True)
            print(f"File size: {os.path.getsize(linux_wav_path) if os.path.exists(linux_wav_path) else 'N/A'}", flush=True)

            if not os.path.exists(linux_wav_path) or os.path.getsize(linux_wav_path) == 0:
                print("No audio captured.", flush=True)
                return None

            with wave.open(linux_wav_path, 'rb') as wav:
                actual_rate = wav.getframerate()
                actual_channels = wav.getnchannels()
                frames = wav.readframes(wav.getnframes())
                print(f"Channels: {actual_channels}, Sample rate: {actual_rate}, Frames: {wav.getnframes()}", flush=True)

            audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

            if actual_channels > 1:
                audio = audio.reshape(-1, actual_channels).mean(axis=1)

            if actual_rate != sample_rate:
                audio = scipy.signal.resample(audio, int(len(audio) * sample_rate / actual_rate))

            if len(audio) < sample_rate * 0.5:
                print("Audio too short.", flush=True)
                return None

            return self.transcribe(audio)

        except Exception as e:
            print(f"Error: {e}", flush=True)
            from src.core.logger import log_error
            log_error(e, "STT")
            return None
        finally:
            if os.path.exists(linux_wav_path):
                os.unlink(linux_wav_path)


    def _transcribe_from_mic_native(self, sample_rate: int = 48000) -> Optional[str]:
        import sounddevice as sd

        print("Recording... (press Enter to stop)", flush=True)
        recording = []

        def callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}", flush=True)
            recording.append(indata.copy())

        try:
            with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32', callback=callback):
                input()
        except Exception as e:
            print(f"Error: {e}", flush=True)
            from src.core.logger import log_error
            log_error(e, "STT")
            return None

        if not recording:
            return None

        audio = np.concatenate(recording, axis=0).flatten()

        if len(audio) < sample_rate * 0.5:
            print("Audio too short.", flush=True)
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
