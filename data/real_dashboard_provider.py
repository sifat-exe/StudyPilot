from datetime import datetime, timedelta
from Database.database import (
    get_connection, get_class_routines, get_upcoming_assignments,
    get_upcoming_exams, get_courses
)

class RealDashboardProvider:

    def get_dashboard_summary(self, user_id):
        routines = get_class_routines(user_id) if user_id else []
        assignments = get_upcoming_assignments(user_id)
        exams = get_upcoming_exams(user_id)
        user_courses = get_courses()

        study_plans = []
        pending_plans = []
        if user_id:
            con = get_connection()
            cur = con.cursor()
            cur.execute("""
                SELECT
                    s.study_date,
                    s.duration_minutes,
                    s.completed
                FROM study_plans AS s
                JOIN courses AS c ON s.course_id = c.course_id
                WHERE c.user_id = ?
            """, (user_id,))
            study_plans = cur.fetchall()

            # Query top 4 pending study sessions for Planner card
            cur.execute("""
                SELECT
                    c.course_code,
                    s.task,
                    s.study_date,
                    s.duration_minutes,
                    s.plan_id
                FROM study_plans AS s
                JOIN courses AS c ON s.course_id = c.course_id
                WHERE c.user_id = ? AND s.completed = 0
                ORDER BY s.study_date ASC
                LIMIT 4
            """, (user_id,))
            pending_plans = cur.fetchall()
            con.close()

        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        start_of_week = now.date() - timedelta(days=now.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        total_sessions_in_plan = len(study_plans)
        completed_sessions_in_plan = 0
        weekly_completed_minutes = 0

        for sp in study_plans:
            study_date_raw, duration_mins, completed_val = sp[0], sp[1], sp[2]
            date_part = str(study_date_raw).split(" ")[0].strip()
            sp_date = None
            try:
                sp_date = datetime.strptime(date_part, "%Y-%m-%d").date()
            except Exception:
                pass

            if completed_val == 1:
                completed_sessions_in_plan += 1
                if sp_date and (start_of_week <= sp_date <= end_of_week):
                    weekly_completed_minutes += duration_mins

        progress_percentage = round((completed_sessions_in_plan / total_sessions_in_plan) * 100) if total_sessions_in_plan > 0 else 0
        weekly_hours = round(weekly_completed_minutes / 60.0, 1)

        # Format pending study sessions for Planner card
        planner_items = []
        for p in pending_plans:
            c_code, task_str, study_date_str = p[0], p[1], p[2]
            parts = str(study_date_str).split(" ", 1)
            date_part = parts[0] if parts else ""
            time_part = parts[1] if len(parts) > 1 else str(study_date_str)

            if date_part == today_str:
                display_time = time_part
            else:
                try:
                    dt_obj = datetime.strptime(date_part, "%Y-%m-%d")
                    display_time = f"{dt_obj.strftime('%b %d')} | {time_part}"
                except Exception:
                    display_time = str(study_date_str)

            planner_items.append({
                "time": display_time,
                "course": c_code,
                "topic": task_str,
                "status": "Pending"
            })

        return {
            "today_progress": {
                "completed": completed_sessions_in_plan,
                "total": total_sessions_in_plan,
                "percentage": progress_percentage
            },
            "weekly_stats": {
                "hours": weekly_hours,
                "sessions": completed_sessions_in_plan
            },
            "schedule": planner_items,
            "deadlines": [
                {
                    "type": "Assignment",
                    "course": a[1],
                    "topic": a[2],
                    "date": a[3],
                    "color": "#e53e3e"
                }
                for a in assignments
            ] + [
                {
                    "type": "Class Test",
                    "course": e[1],
                    "topic": e[2],
                    "date": e[3],
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