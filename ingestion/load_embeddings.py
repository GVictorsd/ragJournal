import json
import chromadb
from pathlib import Path

# Configuration
# EMBEDDINGS_FILE = "data/embeddings.json"
EMBEDDINGS_FILE = Path("data/embedded_fixed_chunks.json").resolve()
# EMBEDDINGS_FILE = Path("data/embedded_semantic_chunks.json").resolve()
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "journal_chunks_fixed"
# COLLECTION_NAME = "journal_chunks_semantic"

# Load JSON
with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks")


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

# Create / get collection
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={
        "description": "Personal journal RAG chunks"
    }
)

# Prepare data
ids = []
documents = []
embeddings = []
metadatas = []

for chunk in chunks:

    ids.append(chunk["chunk_id"])
    # TODO: content or embedding_text??
    documents.append(chunk["content"])
    embeddings.append(chunk["embedding"])

    # Chroma metadata must contain simple values.
    # Convert lists such as keywords into strings.
    metadata = {
        "document_id": chunk["document_id"],
        "title": chunk.get("title", ""),
        "summary": chunk.get("summary", ""),
        "keywords": ", ".join(chunk.get("keywords", [])),
    }

    # Include additional metadata if available
    # TODO: include all the metadata from the chunks properly
    if "date" in chunk:
        metadata["date"] = chunk["date"]

    if "topic" in chunk:
        metadata["topic"] = chunk["topic"]

    metadatas.append(metadata)


# --------------------------------------------------
# Insert into ChromaDB
# --------------------------------------------------

collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas
)


print(f"Inserted {len(ids)} chunks into ChromaDB")


# --------------------------------------------------
# Verify
# --------------------------------------------------

print(
    f"Collection contains "
    f"{collection.count()} chunks"
)