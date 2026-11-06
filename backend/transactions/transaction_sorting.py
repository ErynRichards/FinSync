
def sort_transactions(transactions):
    """
    Sort transactions from newest to oldest.

    Parameters:
        transactions: A list containing financial transaction records.

    Returns:
        A new list with the newest transactions appearing first.
    """

    # Use Python's sorted() function to arrange transactions by date.
    # The key tells Python which field to use when comparing transactions.
    # reverse=True changes the order from oldest-first to newest-first.
    sorted_transactions = sorted(
        transactions,
        key=lambda transaction: transaction["transaction_date"],
        reverse=True
    )

    # Return the sorted list without changing the original list.
    return sorted_transactions
