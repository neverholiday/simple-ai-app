---
status: accepted
---

# Python web app for the lecture demo

The course handoff fixes the Book Manager on Go, but students are not familiar with Go, and lectures already use Python scripts calling the model. The lecture demo is therefore a separate Python web app in the recipe domain, which grows those scripts into an app that shows the course's AI integration lessons: non-determinism, the Draft and Review boundary, validation of confidently wrong output, slowness with timeout and retry, fallback, one doorway to the model with a mock, and Demo Switches.

## Considered Options

- Go, matching the Book Manager: rejected because the audience cannot read it comfortably.
- Keeping plain scripts: rejected because a script cannot show the boundary between model output and a saved record, which is the central lesson.
- Rewriting the Book Manager in Python: out of scope for this app; the language of the labs is a separate decision.

## Consequences

- Students see the same lessons in two languages if the labs stay in Go, so the domain language (Draft, Review, Fallback) must match the Book Manager's concepts closely.
- Streaming, cost observability, prompt injection handling and semantic search are deliberately left out of version 1.
