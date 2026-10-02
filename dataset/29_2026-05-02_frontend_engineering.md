---
date: 2026-05-02
topic: "Frontend Engineering"
entry_id: journal-029
source: personal-journal
---

# Frontend Engineering

I spent time reviewing component design in a React application. Some components had become difficult to reuse because they mixed data fetching, state management, and presentation. I experimented with separating data-loading logic from visual components. This made the UI pieces easier to test and reason about. However, excessive abstraction also created additional files and indirection, so I do not want to split every small component automatically. The useful boundary seems to be where a component has a distinct responsibility or is reused in multiple places. I wrote down a few examples because I want to compare them with future frontend work.
