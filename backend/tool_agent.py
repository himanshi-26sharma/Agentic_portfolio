import requests
import json
from tools import search_projects, search_skills


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:latest"


# ============================================================
# TOOL DEFINITION
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_projects",
            "description": (
                "Search Himanshi's portfolio projects. "
                "Use this when the user asks about projects, "
                "project technologies, domains, features, "
                "or finding projects related to a topic."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Project search query."
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
                "programming languages, AI/ML, data analytics, "
                "frameworks, databases, or technical skills."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Skill search query."
                    }
                },
                "required": ["query"]
            }
        }
    }
]


# ============================================================
# CALL OLLAMA
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
# TOOL EXECUTION
# ============================================================

def execute_tool(tool_call):

    function_name = tool_call["function"]["name"]

    arguments = tool_call["function"]["arguments"]

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


    return {
    "error": f"Unknown tool: {function_name}"
}


# ============================================================
# AGENT LOOP
# ============================================================

def run_agent(question):

    messages = [
        {
            "role": "system",
            "content": """
You are Himanshi's AI portfolio assistant.

You have access to a project search tool.

Use the tool whenever the user asks about:
- projects
- project technologies
- project domains
- project features
- projects related to a particular topic

For other portfolio questions, answer using
the provided context or explain that the information
is unavailable.
"""
        },
        {
            "role": "user",
            "content": question
        }
    ]

    print("\n[AGENT] Sending question to Gemma...")
    print(f"[USER] {question}")

    # --------------------------------------------------------
    # FIRST LLM CALL
    # --------------------------------------------------------

    response = call_ollama(messages)

    assistant_message = response["message"]

    # --------------------------------------------------------
    # CHECK FOR TOOL CALL
    # --------------------------------------------------------

    tool_calls = assistant_message.get(
        "tool_calls"
    )

    if tool_calls:

        print(
            f"\n[AGENT] Gemma requested "
            f"{len(tool_calls)} tool(s)."
        )

        # Add assistant's tool-call message
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

            # Add tool result to conversation
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
        # SECOND LLM CALL
        # ----------------------------------------------------

        print(
            "\n[AGENT] Sending tool result back to Gemma..."
        )

        final_response = call_ollama(
            messages
        )

        return final_response[
            "message"
        ]["content"]

    # --------------------------------------------------------
    # NO TOOL REQUIRED
    # --------------------------------------------------------

    return assistant_message.get(
        "content",
        ""
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    question = (
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