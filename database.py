import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "careerpath.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            education_level TEXT NOT NULL,
            field_of_study TEXT NOT NULL,
            interests TEXT NOT NULL,
            skills TEXT NOT NULL,
            career_goals TEXT NOT NULL,
            work_style TEXT NOT NULL,
            experience_level TEXT NOT NULL,
            resume_scanned INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            student_id INTEGER NOT NULL UNIQUE,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS careers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            avg_salary TEXT NOT NULL,
            outlook TEXT NOT NULL,
            education_fit TEXT NOT NULL,
            keywords TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS career_skills (
            career_id INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,
            importance TEXT NOT NULL,
            PRIMARY KEY (career_id, skill_id),
            FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS roadmap_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            career_id INTEGER NOT NULL,
            month_number INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            resources TEXT NOT NULL,
            FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            career_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            description TEXT NOT NULL,
            skills_used TEXT NOT NULL,
            outcome TEXT NOT NULL,
            FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS interview_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            career_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            tip TEXT NOT NULL,
            category TEXT NOT NULL,
            FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS resume_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            section TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            career_id INTEGER NOT NULL,
            match_score INTEGER NOT NULL,
            reasons TEXT NOT NULL,
            UNIQUE (student_id, career_id),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS student_roadmap (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            step_id INTEGER NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            UNIQUE (student_id, step_id),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (step_id) REFERENCES roadmap_steps(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS student_resume (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            UNIQUE (student_id, item_id),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES resume_items(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS student_resume_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            color_theme TEXT NOT NULL DEFAULT 'warm',
            file_size INTEGER NOT NULL DEFAULT 0,
            uploaded_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()
    _migrate_students_resume_scanned(conn)
    conn.commit()
    conn.close()


def _migrate_students_resume_scanned(conn):
    cols = {row[1] for row in conn.execute("PRAGMA table_info(students)").fetchall()}
    if "resume_scanned" not in cols:
        conn.execute(
            "ALTER TABLE students ADD COLUMN resume_scanned INTEGER NOT NULL DEFAULT 0"
        )
    conn.execute(
        """
        UPDATE students SET resume_scanned = 1
        WHERE id IN (SELECT DISTINCT student_id FROM recommendations)
          AND COALESCE(resume_scanned, 0) = 0
        """
    )


def row_to_dict(row):
    return dict(row) if row else None


def rows_to_dicts(rows):
    return [dict(row) for row in rows]
