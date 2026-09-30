import re
from pathlib import Path


EDUCATION_PATTERNS = [
    (r"\b(ph\.?d|doctorate)\b", "PhD / Doctorate"),
    (r"\b(master'?s?|m\.?sc|m\.?tech|mba|m\.?e\.?)\b", "Master's degree"),
    (r"\b(bachelor'?s?|b\.?tech|b\.?e\.?|b\.?sc|b\.?a\.?|undergraduate)\b", "Bachelor's degree"),
    (r"\b(associate|diploma)\b", "Associate / Diploma"),
    (r"\b(high school|secondary school|12th|hsc)\b", "High school"),
]

FIELD_HINTS = [
    "computer science",
    "information technology",
    "software engineering",
    "electrical engineering",
    "mechanical engineering",
    "business administration",
    "data science",
    "mathematics",
    "statistics",
    "design",
    "marketing",
    "finance",
    "psychology",
    "biology",
    "chemistry",
    "physics",
    "economics",
    "commerce",
    "arts",
    "humanities",
]

EXPERIENCE_PATTERNS = [
    (r"\b(10\+|senior|lead|principal|staff)\b", "advanced"),
    (r"\b(3\+|4\+|5\+|mid[- ]?level|intermediate)\b", "intermediate"),
    (r"\b(intern|internship|fresher|entry[- ]?level|graduate|junior)\b", "beginner"),
]


def extract_text_from_file(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)
    if ext == ".docx":
        from docx import Document

        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    if ext == ".doc":
        raise ValueError("Old .doc format is not supported. Save as PDF or DOCX and try again.")
    raise ValueError("Unsupported file type. Use PDF or DOCX.")


def detect_education(text: str) -> str:
    lower = text.lower()
    for pattern, label in EDUCATION_PATTERNS:
        if re.search(pattern, lower):
            return label
    return "Not specified"


def detect_field(text: str) -> str:
    lower = text.lower()
    for field in FIELD_HINTS:
        if field in lower:
            return field.title()
    edu_match = re.search(
        r"(?:b\.?tech|bachelor|major|degree|studied)\s+(?:in\s+)?([a-z][a-z\s&/-]{2,40})",
        lower,
    )
    if edu_match:
        return edu_match.group(1).strip().title()[:60]
    return "General"


def detect_experience(text: str) -> str:
    lower = text.lower()
    for pattern, level in EXPERIENCE_PATTERNS:
        if re.search(pattern, lower):
            return level
    years = re.findall(r"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience", lower)
    if years:
        y = max(int(y) for y in years)
        if y >= 5:
            return "advanced"
        if y >= 2:
            return "intermediate"
    return "beginner"


def detect_work_style(text: str, skills: list[str]) -> str:
    lower = text.lower()
    skill_text = " ".join(skills).lower()
    if any(w in lower for w in ("ux", "ui design", "figma", "creative", "brand")):
        return "creator"
    if any(w in lower for w in ("stakeholder", "customer", "sales", "team lead", "mentor")):
        return "people"
    if any(w in lower or w in skill_text for w in ("sql", "analytics", "excel", "statistics", "research")):
        return "analyst"
    return "builder"


def match_skills(text: str, skill_names: list[str]) -> list[str]:
    lower = text.lower()
    found = []
    for name in skill_names:
        token = name.lower()
        if len(token) < 2:
            continue
        if token in lower or re.search(rf"\b{re.escape(token)}\b", lower):
            found.append(name)
    return sorted(set(found))


def infer_interests(text: str, field: str, skills: list[str]) -> str:
    section = re.search(
        r"(?:interests?|hobbies|passions?)\s*[:\-]\s*(.{10,200})",
        text,
        re.IGNORECASE,
    )
    if section:
        return section.group(1).split("\n")[0].strip()[:200]
    top = ", ".join(skills[:5])
    if top:
        return f"Building with {top}"
    return f"Careers related to {field}"


def infer_goals(text: str, field: str) -> str:
    section = re.search(
        r"(?:objective|summary|career goal|professional summary)\s*[:\-]?\s*(.{20,280})",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if section:
        line = re.sub(r"\s+", " ", section.group(1)).strip()
        return line[:280]
    return f"Advance in {field} and land a strong first role."


def parse_resume(path: Path, skill_names: list[str], fallback_name: str = "") -> dict:
    text = extract_text_from_file(path)
    if not text.strip():
        raise ValueError("Could not read text from this file. Try a text-based PDF or DOCX.")

    skills = match_skills(text, skill_names)
    education = detect_education(text)
    field = detect_field(text)
    experience = detect_experience(text)
    work_style = detect_work_style(text, skills)
    interests = infer_interests(text, field, skills)
    goals = infer_goals(text, field)

    name = fallback_name
    if not name:
        for line in text.splitlines():
            line = line.strip()
            if 2 < len(line) < 60 and not re.search(r"@|http|phone|\d{3}", line, re.I):
                name = line
                break

    return {
        "name": name or fallback_name or "Student",
        "education_level": education,
        "field_of_study": field,
        "skills": ", ".join(skills) if skills else "Communication, Teamwork",
        "skills_list": skills,
        "interests": interests,
        "career_goals": goals,
        "work_style": work_style,
        "experience_level": experience,
        "raw_excerpt": text[:1200],
    }
