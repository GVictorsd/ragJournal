import sys
import logging
import warnings
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

# Suppress unnecessary logs and warnings
logging.disable(logging.CRITICAL)
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.ERROR)

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.rag.reranker import CrossEncoderReranker, format_chroma_results
from app.rag.generation import generate_answer


CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "journal_chunks_fixed"
# COLLECTION_NAME = "journal_chunks_semantic"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

OLLAMA_HOST = ""
MODEL = "qwen2.5:3b"


def main():
    """Continuously retrieve, rerank, and answer journal questions."""

    print("Loading models and connecting to ChromaDB...")

    model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)

    reranker = CrossEncoderReranker(
        model_name=CROSS_ENCODER_MODEL
    )

    print("Ready! Ask a question about your journal.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            query = input("You: ").strip()

            if not query:
                continue

            if query.lower() in {"exit", "quit", "q"}:
                print("Goodbye!")
                break

            # 1. Embed the query
            query_embedding = model.encode(query).tolist()

            # 2. Retrieve relevant chunks from ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=10,
                include=["documents", "metadatas", "distances"],
            )

            # 3. Format and rerank retrieved chunks
            vector_results = format_chroma_results(results)

            reranked = reranker.rerank(
                query=query,
                results=vector_results,
                top_n=3,
            )

            # 4. Generate an answer using the cloud-hosted LLM
            result = generate_answer(
                query=query,
                reranked_results=reranked,
                ollama_url=OLLAMA_HOST,
                model=MODEL,
            )

            # 5. Display the answer and source references
            print(f"\n{result['answer']}")

            if result.get("sources"):
                print("\nSources:")
                for source in result["sources"]:
                    print(
                        f"[{source['source_id']}] "
                        f"{source['topic']} | "
                        f"{source['date']} | "
                        f"{source['chunk_id']}"
                    )

            print()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

        except Exception:
            print("\nUnable to process your question. Please try again.\n")


if __name__ == "__main__":
    main()