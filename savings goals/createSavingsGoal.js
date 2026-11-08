
// Get the savings form and its buttons
const savingsForm = document.getElementById("savingsGoalForm");
const cancelBtn = document.getElementById("cancelBtn");
const saveBtn = document.getElementById("saveBtn");
const formMessage = document.getElementById("formMessage");

// This must match Michalyn's Savings Goals page filename.
const savingsDashboardUrl = "savings-goals.html";

// Display an error underneath a field
function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const error = document.getElementById(fieldId + "Error");

    field.classList.add("input-error");
    field.setAttribute("aria-invalid", "true");
    error.textContent = message;
}

// Clear the error for a field
function clearError(fieldId) {
    const field = document.getElementById(fieldId);
    const error = document.getElementById(fieldId + "Error");

    field.classList.remove("input-error");
    field.removeAttribute("aria-invalid");
    error.textContent = "";
}

// Display a general message
function showFormMessage(message, type) {
    formMessage.textContent = message;
    formMessage.className = "form-message " + type;
}

// Get today's local date in YYYY-MM-DD format
function getToday() {
    const today = new Date();

    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
}

// Validate all required fields
function validateSavingsForm() {
    let isValid = true;

    const goalName = document.getElementById("goalName").value.trim();
    const amountValue = document.getElementById("targetAmount").value;
    const targetDate = document.getElementById("targetDate").value;

    // Clear previous errors
    ["goalName", "targetAmount", "targetDate"].forEach(clearError);
    showFormMessage("", "");

    // Validate goal name
    if (goalName === "") {
        showError("goalName", "Please enter a goal name.");
        isValid = false;
    }

    // Validate target amount
    if (amountValue.trim() === "" ||
        !Number.isFinite(Number(amountValue)) ||
        Number(amountValue) <= 0) {

        showError(
            "targetAmount",
            "Please enter an amount greater than R 0."
        );

        isValid = false;
    }

    // Validate target date
    if (!targetDate) {
        showError("targetDate", "Please select a target date.");
        isValid = false;
    } else if (targetDate <= getToday()) {
        showError(
            "targetDate",
            "Please select a future date."
        );

        isValid = false;
    }

    return isValid;
}

// Remove validation errors as users correct fields
["goalName", "targetAmount", "targetDate"].forEach(fieldId => {
    document.getElementById(fieldId).addEventListener("input", () => {
        clearError(fieldId);
    });
});

// Handle Save button
savingsForm.addEventListener("submit", function(event) {
    event.preventDefault();

    // Stop if the form contains invalid information
    if (!validateSavingsForm()) {
        showFormMessage("Please correct the highlighted fields.", "error");
        return;
    }

    // Collect the validated form information
    const goalData = {
        goal_name: document.getElementById("goalName").value.trim(),
        target_amount: Number(document.getElementById("targetAmount").value),
        target_date: document.getElementById("targetDate").value,
        category: document.getElementById("category").value || null
    };

    // Integration will be added once the Flask endpoint
    // and expected JSON structure are confirmed.
    // Mishayle will coordinate integration with the backend.
    console.log("Validated savings goal:", goalData);

    showFormMessage(
        "Form validated. Backend saving is not connected yet.",
        "success"
    );
});

// Handle Cancel button
cancelBtn.addEventListener("click", function() {
    window.location.href = savingsDashboardUrl;
});
