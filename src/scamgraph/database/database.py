"""
ScamGraph AI - Database Module
SQLite database setup and connection management using Python's built-in sqlite3.
"""

import sqlite3
from collections.abc import Generator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path

from scamgraph.config import config, get_logger

logger = get_logger(__name__)


class Database:
    """SQLite database wrapper with connection pooling and schema management."""

    def __init__(self, db_path: str | None = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file. Uses config default if not provided.
        """
        self.db_path = Path(db_path or config.database.full_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a new database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for database connections.

        Yields:
            Database connection that auto-commits on success, rolls back on error.
        """
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
        """Initialize database schema with all required tables."""
        schema = """
        -- Users table for authentication (future)
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Investigations table for scam cases
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

        -- Evidence table for collected artifacts
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

        -- Entities table for graph nodes (emails, phones, domains, etc.)
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

        -- Relationships table for graph edges
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

        -- Agent runs table for tracking AI agent activity (future)
        CREATE TABLE IF NOT EXISTS agent_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            investigation_id INTEGER NOT NULL,
            agent_name TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            input_data TEXT,
            output_data TEXT,
            error_message TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (investigation_id) REFERENCES investigations(id) ON DELETE CASCADE
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
        CREATE INDEX IF NOT EXISTS idx_agent_runs_investigation ON agent_runs(investigation_id);
        """

        with self.get_connection() as conn:
            conn.executescript(schema)
        logger.info("Database schema initialized at %s", self.db_path)

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a write query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Cursor with lastrowid and rowcount
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor

    def fetch_one(self, query: str, params: tuple = ()) -> sqlite3.Row | None:
        """
        Fetch a single row.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Row or None
        """
        with self.get_connection() as conn:
            return conn.execute(query, params).fetchone()

    def fetch_all(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        """
        Fetch all rows.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of rows
        """
        with self.get_connection() as conn:
            return conn.execute(query, params).fetchall()

    def list_investigations(self) -> list[sqlite3.Row]:
        """Return investigations in most-recently-created order."""
        return self.fetch_all(
            "SELECT id, title FROM investigations ORDER BY created_at DESC, id DESC"
        )

    def import_evidence(
        self,
        records: Sequence[Mapping[str, str | None]],
        *,
        investigation_id: int | None = None,
        new_investigation_title: str | None = None,
    ) -> tuple[int, int]:
        """Store an evidence batch, optionally creating its investigation atomically."""
        if not records:
            raise ValueError("At least one evidence record is required.")
        if investigation_id is None:
            if not new_investigation_title or not new_investigation_title.strip():
                raise ValueError(
                    "Choose an existing investigation or provide a new investigation title."
                )
            new_investigation_title = new_investigation_title.strip()
        elif new_investigation_title is not None:
            raise ValueError(
                "Choose an existing investigation or provide a new investigation title."
            )

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
            elif conn.execute(
                "SELECT 1 FROM investigations WHERE id = ?", (investigation_id,)
            ).fetchone() is None:
                raise ValueError(f"Investigation {investigation_id} does not exist.")

            conn.executemany(
                """
                INSERT INTO evidence (investigation_id, type, source, content)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        investigation_id,
                        record["type"],
                        record.get("source"),
                        record["content"],
                    )
                    for record in records
                ],
            )

        return investigation_id, len(records)


# Global database instance
db = Database()


def get_db() -> Database:
    """Get the global database instance."""
    return db