from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-small-en-v1.5"


class PortfolioEmbeddings:

    def __init__(self):
        print("Loading embedding model...")

        self.model = SentenceTransformer(MODEL_NAME)

        print("Embedding model loaded successfully.")

    def embed_documents(self, texts):
        """
        Convert multiple text chunks into embeddings.
        """

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return embeddings

    def embed_query(self, query):
        """
        Convert a user query into an embedding.
        """

        embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )

        return embedding[0]


if __name__ == "__main__":

    embedding_model = PortfolioEmbeddings()

    test_text = [
        "Agentic AI systems use agents to reason and perform tasks.",
        "RAG retrieves relevant information from a knowledge base."
    ]

    embeddings = embedding_model.embed_documents(test_text)

    print("\nEmbedding test completed.")
    print("Number of embeddings:", len(embeddings))
    print("Embedding dimensions:", len(embeddings[0]))