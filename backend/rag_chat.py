from retriever import PortfolioRetriever
from llm import generate_answer


def build_context(results):
    """
    Convert retrieved documents into context
    that can be passed to the LLM.
    """

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


def answer_question(question):

    # -----------------------------------------
    # 1. RETRIEVE
    # -----------------------------------------

    retriever = PortfolioRetriever()

    results = retriever.search(
        question,
        top_k=5
    )

    # -----------------------------------------
    # 2. BUILD CONTEXT
    # -----------------------------------------

    context = build_context(results)

    # -----------------------------------------
    # 3. CREATE GROUNDED PROMPT
    # -----------------------------------------

    prompt = f"""
You are the AI Portfolio Assistant for Himanshi Sharma.

Your task is to answer questions about Himanshi
using ONLY the portfolio context provided below.

IMPORTANT RULES:

1. Do not invent information.
2. Do not assume information that is not present.
3. Do not add skills, projects, experience,
   certifications or technologies that are not
   supported by the context.
4. If the context does not contain enough
   information, say:

"I don't have enough information in the
portfolio knowledge base to answer that accurately."

5. Answer clearly and professionally.
6. Keep the answer concise unless the user asks
   for more detail.

PORTFOLIO CONTEXT
==================

{context}

==================

USER QUESTION:
{question}

ANSWER:
"""

    # -----------------------------------------
    # 4. GENERATE ANSWER
    # -----------------------------------------

    answer = generate_answer(prompt)

    return answer


if __name__ == "__main__":

    question = "Which project uses RAG?"

    print("\nSearching portfolio knowledge base...")

    answer = answer_question(question)

    print("\n" + "=" * 70)
    print("QUESTION")
    print("=" * 70)

    print(question)

    print("\n" + "=" * 70)
    print("AI ANSWER")
    print("=" * 70)

    print(answer)

    print("=" * 70)