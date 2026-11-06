
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


# Categories belonging to each budget group
BUDGET_CATEGORIES = {
    "needs": [
        "groceries", "food", "transport", "rent",
        "utilities", "healthcare", "education"
    ],
    "wants": [
        "entertainment", "shopping", "subscriptions",
        "restaurants", "travel"
    ],
    "savings": [
        "savings", "emergency fund", "financial goals"
    ]
}

# Percentages for the 50/30/20 budgeting rule
BUDGET_PERCENTAGES = {
    "needs": Decimal("0.50"),
    "wants": Decimal("0.30"),
    "savings": Decimal("0.20")
}


def round_to_50(amount):
    # Round an amount to the nearest R50
    amount = Decimal(str(amount))
    return int(
        (amount / 50).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        ) * 50
    )


def get_budget_group(category):
    # Find which budget group the selected category belongs to
    category = category.strip().lower()

    for group, categories in BUDGET_CATEGORIES.items():
        if category in categories:
            return group

    return None


def get_previous_three_months(budget_period):
    # Find the previous three complete calendar months
    year = budget_period.year
    month = budget_period.month
    months = []

    for i in range(3):
        month -= 1

        if month == 0:
            month = 12
            year -= 1

        months.append((year, month))

    return months


def calculate_suggested_budget(
    user_id, category, budget_period, monthly_income, transactions
):
    """
    Calculate a recommended budget for the selected category.

    Transactions are supplied by the backend/database.
    """

    # Check that the selected category is valid
    group = get_budget_group(category)

    if group is None:
        return {
            "success": False,
            "message": "Invalid budget category.",
            "suggested_budget": None
        }

    # Check the monthly income
    income = Decimal(str(monthly_income))

    if income <= 0:
        return {
            "success": False,
            "message": "Monthly income must be greater than zero.",
            "suggested_budget": None
        }

    # Calculate the allowance using the 50/30/20 rule
    percentage = BUDGET_PERCENTAGES[group]
    group_allowance = income * percentage

    # Savings uses 20% of income directly
    if group == "savings":
        recommended = round_to_50(group_allowance)

        return {
            "success": True,
            "category": category,
            "budget_group": group,
            "percentage": 20,
            "suggested_budget": recommended,
            "placeholder": f"R{recommended:,.2f}",
            "message": "Savings recommendation calculated."
        }

    # Find the previous three complete months
    previous_months = get_previous_three_months(budget_period)

    monthly_totals = {
        month: Decimal("0") for month in previous_months
    }

    months_with_history = set()

    # Calculate spending for the selected user and category
    for transaction in transactions:

        if transaction["user_id"] != user_id:
            continue

        if transaction["category"].lower() != category.lower():
            continue

        if transaction["type"].lower() != "expense":
            continue

        transaction_date = transaction["date"]

        month_key = (
            transaction_date.year,
            transaction_date.month
        )

        if month_key in monthly_totals:
            amount = Decimal(str(transaction["amount"]))

            if amount >= 0:
                monthly_totals[month_key] += amount
                months_with_history.add(month_key)

    # Check whether enough spending history exists
    if len(months_with_history) < 3:
        return {
            "success": False,
            "message": "Insufficient spending history.",
            "suggested_budget": None,
            "placeholder": "Not enough spending history"
        }

    # Calculate the average spending over three months
    total_spending = sum(monthly_totals.values())
    average_spending = total_spending / 3

    # Round the recommendation to the nearest R50
    recommended = round_to_50(average_spending)

    # Do not exceed the overall needs/wants allowance
    maximum_budget = round_to_50(group_allowance)
    recommended = min(recommended, maximum_budget)

    # Return the result to the backend
    return {
        "success": True,
        "user_id": user_id,
        "category": category,
        "budget_group": group,
        "percentage": int(percentage * 100),
        "average_spending": round(float(average_spending), 2),
        "group_allowance": float(group_allowance),
        "suggested_budget": recommended,
        "placeholder": f"R{recommended:,.2f}",
        "message": "Budget recommendation calculated."
    }


# -------------------------------------------------
# SAMPLE TEST DATA
# This will be replaced by Daniel's database later.
# -------------------------------------------------

if __name__ == "__main__":

    sample_transactions = [
        {
            "user_id": 1,
            "category": "Groceries",
            "type": "expense",
            "amount": 1200,
            "date": date(2026, 8, 10)
        },
        {
            "user_id": 1,
            "category": "Groceries",
            "type": "expense",
            "amount": 1400,
            "date": date(2026, 9, 12)
        },
        {
            "user_id": 1,
            "category": "Groceries",
            "type": "expense",
            "amount": 1300,
            "date": date(2026, 10, 15)
        }
    ]

    result = calculate_suggested_budget(
        user_id=1,
        category="Groceries",
        budget_period=date(2026, 11, 1),
        monthly_income=10000,
        transactions=sample_transactions
    )

    print("FINSYNC - BUDGET RECOMMENDATION")
    print("--------------------------------")

    if result["success"]:
        print("Category:", result["category"])
        print("Budget Group:", result["budget_group"])
        print("Percentage:", result["percentage"], "%")
        print("Average Spending: R", result.get("average_spending", "N/A"))
        print("Recommended Budget:", result["placeholder"])
    else:
        print(result["message"])
