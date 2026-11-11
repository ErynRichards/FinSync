
// Get the savings form and its buttons.
const savingsForm = document.getElementById("savingsGoalForm");
const cancelBtn = document.getElementById("cancelBtn");
const saveBtn = document.getElementById("saveBtn");
const formMessage = document.getElementById("formMessage");

// Savings Goals page.
const savingsDashboardUrl = "savings-goals.html";

// Flask configuration.
// Must match savings-goals.js.
const API_BASE = "";

// Demo storage.
const STORAGE_KEY = "finsync_demo_savings_goals_v1";

// Display validation errors.
function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const error = document.getElementById(fieldId + "Error");

    field.classList.add("input-error");
    field.setAttribute("aria-invalid", "true");

    error.textContent = message;
}

// Clear field errors.
function clearError(fieldId) {
    const field = document.getElementById(fieldId);
    const error = document.getElementById(fieldId + "Error");

    field.classList.remove("input-error");
    field.removeAttribute("aria-invalid");

    error.textContent = "";
}

// Display form feedback.
function showFormMessage(message, type) {
    formMessage.textContent = message;
    formMessage.className = "form-message " + type;
}

// Get today's date.
function getToday() {
    const today = new Date();

    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
}

// Validate the savings form.
function validateSavingsForm() {
    let isValid = true;

    const goalName = document.getElementById(
        "goalName"
    ).value.trim();

    const amountValue = document.getElementById(
        "targetAmount"
    ).value;

    const targetDate = document.getElementById(
        "targetDate"
    ).value;

    // Clear previous errors.
    ["goalName", "targetAmount", "targetDate"]
        .forEach(clearError);

    showFormMessage("", "");

    // Validate goal name.
    if (goalName === "") {
        showError(
            "goalName",
            "Please enter a goal name."
        );

        isValid = false;
    }

    // Validate target amount.
    if (
        amountValue.trim() === "" ||
        !Number.isFinite(Number(amountValue)) ||
        Number(amountValue) <= 0
    ) {
        showError(
            "targetAmount",
            "Please enter an amount greater than R 0."
        );

        isValid = false;
    }

    // Validate target date.
    if (!targetDate) {
        showError(
            "targetDate",
            "Please select a target date."
        );

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

// Clear errors as the user edits the form.
["goalName", "targetAmount", "targetDate"]
    .forEach(fieldId => {

        document.getElementById(fieldId)
            .addEventListener("input", () => {
                clearError(fieldId);
            });
    });

// Handle Save button.
savingsForm.addEventListener("submit", function(event) {
    event.preventDefault();

    if (!validateSavingsForm()) {
        showFormMessage(
            "Please correct the highlighted fields.",
            "error"
        );

        return;
    }

    // Collect form data.
    const goalData = {
        goal_name: document.getElementById(
            "goalName"
        ).value.trim(),

        target_amount: Number(
            document.getElementById("targetAmount").value
        ),

        target_date: document.getElementById(
            "targetDate"
        ).value,

        category: document.getElementById(
            "category"
        ).value || null
    };

    saveBtn.disabled = true;

    showFormMessage("Saving goal…", "");

    // Save goal.
    (async () => {
        try {
            if (API_BASE) {
                // Flask backend mode.
                const response = await fetch(
                    `${API_BASE}/savings-goals`,
                    {
                        method: "POST",
                        credentials: "same-origin",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(goalData)
                    }
                );

                if (!response.ok) {
                    const details = await response.json()
                        .catch(() => ({}));

                    throw new Error(
                        details.error ||
                        "Unable to save savings goal."
                    );
                }

            } else {
                // Demo mode: save in browser storage.
                const existing = JSON.parse(
                    localStorage.getItem(STORAGE_KEY) || "[]"
                );

                existing.push({
                    id:
                        `demo-${Date.now()}-` +
                        Math.random().toString(36).slice(2),

                    name: goalData.goal_name,

                    description: goalData.category || "",

                    targetAmount: goalData.target_amount,

                    savedAmount: 0,

                    targetDate: goalData.target_date
                });

                localStorage.setItem(
                    STORAGE_KEY,
                    JSON.stringify(existing)
                );
            }

            // Return to Savings Goals.
            window.location.href = savingsDashboardUrl;

        } catch (error) {
            showFormMessage(error.message, "error");

        } finally {
            saveBtn.disabled = false;
        }
    })();
});

// Handle Cancel button.
cancelBtn.addEventListener("click", function() {
    window.location.href = savingsDashboardUrl;
});
