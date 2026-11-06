import os
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, declarative_base

try:
    from app.core.config import settings
except ImportError:
    from .core.config import settings

# Normalize Heroku/Supabase postgres:// to postgresql://
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Configure connection arguments & pooling based on driver type
if db_url.startswith("sqlite"):
    if "sqlite:///./" in db_url:
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_filename = db_url.split("sqlite:///./")[-1]
        resolved_db_path = os.path.join(backend_dir, db_filename)
        db_url = f"sqlite:///{resolved_db_path.replace(os.sep, '/')}"

    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
    
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # PostgreSQL / MySQL Production Engine with Connection Pooling
    engine = create_engine(
        db_url,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Health-check helper to verify database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
