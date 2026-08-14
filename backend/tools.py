import json
from pathlib import Path
from langchain_core.tools import tool

BASE_DIR = Path(__file__).resolve().parent.parent

PROJECTS_FILE = BASE_DIR / "data" / "projects.json"


@tool
def search_skills(query: str):
    """
    Search Himanshi's technical skills.

    Use this tool when the user asks about
    programming languages, AI/ML skills,
    data analytics skills, frameworks,
    databases, or other technical skills.
    """

    SKILLS_FILE = BASE_DIR / "data" / "skills.json"

    with open(
        SKILLS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        skills = json.load(file)

    query_lower = query.lower()

    results = []

    # --------------------------------------------------
    # CATEGORY-BASED SEARCH
    # --------------------------------------------------

    category_keywords = {
        "programming": [
            "programming",
            "programming language",
            "programming languages",
            "coding",
            "language",
            "languages"
        ],

        "data_analytics": [
            "data analytics",
            "data analysis",
            "analytics",
            "data analyst"
        ],

        "ai_and_ml": [
            "ai",
            "artificial intelligence",
            "machine learning",
            "generative ai",
            "rag",
            "agentic ai",
            "llm",
            "embeddings"
        ],

        "frameworks_and_tools": [
            "framework",
            "frameworks",
            "tools",
            "libraries",
            "libraries and tools"
        ],

        "databases": [
            "database",
            "databases",
            "sql database"
        ]
    }

    # --------------------------------------------------
    # CHECK WHETHER QUERY MATCHES A CATEGORY
    # --------------------------------------------------

    matched_categories = []

    for category, keywords in category_keywords.items():

        for keyword in keywords:

            if keyword in query_lower:

                matched_categories.append(category)
                break

    # --------------------------------------------------
    # RETURN COMPLETE CATEGORY
    # --------------------------------------------------

    for category in matched_categories:

        if category not in skills:
            continue

        skill_list = skills[category]

        if not isinstance(skill_list, list):
            continue

        for skill in skill_list:

            results.append({
                "score": 1,
                "category": category,
                "skill": skill
            })

    # --------------------------------------------------
    # FALLBACK: INDIVIDUAL SKILL MATCHING
    # --------------------------------------------------

    if not results:

        query_words = set(
            query_lower.split()
        )

        for category, skill_list in skills.items():

            if not isinstance(skill_list, list):
                continue

            for skill in skill_list:

                skill_lower = skill.lower()

                score = 0

                for word in query_words:

                    if word in skill_lower:

                        score += 1

                if score > 0:

                    results.append({
                        "score": score,
                        "category": category,
                        "skill": skill
                    })

    return results

@tool
def search_projects(query: str):
    """
    Search Himanshi's portfolio projects.

    Use this tool when the user asks about
    specific projects, project technologies,
    project domains, project features, or
    finding projects related to a topic.
    """

   

    with open(PROJECTS_FILE, "r", encoding="utf-8") as file:
        projects = json.load(file)

    query_words = set(
        query.lower().split()
    )

    results = []

    for project in projects:

        searchable_text = " ".join([
            project.get("name", ""),
            project.get("domain", ""),
            project.get("type", ""),
            project.get("description", ""),
            project.get("problem", ""),
            project.get("solution", ""),
            " ".join(project.get("technologies", [])),
            " ".join(project.get("key_features", []))
        ]).lower()

        score = 0

        for word in query_words:

            if word in searchable_text:
                score += 1

        if score > 0:

            results.append({
                "score": score,
                "project": project
            })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results

"""if __name__ == "__main__":

    query = "computer vision"

    results = search_projects.invoke({
        "query": query
    })

    print("\nProject Search Results:\n")

    for result in results:

        project = result["project"]

        print(f"Project: {project['name']}")
        print(f"Score: {result['score']}")
        print(f"Domain: {project['domain']}")
        print(
            f"Technologies: "
            f"{', '.join(project['technologies'])}"
        )

        print("-" * 50)"""

if __name__ == "__main__":

    query = "programming languages"

    results = search_skills.invoke({
        "query": query
    })

    print("\nSkill Search Results:\n")

    for result in results:

        print(
            f"Category: {result['category']}"
        )

        print(
            f"Skill: {result['skill']}"
        )

        print("-" * 50)


