# TODO: chunks should look like this:
# {
#   "chunk_id": "journal-001_chunk_001",
#   "date": "2026-01-03",
#   "title": "Career Planning",
#   "summary": "Planning career goals for the upcoming year.",
#   "keywords": ["career", "goals", "planning"],
#   "questions": [
#     "What are my career goals?",
#     "What did I plan for my career?"
#   ],
#   "cleaned_text": "I started the year by writing down..."
# }

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import json
from pathlib import Path
from app.rag.chunk_enricher import ChunkEnricher
from app.models.chunk import EnrichedChunk
from dataclasses import asdict


INPUT_FILE = Path("fixed_chunks.json").resolve()
OUTPUT_FILE = Path("enriched_fixed_chunks.json")
# INPUT_FILE = Path("semantic_chunks.json").resolve()
# OUTPUT_FILE = Path("enriched_semantic_chunks.json")


def main():
    CLOUD_HOST = ''

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks.")

    enricher = ChunkEnricher(
        ollama_host=CLOUD_HOST
    )
    enriched_chunks = []

    for index, chunk in enumerate(chunks, start=1):

        chunk_id = chunk["chunk_id"]

        print(
            f"[{index}/{len(chunks)}] "
            f"Enriching {chunk_id}..."
        )

        # try:

        #     enrichment = enricher.enrich_chunk(
        #         chunk
        #     )

        #     if "metadata" not in chunk:
        #         chunk["metadata"] = {}

        #     chunk["metadata"]["enrichment"] = (
        #         enrichment
        #     )

        #     print(
        #         f"    ✓ {enrichment['title']}"
        #     )

        # except Exception as e:

        #     print(
        #         f"    ✗ Failed: {e}"
        #     )

        #     chunk["metadata"]["enrichment"] = {
        #         "title": "",
        #         "summary": "",
        #         "keywords": [],
        #         "questions": []
        #     }

        try:
            enrichment = enricher.enrich_chunk(chunk)

            enriched_chunk = EnrichedChunk(
                chunk_id=chunk["chunk_id"],
                document_id=chunk["document_id"],
                content=chunk["content"],
                title=enrichment.get("title", ""),
                summary=enrichment.get("summary", ""),
                keywords=enrichment.get("keywords", []),
                questions=enrichment.get("questions", []),
                metadata=chunk.get("metadata", {}),
            )

            enriched_chunks.append(enriched_chunk)

            print(
                f"    ✓ {enriched_chunk.title}"
            )

        except Exception as e:
            print(
                f"    ✗ Failed: {e}"
            )
            enriched_chunk = EnrichedChunk(
                chunk_id=chunk["chunk_id"],
                document_id=chunk["document_id"],
                content=chunk["content"],
                title="",
                summary="",
                keywords=[],
                questions=[],
                metadata=chunk.get("metadata", {}),
            )
            enriched_chunks.append(enriched_chunk)

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            [asdict(chunk) for chunk in enriched_chunks],
            # chunks,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print(
        f"Saved to {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()