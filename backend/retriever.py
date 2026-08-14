import pickle
from pathlib import Path

import faiss
import numpy as np

from embeddings import PortfolioEmbeddings


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

VECTORSTORE_DIR = BASE_DIR / "vectorstore"

INDEX_PATH = VECTORSTORE_DIR / "portfolio.index"
METADATA_PATH = VECTORSTORE_DIR / "metadata.pkl"


# --------------------------------------------------
# RETRIEVER
# --------------------------------------------------

class PortfolioRetriever:

    def __init__(self):

        print("Loading FAISS vector database...")

        self.index = faiss.read_index(
            str(INDEX_PATH)
        )

        print(
            f"FAISS index loaded. "
            f"Vectors: {self.index.ntotal}"
        )

        print("Loading metadata...")

        with open(
            METADATA_PATH,
            "rb"
        ) as file:

            self.documents = pickle.load(file)

        print(
            f"Metadata loaded. "
            f"Documents: {len(self.documents)}"
        )

        self.embedding_model = PortfolioEmbeddings()


    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    def search(self, query, top_k=5):

        # Convert query into embedding
        query_embedding = (
            self.embedding_model.embed_query(query)
        )

        # FAISS expects float32
        query_embedding = np.asarray(
            [query_embedding],
            dtype="float32"
        )

        # Search FAISS
        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index == -1:
                continue

            document = self.documents[index]

            results.append({
                "score": float(score),
                "content": document["content"],
                "metadata": document["metadata"]
            })

        return results


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    retriever = PortfolioRetriever()

    query = "Which project uses RAG?"

    print("\n")
    print("=" * 60)
    print("QUERY:")
    print(query)
    print("=" * 60)

    results = retriever.search(
        query,
        top_k=5
    )

    print("\nRETRIEVED RESULTS:\n")

    for i, result in enumerate(results):

        print("-" * 60)

        print(
            f"Result {i + 1}"
        )

        print(
            f"Score: {result['score']:.4f}"
        )

        print(
            f"Metadata: {result['metadata']}"
        )

        print(
            f"Content:\n{result['content'][:400]}"
        )