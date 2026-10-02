---
date: 2026-08-01
topic: "RAG Chunking"
entry_id: journal-051
source: personal-journal
---

# RAG Chunking

I experimented with different chunk sizes for the journal corpus. Very small chunks retrieved precise phrases but sometimes lacked enough context to explain why something happened. Larger chunks preserved context but occasionally returned unrelated paragraphs. I also tested overlapping chunks and found that a small overlap helped preserve ideas that crossed boundaries. Metadata became especially useful for the journal because entries already have dates and topics. I am considering storing both an entry-level document and chunk-level records so the application can retrieve a precise passage while still displaying the complete source entry when necessary.
