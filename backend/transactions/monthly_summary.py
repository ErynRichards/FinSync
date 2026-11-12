
# Import date to extract the year and month from transaction dates.
from datetime import date

# Import Decimal for accurate financial calculations.
from decimal import Decimal, InvalidOperation


# Handle calculate monthly summary requests or data.
def calculate_monthly_summary(transactions):
    """
    Calculate monthly income and expenses from financial transactions.

    Parameters:
        transactions: A list of financial transaction dictionaries.

    Returns:
        A list containing monthly income and expense totals,
        ordered from the oldest month to the newest month.
    """

    # Store the financial totals for each month.
    monthly_totals = {}

    # Process each transaction.
    for transaction in transactions:

        # Read and validate the transaction date.
        try:
            transaction_date = date.fromisoformat(
                transaction["transaction_date"]
            )
        except (ValueError, TypeError, KeyError):
            # Stop the operation and report an error.
            raise ValueError("A transaction contains an invalid date.")

        # Convert the transaction amount into Decimal.
        try:
            # Save an amount for a calculation or database update.
            amount = Decimal(str(transaction["amount"]))

            # Check the condition before continuing.
            if not amount.is_finite() or amount <= 0:
                # Stop the operation and report an error.
                raise ValueError("Transaction amount must be positive.")

        except (InvalidOperation, ValueError):
            # Stop the operation and report an error.
            raise ValueError("A transaction contains an invalid amount.")

        # Extract the year and month.
        month = transaction_date.strftime("%Y-%m")

        # Create the month's totals if this is the first transaction.
        if month not in monthly_totals:
            monthly_totals[month] = {
                "total_income": Decimal("0.00"),
                "total_expenses": Decimal("0.00")
            }

        # Add income or expenses to the relevant monthly total.
        transaction_type = transaction["transaction_type"]

        # Check the condition before continuing.
        if transaction_type == "income":
            monthly_totals[month]["total_income"] += amount

        # Check the condition before continuing.
        elif transaction_type == "expense":
            monthly_totals[month]["total_expenses"] += amount

        else:
            # Stop the operation and report an error.
            raise ValueError(
                "Transaction type must be income or expense."
            )

    # Sort the months chronologically.
    sorted_months = sorted(monthly_totals.keys())

    # Prepare the monthly summary for the Dashboard.
    monthly_summary = []

    # Go through each item one at a time.
    for month in sorted_months:

        # Retrieve the totals for the current month.
        totals = monthly_totals[month]

        # Add the month's figures to the result.
        monthly_summary.append({
            "month": month,
            "total_income": totals["total_income"],
            "total_expenses": totals["total_expenses"]
        })

    # Send the result back to the code that called this function.
    return monthly_summary
