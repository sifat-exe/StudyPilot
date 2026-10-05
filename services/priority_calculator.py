"""
priority_calculator.py
──────────────────────
Deterministic rule-based priority system for StudyPilot Study Planner.

Formula:
  Priority = Deadline Score + Workload Score + Difficulty Score

Note:
  Credit score is excluded as requested.
  Workload Score and Difficulty Score are modular helper functions that safely return 0 for now.
  When difficulty or topic completion is added in the future, only these helper functions need to be updated.
"""


def calculate_deadline_score(days_remaining: int) -> int:
    """
    Calculates deadline score based on days remaining until CT or assignment.
    """
    if days_remaining is None:
        return 0

    if days_remaining <= 1:
        return 50  # Overdue, Today, or Tomorrow
    elif days_remaining == 2:
        return 45
    elif 3 <= days_remaining <= 4:
        return 35
    elif 5 <= days_remaining <= 7:
        return 25
    elif 8 <= days_remaining <= 14:
        return 15
    else:
        return 5


def calculate_workload_score(course: dict) -> int:
    """
    Modular workload score helper.
    Currently returns 0. Ready to incorporate remaining topics from PDF Analysis in the future.
    """
    # Future integration:
    # remaining_topics = course.get("total_topics", 0) - course.get("completed_topics", 0)
    # return max(0, remaining_topics * 5)
    return 0


def calculate_difficulty_score(course: dict) -> int:
    """
    Modular difficulty score helper.
    Currently returns 0. Ready to incorporate future course difficulty column from DB.
    """
    # Future integration:
    # diff_map = {"Easy": 5, "Medium": 15, "Hard": 25}
    # return diff_map.get(course.get("difficulty"), 0)
    return 0


def calculate_priority(task: dict, course: dict) -> int:
    """
    Calculates overall task priority.

    Parameters
    ----------
    task : dict
        Contains 'days_remaining', 'type', etc.
    course : dict
        Course metadata.

    Returns
    -------
    int
        Calculated non-negative priority score.
    """
    days_remaining = task.get("days_remaining") if task else None
    deadline_score = calculate_deadline_score(days_remaining)
    workload_score = calculate_workload_score(course)
    difficulty_score = calculate_difficulty_score(course)

    total_priority = deadline_score + workload_score + difficulty_score
    return max(0, total_priority)
