"""
Smoke test against YOUR REAL MySQL database.

Run from the project folder (with the venv activated and .env filled in):
    python scripts/mysql_smoke_test.py

It creates a temporary user, runs the whole password-reset flow through
Flask, prints PASS/FAIL for each step, then deletes the temporary user
(its tokens are deleted automatically by ON DELETE CASCADE).
No email is sent - the email function is swapped for a capture.
"""
# Load the tools needed in this file.
import os
# Load the tools needed in this file.
import re
# Load the tools needed in this file.
import secrets
# Load the tools needed in this file.
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load the tools needed in this file.
import app.email_service as email_service  # noqa: E402
# Use functions and classes from another file.
from app import create_app  # noqa: E402
# Use functions and classes from another file.
from app.db import DatabaseError, check_connection, execute  # noqa: E402

# Keep these records for the next step.
results = []


# Handle step requests or data.
def step(name, ok, detail=""):
    # Add this item to the list of results.
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))


# Handle csrf requests or data.
def csrf(client, url):
    m = re.search(r'name="csrf_token" value="([^"]+)"', client.get(url).get_data(as_text=True))
    # Send the result back to the code that called this function.
    return m.group(1) if m else ""


# Handle main requests or data.
def main():
    outbox = []
    email_service.send_email = lambda to, subj, text, html=None: outbox.append(text) or True

    # Set up the Flask application or its routes.
    app = create_app({"MAIL_BACKEND": "console"})
    client = app.test_client()
    email = f"smoketest+{secrets.token_hex(4)}@example.com"
    old_pw, new_pw = "OldPassw0rd!", "NewPassw0rd!"

    # Use this resource and close it when finished.
    with app.app_context():
        ok, msg = check_connection()
        step("Connect to MySQL and read users table", ok, msg)
        # Check the condition before continuing.
        if not ok:
            # Send the result back to the code that called this function.
            return
        # Try the operation and handle any errors.
        try:
            # Run the database query using these values.
            execute("SELECT 1 FROM password_reset_tokens LIMIT 1")
            step("password_reset_tokens table exists", True)
        except DatabaseError as exc:
            step("password_reset_tokens table exists", False, str(exc))
            # Send the result back to the code that called this function.
            return

    # Try the operation and handle any errors.
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

        # Check login details and remember the logged in user.
        def login(pw):
            # Send the result back to the code that called this function.
            return client.post("/login", data={"email": email, "password": pw,
                                               "csrf_token": csrf(client, "/login")}).status_code
        step("Old password rejected", login(old_pw) == 401)
        step("New password accepted", login(new_pw) == 302)
        step("Used link rejected", client.get(path).status_code == 410)
        step("Made-up link rejected", client.get("/reset-password/not-a-real-token").status_code == 400)
    finally:
        # Use this resource and close it when finished.
        with app.app_context():
            # Run the database query using these values.
            execute("DELETE FROM users WHERE email = %s", (email,))
        print("Temporary user removed.")

    print(f"\n{sum(results)}/{len(results)} checks passed.")


# Check the condition before continuing.
if __name__ == "__main__":
    main()
    sys.exit(0 if results and all(results) else 1)
