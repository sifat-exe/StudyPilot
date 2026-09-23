# data/real_profile_provider.py
#
# Uses get_connection() from database.py so profile/courses are stored in
# study_pilot.db. database.py itself is not modified.
#
# Sifat: please move these into Database/database.py later:
#   ensure_student_profile_columns()
#   get_student_profile(user_id)
#   save_student_profile(user_id, name, university, roll, year, semester)
#   get_courses_by_user(user_id)
#   update_course(course_id, course_code, course_title)
# Existing functions already used: add_course, delete_course, get_connection

from database.database import get_connection, add_course, delete_course

PROFILE_COLUMNS = ("university", "roll", "year", "semester")


def _normalize_user_id(user_id):
    if user_id is None or user_id == "":
        return None
    return int(user_id)


def _ensure_student_profile_columns():
    # Will be implemented in database.py as ensure_student_profile_columns()
    con = get_connection()
    try:
        cur = con.cursor()
        existing = {row[1] for row in cur.execute("PRAGMA table_info(users)").fetchall()}
        for column in PROFILE_COLUMNS:
            if column not in existing:
                cur.execute(f"ALTER TABLE users ADD COLUMN {column} TEXT")
        con.commit()
    finally:
        con.close()


class RealProfileProvider:
    """Loads and saves student profile + courses in study_pilot.db."""

    def get_profile(self, user_id):
        # Will be implemented in database.py as get_student_profile(user_id)
        user_id = _normalize_user_id(user_id)
        empty = {
            "name": "",
            "university": "",
            "roll": "",
            "year": "1st",
            "semester": "Odd",
            "courses": [],
        }
        if user_id is None:
            return empty

        _ensure_student_profile_columns()
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                """
                SELECT name, university, roll, year, semester
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            )
            row = cur.fetchone()
        finally:
            con.close()

        if not row:
            empty["courses"] = self.get_courses(user_id)
            return empty

        return {
            "name": row[0] or "",
            "university": row[1] or "",
            "roll": row[2] or "",
            "year": row[3] or "1st",
            "semester": row[4] or "Odd",
            "courses": self.get_courses(user_id),
        }

    def save_profile(self, user_id, profile):
        # Will be implemented in database.py as save_student_profile(...)
        user_id = _normalize_user_id(user_id)
        if user_id is None:
            raise ValueError("Cannot save profile because no logged-in user_id was found.")

        _ensure_student_profile_columns()
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                """
                UPDATE users
                SET name = ?, university = ?, roll = ?, year = ?, semester = ?
                WHERE user_id = ?
                """,
                (
                    (profile.get("name") or "").strip(),
                    (profile.get("university") or "").strip(),
                    (profile.get("roll") or "").strip(),
                    profile.get("year") or "1st",
                    profile.get("semester") or "Odd",
                    user_id,
                ),
            )
            if cur.rowcount == 0:
                raise ValueError("No matching user row was updated in the database.")
            con.commit()
        finally:
            con.close()

        self._save_courses(user_id, profile.get("courses", []))
        return True

    def get_courses(self, user_id):
        # Will be implemented in database.py as get_courses_by_user(user_id)
        user_id = _normalize_user_id(user_id)
        if user_id is None:
            return []

        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                """
                SELECT course_id, user_id, course_code, course_title
                FROM courses
                WHERE user_id = ?
                ORDER BY course_id
                """,
                (user_id,),
            )
            rows = cur.fetchall()
        finally:
            con.close()

        return [
            {
                "course_id": row[0],
                "course_code": row[2] or "",
                "course_title": row[3] or "",
            }
            for row in rows
        ]

    def _save_courses(self, user_id, courses):
        existing = self.get_courses(user_id)
        existing_ids = {c["course_id"] for c in existing}

        kept_ids = set()
        for course in courses:
            code = (course.get("course_code") or "").strip()
            title = (course.get("course_title") or "").strip()
            course_id = course.get("course_id")
            if course_id is not None:
                course_id = int(course_id)

            if not code and not title:
                continue

            if course_id in existing_ids:
                self._update_course(course_id, code, title)
                kept_ids.add(course_id)
            else:
                # Existing database.py function
                add_course(user_id, code, title, None, None)

        for course in existing:
            course_id = course["course_id"]
            if course_id not in kept_ids:
                # Existing database.py function
                delete_course(course_id)

    def _update_course(self, course_id, course_code, course_title):
        # Will be implemented in database.py as update_course(...)
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                """
                UPDATE courses
                SET course_code = ?, course_title = ?
                WHERE course_id = ?
                """,
                (course_code, course_title, course_id),
            )
            con.commit()
        finally:
            con.close()
