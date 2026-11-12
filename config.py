# config.py
# Reads the settings from the .env file so passwords are not written in the code.

# Load the tools needed in this file.
import os

# Use functions and classes from another file.
from dotenv import load_dotenv

load_dotenv()  # loads the values from .env into the environment

# Flask
SECRET_KEY = os.getenv("SECRET_KEY")

# MySQL
DB_HOST = os.getenv("DB_HOST", "localhost")

# Read the db port setting.
DB_PORT = int(os.getenv("DB_PORT", "3306"))

# Read the db name setting.
DB_NAME = os.getenv("DB_NAME", "finsync")

# Read the db user setting.
DB_USER = os.getenv("DB_USER", "finsync_app")

# Read the db password setting.
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Password reset: how long a reset link stays valid
RESET_TOKEN_EXPIRY_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRY_MINUTES", "30"))

# Email
# "console" prints the email in the terminal (for testing)
# "smtp" really sends it using the settings below
MAIL_BACKEND = os.getenv("MAIL_BACKEND", "console")

# Read the mail server setting.
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")

# Read the mail port setting.
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))

# Read the mail username setting.
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")

# Read the mail password setting.
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
