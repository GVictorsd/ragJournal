---
date: 2026-01-10
topic: "Software Architecture"
entry_id: journal-003
source: personal-journal
---

# Software Architecture

I reviewed the architecture of a web application I have been working with and tried to understand it as a set of responsibilities rather than a collection of folders. The frontend handles presentation and interaction, the API coordinates business operations, repositories manage persistence, and background workers handle tasks that do not need to block a request. Thinking this way made several design decisions easier to explain. I also noticed areas where boundaries are not clean and a change in one layer often requires changes elsewhere. I wrote down examples of coupling so I can discuss them later when studying refactoring. One important lesson is that architecture is not about creating as many layers as possible. Every abstraction should have a reason, and the cost of indirection should be justified by the problem it solves.
