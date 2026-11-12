# Use functions and classes from another file.
from flask import Blueprint, request, jsonify, session

# Use functions and classes from another file.
from db import get_connection

# Load the tools needed in this file.
import pymysql

# Load the tools needed in this file.
import re

# Create the profile blueprint
profile = Blueprint("profile", __name__)


# 1. Get the logged-in user's profile
@profile.route("/profile", methods=["GET"])
def get_profile():

    # Check if the user is logged in
    user_id = session.get("user_id")

    # Check the condition before continuing.
    if not user_id:

        # Send the result back to the code that called this function.
        return jsonify({"error": "Please log in first"}), 401

    # Get ready to run database queries.
    connection = None

    # Try the operation and handle any errors.
    try:
        # Connect to MySQL
        connection = get_connection()

        # Use this resource and close it when finished.
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:

            # Get the user's profile information
            cursor.execute("""
                SELECT first_name, last_name, email, phone, appearance
                FROM users
                WHERE user_id = %s
            """, (user_id,))

            user = cursor.fetchone()

        # Check if the user exists
        if user is None:

            # Send the result back to the code that called this function.
            return jsonify({"error": "User not found"}), 404

        # Return profile details to the frontend
        return jsonify(user), 200

    except Exception:

        # Send the result back to the code that called this function.
        return jsonify({"error": "Could not load profile"}), 500

    finally:

        # Check the condition before continuing.
        if connection:

            # Close this resource when finished.
            connection.close()


# 2. Update the user's profile
@profile.route("/profile", methods=["PUT"])
def update_profile():

    # Check if the user is logged in
    user_id = session.get("user_id")

    # Check the condition before continuing.
    if not user_id:

        # Send the result back to the code that called this function.
        return jsonify({"error": "Please log in first"}), 401

    # Get information from the frontend
    data = request.get_json(silent=True)

    # Check the condition before continuing.
    if not isinstance(data, dict):

        # Send the result back to the code that called this function.
        return jsonify({"error": "Invalid information"}), 400

    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    email = data.get("email", "")
    phone = data.get("phone", "")

    # Check that all values are text
    if not all(isinstance(value, str) for value in
               [first_name, last_name, email, phone]):

        # Send the result back to the code that called this function.
        return jsonify({"error": "Invalid information"}), 400

    # Remove unnecessary spaces
    first_name = first_name.strip()
    last_name = last_name.strip()
    email = email.strip()
    phone = phone.strip()

    # Check required fields
    if not first_name or not last_name or not email:

        # Send the result back to the code that called this function.
        return jsonify({
            "error": "First name, last name and email are required"
        }), 400

    # Validate email address
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):

        # Send the result back to the code that called this function.
        return jsonify({"error": "Invalid email address"}), 400

    # Validate optional phone number
    if phone and not re.fullmatch(r"\+?[0-9 ]{7,15}", phone):

        # Send the result back to the code that called this function.
        return jsonify({"error": "Invalid phone number"}), 400

    # Get ready to run database queries.
    connection = None

    # Try the operation and handle any errors.
    try:
        # Connect to MySQL
        connection = get_connection()

        # Use this resource and close it when finished.
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:

            # Check if the user exists
            cursor.execute("""
                SELECT user_id FROM users
                WHERE user_id = %s
            """, (user_id,))

            # Check the condition before continuing.
            if cursor.fetchone() is None:

                # Send the result back to the code that called this function.
                return jsonify({"error": "User not found"}), 404

            # Check if another user has the same email
            cursor.execute("""
                SELECT user_id FROM users
                WHERE email = %s AND user_id != %s
            """, (email, user_id))

            # Check the condition before continuing.
            if cursor.fetchone():

                # Send the result back to the code that called this function.
                return jsonify({
                    "error": "Email address already in use"
                }), 409

            # Save the updated profile information
            cursor.execute("""
                UPDATE users
                SET first_name = %s,
                    last_name = %s,
                    email = %s,
                    phone = %s
                WHERE user_id = %s
            """, (first_name, last_name, email, phone, user_id))

        # Save changes to the database
        connection.commit()

        # Send the result back to the code that called this function.
        return jsonify({
            "message": "Profile updated successfully"
        }), 200

    except pymysql.err.IntegrityError:
        # Check the condition before continuing.
        if connection:

            # Cancel database changes if something goes wrong.
            connection.rollback()

        # Send the result back to the code that called this function.
        return jsonify({"error": "Email address already in use"}), 409

    except Exception:
        # Check the condition before continuing.
        if connection:

            # Cancel database changes if something goes wrong.
            connection.rollback()

        # Send the result back to the code that called this function.
        return jsonify({"error": "Could not update profile"}), 500

    finally:
        # Check the condition before continuing.
        if connection:

            # Close this resource when finished.
            connection.close()


# 3. Save appearance preference
@profile.route("/appearance", methods=["PUT"])
def update_appearance():

    # Check if the user is logged in
    user_id = session.get("user_id")

    # Check the condition before continuing.
    if not user_id:

        # Send the result back to the code that called this function.
        return jsonify({"error": "Please log in first"}), 401

    # Get the selected appearance
    data = request.get_json(silent=True)

    # Check the condition before continuing.
    if not isinstance(data, dict):

        # Send the result back to the code that called this function.
        return jsonify({"error": "Invalid information"}), 400

    appearance = data.get("appearance")

    # Only allow light or dark mode
    if appearance not in ["light", "dark"]:

        # Send the result back to the code that called this function.
        return jsonify({
            "error": "Please select light or dark mode"
        }), 400

    # Get ready to run database queries.
    connection = None

    # Try the operation and handle any errors.
    try:
        # Connect to MySQL
        connection = get_connection()

        # Use this resource and close it when finished.
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:

            # Check if the user exists
            cursor.execute("""
                SELECT user_id FROM users
                WHERE user_id = %s
            """, (user_id,))

            # Check the condition before continuing.
            if cursor.fetchone() is None:

                # Send the result back to the code that called this function.
                return jsonify({"error": "User not found"}), 404

            # Save the selected appearance
            cursor.execute("""
                UPDATE users
                SET appearance = %s
                WHERE user_id = %s
            """, (appearance, user_id))

        # Save changes to MySQL
        connection.commit()

        # Send the result back to the code that called this function.
        return jsonify({
            "message": "Appearance saved successfully"
        }), 200

    except Exception:
        # Check the condition before continuing.
        if connection:

            # Cancel database changes if something goes wrong.
            connection.rollback()

        # Send the result back to the code that called this function.
        return jsonify({
            "error": "Could not save appearance"
        }), 500

    finally:
        # Check the condition before continuing.
        if connection:

            # Close this resource when finished.
            connection.close()