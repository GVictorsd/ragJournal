---
date: 2026-02-20
topic: "System Design"
entry_id: journal-012
source: personal-journal
---

# System Design

I studied caching strategies and compared cache-aside, write-through, and write-behind approaches. The biggest takeaway was that caching introduces consistency and invalidation problems rather than simply making everything faster. I sketched a service where frequently requested data is cached, with the database remaining the source of truth. I then considered what should happen if the cache is unavailable. The API should still be able to fall back to the database, although this could increase load. I also thought about stale values and TTLs. These exercises are helping me move away from memorizing architecture diagrams. During an interview I want to be able to explain why a particular component exists and what trade-off it creates.
