"""
ResumeIQ - Production Section Parser

Responsible for:
- Resume section extraction
- Heading detection
- Structured resume parsing

Output contract:

{
    "summary": str,
    "education": str,
    "skills": str,
    "projects": str,
    "experience": str,
    "internship": str,
    "certifications": str,
    "achievements": str
}
"""

import re



# ======================================================
# Supported Resume Headings
# ======================================================

SECTION_HEADERS = {

    "summary": [
        "summary",
        "profile",
        "objective",
        "professional summary"
    ],


    "education": [
        "education",
        "academic background",
        "qualification"
    ],


    "skills": [
        "skills",
        "technical skills",
        "technical expertise",
        "technologies"
    ],


    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "project experience"
    ],


    "experience": [
        "experience",
        "work experience",
        "professional experience"
    ],


    "internship": [
        "internship",
        "internships"
    ],


    "certifications": [
        "certifications",
        "certificates",
        "courses"
    ],


    "achievements": [
        "achievements",
        "awards",
        "honors"
    ]

}



# ======================================================
# Text Cleaning
# ======================================================

def clean_line(line):

    if not line:
        return ""


    line = line.lower()


    line = re.sub(
        r"[^a-z0-9+#&.\s]",
        "",
        line
    )


    line = re.sub(
        r"\s+",
        " ",
        line
    )


    return line.strip()



# ======================================================
# Heading Detection
# ======================================================

def detect_heading(line):

    cleaned = clean_line(line)


    if not cleaned:
        return None



    for section, names in SECTION_HEADERS.items():

        for name in names:

            if cleaned == name:

                return section



    return None



# ======================================================
# Remove Empty Lines
# ======================================================

def normalize_text(text):

    lines = text.split("\n")


    cleaned=[]


    for line in lines:

        line=line.strip()


        if line:

            cleaned.append(line)



    return cleaned



# ======================================================
# Section Extraction
# ======================================================

def extract_sections(text):

    if not text:

        return {}



    lines = normalize_text(text)



    sections = {

        "summary":"",
        "education":"",
        "skills":"",
        "projects":"",
        "experience":"",
        "internship":"",
        "certifications":"",
        "achievements":""

    }



    current_section=None



    buffer=[]



    for line in lines:


        heading = detect_heading(line)



        if heading:


            if current_section:

                sections[current_section] = (
                    "\n".join(buffer).strip()
                )


            current_section = heading

            buffer=[]


        else:


            buffer.append(line)



    # save last section

    if current_section:

        sections[current_section] = (
            "\n".join(buffer).strip()
        )



    return sections



# ======================================================
# Section Presence Detection
# ======================================================

def detect_sections(sections):

    if not isinstance(
        sections,
        dict
    ):

        return {}



    result={}



    for key,value in sections.items():


        result[key] = bool(

            value and

            len(value.strip()) > 5

        )



    return result