# Ava - Personal Assistant

## Overview
A multi-modal personal assistant starting with text/voice input, powered by local LLMs.

## Tech Stack
- **Language**: Python
- **LLM**: Ollama (local)
- **Voice**: Whisper (STT), TTS (TBD)
- **Storage**: SQLite

## File Structure
```
Ava/
├── src/
│   ├── core/      # LLM, config, storage
│   ├── voice/     # STT/TTS
│   └── cli.py
├── tests/
├── .env
└── PROJECTS.md
```

## Phases

### Phase 1: Core Text Assistant
- [x] Project setup (virtual env, requirements.txt)
- [x] Ollama integration client
- [x] CLI interface for text input
- [x] Conversation history (SQLite)
- [x] Basic config management (.env)

### Phase 2: Voice Input
- [ ] Audio capture (microphone)
- [ ] Whisper integration (STT)
- [ ] Voice command pipeline

### Phase 3: Voice Output
- [ ] TTS integration
- [ ] Response audio playback

### Phase 4: Multi-modal
- [ ] Image input support (vision models)
- [ ] Screen context awareness


