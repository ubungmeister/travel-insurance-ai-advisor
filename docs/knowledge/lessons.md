# Reusable engineering lessons

This is a curated set of rules with evidence, not a raw session history. Approval and verification are separate. A passing check has a scope and date/context; it is not permanent proof. Never copy credentials or user messages into a lesson.

## L-001: Stable effect dependencies need a clear owner
- **Status / scope:** approved guidance; React effects calling a callback from another hook.
- **Lesson:** extract the stable callback and the primitive value used by the effect; reference those names in both body and dependency array. Do not add a whole newly created result object or suppress the warning merely to silence lint.
- **Reason:** dependencies must track what the effect reads without making its lifecycle depend on unrelated result identity changes.
- **Evidence:** the chat auto-selection effect produced a missing-`draft` dependency warning. It was changed to use a stable destructured callback and selected policy ID; see `frontend/src/hooks/conversation/use-chat-session-controller.ts` and [frontend patterns](frontend-patterns.md).
- **Verification limit:** the final lint rerun for that correction was blocked by the harness. Treat it as an approved approach with verification pending, not a verified lint result.

## L-002: A request failure is not proof that its write failed
- **Status / scope:** approved safeguard; state-changing requests with refresh recovery.
- **Lesson:** persist exact request identity/payload before sending; an uncertain outcome uses manual idempotent replay. Keep a definitive rejection distinguishable so users can restore/discard instead of retrying it forever.
- **Reason:** a response can be lost after commit; silently replacing the UUID can create a duplicate conversation/turn. Rejection restore must not overwrite later typing.
- **Evidence:** `backend/tests/test_persisted_chat.py`, `frontend/tests/chat-recovery.test.mjs`, receipt model and the existing recovery contracts in README/ERD.
- **Verification limit:** prior backend/browser checks established particular recovery scenarios, not the final React Query refactor. Rerun current checks before a completion claim; SQLite race tests do not replace live PostgreSQL checks.

## L-003: Reference a real API and always settle controlled test transports
- **Status / scope:** proposed maintenance guidance based on an observed failure; query/mutation interaction tests. The fix's final verification is still pending.
- **Lesson:** check the installed library's actual public/event interface before using an introspection method. A controlled HTTP promise must settle or reject on cleanup even if an assertion fails.
- **Reason:** an invalid test assertion can strand a mock transport and keep the test runner alive, hiding later verification. Do not infer a mutation method from a similarly named query method.
- **Evidence:** the pending refactor's test used a nonexistent mutation observer-count method. The test was changed to observe mutation-cache removal events and guaranteed transport settlement; record in `docs/superpowers/plans/2026-11-21-chat-query-refactor.md`.
- **Verification limit:** latest corrected test run is pending. A review of a test's source is not a passing suite.

## Maintain knowledge after work

1. Decide whether there is a reusable preference, decision or lesson. No reusable change means no new entry is needed.
2. Search the existing guides/IDs first. Improve an existing entry or record a replacement rather than duplicating it.
3. An explicit user preference may be recorded as **approved**, citing that approval. A new inference remains **proposed**; do not silently promote it even if an experiment passed.
4. Record **scope, lesson/choice, reason, sources/evidence, and verification limits**. Observed failure can justify a proposed fix; it does not verify that fix.
5. Align the relevant topic guide, decision and doc blocks when the adopted rule changes. Add tests/lint/validation for enforceable behavior, keeping Superpowers process instructions in their existing skills.
6. Review old entries when affected. Mark superseded guidance with its replacement; keep raw task history in task plans, not in the playbook.

**Example:** after a blocked lint run, record the dependency warning and the intended callback/value split with `verification: pending`. Do not write `lint passed` or make the current file a proven example. Once checks run, update the evidence with the actual command/result.
