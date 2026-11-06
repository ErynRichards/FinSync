# savings_database.py
# Database functions for savings goals.

from db import DatabaseError, execute, fetch_all, fetch_one


def create_savings_goal(user_id, goal_name, target_amount, target_date, category=None):
    """Add a new savings goal and return its id."""
    if goal_name.strip() == "":
        raise DatabaseError("Goal name is required.")
    if float(target_amount) <= 0:
        raise DatabaseError("Target amount must be more than 0.")

    sql = """INSERT INTO savings_goals (user_id, goal_name, category, target_amount, target_date)
             VALUES (%s, %s, %s, %s, %s)"""
    rows_changed, goal_id = execute(sql, (user_id, goal_name, category, target_amount, target_date))
    return goal_id


def get_savings_goals(user_id):
    """Get all of a user's savings goals, closest target date first."""
    sql = "SELECT * FROM savings_goals WHERE user_id = %s ORDER BY target_date"
    return fetch_all(sql, (user_id,))


def get_savings_goal(user_id, goal_id):
    """Get one goal. Returns None if it doesn't belong to this user."""
    sql = "SELECT * FROM savings_goals WHERE goal_id = %s AND user_id = %s"
    return fetch_one(sql, (goal_id, user_id))


def update_goal_target(user_id, goal_id, target_amount, target_date):
    """Change a goal's target amount and date. Returns False if the goal isn't the user's."""
    if get_savings_goal(user_id, goal_id) is None:
        return False
    if float(target_amount) <= 0:
        raise DatabaseError("Target amount must be more than 0.")

    sql = "UPDATE savings_goals SET target_amount = %s, target_date = %s WHERE goal_id = %s"
    execute(sql, (target_amount, target_date, goal_id))
    return True


def update_saved_amount(user_id, goal_id, current_amount):
    """Change how much has been saved so far. Returns False if the goal isn't the user's."""
    if get_savings_goal(user_id, goal_id) is None:
        return False
    if float(current_amount) < 0:
        raise DatabaseError("Saved amount can't be negative.")

    sql = "UPDATE savings_goals SET current_amount = %s WHERE goal_id = %s"
    execute(sql, (current_amount, goal_id))
    return True


def update_goal_status(user_id, goal_id, status):
    """Set a goal to 'active' or 'completed'. Returns False if the goal isn't the user's."""
    if status != "active" and status != "completed":
        raise DatabaseError("Status must be active or completed.")
    if get_savings_goal(user_id, goal_id) is None:
        return False

    execute("UPDATE savings_goals SET status = %s WHERE goal_id = %s", (status, goal_id))
    return True
