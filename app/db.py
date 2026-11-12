"""
MySQL connection handling.

How it works

* get_db() opens ONE connection per web request and stores it on Flask's
  `g` object, so every function in the same request shares it.
* close_db() runs automatically at the end of every request and closes it.
* transaction() wraps several statements so they either ALL succeed
  (commit) or ALL are undone (rollback) - used by the password reset.

Every query in this project uses %s placeholders, e.g.
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
PyMySQL escapes the values itself, which prevents SQL injection.
NEVER build SQL with f-strings or + using user input.
"""
# Load the tools needed in this file.
import logging
# Use functions and classes from another file.
from contextlib import contextmanager

# Load the tools needed in this file.
import pymysql
# Load the tools needed in this file.
import pymysql.cursors
# Use functions and classes from another file.
from pymysql.constants import CLIENT
# Use functions and classes from another file.
from flask import current_app, g

log = logging.getLogger(__name__)


# Define DatabaseError for this part of the program.
class DatabaseError(Exception):
    """Raised for database problems. The message is safe to show users."""


# Define DuplicateEmailError for this part of the program.
class DuplicateEmailError(DatabaseError):
    """Raised when inserting a user whose email already exists."""


# Handle  connect requests or data.
def _connect():
    cfg = current_app.config
    # Send the result back to the code that called this function.
    return pymysql.connect(
        host=cfg["DB_HOST"],
        port=cfg["DB_PORT"],
        user=cfg["DB_USER"],
        password=cfg["DB_PASSWORD"],
        database=cfg["DB_NAME"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,   # rows come back as dicts
        connect_timeout=cfg["DB_CONNECT_TIMEOUT"],
        autocommit=False,
        # Report rows MATCHED (not only rows changed) for UPDATE, so updating
        # a value to the same value still counts as success.
        client_flag=CLIENT.FOUND_ROWS,
    )


# Handle get db requests or data.
def get_db():
    """Return this request's database connection (opening it if needed)."""
    # Check the condition before continuing.
    if "db" not in g:
        # Try the operation and handle any errors.
        try:
            g.db = _connect()
        except pymysql.MySQLError as exc:
            # Full detail goes to the server log only - never to the browser.
            log.error("Could not connect to MySQL: %s", exc)
            # Stop the operation and report an error.
            raise DatabaseError("The database is unavailable. Please try again later.") from exc
    # Send the result back to the code that called this function.
    return g.db


# Handle close db requests or data.
def close_db(_exc=None):
    db = g.pop("db", None)
    # Check the condition before continuing.
    if db is not None:
        # Try the operation and handle any errors.
        try:
            # Close this resource when finished.
            db.close()
        except Exception:  # already closed / connection lost
            pass


# Handle transaction requests or data.
@contextmanager
def transaction():
    """
    Usage:
        with transaction() as cur:
            cur.execute(...)
            cur.execute(...)
    Commits if the block finishes, rolls back if anything raises.
    """
    # Get ready to run database queries.
    conn = get_db()
    cur = conn.cursor()
    # Try the operation and handle any errors.
    try:
        yield cur
        # Save the changes to the database.
        conn.commit()
    except pymysql.err.IntegrityError as exc:
        # Cancel database changes if something goes wrong.
        conn.rollback()
        # MySQL error 1062 = duplicate entry for a UNIQUE key
        if exc.args and exc.args[0] == 1062:
            # Stop the operation and report an error.
            raise DuplicateEmailError("An account with that email address already exists.") from exc
        log.error("Integrity error: %s", exc)
        # Stop the operation and report an error.
        raise DatabaseError("The request could not be saved.") from exc
    except pymysql.MySQLError as exc:
        # Cancel database changes if something goes wrong.
        conn.rollback()
        log.error("Database error: %s", exc)
        # Stop the operation and report an error.
        raise DatabaseError("A database error occurred. Please try again later.") from exc
    except Exception:
        # Cancel database changes if something goes wrong.
        conn.rollback()
        # Stop the operation and report an error.
        raise
    finally:
        # Close this resource when finished.
        cur.close()


# Handle query one requests or data.
def query_one(sql, params=()):
    """Run a SELECT and return the first row as a dict, or None."""
    # Use this resource and close it when finished.
    with transaction() as cur:
        # Run the database query using these values.
        cur.execute(sql, params)
        # Send the result back to the code that called this function.
        return cur.fetchone()


# Handle query all requests or data.
def query_all(sql, params=()):
    """Run a SELECT and return all rows as a list of dicts."""
    # Use this resource and close it when finished.
    with transaction() as cur:
        # Run the database query using these values.
        cur.execute(sql, params)
        # Send the result back to the code that called this function.
        return list(cur.fetchall())


# Run the requested database operation.
def execute(sql, params=()):
    """Run INSERT/UPDATE/DELETE. Returns (rows_affected, last_insert_id)."""
    # Use this resource and close it when finished.
    with transaction() as cur:
        affected = cur.execute(sql, params)
        # Send the result back to the code that called this function.
        return affected, cur.lastrowid


# Handle check connection requests or data.
def check_connection():
    """Used by `flask check-db` and /health/db. Returns (ok, message)."""
    # Try the operation and handle any errors.
    try:
        row = query_one("SELECT COUNT(*) AS n FROM users")
        # Send the result back to the code that called this function.
        return True, f"Connected to MySQL. users table has {row['n']} row(s)."
    except DatabaseError as exc:
        # Send the result back to the code that called this function.
        return False, str(exc)
