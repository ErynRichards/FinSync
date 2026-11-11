
from flask import Blueprint, request, jsonify, session
from datetime import datetime, date
from decimal import Decimal

from savings_database import (
    create_savings_goal,
    get_savings_goals,
    get_savings_goal,
    update_saved_amount,
    update_goal_status
)

from goal_calculations import (
    calculate_progress,
    calculate_total_target,
    calculate_total_saved,
    calculate_average_progress
)

# REECE: Monthly savings recommendation
from monthly_savings_service import calculate_monthly_savings
savings_routes = Blueprint("savings_routes", __name__)

# MISHAYLE: Convert database goals into frontend data.
def format_goal(goal):
    target = float(goal["target_amount"])
    saved = float(goal["current_amount"])

    # REECE: Calculate recommended monthly savings.
    recommendation = calculate_monthly_savings(
        target,
        saved,
        goal["target_date"]
    )

    return {
        "id": goal["goal_id"],
        "goal_name": goal["goal_name"],
        "category": goal["category"],
        "target_amount": target,
        "saved_amount": saved,
        "target_date": str(goal["target_date"]),
        "status": goal["status"],
        "progress": calculate_progress(saved, target),

        # REECE: Additional calculation results.
        "recommended_monthly_saving": recommendation["recommended_monthly_saving"],
        "months_remaining": recommendation["months_remaining"],
        "recommendation_status": recommendation["status"]
    }



# MISHAYLE: Create a savings goal.
@savings_routes.route("/goals", methods=["POST"])
def create_goal():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    data = request.get_json(silent=True) or {}

    goal_name = str(data.get("goal_name") or "").strip()
    target_date = data.get("target_date")
    category = data.get("category")

    if not goal_name:
        return jsonify({"error": "Goal name is required"}), 400

    try:
        target_amount = float(data.get("target_amount"))
        saved_amount = float(data.get("saved_amount", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Amounts must be numbers"}), 400

    if target_amount <= 0:
        return jsonify({"error": "Target must be greater than zero"}), 400

    if saved_amount < 0:
        return jsonify({"error": "Saved amount cannot be negative"}), 400

    try:
        goal_date = datetime.strptime(
            target_date, "%Y-%m-%d"
        ).date()
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid target date"}), 400

    goal_id = create_savings_goal(
        user_id, goal_name, target_amount,
        goal_date, category
    )

    # Daniel's create function starts the saved amount at zero.
    if saved_amount > 0:
        update_saved_amount(user_id, goal_id, saved_amount)

    goal = get_savings_goal(user_id, goal_id)

    return jsonify({
        "message": "Savings goal created successfully",
        "goal": format_goal(goal)
    }), 201


# MISHAYLE: Get all goals and summary calculations.
@savings_routes.route("/goals", methods=["GET"])
def get_goals():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    database_goals = get_savings_goals(user_id)
    goals = [format_goal(goal) for goal in database_goals]

    return jsonify({
        "goals": goals,
        "summary": {
            "total_target": calculate_total_target(goals),
            "total_saved": calculate_total_saved(goals),
            "average_progress": calculate_average_progress(goals)
        }
    })


# MISHAYLE: Get one specific goal.
@savings_routes.route("/goals/<int:goal_id>", methods=["GET"])
def get_one_goal(goal_id):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    goal = get_savings_goal(user_id, goal_id)

    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    return jsonify({"goal": format_goal(goal)})


# MISHAYLE: Update how much has been saved.
@savings_routes.route("/goals/<int:goal_id>/saved", methods=["PUT"])
def update_goal_savings(goal_id):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    data = request.get_json(silent=True) or {}

    try:
        saved_amount = float(data.get("saved_amount"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid saved amount"}), 400

    if saved_amount < 0:
        return jsonify({"error": "Saved amount cannot be negative"}), 400

    updated = update_saved_amount(user_id, goal_id, saved_amount)

    if not updated:
        return jsonify({"error": "Goal not found"}), 404

    goal = get_savings_goal(user_id, goal_id)

    return jsonify({
        "message": "Savings updated",
        "goal": format_goal(goal)
    })


# MISHAYLE: Recalculate a goal's status from its saved amount.
@savings_routes.route("/goals/<int:goal_id>/status", methods=["PUT"])
def change_goal_status(goal_id):

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    goal = get_savings_goal(user_id, goal_id)

    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    saved_amount = float(goal["current_amount"])
    target_amount = float(goal["target_amount"])

    if saved_amount >= target_amount:
        status = "completed"
    else:
        status = "active"

    update_goal_status(user_id, goal_id, status)

    return jsonify({
        "message": "Goal status updated",
        "status": status
    })



# MISHAYLE: Add an amount to an existing goal (not replace its total).

# MISHAYLE: Add money to a savings goal and record it as an expense.
@savings_routes.route("/goals/<int:goal_id>/contributions", methods=["POST"])
def add_goal_contribution(goal_id):
    from decimal import Decimal, InvalidOperation
    from db import get_connection

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    goal = get_savings_goal(user_id, goal_id)

    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    data = request.get_json(silent=True) or {}

    # Validate the contribution amount.
    try:
        amount = Decimal(str(data.get("amount")))
    except (InvalidOperation, TypeError, ValueError):
        return jsonify({"error": "Invalid amount"}), 400

    if (
        not amount.is_finite()
        or amount <= 0
        or amount > Decimal("9999999999.99")
        or amount.as_tuple().exponent < -2
    ):
        return jsonify({
            "error": "Enter a valid positive amount with at most two decimal places"
        }), 400

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            # 1. Lock and retrieve the savings goal.
            cursor.execute("""
                SELECT goal_name, current_amount, target_amount
                FROM savings_goals
                WHERE goal_id = %s AND user_id = %s
                FOR UPDATE
            """, (goal_id, user_id))

            row = cursor.fetchone()

            if not row:
                connection.rollback()
                return jsonify({"error": "Goal not found"}), 404

            current = Decimal(str(row["current_amount"]))
            target = Decimal(str(row["target_amount"]))
            new_amount = current + amount

            if new_amount > target:
                connection.rollback()
                return jsonify({
                    "error": "Contribution exceeds remaining goal amount"
                }), 400

            # 2. Find the user's account.
            cursor.execute("""
                SELECT account_id
                FROM accounts
                WHERE user_id = %s
                ORDER BY account_id
                LIMIT 1
            """, (user_id,))

            account = cursor.fetchone()

            if not account:
                connection.rollback()
                return jsonify({
                    "error": "Please create an account before adding savings"
                }), 400

            account_id = account["account_id"]

            # 3. Find an existing expense category.
            cursor.execute("""
                SELECT category_id
                FROM categories
                WHERE category_name = %s
                  AND category_type = 'expense'
                LIMIT 1
            """, ("Other expense",))

            category = cursor.fetchone()

            if not category:
                connection.rollback()
                return jsonify({
                    "error": "Other expense category not found"
                }), 400

            category_id = category["category_id"]

            # 4. Update the savings goal.
            status = (
                "completed" if new_amount >= target else "active"
            )

            cursor.execute("""
                UPDATE savings_goals
                SET current_amount = %s,
                    status = %s
                WHERE goal_id = %s AND user_id = %s
            """, (new_amount, status, goal_id, user_id))

            # 5. Save the contribution as an expense transaction.
            description = (
                "Savings Contribution - " + row["goal_name"]
            )

            cursor.execute("""
                INSERT INTO transactions
                (
                    account_id,
                    category_id,
                    transaction_type,
                    amount,
                    transaction_date,
                    description,
                    created_at
                )
                VALUES (%s, %s, %s, %s, CURDATE(), %s, NOW())
            """, (
                account_id,
                category_id,
                "expense",
                amount,
                description
            ))

        # 6. Save both changes together.
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return jsonify({
        "message": "Savings added and transaction recorded",
        "goal": format_goal(get_savings_goal(user_id, goal_id))
    })

