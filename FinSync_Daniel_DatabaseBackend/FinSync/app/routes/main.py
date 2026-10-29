"""
Landing page placeholder (Eryn's page replaces templates/index.html) and a
database health check for troubleshooting.
"""
from flask import Blueprint, jsonify, render_template

from ..db import check_connection

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/health/db")
def health_db():
    ok, _detail = check_connection()   # detail stays server-side
    return jsonify(database="ok" if ok else "unavailable"), (200 if ok else 503)
