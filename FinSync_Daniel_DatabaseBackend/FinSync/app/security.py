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
import re

from werkzeug.security import check_password_hash, generate_password_hash

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

# Human-readable version of the rules - also shown on the forms.
# Michalyn's JavaScript validation (static/js/validation.js) uses the same rules.
PASSWORD_RULES_TEXT = (
    f"At least {PASSWORD_MIN_LENGTH} characters, including an uppercase letter, "
    "a lowercase letter, a number and a special character."
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(plain_password: str) -> str:
    return generate_password_hash(plain_password)


def verify_password(password_hash: str, plain_password: str) -> bool:
    if not password_hash or plain_password is None:
        return False
    try:
        return check_password_hash(password_hash, plain_password)
    except (ValueError, TypeError):
        return False


def normalise_email(email) -> str:
    """Trim spaces and lower-case, so 'Bob@Mail.com ' == 'bob@mail.com'."""
    return (email or "").strip().lower()


def is_valid_email(email: str) -> bool:
    return bool(email) and len(email) <= 255 and bool(EMAIL_RE.match(email))


def password_errors(password, confirm=None):
    """
    Server-side password validation. Returns a list of error messages
    (empty list = valid). This runs even if the JavaScript check passed,
    because browser checks can be bypassed.
    """
    errors = []
    password = password or ""
    if not password:
        return ["Password is required."]
    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters.")
    if len(password) > PASSWORD_MAX_LENGTH:
        errors.append(f"Password must be at most {PASSWORD_MAX_LENGTH} characters.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain an uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain a lowercase letter.")
    if not re.search(r"\d", password):
        errors.append("Password must contain a number.")
    if not re.search(r"[^A-Za-z0-9]", password):
        errors.append("Password must contain a special character.")
    if confirm is not None and password != confirm:
        errors.append("Passwords do not match.")
    return errors
