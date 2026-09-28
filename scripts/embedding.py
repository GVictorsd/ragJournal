import json
from pathlib import Path
from typing import List, Dict

from sentence_transformers import SentenceTransformer
from tqdm import tqdm


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

INPUT_FILE = Path("data/enriched_chunks.json")
OUTPUT_FILE = Path("data/embedded_chunks.json")

MODEL_NAME = "BAAI/bge-small-en-v1.5"

BATCH_SIZE = 32


# ---------------------------------------------------------
# Load chunks
# ---------------------------------------------------------

def load_chunks(file_path: Path) -> List[Dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------
# Create text representation for embedding
# ---------------------------------------------------------

def build_embedding_text(chunk: Dict) -> str:
    """
    Build the text that will be converted into an embedding.

    We include useful semantic metadata but avoid chunk_id/date
    because they generally don't contribute to semantic retrieval.
    """

    title = chunk.get("title", "")
    summary = chunk.get("summary", "")
    keywords = chunk.get("keywords", [])
    questions = chunk.get("questions", [])
    text = chunk.get("cleaned_text", "")

    if isinstance(keywords, list):
        keywords_text = ", ".join(keywords)
    else:
        keywords_text = str(keywords)

    if isinstance(questions, list):
        questions_text = " ".join(questions)
    else:
        questions_text = str(questions)

    embedding_text = f"""
Title: {title}

Summary: {summary}

Keywords: {keywords_text}

Questions this chunk can answer:
{questions_text}

Content:
{text}
""".strip()

    return embedding_text


# ---------------------------------------------------------
# Generate embeddings
# ---------------------------------------------------------

def generate_embeddings(
    chunks: List[Dict],
    model: SentenceTransformer,
    batch_size: int = 32
) -> List[List[float]]:

    embedding_texts = [
        build_embedding_text(chunk)
        for chunk in chunks
    ]

    embeddings = model.encode(
        embedding_texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    return embeddings.tolist()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print(f"Loading chunks from: {INPUT_FILE}")

    chunks = load_chunks(INPUT_FILE)

    print(f"Loaded {len(chunks)} chunks")

    print(f"Loading embedding model: {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)

    print("Generating embeddings...")

    embeddings = generate_embeddings(
        chunks,
        model,
        batch_size=BATCH_SIZE
    )

    # Attach embeddings to chunks
    for chunk, embedding in tqdm(
        zip(chunks, embeddings),
        total=len(chunks),
        desc="Attaching embeddings"
    ):
        chunk["embedding"] = embedding

        # Optional:
        # store the exact text used to create the embedding.
        chunk["embedding_text"] = build_embedding_text(chunk)

    # Save
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            chunks,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("Embedding generation complete.")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Chunks: {len(chunks)}")
    print(f"Embedding dimensions: {len(embeddings[0])}")


if __name__ == "__main__":
    main()