---
status: accepted
---

# Review is the second validation layer; no "no validation" Demo Switch

Unlike the Book Manager, which saves extracted output directly and uses `DEMO_NO_VALIDATION` to show the database rejecting a bad genre, this app never saves a Draft: every Recipe is saved through Review, which submits the same form and runs the same rules as Manual Entry. Turning off Draft validation therefore cannot let bad data reach the database, so the switch would only demonstrate something artificial. Lesson 3 is shown by forcing a Rejected Draft instead.

Recipes are stored in SQLite with Unit as a foreign key, kept as a quiet safety net rather than a demo. SQLite ignores foreign keys unless `PRAGMA foreign_keys = ON` is set on every connection, so that setting is required.

## Considered Options

- Postgres in Docker, matching the Book Manager: rejected to keep the demo free of Docker.
- In-memory or a JSON file: rejected because they have no constraints, leaving no safety net below application validation.
