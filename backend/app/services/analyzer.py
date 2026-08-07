import re


SKILLS = [
    "python",
    "java",
    "c++",
    "sql",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "react",
    "fastapi",
    "docker",
    "aws",
    "git",
    "github",
    "mongodb",
    "mysql",
    "javascript"
]


def extract_skills(text):

    found = []

    text = text.lower()

    for skill in SKILLS:
        if skill in text:
            found.append(skill)

    return found



def calculate_score(text, skills):

    score = 0

    text_lower = text.lower()


    # Skills (30 points)
    skill_score = min(len(skills) * 5, 30)
    score += skill_score


    # Projects (25 points)
    if "project" in text_lower:
        score += 25


    # Experience (20 points)
    if "experience" in text_lower or "internship" in text_lower:
        score += 20


    # Education (15 points)
    if "education" in text_lower or "b.tech" in text_lower:
        score += 15


    # Achievements (10 points)
    if "achievement" in text_lower or "certification" in text_lower:
        score += 10


    return min(score, 100)



def analyze_resume(text):

    skills = extract_skills(text)

    score = calculate_score(
        text,
        skills
    )


    suggestions = []


    if len(skills) < 5:
        suggestions.append(
            "Add more technical skills"
        )


    if "project" not in text.lower():
        suggestions.append(
            "Add detailed project descriptions"
        )


    if "experience" not in text.lower():
        suggestions.append(
            "Include internship or experience details"
        )


    suggestions.append(
        "Add measurable achievements with numbers"
    )


    return {
        "ats_score": score,
        "skills_found": skills,
        "suggestions": suggestions
    }