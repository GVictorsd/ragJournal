import sys
from pathlib import Path
import json
from dataclasses import asdict

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.rag.fixedTokenChunker import FixedTokenChunker
from app.rag.semanticChunker import SemanticChunker
from app.rag.ingestion import load_markdown_documents


def main():
    FIXED_TOKEN_CHUNK_SIZE = 200
    FIXED_TOKEN_OVERLAP = 25
    FIXED_TOKEN_OUTPUT_FILE = Path("data/fixed_chunks.json")
    SEMANTIC_CHUNK_OUTPUT_FILE = Path("data/semantic_chunks.json")

    #  Load documents
    documents = load_markdown_documents("dataset")
    print(f"Loaded {len(documents)} documents")

    # Fixed-size chunking
    fixed_chunker = FixedTokenChunker(
        chunk_size=FIXED_TOKEN_CHUNK_SIZE,
        overlap=FIXED_TOKEN_OVERLAP,
    )

    fixed_chunks = (
        fixed_chunker.chunk_documents(
            documents
        )
    )
    print(f"Fixed chunking produced {len(fixed_chunks)} chunks")

    # Semantic chunking
    semantic_chunker = SemanticChunker(
        similarity_threshold=0.65,
        max_chunk_characters=4000,
    )

    semantic_chunks = (
        semantic_chunker.chunk_documents(
            documents
        )
    )
    print(f"Semantic chunking produced {len(semantic_chunks)} chunks")

    # Save results
    with open(
        FIXED_TOKEN_OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            [ asdict(chunk) for chunk in fixed_chunks ],
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    with open(
        SEMANTIC_CHUNK_OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            [ asdict(chunk) for chunk in semantic_chunks ],
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    print("Chunking complete")


if __name__ == "__main__":
    main()