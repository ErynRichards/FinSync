"""Settings integration for the existing root-level FinSync Flask application."""
from flask import Blueprint, jsonify, request, session, render_template, redirect, url_for
from db import DatabaseError, DuplicateEmailError
from security import check_password, check_password_rules, hash_password
from settings_database import (get_profile, update_profile, get_password_hash,
                               update_password_hash, get_preferences, save_preferences)

settings_bp = Blueprint("settings", __name__)


def current_user_id():
    return session.get("user_id")


@settings_bp.get("/settings")
def settings_page():
    if not current_user_id():
        return redirect(url_for("login"))
    return render_template("settings/dashboard.html")


@settings_bp.route("/api/settings/profile", methods=["GET", "PATCH"])
def profile_api():
    user_id = current_user_id()
    if not user_id:
        return jsonify(message="Please log in first."), 401
    if request.method == "GET":
        profile = get_profile(user_id)
        if not profile:
            return jsonify(message="User not found."), 404
        name = (profile["first_name"] + " " + (profile.get("last_name") or "")).strip()
        return jsonify(fullName=name, email=profile["email"], contactNumber=profile.get("phone") or "")
    data = request.get_json(silent=True) or {}
    name = data.get("fullName")
    email = data.get("email")
    phone = data.get("contactNumber", "")
    if not all(isinstance(v, str) for v in (name, email, phone)):
        return jsonify(message="Invalid profile information."), 400
    name, email, phone = name.strip(), email.strip().lower(), phone.strip()
    from security import is_valid_email
    import re
    if not name or not is_valid_email(email):
        return jsonify(message="Please enter a valid name and email."), 400
    if len(name) > 100 or len(email) > 255 or (phone and (len(re.sub(r"\D", "", phone)) < 10 or len(re.sub(r"\D", "", phone)) > 15 or not re.fullmatch(r"\+?[0-9 ()-]+", phone))):
        return jsonify(message="Invalid name, email or phone number."), 400
    first, _, last = name.partition(" ")
    try:
        if get_profile(user_id) is None:
            return jsonify(message="User not found."), 404
        update_profile(user_id, first, last, email, phone or None)
    except DuplicateEmailError:
        return jsonify(message="Email address already in use."), 409
    except DatabaseError:
        return jsonify(message="Could not update profile."), 500
    return jsonify(message="Profile updated successfully.")


@settings_bp.post("/api/settings/change-password")
def change_password():
    # MISHAYLE: Secure password management allocation.
    user_id = current_user_id()
    if not user_id:
        return jsonify(message="Please log in first."), 401
    data = request.get_json(silent=True) or {}
    current = data.get("current_password")
    new = data.get("new_password")
    confirm = data.get("confirm_password")
    if not all(isinstance(v, str) for v in (current, new, confirm)):
        return jsonify(message="Complete all password fields."), 400
    saved_hash = get_password_hash(user_id)
    if not saved_hash or not check_password(saved_hash, current):
        return jsonify(message="Current password is incorrect."), 400
    if current == new:
        return jsonify(message="Choose a different password."), 400
    errors = check_password_rules(new, confirm)
    if errors:
        return jsonify(message=" ".join(errors)), 400
    try:
        update_password_hash(user_id, hash_password(new))
    except DatabaseError:
        return jsonify(message="Password could not be updated."), 500
    return jsonify(message="Password changed successfully."), 200


@settings_bp.route("/api/settings/preferences", methods=["GET", "PUT"])
def preferences_api():
    user_id = current_user_id()
    if not user_id:
        return jsonify(message="Please log in first."), 401
    if request.method == "GET":
        return jsonify(get_preferences(user_id))
    data = request.get_json(silent=True) or {}
    current = get_preferences(user_id)
    theme = data.get("theme", current["theme"])
    budget = data.get("budget_notifications", current["budget_notifications"])
    savings = data.get("savings_notifications", current["savings_notifications"])
    if theme not in ("light", "dark") or not isinstance(budget, bool) or not isinstance(savings, bool):
        return jsonify(message="Invalid preferences."), 400
    try:
        save_preferences(user_id, theme, budget, savings)
    except DatabaseError:
        return jsonify(message="Could not save preferences."), 500
    return jsonify(message="Preferences saved.")
