"""
Configuration management for PiControl application.

All configuration is loaded from environment variables for security and flexibility.
"""

import os
from typing import Optional
from pathlib import Path


class Config:
    """Application configuration loaded from environment variables."""

    # Application metadata
    APP_NAME: str = "PiControl"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "RFID-based employee time tracking system"

    # Security - SECRET_KEY
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
    
    @classmethod
    def get_secret_key(cls) -> str:
        """Get SECRET_KEY with validation and warnings."""
        if not cls.SECRET_KEY:
            import warnings
            warnings.warn(
                "SECRET_KEY not set! Using insecure default. "
                "Set SECRET_KEY environment variable in production.",
                RuntimeWarning,
                stacklevel=2
            )
            return "dev-insecure-change-me-in-production"
        return cls.SECRET_KEY

    # Session configuration
    SESSION_COOKIE_NAME: str = "picontrol_session"
    SESSION_MAX_AGE: int = int(os.environ.get("SESSION_LIFETIME", "3600"))  # 1 hour default
    SESSION_SAME_SITE: str = "lax"
    SESSION_HTTPS_ONLY: bool = os.environ.get("SESSION_HTTPS_ONLY", "0") == "1"

    # Database configuration
    DB_DIR: str = os.environ.get("PICONTROL_DB_DIR", "/var/lib/picontrol")
    
    @classmethod
    def get_db_path(cls) -> str:
        """Get full database file path."""
        return os.path.join(cls.DB_DIR, "pi_control.db")
    
    @classmethod
    def get_db_url(cls) -> str:
        """Get SQLite database URL."""
        return f"sqlite:///{cls.get_db_path()}"

    # Server configuration
    HOST: str = os.environ.get("PICONTROL_HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PICONTROL_PORT", "8000"))
    WORKERS: int = int(os.environ.get("PICONTROL_WORKERS", "1"))

    # Logging configuration
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    ADMIN_LOG_PATH: str = os.environ.get(
        "PICONTROL_ADMIN_LOG",
        "/var/log/picontrol/admin_actions.log"
    )
    APP_LOG_PATH: str = os.environ.get(
        "PICONTROL_APP_LOG",
        "/var/log/picontrol/app.log"
    )

    # RFID configuration
    RFID_ENABLED: bool = os.environ.get("PICONTROL_RFID_ENABLED", "0") == "1"
    RFID_MODE: str = os.environ.get("PICONTROL_RFID_MODE", "evdev")  # evdev or rc522
    RFID_DEVICE: Optional[str] = os.environ.get("PICONTROL_RFID_DEVICE")
    RFID_PENDING_FILE: str = os.environ.get(
        "PICONTROL_RFID_PENDING_FILE",
        "/var/lib/picontrol/rfid_assign_pending.json"
    )
    RC522_ENABLED: bool = os.environ.get("PICONTROL_ENABLE_RC522", "0") == "1"

    # Backup configuration
    BACKUP_DIR: str = os.environ.get("PICONTROL_BACKUP_DIR", "/var/backups/picontrol")
    BACKUP_RETENTION_DAYS: int = int(os.environ.get("PICONTROL_BACKUP_RETENTION_DAYS", "30"))

    # Data retention configuration
    DATA_RETENTION_YEARS: int = int(os.environ.get("PICONTROL_DATA_RETENTION_YEARS", "4"))

    # Admin reset configuration
    ALLOW_PERSISTENT_RESET: bool = os.environ.get("PICONTROL_ALLOW_PERSISTENT_RESET", "0") == "1"

    # Development/Debug configuration
    DEBUG: bool = os.environ.get("DEBUG", "0") == "1"
    RELOAD: bool = os.environ.get("RELOAD", "0") == "1"

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist."""
        directories = [
            cls.DB_DIR,
            cls.BACKUP_DIR,
            os.path.dirname(cls.ADMIN_LOG_PATH),
            os.path.dirname(cls.APP_LOG_PATH),
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError):
                # Log warning but don't fail - may be running in restricted environment
                pass

    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate configuration and return list of warnings/errors.
        
        Returns:
            List of validation messages (warnings/errors)
        """
        messages = []
        
        # Critical: SECRET_KEY
        if not cls.SECRET_KEY or cls.SECRET_KEY == "dev-insecure-change-me-in-production":
            messages.append("CRITICAL: SECRET_KEY not set or using default value")
        
        # Database directory
        if not os.path.exists(cls.DB_DIR):
            messages.append(f"WARNING: Database directory does not exist: {cls.DB_DIR}")
        elif not os.access(cls.DB_DIR, os.W_OK):
            messages.append(f"WARNING: Database directory not writable: {cls.DB_DIR}")
        
        # RFID configuration
        if cls.RFID_ENABLED:
            if cls.RFID_MODE not in ("evdev", "rc522"):
                messages.append(f"WARNING: Invalid RFID_MODE: {cls.RFID_MODE}")
            if cls.RFID_MODE == "evdev" and not cls.RFID_DEVICE:
                messages.append("WARNING: RFID enabled but RFID_DEVICE not set")
        
        return messages

    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (for debugging)."""
        print("=" * 60)
        print(f"{cls.APP_NAME} v{cls.APP_VERSION} - Configuration")
        print("=" * 60)
        print(f"Database: {cls.get_db_path()}")
        print(f"Server: {cls.HOST}:{cls.PORT}")
        print(f"Session timeout: {cls.SESSION_MAX_AGE}s")
        print(f"RFID enabled: {cls.RFID_ENABLED}")
        print(f"Debug mode: {cls.DEBUG}")
        print("=" * 60)
        
        # Validation
        messages = cls.validate()
        if messages:
            print("\n⚠️  Configuration Warnings:")
            for msg in messages:
                print(f"  - {msg}")
            print()


# Singleton instance
config = Config()
