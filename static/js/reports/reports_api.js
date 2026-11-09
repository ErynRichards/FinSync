// REECE + MISHAYLE: Load live Reports data without refreshing the page.
(() => {
  "use strict";
  const period = document.getElementById("reportPeriod");
  const month = document.getElementById("report-month");
  const spendingPeriod = document.getElementById("spending-period");
  const spendingSection = document.getElementById("panel-category");
  const status = document.createElement("p");
  status.id = "reports-api-status";
  status.setAttribute("role", "status");
  document.querySelector(".reports-tabs").before(status);
  let requestId = 0;

  function setMonths(months) {
    const previous = month.value;
    month.replaceChildren();
    for (const value of months) {
      const option = document.createElement("option");
      option.value = value;
      const [year, number] = value.split("-");
      option.textContent = new Date(Date.UTC(Number(year), Number(number)-1, 1))
        .toLocaleDateString("en-ZA", {month:"long", year:"numeric", timeZone:"UTC"});
      month.appendChild(option);
    }
    if (months.includes(previous)) month.value = previous;
    else if (months.length) month.value = months[months.length-1];
  }

  async function loadReports() {
    const current = ++requestId;
    status.textContent = "Loading reports...";
    try {
      const response = await fetch(`/api/reports?period=${encodeURIComponent(period.value)}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Could not load reports");
      if (current !== requestId) return;
      window.updateMonthlyReports(data.monthly_reports);
      setMonths(data.months);
      await loadSpending();
      status.textContent = "Reports updated from your transactions.";
    } catch (error) {
      if (current !== requestId) return;
      status.textContent = `Reports could not load: ${error.message}`;
      window.updateMonthlyReports([]);
      window.updateSpendingByCategory([]);
    }
  }

  async function loadSpending() {
    const current = requestId;
    try {
      const params = new URLSearchParams({month:month.value, range:spendingPeriod.value});
      const response = await fetch(`/api/reports/spending?${params}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Could not load category spending");
      if (current !== requestId) return;
      window.updateSpendingByCategory(data.category_spending);
    } catch (error) {
      if (current !== requestId) return;
      window.updateSpendingByCategory([]);
      status.textContent = `Category spending could not load: ${error.message}`;
    }
  }
  period.addEventListener("change", loadReports);
  spendingSection.addEventListener("spending-filter-change", loadSpending);
  loadReports();
})();
