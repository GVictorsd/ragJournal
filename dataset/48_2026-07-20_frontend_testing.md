---
date: 2026-07-20
topic: "Frontend Testing"
entry_id: journal-048
source: personal-journal
---

# Frontend Testing

I added tests for a few important frontend interactions and discovered that the tests themselves exposed unclear component responsibilities. A component that handled data loading, transformation, rendering, and navigation was difficult to test without a large setup. After separating the responsibilities, the tests became simpler. I also learned that mocking every dependency can make tests pass while providing little confidence. I want tests to exercise realistic boundaries where practical. For future frontend work, I will consider testability during component design rather than waiting until the end.
