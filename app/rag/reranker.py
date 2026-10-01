from sentence_transformers import CrossEncoder
from typing import List, Dict, Any


class CrossEncoderReranker:

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        print(f"Loading reranker: {model_name}")

        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:

        if not results:
            return []

        # Create query-document pairs
        pairs = [
            (query, result["content"])
            for result in results
        ]

        # Cross-encoder relevance score
        scores = self.model.predict(pairs)

        # Attach scores to original results and sort
        reranked = []
        for result, score in zip(results, scores):
            reranked.append({
                **result,
                "rerank_score": float(score),
            })

        reranked.sort(
            key=lambda x: x["rerank_score"],
            reverse=True,
        )

        for rank, result in enumerate(
            reranked[:top_n],
            start=1,
        ):
            result["rerank_rank"] = rank

        return reranked[:top_n]


def format_chroma_results(results) -> list[dict]:

    formatted = []

    for chunk_id, document, metadata, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        formatted.append({
            "chunk_id": chunk_id,
            # "content": document,
            "content": metadata.content,
            "metadata": metadata,
            "vector_distance": float(distance),
        })

    return formatted
