import json
import requests

from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from retriever import PortfolioRetriever
from tools import search_projects, search_skills
from memory import load_memory, save_conversation

class AgentState(TypedDict):

    question: str

    messages: list

    tool_result: str

    answer: str

    memory: list

retriever = PortfolioRetriever()   

TOOLS = [

    {
        "type": "function",

        "function": {
            "name": "search_projects",

            "description": (
                "Search Himanshi's portfolio projects. "
                "Use this for project names, project "
                "technologies, domains, features, or "
                "projects related to a topic."
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
                "Use this for programming languages, "
                "AI/ML, data analytics, frameworks, "
                "tools, and databases."
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
    },

    {
        "type": "function",

        "function": {
            "name": "portfolio_rag",

            "description": (
                "Search the complete portfolio knowledge "
                "base using semantic retrieval. Use this "
                "for resume, education, experience, "
                "certifications, and other portfolio "
                "information."
            ),

            "parameters": {
                "type": "object",

                "properties": {

                    "query": {
                        "type": "string",
                        "description": "Portfolio search query."
                    }

                },

                "required": ["query"]
            }
        }
    }

]

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:latest"


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

def portfolio_rag(query):

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

    context = []

    for result in results:

        metadata = result.get(
            "metadata",
            {}
        )

        content = result.get(
            "content",
            ""
        )

        context.append(
            {
                "source": metadata.get(
                    "source",
                    "unknown"
                ),

                "section": metadata.get(
                    "section",
                    "unknown"
                ),

                "content": content
            }
        )

    return context

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

        return portfolio_rag(
            arguments["query"]
        )


    return {
        "error": f"Unknown tool: {function_name}"
    }

def call_agent(state: AgentState):

    messages = state["messages"]

    response = call_ollama(
        messages
    )

    assistant_message = response["message"]

    messages.append(
        assistant_message
    )

    return {
        **state,
        "messages": messages,
        "answer": assistant_message.get(
            "content",
            ""
        )
    }

def route_after_agent(state: AgentState):

    last_message = state["messages"][-1]

    tool_calls = last_message.get(
        "tool_calls"
    )

    if tool_calls:

        print(
            f"\n[GRAPH] Tool call detected."
        )

        return "tool"

    print(
        "\n[GRAPH] No tool call detected."
    )

    return "answer"

def execute_tools(state: AgentState):

    last_message = state["messages"][-1]

    tool_calls = last_message.get(
        "tool_calls",
        []
    )

    messages = state["messages"]

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

    return {
        **state,
        "messages": messages
    }

def generate_answer(state: AgentState):

    messages = state["messages"]

    messages.append({
        "role": "user",
        "content": """
Using the tool results above, answer the
original user question directly.

Do not ask the user another question.
Do not offer to search for anything else.
Use only the information provided by the
tool results.

Give a concise, useful answer.
"""
    })

    response = call_ollama(
        messages
    )

    answer = response[
        "message"
    ]["content"]

    print(
        "\n[GRAPH] Final answer generated."
    )

    return {
        **state,
        "answer": answer
    }


builder = StateGraph(
    AgentState
)


builder.add_node(
    "agent",
    call_agent
)


builder.add_node(
    "tools",
    execute_tools
)


builder.add_edge(
    START,
    "agent"
)

builder.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "tool": "tools",
        "answer": END
    }
)

builder.add_edge(
    "tools",
    "agent"
)

agent = builder.compile()

if __name__ == "__main__":

    question = (
        "Which project uses YOLO?"
)
       

    # --------------------------------------------------
    # LOAD PREVIOUS CONVERSATION MEMORY
    # --------------------------------------------------

    memory = load_memory()

    print(
        f"\n[MEMORY] Loaded {len(memory)} previous messages."
    )


    # --------------------------------------------------
    # CREATE CURRENT MESSAGE HISTORY
    # --------------------------------------------------

    messages = [

        {
            "role": "system",

            "content": """
You are Himanshi's AI portfolio assistant.

You have access to these tools:

1. search_projects
   Searches Himanshi's projects.

2. search_skills
   Searches Himanshi's technical skills.

3. portfolio_rag
   Searches the complete portfolio knowledge base.

Rules:

- Use a tool whenever portfolio information
  is required.

- Use previous conversation context when
  interpreting follow-up questions.

- After receiving a tool result, answer the
  original user question directly.

- Do not ask follow-up questions if the
  information needed to answer is already
  available.

- Do not offer additional searches.

- Do not invent information.

- If the available information is insufficient,
  clearly say so.
"""
        }

    ]


    # --------------------------------------------------
    # ADD PREVIOUS MEMORY
    # --------------------------------------------------

    messages.extend(memory)


    # --------------------------------------------------
    # ADD CURRENT USER QUESTION
    # --------------------------------------------------

    messages.append({

        "role": "user",

        "content": question

    })


    # --------------------------------------------------
    # RUN LANGGRAPH AGENT
    # --------------------------------------------------

    result = agent.invoke({

        "question": question,

        "messages": messages,

        "tool_result": "",

        "answer": "",

        "memory": memory

    })


    # --------------------------------------------------
    # SAVE CONVERSATION MEMORY
    # --------------------------------------------------

    save_conversation(
        result["messages"]
    )


    # --------------------------------------------------
    # DISPLAY FINAL ANSWER
    # --------------------------------------------------

    print("\n")
    print("=" * 70)
    print("FINAL ANSWER")
    print("=" * 70)

    print(
        result["answer"]
    )

    print("=" * 70)