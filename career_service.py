from collections import defaultdict

from matching import recommend


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


def rebuild_student_plan(conn, student_id):
    """Rank careers and attach roadmap + resume checklist rows for this student."""
    student = dict(conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone())
    conn.execute("DELETE FROM recommendations WHERE student_id = ?", (student_id,))
    conn.execute("DELETE FROM student_roadmap WHERE student_id = ?", (student_id,))
    conn.execute("DELETE FROM student_resume WHERE student_id = ?", (student_id,))

    careers = [dict(r) for r in conn.execute("SELECT * FROM careers").fetchall()]
    ranked = recommend(student, careers, career_skills_map(conn))

    for item in ranked:
        conn.execute(
            """
            INSERT INTO recommendations (student_id, career_id, match_score, reasons)
            VALUES (?, ?, ?, ?)
            """,
            (student_id, item["career"]["id"], item["match_score"], item["reasons"]),
        )

    if not ranked:
        conn.commit()
        return []

    top_career_id = ranked[0]["career"]["id"]
    steps = conn.execute(
        "SELECT id FROM roadmap_steps WHERE career_id = ?", (top_career_id,)
    ).fetchall()
    for step in steps:
        conn.execute(
            "INSERT OR IGNORE INTO student_roadmap (student_id, step_id, completed) VALUES (?, ?, 0)",
            (student_id, step["id"]),
        )

    items = conn.execute("SELECT id FROM resume_items").fetchall()
    for item in items:
        conn.execute(
            "INSERT OR IGNORE INTO student_resume (student_id, item_id, completed) VALUES (?, ?, 0)",
            (student_id, item["id"]),
        )

    conn.execute(
        "UPDATE students SET resume_scanned = 1 WHERE id = ?",
        (student_id,),
    )
    conn.commit()
    return ranked
