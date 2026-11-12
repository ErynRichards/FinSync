
# Load the tools needed in this file.
import unittest

# Use functions and classes from another file.
from decimal import Decimal

# Use functions and classes from another file.
from backend.transactions.budget_notification import (
    check_budget_notification
)


# Define TestBudgetNotification for this part of the program.
class TestBudgetNotification(unittest.TestCase):

    # Handle setUp requests or data.
    def setUp(self):
        # Common test budget for November 2026.
        self.common_details = {
            "user_id": 101,
            "budget_id": 25,
            "budget_month": "2026-11",
            "budget_amount": "5000.00",
            "previous_spending": "4800.00",
            "current_spending": "5200.00"
        }

    # Test case: verify the notification triggers when budget is exceeded behavior.
    def test_notification_triggers_when_budget_is_exceeded(self):

        result = check_budget_notification(
            **self.common_details
        )

        self.assertTrue(result["should_notify"])
        self.assertEqual(
            result["amount_over_budget"],
            Decimal("200.00")
        )
        self.assertEqual(
            result["reason"],
            "Monthly budget exceeded."
        )

    # Test case: verify the notification does not trigger within budget behavior.
    def test_notification_does_not_trigger_within_budget(self):

        details = {
            **self.common_details,
            "previous_spending": "4000.00",
            "current_spending": "4500.00"
        }

        result = check_budget_notification(**details)

        self.assertFalse(result["should_notify"])

    # Test case: verify the notification does not trigger when already over budget behavior.
    def test_notification_does_not_trigger_when_already_over_budget(self):

        details = {
            **self.common_details,
            "previous_spending": "5200.00",
            "current_spending": "5400.00"
        }

        result = check_budget_notification(**details)

        self.assertFalse(result["should_notify"])

    # Test case: verify the notification does not trigger when preference disabled behavior.
    def test_notification_does_not_trigger_when_preference_disabled(self):

        result = check_budget_notification(
            **self.common_details,
            notifications_enabled=False
        )

        self.assertFalse(result["should_notify"])
        self.assertEqual(
            result["reason"],
            "Budget notifications are disabled."
        )

    # Test case: verify the notification does not repeat for recorded event behavior.
    def test_notification_does_not_repeat_for_recorded_event(self):

        event_id = (
            "budget-exceeded:101:25:2026-11"
        )

        result = check_budget_notification(
            **self.common_details,
            notified_event_ids={event_id}
        )

        self.assertFalse(result["should_notify"])
        self.assertEqual(
            result["reason"],
            "This budget notification was already recorded."
        )

    # Test case: verify the new month has a different event id behavior.
    def test_new_month_has_a_different_event_id(self):

        november_result = check_budget_notification(
            **self.common_details
        )

        december_details = {
            **self.common_details,
            "budget_month": "2026-12"
        }

        december_result = check_budget_notification(
            **december_details
        )

        self.assertNotEqual(
            november_result["event_id"],
            december_result["event_id"]
        )

    # Test case: verify the exact budget limit does not trigger behavior.
    def test_exact_budget_limit_does_not_trigger(self):

        details = {
            **self.common_details,
            "previous_spending": "4500.00",
            "current_spending": "5000.00"
        }

        result = check_budget_notification(**details)

        self.assertFalse(result["should_notify"])

    # Test case: verify the invalid budget amount is rejected behavior.
    def test_invalid_budget_amount_is_rejected(self):

        details = {
            **self.common_details,
            "budget_amount": "0"
        }

        # Use this resource and close it when finished.
        with self.assertRaises(ValueError):
            check_budget_notification(**details)

    # Test case: verify the invalid month is rejected behavior.
    def test_invalid_month_is_rejected(self):

        details = {
            **self.common_details,
            "budget_month": "November 2026"
        }

        # Use this resource and close it when finished.
        with self.assertRaises(ValueError):
            check_budget_notification(**details)


# Check the condition before continuing.
if __name__ == "__main__":
    unittest.main()
