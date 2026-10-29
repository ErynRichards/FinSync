# FinSync – Authentication Module (Database, Flask & Password Reset)

**Owner of this part:** Daniel – *Database, Flask Setup & Password Reset Backend* · branch `feature/database_backend`  
**Team deadline:** 5 November 2026  
**Stack:** Python 3 · Flask · MySQL 8 · HTML/CSS/JavaScript

This project contains:

* the MySQL database and tables for the login module,
* the Flask application and its secure database connection,
* reusable functions to insert, retrieve and update users (for Mishayle),
* the complete password-reset backend (forgot password → email link → new password),
* simple placeholder pages so everything can be tested now. Teammates replace these pages with their own work.


## Responsibilities checklist (from *Login – responsibilities.docx*)

| Daniel's responsibility | Where it is done | Status |
|---|---|---|
| Create the MySQL database and users table | `database/01_create_database.sql`, `database/02_schema.sql` | Written. Must be run on your MySQL (Step 4) |
| Configure the Flask application and database connection | `app/__init__.py`, `app/config.py`, `app/db.py`, `.env.example` | Done |
| Functions to insert, retrieve and update user records | `app/users.py` (`create_user`, `get_user_by_email`, `get_user_by_id`, `email_exists`, `update_user`, `update_password_hash`) | Done + tested |
| Parameterised queries and correct error handling | `%s` placeholders everywhere; `DatabaseError` / `DuplicateEmailError` in `app/db.py` | Done + tested |
| Forgot Password Flask route | `GET/POST /forgot-password` in `app/routes/password_reset.py` | Done + tested |
| Secure, expiring, single-use reset tokens | `app/reset_tokens.py` + `password_reset_tokens` table | Done + tested |
| Email service for sending reset links | `app/email_service.py` + `templates/email/` | Code tested with a simulated SMTP server. **Real delivery needs your SMTP details (section 4)** |
| Verify tokens when users open the reset page | `GET /reset-password/<token>` | Done + tested |
| Update the password securely after validation | `POST /reset-password/<token>` (server validation, hashing, one transaction) | Done + tested |
| Reject expired or previously used links | `check_token()` + conditional `UPDATE` claim | Done + tested |
| Help connect the frontend forms to Flask | Working forms + field/route contract in section 7 | Done |
| Support Mishayle with database operations | `app/users.py` + `app/security.py`, notes in section 7 | Done |
| Resolve database and backend connectivity errors | `flask --app run check-db`, `/health/db`, `scripts/mysql_smoke_test.py`, Troubleshooting (section 8) | Done |

---

## 1. What is in the folder

```
FinSync/
├── run.py                        Start the app:  python run.py
├── requirements.txt              Python packages to install
├── .env.example                  Settings template. Copy it to .env (never commit .env)
├── database/
│   ├── 01_create_database.sql    Creates the "finsync" database + "finsync_app" user
│   └── 02_schema.sql             Creates the users and password_reset_tokens tables
├── app/
│   ├── __init__.py               Builds the Flask app (settings, routes, error pages)
│   ├── config.py                 Reads settings from .env
│   ├── db.py                     MySQL connection, transactions, error handling
│   ├── users.py                  create_user / get_user_by_email / update_user / ...
│   ├── security.py               Shared password hashing + password rules
│   ├── reset_tokens.py           Secure, expiring, single-use reset tokens
│   ├── email_service.py          Sends the reset email (SMTP) or prints it (console)
│   ├── csrf.py                   Protects forms against cross-site submissions
│   ├── routes/
│   │   ├── password_reset.py     /forgot-password and /reset-password/<token>   (Daniel)
│   │   ├── placeholders.py       /signup /login /dashboard /logout  (PLACEHOLDERS for Mishayle/Reece)
│   │   └── main.py               /  (landing placeholder for Eryn) and /health/db
│   ├── templates/                HTML pages + the email templates
│   └── static/                   css/style.css and js/validation.js
├── scripts/mysql_smoke_test.py   Tests the whole flow against YOUR real MySQL
└── tests/                        Automated tests (run with: pytest)
```

---

## 2. Windows setup, step by step

### Step 1: Install the tools (skip any you already have)

1. **Python 3.11 or newer**: https://www.python.org/downloads/
   During install, **tick "Add python.exe to PATH"**.
2. **MySQL 8 Community Server + MySQL Workbench**: https://dev.mysql.com/downloads/installer/
   Choose the "Developer Default" or "Server + Workbench" setup. Remember the **root password** you choose.

Check in a new **Command Prompt**:
```
python --version
```

### Step 2: Open the project folder in a terminal

Extract the ZIP, then in Command Prompt:
```
cd C:\path\to\FinSync
```
(Tip: in File Explorer, open the FinSync folder, click the address bar, type `cmd` and press Enter.)

### Step 3: Create a virtual environment and install packages

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
After `activate`, your prompt starts with `(venv)`. Activate it again every time you open a new terminal.

> **PowerShell users:** use `venv\Scripts\Activate.ps1`. If you get "running scripts is disabled", run
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or just use Command Prompt.

### Step 4: Create the database

**Option A: MySQL Workbench (easiest)**
1. Open `database\01_create_database.sql` in Notepad. Change `CHANGE_ME_Strong_Pass_123!` to your own password and save.
2. Open MySQL Workbench and connect to *Local instance* as **root**.
3. *File → Open SQL Script…* → `01_create_database.sql` → click the ⚡ (Execute) button.
4. *File → Open SQL Script…* → `02_schema.sql` → ⚡ Execute.
5. In the left panel, right-click *Schemas* → *Refresh All*. You should see `finsync` with tables `users` and `password_reset_tokens`.

**Option B: Command Prompt** (the MySQL `bin` folder must be on your PATH, or type the full path
`"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"`):
```
mysql -u root -p < database\01_create_database.sql
mysql -u root -p finsync < database\02_schema.sql
```
(`<` works in Command Prompt, **not** in PowerShell.)

### Step 5: Create your `.env` settings file

```
copy .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```
Open `.env` in Notepad and:
* paste the random value printed above into `SECRET_KEY=`
* set `DB_PASSWORD=` to the password you used in Step 4
* leave `MAIL_BACKEND=console` for now (emails will be printed in the terminal)

### Step 6: Check the database connection

```
flask --app run check-db
```
Expected: `OK: Connected to MySQL. users table has 0 row(s).`
If it fails, see **Troubleshooting** below.

### Step 7: Run the full flow against your real MySQL database

```
python scripts\mysql_smoke_test.py
```
Expected: every line says `[PASS]` and it ends with `11/11 checks passed.` The script creates a temporary user and deletes it again afterwards.

### Step 8: Start the website

```
python run.py
```
Open **http://127.0.0.1:5000** in your browser. Press `Ctrl+C` in the terminal to stop.

---

## 3. Testing the password reset by hand

1. Go to **/signup** and register (e.g. your own email, password `OldPassw0rd!`).
2. Log out, go to **/login** and click **Forgot password?**
3. Enter your email and click **Send reset link**. You will see the same message whether or not the email exists.
4. With `MAIL_BACKEND=console`, the email is printed in the **terminal running Flask**, between `=====` lines. Copy the link into your browser.
5. Enter a new password twice (e.g. `NewPassw0rd!`). You will be sent to the login page.
6. Check that the **old password fails** and the **new password works**.
7. Open the same link again. You should see *"already been used"*.

| Test | Expected result |
|---|---|
| Unknown email on Forgot Password | Same "If an account exists…" message, no email |
| Invalid email format | "Please enter a valid email address." |
| Made-up link `/reset-password/abc` | "This password-reset link is invalid" |
| Link used twice | "already been used" |
| Link older than 30 min | "has expired" |
| Passwords don't match / too weak | Error shown, link still usable |
| New password = old password | "must be different from your current password" |
| More than 3 requests in 15 min | Same message on screen, but no further emails |
| Two reset links, use the newer one | The older one stops working as well |

**To test expiry quickly:** in MySQL Workbench run
`UPDATE finsync.password_reset_tokens SET expires_at = '2000-01-01 00:00:00';`
then open the link again.

---

## 4. Sending real emails (Gmail example)

Email only reaches a real inbox once **you** configure it and test it. Until then, use the console mode.

1. Use a Gmail account for the project. Turn on **2-Step Verification**
   (Google Account → Security).
2. Create an **App Password**: Google Account → Security → *App passwords* (or search "App passwords"). Copy the 16-character password.
3. In `.env`:
   ```
   MAIL_BACKEND=smtp
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=1
   MAIL_USE_SSL=0
   MAIL_USERNAME=yourproject@gmail.com
   MAIL_PASSWORD=the16charapppassword
   MAIL_SENDER=yourproject@gmail.com
   ```
4. Restart `python run.py` and request a reset for an account registered with an email address you can open.
5. If the email does not arrive, check the Flask terminal for `Failed to send email via ...` (the error says why) and look in your spam folder.

Other providers (Outlook, Brevo, Mailtrap etc.) work the same way. Use their SMTP server, port and credentials.
**Production:** set `APP_BASE_URL=https://your-domain` and `SESSION_COOKIE_SECURE=1` so reset links use HTTPS.

---

## 5. Running the automated tests

```
pytest
```
Expected: `37 passed`. These tests use a stand-in (SQLite) database, so they run without MySQL. They exercise the real Flask routes, database functions and token logic. Use `scripts\mysql_smoke_test.py` (Step 7) to test against the real MySQL database.

---

## 6. How it works (short explanation)

**Database connection (`db.py`).** Each web request opens one MySQL connection (stored on Flask's `g`). It is closed automatically at the end of the request. All SQL uses `%s` placeholders, for example
`cursor.execute("SELECT ... WHERE email = %s", (email,))`. PyMySQL escapes the value itself, so SQL injection is not possible. MySQL errors are logged on the server, and the user only sees a friendly message. A duplicate email becomes `DuplicateEmailError`.

**Forgot password (`POST /forgot-password`):**
1. The email is checked and normalised (trimmed, lower-case).
2. If the user exists and has made fewer than 3 requests in 15 minutes, `secrets.token_urlsafe(32)` creates a random token.
3. Only the **SHA-256 hash** of the token is saved, with `expires_at` = now + 30 minutes.
4. The email contains `APP_BASE_URL/reset-password/<token>`.
5. The page always shows the same message, so nobody can find out which emails are registered.

**Reset (`/reset-password/<token>`):**
1. The token is hashed and looked up. It is rejected if it is unknown, used, expired, or the user no longer exists.
2. The new password is validated **on the server**. The same rules are also checked in JavaScript.
3. In **one database transaction**: the token is "claimed" with `UPDATE ... SET used_at = now WHERE used_at IS NULL AND expires_at > now`. Only one request can succeed, even if two arrive at the same moment. The new password hash is saved, and all the user's other unused links are cancelled.
4. The session is cleared and the user is redirected to the login page.

**Why hash the token?** If the database leaked, an attacker would only have hashes. Those cannot be turned back into working links.

**Extra protections:** CSRF tokens on every form, `Referrer-Policy: no-referrer` (stops the token in the URL leaking to other sites), HttpOnly session cookies, no passwords or tokens in logs (except the console email mode, which is for local testing only).

---

## 7. Integration notes for the group

This is the **shared Flask project structure**. Everyone works in this same folder structure on their own branch, so the files fit together when Eryn merges the pull requests.

### Where each person's files go

| Teammate · branch | Your files live here | What to keep so integration works |
|---|---|---|
| **Eryn** · `feature/landing_page` | `app/templates/index.html`, own CSS/JS in `app/static/css/` and `app/static/js/` | Sign-up / login buttons: `href="/signup"` and `href="/login"` (or `{{ url_for('auth.signup') }}` / `{{ url_for('auth.login') }}`). |
| **Lashanya** · `feature/login_signup` | `app/templates/login.html`, `app/templates/signup.html`, own CSS/JS in `app/static/` | Sign-up form: `method="post" action="/signup"`, fields `full_name`, `email`, `password`, `confirm_password`. Login form: `method="post" action="/login"`, fields `email`, `password`. Keep the **Forgot password?** link as `href="/forgot-password"`. |
| **Michalyn** · `feature/reset_password` | `app/templates/forgot_password.html`, `reset_password.html`, `reset_invalid.html`, `app/static/js/validation.js` | Forgot form: `POST /forgot-password`, field **`email`**. Reset form: post to the **same URL as the link** (`action="{{ url_for('password_reset.reset_password', token=token) }}"`), fields **`password`** and **`confirm_password`**. **Password rules:** 8+ characters, with uppercase, lowercase, a number and a special character (also enforced in `app/security.py`, so change both if the group changes them). For `fetch()`: send JSON plus the header `X-CSRFToken`. The response is `{"ok": true/false, "message": "...", "errors": [...]}`. |
| **Mishayle** · `feature/auth_backend` | Replace `app/routes/placeholders.py` (or add `app/routes/auth.py` and register it in `app/__init__.py`) | Hash with `app.security.hash_password()` and check with `verify_password()`. Using another method would break login after a reset. Save users with `app.users.create_user(full_name, email, password_hash)`, and catch `DuplicateEmailError` for "email already registered". Load users with `get_user_by_email()` / `get_user_by_id()`. Keep the blueprint name **`auth`** and the endpoints `login`, `signup`, `dashboard`. The session stores `session["user_id"]`. |
| **Reece** · `feature/logout_integration` | The `/logout` route (currently in `app/routes/placeholders.py`) | Use Mishayle's session approach. Logout is a POST form with a CSRF token (see `base.html`). After logout, `/dashboard` must redirect to login. |
| **Daniel** · `feature/database_backend` | `database/`, `app/__init__.py`, `config.py`, `db.py`, `users.py`, `security.py`, `reset_tokens.py`, `email_service.py`, `csrf.py`, `routes/password_reset.py`, `routes/main.py`, `tests/`, `scripts/` | Shared structure, database and password reset. |

### Rules for the HTML pages (frontend team)

* The pages are Flask *templates* in `app/templates/`. Plain HTML works fine. Only the small `{{ ... }}` parts are filled in by Flask.
* **Every `<form method="post">` must contain this line**, or Flask rejects it with "Your form session expired":
  `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`
* Link CSS and JS like this: `<link rel="stylesheet" href="/static/css/yourfile.css">` and `<script src="/static/js/yourfile.js"></script>`.
* To view your page, run `python run.py` and open it at `http://127.0.0.1:5000/...`. Opening the `.html` file directly by double-clicking won't fill in the Flask parts.
* `{% include "_errors.html" %}` shows the backend's error and success messages. Keep it (or your own version) on each form page.
* You don't have to use `base.html`. A page can be a complete HTML document of its own.

**Database note:** the `users` table follows the 4.5 database design (`first_name`, `last_name` …). The sign-up screen has one "Full Name" field, so `create_user()` splits it at the first space: "Mary Jane Smith" → `first_name="Mary"`, `last_name="Jane Smith"`. The finance tables (Accounts, Transactions, etc.) are not part of this module. They should reference `users.user_id`.

---

## 8. Troubleshooting

| Message | Meaning / fix |
|---|---|
| `SECRET_KEY is not set` | `.env` is missing or empty. Repeat Step 5. `.env` must be in the FinSync folder, next to `run.py`. |
| `Access denied for user 'finsync_app'@'localhost'` | `DB_PASSWORD` in `.env` doesn't match the password in `01_create_database.sql`, or that script wasn't run. |
| `Can't connect to MySQL server on 'localhost' (10061)` | MySQL isn't running. Open *Services* (Win+R → `services.msc`) → start **MySQL80**. |
| `Unknown database 'finsync'` | Run `01_create_database.sql`. |
| `Table 'finsync.users' doesn't exist` | Run `02_schema.sql`. |
| `cryptography package is required for sha256_password or caching_sha2_password` | `pip install -r requirements.txt` again with the venv active. |
| `ModuleNotFoundError: No module named 'flask'` / `'pymysql'` | The venv isn't active. Run `venv\Scripts\activate`. |
| `'mysql' is not recognized…` | Use Workbench (Option A) or the full path to `mysql.exe`. |
| "Your form session expired" (400) | The page was open too long or the form lacks the `csrf_token` field. Reload the page. |
| Email not arriving | Check the Flask terminal for `Failed to send email`. With Gmail, use an **App Password**, not your normal password. Check spam. |
| Port 5000 already in use | Close the other program, or change `port=5000` in `run.py` and `APP_BASE_URL` in `.env`. |

---

## 9. Uploading to GitHub (GitHub Desktop)

Daniel's branch is **`feature/database_backend`**. Never work directly on `main`.

1. In GitHub Desktop: *Current Branch* → select **`feature/database_backend`**.
2. Copy the contents of this FinSync folder (`app`, `database`, `scripts`, `tests`, `run.py`, `requirements.txt`, `.env.example`, `.gitignore`, `README.md`, `pytest.ini`) into the cloned FinSync repository folder.
   **Don't copy** `.env`, `venv` or `__pycache__`. If a file already exists there, check with the group before overwriting it.
3. Back in GitHub Desktop, check the *Changes* list. **`.env` must NOT appear** (it holds your passwords). `.gitignore` keeps it out.
4. Commit message, e.g. `Add shared Flask structure, MySQL schema and password-reset backend` → *Commit to feature/database_backend* → *Push origin*.
5. Tell the group it's pushed. **Eryn** opens and manages the pull request into `main`. **Reece** coordinates integration testing with Mishayle and Daniel.

**Teammates starting their part:** after this branch is merged into `main`, switch to your own branch and use *Branch → Update from main*. You'll then have the shared structure and can put your files where section 7 says. Each teammate makes their own `.env` from `.env.example` (README steps 3–5).

---

## 10. Test status (be honest in the group report)

**Tested automatically (37 tests, all passing):**
* creating, retrieving and updating users
* duplicate email rejection, password stored as a hash, SQL-injection input harmless
* the full forgot → email → reset → login flow, with the old password rejected afterwards
* invalid, expired, reused and deleted-user links rejected
* weak or mismatched passwords rejected while the link stays usable
* rate limit, older links cancelled after a reset, double-use race at function level
* CSRF, JSON responses, friendly page when the database is down
* SMTP code path with a simulated server
* the CLI connection check

The pages were also clicked through in a real browser (Chromium).

**Not tested yet (you need to do these on your PC):**
* the SQL scripts on a real MySQL 8 server. The automated tests use a SQLite stand-in for MySQL. Run Steps 4, 6 and 7. The smoke test checks the whole flow on real MySQL.
* real email delivery to an inbox. It needs real SMTP credentials (section 4).
* a true simultaneous double-submit on MySQL. It is protected by the conditional `UPDATE`, but was only tested sequentially.

**Known limitations / choices to confirm with the group:**
* Password rules (8+ characters with upper, lower, number, special) and the 30-minute expiry are my proposals. Both are easy to change.
* The rate limit is per account. There is no per-IP limit.
* Logging in elsewhere is not forced to end after a reset, because Flask's default sessions are stored in the browser. Mishayle could add this later if needed.
* The forgot-password page takes slightly longer when an email is actually sent. This is acceptable for a student project.
