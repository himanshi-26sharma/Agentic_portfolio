from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from retriever import PortfolioRetriever
from llm import generate_answer
from tools import search_projects



# ============================================================
# 1. AGENT STATE
# ============================================================

class AgentState(TypedDict):

    question: str
    rewritten_question: str
    intent: str
    context: str
    relevance: str
    answer: str
    attempts: int


# ============================================================
# 2. INITIALIZE RETRIEVER
# ============================================================

retriever = PortfolioRetriever()


# ============================================================
# 3. BUILD CONTEXT
# ============================================================

def build_context(results):

    context_parts = []

    for result in results:

        metadata = result["metadata"]

        context_parts.append(
            f"""
SOURCE: {metadata.get("source")}
SECTION: {metadata.get("section")}
PROJECT: {metadata.get("project", "N/A")}
DOMAIN: {metadata.get("domain", "N/A")}

CONTENT:
{result["content"]}
"""
        )

    return "\n".join(context_parts)


# ============================================================
# 4. QUERY ANALYZER
# ============================================================

def analyze_query(state: AgentState):

    question = state["question"]

    print("\n[AGENT] Analyzing query...")
    print(f"[AGENT] Question: {question}")

    prompt = f"""
You are a query router for an AI portfolio assistant.

Classify the user's question into exactly ONE
of these categories:

PROJECT
PORTFOLIO
GENERAL

PROJECT:
Questions specifically asking about projects,
project technologies, project domains, project
features, or finding projects.

Examples:
- Which projects use computer vision?
- What technologies are used in the MCP project?
- Tell me about the P&ID project.

PORTFOLIO:
Questions about Himanshi's skills, resume,
education, experience, certifications,
career information, or general portfolio details.

Examples:
- What programming languages does she know?
- What certifications does she have?
- Tell me about her experience.

GENERAL:
Questions unrelated to the portfolio.

Examples:
- What is RAG?
- What is MCP?
- What is the weather today?

USER QUESTION:
{question}

Return ONLY:
PROJECT
or
PORTFOLIO
or
GENERAL
"""

    result = generate_answer(prompt).strip().upper()

    if "PROJECT" in result:
        intent = "project"

    elif "PORTFOLIO" in result:
        intent = "portfolio"

    else:
        intent = "general"

    print(f"[AGENT] Detected intent: {intent}")

    return {
        **state,
        "intent": intent,
        "rewritten_question": question,
        "attempts": 0
    }


def route_query(state: AgentState):

    question = state["question"]

    print("\n[AGENT] Deciding what action to take...")

    routing_prompt = f"""
You are the decision-making component of an AI
portfolio assistant.

The assistant has two available capabilities:

1. PROJECT_TOOL
   Use this when the user is asking about:
   - projects
   - project technologies
   - project domains
   - project features
   - finding projects related to a topic

2. RAG
   Use this for:
   - skills
   - resume information
   - education
   - experience
   - certifications
   - general portfolio information

Choose exactly ONE action.

USER QUESTION:
{question}

Return ONLY:

PROJECT_TOOL

or

RAG
"""

    decision = generate_answer(
        routing_prompt
    ).strip().upper()

    print(
        f"[AGENT] LLM selected: {decision}"
    )

    if decision == "PROJECT_TOOL":

        print(
            "[AGENT] Routing → Project Search Tool"
        )

        return "project_search"

    print(
        "[AGENT] Routing → Portfolio RAG"
    )

    return "retrieve"

# ============================================================
# 5. RETRIEVAL NODE
# ============================================================

def retrieve(state: AgentState):

    question = state["rewritten_question"]

    print("\n[AGENT] Searching knowledge base...")
    print(f"[AGENT] Search query: {question}")

    results = retriever.search(
        question,
        top_k=5
    )

    context = build_context(results)

    print(
        f"[AGENT] Retrieved {len(results)} results."
    )

    return {
        **state,
        "context": context
    }

def project_search(state: AgentState):

    question = state["question"]

    print("\n[AGENT] Using Project Search Tool...")
    print(f"[TOOL] Query: {question}")

    results = search_projects.invoke({
    "query": question
})

    if not results:

        tool_context = (
            "The project search tool did not find "
            "any matching projects."
        )

    else:

        tool_parts = []

        for result in results[:5]:

            project = result["project"]

            tool_parts.append(
                f"""
PROJECT: {project["name"]}
DOMAIN: {project["domain"]}
TYPE: {project["type"]}
TECHNOLOGIES: {", ".join(project["technologies"])}

DESCRIPTION:
{project["description"]}

KEY FEATURES:
{", ".join(project["key_features"])}
"""
            )

        tool_context = "\n".join(tool_parts)

    return {
        **state,
        "context": tool_context
    }



# ============================================================
# 6. RELEVANCE EVALUATOR
# ============================================================

def evaluate_relevance(state: AgentState):

    question = state["rewritten_question"]

    context = state["context"]

    print("\n[AGENT] Evaluating retrieved context...")

    evaluation_prompt = f"""
You are evaluating whether retrieved portfolio
information is relevant to a user's question.

USER QUESTION:
{question}

RETRIEVED CONTEXT:
{context}

Determine whether the retrieved context contains
enough relevant information to answer the question.

Respond with ONLY one word:

RELEVANT

or

IRRELEVANT
"""

    evaluation = generate_answer(
        evaluation_prompt
    ).strip().upper()

    if evaluation == "RELEVANT":
        relevance = "relevant"
    else:
        relevance = "irrelevant"

    print(
        f"[AGENT] Retrieval evaluation: {relevance}"
    )

    return {
        **state,
        "relevance": relevance
    }


# ============================================================
# 7. DECISION
# ============================================================

def decide_next_step(state: AgentState):

    if state["relevance"] == "relevant":

        print(
            "[AGENT] Context is sufficient → generating answer."
        )

        return "generate"

    if state["attempts"] >= 1:

        print(
            "[AGENT] Maximum retrieval attempts reached."
        )

        return "generate"

    print(
        "[AGENT] Context insufficient → rewriting query."
    )

    return "rewrite"


# ============================================================
# 8. QUERY REWRITER
# ============================================================

def rewrite_query(state: AgentState):

    question = state["question"]

    print("\n[AGENT] Rewriting query...")

    rewrite_prompt = f"""
Rewrite the following user question into a
clearer search query for a portfolio knowledge base.

USER QUESTION:
{question}

The search query should focus on the important
keywords and concepts.

Return ONLY the rewritten search query.
"""

    rewritten = generate_answer(
        rewrite_prompt
    ).strip()

    print(
        f"[AGENT] Rewritten query: {rewritten}"
    )

    return {
        **state,
        "rewritten_question": rewritten,
        "attempts": state["attempts"] + 1
    }


# ============================================================
# 9. GENERATE ANSWER
# ============================================================

def generate(state: AgentState):

    question = state["question"]

    context = state["context"]

    print("\n[AGENT] Generating final answer...")

    prompt = f"""
You are the AI Portfolio Assistant for
Himanshi Sharma.

Answer the user's question using ONLY the
portfolio context provided below.

Rules:

1. Never invent information.
2. Never assume information that isn't provided.
3. Do not create projects, skills, experience,
   certifications or achievements.
4. If the context does not contain enough
   information, say:

"I don't have enough information in the
portfolio knowledge base to answer that accurately."

5. Be clear and professional.

PORTFOLIO CONTEXT:
{context}

USER QUESTION:
{question}

FINAL ANSWER:
"""

    answer = generate_answer(prompt)

    return {
        **state,
        "answer": answer
    }


# ============================================================
# 10. BUILD LANGGRAPH
# ============================================================

builder = StateGraph(AgentState)


builder.add_node(
    "analyze_query",
    analyze_query
)

builder.add_node(
    "retrieve",
    retrieve
)

builder.add_node(
    "project_search",
    project_search
)

builder.add_node(
    "evaluate_relevance",
    evaluate_relevance
)

builder.add_node(
    "rewrite_query",
    rewrite_query
)

builder.add_node(
    "generate",
    generate
)


# ============================================================
# GRAPH EDGES
# ============================================================

builder.add_edge(
    START,
    "analyze_query"
)


builder.add_conditional_edges(
    "analyze_query",
    route_query,
    {
        "project_search": "project_search",
        "retrieve": "retrieve"
    }
)


builder.add_edge(
    "project_search",
    "evaluate_relevance"
)


builder.add_edge(
    "retrieve",
    "evaluate_relevance"
)


builder.add_conditional_edges(
    "evaluate_relevance",
    decide_next_step,
    {
        "generate": "generate",
        "rewrite": "rewrite_query"
    }
)


builder.add_edge(
    "rewrite_query",
    "retrieve"
)

# ============================================================
# COMPILE
# ============================================================

agent = builder.compile()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":


      question = "What programming languages does Himanshi know?"

result = agent.invoke({

        "question": question,

        "rewritten_question": "",

        "intent": "",

        "context": "",

        "relevance": "",

        "answer": "",

        "attempts": 0
    })

print("\n")
print("=" * 70)
print("FINAL ANSWER")
print("=" * 70)
print(result["answer"])
print("=" * 70)                     