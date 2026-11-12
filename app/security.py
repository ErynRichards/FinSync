"""
Shared password helpers.

IMPORTANT FOR MISHAYLE (registration/login) AND DANIEL (password reset):
both MUST use hash_password() / verify_password() from this file. If they
used different hashing methods, a password set by the reset page would not
work on the login page.

Werkzeug (installed with Flask) produces salted hashes such as
"scrypt:32768:8:1$<salt>$<hash>". The method name is stored inside the hash,
so verify_password() keeps working even if the default method changes.
"""
# Load the tools needed in this file.
import re

# Use functions and classes from another file.
from werkzeug.security import check_password_hash, generate_password_hash

# Read the password min length setting.
PASSWORD_MIN_LENGTH = 8
# Read the password max length setting.
PASSWORD_MAX_LENGTH = 128

# Human-readable version of the rules - also shown on the forms.
# Michalyn's JavaScript validation (static/js/validation.js) uses the same rules.
PASSWORD_RULES_TEXT = (
    f"At least {PASSWORD_MIN_LENGTH} characters, including an uppercase letter, "
    "a lowercase letter, a number and a special character."
)

# Read the email re setting.
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# Turn the password into a secure hash before saving it.
def hash_password(plain_password: str) -> str:
    # Send the result back to the code that called this function.
    return generate_password_hash(plain_password)


# Handle verify password requests or data.
def verify_password(password_hash: str, plain_password: str) -> bool:
    # Check the condition before continuing.
    if not password_hash or plain_password is None:
        # Send the result back to the code that called this function.
        return False
    # Try the operation and handle any errors.
    try:
        # Send the result back to the code that called this function.
        return check_password_hash(password_hash, plain_password)
    except (ValueError, TypeError):
        # Send the result back to the code that called this function.
        return False


# Handle normalise email requests or data.
def normalise_email(email) -> str:
    """Trim spaces and lower-case, so 'Bob@Mail.com ' == 'bob@mail.com'."""
    # Send the result back to the code that called this function.
    return (email or "").strip().lower()


# Handle is valid email requests or data.
def is_valid_email(email: str) -> bool:
    # Send the result back to the code that called this function.
    return bool(email) and len(email) <= 255 and bool(EMAIL_RE.match(email))


# Handle password errors requests or data.
def password_errors(password, confirm=None):
    """
    Server-side password validation. Returns a list of error messages
    (empty list = valid). This runs even if the JavaScript check passed,
    because browser checks can be bypassed.
    """
    # Collect any input errors to show the user.
    errors = []
    password = password or ""
    # Check the condition before continuing.
    if not password:
        # Send the result back to the code that called this function.
        return ["Password is required."]
    # Check the condition before continuing.
    if len(password) < PASSWORD_MIN_LENGTH:
        # Add this item to the list of results.
        errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters.")
    # Check the condition before continuing.
    if len(password) > PASSWORD_MAX_LENGTH:
        # Add this item to the list of results.
        errors.append(f"Password must be at most {PASSWORD_MAX_LENGTH} characters.")
    # Check the condition before continuing.
    if not re.search(r"[A-Z]", password):
        # Add this item to the list of results.
        errors.append("Password must contain an uppercase letter.")
    # Check the condition before continuing.
    if not re.search(r"[a-z]", password):
        # Add this item to the list of results.
        errors.append("Password must contain a lowercase letter.")
    # Check the condition before continuing.
    if not re.search(r"\d", password):
        # Add this item to the list of results.
        errors.append("Password must contain a number.")
    # Check the condition before continuing.
    if not re.search(r"[^A-Za-z0-9]", password):
        # Add this item to the list of results.
        errors.append("Password must contain a special character.")
    # Check the condition before continuing.
    if confirm is not None and password != confirm:
        # Add this item to the list of results.
        errors.append("Passwords do not match.")
    # Send the result back to the code that called this function.
    return errors
