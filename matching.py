import json


def parse_list(value):
    if not value:
        return []
    return [item.strip().lower() for item in value.split(",") if item.strip()]


def score_career(student, career, career_skills):
    interests = parse_list(student["interests"])
    student_skills = set(parse_list(student["skills"]))
    goals = (student["career_goals"] or "").lower()
    field = (student["field_of_study"] or "").lower()
    education = (student["education_level"] or "").lower()
    keywords = [k.strip().lower() for k in career["keywords"].split(",") if k.strip()]
    education_fit = (career["education_fit"] or "").lower()

    score = 18
    reasons = []

    interest_hits = [word for word in interests if any(word in kw or kw in word for kw in keywords)]
    if interest_hits:
        score += min(24, 8 * len(set(interest_hits)))
        reasons.append("Your interests overlap with this path.")

    core = [s for s in career_skills if s["importance"] == "core"]
    supporting = [s for s in career_skills if s["importance"] != "core"]
    core_names = {s["name"].lower() for s in core}
    all_names = {s["name"].lower() for s in career_skills}
    matched_core = student_skills & core_names
    matched_all = student_skills & all_names
    if matched_core:
        score += min(28, 7 * len(matched_core))
        reasons.append(f"You already have core skills: {', '.join(sorted(matched_core))}.")
    elif matched_all:
        score += 10
        reasons.append("Some of your skills transfer here.")

    if any(token in field for token in education_fit.replace("/", " ").split() if len(token) > 3):
        score += 12
        reasons.append("Your field of study is a natural fit.")
    elif "any major" in education_fit or "portfolio" in education_fit:
        score += 6
        reasons.append("This path welcomes varied academic backgrounds.")

    goal_hits = [kw for kw in keywords if kw in goals]
    if goal_hits:
        score += min(16, 5 * len(set(goal_hits)))
        reasons.append("Your stated goals mention this kind of work.")

    if student["work_style"] == "builder" and career["category"] in ("Technology", "Infrastructure", "Artificial Intelligence"):
        score += 6
    if student["work_style"] == "people" and career["category"] in ("Product", "Marketing", "Design", "Business"):
        score += 6
    if student["work_style"] == "analyst" and career["category"] in ("Data", "Business", "Security"):
        score += 6
    if student["work_style"] == "creator" and career["category"] in ("Design", "Marketing", "Product"):
        score += 6

    if student["experience_level"] == "beginner":
        score += 4
        reasons.append("The 6-month roadmap is paced for someone starting now.")
    elif student["experience_level"] == "intermediate":
        score += 6
    else:
        score += 8

    if "high school" in education and career["title"] in ("Software Engineer", "Digital Marketer", "UX Designer", "Full Stack Developer"):
        score += 4

    score = max(20, min(98, score))
    if not reasons:
        reasons.append("This is a viable option based on your education and goals.")
    return score, reasons


def recommend(student, careers, skills_by_career, top_n=4):
    ranked = []
    for career in careers:
        skills = skills_by_career.get(career["id"], [])
        score, reasons = score_career(student, career, skills)
        ranked.append(
            {
                "career": career,
                "match_score": score,
                "reasons": json.dumps(reasons),
            }
        )
    ranked.sort(key=lambda item: item["match_score"], reverse=True)
    return ranked[:top_n]
