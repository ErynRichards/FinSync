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
import logging
from contextlib import contextmanager

import pymysql
import pymysql.cursors
from pymysql.constants import CLIENT
from flask import current_app, g

log = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Raised for database problems. The message is safe to show users."""


class DuplicateEmailError(DatabaseError):
    """Raised when inserting a user whose email already exists."""


def _connect():
    cfg = current_app.config
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


def get_db():
    """Return this request's database connection (opening it if needed)."""
    if "db" not in g:
        try:
            g.db = _connect()
        except pymysql.MySQLError as exc:
            # Full detail goes to the server log only - never to the browser.
            log.error("Could not connect to MySQL: %s", exc)
            raise DatabaseError("The database is unavailable. Please try again later.") from exc
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        try:
            db.close()
        except Exception:  # already closed / connection lost
            pass


@contextmanager
def transaction():
    """
    Usage:
        with transaction() as cur:
            cur.execute(...)
            cur.execute(...)
    Commits if the block finishes, rolls back if anything raises.
    """
    conn = get_db()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except pymysql.err.IntegrityError as exc:
        conn.rollback()
        # MySQL error 1062 = duplicate entry for a UNIQUE key
        if exc.args and exc.args[0] == 1062:
            raise DuplicateEmailError("An account with that email address already exists.") from exc
        log.error("Integrity error: %s", exc)
        raise DatabaseError("The request could not be saved.") from exc
    except pymysql.MySQLError as exc:
        conn.rollback()
        log.error("Database error: %s", exc)
        raise DatabaseError("A database error occurred. Please try again later.") from exc
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def query_one(sql, params=()):
    """Run a SELECT and return the first row as a dict, or None."""
    with transaction() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def query_all(sql, params=()):
    """Run a SELECT and return all rows as a list of dicts."""
    with transaction() as cur:
        cur.execute(sql, params)
        return list(cur.fetchall())


def execute(sql, params=()):
    """Run INSERT/UPDATE/DELETE. Returns (rows_affected, last_insert_id)."""
    with transaction() as cur:
        affected = cur.execute(sql, params)
        return affected, cur.lastrowid


def check_connection():
    """Used by `flask check-db` and /health/db. Returns (ok, message)."""
    try:
        row = query_one("SELECT COUNT(*) AS n FROM users")
        return True, f"Connected to MySQL. users table has {row['n']} row(s)."
    except DatabaseError as exc:
        return False, str(exc)
