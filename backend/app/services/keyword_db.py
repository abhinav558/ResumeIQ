"""
ResumeIQ - Production Keyword Database

Single source of truth for:

- technical skills
- ATS keywords
- job requirements
- skill categories
- engineering terminology
- networking terminology
- action verbs
- aliases
- role profiles
- role keyword weights

All ResumeIQ analysis services should consume this module
instead of maintaining independent keyword dictionaries.
"""

from __future__ import annotations


# ============================================================
# PROGRAMMING
# ============================================================

PROGRAMMING = {
    "python",
    "java",
    "c",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "go",
    "golang",
    "rust",
    "kotlin",
    "swift",
    "scala",
    "ruby",
    "php",
    "perl",
    "r",
    "matlab",
    "dart",
    "lua",
    "bash",
    "shell",
    "powershell",
}


# ============================================================
# FRONTEND
# ============================================================

FRONTEND = {
    "html",
    "html5",
    "css",
    "css3",
    "javascript",
    "typescript",
    "react",
    "react.js",
    "nextjs",
    "next.js",
    "angular",
    "vue",
    "vue.js",
    "svelte",
    "bootstrap",
    "tailwind",
    "tailwind css",
    "material ui",
    "mui",
    "redux",
    "webpack",
    "vite",
    "jquery",
}


# ============================================================
# BACKEND
# ============================================================

BACKEND = {
    "fastapi",
    "flask",
    "django",
    "django rest framework",
    "drf",
    "spring",
    "spring boot",
    "spring mvc",
    "node",
    "nodejs",
    "express",
    "express.js",
    "nestjs",
    "asp.net",
    "rest api",
    "restful api",
    "graphql",
    "grpc",
    "websocket",
    "api",
    "api development",
    "backend development",
    "microservices",
    "serverless",
}


# ============================================================
# DATABASE
# ============================================================

DATABASE = {
    "sql",
    "mysql",
    "postgresql",
    "postgres",
    "sqlite",
    "oracle",
    "mongodb",
    "redis",
    "cassandra",
    "dynamodb",
    "mariadb",
    "firebase",
    "firestore",
    "database",
    "database design",
    "database management",
    "nosql",
    "orm",
    "object relational mapping",
    "sqlalchemy",
    "hibernate",
    "jdbc",
}


# ============================================================
# AI / ML
# ============================================================

AI_ML = {
    "artificial intelligence",
    "ai",
    "machine learning",
    "ml",
    "deep learning",
    "generative ai",
    "genai",
    "natural language processing",
    "nlp",
    "computer vision",
    "neural network",
    "neural networks",
    "cnn",
    "rnn",
    "lstm",
    "transformer",
    "transformers",
    "reinforcement learning",
    "supervised learning",
    "unsupervised learning",
    "classification",
    "regression",
    "clustering",
    "recommendation systems",
    "recommendation system",
    "time series",
    "feature engineering",
    "model training",
    "model evaluation",
    "model deployment",
    "mlops",
    "prompt engineering",
    "large language models",
    "llm",
    "llms",
    "rag",
    "retrieval augmented generation",
    "vector database",
    "embeddings",
    "fine tuning",

    # Federated Learning
    "federated learning",
    "federated machine learning",
    "federated learning system",
    "federated learning systems",
    "federated averaging",
    "fedavg",
    "federated optimization",
}


# ============================================================
# AI / ML TOOLS
# ============================================================

AI_ML_TOOLS = {
    "tensorflow",
    "keras",
    "pytorch",
    "scikit-learn",
    "sklearn",
    "opencv",
    "pandas",
    "numpy",
    "scipy",
    "matplotlib",
    "seaborn",
    "hugging face",
    "transformers",
    "langchain",
    "llamaindex",
    "openai",
    "xgboost",
    "lightgbm",
}


# ============================================================
# CLOUD
# ============================================================

CLOUD = {
    "aws",
    "amazon web services",
    "azure",
    "microsoft azure",
    "gcp",
    "google cloud",
    "google cloud platform",
    "ec2",
    "s3",
    "lambda",
    "cloud computing",
    "cloud architecture",
    "cloud deployment",
    "cloud services",
    "firebase",
    "vercel",
    "netlify",
    "heroku",
}


# ============================================================
# DEVOPS
# ============================================================

DEVOPS = {
    "docker",
    "kubernetes",
    "k8s",
    "jenkins",
    "github actions",
    "gitlab ci",
    "circleci",
    "ci/cd",
    "ci cd",
    "continuous integration",
    "continuous delivery",
    "continuous deployment",
    "terraform",
    "ansible",
    "prometheus",
    "grafana",
    "monitoring",
    "logging",
    "automation",
    "devops",
    "infrastructure as code",
    "iac",
    "linux",
}


# ============================================================
# TOOLS
# ============================================================

TOOLS = {
    "git",
    "github",
    "gitlab",
    "bitbucket",
    "jira",
    "confluence",
    "postman",
    "swagger",
    "openapi",
    "vs code",
    "visual studio code",
    "intellij",
    "pycharm",
    "eclipse",
    "npm",
    "yarn",
    "pnpm",
}


# ============================================================
# ENGINEERING
# ============================================================

ENGINEERING = {
    "software development",
    "software engineering",
    "software development lifecycle",
    "sdlc",
    "system design",
    "system architecture",
    "software architecture",
    "architecture",
    "design patterns",
    "object oriented programming",
    "oop",
    "data structures",
    "algorithms",
    "data structures and algorithms",
    "testing",
    "unit testing",
    "integration testing",
    "functional testing",
    "regression testing",
    "test automation",
    "automation",
    "debugging",
    "code review",
    "version control",
    "agile",
    "scrum",
    "kanban",
    "problem solving",
    "scalable software",
    "scalable systems",
    "distributed systems",
    "distributed applications",
    "concurrent programming",
    "concurrency",
    "parallel programming",
    "synchronous",
    "asynchronous",
    "asynchronous programming",
    "performance optimization",
    "optimization",
    "reliability",
    "maintainability",
    "documentation",
    "technical documentation",
    "api design",
    "integration",
    "deployment",
    "production support",
}


# ============================================================
# NETWORKING
# ============================================================

NETWORKING = {
    "network",
    "networking",
    "networking systems",
    "network design",
    "network architecture",
    "computer networking",
    "computer networks",
    "tcp",
    "tcp/ip",
    "udp",
    "http",
    "https",
    "dns",
    "dhcp",
    "ip",
    "ipv4",
    "ipv6",
    "subnetting",
    "routing",
    "switching",
    "firewall",
    "vpn",
    "lan",
    "wan",
    "ethernet",
    "osi",
    "osi model",
    "network security",
    "network protocols",
    "load balancing",
    "proxy",
    "reverse proxy",
    "cdn",
    "socket programming",
}


# ============================================================
# BLOCKCHAIN
# ============================================================

BLOCKCHAIN = {
    "blockchain",
    "ethereum",
    "bitcoin",
    "smart contracts",
    "solidity",
    "web3",
    "hyperledger",
}


# ============================================================
# MOBILE
# ============================================================

MOBILE = {
    "android",
    "android development",
    "ios",
    "ios development",
    "flutter",
    "react native",
    "swift",
    "kotlin",
}


# ============================================================
# SECURITY
# ============================================================

SECURITY = {
    "cybersecurity",
    "information security",
    "application security",
    "network security",
    "authentication",
    "authorization",
    "oauth",
    "oauth2",
    "jwt",
    "encryption",
    "cryptography",
    "sha-256",
    "sha256",
    "penetration testing",
    "vulnerability assessment",
    "secure coding",
}


# ============================================================
# PROFESSIONAL
# ============================================================

PROFESSIONAL = {
    "leadership",
    "communication",
    "teamwork",
    "collaboration",
    "project management",
    "time management",
    "problem solving",
    "critical thinking",
    "analytical skills",
    "stakeholder management",
    "mentoring",
    "presentation",
    "research",
    "adaptability",
}


# ============================================================
# ACTION VERBS
# ============================================================

ACTION_VERBS = {
    "achieved",
    "administered",
    "analyzed",
    "architected",
    "automated",
    "built",
    "collaborated",
    "configured",
    "created",
    "debugged",
    "decreased",
    "delivered",
    "deployed",
    "designed",
    "developed",
    "directed",
    "documented",
    "engineered",
    "enhanced",
    "established",
    "evaluated",
    "executed",
    "implemented",
    "improved",
    "increased",
    "integrated",
    "launched",
    "led",
    "maintained",
    "managed",
    "migrated",
    "modernized",
    "optimized",
    "orchestrated",
    "performed",
    "planned",
    "programmed",
    "refactored",
    "reduced",
    "resolved",
    "scaled",
    "streamlined",
    "tested",
    "trained",
    "transformed",
    "troubleshot",
    "validated",
}


# ============================================================
# ALIASES
# ============================================================

ALIASES = {
    # --------------------------------------------------------
    # C++
    # --------------------------------------------------------
    "c plus plus": "c++",
    "cpp": "c++",
    "c + +": "c++",

    # --------------------------------------------------------
    # C#
    # --------------------------------------------------------
    "c sharp": "c#",
    "c-sharp": "c#",

    # --------------------------------------------------------
    # Node
    # --------------------------------------------------------
    "node.js": "nodejs",
    "node js": "nodejs",

    # --------------------------------------------------------
    # Next.js
    # --------------------------------------------------------
    "next.js": "nextjs",
    "next js": "nextjs",

    # --------------------------------------------------------
    # React
    # --------------------------------------------------------
    "react.js": "react",
    "react js": "react",

    # --------------------------------------------------------
    # Vue
    # --------------------------------------------------------
    "vue.js": "vue",
    "vue js": "vue",

    # --------------------------------------------------------
    # HTML / CSS
    # --------------------------------------------------------
    "html 5": "html5",
    "css 3": "css3",

    # --------------------------------------------------------
    # PostgreSQL
    # --------------------------------------------------------
    "postgres": "postgresql",

    # --------------------------------------------------------
    # Scikit-learn
    # --------------------------------------------------------
    "sklearn": "scikit-learn",

    # --------------------------------------------------------
    # Kubernetes
    # --------------------------------------------------------
    "k8s": "kubernetes",

    # --------------------------------------------------------
    # Cloud
    # --------------------------------------------------------
    "amazon web services": "aws",
    "microsoft azure": "azure",
    "google cloud platform": "gcp",
    "google cloud": "gcp",

    # --------------------------------------------------------
    # CI/CD
    # --------------------------------------------------------
    "ci cd": "ci/cd",
    "ci-cd": "ci/cd",
    "continuous integration and continuous delivery": "ci/cd",

    # --------------------------------------------------------
    # REST
    # --------------------------------------------------------
    "restful api": "rest api",
    "restful apis": "rest api",
    "rest apis": "rest api",

    # --------------------------------------------------------
    # ORM
    # --------------------------------------------------------
    "object relational mapping": "orm",

    # --------------------------------------------------------
    # SDLC
    # --------------------------------------------------------
    "sdlc": "software development lifecycle",

    # --------------------------------------------------------
    # Networking
    # --------------------------------------------------------
    "network": "networking",
    "network system": "networking systems",
    "network systems": "networking systems",
    "computer network": "computer networking",
    "computer networks": "computer networking",

    # --------------------------------------------------------
    # Federated Learning
    # --------------------------------------------------------
    "federated machine learning": "federated learning",
    "federated learning system": "federated learning",
    "federated learning systems": "federated learning",
    "federated averaging": "fedavg",
    "federated average": "fedavg",

    # --------------------------------------------------------
    # SHA-256
    # --------------------------------------------------------
    "sha256": "sha-256",
    "sha 256": "sha-256",

    # --------------------------------------------------------
    # AI / ML
    # --------------------------------------------------------
    "artificial intelligence": "artificial intelligence",
    "machine-learning": "machine learning",
    "deep-learning": "deep learning",
    "gen ai": "generative ai",
    "genai": "generative ai",
    "large language model": "llm",
    "large language models": "llm",
}


# ============================================================
# NORMALIZATION
# ============================================================

def get_canonical_skill(skill: str) -> str:
    """
    Return the canonical representation of a skill.

    Normalization:
    - converts to string
    - strips surrounding whitespace
    - case-folds
    - collapses repeated whitespace
    - resolves aliases
    - safely handles chained aliases
    """

    if not skill:
        return ""

    normalized = " ".join(
        str(skill).strip().casefold().split()
    )

    visited: set[str] = set()

    while normalized in ALIASES:

        if normalized in visited:
            break

        visited.add(normalized)

        normalized = (
            str(ALIASES[normalized])
            .strip()
            .casefold()
        )

        normalized = " ".join(
            normalized.split()
        )

    return normalized


def normalize_keyword(value: str) -> str:
    """
    Normalize a keyword while preserving meaningful symbols.
    """

    return get_canonical_skill(value)


# ============================================================
# CATEGORY MAP
# ============================================================

CATEGORY_MAP = {
    "Programming": PROGRAMMING,
    "Frontend": FRONTEND,
    "Backend": BACKEND,
    "Database": DATABASE,
    "AI/ML": AI_ML | AI_ML_TOOLS,
    "Cloud": CLOUD,
    "DevOps": DEVOPS,
    "Tools": TOOLS,
    "Engineering": ENGINEERING,
    "Networking": NETWORKING,
    "Blockchain": BLOCKCHAIN,
    "Mobile": MOBILE,
    "Security": SECURITY,
    "Professional": PROFESSIONAL,
}


# ============================================================
# CATEGORY ALIASES
# ============================================================

CATEGORY_ALIASES = {
    "programming": "Programming",
    "programming languages": "Programming",

    "frontend": "Frontend",
    "front end": "Frontend",
    "front-end": "Frontend",

    "backend": "Backend",
    "back end": "Backend",
    "back-end": "Backend",

    "database": "Database",
    "databases": "Database",

    "ai": "AI/ML",
    "ml": "AI/ML",
    "ai/ml": "AI/ML",
    "ai ml": "AI/ML",
    "machine learning": "AI/ML",

    "cloud": "Cloud",

    "devops": "DevOps",

    "tools": "Tools",

    "engineering": "Engineering",

    "network": "Networking",
    "networking": "Networking",

    "blockchain": "Blockchain",

    "mobile": "Mobile",

    "security": "Security",

    "professional": "Professional",
}


# ============================================================
# NORMALIZED CATEGORY DATABASE
# ============================================================

def get_skill_categories() -> dict[str, set[str]]:
    """
    Return a normalized copy of the central category database.
    """

    return {
        category: {
            get_canonical_skill(skill)
            for skill in skills
            if skill
        }
        for category, skills in CATEGORY_MAP.items()
    }


NORMALIZED_CATEGORY_MAP = get_skill_categories()


# ============================================================
# SKILL CATEGORY HELPERS
# ============================================================

def get_category_for_skill(skill: str) -> str | None:
    """
    Return the primary category for a skill.

    Category priority follows CATEGORY_MAP order.
    """

    normalized = get_canonical_skill(skill)

    if not normalized:
        return None

    for category, skills in NORMALIZED_CATEGORY_MAP.items():

        if normalized in skills:
            return category

    return None


def get_categories_for_skill(skill: str) -> list[str]:
    """
    Return every category containing a skill.

    Duplicate category matches are impossible because the
    result is constructed from unique category names.
    """

    normalized = get_canonical_skill(skill)

    if not normalized:
        return []

    return [
        category
        for category, skills in NORMALIZED_CATEGORY_MAP.items()
        if normalized in skills
    ]


def is_known_skill(skill: str) -> bool:
    """
    Determine whether a skill exists in the database.
    """

    normalized = get_canonical_skill(skill)

    if not normalized:
        return False

    return any(
        normalized in skills
        for skills in NORMALIZED_CATEGORY_MAP.values()
    )


# ============================================================
# ALL TECHNOLOGIES
# ============================================================

ALL_TECHNOLOGIES: set[str] = set()

for category_skills in NORMALIZED_CATEGORY_MAP.values():
    ALL_TECHNOLOGIES.update(category_skills)


# ============================================================
# ALL CANONICAL SKILLS
# ============================================================

def get_all_canonical_skills() -> set[str]:
    """
    Return every known canonical skill.
    """

    skills: set[str] = set()

    for category_skills in NORMALIZED_CATEGORY_MAP.values():
        skills.update(category_skills)

    return skills


ALL_CANONICAL_SKILLS = get_all_canonical_skills()


# ============================================================
# JOB REQUIREMENTS
# ============================================================

ALL_JOB_REQUIREMENTS = sorted(
    ALL_TECHNOLOGIES
    | {
        "software development",
        "software engineering",
        "software development lifecycle",
        "testing",
        "unit testing",
        "integration testing",
        "test automation",
        "continuous integration",
        "continuous delivery",
        "automation",
        "distributed systems",
        "distributed applications",
        "networking",
        "networking systems",
        "network design",
        "synchronous",
        "asynchronous",
        "asynchronous design",
        "scalable systems",
        "system design",
        "system architecture",
        "api design",
        "code review",
        "version control",
        "agile",
        "scrum",
    }
)


# ============================================================
# DEMONSTRATED SKILL CONFIGURATION
# ============================================================

DEMONSTRATED_SKILL_SECTIONS = (
    "skills",
    "projects",
    "experience",
    "internship",
    "summary",
)


# ============================================================
# INDUSTRY-RELEVANT SKILLS
# ============================================================

INDUSTRY_SKILLS = {
    get_canonical_skill(skill)
    for skill in {
        "docker",
        "linux",
        "fastapi",
        "testing",
        "api",
        "rest api",
        "postgresql",
        "mongodb",
        "redis",
        "kubernetes",
        "ci/cd",
        "federated learning",
        "machine learning",
    }
}


# ============================================================
# CANONICAL SKILL DATABASE
# ============================================================

CANONICAL_SKILL_DATABASE = NORMALIZED_CATEGORY_MAP


# ============================================================
# LEGACY COMPATIBILITY EXPORTS
# ============================================================

TECHNICAL = ALL_TECHNOLOGIES

NETWORK = NETWORKING

AI = AI_ML

DATABASES = DATABASE

FRONT_END = FRONTEND

BACK_END = BACKEND


# ============================================================
# ROLE PROFILES
# ============================================================

ROLE_PROFILES = {
    "software_engineer": {
        "title": "Software Engineer",
        "keywords": {
            "python",
            "java",
            "c++",
            "c#",
            "javascript",
            "typescript",
            "sql",
            "git",
            "data structures",
            "algorithms",
            "object oriented programming",
            "software development",
            "testing",
            "debugging",
            "api development",
            "system design",
            "docker",
        },
    },

    "backend_engineer": {
        "title": "Backend Engineer",
        "keywords": {
            "python",
            "java",
            "go",
            "fastapi",
            "flask",
            "django",
            "spring",
            "spring boot",
            "nodejs",
            "express",
            "rest api",
            "graphql",
            "microservices",
            "sql",
            "postgresql",
            "mysql",
            "mongodb",
            "redis",
            "docker",
            "kubernetes",
        },
    },

    "frontend_engineer": {
        "title": "Frontend Engineer",
        "keywords": {
            "html",
            "html5",
            "css",
            "css3",
            "javascript",
            "typescript",
            "react",
            "angular",
            "vue",
            "nextjs",
            "redux",
            "tailwind",
            "webpack",
            "vite",
            "responsive design",
            "accessibility",
            "frontend development",
        },
    },

    "full_stack_engineer": {
        "title": "Full Stack Engineer",
        "keywords": {
            "html",
            "css",
            "javascript",
            "typescript",
            "react",
            "angular",
            "vue",
            "nodejs",
            "python",
            "java",
            "fastapi",
            "django",
            "spring",
            "rest api",
            "graphql",
            "sql",
            "mongodb",
            "docker",
            "git",
        },
    },

    "data_scientist": {
        "title": "Data Scientist",
        "keywords": {
            "python",
            "r",
            "sql",
            "pandas",
            "numpy",
            "scipy",
            "scikit-learn",
            "tensorflow",
            "pytorch",
            "machine learning",
            "deep learning",
            "statistics",
            "data analysis",
            "data visualization",
            "feature engineering",
            "model evaluation",
        },
    },

    "machine_learning_engineer": {
        "title": "Machine Learning Engineer",
        "keywords": {
            "python",
            "machine learning",
            "deep learning",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "numpy",
            "pandas",
            "mlops",
            "model deployment",
            "model training",
            "feature engineering",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "federated learning",
        },
    },

    "ai_engineer": {
        "title": "AI Engineer",
        "keywords": {
            "python",
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "generative ai",
            "llm",
            "rag",
            "embeddings",
            "transformers",
            "pytorch",
            "tensorflow",
            "langchain",
            "vector database",
            "model deployment",
            "docker",
            "cloud",
        },
    },

    "devops_engineer": {
        "title": "DevOps Engineer",
        "keywords": {
            "linux",
            "docker",
            "kubernetes",
            "jenkins",
            "github actions",
            "gitlab ci",
            "ci/cd",
            "continuous integration",
            "continuous delivery",
            "terraform",
            "ansible",
            "aws",
            "azure",
            "gcp",
            "monitoring",
            "prometheus",
            "grafana",
            "infrastructure as code",
        },
    },

    "cloud_engineer": {
        "title": "Cloud Engineer",
        "keywords": {
            "aws",
            "azure",
            "gcp",
            "cloud computing",
            "cloud architecture",
            "ec2",
            "s3",
            "lambda",
            "docker",
            "kubernetes",
            "terraform",
            "ansible",
            "networking",
            "security",
        },
    },

    "network_engineer": {
        "title": "Network Engineer",
        "keywords": {
            "networking",
            "network design",
            "network architecture",
            "tcp/ip",
            "dns",
            "dhcp",
            "routing",
            "switching",
            "firewall",
            "vpn",
            "lan",
            "wan",
            "ethernet",
            "network security",
            "load balancing",
        },
    },

    "security_engineer": {
        "title": "Security Engineer",
        "keywords": {
            "cybersecurity",
            "information security",
            "application security",
            "network security",
            "authentication",
            "authorization",
            "oauth",
            "jwt",
            "encryption",
            "cryptography",
            "sha-256",
            "secure coding",
            "vulnerability assessment",
            "penetration testing",
        },
    },
}


# ============================================================
# ROLE KEYWORD WEIGHTS
# ============================================================

def _build_role_keyword_weights() -> dict[str, dict[str, int]]:
    """
    Build weighted keyword maps from ROLE_PROFILES.

    Weight scale:

        5 = critical
        4 = high
        3 = important
        2 = supporting
        1 = optional
    """

    result: dict[str, dict[str, int]] = {}

    for role, profile in ROLE_PROFILES.items():

        weights: dict[str, int] = {}

        def add_keyword(
            keyword: str,
            weight: int = 3,
        ) -> None:

            if not isinstance(keyword, str):
                return

            normalized = get_canonical_skill(keyword)

            if not normalized:
                return

            weight = max(
                1,
                min(5, int(weight)),
            )

            previous = weights.get(
                normalized,
                0,
            )

            if weight > previous:
                weights[normalized] = weight

        def process(
            value,
            default_weight: int = 3,
        ) -> None:

            if value is None:
                return

            if isinstance(value, str):
                add_keyword(
                    value,
                    default_weight,
                )
                return

            if isinstance(value, dict):

                for key, item in value.items():

                    if isinstance(
                        item,
                        (int, float),
                    ):
                        add_keyword(
                            key,
                            int(item),
                        )
                        continue

                    key_lower = (
                        str(key)
                        .strip()
                        .lower()
                    )

                    if key_lower in {
                        "critical",
                        "critical_keywords",
                        "must_have",
                        "must-have",
                        "must",
                        "required",
                    }:
                        process(item, 5)

                    elif key_lower in {
                        "high",
                        "high_priority",
                        "high-priority",
                    }:
                        process(item, 4)

                    elif key_lower in {
                        "preferred",
                        "preferred_keywords",
                        "recommended",
                        "important",
                    }:
                        process(item, 3)

                    elif key_lower in {
                        "supporting",
                        "supporting_keywords",
                        "secondary",
                    }:
                        process(item, 2)

                    elif key_lower in {
                        "optional",
                        "optional_keywords",
                    }:
                        process(item, 1)

                    elif isinstance(
                        item,
                        (list, tuple, set),
                    ):
                        process(
                            item,
                            default_weight,
                        )

                    elif isinstance(
                        item,
                        dict,
                    ):
                        process(
                            item,
                            default_weight,
                        )

                    else:
                        process(
                            key,
                            default_weight,
                        )

                return

            if isinstance(
                value,
                (list, tuple, set),
            ):
                for item in value:
                    process(
                        item,
                        default_weight,
                    )

        process(
            profile.get("keywords", {}),
            3,
        )

        result[role] = weights

    return result


ROLE_KEYWORD_WEIGHTS = _build_role_keyword_weights()


# ============================================================
# ROLE KEYWORD WEIGHT HELPERS
# ============================================================

def get_role_keyword_weights(
    role: str,
) -> dict[str, int]:
    """
    Return normalized keyword weights for a role.
    """

    if not role:
        return {}

    role_key = str(role).strip()

    if role_key in ROLE_KEYWORD_WEIGHTS:
        return dict(
            ROLE_KEYWORD_WEIGHTS[role_key]
        )

    role_lower = role_key.lower()

    for existing_role, weights in (
        ROLE_KEYWORD_WEIGHTS.items()
    ):
        if (
            str(existing_role).lower()
            == role_lower
        ):
            return dict(weights)

    return {}


def get_keyword_weight(
    role: str,
    keyword: str,
    default: int = 1,
) -> int:
    """
    Safely retrieve the weight of a keyword
    for a role.
    """

    if not keyword:
        return default

    weights = get_role_keyword_weights(
        role
    )

    normalized = get_canonical_skill(
        keyword
    )

    return int(
        weights.get(
            normalized,
            default,
        )
    )


# ============================================================
# ROLE PROFILE VALIDATION
# ============================================================

def validate_role_keyword_weights() -> dict:
    """
    Validate the generated role-weight database.
    """

    roles = len(
        ROLE_KEYWORD_WEIGHTS
    )

    total_keywords = sum(
        len(weights)
        for weights in ROLE_KEYWORD_WEIGHTS.values()
    )

    invalid_weights = []

    for role, weights in (
        ROLE_KEYWORD_WEIGHTS.items()
    ):

        for keyword, weight in weights.items():

            if not isinstance(
                keyword,
                str,
            ):
                invalid_weights.append(
                    {
                        "role": role,
                        "keyword": keyword,
                        "weight": weight,
                    }
                )

            if not isinstance(
                weight,
                int,
            ):
                invalid_weights.append(
                    {
                        "role": role,
                        "keyword": keyword,
                        "weight": weight,
                    }
                )

            elif weight < 1 or weight > 5:
                invalid_weights.append(
                    {
                        "role": role,
                        "keyword": keyword,
                        "weight": weight,
                    }
                )

    return {
        "valid": len(
            invalid_weights
        ) == 0,
        "roles": roles,
        "total_keywords": total_keywords,
        "invalid_weights": invalid_weights,
    }


ROLE_KEYWORD_WEIGHT_VALIDATION = (
    validate_role_keyword_weights()
)