
"use strict";

// Demonstration data for frontend testing only.
// Replace with information from Mishayle's Flask backend
// once integration is ready.

const reportData = [
    { month: "2025-11", income: 8500, expenses: 4200 },
    { month: "2025-12", income: 9200, expenses: 5100 },
    { month: "2026-01", income: 9000, expenses: 4800 },
    { month: "2026-02", income: 10500, expenses: 6000 },
    { month: "2026-03", income: 9800, expenses: 5300 },
    { month: "2026-04", income: 11000, expenses: 6500 },
    { month: "2026-05", income: 9500, expenses: 4200 },
    { month: "2026-06", income: 10200, expenses: 5100 },
    { month: "2026-07", income: 9800, expenses: 3900 },
    { month: "2026-08", income: 11000, expenses: 5800 },
    { month: "2026-09", income: 10500, expenses: 4600 },
    { month: "2026-10", income: 11500, expenses: 5200 }
];

// Format monetary values in South African rands
function formatRand(amount) {
    return new Intl.NumberFormat("en-ZA", {
        style: "currency",
        currency: "ZAR"
    }).format(amount);
}

// Convert YYYY-MM to a readable month
function formatMonth(month) {
    const [year, monthNumber] = month.split("-");

    const date = new Date(
        Date.UTC(Number(year), Number(monthNumber) - 1, 1)
    );

    return date.toLocaleDateString("en-ZA", {
        month: "short",
        year: "numeric",
        timeZone: "UTC"
    });
}

// Get the selected reporting period
const reportPeriod = document.getElementById("reportPeriod");

// Create Monthly Trend line chart
const monthlyTrendChart = new Chart(
    document.getElementById("monthlyTrendChart"),
    {
        type: "line",

        data: {
            labels: [],
            datasets: [{
                label: "Expenses",
                data: [],
                borderColor: "#155eef",
                backgroundColor: "rgba(21, 94, 239, 0.06)",
                fill: true,
                tension: 0.3,
                pointRadius: 4
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: true
                },

                tooltip: {
                    callbacks: {
                        label: context =>
                            "Expenses: " + formatRand(context.parsed.y)
                    }
                }
            },

            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => formatRand(value)
                    }
                }
            }
        }
    }
);

// Create Income vs Expenses double bar chart
const incomeExpensesChart = new Chart(
    document.getElementById("incomeExpensesChart"),
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
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: true
                },

                tooltip: {
                    callbacks: {
                        label: context =>
                            context.dataset.label + ": " +
                            formatRand(context.parsed.y)
                    }
                }
            },

            scales: {
                x: {
                    stacked: false
                },

                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => formatRand(value)
                    }
                }
            }
        }
    }
);

// Update both graphs using the selected period
function updateReports() {

    const months = Number(reportPeriod.value);

    // Select the most recent months from the data
    const selectedData = reportData.slice(-months);

    const labels = selectedData.map(record =>
        formatMonth(record.month)
    );

    const income = selectedData.map(record =>
        record.income
    );

    const expenses = selectedData.map(record =>
        record.expenses
    );

    // Update Monthly Trend graph
    monthlyTrendChart.data.labels = labels;
    monthlyTrendChart.data.datasets[0].data = expenses;
    monthlyTrendChart.update();

    // Update Income vs Expenses graph
    incomeExpensesChart.data.labels = labels;
    incomeExpensesChart.data.datasets[0].data = income;
    incomeExpensesChart.data.datasets[1].data = expenses;
    incomeExpensesChart.update();
}

// Update charts when reporting period changes
reportPeriod.addEventListener("change", updateReports);

// Display initial charts
updateReports();
