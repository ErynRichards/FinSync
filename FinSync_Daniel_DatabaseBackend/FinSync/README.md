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
| `accounts.py` | Add and find a user's accounts, and work out an account's balance |
| `budget_database.py` | Budgets and the spending history for budget suggestions |
| `savings_database.py` | Create, get and update savings goals |
| `reports_database.py` | Transaction data for the Reports screen |
| `settings_database.py` | Profile, password hash and user preferences for Settings |
| `dashboard_summary.py` | Calculates the four dashboard summary cards |
| `transactions.py` | Save, list and delete a user's transactions, and total income and expenses |
| `security.py` | Password hashing and the password rules |
| `reset_tokens.py` | Creates and checks the password-reset tokens |
| `email_service.py` | Sends the reset email (or prints it in the terminal for testing) |
| `check_db.py` | Checks that the database connection works |
| `database/` | SQL scripts that create the database and all five tables (users, password_reset_tokens, accounts, categories, transactions) |
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
You should see five lines starting with `OK`, one for each table. The categories table starts with 5 rows.

**6. Start the app:**
```
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

---

## Database tables

| Table | What it stores | Links to |
|---|---|---|
| `users` | Registered users | – |
| `password_reset_tokens` | One row per "Forgot Password" request | `users` |
| `accounts` | Each user's financial accounts, with an opening balance and currency (default ZAR) | `users` |
| `categories` | How transactions are classified: Salary (income), Groceries, Transport, Entertainment and Utilities (expense) | – |
| `budgets` | Monthly budget amount per category | `users`, `categories` |
| `savings_goals` | Savings goals with target amount, amount saved, target date and status (active/completed) | `users` |
| `user_settings` | Theme (light/dark) and notification settings, one row per user | `users` |
| `transactions` | Income and expenses. `amount` is always positive and `transaction_type` says whether it is income or an expense | `accounts`, `categories` |

An account's current balance isn't stored. Work it out as:
**opening balance + total income − total expenses** for that account.

### Functions for the backend members (dashboard and transactions)

Every function takes the logged-in user's `user_id` (from `session["user_id"]`), so users only ever see their own data. Transactions are linked to a user through their account: **transaction → account → user**.

| Function | What it does |
|---|---|
| `create_account(user_id, name, type, opening_balance, currency)` | Adds an account and returns its id |
| `get_accounts(user_id)` | All the user's accounts |
| `get_account_balance(user_id, account_id)` | Opening balance + income − expenses |
| `get_categories()` | All categories, for the form's drop-down list |
| `add_transaction(user_id, account_id, category_id, description, amount, type, date)` | Checks the details and saves the transaction. Raises `DatabaseError` with a friendly message if the amount isn't more than 0, the type isn't income/expense, the account isn't the user's, or the category doesn't match the type |
| `get_transactions(user_id)` | All the user's transactions, newest first, with the account and category names |
| `get_account_transactions(user_id, account_id)` | Transactions for one account |
| `delete_transaction(user_id, transaction_id)` | Deletes it if it's the user's. Returns `False` otherwise |
| `get_totals(user_id, start_date, end_date)` | Total income and expenses between two dates, for the dashboard |

Example in a Flask route:
```python
from transactions import add_transaction
add_transaction(session["user_id"], request.form["account_id"], request.form["category_id"],
                request.form["description"], request.form["amount"],
                request.form["transaction_type"], request.form["transaction_date"])
```
Dates are text like `2026-11-03`. The form fields above are suggested names; agree on them with the frontend members.

### Dashboard summary cards

`get_summary(user_id)` in `dashboard_summary.py` returns the values for the four cards:

```python
from dashboard_summary import get_summary
summary = get_summary(session["user_id"])
# {"total_balance": 13749.5, "total_income": 15000.0, "total_expenses": 2750.75, "savings": 12249.25}
```

- **Total Balance** = opening balances of all the user's accounts + income − expenses
- **Total Income** = all income transactions
- **Total Expenses** = all expense transactions
- **Savings** = total income − total expenses

The values are plain numbers, so the JavaScript can format them as rand (R).

### Budgets, Savings Goals, Reports and Settings

| File | Function | What it returns / does |
|---|---|---|
| `budget_database.py` | `get_previous_three_months()` | Start and end date of the last 3 full months |
| | `get_category_spending_history(user_id, category_id, start_date, end_date)` | Expenses per month, e.g. `[{"month": "2026-08", "total": 1500.5}, ...]`. Months with no spending show 0 |
| | `create_budget(...)`, `get_budgets(user_id)` | Add and list budgets |
| `savings_database.py` | `create_savings_goal(user_id, goal_name, target_amount, target_date, category)` | Adds a goal, returns its id |
| | `get_savings_goals(user_id)`, `get_savings_goal(user_id, goal_id)` | The user's goals |
| | `update_goal_target(...)`, `update_saved_amount(...)`, `update_goal_status(...)` | Return `False` if the goal isn't the user's |
| `reports_database.py` | `get_report_transactions(user_id, start_date, end_date)` | Date, amount, type and category of each transaction |
| `settings_database.py` | `get_profile(user_id)`, `update_profile(...)` | Name, email and phone |
| | `get_password_hash(user_id)`, `update_password_hash(user_id, hash)` | For changing the password |
| | `get_preferences(user_id)`, `save_preferences(user_id, theme, budget_notifications, savings_notifications)` | Theme and notification settings |

Budget suggestion example (for Lashanya):
```python
from budget_database import get_previous_three_months, get_category_spending_history
start_date, end_date = get_previous_three_months()
history = get_category_spending_history(session["user_id"], category_id, start_date, end_date)
```

If you already ran `02_schema.sql` before, just run it again. It only adds the tables that are missing and doesn't touch existing data.

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
