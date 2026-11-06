from flask import Flask
from flasgger import Swagger
from app.modules.main.route import main_bp
from app.modules.dashboard.dashboard_route import dashboard_bp
from app.db.db import db


def initialize_route(app: Flask):
    with app.app_context():
        # Register the existing Main Blueprint.
        app.register_blueprint(main_bp, url_prefix='/api/v1/main')

        # Register the Dashboard Blueprint.
        app.register_blueprint(dashboard_bp, url_prefix='/api/v1/dashboard')


def initialize_db(app: Flask):
    with app.app_context():
        db.init_app(app)
        db.create_all()


def initialize_swagger(app: Flask):
    with app.app_context():
        swagger = Swagger(app)
        return swagger