# transactions.py
# Functions to save and get a user's transactions.
# Transactions are linked to a user through their account, so the queries
# join to the accounts table and check the user_id.

from accounts import get_account
from db import DatabaseError, execute, fetch_all, fetch_one


def get_categories():
    """Get all categories (Salary, Groceries, etc.)."""
    return fetch_all("SELECT * FROM categories ORDER BY category_name")


def add_transaction(user_id, account_id, category_id, description, amount, transaction_type, transaction_date):
    """Check the details, save the transaction and return its id."""
    if transaction_type != "income" and transaction_type != "expense":
        raise DatabaseError("Transaction type must be income or expense.")

    try:
        amount = float(amount)
    except ValueError:
        raise DatabaseError("Amount must be a number.")
    if amount <= 0:
        raise DatabaseError("Amount must be more than 0.")

    # The account must belong to the logged-in user
    if get_account(user_id, account_id) is None:
        raise DatabaseError("That account was not found.")

    # The category must match the type, e.g. Salary can't be an expense
    category = fetch_one("SELECT * FROM categories WHERE category_id = %s", (category_id,))
    if category is None:
        raise DatabaseError("That category was not found.")
    if category["category_type"] != transaction_type:
        raise DatabaseError("That category is for " + category["category_type"] + " only.")

    sql = """INSERT INTO transactions
             (account_id, category_id, description, amount, transaction_type, transaction_date)
             VALUES (%s, %s, %s, %s, %s, %s)"""
    rows_changed, transaction_id = execute(sql, (account_id, category_id, description, amount,
                                                 transaction_type, transaction_date))
    return transaction_id


def get_transactions(user_id):
    """Get all of a user's transactions, newest first."""
    sql = """SELECT t.*, a.account_name, c.category_name
             FROM transactions t
             JOIN accounts a ON t.account_id = a.account_id
             JOIN categories c ON t.category_id = c.category_id
             WHERE a.user_id = %s
             ORDER BY t.transaction_date DESC"""
    return fetch_all(sql, (user_id,))


def get_account_transactions(user_id, account_id):
    """Get the transactions for one of the user's accounts, newest first."""
    sql = """SELECT t.*, a.account_name, c.category_name
             FROM transactions t
             JOIN accounts a ON t.account_id = a.account_id
             JOIN categories c ON t.category_id = c.category_id
             WHERE a.user_id = %s AND t.account_id = %s
             ORDER BY t.transaction_date DESC"""
    return fetch_all(sql, (user_id, account_id))


def get_transaction(user_id, transaction_id):
    """Get one transaction. Returns None if it doesn't belong to this user."""
    sql = """SELECT t.*
             FROM transactions t
             JOIN accounts a ON t.account_id = a.account_id
             WHERE t.transaction_id = %s AND a.user_id = %s"""
    return fetch_one(sql, (transaction_id, user_id))


def delete_transaction(user_id, transaction_id):
    """Delete a transaction. Returns False if it doesn't belong to this user."""
    if get_transaction(user_id, transaction_id) is None:
        return False
    execute("DELETE FROM transactions WHERE transaction_id = %s", (transaction_id,))
    return True


def get_totals(user_id, start_date, end_date):
    """Total income and expenses between two dates, for the dashboard."""
    sql = """SELECT SUM(t.amount) AS total
             FROM transactions t
             JOIN accounts a ON t.account_id = a.account_id
             WHERE a.user_id = %s AND t.transaction_type = %s
             AND t.transaction_date BETWEEN %s AND %s"""
    income = fetch_one(sql, (user_id, "income", start_date, end_date))["total"]
    expenses = fetch_one(sql, (user_id, "expense", start_date, end_date))["total"]

    # SUM returns None when there are no transactions
    if income is None:
        income = 0
    if expenses is None:
        expenses = 0

    return {"income": income, "expenses": expenses}
