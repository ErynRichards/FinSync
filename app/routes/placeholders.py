# Use functions and classes from another file.
from functools import wraps

# Use functions and classes from another file.
from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)

# Use functions and classes from another file.
from ..csrf import csrf_protect
# Use functions and classes from another file.
from ..db import DatabaseError, DuplicateEmailError
# Use functions and classes from another file.
from ..security import (PASSWORD_RULES_TEXT, hash_password, is_valid_email,
                        normalise_email, password_errors, verify_password)
# Use functions and classes from another file.
from ..users import create_user, get_user_by_email, get_user_by_id

# Set up the Flask application or its routes.
bp = Blueprint("auth", __name__)


# Handle login required requests or data.
def login_required(view):
    # Check access before running the function.
    @wraps(view)
    def wrapped(*args, **kwargs):
        # Check the condition before continuing.
        if "user_id" not in session:
            flash("Please log in first.", "error")
            # Send the result back to the code that called this function.
            return redirect(url_for("auth.login"))
        # Send the result back to the code that called this function.
        return view(*args, **kwargs)
    # Send the result back to the code that called this function.
    return wrapped


# Handle registration form submission, validate details, and create a user account.
@bp.route("/signup", methods=["GET", "POST"])
@csrf_protect
def signup():
    # Check the condition before continuing.
    if request.method == "GET":
        # Send the result back to the code that called this function.
        return render_template("signup.html", rules=PASSWORD_RULES_TEXT)

    full_name = request.form.get("full_name", "").strip()
    email = normalise_email(request.form.get("email"))
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    # Collect any input errors to show the user.
    errors = []
    # Check the condition before continuing.
    if not full_name:
        # Add this item to the list of results.
        errors.append("Full name is required.")
    # Check the condition before continuing.
    if not is_valid_email(email):
        # Add this item to the list of results.
        errors.append("Please enter a valid email address.")
    errors += password_errors(password, confirm)
    # Check the condition before continuing.
    if not errors:
        # Try the operation and handle any errors.
        try:
            create_user(full_name, email, hash_password(password))
            flash("Account created. Please log in.", "success")
            # Send the result back to the code that called this function.
            return redirect(url_for("auth.login"))
        except DuplicateEmailError as exc:
            # Add this item to the list of results.
            errors.append(str(exc))
        except DatabaseError as exc:
            # Add this item to the list of results.
            errors.append(str(exc))
    # Send the result back to the code that called this function.
    return render_template("signup.html", errors=errors, full_name=full_name,
                           email=email, rules=PASSWORD_RULES_TEXT), 400


# Check login details and remember the logged in user.
@bp.route("/login", methods=["GET", "POST"])
@csrf_protect
def login():
    # Check the condition before continuing.
    if request.method == "GET":
        # Send the result back to the code that called this function.
        return render_template("login.html")

    email = normalise_email(request.form.get("email"))
    password = request.form.get("password", "")
    # Try the operation and handle any errors.
    try:
        user = get_user_by_email(email)
    except DatabaseError as exc:
        # Send the result back to the code that called this function.
        return render_template("login.html", errors=[str(exc)], email=email), 503

    # Check the condition before continuing.
    if user is None or not verify_password(user["password_hash"], password):
        # Send the result back to the code that called this function.
        return render_template("login.html", errors=["Invalid email or password."], email=email), 401

    session.clear()
    session["user_id"] = user["user_id"]
    # Send the result back to the code that called this function.
    return redirect(url_for("auth.dashboard"))


# Handle dashboard requests or data.
@bp.route("/dashboard")
@login_required
def dashboard():
    user = get_user_by_id(session["user_id"])
    # Check the condition before continuing.
    if user is None:
        session.clear()
        # Send the result back to the code that called this function.
        return redirect(url_for("auth.login"))
    # Send the result back to the code that called this function.
    return render_template("dashboard.html", user=user)


# End the current login session and return the user to a public page.
@bp.route("/logout", methods=["POST"])
@csrf_protect
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    # Send the result back to the code that called this function.
    return redirect(url_for("auth.login"))
