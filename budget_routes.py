"""MISHAYLE: Flask integration for Lashanya's budget recommendations."""
from datetime import date
from decimal import Decimal
from flask import Blueprint, jsonify, request, session
from db import DatabaseError, fetch_one
from transactions import get_transactions
from budget_recommendations import calculate_suggested_budget

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

        # Read only the authenticated user's transactions.
        rows = get_transactions(user_id)
        transactions = [{
            'user_id': user_id,
            'category': row['category_name'],
            'type': row['transaction_type'],
            'date': row['transaction_date'],
            'amount': row['amount']
        } for row in rows]

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
