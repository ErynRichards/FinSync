
from decimal import Decimal, InvalidOperation

# Support both project-root and backend-folder execution.
try:
    from backend.transactions.transaction_validation import validate_transaction
except ModuleNotFoundError as error:
    if error.name != "backend":
        raise
    from transactions.transaction_validation import validate_transaction


def calculate_account_balance(opening_balance, transactions):
    """
    Calculate the current account balance.

    Formula:
        Opening Balance + Total Income - Total Expenses

    Parameters:
        opening_balance: The account's starting balance.
        transactions: A list of validated transactions.

    Returns:
        The calculated account balance as a Decimal.
    """

    # Convert the opening balance into Decimal.
    try:
        opening_balance = Decimal(str(opening_balance))

        if not opening_balance.is_finite():
            raise ValueError

    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Opening balance must be a valid number.")

    # Ensure transactions are provided as a list.
    if not isinstance(transactions, list):
        raise ValueError("Transactions must be provided as a list.")

    # Start with the opening balance.
    current_balance = opening_balance

    # Validate and process every transaction.
    for transaction in transactions:

        errors = validate_transaction(transaction)

        if errors:
            raise ValueError("; ".join(errors))

        amount = Decimal(str(transaction["amount"]))

        if transaction["transaction_type"] == "income":
            current_balance += amount

        elif transaction["transaction_type"] == "expense":
            current_balance -= amount

    return current_balance
