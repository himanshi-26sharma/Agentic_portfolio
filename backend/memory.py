import json
from pathlib import Path


MEMORY_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "conversation_memory.json"
)


def load_memory():

    if not MEMORY_FILE.exists():
        return []

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, OSError):

        return []


def save_memory(messages):

    MEMORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            messages,
            file,
            indent=2,
            ensure_ascii=False
        )


def save_conversation(messages):

    conversation = []

    for message in messages:

        role = message.get("role")

        # Only save actual conversation messages
        if role not in ["user", "assistant"]:
            continue

        content = message.get(
            "content",
            ""
        )

        if not content:
            continue

        conversation.append({
            "role": role,
            "content": content
        })

    save_memory(conversation)
