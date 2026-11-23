# Persisted Chat Implementation Plan

**Goal:** Persist mock turns and reopen owned conversation history, resuming the most recently active conversation.
**Spec:** `docs/superpowers/specs/2026-11-19-persisted-chat.md` (user approved resume-latest option).
**Execution:** Inline in the current `setup` branch; do not commit or change unrelated files.

## Tasks
- [x] Backend RED: add persistence/reload/order/list-isolation/read/write denial/unbound/rollback/validation tests in `backend/tests/test_persisted_chat.py`; adapt old stateless chat tests. Run and inspect failures.
- [x] Backend GREEN: add conversation repository owner-scoped lookups/listing; response schemas and read routes; transactional send service and authenticated chat router. Reuse models; no migration. Run full backend suite.
- [x] Frontend RED: extend existing frontend tests for history controls, ordered transcript, conversation-aware payload and history-first initialization. Use Node/Vite tooling with a dev-only React renderer for mounted recovery tests.
- [x] Frontend GREEN: typed APIs, history-first session hook with stale-operation guards, sibling history/policy/transcript/form UI, New chat and reload recovery. No browser transcript storage or automatic POST retries.
- [x] Update README, ERD behavior notes, AGENTS.md; run full backend suite, frontend tests/lint/build and targeted formatting. Request independent read-only review and address actionable findings.

## Review focus
- All read/write IDs must be scoped by authenticated UUID, including a user with no local record; no email-based authorization or existence leak.
- Both messages must commit or neither; stable ordering for equal timestamps, and PostgreSQL conversation row lock prevents interleaved turns.
- Refresh resumes without creating another conversation; failed history reads never fall back to creation.
- Pending load/send must not populate a different account/conversation; disable switching during send and ignore stale loads.
- Keep mock disclaimers, no-policy and multi-policy behavior, strict validation, recoverable load errors, and explicit handling of legacy unbound conversations.

## Progress / decisions
- Initial repository status clean on `setup`. Existing backend environment: `backend/.venv-local`; frontend Node/Vite test harness available.
- Most recent means latest message timestamp, falling back to conversation creation timestamp, then conversation ID descending. Messages use ID ascending regardless of timestamps.
- Backend RED: 9 expected failures in new endpoint/persistence tests, then 90 passing in the full suite before review.
- Frontend RED: new resume/payload/render tests failed on missing behavior, then passed. Cancellation test also failed before abort support was added.
- Review found four actionable recovery/order issues; each received a failing regression test before its fix: history retry must GET, ambiguous-send reload resets draft, timestamps are assigned after the lock, and frontend order retains PostgreSQL microseconds.
- Ruling: added dev-only `react-test-renderer@18.3.1` (matching React 18) to exercise mounted UI recovery and account changes, rather than relying only on SSR. No runtime dependencies added. Cost: one test dependency and its lockfile entries.
- Explicit UTC timestamp response normalization handles SQLite's dropped offsets and PostgreSQL session offsets; save/reload equality regression verified this requirement.
- Independent review completed. PostgreSQL row-lock concurrency and live authenticated browser E2E are not exercised by the SQLite/React renderer tests.
- npm installation reported Node 20 engine warnings (existing SDK expects Node >=22) and 12 audit advisories (8 moderate, 4 high); no unrelated dependency upgrades or audit fixes applied.
- Final verification: `backend/.venv-local/Scripts/python.exe -m pytest -q` from backend (relative executable `.venv-local/Scripts/python.exe`): 91 passed; `npm test`: 21 passed; `npm run lint`, `npm run build`, targeted Prettier, and `git diff --check`: passed. Backend emits Starlette/httpx deprecation warning; build emits >500 kB chunk warning.
- No commits, pushes, database migrations, or production-environment operations performed.
