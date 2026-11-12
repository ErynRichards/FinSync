# Calculate the progress of one savings goal
def calculate_progress(saved_amount, target_amount):

    # Check the condition before continuing.
    if target_amount <= 0:
        # Send the result back to the code that called this function.
        return 0

    progress = (saved_amount / target_amount) * 100

    # Do not show progress above 100%
    if progress > 100:
        progress = 100

    # Send the result back to the code that called this function.
    return round(progress, 2)


# Calculate the total target amount for all goals
def calculate_total_target(goals):

    # Save an amount for a calculation or database update.
    total = 0

    # Go through each item one at a time.
    for goal in goals:
        total += goal["target_amount"]

    # Send the result back to the code that called this function.
    return round(total, 2)


# Calculate the total amount saved
def calculate_total_saved(goals):

    # Save an amount for a calculation or database update.
    total = 0

    # Go through each item one at a time.
    for goal in goals:
        total += goal["saved_amount"]

    # Send the result back to the code that called this function.
    return round(total, 2)


# Calculate the average progress of all goals
def calculate_average_progress(goals):

    # Check the condition before continuing.
    if len(goals) == 0:
        # Send the result back to the code that called this function.
        return 0

    # Save an amount for a calculation or database update.
    total_progress = 0

    # Go through each item one at a time.
    for goal in goals:
        progress = calculate_progress(
            goal["saved_amount"],
            goal["target_amount"]
        )

        total_progress += progress

    average = total_progress / len(goals)

    # Send the result back to the code that called this function.
    return round(average, 2)