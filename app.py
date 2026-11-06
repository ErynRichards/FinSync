# app.py
# The main Flask application. Run it with:  python app.py
# Then open http://127.0.0.1:5000 in your browser.

from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask import send_file

import config
from Images.income_vs_expense_dash import create_cash_flow_graph
from accounts import create_account
from backend.dashboard_service import build_dashboard_data
from db import DatabaseError, DuplicateEmailError
from db import get_connection
from email_service import send_reset_email
from monthly_calculations import calculate_last_7_days
from reset_tokens import check_token, create_token, use_token
from security import check_password, check_password_rules, hash_password, is_valid_email
from transactions import get_transactions, TransactionValidationError, delete_transaction, edit_transaction, \
    add_transaction, get_accounts, get_categories
from users import create_user, get_user_by_email, get_user_by_id
# DANIEL: Financial summary calculations
from dashboard_summary import get_summary

app = Flask(__name__)
app.secret_key = config.SECRET_KEY  # needed for sessions and flash messages


# MISHAYLE: Register the Budget Recommendation Flask routes
from budget_routes import budget_routes
app.register_blueprint(budget_routes)


if not app.secret_key:
    raise RuntimeError("SECRET_KEY is missing. Copy .env.example to .env and fill it in.")


# If the database is down, show a friendly page instead of crashing
@app.errorhandler(DatabaseError)
def database_error(error):
    return render_template("error.html", message=str(error)), 500


# ---------------------------------------------------------------------
# ERYN: Landing page from Phase 5.1 Frontend.zip
# ---------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ERYN: About and Features pages from Phase 5.1 Frontend.zip
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/features")
def features():
    return render_template("features.html")


# ---------------------------------------------------------------------
# MISHAYLE'S PART: REGISTRATION, LOGIN AND AUTHENTICATION BACKEND
# Uses Daniel's users.py (database) and security.py (password hashing).
# The HTML forms are Lashanya's part. Logout below is Reece's part.
# ---------------------------------------------------------------------

# MISHAYLE: Register a new FinSync user.
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    # MISHAYLE: Read the details submitted by the sign-up form.
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # MISHAYLE: Validate the name, email and password.
    errors = []
    if not full_name:
        errors.append("Full name is required.")
    if not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    errors += check_password_rules(password, confirm_password)

    if not errors:
        try:
            # MISHAYLE: Hash password before Daniel's function saves the user.

            # Create the new user
            user_id = create_user(
                full_name,
                email,
                hash_password(password)
            )

            # Automatically create one financial account
            create_account(
                user_id,
                "FinSync Account",
                "Personal",
                0.00,
                "ZAR"
            )

            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))

        except DuplicateEmailError:
            errors.append("An account with that email address already exists.")

    return render_template("signup.html", errors=errors,
                           full_name=full_name, email=email)


# MISHAYLE: Log in an existing user.
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        return render_template("login.html",
                               errors=["Please enter your email and password."],
                               email=email)

    # MISHAYLE: Find the user and compare the password to its saved hash.
    user = get_user_by_email(email)
    if user is None or not check_password(user["password_hash"], password):
        return render_template("login.html",
                               errors=["Invalid email or password."], email=email)

    # MISHAYLE: Clear an old session and remember the logged-in user's ID.
    session.clear()
    session["user_id"] = user["user_id"]
    return redirect(url_for("dashboard"))


# MISHAYLE: Only a logged-in user can open the dashboard.
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    # MISHAYLE: Confirm that the account still exists in the database.
    user = get_user_by_id(session["user_id"])
    if user is None:
        session.clear()
        flash("Please log in again.", "error")
        return redirect(url_for("login"))

    # Pass the logged-in user's transactions to Reece's dashboard functions.
    records = get_transactions(session["user_id"])
    prepared = []
    for record in records:
        item = dict(record)
        item["transaction_date"] = str(item["transaction_date"])
        item["description"] = item.get("description") or ""
        prepared.append(item)

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COALESCE(SUM(opening_balance), 0) AS total FROM accounts WHERE user_id = %s",
                           (session["user_id"],))
            opening_balance = cursor.fetchone()["total"]
    finally:
        connection.close()

    data = build_dashboard_data(prepared, opening_balance)

    # DANIEL: Get financial summary from the database
    summary = get_summary(session["user_id"])

    # MICHALYN: Values displayed in the dashboard cards
    dashboard_values = {
        "balance": summary["total_balance"],
        "income": summary["total_income"],
        "expenses": summary["total_expenses"],
        "savings": summary["savings"]
    }

    # Prepare transaction data for JavaScript
    dashboard_transactions = []

    for record in prepared:
        dashboard_transactions.append({
            "date": record["transaction_date"],
            "type": record["transaction_type"].capitalize(),
            "category": record.get("category_name") or "Other",
            "description": record["description"],
            "amount": float(record["amount"])
        })

    return render_template(
        "dashboard.html",
        user=user,
        data=data,
        dashboard_values=dashboard_values,
        dashboard_transactions=dashboard_transactions
    )


# Dashboard graph integration
@app.route("/dashboard/graph")
def dashboard_graph():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # Get transactions for the logged-in user
    transactions = get_transactions(session["user_id"])

    # MISHAYLE: Calculate the last 7 days
    daily_data = calculate_last_7_days(transactions)

    # LASHANYA: Create the Matplotlib graph
    graph = create_cash_flow_graph(daily_data)

    # Send the graph to the dashboard
    return send_file(graph, mimetype="image/png")


# transactions
@app.route("/transactions")
def transactions_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "transactions/dashboard.html",
        transactions=get_transactions(session["user_id"]),
        accounts=get_accounts(session["user_id"]),
        categories=get_categories()
    )


@app.route("/transactions/add", methods=["POST"])
def add_transaction_route():
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        add_transaction(session["user_id"], request.form)
        flash("Transaction added successfully.", "success")
    except TransactionValidationError as error:
        flash(str(error), "error")

    return redirect(url_for("transactions_page"))


@app.route("/transactions/<int:transaction_id>/edit", methods=["POST"])
def edit_transaction_route(transaction_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        updated = edit_transaction(
            session["user_id"], transaction_id, request.form
        )
        flash(
            "Transaction updated." if updated else "Transaction not found.",
            "success" if updated else "error"
        )
    except TransactionValidationError as error:
        flash(str(error), "error")

    return redirect(url_for("transactions_page"))


@app.route("/transactions/<int:transaction_id>/delete", methods=["POST"])
def delete_transaction_route(transaction_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    deleted = delete_transaction(session["user_id"], transaction_id)

    flash(
        "Transaction deleted." if deleted else "Transaction not found.",
        "success" if deleted else "error"
    )

    return redirect(url_for("transactions_page"))


# REECE'S PART: Logout (existing placeholder preserved).
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------
# Password reset (Daniel)
# ---------------------------------------------------------------------
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")

    email = request.form["email"].strip().lower()
    if not is_valid_email(email):
        error = "Please enter a valid email address."
        return render_template("forgot_password.html", error=error, email=email)

    user = get_user_by_email(email)
    if user is not None:
        token = create_token(user["user_id"])
        reset_link = url_for("reset_password", token=token, _external=True)
        send_reset_email(user["email"], user["first_name"], reset_link)

    # Same message whether or not the account exists, so nobody can find out who is registered
    message = "If an account exists for that email address, a password-reset link has been sent."
    return render_template("forgot_password.html", success=message)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # Check the link first (on both GET and POST)
    token_row, error_message = check_token(token)
    if token_row is None:
        return render_template("reset_invalid.html", message=error_message)

    if request.method == "GET":
        return render_template("reset_password.html", token=token)

    # Check the new password on the server (even if JavaScript already checked it)
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    errors = check_password_rules(password, confirm_password)
    if errors:
        return render_template("reset_password.html", token=token, errors=errors)

    # Save the new password and mark the link as used
    if not use_token(token_row, hash_password(password)):
        message = "This password-reset link has already been used."
        return render_template("reset_invalid.html", message=message)

    session.clear()
    flash("Your password has been reset. You can now log in with your new password.", "success")
    return redirect(url_for("login"))


# ERYN: Financial Summary

@app.route("/financial-summary")
def financial_summary_page():
    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))

    from financial_summary_service import get_user_financial_summary

    # Calculate the user's financial summary
    summary = get_user_financial_summary(session["user_id"])

    # Display the summary page
    return render_template("financial_summary.html", summary=summary)


# Transactions API for the original frontend JavaScript.
@app.route("/api/transactions", methods=["GET", "POST"])
def transactions_api():
    if "user_id" not in session:
        return jsonify({"error": "Please log in first."}), 401
    user_id = session["user_id"]
    if request.method == "GET":
        rows = get_transactions(user_id)
        return jsonify([{
            "id": row["transaction_id"], "type": row["transaction_type"].capitalize(),
            "amount": str(row["amount"]), "category": row["category_name"],
            "description": row["description"] or "", "date": str(row["transaction_date"])
        } for row in rows])

    values = request.get_json(silent=True) or {}
    try:
        accounts = get_accounts(user_id)
        if not accounts:
            return jsonify({"error": "Create a financial account before adding transactions."}), 400
        category = next((c for c in get_categories()
                         if c["category_name"] == values.get("category")
                         and c["category_type"] == str(values.get("type", "")).lower()), None)
        if category is None:
            return jsonify({"error": "Invalid category for this transaction type."}), 400
        payload = {
            "account_id": accounts[0]["account_id"],
            "category_id": category["category_id"],
            "transaction_type": str(values.get("type", "")).lower(),
            "amount": values.get("amount", ""),
            "transaction_date": values.get("date", ""),
            "description": values.get("description", "")
        }
        new_id = add_transaction(user_id, payload)
        return jsonify({"id": new_id, "type": values["type"],
                        "amount": str(values["amount"]), "category": category["category_name"],
                        "description": payload["description"], "date": payload["transaction_date"]}), 201
    except (TransactionValidationError, ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


@app.route("/api/transaction-options")
def transaction_options():
    if "user_id" not in session:
        return jsonify({"error": "Please log in first."}), 401
    return jsonify({"accounts": get_accounts(session["user_id"]), "categories": get_categories()})


@app.route("/accounts", methods=["GET", "POST"])
def accounts_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    if request.method == "POST":

        account_name = request.form.get("account_name", "").strip()
        account_type = request.form.get("account_type", "").strip()

        if not account_name or not account_type:
            return "Account name and type are required.", 400

        try:
            create_account(
                user_id,
                account_name,
                account_type
            )
        except DatabaseError as error:
            return str(error), 400

        return redirect(url_for("accounts_page"))

    accounts = get_accounts(user_id)

    return render_template(
        "accounts.html",
        accounts=accounts
    )


if __name__ == "__main__":
    app.run(debug=True)
