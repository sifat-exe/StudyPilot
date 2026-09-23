from database.database import (
    get_class_routines, get_upcoming_assignments, get_upcoming_exams,
    get_completed_assignment_count, get_total_study_time, get_courses
)

class RealDashboardProvider:

    def get_dashboard_summary(self, user_id):
        routines = get_class_routines(user_id) if user_id else []
        assignments = get_upcoming_assignments()
        exams = get_upcoming_exams()
        completed_assignments = get_completed_assignment_count()
        total_study_time = get_total_study_time()
        user_courses = get_courses()

        return {
            "today_progress": {
                "completed": completed_assignments,
                "total": max(completed_assignments + len(assignments), 1),
                "percentage": 50
            },
            "weekly_stats": {
                "hours": round(total_study_time / 60.0, 1),
                "sessions": completed_assignments,
                "streak": 3
            },
            "schedule": [
                {
                    "time": f"{r[3]} - {r[4]}",
                    "course": r[1],
                    "topic": r[2],
                    "status": "Pending"
                }
                for r in routines
            ],
            "deadlines": [
                {
                    "title": a[2],
                    "subtitle": f"Assignment • {a[1]}",
                    "due": a[3],
                    "color": "#e53e3e"
                }
                for a in assignments
            ] + [
                {
                    "title": e[2],
                    "subtitle": f"Class Test • {e[1]}",
                    "due": e[3],
                    "color": "#dd6b20"
                }
                for e in exams
            ],
            "courses": [
                {
                    "name": c[3],
                    "progress": 50,
                    "color": "#3182ce"
                }
                for c in user_courses if c[1] == user_id
            ]
        }