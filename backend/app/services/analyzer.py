def analyze_resume(text: str):

    skills = [
        "python",
        "java",
        "sql",
        "machine learning",
        "react",
        "fastapi"
    ]

    found_skills = []

    lower_text = text.lower()

    for skill in skills:
        if skill in lower_text:
            found_skills.append(skill)

    score = min(len(found_skills) * 15, 100)

    return {
        "score": score,
        "skills_found": found_skills,
        "suggestions": [
            "Add more technical skills",
            "Include measurable project achievements",
            "Improve resume keywords"
        ]
    }