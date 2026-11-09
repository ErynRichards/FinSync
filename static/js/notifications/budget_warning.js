
// MISHAYLE: Connect the Eryn/Michalyn popup to live budget warnings.

// Check for exceeded budgets and display the warning popup.
async function checkBudgetNotifications() {
    const dialog = document.getElementById("budget-warning");

    if (!dialog) return;

    try {
        const response = await fetch("/api/notifications/budgets", {
            credentials: "same-origin"
        });

        if (!response.ok) return;

        const data = await response.json();

        const money = value => "R" + Number(value).toLocaleString("en-ZA", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });

        for (const alert of data.notifications || []) {
            document.getElementById("budget-warning-category").textContent =
                alert.category;

            document.getElementById("budget-warning-limit").textContent =
                money(alert.monthlyBudget);

            document.getElementById("budget-warning-expenses").textContent =
                money(alert.totalExpenses);

            document.getElementById("budget-warning-excess").textContent =
                money(alert.exceededBy);

            if (typeof dialog.showModal === "function") {
                dialog.showModal();

                await new Promise(resolve => {
                    dialog.addEventListener("close", resolve, {once: true});
                });
            }
        }

    } catch (error) {
        console.error("Budget warning check failed", error);
    }
}

// MISHAYLE: Allow the Transactions page to run this function after saving.
window.checkBudgetNotifications = checkBudgetNotifications;

// Keep the original check when the page first loads.
document.addEventListener("DOMContentLoaded", checkBudgetNotifications);
