"""MISHAYLE: Flask integration for Lashanya's budget recommendations."""
# Use functions and classes from another file.
from datetime import date, timedelta

# Use functions and classes from another file.
from calendar import monthrange

# Use functions and classes from another file.
from decimal import Decimal

# Use functions and classes from another file.
from flask import Blueprint, jsonify, request, session

# Use functions and classes from another file.
from db import DatabaseError, fetch_one, fetch_all

# Use functions and classes from another file.
from transactions import get_transactions

# Use functions and classes from another file.
from budget_recommendations import (
    calculate_suggested_budget,
    NEEDS_CATEGORIES,
    WANTS_CATEGORIES
)
# Use functions and classes from another file.
from budget_database import (
    create_budget,
    BudgetOverlapError,
    get_budgets,
    get_category_spending_history
)

# Save an amount for a calculation or database update.
budget_routes = Blueprint('budget_routes', __name__)

# Handle get budget recommendation requests or data.
@budget_routes.route('/api/budgets/recommendation', methods=['GET'])
def get_budget_recommendation():
    # Check the condition before continuing.
    if 'user_id' not in session:
        # Send the result back to the code that called this function.
        return jsonify({'error': 'Please log in first.'}), 401

    # Keep the ID of the record being used.
    user_id = session['user_id']

    # Try the operation and handle any errors.
    try:
        # Keep the ID of the record being used.
        category_id = int(request.args.get('category_id', ''))

        # Check the condition before continuing.
        if category_id <= 0:

            # Stop the operation and report an error.
            raise ValueError
    except (ValueError, TypeError):
        # Send the result back to the code that called this function.
        return jsonify({'error': 'Please select a valid expense category.'}), 400

    period_text = request.args.get('period', date.today().strftime('%Y-%m'))
    # Try the operation and handle any errors.
    try:
        # Save an amount for a calculation or database update.
        budget_period = date.fromisoformat(period_text + '-01')

        # Check the condition before continuing.
        if budget_period.strftime('%Y-%m') != period_text:

            # Stop the operation and report an error.
            raise ValueError
    except (ValueError, TypeError):

        # Send the result back to the code that called this function.
        return jsonify({'error': 'Period must be YYYY-MM.'}), 400

    # Try the operation and handle any errors.
    try:
        category = fetch_one(
            'SELECT category_name FROM categories WHERE category_id = %s AND category_type = %s',
            (category_id, 'expense')
        )
        # Check the condition before continuing.
        if category is None:
            # Send the result back to the code that called this function.
            return jsonify({'error': 'Expense category not found.'}), 400

        # MISHAYLE + DANIEL:
        # Find the previous three completed months for the selected budget.

        first_of_period = budget_period.replace(day=1)

        # Last day of the month before the budget
        history_end = first_of_period - timedelta(days=1)

        # First day of the earliest of the previous three months
        history_start = first_of_period

        # Go through each item one at a time.
        for i in range(3):
            history_start = (
                    history_start - timedelta(days=1)
            ).replace(day=1)

        # DANIEL: Retrieve category spending totals from MySQL
        category_history = get_category_spending_history(
            user_id,
            category_id,
            history_start,
            history_end
        )

        # Convert Daniel's monthly totals into the transaction
        # format expected by Lashanya's calculation.
        # MISHAYLE: Prepare the previous three months of expenses
        # for Lashanya's updated recommendation calculation.

        # Save an amount for a calculation or database update.
        monthly_expenses = []

        # Go through each item one at a time.
        for item in category_history:
            # Save an amount for a calculation or database update.
            total = float(item["total"])

            # Check the condition before continuing.
            if total > 0:
                # Add this item to the list of results.
                monthly_expenses.append(total)
            else:
                # No spending history for this month
                monthly_expenses.append(None)

        # MISHAYLE: Prefer recorded income for the selected budget month.
        # If none was recorded, use the average of the preceding three months.
        rows = get_transactions(user_id)
        previous_months = set()
        current_month = budget_period

        # Go through each item one at a time.
        for _ in range(3):
            previous_day = current_month - timedelta(days=1)
            current_month = date(previous_day.year, previous_day.month, 1)
            previous_months.add((current_month.year, current_month.month))

        # Save an amount for a calculation or database update.
        selected_income = Decimal('0')

        # Save an amount for a calculation or database update.
        previous_income = Decimal('0')

        # Go through each item one at a time.
        for row in rows:

            # Check the condition before continuing.
            if str(row['transaction_type']).lower() != 'income':
                continue

            transaction_date = row['transaction_date']
            # Check the condition before continuing.
            if isinstance(transaction_date, str):
                transaction_date = date.fromisoformat(transaction_date[:10])
            month = (transaction_date.year, transaction_date.month)

            # Save an amount for a calculation or database update.
            amount = Decimal(str(row['amount']))

            # Check the condition before continuing.
            if month == (budget_period.year, budget_period.month):
                selected_income += amount

            # Check the condition before continuing.
            elif month in previous_months:
                previous_income += amount

        # Check the condition before continuing.
        if selected_income > 0:

            # Save an amount for a calculation or database update.
            monthly_income = selected_income

            # Save an amount for a calculation or database update.
            income_source = 'Selected month income'
        else:
            # Save an amount for a calculation or database update.
            monthly_income = previous_income / Decimal('3')

            # Save an amount for a calculation or database update.
            income_source = 'Previous three-month average income'

        # MISHAYLE: Calculate existing budgets in the same group

        category_name = category["category_name"]

        # Check the condition before continuing.
        if category_name in NEEDS_CATEGORIES:
            group_categories = NEEDS_CATEGORIES

        # Check the condition before continuing.
        elif category_name in WANTS_CATEGORIES:
            group_categories = WANTS_CATEGORIES
        else:
            group_categories = []

        # Save an amount for a calculation or database update.
        other_category_budgets = 0

        # Save an amount for a calculation or database update.
        existing_budgets = get_budgets(user_id)

        period_end = date(
            budget_period.year,
            budget_period.month,
            monthrange(budget_period.year, budget_period.month)[1]
        )

        # Go through each item one at a time.
        for budget in existing_budgets:

            # Exclude the category currently being recommended
            if budget["category_name"] == category_name:
                continue

            # Only include budgets from the same group
            if budget["category_name"] not in group_categories:
                continue

            # Only include budgets covering the selected month
            if (
                    budget["start_date"] <= period_end
                    and budget["end_date"] >= first_of_period
            ):
                other_category_budgets += float(budget["budget_amount"])

        result = calculate_suggested_budget(
            user_id=user_id,
            category=category['category_name'],
            period=period_text,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            other_category_budgets=other_category_budgets
        )

        # Save an amount for a calculation or database update.
        amount = result.get('suggested_budget') if result.get('success') else None

        # Check the condition before continuing.
        if result.get('success'):
            method = result.get('method', '')
            # Check the condition before continuing.

            if amount == 0:
                message = 'No allocation remains in this budget group.'
            else:
                message = f'{method}. Income source: {income_source}.'
        else:
            message = result.get('message', '')

        # Send the result back to the code that called this function.
        return jsonify({
            'category_id': category_id,
            'period': period_text,
            'suggested_amount': amount,
            'message': message,
            'method': result.get('method'),
            'income_source': income_source
        }), 200
    except (DatabaseError, ValueError, TypeError, KeyError, AttributeError):

        # Send the result back to the code that called this function.
        return jsonify({'error': 'Could not calculate the suggested budget.'}), 500


# MISHAYLE + DANIEL: List saved budgets and actual expenses for a selected month.
@budget_routes.route('/api/budgets', methods=['GET'])
def list_budgets():
    # Check the condition before continuing.
    if 'user_id' not in session:
        # Send the result back to the code that called this function.

        return jsonify({'error': 'Please log in first.'}), 401
    period = request.args.get('period', date.today().strftime('%Y-%m'))

    # Try the operation and handle any errors.
    try:
        first = date.fromisoformat(period + '-01')
        # Check the condition before continuing.
        if first.strftime('%Y-%m') != period:

            # Stop the operation and report an error.
            raise ValueError

        # Use functions and classes from another file.
        from calendar import monthrange
        last = date(first.year, first.month, monthrange(first.year, first.month)[1])
    except ValueError:

        # Send the result back to the code that called this function.
        return jsonify({'error': 'Period must be YYYY-MM.'}), 400

    # Try the operation and handle any errors.
    try:
        # Save an amount for a calculation or database update.
        budgets = get_budgets(session['user_id'])

        # Actual spending is scoped to the signed-in user's accounts and selected month.
        spent_rows = fetch_all("""SELECT t.category_id, COALESCE(SUM(t.amount),0) AS spent
            FROM transactions t JOIN accounts a ON a.account_id=t.account_id
            WHERE a.user_id=%s AND t.transaction_type='expense'
              AND t.transaction_date BETWEEN %s AND %s
            GROUP BY t.category_id""", (session['user_id'], first, last))
        spent_by_category = {int(r['category_id']): float(r['spent']) for r in spent_rows}
        result = []

        # Go through each item one at a time.
        for b in budgets:

            # Show budgets that cover any part of the selected month.
            if b['start_date'] > last or b['end_date'] < first:
                continue

            # Add this item to the list of results.
            result.append({
                'budget_id': b['budget_id'], 'category_id': b['category_id'],
                'category': b['category_name'], 'budget': float(b['budget_amount']),
                'spent': spent_by_category.get(int(b['category_id']), 0.0),
                'start_date': b['start_date'].isoformat(), 'end_date': b['end_date'].isoformat()
            })

        # Send the result back to the code that called this function.
        return jsonify({'period': period, 'budgets': result})
    except DatabaseError:

        # Send the result back to the code that called this function.
        return jsonify({'error': 'Unable to load budgets.'}), 500


# MISHAYLE + DANIEL: Save a budget only for the logged-in user.
@budget_routes.route('/api/budgets', methods=['POST'])
def save_budget():
    # Check the condition before continuing.
    if 'user_id' not in session:

        # Send the result back to the code that called this function.
        return jsonify({'error': 'Please log in first.'}), 401
    data = request.get_json(silent=True)

    # Check the condition before continuing.
    if not isinstance(data, dict):

        # Send the result back to the code that called this function.
        return jsonify({'error': 'Please provide budget details.'}), 400

    # Try the operation and handle any errors.
    try:
        # Keep the ID of the record being used.
        category_id = int(data.get('category_id'))

        # Save an amount for a calculation or database update.
        amount = Decimal(str(data.get('budget_amount')))
        start = date.fromisoformat(data.get('start_date', ''))
        end = date.fromisoformat(data.get('end_date', ''))

        # Check the condition before continuing.
        if category_id <= 0 or not amount.is_finite() or amount <= 0 or end < start:

            # Stop the operation and report an error.
            raise ValueError
    except (ValueError, TypeError, ArithmeticError):

        # Send the result back to the code that called this function.
        return jsonify({'error': 'Please enter a valid category, amount and date range.'}), 400

    # Try the operation and handle any errors.
    try:
        category = fetch_one('SELECT category_id FROM categories WHERE category_id=%s AND category_type=%s', (category_id, 'expense'))

        # Check the condition before continuing.
        if not category:

            # Send the result back to the code that called this function.
            return jsonify({'error': 'Please select an expense category.'}), 400

        # Save an amount for a calculation or database update.
        budget_id = create_budget(session['user_id'], category_id, amount, start, end)

        # Send the result back to the code that called this function.
        return jsonify({'message': 'Budget saved successfully.', 'budget_id': budget_id}), 201
    except BudgetOverlapError:

        # Send the result back to the code that called this function.
        return jsonify({'error': 'A budget for this category already overlaps the selected dates. Choose different dates.'}), 409
    except DatabaseError:

        # Send the result back to the code that called this function.
        return jsonify({'error': 'Unable to save budget. Please try again.'}), 500
