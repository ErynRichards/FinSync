
import unittest

from decimal import Decimal

# Import the function we want to test.
from backend.transactions.transaction_summary import calculate_transaction_summary


class TestTransactionSummary(unittest.TestCase):

    def test_income_expenses_and_net_cash_flow(self):

        # Create sample financial transactions.
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
            }
        ]

        # Calculate the financial summary.
        summary = calculate_transaction_summary(transactions)

        # Check that the income total is correct.
        self.assertEqual(summary["total_income"], Decimal("28000.00"))

        # Check that the expenses total is correct.
        self.assertEqual(summary["total_expenses"], Decimal("1300.00"))

        # Check that the net cash flow is correct.
        self.assertEqual(summary["net_cash_flow"], Decimal("26700.00"))


# Run the tests when this file is executed directly.
if __name__ == "__main__":
    # Import Decimal for the expected financial values.
    from decimal import Decimal
    unittest.main()
