"""
ScamGraph AI - Database Session and Initialization
Handles SQLAlchemy engine, session maker, WAL pragmas, and schema setup.
"""

from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.models.investigation import Base

# Ensure data directory exists
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///"):
    raw_path = db_url.replace("sqlite:///", "")
    Path(raw_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
)

# Enable WAL mode and foreign key enforcement for SQLite
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency to provide a transactional database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
