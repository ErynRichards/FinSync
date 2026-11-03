"""End-to-end tests of the forgot/reset password flow through Flask."""
import smtplib
from datetime import timedelta

import fake_pymysql
from app import reset_tokens, users
from app.security import hash_password
from conftest import extract_reset_path, get_csrf

OLD_PW = "OldPassw0rd!"
NEW_PW = "NewPassw0rd!"
GENERIC = "If an account exists for that email address"


def make_user(app, email="user@example.com", pw=OLD_PW):
    with app.app_context():
        return users.create_user("Test User", email, hash_password(pw))


def request_reset(client, email):
    token = get_csrf(client, "/forgot-password")
    return client.post("/forgot-password", data={"email": email, "csrf_token": token})


def submit_new_password(client, path, pw, confirm=None):
    token = get_csrf(client, path)
    return client.post(path, data={"password": pw, "confirm_password": confirm or pw,
                                   "csrf_token": token})


def login(client, email, pw):
    token = get_csrf(client, "/login")
    return client.post("/login", data={"email": email, "password": pw, "csrf_token": token})


def token_rows(app):
    with app.app_context():
        from app.db import query_all
        return query_all("SELECT * FROM password_reset_tokens ORDER BY token_id")


# ---------------------------------------------------------------------------

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


def test_token_stored_as_hash_only(app, client, sent_emails):
    make_user(app)
    request_reset(client, "user@example.com")
    raw = extract_reset_path(sent_emails[0]["text"]).rsplit("/", 1)[1]
    rows = token_rows(app)
    assert len(rows) == 1
    assert rows[0]["token_hash"] == reset_tokens.hash_token(raw)
    assert raw not in str(rows[0])
    assert len(raw) >= 40


def test_unknown_email_same_response_no_token(app, client, sent_emails):
    make_user(app)
    r = request_reset(client, "nobody@example.com")
    assert r.status_code == 200 and GENERIC in r.get_data(as_text=True)
    assert sent_emails == [] and token_rows(app) == []


def test_invalid_email_format(client, sent_emails):
    r = request_reset(client, "not-an-email")
    assert r.status_code == 400 and "valid email" in r.get_data(as_text=True)


def test_invalid_token_rejected(client):
    r = client.get("/reset-password/made-up-token")
    assert r.status_code == 400 and "invalid" in r.get_data(as_text=True)


def test_expired_token_rejected(app, client, sent_emails):
    make_user(app)
    request_reset(client, "user@example.com")
    path = extract_reset_path(sent_emails[0]["text"])
    with app.app_context():
        from app.db import execute
        past = reset_tokens.utcnow() - timedelta(minutes=1)
        execute("UPDATE password_reset_tokens SET expires_at = %s", (past,))
    r = client.get(path)
    assert r.status_code == 410 and "expired" in r.get_data(as_text=True)
    # POST is rejected as well, password unchanged
    r = client.post(path, data={"password": NEW_PW, "confirm_password": NEW_PW,
                                "csrf_token": get_csrf(client, "/login")})
    assert r.status_code == 410
    assert login(client, "user@example.com", OLD_PW).status_code == 302


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


def test_new_reset_invalidates_other_links(app, client, sent_emails):
    make_user(app)
    request_reset(client, "user@example.com")
    request_reset(client, "user@example.com")
    first, second = (extract_reset_path(m["text"]) for m in sent_emails)
    assert submit_new_password(client, second, NEW_PW).status_code == 302
    assert client.get(first).status_code == 410     # older link is dead too


def test_token_single_use_at_function_level(app, client, sent_emails):
    """Simulates two submissions racing with the same token."""
    make_user(app)
    request_reset(client, "user@example.com")
    raw = extract_reset_path(sent_emails[0]["text"]).rsplit("/", 1)[1]
    with app.app_context():
        assert reset_tokens.consume_token_and_set_password(raw, hash_password(NEW_PW)) == (True, None)
        assert reset_tokens.consume_token_and_set_password(raw, hash_password("Other1!pass")) == (False, "used")


def test_rate_limit(app, client, sent_emails):
    make_user(app)
    for _ in range(5):
        r = request_reset(client, "user@example.com")
        assert r.status_code == 200 and GENERIC in r.get_data(as_text=True)
    assert len(sent_emails) == 3            # RESET_MAX_REQUESTS
    assert len(token_rows(app)) == 3


def test_csrf_required(client):
    r = client.post("/forgot-password", data={"email": "user@example.com"})
    assert r.status_code == 400


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


def test_database_down_friendly_page(app, client):
    csrf = get_csrf(client, "/forgot-password")
    fake_pymysql.STATE["down"] = True
    r = client.post("/forgot-password", data={"email": "a@example.com", "csrf_token": csrf})
    body = r.get_data(as_text=True)
    assert r.status_code == 503 and "unavailable" in body and "10061" not in body
    assert client.get("/health/db").status_code == 503


def test_security_headers(client):
    r = client.get("/forgot-password")
    assert r.headers["Referrer-Policy"] == "no-referrer"
    assert r.headers["X-Frame-Options"] == "DENY"


def test_deleted_user_token_invalid(app, client, sent_emails):
    uid = make_user(app)
    request_reset(client, "user@example.com")
    path = extract_reset_path(sent_emails[0]["text"])
    with app.app_context():
        from app.db import execute
        execute("DELETE FROM users WHERE user_id = %s", (uid,))
    assert client.get(path).status_code == 400


def test_cleanup_tokens(app, client, sent_emails):
    make_user(app)
    request_reset(client, "user@example.com")
    with app.app_context():
        from app.db import execute
        old = reset_tokens.utcnow() - timedelta(days=10)
        execute("UPDATE password_reset_tokens SET expires_at = %s", (old,))
        assert reset_tokens.delete_old_tokens(7) == 1


# --- real email_service code paths (SMTP mocked, console backend) ----------

class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout=None):
        self.host, self.port, self.calls = host, port, []
        FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def starttls(self, context=None):
        self.calls.append("starttls")

    def login(self, user, pw):
        self.calls.append(("login", user))

    def send_message(self, msg):
        self.calls.append(("send", msg["To"], msg["Subject"]))
        self.msg = msg


def test_smtp_backend_sends(app, monkeypatch):
    FakeSMTP.instances = []
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    app.config.update(MAIL_BACKEND="smtp", MAIL_SERVER="smtp.test", MAIL_PORT=587,
                      MAIL_USERNAME="me@test", MAIL_PASSWORD="x", MAIL_SENDER="me@test")
    from app.email_service import send_password_reset_email
    with app.test_request_context():
        assert send_password_reset_email("u@example.com", "Ann", "http://x/reset-password/abc", 30)
    s = FakeSMTP.instances[0]
    assert s.calls[0] == "starttls" and s.calls[1] == ("login", "me@test")
    assert s.calls[2] == ("send", "u@example.com", "Reset your FinSync password")
    assert "http://x/reset-password/abc" in s.msg.get_body(("plain",)).get_content()


def test_smtp_failure_is_handled(app, client, monkeypatch):
    class Broken(FakeSMTP):
        def login(self, user, pw):
            raise smtplib.SMTPAuthenticationError(535, b"bad credentials")
    monkeypatch.setattr(smtplib, "SMTP", Broken)
    app.config.update(MAIL_BACKEND="smtp", MAIL_SERVER="smtp.test", MAIL_USERNAME="me@test",
                      MAIL_PASSWORD="x", MAIL_SENDER="me@test")
    make_user(app)
    r = request_reset(client, "user@example.com")
    assert r.status_code == 200 and GENERIC in r.get_data(as_text=True)   # no leak, no crash


def test_console_backend_prints(app, capsys):
    from app.email_service import send_email
    with app.app_context():
        assert send_email("u@example.com", "Subj", "the body")
    assert "NOT actually sent" in capsys.readouterr().out
