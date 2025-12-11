"""SQLite Database Layer for Máquina Orquestadora GL Strategic v2.3

Provides persistence for conversations, users, and system metrics.
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import logging
import json

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for Orquestadora"""
    
    def __init__(self, db_path: str = "orquestadora.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_db()
        logger.info(f"Database initialized at {db_path}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    model TEXT,
                    tokens_used INTEGER,
                    latency_ms FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id)
                )
            """)
            
            # Metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value FLOAT NOT NULL,
                    model TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indices for better query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name)")
            
            conn.commit()
            logger.info("Database tables initialized")
    
    # User operations
    def create_user(self, user_id: str, name: str) -> Dict[str, Any]:
        """Create a new user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (user_id, name) VALUES (?, ?)",
                (user_id, name)
            )
            return {"user_id": user_id, "name": name, "created_at": datetime.now().isoformat()}
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # Conversation operations
    def create_conversation(self, conversation_id: str, user_id: str, title: str) -> Dict[str, Any]:
        """Create a new conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (conversation_id, user_id, title) VALUES (?, ?, ?)",
                (conversation_id, user_id, title)
            )
            return {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "title": title,
                "created_at": datetime.now().isoformat()
            }
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversations WHERE conversation_id = ?", (conversation_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # Message operations
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        model: Optional[str] = None,
        tokens_used: Optional[int] = None,
        latency_ms: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Add message to conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO messages 
                (conversation_id, role, content, model, tokens_used, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (conversation_id, role, content, model, tokens_used, latency_ms)
            )
            return {
                "conversation_id": conversation_id,
                "role": role,
                "created_at": datetime.now().isoformat()
            }
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get message history for a conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT role, content FROM messages 
                WHERE conversation_id = ? 
                ORDER BY created_at ASC""",
                (conversation_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # Metrics operations
    def record_metric(self, metric_name: str, metric_value: float, model: Optional[str] = None) -> None:
        """Record a performance metric"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO metrics (metric_name, metric_value, model) VALUES (?, ?, ?)",
                (metric_name, metric_value, model)
            )
    
    def get_metrics(self, metric_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM metrics 
                WHERE metric_name = ? 
                ORDER BY created_at DESC 
                LIMIT ?""",
                (metric_name, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_metric_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT 
                AVG(metric_value) as avg,
                MIN(metric_value) as min,
                MAX(metric_value) as max,
                COUNT(*) as count
                FROM metrics 
                WHERE metric_name = ?""",
                (metric_name,)
            )
            row = cursor.fetchone()
            return dict(row) if row else {}


# Global database instance
_db: Optional[Database] = None


def get_db(db_path: str = "orquestadora.db") -> Database:
    """Get or create global database instance"""
    global _db
    if _db is None:
        _db = Database(db_path)
    return _db
