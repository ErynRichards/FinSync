# db.py
# MySQL connection and query functions.
# Queries use %s placeholders to prevent SQL injection.

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
            cursorclass=pymysql.cursors.DictCursor,  # rows come back as dictionaries
        )
    except pymysql.MySQLError as error:
        print("Could not connect to MySQL:", error)
        raise DatabaseError("The database is unavailable. Please try again later.")


def fetch_one(sql, values=()):
    """Run a SELECT and return the first row (or None)."""
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


def fetch_all(sql, values=()):
    """Run a SELECT and return all rows."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(sql, values)
        return cursor.fetchall()
    except pymysql.MySQLError as error:
        print("Database error:", error)
        raise DatabaseError("A database error occurred. Please try again later.")
    finally:
        connection.close()


def execute(sql, values=()):
    """Run an INSERT, UPDATE or DELETE. Returns (rows changed, new id)."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        rows_changed = cursor.execute(sql, values)
        connection.commit()
        return rows_changed, cursor.lastrowid
    except pymysql.MySQLError as error:
        connection.rollback()
        print("Database error:", error)
        if error.args[0] == 1062:  # 1062 = duplicate email
            raise DuplicateEmailError("An account with that email address already exists.")
        raise DatabaseError("A database error occurred. Please try again later.")
    finally:
        connection.close()
