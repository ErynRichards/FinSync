
// Page descriptions
const descriptions = {
    "Dashboard": "Overview of your financial activity",
    "Transactions": "View and manage all of your income and expenses",
    "Budgets": "Manage your monthly budgets",
    "Goals": "Track your savings goals",
    "Reports": "View your financial reports",
    "Settings": "Manage your account settings"
};

// Available transaction categories
const transactionCategories = {

    Expense: [
        "Groceries",
        "Housing",
        "Transport",
        "Entertainment",
        "Education",
        "Utilities",
        "Other expense"
    ],

    Income: [
        "Salary",
        "Freelance",
        "Allowance",
        "Other income"
    ]

};

// Start with an empty transaction list
let transactions = [];

// Transactions page
const transactionsPage = `

    <!-- Add Transaction button -->
    <div class="transaction-actions">

        <button id="add-transaction-btn" type="button">
            + Add Transaction
        </button>

    </div>

    <!-- Filters -->
    <div class="transaction-filters">

        <!-- Type filter -->
        <select id="type-filter" aria-label="Filter by type">

            <option value="All">All Transactions</option>
            <option value="Income">Income</option>
            <option value="Expense">Expense</option>

        </select>

        <!-- Category filter -->
        <select id="category-filter" aria-label="Filter by category">

            <option value="All">All Categories</option>

        </select>

        <!-- Month calendar -->
        <div class="month-filter-container">

            <input
                type="month"
                id="month-filter"
                aria-label="Select month and year"
                title="Select month and year"
            >

            <button type="button" id="clear-month-btn">
                Clear
            </button>

        </div>

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

    <p id="transactions-status" role="status"></p>
`;

// Other pages
const pages = {
    "Dashboard": "<h2>Dashboard Overview</h2><p>Your financial summary will appear here.</p>",
    "Budgets": "<h2>Budgets</h2><p>Your budgets will appear here.</p>",
    "Goals": "<h2>Goals</h2><p>Your savings goals will appear here.</p>",
    "Reports": "<h2>Reports</h2><p>Your financial reports will appear here.</p>",
    "Settings": "<h2>Settings</h2><p>Your account settings will appear here.</p>"
};

// Display selected page
function showPage(pageName) {

    document.getElementById("page-title").textContent = pageName;

    document.getElementById("page-description").textContent =
        descriptions[pageName];

    const content = document.getElementById("page-content");

    if (pageName === "Transactions") {

        content.innerHTML = transactionsPage;

        // Add Transaction button
        document.getElementById("add-transaction-btn")
            .addEventListener("click", function () {

                window.AddTransactionForm.open();

            });

        // Type filter
        document.getElementById("type-filter")
            .addEventListener("change", function () {

                updateCategoryFilter();
                displayTransactions();

            });

        // Category filter
        document.getElementById("category-filter")
            .addEventListener("change", displayTransactions);

        // Month filter
        document.getElementById("month-filter")
            .addEventListener("change", displayTransactions);

        // Clear month
        document.getElementById("clear-month-btn")
            .addEventListener("click", function () {

                document.getElementById("month-filter").value = "";

                displayTransactions();

            });

        // Load all categories
        updateCategoryFilter();

        // Display table
        displayTransactions();

    } else {

        content.innerHTML =
            '<div class="page-box">' + pages[pageName] + '</div>';

    }

    // Active navigation button
    document.querySelectorAll(".nav-btn").forEach(function (button) {

        button.classList.toggle(
            "active",
            button.dataset.page === pageName
        );

    });
}

// Update category dropdown
function updateCategoryFilter() {

    const typeFilter = document.getElementById("type-filter");
    const categoryFilter = document.getElementById("category-filter");

    if (!typeFilter || !categoryFilter) {
        return;
    }

    const selectedType = typeFilter.value;
    const previousCategory = categoryFilter.value;

    // Clear category dropdown
    categoryFilter.innerHTML =
        '<option value="All">All Categories</option>';

    let categories = [];

    // Show expense categories
    if (selectedType === "Expense") {

        categories = transactionCategories.Expense;

    }

    // Show income categories
    else if (selectedType === "Income") {

        categories = transactionCategories.Income;

    }

    // Show all categories
    else {

        categories = [
            ...transactionCategories.Expense,
            ...transactionCategories.Income
        ];

    }

    // Add category options
    categories.forEach(function (category) {

        const option = document.createElement("option");

        option.value = category;
        option.textContent = category;

        categoryFilter.appendChild(option);

    });

    // Keep previous category if available
    if (categories.includes(previousCategory)) {

        categoryFilter.value = previousCategory;

    }
}

// Display transactions
function displayTransactions() {

    const table = document.getElementById("transaction-list");

    if (!table) {
        return;
    }

    // Selected filters
    const type = document.getElementById("type-filter").value;
    const category = document.getElementById("category-filter").value;
    const month = document.getElementById("month-filter").value;

    // Clear table
    table.innerHTML = "";

    // Filter transactions
    const filtered = transactions.filter(function (transaction) {

        const matchesType =
            type === "All" || transaction.type === type;

        const matchesCategory =
            category === "All" || transaction.category === category;

        const matchesMonth =
            month === "" || transaction.date.startsWith(month);

        return matchesType && matchesCategory && matchesMonth;

    });

    // Sort newest first
    filtered.sort(function (a, b) {

        return b.date.localeCompare(a.date);

    });

    // Add transaction rows
    filtered.forEach(function (transaction) {

        const row = document.createElement("tr");

        // Format date
        const date = new Date(transaction.date + "T00:00:00");

        const formattedDate = date.toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        });

        const values = [
            formattedDate,
            transaction.category,
            transaction.description,
            transaction.type
        ];

        // Add text cells
        values.forEach(function (value) {

            const cell = document.createElement("td");

            cell.textContent = value;

            row.appendChild(cell);

        });

        // Amount cell
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

    // Empty table message
    if (filtered.length === 0) {

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 5;
        cell.className = "empty-message";

        if (transactions.length === 0) {

            cell.textContent =
                "No transactions recorded yet. Click Add Transaction to get started.";

        } else {

            cell.textContent = "No matching transactions found.";

        }

        row.appendChild(cell);
        table.appendChild(row);

    }
}

// Add new transaction
function addTransaction(transaction) {

    // Save transaction in array
    transactions.push(transaction);

    // Reset filters
    document.getElementById("type-filter").value = "All";

    updateCategoryFilter();

    document.getElementById("category-filter").value = "All";
    document.getElementById("month-filter").value = "";

    // Update table
    displayTransactions();

    document.getElementById("transactions-status").textContent =
        "Transaction added successfully for this session.";

}

// Navigation buttons
document.querySelectorAll(".nav-btn").forEach(function (button) {

    button.addEventListener("click", function () {

        showPage(button.dataset.page);

    });

});

// Logout
document.getElementById("logout-btn")
    .addEventListener("click", function () {

        alert("Logout will be connected to the login system later.");

    });

// Open Transactions page
showPage("Transactions");

// Allow Add Transaction form to add records
window.FinSyncTransactions = {
    addToTable: addTransaction
};
