
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_CEILING


def calculate_monthly_savings(
    target_amount,
    current_amount,
    target_date,
    today=None
):
    """
    Calculate the recommended monthly savings contribution.

    The calculation considers the amount already saved and
    the time remaining until the target date.
    """

    # Use today's date unless a date is supplied for testing.
    if today is None:
        today = date.today()

    # Convert monetary values into Decimal for accurate currency calculations.
    try:
        target = Decimal(str(target_amount))
        current = Decimal(str(current_amount))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Savings amounts must be valid numbers.")

    # Reject invalid monetary values.
    if not target.is_finite() or not current.is_finite():
        raise ValueError("Savings amounts must be finite numbers.")

    if target <= 0:
        raise ValueError("Target amount must be greater than zero.")

    if current < 0:
        raise ValueError("Current savings cannot be negative.")

    # Convert the target date into a date object when necessary.
    if isinstance(target_date, str):
        try:
            target_date = date.fromisoformat(target_date)
        except ValueError:
            raise ValueError("Target date must use YYYY-MM-DD format.")

    if not isinstance(target_date, date):
        raise ValueError("A valid target date is required.")

    if not isinstance(today, date):
        raise ValueError("Today's date must be valid.")

    # Calculate how much remains to be saved.
    remaining = max(Decimal("0.00"), target - current)

    # Return a completed status if the goal has been reached.
    if remaining == 0:
        return {
            "status": "completed",
            "remaining_amount": "0.00",
            "months_remaining": 0,
            "recommended_monthly_saving": "0.00"
        }

    # Do not calculate a recommendation for an overdue goal.
    if target_date < today:
        return {
            "status": "overdue",
            "remaining_amount": f"{remaining:.2f}",
            "months_remaining": 0,
            "recommended_monthly_saving": None
        }

    # Calculate the number of calendar months remaining.
    months = (
        (target_date.year - today.year) * 12
        + target_date.month - today.month
    )

    # A future deadline in the current month still requires one contribution.
    months = max(1, months)

    # Divide the remaining amount across the available months.
    monthly_amount = remaining / Decimal(months)

    # Round upwards to ensure the target can be reached.
    monthly_amount = monthly_amount.quantize(
        Decimal("0.01"),
        rounding=ROUND_CEILING
    )

    return {
        "status": "active",
        "remaining_amount": f"{remaining:.2f}",
        "months_remaining": months,
        "recommended_monthly_saving": f"{monthly_amount:.2f}"
    }
