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
    """Update the target and automatically recalculate the status."""

    goal = get_savings_goal(user_id, goal_id)

    if goal is None:
        return False

    if float(target_amount) <= 0:
        raise DatabaseError("Target amount must be greater than zero.")

    # Check whether the saved amount meets the new target.
    if float(goal["current_amount"]) >= float(target_amount):
        status = "completed"
    else:
        status = "active"

    sql = """
        UPDATE savings_goals
        SET target_amount = %s,
            target_date = %s,
            status = %s
        WHERE goal_id = %s AND user_id = %s
    """

    execute(sql, (target_amount, target_date, status, goal_id, user_id))
    return True


def update_saved_amount(user_id, goal_id, current_amount):
    """Update savings and automatically determine goal status."""

    goal = get_savings_goal(user_id, goal_id)

    if goal is None:
        return False

    if float(current_amount) < 0:
        raise DatabaseError("Saved amount cannot be negative.")

    target_amount = float(goal["target_amount"])

    # MISHAYLE: Automatically update the status.
    if float(current_amount) >= target_amount:
        status = "completed"
    else:
        status = "active"

    sql = """
        UPDATE savings_goals
        SET current_amount = %s,
            status = %s
        WHERE goal_id = %s AND user_id = %s
    """

    execute(sql, (current_amount, status, goal_id, user_id))
    return True


def update_goal_status(user_id, goal_id, status):
    """Update a goal's status for its owner only."""

    if status not in ("active", "completed"):
        raise DatabaseError("Invalid goal status.")

    goal = get_savings_goal(user_id, goal_id)

    if goal is None:
        return False

    sql = """
        UPDATE savings_goals
        SET status = %s
        WHERE goal_id = %s AND user_id = %s
    """

    execute(sql, (status, goal_id, user_id))
    return True

