
/* --------------------------------------------------
   FinSync - Notification Preferences

   Handles:
   1. Loading saved notification preferences.
   2. Enabling and disabling notification types.
   3. Saving preferences.
   4. Cancelling unsaved changes.
   5. Handling browser storage errors.

   TEMPORARY:
   Preferences are stored in browser localStorage.
   This will later be replaced by the FinSync API.
-------------------------------------------------- */

// Use one storage key for the notification preferences.
const STORAGE_KEY = "finsync_notification_preferences";

// Default notification settings.
// Both notification types are enabled for a new user.
const DEFAULT_PREFERENCES = {
    budgetWarnings: true,
    savingsGoalNotifications: true
};

// Get references to the HTML elements.
const budgetWarningsInput =
    document.getElementById("budgetWarnings");

const savingsGoalNotificationsInput =
    document.getElementById("savingsGoalNotifications");

const saveButton =
    document.getElementById("saveButton");

const cancelButton =
    document.getElementById("cancelButton");

const preferenceMessage =
    document.getElementById("preferenceMessage");

const backButton =
    document.getElementById("backButton");

// Keep track of the last successfully saved preferences.
// Cancel will restore these values.
let savedPreferences = { ...DEFAULT_PREFERENCES };


// --------------------------------------------------
// Display a message to the user.
// --------------------------------------------------

function showMessage(message, type = "") {

    preferenceMessage.textContent = message;

    // Clear existing message styling.
    preferenceMessage.className = "message";

    // Apply success or error styling when required.
    if (type) {
        preferenceMessage.classList.add(type);
    }
}


// --------------------------------------------------
// Read the current selections from the controls.
// --------------------------------------------------

function getCurrentPreferences() {

    return {
        budgetWarnings: budgetWarningsInput.checked,

        savingsGoalNotifications:
            savingsGoalNotificationsInput.checked
    };

}


// --------------------------------------------------
// Display preferences in the checkbox controls.
// --------------------------------------------------

function displayPreferences(preferences) {

    budgetWarningsInput.checked =
        preferences.budgetWarnings;

    savingsGoalNotificationsInput.checked =
        preferences.savingsGoalNotifications;

}


// --------------------------------------------------
// Validate the saved preference structure.
// --------------------------------------------------

function isValidPreferences(preferences) {

    return (
        preferences !== null &&
        typeof preferences === "object" &&
        typeof preferences.budgetWarnings === "boolean" &&
        typeof preferences.savingsGoalNotifications === "boolean"
    );

}


// --------------------------------------------------
// Load preferences from browser storage.
// --------------------------------------------------

function loadPreferences() {

    try {

        // Retrieve the previously saved preferences.
        const storedPreferences =
            localStorage.getItem(STORAGE_KEY);

        // Use default settings for a new user.
        if (storedPreferences === null) {

            savedPreferences = { ...DEFAULT_PREFERENCES };

            displayPreferences(savedPreferences);

            showMessage(
                "Default notification preferences loaded."
            );

            return;
        }

        // Convert the stored JSON string into an object.
        const preferences = JSON.parse(storedPreferences);

        // Check that the stored information is valid.
        if (!isValidPreferences(preferences)) {

            throw new Error("Stored preferences have an invalid format.");

        }

        // Keep a copy of the saved settings.
        savedPreferences = { ...preferences };

        // Display the saved settings.
        displayPreferences(savedPreferences);

        showMessage("Your saved preferences have been loaded.");

    } catch (error) {

        console.error("Unable to load notification preferences:", error);

        // Restore safe default values.
        savedPreferences = { ...DEFAULT_PREFERENCES };

        displayPreferences(savedPreferences);

        showMessage(
            "Unable to load saved preferences. Default settings are displayed.",
            "error"
        );

    }

}


// --------------------------------------------------
// Save the selected notification preferences.
// --------------------------------------------------

function savePreferences() {

    // Read the user's current selections.
    const currentPreferences = getCurrentPreferences();

    try {

        // Convert the preference object into JSON.
        const preferencesJSON =
            JSON.stringify(currentPreferences);

        // Save the preferences in browser storage.
        localStorage.setItem(STORAGE_KEY, preferencesJSON);

        // Update the last successfully saved settings.
        savedPreferences = { ...currentPreferences };

        showMessage(
            "Your notification preferences have been saved successfully.",
            "success"
        );

        console.log(
            "Saved notification preferences:",
            savedPreferences
        );

    } catch (error) {

        console.error("Unable to save notification preferences:", error);

        showMessage(
            "Your preferences could not be saved. Please check your browser storage settings and try again.",
            "error"
        );

    }

}


// --------------------------------------------------
// Cancel unsaved changes.
// --------------------------------------------------

function cancelChanges() {

    // Restore the last successfully saved preferences.
    displayPreferences(savedPreferences);

    showMessage(
        "Changes cancelled. Your last saved preferences have been restored."
    );

}


// --------------------------------------------------
// Save button event.
// --------------------------------------------------

saveButton.addEventListener("click", function () {

    savePreferences();

});


// --------------------------------------------------
// Cancel button event.
// --------------------------------------------------

cancelButton.addEventListener("click", function () {

    cancelChanges();

});


// --------------------------------------------------
// Back button demonstration.
// --------------------------------------------------

backButton.addEventListener("click", function (event) {

    event.preventDefault();

    showMessage(
        "The Settings page will be connected during frontend integration."
    );

});


// --------------------------------------------------
// Load preferences when the page opens.
// --------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {

    loadPreferences();

});
