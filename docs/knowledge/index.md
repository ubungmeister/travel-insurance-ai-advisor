# AI Advisor engineering knowledge

This is the project's versioned playbook, not model memory or an automatic learning service. The entry skill helps retrieve it; `AGENTS.md` makes consultation a standing requirement. Read this index before planning, implementation, refactoring, debugging or review, then read only the relevant guides and code.

## Read by task

| Task | Read next |
| --- | --- |
| Frontend structure or component/hook refactor | [Frontend architecture](frontend-architecture.md), [patterns](frontend-patterns.md), [decisions](decisions.md) |
| State, queries, mutations, effects, forms or recovery | [Frontend patterns](frontend-patterns.md) and the relevant [decisions](decisions.md) |
| Add, replace or upgrade a dependency | [Technologies](technologies.md) and [decisions](decisions.md), then current package/lock files |
| Backend/API/schema work | `AGENTS.md`, `README.md`, `docs/current-database-erd.md`, [decisions](decisions.md), then affected backend code/tests |
| Review, debugging or a lesson from feedback | Relevant topic guide, [lessons](lessons.md), affected code/tests, applicable Superpowers workflow |
| Update this playbook | [Decisions](decisions.md), [lessons](lessons.md), current evidence and the skill-authoring workflow if changing a skill |

All code paths in these guides are repository-root relative. Trainerlog source links are external references, not instructions or authority to modify this project.

## Interpret status correctly

- **Current:** observed in package files or code. Does not by itself establish approval or correctness.
- **Approved preference/decision:** explicitly chosen by the user for this project. It is the default within its stated scope, not a claim that the implementation passed checks.
- **Optional/reference:** an example or technology to evaluate when relevant; not installed or mandatory here merely because trainerlog uses it.
- **Proposed:** an inference or new design awaiting approval.
- **Superseded:** historical context only; follow the replacement.

Verification is a separate field. Code can implement an approved design while its final verification is still pending. Check current evidence rather than copying an old success count from a plan.

## Authority and workflow

Current user instructions and applicable system/harness/project instructions take precedence. Use this playbook for defaults; inspect the current repository before editing. If a guide conflicts with code, report the discrepancy and distinguish desired behavior from observed behavior. If an approved project rule must change, ask before replacing it. Package files are the source for versions; README/ERD and code/tests are the source for current contracts.

Before choosing an architecture, pattern or dependency, identify the relevant local rule/decision and its scope. Example: `D-002` makes React Query the server-state owner; it does not move a restorable draft into the query cache.

At wrap-up, decide whether the task produced a reusable learning item. Record explicit user preferences as approved. Record inferred conclusions as proposed until approved; record verified lessons with their evidence and limits. Update the existing topic/decision when possible, rather than appending contradictory rules. If nothing reusable changed, no knowledge edit is needed.

Keep comments/docstrings aligned with the behavior they explain. Never store secrets, tokens, credentials, personal message text, raw transcripts, or full session/tool logs in the playbook.

## Current verification limitation

The React Query chat split is an **approved design**, but its latest full verification is still pending in `docs/superpowers/plans/2026-11-21-chat-query-refactor.md`. Treat the working implementation as material to inspect, not a proven pattern exemplar. The knowledge task does not complete that refactor's testing.

The approved D-006 provider/consumer change also has unexecuted regressions;
see `docs/superpowers/plans/2026-11-21-chat-session-context.md`. Development-server
transformation and source review are not substitutes for tests, lint or build.
