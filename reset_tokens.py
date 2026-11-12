# reset_tokens.py
# Creates and checks the tokens used in password-reset links.
# Only a hash of each token is saved, so the database alone can't be used to reset a password.

# Load the tools needed in this file.
import hashlib

# Load the tools needed in this file.
import secrets

# Use functions and classes from another file.
from datetime import datetime, timedelta

# Load the tools needed in this file.
import pymysql

# Load the tools needed in this file.
import config

# Use functions and classes from another file.
from db import DatabaseError, execute, fetch_one, get_connection


# Handle hash token requests or data.
def hash_token(token):
    """Return the SHA-256 hash of a token."""
    # Send the result back to the code that called this function.
    return hashlib.sha256(token.encode()).hexdigest()


# Handle create token requests or data.
def create_token(user_id):
    """Create a random reset token for a user, save its hash, and return the token."""
    token = secrets.token_urlsafe(32)
    created_at = datetime.now()
    expires_at = created_at + timedelta(minutes=config.RESET_TOKEN_EXPIRY_MINUTES)

    sql = """INSERT INTO password_reset_tokens (user_id, token_hash, created_at, expires_at)
             VALUES (%s, %s, %s, %s)"""

    # Run the database query using these values.
    execute(sql, (user_id, hash_token(token), created_at, expires_at))

    # Send the result back to the code that called this function.
    return token


# Handle check token requests or data.
def check_token(token):
    """Check a reset link's token.
    Returns (token_row, None) if it is valid, or (None, error_message) if not."""
    sql = "SELECT * FROM password_reset_tokens WHERE token_hash = %s"
    row = fetch_one(sql, (hash_token(token),))

    # Check the condition before continuing.
    if row is None:

        # Send the result back to the code that called this function.
        return None, "This password-reset link is invalid. Please request a new one."

    # Check the condition before continuing.
    if row["used_at"] is not None:
        # Send the result back to the code that called this function.

        return None, "This password-reset link has already been used. Please request a new one."

    # Check the condition before continuing.
    if row["expires_at"] < datetime.now():

        # Send the result back to the code that called this function.
        return None, "This password-reset link has expired. Please request a new one."

    # Send the result back to the code that called this function.
    return row, None


# Handle use token requests or data.
def use_token(token_row, password_hash):
    """Save the new password and mark the token as used.
    Both changes are saved together, or not at all (a transaction).
    Returns False if the token was already used."""
    now = datetime.now()

    # Get ready to run database queries.
    connection = get_connection()

    # Try the operation and handle any errors.
    try:
        # Get ready to run database queries.
        cursor = connection.cursor()

        # 1. Mark the token as used (only works if it hasn't been used yet)
        rows_changed = cursor.execute(
            "UPDATE password_reset_tokens SET used_at = %s WHERE token_id = %s AND used_at IS NULL",
            (now, token_row["token_id"]))

        # Check the condition before continuing.
        if rows_changed == 0:

            # Cancel database changes if something goes wrong.
            connection.rollback()

            # Send the result back to the code that called this function.
            return False

        # 2. Save the new password
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (password_hash, token_row["user_id"]))

        # 3. Cancel the user's other unused reset links
        cursor.execute(
            "UPDATE password_reset_tokens SET used_at = %s WHERE user_id = %s AND used_at IS NULL",
            (now, token_row["user_id"]))

        # Save the changes to the database.
        connection.commit()

        # Send the result back to the code that called this function.
        return True
    except pymysql.MySQLError as error:

        # Cancel database changes if something goes wrong.
        connection.rollback()
        print("Database error:", error)

        # Stop the operation and report an error.
        raise DatabaseError("A database error occurred. Please try again later.")

    finally:
        # Close this resource when finished.
        connection.close()
