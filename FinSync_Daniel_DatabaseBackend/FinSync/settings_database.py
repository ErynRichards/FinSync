# settings_database.py
# Database functions for the Settings screen: profile, password and preferences.

from db import DatabaseError, execute, fetch_one


def get_profile(user_id):
    """Get the user's profile details (without the password)."""
    sql = "SELECT user_id, first_name, last_name, email, phone FROM users WHERE user_id = %s"
    return fetch_one(sql, (user_id,))


def update_profile(user_id, first_name, last_name, email, phone):
    """Update the user's name, email and phone number.
    Raises DuplicateEmailError if the email is already used by someone else."""
    if first_name.strip() == "" or email.strip() == "":
        raise DatabaseError("Name and email are required.")

    sql = """UPDATE users SET first_name = %s, last_name = %s, email = %s, phone = %s
             WHERE user_id = %s"""
    execute(sql, (first_name, last_name, email.lower(), phone, user_id))


def get_password_hash(user_id):
    """Get the saved password hash, to check the current password."""
    row = fetch_one("SELECT password_hash FROM users WHERE user_id = %s", (user_id,))
    if row is None:
        return None
    return row["password_hash"]


def update_password_hash(user_id, password_hash):
    """Save a new password hash."""
    execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (password_hash, user_id))


def get_preferences(user_id):
    """Get the user's theme and notification settings.
    Returns the default settings if the user hasn't saved any yet."""
    row = fetch_one("SELECT * FROM user_settings WHERE user_id = %s", (user_id,))
    if row is None:
        return {"theme": "light", "budget_notifications": True, "savings_notifications": True}

    return {
        "theme": row["theme"],
        "budget_notifications": bool(row["budget_notifications"]),
        "savings_notifications": bool(row["savings_notifications"]),
    }


def save_preferences(user_id, theme, budget_notifications, savings_notifications):
    """Save the user's theme and notification settings."""
    if theme != "light" and theme != "dark":
        raise DatabaseError("Theme must be light or dark.")

    existing = fetch_one("SELECT user_id FROM user_settings WHERE user_id = %s", (user_id,))
    if existing is None:
        sql = """INSERT INTO user_settings (theme, budget_notifications, savings_notifications, user_id)
                 VALUES (%s, %s, %s, %s)"""
    else:
        sql = """UPDATE user_settings
                 SET theme = %s, budget_notifications = %s, savings_notifications = %s
                 WHERE user_id = %s"""
    execute(sql, (theme, budget_notifications, savings_notifications, user_id))
