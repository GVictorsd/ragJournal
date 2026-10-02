---
date: 2026-03-09
topic: "Database Design"
entry_id: journal-016
source: personal-journal
---

# Database Design

I reviewed several database schemas from past projects and focused on indexing decisions. I realized that I understand basic indexes but do not always reason systematically about query patterns, cardinality, and write overhead. I designed a small example involving users, projects, tasks, and events, then listed the queries the application would run most frequently. Only after writing those queries did I choose candidate indexes. I also considered the cost of indexes on insert and update operations. This exercise reinforced the idea that database design should follow access patterns rather than adding indexes simply because a column appears in a WHERE clause.
