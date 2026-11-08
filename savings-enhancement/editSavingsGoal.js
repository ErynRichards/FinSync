
// --------------------------------------------------
// FinSync - Edit Savings Goal
// Handles editing, validation and monthly savings
// recommendations.
// --------------------------------------------------

// Sample goal information for standalone testing.
// This will eventually be replaced by information
// retrieved from the FinSync savings database.
const sampleGoal = {
    goal_id: 1,
    name: "Save for a Laptop",
    currentAmount: 3000.00,
    targetAmount: 12000.00,
    targetDate: "2027-05-08"
};

// Store the last successfully confirmed goal.
// Cancel will restore this version.
let savedGoal = { ...sampleGoal };

// Identify the form and its input fields.
const editForm = document.getElementById("editSavingsForm");
const goalNameInput = document.getElementById("goalName");
const currentAmountInput = document.getElementById("currentAmount");
const targetAmountInput = document.getElementById("targetAmount");
const targetDateInput = document.getElementById("targetDate");

// Identify recommendation and feedback elements.
const recommendationMessage = document.getElementById("recommendationMessage");
const monthlyRecommendation = document.getElementById("monthlyRecommendation");
const remainingAmount = document.getElementById("remainingAmount");
const formMessage = document.getElementById("formMessage");

// Format an amount as South African Rand.
function formatCurrency(amount) {
    return new Intl.NumberFormat("en-ZA", {
        style: "currency",
        currency: "ZAR",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

// Load a goal into the form.
function loadGoal(goal) {
    goalNameInput.value = goal.name;
    currentAmountInput.value = Number(goal.currentAmount).toFixed(2);
    targetAmountInput.value = Number(goal.targetAmount).toFixed(2);
    targetDateInput.value = goal.targetDate;

    calculateRecommendation();
}

// Calculate the number of calendar months remaining.
function calculateMonthsRemaining(today, deadline) {
    const months =
        (deadline.getFullYear() - today.getFullYear()) * 12 +
        deadline.getMonth() - today.getMonth();

    return Math.max(1, months);
}

// Calculate and display the monthly savings recommendation.
function calculateRecommendation() {
    const target = Number(targetAmountInput.value);
    const current = Number(currentAmountInput.value);
    const dateValue = targetDateInput.value;

    // Check that the entered values are valid.
    if (
        targetAmountInput.value.trim() === "" ||
        !Number.isFinite(target) ||
        !Number.isFinite(current) ||
        target <= 0 ||
        current < 0 ||
        !dateValue
    ) {
        recommendationMessage.textContent =
            "Enter a valid target amount and target date to see your recommendation.";

        monthlyRecommendation.textContent = "—";
        remainingAmount.textContent = "Remaining amount: —";
        return;
    }

    // Calculate the amount still needed.
    const remaining = Math.max(0, target - current);

    remainingAmount.textContent =
        "Remaining amount: " + formatCurrency(remaining);

    // Check whether the goal has already been reached.
    if (remaining === 0) {
        recommendationMessage.textContent =
            "Congratulations! You have already reached your savings goal.";

        monthlyRecommendation.textContent = formatCurrency(0);
        return;
    }

    // Use local dates to avoid timezone conversion issues.
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const deadline = new Date(dateValue + "T00:00:00");

    // Do not calculate recommendations for overdue goals.
    if (Number.isNaN(deadline.getTime()) || deadline < today) {
        recommendationMessage.textContent =
            "Your target date has passed. Please select today or a future date.";

        monthlyRecommendation.textContent = "Unavailable";
        return;
    }

    // Calculate the remaining calendar months.
    const months = calculateMonthsRemaining(today, deadline);

    // Round upwards to ensure the target can be reached.
    const monthlyAmount =
        Math.ceil((remaining / months) * 100) / 100;

    recommendationMessage.textContent =
        "Based on your remaining target and deadline, aim to save this amount each month:";

    monthlyRecommendation.textContent =
        formatCurrency(monthlyAmount);

    remainingAmount.textContent =
        "Remaining amount: " + formatCurrency(remaining) +
        " | Months remaining: " + months;
}

// Clear previous validation messages.
function clearErrors() {
    document.getElementById("goalNameError").textContent = "";
    document.getElementById("targetAmountError").textContent = "";
    document.getElementById("targetDateError").textContent = "";

    formMessage.textContent = "";
    formMessage.className = "";
}

// Validate the form before accepting changes.
function validateForm() {
    clearErrors();

    let isValid = true;

    const goalName = goalNameInput.value.trim();
    const target = Number(targetAmountInput.value);
    const current = Number(currentAmountInput.value);
    const dateValue = targetDateInput.value;

    // Validate the goal name.
    if (!goalName) {
        document.getElementById("goalNameError").textContent =
            "Please enter a goal name.";

        isValid = false;
    }

    // Validate the target amount.
    if (
        targetAmountInput.value.trim() === "" ||
        !Number.isFinite(target) ||
        target <= 0
    ) {
        document.getElementById("targetAmountError").textContent =
            "Target amount must be greater than zero.";

        isValid = false;
    } else if (target < current) {
        document.getElementById("targetAmountError").textContent =
            "Target amount cannot be less than the amount already saved.";

        isValid = false;
    }

    // Validate the target date.
    if (!dateValue) {
        document.getElementById("targetDateError").textContent =
            "Please select a target date.";

        isValid = false;
    } else {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const deadline = new Date(dateValue + "T00:00:00");

        if (Number.isNaN(deadline.getTime()) || deadline < today) {
            document.getElementById("targetDateError").textContent =
                "Please select today or a future date.";

            isValid = false;
        }
    }

    return isValid;
}

// Handle the Save Changes button.
editForm.addEventListener("submit", function (event) {
    event.preventDefault();

    // Do not continue if the form contains invalid information.
    if (!validateForm()) {
        formMessage.textContent =
            "Please correct the highlighted fields.";

        formMessage.className = "error";
        return;
    }

    // Ask the user to confirm before accepting the changes.
    const confirmed = window.confirm(
        "Are you sure you want to save these changes?"
    );

    if (!confirmed) {
        formMessage.textContent = "Changes were not saved.";
        formMessage.className = "";
        return;
    }

    // Prepare the updated savings goal.
    const updatedGoal = {
        goal_id: savedGoal.goal_id,
        name: goalNameInput.value.trim(),
        currentAmount: savedGoal.currentAmount,
        targetAmount: Number(targetAmountInput.value),
        targetDate: targetDateInput.value
    };

    // Update the last confirmed version.
    savedGoal = { ...updatedGoal };

    formMessage.textContent =
        "Goal changes confirmed successfully. Database saving is not connected yet.";

    formMessage.className = "success";

    console.log("Updated savings goal:", updatedGoal);

    // Refresh the recommendation.
    calculateRecommendation();
});

// Recalculate when the target amount changes.
targetAmountInput.addEventListener("input", calculateRecommendation);

// Recalculate when the target date changes.
targetDateInput.addEventListener("change", calculateRecommendation);

// Cancel editing and restore the last confirmed goal.
document.getElementById("cancelButton").addEventListener("click", function () {
    loadGoal(savedGoal);

    clearErrors();

    formMessage.textContent =
        "Changes cancelled. Your last confirmed goal has been restored.";

    formMessage.className = "";
});

// Back button demonstration.
document.getElementById("backButton").addEventListener("click", function (event) {
    event.preventDefault();

    alert("The Savings Goals page will be connected during frontend integration.");
});

// Load the sample goal when the page opens.
loadGoal(sampleGoal);
