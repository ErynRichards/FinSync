# MISHAYLE: Reports routes integrated with FinSync's existing authentication and MySQL.
from datetime import date, datetime, timedelta

# Use functions and classes from another file.
from flask import Blueprint, jsonify, request, session

# Use functions and classes from another file.
from transactions import get_transactions

# Use functions and classes from another file.
from backend.reports.reporting_service import build_monthly_reports, get_reporting_months

# Use functions and classes from another file.
from backend.reports.spending_analysis import analyse_spending

reports_bp = Blueprint("reports", __name__)


# Handle user transactions requests or data.
def user_transactions():

    # Keep these records for the next step.
    rows = get_transactions(session["user_id"])
    result = []

    # Go through each item one at a time.
    for row in rows:
        item = dict(row)
        value = item["transaction_date"]
        item["transaction_date"] = value.isoformat() if hasattr(value, "isoformat") else str(value)

        # Add this item to the list of results.
        result.append(item)

    # Send the result back to the code that called this function.
    return result


# Handle monthly reports api requests or data.
@reports_bp.route("/api/reports", methods=["GET"])
def monthly_reports_api():

    # Check the condition before continuing.
    if "user_id" not in session:

        # Send the result back to the code that called this function.
        return jsonify({"error": "Please log in first"}), 401

    # Try the operation and handle any errors.
    try:
        period = int(request.args.get("period", "6"))
        # Check the condition before continuing.

        if period not in (1, 3, 6, 12):

            # Send the result back to the code that called this function.
            return jsonify({"error": "Period must be 1, 3, 6 or 12"}), 400
        months = get_reporting_months(period)
        monthly = build_monthly_reports(user_transactions(), period)

        # Send the result back to the code that called this function.
        return jsonify({"period":period, "months":months, "monthly_reports":monthly})
    except ValueError as error:

        # Send the result back to the code that called this function.
        return jsonify({"error":str(error)}), 400


# Handle spending reports api requests or data.
@reports_bp.route("/api/reports/spending", methods=["GET"])
def spending_reports_api():

    # Check the condition before continuing.
    if "user_id" not in session:

        # Send the result back to the code that called this function.
        return jsonify({"error": "Please log in first"}), 401
    month = request.args.get("month", "")
    period = request.args.get("range", "month")

    # Check the condition before continuing.
    if period not in ("week", "month"):

        # Send the result back to the code that called this function.
        return jsonify({"error":"Invalid spending period"}), 400

    # Try the operation and handle any errors.
    try:
        year, number = map(int, month.split("-"))
        month_start = date(year, number, 1)
    except (ValueError, TypeError):

        # Send the result back to the code that called this function.
        return jsonify({"error":"Invalid month"}), 400

    # Check the condition before continuing.
    if period == "week":

        # Last seven days of the selected month (or through today if current month).
        last_day = date(year + (number == 12), (number % 12) + 1, 1) - timedelta(days=1)
        end = min(date.today(), last_day) if month_start <= date.today() <= last_day else last_day
        start = max(month_start, end - timedelta(days=6))
    else:
        start = month_start
        end = date(year + (number == 12), (number % 12) + 1, 1) - timedelta(days=1)

    # Keep these records for the next step.
    transactions = []

    # Go through each item one at a time.
    for row in user_transactions():
        transaction_date = date.fromisoformat(row["transaction_date"][:10])

        # Check the condition before continuing.
        if start <= transaction_date <= end:

            # Add this item to the list of results.
            transactions.append({
                "type":row["transaction_type"],
                "category":row.get("category_name") or "Other",
                "amount":row["amount"]
            })
    # Send the result back to the code that called this function.
    return jsonify(analyse_spending(transactions))
