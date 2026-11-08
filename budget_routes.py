"""MISHAYLE: Flask integration for Lashanya's budget recommendations."""
from datetime import date, timedelta
from decimal import Decimal
from flask import Blueprint, jsonify, request, session
from db import DatabaseError, fetch_one, fetch_all
from transactions import get_transactions
from budget_recommendations import calculate_suggested_budget
from budget_database import (
    create_budget,
    get_budgets,
    get_category_spending_history
)

budget_routes = Blueprint('budget_routes', __name__)

@budget_routes.route('/api/budgets/recommendation', methods=['GET'])
def get_budget_recommendation():
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in first.'}), 401

    user_id = session['user_id']
    try:
        category_id = int(request.args.get('category_id', ''))
        if category_id <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'error': 'Please select a valid expense category.'}), 400

    period_text = request.args.get('period', date.today().strftime('%Y-%m'))
    try:
        budget_period = date.fromisoformat(period_text + '-01')
        if budget_period.strftime('%Y-%m') != period_text:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'error': 'Period must be YYYY-MM.'}), 400

    try:
        category = fetch_one(
            'SELECT category_name FROM categories WHERE category_id = %s AND category_type = %s',
            (category_id, 'expense')
        )
        if category is None:
            return jsonify({'error': 'Expense category not found.'}), 400

        # MISHAYLE + DANIEL:
        # Find the previous three completed months for the selected budget.

        first_of_period = budget_period.replace(day=1)

        # Last day of the month before the budget
        history_end = first_of_period - timedelta(days=1)

        # First day of the earliest of the previous three months
        history_start = first_of_period

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
        transactions = []

        for item in category_history:
            # Daniel returns the month as YYYY-MM
            month_date = date.fromisoformat(item["month"] + "-01")

            # Months with no spending must not count as history
            if Decimal(str(item["total"])) > 0:
                transactions.append({
                    "user_id": user_id,
                    "category": category["category_name"],
                    "type": "expense",
                    "date": month_date,
                    "amount": item["total"]
                })

        # We still need the user's transactions to calculate income.
        rows = get_transactions(user_id)

        # Calculate average income for the three completed months before the period.
        # Lashanya's function requires monthly_income for its 50/30/20 cap.
        from budget_recommendations import get_previous_three_months
        previous_months = set(get_previous_three_months(budget_period))
        income_total = sum((Decimal(str(row['amount'])) for row in rows
            if row['transaction_type'].lower() == 'income'
            and (row['transaction_date'].year, row['transaction_date'].month) in previous_months),
            Decimal('0'))
        monthly_income = income_total / Decimal('3')

        result = calculate_suggested_budget(
            user_id, category['category_name'], budget_period,
            monthly_income, transactions
        )
        amount = result.get('suggested_budget') if result.get('success') else None
        return jsonify({
            'category_id': category_id,
            'period': period_text,
            'suggested_amount': amount,
            'message': result.get('message', '')
        }), 200
    except (DatabaseError, ValueError, TypeError, KeyError, AttributeError):
        return jsonify({'error': 'Could not calculate the suggested budget.'}), 500


# MISHAYLE + DANIEL: List saved budgets and actual expenses for a selected month.
@budget_routes.route('/api/budgets', methods=['GET'])
def list_budgets():
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in first.'}), 401
    period = request.args.get('period', date.today().strftime('%Y-%m'))
    try:
        first = date.fromisoformat(period + '-01')
        if first.strftime('%Y-%m') != period:
            raise ValueError
        from calendar import monthrange
        last = date(first.year, first.month, monthrange(first.year, first.month)[1])
    except ValueError:
        return jsonify({'error': 'Period must be YYYY-MM.'}), 400
    try:
        budgets = get_budgets(session['user_id'])
        # Actual spending is scoped to the signed-in user's accounts and selected month.
        spent_rows = fetch_all("""SELECT t.category_id, COALESCE(SUM(t.amount),0) AS spent
            FROM transactions t JOIN accounts a ON a.account_id=t.account_id
            WHERE a.user_id=%s AND t.transaction_type='expense'
              AND t.transaction_date BETWEEN %s AND %s
            GROUP BY t.category_id""", (session['user_id'], first, last))
        spent_by_category = {int(r['category_id']): float(r['spent']) for r in spent_rows}
        result = []
        for b in budgets:
            # Show budgets that cover any part of the selected month.
            if b['start_date'] > last or b['end_date'] < first:
                continue
            result.append({
                'budget_id': b['budget_id'], 'category_id': b['category_id'],
                'category': b['category_name'], 'budget': float(b['budget_amount']),
                'spent': spent_by_category.get(int(b['category_id']), 0.0),
                'start_date': b['start_date'].isoformat(), 'end_date': b['end_date'].isoformat()
            })
        return jsonify({'period': period, 'budgets': result})
    except DatabaseError:
        return jsonify({'error': 'Unable to load budgets.'}), 500


# MISHAYLE + DANIEL: Save a budget only for the logged-in user.
@budget_routes.route('/api/budgets', methods=['POST'])
def save_budget():
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in first.'}), 401
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Please provide budget details.'}), 400
    try:
        category_id = int(data.get('category_id'))
        amount = Decimal(str(data.get('budget_amount')))
        start = date.fromisoformat(data.get('start_date', ''))
        end = date.fromisoformat(data.get('end_date', ''))
        if category_id <= 0 or not amount.is_finite() or amount <= 0 or end < start:
            raise ValueError
    except (ValueError, TypeError, ArithmeticError):
        return jsonify({'error': 'Please enter a valid category, amount and date range.'}), 400
    try:
        category = fetch_one('SELECT category_id FROM categories WHERE category_id=%s AND category_type=%s', (category_id, 'expense'))
        if not category:
            return jsonify({'error': 'Please select an expense category.'}), 400
        budget_id = create_budget(session['user_id'], category_id, amount, start, end)
        return jsonify({'message': 'Budget saved successfully.', 'budget_id': budget_id}), 201
    except DatabaseError:
        return jsonify({'error': 'Unable to save budget. Please try again.'}), 500
