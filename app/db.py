from sqlmodel import SQLModel, create_engine
import os

# Database stored outside repository for security and permissions management
DB_DIR = os.environ.get("PICONTROL_DB_DIR", "/var/lib/picontrol")
DB_PATH = os.path.join(DB_DIR, "pi_control.db")
sqlite_url = f"sqlite:///{DB_PATH}"
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})


def init_db():
    """Initialize database schema and create all tables."""
    import app.models  # noqa: F401
    
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    except Exception:
        pass
    
    SQLModel.metadata.create_all(engine)
    
    try:
        with engine.connect() as conn:
            res = conn.exec("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in res.fetchall()]
            print("[init_db] tables in DB:", tables)
    except Exception:
        pass


def get_engine():
    return engine


def get_session():
    from sqlmodel import Session
    with Session(engine) as session:
        yield session


try:
    init_db()
except Exception:
    pass  # Allow explicit initialization to handle errors
