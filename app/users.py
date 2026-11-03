"""
User database functions (Daniel).

These are the functions Mishayle's registration/login routes call instead of
writing SQL themselves. All of them use parameterised queries (%s).

    create_user(full_name, email, password_hash, phone=None) -> user_id
    get_user_by_email(email)  -> dict or None
    get_user_by_id(user_id)   -> dict or None
    email_exists(email)       -> True/False
    update_user(user_id, first_name=..., last_name=..., phone=...) -> True/False
    update_password_hash(user_id, new_hash) -> True/False

Errors:
    DuplicateEmailError - email already registered (show a friendly message)
    DatabaseError       - anything else went wrong (message is safe to show)

NOTE: create_user expects an ALREADY HASHED password. Hash it with
app.security.hash_password() first.
"""
from .db import DatabaseError, execute, query_one
from .security import normalise_email

# Columns returned to callers. password_hash is included because the login
# route needs it to verify passwords - never send it to the browser.
_USER_COLUMNS = (
    "user_id, first_name, last_name, email, password_hash, phone, created_at, updated_at"
)

# Only these columns may be changed through update_user()
_UPDATABLE = {"first_name", "last_name", "phone"}


def split_full_name(full_name: str):
    """'Daniel de Gois' -> ('Daniel', 'de Gois'). Single word -> (word, '')."""
    parts = (full_name or "").strip().split(None, 1)
    if not parts:
        return "", ""
    return parts[0][:50], (parts[1] if len(parts) > 1 else "")[:50]


def create_user(full_name, email, password_hash, phone=None):
    """Insert a user and return the new user_id."""
    first_name, last_name = split_full_name(full_name)
    email = normalise_email(email)
    if not first_name or not email or not password_hash:
        raise DatabaseError("Name, email and password are required.")
    _, new_id = execute(
        "INSERT INTO users (first_name, last_name, email, password_hash, phone) "
        "VALUES (%s, %s, %s, %s, %s)",
        (first_name, last_name, email, password_hash, phone),
    )
    return new_id


def get_user_by_email(email):
    return query_one(
        f"SELECT {_USER_COLUMNS} FROM users WHERE email = %s",
        (normalise_email(email),),
    )


def get_user_by_id(user_id):
    return query_one(f"SELECT {_USER_COLUMNS} FROM users WHERE user_id = %s", (user_id,))


def email_exists(email) -> bool:
    row = query_one("SELECT 1 AS found FROM users WHERE email = %s", (normalise_email(email),))
    return row is not None


def update_user(user_id, **fields) -> bool:
    """
    Update profile fields, e.g. update_user(5, phone="0821234567").
    Column NAMES come from a fixed whitelist (never from user input);
    VALUES are passed as parameters.
    """
    changes = {k: v for k, v in fields.items() if k in _UPDATABLE}
    unknown = set(fields) - _UPDATABLE
    if unknown:
        raise ValueError(f"Cannot update column(s): {', '.join(sorted(unknown))}")
    if not changes:
        return False
    set_clause = ", ".join(f"{col} = %s" for col in changes)
    affected, _ = execute(
        f"UPDATE users SET {set_clause} WHERE user_id = %s",
        (*changes.values(), user_id),
    )
    return affected > 0


def update_password_hash(user_id, new_password_hash) -> bool:
    affected, _ = execute(
        "UPDATE users SET password_hash = %s WHERE user_id = %s",
        (new_password_hash, user_id),
    )
    return affected > 0
