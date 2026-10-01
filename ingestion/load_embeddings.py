import json
import chromadb
from pathlib import Path

# Configuration
# EMBEDDINGS_FILE = Path("data/embedded_fixed_chunks.json").resolve()
EMBEDDINGS_FILE = Path("data/embedded_semantic_chunks.json").resolve()
CHROMA_PATH = "./chroma_db"
# COLLECTION_NAME = "journal_chunks_fixed"
COLLECTION_NAME = "journal_chunks_semantic"

def load_embeddings_to_chroma(
    embeddings_file: str,
    collection_name: str,
    chroma_path: str = "./chroma_db"
):
    with open(embeddings_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    client = chromadb.PersistentClient(path=chroma_path)

    collection = client.get_or_create_collection(
        name=collection_name
    )

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for chunk in chunks:
        ids.append(chunk["chunk_id"])
        documents.append(chunk["embedding_text"])
        embeddings.append(chunk["embedding"])

        source_metadata = chunk.get("metadata", {})
        metadata = {
            **source_metadata,
            "document_id": chunk["document_id"],
            "title": chunk.get("title", ""),
            "content": chunk["content"],
        }
        metadatas.append(metadata)

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )
    print(f"Loaded {len(ids)} chunks")
    print(f"Collection count: {collection.count()}")

    return collection


def main():
    col = load_embeddings_to_chroma(
        embeddings_file=EMBEDDINGS_FILE,
        collection_name=COLLECTION_NAME,
        chroma_path=CHROMA_PATH
    )
    print(col)

if __name__=='__main__':
    main()