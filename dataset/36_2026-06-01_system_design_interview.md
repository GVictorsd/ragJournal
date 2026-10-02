---
date: 2026-06-01
topic: "System Design Interview"
entry_id: journal-036
source: personal-journal
---

# System Design Interview

I practiced designing a notification system. The requirements included sending notifications asynchronously, supporting retries, preventing duplicate sends, and allowing users to choose notification preferences. I started with a simple API and database, then introduced a queue when I considered slow external providers. I also added an idempotency key to prevent repeated requests from creating duplicate notifications. The exercise showed me that good system design starts with requirements and constraints rather than immediately choosing technologies. I am going to practice more designs this way, writing down functional requirements, scale assumptions, failure modes, and consistency requirements before drawing the architecture.
