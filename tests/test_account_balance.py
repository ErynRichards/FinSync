
# Import unittest to create automated tests.
import unittest

# Import Decimal for accurate financial comparisons.
from decimal import Decimal

# Import the account balance calculation function.
from backend.transactions.account_balance import calculate_account_balance


class TestAccountBalance(unittest.TestCase):

    # Test that income and expenses are correctly added
    # to and deducted from the opening balance.
    def test_calculate_account_balance(self):

        opening_balance = 10000.00

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
            }
        ]

        # Calculate the final account balance.
        balance = calculate_account_balance(
            opening_balance,
            transactions
        )

        # Expected: 10000 + 25000 - 850 - 450 = 33700.
        self.assertEqual(balance, Decimal("33700.00"))

    # Test that an account with no transactions
    # retains its original opening balance.
    def test_balance_without_transactions(self):

        balance = calculate_account_balance(5000.00, [])

        self.assertEqual(balance, Decimal("5000.0"))

    # Test that income increases the account balance.
    def test_income_increases_balance(self):

        transactions = [
            {
                "transaction_id": 1,
                "description": "Freelance Payment",
                "amount": 3000.00,
                "transaction_type": "income",
                "transaction_date": "2026-11-04"
            }
        ]

        balance = calculate_account_balance(2000.00, transactions)

        self.assertEqual(balance, Decimal("5000.00"))

    # Test that expenses decrease the account balance.
    def test_expense_decreases_balance(self):

        transactions = [
            {
                "transaction_id": 1,
                "description": "Electricity",
                "amount": 1200.00,
                "transaction_type": "expense",
                "transaction_date": "2026-11-05"
            }
        ]

        balance = calculate_account_balance(5000.00, transactions)

        self.assertEqual(balance, Decimal("3800.00"))

    # Test that invalid transactions are rejected.
    def test_invalid_transaction_is_rejected(self):

        transactions = [
            {
                "transaction_id": 1,
                "description": "Shopping",
                "amount": -500.00,
                "transaction_type": "expense",
                "transaction_date": "2026-11-06"
            }
        ]

        # The function should raise an error for invalid data.
        with self.assertRaises(ValueError):
            calculate_account_balance(5000.00, transactions)

    # Test that an invalid opening balance is rejected.
    def test_invalid_opening_balance_is_rejected(self):

        transactions = []

        # A non-numeric opening balance must not be accepted.
        with self.assertRaises(ValueError):
            calculate_account_balance("invalid", transactions)


# Run the tests when this file is executed directly.
if __name__ == "__main__":
    unittest.main()
