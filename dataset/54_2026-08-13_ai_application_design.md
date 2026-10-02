---
date: 2026-08-13
topic: "AI Application Design"
entry_id: journal-054
source: personal-journal
---

# AI Application Design

I sketched a more complete architecture for the journal assistant. A document ingestion service would parse markdown entries, normalize metadata, create chunks, and generate embeddings. A retrieval service would combine semantic search with metadata filtering. The application API would pass retrieved evidence to the generation model and return both the answer and citations. I also want a feedback mechanism so incorrect retrievals can be recorded for evaluation. The design is becoming more interesting than the original prototype because it now includes ingestion, retrieval, generation, evaluation, and observability as separate concerns.
