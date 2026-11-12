# Import pytest for testing.
import pytest

# Import the monthly summary function.
from backend.transactions.monthly_summary import calculate_monthly_summary


# Test case: verify the monthly summary calculates income and expenses behavior.
def test_monthly_summary_calculates_income_and_expenses():
    """Check that income and expenses are correctly grouped by month."""

    # Keep these records for the next step.
    transactions = [
        {
            "transaction_id": 1,
            "description": "Salary",
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
        }
    ]

    result = calculate_monthly_summary(transactions)

    assert result[0]["month"] == "2026-11"
    assert result[0]["total_income"] == 15000
    assert result[0]["total_expenses"] == 1200


# Test case: verify the monthly summary orders months chronologically behavior.
def test_monthly_summary_orders_months_chronologically():
    """Check that months are returned from oldest to newest."""

    # Keep these records for the next step.
    transactions = [
        {
            "transaction_id": 1,
            "description": "November Salary",
            "amount": "15000.00",
            "transaction_type": "income",
            "transaction_date": "2026-11-01"
        },
        {
            "transaction_id": 2,
            "description": "October Salary",
            "amount": "14000.00",
            "transaction_type": "income",
            "transaction_date": "2026-10-01"
        }
    ]

    result = calculate_monthly_summary(transactions)

    assert result[0]["month"] == "2026-10"
    assert result[1]["month"] == "2026-11"


# Test case: verify the monthly summary handles empty transactions behavior.
def test_monthly_summary_handles_empty_transactions():
    """Check that an empty transaction list returns an empty result."""

    result = calculate_monthly_summary([])

    assert result == []


# Test case: verify the monthly summary rejects invalid transaction type behavior.
def test_monthly_summary_rejects_invalid_transaction_type():
    """Check that unsupported transaction types are rejected."""

    # Keep these records for the next step.
    transactions = [
        {
            "transaction_id": 1,
            "description": "Other",
            "amount": "500.00",
            "transaction_type": "transfer",
            "transaction_date": "2026-11-01"
        }
    ]

    # Use this resource and close it when finished.
    with pytest.raises(ValueError):
        calculate_monthly_summary(transactions)