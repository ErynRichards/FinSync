# users.py
# Functions to add, find and update users.
# Passwords must be hashed (security.py) before they are passed in here.

from db import DatabaseError, execute, fetch_one


def create_user(full_name, email, password_hash):
    """Add a new user and return their user_id.
    The full name is split into first and last name, e.g. 'Daniel de Gois' -> 'Daniel', 'de Gois'."""
    names = full_name.strip().split(" ", 1)
    first_name = names[0]
    last_name = ""
    if len(names) == 2:
        last_name = names[1].strip()

    if first_name == "" or email == "" or password_hash == "":
        raise DatabaseError("Name, email and password are required.")

    sql = "INSERT INTO users (first_name, last_name, email, password_hash) VALUES (%s, %s, %s, %s)"
    rows_changed, user_id = execute(sql, (first_name, last_name, email.lower(), password_hash))
    return user_id


def get_user_by_email(email):
    """Find a user by email. Returns None if not found."""
    return fetch_one("SELECT * FROM users WHERE email = %s", (email.lower(),))


def get_user_by_id(user_id):
    """Find a user by ID. Returns None if not found."""
    return fetch_one("SELECT * FROM users WHERE user_id = %s", (user_id,))


def update_user(user_id, first_name, last_name, phone):
    """Update a user's name and phone number."""
    sql = "UPDATE users SET first_name = %s, last_name = %s, phone = %s WHERE user_id = %s"
    execute(sql, (first_name, last_name, phone, user_id))


def update_password(user_id, password_hash):
    """Save a new password hash for a user."""
    execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (password_hash, user_id))
