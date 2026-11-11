
# Import pytest for automated testing.
import pytest

# Import Flask to create a lightweight test application.
from flask import Flask

# Import the Dashboard Blueprint.
from backend.app.modules.dashboard.dashboard_route import dashboard_bp


# Create a reusable test client for the Dashboard API.
@pytest.fixture
def client():
    # Create a separate Flask application for testing.
    app = Flask(__name__)

    # Enable testing mode.
    app.config["TESTING"] = True

    # Register only the Dashboard Blueprint.
    # This avoids changing or loading the existing group application.
    app.register_blueprint(
        dashboard_bp,
        url_prefix="/api/v1/dashboard"
    )

    # Return a test client that can send HTTP requests.
    return app.test_client()


# Prepare sample financial transactions for testing.
def sample_transactions():
    return [
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


# Test that the Dashboard API returns correctly calculated information.
def test_dashboard_success(client):
    # Supply sample transactions through Flask configuration.
    client.application.config["DASHBOARD_TRANSACTIONS"] = sample_transactions()

    # Supply the account opening balance.
    client.application.config["DASHBOARD_OPENING_BALANCE"] = "5000.00"

    # Send a GET request to the Dashboard endpoint.
    response = client.get("/api/v1/dashboard/")

    # Check that the request was successful.
    assert response.status_code == 200

    # Read the returned JSON information.
    data = response.get_json()

    # Check the calculated account balance.
    assert data["account_balance"] == "18800.00"

    # Check total income.
    assert data["financial_summary"]["total_income"] == "15000.00"

    # Check total expenses.
    assert data["financial_summary"]["total_expenses"] == "1200.00"

    # Check net cash flow.
    assert data["financial_summary"]["net_cash_flow"] == "13800.00"

    # Check the number of transactions.
    assert data["transaction_count"] == 2

    # Confirm the newest transaction appears first.
    assert data["recent_transactions"][0]["description"] == "Groceries"


# Test that the API handles missing transaction data.
def test_dashboard_missing_transactions(client):
    # Send a GET request without configuring transaction data.
    response = client.get("/api/v1/dashboard/")

    # The endpoint should indicate that data is not yet available.
    assert response.status_code == 503

    # Check the returned error message.
    assert response.get_json()["error"] == (
        "Dashboard transaction data is not yet connected."
    )


# Test that invalid transaction information is rejected.
def test_dashboard_invalid_transaction(client):
    # Supply an invalid transaction amount.
    client.application.config["DASHBOARD_TRANSACTIONS"] = [
        {
            "transaction_id": 1,
            "description": "Invalid transaction",
            "amount": "not-a-number",
            "transaction_type": "expense",
            "transaction_date": "2026-11-03"
        }
    ]

    # Send a GET request to the Dashboard endpoint.
    response = client.get("/api/v1/dashboard/")

    # The endpoint should reject invalid financial information.
    assert response.status_code == 422

    # Confirm that an error message is returned.
    assert "error" in response.get_json()
