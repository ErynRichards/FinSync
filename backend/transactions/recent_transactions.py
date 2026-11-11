
# Support both project-root and backend-folder execution.
try:
    from backend.transactions.transaction_sorting import sort_transactions
except ModuleNotFoundError as error:
    if error.name != "backend":
        raise
    from transactions.transaction_sorting import sort_transactions


def get_recent_transactions(transactions, limit=5):
    """
    Retrieve the most recent transactions.

    Transactions are sorted from newest to oldest.

    Parameters:
        transactions: A list of transactions.
        limit: Maximum number of transactions to return.

    Returns:
        A list containing the most recent transactions.
    """

    # Validate the requested transaction limit.
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 0:
        raise ValueError("The limit must be a non-negative integer.")

    # Sort transactions from newest to oldest.
    sorted_transactions = sort_transactions(transactions)

    # Return only the requested number of recent transactions.
    recent_transactions = sorted_transactions[:limit]

    return recent_transactions
