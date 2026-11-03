"""
TEST-ONLY stand-in for PyMySQL, backed by SQLite.

Why: the automated tests must run on machines without a MySQL server
(e.g. GitHub, or the environment this project was built in). This fake
lets the REAL application code (app/db.py, users.py, reset_tokens.py,
routes) run unchanged. It is NOT used when you run the app normally.

It does not prove the MySQL scripts themselves are correct - run those
on a real MySQL server (README step 4) and use `flask --app run check-db`.
"""
import sqlite3
import types
from datetime import datetime

sqlite3.register_adapter(datetime, lambda d: d.isoformat(sep=" "))
sqlite3.register_converter("DATETIME", lambda b: datetime.fromisoformat(b.decode()))

SCHEMA = """
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    phone TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE password_reset_tokens (
    token_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    created_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL
);
"""


class MySQLError(Exception):
    pass


class IntegrityError(MySQLError):
    pass


class OperationalError(MySQLError):
    pass


class _Cursor:
    def __init__(self, conn):
        self._cur = conn.cursor()
        self.lastrowid = None
        self._rows = []

    def execute(self, sql, params=()):
        sql = sql.replace("%s", "?")
        try:
            self._cur.execute(sql, tuple(params))
        except sqlite3.IntegrityError as exc:
            code = 1062 if "UNIQUE" in str(exc) else 1452
            raise IntegrityError(code, str(exc)) from exc
        except sqlite3.Error as exc:
            raise OperationalError(2000, str(exc)) from exc
        self.lastrowid = self._cur.lastrowid
        # Like PyMySQL: buffer SELECT results and return the row count
        self._rows = [dict(r) for r in self._cur.fetchall()] if self._cur.description else []
        return self._cur.rowcount if self._cur.rowcount >= 0 else len(self._rows)

    def fetchone(self):
        return self._rows.pop(0) if self._rows else None

    def fetchall(self):
        rows, self._rows = self._rows, []
        return rows

    def close(self):
        self._cur.close()


class _Connection:
    def __init__(self, path):
        self._conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def cursor(self):
        return _Cursor(self._conn)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


# set by the test fixture
STATE = {"path": None, "down": False, "connect_calls": []}


def connect(**kwargs):
    STATE["connect_calls"].append(kwargs)
    if STATE["down"]:
        raise OperationalError(2003, "Can't connect to MySQL server on 'localhost' (10061)")
    return _Connection(STATE["path"])


def create_schema(path):
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.close()


def install(sys_modules):
    """Register this fake as 'pymysql' (+ submodules) before the app is imported."""
    mod = types.ModuleType("pymysql")
    mod.connect = connect
    mod.MySQLError = MySQLError
    mod.err = types.SimpleNamespace(IntegrityError=IntegrityError, OperationalError=OperationalError)
    cursors = types.ModuleType("pymysql.cursors")
    cursors.DictCursor = object
    constants = types.ModuleType("pymysql.constants")
    constants.CLIENT = types.SimpleNamespace(FOUND_ROWS=2)
    mod.cursors = cursors
    mod.constants = constants
    sys_modules["pymysql"] = mod
    sys_modules["pymysql.cursors"] = cursors
    sys_modules["pymysql.constants"] = constants
