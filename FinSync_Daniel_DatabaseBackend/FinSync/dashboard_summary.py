# dashboard_summary.py
# Calculates the values for the four financial summary cards on the dashboard.

from db import fetch_one


def get_total(sql, user_id):
    """Run a SUM query for the user. Returns 0 if there is nothing to add up."""
    total = fetch_one(sql, (user_id,))["total"]
    if total is None:
        return 0
    return float(total)


def get_summary(user_id):
    """Return Total Balance, Total Income, Total Expenses and Savings for a user."""
    opening_balances = get_total(
        "SELECT SUM(opening_balance) AS total FROM accounts WHERE user_id = %s", user_id)

    total_income = get_total(
        """SELECT SUM(t.amount) AS total
           FROM transactions t
           JOIN accounts a ON t.account_id = a.account_id
           WHERE a.user_id = %s AND t.transaction_type = 'income'""", user_id)

    total_expenses = get_total(
        """SELECT SUM(t.amount) AS total
           FROM transactions t
           JOIN accounts a ON t.account_id = a.account_id
           WHERE a.user_id = %s AND t.transaction_type = 'expense'""", user_id)

    # Savings is what's left of the income after expenses
    savings = total_income - total_expenses
    total_balance = opening_balances + savings

    return {
        "total_balance": round(total_balance, 2),
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "savings": round(savings, 2),
    }
