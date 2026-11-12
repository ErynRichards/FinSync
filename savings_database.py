# savings_database.py
# Database functions for savings goals.

# Use functions and classes from another file.
from db import DatabaseError, execute, fetch_all, fetch_one


# Handle create savings goal requests or data.
def create_savings_goal(user_id, goal_name, target_amount, target_date, category=None):
    """Add a new savings goal and return its id."""

    # Check the condition before continuing.
    if goal_name.strip() == "":

        # Stop the operation and report an error.
        raise DatabaseError("Goal name is required.")

    # Check the condition before continuing.
    if float(target_amount) <= 0:

        # Stop the operation and report an error.
        raise DatabaseError("Target amount must be more than 0.")

    sql = """INSERT INTO savings_goals (user_id, goal_name, category, target_amount, target_date)
             VALUES (%s, %s, %s, %s, %s)"""

    rows_changed, goal_id = execute(sql, (user_id, goal_name, category, target_amount, target_date))
    # Send the result back to the code that called this function.
    return goal_id


# Handle get savings goals requests or data.
def get_savings_goals(user_id):
    """Get all of a user's savings goals, closest target date first."""
    sql = "SELECT * FROM savings_goals WHERE user_id = %s ORDER BY target_date"

    # Send the result back to the code that called this function.
    return fetch_all(sql, (user_id,))


# Handle get savings goal requests or data.
def get_savings_goal(user_id, goal_id):
    """Get one goal. Returns None if it doesn't belong to this user."""
    sql = "SELECT * FROM savings_goals WHERE goal_id = %s AND user_id = %s"

    # Send the result back to the code that called this function.
    return fetch_one(sql, (goal_id, user_id))



# Handle update goal target requests or data.
def update_goal_target(user_id, goal_id, target_amount, target_date):
    """Update the target and automatically recalculate the status."""

    goal = get_savings_goal(user_id, goal_id)

    # Check the condition before continuing.
    if goal is None:

        # Send the result back to the code that called this function.
        return False

    # Check the condition before continuing.
    if float(target_amount) <= 0:

        # Stop the operation and report an error.
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

    # Run the database query using these values.
    execute(sql, (target_amount, target_date, status, goal_id, user_id))

    # Send the result back to the code that called this function.
    return True


# Handle update saved amount requests or data.
def update_saved_amount(user_id, goal_id, current_amount):
    """Update savings and automatically determine goal status."""

    goal = get_savings_goal(user_id, goal_id)

    # Check the condition before continuing.
    if goal is None:

        # Send the result back to the code that called this function.
        return False

    # Check the condition before continuing.
    if float(current_amount) < 0:

        # Stop the operation and report an error.
        raise DatabaseError("Saved amount cannot be negative.")

    # Save an amount for a calculation or database update.
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

    # Run the database query using these values.
    execute(sql, (current_amount, status, goal_id, user_id))

    # Send the result back to the code that called this function.
    return True


# Handle update goal status requests or data.
def update_goal_status(user_id, goal_id, status):
    """Update a goal's status for its owner only."""

    # Check the condition before continuing.
    if status not in ("active", "completed"):

        # Stop the operation and report an error.
        raise DatabaseError("Invalid goal status.")

    goal = get_savings_goal(user_id, goal_id)

    # Check the condition before continuing.
    if goal is None:

        # Send the result back to the code that called this function.
        return False

    sql = """
        UPDATE savings_goals
        SET status = %s
        WHERE goal_id = %s AND user_id = %s
    """

    # Run the database query using these values.
    execute(sql, (status, goal_id, user_id))

    # Send the result back to the code that called this function.
    return True

