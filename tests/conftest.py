# Load the tools needed in this file.
import os
# Load the tools needed in this file.
import re
# Load the tools needed in this file.
import sys

# Load the tools needed in this file.
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The automated tests use a SQLite-backed stand-in for PyMySQL so they run
# without a MySQL server. To test against your REAL MySQL database, use
# scripts/mysql_smoke_test.py instead (see README).
import fake_pymysql  # noqa: E402
fake_pymysql.install(sys.modules)

# Use functions and classes from another file.
from app import create_app  # noqa: E402

# Read the test config setting.
TEST_CONFIG = {
    "TESTING": True,
    "SECRET_KEY": "test-secret-key",
    "MAIL_BACKEND": "console",
    "APP_BASE_URL": "http://127.0.0.1:5000",
    "RESET_TOKEN_EXPIRY_MINUTES": 30,
    "RESET_MAX_REQUESTS": 3,
    "RESET_WINDOW_MINUTES": 15,
}


# Handle app requests or data.
@pytest.fixture
def app(tmp_path):
    db_path = str(tmp_path / "test.db")
    fake_pymysql.create_schema(db_path)
    fake_pymysql.STATE.update(path=db_path, down=False, connect_calls=[])
    # Send the result back to the code that called this function.
    return create_app(TEST_CONFIG)


# Handle client requests or data.
@pytest.fixture
def client(app):
    # Send the result back to the code that called this function.
    return app.test_client()


# Handle sent emails requests or data.
@pytest.fixture
def sent_emails(monkeypatch):
    """Capture emails instead of printing/sending them."""
    outbox = []

    # Handle fake send requests or data.
    def fake_send(to_address, subject, text_body, html_body=None):
        # Add this item to the list of results.
        outbox.append({"to": to_address, "subject": subject, "text": text_body, "html": html_body})
        # Send the result back to the code that called this function.
        return True

    # Load the tools needed in this file.
    import app.email_service as es
    monkeypatch.setattr(es, "send_email", fake_send)
    # Send the result back to the code that called this function.
    return outbox


# Handle get csrf requests or data.
def get_csrf(client, url):
    html = client.get(url).get_data(as_text=True)
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert m, f"no csrf token on {url}"
    # Send the result back to the code that called this function.
    return m.group(1)


# Handle extract reset path requests or data.
def extract_reset_path(email_text):
    m = re.search(r"http://127\.0\.0\.1:5000(/reset-password/[A-Za-z0-9_\-]+)", email_text)
    assert m, "no reset link in email"
    # Send the result back to the code that called this function.
    return m.group(1)
