"""
=====================================================================
 PLACEHOLDER ROUTES - TO BE REPLACED BY TEAMMATES
=====================================================================
These minimal routes exist ONLY so the password-reset feature can be
tested end-to-end (register -> forget password -> reset -> log in).

  /signup, /login, /dashboard  -> Mishayle (registration, login, sessions)
  /logout                      -> Reece    (logout route)

When replacing them, please keep:
  * blueprint name "auth" and endpoint names login / signup / logout / dashboard
    (the reset page redirects to url_for("auth.login"))
  * users.create_user(...) / users.get_user_by_email(...) for database access
  * security.hash_password(...) / security.verify_password(...) for hashing,
    otherwise passwords set via the reset page will not work at login.
=====================================================================
"""
from functools import wraps

from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)

from ..csrf import csrf_protect
from ..db import DatabaseError, DuplicateEmailError
from ..security import (PASSWORD_RULES_TEXT, hash_password, is_valid_email,
                        normalise_email, password_errors, verify_password)
from ..users import create_user, get_user_by_email, get_user_by_id

bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


@bp.route("/signup", methods=["GET", "POST"])
@csrf_protect
def signup():
    if request.method == "GET":
        return render_template("signup.html", rules=PASSWORD_RULES_TEXT)

    full_name = request.form.get("full_name", "").strip()
    email = normalise_email(request.form.get("email"))
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    errors = []
    if not full_name:
        errors.append("Full name is required.")
    if not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    errors += password_errors(password, confirm)
    if not errors:
        try:
            create_user(full_name, email, hash_password(password))
            flash("Account created. Please log in.", "success")
            return redirect(url_for("auth.login"))
        except DuplicateEmailError as exc:
            errors.append(str(exc))
        except DatabaseError as exc:
            errors.append(str(exc))
    return render_template("signup.html", errors=errors, full_name=full_name,
                           email=email, rules=PASSWORD_RULES_TEXT), 400


@bp.route("/login", methods=["GET", "POST"])
@csrf_protect
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = normalise_email(request.form.get("email"))
    password = request.form.get("password", "")
    try:
        user = get_user_by_email(email)
    except DatabaseError as exc:
        return render_template("login.html", errors=[str(exc)], email=email), 503

    if user is None or not verify_password(user["password_hash"], password):
        return render_template("login.html", errors=["Invalid email or password."], email=email), 401

    session.clear()
    session["user_id"] = user["user_id"]
    return redirect(url_for("auth.dashboard"))


@bp.route("/dashboard")
@login_required
def dashboard():
    user = get_user_by_id(session["user_id"])
    if user is None:
        session.clear()
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html", user=user)


@bp.route("/logout", methods=["POST"])
@csrf_protect
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
