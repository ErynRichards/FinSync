
"""
FinSync - Financial Calculations
Backend Development - Eryn

Purpose:
This module calculates financial information
from a user's recorded transactions.

Functions:
1. Calculate total income
2. Calculate total expenses
3. Calculate available balance
4. Calculate spending totals by category

These functions can be imported into the
FinSync Flask application for use on the
Dashboard, Transactions and Reports screens.
"""

# Use functions and classes from another file.
from decimal import Decimal



# FUNCTION 1: CALCULATE TOTAL INCOME


# Handle calculate total income requests or data.
def calculate_total_income(transactions):
    """
    Calculates the total income received by a user.

    Only transactions marked as 'income' are added.
    """

    # Initialise total income at zero
    total_income = Decimal("0.00")

    # Loop through all transactions
    for transaction in transactions:

        # Check whether the transaction is income
        if transaction["type"].strip().lower() == "income":

            # Convert amount to Decimal for accuracy
            amount = Decimal(str(transaction["amount"]))

            # Add amount to total income
            total_income += amount

    # Return calculated income
    return total_income



# FUNCTION 2: CALCULATE TOTAL EXPENSES


# Handle calculate total expenses requests or data.
def calculate_total_expenses(transactions):
    """
    Calculates the total expenses recorded by a user.

    Only transactions marked as 'expense' are added.
    """

    # Initialise total expenses at zero
    total_expenses = Decimal("0.00")

    # Loop through all transactions
    for transaction in transactions:

        # Check whether the transaction is an expense
        if transaction["type"].strip().lower() == "expense":

            # Convert amount to Decimal
            amount = Decimal(str(transaction["amount"]))

            # Add amount to total expenses
            total_expenses += amount

    # Return calculated expenses
    return total_expenses



# FUNCTION 3: CALCULATE AVAILABLE BALANCE


# Handle calculate balance requests or data.
def calculate_balance(transactions):
    """
    Calculates the user's balance.

    Formula:
    Balance = Total Income - Total Expenses
    """

    # Calculate income using Function 1
    income = calculate_total_income(transactions)

    # Calculate expenses using Function 2
    expenses = calculate_total_expenses(transactions)

    # Subtract expenses from income
    balance = income - expenses

    # Return the calculated balance
    return balance



# FUNCTION 4: CALCULATE SPENDING BY CATEGORY


# Handle calculate spending by category requests or data.
def calculate_spending_by_category(transactions):
    """
    Calculates how much a user spends in each category.

    Examples:
    Food, Transport, Shopping and Entertainment.

    Only expense transactions are included.
    """

    # Dictionary to store category totals
    category_totals = {}

    # Loop through all transactions
    for transaction in transactions:

        # Only process expense transactions
        if transaction["type"].strip().lower() == "expense":

            # Get the transaction category
            category = transaction["category"]

            # Get the expense amount
            amount = Decimal(str(transaction["amount"]))

            # Check whether category already exists
            if category in category_totals:

                # Add amount to existing category total
                category_totals[category] += amount

            else:

                # Create a new category entry
                category_totals[category] = amount

    # Return spending totals for all categories
    return category_totals



# FUNCTION 5: GENERATE FINANCIAL SUMMARY


# Handle get financial summary requests or data.
def get_financial_summary(transactions):
    """
    Combines all financial calculations into
    one reusable financial summary.

    This is useful for the FinSync Dashboard
    and Reports screens.
    """

    # Calculate total income
    income = calculate_total_income(transactions)

    # Calculate total expenses
    expenses = calculate_total_expenses(transactions)

    # Calculate balance
    balance = calculate_balance(transactions)

    # Calculate category spending
    spending = calculate_spending_by_category(transactions)

    # Return all results together
    return {
        "total_income": income,
        "total_expenses": expenses,
        "balance": balance,
        "spending_by_category": spending
    }
