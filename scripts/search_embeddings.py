import sys
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.rag.reranker import *


CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "journal_chunks_fixed"
# COLLECTION_NAME = "journal_chunks_semantic"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL= "cross-encoder/ms-marco-MiniLM-L-6-v2"

def main():
    '''
    Embed the query and perform semantic search on the vector database
    Perform Re-Ranking through a Cross Encoder on the results
    '''
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)

    query = input("Enter your query: ")
    query_embedding = model.encode(query).tolist()
    print(f"Embedding dimensions: {len(query_embedding)}")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        include=["documents", "metadatas", "distances"],
    )

    # results = collection.query(
    #     query_embeddings=[query_embedding],
    #     n_results=5,
    #     where={
    #         "$and": [
    #             {"topic": "Career Planning"},
    #             {"chunking_method": "semantic"}
    #         ]
    #     }
    # )

    reranker = CrossEncoderReranker(model_name=CROSS_ENCODER_MODEL)
    vector_results = format_chroma_results(results)

    reranked = reranker.rerank(
        query=query,
        results=vector_results,
        top_n=2,
    )

    print("\nRERANKED RESULTS\n")

    for result in reranked:
        print(
            f"Rank: {result['rerank_rank']}\n"
            f"Score: {result['rerank_score']:.4f}\n"
            f"Chunk: {result['chunk_id']}\n"
            f"Topic: {result['metadata']['topic']}\n"
            f"Content: {result['content']}\n"
        )

if __name__=='__main__':
    main()