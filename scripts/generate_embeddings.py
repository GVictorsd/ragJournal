import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.rag.embedding import *

INPUT_FILE = Path("data/enriched_fixed_chunks.json").resolve()
OUTPUT_FILE = Path("data/embedded_fixed_chunks.json")
# INPUT_FILE = Path("data/enriched_semantic_chunks.json").resolve()
# OUTPUT_FILE = Path("data/embedded_semantic_chunks.json")
MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    '''
    Generate embeddings for the enriched chunks
    '''
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