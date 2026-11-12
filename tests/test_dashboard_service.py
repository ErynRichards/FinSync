
# Load the tools needed in this file.
import unittest

# Import json to verify that Dashboard data can be converted to JSON.
import json

# Import the Dashboard service we want to test.
from backend.dashboard_service import build_dashboard_data


# Define TestDashboardService for this part of the program.
class TestDashboardService(unittest.TestCase):

    # Test case: verify the dashboard returns correct information behavior.
    def test_dashboard_returns_correct_information(self):

        # Create sample financial transactions for a FinSync user.
        transactions = [
            {
                "transaction_id": 1,
                "description": "Monthly Salary",
                "amount": 25000.00,
                "transaction_type": "income",
                "transaction_date": "2026-11-01"
            },
            {
                "transaction_id": 2,
                "description": "Groceries",
                "amount": 850.00,
                "transaction_type": "expense",
                "transaction_date": "2026-11-02"
            },
            {
                "transaction_id": 3,
                "description": "Transport",
                "amount": 450.00,
                "transaction_type": "expense",
                "transaction_date": "2026-11-03"
            },
            {
                "transaction_id": 4,
                "description": "Freelance Work",
                "amount": 3000.00,
                "transaction_type": "income",
                "transaction_date": "2026-11-04"
            },
            {
                "transaction_id": 5,
                "description": "Electricity",
                "amount": 1200.00,
                "transaction_type": "expense",
                "transaction_date": "2026-11-05"
            },
            {
                "transaction_id": 6,
                "description": "Internet",
                "amount": 700.00,
                "transaction_type": "expense",
                "transaction_date": "2026-11-06"
            }
        ]

        # Generate all the Dashboard information.
        dashboard = build_dashboard_data(transactions)

        # Convert the Dashboard response into JSON.
        # Flask will use JSON to communicate with the frontend.
        json_response = json.dumps(dashboard)

        # Confirm that the JSON response was successfully created.
        self.assertIsInstance(json_response, str)

        # Check that total income is calculated correctly.
        self.assertEqual(
            dashboard["financial_summary"]["total_income"],
            "28000.00"
        )

        # Check that total expenses are calculated correctly.
        self.assertEqual(
            dashboard["financial_summary"]["total_expenses"],
            "3200.00"
        )

        # Check that net cash flow is calculated correctly.
        self.assertEqual(
            dashboard["financial_summary"]["net_cash_flow"],
            "24800.00"
        )

        # Check that the total transaction count is correct.
        self.assertEqual(dashboard["transaction_count"], 6)

        # Check that only five recent transactions are returned.
        self.assertEqual(len(dashboard["recent_transactions"]), 5)

        # Confirm that the newest transaction appears first.
        self.assertEqual(
            dashboard["recent_transactions"][0]["description"],
            "Internet"
        )

    # Test case: verify the dashboard with no transactions behavior.
    def test_dashboard_with_no_transactions(self):

        # Test what happens when a user has not recorded transactions.
        dashboard = build_dashboard_data([])

        # Confirm that an empty Dashboard response can be converted to JSON.
        json_response = json.dumps(dashboard)
        self.assertIsInstance(json_response, str)

        # All financial totals should be zero.
        self.assertEqual(
            dashboard["financial_summary"]["total_income"],
            "0.00"
        )

        self.assertEqual(
            dashboard["financial_summary"]["total_expenses"],
            "0.00"
        )

        self.assertEqual(
            dashboard["financial_summary"]["net_cash_flow"],
            "0.00"
        )

        # There should be no transactions to display.
        self.assertEqual(dashboard["recent_transactions"], [])
        self.assertEqual(dashboard["transaction_count"], 0)


    # Test that the Dashboard rejects an invalid transaction.
    def test_dashboard_rejects_invalid_transaction(self):

        # Create a transaction with an unsupported transaction type.
        transactions = [
            {
                "transaction_id": 1,
                "description": "Monthly Salary",
                "amount": 25000.00,
                "transaction_type": "salary",
                "transaction_date": "2026-11-01"
            }
        ]

        # Confirm that the Dashboard raises a validation error.
        with self.assertRaises(ValueError):
            build_dashboard_data(transactions)

    # Test that the Dashboard rejects a list containing both
    # valid and invalid transactions.
    def test_dashboard_rejects_mixed_transactions(self):

        # Keep these records for the next step.
        transactions = [
            {
                "transaction_id": 1,
                "description": "Monthly Salary",
                "amount": 25000.00,
                "transaction_type": "income",
                "transaction_date": "2026-11-01"
            },
            {
                "transaction_id": 2,
                "description": "Groceries",
                "amount": -500.00,
                "transaction_type": "expense",
                "transaction_date": "2026-11-02"
            }
        ]

        # The entire dataset should be rejected because
        # one of its transactions contains invalid information.
        with self.assertRaises(ValueError):
            build_dashboard_data(transactions)

    # Test that the Dashboard only accepts a list of transactions.
    def test_dashboard_rejects_non_list_input(self):

        # Supply a string instead of a transaction list.
        transactions = "Monthly Salary"

        # Confirm that the Dashboard rejects the incorrect input.
        with self.assertRaises(ValueError):
            build_dashboard_data(transactions)


    # Test that the Dashboard calculates the account balance correctly.
    def test_dashboard_calculates_account_balance(self):

        # Keep these records for the next step.
        transactions = [
            {
                "transaction_id": 1,
                "description": "Monthly Salary",
                "amount": 25000.00,
                "transaction_type": "income",
                "transaction_date": "2026-11-01"
            },
            {
                "transaction_id": 2,
                "description": "Groceries",
                "amount": 850.00,
                "transaction_type": "expense",
                "transaction_date": "2026-11-02"
            }
        ]

        # Supply the account's opening balance.
        dashboard = build_dashboard_data(
            transactions,
            opening_balance=10000.00
        )

        # Expected: 10000 + 25000 - 850 = 34150.
        self.assertEqual(
            dashboard["account_balance"],
            "34150.00"
        )

    # Test that the Dashboard does not assume an account balance
    # when no opening balance has been supplied.
    def test_dashboard_without_opening_balance(self):

        # Keep these records for the next step.
        transactions = []

        dashboard = build_dashboard_data(transactions)

        self.assertIsNone(dashboard["account_balance"])

    # Test that an invalid opening balance is rejected.
    def test_dashboard_rejects_invalid_opening_balance(self):

        # Keep these records for the next step.
        transactions = []

        # Use this resource and close it when finished.
        with self.assertRaises(ValueError):
            build_dashboard_data(
                transactions,
                opening_balance="invalid"
            )


# Run the tests when this file is executed directly.
if __name__ == "__main__":
    unittest.main()
