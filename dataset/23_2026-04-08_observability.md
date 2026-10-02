---
date: 2026-04-08
topic: "Observability"
entry_id: journal-023
source: personal-journal
---

# Observability

I studied logging, metrics, and tracing after encountering a bug that was difficult to reproduce locally. The application logs contained useful information, but different services used inconsistent formats, making it hard to follow one request across the system. I experimented with structured logs containing request identifiers and operation names. I also learned more about the distinction between metrics and traces. Metrics are useful for seeing that latency increased, while traces can help explain which part of a request caused the delay. I want to include observability in my cloud project from the beginning rather than treating it as something added after deployment.
