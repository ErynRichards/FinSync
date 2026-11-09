
/*
 * FinSync - Budget Notification Popup
 *
 * Responsibilities:
 * 1. Listen for budget-exceeded events.
 * 2. Check the user's notification preference.
 * 3. Prevent duplicate popups in the current tab session.
 * 4. Display the notification without refreshing the page.
 * 5. Allow a new notification in a later month.
 *
 * The real expense-saving process must dispatch the event
 * only after the backend confirms that the expense was saved.
 */

document.addEventListener("DOMContentLoaded", function () {

    // --------------------------------------------------
    // 1. Get the HTML elements
    // --------------------------------------------------

    const dialog = document.getElementById(
        "budgetNotificationDialog"
    );

    const notificationMessage = document.getElementById(
        "notificationMessage"
    );

    const dismissButton = document.getElementById(
        "dismissBudgetNotification"
    );

    const preferenceToggle = document.getElementById(
        "budgetWarningsToggle"
    );

    const testStatus = document.getElementById(
        "testStatus"
    );

    const triggerButton = document.getElementById(
        "triggerBudgetExceeded"
    );

    const duplicateButton = document.getElementById(
        "triggerDuplicate"
    );

    const nextMonthButton = document.getElementById(
        "triggerNextMonth"
    );

    const failedSaveButton = document.getElementById(
        "simulateFailedSave"
    );

    // Existing notification preference storage key.
    const PREFERENCE_KEY =
        "finsync_notification_preferences";

    // Stores event IDs already displayed in this tab session.
    const NOTIFIED_EVENTS_KEY =
        "finsync_displayed_budget_notifications";

    // Keep notifications waiting if another popup is open.
    const notificationQueue = [];

    // --------------------------------------------------
    // 2. Read notification preferences
    // --------------------------------------------------

    function getPreferences() {

        const defaultPreferences = {
            budgetWarnings: true,
            savingsGoalNotifications: true
        };

        try {

            const savedPreferences = localStorage.getItem(
                PREFERENCE_KEY
            );

            if (!savedPreferences) {
                return defaultPreferences;
            }

            const parsedPreferences = JSON.parse(
                savedPreferences
            );

            if (
                !parsedPreferences ||
                typeof parsedPreferences !== "object" ||
                Array.isArray(parsedPreferences)
            ) {
                return defaultPreferences;
            }

            return {
                ...defaultPreferences,
                ...parsedPreferences
            };

        } catch (error) {

            console.error(
                "Unable to load notification preferences:",
                error
            );

            return defaultPreferences;
        }
    }

    // --------------------------------------------------
    // 3. Save the budget warning preference
    // --------------------------------------------------

    function savePreference(enabled) {

        try {

            const preferences = getPreferences();

            preferences.budgetWarnings = enabled;

            localStorage.setItem(
                PREFERENCE_KEY,
                JSON.stringify(preferences)
            );

            return true;

        } catch (error) {

            console.error(
                "Unable to save notification preference:",
                error
            );

            return false;
        }
    }

    // --------------------------------------------------
    // 4. Load previously displayed event IDs
    // --------------------------------------------------

    function getNotifiedEvents() {

        try {

            const savedEvents = sessionStorage.getItem(
                NOTIFIED_EVENTS_KEY
            );

            if (!savedEvents) {
                return [];
            }

            const parsedEvents = JSON.parse(savedEvents);

            return Array.isArray(parsedEvents)
                ? parsedEvents
                : [];

        } catch (error) {

            console.error(
                "Unable to retrieve notification history:",
                error
            );

            return [];
        }
    }

    // --------------------------------------------------
    // 5. Record a displayed notification
    // --------------------------------------------------

    function recordNotification(eventId) {

        const notifiedEvents = getNotifiedEvents();

        if (notifiedEvents.includes(eventId)) {
            return;
        }

        notifiedEvents.push(eventId);

        try {

            sessionStorage.setItem(
                NOTIFIED_EVENTS_KEY,
                JSON.stringify(notifiedEvents)
            );

        } catch (error) {

            console.error(
                "Unable to record notification history:",
                error
            );
        }
    }

    // --------------------------------------------------
    // 6. Display the notification
    // --------------------------------------------------

    function displayNotification(notification) {

        if (!dialog || !notificationMessage) {
            return;
        }

        // Use the supplied message or a safe default.
        const message =
            typeof notification.message === "string" &&
            notification.message.trim() !== ""
                ? notification.message
                : "Your monthly budget has been exceeded.";

        // textContent prevents supplied text being interpreted as HTML.
        notificationMessage.textContent = message;

        // Record the event before displaying the popup.
        recordNotification(notification.event_id);

        dialog.showModal();

        testStatus.textContent =
            "Budget warning notification displayed.";
    }

    // --------------------------------------------------
    // 7. Process the notification queue
    // --------------------------------------------------

    function processNotificationQueue() {

        if (dialog.open || notificationQueue.length === 0) {
            return;
        }

        const notification = notificationQueue.shift();

        displayNotification(notification);
    }

    // --------------------------------------------------
    // 8. Handle incoming budget-exceeded events
    // --------------------------------------------------

    function handleBudgetExceeded(event) {

        const notification = event.detail;

        if (!notification || typeof notification !== "object") {
            return;
        }

        // Only process an event approved by the backend checker.
        if (notification.should_notify !== true) {
            testStatus.textContent =
                "No notification required for this event.";

            return;
        }

        // An event ID is required for duplicate protection.
        if (
            typeof notification.event_id !== "string" ||
            notification.event_id.trim() === ""
        ) {
            testStatus.textContent =
                "Notification ignored: event ID is missing.";

            return;
        }

        // Respect the saved notification preference.
        const preferences = getPreferences();

        if (preferences.budgetWarnings !== true) {

            testStatus.textContent =
                "Budget warnings are disabled in Settings.";

            return;
        }

        // Prevent the same event from appearing repeatedly.
        const notifiedEvents = getNotifiedEvents();

        if (notifiedEvents.includes(notification.event_id)) {

            testStatus.textContent =
                "Duplicate notification ignored.";

            return;
        }

        // Queue the notification if another one is open.
        notificationQueue.push(notification);

        processNotificationQueue();
    }

    // --------------------------------------------------
    // 9. Load the saved preference into the checkbox
    // --------------------------------------------------

    const preferences = getPreferences();

    if (preferenceToggle) {

        preferenceToggle.checked =
            preferences.budgetWarnings === true;

        preferenceToggle.addEventListener(
            "change",
            function () {

                const saved = savePreference(
                    preferenceToggle.checked
                );

                if (saved) {

                    testStatus.textContent =
                        preferenceToggle.checked
                            ? "Budget warnings enabled."
                            : "Budget warnings disabled.";

                } else {

                    testStatus.textContent =
                        "Unable to save the preference.";

                    preferenceToggle.checked =
                        getPreferences().budgetWarnings === true;
                }
            }
        );
    }

    // --------------------------------------------------
    // 10. Close the notification
    // --------------------------------------------------

    if (dismissButton) {

        dismissButton.addEventListener(
            "click",
            function () {

                dialog.close();

                processNotificationQueue();
            }
        );
    }

    // --------------------------------------------------
    // 11. Listen for budget-exceeded events
    // --------------------------------------------------

    window.addEventListener(
        "finsync:budget-exceeded",
        handleBudgetExceeded
    );

    // --------------------------------------------------
    // 12. Test event helper
    // --------------------------------------------------

    function simulateBudgetEvent(eventId, month) {

        const simulatedNotification = {

            should_notify: true,

            event_id: eventId,

            budget_id: "25",

            budget_month: month,

            amount_over_budget: "200.00",

            message:
                "You have exceeded your budget by R200.00."
        };

        window.dispatchEvent(
            new CustomEvent(
                "finsync:budget-exceeded",
                {
                    detail: simulatedNotification
                }
            )
        );
    }

    // --------------------------------------------------
    // 13. Simulate a successful expense
    // --------------------------------------------------

    if (triggerButton) {

        triggerButton.addEventListener(
            "click",
            function () {

                simulateBudgetEvent(
                    "budget-exceeded:101:25:2026-11",
                    "2026-11"
                );
            }
        );
    }

    // --------------------------------------------------
    // 14. Simulate a duplicate event
    // --------------------------------------------------

    if (duplicateButton) {

        duplicateButton.addEventListener(
            "click",
            function () {

                simulateBudgetEvent(
                    "budget-exceeded:101:25:2026-11",
                    "2026-11"
                );
            }
        );
    }

    // --------------------------------------------------
    // 15. Simulate a new month's exceeded budget
    // --------------------------------------------------

    if (nextMonthButton) {

        nextMonthButton.addEventListener(
            "click",
            function () {

                simulateBudgetEvent(
                    "budget-exceeded:101:25:2026-12",
                    "2026-12"
                );
            }
        );
    }

    // --------------------------------------------------
    // 16. Simulate a failed expense save
    // --------------------------------------------------

    if (failedSaveButton) {

        failedSaveButton.addEventListener(
            "click",
            function () {

                // A failed save must not dispatch a budget event.
                testStatus.textContent =
                    "Expense save failed. No notification was triggered.";
            }
        );
    }

});
