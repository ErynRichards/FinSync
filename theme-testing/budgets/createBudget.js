
/*NOTE: Temporary sample data is used for testing.
    Real recommendations will come from Flask.
*/



// 1. GET HTML ELEMENTS


const budgetForm = document.getElementById("budgetForm");

const categorySelect = document.getElementById("category");

const monthlyAmount = document.getElementById("monthlyAmount");

const startDate = document.getElementById("startDate");

const endDate = document.getElementById("endDate");

const suggestionMessage = document.getElementById("suggestionMessage");

const suggestionResult = document.getElementById("suggestionResult");

const suggestedAmount = document.getElementById("suggestedAmount");

const useAmountBtn = document.getElementById("useAmountBtn");

const formMessage = document.getElementById("formMessage");


// 2. TEMPORARY TEST DATA


// These are sample amounts for frontend testing.
// They are NOT calculated from real transactions.

const testRecommendations = {
    housing: 5000,
    groceries: 2000,
    transport: 1500,
    entertainment: 1000,
    shopping: 1500,
    utilities: 1800
};

// Store the currently displayed recommendation.
let currentRecommendation = null;

// Prevent outdated requests from displaying
// the wrong recommendation.
let recommendationRequestId = 0;



// 3. FORMAT RAND AMOUNTS


function formatRand(amount) {

    return new Intl.NumberFormat("en-ZA", {
        style: "currency",
        currency: "ZAR"
    }).format(amount);

}


// 4. DISPLAY SUGGESTED BUDGET


async function updateSuggestedBudget() {

    const selectedCategory = categorySelect.value;

    // Identify the latest recommendation request.
    const requestId = ++recommendationRequestId;

    // Clear the previous suggestion.
    currentRecommendation = null;
    suggestionResult.hidden = true;

    // No category selected.
    if (!selectedCategory) {

        suggestionMessage.textContent =
            "Select a category to view your suggested budget.";

        return;
    }

    // Display loading message.
    suggestionMessage.textContent =
        "Calculating suggested budget...";

    try {

        // Simulate a backend response.
        // Mishayle will replace this with a Flask request.
        await new Promise(resolve =>
            setTimeout(resolve, 700)
        );

        // Ignore outdated requests.
        if (requestId !== recommendationRequestId) {
            return;
        }

        // Retrieve temporary test recommendation.
        const recommendation =
            testRecommendations[selectedCategory];

        // Handle missing spending history.
        if (recommendation === undefined) {

            suggestionMessage.textContent =
                "Insufficient spending history to suggest a budget.";

            return;
        }

        // Store the recommendation.
        currentRecommendation = recommendation;

        // Display the suggested amount.
        suggestedAmount.textContent =
            formatRand(recommendation);

        suggestionMessage.textContent =
            "Based on your previous three months of spending.";

        suggestionResult.hidden = false;

    } catch (error) {

        // Ignore outdated errors.
        if (requestId !== recommendationRequestId) {
            return;
        }

        suggestionMessage.textContent =
            "Unable to retrieve a suggested budget.";

        suggestionResult.hidden = true;

        console.error("Recommendation error:", error);
    }
}


// 5. CATEGORY CHANGE EVENT


// Update the suggestion when the category changes.
// Do not overwrite the amount entered by the user.

categorySelect.addEventListener("change", function () {

    // Clear previous form feedback.
    formMessage.textContent = "";

    // Request a new recommendation.
    updateSuggestedBudget();

});



// 6. USE SUGGESTED AMOUNT BUTTON


useAmountBtn.addEventListener("click", function () {

    // Only use a valid recommendation.
    if (currentRecommendation === null) {
        return;
    }

    // Populate the monthly amount input.
    monthlyAmount.value = currentRecommendation;

    // Allow the user to edit the amount.
    monthlyAmount.focus();

    // Display confirmation.
    formMessage.textContent =
        "Suggested amount applied. You can still change it.";

    formMessage.style.color = "#1558e8";

});


// 7. VALIDATE START AND END DATES


startDate.addEventListener("change", function () {

    // Prevent selecting an earlier end date.
    endDate.min = startDate.value;

    // Clear the end date if it is now invalid.
    if (endDate.value &&
        endDate.value < startDate.value) {

        endDate.value = "";
    }

    // Clear previous feedback.
    formMessage.textContent = "";

});



// 8. HANDLE SAVE BUDGET


budgetForm.addEventListener("submit", function (event) {

    // Prevent submission until Flask is connected.
    event.preventDefault();

    const selectedCategory = categorySelect.value;

    const amount = Number(monthlyAmount.value);

    const start = startDate.value;

    const end = endDate.value;

    // Validate category.
    if (!selectedCategory) {

        showFormError("Please select a category.");
        return;
    }

    // Validate monthly amount.
    if (
        monthlyAmount.value.trim() === "" ||
        !Number.isFinite(amount) ||
        amount <= 0
    ) {

        showFormError(
            "Please enter a valid monthly amount."
        );

        return;
    }

    // Validate dates.
    if (!start || !end) {

        showFormError(
            "Please select both dates."
        );

        return;
    }

    // Ensure end date is not before start date.
    if (end < start) {

        showFormError(
            "End date cannot be earlier than start date."
        );

        return;
    }

    // Prepare data for future Flask integration.
    const budgetData = {
        category: selectedCategory,
        monthly_amount: amount,
        start_date: start,
        end_date: end
    };

    // Display test data in browser console.
    console.log("Budget test data:", budgetData);

    // Test-mode confirmation.
    // No budget is saved to the database yet.
    formMessage.textContent =
        "Form validated successfully! Test mode: budget not saved.";

    formMessage.style.color = "#1558e8";

});

// 9. DISPLAY FORM ERRORS


function showFormError(message) {

    formMessage.textContent = message;

    formMessage.style.color = "#d62828";

}



// 10. CLEAR OLD FORM FEEDBACK


// Clear messages when the amount changes.
monthlyAmount.addEventListener("input", function () {

    formMessage.textContent = "";

});

// Clear messages when the end date changes.
endDate.addEventListener("change", function () {

    formMessage.textContent = "";

});



// 11. INITIALISE THE FORM


// Handles cases where the browser remembers
// a previously selected category.

updateSuggestedBudget();
