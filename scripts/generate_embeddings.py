from pathlib import Path
from sentence_transformers import SentenceTransformer

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.rag.embedding import *

# INPUT_FILE = Path("enriched_fixed_chunks.json").resolve()
# OUTPUT_FILE = Path("embedded_fixed_chunks.json")
INPUT_FILE = Path("enriched_semantic_chunks.json").resolve()
OUTPUT_FILE = Path("embedded_semantic_chunks.json")
MODEL_NAME = "all-MiniLM-L6-v2"


def main():
    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print(f"Loading chunks from: {INPUT_FILE}")

    chunks = load_chunks(INPUT_FILE)
    if not chunks:
        raise ValueError("No chunks found in input file.")

    embeddings = generate_embeddings(
        chunks,
        model
    )

    save_embedded_chunks(
        chunks,
        embeddings,
        OUTPUT_FILE
    )

if __name__ == "__main__":
    main()