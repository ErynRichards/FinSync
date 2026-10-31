# FinSync – Database, Flask Setup & Password Reset

**Daniel** · branch `feature/database_backend` · deadline 5 November 2026

This part of FinSync contains:
- the MySQL database and tables,
- the Flask app and its connection to MySQL,
- functions to add, find and update users,
- the full password reset: forgot password → email link → choose a new password.

The sign-up, login, dashboard and landing pages are simple **placeholders**, so the
password reset can be tested now. Teammates replace them with their own work.

---

## Files

| File | What it does |
|---|---|
| `app.py` | The Flask app and all the routes (pages). Start it with `python app.py` |
| `config.py` | Reads the settings from `.env` |
| `db.py` | Connects to MySQL and runs queries |
| `users.py` | Add, find and update users |
| `security.py` | Password hashing and the password rules |
| `reset_tokens.py` | Creates and checks the password-reset tokens |
| `email_service.py` | Sends the reset email (or prints it in the terminal for testing) |
| `check_db.py` | Checks that the database connection works |
| `database/` | SQL scripts that create the database and tables |
| `templates/` | The HTML pages |
| `static/` | CSS and JavaScript |
| `.env.example` | Settings template. Copy it to `.env` and fill it in |

---

## Setup on Windows

**1. Install** Python 3 (tick *"Add python.exe to PATH"*) and MySQL 8 Community Server with MySQL Workbench.

**2. Open Command Prompt in the FinSync folder** and install the packages:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**3. Create the database** in MySQL Workbench (logged in as root):
1. Open `database\01_create_database.sql`, change the password `CHANGE_ME_Strong_Pass_123!` to your own, and click ⚡ Execute.
2. Open `database\02_schema.sql` and click ⚡ Execute.

**4. Create your `.env` file:**
```
copy .env.example .env
```
Open `.env` in Notepad. Put any long random text in `SECRET_KEY` and put your MySQL password from step 3 in `DB_PASSWORD`.

**5. Check the database connection:**
```
python check_db.py
```
You should see two lines starting with `OK`.

**6. Start the app:**
```
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

---

## Testing the password reset

1. Sign up at `/signup`, then log out.
2. On the login page, click **Forgot password?** and enter your email.
3. The email is printed in the terminal where `app.py` is running. Copy the link into your browser.
4. Enter a new password twice. You are sent back to the login page.
5. Check that the old password no longer works and the new one does.

| Test | Expected result |
|---|---|
| Email that isn't registered | Same "If an account exists…" message |
| Invalid email format | "Please enter a valid email address." |
| Made-up link, e.g. `/reset-password/abc` | "This password-reset link is invalid" |
| Using the same link twice | "already been used" |
| Link older than 30 minutes | "has expired" |
| Passwords don't match or are too weak | Error shown, the link still works |

To test expiry quickly, run this in Workbench and then open the link again:
`UPDATE finsync.password_reset_tokens SET expires_at = '2000-01-01 00:00:00';`

---

## Sending real emails (Gmail)

1. Turn on 2-Step Verification on the Gmail account and create an **App Password**.
2. In `.env`, set `MAIL_BACKEND=smtp`, then fill in `MAIL_USERNAME` (the Gmail address) and `MAIL_PASSWORD` (the App Password).
3. Restart `python app.py`.

---

## How the password reset works

1. **Forgot password:** the user enters their email. If the account exists, `create_token()` makes a random token with Python's `secrets` module. Only a SHA-256 **hash** of the token is saved in `password_reset_tokens`, together with an expiry time. The link with the real token is emailed. The page shows the same message either way, so nobody can find out who is registered.
2. **Opening the link:** `check_token()` hashes the token from the link and looks it up. It rejects the link if it is unknown, already used or expired.
3. **New password:** the password is checked on the server. `use_token()` then marks the token as used, saves the new password hash and cancels the user's other reset links. All three happen in **one transaction**, so either everything saves or nothing does.

All SQL uses `%s` placeholders, which protects against SQL injection. Passwords are stored only as hashes.

---

## For the rest of the group

| Who | What to keep |
|---|---|
| **Mishayle** | Use `hash_password()` and `check_password()` from `security.py`, and `create_user()`, `get_user_by_email()` and `get_user_by_id()` from `users.py`. Replace the placeholder signup/login/dashboard routes in `app.py`. The login stores `session["user_id"]`. |
| **Reece** | Replace the placeholder `/logout` route in `app.py`. |
| **Lashanya** | Sign-up fields: `full_name`, `email`, `password`, `confirm_password`. Login fields: `email`, `password`. Keep the **Forgot password?** link (`/forgot-password`). |
| **Michalyn** | Forgot form field: `email`. Reset form fields: `password`, `confirm_password`. You can restyle `forgot_password.html`, `reset_password.html` and `reset_invalid.html`, and replace `static/js/validation.js`. |
| **Eryn** | Replace `templates/index.html`. Link to `/signup` and `/login`. |

---

## Troubleshooting

| Message | Fix |
|---|---|
| `SECRET_KEY is missing` | Create `.env` (step 4) in the same folder as `app.py`. |
| `Access denied for user 'finsync_app'` | `DB_PASSWORD` in `.env` doesn't match the password in `01_create_database.sql`. |
| `Can't connect to MySQL server` | MySQL isn't running. Start **MySQL80** in Windows *Services*. |
| `Unknown database 'finsync'` or `Table ... doesn't exist` | Run the two SQL scripts again (step 3). |
| `No module named 'flask'` | Activate the venv: `venv\Scripts\activate`. |
| `cryptography package is required` | Run `pip install -r requirements.txt` again. |
| Email not arriving | Check the terminal for `Could not send email`. Use a Gmail **App Password**, not your normal password. |
