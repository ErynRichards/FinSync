# Load the tools needed in this file.
import matplotlib
matplotlib.use("Agg")

# Load the tools needed in this file.
import matplotlib.pyplot as plt

# Use functions and classes from another file.
from datetime import date, timedelta

# Use functions and classes from another file.
from io import BytesIO


# LASHANYA'S PART: Graph styling and Matplotlib image generation.
# MISHAYLE'S PART calculates the daily data before this function is called.
def create_cash_flow_graph(daily_data):
    dates = list(daily_data.keys())
    # Save an amount for a calculation or database update.
    income = [float(daily_data[day]["income"]) for day in dates]
    # Save an amount for a calculation or database update.
    expenses = [float(daily_data[day]["expenses"]) for day in dates]
    net_cash_flow = [float(daily_data[day]["net_cash_flow"]) for day in dates]
    dates = [date.fromisoformat(day) for day in dates]

    # Labels for the last 7 days
    labels = [
        day.strftime("%d %b")
        for day in dates
    ]

    # Create graph
    fig, ax = plt.subplots(figsize=(10, 4.5))

    # Income line
    ax.plot(
        labels,
        income,
        color="#00AFC1",
        marker="o",
        linewidth=2.5,
        label="Income"
    )

    # Expenses line
    ax.plot(
        labels,
        expenses,
        color="#0077B6",
        marker="o",
        linewidth=2.5,
        label="Expenses"
    )

    # Net Cash Flow line
    ax.plot(
        labels,
        net_cash_flow,
        color="#E76F6F",
        marker="o",
        linewidth=2.5,
        label="Net Cash Flow"
    )

    # Graph labels
    ax.set_title(
        "Income, Expenses and Net Cash Flow",
        fontsize=14,
        fontweight="bold",
        color="#050A32",
        pad=20
    )

    ax.set_ylabel("Amount (ZAR)")
    ax.set_xlabel("Date")

    # Grid lines
    ax.grid(axis="y", linestyle="-", alpha=0.2)

    # Legend
    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        ncol=1,
        frameon=False
    )

    # Remove unnecessary borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Allow negative cash flow
    ax.axhline(0, color="#CCCCCC", linewidth=1)

    fig.tight_layout()
    fig.subplots_adjust(right=0.75)

    # Save graph in memory
    image = BytesIO()

    fig.savefig(
        image,
        format="png",
        dpi=130,
        bbox_inches="tight"
    )

    # Close this resource when finished.
    plt.close(fig)

    image.seek(0)

    # Send the result back to the code that called this function.
    return image
