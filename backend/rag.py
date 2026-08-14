import json
from pathlib import Path
from pypdf import PdfReader


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = BASE_DIR / "documents"


def load_json_file(file_path):
    """Load a JSON file and return its contents."""

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_resume():
    """Extract text from the resume PDF."""

    resume_path = DOCUMENTS_DIR / "resume.pdf"

    reader = PdfReader(resume_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def load_portfolio_documents():
    """
    Load all portfolio information and convert it
    into a common document format.
    """

    documents = []

    # -------------------------
    # ABOUT
    # -------------------------

    about = load_json_file(DATA_DIR / "about.json")

    documents.append({
        "content": json.dumps(about, indent=2),
        "metadata": {
            "source": "about.json",
            "section": "about"
        }
    })

    # -------------------------
    # SKILLS
    # -------------------------

    skills = load_json_file(DATA_DIR / "skills.json")

    documents.append({
        "content": json.dumps(skills, indent=2),
        "metadata": {
            "source": "skills.json",
            "section": "skills"
        }
    })

    # -------------------------
    # PROJECTS
    # -------------------------

    projects = load_json_file(DATA_DIR / "projects.json")

    for project in projects:

        documents.append({
            "content": json.dumps(project, indent=2),
            "metadata": {
                "source": "projects.json",
                "section": "project",
                "project": project.get("name"),
                "domain": project.get("domain"),
                "type": project.get("type")
            }
        })

    # -------------------------
    # RESUME
    # -------------------------

    resume_text = load_resume()

    documents.append({
        "content": resume_text,
        "metadata": {
            "source": "resume.pdf",
            "section": "resume"
        }
    })

    return documents

def chunk_documents(documents, chunk_size=500, overlap=100):
    """
    Split documents into smaller chunks while preserving metadata.
    """

    chunks = []

    for document in documents:

        text = document["content"]
        metadata = document["metadata"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end]

            if chunk_text.strip():

                chunk_metadata = metadata.copy()

                chunk_metadata["chunk_start"] = start
                chunk_metadata["chunk_end"] = end

                chunks.append({
                    "content": chunk_text,
                    "metadata": chunk_metadata
                })

            start += chunk_size - overlap

    return chunks

if __name__ == "__main__":

    documents = load_portfolio_documents()

    print("\nPortfolio documents loaded successfully.")
    print("Number of documents:", len(documents))

    chunks = chunk_documents(documents)

    print("\nChunking completed.")
    print("Number of chunks:", len(chunks))

    for i, chunk in enumerate(chunks[:5]):

        print("\n----------------------------")
        print("Chunk:", i + 1)
        print("Metadata:", chunk["metadata"])
        print("Content:")
        print(chunk["content"][:300])
