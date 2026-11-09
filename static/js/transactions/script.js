// Descriptions for each page
const descriptions = {
    "Dashboard": "Overview of your financial activity",
    "Transactions": "View and manage all of your income and expenses",
    "Budgets": "Manage your monthly budgets",
    "Savings Goals": "Track your savings goals",
    "Reports": "View your financial reports",
    "Settings": "Manage your account settings"
};

// Empty transaction list
// Data will be retrieved from the database later
let transactions = [];

// Transactions screen HTML
const transactionsPage = `

    <!-- Add Transaction button -->

    <div class="transaction-actions">

        <button id="add-transaction-btn" type="button">
            + Add Transaction
        </button>

    </div>

    <p id="transactions-status" role="status"></p>
    <p class="preview-note">Transactions are saved to your FinSync account.</p>
    <!-- Transaction filters -->
    <div class="transaction-filters">

        <select aria-label="Transaction type" id="type-filter" onchange="displayTransactions()">
            <option value="All">All Transactions</option>
            <option value="Income">Income</option>
            <option value="Expense">Expense</option>
        </select>

        <select aria-label="Category filter" id="category-filter" onchange="displayTransactions()">
            <option value="All">All Categories</option>
            <option value="Salary">Salary</option>
            <option value="Housing">Housing</option>
            <option value="Groceries">Groceries</option>
            <option value="Transport">Transport</option>
            <option value="Freelance">Freelance</option>
            <option value="Entertainment">Entertainment</option>
            <option value="Allowance">Allowance</option>
            <option value="Education">Education</option>
            <option value="Utilities">Utilities</option>
            <option value="Other expense">Other expense</option>
            <option value="Other income">Other income</option>
            <option value="Other">Other</option>
        </select>

        
    <!-- Month and year calendar filter -->
    <div class="month-filter-container">
        <input
            type="month"
            id="month-filter"
            aria-label="Select month and year"
            title="Select month and year"
            onchange="displayTransactions()"
        >
    </div>

        <button type="button" id="clear-filters-btn" onclick="clearTransactionFilters()">Clear Filters</button>

    </div>

    <!-- Transaction table -->
    <div class="table-container">

        <table class="transaction-table">

            <thead>
                <tr>
                    <th>Date</th>
                    <th>Category</th>
                    <th>Description</th>
                    <th>Type</th>
                    <th>Amount (ZAR)</th>
                </tr>
            </thead>

            <tbody id="transaction-list"></tbody>

        </table>

    </div>
`;

// Temporary content for other screens
const pages = {
    "Dashboard": "<h2>Dashboard Overview</h2><p>Your financial summary will appear here.</p>",

    "Budgets": "<h2>Budgets</h2><p>Your budgets will appear here.</p>",

    "Savings Goals": "<h2>Savings Goals</h2><p>Your savings goals will appear here.</p>",

    "Reports": "<h2>Reports</h2><p>Your financial reports will appear here.</p>",

    "Settings": "<h2>Settings</h2><p>Your account settings will appear here.</p>"
};

// Function to change pages
function showPage(pageName) {

    // Change page heading
    document.getElementById("page-title").textContent = pageName;

    // Change page description
    document.getElementById("page-description").textContent =
        descriptions[pageName];

    // Get main content area
    const content = document.getElementById("page-content");

    // Display Transactions screen
    if (pageName === "Transactions") {

        content.innerHTML = transactionsPage;

        document.getElementById("add-transaction-btn").addEventListener("click", function () {
            window.AddTransactionForm.open();
        });

        // Display available transactions
        displayTransactions();

    } else {

        // Display temporary content for other screens
        content.innerHTML =
            '<div class="page-box">' + pages[pageName] + '</div>';
    }

    // Highlight selected navigation button
    const buttons = document.querySelectorAll(".nav-btn");

    buttons.forEach(function(button) {

        if (button.dataset.page === pageName) {
            button.classList.add("active");
        } else {
            button.classList.remove("active");
        }

    });
}

// Display transactions in the table
function displayTransactions() {

    const table = document.getElementById("transaction-list");

    if (!table) {
        return;
    }

    // Get selected filters
    const type = document.getElementById("type-filter").value;
    const category = document.getElementById("category-filter").value;
    const month = document.getElementById("month-filter").value;

    // Clear existing rows
    table.innerHTML = "";

    // Filter transactions
    const filtered = transactions.filter(function(transaction) {

        const matchesType =
            type === "All" || transaction.type === type;

        const matchesCategory =
            category === "All" || transaction.category === category;

        const matchesMonth =
            month === "" || transaction.date.startsWith(month);
        return matchesType && matchesCategory && matchesMonth;
    });

    // Display matching transactions
    filtered.forEach(function(transaction) {

        const row = document.createElement("tr");

        // Format transaction date
        const date = new Date(transaction.date + "T00:00:00");

        const formattedDate = date.toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        });

        // Add transaction details
        const values = [
            formattedDate,
            transaction.category,
            transaction.description,
            transaction.type
        ];

        values.forEach(function(value) {

            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);

        });

        // Format amount
        const amountCell = document.createElement("td");

        const amount = Number(transaction.amount).toLocaleString("en-ZA", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });

        if (transaction.type === "Income") {

            amountCell.textContent = "+R " + amount;
            amountCell.className = "income";

        } else {

            amountCell.textContent = "-R " + amount;
            amountCell.className = "expense";
        }

        row.appendChild(amountCell);
        table.appendChild(row);
    });

    // Display message if no transactions exist
    if (filtered.length === 0) {

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 5;
        cell.className = "empty-message";

        if (transactions.length === 0) {

            cell.textContent =
                "No transactions found. Add your first transaction to get started.";

        } else {

            cell.textContent = "No matching transactions found.";
        }

        row.appendChild(cell);
        table.appendChild(row);
    }
}

// Reset transaction type, category and calendar filters.
function clearTransactionFilters() {
    document.getElementById("type-filter").value = "All";
    document.getElementById("category-filter").value = "All";
    document.getElementById("month-filter").value = "";
    displayTransactions();
}

// Connect navigation buttons

const navButtons = document.querySelectorAll(".nav-btn");

navButtons.forEach(function(button) {

    button.addEventListener("click", function() {

        // Open the main Dashboard
        if (button.dataset.page === "Dashboard") {
            window.location.href = "/dashboard";
            return;
        }

        // MISHAYLE: Open Michalyn's Budgets dashboard
        if (button.dataset.page === "Budgets") {
            window.location.href = "/budgets";
            return;
        }

        // MISHAYLE: Open Savings Goals
        if (button.dataset.page === "Savings Goals") {
            window.location.href = "/savings-goals";
            return;
        }

        // MISHAYLE: Open the Reports page
        if (button.dataset.page === "Reports") {
            window.location.href = "/reports";
            return;
        }
        if (button.dataset.page === "Settings") {
            window.location.href = "/settings";
            return;
        }

        // Keep the existing navigation for other pages
        showPage(button.dataset.page);
    });

});


// Temporary logout function
document.getElementById("logout-btn").addEventListener("click", function() {

    window.location.href = "/logout";

});

// Display Transactions when the application opens
showPage("Transactions");

// Backend team can replace save/list without changing the form layout.
// Default save is session-only; no database success is claimed.
window.FinSyncTransactions = {
    persistent: true,
    async save(transaction) {
    const response = await fetch("/api/transactions", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(transaction)
    });

    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.error || "Could not save transaction");
    }

    // MISHAYLE: Check budget notifications after saving an expense
    if (transaction.type?.toLowerCase() === "expense") {
        window.checkBudgetNotifications?.();
    }

    return result;
},
    setTransactions(records) {
        transactions = records;
        displayTransactions();
    },
    addToTable(transaction) {
        transactions.push(transaction);
        ["type-filter", "category-filter"].forEach(id => document.getElementById(id).value = "All");
        document.getElementById("month-filter").value = "";
        displayTransactions();
        document.getElementById("transactions-status").textContent = "Transaction saved.";
    }
};

fetch("/api/transactions").then(response => response.json()).then(records => {
    if (Array.isArray(records)) window.FinSyncTransactions.setTransactions(records);
}).catch(error => console.error("Could not load transactions", error));
