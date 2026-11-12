
(() => {
  "use strict";

  // Find the part of the page this code will update.
  const section = document.querySelector(".spending-category");
  if (!section) return;

  const canvas = section.querySelector("#spending-chart");
  const plot = section.querySelector("#spending-plot");
  const status = section.querySelector("#spending-status");
  const breakdown = section.querySelector("#spending-breakdown");
  const period = section.querySelector("#spending-period");
  // Find the part of the page this code will update.
  const month = document.querySelector("#report-month");

  const rand = new Intl.NumberFormat("en-ZA", {
    style: "currency",
    currency: "ZAR"
  });

  const colors = {
    groceries: "#3498DB",       // Blue
    entertainment: "#9B59B6",   // Purple
    utilities: "#2ECC71",       // Green
    "other expense": "#E74C3C", // Red
    transport: "#F39C12",       // Orange
    housing: "#1ABC9C",         // Turquoise
    education: "#F1C40F",       // Yellow
    shopping: "#E91E63",        // Pink
    food: "#8E44AD",            // Dark purple
    bills: "#16A085",           // Teal
    medicine: "#D35400",        // Dark orange
    others: "#7F8C8D"           // Grey
};

const extraColors = [
    "#2E86C1",
    "#AF7AC5",
    "#48C9B0",
    "#E59866",
    "#F4D03F"
];

  let chart;
  let categories = [];

  // Display category labels around the doughnut chart.
  const ringLabels = {
    id: "spendingRingLabels",

    afterDatasetsDraw(instance) {
      if (categories.length > 5 || instance.width < 260) return;

      const context = instance.ctx;
      context.save();

      context.font = "bold 12px Arial";

      // Red text with a white outline.
      context.fillStyle = "#CC0000";
      context.strokeStyle = "#FFFFFF";
      context.lineWidth = 3;
      context.lineJoin = "round";

      context.textAlign = "center";
      context.textBaseline = "middle";


      instance.getDatasetMeta(0).data.forEach((arc, index) => {
        const category = categories[index];
        if (category.percent < 8) return;

        // Move the labels further away from the doughnut chart.
        const angle = (arc.startAngle + arc.endAngle) / 2;
        const radius = arc.outerRadius + 45;

        const name = category.name.length > 15
          ? category.name.slice(0, 13) + "…"
          : category.name;

        const halfWidth = context.measureText(name).width / 2 + 3;

        const x = Math.min(
          instance.width - halfWidth,
          Math.max(halfWidth, arc.x + Math.cos(angle) * radius)
        );

        const y = arc.y + Math.sin(angle) * radius;


        // Draw the white outline first.
        context.strokeText(name, x, y - 7);
        context.strokeText(category.percent.toFixed(1) + "%", x, y + 7);

        // Draw the red text on top.
        context.fillText(name, x, y - 7);
        context.fillText(category.percent.toFixed(1) + "%", x, y + 7);

      });

      context.restore();
    }
  };

  // Create an individual category breakdown item.
  function makeCategoryItem(category) {
    const item = document.createElement("li");
    const name = document.createElement("strong");
    const values = document.createElement("span");
    const track = document.createElement("span");
    const fill = document.createElement("span");

    name.textContent = category.name;

    values.className = "spending-values";
    values.textContent =
      rand.format(category.cents / 100) +
      " · " +
      category.percent.toFixed(1) + "%";

    track.className = "spending-track";
    track.setAttribute("aria-hidden", "true");

    fill.className = "spending-fill";
    fill.style.width = category.percent + "%";
    fill.style.backgroundColor = category.color;

    track.append(fill);
    item.append(name, track, values);

    return item;
  }

  // Update Spending by Category using financial data.
  // Expected: [{ category: "Food", total: 420.50 }]
  window.updateSpendingByCategory = function(rows) {
    const grouped = new Map();

    for (const row of rows) {
      const name = typeof row?.category === "string"
        ? row.category.trim()
        : "";

      const amount =
        typeof row?.amount === "string" ||
        typeof row?.amount === "number"
          ? Number(row.amount)
          : NaN;

      const cents = Math.round(amount * 100);

      if (!name || !Number.isSafeInteger(cents) || cents <= 0) {
        continue;
      }

      const key = name.toLowerCase();
      const previous = grouped.get(key);

      grouped.set(key, {
        name: previous?.name ?? name,
        cents: (previous?.cents ?? 0) + cents
      });
    }

    const total = [...grouped.values()].reduce(
      (sum, category) => sum + category.cents,
      0
    );

    categories = [...grouped].map(([key, category], index) => ({
      ...category,
      percent: category.cents / total * 100,
      color: Object.hasOwn(colors, key)
        ? colors[key]
        : extraColors[index % extraColors.length]
    }));

    const hasExpenses = categories.length > 0;
    const canDraw = hasExpenses && typeof window.Chart === "function";

    plot.hidden = !canDraw;
    breakdown.hidden = !hasExpenses;
    status.hidden = canDraw;

    status.textContent = hasExpenses
      ? "The chart could not load. Category totals are shown beside it."
      : "No expense information available for this period.";

    const panelOrder = [
      "shopping", "bills", "food", "medicine"
    ];

    const panelCategories = panelOrder
      .map(key =>
        categories.find(category =>
          category.name.toLowerCase() === key
        )
      )
      .filter(Boolean);

    panelCategories.push(
      ...categories.filter(category =>
        !panelOrder.includes(category.name.toLowerCase())
      )
    );

    breakdown.replaceChildren(
      ...panelCategories.map(makeCategoryItem)
    );

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
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    cutout: "50%",


      layout: {
          padding: {
              top: 55,
              right: 65,
              bottom: 55,
              left: 65
          }
      },


        plugins: {
          legend: {
            display: false
          },

          tooltip: {
            callbacks: {
              label({ dataIndex }) {
                const category = categories[dataIndex];

                return (
                  rand.format(category.cents / 100) +
                  " · " +
                  category.percent.toFixed(1) + "%"
                );
              }
            }
          }
        }
      }
    });
  };

  // Handle spending period and month filters.
  function changeFilters() {
    const filters = {
      month: month?.value,
      period: period.value
    };

    // Demonstration values for frontend testing.
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

      window.updateSpendingByCategory(
        filters.month === "2026-05"
          ? (filters.period === "week" ? week : monthly)
          : []
      );

      return;
    }

    // Notify backend integration code when filters change.
    section.dispatchEvent(
      new CustomEvent("spending-filter-change", {
        bubbles: true,
        detail: filters
      })
    );
  }

  // Run this code when the user interacts with the page.
  period.addEventListener("change", changeFilters);
  // Run this code when the user interacts with the page.
  month?.addEventListener("change", changeFilters);

  if (section.hasAttribute("data-preview")) {
    changeFilters();
  }
})();


// ERYN - MONTHLY TREND AND INCOME VS EXPENSES

(() => {
  "use strict";

  // Data arrives from the authenticated FinSync Reports API.
  let monthlyReports = [];

  let trendChart;
  let comparisonChart;

  // Find the part of the page this code will update.
  const period = document.querySelector("#reportPeriod");

  const tabs = [
    ...document.querySelectorAll("[data-report-tab]")
  ];

  const panels = {
    category: document.querySelector("#panel-category"),
    trend: document.querySelector("#panel-trend"),
    comparison: document.querySelector("#panel-comparison")
  };

  // Format values as South African rands.
  const currency = new Intl.NumberFormat("en-ZA", {
    style: "currency",
    currency: "ZAR"
  });

  const money = value => currency.format(value);

  // Convert YYYY-MM into a readable month label.
  const monthLabel = value => {
    const [year, month] = value.split("-").map(Number);

    return new Date(
      Date.UTC(year, month - 1, 1)
    ).toLocaleDateString("en-ZA", {
      month: "short",
      year: "numeric",
      timeZone: "UTC"
    });
  };

  // Switch between the three Reports tabs.
  function activateTab(name) {
    for (const tab of tabs) {
      const active = tab.dataset.reportTab === name;

      tab.setAttribute("aria-selected", String(active));
      tab.tabIndex = active ? 0 : -1;
    }

    for (const [key, panel] of Object.entries(panels)) {
      panel.hidden = key !== name;
    }

    document.querySelector(
      "#report-period-control"
    ).hidden = name === "category";

    document.querySelector(
      ".reports-month"
    ).hidden = name !== "category";

    if (name !== "category") {
      updateCharts();
    }
  }

  // Add click and keyboard navigation to Reports tabs.
  tabs.forEach((tab, index) => {
    // Run this code when the user interacts with the page.
    tab.addEventListener("click", () => {
      activateTab(tab.dataset.reportTab);
    });

    // Run this code when the user interacts with the page.
    tab.addEventListener("keydown", event => {
      if (![
        "ArrowLeft", "ArrowRight", "Home", "End"
      ].includes(event.key)) {
        return;
      }

      event.preventDefault();

      const next =
        event.key === "Home" ? 0 :
        event.key === "End" ? tabs.length - 1 :
        (
          index +
          (event.key === "ArrowRight" ? 1 : -1) +
          tabs.length
        ) % tabs.length;

      tabs[next].focus();
      activateTab(tabs[next].dataset.reportTab);
    });
  });

  // Update both financial graphs.
  function updateCharts() {
    if (typeof window.Chart !== "function") return;

    const selected = monthlyReports.slice(
      -Number(period.value)
    );

    const labels = selected.map(row =>
      monthLabel(row.month)
    );

    const incomes = selected.map(row => row.income);
    const expenses = selected.map(row => row.expenses);

    const empty = !selected.length;

    document.querySelector("#trend-empty").hidden = !empty;
    document.querySelector("#comparison-empty").hidden = !empty;

    document.querySelectorAll(
      ".report-chart-container"
    ).forEach(element => {
      element.hidden = empty;
    });

    if (empty) return;

    // Shared Chart.js configuration.

    // Shared Chart.js configuration for line and bar charts.
    const common = {
      responsive: true,
      maintainAspectRatio: false,

      layout: {
        padding: 15
      },

      plugins: {
        legend: {
          display: true
        },

        tooltip: {
          callbacks: {
            label: context =>
              context.dataset.label + ": " +
              money(context.parsed.y)
          }
        }
      },

      scales: {
        x: {
          grid: {
            display: false
          },
          ticks: {
            autoSkip: true,
            maxRotation: 0
          }
        },

        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              if (value === 0) return "R0";
              if (Math.abs(value) < 1000) return "R" + value;
              return "R" + (value / 1000) + "k";
            }
          }
        }
      }
    };


    // Monthly Trend line graph.
    if (!trendChart) {
      trendChart = new Chart(
        document.querySelector("#monthlyTrendChart"),
        {
          type: "line",

          data: {
            labels: [],
            datasets: [{
              label: "Expenses",
              data: [],
              borderColor: "#155eef",
              backgroundColor: "rgba(21,94,239,.06)",
              fill: true,
              tension: 0.3,
              pointRadius: 4
            }]
          },

          options: common
        }
      );
    }


    // Income vs Expenses double bar graph.
    if (!comparisonChart) {
      comparisonChart = new Chart(
        document.querySelector("#incomeExpensesChart"),
        {
          type: "bar",

          data: {
            labels: [],
            datasets: [
              {
                label: "Income",
                data: [],
                backgroundColor: "#155eef",
                borderRadius: 5
              },
              {
                label: "Expenses",
                data: [],
                backgroundColor: "#76a0f5",
                borderRadius: 5
              }
            ]
          },

          options: {
            ...common,

            // Add spacing around the chart.
            layout: {
              padding: {
                top: 15,
                right: 35,
                bottom: 15,
                left: 15
              }
            },

            // Prevent the first and last month's bars
            // from being cut off.
            scales: {
              ...common.scales,

              x: {
                ...common.scales.x,
                offset: true
              }
            },

            // Adjust the width of the bars.
            datasets: {
              bar: {
                categoryPercentage: 0.6,
                barPercentage: 0.7,
                maxBarThickness: 35
              }
            }
          }
        }
      );
    }


    // Refresh Monthly Trend.
    trendChart.data.labels = labels;
    trendChart.data.datasets[0].data = expenses;
    trendChart.update();

    // Refresh Income vs Expenses.
    comparisonChart.data.labels = labels;
    comparisonChart.data.datasets[0].data = incomes;
    comparisonChart.data.datasets[1].data = expenses;
    comparisonChart.update();
  }

  // Backend integration function.
  // Expected records:
  // [{month:"2026-10", income:11500, expenses:5200}]
  window.updateMonthlyReports = function(rows) {
    if (!Array.isArray(rows)) {
      throw new TypeError(
        "Expected an array of monthly reports"
      );
    }

    monthlyReports = rows.map(row => {
      if (
        !/^\d{4}-(0[1-9]|1[0-2])$/.test(row.month) ||
        !Number.isFinite(Number(row.income)) ||
        Number(row.income) < 0 ||
        !Number.isFinite(Number(row.expenses)) ||
        Number(row.expenses) < 0
      ) {
        throw new Error("Invalid monthly report record");
      }

      return {
        month: row.month,
        income: Number(row.income),
        expenses: Number(row.expenses)
      };
    }).sort((a, b) =>
      a.month.localeCompare(b.month)
    );

    updateCharts();
  };

  // Update the graphs when the reporting period changes.
  period.addEventListener("change", updateCharts);

  // Display Spending by Category first.
  activateTab("category");
})();
