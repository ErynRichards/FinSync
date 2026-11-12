"""
CSRF protection (stops other websites from submitting our forms
on a logged-in user's behalf).

In a template form:   <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
For fetch() calls:    send header  X-CSRFToken: <value of the hidden field>
On a POST route:      put @csrf_protect under the @bp.route(...) line
"""
import hmac
import secrets
from functools import wraps

from flask import abort, request, session

_SESSION_KEY = "_csrf_token"


def csrf_token() -> str:
    if _SESSION_KEY not in session:
        session[_SESSION_KEY] = secrets.token_urlsafe(32)
    return session[_SESSION_KEY]


def csrf_protect(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if request.method == "POST":
            sent = request.form.get("csrf_token") or request.headers.get("X-CSRFToken", "")
            expected = session.get(_SESSION_KEY, "")
            if not expected or not hmac.compare_digest(sent, expected):
                abort(400, description="Your form session expired. Please reload the page and try again.")
        return view(*args, **kwargs)
    return wrapped
