
"""
FinSync - Financial Calculations Testing
Tests the financial calculations using
sample income and expense transactions.
"""

from decimal import Decimal

from financial_calculations import (
    get_financial_summary
)


# Sample transaction records
transactions = [
    {
        "type": "Income",
        "amount": 15000,
        "category": "Salary"
    },
    {
        "type": "Income",
        "amount": 2000,
        "category": "Freelance"
    },
    {
        "type": "Expense",
        "amount": 1500,
        "category": "Food"
    },
    {
        "type": "Expense",
        "amount": 800,
        "category": "Transport"
    },
    {
        "type": "Expense",
        "amount": 500,
        "category": "Food"
    },
    {
        "type": "Expense",
        "amount": 1200,
        "category": "Shopping"
    }
]


# Generate the financial summary
summary = get_financial_summary(transactions)


# Display calculated results
print("FIN SYNC FINANCIAL SUMMARY")
print("--------------------------")

print("Total Income: R", summary["total_income"])
print("Total Expenses: R", summary["total_expenses"])
print("Balance: R", summary["balance"])

print("\nSpending by Category:")

for category, amount in summary["spending_by_category"].items():
    print(category, ": R", amount)


# Check that calculations are correct
assert summary["total_income"] == Decimal("17000")
assert summary["total_expenses"] == Decimal("4000")
assert summary["balance"] == Decimal("13000")
assert summary["spending_by_category"]["Food"] == Decimal("2000")

print("\nAll calculation tests passed!")
