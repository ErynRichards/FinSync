
# Import Decimal for accurate financial calculations and formatting.
from decimal import Decimal

# Import the existing transaction functions.
from backend.transactions.transaction_summary import calculate_transaction_summary
from backend.transactions.recent_transactions import get_recent_transactions

# Import transaction validation.
from backend.transactions.transaction_validation import validate_transaction

# Import the account balance calculation function.
from backend.transactions.account_balance import calculate_account_balance

# REECE: Monthly income and expense summary
from backend.transactions.monthly_summary import calculate_monthly_summary

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
        opening_balance: The account's starting balance.
        This is optional until database integration is completed.

    Returns:
        A dictionary containing account balance, financial summaries,
        recent transactions and transaction count.

    Raises:
        ValueError: If transaction records or opening balance are invalid.
    """

    # Check that transactions are supplied as a list.
    if not isinstance(transactions, list):
        raise ValueError("Transactions must be provided as a list.")

    # Store any transaction validation errors.
    validation_errors = []

    # Validate every transaction before processing it.
    for index, transaction in enumerate(transactions):

        # Check whether the individual transaction is valid.
        errors = validate_transaction(transaction)

        # Add the transaction position to any errors found.
        for error in errors:
            validation_errors.append(
                f"Transaction {index + 1}: {error}"
            )

    # Reject the entire dataset if any transaction is invalid.
    if validation_errors:
        raise ValueError("; ".join(validation_errors))

    # Calculate income, expenses and net cash flow.
    financial_summary = calculate_transaction_summary(transactions)

    # Retrieve the five newest transactions.
    recent_transactions = get_recent_transactions(transactions)

    # Calculate the account balance only when an opening
    # balance has been supplied.
    if opening_balance is not None:

        account_balance = calculate_account_balance(
            opening_balance,
            transactions
        )

        # Format the calculated balance for JSON responses.
        formatted_account_balance = format_money(account_balance)

    else:
        # Do not assume an account balance when the opening
        # balance is not yet available.
        formatted_account_balance = None

    # Format the financial summary for JSON compatibility.
    formatted_summary = {
        "total_income": format_money(financial_summary["total_income"]),
        "total_expenses": format_money(financial_summary["total_expenses"]),
        "net_cash_flow": format_money(financial_summary["net_cash_flow"])
    }

    # Prepare copies of the recent transactions.
    formatted_recent_transactions = []

    for transaction in recent_transactions:

        # Copy the transaction to avoid changing the original record.
        formatted_transaction = transaction.copy()

        # Format the transaction amount to two decimal places.
        formatted_transaction["amount"] = format_money(
            formatted_transaction["amount"]
        )

        # Add the formatted transaction to the Dashboard results.
        formatted_recent_transactions.append(formatted_transaction)

    # Count all validated transactions.
    transaction_count = len(transactions)


    # REECE: Prepare transactions for the monthly summary.
    monthly_transactions = []

    for transaction in transactions:
        monthly_transaction = transaction.copy()

        # MySQL can return dates as Python date objects.
        transaction_date = monthly_transaction["transaction_date"]

        if hasattr(transaction_date, "isoformat"):
            monthly_transaction["transaction_date"] = (
                transaction_date.isoformat()
            )

        monthly_transactions.append(monthly_transaction)

    # REECE: Calculate monthly income and expenses.
    monthly_summary = calculate_monthly_summary(monthly_transactions)

    # Convert Decimal amounts to strings for JSON.
    formatted_monthly_summary = []

    for month in monthly_summary:
        formatted_monthly_summary.append({
            "month": month["month"],
            "total_income": format_money(month["total_income"]),
            "total_expenses": format_money(month["total_expenses"])
        })


    # Combine all information into one Dashboard response.
    dashboard_data = {
        "account_balance": formatted_account_balance,
        "financial_summary": formatted_summary,
        "recent_transactions": formatted_recent_transactions,
        "transaction_count": transaction_count,
        "monthly_summary": formatted_monthly_summary
    }

    return dashboard_data
