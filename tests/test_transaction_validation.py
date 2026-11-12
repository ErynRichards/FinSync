
# Import unittest to create automated tests.
import unittest

# Import the transaction validation function.
from backend.transactions.transaction_validation import validate_transaction


# Define TestTransactionValidation for this part of the program.
class TestTransactionValidation(unittest.TestCase):

    # Test that a correctly completed transaction is accepted.
    def test_valid_transaction(self):
        transaction = {
            "transaction_id": 1,
            "description": "Monthly Salary",
            "amount": 25000.00,
            "transaction_type": "income",
            "transaction_date": "2026-11-01"
        }

        # A valid transaction should return no errors.
        self.assertEqual(validate_transaction(transaction), [])

    # Test that a transaction with an invalid type is rejected.
    def test_invalid_transaction_type(self):
        transaction = {
            "transaction_id": 2,
            "description": "Monthly Salary",
            "amount": 25000.00,
            "transaction_type": "salary",
            "transaction_date": "2026-11-01"
        }

        # Collect any input errors to show the user.
        errors = validate_transaction(transaction)

        self.assertIn(
            "Transaction type must be income or expense.",
            errors
        )

    # Test that zero or negative amounts are rejected.
    def test_invalid_transaction_amount(self):
        transaction = {
            "transaction_id": 3,
            "description": "Groceries",
            "amount": -500,
            "transaction_type": "expense",
            "transaction_date": "2026-11-02"
        }

        # Collect any input errors to show the user.
        errors = validate_transaction(transaction)

        self.assertIn(
            "Transaction amount must be greater than zero.",
            errors
        )

    # Test that an invalid date is rejected.
    def test_invalid_transaction_date(self):
        transaction = {
            "transaction_id": 4,
            "description": "Transport",
            "amount": 200,
            "transaction_type": "expense",
            "transaction_date": "2026-15-40"
        }

        # Collect any input errors to show the user.
        errors = validate_transaction(transaction)

        self.assertIn(
            "Transaction date must be a valid YYYY-MM-DD date.",
            errors
        )

    # Test that an empty description is rejected.
    def test_empty_description(self):
        transaction = {
            "transaction_id": 5,
            "description": "   ",
            "amount": 150,
            "transaction_type": "expense",
            "transaction_date": "2026-11-03"
        }

        # Collect any input errors to show the user.
        errors = validate_transaction(transaction)

        self.assertIn(
            "Transaction description cannot be empty.",
            errors
        )

    # Test that missing required fields are detected.
    def test_missing_required_field(self):
        transaction = {
            "transaction_id": 6,
            "description": "Electricity",
            "amount": 1200,
            "transaction_type": "expense"
        }

        # Collect any input errors to show the user.
        errors = validate_transaction(transaction)

        self.assertIn(
            "Missing required field: transaction_date",
            errors
        )

    # Test that a transaction ID must be a positive integer.
    def test_invalid_transaction_id(self):
        transaction = {
            "transaction_id": 0,
            "description": "Internet",
            "amount": 700,
            "transaction_type": "expense",
            "transaction_date": "2026-11-03"
        }

        # Collect any input errors to show the user.
        errors = validate_transaction(transaction)

        self.assertIn(
            "Transaction ID must be a positive integer.",
            errors
        )

    # Test that a transaction amount must be numeric.
    def test_non_numeric_amount(self):
        transaction = {
            "transaction_id": 8,
            "description": "Shopping",
            "amount": "invalid",
            "transaction_type": "expense",
            "transaction_date": "2026-11-03"
        }

        # Collect any input errors to show the user.
        errors = validate_transaction(transaction)

        self.assertIn(
            "Transaction amount must be a valid number.",
            errors
        )


# Run the tests when this file is executed directly.
if __name__ == "__main__":
    unittest.main()
