import requests
import json

from retriever import PortfolioRetriever
from tools import search_projects, search_skills


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:latest"


# ============================================================
# RAG RETRIEVER
# ============================================================

retriever = PortfolioRetriever()


# ============================================================
# TOOL DEFINITIONS
# ============================================================

TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "search_projects",

            "description": (
                "Search Himanshi's portfolio projects. "
                "Use this when the user asks about projects, "
                "project technologies, project domains, "
                "project features, or projects related to "
                "a particular topic."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The project search query."
                        )
                    }
                },

                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "search_skills",

            "description": (
                "Search Himanshi's technical skills. "
                "Use this when the user asks about "
                "programming languages, AI/ML skills, "
                "data analytics, frameworks, tools, "
                "or databases."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The skill search query."
                        )
                    }
                },

                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "portfolio_rag",

            "description": (
                "Search the complete portfolio knowledge "
                "base using semantic retrieval. Use this "
                "for resume information, education, "
                "experience, certifications, career "
                "information, or portfolio information "
                "that is not specifically handled by "
                "another tool."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The portfolio information "
                            "to search for."
                        )
                    }
                },

                "required": ["query"]
            }
        }
    }

]


# ============================================================
# OLLAMA
# ============================================================

def call_ollama(messages):

    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# RAG TOOL
# ============================================================

def run_portfolio_rag(query):

    print("\n[RAG] Searching portfolio knowledge base...")
    print(f"[RAG] Query: {query}")

    results = retriever.search(
        query,
        top_k=5
    )

    if not results:

        return {
            "message": (
                "No relevant information was found "
                "in the portfolio knowledge base."
            )
        }

    context_parts = []

    for result in results:

        metadata = result.get(
            "metadata",
            {}
        )

        content = result.get(
            "content",
            ""
        )

        context_parts.append(
            f"""
SOURCE: {metadata.get("source", "unknown")}
SECTION: {metadata.get("section", "unknown")}

CONTENT:
{content}
"""
        )

    return {
        "results": context_parts
    }


# ============================================================
# TOOL EXECUTOR
# ============================================================

def execute_tool(tool_call):

    function_name = (
        tool_call["function"]["name"]
    )

    arguments = (
        tool_call["function"]["arguments"]
    )

    print(
        f"\n[TOOL CALL] {function_name}"
    )

    print(
        f"[TOOL ARGUMENTS] {arguments}"
    )


    if function_name == "search_projects":

        return search_projects.invoke(
            arguments
        )


    if function_name == "search_skills":

        return search_skills.invoke(
            arguments
        )


    if function_name == "portfolio_rag":

        return run_portfolio_rag(
            arguments["query"]
        )


    return {
        "error": (
            f"Unknown tool: {function_name}"
        )
    }


# ============================================================
# AGENT
# ============================================================

def run_agent(question):

    messages = [

        {
            "role": "system",

            "content": """
You are Himanshi's AI portfolio assistant.

You have three capabilities:

1. search_projects
Use for questions about projects,
project technologies, domains,
features, or project-related topics.

2. search_skills
Use for questions about technical skills,
programming languages, AI/ML, data analytics,
frameworks, tools, and databases.

3. portfolio_rag
Use for resume, education, experience,
certifications, career information,
or other portfolio information.

IMPORTANT:
Use a tool whenever the answer requires
information from Himanshi's portfolio.

Do not invent portfolio information.

After receiving a tool result, answer
the user's original question clearly
and concisely.
"""
        },

        {
            "role": "user",
            "content": question
        }

    ]


    print(
        "\n[AGENT] Sending question to Gemma..."
    )

    print(
        f"[USER] {question}"
    )


    # --------------------------------------------------------
    # FIRST CALL
    # --------------------------------------------------------

    response = call_ollama(
        messages
    )

    assistant_message = (
        response["message"]
    )


    # --------------------------------------------------------
    # CHECK TOOL CALL
    # --------------------------------------------------------

    tool_calls = (
        assistant_message.get(
            "tool_calls"
        )
    )


    if tool_calls:

        print(
            f"\n[AGENT] Gemma requested "
            f"{len(tool_calls)} tool(s)."
        )


        messages.append(
            assistant_message
        )


        # ----------------------------------------------------
        # EXECUTE TOOLS
        # ----------------------------------------------------

        for tool_call in tool_calls:

            result = execute_tool(
                tool_call
            )

            messages.append(
                {
                    "role": "tool",

                    "content": json.dumps(
                        result,
                        ensure_ascii=False
                    )
                }
            )


        # ----------------------------------------------------
        # SECOND CALL
        # ----------------------------------------------------

        print(
            "\n[AGENT] Sending tool results "
            "back to Gemma..."
        )

        final_response = call_ollama(
            messages
        )

        return final_response[
            "message"
        ]["content"]


    # --------------------------------------------------------
    # NO TOOL CALL
    # --------------------------------------------------------

    return assistant_message.get(
        "content",
        ""
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    question = question = (
    "What programming languages does Himanshi know?"
    )

    answer = run_agent(
        question
    )

    print("\n")
    print("=" * 70)
    print("FINAL ANSWER")
    print("=" * 70)

    print(answer)

    print("=" * 70)