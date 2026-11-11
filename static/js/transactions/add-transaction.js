// Keep form variables separate from the Transactions page variables.
(function () {
// Find the form and its input fields.
const form = document.getElementById("transactionForm");
const typeInput = document.getElementById("transactionType");
const amountInput = document.getElementById("amount");
const descriptionInput = document.getElementById("description");
const categoryInput = document.getElementById("category");

const dayInput = document.getElementById("day");
const monthInput = document.getElementById("month");
const yearInput = document.getElementById("year");

const message = document.getElementById("message");

// Income and Expense have different category choices.
const categories = {
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

// Load available categories from Daniel's database.
// MISHAYLE: Load categories from the database
// while keeping the additional categories.

fetch("/api/transaction-options")
    .then(response => {
        if (!response.ok) {
            throw new Error("Could not load categories");
        }
        return response.json();
    })
    .then(options => {
        if (!Array.isArray(options.categories)) return;

        const dbExpenses = options.categories
            .filter(c => c.category_type === "expense")
            .map(c => c.category_name);

        const dbIncome = options.categories
            .filter(c => c.category_type === "income")
            .map(c => c.category_name);

        categories.Expense = [
            ...new Set([...categories.Expense, ...dbExpenses])
        ];

        categories.Income = [
            ...new Set([...categories.Income, ...dbIncome])
        ];

        updateCategories();
    })
    .catch(error => {
        console.error("Could not load categories", error);
    });

// Fill the category dropdown for the selected transaction type.
function updateCategories() {
    categoryInput.replaceChildren();

    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Select category";

    categoryInput.appendChild(placeholder);

    categories[typeInput.value].forEach(function (category) {
        const option = document.createElement("option");

        option.value = category;
        option.textContent = category;

        categoryInput.appendChild(option);
    });

    descriptionInput.placeholder =
        typeInput.value === "Expense"
            ? "E.g. Checkers"
            : "E.g. Monthly salary";

    message.textContent = "";
}

// Validate descriptions containing spaces only.
function validateDescription() {
    if (descriptionInput.value.trim() === "") {
        descriptionInput.setCustomValidity(
            "Please enter a description."
        );
    } else {
        descriptionInput.setCustomValidity("");
    }
}

// Check that the entered day, month and year form a real date.
function validateDate() {
    // Clear any previous calendar error before checking again.
    dayInput.setCustomValidity("");

    // HTML validation handles empty fields and numeric limits.
    if (
        !dayInput.value ||
        !monthInput.value ||
        !yearInput.value ||
        !dayInput.validity.valid ||
        !monthInput.validity.valid ||
        !yearInput.validity.valid
    ) {
        return;
    }

    const day = Number(dayInput.value);
    const month = Number(monthInput.value);
    const year = Number(yearInput.value);

    const date = new Date(year, month - 1, day);

    // JavaScript rolls impossible dates into the following month.
    // Comparing each part catches dates such as 31 February.
    if (
        date.getFullYear() !== year ||
        date.getMonth() !== month - 1 ||
        date.getDate() !== day
    ) {
        dayInput.setCustomValidity(
            "Please enter a real calendar date."
        );
    }
}

// Reset the form and clear validation feedback.
function resetForm() {
    form.reset();

    descriptionInput.setCustomValidity("");
    dayInput.setCustomValidity("");

    selectTransactionType("Expense");
    message.textContent = "";
}

// Update categories when Income or Expense is selected.

const expenseButton = document.getElementById("expenseButton");
const incomeButton = document.getElementById("incomeButton");

function selectTransactionType(type) {
    typeInput.value = type;

    expenseButton.classList.toggle("selected", type === "Expense");
    incomeButton.classList.toggle("selected", type === "Income");

    expenseButton.setAttribute("aria-pressed", type === "Expense");
    incomeButton.setAttribute("aria-pressed", type === "Income");

    updateCategories();
}

expenseButton.addEventListener("click", function () {
    selectTransactionType("Expense");
});

incomeButton.addEventListener("click", function () {
    selectTransactionType("Income");
});

typeInput.addEventListener("change", function () {
    selectTransactionType(typeInput.value);
});


// Update validation while users correct their entries.
descriptionInput.addEventListener("input", function () {
    validateDescription();
    message.textContent = "";
});

[dayInput, monthInput, yearInput].forEach(function (input) {
    input.addEventListener("input", function () {
        validateDate();
        message.textContent = "";
    });
});

// Clear old preview feedback if other form values change.
amountInput.addEventListener("input", function () {
    message.textContent = "";
});

categoryInput.addEventListener("change", function () {
    message.textContent = "";
});

// Close the shared dialog without adding a record.
const dialog = document.getElementById("transactionDialog");
const saveButton = document.getElementById("saveButton");
let saving = false;
document.getElementById("cancelButton").addEventListener("click", function () {
    if (!saving) dialog.close();
});
dialog.addEventListener("cancel", function (event) {
    if (saving) event.preventDefault();
});

// Validate first, then call the backend-ready save function.
form.addEventListener("submit", async function (event) {
    event.preventDefault();
    if (saving) return;
    validateDescription();
    validateDate();
    if (!form.reportValidity()) return;
    const transaction = {
        type: typeInput.value,
        amount: Number(amountInput.value).toFixed(2),
        description: descriptionInput.value.trim(),
        category: categoryInput.value,
        date: String(Number(yearInput.value)).padStart(4, "0") + "-" +
            String(Number(monthInput.value)).padStart(2, "0") + "-" +
            String(Number(dayInput.value)).padStart(2, "0")
    };
    saving = true;
    saveButton.disabled = true;
    document.getElementById("cancelButton").disabled = true;
    message.classList.remove("error");
    message.textContent = "Saving transaction...";
    // Freeze inputs while waiting so the visible data matches the request.
    const inputs = form.querySelectorAll("input, select");
    inputs.forEach(input => input.disabled = true);
    try {
        const saved = await window.FinSyncTransactions.save(transaction);
        // Adapter must return the saved record, including its five fields.
        if (!saved || saved.type !== transaction.type || !saved.date ||
            !saved.category || !saved.description || !Number.isFinite(Number(saved.amount)) || Number(saved.amount) <= 0) {
            throw new Error("The saved transaction response is incomplete.");
        }
        window.FinSyncTransactions.addToTable(saved);
        dialog.close();
    } catch (error) {
        message.classList.add("error");
        message.textContent = "Could not save the transaction. Please try again.";
        // Keep entered values so the user can retry.
    } finally {
        saving = false;
        saveButton.disabled = false;
        document.getElementById("cancelButton").disabled = false;
        inputs.forEach(input => input.disabled = false);
    }
});

// Called by the partner's Add Transaction button.
window.AddTransactionForm = {
    open() {
        resetForm();
        message.classList.remove("error");
        dialog.showModal();
    }
};
resetForm();

})();
