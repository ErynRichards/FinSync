
/*
==========================================================
FINSYNC - INTERACTIVE REPORTING API INTEGRATION
Developer: Reece
Purpose:
- Retrieve monthly reporting information from Flask.
- Refresh the Monthly Trend and Income vs Expenses charts.
- Handle reporting period changes without refreshing the page.
- Handle loading states, API errors and outdated requests.
==========================================================
*/

(() => {
    "use strict";

    // --------------------------------------------------
    // 1. API CONFIGURATION
    // --------------------------------------------------

    // Flask reporting endpoint running on the local machine.
    const API_URL = "http://127.0.0.1:5000/api/v1/reports/";

    // Reporting periods supported by the FinSync backend.
    const SUPPORTED_PERIODS = [1, 3, 6, 12];


    // --------------------------------------------------
    // 2. FIND THE EXISTING REPORTS PAGE ELEMENTS
    // --------------------------------------------------

    const periodSelect = document.querySelector("#reportPeriod");

    const periodControl = document.querySelector(
        "#report-period-control"
    );

    // Stop safely if this script is loaded on another page.
    if (!periodSelect || !periodControl) {
        console.warn(
            "Reporting API: Reporting period selector not found."
        );
        return;
    }

    // Eryn's reports.js provides this function.
    // It validates the data and refreshes both charts.
    if (typeof window.updateMonthlyReports !== "function") {
        console.error(
            "Reporting API: updateMonthlyReports() is unavailable. " +
            "Load reports.js before reporting-api.js."
        );
        return;
    }


    // --------------------------------------------------
    // 3. CREATE A REPORTING STATUS MESSAGE
    // --------------------------------------------------

    // Create an accessible status message without changing
    // Eryn's existing HTML.
    const statusElement = document.createElement("p");

    statusElement.id = "reporting-api-status";
    statusElement.setAttribute("role", "status");
    statusElement.setAttribute("aria-live", "polite");

    statusElement.style.marginTop = "8px";
    statusElement.style.fontSize = "0.9rem";

    periodControl.appendChild(statusElement);


    // --------------------------------------------------
    // 4. REQUEST MANAGEMENT
    // --------------------------------------------------

    // Store the current request so an older request can
    // be cancelled when the user selects another period.
    let activeController = null;

    // Each request receives a unique number.
    // This prevents outdated responses from updating charts.
    let requestNumber = 0;

    // Track whether live data has ever loaded successfully.
    let hasLoadedApiData = false;


    // --------------------------------------------------
    // 5. HELPER: DISPLAY STATUS MESSAGES
    // --------------------------------------------------

    function displayStatus(message) {
        statusElement.textContent = message;
    }


    // --------------------------------------------------
    // 6. FETCH REPORTING DATA FROM FLASK
    // --------------------------------------------------

    async function loadMonthlyReports() {

        // Read the reporting period selected by the user.
        const period = Number(periodSelect.value);

        // Validate the selected reporting period.
        if (!SUPPORTED_PERIODS.includes(period)) {
            displayStatus(
                "Please select a valid reporting period."
            );
            return;
        }

        // Increase the request number.
        // Responses from older requests will be ignored.
        const currentRequest = ++requestNumber;

        // Cancel the previous request if it is still running.
        if (activeController) {
            activeController.abort();
        }

        // Create a controller for the new request.
        activeController = new AbortController();

        // Show a loading message.
        displayStatus(
            `Loading your ${period}-month report...`
        );

        try {

            // Build the API request URL.
            const requestUrl = new URL(API_URL);

            requestUrl.searchParams.set("period", period);

            // Send the request to Flask.
            const response = await fetch(requestUrl, {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                },
                signal: activeController.signal,
                cache: "no-store"
            });

            // Read the JSON response.
            const data = await response.json();

            // Ignore a response if a newer request was made.
            if (currentRequest !== requestNumber) {
                return;
            }

            // Handle unsuccessful HTTP responses.
            if (!response.ok) {

                const errorMessage =
                    data.error || "Unable to retrieve reporting data.";

                throw new Error(
                    `HTTP ${response.status}: ${errorMessage}`
                );
            }

            // Confirm that the backend returned the requested period.
            if (data.period !== period) {
                throw new Error(
                    "The backend returned an unexpected reporting period."
                );
            }

            // Confirm that monthly reporting records were supplied.
            if (!Array.isArray(data.monthly_reports)) {
                throw new Error(
                    "The backend returned an invalid reporting response."
                );
            }

            // Send the live data to Eryn's existing chart function.
            // This refreshes both financial graphs.
            window.updateMonthlyReports(data.monthly_reports);

            // Record that live reporting data has loaded.
            hasLoadedApiData = true;

            // Display the successfully loaded reporting period.
            displayStatus(
                `Live reporting data loaded successfully for the last ${period} ` +
                (period === 1 ? "month." : "months.")
            );

            console.info(
                "FinSync Reporting: Successfully loaded",
                data.monthly_reports
            );

        } catch (error) {

            // Ignore requests cancelled because the user
            // selected a different reporting period.
            if (error.name === "AbortError") {
                return;
            }

            // Ignore errors from outdated requests.
            if (currentRequest !== requestNumber) {
                return;
            }

            console.error(
                "FinSync Reporting API Error:",
                error
            );

            // Preserve Eryn's demonstration data if live data
            // has not loaded successfully yet.
            if (!hasLoadedApiData) {

                displayStatus(
                    "Live reporting data is unavailable. " +
                    "Demonstration data is still displayed. " +
                    error.message
                );

            } else {

                // Be transparent if the latest request fails
                // after an earlier live request succeeded.
                displayStatus(
                    `Could not load the selected ${period}-month report. ` +
                    "The charts may still show the last successfully loaded data. " +
                    error.message
                );
            }
        }
    }


    // --------------------------------------------------
    // 7. LISTEN FOR REPORTING PERIOD CHANGES
    // --------------------------------------------------

    // Fetch new information whenever the user selects
    // a different reporting period.
    periodSelect.addEventListener(
        "change",
        loadMonthlyReports
    );


    // --------------------------------------------------
    // 8. LOAD INITIAL REPORTING DATA
    // --------------------------------------------------

    // Retrieve the default reporting period when the
    // Reports page first loads.
    loadMonthlyReports();


    // --------------------------------------------------
    // 9. EXPOSE THE FUNCTION FOR FUTURE INTEGRATION
    // --------------------------------------------------

    // Allows another frontend component to request
    // refreshed reporting information when needed.
    window.loadFinSyncMonthlyReports = loadMonthlyReports;

})();
