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

    updateCategories();
    message.textContent = "";
}

// Update categories when Income or Expense is selected.
typeInput.addEventListener("change", updateCategories);

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

// Cancel clears this standalone form.
// During integration, this can also close your partner's dialog.
document.getElementById("cancelButton").addEventListener(
    "click",
    function () {
        resetForm();

        message.textContent =
            "Entry cancelled. The form has been cleared.";
    }
);

// Validate and collect the transaction without reloading the page.
form.addEventListener("submit", function (event) {
    event.preventDefault();

    validateDescription();
    validateDate();

    if (!form.reportValidity()) {
        return;
    }

    // Format the date as YYYY-MM-DD for backend integration.
    const formattedDate =
        yearInput.value.padStart(4, "0") + "-" +
        monthInput.value.padStart(2, "0") + "-" +
        dayInput.value.padStart(2, "0");

    const transaction = {
        type: typeInput.value,
        amount: amountInput.value,
        description: descriptionInput.value.trim(),
        category: categoryInput.value,
        date: formattedDate
    };

    /*
     * Send this transaction using fetch() once the Python developer
     * provides the endpoint and confirms the expected field names.
     * Show a saved message only after the backend confirms success.
     */

    message.textContent =
        transaction.type +
        " details validated. Preview only: nothing has been saved.";
});

// Start with the Expense categories and blank input fields.
resetForm();