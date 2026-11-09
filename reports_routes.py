# MISHAYLE: Reports routes integrated with FinSync's existing authentication and MySQL.
from datetime import date, datetime, timedelta
from flask import Blueprint, jsonify, request, session
from transactions import get_transactions
from backend.reports.reporting_service import build_monthly_reports, get_reporting_months
from backend.reports.spending_analysis import analyse_spending

reports_bp = Blueprint("reports", __name__)


def user_transactions():
    rows = get_transactions(session["user_id"])
    result = []
    for row in rows:
        item = dict(row)
        value = item["transaction_date"]
        item["transaction_date"] = value.isoformat() if hasattr(value, "isoformat") else str(value)
        result.append(item)
    return result


@reports_bp.route("/api/reports", methods=["GET"])
def monthly_reports_api():
    if "user_id" not in session:
        return jsonify({"error": "Please log in first"}), 401
    try:
        period = int(request.args.get("period", "6"))
        if period not in (1, 3, 6, 12):
            return jsonify({"error": "Period must be 1, 3, 6 or 12"}), 400
        months = get_reporting_months(period)
        monthly = build_monthly_reports(user_transactions(), period)
        return jsonify({"period":period, "months":months, "monthly_reports":monthly})
    except ValueError as error:
        return jsonify({"error":str(error)}), 400


@reports_bp.route("/api/reports/spending", methods=["GET"])
def spending_reports_api():
    if "user_id" not in session:
        return jsonify({"error": "Please log in first"}), 401
    month = request.args.get("month", "")
    period = request.args.get("range", "month")
    if period not in ("week", "month"):
        return jsonify({"error":"Invalid spending period"}), 400
    try:
        year, number = map(int, month.split("-"))
        month_start = date(year, number, 1)
    except (ValueError, TypeError):
        return jsonify({"error":"Invalid month"}), 400
    if period == "week":
        # Last seven days of the selected month (or through today if current month).
        last_day = date(year + (number == 12), (number % 12) + 1, 1) - timedelta(days=1)
        end = min(date.today(), last_day) if month_start <= date.today() <= last_day else last_day
        start = max(month_start, end - timedelta(days=6))
    else:
        start = month_start
        end = date(year + (number == 12), (number % 12) + 1, 1) - timedelta(days=1)
    transactions = []
    for row in user_transactions():
        transaction_date = date.fromisoformat(row["transaction_date"][:10])
        if start <= transaction_date <= end:
            transactions.append({
                "type":row["transaction_type"],
                "category":row.get("category_name") or "Other",
                "amount":row["amount"]
            })
    return jsonify(analyse_spending(transactions))
