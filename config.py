# config.py
# Reads the settings from the .env file so passwords are not written in the code.

import os

from dotenv import load_dotenv

load_dotenv()  # loads the values from .env into the environment

# Flask
SECRET_KEY = os.getenv("SECRET_KEY")

# MySQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "finsync")
DB_USER = os.getenv("DB_USER", "finsync_app")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Password reset: how long a reset link stays valid
RESET_TOKEN_EXPIRY_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRY_MINUTES", "30"))

# Email
# "console" prints the email in the terminal (for testing)
# "smtp" really sends it using the settings below
MAIL_BACKEND = os.getenv("MAIL_BACKEND", "console")
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
