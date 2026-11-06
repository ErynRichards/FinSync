# reports_database.py
# Gets the transaction data needed for the Reports screen.

from db import fetch_all


def get_report_transactions(user_id, start_date, end_date):
    """Get a user's transactions between two dates, oldest first.
    Each row has the date, amount, type and category name."""
    sql = """SELECT t.transaction_date, t.amount, t.transaction_type, c.category_name
             FROM transactions t
             JOIN accounts a ON t.account_id = a.account_id
             JOIN categories c ON t.category_id = c.category_id
             WHERE a.user_id = %s
             AND t.transaction_date BETWEEN %s AND %s
             ORDER BY t.transaction_date"""
    rows = fetch_all(sql, (user_id, start_date, end_date))

    # Change the amounts to normal numbers so they are easy to use in calculations
    for row in rows:
        row["amount"] = float(row["amount"])
    return rows
