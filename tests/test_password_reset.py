"""End-to-end tests of the forgot/reset password flow through Flask."""
# Load the tools needed in this file.
import smtplib
# Use functions and classes from another file.
from datetime import timedelta

# Load the tools needed in this file.
import fake_pymysql
# Use functions and classes from another file.
from app import reset_tokens, users
# Use functions and classes from another file.
from app.security import hash_password
# Use functions and classes from another file.
from conftest import extract_reset_path, get_csrf

# Read the old pw setting.
OLD_PW = "OldPassw0rd!"
# Read the new pw setting.
NEW_PW = "NewPassw0rd!"
# Read the generic setting.
GENERIC = "If an account exists for that email address"


# Handle make user requests or data.
def make_user(app, email="user@example.com", pw=OLD_PW):
    # Use this resource and close it when finished.
    with app.app_context():
        # Send the result back to the code that called this function.
        return users.create_user("Test User", email, hash_password(pw))


# Handle request reset requests or data.
def request_reset(client, email):
    token = get_csrf(client, "/forgot-password")
    # Send the result back to the code that called this function.
    return client.post("/forgot-password", data={"email": email, "csrf_token": token})


# Handle submit new password requests or data.
def submit_new_password(client, path, pw, confirm=None):
    token = get_csrf(client, path)
    # Send the result back to the code that called this function.
    return client.post(path, data={"password": pw, "confirm_password": confirm or pw,
                                   "csrf_token": token})


# Check login details and remember the logged in user.
def login(client, email, pw):
    token = get_csrf(client, "/login")
    # Send the result back to the code that called this function.
    return client.post("/login", data={"email": email, "password": pw, "csrf_token": token})


# Handle token rows requests or data.
def token_rows(app):
    # Use this resource and close it when finished.
    with app.app_context():
        # Use functions and classes from another file.
        from app.db import query_all
        # Send the result back to the code that called this function.
        return query_all("SELECT * FROM password_reset_tokens ORDER BY token_id")


# Test case: verify the full reset flow behavior.
def test_full_reset_flow(app, client, sent_emails):
    make_user(app)
    r = request_reset(client, "USER@example.com")
    assert r.status_code == 200 and GENERIC in r.get_data(as_text=True)
    assert len(sent_emails) == 1
    mail = sent_emails[0]
    assert mail["to"] == "user@example.com"
    assert "30 minutes" in mail["text"] and "ignore this email" in mail["text"]
    path = extract_reset_path(mail["text"])

    # opening the link shows the form
    r = client.get(path)
    assert r.status_code == 200 and 'name="confirm_password"' in r.get_data(as_text=True)

    # successful reset -> redirect to login
    r = submit_new_password(client, path, NEW_PW)
    assert r.status_code == 302 and r.headers["Location"].endswith("/login")

    # old password fails, new password works
    assert login(client, "user@example.com", OLD_PW).status_code == 401
    r = login(client, "user@example.com", NEW_PW)
    assert r.status_code == 302 and r.headers["Location"].endswith("/dashboard")

    # the link cannot be reused
    r = client.get(path)
    assert r.status_code == 410 and "already been used" in r.get_data(as_text=True)


# Test case: verify the token stored as hash only behavior.
def test_token_stored_as_hash_only(app, client, sent_emails):
    make_user(app)
    request_reset(client, "user@example.com")
    raw = extract_reset_path(sent_emails[0]["text"]).rsplit("/", 1)[1]
    # Keep these records for the next step.
    rows = token_rows(app)
    assert len(rows) == 1
    assert rows[0]["token_hash"] == reset_tokens.hash_token(raw)
    assert raw not in str(rows[0])
    assert len(raw) >= 40


# Test case: verify the unknown email same response no token behavior.
def test_unknown_email_same_response_no_token(app, client, sent_emails):
    make_user(app)
    r = request_reset(client, "nobody@example.com")
    assert r.status_code == 200 and GENERIC in r.get_data(as_text=True)
    assert sent_emails == [] and token_rows(app) == []


# Test case: verify the invalid email format behavior.
def test_invalid_email_format(client, sent_emails):
    r = request_reset(client, "not-an-email")
    assert r.status_code == 400 and "valid email" in r.get_data(as_text=True)


# Test case: verify the invalid token rejected behavior.
def test_invalid_token_rejected(client):
    r = client.get("/reset-password/made-up-token")
    assert r.status_code == 400 and "invalid" in r.get_data(as_text=True)


# Test case: verify the expired token rejected behavior.
def test_expired_token_rejected(app, client, sent_emails):
    make_user(app)
    request_reset(client, "user@example.com")
    path = extract_reset_path(sent_emails[0]["text"])
    # Use this resource and close it when finished.
    with app.app_context():
        # Use functions and classes from another file.
        from app.db import execute
        past = reset_tokens.utcnow() - timedelta(minutes=1)
        # Run the database query using these values.
        execute("UPDATE password_reset_tokens SET expires_at = %s", (past,))
    r = client.get(path)
    assert r.status_code == 410 and "expired" in r.get_data(as_text=True)
    # POST is rejected as well, password unchanged
    r = client.post(path, data={"password": NEW_PW, "confirm_password": NEW_PW,
                                "csrf_token": get_csrf(client, "/login")})
    assert r.status_code == 410
    assert login(client, "user@example.com", OLD_PW).status_code == 302


# Test case: verify the validation errors keep token usable behavior.
def test_validation_errors_keep_token_usable(app, client, sent_emails):
    make_user(app)
    request_reset(client, "user@example.com")
    path = extract_reset_path(sent_emails[0]["text"])
    r = submit_new_password(client, path, NEW_PW, "Different1!")
    assert r.status_code == 400 and "do not match" in r.get_data(as_text=True)
    r = submit_new_password(client, path, "weak")
    assert r.status_code == 400 and "at least 8" in r.get_data(as_text=True)
    r = submit_new_password(client, path, OLD_PW)
    assert r.status_code == 400 and "different from your current" in r.get_data(as_text=True)
    # still usable after the failed attempts
    assert submit_new_password(client, path, NEW_PW).status_code == 302


# Test case: verify the new reset invalidates other links behavior.
def test_new_reset_invalidates_other_links(app, client, sent_emails):
    make_user(app)
    request_reset(client, "user@example.com")
    request_reset(client, "user@example.com")
    first, second = (extract_reset_path(m["text"]) for m in sent_emails)
    assert submit_new_password(client, second, NEW_PW).status_code == 302
    assert client.get(first).status_code == 410     # older link is dead too


# Test case: verify the token single use at function level behavior.
def test_token_single_use_at_function_level(app, client, sent_emails):
    """Simulates two submissions racing with the same token."""
    make_user(app)
    request_reset(client, "user@example.com")
    raw = extract_reset_path(sent_emails[0]["text"]).rsplit("/", 1)[1]
    # Use this resource and close it when finished.
    with app.app_context():
        assert reset_tokens.consume_token_and_set_password(raw, hash_password(NEW_PW)) == (True, None)
        assert reset_tokens.consume_token_and_set_password(raw, hash_password("Other1!pass")) == (False, "used")


# Test case: verify the rate limit behavior.
def test_rate_limit(app, client, sent_emails):
    make_user(app)
    # Go through each item one at a time.
    for _ in range(5):
        r = request_reset(client, "user@example.com")
        assert r.status_code == 200 and GENERIC in r.get_data(as_text=True)
    assert len(sent_emails) == 3            # RESET_MAX_REQUESTS
    assert len(token_rows(app)) == 3


# Test case: verify the csrf required behavior.
def test_csrf_required(client):
    r = client.post("/forgot-password", data={"email": "user@example.com"})
    assert r.status_code == 400


# Test case: verify the json api behavior.
def test_json_api(app, client, sent_emails):
    make_user(app)
    csrf = get_csrf(client, "/forgot-password")
    r = client.post("/forgot-password", json={"email": "user@example.com"},
                    headers={"X-CSRFToken": csrf})
    assert r.status_code == 200 and r.get_json()["ok"] is True
    path = extract_reset_path(sent_emails[0]["text"])
    r = client.post(path, json={"password": NEW_PW, "confirm_password": "nope"},
                    headers={"X-CSRFToken": csrf})
    assert r.status_code == 400 and r.get_json()["ok"] is False
    r = client.post(path, json={"password": NEW_PW, "confirm_password": NEW_PW},
                    headers={"X-CSRFToken": csrf})
    assert r.status_code == 200 and r.get_json() == {
        "ok": True, "redirect": "/login",
        "message": "Your password has been reset. You can now log in with your new password."}


# Test case: verify the database down friendly page behavior.
def test_database_down_friendly_page(app, client):
    csrf = get_csrf(client, "/forgot-password")
    fake_pymysql.STATE["down"] = True
    r = client.post("/forgot-password", data={"email": "a@example.com", "csrf_token": csrf})
    body = r.get_data(as_text=True)
    assert r.status_code == 503 and "unavailable" in body and "10061" not in body
    assert client.get("/health/db").status_code == 503


# Test case: verify the security headers behavior.
def test_security_headers(client):
    r = client.get("/forgot-password")
    assert r.headers["Referrer-Policy"] == "no-referrer"
    assert r.headers["X-Frame-Options"] == "DENY"


# Test case: verify the deleted user token invalid behavior.
def test_deleted_user_token_invalid(app, client, sent_emails):
    uid = make_user(app)
    request_reset(client, "user@example.com")
    path = extract_reset_path(sent_emails[0]["text"])
    # Use this resource and close it when finished.
    with app.app_context():
        # Use functions and classes from another file.
        from app.db import execute
        # Run the database query using these values.
        execute("DELETE FROM users WHERE user_id = %s", (uid,))
    assert client.get(path).status_code == 400


# Test case: verify the cleanup tokens behavior.
def test_cleanup_tokens(app, client, sent_emails):
    make_user(app)
    request_reset(client, "user@example.com")
    # Use this resource and close it when finished.
    with app.app_context():
        # Use functions and classes from another file.
        from app.db import execute
        old = reset_tokens.utcnow() - timedelta(days=10)
        # Run the database query using these values.
        execute("UPDATE password_reset_tokens SET expires_at = %s", (old,))
        assert reset_tokens.delete_old_tokens(7) == 1


#real email_service code paths (SMTP mocked, console backend)

# Define FakeSMTP for this part of the program.
class FakeSMTP:
    instances = []

    # Set up a new object.
    def __init__(self, host, port, timeout=None):
        self.host, self.port, self.calls = host, port, []
        # Add this item to the list of results.
        FakeSMTP.instances.append(self)

    # Handle   enter   requests or data.
    def __enter__(self):
        # Send the result back to the code that called this function.
        return self

    # Handle   exit   requests or data.
    def __exit__(self, *a):
        # Send the result back to the code that called this function.
        return False

    # Handle starttls requests or data.
    def starttls(self, context=None):
        # Add this item to the list of results.
        self.calls.append("starttls")

    # Check login details and remember the logged in user.
    def login(self, user, pw):
        # Add this item to the list of results.
        self.calls.append(("login", user))

    # Handle send message requests or data.
    def send_message(self, msg):
        # Add this item to the list of results.
        self.calls.append(("send", msg["To"], msg["Subject"]))
        self.msg = msg


# Test case: verify the smtp backend sends behavior.
def test_smtp_backend_sends(app, monkeypatch):
    FakeSMTP.instances = []
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    app.config.update(MAIL_BACKEND="smtp", MAIL_SERVER="smtp.test", MAIL_PORT=587,
                      MAIL_USERNAME="me@test", MAIL_PASSWORD="x", MAIL_SENDER="me@test")
    # Use functions and classes from another file.
    from app.email_service import send_password_reset_email
    # Use this resource and close it when finished.
    with app.test_request_context():
        assert send_password_reset_email("u@example.com", "Ann", "http://x/reset-password/abc", 30)
    s = FakeSMTP.instances[0]
    assert s.calls[0] == "starttls" and s.calls[1] == ("login", "me@test")
    assert s.calls[2] == ("send", "u@example.com", "Reset your FinSync password")
    assert "http://x/reset-password/abc" in s.msg.get_body(("plain",)).get_content()


# Test case: verify the smtp failure is handled behavior.
def test_smtp_failure_is_handled(app, client, monkeypatch):
    # Define Broken for this part of the program.
    class Broken(FakeSMTP):
        # Check login details and remember the logged in user.
        def login(self, user, pw):
            # Stop the operation and report an error.
            raise smtplib.SMTPAuthenticationError(535, b"bad credentials")
    monkeypatch.setattr(smtplib, "SMTP", Broken)
    app.config.update(MAIL_BACKEND="smtp", MAIL_SERVER="smtp.test", MAIL_USERNAME="me@test",
                      MAIL_PASSWORD="x", MAIL_SENDER="me@test")
    make_user(app)
    r = request_reset(client, "user@example.com")
    assert r.status_code == 200 and GENERIC in r.get_data(as_text=True)   # no leak, no crash


# Test case: verify the console backend prints behavior.
def test_console_backend_prints(app, capsys):
    # Use functions and classes from another file.
    from app.email_service import send_email
    # Use this resource and close it when finished.
    with app.app_context():
        assert send_email("u@example.com", "Subj", "the body")
    assert "NOT actually sent" in capsys.readouterr().out
