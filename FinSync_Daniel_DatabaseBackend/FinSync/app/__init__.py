"""
FinSync Flask application factory.

create_app() builds the app: loads settings, connects the database
teardown, registers routes (blueprints) and error pages.
"""
import logging
import os

import click
from dotenv import load_dotenv
from flask import Flask, render_template

# Load .env from the project root BEFORE config.py reads the environment
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from .config import Config  # noqa: E402
from .csrf import csrf_token  # noqa: E402
from .db import DatabaseError, check_connection, close_db  # noqa: E402


def create_app(overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY is not set. Copy .env.example to .env and fill it in "
            "(see README, step 5).")
    if app.config["MAIL_BACKEND"] == "console":
        app.logger.warning("MAIL_BACKEND=console: reset emails are printed in this terminal, "
                           "not sent. Use only for local testing.")

    # Database connection is closed at the end of every request
    app.teardown_appcontext(close_db)

    # {{ csrf_token() }} available in every template
    app.jinja_env.globals["csrf_token"] = csrf_token

    from .routes import main, password_reset, placeholders
    app.register_blueprint(main.bp)
    app.register_blueprint(password_reset.bp)
    app.register_blueprint(placeholders.bp)

    _register_error_handlers(app)
    _register_security_headers(app)
    _register_cli(app)
    return app


def _register_error_handlers(app):
    @app.errorhandler(DatabaseError)
    def database_error(exc):
        return render_template("error.html", title="Service unavailable", message=str(exc)), 503

    @app.errorhandler(400)
    def bad_request(exc):
        return render_template("error.html", title="Bad request",
                               message=getattr(exc, "description", "Bad request.")), 400

    @app.errorhandler(404)
    def not_found(_exc):
        return render_template("error.html", title="Page not found",
                               message="The page you requested does not exist."), 404

    @app.errorhandler(500)
    def server_error(_exc):
        return render_template("error.html", title="Something went wrong",
                               message="An unexpected error occurred. Please try again."), 500


def _register_security_headers(app):
    @app.after_request
    def add_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        # Stops the reset token in the URL leaking to other sites via the Referer header
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Cache-Control", "no-store")
        return response


def _register_cli(app):
    @app.cli.command("check-db")
    def check_db_command():
        """Test the MySQL connection:  flask --app run check-db"""
        ok, message = check_connection()
        click.echo(("OK: " if ok else "FAILED: ") + message)
        if not ok:
            click.echo("See the server log above for the exact MySQL error, "
                       "and README > Troubleshooting.")

    @app.cli.command("cleanup-tokens")
    @click.option("--days", default=7, show_default=True)
    def cleanup_tokens_command(days):
        """Delete reset tokens that expired more than N days ago."""
        from .reset_tokens import delete_old_tokens
        click.echo(f"Deleted {delete_old_tokens(days)} old token(s).")
