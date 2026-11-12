
"""
FinSync Interactive Reporting Service.

This module prepares monthly income and expense figures for the
Interactive Reporting feature.

The service currently receives transactions from the existing
Flask configuration-based data source. Database integration
can be added when the group's transaction database is available.
"""

# Use functions and classes from another file.
from datetime import date
# Use functions and classes from another file.
from decimal import Decimal, InvalidOperation

# Transactions have already been validated when recorded in FinSync.
# Report inputs are read from the authenticated user's database records.
def validate_transaction(transaction):

    # Collect any input errors to show the user.
    errors = []

    # Check the condition before continuing.
    if not isinstance(transaction, dict):

        # Send the result back to the code that called this function.
        return ["Invalid transaction"]

    # Check the condition before continuing.
    if transaction.get("transaction_type") not in ("income", "expense"):

        # Add this item to the list of results.
        errors.append("Invalid transaction type")

    # Check the condition before continuing.
    if not isinstance(transaction.get("transaction_date"), str):

        # Add this item to the list of results.
        errors.append("Invalid transaction date")

    # Try the operation and handle any errors.
    try:
        # Save an amount for a calculation or database update.
        amount = Decimal(str(transaction.get("amount")))

        # Check the condition before continuing.
        if not amount.is_finite() or amount <= 0:

            # Add this item to the list of results.
            errors.append("Invalid transaction amount")
    except (InvalidOperation, ValueError, TypeError):

        # Add this item to the list of results.
        errors.append("Invalid transaction amount")

    # Send the result back to the code that called this function.
    return errors


# Supported reporting periods used by Eryn's Reports frontend.
SUPPORTED_REPORTING_PERIODS = [1, 3, 6, 12]


# Handle get reporting months requests or data.
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
        # Stop the operation and report an error.
        raise ValueError(
            "Reporting period must be 1, 3, 6 or 12 months."
        )

    # Use today's date unless a reference date is supplied.
    if reference_date is None:
        reference_date = date.today()

    # Check the condition before continuing.
    if not isinstance(reference_date, date):

        # Stop the operation and report an error.
        raise ValueError("Reference date must be a valid date.")

    # Calculate the first month in the requested reporting period.
    months = []

    year = reference_date.year
    month = reference_date.month - period + 1

    # Repeat while the condition remains true.
    while month <= 0:
        month += 12
        year -= 1

    # Generate every month in chronological order.
    for _ in range(period):

        # Add this item to the list of results.
        months.append(f"{year:04d}-{month:02d}")

        month += 1

        # Check the condition before continuing.
        if month > 12:
            month = 1
            year += 1

    # Send the result back to the code that called this function.
    return months


# Handle build monthly reports requests or data.
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

        # Stop the operation and report an error.
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

        # Check the condition before continuing.
        if errors:
            # Stop the operation and report an error.
            raise ValueError("; ".join(errors))

        # Convert the transaction amount into Decimal.
        try:
            # Save an amount for a calculation or database update.
            amount = Decimal(str(transaction["amount"]))

            # Check the condition before continuing.
            if not amount.is_finite() or amount <= 0:

                # Stop the operation and report an error.
                raise ValueError("Transaction amount must be positive.")

        except (InvalidOperation, ValueError):
            # Stop the operation and report an error.
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

        # Check the condition before continuing.
        elif transaction["transaction_type"] == "expense":
            monthly_totals[transaction_month]["expenses"] += amount

    # Format the monthly figures for the frontend.
    monthly_reports = []

    # Go through each item one at a time.
    for month in reporting_months:
        # Add this item to the list of results.
        monthly_reports.append({
            "month": month,
            "income": f"{monthly_totals[month]['income']:.2f}",
            "expenses": f"{monthly_totals[month]['expenses']:.2f}"
        })

    # Send the result back to the code that called this function.
    return monthly_reports
