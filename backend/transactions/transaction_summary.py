
# Use functions and classes from another file.
from decimal import Decimal


# Handle calculate transaction summary requests or data.
def calculate_transaction_summary(transactions):
    """
    Calculate the income, expenses and net cash flow
    from a user's financial transactions.

    Parameters:
        transactions: A list of financial transaction records.

    Returns:
        A dictionary containing the calculated financial totals.
    """

    # Start all financial totals at zero.
    # Decimal is used to avoid common floating-point rounding issues
    # when working with money.
    total_income = Decimal("0.00")
    # Save an amount for a calculation or database update.
    total_expenses = Decimal("0.00")

    # Go through each transaction in the supplied list.
    for transaction in transactions:

        # Convert the transaction amount to Decimal.
        # Using str() helps avoid floating-point conversion issues.
        amount = Decimal(str(transaction["amount"]))

        # Check whether the transaction represents money received.
        if transaction["transaction_type"] == "income":
            total_income += amount

        # Check whether the transaction represents money spent.
        elif transaction["transaction_type"] == "expense":
            total_expenses += amount

    # Calculate the net cash flow.
    # This is income minus expenses, not necessarily the user's
    # actual bank account balance.
    net_cash_flow = total_income - total_expenses

    # Return the calculated figures in a dictionary.
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_cash_flow": net_cash_flow
    }
