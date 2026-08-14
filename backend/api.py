from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from mcp_agent import ask_portfolio_agent


app = FastAPI(
    title="Himanshi AI Portfolio"
)


app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)


class ChatRequest(BaseModel):

    message: str

    agent: str | None = None


@app.get("/")

def home():

    return {

        "status": "online",

        "message":
            "Himanshi AI Portfolio Agent is running."

    }


@app.post("/chat")

async def chat(
    request: ChatRequest
):

    result = await ask_portfolio_agent(

        request.message,

        request.agent

    )

    return result