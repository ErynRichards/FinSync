
"""
Unit tests for the FinSync Interactive Reporting API.
"""

import pytest

from app.app import create_app


# Create valid sample transactions for API testing.
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
        }
    ]


# Create a Flask test client for the reporting API.
@pytest.fixture
def client():
    app = create_app("testing")
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


# Test that the API reports missing transaction data.
def test_reports_endpoint_returns_503_when_data_is_missing(client):
    response = client.get("/api/v1/reports/?period=6")

    assert response.status_code == 503
    assert "error" in response.get_json()


# Test that the API rejects an unsupported reporting period.
@pytest.mark.parametrize("period", ["0", "2", "4", "13", "-1"])
def test_reports_endpoint_rejects_unsupported_period(client, period):
    response = client.get(
        f"/api/v1/reports/?period={period}"
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


# Test that the API rejects a non-numeric reporting period.
@pytest.mark.parametrize("period", ["abc", "six", "6.5"])
def test_reports_endpoint_rejects_non_numeric_period(client, period):
    response = client.get(
        f"/api/v1/reports/?period={period}"
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


# Test that the API returns monthly figures for a valid request.
def test_reports_endpoint_returns_monthly_reports(client):
    from flask import current_app

    # Configure the temporary transaction data source.
    with client.application.app_context():
        current_app.config["DASHBOARD_TRANSACTIONS"] = sample_transactions()

    response = client.get("/api/v1/reports/?period=3")

    assert response.status_code == 200

    response_data = response.get_json()

    assert response_data["period"] == 3
    assert "monthly_reports" in response_data

    assert len(response_data["monthly_reports"]) == 3

    # Confirm that each reporting record has the expected fields.
    for report in response_data["monthly_reports"]:
        assert "month" in report
        assert "income" in report
        assert "expenses" in report


# Test that the API returns the default six-month period.
def test_reports_endpoint_defaults_to_six_months(client):
    from flask import current_app

    with client.application.app_context():
        current_app.config["DASHBOARD_TRANSACTIONS"] = sample_transactions()

    response = client.get("/api/v1/reports/")

    assert response.status_code == 200

    response_data = response.get_json()

    assert response_data["period"] == 6
    assert len(response_data["monthly_reports"]) == 6


# Test that invalid transaction data produces an HTTP 422 response.
def test_reports_endpoint_returns_422_for_invalid_transactions(client):
    from flask import current_app

    invalid_transactions = [
        {
            "transaction_id": 1,
            "description": "Invalid transaction",
            "amount": "-100.00",
            "transaction_type": "expense",
            "transaction_date": "2026-11-03"
        }
    ]

    with client.application.app_context():
        current_app.config["DASHBOARD_TRANSACTIONS"] = invalid_transactions

    response = client.get("/api/v1/reports/?period=6")

    assert response.status_code == 422
    assert "error" in response.get_json()
