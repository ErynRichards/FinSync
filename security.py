# security.py
# Password hashing and input checks.
# Sign-up, login and password reset must all use these functions,
# otherwise a password changed on the reset page won't work at login.

# Load the tools needed in this file.
import re

# Use functions and classes from another file.
from werkzeug.security import check_password_hash, generate_password_hash


# Turn the password into a secure hash before saving it.
def hash_password(password):
    """Turn a password into a secure hash before saving it."""

    # Send the result back to the code that called this function.
    return generate_password_hash(password)


# Verify a submitted password against its saved password hash.
def check_password(password_hash, password):
    """Return True if the password matches the saved hash."""

    # Send the result back to the code that called this function.
    return check_password_hash(password_hash, password)


# Handle is valid email requests or data.
def is_valid_email(email):
    """Check that the email looks like name@example.com."""
    # Send the result back to the code that called this function.
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


# Handle check password rules requests or data.
def check_password_rules(password, confirm_password):
    """Return a list of problems with the password. An empty list means it's fine."""

    # Collect any input errors to show the user.
    errors = []

    # Check the condition before continuing.
    if len(password) < 8:

        # Add this item to the list of results.
        errors.append("Password must be at least 8 characters.")

    # Check the condition before continuing.
    if not re.search("[A-Z]", password):

        # Add this item to the list of results.
        errors.append("Password must contain an uppercase letter.")

    # Check the condition before continuing.
    if not re.search("[a-z]", password):

        # Add this item to the list of results.
        errors.append("Password must contain a lowercase letter.")

    # Check the condition before continuing.
    if not re.search("[0-9]", password):

        # Add this item to the list of results.
        errors.append("Password must contain a number.")

    # Check the condition before continuing.
    if not re.search("[^A-Za-z0-9]", password):

        # Add this item to the list of results.
        errors.append("Password must contain a special character.")

    # Check the condition before continuing.
    if password != confirm_password:

        # Add this item to the list of results.
        errors.append("Passwords do not match.")

    # Send the result back to the code that called this function.
    return errors
