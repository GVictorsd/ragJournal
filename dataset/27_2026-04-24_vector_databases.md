---
date: 2026-04-24
topic: "Vector Databases"
entry_id: journal-027
source: personal-journal
---

# Vector Databases

I compared several concepts behind vector databases and embedding indexes. The most important distinction is between storing vectors and actually designing a useful retrieval system. An embedding model determines how text is represented, while the index determines how efficiently similar vectors can be found. I also learned that similarity does not always equal relevance. Two chunks can be semantically similar while only one actually answers the question. For the journal project, I want to preserve the original text and metadata along with the embedding so that retrieved results remain understandable. I also plan to test different chunk sizes because an overly small chunk may lose context while an overly large chunk may reduce retrieval precision.
