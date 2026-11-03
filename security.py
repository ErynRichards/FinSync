# security.py
# Password hashing and input checks.
# Sign-up, login and password reset must all use these functions,
# otherwise a password changed on the reset page won't work at login.

import re

from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password):
    """Turn a password into a secure hash before saving it."""
    return generate_password_hash(password)


def check_password(password_hash, password):
    """Return True if the password matches the saved hash."""
    return check_password_hash(password_hash, password)


def is_valid_email(email):
    """Check that the email looks like name@example.com."""
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def check_password_rules(password, confirm_password):
    """Return a list of problems with the password. An empty list means it's fine."""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if not re.search("[A-Z]", password):
        errors.append("Password must contain an uppercase letter.")
    if not re.search("[a-z]", password):
        errors.append("Password must contain a lowercase letter.")
    if not re.search("[0-9]", password):
        errors.append("Password must contain a number.")
    if not re.search("[^A-Za-z0-9]", password):
        errors.append("Password must contain a special character.")
    if password != confirm_password:
        errors.append("Passwords do not match.")
    return errors
