# Use functions and classes from another file.
from flask import Blueprint, jsonify, request

# Create a Blueprint for spending analysis
spending_bp = Blueprint("spending", __name__)


# Calculate the total expenses
def calculate_total_expenses(transactions):

    # Save an amount for a calculation or database update.
    total = 0

    # Go through each item one at a time.
    for transaction in transactions:

        # Check the condition before continuing.
        if transaction["type"].lower() == "expense":
            total += float(transaction["amount"])

    # Send the result back to the code that called this function.
    return round(total, 2)


# Group expenses according to category
def group_expenses_by_category(transactions):
    categories = {}

    # Go through each item one at a time.
    for transaction in transactions:

        # Only include expense transactions
        if transaction["type"].lower() == "expense":

            category = transaction["category"]
            # Save an amount for a calculation or database update.
            amount = float(transaction["amount"])

            # Add amounts belonging to the same category
            if category in categories:
                categories[category] += amount
            else:
                categories[category] = amount

    # Send the result back to the code that called this function.
    return categories


# Calculate the percentage spent on each category
def calculate_category_percentages(categories, total_expenses):
    percentages = {}

    # Go through each item one at a time.
    for category, amount in categories.items():

        # Check the condition before continuing.
        if total_expenses > 0:
            percentage = (amount / total_expenses) * 100
        else:
            percentage = 0

        percentages[category] = round(percentage, 2)

    # Send the result back to the code that called this function.
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

    # Go through each item one at a time.
    for category, amount in categories.items():

        # Add this item to the list of results.
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

        # Send the result back to the code that called this function.
        return jsonify({"error": "Invalid JSON data"}), 400

    # Keep these records for the next step.
    transactions = data.get("transactions")

    # Check the condition before continuing.
    if not isinstance(transactions, list):

        # Send the result back to the code that called this function.
        return jsonify({"error": "Transactions must be a list"}), 400

    # Validate transaction information
    for transaction in transactions:

        # Check the condition before continuing.
        if not isinstance(transaction, dict):

            # Send the result back to the code that called this function.
            return jsonify({"error": "Invalid transaction"}), 400

        # Check the condition before continuing.
        if not all(key in transaction for key in
                   ["type", "category", "amount"]):

            # Send the result back to the code that called this function.
            return jsonify({"error": "Missing transaction information"}), 400

        # Check the condition before continuing.
        if not isinstance(transaction["type"], str):

            # Send the result back to the code that called this function.
            return jsonify({"error": "Invalid transaction type"}), 400

        # Check the condition before continuing.
        if transaction["type"].lower() not in ["income", "expense"]:

            # Send the result back to the code that called this function.
            return jsonify({"error": "Invalid transaction type"}), 400

        # Check the condition before continuing.
        if not isinstance(transaction["category"], str):

            # Send the result back to the code that called this function.
            return jsonify({"error": "Invalid category"}), 400

        # Check the condition before continuing.
        if not transaction["category"].strip():

            # Send the result back to the code that called this function.
            return jsonify({"error": "Category cannot be empty"}), 400

        # Try the operation and handle any errors.
        try:
            # Save an amount for a calculation or database update.
            amount = float(transaction["amount"])

            # Check the condition before continuing.
            if not 0 <= amount < float("inf"):

                # Stop the operation and report an error.
                raise ValueError

        except (ValueError, TypeError, OverflowError):

            # Send the result back to the code that called this function.
            return jsonify({"error": "Invalid transaction amount"}), 400

    # Analyse the transactions
    results = analyse_spending(transactions)

    # Send the results to the frontend
    return jsonify(results), 200
