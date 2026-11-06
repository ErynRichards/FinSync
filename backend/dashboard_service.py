
# Import Decimal for accurate financial calculations and formatting.
from decimal import Decimal

# Import the existing transaction functions.
# Support both project-root and backend-folder execution.
try:
    from backend.transactions.transaction_summary import calculate_transaction_summary
    from backend.transactions.recent_transactions import get_recent_transactions
    from backend.transactions.transaction_validation import validate_transaction
    from backend.transactions.account_balance import calculate_account_balance

except ModuleNotFoundError as error:
    if error.name != "backend":
        raise

    from transactions.transaction_summary import calculate_transaction_summary
    from transactions.recent_transactions import get_recent_transactions
    from transactions.transaction_validation import validate_transaction
    from transactions.account_balance import calculate_account_balance


def format_money(amount):
    """
    Convert a monetary amount into a two-decimal-place string.

    This makes financial values suitable for JSON responses.
    """

    # Convert the amount to Decimal before formatting.
    amount = Decimal(str(amount))

    # Return the amount with exactly two decimal places.
    return f"{amount:.2f}"


def build_dashboard_data(transactions, opening_balance=None):
    """
    Prepare validated financial information for the FinSync Dashboard.

    Parameters:
        transactions: A list of the user's financial transactions.
        opening_balance: The account's opening balance (optional).

    Returns:
        A dictionary containing the Dashboard financial information.
    """

    # Check that transactions are provided as a list.
    if not isinstance(transactions, list):
        raise ValueError("Transactions must be provided as a list.")

    # Validate every transaction before performing calculations.
    for transaction in transactions:
        errors = validate_transaction(transaction)

        if errors:
            raise ValueError("; ".join(errors))

    # Calculate total income, expenses and net cash flow.
    summary = calculate_transaction_summary(transactions)

    # Retrieve the five most recent transactions.
    recent_transactions = get_recent_transactions(transactions, limit=5)

    # Calculate the account balance only when an opening balance is provided.
    account_balance = None

    if opening_balance is not None:
        account_balance = calculate_account_balance(
            opening_balance,
            transactions
        )

    # Prepare the Dashboard response.
    dashboard_data = {
        "account_balance": (
            format_money(account_balance)
            if account_balance is not None
            else None
        ),
        "financial_summary": {
            "total_income": format_money(summary["total_income"]),
            "total_expenses": format_money(summary["total_expenses"]),
            "net_cash_flow": format_money(summary["net_cash_flow"])
        },
        "recent_transactions": recent_transactions,
        "transaction_count": len(transactions)
    }

    return dashboard_data
