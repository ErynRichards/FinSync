"""
Smoke test against YOUR REAL MySQL database.

Run from the project folder (with the venv activated and .env filled in):
    python scripts/mysql_smoke_test.py

It creates a temporary user, runs the whole password-reset flow through
Flask, prints PASS/FAIL for each step, then deletes the temporary user
(its tokens are deleted automatically by ON DELETE CASCADE).
No email is sent - the email function is swapped for a capture.
"""
import os
import re
import secrets
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.email_service as email_service  # noqa: E402
from app import create_app  # noqa: E402
from app.db import DatabaseError, check_connection, execute  # noqa: E402

results = []


def step(name, ok, detail=""):
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))


def csrf(client, url):
    m = re.search(r'name="csrf_token" value="([^"]+)"', client.get(url).get_data(as_text=True))
    return m.group(1) if m else ""


def main():
    outbox = []
    email_service.send_email = lambda to, subj, text, html=None: outbox.append(text) or True

    app = create_app({"MAIL_BACKEND": "console"})
    client = app.test_client()
    email = f"smoketest+{secrets.token_hex(4)}@example.com"
    old_pw, new_pw = "OldPassw0rd!", "NewPassw0rd!"

    with app.app_context():
        ok, msg = check_connection()
        step("Connect to MySQL and read users table", ok, msg)
        if not ok:
            return
        try:
            execute("SELECT 1 FROM password_reset_tokens LIMIT 1")
            step("password_reset_tokens table exists", True)
        except DatabaseError as exc:
            step("password_reset_tokens table exists", False, str(exc))
            return

    try:
        r = client.post("/signup", data={"full_name": "Smoke Test", "email": email,
                                         "password": old_pw, "confirm_password": old_pw,
                                         "csrf_token": csrf(client, "/signup")})
        step("Create user (insert)", r.status_code == 302, f"HTTP {r.status_code}")

        r = client.post("/signup", data={"full_name": "Smoke Test", "email": email,
                                         "password": old_pw, "confirm_password": old_pw,
                                         "csrf_token": csrf(client, "/signup")})
        step("Duplicate email rejected", r.status_code == 400 and "already exists" in r.get_data(as_text=True))

        r = client.post("/forgot-password", data={"email": email, "csrf_token": csrf(client, "/forgot-password")})
        step("Forgot-password request accepted", r.status_code == 200 and len(outbox) == 1)
        m = re.search(r"(/reset-password/[A-Za-z0-9_\-]+)", outbox[0] if outbox else "")
        path = m.group(1) if m else "/reset-password/missing"

        step("Reset link opens form", client.get(path).status_code == 200)
        r = client.post(path, data={"password": new_pw, "confirm_password": new_pw,
                                    "csrf_token": csrf(client, path)})
        step("Password reset succeeds", r.status_code == 302)

        def login(pw):
            return client.post("/login", data={"email": email, "password": pw,
                                               "csrf_token": csrf(client, "/login")}).status_code
        step("Old password rejected", login(old_pw) == 401)
        step("New password accepted", login(new_pw) == 302)
        step("Used link rejected", client.get(path).status_code == 410)
        step("Made-up link rejected", client.get("/reset-password/not-a-real-token").status_code == 400)
    finally:
        with app.app_context():
            execute("DELETE FROM users WHERE email = %s", (email,))
        print("Temporary user removed.")

    print(f"\n{sum(results)}/{len(results)} checks passed.")


if __name__ == "__main__":
    main()
    sys.exit(0 if results and all(results) else 1)
