
# accounts.py
# Functions for a user's accounts (e.g. Cheque, Savings, Cash).

# Use functions and classes from another file.
from db import DatabaseError, execute, fetch_all, fetch_one



# Handle create account requests or data.
def create_account(user_id, account_name, account_type,
                   opening_balance=0, currency="ZAR"):

    # Check if the user already has an account
    existing_account = fetch_one(
        "SELECT account_id FROM accounts WHERE user_id = %s",
        (user_id,)
    )

    # Check the condition before continuing.
    if existing_account is not None:
        # Stop the operation and report an error.
        raise DatabaseError(
            "This user already has a financial account."
        )

    # Check required fields
    if not account_name.strip() or not account_type.strip():
        # Stop the operation and report an error.
        raise DatabaseError(
            "Account name and type are required."
        )

    # Create the account
    sql = """
        INSERT INTO accounts
        (user_id, account_name, account_type,
         opening_balance, currency)
        VALUES (%s, %s, %s, %s, %s)
    """

    rows_changed, account_id = execute(
        sql,
        (
            user_id,
            account_name,
            account_type,
            opening_balance,
            currency
        )
    )

    # Send the result back to the code that called this function.
    return account_id



# Handle get accounts requests or data.
def get_accounts(user_id):
    """Get all of a user's accounts."""
    # Send the result back to the code that called this function.
    return fetch_all("SELECT * FROM accounts WHERE user_id = %s", (user_id,))


# Handle get account requests or data.
def get_account(user_id, account_id):
    """Get one account. Returns None if it doesn't belong to this user."""
    sql = "SELECT * FROM accounts WHERE account_id = %s AND user_id = %s"
    # Send the result back to the code that called this function.
    return fetch_one(sql, (account_id, user_id))


# Handle get account balance requests or data.
def get_account_balance(user_id, account_id):
    """Balance = opening balance + income - expenses."""
    account = get_account(user_id, account_id)

    # Check the condition before continuing.
    if account is None:
        # Send the result back to the code that called this function.
        return None

    sql = "SELECT SUM(amount) AS total FROM transactions WHERE account_id = %s AND transaction_type = %s"

    # Save an amount for a calculation or database update.
    income = fetch_one(sql, (account_id, "income"))["total"]

    # Save an amount for a calculation or database update.
    expenses = fetch_one(sql, (account_id, "expense"))["total"]

    # SUM returns None when there are no transactions yet
    if income is None:

        # Save an amount for a calculation or database update.
        income = 0

    # Check the condition before continuing.
    if expenses is None:
        # Save an amount for a calculation or database update.
        expenses = 0

    # Send the result back to the code that called this function.
    return account["opening_balance"] + income - expenses
