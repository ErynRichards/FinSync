(() => {
  "use strict";

  const section = document.querySelector(".spending-category");
  if (!section) return;

  const canvas = section.querySelector("#spending-chart");
  const plot = section.querySelector("#spending-plot");
  const status = section.querySelector("#spending-status");
  const breakdown = section.querySelector("#spending-breakdown");
  const period = section.querySelector("#spending-period");
  const month = document.querySelector("#report-month");

  const rand = new Intl.NumberFormat("en-ZA", { style: "currency", currency: "ZAR" });
  const colors = {
    shopping: "#8de0e6",
    food: "#61b0ca",
    bills: "#4484ab",
    medicine: "#385988",
    others: "#303262"
  };
  const extraColors = ["#467b9a", "#71518e", "#34908c", "#a56072"];

  let chart;
  let categories = [];

  // Put short labels around the ring, just like the reference.
  // When there are many categories or narrow slices, the list and tooltips
  // still show every value without crowding the graph with overlapping text.
  const ringLabels = {
    id: "spendingRingLabels",
    afterDatasetsDraw(instance) {
      if (categories.length > 5 || instance.width < 260) return;

      const context = instance.ctx;
      context.save();
      context.font = "bold 10px Arial";
      context.fillStyle = "#242851";
      context.textAlign = "center";
      context.textBaseline = "middle";

      instance.getDatasetMeta(0).data.forEach((arc, index) => {
        const category = categories[index];
        if (category.percent < 8) return;

        const angle = (arc.startAngle + arc.endAngle) / 2;
        const radius = arc.outerRadius + 18;
        const name = category.name.length > 15 ? category.name.slice(0, 13) + "…" : category.name;
        const halfWidth = context.measureText(name).width / 2 + 3;
        const x = Math.min(instance.width - halfWidth,
          Math.max(halfWidth, arc.x + Math.cos(angle) * radius));
        const y = arc.y + Math.sin(angle) * radius;

        context.fillText(name, x, y - 6);
        context.fillText(category.percent.toFixed(1) + "%", x, y + 6);
      });

      context.restore();
    }
  };

  // The panel uses the same colors and percentages as the chart.
  function makeCategoryItem(category) {
    const item = document.createElement("li");
    const name = document.createElement("strong");
    const values = document.createElement("span");
    const track = document.createElement("span");
    const fill = document.createElement("span");

    // textContent displays backend category names as text, never as HTML.
    name.textContent = category.name;
    values.className = "spending-values";
    values.textContent = rand.format(category.cents / 100) + " · " + category.percent.toFixed(1) + "%";
    track.className = "spending-track";
    track.setAttribute("aria-hidden", "true");
    fill.className = "spending-fill";
    fill.style.width = category.percent + "%";
    fill.style.backgroundColor = category.color;
    track.append(fill);
    item.append(name, track, values);
    return item;
  }

  // Call this after each successful backend response. Expected input:
  // [{ category: "Food", total: 420.50 }, { category: "Transport", total: "180.00" }]
  // Amounts are in rand. An empty array clears the chart and shows the empty message.
  window.updateSpendingByCategory = function (rows) {
    const grouped = new Map();

    for (const row of rows) {
      const name = typeof row?.category === "string" ? row.category.trim() : "";
      const amount = typeof row?.total === "string" || typeof row?.total === "number"
        ? Number(row.total) : NaN;
      const cents = Math.round(amount * 100);
      if (!name || !Number.isSafeInteger(cents) || cents <= 0) continue;

      // Combine repeated category names and add amounts in cents.
      const key = name.toLowerCase();
      const previous = grouped.get(key);
      grouped.set(key, { name: previous?.name ?? name, cents: (previous?.cents ?? 0) + cents });
    }

    const total = [...grouped.values()].reduce((sum, category) => sum + category.cents, 0);
    categories = [...grouped].map(([key, category], index) => ({
      ...category,
      percent: category.cents / total * 100,
      color: Object.hasOwn(colors, key) ? colors[key] : extraColors[index % extraColors.length]
    }));

    const hasExpenses = categories.length > 0;
    const canDraw = hasExpenses && typeof window.Chart === "function";
    plot.hidden = !canDraw;
    breakdown.hidden = !hasExpenses;
    status.hidden = canDraw;
    status.textContent = hasExpenses
      ? "The chart could not load. Category totals are shown beside it."
      : "No expense information available for this period.";

    // The legend uses the screenshot order while keeping every backend category.
    const panelOrder = ["shopping", "bills", "food", "medicine"];
    const panelCategories = panelOrder
      .map(key => categories.find(category => category.name.toLowerCase() === key))
      .filter(Boolean);
    panelCategories.push(...categories.filter(category => !panelOrder.includes(category.name.toLowerCase())));
    breakdown.replaceChildren(...panelCategories.map(makeCategoryItem));

    if (!canDraw) {
      chart?.destroy();
      chart = undefined;
      return;
    }

    const data = {
      labels: categories.map(category => category.name),
      datasets: [{
        data: categories.map(category => category.cents),
        backgroundColor: categories.map(category => category.color),
        borderWidth: 0
      }]
    };

    // Reuse the same chart when new data arrives. Chart.js redraws its slices.
    if (chart) {
      chart.data = data;
      chart.update();
      return;
    }

    chart = new window.Chart(canvas, {
      type: "doughnut",
      data,
      plugins: [ringLabels],
      options: {
        maintainAspectRatio: false,
        animation: false,
        cutout: "50%",
        layout: { padding: { top: 23, right: 37, bottom: 19, left: 19 } },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label({ dataIndex }) {
                const category = categories[dataIndex];
                return rand.format(category.cents / 100) + " · " + category.percent.toFixed(1) + "%";
              }
            }
          }
        }
      }
    });
  };

  function changeFilters() {
    const filters = { month: month?.value, period: period.value };

    // Demo values reproduce the screenshot. The second month tests the empty state.
    // Remove data-preview from the section when integrating with FinSync.
    if (section.hasAttribute("data-preview")) {
      const week = [
        { category: "Shopping", total: 200 },
        { category: "Food", total: 200 },
        { category: "Bills", total: 300 },
        { category: "Medicine", total: 400 },
        { category: "Others", total: 600 }
      ];
      const monthly = [
        ...week,
        { category: "Transport", total: 240 },
        { category: "Entertainment", total: 160 }
      ];
      window.updateSpendingByCategory(filters.month === "2026-05"
        ? (filters.period === "week" ? week : monthly) : []);
      return;
    }

    // The Reports page can listen for this event, fetch the selected period,
    // and pass its latest response to updateSpendingByCategory(rows).
    section.dispatchEvent(new CustomEvent("spending-filter-change", { bubbles: true, detail: filters }));
  }

  period.addEventListener("change", changeFilters);
  month?.addEventListener("change", changeFilters);
  if (section.hasAttribute("data-preview")) changeFilters();
})();
