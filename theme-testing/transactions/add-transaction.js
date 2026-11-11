
// Add Transaction form
(function () {

    // Form elements
    const dialog = document.getElementById("transactionDialog");
    const form = document.getElementById("transactionForm");

    const expenseButton = document.getElementById("expenseButton");
    const incomeButton = document.getElementById("incomeButton");

    const amountInput = document.getElementById("amount");
    const descriptionInput = document.getElementById("description");
    const categoryInput = document.getElementById("category");

    const dayInput = document.getElementById("day");
    const monthInput = document.getElementById("month");
    const yearInput = document.getElementById("year");

    const cancelButton = document.getElementById("cancelButton");
    const message = document.getElementById("message");

    // Default transaction type
    let transactionType = "Expense";

    // Select Income or Expense
    function selectType(type) {

        transactionType = type;

        expenseButton.classList.remove("selected");
        incomeButton.classList.remove("selected");

        expenseButton.setAttribute("aria-pressed", type === "Expense");
        incomeButton.setAttribute("aria-pressed", type === "Income");

        if (type === "Expense") {

            expenseButton.classList.add("selected");
            descriptionInput.placeholder = "E.g. Checkers";

        } else {

            incomeButton.classList.add("selected");
            descriptionInput.placeholder = "E.g. Monthly salary";

        }

        updateCategories();
    }

    // Update form category options
    function updateCategories() {

        categoryInput.innerHTML =
            '<option value="">Select category</option>';

        // Use the same categories as the main filter
        transactionCategories[transactionType].forEach(function (category) {

            const option = document.createElement("option");

            option.value = category;
            option.textContent = category;

            categoryInput.appendChild(option);

        });
    }

    // Expense button
    expenseButton.addEventListener("click", function () {

        selectType("Expense");

    });

    // Income button
    incomeButton.addEventListener("click", function () {

        selectType("Income");

    });

    // Validate date
    function validateDate() {

        const day = Number(dayInput.value);
        const month = Number(monthInput.value);
        const year = Number(yearInput.value);

        if (!day || !month || !year) {
            return false;
        }

        if (
            day < 1 || day > 31 ||
            month < 1 || month > 12 ||
            year < 1900 || year > 9999
        ) {
            return false;
        }

        const date = new Date(year, month - 1, day);

        return (
            date.getFullYear() === year &&
            date.getMonth() === month - 1 &&
            date.getDate() === day
        );
    }

    // Reset form
    function resetForm() {

        form.reset();

        selectType("Expense");

        message.textContent = "";
        message.classList.remove("error");
    }

    // Cancel button
    cancelButton.addEventListener("click", function () {

        dialog.close();

    });

    // Save transaction
    form.addEventListener("submit", function (event) {

        event.preventDefault();

        message.textContent = "";
        message.classList.remove("error");

        const description = descriptionInput.value.trim();
        const amount = Number(amountInput.value);

        // Check description
        if (description === "") {

            message.textContent = "Please enter a description.";
            message.classList.add("error");
            return;
        }

        // Check amount
        if (!Number.isFinite(amount) || amount <= 0) {

            message.textContent = "Please enter a valid amount.";
            message.classList.add("error");
            return;
        }

        // Check date
        if (!validateDate()) {

            message.textContent = "Please enter a valid date.";
            message.classList.add("error");
            return;
        }

        // Format date
        const year = String(Number(yearInput.value)).padStart(4, "0");
        const month = String(Number(monthInput.value)).padStart(2, "0");
        const day = String(Number(dayInput.value)).padStart(2, "0");

        const formattedDate = year + "-" + month + "-" + day;

        // Create transaction
        const transaction = {

            type: transactionType,
            amount: amount.toFixed(2),
            description: description,
            category: categoryInput.value,
            date: formattedDate

        };

        // Add to transaction table
        window.FinSyncTransactions.addToTable(transaction);

        // Close form
        dialog.close();

        // Clear form
        resetForm();

    });

    // Open form
    window.AddTransactionForm = {

        open: function () {

            resetForm();
            dialog.showModal();

        }

    };

    // Load default categories
    selectType("Expense");

})();
