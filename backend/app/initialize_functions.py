
from flask import Flask
from flasgger import Swagger
from flask_cors import CORS

from app.modules.main.route import main_bp
from app.modules.dashboard.dashboard_route import dashboard_bp
from app.modules.reports.reporting_route import reporting_bp

from app.db.db import db


def initialize_cors(app: Flask):
    """
    Allow the local FinSync frontend to communicate with Flask.

    Restrict access to the development frontend instead of
    allowing requests from every website.
    """

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://127.0.0.1:5500",
                    "http://localhost:5500"
                ]
            }
        }
    )


def initialize_route(app: Flask):
    with app.app_context():

        # Register the existing Main Blueprint.
        app.register_blueprint(
            main_bp,
            url_prefix='/api/v1/main'
        )

        # Register the existing Dashboard Blueprint.
        app.register_blueprint(
            dashboard_bp,
            url_prefix='/api/v1/dashboard'
        )

        # Register the Interactive Reports Blueprint.
        app.register_blueprint(
            reporting_bp,
            url_prefix='/api/v1/reports'
        )


def initialize_db(app: Flask):
    with app.app_context():
        db.init_app(app)
        db.create_all()


def initialize_swagger(app: Flask):
    with app.app_context():
        swagger = Swagger(app)
        return swagger
