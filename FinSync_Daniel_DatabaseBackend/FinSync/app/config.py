"""
Application settings.

Every value comes from environment variables, which are loaded from the
.env file in the project root (see .env.example). This keeps passwords and
secret keys OUT of the source code and out of GitHub.
"""
import os


def _bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _int(name, default):
    value = os.environ.get(name)
    return int(value) if value not in (None, "") else default


class Config:
    # --- Flask ---------------------------------------------------------
    # Signs the session cookie. Must be long and random in real use.
    SECRET_KEY = os.environ.get("SECRET_KEY", "")

    # Session cookie hardening
    SESSION_COOKIE_HTTPONLY = True          # JavaScript cannot read the cookie
    SESSION_COOKIE_SAMESITE = "Lax"         # basic cross-site protection
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", False)  # True when using HTTPS

    # --- MySQL ---------------------------------------------------------
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = _int("DB_PORT", 3306)
    DB_NAME = os.environ.get("DB_NAME", "finsync")
    DB_USER = os.environ.get("DB_USER", "finsync_app")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_CONNECT_TIMEOUT = _int("DB_CONNECT_TIMEOUT", 5)

    # --- Password reset ------------------------------------------------
    # Public address of the site, used to build the link in the email.
    # Locally: http://127.0.0.1:5000   In production: https://your-domain
    # (We do NOT build the link from the request's Host header, because an
    # attacker could forge that header and make the email point elsewhere.)
    APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
    RESET_TOKEN_EXPIRY_MINUTES = _int("RESET_TOKEN_EXPIRY_MINUTES", 30)
    # Max reset emails per account within the window below (abuse protection)
    RESET_MAX_REQUESTS = _int("RESET_MAX_REQUESTS", 3)
    RESET_WINDOW_MINUTES = _int("RESET_WINDOW_MINUTES", 15)

    # --- Email ---------------------------------------------------------
    # "console" = print the email in the terminal (LOCAL TESTING ONLY)
    # "smtp"    = really send it through the SMTP server below
    MAIL_BACKEND = os.environ.get("MAIL_BACKEND", "console").strip().lower()
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = _int("MAIL_PORT", 587)
    MAIL_USE_TLS = _bool("MAIL_USE_TLS", True)    # STARTTLS on port 587
    MAIL_USE_SSL = _bool("MAIL_USE_SSL", False)   # implicit SSL on port 465
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_SENDER = os.environ.get("MAIL_SENDER", "") or MAIL_USERNAME
    MAIL_TIMEOUT = _int("MAIL_TIMEOUT", 10)
