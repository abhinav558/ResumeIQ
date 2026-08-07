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
    "javascript",
    "kubernetes"
]


RECOMMENDED_SKILLS = [
    "docker",
    "aws",
    "git",
    "github",
    "fastapi",
    "sql"
]


def extract_skills(text):

    found = []

    text = text.lower()

    for skill in SKILLS:
        if skill in text:
            found.append(skill)

    return found



def detect_sections(text):

    text = text.lower()

    sections = {
        "education": False,
        "experience": False,
        "projects": False,
        "skills": False,
        "certifications": False
    }


    keywords = {
        "education": ["education", "b.tech", "degree"],
        "experience": ["experience", "internship", "work"],
        "projects": ["projects", "project"],
        "skills": ["skills", "technical skills"],
        "certifications": ["certification", "certificate"]
    }


    for section, words in keywords.items():
        for word in words:
            if word in text:
                sections[section] = True
                break


    return sections



def calculate_score(sections, skills):

    breakdown = {}


    breakdown["skills"] = min(len(skills) * 5, 30)

    breakdown["projects"] = (
        25 if sections["projects"] else 0
    )

    breakdown["experience"] = (
        20 if sections["experience"] else 0
    )

    breakdown["education"] = (
        15 if sections["education"] else 0
    )

    breakdown["certifications"] = (
        10 if sections["certifications"] else 0
    )


    total = sum(breakdown.values())


    return total, breakdown



def analyze_resume(text):

    skills = extract_skills(text)

    sections = detect_sections(text)


    score, breakdown = calculate_score(
        sections,
        skills
    )


    missing_skills = []

    for skill in RECOMMENDED_SKILLS:
        if skill not in skills:
            missing_skills.append(skill)



    suggestions = []


    for section, present in sections.items():

        if not present:
            suggestions.append(
                f"Add {section} section"
            )


    if missing_skills:
        suggestions.append(
            "Consider adding missing technical skills"
        )


    suggestions.append(
        "Add measurable achievements with numbers"
    )


    return {

        "ats_score": score,

        "score_breakdown": breakdown,

        "skills_found": skills,

        "missing_skills": missing_skills,

        "sections_detected": sections,

        "suggestions": suggestions

    }