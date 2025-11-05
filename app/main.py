import warnings

# Suprimir warning deprecación relacionado con el módulo 'crypt' que algunos entornos
# emiten a través de passlib (solo en desarrollo). Esto evita ruido en tests.
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib.utils")

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
import os
from fastapi.responses import RedirectResponse

from app.db import init_db
from app.routers import empleados, fichajes, web

app = FastAPI(title="PiControl - API")

# Suprimir warning deprecación relacionado con el módulo 'crypt' que algunos entornos
# emiten a través de passlib (solo en desarrollo). Esto evita ruido en tests.
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib.utils")

# Session middleware simple (dev) para la interfaz web
secret = os.environ.get("SECRET_KEY", "devsecret")
app.add_middleware(SessionMiddleware, secret_key=secret)

app.include_router(empleados.router)
app.include_router(fichajes.router)
app.include_router(web.router)

# Montar carpeta static (opcional)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
	app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Crear las tablas al importar el módulo (útil para tests y para la fase 1 simulada)
init_db()


@app.get("/")
def root_redirect():
	"""Redirige la raíz al panel de administración para una experiencia más directa."""
	return RedirectResponse(url="/admin")


