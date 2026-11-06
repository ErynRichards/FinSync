
# Import Flask tools needed to create an API endpoint.
from flask import Blueprint, current_app, jsonify

# Import the Dashboard controller.
# Support both project-root and backend-folder execution.
try:
    from backend.app.modules.dashboard.dashboard_controller import DashboardController
except ModuleNotFoundError as error:
    if error.name != "backend":
        raise

    from app.modules.dashboard.dashboard_controller import DashboardController


# Create a separate Blueprint for the Dashboard API.
dashboard_bp = Blueprint("dashboard", __name__)

# Create the controller that prepares the financial information.
dashboard_controller = DashboardController()


@dashboard_bp.route("/", methods=["GET"])
def get_dashboard():
    """
    Retrieve financial information for the FinSync Dashboard.

    The transaction data is temporarily supplied through Flask
    configuration for testing.

    Database integration will replace this temporary data source.
    """

    # Retrieve the temporary transaction data from Flask configuration.
    transactions = current_app.config.get("DASHBOARD_TRANSACTIONS")

    # Check whether a transaction data source has been configured.
    if transactions is None:
        return jsonify({
            "error": "Dashboard transaction data is not yet connected."
        }), 503

    # Retrieve the optional account opening balance.
    opening_balance = current_app.config.get("DASHBOARD_OPENING_BALANCE")

    try:
        # Use the controller to calculate the Dashboard information.
        dashboard_data = dashboard_controller.get_dashboard_data(
            transactions=transactions,
            opening_balance=opening_balance
        )

        # Return the calculated Dashboard information as JSON.
        return jsonify(dashboard_data), 200

    except ValueError as error:
        # Return an error if the supplied financial information is invalid.
        return jsonify({
            "error": str(error)
        }), 422
