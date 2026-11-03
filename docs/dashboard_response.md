# FinSync – Dashboard Backend Response Documentation

## 1. Purpose

This document describes the financial information prepared by the FinSync backend for display on the Dashboard.

The Dashboard is designed to help users understand their financial position by displaying their account balance, income, expenses, recent transactions and overall transaction activity.

The backend processes and validates transaction information before preparing the Dashboard response.

## 2. Dashboard Information

The backend currently prepares the following information:

| Dashboard Information | Description |
|---|---|
| Account Balance | Displays the calculated current account balance when an opening balance is provided. |
| Total Income | Calculates the total money received from income transactions. |
| Total Expenses | Calculates the total money spent through expense transactions. |
| Net Cash Flow | Calculates the difference between total income and total expenses. |
| Recent Transactions | Retrieves the five most recent transactions, ordered from newest to oldest. |
| Transaction Count | Displays the total number of transactions processed. |

## 3. Transaction Information Required

Each transaction supplied to the backend must contain the following information:

| Field | Description |
|---|---|
| transaction_id | Unique identifier for the transaction. |
| description | Description of the financial transaction. |
| amount | Monetary value of the transaction. |
| transaction_type | Indicates whether the transaction is income or expense. |
| transaction_date | Date on which the transaction occurred, using YYYY-MM-DD format. |

These fields are currently used by the backend functions to validate, sort and calculate financial information.

Additional fields, such as account ID and category ID, may be incorporated when the agreed database structure is available.

## 4. Transaction Validation

Before transaction information is processed, the backend checks whether the supplied information is valid.

The following validation rules are applied:

- A transaction must be provided as a dictionary.
- All required transaction fields must be present.
- The transaction ID must be a positive integer.
- The description must contain valid text and cannot be empty.
- The transaction amount must be a valid positive financial value.
- The transaction type must be either income or expense.
- The transaction date must be a valid date in YYYY-MM-DD format.

If a transaction contains invalid information, the backend returns validation errors and prevents invalid transaction data from being used in the Dashboard calculations.

## 5. Transaction Sorting

The backend includes a transaction sorting function that arranges transactions according to their transaction date.

Transactions are displayed in descending date order, meaning the newest transaction appears first.

The sorting functionality uses Python's built-in sorted() function with reverse=True.

The original transaction list is not modified during sorting.

## 6. Financial Summary Calculations

The backend calculates three financial summary values.

### 6.1 Total Income

Total income represents the combined value of all transactions classified as income.

### 6.2 Total Expenses

Total expenses represent the combined value of all transactions classified as expenses.

### 6.3 Net Cash Flow

Net cash flow represents the difference between the user's total income and total expenses.

**Formula:**

Net Cash Flow = Total Income - Total Expenses

All financial calculations use Python's Decimal data type to improve monetary calculation accuracy.

## 7. Account Balance Calculation

The backend includes an account balance calculation function.

The current account balance is calculated using the account's opening balance and its validated financial transactions.

**Formula:**

Current Balance = Opening Balance + Total Income - Total Expenses

Income transactions increase the account balance, while expense transactions decrease it.

The opening balance is currently an optional parameter because the shared database has not yet been integrated.

If an opening balance is not provided, the Dashboard returns null for the account_balance field rather than assuming that the account balance is R0.00.

### Current Calculation Scope

- The calculation currently processes transactions belonging to one account at a time.
- All transactions are validated before they are included in the calculation.
- Invalid transactions are rejected.
- Transfers between accounts are not yet supported.
- Actual account balances will depend on the account information and transaction records retrieved from the shared database.

## 8. Recent Transactions

The backend retrieves the five most recent transactions for display on the Dashboard.

The transactions are first sorted from newest to oldest before the five most recent records are selected.

The function also supports an adjustable limit, allowing the number of returned transactions to be changed when required.

If fewer than five transactions exist, all available transactions are returned.

If no transactions exist, an empty list is returned.

## 9. Dashboard Response Structure

The backend combines the processed financial information into a single Dashboard response.

The current response structure is illustrated below:

```json
{
    "account_balance": "34150.00",
    "financial_summary": {
        "total_income": "25000.00",
        "total_expenses": "850.00",
        "net_cash_flow": "24150.00"
    },
    "recent_transactions": [
        {
            "transaction_id": 2,
            "description": "Groceries",
            "amount": "850.00",
            "transaction_type": "expense",
            "transaction_date": "2026-11-02"
        },
        {
            "transaction_id": 1,
            "description": "Monthly Salary",
            "amount": "25000.00",
            "transaction_type": "income",
            "transaction_date": "2026-11-01"
        }
    ],
    "transaction_count": 2
}
```

**Note:** The example demonstrates the expected response structure. Actual information will be populated using the user's transaction and account records.

If an opening balance is unavailable, account_balance will return null.

## 10. Backend Components Developed

The following Python files have been developed as part of the FinSync Dashboard backend functionality:

| File | Responsibility |
|---|---|
| transaction_sorting.py | Sorts transactions from newest to oldest. |
| transaction_summary.py | Calculates total income, expenses and net cash flow. |
| recent_transactions.py | Retrieves the most recent transactions. |
| transaction_validation.py | Validates transaction information. |
| account_balance.py | Calculates the account balance using an opening balance and transactions. |
| dashboard_service.py | Combines the financial calculations and prepares the Dashboard response. |

## 11. Testing and Verification

Automated unit tests have been developed to verify that the backend functions operate correctly.

The following functionality has been tested:

- Sorting transactions from newest to oldest.
- Ensuring the original transaction list remains unchanged.
- Calculating total income and expenses.
- Calculating net cash flow.
- Retrieving the five most recent transactions.
- Handling empty transaction lists.
- Validating required transaction information.
- Rejecting invalid transaction amounts, dates and transaction types.
- Calculating account balances using opening balances.
- Rejecting invalid opening balances.
- Preparing the complete Dashboard response.
- Handling situations where an opening balance is not supplied.

**Testing result: 28 out of 28 automated unit tests passed successfully.**

## 12. Outstanding Development Requirements

The current backend functionality has been developed and tested using sample transaction data.

The following activities remain necessary before full database and frontend integration:

1. Obtain the shared MySQL database hostname, port and authorised connection credentials.
2. Confirm the agreed database structure with the FinSync development team.
3. Confirm the account, transaction and category table structures and relationships.
4. Establish the Python-to-MySQL database connection.
5. Retrieve actual account and transaction information from the database.
6. Connect the Dashboard backend functionality to the Flask API.
7. Integrate the API response with the Dashboard frontend.
8. Test the complete process using actual database records.

## 13. Current Development Status

The transaction processing and Dashboard data preparation functionality has been developed in Python.

The backend currently supports transaction sorting, financial summaries, transaction validation, recent transaction retrieval and account balance calculations.

All 28 automated unit tests have passed successfully.

Database connectivity, actual account data retrieval, Flask API integration and frontend integration remain outstanding.

The current implementation therefore provides the foundation for connecting FinSync's financial transaction functionality to the Dashboard.

---

**Project:** FINSYNC – Intelligent Financial Wellness Banking System

**Tagline:** Helping users understand their money – not just see their balance.