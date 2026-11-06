
# accounts.py
# Functions for a user's accounts (e.g. Cheque, Savings, Cash).

from db import DatabaseError, execute, fetch_all, fetch_one



def create_account(user_id, account_name, account_type,
                   opening_balance=0, currency="ZAR"):

    # Check if the user already has an account
    existing_account = fetch_one(
        "SELECT account_id FROM accounts WHERE user_id = %s",
        (user_id,)
    )

    if existing_account is not None:
        raise DatabaseError(
            "This user already has a financial account."
        )

    # Check required fields
    if not account_name.strip() or not account_type.strip():
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

    return account_id



def get_accounts(user_id):
    """Get all of a user's accounts."""
    return fetch_all("SELECT * FROM accounts WHERE user_id = %s", (user_id,))


def get_account(user_id, account_id):
    """Get one account. Returns None if it doesn't belong to this user."""
    sql = "SELECT * FROM accounts WHERE account_id = %s AND user_id = %s"
    return fetch_one(sql, (account_id, user_id))


def get_account_balance(user_id, account_id):
    """Balance = opening balance + income - expenses."""
    account = get_account(user_id, account_id)
    if account is None:
        return None

    sql = "SELECT SUM(amount) AS total FROM transactions WHERE account_id = %s AND transaction_type = %s"
    income = fetch_one(sql, (account_id, "income"))["total"]
    expenses = fetch_one(sql, (account_id, "expense"))["total"]

    # SUM returns None when there are no transactions yet
    if income is None:
        income = 0
    if expenses is None:
        expenses = 0

    return account["opening_balance"] + income - expenses
