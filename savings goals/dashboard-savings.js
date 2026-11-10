
"use strict";

// Flask API configuration.
// Must match the Savings Goals API.
const SAVINGS_API_BASE = "";

// Same demo storage used by the Savings Goals page.
const SAVINGS_STORAGE_KEY =
  "finsync_demo_savings_goals_v1";

// Update the Dashboard savings amount.
async function refreshDashboardSavings() {

  // Find the existing Savings card value.
  const valueElement = document.getElementById(
    "dashboard-savings-total"
  );

  if (!valueElement) {
    return;
  }

  try {
    let items;

    if (SAVINGS_API_BASE) {

      // Get savings goals from Flask.
      const response = await fetch(
        `${SAVINGS_API_BASE}/savings-goals`,
        {
          credentials: "same-origin"
        }
      );

      if (!response.ok) {
        throw new Error("Could not load savings");
      }

      const data = await response.json();

      items = Array.isArray(data)
        ? data
        : data.goals;

    } else {

      // Demo mode: read the saved goals.
      items = JSON.parse(
        localStorage.getItem(SAVINGS_STORAGE_KEY) || "[]"
      );
    }

    if (!Array.isArray(items)) {
      throw new Error("Invalid savings response");
    }

    // Calculate total saved amount.
    const totalCents = items.reduce((sum, item) => {

      const amount = Number(
        item.savedAmount ?? item.saved_amount ?? 0
      );

      if (!Number.isFinite(amount) || amount < 0) {
        throw new Error("Invalid savings amount");
      }

      return sum + Math.round(amount * 100);

    }, 0);

    // Display total savings in rand.
    valueElement.textContent =
      "R " + new Intl.NumberFormat("en-ZA", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(totalCents / 100);

  } catch (error) {

    valueElement.textContent = "Unavailable";

    console.error("Dashboard savings:", error);
  }
}

// Load savings when the Dashboard opens.
document.addEventListener(
  "DOMContentLoaded",
  refreshDashboardSavings
);

// Refresh when returning to the Dashboard.
window.addEventListener(
  "pageshow",
  refreshDashboardSavings
);

// Refresh if demo storage changes in another tab.
window.addEventListener("storage", event => {
  if (event.key === SAVINGS_STORAGE_KEY) {
    refreshDashboardSavings();
  }
});
