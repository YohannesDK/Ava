# Usage
This document details requirements and usage instructions for Ava.


As of 02/15/2026, the planned development consists of 4 phases.

- [x] - Phase 1: Core Text Assistant
- [ ] - Phase 2: Voice Input
- [ ] - Phase 3: Voice Output
- [ ] - Phase 4: Multi-modal


## Installation & Usage (per phase)

### Phase 1

```bash
# 1. Install Ollama (if not installed)
# https://ollama.ai

# 2. Pull a model
ollama pull llama3

# 3. Start Ollama server (in a separate terminal)
ollama serve

# 4. Run Ava
python3 src/cli.py
```

### Commands
- `new` - Start a new conversation
- `exit` - Quit Ava

### Configuration
Edit `.env` to change:
- `OLLAMA_BASE_URL` - Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL` - Model to use (default: llama3)
