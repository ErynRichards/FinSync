
"""
FinSync - Budget Exceeded Notification Checker

Responsibilities:
1. Check whether monthly spending has exceeded a budget.
2. Detect the transition from within budget to over budget.
3. Respect the user's budget notification preference.
4. Generate a unique identifier for each user, budget and month.
5. Prevent duplicate notifications when an event was already recorded.

This module does not save transactions or display pop-ups.
Those responsibilities are handled during integration.
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation


def _to_decimal(value, field_name):
    """
    Convert a supplied financial value to Decimal.

    Decimal is used to avoid floating-point rounding issues
    when working with money.
    """

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid number.")

    if not amount.is_finite():
        raise ValueError(f"{field_name} must be a finite number.")

    return amount


def check_budget_notification(
    user_id,
    budget_id,
    budget_month,
    budget_amount,
    previous_spending,
    current_spending,
    notifications_enabled=True,
    notified_event_ids=None
):
    """
    Determine whether a budget-exceeded notification should appear.

    Parameters:
        user_id: ID of the user who owns the budget.
        budget_id: Unique ID of the relevant budget.
        budget_month: Budget month in YYYY-MM format.
        budget_amount: Maximum permitted spending.
        previous_spending: Spending total before the new expense.
        current_spending: Spending total after the new expense.
        notifications_enabled: User's budget-warning preference.
        notified_event_ids: Previously recorded notification IDs.

    Returns:
        A dictionary describing whether a notification should trigger.
    """

    # Validate the identifiers.
    if user_id is None or str(user_id).strip() == "":
        raise ValueError("A valid user ID is required.")

    if budget_id is None or str(budget_id).strip() == "":
        raise ValueError("A valid budget ID is required.")

    # Validate the month format.
    try:
        datetime.strptime(budget_month, "%Y-%m")
    except (ValueError, TypeError):
        raise ValueError("Budget month must use YYYY-MM format.")

    # Convert financial values to Decimal.
    budget = _to_decimal(budget_amount, "Budget amount")
    previous_total = _to_decimal(
        previous_spending, "Previous spending"
    )
    current_total = _to_decimal(
        current_spending, "Current spending"
    )

    # Validate the financial values.
    if budget <= Decimal("0"):
        raise ValueError("Budget amount must be greater than zero.")

    if previous_total < Decimal("0"):
        raise ValueError("Previous spending cannot be negative.")

    if current_total < Decimal("0"):
        raise ValueError("Current spending cannot be negative.")

    # Generate a unique event ID for this user's budget and month.
    event_id = (
        f"budget-exceeded:{user_id}:{budget_id}:{budget_month}"
    )

    # Use an empty set when no previous events are supplied.
    if notified_event_ids is None:
        notified_event_ids = set()

    # Check whether the user has enabled budget warnings.
    if not notifications_enabled:
        return {
            "should_notify": False,
            "reason": "Budget notifications are disabled.",
            "event_id": event_id
        }

    # Check whether this event has already been recorded.
    if event_id in notified_event_ids:
        return {
            "should_notify": False,
            "reason": "This budget notification was already recorded.",
            "event_id": event_id
        }

    # A notification is only triggered when spending crosses
    # from within the budget to above the budget.
    crossed_budget_limit = (
        previous_total <= budget
        and current_total > budget
    )

    if not crossed_budget_limit:
        return {
            "should_notify": False,
            "reason": "No new budget limit crossing occurred.",
            "event_id": event_id
        }

    # Calculate how much spending is above the budget.
    amount_over_budget = current_total - budget

    return {
        "should_notify": True,
        "reason": "Monthly budget exceeded.",
        "event_id": event_id,
        "user_id": str(user_id),
        "budget_id": str(budget_id),
        "budget_month": budget_month,
        "budget_amount": budget,
        "previous_spending": previous_total,
        "current_spending": current_total,
        "amount_over_budget": amount_over_budget,
        "message": (
            f"You have exceeded your budget by "
            f"R{amount_over_budget:,.2f}."
        )
    }
