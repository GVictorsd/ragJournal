import json
from pathlib import Path

# Load enriched chunks
def load_chunks(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict) and "chunks" in data:
        return data["chunks"]

    raise ValueError(
        "Expected JSON to contain either a list of chunks "
        "or an object with a 'chunks' field."
    )

# Build text for embedding
def build_embedding_text(chunk: dict) -> str:
    """
    Construct the semantic representation that will be embedded.

    We intentionally do not embed the entire JSON object because
    fields such as source path, filename, chunk_index, etc. are
    metadata rather than semantic content.
    """

    title = chunk.get("title", "").strip()
    summary = chunk.get("summary", "").strip()
    content = chunk.get("content", "").strip()
    keywords = chunk.get("keywords", [])
    questions = chunk.get("questions", [])

    # Convert lists into readable text
    keywords_text = ", ".join(
        str(keyword).strip()
        for keyword in keywords
        if str(keyword).strip()
    )

    questions_text = " | ".join(
        str(question).strip()
        for question in questions
        if str(question).strip()
    )

    embedding_text = (
        f"Title: {title}\n"
        f"Summary: {summary}\n"
        f"Keywords: {keywords_text}\n"
        f"Questions: {questions_text}\n"
        f"Content: {content}"
    )

    return embedding_text

# Generate embeddings
def generate_embeddings(chunks, model):
    embedding_texts = [
        build_embedding_text(chunk)
        for chunk in chunks
    ]
    print(f"Generating embeddings for {len(chunks)} chunks...")

    embeddings = model.encode(
        embedding_texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    return embeddings

# Save output
def save_embedded_chunks(chunks, embeddings, output_file: Path):

    output = []
    for chunk, embedding in zip(chunks, embeddings):

        embedded_chunk = {
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],

            # Original chunk information
            "content": chunk.get("content", ""),
            "title": chunk.get("title", ""),
            "summary": chunk.get("summary", ""),
            "keywords": chunk.get("keywords", []),
            "questions": chunk.get("questions", []),

            # Original metadata
            "metadata": chunk.get("metadata", {}),

            # Text actually sent to the embedding model
            "embedding_text": build_embedding_text(chunk),

            # Vector
            "embedding": embedding.tolist()
        }
        output.append(embedded_chunk)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved embedded chunks to: {output_file}")
    print(f"Number of chunks: {len(output)}")
    print(f"Embedding dimensions: {len(embeddings[0])}")