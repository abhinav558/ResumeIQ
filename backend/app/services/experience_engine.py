"""
ResumeIQ - Production Experience Intelligence Engine

Analyzes:
- Work experience
- Internship experience
- Roles
- Companies
- Technical exposure
- Achievements

Important:
Projects are NOT counted as experience.
"""


import re



# ======================================================
# Experience Keywords
# ======================================================

ROLE_KEYWORDS = [

    "intern",

    "developer",

    "engineer",

    "software",

    "machine learning",

    "data scientist",

    "analyst",

    "research"

]



ACTION_KEYWORDS = [

    "developed",

    "built",

    "implemented",

    "designed",

    "optimized",

    "created",

    "automated",

    "integrated"

]



TECH_KEYWORDS = [

    "python",

    "java",

    "javascript",

    "react",

    "tensorflow",

    "pytorch",

    "machine learning",

    "deep learning",

    "sql",

    "aws",

    "docker",

    "flask",

    "fastapi"

]



METRIC_PATTERN = [

    r"\d+(?:\.\d+)?%",

    r"\d+\+",

    r"\d+\s*(users|records|samples)"

]



# ======================================================
# Clean Text
# ======================================================

def clean_text(text):

    if not text:

        return ""


    text=text.lower()


    text=re.sub(

        r"\s+",

        " ",

        text

    )


    return text.strip()



# ======================================================
# Extract Metrics
# ======================================================

def extract_metrics(text):

    metrics=[]


    for pattern in METRIC_PATTERN:

        metrics.extend(

            re.findall(

                pattern,

                text

            )

        )


    return list(set(metrics))



# ======================================================
# Detect Experience
# ======================================================

def detect_experience_items(text):

    if not text:

        return []



    lines=text.split("\n")


    items=[]

    current=[]



    for line in lines:


        line=line.strip()



        if not line:

            continue



        current.append(line)



        # Experience blocks usually contain dates

        if re.search(

            r"(20\d{2}|present|current)",

            line.lower()

        ):


            items.append(

                " ".join(current)

            )


            current=[]



    if current and len(current)>2:

        items.append(

            " ".join(current)

        )



    return items



# ======================================================
# Analyze Single Experience
# ======================================================

def analyze_item(item):

    text=clean_text(item)



    actions=[]


    for word in ACTION_KEYWORDS:

        if word in text:

            actions.append(word)



    technologies=[]


    for tech in TECH_KEYWORDS:

        if tech in text:

            technologies.append(tech)



    metrics=extract_metrics(text)



    score=0


    if actions:

        score+=20


    if technologies:

        score+=20


    if metrics:

        score+=20



    if any(

        role in text

        for role in ROLE_KEYWORDS

    ):

        score+=20



    score=min(

        score,

        100

    )



    return {

        "score":score,

        "actions":list(set(actions)),

        "technical_features":
            list(set(technologies)),

        "metrics":
            metrics

    }



# ======================================================
# Main Experience Analyzer
# ======================================================

def analyze_experience(sections):


    if not isinstance(

        sections,

        dict

    ):

        return {

            "experience_score":0,

            "experience_type":"None",

            "count":0,

            "items":[]

        }



    experience_text = (

        sections.get(

            "experience",

            ""

        )

        +

        "\n"

        +

        sections.get(

            "internship",

            ""

        )

    )



    experience_text=experience_text.strip()



    # No experience found

    if not experience_text:


        return {


            "experience_score":0,


            "experience_type":
                "No professional experience",


            "count":0,


            "items":[],


            "technical_features":[],


            "actions":[],


            "metrics":[],


            "message":
                "No internship or work experience detected"

        }



    items=detect_experience_items(

        experience_text

    )



    if not items:


        items=[experience_text]



    results=[]



    for item in items:

        results.append(

            analyze_item(item)

        )



    score=sum(

        x["score"]

        for x in results

    ) / len(results)



    technologies=[]

    actions=[]

    metrics=[]



    for item in results:

        technologies.extend(

            item["technical_features"]

        )

        actions.extend(

            item["actions"]

        )

        metrics.extend(

            item["metrics"]

        )



    return {


        "experience_score":

            round(

                score,

                2

            ),



        "experience_type":

            "Professional Experience",



        "count":

            len(results),



        "items":

            items,



        "technical_features":

            list(set(technologies)),



        "actions":

            list(set(actions)),



        "metrics":

            list(set(metrics)),



        "message":

            "Professional experience detected"

    }