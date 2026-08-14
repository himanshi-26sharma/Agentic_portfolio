import asyncio
import json
import requests

from mcp import Client, StdioServerParameters
from mcp import stdio_client


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:latest"


# ============================================================
# OLLAMA
# ============================================================

def call_ollama(messages, tools=None):

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }

    if tools:
        payload["tools"] = tools

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# MCP → OLLAMA TOOLS
# ============================================================

def convert_mcp_tools(mcp_tools):

    tools = []

    for tool in mcp_tools:

        tools.append({

            "type": "function",

            "function": {

                "name": tool.name,

                "description":
                    tool.description or "",

                # MCP v2 uses input_schema
                "parameters":
                    tool.input_schema

            }

        })

    return tools


# ============================================================
# MCP RESULT → TEXT
# ============================================================

def extract_tool_result(result):

    parts = []

    for content in result.content:

        if hasattr(content, "text"):

            parts.append(
                content.text
            )

    return "\n".join(parts)


# ============================================================
# PERSONA PROMPTS
# ============================================================

PERSONAS = {

    "bubbly": """

You are Bubbly 🫧, Himanshi's cheerful Project Guide.

Your job is to give users a fun tour of Himanshi's projects.

You specialize in:
- Projects
- Project technologies
- Project architecture
- Project features
- AI projects
- RAG projects
- Computer vision projects
- Agentic AI projects

Whenever project information is required,
use the appropriate MCP project tool.

Your personality:
- Cheerful
- Curious
- Friendly
- Slightly playful
- Professional when explaining technical details

Never invent project information.

After receiving tool results, explain them naturally.

Do not ask unnecessary follow-up questions.
""",

    "mochi": """

You are Mochi 🍡, Himanshi's friendly Skill Guide.

Your job is to give users a tour of Himanshi's technical skills.

You specialize in:
- Programming languages
- Python
- SQL
- AI/ML
- Data Analytics
- Frameworks
- Databases
- Developer tools
- Technical skills

Whenever skill information is required,
use the appropriate MCP skill tool.

Your personality:
- Sweet
- Helpful
- Encouraging
- Clear
- Slightly playful

Never invent skills.

After receiving tool results, answer naturally.

Do not ask unnecessary follow-up questions.
""",

    "poppy": """

You are Poppy 🌷, Himanshi's Resume & Career Guide.

Your job is to give users a friendly tour of Himanshi's
resume and professional background.

You specialize in:
- Education
- Resume
- Experience
- Certifications
- Career background
- Internship information
- Professional journey
- Contact guidance

Use the portfolio RAG tool whenever portfolio information
is required.

Never invent resume information.

If the user wants to contact Himanshi, explain that
you can guide them to the contact section if actual
contact information is not available to you.

Your personality:
- Warm
- Elegant
- Helpful
- Professional
- Slightly playful

Do not ask unnecessary follow-up questions.
"""
}


# ============================================================
# MAIN AGENT FUNCTION
# ============================================================

async def ask_portfolio_agent(
    question,
    selected_agent=None
):

    server_params = StdioServerParameters(

        command="py",

        args=[
            "backend/mcp_server.py"
        ]

    )


    async with stdio_client(
        server_params
    ) as (read, write):

        async with Client(
            read,
            write
        ) as client:

            tools_result = (
                await client.list_tools()
            )

            mcp_tools = tools_result.tools

            ollama_tools = convert_mcp_tools(
                mcp_tools
            )


            # ------------------------------------------------
            # SELECT PERSONA
            # ------------------------------------------------

            if selected_agent in PERSONAS:

                system_prompt = PERSONAS[
                    selected_agent
                ]

            else:

                system_prompt = """

You are the host of Himanshi's AI portfolio.

You have a small AI crew:

🫧 Bubbly — Project Guide
🍡 Mochi — Skill Guide
🌷 Poppy — Resume & Career Guide

Your job is to understand the user's request
and choose the appropriate tool.

If the user asks about projects,
introduce Bubbly naturally.

If the user asks about skills,
introduce Mochi naturally.

If the user asks about resume, education,
experience or certifications,
introduce Poppy naturally.

You can use MCP tools to retrieve actual
portfolio information.

Never invent information.

Be warm, conversational, fun and professional.

Do not ask unnecessary follow-up questions.
"""


            messages = [

                {
                    "role": "system",

                    "content":
                        system_prompt

                },

                {
                    "role": "user",

                    "content":
                        question

                }

            ]


            # ------------------------------------------------
            # GEMMA
            # ------------------------------------------------

            response = call_ollama(
                messages,
                ollama_tools
            )

            assistant_message = (
                response["message"]
            )

            messages.append(
                assistant_message
            )


            # ------------------------------------------------
            # TOOL LOOP
            # ------------------------------------------------

            while assistant_message.get(
                "tool_calls"
            ):

                for tool_call in (
                    assistant_message[
                        "tool_calls"
                    ]
                ):

                    function = (
                        tool_call["function"]
                    )

                    tool_name = (
                        function["name"]
                    )

                    arguments = (
                        function["arguments"]
                    )


                    if isinstance(
                        arguments,
                        str
                    ):

                        arguments = json.loads(
                            arguments
                        )


                    print(
                        f"[MCP] Tool: {tool_name}"
                    )


                    result = (
                        await client.call_tool(
                            tool_name,
                            arguments
                        )
                    )


                    tool_text = (
                        extract_tool_result(
                            result
                        )
                    )


                    messages.append({

                        "role": "tool",

                        "content": tool_text

                    })


                response = call_ollama(
                    messages,
                    ollama_tools
                )

                assistant_message = (
                    response["message"]
                )

                messages.append(
                    assistant_message
                )


            return {

                "answer":
                    assistant_message.get(
                        "content",
                        ""
                    ),

                "agent":
                    selected_agent,

                "tool_used":
                    None

            }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = asyncio.run(

        ask_portfolio_agent(
            "Which projects are related to computer vision?",
            "bubbly"
        )

    )

    print(
        "\nFINAL ANSWER:\n"
    )

    print(
        result["answer"]
    )