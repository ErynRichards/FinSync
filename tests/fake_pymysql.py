"""
TEST-ONLY stand-in for PyMySQL, backed by SQLite.

Why: the automated tests must run on machines without a MySQL server
(e.g. GitHub, or the environment this project was built in). This fake
lets the REAL application code (app/db.py, users.py, reset_tokens.py,
routes) run unchanged. It is NOT used when you run the app normally.

It does not prove the MySQL scripts themselves are correct - run those
on a real MySQL server (README step 4) and use `flask --app run check-db`.
"""
# Load the tools needed in this file.
import sqlite3
# Load the tools needed in this file.
import types
# Use functions and classes from another file.
from datetime import datetime

sqlite3.register_adapter(datetime, lambda d: d.isoformat(sep=" "))
sqlite3.register_converter("DATETIME", lambda b: datetime.fromisoformat(b.decode()))

# Read the schema setting.
SCHEMA = """
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    phone TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE password_reset_tokens (
    token_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    created_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL
);
"""


# Define MySQLError for this part of the program.
class MySQLError(Exception):
    pass


# Define IntegrityError for this part of the program.
class IntegrityError(MySQLError):
    pass


# Define OperationalError for this part of the program.
class OperationalError(MySQLError):
    pass


# Define _Cursor for this part of the program.
class _Cursor:
    # Set up a new object.
    def __init__(self, conn):
        self._cur = conn.cursor()
        self.lastrowid = None
        self._rows = []

    # Run the requested database operation.
    def execute(self, sql, params=()):
        sql = sql.replace("%s", "?")
        # Try the operation and handle any errors.
        try:
            # Run the database query using these values.
            self._cur.execute(sql, tuple(params))
        except sqlite3.IntegrityError as exc:
            code = 1062 if "UNIQUE" in str(exc) else 1452
            # Stop the operation and report an error.
            raise IntegrityError(code, str(exc)) from exc
        except sqlite3.Error as exc:
            # Stop the operation and report an error.
            raise OperationalError(2000, str(exc)) from exc
        self.lastrowid = self._cur.lastrowid
        # Like PyMySQL: buffer SELECT results and return the row count
        self._rows = [dict(r) for r in self._cur.fetchall()] if self._cur.description else []
        # Send the result back to the code that called this function.
        return self._cur.rowcount if self._cur.rowcount >= 0 else len(self._rows)

    # Handle fetchone requests or data.
    def fetchone(self):
        # Send the result back to the code that called this function.
        return self._rows.pop(0) if self._rows else None

    # Handle fetchall requests or data.
    def fetchall(self):
        rows, self._rows = self._rows, []
        # Send the result back to the code that called this function.
        return rows

    # Handle close requests or data.
    def close(self):
        # Close this resource when finished.
        self._cur.close()


# Define _Connection for this part of the program.
class _Connection:
    # Set up a new object.
    def __init__(self, path):
        self._conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        self._conn.row_factory = sqlite3.Row
        # Run the database query using these values.
        self._conn.execute("PRAGMA foreign_keys = ON")

    # Handle cursor requests or data.
    def cursor(self):
        # Send the result back to the code that called this function.
        return _Cursor(self._conn)

    # Handle commit requests or data.
    def commit(self):
        # Save the changes to the database.
        self._conn.commit()

    # Handle rollback requests or data.
    def rollback(self):
        # Cancel database changes if something goes wrong.
        self._conn.rollback()

    # Handle close requests or data.
    def close(self):
        # Close this resource when finished.
        self._conn.close()


# set by the test fixture
STATE = {"path": None, "down": False, "connect_calls": []}


# Handle connect requests or data.
def connect(**kwargs):
    # Add this item to the list of results.
    STATE["connect_calls"].append(kwargs)
    # Check the condition before continuing.
    if STATE["down"]:
        # Stop the operation and report an error.
        raise OperationalError(2003, "Can't connect to MySQL server on 'localhost' (10061)")
    # Send the result back to the code that called this function.
    return _Connection(STATE["path"])


# Handle create schema requests or data.
def create_schema(path):
    # Get ready to run database queries.
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    # Close this resource when finished.
    conn.close()


# Handle install requests or data.
def install(sys_modules):
    """Register this fake as 'pymysql' (+ submodules) before the app is imported."""
    mod = types.ModuleType("pymysql")
    mod.connect = connect
    mod.MySQLError = MySQLError
    mod.err = types.SimpleNamespace(IntegrityError=IntegrityError, OperationalError=OperationalError)
    # Get ready to run database queries.
    cursors = types.ModuleType("pymysql.cursors")
    cursors.DictCursor = object
    constants = types.ModuleType("pymysql.constants")
    constants.CLIENT = types.SimpleNamespace(FOUND_ROWS=2)
    mod.cursors = cursors
    mod.constants = constants
    sys_modules["pymysql"] = mod
    sys_modules["pymysql.cursors"] = cursors
    sys_modules["pymysql.constants"] = constants
