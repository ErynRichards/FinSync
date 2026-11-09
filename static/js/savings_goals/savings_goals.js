"use strict";

// Leave this empty to run the standalone preview. Set it to your team's
// agreed URL (for example, "/api/savings-goals") to use the backend instead.
// GET must return an array of goals, or { goals: [...] }.
const goalsUrl = "/goals";

const demoGoals = [
  { name: "Save for a laptop", description: "For studies and personal use", savedAmount: 4000, targetAmount: 8000, targetDate: "2027-03-31" },
  { name: "Holiday Fund", description: "Save for a trip to Cape Town", savedAmount: 1250, targetAmount: 5000, targetDate: "2027-06-30" },
  { name: "Emergency Fund", description: "Be prepared for unexpected expenses", savedAmount: 2500, targetAmount: 10000, targetDate: "2027-12-31" },
  { name: "Save for a laptop", description: "For studies and personal use", savedAmount: 7500, targetAmount: 7500, targetDate: "2026-10-01" }
];

const goalList = document.querySelector("#goal-list");
const cardTemplate = document.querySelector("#goal-card");
const sortGoals = document.querySelector("#sort-goals");
const goalsMessage = document.querySelector("#goals-message");
let goals = [];

const numberFormat = new Intl.NumberFormat("en-GB", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const dateFormat = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });

function rand(amount) {
  return "R " + numberFormat.format(amount).replace(/,/g, " ");
}

function isComplete(goal) {
  return goal.savedAmount >= goal.targetAmount;
}

function progressOf(goal) {
  // A goal can exceed its target, but the progress bar stops at 100%.
  return Math.min(100, goal.savedAmount / goal.targetAmount * 100);
}

function showMessage(element, message) {
  element.textContent = message;
  element.hidden = message === "";
}

function renderGoals() {
  const direction = sortGoals.value === "latest" ? -1 : 1;
  // Copy the array before sorting. Keep completed goals below active goals,
  // like the design, and sort target dates inside each group.
  const sortedGoals = [...goals].sort((first, second) =>
    Number(isComplete(first)) - Number(isComplete(second)) ||
    direction * first.targetDate.localeCompare(second.targetDate)
  );

  const cards = document.createDocumentFragment();
  for (const goal of sortedGoals) {
    const card = cardTemplate.content.cloneNode(true);
    const description = goal.description || goal.category || "";
    const complete = isComplete(goal);
    const progress = progressOf(goal);
    // An unfinished goal should never display 100% due to rounding.
    const percent = complete ? 100 : Math.min(99, Math.round(progress));

    // textContent displays backend values as text, even if they contain HTML.
    card.querySelector("h2").textContent = goal.name;
    const descriptionElement = card.querySelector(".goal-description");
    descriptionElement.textContent = description;
    descriptionElement.hidden = !description;

    const badge = card.querySelector(".goal-status");
    badge.textContent = complete ? "Completed" : "In Progress";
    badge.classList.toggle("completed", complete);
    card.querySelector(".goal-card").classList.toggle("completed", complete);

    card.querySelector(".goal-percent").textContent = percent + "%";
    const bar = card.querySelector("progress");
    bar.value = progress;
    bar.setAttribute("aria-label", goal.name + " savings progress");
    card.querySelector(".goal-saved").textContent = rand(goal.savedAmount) + " saved";
    card.querySelector(".goal-target").textContent = rand(goal.targetAmount) + " target";

    // The server supplies a date-only string (YYYY-MM-DD). UTC formatting
    // keeps the displayed day the same in different time zones.
    const date = card.querySelector("time");
    date.dateTime = goal.targetDate;
    date.textContent = dateFormat.format(new Date(goal.targetDate));

    // REECE: Display the monthly savings recommendation.
    const monthly = card.querySelector(".goal-monthly-recommendation");

    if (goal.recommendation_status === "completed") {
        monthly.textContent =
            "Goal reached - no further monthly savings needed.";
    }
    else if (goal.recommendation_status === "overdue") {
        monthly.textContent =
            "Target date has passed - no monthly recommendation available.";
    }
    else if (goal.recommended_monthly_saving != null) {
        monthly.textContent =
            "Recommended monthly saving: " +
            rand(Number(goal.recommended_monthly_saving)) +
            " (" + goal.months_remaining + " months remaining)";
    }
    else {
        monthly.textContent = "";
    }

    cards.append(card);
  }

  goalList.replaceChildren(cards);
  document.querySelector("#goal-count").textContent = goals.length;
  document.querySelector("#total-target").textContent = rand(goals.reduce((sum, goal) => sum + goal.targetAmount, 0));
  document.querySelector("#total-saved").textContent = rand(goals.reduce((sum, goal) => sum + goal.savedAmount, 0));
  const totalProgress = goals.reduce((sum, goal) => sum + progressOf(goal), 0);
  document.querySelector("#average-progress").textContent = Math.round(totalProgress / (goals.length || 1)) + "%";
  showMessage(goalsMessage, goals.length ? "" : "No savings goals yet.");
}

// Convert amounts to numbers in case the database sends decimals as strings.
// Update this function if your teammate's API uses different field names.

function readGoal(goal) {
    const savedAmount = Number(goal.saved_amount);
    const targetAmount = Number(goal.target_amount);

    if (!goal.goal_name ||
        !Number.isFinite(savedAmount) ||
        !Number.isFinite(targetAmount) ||
        targetAmount <= 0) {
        throw new Error("Invalid savings goal");
    }

    return {
        ...goal,
        name: goal.goal_name,
        savedAmount: savedAmount,
        targetAmount: targetAmount,
        targetDate: goal.target_date
    };
}


async function loadGoals() {
  if (!goalsUrl) {
    goals = [...demoGoals];
    renderGoals();
    return;
  }

  sortGoals.disabled = true;
  showMessage(goalsMessage, "Loading savings goals…");
  try {
    const response = await fetch(goalsUrl);
    if (!response.ok) throw new Error("Could not load goals");
    const data = await response.json();
    const records = Array.isArray(data) ? data : data.goals;
    goals = records.map(readGoal);
    renderGoals();
    sortGoals.disabled = false;
  } catch {
    showMessage(goalsMessage, "Savings goals could not be loaded. Refresh the page to try again.");
  }
}

sortGoals.addEventListener("change", renderGoals);

loadGoals();

// MISHAYLE: Open Eryn's create goal form.
document.querySelector("#add-goal").addEventListener("click", () => { window.location.href = "/savings-goals/create"; });
