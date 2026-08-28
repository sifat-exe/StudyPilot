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
            course_name TEXT NOT NULL,
            difficulty TEXT,
            credit_hours INTEGER,
            
            FOREIGN KEY (user_id)
                REFERENCES users(user_id)
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

def add_course(user_id, course_code, course_name, difficulty, credit_hours):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO courses
        (user_id, course_code, course_name, difficulty, credit_hours)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, course_code, course_name, difficulty, credit_hours))

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

def get_courses():
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT course_id, user_id, course_code,
               course_name, difficulty, credit_hours
        FROM courses
    """)

    courses = cur.fetchall()

    con.close()

    return courses

    return users