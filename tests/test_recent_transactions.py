
import unittest

# Import the function we want to test.
from backend.transactions.recent_transactions import get_recent_transactions


class TestRecentTransactions(unittest.TestCase):

    def test_returns_only_five_most_recent_transactions(self):

        # Create seven transactions in deliberately mixed date order.
        transactions = [
            {"transaction_id": 1, "description": "Groceries", "transaction_date": "2026-10-20"},
            {"transaction_id": 2, "description": "Salary", "transaction_date": "2026-11-01"},
            {"transaction_id": 3, "description": "Transport", "transaction_date": "2026-10-25"},
            {"transaction_id": 4, "description": "Electricity", "transaction_date": "2026-10-28"},
            {"transaction_id": 5, "description": "Shopping", "transaction_date": "2026-10-30"},
            {"transaction_id": 6, "description": "Freelance Work", "transaction_date": "2026-11-03"},
            {"transaction_id": 7, "description": "Internet", "transaction_date": "2026-10-22"}
        ]

        # Retrieve the five most recent transactions.
        recent = get_recent_transactions(transactions)

        # Confirm that exactly five transactions were returned.
        self.assertEqual(len(recent), 5)

        # Confirm that they are arranged from newest to oldest.
        expected_ids = [6, 2, 5, 4, 3]

        actual_ids = [
            transaction["transaction_id"]
            for transaction in recent
        ]

        self.assertEqual(actual_ids, expected_ids)

    def test_returns_empty_list_when_no_transactions_exist(self):

        # An account with no recorded transactions should return an empty list.
        recent = get_recent_transactions([])

        self.assertEqual(recent, [])

    def test_returns_all_transactions_when_fewer_than_five_exist(self):

        # Create only two transactions.
        transactions = [
            {"transaction_id": 1, "transaction_date": "2026-10-20"},
            {"transaction_id": 2, "transaction_date": "2026-11-01"}
        ]

        # Both transactions should be returned, newest first.
        recent = get_recent_transactions(transactions)

        self.assertEqual(
            [transaction["transaction_id"] for transaction in recent],
            [2, 1]
        )


# Execute the tests when this file is run directly.
if __name__ == "__main__":
    unittest.main()
