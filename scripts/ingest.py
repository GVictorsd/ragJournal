import sys
from pathlib import Path
# 1. Get the directory of myscript.py, then get its parent (my_project root)
root_dir = Path(__file__).resolve().parent.parent
# 2. Add the root directory to Python's module search path
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import json
from dataclasses import asdict

from app.rag.ingestion import load_markdown_documents
from app.rag.chunking import (
    FixedTokenChunker,
    SemanticChunker,
)


def main():

    # --------------------------------
    # 1. Load documents
    # --------------------------------

    documents = load_markdown_documents(
        "../dataset"
    )

    print(
        f"Loaded {len(documents)} documents"
    )

    # --------------------------------
    # 2. Fixed-size chunking
    # --------------------------------

    fixed_chunker = FixedTokenChunker(
        chunk_size=500,
        overlap=100,
    )

    fixed_chunks = (
        fixed_chunker.chunk_documents(
            documents
        )
    )

    print(
        f"Fixed chunking produced "
        f"{len(fixed_chunks)} chunks"
    )

    return

    # --------------------------------
    # 3. Semantic chunking
    # --------------------------------

    semantic_chunker = SemanticChunker(
        similarity_threshold=0.65,
        max_chunk_characters=4000,
    )

    semantic_chunks = (
        semantic_chunker.chunk_documents(
            documents
        )
    )

    print(
        f"Semantic chunking produced "
        f"{len(semantic_chunks)} chunks"
    )

    # --------------------------------
    # 4. Save results for inspection
    # --------------------------------

    with open(
        "fixed_chunks.json",
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            [
                asdict(chunk)
                for chunk in fixed_chunks
            ],
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    with open(
        "semantic_chunks.json",
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            [
                asdict(chunk)
                for chunk in semantic_chunks
            ],
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    print("Chunking complete.")


if __name__ == "__main__":
    main()