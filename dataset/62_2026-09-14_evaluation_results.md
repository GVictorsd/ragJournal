---
date: 2026-09-14
topic: "Evaluation Results"
entry_id: journal-062
source: personal-journal
---

# Evaluation Results

I ran the latest evaluation set against the journal assistant. Simple factual questions were generally straightforward, while multi-entry questions exposed more problems. The system sometimes retrieved two relevant entries but missed a third entry containing an important detail. In a few cases the model combined information correctly but did not make it clear which source supported which statement. I am going to improve citation formatting and increase retrieval depth for synthesis questions. I also want to distinguish retrieval failure from generation failure in the evaluation logs. Without that distinction, it is difficult to know which part of the pipeline needs improvement.
