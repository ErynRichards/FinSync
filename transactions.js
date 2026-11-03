// Sample records are used until the backend is connected.
// Store money as integer cents: 125000 cents equals R1,250.00.
const transactions = [
    {
        date: "2026-05-02",
        category: "Salary",
        description: "Monthly salary payment",
        type: "Income",
        cents: 1500000
    },
    {
        date: "2026-05-05",
        category: "Housing",
        description: "Monthly rent payment",
        type: "Expense",
        cents: 450000
    },
    {
        date: "2026-05-09",
        category: "Groceries",
        description: "Grocery shopping",
        type: "Expense",
        cents: 125000
    },
    {
        date: "2026-05-14",
        category: "Transport",
        description: "Fuel expenses",
        type: "Expense",
        cents: 85000
    },
    {
        date: "2026-05-20",
        category: "Freelance",
        description: "Website design project",
        type: "Income",
        cents: 250000
    },
    {
        date: "2026-05-26",
        category: "Entertainment",
        description: "Movie and dinner",
        type: "Expense",
        cents: 65000
    }
];

// These categories are available for both the form and filter.
const categories = [
    "Salary",
    "Freelance",
    "Allowance",
    "Housing",
    "Groceries",
    "Transport",
    "Entertainment",
    "Education",
    "Utilities",
    "Other"
];

// This helper finds an HTML element using its ID.
function getElement(id) {
    return document.getElementById(id);
}

// Store references to the form and dialog.
const form = getElement("transactionForm");
const dialog = getElement("transactionDialog");

// Add the same categories to the form and category filter.
categories.forEach(function (category) {
    const formOption = document.createElement("option");
    formOption.value = category;
    formOption.textContent = category;

    getElement("category").appendChild(formOption);

    const filterOption = document.createElement("option");
    filterOption.value = category;
    filterOption.textContent = category;

    getElement("categoryFilter").appendChild(filterOption);
});

// Display records that match all active search and filter controls.
function displayTransactions() {
    const search = getElement("search").value.trim().toLowerCase();
    const type = getElement("typeFilter").value;
    const category = getElement("categoryFilter").value;
    const month = getElement("monthFilter").value;

    const tableBody = getElement("transactionRows");

    // Remove old rows before drawing the updated results.
    tableBody.replaceChildren();

    const results = transactions.filter(function (transaction) {
        const text =
            (transaction.description + " " + transaction.category)
                .toLowerCase();

        const matchesSearch = text.includes(search);

        const matchesType =
            type === "" || transaction.type === type;

        const matchesCategory =
            category === "" || transaction.category === category;

        const matchesMonth =
            month === "" || transaction.date.startsWith(month);

        return matchesSearch &&
            matchesType &&
            matchesCategory &&
            matchesMonth;
    });

    // Put the newest dates at the top of the table.
    results.sort(function (a, b) {
        return b.date.localeCompare(a.date);
    });

    // Create one table row for each matching transaction.
    results.forEach(function (transaction) {
        const row = document.createElement("tr");

        const date = new Date(transaction.date + "T00:00:00");

        const formattedDate = date.toLocaleDateString("en-ZA", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        });

        const amount = new Intl.NumberFormat("en-ZA", {
            style: "currency",
            currency: "ZAR"
        }).format(transaction.cents / 100);

        const sign = transaction.type === "Income" ? "+ " : "- ";

        const values = [
            formattedDate,
            transaction.category,
            transaction.description,
            transaction.type,
            sign + amount
        ];

        values.forEach(function (value, index) {
            const cell = document.createElement("td");

            // Display user-entered text safely instead of inserting HTML.
            cell.textContent = value;

            // Colour the amount according to the transaction type.
            if (index === 4) {
                cell.className = transaction.type.toLowerCase();
            }

            row.appendChild(cell);
        });

        tableBody.appendChild(row);
    });

    // Show a message when no transactions match.
    getElement("emptyMessage").hidden = results.length !== 0;
}

// Clear all search and filter values.
function clearFilters() {
    getElement("search").value = "";
    getElement("typeFilter").value = "";
    getElement("categoryFilter").value = "";
    getElement("monthFilter").value = "";

    displayTransactions();
}

// Open the form and insert today's local date.
getElement("openForm").addEventListener("click", function () {
    form.reset();

    const today = new Date();

    getElement("date").value =
        today.getFullYear() + "-" +
        String(today.getMonth() + 1).padStart(2, "0") + "-" +
        String(today.getDate()).padStart(2, "0");

    dialog.showModal();
});

// Cancel closes the dialog without adding a record.
getElement("cancelForm").addEventListener("click", function () {
    dialog.close();
});

// Reject descriptions that contain only spaces.
// The browser displays this message when Save is clicked.
getElement("description").addEventListener("input", function () {
    const description = getElement("description");

    if (description.value.trim() === "") {
        description.setCustomValidity("Please enter a description.");
    } else {
        description.setCustomValidity("");
    }
});

// The HTML required, min, max and step attributes provide basic validation.
// The submit event runs after the browser accepts the form inputs.
form.addEventListener("submit", function (event) {
    // Prevent submission from reloading the page.
    event.preventDefault();

    const newTransaction = {
        date: getElement("date").value,
        category: getElement("category").value,
        description: getElement("description").value.trim(),
        type: getElement("type").value,

        // Convert rand to integer cents before storing the amount.
        cents: Math.round(Number(getElement("amount").value) * 100)
    };

    // Add the new record to the frontend array.
    // A Flask request will replace this step during backend integration.
    transactions.push(newTransaction);

    // Clear filters so the newly added record is visible.
    clearFilters();

    dialog.close();

    getElement("message").textContent =
        "Transaction added for this session. " +
        "It has not been saved to the database.";
});

// Update the table whenever the search or filters change.
const filterIds = [
    "search",
    "typeFilter",
    "categoryFilter",
    "monthFilter"
];

filterIds.forEach(function (id) {
    getElement(id).addEventListener("input", displayTransactions);
});

// Connect the Clear filters button.
getElement("clearFilters").addEventListener("click", clearFilters);

// Display the sample transactions when the page opens.
displayTransactions();