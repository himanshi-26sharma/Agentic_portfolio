import asyncio
import json
import requests

from mcp import Client
from mcp import StdioServerParameters
from mcp import stdio_client

from agent_router import (
    choose_agent,
    get_agent_prompt,
)


# ============================================================
# OLLAMA
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/chat"

MODEL = "gemma4:latest"


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
# AGENT TOOL POLICY
# ============================================================

AGENT_TOOLS = {

    "bubbly": [
        "search_projects",
        "portfolio_rag"
    ],

    "mochi": [
        "search_skills_mcp",
        "portfolio_rag"
    ],

    "poppy": [
        "portfolio_rag"
    ]

}


# ============================================================
# MCP → OLLAMA TOOL FORMAT
# ============================================================

def convert_mcp_tools(
    mcp_tools,
    allowed_tools
):

    tools = []

    for tool in mcp_tools:

        if tool.name not in allowed_tools:
            continue

        tools.append({

            "type": "function",

            "function": {

                "name": tool.name,

                "description":
                    tool.description or "",

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
# EXECUTE AGENT
# ============================================================

async def run_agent(
    question,
    selected_agent=None
):

    # ========================================================
    # 1. ROUTE QUESTION
    # ========================================================

    agent = choose_agent(
        question,
        selected_agent
    )

    print(
        f"\n[EXECUTOR] Agent → {agent}"
    )


    # ========================================================
    # 2. GENERAL AGENT
    # ========================================================

    if agent == "general":

        messages = [

            {
                "role": "system",

                "content":
                    get_agent_prompt(
                        "general"
                    )
            },

            {
                "role": "user",

                "content": question
            }

        ]

        response = call_ollama(
            messages
        )

        return {

            "agent": "general",

            "answer":
                response["message"]["content"]

        }


    # ========================================================
    # 3. MCP SERVER CONFIGURATION
    # ========================================================

    server_params = StdioServerParameters(

        command="python",

        args=[
            "backend/mcp_server.py"
        ]

    )


    # ========================================================
    # 4. CONNECT TO MCP SERVER
    # ========================================================

    async with Client(
        stdio_client(server_params)
    ) as client:

        print(
            "\n[MCP] Connected to server."
        )


        # ====================================================
        # 5. DISCOVER MCP TOOLS
        # ====================================================

        tools_result = (
            await client.list_tools()
        )

        mcp_tools = (
            tools_result.tools
        )


        print(
            "\n[MCP] Available tools:"
        )

        for tool in mcp_tools:

            print(
                f"  - {tool.name}"
            )


        # ====================================================
        # 6. FILTER TOOLS FOR AGENT
        # ====================================================

        allowed_tools = (
            AGENT_TOOLS.get(
                agent,
                []
            )
        )


        ollama_tools = (
            convert_mcp_tools(
                mcp_tools,
                allowed_tools
            )
        )


        print(
            "\n[EXECUTOR] Tools available "
            f"to {agent}:"
        )

        for tool in ollama_tools:

            print(
                "  - "
                + tool["function"]["name"]
            )


        # ====================================================
        # 7. AGENT SYSTEM PROMPT
        # ====================================================

        system_prompt = (
            get_agent_prompt(
                agent
            )
        )


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


        # ====================================================
        # 8. FIRST GEMMA CALL
        # ====================================================

        print(
            "\n[EXECUTOR] Sending "
            "question to Gemma..."
        )


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


        # ====================================================
        # 9. TOOL CALL LOOP
        # ====================================================

        while assistant_message.get(
            "tool_calls"
        ):

            tool_calls = (
                assistant_message[
                    "tool_calls"
                ]
            )


            print(
                f"\n[EXECUTOR] Gemma requested "
                f"{len(tool_calls)} tool(s)."
            )


            # ------------------------------------------------
            # EXECUTE EACH TOOL
            # ------------------------------------------------

            for tool_call in tool_calls:

                function = (
                    tool_call[
                        "function"
                    ]
                )


                tool_name = (
                    function[
                        "name"
                    ]
                )


                arguments = (
                    function[
                        "arguments"
                    ]
                )


                print(
                    "\n[TOOL CALL]"
                )

                print(
                    f"Name: {tool_name}"
                )

                print(
                    f"Arguments: {arguments}"
                )


                # --------------------------------------------
                # SAFETY CHECK
                # --------------------------------------------

                if tool_name not in allowed_tools:

                    print(
                        "[EXECUTOR] Tool not "
                        "allowed for this agent."
                    )

                    tool_text = (
                        "This tool is not "
                        "available to this agent."
                    )

                else:

                    # ----------------------------------------
                    # CALL MCP TOOL
                    # ----------------------------------------

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


                print(
                    "\n[TOOL RESULT]"
                )

                print(
                    tool_text
                )


                # --------------------------------------------
                # SEND RESULT BACK TO GEMMA
                # --------------------------------------------

                messages.append({

                    "role": "tool",

                    "content":
                        tool_text

                })


            # =================================================
            # 10. GEMMA PROCESSES TOOL RESULT
            # =================================================

            print(
                "\n[EXECUTOR] Sending "
                "tool result back to Gemma..."
            )


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


        # ====================================================
        # 11. FINAL ANSWER
        # ====================================================

        answer = (
            assistant_message.get(
                "content",
                ""
            )
        )


        print(
            "\n[EXECUTOR] Final answer generated."
        )


        return {

            "agent": agent,

            "answer": answer

        }


# ============================================================
# TEST
# ============================================================

async def main():

    questions = [

        (
            "bubbly",

            "Which projects are related "
            "to computer vision?"
        ),

        (
            "mochi",

            "What programming languages "
            "does Himanshi know?"
        ),

        (
            "poppy",

            "Tell me about Himanshi's "
            "professional background."
        )

    ]


    for selected_agent, question in questions:

        print(
            "\n"
            + "=" * 70
        )

        print(
            f"USER: {question}"
        )


        result = await run_agent(

            question,

            selected_agent

        )


        print(
            "\nAGENT:"
        )

        print(
            result["agent"]
        )


        print(
            "\nANSWER:"
        )

        print(
            result["answer"]
        )


        print(
            "=" * 70
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )