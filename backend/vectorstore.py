import pickle
from pathlib import Path

import faiss
import numpy as np

from rag import load_portfolio_documents, chunk_documents
from embeddings import PortfolioEmbeddings


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

VECTORSTORE_DIR = BASE_DIR / "vectorstore"

INDEX_PATH = VECTORSTORE_DIR / "portfolio.index"
METADATA_PATH = VECTORSTORE_DIR / "metadata.pkl"


# --------------------------------------------------
# VECTOR STORE CLASS
# --------------------------------------------------

class PortfolioVectorStore:

    def __init__(self):

        self.embedding_model = PortfolioEmbeddings()

        self.index = None
        self.documents = []

    # --------------------------------------------------
    # BUILD VECTOR DATABASE
    # --------------------------------------------------

    def build(self):

        print("\nLoading portfolio documents...")

        documents = load_portfolio_documents()

        print(f"Loaded {len(documents)} documents.")

        print("\nCreating chunks...")

        chunks = chunk_documents(documents)

        print(f"Created {len(chunks)} chunks.")

        # Extract text
        texts = [
            chunk["content"]
            for chunk in chunks
        ]

        print("\nGenerating embeddings...")

        embeddings = self.embedding_model.embed_documents(texts)

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        print(
            f"Generated embeddings with shape: "
            f"{embeddings.shape}"
        )

        # --------------------------------------------------
        # CREATE FAISS INDEX
        # --------------------------------------------------

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        self.documents = chunks

        print("\nFAISS index created.")

        print(
            f"Number of vectors stored: "
            f"{self.index.ntotal}"
        )

        # --------------------------------------------------
        # SAVE VECTOR DATABASE
        # --------------------------------------------------

        VECTORSTORE_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            str(INDEX_PATH)
        )

        with open(
            METADATA_PATH,
            "wb"
        ) as file:

            pickle.dump(
                self.documents,
                file
            )

        print("\nVector database saved successfully.")

        print(
            f"FAISS index: {INDEX_PATH}"
        )

        print(
            f"Metadata: {METADATA_PATH}"
        )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    vector_store = PortfolioVectorStore()

    vector_store.build()