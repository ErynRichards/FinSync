# Calculate the progress of one savings goal
def calculate_progress(saved_amount, target_amount):

    if target_amount <= 0:
        return 0

    progress = (saved_amount / target_amount) * 100

    # Do not show progress above 100%
    if progress > 100:
        progress = 100

    return round(progress, 2)


# Calculate the total target amount for all goals
def calculate_total_target(goals):

    total = 0

    for goal in goals:
        total += goal["target_amount"]

    return round(total, 2)


# Calculate the total amount saved
def calculate_total_saved(goals):

    total = 0

    for goal in goals:
        total += goal["saved_amount"]

    return round(total, 2)


# Calculate the average progress of all goals
def calculate_average_progress(goals):

    if len(goals) == 0:
        return 0

    total_progress = 0

    for goal in goals:
        progress = calculate_progress(
            goal["saved_amount"],
            goal["target_amount"]
        )

        total_progress += progress

    average = total_progress / len(goals)

    return round(average, 2)