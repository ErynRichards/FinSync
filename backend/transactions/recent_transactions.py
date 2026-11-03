
# Import our existing sorting function.
# This allows us to reuse code instead of writing the same logic twice.
from backend.transactions.transaction_sorting import sort_transactions


def get_recent_transactions(transactions, limit=5):
    """
    Retrieve the most recent financial transactions.

    Parameters:
        transactions: A list of financial transaction records.
        limit: The maximum number of transactions to return.
               The default is 5.

    Returns:
        A list containing the most recent transactions.
    """

    # Check that the requested limit is a valid positive number.
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 0:
        raise ValueError("The limit must be a non-negative integer.")

    # First arrange all transactions from newest to oldest.
    sorted_transactions = sort_transactions(transactions)

    # Return only the requested number of most recent transactions.
    # [:5] means we take the first five items from the sorted list.
    recent_transactions = sorted_transactions[:limit]

    return recent_transactions
