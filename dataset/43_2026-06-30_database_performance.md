---
date: 2026-06-30
topic: "Database Performance"
entry_id: journal-043
source: personal-journal
---

# Database Performance

I investigated a query that became slow after the amount of data increased. The query plan showed that the database was scanning more rows than expected. I compared the filter conditions with existing indexes and found that the index did not align well with the most selective part of the query. After testing an alternative index, the query improved significantly. I also checked the write cost because every index has a maintenance cost. This was a good reminder that performance depends on real data distribution and workload. A query that works perfectly on a small development database can behave very differently in production.
