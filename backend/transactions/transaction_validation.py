
# Import date to check whether transaction dates are valid.
from datetime import date

# Import Decimal to validate financial amounts accurately.
from decimal import Decimal, InvalidOperation


# Check the submitted transaction fields before any database write.
def validate_transaction(transaction):
    """
    Validate a single FinSync financial transaction.

    The function checks that all required information is present
    and that the transaction contains valid financial data.

    Returns:
        A list of validation error messages.
        An empty list means the transaction is valid.
    """

    # Store any validation problems found.
    errors = []

    # Define the fields that every transaction must contain.
    required_fields = [
        "transaction_id",
        "description",
        "amount",
        "transaction_type",
        "transaction_date"
    ]

    # Check whether the transaction is a dictionary.
    if not isinstance(transaction, dict):
        # Send the result back to the code that called this function.
        return ["Transaction must be provided as a dictionary."]

    # Check that all required fields are available.
    for field in required_fields:
        # Check the condition before continuing.
        if field not in transaction or transaction[field] is None:
            # Add this item to the list of results.
            errors.append(f"Missing required field: {field}")

    # Stop further checks if required fields are missing.
    if errors:
        # Send the result back to the code that called this function.
        return errors

    # Check that the transaction ID is a positive integer.
    transaction_id = transaction["transaction_id"]

    # Check the condition before continuing.
    if (
        not isinstance(transaction_id, int)
        or isinstance(transaction_id, bool)
        or transaction_id <= 0
    ):
        # Add this item to the list of results.
        errors.append("Transaction ID must be a positive integer.")

    # Check that the description contains actual text.
    description = transaction["description"]

    # Check the condition before continuing.
    if not isinstance(description, str):
        # Add this item to the list of results.
        errors.append("Transaction description must be text.")

    # Check that the amount is a valid positive financial value.
    try:
        # Save an amount for a calculation or database update.
        amount = Decimal(str(transaction["amount"]))

        # Check the condition before continuing.
        if not amount.is_finite() or amount <= 0:
            # Add this item to the list of results.
            errors.append("Transaction amount must be greater than zero.")

    except (InvalidOperation, ValueError):
        # Add this item to the list of results.
        errors.append("Transaction amount must be a valid number.")

    # Check that the transaction type is supported.
    transaction_type = transaction["transaction_type"]

    # Check the condition before continuing.
    if transaction_type not in ["income", "expense"]:
        # Add this item to the list of results.
        errors.append("Transaction type must be income or expense.")

    # Check that the transaction date follows YYYY-MM-DD.
    try:
        transaction_date = date.fromisoformat(
            transaction["transaction_date"]
        )

        # Ensure the supplied date uses the required format.
        if transaction_date.isoformat() != transaction["transaction_date"]:
            # Add this item to the list of results.
            errors.append("Transaction date must use YYYY-MM-DD format.")

    except (ValueError, TypeError):
        # Add this item to the list of results.
        errors.append("Transaction date must be a valid YYYY-MM-DD date.")

    # Return all validation errors found.
    return errors
