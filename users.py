# users.py
# Functions to add, find and update users.
# Passwords must be hashed (security.py) before they are passed in here.

# Use functions and classes from another file.
from db import DatabaseError, execute, fetch_one


# Handle create user requests or data.
def create_user(full_name, email, password_hash):
    """Add a new user and return their user_id.
    The full name is split into first and last name, e.g. 'Daniel de Gois' -> 'Daniel', 'de Gois'."""
    names = full_name.strip().split(" ", 1)
    first_name = names[0]
    last_name = ""

    # Check the condition before continuing.
    if len(names) == 2:
        last_name = names[1].strip()

    # Check the condition before continuing.
    if first_name == "" or email == "" or password_hash == "":

        # Stop the operation and report an error.
        raise DatabaseError("Name, email and password are required.")

    sql = "INSERT INTO users (first_name, last_name, email, password_hash) VALUES (%s, %s, %s, %s)"
    rows_changed, user_id = execute(sql, (first_name, last_name, email.lower(), password_hash))

    # Send the result back to the code that called this function.
    return user_id


# Handle get user by email requests or data.
def get_user_by_email(email):
    """Find a user by email. Returns None if not found."""

    # Send the result back to the code that called this function.
    return fetch_one("SELECT * FROM users WHERE email = %s", (email.lower(),))


# Handle get user by id requests or data.
def get_user_by_id(user_id):
    """Find a user by ID. Returns None if not found."""

    # Send the result back to the code that called this function.
    return fetch_one("SELECT * FROM users WHERE user_id = %s", (user_id,))


# Handle update user requests or data.
def update_user(user_id, first_name, last_name, phone):
    """Update a user's name and phone number."""
    sql = "UPDATE users SET first_name = %s, last_name = %s, phone = %s WHERE user_id = %s"

    # Run the database query using these values.
    execute(sql, (first_name, last_name, phone, user_id))


# Handle update password requests or data.
def update_password(user_id, password_hash):
    """Save a new password hash for a user."""

    # Run the database query using these values.
    execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (password_hash, user_id))
