/* DASHBOARD JAVASCRIPT */

// Descriptions displayed below page headings.
const descriptions = {
    "Dashboard": "Here's your financial overview",
    "Transactions": "View and manage all of your income and expenses",
    "Budgets": "Manage your monthly budgets",
    "Savings Goals": "Track your savings goals",
    "Reports": "View your financial reports",
    "Settings": "Manage your account settings"
};

// Temporary username.
// This will later come from the Flask login session.
let username = window.finSyncUsername || "User";

// Display the user's first initial in the profile icon.
function updateProfile() {
    // Find the part of the page this code will update.
    const profile = document.querySelector(".profile");

    if (profile) {
        profile.textContent = username.charAt(0).toUpperCase();
    }
}

// Choose a greeting based on the current time.
function getGreeting() {
    const hour = new Date().getHours();

    if (hour < 12) {
        return "Good morning";
    } else if (hour < 17) {
        return "Good afternoon";
    } else {
        return "Good evening";
    }
}


/* TRANSACTION DATA */

// Transactions will be retrieved from the database during integration.
let transactions = window.finSyncTransactions || [];


/* FINANCIAL SUMMARY */

// Initial values until financial data becomes available.
let dashboardData = window.finSyncDashboard || {balance: 0, income: 0, expenses: 0, savings: 0};

// Format an amount in South African rand with two decimal places.
function formatCurrency(amount) {
    return "R " + Number(amount).toLocaleString("en-ZA", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Update the financial summary when new data becomes available.

function updateFinancialSummary(data) {
    // Keep the latest figures for when the Dashboard is opened again.
    dashboardData = data;

    // Match each summary card's HTML ID to its value.
    const summaryFields = {
        "total-balance": data.balance,
        "total-income": data.income,
        "total-expenses": data.expenses,
        "total-savings": data.savings
    };

    // Update the cards if they are currently displayed.
    Object.keys(summaryFields).forEach(function (id) {
        const element = document.getElementById(id);

        if (element) {
            element.textContent = formatCurrency(summaryFields[id]);
        }
    });
}


/* DASHBOARD PAGE */

// Handle this part of the page.
function loadDashboard() {
    // Update the Dashboard heading and description.
    document.getElementById("page-title").textContent =
        getGreeting() + ", " + username + "!";

    document.getElementById("page-description").textContent =
        descriptions["Dashboard"];

    const content = document.getElementById("page-content");

    // Display the four summary cards using the latest figures.
    content.innerHTML = `
        <div class="dashboard-summary">

            <div class="summary-card">
                <h3>Total balance</h3>

                <div class="summary-amount" id="total-balance">
                    ${formatCurrency(dashboardData.balance)}
                </div>
            </div>

            <div class="summary-card">
                <h3>Total income</h3>

                <div class="summary-amount" id="total-income">
                    ${formatCurrency(dashboardData.income)}
                </div>
            </div>

            <div class="summary-card">
                <h3>Total expense</h3>

                <div class="summary-amount" id="total-expenses">
                    ${formatCurrency(dashboardData.expenses)}
                </div>
            </div>

            <div class="summary-card">
                <h3>Savings</h3>

                <div class="summary-amount" id="total-savings">
                    ${formatCurrency(dashboardData.savings)}
                </div>
            </div>

        </div>

        <!-- Lashanya's Matplotlib graph, using Mishayle's daily calculations. -->
        <div class="dashboard-chart" id="dashboard-chart">
            <img src="${window.finSyncGraphUrl}" alt="Last 7 days income, expenses and net cash flow" style="width:100%;height:auto;" />
        </div>
    `;
}


/* TRANSACTIONS PAGE HTML */

const transactionsPage = `
    <!-- The Add Transaction form will be connected here. -->
    <div class="transaction-actions">
        <button id="add-transaction-btn" type="button">
            + Add Transaction
        </button>
    </div>

    <div class="transaction-filters">

        <select id="type-filter"
                onchange="displayTransactions()">
            <option value="All">All Transactions</option>
            <option value="Income">Income</option>
            <option value="Expense">Expense</option>
        </select>

        <select id="category-filter"
                onchange="displayTransactions()">
            <option value="All">All Categories</option>
            <option value="Salary">Salary</option>
            <option value="Housing">Housing</option>
            <option value="Groceries">Groceries</option>
            <option value="Transport">Transport</option>
            <option value="Freelance">Freelance</option>
            <option value="Entertainment">Entertainment</option>
            <option value="Utilities">Utilities</option>
            <option value="Other">Other</option>
        </select>
         
        <input type="month"
               id="month-filter"
               onchange="displayTransactions()">

        <button type="button" onclick="clearTransactionFilters()">Clear Filters</button>
    </div>

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


/* PLACEHOLDERS FOR OTHER GROUP MEMBERS' PAGES */

const pages = {
    "Savings Goals":
        "<h2>Savings Goals</h2><p>Your savings goals will appear here.</p>",

    "Reports":
        "<h2>Reports</h2><p>Your financial reports will appear here.</p>",

    "Settings":
        "<h2>Settings</h2><p>Your account settings will appear here.</p>"
};


/* PAGE NAVIGATION */

// Display the page selected from the sidebar.
function showPage(pageName) {
    const content = document.getElementById("page-content");

    if (pageName === "Dashboard") {
        loadDashboard();

    } else if (pageName === "Transactions") {
        document.getElementById("page-title").textContent =
            "Transactions";

        document.getElementById("page-description").textContent =
            descriptions["Transactions"];

        content.innerHTML = transactionsPage;

        displayTransactions();

    } else if (pages[pageName] !== undefined) {
        document.getElementById("page-title").textContent =
            pageName;

        document.getElementById("page-description").textContent =
            descriptions[pageName];

        content.innerHTML =
            '<div class="page-box">' + pages[pageName] + "</div>";
    }

    // Highlight the selected navigation button.
    const buttons = document.querySelectorAll(".nav-btn");

    buttons.forEach(function (button) {
        if (button.dataset.page === pageName) {
            button.classList.add("active");
        } else {
            button.classList.remove("active");
        }
    });
}


/* TRANSACTION TABLE */

// Display transactions that match the selected filters.
function displayTransactions() {
    const table = document.getElementById("transaction-list");

    // The table does not exist when another page is displayed.
    if (!table) {
        return;
    }

    const type = document.getElementById("type-filter").value;
    const category = document.getElementById("category-filter").value;
    const month = document.getElementById("month-filter").value;

    table.innerHTML = "";

    const filtered = transactions.filter(function (transaction) {
        const matchesType =
            type === "All" || transaction.type === type;

        const matchesCategory =
            category === "All" ||
            transaction.category === category;

        const matchesMonth =
            month === "" || transaction.date.startsWith(month);

        return matchesType && matchesCategory && matchesMonth;
    });

    filtered.forEach(function (transaction) {
        const row = document.createElement("tr");

        // Format the stored transaction date for display.
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

        // Use textContent to display transaction details as text.
        values.forEach(function (value) {
            const cell = document.createElement("td");

            cell.textContent = value;
            row.appendChild(cell);
        });

        const amountCell = document.createElement("td");

        const amount = Number(transaction.amount).toLocaleString(
            "en-ZA",
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }
        );

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

    // Display an appropriate message if there are no results.
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


// Reset all transaction filters.
function clearTransactionFilters() {
    document.getElementById("type-filter").value = "All";
    document.getElementById("category-filter").value = "All";
    document.getElementById("month-filter").value = "";
    displayTransactions();
}


/* NAVIGATION BUTTON EVENTS */

// Find the part of the page this code will update.
const navButtons = document.querySelectorAll(".nav-btn");

navButtons.forEach(function (button) {
    // Run this code when the user interacts with the page.
    button.addEventListener("click", function () {

        // Open Transactions
        if (button.dataset.page === "Transactions") {
            window.location.href = "/transactions";
            return;
        }

        // MISHAYLE: Open Michalyn's real Budgets page
        if (button.dataset.page === "Budgets") {
            window.location.href = "/budgets";
            return;
        }

        // MISHAYLE: Open the Savings Goals dashboard
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
        // Keep existing navigation for other pages
        showPage(button.dataset.page);
    });
});



/* TEMPORARY LOGOUT */

// Flask authentication will provide the actual logout behaviour.
document.getElementById("logout-btn").addEventListener(
    "click",
    function () {
        window.location.href = window.finSyncLogoutUrl;
    }
);


/* INITIAL PAGE LOAD */

updateProfile();
showPage("Dashboard");