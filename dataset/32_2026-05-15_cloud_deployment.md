---
date: 2026-05-15
topic: "Cloud Deployment"
entry_id: journal-032
source: personal-journal
---

# Cloud Deployment

I containerized the small journal application and ran the frontend, API, database, and worker as separate services locally. This exposed several assumptions that were invisible when everything ran directly on my machine. Environment variables needed to be configured consistently, the API had to wait for the database, and the worker needed a reliable way to connect to the queue. I added health checks and documented the startup dependencies. The next step is to deploy the system to a cloud environment. Before doing that, I want to understand how secrets, networking, persistent storage, and logging should be handled instead of copying a local configuration directly into production.
