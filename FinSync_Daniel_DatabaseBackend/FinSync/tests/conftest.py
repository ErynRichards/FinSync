import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The automated tests use a SQLite-backed stand-in for PyMySQL so they run
# without a MySQL server. To test against your REAL MySQL database, use
# scripts/mysql_smoke_test.py instead (see README).
import fake_pymysql  # noqa: E402
fake_pymysql.install(sys.modules)

from app import create_app  # noqa: E402

TEST_CONFIG = {
    "TESTING": True,
    "SECRET_KEY": "test-secret-key",
    "MAIL_BACKEND": "console",
    "APP_BASE_URL": "http://127.0.0.1:5000",
    "RESET_TOKEN_EXPIRY_MINUTES": 30,
    "RESET_MAX_REQUESTS": 3,
    "RESET_WINDOW_MINUTES": 15,
}


@pytest.fixture
def app(tmp_path):
    db_path = str(tmp_path / "test.db")
    fake_pymysql.create_schema(db_path)
    fake_pymysql.STATE.update(path=db_path, down=False, connect_calls=[])
    return create_app(TEST_CONFIG)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sent_emails(monkeypatch):
    """Capture emails instead of printing/sending them."""
    outbox = []

    def fake_send(to_address, subject, text_body, html_body=None):
        outbox.append({"to": to_address, "subject": subject, "text": text_body, "html": html_body})
        return True

    import app.email_service as es
    monkeypatch.setattr(es, "send_email", fake_send)
    return outbox


def get_csrf(client, url):
    html = client.get(url).get_data(as_text=True)
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert m, f"no csrf token on {url}"
    return m.group(1)


def extract_reset_path(email_text):
    m = re.search(r"http://127\.0\.0\.1:5000(/reset-password/[A-Za-z0-9_\-]+)", email_text)
    assert m, "no reset link in email"
    return m.group(1)
