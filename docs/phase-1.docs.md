# Phase 1: Core Text Assistant

## Overview

Phase 1 establishes the foundation: a CLI-based text assistant with local LLM integration and conversation persistence.

## Components

### 1. CLI Entry Point (`src/cli.py`)

**Location**: `src/cli.py`

**Responsibilities**:
- Main application loop
- User input handling
- Coordinates between storage and LLM client

**Key Functions**:
- `main()` - Entry point, initializes storage/llm, runs REPL loop
- Handles commands: `exit`, `new`
- Loads conversation context before each LLM call

**Flow**:
```
Start → Create conversation → Input loop → Add message → Get context → 
LLM generate → Save response → Print → Repeat
```

---

### 2. Configuration (`src/core/config.py`)

**Location**: `src/core/config.py`

**Responsibilities**:
- Load environment variables from `.env`
- Provide config values for Ollama connection

**Functions**:
- `load_config()` - Loads .env file
- `get_ollama_url()` - Returns Ollama base URL (default: `http://localhost:11434`)
- `get_default_model()` - Returns model name (default: `llama3`)

**Environment Variables**:
| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama API endpoint |
| `OLLAMA_MODEL` | llama3 | Model to use |

---

### 3. LLM Client (`src/core/llm.py`)

**Location**: `src/core/llm.py`

**Responsibilities**:
- Communicate with local Ollama instance
- Handle request/response formatting

**Class**: `OllamaClient`

**Methods**:
- `__init__(base_url, model)` - Initialize with custom URL/model
- `generate(prompt, context)` - Generate response with conversation history
- `chat(messages)` - Direct chat with message list

**API**: Uses Ollama's `/api/chat` endpoint

**Request Format**:
```json
{
  "model": "llama3",
  "messages": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
  ]
}
```

---

### 4. Storage (`src/core/storage.py`)

**Location**: `src/core/storage.py`

**Responsibilities**:
- SQLite database management
- Persist conversations and messages

**Database Schema**:

```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    title TEXT
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

**Class**: `Storage`

**Methods**:
- `create_conversation(title)` - Create new conversation, returns ID
- `add_message(conversation_id, role, content)` - Save a message
- `get_conversation(conversation_id)` - Get all messages for a conversation
- `list_conversations()` - List all conversations

**Storage Location**: `data/conversations.db`

---

### 5. Configuration File (`.env`)

**Location**: `.env`

Contains environment variables for Ollama connection.

---

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                        CLI                               │
│  ┌─────────────┐    ┌─────────────┐    ┌────────────┐  │
│  │   Input     │───▶│   Storage   │───▶│   LLM      │  │
│  │  (user)     │    │  (context)  │    │  (Ollama)  │  │
│  └─────────────┘    └─────────────┘    └────────────┘  │
│         │                                    │           │
│         │           ┌─────────────┐          │           │
│         └──────────▶│   Storage   │◀─────────┘           │
│                     │  (save msg) │                      │
│                     └─────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

## Usage

```bash
# Run the assistant
python -m src.cli

# Commands
# - Type your message and press Enter
# - Type "new" for new conversation
# - Type "exit" to quit
```

## Dependencies

- `requests` - HTTP client for Ollama
- `python-dotenv` - .env file loading
- `sqlite3` - Built-in, no install needed
