"use strict";

/*
 * FinSync shared theme loader.
 *
 * Uses the existing "finsync-theme" localStorage key
 * already used by the Settings page.
 */

(function () {
    const THEME_STORAGE_KEY = "finsync-theme";

    // Handle this part of the page.
    function applySavedTheme() {
        let theme = "light";

        try {
            theme = localStorage.getItem(THEME_STORAGE_KEY) === "dark"
                ? "dark"
                : "light";
        } catch (error) {
            console.warn("Could not read the saved FinSync theme.", error);
        }

        document.documentElement.dataset.theme = theme;
    }

    // Apply the saved theme when the page loads.
    applySavedTheme();

    // Update the theme if it is changed in another browser tab.
    window.addEventListener("storage", function (event) {
        if (event.key === THEME_STORAGE_KEY) {
            applySavedTheme();
        }
    });
})();
