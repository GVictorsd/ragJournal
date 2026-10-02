---
date: 2026-09-10
topic: "RAG Retrieval Comparison"
entry_id: journal-061
source: personal-journal
---

# RAG Retrieval Comparison

I compared keyword retrieval with vector retrieval using a small set of journal questions. Keyword search worked very well for exact terms such as “Kubernetes” or “cache-aside,” while vector search handled paraphrased questions better. However, vector retrieval sometimes returned conceptually related entries that were not actually useful. A hybrid approach appears promising because lexical matching can provide precision for important terms while semantic similarity can handle variations in wording. I also want to experiment with reranking the top results before sending them to the language model. Retrieval quality seems to be the part of the project with the most room for improvement.
