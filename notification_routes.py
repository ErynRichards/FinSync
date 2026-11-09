"""MISHAYLE: integrate Reece's budget checker, Daniel's schema and Settings preferences."""
from datetime import date
from calendar import monthrange
from decimal import Decimal
from flask import Blueprint, jsonify, session, request
from db import fetch_all, fetch_one, execute, DatabaseError, DuplicateEmailError
from backend.transactions.budget_notification import check_budget_notification
from settings_database import get_preferences

notification_bp = Blueprint("notification_bp", __name__)

@notification_bp.get("/api/notifications/budgets")
def budget_warnings():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Please log in first"}), 401
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    try:
        first = date.fromisoformat(month + "-01")
        if first.strftime("%Y-%m") != month:
            raise ValueError
        last = date(first.year, first.month, monthrange(first.year, first.month)[1])
    except ValueError:
        return jsonify({"error": "Month must be YYYY-MM"}), 400
    try:
        if not get_preferences(user_id)["budget_notifications"]:
            return jsonify({"notifications": []})
        budgets = fetch_all("""SELECT b.budget_id, b.category_id, b.budget_amount,
                                  b.start_date, b.end_date, c.category_name
                           FROM budgets b JOIN categories c ON c.category_id=b.category_id
                           WHERE b.user_id=%s AND b.start_date<=%s AND b.end_date>=%s""",
                            (user_id, last, first))
        totals = fetch_all("""SELECT t.category_id, COALESCE(SUM(t.amount),0) AS spent
                             FROM transactions t JOIN accounts a ON a.account_id=t.account_id
                             WHERE a.user_id=%s AND t.transaction_type='expense'
                               AND t.transaction_date BETWEEN %s AND %s
                             GROUP BY t.category_id""", (user_id, first, last))
        spending = {int(x["category_id"]): Decimal(str(x["spent"])) for x in totals}
        alerts = []
        for budget in budgets:
            amount = Decimal(str(budget["budget_amount"]))
            spent = spending.get(int(budget["category_id"]), Decimal("0"))
            if spent <= amount:
                continue
            bid = budget["budget_id"]
            exists = fetch_one("""SELECT notification_id FROM budget_notification_history
                                  WHERE user_id=%s AND budget_id=%s AND budget_month=%s""",
                               (user_id, bid, month))
            if exists:
                continue
            # First discovery of an overrun: Reece's checker decides if eligible.
            # This is NOT a historical pre-transaction spending value.
            result = check_budget_notification(user_id, bid, month, amount,
                                               amount, spent, notifications_enabled=True)
            if not result["should_notify"]:
                continue
            try:
                execute("""INSERT INTO budget_notification_history
                           (user_id, budget_id, budget_month) VALUES (%s,%s,%s)""",
                        (user_id, bid, month))
            except DuplicateEmailError:
                continue  # UNIQUE constraint prevents duplicate warnings
            alerts.append({"budget_id": bid, "category": budget["category_name"],
                           "monthlyBudget": float(amount), "totalExpenses": float(spent),
                           "exceededBy": float(spent - amount)})
        return jsonify({"notifications": alerts})
    except DatabaseError:
        return jsonify({"error": "Unable to check budget notifications"}), 500
