from flask import Blueprint, request, jsonify, session
from db import get_connection
import pymysql
import re

# Create the profile blueprint
profile = Blueprint("profile", __name__)


# 1. Get the logged-in user's profile
@profile.route("/profile", methods=["GET"])
def get_profile():

    # Check if the user is logged in
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    connection = None

    try:
        # Connect to MySQL
        connection = get_connection()

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
            return jsonify({"error": "User not found"}), 404

        # Return profile details to the frontend
        return jsonify(user), 200

    except Exception:
        return jsonify({"error": "Could not load profile"}), 500

    finally:
        if connection:
            connection.close()


# 2. Update the user's profile
@profile.route("/profile", methods=["PUT"])
def update_profile():

    # Check if the user is logged in
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    # Get information from the frontend
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid information"}), 400

    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    email = data.get("email", "")
    phone = data.get("phone", "")

    # Check that all values are text
    if not all(isinstance(value, str) for value in
               [first_name, last_name, email, phone]):
        return jsonify({"error": "Invalid information"}), 400

    # Remove unnecessary spaces
    first_name = first_name.strip()
    last_name = last_name.strip()
    email = email.strip()
    phone = phone.strip()

    # Check required fields
    if not first_name or not last_name or not email:
        return jsonify({
            "error": "First name, last name and email are required"
        }), 400

    # Validate email address
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({"error": "Invalid email address"}), 400

    # Validate optional phone number
    if phone and not re.fullmatch(r"\+?[0-9 ]{7,15}", phone):
        return jsonify({"error": "Invalid phone number"}), 400

    connection = None

    try:
        # Connect to MySQL
        connection = get_connection()

        with connection.cursor(pymysql.cursors.DictCursor) as cursor:

            # Check if the user exists
            cursor.execute("""
                SELECT user_id FROM users
                WHERE user_id = %s
            """, (user_id,))

            if cursor.fetchone() is None:
                return jsonify({"error": "User not found"}), 404

            # Check if another user has the same email
            cursor.execute("""
                SELECT user_id FROM users
                WHERE email = %s AND user_id != %s
            """, (email, user_id))

            if cursor.fetchone():
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

        return jsonify({
            "message": "Profile updated successfully"
        }), 200

    except pymysql.err.IntegrityError:
        if connection:
            connection.rollback()
        return jsonify({"error": "Email address already in use"}), 409

    except Exception:
        if connection:
            connection.rollback()
        return jsonify({"error": "Could not update profile"}), 500

    finally:
        if connection:
            connection.close()


# 3. Save appearance preference
@profile.route("/appearance", methods=["PUT"])
def update_appearance():

    # Check if the user is logged in
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    # Get the selected appearance
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid information"}), 400

    appearance = data.get("appearance")

    # Only allow light or dark mode
    if appearance not in ["light", "dark"]:
        return jsonify({
            "error": "Please select light or dark mode"
        }), 400

    connection = None

    try:
        # Connect to MySQL
        connection = get_connection()

        with connection.cursor(pymysql.cursors.DictCursor) as cursor:

            # Check if the user exists
            cursor.execute("""
                SELECT user_id FROM users
                WHERE user_id = %s
            """, (user_id,))

            if cursor.fetchone() is None:
                return jsonify({"error": "User not found"}), 404

            # Save the selected appearance
            cursor.execute("""
                UPDATE users
                SET appearance = %s
                WHERE user_id = %s
            """, (appearance, user_id))

        # Save changes to MySQL
        connection.commit()

        return jsonify({
            "message": "Appearance saved successfully"
        }), 200

    except Exception:
        if connection:
            connection.rollback()
        return jsonify({
            "error": "Could not save appearance"
        }), 500

    finally:
        if connection:
            connection.close()