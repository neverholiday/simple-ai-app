---
status: accepted
---

# Starter and Solution as folders holding only the Gap module

Students need the finished app for the Worksheet and a version with the three Gaps missing for the second exercise. The app code is shared and written once; only the module containing the Gaps exists twice, in `starter/` and `solution/`, and students choose which one the app uses when they start it. The same tests run against either. The Solution is deliberately visible in the repo: students may read it when stuck.

## Considered Options

- Git tags for starter and solution, like the Book Manager: rejected in favour of a layout that needs no git commands during the lab, since a failed checkout would stall a student.
- The whole app copied into two folders: rejected because every fix to shared code would have to be made twice, and the copies would drift.
- Worksheet on the instructor's app only: rejected because the Worksheet must be hands-on for every student.

## Consequences

- Anything students must write belongs in the Gap module; if a Gap ever needs code elsewhere, this layout has to be revisited.
- Before class, the Gap tests must pass against `solution/` and fail with clear messages against `starter/`.
