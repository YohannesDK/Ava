import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "conversations.db"

class Storage:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._init_db()
    
    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                title TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        conn.commit()
        conn.close()
    
    def create_conversation(self, title: Optional[str] = None) -> int:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (created_at, title) VALUES (?, ?)",
            (datetime.now().isoformat(), title or "New Conversation")
        )
        conversation_id = cursor.lastrowid
        if conversation_id is None:
            raise Exception("Failed to create conversation")
        conn.commit()
        conn.close()
        return conversation_id
    
    def add_message(self, conversation_id: int, role: str, content: str):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (conversation_id, role, content, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    
    def get_conversation(self, conversation_id: int) -> list[dict]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at",
            (conversation_id,)
        )
        messages = [{"role": r, "content": c} for r, c in cursor.fetchall()]
        conn.close()
        return messages
    
    def list_conversations(self) -> list[dict]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute(
            "SELECT id, title, created_at FROM conversations ORDER BY created_at DESC"
        )
        conversations = [{"id": i, "title": t, "created_at": c} for i, t, c in cursor.fetchall()]
        conn.close()
        return conversations
