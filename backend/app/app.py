
from flask import Flask

from app.config.config import get_config_by_name

from app.initialize_functions import (
    initialize_cors,
    initialize_route,
    initialize_db,
    initialize_swagger
)


def create_app(config=None) -> Flask:
    """
    Create and configure the FinSync Flask application.

    Args:
        config: The configuration object to use.

    Returns:
        A configured Flask application.
    """

    app = Flask(__name__)

    if config:
        app.config.from_object(get_config_by_name(config))

    # Initialize database extensions.
    initialize_db(app)

    # Register the application routes.
    initialize_route(app)

    # Enable CORS for the local development frontend.
    initialize_cors(app)

    # Initialize Swagger documentation.
    initialize_swagger(app)

    return app
