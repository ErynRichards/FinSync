"""
Application settings.

Every value comes from environment variables, which are loaded from the
.env file in the project root (see .env.example). This keeps passwords and
secret keys OUT of the source code and out of GitHub.
"""
# Load the tools needed in this file.
import os


# Handle  bool requests or data.
def _bool(name, default=False):
    value = os.environ.get(name)
    # Check the condition before continuing.
    if value is None:
        # Send the result back to the code that called this function.
        return default
    # Send the result back to the code that called this function.
    return value.strip().lower() in ("1", "true", "yes", "on")


# Handle  int requests or data.
def _int(name, default):
    value = os.environ.get(name)
    # Send the result back to the code that called this function.
    return int(value) if value not in (None, "") else default


# Define Config for this part of the program.
class Config:
    #Flask
    # Signs the session cookie. Must be long and random in real use.
    SECRET_KEY = os.environ.get("SECRET_KEY", "")

    # Session cookie hardening
    SESSION_COOKIE_HTTPONLY = True          # JavaScript cannot read the cookie
    # Read the session cookie samesite setting.
    SESSION_COOKIE_SAMESITE = "Lax"         # basic cross-site protection
    # Read the session cookie secure setting.
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", False)  # True when using HTTPS

    #MySQL
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    # Read the db port setting.
    DB_PORT = _int("DB_PORT", 3306)
    # Read the db name setting.
    DB_NAME = os.environ.get("DB_NAME", "finsync")
    # Read the db user setting.
    DB_USER = os.environ.get("DB_USER", "finsync_app")
    # Read the db password setting.
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    # Read the db connect timeout setting.
    DB_CONNECT_TIMEOUT = _int("DB_CONNECT_TIMEOUT", 5)

    #  Password reset
    # Public address of the site, used to build the link in the email.
    # Locally: http://127.0.0.1:5000   In production: https://your-domain
    # (We do NOT build the link from the request's Host header, because an
    # attacker could forge that header and make the email point elsewhere.)

    APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
    # Read the reset token expiry minutes setting.
    RESET_TOKEN_EXPIRY_MINUTES = _int("RESET_TOKEN_EXPIRY_MINUTES", 30)
    # Max reset emails per account within the window below (abuse protection)
    RESET_MAX_REQUESTS = _int("RESET_MAX_REQUESTS", 3)
    # Read the reset window minutes setting.
    RESET_WINDOW_MINUTES = _int("RESET_WINDOW_MINUTES", 15)

    #  Email
    # "console" = print the email in the terminal (LOCAL TESTING ONLY)
    # "smtp"    = really send it through the SMTP server below
    MAIL_BACKEND = os.environ.get("MAIL_BACKEND", "console").strip().lower()
    # Read the mail server setting.
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    # Read the mail port setting.
    MAIL_PORT = _int("MAIL_PORT", 587)
    # Read the mail use tls setting.
    MAIL_USE_TLS = _bool("MAIL_USE_TLS", True)    # STARTTLS on port 587
    # Read the mail use ssl setting.
    MAIL_USE_SSL = _bool("MAIL_USE_SSL", False)   # implicit SSL on port 465
    # Read the mail username setting.
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    # Read the mail password setting.
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    # Read the mail sender setting.
    MAIL_SENDER = os.environ.get("MAIL_SENDER", "") or MAIL_USERNAME
    # Read the mail timeout setting.
    MAIL_TIMEOUT = _int("MAIL_TIMEOUT", 10)
