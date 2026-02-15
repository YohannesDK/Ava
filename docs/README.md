# Ava - Personal Assistant

Ava is a multi-modal personal assistant that starts with text/voice input, powered by local LLMs.

## How It Works

### Core Flow

```
User Input → CLI → LLM Client → Ollama (local LLM) → Response → CLI → User
                    ↓
              Storage (SQLite)
```

1. **User Input**: User types message via CLI
2. **Context Retrieval**: Previous messages are loaded from SQLite
3. **LLM Processing**: Message + context sent to local Ollama instance
4. **Storage**: Both user message and AI response are saved
5. **Output**: Response displayed to user

### Conversations

- Each CLI session creates a new conversation in the database
- Messages are stored with role (user/assistant) and timestamp
- Ava has memory within a conversation (session)
- Type `new` to start a fresh conversation

### Storage

- SQLite database at `data/conversations.db`
- Two tables: `conversations` and `messages`
- Persists across sessions

## Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Core Text Assistant | Complete |
| 2 | Voice Input (STT) | Planned |
| 3 | Voice Output (TTS) | Planned |
| 4 | Multi-modal (vision) | Planned |

See individual phase docs for detailed component information.
