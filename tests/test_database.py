"""Database functions (users.py) and password helpers (security.py)."""
# Load the tools needed in this file.
import pytest

# Load the tools needed in this file.
import fake_pymysql
# Use functions and classes from another file.
from app import users
# Use functions and classes from another file.
from app.db import DatabaseError, DuplicateEmailError
# Use functions and classes from another file.
from app.security import hash_password, password_errors, verify_password


# Test case: verify the create and get user behavior.
def test_create_and_get_user(app):
    # Use this resource and close it when finished.
    with app.app_context():
        uid = users.create_user("Daniel de Gois", "  Daniel@Example.COM ", hash_password("Passw0rd!"))
        u = users.get_user_by_email("daniel@example.com")
        assert u["user_id"] == uid
        assert u["first_name"] == "Daniel" and u["last_name"] == "de Gois"
        assert u["email"] == "daniel@example.com"          # normalised
        assert users.get_user_by_id(uid)["email"] == "daniel@example.com"
        assert users.email_exists("DANIEL@example.com")
        assert users.get_user_by_email("nobody@example.com") is None


# Test case: verify the password is hashed not plaintext behavior.
def test_password_is_hashed_not_plaintext(app):
    # Use this resource and close it when finished.
    with app.app_context():
        users.create_user("A B", "a@example.com", hash_password("Passw0rd!"))
        stored = users.get_user_by_email("a@example.com")["password_hash"]
        assert "Passw0rd!" not in stored
        assert stored.startswith(("scrypt:", "pbkdf2:"))
        assert verify_password(stored, "Passw0rd!")
        assert not verify_password(stored, "wrong")


# Test case: verify the duplicate email rejected behavior.
def test_duplicate_email_rejected(app):
    # Use this resource and close it when finished.
    with app.app_context():
        users.create_user("A B", "dup@example.com", hash_password("Passw0rd!"))
        # Use this resource and close it when finished.
        with pytest.raises(DuplicateEmailError):
            users.create_user("C D", "DUP@example.com", hash_password("Passw0rd!"))


# Test case: verify the update user and password behavior.
def test_update_user_and_password(app):
    # Use this resource and close it when finished.
    with app.app_context():
        uid = users.create_user("A B", "u@example.com", hash_password("Passw0rd!"))
        assert users.update_user(uid, phone="0821234567", first_name="Ann")
        u = users.get_user_by_id(uid)
        assert u["phone"] == "0821234567" and u["first_name"] == "Ann"
        assert users.update_password_hash(uid, hash_password("N3w-Pass!"))
        assert verify_password(users.get_user_by_id(uid)["password_hash"], "N3w-Pass!")
        assert users.update_user(9999, phone="1") is False


# Test case: verify the update user rejects unknown columns behavior.
def test_update_user_rejects_unknown_columns(app):
    # Use this resource and close it when finished.
    with app.app_context():
        uid = users.create_user("A B", "w@example.com", hash_password("Passw0rd!"))
        # Use this resource and close it when finished.
        with pytest.raises(ValueError):
            users.update_user(uid, password_hash="x")
        # Use this resource and close it when finished.
        with pytest.raises(ValueError):
            users.update_user(uid, **{"email = 'x'; --": "y"})


# Test case: verify the sql injection attempt is harmless behavior.
def test_sql_injection_attempt_is_harmless(app):
    # Use this resource and close it when finished.
    with app.app_context():
        users.create_user("A B", "safe@example.com", hash_password("Passw0rd!"))
        assert users.get_user_by_email("' OR '1'='1") is None
        assert users.email_exists("safe@example.com")


# Test case: verify the database down gives friendly error behavior.
def test_database_down_gives_friendly_error(app):
    fake_pymysql.STATE["down"] = True
    # Use this resource and close it when finished.
    with app.app_context():
        # Use this resource and close it when finished.
        with pytest.raises(DatabaseError) as exc:
            users.get_user_by_email("a@example.com")
        assert "unavailable" in str(exc.value)
        assert "10061" not in str(exc.value)   # internal detail not exposed


# Test case: verify the split full name behavior.
def test_split_full_name():
    assert users.split_full_name("Mary") == ("Mary", "")
    assert users.split_full_name("  Mary   Jane Smith ") == ("Mary", "Jane Smith")


# Test case: verify the password rules behavior.
@pytest.mark.parametrize("pw,ok", [
    ("Passw0rd!", True), ("short1!", False), ("alllowercase1!", False),
    ("ALLUPPER1!", False), ("NoDigits!!", False), ("NoSpecial11", False), ("", False),
])
def test_password_rules(pw, ok):
    assert (password_errors(pw) == []) is ok


# Test case: verify the password mismatch behavior.
def test_password_mismatch():
    assert "Passwords do not match." in password_errors("Passw0rd!", "Passw0rd?")


# Test case: verify the cli check db behavior.
def test_cli_check_db(app):
    runner = app.test_cli_runner()
    assert "OK: Connected to MySQL" in runner.invoke(args=["check-db"]).output
    fake_pymysql.STATE["down"] = True
    assert "FAILED" in runner.invoke(args=["check-db"]).output


# Test case: verify the missing secret key is reported behavior.
def test_missing_secret_key_is_reported(app):
    # Use functions and classes from another file.
    from app import create_app
    # Use this resource and close it when finished.
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app({"SECRET_KEY": ""})
