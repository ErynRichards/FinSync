
"use strict";

// FinSync Settings - Eryn's Allocation

// Flask backend endpoint for changing passwords.
// The backend developer must implement this endpoint.
const CHANGE_PASSWORD_ENDPOINT =
    "/api/settings/change-password";

// Get HTML elements
const passwordForm =
    document.getElementById("passwordForm");

const passwordMessage =
    document.getElementById("passwordMessage");

const changePasswordButton =
    document.getElementById("changePasswordButton");

const themeMessage =
    document.getElementById("themeMessage");

// Display success and error messages
function showMessage(element, message, type) {
    element.textContent = message;
    element.className = "message " + type;
}

// Change Password form submission
passwordForm.addEventListener("submit", async (event) => {

    // Prevent the page from refreshing
    event.preventDefault();

    // Retrieve password values
    const currentPassword =
        document.getElementById("currentPassword").value;

    const newPassword =
        document.getElementById("newPassword").value;

    const confirmPassword =
        document.getElementById("confirmPassword").value;

    // Validate required fields
    if (!currentPassword || !newPassword || !confirmPassword) {
        showMessage(
            passwordMessage,
            "Please complete all password fields.",
            "error"
        );
        return;
    }

    // Validate minimum password length
    if (newPassword.length < 8) {
        showMessage(
            passwordMessage,
            "New password must be at least 8 characters.",
            "error"
        );
        return;
    }

    // Ensure passwords match
    if (newPassword !== confirmPassword) {
        showMessage(
            passwordMessage,
            "New passwords do not match.",
            "error"
        );
        return;
    }

    // Prevent reusing the current password
    if (currentPassword === newPassword) {
        showMessage(
            passwordMessage,
            "Choose a password different from your current password.",
            "error"
        );
        return;
    }

    // Disable button while processing
    changePasswordButton.disabled = true;

    showMessage(
        passwordMessage,
        "Updating password...",
        ""
    );

    try {
        // Send password change request to Flask
        const response = await fetch(CHANGE_PASSWORD_ENDPOINT, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...(document.querySelector('meta[name="csrf-token"]')?.content ? {"X-CSRF-Token": document.querySelector('meta[name="csrf-token"]').content} : {})
            },
            credentials: "same-origin",
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword,
                confirm_password: confirmPassword
            })
        });

        // Read the backend response
        const result = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(
                result.message ||
                "Password could not be updated. Please try again."
            );
        }

        // Clear form after successful update
        passwordForm.reset();

        showMessage(
            passwordMessage,
            result.message || "Password changed successfully.",
            "success"
        );

    } catch (error) {

        // Display server or connection errors
        showMessage(
            passwordMessage,
            error instanceof TypeError
                ? "Cannot connect to the server. Password was not changed."
                : error.message,
            "error"
        );

    } finally {
        // Re-enable button
        changePasswordButton.disabled = false;
    }
});


// APPEARANCE SETTINGS

// Retrieve Light Mode and Dark Mode options
const themeRadios =
    document.querySelectorAll('input[name="theme"]');

// Default theme
let savedTheme = "light";

// Load previously saved theme
try {
    savedTheme =
        localStorage.getItem("finsync-theme") === "dark"
            ? "dark"
            : "light";
} catch (error) {
    savedTheme = "light";
}

// Apply the saved theme
document.documentElement.dataset.theme = savedTheme;

// Select the matching radio option
const activeRadio = document.querySelector(
    `input[name="theme"][value="${savedTheme}"]`
);

if (activeRadio) {
    activeRadio.checked = true;
}

// Save Appearance button
document.getElementById("saveThemeButton")
    .addEventListener("click", () => {

        // Retrieve selected theme
        const chosen = document.querySelector(
            'input[name="theme"]:checked'
        );

        // Ensure a theme was selected
        if (!chosen) {
            showMessage(
                themeMessage,
                "Please select a theme.",
                "error"
            );
            return;
        }

        try {
            // Save the selected theme in browser storage
            localStorage.setItem(
                "finsync-theme",
                chosen.value
            );

            // Apply the selected theme
            document.documentElement.dataset.theme =
                chosen.value;

            // Display confirmation
            showMessage(
                themeMessage,
                "Appearance settings saved successfully.",
                "success"
            );

        } catch (error) {

            // Apply theme even if browser storage fails
            document.documentElement.dataset.theme =
                chosen.value;

            showMessage(
                themeMessage,
                "Theme applied, but could not be saved in this browser.",
                "error"
            );
        }
    });

// Notification preferences (Reece's allocation, connected to saved account preferences)
(async function () {
  const budget = document.getElementById("budgetNotifications");
  const savings = document.getElementById("savingsNotifications");
  const save = document.getElementById("saveNotificationsButton");
  const message = document.getElementById("notificationsMessage");
  if (!budget || !savings || !save) return;

  try {
    const response = await fetch("/api/settings/preferences", {credentials:"same-origin"});
    if (!response.ok) throw new Error("Unable to load preferences");

    const data = await response.json();
    budget.checked = Boolean(data.budget_notifications);
    savings.checked = Boolean(data.savings_notifications);

  } catch(e) { message.textContent = e.message; }

  // Run this code when the user interacts with the page.
  save.addEventListener("click", async function () {
    save.disabled = true;

    try {
      const response = await fetch("/api/settings/preferences", {
        method:"PUT", credentials:"same-origin", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({budget_notifications:budget.checked,savings_notifications:savings.checked})

      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.message || "Could not save preferences");

      message.textContent = "Notification preferences saved.";

    } catch(e) { message.textContent = e.message; }
    finally { save.disabled = false; }
  });
})();
