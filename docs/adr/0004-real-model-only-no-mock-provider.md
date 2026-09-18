---
status: accepted
---

# Real model only; no Mock provider in the app

Students run the app themselves in a hands-on session, and each student uses their own Gemini API key, created and tested before class. Every Extraction therefore calls the real model, and the app has no Mock provider. Failures are still reproducible because Demo Switches wrap the real provider. Automated tests use a fake defined in the test code, which the app never loads.

This narrows the "one doorway to the model with a mock" wording in ADR-0001: the doorway remains, as the place where Demo Switches, timeouts and retries apply.

## Considered Options

- A Mock provider inside the app, like the Book Manager: rejected. Its only remaining purpose was insurance against poor wifi or missing keys, while it cost prepared Drafts to keep in sync with real model behaviour and made the Comparison page show identical columns.
- A shared instructor key: rejected because many students on one key would hit rate limits, which would look like random Errors during the lab.

## Consequences

- The hands-on session depends on working wifi and every student having a working key before it starts.
- Real non-determinism is always visible, including in the Comparison page.
