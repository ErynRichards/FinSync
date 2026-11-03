# check_db.py
# Checks that the app can connect to MySQL and that both tables exist.
# Run it with:  python check_db.py

from db import DatabaseError, fetch_one

try:
    users = fetch_one("SELECT COUNT(*) AS total FROM users")
    print("OK: connected. The users table has", users["total"], "row(s).")

    tokens = fetch_one("SELECT COUNT(*) AS total FROM password_reset_tokens")
    print("OK: the password_reset_tokens table has", tokens["total"], "row(s).")
except DatabaseError:
    print("FAILED: read the MySQL error above and check the Troubleshooting section in the README.")
