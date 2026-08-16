/* =========================================================
   HIMANSHI AI PORTFOLIO
   Frontend → FastAPI → Agent Router → MCP → Tools/RAG
========================================================= */


/* =========================================================
   CONFIGURATION
========================================================= */

const API_URL = "http://127.0.0.1:8000";

let selectedAgent = null;


/* =========================================================
   DOM ELEMENTS
========================================================= */

const messages = document.getElementById(
    "chatMessages"
);

const input = document.getElementById(
    "messageInput"
);

const sendButton = document.getElementById(
    "sendButton"
);

const activeAgent = document.getElementById(
    "activeAgent"
);

const clearChat = document.getElementById(
    "clearChat"
);


/* =========================================================
   AGENT INFORMATION
========================================================= */

const agentNames = {

    bubbly:
        "🫧 Bubbly — Project Guide",

    mochi:
        "🍡 Mochi — Skill Guide",

    poppy:
        "🌷 Poppy — Resume Guide",

    general:
        "✨ Himanshi's AI Crew"

};


/* =========================================================
   AGENT GREETINGS
========================================================= */

const agentGreetings = {

    bubbly:
        "Bubbly here! 🫧 I'm Himanshi's Project Guide. " +
        "I'll take you on a tour of her projects, AI systems, " +
        "computer vision work, RAG pipelines and more. " +
        "Ask me anything about what she's built!",

    mochi:
        "Mochi here! 🍡 I'm Himanshi's Skill Guide. " +
        "Let's explore her technical toolkit — programming, " +
        "AI, data analytics, frameworks, databases and all " +
        "the technologies she works with!",

    poppy:
        "Poppy here! 🌷 I'm Himanshi's Resume Guide. " +
        "I'll walk you through her education, experience, " +
        "internships, certifications and professional journey.",

    general:
        "Hi there! ✨ Himanshi's AI crew is ready to help you explore her portfolio."
};


/* =========================================================
   ADD USER MESSAGE
========================================================= */

function addUserMessage(text) {

    const wrapper =
        document.createElement("div");

    wrapper.className =
        "user-message";


    const bubble =
        document.createElement("div");

    bubble.textContent =
        text;


    wrapper.appendChild(
        bubble
    );


    messages.appendChild(
        wrapper
    );


    scrollToBottom();

}


/* =========================================================
   ADD BOT MESSAGE
========================================================= */

function addBotMessage(
    text,
    agent = selectedAgent
) {

    const wrapper =
        document.createElement("div");

    wrapper.className =
        "bot-message";


    const agentName =
        agentNames[agent]
        || agentNames.general;


    wrapper.innerHTML = `

        <div class="bot-avatar">
            ✨
        </div>

        <div class="bot-content">

            <strong>
                ${agentName}
            </strong>

            <p></p>

        </div>

    `;


    const paragraph =
        wrapper.querySelector("p");


    paragraph.textContent =
        text;


    messages.appendChild(
        wrapper
    );


    scrollToBottom();

}


/* =========================================================
   SCROLL CHAT TO BOTTOM
========================================================= */

function scrollToBottom() {

    messages.scrollTop =
        messages.scrollHeight;

}


/* =========================================================
   SELECT AGENT
========================================================= */

function selectAgent(agent) {

    selectedAgent =
        agent;


    document.body.dataset.agent =
        agent;


    if (activeAgent) {

        activeAgent.textContent =
            agentNames[agent]
            || agentNames.general;

    }


    const greeting =
        agentGreetings[agent];


    if (greeting) {

        addBotMessage(
            greeting,
            agent
        );

    }


    input.focus();

}


/* =========================================================
   AGENT CARD CLICK
========================================================= */

document
    .querySelectorAll(".specimen")
    .forEach(card => {

        const agent =
            card.dataset.agent;


        /* Mouse click */

        card.addEventListener(
            "click",
            () => {

                selectAgent(
                    agent
                );

            }
        );


        /* Keyboard accessibility */

        card.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter" ||
                    event.key === " "
                ) {

                    event.preventDefault();


                    selectAgent(
                        agent
                    );

                }

            }
        );

    });


/* =========================================================
   CALL FASTAPI
========================================================= */

async function askPortfolioAgent(
    question,
    agent = null
) {

    console.log(
        "[FRONTEND] Sending request..."
    );

    console.log(
        "[QUESTION]",
        question
    );

    console.log(
        "[AGENT]",
        agent
    );


    const response =
        await fetch(
            `${API_URL}/chat`,
            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify({

                        message:
                            question,

                        agent:
                            agent

                    })

            }
        );


    if (!response.ok) {

        throw new Error(
            `Backend returned HTTP ${response.status}`
        );

    }


    const data =
        await response.json();


    console.log(
        "[BACKEND RESPONSE]",
        data
    );


    return data;

}


/* =========================================================
   SEND MESSAGE
========================================================= */

async function sendMessage() {

    const question =
        input.value.trim();


    if (!question) {

        return;

    }


    /* -----------------------------------------
       SHOW USER MESSAGE
    ----------------------------------------- */

    addUserMessage(
        question
    );


    input.value = "";


    /* -----------------------------------------
       DISABLE SEND BUTTON
    ----------------------------------------- */

    sendButton.disabled =
        true;


    sendButton.textContent =
        "Thinking...";


    /* -----------------------------------------
       TEMPORARY THINKING MESSAGE
    ----------------------------------------- */

    const thinkingAgent =
        selectedAgent
        || "general";


    try {

        /* -------------------------------------
           CALL BACKEND
        ------------------------------------- */

        const data =
            await askPortfolioAgent(
                question,
                selectedAgent
            );


        /* -------------------------------------
           UPDATE AGENT IF ROUTER SELECTED ONE
        ------------------------------------- */

        if (
            data.agent &&
            agentNames[data.agent]
        ) {

            selectedAgent =
                data.agent;


            document.body.dataset.agent =
                selectedAgent;


            if (activeAgent) {

                activeAgent.textContent =
                    agentNames[
                        selectedAgent
                    ];

            }

        }


        /* -------------------------------------
           GET ANSWER
        ------------------------------------- */

        const answer =
            data.answer
            || data.message
            || data.response;


        if (!answer) {

            addBotMessage(
                "I received a response, but there wasn't an answer to display.",
                selectedAgent
            );

        }

        else {

            addBotMessage(
                answer,
                selectedAgent
            );

        }


    }

    catch (error) {

        console.error(
            "[FRONTEND ERROR]",
            error
        );


        addBotMessage(

            "Oops! 😅 My AI crew couldn't reach " +
            "the portfolio server right now. " +
            "Please make sure the FastAPI backend is running.",

            selectedAgent

        );

    }


    finally {

        /* -------------------------------------
           ENABLE SEND BUTTON
        ------------------------------------- */

        sendButton.disabled =
            false;


        sendButton.innerHTML =
            "Send <span>➜</span>";


        input.focus();

    }

}


/* =========================================================
   SEND BUTTON
========================================================= */

sendButton.addEventListener(
    "click",
    sendMessage
);


/* =========================================================
   ENTER KEY
========================================================= */

input.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


/* =========================================================
   SUGGESTION BUTTONS
========================================================= */

document
    .querySelectorAll(
        ".suggestions button"
    )
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                input.value =
                    button.textContent.trim();


                sendMessage();

            }
        );

    });


/* =========================================================
   CLEAR CHAT
========================================================= */

if (clearChat) {

    clearChat.addEventListener(
        "click",
        () => {

            messages.innerHTML = "";


            selectedAgent =
                null;


            delete document.body.dataset.agent;


            if (activeAgent) {

                activeAgent.textContent =
                    "AI Crew";

            }


            addBotMessage(

                "Fresh start! ✨ " +
                "Who would you like to meet — " +
                "Bubbly, Mochi or Poppy?",

                "general"

            );


            input.focus();

        }
    );

}


/* =========================================================
   INITIAL STATE
========================================================= */

console.log(
    "✨ Himanshi AI Portfolio frontend loaded."
);

console.log(
    "Backend:",
    API_URL
);