
# Import the unittest module so we can test our code.
import unittest

# Import the transaction sorting function from our backend.
from backend.transactions.transaction_sorting import sort_transactions


# Define TestTransactionSorting for this part of the program.
class TestTransactionSorting(unittest.TestCase):

    # Test case: verify the transactions sorted newest first behavior.
    def test_transactions_sorted_newest_first(self):

        # Create sample transactions to simulate FinSync user activity.
        # These transactions are deliberately NOT arranged by date.
        transactions = [
            {
                "transaction_id": 1,
                "description": "Groceries",
                "amount": 850.00,
                "transaction_type": "expense",
                "transaction_date": "2026-10-25"
            },
            {
                "transaction_id": 2,
                "description": "Monthly Salary",
                "amount": 25000.00,
                "transaction_type": "income",
                "transaction_date": "2026-11-01"
            },
            {
                "transaction_id": 3,
                "description": "Transport",
                "amount": 450.00,
                "transaction_type": "expense",
                "transaction_date": "2026-10-29"
            }
        ]

        # Call the function we created in transaction_sorting.py.
        sorted_transactions = sort_transactions(transactions)

        # Define the order we expect: newest transaction first.
        expected_order = [
            "2026-11-01",
            "2026-10-29",
            "2026-10-25"
        ]

        # Extract the dates from the sorted results.
        actual_order = [
            transaction["transaction_date"]
            for transaction in sorted_transactions
        ]

        # Check whether the actual order matches our expected order.
        self.assertEqual(actual_order, expected_order)

    # Test case: verify the original transactions remain unchanged behavior.
    def test_original_transactions_remain_unchanged(self):

        # Create a small sample list of transactions.
        transactions = [
            {"transaction_date": "2026-10-25"},
            {"transaction_date": "2026-11-01"}
        ]

        # Keep a copy of the original list for comparison.
        original_transactions = transactions.copy()

        # Sort the transactions.
        sort_transactions(transactions)

        # Confirm that the original list was not changed.
        self.assertEqual(transactions, original_transactions)


# Run the tests when this file is executed directly.
if __name__ == "__main__":
    unittest.main()
