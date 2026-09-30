import json
import os
from collections import defaultdict
from pathlib import Path
from uuid import uuid4

from flask import Flask, g, jsonify, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from career_service import rebuild_student_plan
from database import get_connection, init_db, row_to_dict, rows_to_dicts
from resume_parser import parse_resume
from seed import seed

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "careerpath-dev-secret-change-in-production")

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads" / "resumes"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}


def allowed_resume_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_RESUME_EXTENSIONS


def db():
    if "db" not in g:
        g.db = get_connection()
    return g.db


@app.teardown_appcontext
def close_db(_error):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def get_student_or_404(student_id):
    row = db().execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if not row:
        return None
    return dict(row)


def session_student_id():
    return session.get("student_id")


def require_session_student():
    student_id = session_student_id()
    if not student_id:
        return None, (jsonify({"error": "Login required"}), 401)
    if not get_student_or_404(student_id):
        session.clear()
        return None, (jsonify({"error": "Login required"}), 401)
    return student_id, None


def assert_student_access(student_id):
    if session_student_id() != student_id:
        return jsonify({"error": "Forbidden"}), 403
    return None


def create_student_for_user(conn, name, email):
    cur = conn.execute(
        """
        INSERT INTO students (
            name, email, education_level, field_of_study, interests,
            skills, career_goals, work_style, experience_level, resume_scanned
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (
            name.strip(),
            email.strip().lower(),
            "Not specified",
            "General",
            "",
            "",
            "Define career direction from my resume",
            "builder",
            "beginner",
        ),
    )
    return cur.lastrowid


def career_skills_map(conn):
    rows = conn.execute(
        """
        SELECT cs.career_id, s.id, s.name, s.category, cs.importance
        FROM career_skills cs
        JOIN skills s ON s.id = cs.skill_id
        ORDER BY cs.importance, s.name
        """
    ).fetchall()
    mapping = defaultdict(list)
    for row in rows:
        mapping[row["career_id"]].append(
            {
                "id": row["id"],
                "name": row["name"],
                "category": row["category"],
                "importance": row["importance"],
            }
        )
    return mapping


def primary_career_id(student_id):
    row = (
        db()
        .execute(
            """
            SELECT career_id FROM recommendations
            WHERE student_id = ?
            ORDER BY match_score DESC, id ASC
            LIMIT 1
            """,
            (student_id,),
        )
        .fetchone()
    )
    return row["career_id"] if row else None


@app.route("/")
def landing():
    if session_student_id():
        student = get_student_or_404(session_student_id())
        if student and not student.get("resume_scanned"):
            return redirect(url_for("upload_page"))
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/login")
def login_page():
    if session_student_id():
        return redirect(url_for("upload_page"))
    return render_template("login.html")


@app.route("/signup")
def signup_page():
    if session_student_id():
        return redirect(url_for("upload_page"))
    return render_template("signup.html")


@app.route("/upload")
def upload_page():
    if not session_student_id():
        return redirect(url_for("login_page"))
    return render_template("upload.html")


@app.route("/assess")
def assess():
    return redirect(url_for("upload_page"))


@app.route("/results")
def results():
    return render_template("results.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/roadmap")
def roadmap_page():
    return render_template("roadmap.html")


@app.route("/resume")
def resume_page():
    return render_template("resume.html")


@app.route("/interview")
def interview_page():
    return render_template("interview.html")


@app.post("/api/auth/register")
def api_register():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    if not name or not email or len(password) < 6:
        return jsonify({"error": "Name, email, and password (6+ characters) are required."}), 400

    conn = db()
    if conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
        return jsonify({"error": "An account with this email already exists."}), 409

    existing_student = conn.execute("SELECT id FROM students WHERE email = ?", (email,)).fetchone()
    if existing_student:
        student_id = existing_student["id"]
        conn.execute("UPDATE students SET name = ? WHERE id = ?", (name, student_id))
    else:
        student_id = create_student_for_user(conn, name, email)
    conn.execute(
        "INSERT INTO users (email, password_hash, name, student_id) VALUES (?, ?, ?, ?)",
        (email, generate_password_hash(password), name, student_id),
    )
    conn.commit()
    session.clear()
    session["student_id"] = student_id
    session["user_name"] = name
    return jsonify(
        {
            "student_id": student_id,
            "name": name,
            "email": email,
            "resume_scanned": 0,
        }
    )


@app.post("/api/auth/login")
def api_login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    row = db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    student = get_student_or_404(row["student_id"])
    session.clear()
    session["student_id"] = row["student_id"]
    session["user_name"] = row["name"]
    return jsonify(
        {
            "student_id": row["student_id"],
            "name": row["name"],
            "email": row["email"],
            "resume_scanned": student.get("resume_scanned", 0) if student else 0,
        }
    )


@app.post("/api/auth/logout")
def api_logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/auth/me")
def api_me():
    student_id, err = require_session_student()
    if err:
        return err
    student = get_student_or_404(student_id)
    user = db().execute("SELECT name, email FROM users WHERE student_id = ?", (student_id,)).fetchone()
    return jsonify(
        {
            "student_id": student_id,
            "name": user["name"] if user else student["name"],
            "email": user["email"] if user else student["email"],
            "resume_scanned": student.get("resume_scanned", 0),
            "student": student,
        }
    )


@app.get("/api/skills")
def api_skills():
    rows = db().execute("SELECT id, name, category FROM skills ORDER BY name").fetchall()
    return jsonify(rows_to_dicts(rows))


@app.get("/api/students/<int:student_id>")
def api_student(student_id):
    denied = assert_student_access(student_id)
    if denied:
        return denied
    student = get_student_or_404(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student)


@app.post("/api/assess")
def api_assess():
    payload = request.get_json(silent=True) or {}
    required = [
        "name",
        "email",
        "education_level",
        "field_of_study",
        "interests",
        "skills",
        "career_goals",
        "work_style",
        "experience_level",
    ]
    missing = [field for field in required if not str(payload.get(field, "")).strip()]
    if missing:
        return jsonify({"error": "Missing fields", "fields": missing}), 400

    interests = payload["interests"]
    skills = payload["skills"]
    if isinstance(interests, list):
        interests = ", ".join(interests)
    if isinstance(skills, list):
        skills = ", ".join(skills)

    conn = db()
    existing = conn.execute(
        "SELECT id FROM students WHERE email = ?", (payload["email"].strip().lower(),)
    ).fetchone()

    values = (
        payload["name"].strip(),
        payload["email"].strip().lower(),
        payload["education_level"].strip(),
        payload["field_of_study"].strip(),
        interests,
        skills,
        payload["career_goals"].strip(),
        payload["work_style"].strip(),
        payload["experience_level"].strip(),
    )

    if existing:
        student_id = existing["id"]
        conn.execute(
            """
            UPDATE students
            SET name=?, email=?, education_level=?, field_of_study=?, interests=?,
                skills=?, career_goals=?, work_style=?, experience_level=?
            WHERE id=?
            """,
            (*values, student_id),
        )
        conn.execute("DELETE FROM recommendations WHERE student_id = ?", (student_id,))
        conn.execute("DELETE FROM student_roadmap WHERE student_id = ?", (student_id,))
        conn.execute("DELETE FROM student_resume WHERE student_id = ?", (student_id,))
    else:
        cur = conn.execute(
            """
            INSERT INTO students (
                name, email, education_level, field_of_study, interests,
                skills, career_goals, work_style, experience_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
        student_id = cur.lastrowid

    rebuild_student_plan(conn, student_id)
    return jsonify({"student_id": student_id})


@app.get("/api/students/<int:student_id>/recommendations")
def api_recommendations(student_id):
    denied = assert_student_access(student_id)
    if denied:
        return denied
    if not get_student_or_404(student_id):
        return jsonify({"error": "Student not found"}), 404
    rows = db().execute(
        """
        SELECT r.match_score, r.reasons, c.*
        FROM recommendations r
        JOIN careers c ON c.id = r.career_id
        WHERE r.student_id = ?
        ORDER BY r.match_score DESC
        """,
        (student_id,),
    ).fetchall()
    results = []
    for row in rows:
        item = dict(row)
        item["reasons"] = json.loads(item["reasons"])
        results.append(item)
    return jsonify(results)


@app.get("/api/students/<int:student_id>/skill-gap")
def api_skill_gap(student_id):
    denied = assert_student_access(student_id)
    if denied:
        return denied
    student = get_student_or_404(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    career_id = request.args.get("career_id", type=int) or primary_career_id(student_id)
    if not career_id:
        return jsonify({"error": "No recommended career yet"}), 400

    career = row_to_dict(db().execute("SELECT * FROM careers WHERE id = ?", (career_id,)).fetchone())
    skills = career_skills_map(db()).get(career_id, [])
    have = {s.strip().lower() for s in student["skills"].split(",") if s.strip()}
    have_display = [s.strip() for s in student["skills"].split(",") if s.strip()]

    matched, missing = [], []
    for skill in skills:
        entry = {
            "name": skill["name"],
            "importance": skill["importance"],
            "category": skill["category"],
        }
        if skill["name"].lower() in have:
            matched.append(entry)
        else:
            missing.append(entry)

    return jsonify(
        {
            "career": career,
            "student_skills": have_display,
            "matched": matched,
            "missing": missing,
            "match_percent": round(100 * len(matched) / max(1, len(skills))),
        }
    )


@app.get("/api/students/<int:student_id>/roadmap")
def api_roadmap(student_id):
    denied = assert_student_access(student_id)
    if denied:
        return denied
    if not get_student_or_404(student_id):
        return jsonify({"error": "Student not found"}), 404
    career_id = request.args.get("career_id", type=int) or primary_career_id(student_id)
    if not career_id:
        return jsonify({"error": "No recommended career yet"}), 400

    career = row_to_dict(db().execute("SELECT * FROM careers WHERE id = ?", (career_id,)).fetchone())
    rows = db().execute(
        """
        SELECT rs.id, rs.month_number, rs.title, rs.description, rs.resources,
               COALESCE(sr.completed, 0) AS completed, sr.id AS progress_id
        FROM roadmap_steps rs
        LEFT JOIN student_roadmap sr
          ON sr.step_id = rs.id AND sr.student_id = ?
        WHERE rs.career_id = ?
        ORDER BY rs.month_number
        """,
        (student_id, career_id),
    ).fetchall()
    steps = rows_to_dicts(rows)
    done = sum(1 for step in steps if step["completed"])
    return jsonify(
        {
            "career": career,
            "steps": steps,
            "completed": done,
            "total": len(steps),
            "percent": round(100 * done / max(1, len(steps))),
        }
    )


@app.patch("/api/progress/<int:progress_id>")
def api_toggle_progress(progress_id):
    payload = request.get_json(silent=True) or {}
    completed = 1 if payload.get("completed") else 0
    conn = db()
    row = conn.execute("SELECT * FROM student_roadmap WHERE id = ?", (progress_id,)).fetchone()
    if not row:
        return jsonify({"error": "Progress row not found"}), 404
    denied = assert_student_access(row["student_id"])
    if denied:
        return denied
    conn.execute("UPDATE student_roadmap SET completed = ? WHERE id = ?", (completed, progress_id))
    conn.commit()
    return jsonify({"id": progress_id, "completed": completed})


@app.get("/api/students/<int:student_id>/projects")
def api_projects(student_id):
    denied = assert_student_access(student_id)
    if denied:
        return denied
    if not get_student_or_404(student_id):
        return jsonify({"error": "Student not found"}), 404
    career_id = request.args.get("career_id", type=int) or primary_career_id(student_id)
    if not career_id:
        return jsonify({"error": "No recommended career yet"}), 400
    career = row_to_dict(db().execute("SELECT * FROM careers WHERE id = ?", (career_id,)).fetchone())
    projects = rows_to_dicts(
        db()
        .execute(
            "SELECT * FROM projects WHERE career_id = ? ORDER BY id",
            (career_id,),
        )
        .fetchall()
    )
    return jsonify({"career": career, "projects": projects})


@app.get("/api/students/<int:student_id>/resume")
def api_resume(student_id):
    denied = assert_student_access(student_id)
    if denied:
        return denied
    if not get_student_or_404(student_id):
        return jsonify({"error": "Student not found"}), 404
    rows = db().execute(
        """
        SELECT ri.id, ri.title, ri.description, ri.section,
               COALESCE(sr.completed, 0) AS completed, sr.id AS progress_id
        FROM resume_items ri
        LEFT JOIN student_resume sr
          ON sr.item_id = ri.id AND sr.student_id = ?
        ORDER BY ri.id
        """,
        (student_id,),
    ).fetchall()
    items = rows_to_dicts(rows)
    done = sum(1 for item in items if item["completed"])
    return jsonify(
        {
            "items": items,
            "completed": done,
            "total": len(items),
            "percent": round(100 * done / max(1, len(items))),
        }
    )


@app.post("/api/students/<int:student_id>/resume/upload")
def api_resume_upload(student_id):
    denied = assert_student_access(student_id)
    if denied:
        return denied
    student = get_student_or_404(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    upload = request.files["file"]
    if not upload or not upload.filename:
        return jsonify({"error": "No file selected"}), 400
    if not allowed_resume_file(upload.filename):
        return jsonify({"error": "Use PDF, DOC, or DOCX only"}), 400

    original = secure_filename(upload.filename) or "resume"
    ext = Path(original).suffix.lower()
    stored = f"{student_id}_{uuid4().hex}{ext}"
    path = UPLOAD_DIR / stored
    upload.save(path)
    size = path.stat().st_size

    conn = db()
    user = conn.execute("SELECT name FROM users WHERE student_id = ?", (student_id,)).fetchone()
    skill_rows = conn.execute("SELECT name FROM skills ORDER BY name").fetchall()
    skill_names = [r["name"] for r in skill_rows]

    try:
        parsed = parse_resume(path, skill_names, fallback_name=user["name"] if user else student["name"])
    except ValueError as exc:
        path.unlink(missing_ok=True)
        return jsonify({"error": str(exc)}), 400

    conn.execute(
        """
        UPDATE students
        SET name=?, education_level=?, field_of_study=?, interests=?,
            skills=?, career_goals=?, work_style=?, experience_level=?
        WHERE id=?
        """,
        (
            parsed["name"],
            parsed["education_level"],
            parsed["field_of_study"],
            parsed["interests"],
            parsed["skills"],
            parsed["career_goals"],
            parsed["work_style"],
            parsed["experience_level"],
            student_id,
        ),
    )

    old_files = conn.execute(
        "SELECT stored_filename FROM student_resume_files WHERE student_id = ?",
        (student_id,),
    ).fetchall()
    for old in old_files:
        (UPLOAD_DIR / old["stored_filename"]).unlink(missing_ok=True)
    conn.execute("DELETE FROM student_resume_files WHERE student_id = ?", (student_id,))

    cur = conn.execute(
        """
        INSERT INTO student_resume_files
            (student_id, original_filename, stored_filename, color_theme, file_size)
        VALUES (?, ?, ?, 'warm', ?)
        """,
        (student_id, original, stored, size),
    )

    ranked = rebuild_student_plan(conn, student_id)
    top = ranked[0]["career"] if ranked else None

    return jsonify(
        {
            "file_id": cur.lastrowid,
            "parsed": {
                "education_level": parsed["education_level"],
                "field_of_study": parsed["field_of_study"],
                "skills": parsed["skills_list"],
                "experience_level": parsed["experience_level"],
                "work_style": parsed["work_style"],
            },
            "top_career": top["title"] if top else None,
            "resume_scanned": 1,
        }
    ), 201


@app.patch("/api/resume-progress/<int:progress_id>")
def api_toggle_resume(progress_id):
    payload = request.get_json(silent=True) or {}
    completed = 1 if payload.get("completed") else 0
    conn = db()
    row = conn.execute("SELECT * FROM student_resume WHERE id = ?", (progress_id,)).fetchone()
    if not row:
        return jsonify({"error": "Resume progress not found"}), 404
    denied = assert_student_access(row["student_id"])
    if denied:
        return denied
    conn.execute("UPDATE student_resume SET completed = ? WHERE id = ?", (completed, progress_id))
    conn.commit()
    return jsonify({"id": progress_id, "completed": completed})


@app.get("/api/students/<int:student_id>/interview")
def api_interview(student_id):
    denied = assert_student_access(student_id)
    if denied:
        return denied
    if not get_student_or_404(student_id):
        return jsonify({"error": "Student not found"}), 404
    career_id = request.args.get("career_id", type=int) or primary_career_id(student_id)
    if not career_id:
        return jsonify({"error": "No recommended career yet"}), 400
    career = row_to_dict(db().execute("SELECT * FROM careers WHERE id = ?", (career_id,)).fetchone())
    questions = rows_to_dicts(
        db()
        .execute(
            "SELECT * FROM interview_questions WHERE career_id = ? ORDER BY id",
            (career_id,),
        )
        .fetchall()
    )
    return jsonify({"career": career, "questions": questions})


@app.get("/api/students/<int:student_id>/dashboard")
def api_dashboard(student_id):
    denied = assert_student_access(student_id)
    if denied:
        return denied
    student = get_student_or_404(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    recs = db().execute(
        """
        SELECT r.match_score, c.id AS career_id, c.title, c.category
        FROM recommendations r
        JOIN careers c ON c.id = r.career_id
        WHERE r.student_id = ?
        ORDER BY r.match_score DESC
        """,
        (student_id,),
    ).fetchall()
    career_id = primary_career_id(student_id)
    road = {"percent": 0, "completed": 0, "total": 0, "career": None}
    if career_id:
        steps = db().execute(
            """
            SELECT COALESCE(sr.completed, 0) AS completed
            FROM roadmap_steps rs
            LEFT JOIN student_roadmap sr
              ON sr.step_id = rs.id AND sr.student_id = ?
            WHERE rs.career_id = ?
            """,
            (student_id, career_id),
        ).fetchall()
        done = sum(1 for s in steps if s["completed"])
        career = row_to_dict(db().execute("SELECT * FROM careers WHERE id = ?", (career_id,)).fetchone())
        road = {
            "percent": round(100 * done / max(1, len(steps))),
            "completed": done,
            "total": len(steps),
            "career": career,
        }
    resume_rows = db().execute(
        """
        SELECT COALESCE(sr.completed, 0) AS completed
        FROM resume_items ri
        LEFT JOIN student_resume sr ON sr.item_id = ri.id AND sr.student_id = ?
        """,
        (student_id,),
    ).fetchall()
    rdone = sum(1 for s in resume_rows if s["completed"])
    resume = {
        "percent": round(100 * rdone / max(1, len(resume_rows))),
        "completed": rdone,
        "total": len(resume_rows),
    }
    return jsonify(
        {
            "student": student,
            "recommendations": rows_to_dicts(recs),
            "roadmap": road,
            "resume": resume,
        }
    )


init_db()
seed()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
