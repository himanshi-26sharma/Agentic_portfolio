import json
import contextlib
import io
import sys

from pathlib import Path

from mcp.server.mcpserver import MCPServer


# ============================================================
# MCP SERVER
# ============================================================

mcp = MCPServer(
    "Himanshi Portfolio Server"
)


# ============================================================
# PATH
# ============================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

PROJECTS_FILE = (
    BASE_DIR
    / "data"
    / "projects.json"
)


# ============================================================
# PROJECT SEARCH TOOL
# ============================================================

@mcp.tool()
def search_projects(query: str) -> list:
    """
    Search Himanshi's portfolio projects.

    Use this tool when the user asks about
    projects, project technologies, domains,
    features, or projects related to a topic.
    """

    with open(
        PROJECTS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        projects = json.load(file)

    query_words = set(
        query.lower().split()
    )

    results = []

    for project in projects:

        searchable_text = " ".join([

            project.get(
                "name",
                ""
            ),

            project.get(
                "domain",
                ""
            ),

            project.get(
                "type",
                ""
            ),

            project.get(
                "description",
                ""
            ),

            project.get(
                "problem",
                ""
            ),

            project.get(
                "solution",
                ""
            ),

            " ".join(
                project.get(
                    "technologies",
                    []
                )
            ),

            " ".join(
                project.get(
                    "key_features",
                    []
                )
            )

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

    return results[:5]


# ============================================================
# SKILL SEARCH TOOL
# ============================================================

@mcp.tool()
def search_skills_mcp(query: str) -> list:
    """
    Search Himanshi's technical skills.

    Use this for programming languages,
    AI/ML skills, data analytics, frameworks,
    tools, and databases.
    """

    # Import here so any initialization output
    # can be captured.
    from tools import search_skills

    captured_output = io.StringIO()

    with contextlib.redirect_stdout(
        captured_output
    ):

        result = search_skills.invoke({
            "query": query
        })

    # Send diagnostic output to stderr.
    diagnostic_output = (
        captured_output.getvalue()
    )

    if diagnostic_output:

        print(
            diagnostic_output,
            file=sys.stderr,
            end=""
        )

    return result


# ============================================================
# PORTFOLIO RAG TOOL
# ============================================================

@mcp.tool()
def portfolio_rag(query: str) -> list:
    """
    Search the complete Himanshi portfolio
    knowledge base using semantic retrieval.
    """

    from retriever import PortfolioRetriever

    captured_output = io.StringIO()

    with contextlib.redirect_stdout(
        captured_output
    ):

        retriever = PortfolioRetriever()

        results = retriever.search(
            query,
            top_k=5
        )

    # Send diagnostic output to stderr.
    diagnostic_output = (
        captured_output.getvalue()
    )

    if diagnostic_output:

        print(
            diagnostic_output,
            file=sys.stderr,
            end=""
        )

    # --------------------------------------------------------
    # NO RESULTS
    # --------------------------------------------------------

    if not results:

        return [
            {
                "message":
                "No relevant information was found "
                "in the portfolio knowledge base."
            }
        ]

    # --------------------------------------------------------
    # FORMAT RESULTS
    # --------------------------------------------------------

    formatted_results = []

    for result in results:

        metadata = result.get(
            "metadata",
            {}
        )

        formatted_results.append({

            "source": metadata.get(
                "source",
                "unknown"
            ),

            "section": metadata.get(
                "section",
                "unknown"
            ),

            "content": result.get(
                "content",
                ""
            )

        })

    return formatted_results


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    # IMPORTANT:
    # Do not use print() here.
    #
    # MCP stdio transport uses stdout for JSON-RPC
    # communication.

    mcp.run(
        transport="stdio"
    )