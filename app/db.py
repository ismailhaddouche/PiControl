from sqlmodel import SQLModel, create_engine
import os

# Use an absolute path for the sqlite DB stored under /var/lib/picontrol so data
# is persisted outside the repository working tree and can be managed with
# appropriate permissions.
DB_DIR = os.environ.get("PICONTROL_DB_DIR", "/var/lib/picontrol")
DB_PATH = os.path.join(DB_DIR, "pi_control.db")
sqlite_url = f"sqlite:///{DB_PATH}"
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})


def init_db():
    # Import models here to ensure they are registered on metadata
    import app.models  # noqa: F401
    # Ensure the target directory exists before creating the DB file
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    except Exception:
        pass
    SQLModel.metadata.create_all(engine)
    # Debug: list created tables (helpful for tests)
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


# Create the database and tables when importing this module for test/execution environments
try:
    init_db()
except Exception:
    # if something fails here, let explicit initialization handle it
    pass
