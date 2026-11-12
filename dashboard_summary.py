# dashboard_summary.py
# Calculates the values for the four financial summary cards on the dashboard.

# Use functions and classes from another file.
from db import fetch_one


# Handle get total requests or data.
def get_total(sql, user_id):
    """Run a SUM query for the user. Returns 0 if there is nothing to add up."""

    # Save an amount for a calculation or database update.
    total = fetch_one(sql, (user_id,))["total"]

    # Check the condition before continuing.
    if total is None:

        # Send the result back to the code that called this function.
        return 0

    # Send the result back to the code that called this function.
    return float(total)


# Handle get summary requests or data.
def get_summary(user_id):
    """Return Total Balance, Total Income, Total Expenses and Savings for a user."""
    # Save an amount for a calculation or database update.
    opening_balances = get_total(
        "SELECT SUM(opening_balance) AS total FROM accounts WHERE user_id = %s", user_id)

    # Save an amount for a calculation or database update.
    total_income = get_total(
        """SELECT SUM(t.amount) AS total
           FROM transactions t
           JOIN accounts a ON t.account_id = a.account_id
           WHERE a.user_id = %s AND t.transaction_type = 'income'""", user_id)

    # Save an amount for a calculation or database update.
    total_expenses = get_total(
        """SELECT SUM(t.amount) AS total
           FROM transactions t
           JOIN accounts a ON t.account_id = a.account_id
           WHERE a.user_id = %s AND t.transaction_type = 'expense'""", user_id)

    # Savings is what's left of the income after expenses
    savings = total_income - total_expenses
    # Save an amount for a calculation or database update.
    total_balance = opening_balances + savings

    # Send the result back to the code that called this function.
    return {
        "total_balance": round(total_balance, 2),
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "savings": round(savings, 2),
    }
