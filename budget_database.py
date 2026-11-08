# budget_database.py
# Database functions for budgets and the spending history used for budget suggestions.

from datetime import date, timedelta

from db import DatabaseError, execute, fetch_all


def create_budget(user_id, category_id, budget_amount, start_date, end_date):
    """Add a budget for a category and return its id."""
    if float(budget_amount) <= 0:
        raise DatabaseError("Budget amount must be more than 0.")

    sql = """INSERT INTO budgets (user_id, category_id, budget_amount, start_date, end_date)
             VALUES (%s, %s, %s, %s, %s)"""
    rows_changed, budget_id = execute(sql, (user_id, category_id, budget_amount, start_date, end_date))
    return budget_id


def get_budgets(user_id):
    """Get all of a user's budgets with the category name."""
    sql = """SELECT b.*, c.category_name
             FROM budgets b
             JOIN categories c ON b.category_id = c.category_id
             WHERE b.user_id = %s
             ORDER BY b.start_date DESC"""
    return fetch_all(sql, (user_id,))


def get_previous_three_months():
    """Return the start and end date of the last three full months.
    e.g. on 6 Nov 2026 this gives 1 Aug 2026 to 31 Oct 2026."""
    first_of_this_month = date.today().replace(day=1)
    end_date = first_of_this_month - timedelta(days=1)

    start_date = first_of_this_month
    for i in range(3):
        start_date = (start_date - timedelta(days=1)).replace(day=1)

    return start_date, end_date


def get_category_spending_history(user_id, category_id, start_date, end_date):
    """Total expenses per month for one category between two dates.
    Returns a list like [{"month": "2026-08", "total": 1200.0}, ...]"""
    # Dates from a form come in as text, e.g. "2026-08-01"
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = date.fromisoformat(end_date)

    sql = """SELECT YEAR(t.transaction_date) AS year,
                    MONTH(t.transaction_date) AS month,
                    SUM(t.amount) AS total
             FROM transactions t
             JOIN accounts a ON t.account_id = a.account_id
             WHERE a.user_id = %s
             AND t.category_id = %s
             AND t.transaction_type = 'expense'
             AND t.transaction_date BETWEEN %s AND %s
             GROUP BY YEAR(t.transaction_date), MONTH(t.transaction_date)"""
    rows = fetch_all(sql, (user_id, category_id, start_date, end_date))

    # Put the totals in a dictionary, e.g. {"2026-08": 1200.0}
    totals = {}
    for row in rows:
        month_name = f"{row['year']}-{row['month']:02d}"
        totals[month_name] = float(row["total"])

    # Add every month in the range, using 0 for months with no spending
    history = []
    current = date(start_date.year, start_date.month, 1)
    while current <= end_date:
        month_name = current.strftime("%Y-%m")
        history.append({"month": month_name, "total": totals.get(month_name, 0.0)})
        current = (current + timedelta(days=32)).replace(day=1)  # go to the next month

    return history
