# Voice Models for Piper TTS

This directory contains Piper TTS voice model files. Due to their large size, only the `.json` config files are tracked in git. You need to download the `.onnx` model files manually.

## Downloading Voice Models

### Option 1: Download from HuggingFace

The easiest way is to use curl or wget:

```bash
cd voices

# Download model (.onnx) and config (.json) files
curl -L -o en_GB-cori-high.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high/en_GB-cori-high.onnx"
curl -L -o en_GB-cori-high.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high/en_GB-cori-high.onnx.json"
```

### Option 2: Using Python

```python
from huggingface_hub import hf_hub_download

model_path = hf_hub_download(repo_id="rhasspy/piper-voices", filename="en/en_GB/cori/high/en_GB-cori-high.onnx")
config_path = hf_hub_download(repo_id="rhasspy/piper-voices", filename="en/en_GB/cori/high/en_GB-cori-high.onnx.json")
```

## Available Voices

### Recommended Voices

| Voice ID | Description | Quality | Approx Size |
|----------|-------------|---------|-------------|
| `en_GB-cori-high` | British female (high quality) | High | 114 MB |
| `en_GB-southern_english_female` | British female | Medium | 45 MB |
| `en_GB-aru-medium` | British female (default) | Medium | 76 MB |

### Jarvis Voice (Iron Man)

To get the JARVIS voice from Iron Man:

```bash
cd voices
curl -L -o jarvis-medium.onnx "https://huggingface.co/jgkawell/jarvis/resolve/main/en/en_GB/jarvis/medium/jarvis-medium.onnx"
curl -L -o jarvis-medium.onnx.json "https://huggingface.co/jgkawell/jarvis/resolve/main/en/en_GB/jarvis/medium/jarvis-medium.onnx.json"
```

Note: The JARVIS voice is ~2GB and requires training your own model for the best results.

## Finding More Voices

Browse available voices at:
- https://huggingface.co/rhasspy/piper-voices
- https://github.com/rhasspy/piper/blob/master/VOICES.md

## Configuration

Edit `config/voices.yaml` to change the default voice:

```yaml
default: en_GB-cori-high

voices:
  en_GB-cori-high:
    description: "British female voice - high quality"
```

## Current Voices in This Project

Currently configured voices (model files must be downloaded):
- `en_GB-cori-high` - British female (high quality) - **recommended**
- `en_GB-aru-medium` - British female (medium quality)
- `jarvis-medium` - Jarvis voice from Iron Man (downloaded)

## Personality to Voice Mapping

Each personality in `config/personality.yaml` can have its own voice:

```yaml
personalities:
  british:
    name: Ava
    voice: en_GB-cori-high
    system_prompt: |
      ...

  jarvis:
    name: Jarvis
    voice: jarvis-medium
    system_prompt: |
      ...
```

The voice is automatically loaded when you select a personality.
