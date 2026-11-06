
# Import the existing Dashboard calculation and formatting functions.
# Support both project-root and backend-folder execution.
try:
    from backend.dashboard_service import build_dashboard_data, format_money
    from backend.transactions.monthly_summary import calculate_monthly_summary
except ModuleNotFoundError as error:
    if error.name != "backend":
        raise

    from dashboard_service import build_dashboard_data, format_money
    from transactions.monthly_summary import calculate_monthly_summary


class DashboardController:
    """
    Handle the preparation of financial information for the FinSync Dashboard.
    """

    def get_dashboard_data(self, transactions, opening_balance=None):
        """
        Prepare the Dashboard information, including monthly graph data.
        """

        # Build the existing Dashboard information.
        # This also validates the supplied transactions.
        dashboard_data = build_dashboard_data(
            transactions=transactions,
            opening_balance=opening_balance
        )

        # Calculate income and expenses grouped by month.
        monthly_summary = calculate_monthly_summary(transactions)

        # Convert Decimal amounts into strings for JSON compatibility.
        dashboard_data["monthly_summary"] = [
            {
                "month": item["month"],
                "total_income": format_money(item["total_income"]),
                "total_expenses": format_money(item["total_expenses"])
            }
            for item in monthly_summary
        ]

        # Return the complete Dashboard information.
        return dashboard_data
