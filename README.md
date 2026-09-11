# ResumeIQ

### Resume Intelligence & ATS Analysis Platform

ResumeIQ is a full-stack resume analysis platform designed to help candidates understand how their resume performs across **ATS compatibility, technical skills, projects, experience, keywords, and overall resume quality**.

Instead of reducing a resume to a single score, ResumeIQ decomposes it into measurable components and generates structured, actionable insights.

---

## Overview

A resume contains much more information than its formatting and keyword count.

ResumeIQ analyzes the underlying content of a resume and converts it into structured intelligence covering:

* ATS compatibility
* Technical skills
* Projects
* Experience
* Education
* Certifications
* Achievements
* Keywords
* Quantifiable metrics
* Action verbs
* Engineering signals
* Candidate profile
* Improvement recommendations

The platform is built with a modular analysis architecture so that individual scoring and extraction components can be developed, tested, and improved independently.

---

## Features

### ATS Analysis

Evaluates a resume using multiple ATS-oriented signals:

* Keyword coverage
* Required section presence
* Technical terminology
* Quantifiable metrics
* Readability
* Action verbs
* Missing keywords
* Role-dependent keywords

The ATS engine uses the following scoring distribution:

| Signal               | Weight |
| -------------------- | -----: |
| Keyword Coverage     |    35% |
| Section Completeness |    20% |
| Quantifiable Metrics |    15% |
| Readability          |    15% |
| Technical Content    |    15% |

ResumeIQ also distinguishes between **actionable missing keywords** and **role-dependent keywords**, helping avoid treating every missing technology as universally required.

---

### Skills Intelligence

Extracts and evaluates technical skills from the resume.

Supported categories can include:

* Programming languages
* Frameworks
* Libraries
* Databases
* Cloud technologies
* AI/ML technologies
* Developer tools
* Other technical technologies

The engine produces a structured skills analysis and score rather than relying solely on the number of technologies detected.

---

### Project Analysis

Projects are analyzed for technical and engineering signals, including:

* Technologies used
* Technical complexity
* Development practices
* Backend/frontend technologies
* AI/ML technologies
* APIs
* Application serving
* Deployment-related terminology
* Engineering depth

ResumeIQ attempts to distinguish between technologies that are merely listed and technologies that are actually demonstrated through project descriptions.

---

### Experience Analysis

Evaluates experience descriptions for:

* Technical contributions
* Responsibilities
* Action verbs
* Quantifiable outcomes
* Technologies used
* Engineering impact

This helps identify experience descriptions that could communicate stronger technical ownership and measurable results.

---

### Education Analysis

Extracts structured education information such as:

* Institution
* Degree
* Field of study
* CGPA / percentage
* Start year
* End year

The analysis also handles fragmented resume text and attempts to consolidate related education information into coherent records.

---

### Certifications & Achievements

Identifies and evaluates additional candidate signals, including:

* Certifications
* Awards
* Competitions
* Academic achievements
* Other notable accomplishments

---

### Keyword Intelligence

ResumeIQ provides more than a simple keyword count.

It identifies:

* Matched keywords
* Missing keywords
* Technical keywords
* Actionable missing keywords
* Role-dependent keywords

This makes the analysis useful when tailoring a resume toward different software and technical roles.

---

### Metrics Detection

Quantifiable results can significantly strengthen resume statements.

ResumeIQ detects measurable signals such as:

* Percentages
* Accuracy values
* Performance improvements
* Scale
* User counts
* Time reductions
* Other numerical outcomes

For example:

```text
Improved model accuracy by 15%
```

contains a measurable outcome that provides stronger evidence of impact than a purely descriptive statement.

---

### Engineering & Deployment Signals

ResumeIQ analyzes technical terminology while avoiding unsupported assumptions.

For example:

```text
Built a Flask API
```

is not automatically interpreted as:

```text
Deployed a production application
```

The platform distinguishes application-serving technologies from evidence of actual production deployment.

This is particularly important when analyzing technical resumes where terminology can otherwise be misleading.

---

## Architecture

```text
                         ┌──────────────────┐
                         │      Resume      │
                         │      Upload      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  React Frontend  │
                         │    Dashboard     │
                         └────────┬─────────┘
                                  │
                              REST API
                                  │
                                  ▼
                     ┌────────────────────────┐
                     │    FastAPI Backend     │
                     └───────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │ ATS Engine  │    │ Skills      │    │ Project     │
       │             │    │ Engine      │    │ Engine      │
       └─────────────┘    └─────────────┘    └─────────────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │ Analysis & Scoring     │
                     │ Engine                  │
                     └───────────┬────────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │ Recommendation Engine  │
                     └───────────┬────────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │ Structured JSON Result │
                     └───────────┬────────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │    ResumeIQ Dashboard  │
                     └────────────────────────┘
```

---

## Technology Stack

### Frontend

* React
* JavaScript
* Vite
* Tailwind CSS
* React Router

### Backend

* Python
* FastAPI
* Pydantic
* Pytest

### Analysis

* Custom resume analysis engines
* Rule-based extraction
* Keyword analysis
* Section detection
* Skill extraction
* Project analysis
* ATS scoring
* Recommendation generation

---

## Project Structure

```text
ResumeIQ/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   │
│   │   ├── candidate/
│   │   │   └── profile_builder.py
│   │   │
│   │   ├── services/
│   │   │   ├── analyzer.py
│   │   │   ├── ats_engine.py
│   │   │   ├── scoring_engine.py
│   │   │   └── project_engine.py
│   │   │
│   │   └── main.py
│   │
│   └── tests/
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   └── ResumeAnalysis.jsx
│       ├── context/
│       └── App.jsx
│
└── README.md
```

---

## API

### Analyze Resume

```http
POST /resume/analyze
```

Analyzes an uploaded resume and returns a structured ResumeIQ analysis.

### Resume Matching

```http
POST /resume/match
```

Compares resume content against a target job description and returns matching insights.

---

## Analysis Pipeline

```text
Resume
   │
   ▼
Text Extraction
   │
   ▼
Section Detection
   │
   ├── Education
   ├── Skills
   ├── Projects
   ├── Experience
   ├── Certifications
   └── Achievements
   │
   ▼
Specialized Analysis
   │
   ├── ATS
   ├── Skills
   ├── Projects
   ├── Experience
   └── Candidate Profile
   │
   ▼
Scoring
   │
   ▼
Recommendations
   │
   ▼
Structured Analysis JSON
   │
   ▼
React Dashboard
```

---

## Example Response

A simplified response structure:

```json
{
  "resume_intelligence_score": 71.4,
  "ats_analysis": {
    "ats_score": 71.4,
    "matched_keywords": [],
    "missing_keywords": [],
    "strengths": [],
    "issues": []
  },
  "skills_analysis": {
    "skill_score": 76,
    "skills": []
  },
  "project_analysis": {
    "score": 80,
    "projects": []
  },
  "experience_analysis": {
    "experience_score": 72
  },
  "candidate_profile": {
    "name": "Candidate Name",
    "headline": "Software Engineer"
  },
  "recommendations": []
}
```

The production response contains additional structured analysis data.

---

## Running Locally

### Prerequisites

* Python 3.x
* Node.js
* npm

### Backend

```bash
cd backend

python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app.main:app --reload
```

---

### Frontend

Open a second terminal:

```bash
cd frontend

npm install

npm run dev
```

Open the local URL displayed by Vite.

---

## Testing

ResumeIQ includes an automated backend test suite covering analysis engines, scoring behavior, API behavior, and regression cases.

Run:

```bash
cd backend
python -m pytest -q
```

Current backend baseline:

```text
175 passed
```

---

## Design Principles

### Modular Analysis

Each major resume component has its own analysis logic, making the system easier to test and extend.

### Explainable Scoring

Scores are derived from identifiable resume signals rather than being treated as opaque predictions.

### Actionable Feedback

The goal is not simply to tell a candidate that a resume has weaknesses, but to identify areas that can be improved.

### Evidence-Based Analysis

ResumeIQ avoids interpreting unsupported claims as established experience.

For example, mentioning a framework does not automatically prove production experience with that framework.

### Structured Output

Analysis is returned as structured JSON so the frontend can independently render and consume individual insights.

---

## Current Capabilities

| Capability              | Status |
| ----------------------- | :----: |
| Resume Analysis         |    ✅   |
| ATS Analysis            |    ✅   |
| Skill Analysis          |    ✅   |
| Project Analysis        |    ✅   |
| Experience Analysis     |    ✅   |
| Education Analysis      |    ✅   |
| Certification Analysis  |    ✅   |
| Achievement Analysis    |    ✅   |
| Keyword Analysis        |    ✅   |
| Metrics Detection       |    ✅   |
| Candidate Profile       |    ✅   |
| Recommendations         |    ✅   |
| Resume Matching         |    ✅   |
| Automated Backend Tests |    ✅   |
| Interactive Dashboard   |    ✅   |

---

## Roadmap

Planned areas for future development include:

* Job-description-specific resume optimization
* Semantic resume-to-job matching
* Resume version management
* Resume comparison
* AI-assisted bullet improvement
* Role-specific scoring
* Industry-specific analysis
* Personalized improvement tracking
* User authentication
* Persistent resume history
* Production deployment

---

## Project Motivation

ResumeIQ was built around a simple problem:

> **A resume should be evaluated as technical evidence, not just as a formatted document.**

A strong resume needs to communicate skills, experience, engineering ability, measurable impact, and relevance to a target role.

ResumeIQ brings these signals together into a single structured analysis platform.

---

## Author

**Abhinav Vanaparthy**

B.Tech — Artificial Intelligence & Machine Learning

Areas of interest:

* Software Engineering
* Artificial Intelligence
* Machine Learning
* Backend Development
* Full-Stack Development
* Developer Tools

---

## License

This project is currently a personal portfolio project.

If the repository is made open source, an appropriate license can be added here.
