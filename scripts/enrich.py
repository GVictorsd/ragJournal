import sys
import json
from pathlib import Path
from dataclasses import asdict

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.rag.chunk_enricher import ChunkEnricher
from app.models.chunk import EnrichedChunk

INPUT_FILE = Path("data/fixed_chunks.json").resolve()
OUTPUT_FILE = Path("data/enriched_fixed_chunks.json")
# INPUT_FILE = Path("data/semantic_chunks.json").resolve()
# OUTPUT_FILE = Path("data/enriched_semantic_chunks.json")


def main():
    '''
    Generate enrichment fields (summary, keywords, questions)
    from an LLM through Ollama
    '''

    OLLAMA_HOST = ''
    MODEL = "qwen2.5:3b"

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks.")

    enricher = ChunkEnricher(
        ollama_host=OLLAMA_HOST,
        model=MODEL
    )

    enriched_chunks = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_id = chunk["chunk_id"]
        print(
            f"[{index}/{len(chunks)}] "
            f"Enriching {chunk_id}..."
        )

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
            print(f"Fone: {enriched_chunk.title}")

        except Exception as e:
            print(f"Failed: {e}")
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
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()