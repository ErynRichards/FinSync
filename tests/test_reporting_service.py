
"""
Unit tests for the FinSync Interactive Reporting Service.
"""

import pytest

from datetime import date

from backend.reports.reporting_service import (
    get_reporting_months,
    build_monthly_reports
)


# Reusable sample transactions for reporting tests.
def sample_transactions():
    return [
        {
            "transaction_id": 1,
            "description": "Monthly Salary",
            "amount": "15000.00",
            "transaction_type": "income",
            "transaction_date": "2026-11-01"
        },
        {
            "transaction_id": 2,
            "description": "Groceries",
            "amount": "1200.00",
            "transaction_type": "expense",
            "transaction_date": "2026-11-03"
        },
        {
            "transaction_id": 3,
            "description": "Transport",
            "amount": "500.00",
            "transaction_type": "expense",
            "transaction_date": "2026-10-15"
        },
        {
            "transaction_id": 4,
            "description": "Freelance Work",
            "amount": "3000.00",
            "transaction_type": "income",
            "transaction_date": "2026-09-10"
        },
        {
            "transaction_id": 5,
            "description": "Old Salary",
            "amount": "10000.00",
            "transaction_type": "income",
            "transaction_date": "2025-11-01"
        }
    ]


# Test the one-month reporting period.
def test_get_reporting_months_one_month():
    months = get_reporting_months(
        1,
        date(2026, 11, 8)
    )

    assert months == ["2026-11"]


# Test the three-month reporting period.
def test_get_reporting_months_three_months():
    months = get_reporting_months(
        3,
        date(2026, 11, 8)
    )

    assert months == [
        "2026-09",
        "2026-10",
        "2026-11"
    ]


# Test the six-month reporting period.
def test_get_reporting_months_six_months():
    months = get_reporting_months(
        6,
        date(2026, 11, 8)
    )

    assert months == [
        "2026-06",
        "2026-07",
        "2026-08",
        "2026-09",
        "2026-10",
        "2026-11"
    ]


# Test the twelve-month reporting period.
def test_get_reporting_months_twelve_months():
    months = get_reporting_months(
        12,
        date(2026, 11, 8)
    )

    assert len(months) == 12
    assert months[0] == "2025-12"
    assert months[-1] == "2026-11"


# Test month generation across a year boundary.
def test_get_reporting_months_crosses_year_boundary():
    months = get_reporting_months(
        3,
        date(2027, 1, 15)
    )

    assert months == [
        "2026-11",
        "2026-12",
        "2027-01"
    ]


# Test that unsupported reporting periods are rejected.
@pytest.mark.parametrize("period", [0, 2, 4, 5, 13, -1])
def test_invalid_reporting_period(period):
    with pytest.raises(ValueError):
        get_reporting_months(
            period,
            date(2026, 11, 8)
        )


# Test that a Boolean is not accepted as a reporting period.
def test_boolean_reporting_period_is_rejected():
    with pytest.raises(ValueError):
        get_reporting_months(
            True,
            date(2026, 11, 8)
        )


# Test that an invalid reference date is rejected.
def test_invalid_reference_date_is_rejected():
    with pytest.raises(ValueError):
        get_reporting_months(6, "2026-11-08")


# Test that the service calculates monthly income and expenses.
def test_build_monthly_reports_calculates_correct_totals():
    reports = build_monthly_reports(
        sample_transactions(),
        3,
        date(2026, 11, 8)
    )

    assert reports == [
        {
            "month": "2026-09",
            "income": "3000.00",
            "expenses": "0.00"
        },
        {
            "month": "2026-10",
            "income": "0.00",
            "expenses": "500.00"
        },
        {
            "month": "2026-11",
            "income": "15000.00",
            "expenses": "1200.00"
        }
    ]


# Test that transactions outside the selected period are excluded.
def test_transactions_outside_reporting_period_are_excluded():
    reports = build_monthly_reports(
        sample_transactions(),
        1,
        date(2026, 11, 8)
    )

    assert reports == [
        {
            "month": "2026-11",
            "income": "15000.00",
            "expenses": "1200.00"
        }
    ]


# Test that months without transactions still appear with zero values.
def test_months_without_transactions_return_zero_values():
    reports = build_monthly_reports(
        [],
        3,
        date(2026, 11, 8)
    )

    assert reports == [
        {
            "month": "2026-09",
            "income": "0.00",
            "expenses": "0.00"
        },
        {
            "month": "2026-10",
            "income": "0.00",
            "expenses": "0.00"
        },
        {
            "month": "2026-11",
            "income": "0.00",
            "expenses": "0.00"
        }
    ]


# Test that non-list transaction input is rejected.
def test_non_list_transactions_are_rejected():
    with pytest.raises(ValueError):
        build_monthly_reports(
            "invalid transactions",
            6,
            date(2026, 11, 8)
        )


# Test that invalid transactions are rejected.
def test_invalid_transaction_is_rejected():
    invalid_transactions = [
        {
            "transaction_id": 1,
            "description": "Invalid transaction",
            "amount": "-100.00",
            "transaction_type": "expense",
            "transaction_date": "2026-11-03"
        }
    ]

    with pytest.raises(ValueError):
        build_monthly_reports(
            invalid_transactions,
            6,
            date(2026, 11, 8)
        )


# Test that an unsupported transaction type is rejected.
def test_invalid_transaction_type_is_rejected():
    invalid_transactions = [
        {
            "transaction_id": 1,
            "description": "Unsupported transaction",
            "amount": "100.00",
            "transaction_type": "transfer",
            "transaction_date": "2026-11-03"
        }
    ]

    with pytest.raises(ValueError):
        build_monthly_reports(
            invalid_transactions,
            6,
            date(2026, 11, 8)
        )
