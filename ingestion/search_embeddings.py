import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "journal_chunks_fixed"
model = SentenceTransformer("all-MiniLM-L6-v2")

# def get_query_embedding(query: str) -> list[float]:
#     return model.encode(query).tolist()

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    name=COLLECTION_NAME
)

query = input("Enter your query: ")
# query_embedding = get_query_embedding(query)
query_embedding = model.encode(query).tolist()
print(f"Query: {query}")
print(f"Embedding dimensions: {len(query_embedding)}")

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5
)

for i in range(len(results["ids"][0])):

    print("=" * 60)

    print("ID:")
    print(results["ids"][0][i])

    print("\nDocument:")
    print(results["documents"][0][i])

    print("\nMetadata:")
    print(results["metadatas"][0][i])

    print("\nDistance:")
    print(results["distances"][0][i])