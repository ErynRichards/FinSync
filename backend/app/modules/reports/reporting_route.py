
"""
FinSync Interactive Reporting API Route.

Provides monthly income and expense information
for the Interactive Reports frontend.
"""

from flask import Blueprint, current_app, jsonify, request

# Import the reporting service.
# Support both project-root and backend-folder execution.
try:
    from backend.reports.reporting_service import build_monthly_reports
except ModuleNotFoundError as error:
    if error.name != "backend":
        raise

    from reports.reporting_service import build_monthly_reports


# Create a separate Blueprint for the Reports API.
reporting_bp = Blueprint("reports", __name__)


@reporting_bp.route("/", methods=["GET"])
def get_monthly_reports():
    """
    Retrieve monthly income and expenses for a selected period.

    Query parameter:
        period: 1, 3, 6 or 12 months. Defaults to 6.

    Example:
        GET /api/v1/reports/?period=6

    Successful response:
        {
            "period": 6,
            "monthly_reports": [
                {
                    "month": "2026-06",
                    "income": "15000.00",
                    "expenses": "4200.00"
                }
            ]
        }
    """

    # Retrieve the selected reporting period.
    period_value = request.args.get("period", "6")

    # Validate the reporting period before processing transactions.
    try:
        period = int(period_value)

        if period not in [1, 3, 6, 12]:
            raise ValueError

    except (TypeError, ValueError):
        return jsonify({
            "error": "Invalid reporting period. Choose 1, 3, 6 or 12 months."
        }), 400

    # Use the existing Dashboard transaction source temporarily.
    transactions = current_app.config.get("DASHBOARD_TRANSACTIONS")

    # Check whether transaction data is available.
    if transactions is None:
        return jsonify({
            "error": "Reporting transaction data is not yet connected."
        }), 503

    try:
        # Calculate the monthly income and expense figures.
        monthly_reports = build_monthly_reports(
            transactions=transactions,
            period=period
        )

        # Return the selected period and monthly figures.
        return jsonify({
            "period": period,
            "monthly_reports": monthly_reports
        }), 200

    except ValueError as error:
        # Return an error if the supplied transaction data is invalid.
        return jsonify({
            "error": str(error)
        }), 422
