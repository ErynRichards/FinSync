
import unittest
from datetime import date

from backend.savings.savings_service import calculate_monthly_savings


class TestSavingsService(unittest.TestCase):

    # Test a normal savings goal with money already saved.
    def test_calculates_monthly_saving_correctly(self):

        result = calculate_monthly_savings(
            target_amount=12000,
            current_amount=3000,
            target_date="2027-05-08",
            today=date(2026, 11, 8)
        )

        self.assertEqual(result["status"], "active")
        self.assertEqual(result["remaining_amount"], "9000.00")
        self.assertEqual(result["months_remaining"], 6)
        self.assertEqual(
            result["recommended_monthly_saving"],
            "1500.00"
        )

    # Test that a completed goal does not recommend further saving.
    def test_completed_savings_goal(self):

        result = calculate_monthly_savings(
            target_amount=5000,
            current_amount=5000,
            target_date="2027-05-08",
            today=date(2026, 11, 8)
        )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["remaining_amount"], "0.00")
        self.assertEqual(
            result["recommended_monthly_saving"],
            "0.00"
        )

    # Test a goal where the saved amount exceeds the target.
    def test_saved_amount_exceeds_target(self):

        result = calculate_monthly_savings(
            target_amount=5000,
            current_amount=5500,
            target_date="2027-05-08",
            today=date(2026, 11, 8)
        )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["remaining_amount"], "0.00")

    # Test that an overdue goal does not receive a monthly recommendation.
    def test_overdue_savings_goal(self):

        result = calculate_monthly_savings(
            target_amount=10000,
            current_amount=4000,
            target_date="2026-10-31",
            today=date(2026, 11, 8)
        )

        self.assertEqual(result["status"], "overdue")
        self.assertEqual(result["remaining_amount"], "6000.00")
        self.assertIsNone(result["recommended_monthly_saving"])

    # Test that a deadline in the current month uses one month.
    def test_deadline_within_current_month(self):

        result = calculate_monthly_savings(
            target_amount=3000,
            current_amount=1000,
            target_date="2026-11-30",
            today=date(2026, 11, 8)
        )

        self.assertEqual(result["months_remaining"], 1)
        self.assertEqual(
            result["recommended_monthly_saving"],
            "2000.00"
        )

    # Test that the monthly amount is rounded upwards to cents.
    def test_monthly_saving_rounds_up(self):

        result = calculate_monthly_savings(
            target_amount=100,
            current_amount=0,
            target_date="2027-02-08",
            today=date(2026, 11, 8)
        )

        self.assertEqual(result["months_remaining"], 3)
        self.assertEqual(
            result["recommended_monthly_saving"],
            "33.34"
        )

    # Test that a zero target amount is rejected.
    def test_rejects_zero_target_amount(self):

        with self.assertRaises(ValueError):
            calculate_monthly_savings(
                target_amount=0,
                current_amount=0,
                target_date="2027-05-08",
                today=date(2026, 11, 8)
            )

    # Test that a negative current savings amount is rejected.
    def test_rejects_negative_current_amount(self):

        with self.assertRaises(ValueError):
            calculate_monthly_savings(
                target_amount=5000,
                current_amount=-100,
                target_date="2027-05-08",
                today=date(2026, 11, 8)
            )

    # Test that an invalid target date is rejected.
    def test_rejects_invalid_target_date(self):

        with self.assertRaises(ValueError):
            calculate_monthly_savings(
                target_amount=5000,
                current_amount=1000,
                target_date="invalid-date",
                today=date(2026, 11, 8)
            )


if __name__ == "__main__":
    unittest.main()
