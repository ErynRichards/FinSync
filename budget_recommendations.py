# FinSync - Budget Recommendation Calculations
# Uses the 50/30/20 rule and previous spending history.

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


# Categories used in FinSync

INCOME_CATEGORIES = [
    "Salary",
    "Freelance",
    "Allowance",
    "Other income"
]

NEEDS_CATEGORIES = [
    "Housing",
    "Groceries",
    "Transport",
    "Education",
    "Utilities"
]

WANTS_CATEGORIES = [
    "Entertainment",
    "Other expense"
]

# "Other" is not automatically classified because
# it may represent either income or an expense.


def round_to_50(amount):
    """Round an amount to the nearest R50."""
    value = Decimal(str(amount))
    return float(
        (value / Decimal("50")).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        ) * Decimal("50")
    )


def calculate_suggested_budget(
    user_id,
    category,
    period,
    monthly_income,
    monthly_expenses=None,
    other_category_budgets=0
):
    """
    Calculate the recommended budget for one expense category.

    user_id: Logged-in user's ID
    category: Selected expense category
    period: Budget month in YYYY-MM format
    monthly_income: Total income for the budget month
    monthly_expenses: Previous 3 complete months of spending
    other_category_budgets: Amount already allocated to
                            other categories in the same group
    """

    # Validate the selected budget period
    try:
        datetime.strptime(period, "%Y-%m")
    except (ValueError, TypeError):
        return {
            "success": False,
            "message": "Invalid budget period.",
            "suggested_budget": None
        }

    # Validate monthly income
    try:
        monthly_income = float(monthly_income)
    except (TypeError, ValueError):
        monthly_income = 0

    if monthly_income <= 0:
        return {
            "success": False,
            "message": "Add your monthly income first.",
            "suggested_budget": None
        }

    # Calculate the 50/30/20 allocations
    needs_budget = monthly_income * 0.50
    wants_budget = monthly_income * 0.30
    savings_budget = monthly_income * 0.20

    # Identify the selected category's group
    if category in NEEDS_CATEGORIES:
        group = "Needs"
        group_budget = needs_budget
        category_count = len(NEEDS_CATEGORIES)

    elif category in WANTS_CATEGORIES:
        group = "Wants"
        group_budget = wants_budget
        category_count = len(WANTS_CATEGORIES)

    else:
        return {
            "success": False,
            "message": "Select a valid expense category.",
            "suggested_budget": None
        }

    # Calculate the default income-based recommendation
    income_based_budget = group_budget / category_count

    # Check previous spending history
    # Expected: three monthly totals in chronological order
    # None means that month's history is unavailable.
    history_available = (
        monthly_expenses is not None
        and len(monthly_expenses) == 3
        and all(
            amount is not None
            for amount in monthly_expenses
        )
    )

    if history_available:

        # Calculate average spending over three months
        expenses = [float(x) for x in monthly_expenses]

        if any(x < 0 for x in expenses):
            return {
                "success": False,
                "message": "Invalid expense history.",
                "suggested_budget": None
            }

        average_spending = sum(expenses) / 3

        # Use previous spending to personalise the budget
        suggested_budget = average_spending
        method = "Three-month spending average"

    else:

        # Use 50/30/20 when history is insufficient
        average_spending = None
        suggested_budget = income_based_budget
        method = "50/30/20 income-based allocation"

    # Calculate remaining allocation for this group
    try:
        allocated = float(other_category_budgets)
    except (TypeError, ValueError):
        allocated = 0

    if allocated < 0:
        return {
            "success": False,
            "message": "Invalid existing budget allocation.",
            "suggested_budget": None
        }

    remaining_budget = max(0, group_budget - allocated)

    # Keep recommendation within the remaining limit
    suggested_budget = min(
        suggested_budget,
        remaining_budget
    )

    # Round recommendation to a practical R50
    suggested_budget = round_to_50(suggested_budget)

    # Do not exceed the remaining allocation after rounding
    if suggested_budget > remaining_budget:
        suggested_budget = float(
            Decimal(str(remaining_budget))
            // Decimal("50") * Decimal("50")
        )

    # Return the result to the Flask backend
    return {
        "success": True,
        "user_id": user_id,
        "category": category,
        "period": period,
        "group": group,
        "monthly_income": round(monthly_income, 2),
        "needs_budget": round(needs_budget, 2),
        "wants_budget": round(wants_budget, 2),
        "savings_budget": round(savings_budget, 2),
        "average_spending": (
            round(average_spending, 2)
            if average_spending is not None
            else None
        ),
        "method": method,
        "suggested_budget": suggested_budget
    }