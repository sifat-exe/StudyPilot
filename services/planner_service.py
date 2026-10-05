"""
planner_service.py
──────────────────
High-level service layer orchestrating the Study Planner workflow.
"""

from datetime import datetime
from data.real_planner_provider import RealPlannerProvider
from services.schedule_generator import ScheduleGenerator


def _parse_study_date(study_date_str: str) -> datetime:
    """
    Parses the study_date string stored in the DB (e.g. '2026-10-07 01:20 PM - 02:20 PM')
    into a datetime for proper chronological sorting.
    Falls back to a far-future sentinel so unparseable entries sort last.
    """
    try:
        # Take only the start portion: "2026-10-07 01:20 PM"
        start_part = study_date_str.split(" - ")[0].strip()
        return datetime.strptime(start_part, "%Y-%m-%d %I:%M %p")
    except Exception:
        return datetime(9999, 12, 31)


class PlannerService:
    """Service layer connecting UI controls with ScheduleGenerator and RealPlannerProvider."""

    def __init__(self):
        self.provider = RealPlannerProvider()
        self.generator = ScheduleGenerator()

    def get_planner_summary(self, user_id):
        """
        Computes summary metrics for the header banner:
          - Total Study Hours & Sessions from saved study_plans.
          - Per-course study hours breakdown.
          - Upcoming CTs and Assignments.
        """
        plans = self.provider.get_study_plans_for_user(user_id)
        # Sort by actual start datetime (DB stores study_date as string; string sort
        # is unreliable on 12-hour AM/PM format, e.g. "01:20 PM" sorts before "08:00 AM")
        plans.sort(key=lambda p: _parse_study_date(p.get("study_date", "")))
        cts = self.provider.get_upcoming_cts(user_id)
        assignments = self.provider.get_upcoming_assignments(user_id)

        total_mins = sum(p["duration_minutes"] for p in plans)
        total_hours = round(total_mins / 60.0, 1)
        total_sessions = len(plans)

        # Course breakdown
        course_hours = {}
        for p in plans:
            c_code = p["course_code"]
            c_hrs = p["duration_minutes"] / 60.0
            course_hours[c_code] = round(course_hours.get(c_code, 0.0) + c_hrs, 1)

        # Format upcoming deadlines list
        upcoming = []
        for c in cts:
            upcoming.append(f"{c['course_code']} {c['title']} — {c['days_remaining']} day(s)")
        for a in assignments:
            if not a.get("completed"):
                upcoming.append(f"{a['course_code']} {a['title']} — {a['days_remaining']} day(s)")

        return {
            "total_hours": total_hours,
            "total_sessions": total_sessions,
            "course_breakdown": course_hours,
            "upcoming_deadlines": upcoming,
            "plans": plans
        }

    def generate_and_save_plan(
        self,
        user_id,
        planning_period: str = "Next 7 days",
        hours_per_day: float = 3.0,
        session_length_mins: int = 60,
        preferred_time: str = "Any time"
    ) -> list:
        """
        Runs the deterministic scheduler and persists the output to study_plans DB table.
        Replaces existing uncompleted plans to avoid duplication.
        """
        courses = self.provider.get_user_courses(user_id)
        if not courses:
            return []

        cts = self.provider.get_upcoming_cts(user_id)
        assignments = self.provider.get_upcoming_assignments(user_id)
        routines = self.provider.get_class_routines(user_id)

        generated_sessions = self.generator.generate(
            courses=courses,
            cts=cts,
            assignments=assignments,
            routines=routines,
            planning_period=planning_period,
            hours_per_day=hours_per_day,
            session_length_mins=session_length_mins,
            preferred_time=preferred_time
        )

        # Clear existing pending plans for user to avoid duplication
        self.provider.clear_pending_study_plans(user_id)

        # Save newly generated sessions to DB
        saved_plans = []
        for s in generated_sessions:
            plan_id = self.provider.save_study_plan(
                course_id=s["course_id"],
                study_date=s["study_date"],
                duration_minutes=s["duration_minutes"],
                task=s["task"]
            )
            s["plan_id"] = plan_id
            saved_plans.append(s)

        return saved_plans

    def update_session_completion(self, plan_id: int, completed: int):
        """Updates plan completion status in the database (0=Pending, 1=Completed, 2=Skipped)."""
        return self.provider.update_plan_status(plan_id, completed)
