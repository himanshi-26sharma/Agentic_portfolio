import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "gemma4:latest"

def generate_answer(prompt):

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    result = response.json()

    return result["response"]


if __name__ == "__main__":

    prompt = """
    Explain RAG in two simple sentences.
    """

    answer = generate_answer(prompt)

    print("\nOllama Response:\n")
    print(answer)