# db.py
# Connects to the MySQL database and runs queries.
# The %s placeholders in the queries keep them safe from SQL injection.

import pymysql

import config


class DatabaseError(Exception):
    pass


class DuplicateEmailError(DatabaseError):
    pass


def get_connection():
    """Open a connection to the MySQL database."""
    try:
        return pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,  # each row is returned as a dictionary
        )
    except pymysql.MySQLError as error:
        print("Could not connect to MySQL:", error)
        raise DatabaseError("The database is unavailable. Please try again later.")


def fetch_one(sql, values=()):
    """Run a SELECT query and return the first row (or None)."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(sql, values)
        return cursor.fetchone()
    except pymysql.MySQLError as error:
        print("Database error:", error)
        raise DatabaseError("A database error occurred. Please try again later.")
    finally:
        connection.close()


def execute(sql, values=()):
    """Run an INSERT, UPDATE or DELETE query and save the change.
    Returns the number of rows changed and the id of the new row."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        rows_changed = cursor.execute(sql, values)
        connection.commit()
        return rows_changed, cursor.lastrowid
    except pymysql.MySQLError as error:
        connection.rollback()
        print("Database error:", error)
        if error.args[0] == 1062:  # MySQL error 1062 = this email is already used
            raise DuplicateEmailError("An account with that email address already exists.")
        raise DatabaseError("A database error occurred. Please try again later.")
    finally:
        connection.close()
