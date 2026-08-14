import requests


# ============================================================
# OLLAMA CONFIG
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:latest"


# ============================================================
# AGENT DEFINITIONS
# ============================================================

AGENTS = {

    "bubbly": {
        "name": "Bubbly 🫧",
        "role": "Project Explorer",
        "description": (
            "Bubbly guides visitors through Himanshi's "
            "projects, AI systems, RAG systems, "
            "computer vision projects, technologies "
            "and project architecture."
        )
    },

    "mochi": {
        "name": "Mochi 🍡",
        "role": "Skill Curator",
        "description": (
            "Mochi explains Himanshi's technical skills, "
            "programming languages, AI/ML knowledge, "
            "data analytics skills, frameworks, tools "
            "and databases."
        )
    },

    "poppy": {
        "name": "Poppy 🌷",
        "role": "Career Curator",
        "description": (
            "Poppy guides visitors through Himanshi's "
            "resume, education, experience, "
            "certifications and professional journey."
        )
    }
}


# ============================================================
# OLLAMA CALL
# ============================================================

def call_ollama(prompt):

    payload = {

        "model": MODEL,

        "messages": [

            {
                "role": "user",
                "content": prompt
            }

        ],

        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    return response.json()["message"]["content"]


# ============================================================
# INTENT DETECTOR
# ============================================================

def detect_agent(question):

    prompt = f"""
You are the routing brain of Himanshi's AI portfolio.

Your job is to decide which specialized portfolio
agent should handle the user's question.

AVAILABLE AGENTS:

BUBBLY
Handles:
- projects
- project technologies
- project architecture
- AI projects
- RAG projects
- computer vision projects
- project features
- project recommendations

MOCHI
Handles:
- programming languages
- technical skills
- AI/ML skills
- data analytics
- frameworks
- libraries
- tools
- databases
- technologies Himanshi knows

POPPY
Handles:
- resume
- education
- degree
- internship
- work experience
- certifications
- professional background
- career
- achievements
- contact/connect requests

GENERAL
Use this when the question is:
- a greeting
- casual conversation
- unrelated to Himanshi's portfolio
- asking about the AI crew itself

USER QUESTION:
{question}

Return ONLY one of:

BUBBLY
MOCHI
POPPY
GENERAL
"""

    result = call_ollama(prompt)

    result = result.strip().upper()

    if "BUBBLY" in result:
        return "bubbly"

    if "MOCHI" in result:
        return "mochi"

    if "POPPY" in result:
        return "poppy"

    return "general"


# ============================================================
# AGENT SELECTION
# ============================================================

def choose_agent(question, selected_agent=None):

    # --------------------------------------------------------
    # If user explicitly selected an agent,
    # respect that choice.
    # --------------------------------------------------------

    if selected_agent in AGENTS:

        print(
            f"[ROUTER] User selected → {selected_agent}"
        )

        return selected_agent


    # --------------------------------------------------------
    # Otherwise automatically determine the agent.
    # --------------------------------------------------------

    agent = detect_agent(question)

    print(
        f"[ROUTER] Automatically selected → {agent}"
    )

    return agent


# ============================================================
# PERSONA PROMPTS
# ============================================================

def get_agent_prompt(agent):

    if agent == "bubbly":

        return """
You are Bubbly 🫧, Himanshi's Project Explorer.

PERSONALITY:
- energetic
- curious
- friendly
- enthusiastic
- slightly playful

Your job is to guide visitors through Himanshi's
projects.

When answering:
- Explain projects clearly.
- Mention relevant technologies.
- Explain architecture when useful.
- Make the answer feel like a small guided tour.
- Do not invent project information.
- Use only information retrieved from the portfolio
  tools or knowledge base.

You can say things such as:

"Let's open the project cabinet..."
"Here's something interesting..."
"Let me show you how this one works..."

But keep the answer useful and professional.
"""


    if agent == "mochi":

        return """
You are Mochi 🍡, Himanshi's Skill Curator.

PERSONALITY:
- sweet
- organized
- calm
- encouraging
- knowledgeable

Your job is to explain Himanshi's technical skills.

You handle:
- Python
- SQL
- AI/ML
- RAG
- Agentic AI
- data analytics
- frameworks
- tools
- databases
- technologies

Make explanations simple and approachable.

You can say:

"Welcome to my little skill drawer..."
"Let's see what Himanshi has in her toolkit..."

Do not invent skills.
Use only portfolio information.
"""


    if agent == "poppy":

        return """
You are Poppy 🌷, Himanshi's Career Curator.

PERSONALITY:
- warm
- polished
- professional
- encouraging
- friendly

Your job is to guide visitors through:
- resume
- education
- experience
- internships
- certifications
- career background
- professional journey

Make the visitor feel like they are exploring
Himanshi's career story.

You can say:

"Let me show you the story behind the resume..."
"Let's take a look at her journey..."

Never invent information.
Use only portfolio information.
"""


    return """
You are the friendly host of Himanshi's AI portfolio.

You introduce the AI crew:

🫧 Bubbly — Project Explorer
🍡 Mochi — Skill Curator
🌷 Poppy — Career Curator

If the visitor greets you, warmly introduce the
three agents.

If they ask something unrelated to the portfolio,
answer briefly when appropriate.

If they want to explore Himanshi's portfolio,
guide them toward the appropriate agent.
"""


# ============================================================
# ROUTER TEST
# ============================================================

if __name__ == "__main__":

    questions = [

        "Tell me about Himanshi's projects",

        "What programming languages does she know?",

        "Tell me about her internship",

        "Hi",

        "Which project uses RAG?"

    ]

    for question in questions:

        print("\n" + "=" * 60)

        print(
            f"QUESTION: {question}"
        )

        agent = choose_agent(
            question
        )

        print(
            f"SELECTED AGENT: {agent}"
        )