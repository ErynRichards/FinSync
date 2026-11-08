/*
    This function keeps the component's variables separate from
    variables used by other group members' scripts.
*/
(function () {
    "use strict";

    // Find the HTML controls used by this component.
    const form = document.getElementById("budgetForm");
    const category = document.getElementById("category");
    const suggestion = document.getElementById("suggestion");
    const formMessage = document.getElementById("formMessage");
    const startDate = document.getElementById("startDate");
    const endDate = document.getElementById("endDate");

    /*
        If the component is not displayed on the current page,
        stop instead of trying to use missing elements.

        When integrating with dynamically loaded pages, run this
        setup after the Create Budget form has been inserted.
    */
    if (
        !form ||
        !category ||
        !suggestion ||
        !formMessage ||
        !startDate ||
        !endDate
    ) {
        return;
    }

    /*
        true:
        Use sample recommendations for independent frontend testing.

        false:
        Request recommendations from Flask.

        Before changing this to false, confirm the endpoint,
        real category IDs and JSON response with the backend code.
    */
    const demoMode = false;

    /*
        Leave this empty until the actual Flask route is confirmed.
        The request below assumes a GET endpoint accepting category_id.
        Adjust that request if the real API uses a different format.
    */
    const endpoint = "/api/budgets/recommendation";

    // Sample amounts associated with the preview's sample category IDs.
    const demoAmounts = {
        "demo-groceries": 1200,
        "demo-transport": 800,
        "demo-entertainment": 450
    };

    /*
        Every category change increases this counter.
        A response can update the screen only if its request number
        still matches the latest counter value.
    */
    let latestRequest = 0;

    // Format a valid numeric amount as South African rand.
    function formatRand(amount) {
        return new Intl.NumberFormat("en-ZA", {
            style: "currency",
            currency: "ZAR",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }

    /*
        Retrieve a recommendation.

        Expected example response:
        {
            "category_id": "the-selected-category-id",
            "recommended_amount": "1200.00"
        }

        These response field names must match the real Flask API.
    */
    async function getRecommendation(categoryId) {
        if (demoMode) {
            /*
                Groceries loads more slowly than the other categories.
                This lets us test whether an old response is correctly
                ignored after the user selects another category.
            */
            const delay =
                categoryId === "demo-groceries" ? 1800 : 500;

            await new Promise(function (resolve) {
                setTimeout(resolve, delay);
            });

            return {
                category_id: categoryId,
                recommended_amount: demoAmounts[categoryId]
            };
        }

        // Stop with an error if real mode has no configured endpoint.
        if (!endpoint) {
            throw new Error("Flask endpoint is not configured.");
        }

        /*
            URLSearchParams safely adds the selected category ID.
            Send the option's value, not its visible category name.
        */
        const url = new URL(endpoint, window.location.href);
        url.searchParams.set("category_id", categoryId);

        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            },
            credentials: "same-origin"
        });

        // fetch does not automatically throw for HTTP error responses.
        if (!response.ok) {
            throw new Error("Recommendation request failed.");
        }

        // Convert the JSON response into a JavaScript object.
        return response.json();
    }

    // Request and display the current category's recommendation.
    async function updateSuggestion() {
        latestRequest++;

        // Remember which request this function call belongs to.
        const requestId = latestRequest;
        const categoryId = category.value;

        /*
            Immediately remove the old recommendation.
            It must not remain visible underneath the newly selected
            category while that category's request is loading.
        */
        suggestion.textContent = "";
        suggestion.classList.remove("error");
        formMessage.textContent = "";

        // Do not make a request when the blank option is selected.
        if (!categoryId) {
            suggestion.textContent =
                "Select a category to see a suggestion.";
            return;
        }

        // The name is used for display; the ID is used for the request.
        const categoryName =
            category.options[category.selectedIndex].text.trim();

        suggestion.textContent =
            "Loading suggestion for " + categoryName + "...";

        try {
            const data = await getRecommendation(categoryId);

            /*
                Ignore an old response if:
                1. A newer request has started, or
                2. The selected category has changed.

                This also handles switching A -> B -> A quickly:
                only the newest request number can update the screen.
            */
            if (
                requestId !== latestRequest ||
                category.value !== categoryId
            ) {
                return;
            }

            // Check that the response belongs to the requested category.
            if (!data || String(data.category_id) !== categoryId) {
                throw new Error("Category does not match.");
            }

            const value = data.suggested_amount;

            /*
                Missing recommendations are different from a valid zero.
                Do not convert null or an empty string into a misleading R0.
            */
            if (
                value === null ||
                value === undefined ||
                (
                    typeof value === "string" &&
                    value.trim() === ""
                )
            ) {
                suggestion.textContent =
                    "No suggestion available for " + categoryName + ".";
                return;
            }

            // Accept a number or numeric string; reject invalid values.
            if (
                (
                    typeof value !== "number" &&
                    typeof value !== "string"
                ) ||
                !Number.isFinite(Number(value)) ||
                Number(value) < 0
            ) {
                throw new Error("Invalid recommendation amount.");
            }

            suggestion.textContent =
                "Suggested for " + categoryName + ": " +
                formatRand(Number(value));

            /*
                The amount input is deliberately not assigned a value.
                A suggestion must not overwrite the user's chosen budget.
            */
        } catch (error) {
            /*
                An old failed request must not replace a newer
                recommendation or loading message.
            */
            if (
                requestId !== latestRequest ||
                category.value !== categoryId
            ) {
                return;
            }

            suggestion.classList.add("error");
            suggestion.textContent =
                "Could not load the suggestion. " +
                "Change category to retry.";
        }
    }

    // Run the update whenever the user changes the category.
    category.addEventListener("change", updateSuggestion);

    /*
        Clear the recommendation and invalidate outstanding requests.
        Pending requests may finish, but their results will be ignored.
    */
    function clearRecommendation() {
        latestRequest++;

        suggestion.classList.remove("error");
        suggestion.textContent =
            "Select a category to see a suggestion.";

        formMessage.textContent = "";
    }

    // Cancel resets the form, including the user's entered amount.
    // This differs from changing categories, which preserves the amount.
    form.addEventListener("reset", clearRecommendation);

    /*
        This preview validates the dates but does not save a budget.
        Real budget saving will be handled during form integration.
    */
    form.addEventListener("submit", function (event) {
        event.preventDefault();

        // YYYY-MM-DD date strings can be compared in chronological order.
        if (endDate.value < startDate.value) {
            formMessage.textContent =
                "End date must be on or after the start date.";
            return;
        }

        formMessage.textContent =
            "Preview validated. No budget has been saved.";
    });

    /*
        Provide two functions for later integration:
        - refresh(): request the selected category's recommendation.
        - clear(): invalidate requests when the form closes or is cleared.
    */
    window.FinSyncBudgetRecommendations = {
        refresh: updateSuggestion,
        clear: clearRecommendation
    };
})();