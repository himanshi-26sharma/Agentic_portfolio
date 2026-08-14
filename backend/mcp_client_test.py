import asyncio
import sys

from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    # ============================================================
    # MCP SERVER PARAMETERS
    # ============================================================

    server_params = StdioServerParameters(

        command=sys.executable,

        args=[
            "backend/mcp_server.py"
        ]

    )


    # ============================================================
    # CONNECT TO MCP SERVER
    # ============================================================

    async with Client(
        stdio_client(server_params)
    ) as client:

        print(
            "\n[MCP] Connected to server."
        )


        # ========================================================
        # DISCOVER AVAILABLE TOOLS
        # ========================================================

        result = await client.list_tools()


        print(
            "\n[MCP] Available Tools:"
        )

        print(
            "-" * 60
        )


        for tool in result.tools:

            print(
                f"Tool: {tool.name}"
            )

            print(
                f"Description: {tool.description}"
            )

            print(
                "-" * 60
            )


        # ========================================================
        # TEST 1 — PROJECT SEARCH
        # ========================================================

        print(
            "\n[MCP] Calling search_projects..."
        )


        project_result = await client.call_tool(

            "search_projects",

            {
                "query": "computer vision"
            }

        )


        print(
            "\n[MCP] Project Tool Result:"
        )

        print(
            project_result
        )


        # ========================================================
        # TEST 2 — SKILLS SEARCH
        # ========================================================

        print(
            "\n[MCP] Calling search_skills_mcp..."
        )


        skill_result = await client.call_tool(

            "search_skills_mcp",

            {
                "query": "programming languages"
            }

        )


        print(
            "\n[MCP] Skills Tool Result:"
        )

        print(
            skill_result
        )


        # ========================================================
        # TEST 3 — PORTFOLIO RAG
        # ========================================================

        print(
            "\n[MCP] Calling portfolio_rag..."
        )


        rag_result = await client.call_tool(

            "portfolio_rag",

            {
                "query":
                "What programming languages does Himanshi know?"
            }

        )


        print(
            "\n[MCP] RAG Tool Result:"
        )

        print(
            rag_result
        )


# ================================================================
# START CLIENT
# ================================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )