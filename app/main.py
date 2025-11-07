import warnings

# Suppress deprecation warning related to the 'crypt' module that some environments
# emit through passlib (dev only). This avoids noise in tests.
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib.utils")

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
import os
from fastapi.responses import RedirectResponse
import logging
from logging.handlers import TimedRotatingFileHandler

from app.config import config
from app.db import init_db
from app.routers import employees, checkins, web
from app.routers import rfid as rfid_router
from app import rfid as rfid_service

app = FastAPI(
    title=f"{config.APP_NAME} - API",
    version=config.APP_VERSION,
    description=config.APP_DESCRIPTION
)

# Session middleware - CRITICAL: SECRET_KEY must be set in production
app.add_middleware(
    SessionMiddleware,
    secret_key=config.get_secret_key(),
    session_cookie=config.SESSION_COOKIE_NAME,
    max_age=config.SESSION_MAX_AGE,
    same_site=config.SESSION_SAME_SITE,
    https_only=config.SESSION_HTTPS_ONLY
)


def setup_admin_logging():
	"""Configure a rotating logger for administrative actions.

	Attempts to write to configured log path. If not possible, falls back to a
	local file within the project.
	"""
	log_path = config.ADMIN_LOG_PATH
	try:
		log_dir = os.path.dirname(log_path)
		if log_dir:
			os.makedirs(log_dir, exist_ok=True)
	except Exception:
		# fallback to a path within the project
		log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "admin_actions.log"))
		try:
			os.makedirs(os.path.dirname(log_path), exist_ok=True)
		except Exception:
			pass

	logger = logging.getLogger("picontrol.admin")
	if not logger.handlers:
		logger.setLevel(logging.INFO)
		try:
			handler = TimedRotatingFileHandler(log_path, when="midnight", backupCount=14, encoding="utf-8")
			formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
			handler.setFormatter(formatter)
			logger.addHandler(handler)
		except Exception:
			# último recurso: no vomitar error en arranque
			pass


# Ensure required directories exist
config.ensure_directories()

# Print configuration if in debug mode
if config.DEBUG:
	config.print_config()


# configure audit logging before tables are created
setup_admin_logging()

app.include_router(employees.router)
app.include_router(checkins.router)
app.include_router(web.router)
app.include_router(rfid_router.router)

# Mount static folder (optional)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
	app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Create tables when importing the module (useful for tests and for simulated phase 1)
init_db()


@app.get("/")
def root_redirect():
	"""Redirect root to admin panel for a more direct experience."""
	return RedirectResponse(url="/admin")


@app.on_event("startup")
def _start_rfid_service():
	# Start hardware RFID listener if configured via environment
	try:
		rfid_service.start_service_if_configured()
	except Exception:
		logger = logging.getLogger("picontrol.rfid")
		logger.exception("Failed to start RFID service on startup")


@app.on_event("shutdown")
def _stop_rfid_service():
	try:
		rfid_service.stop_service()
	except Exception:
		pass


