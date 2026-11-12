
"""Connects Eryn's calculations to the database transactions"""

# Use functions and classes from another file.
from decimal import Decimal

# Use functions and classes from another file.
from financial_calculations import get_financial_summary

# Use functions and classes from another file.
from transactions import get_transactions

# Use functions and classes from another file.
from db import get_connection


# Handle get user financial summary requests or data.
def get_user_financial_summary(user_id):

    # Gets the logged-in users transactions
    records = get_transactions(user_id)

    # Convert the transaction fields into Eryns format
    adapted = [
        {
            "type": row["transaction_type"],
            "amount": row["amount"],
            "category": row["category_name"]
        }
        for row in records
    ]

    # Use Eryn's calculations
    summary = get_financial_summary(adapted)

    # Get opening balances from the database
    connection = get_connection()

    # Try the operation and handle any errors.
    try:
        # Use this resource and close it when finished.
        with connection.cursor() as cursor:
            # Run the database query using these values.
            cursor.execute(
                "SELECT COALESCE(SUM(opening_balance), 0) AS opening_total "
                "FROM accounts WHERE user_id = %s",
                (user_id,)
            )

            result = cursor.fetchone()

        # Save an amount for a calculation or database update.
        opening_total = Decimal(str(result["opening_total"]))

    finally:
        # Close this resource when finished.
        connection.close()

    # Calculate the current balance
    summary["opening_balance_total"] = opening_total
    summary["current_balance"] = opening_total + summary["balance"]

    # Send the result back to the code that called this function.
    return summary
