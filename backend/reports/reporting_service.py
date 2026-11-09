
"""
FinSync Interactive Reporting Service.

This module prepares monthly income and expense figures for the
Interactive Reporting feature.

The service currently receives transactions from the existing
Flask configuration-based data source. Database integration
can be added when the group's transaction database is available.
"""

from datetime import date
from decimal import Decimal, InvalidOperation

# Transactions have already been validated when recorded in FinSync.
# Report inputs are read from the authenticated user's database records.
def validate_transaction(transaction):
    errors = []
    if not isinstance(transaction, dict):
        return ["Invalid transaction"]
    if transaction.get("transaction_type") not in ("income", "expense"):
        errors.append("Invalid transaction type")
    if not isinstance(transaction.get("transaction_date"), str):
        errors.append("Invalid transaction date")
    try:
        amount = Decimal(str(transaction.get("amount")))
        if not amount.is_finite() or amount <= 0:
            errors.append("Invalid transaction amount")
    except (InvalidOperation, ValueError, TypeError):
        errors.append("Invalid transaction amount")
    return errors


# Supported reporting periods used by Eryn's Reports frontend.
SUPPORTED_REPORTING_PERIODS = [1, 3, 6, 12]


def get_reporting_months(period, reference_date=None):
    """
    Generate the calendar months included in a reporting period.

    The current month is included as the final month.

    Example:
        A six-month period ending November 2026 includes
        June 2026 through November 2026.

    Parameters:
        period: Number of months to include.
        reference_date: Optional date used for testing.

    Returns:
        A list of month strings in YYYY-MM format.
    """

    # Reject unsupported reporting periods.
    if (
        not isinstance(period, int)
        or isinstance(period, bool)
        or period not in SUPPORTED_REPORTING_PERIODS
    ):
        raise ValueError(
            "Reporting period must be 1, 3, 6 or 12 months."
        )

    # Use today's date unless a reference date is supplied.
    if reference_date is None:
        reference_date = date.today()

    if not isinstance(reference_date, date):
        raise ValueError("Reference date must be a valid date.")

    # Calculate the first month in the requested reporting period.
    months = []

    year = reference_date.year
    month = reference_date.month - period + 1

    while month <= 0:
        month += 12
        year -= 1

    # Generate every month in chronological order.
    for _ in range(period):
        months.append(f"{year:04d}-{month:02d}")

        month += 1

        if month > 12:
            month = 1
            year += 1

    return months


def build_monthly_reports(transactions, period, reference_date=None):
    """
    Calculate monthly income and expenses for the selected period.

    Parameters:
        transactions: List of financial transaction dictionaries.
        period: Reporting period (1, 3, 6 or 12 months).
        reference_date: Optional date used for testing.

    Returns:
        A list of monthly reporting dictionaries.

        Example:
        [
            {
                "month": "2026-10",
                "income": "15000.00",
                "expenses": "5200.00"
            }
        ]
    """

    # Confirm that transaction data is supplied as a list.
    if not isinstance(transactions, list):
        raise ValueError("Transactions must be provided as a list.")

    # Generate the months included in the selected period.
    reporting_months = get_reporting_months(
        period,
        reference_date
    )

    # Prepare zero-value totals for every reporting month.
    # This ensures months without transactions are still displayed.
    monthly_totals = {
        month: {
            "income": Decimal("0.00"),
            "expenses": Decimal("0.00")
        }
        for month in reporting_months
    }

    # Validate and process every supplied transaction.
    for transaction in transactions:

        # Reuse the project's existing transaction validation.
        errors = validate_transaction(transaction)

        if errors:
            raise ValueError("; ".join(errors))

        # Convert the transaction amount into Decimal.
        try:
            amount = Decimal(str(transaction["amount"]))

            if not amount.is_finite() or amount <= 0:
                raise ValueError("Transaction amount must be positive.")

        except (InvalidOperation, ValueError):
            raise ValueError("Transaction contains an invalid amount.")

        # Extract the transaction's reporting month.
        transaction_date = date.fromisoformat(
            transaction["transaction_date"]
        )

        transaction_month = transaction_date.strftime("%Y-%m")

        # Only include transactions inside the selected period.
        if transaction_month not in monthly_totals:
            continue

        # Add the transaction to the correct monthly total.
        if transaction["transaction_type"] == "income":
            monthly_totals[transaction_month]["income"] += amount

        elif transaction["transaction_type"] == "expense":
            monthly_totals[transaction_month]["expenses"] += amount

    # Format the monthly figures for the frontend.
    monthly_reports = []

    for month in reporting_months:
        monthly_reports.append({
            "month": month,
            "income": f"{monthly_totals[month]['income']:.2f}",
            "expenses": f"{monthly_totals[month]['expenses']:.2f}"
        })

    return monthly_reports
