from flask import Blueprint, jsonify, request

# Create a Blueprint for spending analysis
spending_bp = Blueprint("spending", __name__)


# Calculate the total expenses
def calculate_total_expenses(transactions):
    total = 0

    for transaction in transactions:
        if transaction["type"].lower() == "expense":
            total += float(transaction["amount"])

    return round(total, 2)


# Group expenses according to category
def group_expenses_by_category(transactions):
    categories = {}

    for transaction in transactions:

        # Only include expense transactions
        if transaction["type"].lower() == "expense":

            category = transaction["category"]
            amount = float(transaction["amount"])

            # Add amounts belonging to the same category
            if category in categories:
                categories[category] += amount
            else:
                categories[category] = amount

    return categories


# Calculate the percentage spent on each category
def calculate_category_percentages(categories, total_expenses):
    percentages = {}

    for category, amount in categories.items():

        if total_expenses > 0:
            percentage = (amount / total_expenses) * 100
        else:
            percentage = 0

        percentages[category] = round(percentage, 2)

    return percentages


# Prepare spending data for the frontend
def analyse_spending(transactions):

    # Calculate total spending
    total_expenses = calculate_total_expenses(transactions)

    # Calculate spending per category
    categories = group_expenses_by_category(transactions)

    # Calculate percentages
    percentages = calculate_category_percentages(
        categories, total_expenses
    )

    # Prepare data for the doughnut graph
    chart_data = []

    for category, amount in categories.items():
        chart_data.append({
            "category": category,
            "amount": round(amount, 2),
            "percentage": percentages[category]
        })

    # Return all spending analysis results
    return {
        "total_expenses": total_expenses,
        "category_spending": chart_data
    }


# Flask API endpoint for spending analysis
@spending_bp.route("/api/spending-analysis", methods=["POST"])
def spending_analysis():

    data = request.get_json(silent=True)

    # Check whether valid transaction data was received
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    transactions = data.get("transactions")

    if not isinstance(transactions, list):
        return jsonify({"error": "Transactions must be a list"}), 400

    # Validate transaction information
    for transaction in transactions:
        if not isinstance(transaction, dict):
            return jsonify({"error": "Invalid transaction"}), 400

        if not all(key in transaction for key in
                   ["type", "category", "amount"]):
            return jsonify({"error": "Missing transaction information"}), 400

        if not isinstance(transaction["type"], str):
            return jsonify({"error": "Invalid transaction type"}), 400

        if transaction["type"].lower() not in ["income", "expense"]:
            return jsonify({"error": "Invalid transaction type"}), 400

        if not isinstance(transaction["category"], str):
            return jsonify({"error": "Invalid category"}), 400

        if not transaction["category"].strip():
            return jsonify({"error": "Category cannot be empty"}), 400

        try:
            amount = float(transaction["amount"])

            if not 0 <= amount < float("inf"):
                raise ValueError

        except (ValueError, TypeError, OverflowError):
            return jsonify({"error": "Invalid transaction amount"}), 400

    # Analyse the transactions
    results = analyse_spending(transactions)

    # Send the results to the frontend
    return jsonify(results), 200
