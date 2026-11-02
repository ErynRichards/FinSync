"""
Password-reset routes (Daniel).

  GET  /forgot-password          show the "enter your email" form
  POST /forgot-password          create token + send email (field: email)
  GET  /reset-password/<token>   check the link, show New Password form
  POST /reset-password/<token>   validate + save new password
                                 (fields: password, confirm_password)

Each POST accepts either a normal HTML form or JSON (for fetch() calls):
  JSON in : {"email": "..."}  or  {"password": "...", "confirm_password": "..."}
  JSON out: {"ok": true/false, "message": "...", "errors": [...]}
JSON callers must send the X-CSRFToken header.
"""
import logging

from flask import (Blueprint, current_app, flash, jsonify, redirect,
                   render_template, request, session, url_for)

from .. import reset_tokens
from ..csrf import csrf_protect
from ..db import DatabaseError
from ..email_service import send_password_reset_email
from ..security import (PASSWORD_RULES_TEXT, hash_password, is_valid_email,
                        normalise_email, password_errors, verify_password)
from ..users import get_user_by_email

log = logging.getLogger(__name__)
bp = Blueprint("password_reset", __name__)

# Same message whether or not the account exists (prevents email probing)
GENERIC_SENT_MESSAGE = ("If an account exists for that email address, a password-reset "
                        "link has been sent. Please check your inbox and spam folder.")

TOKEN_MESSAGES = {
    reset_tokens.INVALID: "This password-reset link is invalid. Please request a new one.",
    reset_tokens.EXPIRED: "This password-reset link has expired. Please request a new one.",
    reset_tokens.USED: "This password-reset link has already been used. Please request a new one.",
}


def _wants_json():
    return request.is_json


def _field(name):
    if request.is_json:
        data = request.get_json(silent=True) or {}
        value = data.get(name, "")
        return value if isinstance(value, str) else ""
    return request.form.get(name, "")


# ---------------------------------------------------------------------------
# Forgot password
# ---------------------------------------------------------------------------
@bp.route("/forgot-password", methods=["GET", "POST"])
@csrf_protect
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")

    email = normalise_email(_field("email"))

    if not is_valid_email(email):
        msg = "Please enter a valid email address."
        if _wants_json():
            return jsonify(ok=False, message=msg, errors=[msg]), 400
        return render_template("forgot_password.html", error=msg, email=email), 400

    cfg = current_app.config
    try:
        user = get_user_by_email(email)
        if user is not None:
            recent = reset_tokens.count_recent_requests(user["user_id"], cfg["RESET_WINDOW_MINUTES"])
            if recent >= cfg["RESET_MAX_REQUESTS"]:
                # Silently skip - same response as success, so no information leaks
                log.warning("Reset rate limit reached for user_id=%s", user["user_id"])
            else:
                raw_token, _expires = reset_tokens.create_reset_token(
                    user["user_id"], cfg["RESET_TOKEN_EXPIRY_MINUTES"])
                reset_url = cfg["APP_BASE_URL"] + url_for(
                    "password_reset.reset_password", token=raw_token)
                sent = send_password_reset_email(
                    user["email"], user["first_name"], reset_url, cfg["RESET_TOKEN_EXPIRY_MINUTES"])
                if not sent:
                    log.error("Reset email could not be sent for user_id=%s", user["user_id"])
    except DatabaseError as exc:
        msg = str(exc)
        if _wants_json():
            return jsonify(ok=False, message=msg, errors=[msg]), 503
        return render_template("forgot_password.html", error=msg, email=email), 503

    if _wants_json():
        return jsonify(ok=True, message=GENERIC_SENT_MESSAGE)
    return render_template("forgot_password.html", success=GENERIC_SENT_MESSAGE)


# ---------------------------------------------------------------------------
# Reset password (link from the email)
# ---------------------------------------------------------------------------
def _invalid_link(reason):
    msg = TOKEN_MESSAGES.get(reason, TOKEN_MESSAGES[reset_tokens.INVALID])
    status = 410 if reason in (reset_tokens.EXPIRED, reset_tokens.USED) else 400
    if _wants_json():
        return jsonify(ok=False, message=msg, errors=[msg], reason=reason), status
    return render_template("reset_invalid.html", message=msg), status


@bp.route("/reset-password/<token>", methods=["GET", "POST"])
@csrf_protect
def reset_password(token):
    # 1. Is the link still valid? (checked on GET and again on POST)
    row, reason = reset_tokens.check_token(token)
    if row is None:
        return _invalid_link(reason)

    if request.method == "GET":
        return render_template("reset_password.html", token=token, rules=PASSWORD_RULES_TEXT)

    # 2. Validate the new password on the server
    password = _field("password")
    confirm = _field("confirm_password")
    errors = password_errors(password, confirm)
    if not errors and verify_password(row["password_hash"], password):
        errors.append("Your new password must be different from your current password.")
    if errors:
        if _wants_json():
            return jsonify(ok=False, message=errors[0], errors=errors), 400
        return render_template("reset_password.html", token=token,
                               rules=PASSWORD_RULES_TEXT, errors=errors), 400

    # 3. Save the password and burn the token in one transaction
    ok, reason = reset_tokens.consume_token_and_set_password(token, hash_password(password))
    if not ok:
        return _invalid_link(reason)

    log.info("Password reset completed for user_id=%s", row["user_id"])
    session.clear()   # log out any session in this browser
    msg = "Your password has been reset. You can now log in with your new password."
    if _wants_json():
        return jsonify(ok=True, message=msg, redirect=url_for("auth.login"))
    flash(msg, "success")
    return redirect(url_for("auth.login"))
