
"""Connects Eryn's calculations to the database transactions"""

from decimal import Decimal
from financial_calculations import get_financial_summary
from transactions import get_transactions
from db import get_connection


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

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(SUM(opening_balance), 0) AS opening_total "
                "FROM accounts WHERE user_id = %s",
                (user_id,)
            )

            result = cursor.fetchone()

        opening_total = Decimal(str(result["opening_total"]))

    finally:
        connection.close()

    # Calculate the current balance
    summary["opening_balance_total"] = opening_total
    summary["current_balance"] = opening_total + summary["balance"]

    return summary
