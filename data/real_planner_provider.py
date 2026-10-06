from datetime import datetime, timedelta
from Database.database import (
    get_connection, get_courses, get_assignments_with_courses,
    get_exams_with_courses, get_class_routines
)


class RealPlannerProvider:
    """Interacts with Database.py tables to fetch data and persist generated study plans."""

    def get_user_courses(self, user_id):
        """Retrieves courses for the specified user."""
        all_courses = get_courses()
        user_courses = []
        for c in all_courses:
            # c = (course_id, user_id, course_code, course_title, difficulty, credit_hours)
            if c[1] == user_id:
                user_courses.append({
                    "course_id": c[0],
                    "user_id": c[1],
                    "course_code": c[2],
                    "course_title": c[3],
                    "difficulty": c[4],
                    "credit_hours": c[5]
                })
        return user_courses

    def get_upcoming_cts(self, user_id):
        """Retrieves upcoming class tests / exams for user's courses."""
        exams = get_exams_with_courses(user_id)
        # returns (course_code, exam_title, exam_date, exam_id)
        results = []
        now = datetime.now()
        for e in exams:
            course_code, exam_title, exam_date_str, exam_id = e[0], e[1], e[2], e[3]
            
            # Parse exam date
            days_remaining = 999
            try:
                date_part = exam_date_str.split(" ")[0]
                dt = datetime.strptime(date_part, "%Y-%m-%d")
                delta = (dt.date() - now.date()).days
                days_remaining = delta
            except Exception:
                days_remaining = 7

            results.append({
                "type": "CT",
                "id": exam_id,
                "course_code": course_code,
                "title": exam_title,
                "date_str": exam_date_str,
                "days_remaining": days_remaining
            })
        return results

    def get_upcoming_assignments(self, user_id):
        """Retrieves upcoming assignments for user's courses."""
        assignments = get_assignments_with_courses(user_id)
        # returns (course_code, title, deadline, completed, assignment_id)
        results = []
        now = datetime.now()
        for a in assignments:
            course_code, title, deadline_str, completed, assignment_id = a[0], a[1], a[2], a[3], a[4]
            
            days_remaining = 999
            try:
                date_part = deadline_str.split(" ")[0]
                dt = datetime.strptime(date_part, "%Y-%m-%d")
                delta = (dt.date() - now.date()).days
                days_remaining = delta
            except Exception:
                days_remaining = 7

            results.append({
                "type": "Assignment",
                "id": assignment_id,
                "course_code": course_code,
                "title": title,
                "date_str": deadline_str,
                "days_remaining": days_remaining,
                "completed": bool(completed)
            })
        return results

    def get_class_routines(self, user_id):
        """Retrieves class routine slots for user."""
        routines = get_class_routines(user_id)
        # returns (routine_id, course_title, day_of_week, start_time, end_time)
        return [
            {
                "routine_id": r[0],
                "course_title": r[1],
                "day_of_week": r[2],
                "start_time": r[3],
                "end_time": r[4]
            }
            for r in routines
        ]

    def get_study_plans_for_user(self, user_id):
        """Retrieves generated study plans for the user's courses."""
        con = get_connection()
        cur = con.cursor()
        cur.execute("""
            SELECT
                s.plan_id,
                s.course_id,
                c.course_code,
                c.course_title,
                s.study_date,
                s.duration_minutes,
                s.task,
                s.completed
            FROM study_plans AS s
            JOIN courses AS c ON s.course_id = c.course_id
            WHERE c.user_id = ?
            ORDER BY s.study_date ASC
        """, (user_id,))
        rows = cur.fetchall()
        con.close()

        plans = []
        for r in rows:
            plans.append({
                "plan_id": r[0],
                "course_id": r[1],
                "course_code": r[2],
                "course_title": r[3],
                "study_date": r[4],
                "duration_minutes": r[5],
                "task": r[6],
                "completed": r[7]
            })
        return plans

    def clear_pending_study_plans(self, user_id, start_date_str=None, end_date_str=None):
        """Clears pending (uncompleted) generated study plans for user's courses in the planning window."""
        con = get_connection()
        cur = con.cursor()
        cur.execute("""
            DELETE FROM study_plans
            WHERE completed = 0 AND course_id IN (
                SELECT course_id FROM courses WHERE user_id = ?
            )
        """, (user_id,))
        con.commit()
        con.close()

    def save_study_plan(self, course_id, study_date, duration_minutes, task):
        """Saves a generated study plan to database."""
        con = get_connection()
        cur = con.cursor()
        cur.execute("""
            INSERT INTO study_plans (course_id, study_date, duration_minutes, task, completed)
            VALUES (?, ?, ?, ?, 0)
        """, (course_id, study_date, duration_minutes, task))
        plan_id = cur.lastrowid
        con.commit()
        con.close()
        return plan_id

    def update_plan_status(self, plan_id, completed: int):
        """Updates plan completion status (0=Pending, 1=Completed, 2=Skipped)."""
        con = get_connection()
        cur = con.cursor()
        cur.execute("""
            UPDATE study_plans
            SET completed = ?
            WHERE plan_id = ?
        """, (completed, plan_id))
        con.commit()
        con.close()
        return True
