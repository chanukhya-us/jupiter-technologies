from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
UPLOAD_DIR = BASE_DIR / "uploads"
BACKUP_DIR = BASE_DIR / "backups"
STATIC_DIR = BASE_DIR / "app" / "static"
ASSET_MANIFEST_PATH = STATIC_DIR / "images" / "manifest.json"


def _bool_env(var_name: str, default: bool) -> bool:
    raw = os.environ.get(var_name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{INSTANCE_DIR / 'app.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_EXTENSIONS = {".pdf", ".doc", ".docx"}
    UPLOAD_FOLDER = str(UPLOAD_DIR)
    ASSET_MANIFEST_PATH = str(ASSET_MANIFEST_PATH)
    SHOW_PARTNER_LOGOS = True
    DASHBOARD_PARTNER_LOGO_LIMIT = 12
    CLIENTS_PARTNER_LOGO_LIMIT = 31

    MAIL_ENABLED = _bool_env("MAIL_ENABLED", False)
    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_USE_TLS = _bool_env("SMTP_USE_TLS", True)
    MAIL_FROM = os.environ.get("MAIL_FROM", "noreply@recruittrack.local")

    MARKETER_DEFAULT_TIMEZONE = os.environ.get("MARKETER_DEFAULT_TIMEZONE", "America/New_York")
    MARKETER_DEFAULT_CUTOFF_LOCAL = os.environ.get("MARKETER_DEFAULT_CUTOFF_LOCAL", "18:00")
    MARKETER_DEFAULT_REMINDER_TIMES = os.environ.get(
        "MARKETER_DEFAULT_REMINDER_TIMES",
        "16:00,17:30",
    )
    MARKETER_DEFAULT_ESCALATION_AFTER_MISSES = int(
        os.environ.get("MARKETER_DEFAULT_ESCALATION_AFTER_MISSES", "3")
    )


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class DevelopmentConfig(Config):
    DEBUG = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "default": Config,
}
