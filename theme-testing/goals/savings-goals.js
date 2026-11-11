
"use strict";

// Flask API configuration.
// Leave empty for demo testing.
// Mishayle will set this to the agreed Flask API path.
const API_BASE = "";

// Browser-only demo storage.
const STORAGE_KEY = "finsync_demo_savings_goals_v1";

// Sample savings goals for testing.
const INITIAL_DEMO_GOALS = [
  {
    id: "demo-1",
    name: "Save for a laptop",
    description: "For studies and personal use",
    savedAmount: 4000,
    targetAmount: 8000,
    targetDate: "2027-03-31"
  },
  {
    id: "demo-2",
    name: "Holiday Fund",
    description: "Save for a trip to Cape Town",
    savedAmount: 1250,
    targetAmount: 5000,
    targetDate: "2027-06-30"
  },
  {
    id: "demo-3",
    name: "Emergency Fund",
    description: "Be prepared for unexpected expenses",
    savedAmount: 2500,
    targetAmount: 10000,
    targetDate: "2027-12-31"
  }
];

// Page elements.
const goalList = document.querySelector("#goal-list");
const cardTemplate = document.querySelector("#goal-card");
const sortGoals = document.querySelector("#sort-goals");
const goalsMessage = document.querySelector("#goals-message");

const dialog = document.querySelector("#contribution-dialog");
const form = document.querySelector("#contribution-form");
const amountInput = document.querySelector("#contribution-amount");
const errorText = document.querySelector("#contribution-error");
const submitButton = document.querySelector("#save-contribution");

let goals = [];
let selectedGoalId = null;

// Currency and date formatting.
const moneyFormatter = new Intl.NumberFormat("en-ZA", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});

const dateFormatter = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: "UTC"
});

const rand = value => "R " + moneyFormatter.format(value);

const cents = value => Math.round(Number(value) * 100);

// Check whether the savings target is reached.
const isComplete = goal =>
  cents(goal.savedAmount) >= cents(goal.targetAmount);

// Calculate progress percentage.
const progressOf = goal =>
  Math.min(100, (goal.savedAmount / goal.targetAmount) * 100);

// Convert backend goal data to frontend format.
function readGoal(item) {
  const goal = {
    id: item.id,
    name: item.name ?? item.goal_name,
    description: item.description ?? item.category ?? "",
    savedAmount: Number(
      item.savedAmount ?? item.saved_amount ?? 0
    ),
    targetAmount: Number(
      item.targetAmount ?? item.target_amount
    ),
    targetDate: item.targetDate ?? item.target_date
  };

  if (
    goal.id === undefined ||
    goal.id === null ||
    !String(goal.id) ||
    typeof goal.name !== "string" ||
    !goal.name.trim() ||
    !Number.isFinite(goal.savedAmount) ||
    goal.savedAmount < 0 ||
    !Number.isFinite(goal.targetAmount) ||
    goal.targetAmount <= 0 ||
    typeof goal.targetDate !== "string" ||
    !/^\d{4}-\d{2}-\d{2}$/.test(goal.targetDate) ||
    Number.isNaN(Date.parse(goal.targetDate))
  ) {
    throw new Error("Invalid goal data returned by server");
  }

  return goal;
}

// Read demonstration goals from browser storage.
function readDemo() {
  const stored = localStorage.getItem(STORAGE_KEY);

  if (!stored) {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(INITIAL_DEMO_GOALS)
    );

    return INITIAL_DEMO_GOALS.map(readGoal);
  }

  return JSON.parse(stored).map(readGoal);
}

// Display all savings goals.
function renderGoals() {
  const direction = sortGoals.value === "latest" ? -1 : 1;

  const ordered = [...goals].sort((a, b) =>
    Number(isComplete(a)) - Number(isComplete(b)) ||
    direction * a.targetDate.localeCompare(b.targetDate)
  );

  const cards = document.createDocumentFragment();

  for (const goal of ordered) {
    const card = cardTemplate.content.cloneNode(true);

    const completed = isComplete(goal);
    const progress = progressOf(goal);

    // Goal name.
    card.querySelector("h2").textContent = goal.name;

    // Goal description.
    const description = card.querySelector(
      ".goal-description"
    );

    description.textContent = goal.description;
    description.hidden = !goal.description;

    // Goal status.
    const status = card.querySelector(".goal-status");

    status.textContent = completed
      ? "Completed"
      : "In Progress";

    status.classList.toggle("completed", completed);

    card.querySelector(".goal-card")
      .classList.toggle("completed", completed);

    // Progress percentage.
    card.querySelector(".goal-percent").textContent =
      completed
        ? "100%"
        : Math.min(99, Math.round(progress)) + "%";

    // Progress bar.
    const bar = card.querySelector("progress");

    bar.value = progress;

    bar.setAttribute(
      "aria-label",
      goal.name + " savings progress"
    );

    // Savings amounts.
    card.querySelector(".goal-saved").textContent =
      rand(goal.savedAmount) + " saved";

    card.querySelector(".goal-target").textContent =
      rand(goal.targetAmount) + " target";

    // Target date.
    const time = card.querySelector("time");

    time.dateTime = goal.targetDate;

    time.textContent = dateFormatter.format(
      new Date(goal.targetDate + "T00:00:00Z")
    );

    // Eryn: Add Savings button.
    const button = card.querySelector(".contribute-btn");

    button.disabled = completed;
    button.hidden = completed;

    button.addEventListener("click", () => {
      openContribution(goal.id);
    });

    cards.append(card);
  }

  goalList.replaceChildren(cards);

  // Update total goals.
  document.querySelector("#goal-count").textContent =
    goals.length;

  // Update total target amount.
  document.querySelector("#total-target").textContent =
    rand(
      goals.reduce(
        (sum, goal) => sum + goal.targetAmount,
        0
      )
    );

  // Update total savings.
  document.querySelector("#total-saved").textContent =
    rand(
      goals.reduce(
        (sum, goal) => sum + goal.savedAmount,
        0
      )
    );

  // Update average progress.
  const totalProgress = goals.reduce(
    (sum, goal) => sum + progressOf(goal),
    0
  );

  document.querySelector("#average-progress").textContent =
    Math.round(totalProgress / (goals.length || 1)) + "%";

  goalsMessage.hidden = goals.length > 0;

  goalsMessage.textContent =
    goals.length ? "" : "No savings goals yet.";
}

// Load savings goals.
async function loadGoals() {
  try {
    if (!API_BASE) {
      // Demonstration mode.
      goals = readDemo();
    } else {
      // Fetch real goals from Flask.
      const response = await fetch(
        `${API_BASE}/savings-goals`,
        { credentials: "same-origin" }
      );

      if (!response.ok) {
        throw new Error("Could not load savings goals");
      }

      const data = await response.json();

      const items = Array.isArray(data)
        ? data
        : data.goals;

      if (!Array.isArray(items)) {
        throw new Error(
          "Unexpected savings goals response"
        );
      }

      goals = items.map(readGoal);
    }

    renderGoals();

  } catch (error) {
    goalsMessage.hidden = false;
    goalsMessage.textContent = error.message;
  }
}

// Open the Add Savings popup.
function openContribution(goalId) {
  const goal = goals.find(
    goal => String(goal.id) === String(goalId)
  );

  if (!goal || isComplete(goal)) {
    return;
  }

  selectedGoalId = goal.id;

  form.reset();
  errorText.textContent = "";

  document.querySelector(
    "#contribution-goal-name"
  ).textContent =
    `${goal.name} — ${rand(goal.savedAmount)} ` +
    `of ${rand(goal.targetAmount)} saved`;

  dialog.showModal();
  amountInput.focus();
}

// Handle adding money to a savings goal.
form.addEventListener("submit", async event => {
  event.preventDefault();

  const goal = goals.find(
    goal => String(goal.id) === String(selectedGoalId)
  );

  if (!goal) {
    return;
  }

  const amount = Number(amountInput.value);
  const amountCents = cents(amount);

  const remainingCents =
    cents(goal.targetAmount) -
    cents(goal.savedAmount);

  // Validate the contribution amount.
  if (
    !Number.isFinite(amount) ||
    !Number.isSafeInteger(amountCents) ||
    amountCents <= 0 ||
    amountCents > remainingCents ||
    Math.abs(amount * 100 - amountCents) > 0.000001
  ) {
    errorText.textContent =
      `Enter a positive amount up to ` +
      `${rand(remainingCents / 100)} ` +
      `(two decimal places).`;

    return;
  }

  submitButton.disabled = true;
  errorText.textContent = "";

  try {
    if (API_BASE) {
      // Backend integration.
      // Mishayle must validate:
      // 1. Goal ownership
      // 2. Available balance
      // 3. Remaining goal amount
      // 4. Atomic database updates

      const response = await fetch(
        `${API_BASE}/savings-goals/` +
        `${encodeURIComponent(goal.id)}/contributions`,
        {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            amount: amountCents / 100
          })
        }
      );

      if (!response.ok) {
        const details = await response.json()
          .catch(() => ({}));

        throw new Error(
          details.error || "Could not add savings"
        );
      }

      // Reload from the database after saving.
      await loadGoals();

    } else {
      // Demonstration mode only.
      // No real account balance is deducted.

      goal.savedAmount =
        (cents(goal.savedAmount) + amountCents) / 100;

      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(goals)
      );

      renderGoals();
    }

    dialog.close();

  } catch (error) {
    errorText.textContent = error.message;

  } finally {
    submitButton.disabled = false;
  }
});

// Cancel adding savings.
document.querySelector(
  "#cancel-contribution"
).addEventListener("click", () => {
  dialog.close();
});

// Clear selected goal when popup closes.
dialog.addEventListener("close", () => {
  selectedGoalId = null;
});

// Sort savings goals.
sortGoals.addEventListener("change", renderGoals);

// Navigate to Create Savings Goal.
document.querySelector("#add-goal")
  .addEventListener("click", () => {
    window.location.href = "createSavingsGoal.html";
  });

// Load goals when page opens.
loadGoals();
