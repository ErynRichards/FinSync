# app.py
# The main Flask application. Run it with:  python app.py
# Then open http://127.0.0.1:5000 in your browser.

# Use functions and classes from another file.
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
# Use functions and classes from another file.
from flask import send_file

# Load the tools needed in this file.
import config
# Use functions and classes from another file.

from Images.income_vs_expense_dash import create_cash_flow_graph
# Use functions and classes from another file.
from accounts import create_account

# Use functions and classes from another file.
from backend.dashboard_service import build_dashboard_data

# Use functions and classes from another file.
from db import DatabaseError, DuplicateEmailError

# Use functions and classes from another file.
from db import get_connection

# Use functions and classes from another file.
from email_service import send_reset_email

# Use functions and classes from another file.
from monthly_calculations import calculate_last_7_days

# Use functions and classes from another file.
from reset_tokens import check_token, create_token, use_token

# Use functions and classes from another file.
from security import check_password, check_password_rules, hash_password, is_valid_email

# Use functions and classes from another file.
from transactions import get_transactions, TransactionValidationError, delete_transaction, edit_transaction, \
    add_transaction, get_accounts, get_categories

# Use functions and classes from another file.
from users import create_user, get_user_by_email, get_user_by_id

# DANIEL: Financial summary calculations
from dashboard_summary import get_summary

# Set up the Flask application or its routes.
app = Flask(__name__)
app.secret_key = config.SECRET_KEY  # needed for sessions and flash messages


# MISHAYLE: Register Reports backend routes
from reports_routes import reports_bp
app.register_blueprint(reports_bp)


# MISHAYLE: Register Savings Goals routes
from savings_routes import savings_routes
app.register_blueprint(savings_routes)

# MISHAYLE: Register the Budget Recommendation Flask routes
from budget_routes import budget_routes
app.register_blueprint(budget_routes)

#settings/profile routes
from settings_routes import settings_bp
app.register_blueprint(settings_bp)

#notification routes
from notification_routes import notification_bp
app.register_blueprint(notification_bp)

# Check the condition before continuing.
if not app.secret_key:
    # Stop the operation and report an error.
    raise RuntimeError("SECRET_KEY is missing. Copy .env.example to .env and fill it in.")


# If the database is down, show a friendly page instead of crashing
@app.errorhandler(DatabaseError)
def database_error(error):
    # Send the result back to the code that called this function.
    return render_template("error.html", message=str(error)), 500


# ERYN: Landing page from Phase 5.1 Frontend.zip

# Handle index requests or data.
@app.route("/")
def index():
    # Send the result back to the code that called this function.
    return render_template("index.html")


# ERYN: About and Features pages from Phase 5.1 Frontend.zip
@app.route("/about")
def about():
    # Send the result back to the code that called this function.
    return render_template("about.html")


# Handle features requests or data.
@app.route("/features")
def features():
    # Send the result back to the code that called this function.
    return render_template("features.html")


# MISHAYLE'S PART: REGISTRATION, LOGIN AND AUTHENTICATION BACKEND
# Uses Daniel's users.py (database) and security.py (password hashing)
# The HTML forms are Lashanya's part. Logout below is Reece's part

# MISHAYLE: Register a new FinSync user.
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # Check the condition before continuing.
    if request.method == "GET":
        # Send the result back to the code that called this function.
        return render_template("signup.html")

    # MISHAYLE: Read the details submitted by the sign-up form.
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # MISHAYLE: Validate the name, email and password.
    errors = []
    # Check the condition before continuing.
    if not full_name:
        # Add this item to the list of results.
        errors.append("Full name is required.")

    # Check the condition before continuing.
    elif not all(char.isalpha() or char in " -'" for char in full_name):

        # Add this item to the list of results.
        errors.append("Name can only contain letters, spaces, hyphens and apostrophes.")

    # Check the condition before continuing.
    elif not any(char.isalpha() for char in full_name):

        # Add this item to the list of results.
        errors.append("Name must contain letters.")

    # Check the condition before continuing.
    if not is_valid_email(email):

        # Add this item to the list of results.
        errors.append("Please enter a valid email address.")
    errors += check_password_rules(password, confirm_password)

    # Check the condition before continuing.
    if not errors:
        # Try the operation and handle any errors.
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
            # Send the result back to the code that called this function.
            return redirect(url_for("login"))

        except DuplicateEmailError:
            # Add this item to the list of results.
            errors.append("An account with that email address already exists.")

    # Send the result back to the code that called this function.
    return render_template("signup.html", errors=errors,
                           full_name=full_name, email=email)


# MISHAYLE: Log in an existing user.
@app.route("/login", methods=["GET", "POST"])
def login():
    # Check the condition before continuing.
    if request.method == "GET":
        # Send the result back to the code that called this function.
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    # Check the condition before continuing.
    if not email or not password:
        # Send the result back to the code that called this function.
        return render_template("login.html",
                               errors=["Please enter your email and password."],
                               email=email)

    # MISHAYLE: Find the user and compare the password to its saved hash.
    user = get_user_by_email(email)

    # Check the condition before continuing.
    if user is None or not check_password(user["password_hash"], password):
        # Send the result back to the code that called this function.
        return render_template("login.html",
                               errors=["Invalid email or password."], email=email)

    # MISHAYLE: Clear an old session and remember the logged-in user's ID.
    session.clear()
    session["user_id"] = user["user_id"]
    # Send the result back to the code that called this function.
    return redirect(url_for("dashboard"))


# MISHAYLE: Only a logged-in user can open the dashboard.
@app.route("/dashboard")
def dashboard():
    # Check the condition before continuing.
    if "user_id" not in session:
        flash("Please log in first.", "error")
        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    # MISHAYLE: Confirm that the account still exists in the database.
    user = get_user_by_id(session["user_id"])
    # Check the condition before continuing.
    if user is None:
        session.clear()
        flash("Please log in again.", "error")
        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    # Pass the logged-in user's transactions to Reece's dashboard functions.
    records = get_transactions(session["user_id"])
    prepared = []
    # Go through each item one at a time.
    for record in records:
        item = dict(record)
        item["transaction_date"] = str(item["transaction_date"])
        item["description"] = item.get("description") or ""
        # Add this item to the list of results.
        prepared.append(item)

    # Get ready to run database queries.
    connection = get_connection()
    # Try the operation and handle any errors.
    try:
        # Use this resource and close it when finished.
        with connection.cursor() as cursor:
            # Run the database query using these values.
            cursor.execute("SELECT COALESCE(SUM(opening_balance), 0) AS total FROM accounts WHERE user_id = %s",
                           (session["user_id"],))
            # Save an amount for a calculation or database update.
            opening_balance = cursor.fetchone()["total"]
    finally:
        # Close this resource when finished.
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

    # Go through each item one at a time.
    for record in prepared:
        # Add this item to the list of results.
        dashboard_transactions.append({
            "date": record["transaction_date"],
            "type": record["transaction_type"].capitalize(),
            "category": record.get("category_name") or "Other",
            "description": record["description"],
            "amount": float(record["amount"])
        })

    # Send the result back to the code that called this function.
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

    # Check the condition before continuing.
    if "user_id" not in session:
        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    # Get transactions for the logged-in user
    transactions = get_transactions(session["user_id"])

    # MISHAYLE: Calculate the last 7 days
    daily_data = calculate_last_7_days(transactions)

    # LASHANYA: Create the Matplotlib graph
    graph = create_cash_flow_graph(daily_data)

    # Send the graph to the dashboard
    return send_file(graph, mimetype="image/png")


# MISHAYLE: Combined Reports page
@app.route("/reports")
def reports_page():
    # Check the condition before continuing.
    if "user_id" not in session:
        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    # Send the result back to the code that called this function.
    return render_template("reports/dashboard.html")


# transactions
@app.route("/transactions")
def transactions_page():
    # Check the condition before continuing.
    if "user_id" not in session:
        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    # Send the result back to the code that called this function.
    return render_template(
        "transactions/dashboard.html",
        transactions=get_transactions(session["user_id"]),
        accounts=get_accounts(session["user_id"]),
        categories=get_categories()
    )


# Handle add transaction route requests or data.
@app.route("/transactions/add", methods=["POST"])
def add_transaction_route():
    # Check the condition before continuing.
    if "user_id" not in session:
        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    # Try the operation and handle any errors.
    try:
        add_transaction(session["user_id"], request.form)
        flash("Transaction added successfully.", "success")
    except TransactionValidationError as error:
        flash(str(error), "error")

    # Send the result back to the code that called this function.
    return redirect(url_for("transactions_page"))


# Handle edit transaction route requests or data.
@app.route("/transactions/<int:transaction_id>/edit", methods=["POST"])
def edit_transaction_route(transaction_id):
    # Check the condition before continuing.
    if "user_id" not in session:
        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    # Try the operation and handle any errors.
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

    # Send the result back to the code that called this function.
    return redirect(url_for("transactions_page"))


# Handle delete transaction route requests or data.
@app.route("/transactions/<int:transaction_id>/delete", methods=["POST"])
def delete_transaction_route(transaction_id):
    # Check the condition before continuing.
    if "user_id" not in session:
        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    deleted = delete_transaction(session["user_id"], transaction_id)

    flash(
        "Transaction deleted." if deleted else "Transaction not found.",
        "success" if deleted else "error"
    )

    # Send the result back to the code that called this function.
    return redirect(url_for("transactions_page"))


# MISHAYLE: Display the Savings Goals dashboard
@app.route("/savings-goals")
def savings_goals_page():

    # Check the condition before continuing.
    if "user_id" not in session:
        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    # Send the result back to the code that called this function.
    return render_template("savings_goals/dashboard.html")


# MISHAYLE: Display the Create Savings Goal page
@app.route("/savings-goals/create")
def savings_goal_create_page():

    # Check the condition before continuing.
    if "user_id" not in session:
        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    # Send the result back to the code that called this function.
    return render_template("savings_goals/create.html")


# REECE'S PART: Logout (existing placeholder preserved).
# DANIEL: Logout now goes back to the landing page.
@app.route("/logout")
def logout():
    session.clear()
    # Send the result back to the code that called this function.
    return redirect(url_for("index"))


# Password reset (Daniel)
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    # Check the condition before continuing.
    if request.method == "GET":
        # Send the result back to the code that called this function.
        return render_template("forgot_password.html")

    email = request.form["email"].strip().lower()
    # Check the condition before continuing.
    if not is_valid_email(email):
        # Collect any input errors to show the user.
        error = "Please enter a valid email address."
        # Send the result back to the code that called this function.
        return render_template("forgot_password.html", error=error, email=email)

    user = get_user_by_email(email)
    # Check the condition before continuing.
    if user is not None:
        token = create_token(user["user_id"])
        reset_link = url_for("reset_password", token=token, _external=True)
        send_reset_email(user["email"], user["first_name"], reset_link)

    # Same message whether or not the account exists, so nobody can find out who is registered
    message = "If an account exists for that email address, a password-reset link has been sent."
    # Send the result back to the code that called this function.
    return render_template("forgot_password.html", success=message)


# Handle reset password requests or data.
@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # Check the link first (on both GET and POST)
    token_row, error_message = check_token(token)

    # Check the condition before continuing.
    if token_row is None:
        # Send the result back to the code that called this function.
        return render_template("reset_invalid.html", message=error_message)

    # Check the condition before continuing.
    if request.method == "GET":
        # Send the result back to the code that called this function.
        return render_template("reset_password.html", token=token)

    # Check the new password on the server (even if JavaScript already checked it)
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    # Collect any input errors to show the user.
    errors = check_password_rules(password, confirm_password)

    # Check the condition before continuing.
    if errors:
        # Send the result back to the code that called this function.
        return render_template("reset_password.html", token=token, errors=errors)

    # Save the new password and mark the link as used
    if not use_token(token_row, hash_password(password)):
        message = "This password-reset link has already been used."

        # Send the result back to the code that called this function.
        return render_template("reset_invalid.html", message=message)

    session.clear()
    flash("Your password has been reset. You can now log in with your new password.", "success")
    # Send the result back to the code that called this function.
    return redirect(url_for("login"))


# ERYN: Financial Summary

# Handle financial summary page requests or data.
@app.route("/financial-summary")
def financial_summary_page():
    # Make sure the user is logged in
    if "user_id" not in session:
        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    # Use functions and classes from another file.
    from financial_summary_service import get_user_financial_summary

    # Calculate the user's financial summary
    summary = get_user_financial_summary(session["user_id"])

    # Display the summary page
    return render_template("financial_summary.html", summary=summary)


# Transactions API for the original frontend JavaScript.
@app.route("/api/transactions", methods=["GET", "POST"])
def transactions_api():

    # Check the condition before continuing.
    if "user_id" not in session:

        # Send the result back to the code that called this function.
        return jsonify({"error": "Please log in first."}), 401

    # Keep the ID of the record being used.
    user_id = session["user_id"]

    # Check the condition before continuing.
    if request.method == "GET":
        # Keep these records for the next step.
        rows = get_transactions(user_id)
        # Send the result back to the code that called this function.
        return jsonify([{
            "id": row["transaction_id"], "type": row["transaction_type"].capitalize(),
            "amount": str(row["amount"]), "category": row["category_name"],
            "description": row["description"] or "", "date": str(row["transaction_date"])
        } for row in rows])

    values = request.get_json(silent=True) or {}
    # Try the operation and handle any errors.
    try:
        accounts = get_accounts(user_id)
        # Check the condition before continuing.
        if not accounts:
            # Send the result back to the code that called this function.
            return jsonify({"error": "Create a financial account before adding transactions."}), 400
        category = next((c for c in get_categories()
                         if c["category_name"] == values.get("category")
                         and c["category_type"] == str(values.get("type", "")).lower()), None)
        # Check the condition before continuing.
        if category is None:
            # Send the result back to the code that called this function.
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
        # Send the result back to the code that called this function.
        return jsonify({"id": new_id, "type": values["type"],
                        "amount": str(values["amount"]), "category": category["category_name"],
                        "description": payload["description"], "date": payload["transaction_date"]}), 201
    except (TransactionValidationError, ValueError, TypeError) as error:
        # Send the result back to the code that called this function.
        return jsonify({"error": str(error)}), 400


# Handle transaction options requests or data.
@app.route("/api/transaction-options")
def transaction_options():
    # Check the condition before continuing.
    if "user_id" not in session:
        # Send the result back to the code that called this function.
        return jsonify({"error": "Please log in first."}), 401
    # Send the result back to the code that called this function.
    return jsonify({"accounts": get_accounts(session["user_id"]), "categories": get_categories()})


# Handle accounts page requests or data.
@app.route("/accounts", methods=["GET", "POST"])
def accounts_page():
    # Check the condition before continuing.
    if "user_id" not in session:
        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    # Keep the ID of the record being used.
    user_id = session["user_id"]

    # Check the condition before continuing.
    if request.method == "POST":

        account_name = request.form.get("account_name", "").strip()
        account_type = request.form.get("account_type", "").strip()

        # Check the condition before continuing.
        if not account_name or not account_type:
            # Send the result back to the code that called this function.
            return "Account name and type are required.", 400

        # Try the operation and handle any errors.
        try:
            create_account(
                user_id,
                account_name,
                account_type
            )
        except DatabaseError as error:
            # Send the result back to the code that called this function.
            return str(error), 400

        # Send the result back to the code that called this function.
        return redirect(url_for("accounts_page"))

    accounts = get_accounts(user_id)

    # Send the result back to the code that called this function.
    return render_template(
        "accounts.html",
        accounts=accounts
    )


# MISHAYLE: Main Budgets dashboard using Michalyn's frontend.
@app.route('/budgets')
def budgets_page():
    # Check the condition before continuing.
    if 'user_id' not in session:
        # Send the result back to the code that called this function.
        return redirect(url_for('login'))
    user = get_user_by_id(session['user_id'])

    # Check the condition before continuing.
    if user is None:
        session.clear()
        # Send the result back to the code that called this function.
        return redirect(url_for('login'))
    # Use functions and classes from another file.
    from datetime import date
    period = request.args.get('period', date.today().strftime('%Y-%m'))
    # Send the result back to the code that called this function.
    return render_template('budgets/dashboard.html', user=user, selected_period=period)


# MISHAYLE: Display Eryn's Create Budget form
@app.route("/budgets/create")
def create_budget_page():
    # Check the condition before continuing.
    if "user_id" not in session:
        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    # Send the result back to the code that called this function.
    return render_template("budgets/createBudget.html")



# Check the condition before continuing.
if __name__ == "__main__":
    app.run(debug=True)
