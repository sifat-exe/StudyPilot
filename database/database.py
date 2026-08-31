import sqlite3


def get_connection():
    return sqlite3.connect("study_pilot.db")


def create_tables():
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_code TEXT NOT NULL,
            course_title TEXT NOT NULL,
            difficulty TEXT,
            credit_hours INTEGER,
            
            FOREIGN KEY (user_id)
                REFERENCES users(user_id)
        )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        deadline TEXT,
        completed INTEGER DEFAULT 0,

        FOREIGN KEY (course_id)
            REFERENCES courses(course_id)
        )
    """)

    cur.execute("""
    
        CREATE TABLE IF NOT EXISTS exams(
            exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            exam_title TEXT NOT NULL,
            exam_date TEXT NOT NULL,
            
            FOREIGN KEY (course_id)
                REFERENCES courses(course_id)
        )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS study_sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        session_date TEXT NOT NULL,
        duration_minutes INTEGER NOT NULL,
        completed INTEGER DEFAULT 0,

        FOREIGN KEY (course_id)
            REFERENCES courses(course_id)
    )
""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS study_plans (
        plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        study_date TEXT NOT NULL,
        duration_minutes INTEGER NOT NULL,
        task TEXT NOT NULL,
        completed INTEGER DEFAULT 0,

        FOREIGN KEY (course_id)
            REFERENCES courses(course_id)
        )
    """)

    con.commit()
    con.close()


def add_user(name, email):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO users (name, email)
        VALUES (?, ?)
    """, (name, email))

    con.commit()
    con.close()

def add_course(user_id, course_code, course_title, difficulty, credit_hours):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO courses
        (user_id, course_code, course_title, difficulty, credit_hours)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, course_code, course_title, difficulty, credit_hours))

    con.commit()
    con.close()
    
def add_assignment(course_id, title, deadline):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO assignments
        (course_id, title, deadline)
        VALUES (?, ?, ?)
    """, (course_id, title, deadline))

    con.commit()
    con.close()

def add_exam(course_id, exam_title, exam_date):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO exams
        (course_id, exam_title, exam_date)
        VALUES (?, ?, ?)
    """, (course_id, exam_title, exam_date))

    con.commit()
    con.close()

def add_study_session(course_id, session_date, duration_minutes):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO study_sessions
        (course_id, session_date, duration_minutes)
        VALUES (?, ?, ?)
    """, (course_id, session_date, duration_minutes))

    con.commit()
    con.close()

def add_study_plan(course_id,study_date,duration_minutes,task):
    con = get_connection()
    cur = con.cursor()
    
    cur.execute("""
        INSERT INTO study_plans
            (course_id,study_date,duration_minutes,task)
        VALUES 
            (?,?,?,?)
    """,(course_id, study_date, duration_minutes, task))
    
    con.commit()
    con.close()

def complete_assignment(assignment_id):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        UPDATE assignments
        SET completed = 1
        WHERE assignment_id = ?
    """, (assignment_id,))

    con.commit()
    con.close()

def complete_study_session(session_id):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        UPDATE study_sessions
        SET completed = 1
        WHERE session_id = ?
    """, (session_id,))

    con.commit()
    con.close()

def complete_study_plan(plan_id):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        UPDATE study_plans
        SET completed = 1
        WHERE plan_id = ?
    """, (plan_id,))

    con.commit()
    con.close()

def delete_course(course_id):
    con=get_connection()
    cur=con.cursor()

    cur.execute("""
        DELETE FROM courses 
        WHERE course_id=?
    """,(course_id,))

    con.commit()
    con.close()
    
def get_users():
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT user_id, name, email
        FROM users
    """)

    users = cur.fetchall()
    con.close()

    return users

def get_courses():
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT course_id, user_id, course_code,
               course_title, difficulty, credit_hours
        FROM courses
    """)

    courses = cur.fetchall()

    con.close()

    return courses

def get_assignments():
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT
            assignment_id,
            course_id,
            title,
            deadline,
            completed
        FROM assignments
    """)

    assignments = cur.fetchall()

    con.close()

    return assignments

def get_exams():
    con=get_connection()
    cur=con.cursor()

    cur.execute("""
        SELECT exam_id,course_id,exam_title,exam_date
        FROM exams 
    """)

    exams=cur.fetchall()
    con.close()
    return exams

def get_assignments_with_courses():
    
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT
            courses.course_title,
            assignments.title,
            assignments.deadline,
            assignments.completed
        FROM assignments
        JOIN courses 
            ON assignments.course_id=courses.course_id
    """)

    assignments = cur.fetchall()

    con.close()

    return assignments

def get_exams_with_courses():
    con = get_connection()
    cur = con.cursor()
    
    cur.execute("""
        SELECT 
            courses.course_title,
            exams.exam_title,
            exams.exam_date
        FROM exams 
        JOIN courses 
        ON exams.course_id=courses.course_id
    """)

    exams=cur.fetchall()
    con.close()

    return exams

def get_study_sessions():
    con = get_connection()
    cur = con.cursor()
    
    cur.execute("""
        SELECT session_id,course_id,session_date, duration_minutes, completed
        FROM study_sessions
    """)

    sessions=cur.fetchall()
    con.close()
    return sessions

def get_total_study_time():
    con = get_connection()
    cur = con.cursor()
    
    cur.execute("""
        SELECT COALESCE(SUM(duration_minutes), 0)
        FROM study_sessions
        WHERE completed = 1 
    """)

    total_minutes=cur.fetchone()[0]

    con.close()

    return total_minutes

def get_study_plans():
    con = get_connection()
    cur = con.cursor()
    
    cur.execute("""
        SELECT plan_id, course_id, study_date, duration_minutes, task, completed
        FROM study_plans
        ORDER BY study_date 
    """)
    plans=cur.fetchall()
    con.close()
    return plans

def get_study_plans_with_courses():
    con = get_connection()
    cur = con.cursor()
        
    cur.execute("""
        SELECT c.course_title, s.study_date, s.duration_minutes, s.task, s.completed
        FROM study_plans AS s
        JOIN courses AS c
            ON s.course_id=c.course_id
        ORDER BY s.study_date 
        """)
    plans=cur.fetchall()
    con.close()
    return plans

def get_course_study_time(course_id):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT COALESCE(SUM(duration_minutes), 0)
        FROM study_sessions
        WHERE course_id = ?
        AND completed = 1
    """, (course_id,))

    total_minutes = cur.fetchone()[0]

    con.close()

    return total_minutes

def get_completed_assignment_count():
    con = get_connection()
    cur = con.cursor()
    
    cur.execute("""
        SELECT COUNT(*)
        FROM assignments
        WHERE completed = 1
    """)

    count=cur.fetchone()[0]

    con.close() 

    return count

def  get_completed_study_plan_count():
    con = get_connection()
    cur = con.cursor()
    
    cur.execute("""
        SELECT COUNT(*)
        FROM study_plans
        WHERE completed = 1
    """)

    count = cur.fetchone()[0]
   
    con.close()

    return count