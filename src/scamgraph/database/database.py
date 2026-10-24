"""
ScamGraph AI - Database Module
==============================
SQLite database setup, schema management, and forensic data persistence.
Stores investigations, evidence, entities, relationships, processed email IDs,
and live email investigation records.
"""

import json
import sqlite3
from collections.abc import Generator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from scamgraph.config import config, get_logger

logger = get_logger(__name__)


class Database:
    """SQLite database wrapper with connection pooling, schema management, and email storage."""

    def __init__(self, db_path: str | None = None):
        self.db_path = Path(db_path or config.database.full_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        schema = """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Investigations table
        CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'open',
            risk_score REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );

        -- Evidence table
        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            investigation_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            source TEXT,
            content TEXT NOT NULL,
            metadata TEXT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (investigation_id) REFERENCES investigations(id) ON DELETE CASCADE
        );

        -- Entities table (graph nodes)
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            investigation_id INTEGER NOT NULL,
            entity_type TEXT NOT NULL,
            value TEXT NOT NULL,
            risk_score REAL DEFAULT 0.0,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (investigation_id) REFERENCES investigations(id) ON DELETE CASCADE,
            UNIQUE(investigation_id, entity_type, value)
        );

        -- Relationships table (graph edges)
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            investigation_id INTEGER NOT NULL,
            source_entity_id INTEGER NOT NULL,
            target_entity_id INTEGER NOT NULL,
            relationship_type TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (investigation_id) REFERENCES investigations(id) ON DELETE CASCADE,
            FOREIGN KEY (source_entity_id) REFERENCES entities(id) ON DELETE CASCADE,
            FOREIGN KEY (target_entity_id) REFERENCES entities(id) ON DELETE CASCADE
        );

        -- Processed emails tracking table (prevents duplicate alerts across restarts)
        CREATE TABLE IF NOT EXISTS processed_emails (
            message_id TEXT PRIMARY KEY,
            folder TEXT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Email investigations table for authentic forensic records
        CREATE TABLE IF NOT EXISTS email_investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE NOT NULL,
            folder TEXT NOT NULL,
            subject TEXT,
            sender TEXT,
            sender_email TEXT,
            sender_domain TEXT,
            received_at TEXT,
            snippet TEXT,
            content TEXT,
            is_spam BOOLEAN DEFAULT 0,
            spam_score REAL DEFAULT 0.0,
            confidence REAL DEFAULT 0.0,
            evidence_json TEXT,
            extracted_urls TEXT,
            extracted_domains TEXT,
            extracted_phones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_investigations_user ON investigations(user_id);
        CREATE INDEX IF NOT EXISTS idx_investigations_status ON investigations(status);
        CREATE INDEX IF NOT EXISTS idx_evidence_investigation ON evidence(investigation_id);
        CREATE INDEX IF NOT EXISTS idx_entities_investigation ON entities(investigation_id);
        CREATE INDEX IF NOT EXISTS idx_entities_type_value ON entities(entity_type, value);
        CREATE INDEX IF NOT EXISTS idx_relationships_investigation ON relationships(investigation_id);
        CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_entity_id);
        CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_entity_id);
        CREATE INDEX IF NOT EXISTS idx_email_sender_email ON email_investigations(sender_email);
        CREATE INDEX IF NOT EXISTS idx_email_sender_domain ON email_investigations(sender_domain);
        CREATE INDEX IF NOT EXISTS idx_email_is_spam ON email_investigations(is_spam);
        CREATE INDEX IF NOT EXISTS idx_email_message_id ON email_investigations(message_id);
        """

        with self.get_connection() as conn:
            conn.executescript(schema)
        logger.info("Database schema initialized at %s", self.db_path)

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        with self.get_connection() as conn:
            return conn.execute(query, params)

    def fetch_one(self, query: str, params: tuple = ()) -> sqlite3.Row | None:
        with self.get_connection() as conn:
            return conn.execute(query, params).fetchone()

    def fetch_all(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        with self.get_connection() as conn:
            return conn.execute(query, params).fetchall()

    def list_investigations(self) -> list[sqlite3.Row]:
        return self.fetch_all(
            "SELECT id, title FROM investigations ORDER BY created_at DESC, id DESC"
        )

    # =========================================================================
    # EMAIL DEDUPLICATION & TRACKING
    # =========================================================================
    def is_message_processed(self, message_id: str) -> bool:
        """Checks if a message ID has already been recorded."""
        row = self.fetch_one("SELECT 1 FROM processed_emails WHERE message_id = ?", (message_id,))
        return row is not None

    def mark_message_processed(self, message_id: str, folder: str = "INBOX") -> None:
        """Records a message ID as processed."""
        self.execute(
            "INSERT OR IGNORE INTO processed_emails (message_id, folder) VALUES (?, ?)",
            (message_id, folder)
        )

    def mark_messages_processed_batch(self, items: list[tuple[str, str]]) -> None:
        """Records multiple message IDs in a single high-speed database transaction."""
        if not items:
            return
        with self.get_connection() as conn:
            conn.executemany(
                "INSERT OR IGNORE INTO processed_emails (message_id, folder) VALUES (?, ?)",
                items
            )

    # =========================================================================
    # EMAIL INVESTIGATION FORENSICS
    # =========================================================================
    def save_email_investigation(self, data: dict[str, Any]) -> int:
        """Saves an incoming email investigation record with extracted indicators."""
        query = """
        INSERT OR REPLACE INTO email_investigations (
            message_id, folder, subject, sender, sender_email, sender_domain,
            received_at, snippet, content, is_spam, spam_score, confidence,
            evidence_json, extracted_urls, extracted_domains, extracted_phones
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data.get("message_id", ""),
            data.get("folder", "INBOX"),
            data.get("subject", "No Subject"),
            data.get("sender", "Unknown"),
            data.get("sender_email", ""),
            data.get("sender_domain", ""),
            data.get("received_at", ""),
            data.get("snippet", ""),
            data.get("content", ""),
            1 if data.get("is_spam", False) else 0,
            float(data.get("spam_score", 0.0)),
            float(data.get("confidence", 0.0)),
            json.dumps(data.get("evidence", [])),
            json.dumps(data.get("extracted_urls", [])),
            json.dumps(data.get("extracted_domains", [])),
            json.dumps(data.get("extracted_phones", []))
        )
        cursor = self.execute(query, params)
        email_id = cursor.lastrowid

        # Also register processed message
        self.mark_message_processed(data.get("message_id", ""), data.get("folder", "INBOX"))
        return email_id

    def get_email_investigation(self, email_id: int) -> sqlite3.Row | None:
        """Fetches full forensic email record by database ID."""
        return self.fetch_one("SELECT * FROM email_investigations WHERE id = ?", (email_id,))

    def get_email_by_message_id(self, message_id: str) -> sqlite3.Row | None:
        """Fetches email record by unique Gmail Message ID."""
        return self.fetch_one("SELECT * FROM email_investigations WHERE message_id = ?", (message_id,))

    def list_email_investigations(self, limit: int = 100, spam_only: bool | None = None) -> list[sqlite3.Row]:
        """Lists email investigation records ordered by creation."""
        if spam_only is True:
            return self.fetch_all("SELECT * FROM email_investigations WHERE is_spam = 1 ORDER BY id DESC LIMIT ?", (limit,))
        elif spam_only is False:
            return self.fetch_all("SELECT * FROM email_investigations WHERE is_spam = 0 ORDER BY id DESC LIMIT ?", (limit,))
        return self.fetch_all("SELECT * FROM email_investigations ORDER BY id DESC LIMIT ?", (limit,))

    def get_correlated_emails(self, email_id: int) -> list[sqlite3.Row]:
        """
        Finds real cross-email correlations based on strictly shared indicators:
        - Same exact sender_email
        - Same exact sender_domain
        Never fabricates relationships.
        """
        current = self.get_email_investigation(email_id)
        if not current:
            return []

        sender_email = current["sender_email"]
        sender_domain = current["sender_domain"]

        query = """
        SELECT * FROM email_investigations
        WHERE id != ?
          AND (
              (sender_email = ? AND sender_email != '' AND sender_email != 'unknown@domain.com')
              OR
              (sender_domain = ? AND sender_domain != '' AND sender_domain != 'unknown.com' AND sender_domain NOT IN ('gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com'))
          )
        ORDER BY id DESC LIMIT 20
        """
        return self.fetch_all(query, (email_id, sender_email, sender_domain))

    def import_evidence(
        self,
        records: Sequence[Mapping[str, str | None]],
        *,
        investigation_id: int | None = None,
        new_investigation_title: str | None = None,
    ) -> tuple[int, int]:
        if not records:
            raise ValueError("At least one evidence record is required.")
        if investigation_id is None:
            if not new_investigation_title or not new_investigation_title.strip():
                raise ValueError("Choose an existing investigation or provide a new investigation title.")
            new_investigation_title = new_investigation_title.strip()
        elif new_investigation_title is not None:
            raise ValueError("Choose an existing investigation or provide a new investigation title.")

        with self.get_connection() as conn:
            if investigation_id is None:
                cursor = conn.execute(
                    "INSERT INTO investigations (title) VALUES (?)",
                    (new_investigation_title,),
                )
                created_id = cursor.lastrowid
                if created_id is None:
                    raise RuntimeError("SQLite did not return the new investigation ID.")
                investigation_id = created_id
            elif conn.execute("SELECT 1 FROM investigations WHERE id = ?", (investigation_id,)).fetchone() is None:
                raise ValueError(f"Investigation {investigation_id} does not exist.")

            conn.executemany(
                "INSERT INTO evidence (investigation_id, type, source, content) VALUES (?, ?, ?, ?)",
                [(investigation_id, r["type"], r.get("source"), r["content"]) for r in records],
            )

        return investigation_id, len(records)


# Global database instance
db = Database()


def get_db() -> Database:
    return db
