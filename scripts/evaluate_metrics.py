"""
Compare ChromaDB retrieval metrics before and after cross-encoder reranking.
No pandas required.

Evaluation JSON format:
[
  {"query": "...", "relevant_chunk_ids": ["journal-001_chunk_0"]}
]

Install:
    pip install chromadb sentence-transformers

Update CHROMA_PATH, COLLECTION_NAME, and EMBEDDING_MODEL_NAME below.
Run:
    python evaluate_retrieval_with_reranking.py

How it works:
1. Retrieve CANDIDATE_K chunks from ChromaDB using the existing embedding model.
2. Measure baseline metrics on the initial vector-search ranking.
3. Score each (query, chunk text) pair with a cross-encoder and reorder candidates.
4. Measure the same metrics on the reranked ranking.
5. Save per-query and aggregate before/after results.

The cross-encoder model is downloaded on first use. You need stored documents in ChromaDB
(or chunk text in metadata under CONTENT_METADATA_KEY) for reranking.
"""

import csv
import json
import math
from pathlib import Path
from statistics import mean, median

import chromadb
from sentence_transformers import CrossEncoder, SentenceTransformer


# --------------------------- Configuration ---------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
EVALUATION_DATASET = BASE_DIR / "eval_dataset/fixed_token_evaluation_dataset.json"
COLLECTION_NAME = "journal_chunks_fixed"
# EVALUATION_DATASET = BASE_DIR / "eval_dataset/semantic_chunks_evaluation_dataset.json"
# COLLECTION_NAME = "journal_chunks_semantic"

CHROMA_PATH = BASE_DIR / "chroma_db"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Cross-encoder used to rerank retrieved query/chunk pairs.
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

K_VALUES = [1, 3, 5]
MAX_K = max(K_VALUES)

# Retrieve more candidates than MAX_K so the reranker can improve their order.
# Set this to a value such as 20 or 50; it cannot exceed collection.count().
CANDIDATE_K = 10

# False: evaluation IDs match Chroma record IDs.
# True: evaluation IDs match metadata["chunk_id"].
USE_METADATA_CHUNK_ID = False

# Used only if Chroma's documents are absent. Set to the metadata field containing
# the actual chunk text, commonly "content" or "embedding_text".
CONTENT_METADATA_KEY = "content"

OUTPUT_CSV = BASE_DIR / "fixed_token_reranking_evaluation_results.csv"
OUTPUT_JSON = BASE_DIR / "fixed_token_reranking_evaluation_summary.json"
# OUTPUT_CSV = BASE_DIR / "semantic_reranking_evaluation_results.csv"
# OUTPUT_JSON = BASE_DIR / "semantic_reranking_evaluation_summary.json"


# --------------------------- Metrics ---------------------------

def precision_at_k(retrieved, relevant, k):
    return sum(chunk_id in relevant for chunk_id in retrieved[:k]) / k if k else 0.0


def recall_at_k(retrieved, relevant, k):
    if not relevant:
        return float("nan")
    return sum(chunk_id in relevant for chunk_id in retrieved[:k]) / len(relevant)


def mrr_at_k(retrieved, relevant, k):
    for rank, chunk_id in enumerate(retrieved[:k], start=1):
        if chunk_id in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved, relevant, k):
    if not relevant:
        return float("nan")
    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, chunk_id in enumerate(retrieved[:k], start=1)
        if chunk_id in relevant
    )
    ideal_count = min(len(relevant), k)
    idcg = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(1, ideal_count + 1)
    )
    return dcg / idcg if idcg else 0.0


def metrics_for_ranking(retrieved_ids, relevant_ids):
    """Return every configured metric for a single ranking."""
    result = {}
    for k in K_VALUES:
        result[f"precision@{k}"] = precision_at_k(retrieved_ids, relevant_ids, k)
        result[f"recall@{k}"] = recall_at_k(retrieved_ids, relevant_ids, k)
        result[f"mrr@{k}"] = mrr_at_k(retrieved_ids, relevant_ids, k)
        result[f"ndcg@{k}"] = ndcg_at_k(retrieved_ids, relevant_ids, k)
    return result


# --------------------------- Data helpers ---------------------------

def load_dataset(path):
    with path.open("r", encoding="utf-8") as file:
        dataset = json.load(file)
    if not isinstance(dataset, list):
        raise ValueError("Evaluation dataset must be a JSON list.")
    for i, item in enumerate(dataset):
        if not isinstance(item, dict) or "query" not in item or "relevant_chunk_ids" not in item:
            raise ValueError(f"Dataset item {i} must contain query and relevant_chunk_ids.")
        if not isinstance(item["relevant_chunk_ids"], list):
            raise ValueError(f"Dataset item {i}: relevant_chunk_ids must be a list.")
    return dataset


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def get_chunk_text(document, metadata, chunk_id):
    """Get text for cross-encoder scoring from stored document or metadata."""
    if document and str(document).strip():
        return str(document)
    if metadata:
        value = metadata.get(CONTENT_METADATA_KEY)
        if value is not None and str(value).strip():
            return str(value)
        # Common fallback field if CONTENT_METADATA_KEY wasn't set correctly.
        for key in ("content", "embedding_text", "text", "chunk_text"):
            value = metadata.get(key)
            if value is not None and str(value).strip():
                return str(value)
    raise ValueError(
        f"No chunk text found for Chroma ID {chunk_id!r}. "
        "Store documents in ChromaDB or set CONTENT_METADATA_KEY to the metadata text field."
    )


# --------------------------- Evaluation ---------------------------

def main():
    if not EVALUATION_DATASET.exists():
        raise FileNotFoundError(f"Evaluation dataset not found: {EVALUATION_DATASET}")
    if not CHROMA_PATH.exists():
        raise FileNotFoundError(
            f"ChromaDB directory not found: {CHROMA_PATH}. "
            "Update CHROMA_PATH to your persisted database."
        )

    dataset = load_dataset(EVALUATION_DATASET)
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as exc:
        available = [getattr(c, "name", str(c)) for c in client.list_collections()]
        raise RuntimeError(
            f"Collection {COLLECTION_NAME!r} not found. Available collections: {available}. "
            "Update COLLECTION_NAME."
        ) from exc

    collection_count = collection.count()
    if collection_count == 0:
        raise ValueError(f"Collection {COLLECTION_NAME!r} is empty.")

    retrieval_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    reranker = CrossEncoder(RERANKER_MODEL_NAME)
    candidate_k = min(CANDIDATE_K, collection_count)
    rows = []

    for query_number, item in enumerate(dataset, start=1):
        query = str(item["query"])
        relevant_ids = {str(x) for x in item["relevant_chunk_ids"]}
        query_embedding = retrieval_model.encode(query).tolist()

        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=candidate_k,
            include=["documents", "metadatas", "distances"],
        )

        chroma_ids = result["ids"][0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        if USE_METADATA_CHUNK_ID:
            candidate_ids = [
                str(metadata.get("chunk_id", chroma_id)) if metadata else str(chroma_id)
                for chroma_id, metadata in zip(chroma_ids, metadatas)
            ]
        else:
            candidate_ids = [str(chroma_id) for chroma_id in chroma_ids]

        candidate_texts = []
        for i, chroma_id in enumerate(chroma_ids):
            document = documents[i] if i < len(documents) else None
            metadata = metadatas[i] if i < len(metadatas) else None
            candidate_texts.append(get_chunk_text(document, metadata, str(chroma_id)))

        # Baseline is the original vector-search order.
        baseline_ids = candidate_ids[:MAX_K]

        # Cross-encoder scores each query/chunk pair, then sorts descending by score.
        pairs = [[query, text] for text in candidate_texts]
        scores = reranker.predict(pairs, show_progress_bar=False)
        ranked_indices = sorted(
            range(len(candidate_ids)),
            key=lambda i: float(scores[i]),
            reverse=True,
        )
        reranked_ids = [candidate_ids[i] for i in ranked_indices[:MAX_K]]

        answerable = bool(relevant_ids)
        row = {
            "query_id": query_number,
            "query": query,
            "is_answerable": answerable,
            "num_relevant_chunks": len(relevant_ids),
            "baseline_retrieved_ids": json.dumps(baseline_ids, ensure_ascii=False),
            "reranked_retrieved_ids": json.dumps(reranked_ids, ensure_ascii=False),
            "relevant_chunk_ids": json.dumps(sorted(relevant_ids), ensure_ascii=False),
            "baseline_top_1_is_relevant": (
                baseline_ids[0] in relevant_ids if answerable and baseline_ids else ""
            ),
            "reranked_top_1_is_relevant": (
                reranked_ids[0] in relevant_ids if answerable and reranked_ids else ""
            ),
            "vector_top_1_distance": distances[0] if distances else "",
            "reranked_top_1_score": (
                float(scores[ranked_indices[0]]) if ranked_indices else ""
            ),
        }

        baseline_metrics = metrics_for_ranking(baseline_ids, relevant_ids)
        reranked_metrics = metrics_for_ranking(reranked_ids, relevant_ids)

        for metric, value in baseline_metrics.items():
            row[f"baseline_{metric}"] = value if answerable else ""
        for metric, value in reranked_metrics.items():
            row[f"reranked_{metric}"] = value if answerable else ""

        rows.append(row)
        print(f"Evaluated query {query_number}/{len(dataset)}")

    write_csv(OUTPUT_CSV, rows)

    answerable_rows = [row for row in rows if row["is_answerable"]]
    unanswerable_rows = [row for row in rows if not row["is_answerable"]]

    metric_names = [
        f"{metric}@{k}"
        for k in K_VALUES
        for metric in ("precision", "recall", "mrr", "ndcg")
    ]
    baseline_summary = {}
    reranked_summary = {}
    deltas = {}

    for metric in metric_names:
        baseline_values = [
            float(row[f"baseline_{metric}"])
            for row in answerable_rows
            if row[f"baseline_{metric}"] != ""
        ]
        reranked_values = [
            float(row[f"reranked_{metric}"])
            for row in answerable_rows
            if row[f"reranked_{metric}"] != ""
        ]
        baseline_mean = mean(baseline_values) if baseline_values else None
        reranked_mean = mean(reranked_values) if reranked_values else None
        baseline_summary[metric] = baseline_mean
        reranked_summary[metric] = reranked_mean
        deltas[metric] = (
            reranked_mean - baseline_mean
            if baseline_mean is not None and reranked_mean is not None
            else None
        )

    summary = {
        "total_queries": len(rows),
        "answerable_queries": len(answerable_rows),
        "unanswerable_queries": len(unanswerable_rows),
        "collection_name": COLLECTION_NAME,
        "embedding_model": EMBEDDING_MODEL_NAME,
        "reranker_model": RERANKER_MODEL_NAME,
        "candidate_k": candidate_k,
        "macro_average_answerable_queries_only": {
            "baseline": baseline_summary,
            "after_reranking": reranked_summary,
            "absolute_delta_after_minus_before": deltas,
        },
        "notes": [
            "Metrics are macro-averaged over answerable queries only.",
            "Reranking can only reorder chunks in the retrieved candidate pool; it cannot recover chunks absent from that pool.",
            "A positive delta indicates an improvement for that metric; a negative delta indicates a regression.",
            "Cross-encoder scores are ranking scores, not calibrated probabilities.",
        ],
    }

    with OUTPUT_JSON.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    print("\\n=== Retrieval Metrics: Before vs After Reranking ===")
    print(f"Queries: {len(rows)} | Answerable: {len(answerable_rows)} | Unanswerable: {len(unanswerable_rows)}")
    print(f"Candidate pool per query: {candidate_k}")
    print(f"Reranker: {RERANKER_MODEL_NAME}")
    print("\\nMetric        Before     After      Delta")
    print("-" * 44)
    for metric in metric_names:
        before = baseline_summary[metric]
        after = reranked_summary[metric]
        delta = deltas[metric]
        before_s = "N/A" if before is None else f"{before:.4f}"
        after_s = "N/A" if after is None else f"{after:.4f}"
        delta_s = "N/A" if delta is None else f"{delta:+.4f}"
        print(f"{metric:12s} {before_s:>8s}   {after_s:>8s}   {delta_s:>8s}")

    print(f"\\nPer-query CSV: {OUTPUT_CSV}")
    print(f"Summary JSON : {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
