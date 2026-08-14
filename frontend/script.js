const API_URL =
    "http://127.0.0.1:8000/chat";


let selectedAgent = null;


const messages =
    document.getElementById(
        "chatMessages"
    );

const input =
    document.getElementById(
        "messageInput"
    );

const sendButton =
    document.getElementById(
        "sendButton"
    );

const activeAgent =
    document.getElementById(
        "activeAgent"
    );


const agentNames = {

    bubbly:
        "🫧 Bubbly — Project Guide",

    mochi:
        "🍡 Mochi — Skill Guide",

    poppy:
        "🌷 Poppy — Resume Guide"

};


/* =====================================
   ADD USER MESSAGE
===================================== */

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


    messages.scrollTop =
        messages.scrollHeight;

}


/* =====================================
   ADD AI MESSAGE
===================================== */

function addBotMessage(text) {

    const wrapper =
        document.createElement("div");

    wrapper.className =
        "bot-message";


    wrapper.innerHTML = `

        <div class="bot-avatar">
            ✨
        </div>

        <div>

            <strong>
                ${agentNames[selectedAgent]
                    || "Himanshi's AI Crew"}
            </strong>

            <p></p>

        </div>

    `;


    wrapper.querySelector(
        "p"
    ).textContent = text;


    messages.appendChild(
        wrapper
    );


    messages.scrollTop =
        messages.scrollHeight;

}


/* =====================================
   AGENT SELECTION
===================================== */

document
    .querySelectorAll(
        ".specimen"
    )
    .forEach(card => {

        function wake() {

            selectedAgent =
                card.dataset.agent;


            document.body.dataset.agent =
                selectedAgent;


            activeAgent.textContent =
                agentNames[
                    selectedAgent
                ];


            let greeting = "";

            if (
                selectedAgent ===
                "bubbly"
            ) {

                greeting =
                    "Bubbly here! 🫧 " +
                    "Ready to take you on a tour " +
                    "of Himanshi's projects. " +
                    "Ask me about anything she's built!";

            }


            if (
                selectedAgent ===
                "mochi"
            ) {

                greeting =
                    "Mochi here! 🍡 " +
                    "Let's explore Himanshi's technical " +
                    "toolkit. Ask me about her skills, " +
                    "languages or technologies!";

            }


            if (
                selectedAgent ===
                "poppy"
            ) {

                greeting =
                    "Poppy here! 🌷 " +
                    "I'll walk you through Himanshi's " +
                    "resume, education, experience " +
                    "and professional journey.";

            }


            addBotMessage(
                greeting
            );

            input.focus();

        }


        card.addEventListener(
            "click",
            wake
        );


        card.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter" ||
                    event.key === " "
                ) {

                    event.preventDefault();

                    wake();

                }

            }
        );

    });


/* =====================================
   SEND MESSAGE
===================================== */

async function sendMessage() {

    const question =
        input.value.trim();


    if (!question) {

        return;

    }


    addUserMessage(
        question
    );


    input.value = "";


    sendButton.disabled =
        true;


    sendButton.textContent =
        "Thinking...";


    try {

        const response =
            await fetch(
                API_URL,
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
                                selectedAgent

                        })

                }
            );


        if (!response.ok) {

            throw new Error(
                "Backend request failed"
            );

        }


        const data =
            await response.json();


        if (
            data.agent &&
            agentNames[data.agent]
        ) {

            selectedAgent =
                data.agent;

            document.body.dataset.agent =
                selectedAgent;

            activeAgent.textContent =
                agentNames[
                    data.agent
                ];

        }


        addBotMessage(
            data.answer
        );


    }

    catch (error) {

        console.error(
            error
        );


        addBotMessage(

            "Oops! My AI crew seems to be " +
            "having trouble connecting to the " +
            "portfolio server right now. " +
            "Please make sure the backend is running."

        );

    }

    finally {

        sendButton.disabled =
            false;

        sendButton.innerHTML =
            "Send <span>➜</span>";

        input.focus();

    }

}


/* =====================================
   SEND BUTTON
===================================== */

sendButton.addEventListener(
    "click",
    sendMessage
);


/* =====================================
   ENTER
===================================== */

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


/* =====================================
   SUGGESTIONS
===================================== */

document
    .querySelectorAll(
        ".suggestions button"
    )
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                input.value =
                    button.textContent;

                sendMessage();

            }
        );

    });


/* =====================================
   CLEAR
===================================== */

document
    .getElementById(
        "clearChat"
    )
    .addEventListener(
        "click",
        () => {

            messages.innerHTML = "";

            selectedAgent =
                null;

            delete document.body.dataset.agent;

            activeAgent.textContent =
                "AI Crew";

            addBotMessage(

                "Fresh start! ✨ " +
                "Who would you like to meet — " +
                "Bubbly, Mochi or Poppy?"

            );

        }
    );