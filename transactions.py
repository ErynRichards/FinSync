#MISHAYLE
from decimal import Decimal, InvalidOperation
# Use functions and classes from another file.
from datetime import date
# Use functions and classes from another file.
from db import get_connection

# Define TransactionValidationError for this part of the program.
class TransactionValidationError(ValueError):
    pass

#validating transactions
def validate_transaction(data):

    """Check form values before saving a transaction."""
    # Try the operation and handle any errors.
    try:

        # Keep the ID of the record being used.
        account_id = int(data.get("account_id", ""))

        # Keep the ID of the record being used.
        category_id = int(data.get("category_id", ""))
    except (TypeError, ValueError):

        # Stop the operation and report an error.
        raise TransactionValidationError(
            "Please select an account and category."
        )

    # Check the condition before continuing.
    if account_id <= 0 or category_id <= 0:

        # Stop the operation and report an error.
        raise TransactionValidationError(
            "Please select an account and category."
        )

    transaction_type = str(
        data.get("transaction_type", "")
    ).strip().lower()

    # Check the condition before continuing.
    if transaction_type not in ("income", "expense"):

        # Stop the operation and report an error.
        raise TransactionValidationError(
            "Please select income or expense."
        )

    # Try the operation and handle any errors.
    try:

        # Save an amount for a calculation or database update.
        amount = Decimal(str(data.get("amount", "")).strip())

    except (InvalidOperation, ValueError):
        # Stop the operation and report an error.
        raise TransactionValidationError(
            "Please enter a valid amount."
        )

    # Check the condition before continuing.
    if not amount.is_finite() or amount <= 0 or amount > Decimal("9999999999.99"):

        # Stop the operation and report an error.
        raise TransactionValidationError(
            "Amount must be greater than zero and within the allowed range."
        )

    # Check the condition before continuing.
    if amount.as_tuple().exponent < -2:

        # Stop the operation and report an error.
        raise TransactionValidationError(
            "Amount cannot have more than two decimal places."
        )

    # Try the operation and handle any errors.
    try:
        transaction_date = date.fromisoformat(
            str(data.get("transaction_date", ""))
        )
    except (ValueError, TypeError):

        # Stop the operation and report an error.
        raise TransactionValidationError(
            "Please enter a valid date."
        )

    description = str(data.get("description", "")).strip()

    # Check the condition before continuing.
    if len(description) > 255:

        # Stop the operation and report an error.
        raise TransactionValidationError(
            "Description must be 255 characters or less."
        )

    # Send the result back to the code that called this function.
    return account_id, category_id, transaction_type, amount, transaction_date, description

#checking account and category before saving
#checks if account belongs to logged-in user
#checks if category exists and matches the transaction type
def check_account_and_category(connection, user_id, account_id, category_id, kind):

    # Use this resource and close it when finished.
    with connection.cursor() as cursor:

        # Check that the account belongs to the user
        cursor.execute("""
            SELECT account_id
            FROM accounts
            WHERE account_id = %s AND user_id = %s
        """, (account_id, user_id))

        # Check the condition before continuing.
        if cursor.fetchone() is None:

            # Stop the operation and report an error.
            raise TransactionValidationError(
                "Invalid account selected."
            )

        # Check that the category exists and matches income/expense
        cursor.execute("""
            SELECT category_id
            FROM categories
            WHERE category_id = %s AND category_type = %s
        """, (category_id, kind))

        # Check the condition before continuing.
        if cursor.fetchone() is None:

            # Stop the operation and report an error.
            raise TransactionValidationError(
                "Invalid category selected."
            )

#adding transactions
def add_transaction(user_id, data):
    """Save a new transaction and return its ID."""
    account_id, category_id, kind, amount, when, description = validate_transaction(data)

    # Get ready to run database queries.
    connection = get_connection()

    # Try the operation and handle any errors.
    try:
        check_account_and_category(
            connection, user_id, account_id, category_id, kind
        )

        # Use this resource and close it when finished.
        with connection.cursor() as cursor:

            # Run the database query using these values.
            cursor.execute("""INSERT INTO transactions
                (account_id, category_id, transaction_type, amount,
                 transaction_date, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())""",
                (account_id, category_id, kind, amount, when, description))

            new_id = cursor.lastrowid

        # Save the changes to the database.
        connection.commit()

        # Send the result back to the code that called this function.
        return new_id

    except Exception:
        # Cancel database changes if something goes wrong.
        connection.rollback()

        # Stop the operation and report an error.
        raise

    finally:
        # Close this resource when finished.
        connection.close()


#viewing transactions
def get_transactions(user_id):
    """Shared with Eryn and Reece: only transactions belonging to this user."""

    # Get ready to run database queries.
    connection = get_connection()

    # Try the operation and handle any errors.
    try:

        # Use this resource and close it when finished.
        with connection.cursor() as cursor:

            # Run the database query using these values.
            cursor.execute("""SELECT t.transaction_id, t.account_id, a.account_name,
                t.category_id, c.category_name, t.transaction_type,
                t.amount, t.transaction_date, t.description, t.created_at
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                JOIN categories c ON t.category_id = c.category_id
                WHERE a.user_id = %s""", (user_id,))

            # Send the result back to the code that called this function.
            return cursor.fetchall()

    finally:

        # Close this resource when finished.
        connection.close()

#editing a transaction
def edit_transaction(user_id, transaction_id, data):
    """Update a transaction if the logged-in user owns it."""
    account_id, category_id, kind, amount, when, description = validate_transaction(data)

    # Get ready to run database queries.
    connection = get_connection()

    # Try the operation and handle any errors.
    try:

        # Use this resource and close it when finished.
        with connection.cursor() as cursor:

            # Run the database query using these values.
            cursor.execute("""SELECT t.transaction_id FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE t.transaction_id = %s AND a.user_id = %s FOR UPDATE""",
                (transaction_id, user_id))

            # Check the condition before continuing.
            if cursor.fetchone() is None:

                # Send the result back to the code that called this function.
                return False

            check_account_and_category(
                connection, user_id, account_id, category_id, kind
            )

            # Run the database query using these values.
            cursor.execute("""UPDATE transactions SET account_id = %s,
                category_id = %s, transaction_type = %s, amount = %s,
                transaction_date = %s, description = %s
                WHERE transaction_id = %s""",
                (account_id, category_id, kind, amount,
                 when, description, transaction_id))

        # Save the changes to the database.
        connection.commit()

        # Send the result back to the code that called this function.
        return True

    except Exception:
        # Cancel database changes if something goes wrong.
        connection.rollback()

        # Stop the operation and report an error.
        raise

    finally:
        # Close this resource when finished.
        connection.close()


#deleting a transaction
def delete_transaction(user_id, transaction_id):
    """Delete only a transaction belonging to the logged-in user."""

    # Get ready to run database queries.
    connection = get_connection()

    # Try the operation and handle any errors.
    try:

        # Use this resource and close it when finished.
        with connection.cursor() as cursor:

            # Run the database query using these values.
            cursor.execute("""DELETE t FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE t.transaction_id = %s AND a.user_id = %s""",
                (transaction_id, user_id))

            deleted = cursor.rowcount > 0

        # Save the changes to the database.
        connection.commit()

        # Send the result back to the code that called this function.
        return deleted

    except Exception:
        # Cancel database changes if something goes wrong.
        connection.rollback()

        # Stop the operation and report an error.
        raise

    finally:
        # Close this resource when finished.
        connection.close()

# Handle get accounts requests or data.
def get_accounts(user_id):

    # Get ready to run database queries.
    connection = get_connection()

    # Try the operation and handle any errors.
    try:
        # Use this resource and close it when finished.
        with connection.cursor() as cursor:

            # Run the database query using these values.
            cursor.execute("SELECT account_id, account_name FROM accounts WHERE user_id = %s", (user_id,))

            # Send the result back to the code that called this function.
            return cursor.fetchall()
    finally:

        # Close this resource when finished.
        connection.close()

# Handle get categories requests or data.
def get_categories():

    # Get ready to run database queries.
    connection = get_connection()

    # Try the operation and handle any errors.
    try:
        # Use this resource and close it when finished.
        with connection.cursor() as cursor:

            # Run the database query using these values.
            cursor.execute("SELECT category_id, category_name, category_type FROM categories ORDER BY category_name")

            # Send the result back to the code that called this function.
            return cursor.fetchall()
    finally:
        # Close this resource when finished.
        connection.close()
