"""Settings integration for the existing root-level FinSync Flask application."""
# Use functions and classes from another file.
from flask import Blueprint, jsonify, request, session, render_template, redirect, url_for

# Use functions and classes from another file.
from db import DatabaseError, DuplicateEmailError

# Use functions and classes from another file.
from security import check_password, check_password_rules, hash_password

# Use functions and classes from another file.
from settings_database import (get_profile, update_profile, get_password_hash,
                               update_password_hash, get_preferences, save_preferences)

settings_bp = Blueprint("settings", __name__)


# Handle current user id requests or data.
def current_user_id():

    # Send the result back to the code that called this function.
    return session.get("user_id")


# Handle settings page requests or data.
@settings_bp.get("/settings")
def settings_page():

    # Check the condition before continuing.
    if not current_user_id():

        # Send the result back to the code that called this function.
        return redirect(url_for("login"))

    # Send the result back to the code that called this function.
    return render_template("settings/dashboard.html")


# Handle profile api requests or data.
@settings_bp.route("/api/settings/profile", methods=["GET", "PATCH"])
def profile_api():

    # Keep the ID of the record being used.
    user_id = current_user_id()

    # Check the condition before continuing.
    if not user_id:

        # Send the result back to the code that called this function.
        return jsonify(message="Please log in first."), 401

    # Check the condition before continuing.
    if request.method == "GET":
        profile = get_profile(user_id)

        # Check the condition before continuing.
        if not profile:

            # Send the result back to the code that called this function.
            return jsonify(message="User not found."), 404
        name = (profile["first_name"] + " " + (profile.get("last_name") or "")).strip()

        # Send the result back to the code that called this function.
        return jsonify(fullName=name, email=profile["email"], contactNumber=profile.get("phone") or "")


    data = request.get_json(silent=True) or {}
    name = data.get("fullName")
    email = data.get("email")
    phone = data.get("contactNumber", "")

    # Check the condition before continuing.
    if not all(isinstance(v, str) for v in (name, email, phone)):

        # Send the result back to the code that called this function.
        return jsonify(message="Invalid profile information."), 400
    name, email, phone = name.strip(), email.strip().lower(), phone.strip()


    # Use functions and classes from another file.
    from security import is_valid_email

    # Load the tools needed in this file.
    import re
    # Check the condition before continuing.


    if not name or not is_valid_email(email):
        # Send the result back to the code that called this function.

        return jsonify(message="Please enter a valid name and email."), 400

    # Check the condition before continuing.
    if len(name) > 100 or len(email) > 255 or (phone and (len(re.sub(r"\D", "", phone)) < 10 or len(re.sub(r"\D", "", phone)) > 15 or not re.fullmatch(r"\+?[0-9 ()-]+", phone))):

        # Send the result back to the code that called this function.
        return jsonify(message="Invalid name, email or phone number."), 400
    first, _, last = name.partition(" ")

    # Try the operation and handle any errors.
    try:
        # Check the condition before continuing.
        if get_profile(user_id) is None:

            # Send the result back to the code that called this function.
            return jsonify(message="User not found."), 404
        update_profile(user_id, first, last, email, phone or None)
    except DuplicateEmailError:

        # Send the result back to the code that called this function.
        return jsonify(message="Email address already in use."), 409
    except DatabaseError:

        # Send the result back to the code that called this function.
        return jsonify(message="Could not update profile."), 500

    # Send the result back to the code that called this function.
    return jsonify(message="Profile updated successfully.")


# Handle change password requests or data.
@settings_bp.post("/api/settings/change-password")
def change_password():

    # MISHAYLE: Secure password management allocation.
    user_id = current_user_id()

    # Check the condition before continuing.
    if not user_id:

        # Send the result back to the code that called this function.
        return jsonify(message="Please log in first."), 401
    data = request.get_json(silent=True) or {}
    current = data.get("current_password")
    new = data.get("new_password")
    confirm = data.get("confirm_password")

    # Check the condition before continuing.

    if not all(isinstance(v, str) for v in (current, new, confirm)):

        # Send the result back to the code that called this function.
        return jsonify(message="Complete all password fields."), 400
    saved_hash = get_password_hash(user_id)

    # Check the condition before continuing.
    if not saved_hash or not check_password(saved_hash, current):

        # Send the result back to the code that called this function.
        return jsonify(message="Current password is incorrect."), 400

    # Check the condition before continuing.
    if current == new:

        # Send the result back to the code that called this function.
        return jsonify(message="Choose a different password."), 400

    # Collect any input errors to show the user.
    errors = check_password_rules(new, confirm)

    # Check the condition before continuing.
    if errors:

        # Send the result back to the code that called this function.
        return jsonify(message=" ".join(errors)), 400

    # Try the operation and handle any errors.
    try:
        update_password_hash(user_id, hash_password(new))
    except DatabaseError:

        # Send the result back to the code that called this function.
        return jsonify(message="Password could not be updated."), 500

    # Send the result back to the code that called this function.
    return jsonify(message="Password changed successfully."), 200


# Handle preferences api requests or data.
@settings_bp.route("/api/settings/preferences", methods=["GET", "PUT"])
def preferences_api():

    # Keep the ID of the record being used.
    user_id = current_user_id()

    # Check the condition before continuing.
    if not user_id:

        # Send the result back to the code that called this function.
        return jsonify(message="Please log in first."), 401

    # Check the condition before continuing.
    if request.method == "GET":

        # Send the result back to the code that called this function.
        return jsonify(get_preferences(user_id))
    data = request.get_json(silent=True) or {}
    current = get_preferences(user_id)
    theme = data.get("theme", current["theme"])

    # Save an amount for a calculation or database update.
    budget = data.get("budget_notifications", current["budget_notifications"])
    savings = data.get("savings_notifications", current["savings_notifications"])

    # Check the condition before continuing.
    if theme not in ("light", "dark") or not isinstance(budget, bool) or not isinstance(savings, bool):

        # Send the result back to the code that called this function.
        return jsonify(message="Invalid preferences."), 400

    # Try the operation and handle any errors.
    try:
        save_preferences(user_id, theme, budget, savings)
    except DatabaseError:

        # Send the result back to the code that called this function.
        return jsonify(message="Could not save preferences."), 500

    # Send the result back to the code that called this function.
    return jsonify(message="Preferences saved.")
