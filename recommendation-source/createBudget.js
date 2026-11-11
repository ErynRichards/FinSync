/*
 * FinSync - Budget Recommendation Interface
 *
 * This version uses demonstration data so the interface can be
 * tested independently of the group's Flask backend.
 *
 * Recommendations are never saved automatically.
 */

// Set to false only when the backend endpoint and category IDs
// have been confirmed and configured.
const USE_DEMO_DATA = true;

// Demo recommendations are examples, not calculations from real
// transaction history.
const sampleRecommendations = {
    housing: 5000,
    groceries: 2000,
    transport: 1500,
    entertainment: 1000,
    shopping: 1500,
    utilities: 1800
};

// Get the page elements.
const budgetForm = document.getElementById("budgetForm");
const categorySelect = document.getElementById("category");
const budgetMonth = document.getElementById("budgetMonth");
const monthlyAmount = document.getElementById("monthlyAmount");

const suggestionMessage = document.getElementById("suggestionMessage");
const suggestionResult = document.getElementById("suggestionResult");
const suggestedAmount = document.getElementById("suggestedAmount");
const useAmountBtn = document.getElementById("useAmountBtn");

const alertMessage = document.getElementById("alertMessage");
const formMessage = document.getElementById("formMessage");
const budgetList = document.getElementById("budgetList");
const emptyBudgetMessage = document.getElementById("emptyBudgetMessage");
const cancelBtn = document.getElementById("cancelBtn");

// Store the current recommendation separately from the amount
// entered by the user.
let currentRecommendation = null;

// Every new request receives a unique number. Older responses
// are ignored if the user changes the category or month.
let latestRequestId = 0;

// Demonstration budgets are stored only while this page is open.
let budgets = [];
let editingBudgetId = null;

// Format amounts consistently in South African Rand.
function formatCurrency(amount) {
    return new Intl.NumberFormat("en-ZA", {
        style: "currency",
        currency: "ZAR"
    }).format(amount);
}

// Display a page-level alert.
function showAlert(message, type = "success") {
    alertMessage.textContent = message;
    alertMessage.className = "alert";

    if (type === "error" || type === "warning") {
        alertMessage.classList.add(type);
    }

    alertMessage.hidden = false;
}

// Clear the page-level alert.
function clearAlert() {
    alertMessage.textContent = "";
    alertMessage.hidden = true;
}

// Set the current month as the initial budget month.
function initialiseMonth() {
    const now = new Date();
    const month = String(now.getMonth() + 1).padStart(2, "0");

    budgetMonth.value = `${now.getFullYear()}-${month}`;
}

// Return a demonstration recommendation.
async function fetchDemoRecommendation(category) {
    // A short delay makes the loading state visible during testing.
    await new Promise(resolve => setTimeout(resolve, 600));

    // These categories demonstrate the insufficient-history case.
    if (category === "shopping") {
        return {
            suggested_amount: null,
            message: "Insufficient transaction history. You can enter an amount manually."
        };
    }

    return {
        suggested_amount: sampleRecommendations[category] ?? null,
        message: "Demonstration recommendation only. It is not based on your actual transactions."
    };
}

// Retrieve the recommendation.
// Backend integration can be added here once the real category IDs
// and API response have been confirmed.
async function fetchCategoryRecommendation(category, period) {
    if (USE_DEMO_DATA) {
        return await fetchDemoRecommendation(category);
    }

    throw new Error(
        "Backend integration is not configured. Please use manual budget entry."
    );
}

// Clear the displayed recommendation.
function clearRecommendation(message) {
    currentRecommendation = null;
    suggestionResult.hidden = true;
    suggestionMessage.textContent = message;
}

// Request and display a recommendation.
async function updateSuggestedBudget() {
    const category = categorySelect.value;
    const period = budgetMonth.value;

    // Increase the request ID so any earlier request becomes outdated.
    const requestId = ++latestRequestId;

    clearRecommendation(
        "Select a category and month to view a suggested budget."
    );

    if (!category) {
        return;
    }

    if (!period) {
        suggestionMessage.textContent =
            "Please select a budget month.";
        return;
    }

    clearAlert();

    suggestionMessage.textContent =
        "Calculating suggested budget...";

    try {
        const data = await fetchCategoryRecommendation(category, period);

        // Ignore responses from older category/month selections.
        if (requestId !== latestRequestId) {
            return;
        }

        const rawAmount = data.suggested_amount;

        // A null amount means that a recommendation is unavailable.
        if (rawAmount === null || rawAmount === undefined) {
            suggestionMessage.textContent =
                data.message ||
                "Insufficient transaction history. You can enter an amount manually.";
            return;
        }

        const amount = Number(rawAmount);

        // Reject invalid or negative recommendation amounts.
        if (
            rawAmount === "" ||
            !Number.isFinite(amount) ||
            amount <= 0
        ) {
            throw new Error("The recommendation amount is invalid.");
        }

        currentRecommendation = Math.round(amount * 100) / 100;

        suggestedAmount.textContent =
            formatCurrency(currentRecommendation);

        suggestionMessage.textContent =
            data.message ||
            "A suggested amount is available for this category.";

        suggestionResult.hidden = false;

    } catch (error) {
        // Do not let an older failed request overwrite a newer result.
        if (requestId !== latestRequestId) {
            return;
        }

        clearRecommendation(
            "Unable to retrieve a recommendation. You can enter a budget manually."
        );

        showAlert(error.message, "error");
    }
}

// Refresh the recommendation when the category or month changes.
categorySelect.addEventListener("change", updateSuggestedBudget);
budgetMonth.addEventListener("change", updateSuggestedBudget);

// Apply the recommendation to the amount field.
// This does NOT save the budget.
useAmountBtn.addEventListener("click", function () {
    if (currentRecommendation === null) {
        return;
    }

    monthlyAmount.value = currentRecommendation.toFixed(2);

    formMessage.textContent =
        "Suggested amount added. Select Save Budget when you are ready.";

    showAlert(
        "The suggested amount has been entered. It has not been saved.",
        "success"
    );
});

// Display all demonstration budgets.
function renderBudgets() {
    budgetList.innerHTML = "";

    if (budgets.length === 0) {
        const message = document.createElement("p");
        message.id = "emptyBudgetMessage";
        message.textContent = "No budgets have been added yet.";
        budgetList.appendChild(message);
        return;
    }

    budgets.forEach(function (budget) {
        const item = document.createElement("article");
        item.className = "budget-item";

        const details = document.createElement("div");

        const heading = document.createElement("h3");
        heading.textContent = budget.category;

        const description = document.createElement("p");
        description.textContent =
            `${budget.period} | ${formatCurrency(budget.amount)}`;

        details.appendChild(heading);
        details.appendChild(description);

        const actions = document.createElement("div");
        actions.className = "budget-item-actions";

        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.className = "secondary-button";
        editButton.textContent = "Edit";

        editButton.addEventListener("click", function () {
            editBudget(budget.id);
        });

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "delete-button";
        deleteButton.textContent = "Delete";

        deleteButton.addEventListener("click", function () {
            deleteBudget(budget.id);
        });

        actions.appendChild(editButton);
        actions.appendChild(deleteButton);

        item.appendChild(details);
        item.appendChild(actions);

        budgetList.appendChild(item);
    });
}

// Save a new budget or update an existing demonstration budget.
budgetForm.addEventListener("submit", function (event) {
    event.preventDefault();
    clearAlert();

    const category = categorySelect.value;
    const period = budgetMonth.value;
    const amount = Number(monthlyAmount.value);

    if (!category || !period || !Number.isFinite(amount) || amount <= 0) {
        showAlert("Please select a category, month and valid budget amount.", "error");
        return;
    }

    if (editingBudgetId !== null) {
        const existingBudget = budgets.find(
            budget => budget.id === editingBudgetId
        );

        if (existingBudget) {
            existingBudget.category = category;
            existingBudget.period = period;
            existingBudget.amount = amount;
        }

        editingBudgetId = null;
        showAlert("Demonstration budget updated successfully.");
    } else {
        budgets.push({
            id: Date.now(),
            category: category,
            period: period,
            amount: amount
        });

        showAlert("Demonstration budget added successfully.");
    }

    renderBudgets();
    resetForm();
});

// Load a budget into the form for editing.
function editBudget(id) {
    const budget = budgets.find(item => item.id === id);

    if (!budget) {
        return;
    }

    editingBudgetId = id;

    categorySelect.value = budget.category;
    budgetMonth.value = budget.period;
    monthlyAmount.value = budget.amount.toFixed(2);

    formMessage.textContent =
        "Editing budget. Save Budget to apply your changes.";

    updateSuggestedBudget();

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

// Delete a budget after user confirmation.
function deleteBudget(id) {
    const confirmed = window.confirm(
        "Are you sure you want to delete this budget?"
    );

    if (!confirmed) {
        return;
    }

    budgets = budgets.filter(budget => budget.id !== id);

    if (editingBudgetId === id) {
        editingBudgetId = null;
        resetForm();
    }

    renderBudgets();
    showAlert("Demonstration budget deleted.");
}

// Reset the form without saving anything.
function resetForm() {
    // Invalidate any pending recommendation request.
    latestRequestId++;

    budgetForm.reset();
    initialiseMonth();

    editingBudgetId = null;
    currentRecommendation = null;

    suggestionResult.hidden = true;
    suggestionMessage.textContent =
        "Select a category to view a suggested budget.";

    formMessage.textContent = "";
}

// Cancel button clears the current form.
cancelBtn.addEventListener("click", function () {
    resetForm();
    clearAlert();
});

// Initial page setup.
initialiseMonth();
renderBudgets();