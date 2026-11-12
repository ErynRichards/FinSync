
# check_db.py
# Checks that the app can connect to MySQL and that all the tables exist.
# Run it with:  python check_db.py

# Use functions and classes from another file.
from db import DatabaseError, fetch_one

tables = ["users", "password_reset_tokens", "accounts", "categories", "transactions"]

# Try the operation and handle any errors.
try:
    # Go through each item one at a time.
    for table in tables:
        result = fetch_one("SELECT COUNT(*) AS total FROM " + table)
        print("OK:", table, "table has", result["total"], "row(s).")
except DatabaseError:
    print("FAILED: read the MySQL error above and check the Troubleshooting section in the README.")
