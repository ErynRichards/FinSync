# settings_database.py
# Database functions for the Settings screen: profile, password and preferences.

# Use functions and classes from another file.
from db import DatabaseError, execute, fetch_one


# Handle get profile requests or data.
def get_profile(user_id):
    """Get the user's profile details (without the password)."""
    sql = "SELECT user_id, first_name, last_name, email, phone FROM users WHERE user_id = %s"
    # Send the result back to the code that called this function.
    return fetch_one(sql, (user_id,))


# Handle update profile requests or data.
def update_profile(user_id, first_name, last_name, email, phone):
    """Update the user's name, email and phone number.
    Raises DuplicateEmailError if the email is already used by someone else."""

    # Check the condition before continuing.
    if first_name.strip() == "" or email.strip() == "":

        # Stop the operation and report an error.
        raise DatabaseError("Name and email are required.")

    sql = """UPDATE users SET first_name = %s, last_name = %s, email = %s, phone = %s
             WHERE user_id = %s"""

    # Run the database query using these values.
    execute(sql, (first_name, last_name, email.lower(), phone, user_id))


# Handle get password hash requests or data.
def get_password_hash(user_id):
    """Get the saved password hash, to check the current password."""
    row = fetch_one("SELECT password_hash FROM users WHERE user_id = %s", (user_id,))

    # Check the condition before continuing.
    if row is None:

        # Send the result back to the code that called this function.
        return None

    # Send the result back to the code that called this function.
    return row["password_hash"]


# Handle update password hash requests or data.
def update_password_hash(user_id, password_hash):
    """Save a new password hash."""

    # Run the database query using these values.
    execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (password_hash, user_id))


# Handle get preferences requests or data.
def get_preferences(user_id):
    """Get the user's theme and notification settings.
    Returns the default settings if the user hasn't saved any yet."""
    row = fetch_one("SELECT * FROM user_settings WHERE user_id = %s", (user_id,))

    # Check the condition before continuing.
    if row is None:

        # Send the result back to the code that called this function.
        return {"theme": "light", "budget_notifications": True, "savings_notifications": True}

    # Send the result back to the code that called this function.
    return {
        "theme": row["theme"],
        "budget_notifications": bool(row["budget_notifications"]),
        "savings_notifications": bool(row["savings_notifications"]),
    }


# Handle save preferences requests or data.
def save_preferences(user_id, theme, budget_notifications, savings_notifications):
    """Save the user's theme and notification settings."""

    # Check the condition before continuing.
    if theme != "light" and theme != "dark":

        # Stop the operation and report an error.
        raise DatabaseError("Theme must be light or dark.")

    existing = fetch_one("SELECT user_id FROM user_settings WHERE user_id = %s", (user_id,))

    # Check the condition before continuing.
    if existing is None:
        sql = """INSERT INTO user_settings (theme, budget_notifications, savings_notifications, user_id)
                 VALUES (%s, %s, %s, %s)"""
    else:
        sql = """UPDATE user_settings
                 SET theme = %s, budget_notifications = %s, savings_notifications = %s
                 WHERE user_id = %s"""

    # Run the database query using these values.
    execute(sql, (theme, budget_notifications, savings_notifications, user_id))
