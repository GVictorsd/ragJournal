---
date: 2026-03-17
topic: "RAG Experiment"
entry_id: journal-018
source: personal-journal
---

# RAG Experiment

I built the first small version of the journal RAG pipeline. I used markdown files as the document format because they are easy to inspect and can include metadata such as dates and topics. I tested splitting entries into chunks and storing metadata alongside each chunk. A question like “What did I learn about caching?” worked reasonably well, but broad questions about changes over time were harder. I realized that retrieval needs both semantic similarity and metadata filtering. For example, a query about career decisions may benefit from restricting results to entries in a particular period. I want to compare pure vector search with a hybrid approach using keyword and semantic signals.
