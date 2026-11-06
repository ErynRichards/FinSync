#MISHAYLE
from decimal import Decimal, InvalidOperation
from datetime import date
from db import get_connection

class TransactionValidationError(ValueError):
    pass

#validating transactions
def validate_transaction(data):
    """Check form values before saving a transaction."""
    try:
        account_id = int(data.get("account_id", ""))
        category_id = int(data.get("category_id", ""))
    except (TypeError, ValueError):
        raise TransactionValidationError(
            "Please select an account and category."
        )

    if account_id <= 0 or category_id <= 0:
        raise TransactionValidationError(
            "Please select an account and category."
        )

    transaction_type = str(
        data.get("transaction_type", "")
    ).strip().lower()

    if transaction_type not in ("income", "expense"):
        raise TransactionValidationError(
            "Please select income or expense."
        )

    try:
        amount = Decimal(str(data.get("amount", "")).strip())
    except (InvalidOperation, ValueError):
        raise TransactionValidationError(
            "Please enter a valid amount."
        )

    if not amount.is_finite() or amount <= 0 or amount > Decimal("9999999999.99"):
        raise TransactionValidationError(
            "Amount must be greater than zero and within the allowed range."
        )

    if amount.as_tuple().exponent < -2:
        raise TransactionValidationError(
            "Amount cannot have more than two decimal places."
        )

    try:
        transaction_date = date.fromisoformat(
            str(data.get("transaction_date", ""))
        )
    except (ValueError, TypeError):
        raise TransactionValidationError(
            "Please enter a valid date."
        )

    description = str(data.get("description", "")).strip()

    if len(description) > 255:
        raise TransactionValidationError(
            "Description must be 255 characters or less."
        )

    return account_id, category_id, transaction_type, amount, transaction_date, description

#checking account and category before saving
#checks if account belongs to logged-in user
#checks if category exists and matches the transaction type
def check_account_and_category(connection, user_id, account_id, category_id, kind):

    with connection.cursor() as cursor:

        # Check that the account belongs to the user
        cursor.execute("""
            SELECT account_id
            FROM accounts
            WHERE account_id = %s AND user_id = %s
        """, (account_id, user_id))

        if cursor.fetchone() is None:
            raise TransactionValidationError(
                "Invalid account selected."
            )

        # Check that the category exists and matches income/expense
        cursor.execute("""
            SELECT category_id
            FROM categories
            WHERE category_id = %s AND category_type = %s
        """, (category_id, kind))

        if cursor.fetchone() is None:
            raise TransactionValidationError(
                "Invalid category selected."
            )

#adding transactions
def add_transaction(user_id, data):
    """Save a new transaction and return its ID."""
    account_id, category_id, kind, amount, when, description = validate_transaction(data)
    connection = get_connection()

    try:
        check_account_and_category(
            connection, user_id, account_id, category_id, kind
        )

        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO transactions
                (account_id, category_id, transaction_type, amount,
                 transaction_date, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())""",
                (account_id, category_id, kind, amount, when, description))

            new_id = cursor.lastrowid

        connection.commit()
        return new_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


#viewing transactions
def get_transactions(user_id):
    """Shared with Eryn and Reece: only transactions belonging to this user."""
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT t.transaction_id, t.account_id, a.account_name,
                t.category_id, c.category_name, t.transaction_type,
                t.amount, t.transaction_date, t.description, t.created_at
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                JOIN categories c ON t.category_id = c.category_id
                WHERE a.user_id = %s""", (user_id,))

            return cursor.fetchall()

    finally:
        connection.close()

#editing a transaction
def edit_transaction(user_id, transaction_id, data):
    """Update a transaction if the logged-in user owns it."""
    account_id, category_id, kind, amount, when, description = validate_transaction(data)
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT t.transaction_id FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE t.transaction_id = %s AND a.user_id = %s FOR UPDATE""",
                (transaction_id, user_id))

            if cursor.fetchone() is None:
                return False

            check_account_and_category(
                connection, user_id, account_id, category_id, kind
            )

            cursor.execute("""UPDATE transactions SET account_id = %s,
                category_id = %s, transaction_type = %s, amount = %s,
                transaction_date = %s, description = %s
                WHERE transaction_id = %s""",
                (account_id, category_id, kind, amount,
                 when, description, transaction_id))

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


#deleting a transaction
def delete_transaction(user_id, transaction_id):
    """Delete only a transaction belonging to the logged-in user."""
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""DELETE t FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE t.transaction_id = %s AND a.user_id = %s""",
                (transaction_id, user_id))

            deleted = cursor.rowcount > 0

        connection.commit()
        return deleted

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def get_accounts(user_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT account_id, account_name FROM accounts WHERE user_id = %s", (user_id,))
            return cursor.fetchall()
    finally:
        connection.close()

def get_categories():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT category_id, category_name, category_type FROM categories ORDER BY category_name")
            return cursor.fetchall()
    finally:
        connection.close()
