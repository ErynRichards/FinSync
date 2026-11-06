
# Import Decimal for accurate financial calculations.
from decimal import Decimal, InvalidOperation

# Import the existing transaction validation function.
from backend.transactions.transaction_validation import validate_transaction


def calculate_account_balance(opening_balance, transactions):
    """
    Calculate an account's current balance using its opening balance
    and validated financial transactions.

    Parameters:
        opening_balance: The amount available when the account started.
        transactions: A list of the account's financial transactions.

    Returns:
        The calculated account balance as a Decimal.

    Raises:
        ValueError: If the opening balance or transactions are invalid.
    """

    # Convert the opening balance into a Decimal value.
    try:
        opening_balance = Decimal(str(opening_balance))

        # Ensure the opening balance is a valid finite number.
        if not opening_balance.is_finite():
            raise ValueError("Opening balance must be a valid number.")

    except (InvalidOperation, ValueError):
        raise ValueError("Opening balance must be a valid number.")

    # Check that the transaction information is supplied as a list.
    if not isinstance(transactions, list):
        raise ValueError("Transactions must be provided as a list.")

    # Start calculating from the account's opening balance.
    current_balance = opening_balance

    # Process each transaction individually.
    for index, transaction in enumerate(transactions):

        # Validate the transaction before using it.
        errors = validate_transaction(transaction)

        # Reject invalid transactions instead of using incorrect data.
        if errors:
            raise ValueError(
                f"Transaction {index + 1} is invalid: {'; '.join(errors)}"
            )

        # Convert the transaction amount into Decimal.
        amount = Decimal(str(transaction["amount"]))

        # Add income to the account balance.
        if transaction["transaction_type"] == "income":
            current_balance += amount

        # Subtract expenses from the account balance.
        elif transaction["transaction_type"] == "expense":
            current_balance -= amount

    # Return the final calculated account balance.
    return current_balance
