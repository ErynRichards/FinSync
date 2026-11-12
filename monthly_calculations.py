
# MISHAYLE'S PART
# Calculate income, expenses and net cash flow
# for the last 7 days.

# Use functions and classes from another file.
from datetime import date, datetime, timedelta

# Use functions and classes from another file.
from decimal import Decimal


# Handle calculate last 7 days requests or data.
def calculate_last_7_days(transactions):

    today = date.today()
    start_date = today - timedelta(days=6)

    daily_data = {}

    # Create entries for all 7 days
    for i in range(7):
        day = start_date + timedelta(days=i)

        daily_data[str(day)] = {
            "income": Decimal("0.00"),
            "expenses": Decimal("0.00"),
            "net_cash_flow": Decimal("0.00")
        }

    # Go through the user's transactions
    for transaction in transactions:

        transaction_date = transaction["transaction_date"]

        # Convert the date to a date object
        if isinstance(transaction_date, str):
            transaction_date = date.fromisoformat(transaction_date)

        # Check the condition before continuing.
        elif isinstance(transaction_date, datetime):
            transaction_date = transaction_date.date()

        day = str(transaction_date)

        # Only include transactions from the last 7 days
        if day not in daily_data:
            continue

        # Save an amount for a calculation or database update.
        amount = Decimal(str(transaction["amount"]))
        transaction_type = transaction["transaction_type"].lower()

        # Check the condition before continuing.
        if transaction_type == "income":
            daily_data[day]["income"] += amount

        # Check the condition before continuing.
        elif transaction_type == "expense":
            daily_data[day]["expenses"] += amount

    # Calculate net cash flow for each day
    for day in daily_data:

        # Save an amount for a calculation or database update.
        income = daily_data[day]["income"]

        # Save an amount for a calculation or database update.
        expenses = daily_data[day]["expenses"]

        daily_data[day]["net_cash_flow"] = income - expenses

    # Send the result back to the code that called this function.
    return daily_data
