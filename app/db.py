from sqlmodel import SQLModel, create_engine

sqlite_url = "sqlite:///./pi_control.db"
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})


def init_db():
    # Import models here to ensure they are registered on metadata
    import app.models  # noqa: F401
    SQLModel.metadata.create_all(engine)
    # Debug: listar tablas creadas (ayuda en tests)
    try:
        with engine.connect() as conn:
            res = conn.exec("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in res.fetchall()]
            print("[init_db] tablas en la BD:", tables)
    except Exception:
        pass


def get_engine():
    return engine


# Crear la base de datos y tablas al importar este módulo para entornos de test/ejecución
try:
    init_db()
except Exception:
    # si algo falla aquí, lo dejamos para que la inicialización explícita lo maneje
    pass
