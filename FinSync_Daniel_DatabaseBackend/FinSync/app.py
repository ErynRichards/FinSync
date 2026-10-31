# app.py
# The main Flask application. Run it with:  python app.py
# Then open http://127.0.0.1:5000 in your browser.

from flask import Flask, flash, redirect, render_template, request, session, url_for

import config
from db import DatabaseError, DuplicateEmailError
from email_service import send_reset_email
from reset_tokens import check_token, create_token, use_token
from security import check_password, check_password_rules, hash_password, is_valid_email
from users import create_user, get_user_by_email, get_user_by_id

app = Flask(__name__)
app.secret_key = config.SECRET_KEY  # needed for sessions and flash messages

if not app.secret_key:
    raise RuntimeError("SECRET_KEY is missing. Copy .env.example to .env and fill it in.")


# If the database is down, show a friendly page instead of crashing
@app.errorhandler(DatabaseError)
def database_error(error):
    return render_template("error.html", message=str(error)), 500


# ---------------------------------------------------------------------
# Landing page (placeholder - Eryn replaces templates/index.html)
# ---------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------
# Sign up, login, dashboard and logout
# PLACEHOLDERS so the password reset can be tested.
# Mishayle replaces signup/login/dashboard, Reece replaces logout.
# ---------------------------------------------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    full_name = request.form["full_name"].strip()
    email = request.form["email"].strip().lower()
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    errors = check_password_rules(password, confirm_password)
    if full_name == "":
        errors.append("Full name is required.")
    if not is_valid_email(email):
        errors.append("Please enter a valid email address.")

    if not errors:
        try:
            create_user(full_name, email, hash_password(password))
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        except DuplicateEmailError as error:
            errors.append(str(error))

    return render_template("signup.html", errors=errors, full_name=full_name, email=email)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form["email"].strip().lower()
    password = request.form["password"]
    user = get_user_by_email(email)

    if user is None or not check_password(user["password_hash"], password):
        return render_template("login.html", errors=["Invalid email or password."], email=email)

    session["user_id"] = user["user_id"]
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))
    user = get_user_by_id(session["user_id"])
    return render_template("dashboard.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------
# Password reset (Daniel)
# ---------------------------------------------------------------------
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")

    email = request.form["email"].strip().lower()
    if not is_valid_email(email):
        error = "Please enter a valid email address."
        return render_template("forgot_password.html", error=error, email=email)

    user = get_user_by_email(email)
    if user is not None:
        token = create_token(user["user_id"])
        reset_link = url_for("reset_password", token=token, _external=True)
        send_reset_email(user["email"], user["first_name"], reset_link)

    # Same message whether or not the account exists, so nobody can find out who is registered
    message = "If an account exists for that email address, a password-reset link has been sent."
    return render_template("forgot_password.html", success=message)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # Check the link first (on both GET and POST)
    token_row, error_message = check_token(token)
    if token_row is None:
        return render_template("reset_invalid.html", message=error_message)

    if request.method == "GET":
        return render_template("reset_password.html", token=token)

    # Check the new password on the server (even if JavaScript already checked it)
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    errors = check_password_rules(password, confirm_password)
    if errors:
        return render_template("reset_password.html", token=token, errors=errors)

    # Save the new password and mark the link as used
    if not use_token(token_row, hash_password(password)):
        message = "This password-reset link has already been used."
        return render_template("reset_invalid.html", message=message)

    session.clear()
    flash("Your password has been reset. You can now log in with your new password.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
