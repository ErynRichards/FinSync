"""
Landing page placeholder (Eryn's page replaces templates/dashboard.html) and a
database health check for troubleshooting.
"""
# Use functions and classes from another file.
from flask import Blueprint, jsonify, render_template

# Use functions and classes from another file.
from ..db import check_connection

# Set up the Flask application or its routes.
bp = Blueprint("main", __name__)


# Handle index requests or data.
@bp.route("/")
def index():
    # Send the result back to the code that called this function.
    return render_template("dashboard.html")


# Handle health db requests or data.
@bp.route("/health/db")
def health_db():
    ok, _detail = check_connection()   # detail stays server-side
    # Send the result back to the code that called this function.
    return jsonify(database="ok" if ok else "unavailable"), (200 if ok else 503)
