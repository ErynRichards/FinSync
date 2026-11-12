
# db.py
# MySQL connection and query functions.
# Queries use %s placeholders to prevent SQL injection.

# Load the tools needed in this file.
import pymysql

# Load the tools needed in this file.
import config


# Define DatabaseError for this part of the program.
class DatabaseError(Exception):
    pass


# Define DuplicateEmailError for this part of the program.
class DuplicateEmailError(DatabaseError):
    pass


# Handle get connection requests or data.
def get_connection():
    """Open a connection to the MySQL database."""
    # Try the operation and handle any errors.
    try:
        # Send the result back to the code that called this function.
        return pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,  # rows come back as dictionaries
        )
    except pymysql.MySQLError as error:
        print("Could not connect to MySQL:", error)
        # Stop the operation and report an error.
        raise DatabaseError("The database is unavailable. Please try again later.")


# Handle fetch one requests or data.
def fetch_one(sql, values=()):
    """Run a SELECT and return the first row (or None)."""

    # Get ready to run database queries.
    connection = get_connection()

    # Try the operation and handle any errors.
    try:

        # Get ready to run database queries.
        cursor = connection.cursor()

        # Run the database query using these values.
        cursor.execute(sql, values)

        # Send the result back to the code that called this function.
        return cursor.fetchone()
    except pymysql.MySQLError as error:
        print("Database error:", error)

        # Stop the operation and report an error.
        raise DatabaseError("A database error occurred. Please try again later.")
    finally:
        # Close this resource when finished.
        connection.close()


# Handle fetch all requests or data.
def fetch_all(sql, values=()):
    """Run a SELECT and return all rows."""

    # Get ready to run database queries.
    connection = get_connection()

    # Try the operation and handle any errors.
    try:
        # Get ready to run database queries.

        cursor = connection.cursor()
        # Run the database query using these values.

        cursor.execute(sql, values)
        # Send the result back to the code that called this function.
        return cursor.fetchall()
    except pymysql.MySQLError as error:
        print("Database error:", error)

        # Stop the operation and report an error.
        raise DatabaseError("A database error occurred. Please try again later.")
    finally:
        # Close this resource when finished.
        connection.close()


# Run the requested database operation.
def execute(sql, values=()):
    """Run an INSERT, UPDATE or DELETE. Returns (rows changed, new id)."""

    # Get ready to run database queries.
    connection = get_connection()

    # Try the operation and handle any errors.
    try:
        # Get ready to run database queries.

        cursor = connection.cursor()

        # Keep these records for the next step.
        rows_changed = cursor.execute(sql, values)

        # Save the changes to the database.
        connection.commit()

        # Send the result back to the code that called this function.
        return rows_changed, cursor.lastrowid
    except pymysql.MySQLError as error:

        # Cancel database changes if something goes wrong.
        connection.rollback()
        print("Database error:", error)

        # Check the condition before continuing.
        if error.args[0] == 1062:  # 1062 = duplicate email

            # Stop the operation and report an error.
            raise DuplicateEmailError("An account with that email address already exists.")

        # Stop the operation and report an error.
        raise DatabaseError("A database error occurred. Please try again later.")

    finally:
        # Close this resource when finished.
        connection.close()
