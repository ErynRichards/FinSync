# notification_database.py
# Budget-exceeded notification history, so each warning is only sent once a month.

from db import DatabaseError, DuplicateEmailError, execute, fetch_all, fetch_one


def notification_already_sent(user_id, budget_id, budget_month):
    """Return True if a notification was already sent for this budget and month."""
    sql = """SELECT notification_id FROM budget_notification_history
             WHERE user_id = %s AND budget_id = %s AND budget_month = %s"""
    return fetch_one(sql, (user_id, budget_id, budget_month)) is not None


def record_budget_notification(user_id, budget_id, budget_month):
    """Save a notification. Returns False if one was already sent this month."""
    if len(budget_month) != 7:
        raise DatabaseError("Budget month must look like 2026-11.")

    # The budget must belong to this user
    budget = fetch_one("SELECT budget_id FROM budgets WHERE budget_id = %s AND user_id = %s",
                       (budget_id, user_id))
    if budget is None:
        raise DatabaseError("That budget was not found.")

    sql = """INSERT INTO budget_notification_history (user_id, budget_id, budget_month)
             VALUES (%s, %s, %s)"""
    try:
        execute(sql, (user_id, budget_id, budget_month))
        return True
    except DuplicateEmailError:  # the unique key blocked a second notification
        return False


def get_notification_history(user_id):
    """Get a user's past budget notifications, newest first."""
    sql = """SELECT n.*, c.category_name, b.budget_amount
             FROM budget_notification_history n
             JOIN budgets b ON n.budget_id = b.budget_id
             JOIN categories c ON b.category_id = c.category_id
             WHERE n.user_id = %s
             ORDER BY n.created_at DESC"""
    return fetch_all(sql, (user_id,))
