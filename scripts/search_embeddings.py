import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import chromadb
from sentence_transformers import SentenceTransformer
from app.rag.reranker import *

CHROMA_PATH = "./chroma_db"
# COLLECTION_NAME = "journal_chunks_fixed"
COLLECTION_NAME = "journal_chunks_semantic"
model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(name=COLLECTION_NAME)

query = input("Enter your query: ")
query_embedding = model.encode(query).tolist()
print(f"Query: {query}")
print(f"Embedding dimensions: {len(query_embedding)}")

# results = collection.query(
#     query_embeddings=[query_embedding],
#     n_results=5
# )
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    include=["documents", "metadatas", "distances"],
)

# results = collection.query(
#     query_embeddings=[query_embedding],
#     n_results=5,
#     where={
#         "file_type": "markdown"
#     }
# )

    # where={
    #     "$and": [
    #         {"topic": "Career Planning"},
    #         {"chunking_method": "semantic"}
    #     ]
    # }

# for i in range(len(results["ids"][0])):

#     print("=" * 60)

#     print("ID:")
#     print(results["ids"][0][i])

#     print("\nDocument:")
#     print(results["documents"][0][i])

#     print("\nMetadata:")
#     print(results["metadatas"][0][i])

#     print("\nDistance:")
#     print(results["distances"][0][i])

reranker = CrossEncoderReranker()

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