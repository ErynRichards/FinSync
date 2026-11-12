"""MISHAYLE: integrate Reece's budget checker, Daniel's schema and Settings preferences."""
# Use functions and classes from another file.
from datetime import date

# Use functions and classes from another file.
from calendar import monthrange

# Use functions and classes from another file.
from decimal import Decimal

# Use functions and classes from another file.
from flask import Blueprint, jsonify, session, request

# Use functions and classes from another file.
from db import fetch_all, fetch_one, execute, DatabaseError, DuplicateEmailError

# Use functions and classes from another file.
from backend.transactions.budget_notification import check_budget_notification

# Use functions and classes from another file.
from settings_database import get_preferences

notification_bp = Blueprint("notification_bp", __name__)

# Handle budget warnings requests or data.
@notification_bp.get("/api/notifications/budgets")
def budget_warnings():

    # Keep the ID of the record being used.
    user_id = session.get("user_id")

    # Check the condition before continuing.
    if not user_id:

        # Send the result back to the code that called this function.
        return jsonify({"error": "Please log in first"}), 401
    month = request.args.get("month", date.today().strftime("%Y-%m"))

    # Try the operation and handle any errors.
    try:
        first = date.fromisoformat(month + "-01")

        # Check the condition before continuing.
        if first.strftime("%Y-%m") != month:

            # Stop the operation and report an error.
            raise ValueError
        last = date(first.year, first.month, monthrange(first.year, first.month)[1])
    except ValueError:

        # Send the result back to the code that called this function.
        return jsonify({"error": "Month must be YYYY-MM"}), 400

    # Try the operation and handle any errors.
    try:
        # Check the condition before continuing.
        if not get_preferences(user_id)["budget_notifications"]:

            # Send the result back to the code that called this function.
            return jsonify({"notifications": []})

        # Save an amount for a calculation or database update.
        budgets = fetch_all("""SELECT b.budget_id, b.category_id, b.budget_amount,
                                  b.start_date, b.end_date, c.category_name
                           FROM budgets b JOIN categories c ON c.category_id=b.category_id
                           WHERE b.user_id=%s AND b.start_date<=%s AND b.end_date>=%s""",
                            (user_id, last, first))

        # Save an amount for a calculation or database update.
        totals = fetch_all("""SELECT t.category_id, COALESCE(SUM(t.amount),0) AS spent
                             FROM transactions t JOIN accounts a ON a.account_id=t.account_id
                             WHERE a.user_id=%s AND t.transaction_type='expense'
                               AND t.transaction_date BETWEEN %s AND %s
                             GROUP BY t.category_id""", (user_id, first, last))

        spending = {int(x["category_id"]): Decimal(str(x["spent"])) for x in totals}
        alerts = []

        # Go through each item one at a time.
        for budget in budgets:
            # Save an amount for a calculation or database update.

            amount = Decimal(str(budget["budget_amount"]))
            spent = spending.get(int(budget["category_id"]), Decimal("0"))

            # Check the condition before continuing.
            if spent <= amount:
                continue

            bid = budget["budget_id"]
            exists = fetch_one("""SELECT notification_id FROM budget_notification_history
                                  WHERE user_id=%s AND budget_id=%s AND budget_month=%s""",
                               (user_id, bid, month))

            # Check the condition before continuing.
            if exists:
                continue
            # First discovery of an overrun: Reece's checker decides if eligible.
            # This is NOT a historical pre-transaction spending value.
            result = check_budget_notification(user_id, bid, month, amount,
                                               amount, spent, notifications_enabled=True)

            # Check the condition before continuing.
            if not result["should_notify"]:
                continue
            # Try the operation and handle any errors.
            try:
                # Run the database query using these values.
                execute("""INSERT INTO budget_notification_history
                           (user_id, budget_id, budget_month) VALUES (%s,%s,%s)""",
                        (user_id, bid, month))
            except DuplicateEmailError:
                continue  # UNIQUE constraint prevents duplicate warnings

            # Add this item to the list of results.
            alerts.append({"budget_id": bid, "category": budget["category_name"],
                           "monthlyBudget": float(amount), "totalExpenses": float(spent),
                           "exceededBy": float(spent - amount)})

        # Send the result back to the code that called this function.
        return jsonify({"notifications": alerts})
    except DatabaseError:

        # Send the result back to the code that called this function.
        return jsonify({"error": "Unable to check budget notifications"}), 500
