# Policy Selection Implementation Plan

**Goal:** Start mock chats with an authenticated user's selected policy, never creating unbound conversations.

**Architecture:** Reuse the conversation creation endpoint with an optional positive integer `policy_id`. No body/empty body preserves automatic single-policy selection; multiple policies return choices with HTTP 200 and no saved conversation. Explicit selection is checked against authenticated ownership and returns HTTP 201 only on creation; unavailable IDs return identical HTTP 404 responses.

**Tech stack:** Existing FastAPI/Pydantic/SQLAlchemy and React/TypeScript/React Query. No dependencies or database migrations needed.

**Scope:** User's milestone request is the specification. Keep mock chat stateless; no RAG, advice, history, streaming, or policy upload. Execute inline without an approval pause as requested. Preserve unrelated existing AGENTS.md changes; do not commit automatically.

## Tasks
- [x] Backend tests first: update multiple-policy test to assert no saved conversation, then select an owned choice; cover missing/foreign IDs (including users with no local record/policies), invalid bodies, and authentication. Run and confirm expected failures.
- [x] Backend: add strict optional `policy_id` request schema; validate ownership using the existing user-scoped repository; return choices without writes; create only with a selected policy. Run conversation/policy/model/chat/auth regression tests.
- [x] Frontend: add typed conversation API and mutation hook; automatically resolve policies after login with loading/error/retry and no-policy states, accessible policy-choice buttons and selected-policy summary. Show chat immediately; gate sending on successful creation. Keep state scoped to the current auth user and disable duplicate clicks. Use the existing response choices rather than an extra listing request.
- [x] Documentation: update README, ERD behavior notes, and AGENTS.md current contracts/limitations without overwriting existing user work.
- [x] Verify: backend suite, frontend lint/build, diff whitespace and focused review. Report exact commands and unavailable checks; do not claim live browser verification if it was not run.

## Review focus
- Missing/other-user IDs must return the same response and save nothing, even when the caller has one policy (no silent fallback).
- Strict positive integer IDs and rejected extra fields must prevent ownership/identity injection.
- Choice discovery must never persist; selection must persist exactly one owned, bound conversation and no messages.
- Frontend resolves on mount once (including StrictMode effect replay), not on every render/refetch. It must not expose prior-user state on account changes; error recovery must retain choices.
- Policy summaries must distinguish number, plan/version, territory, dates and status; UI must explicitly identify mock replies as not coverage advice.

## Execution record
- Worked inline in the current `setup` checkout as requested; preserved pre-existing AGENTS.md content and made no commits.
- Backend RED: 13 expected failures / 7 passes in conversation tests before implementation. GREEN: 58 focused tests, then 75 tests in the full backend suite.
- Used `backend/.venv-local/Scripts/python.exe`: root `.venv` lacks pytest and `backend/.venv` has no executable. No dependencies installed.
- Frontend tests added using existing Node/Vite/React tooling without new dependencies; rendered-state tests and choice/start callback tests are not browser integration tests.
- Frontend lint and production build passed. Build has a >500 kB chunk warning; backend suite has a Starlette/httpx deprecation warning.
- Independent read-only review: no blocking findings. Deferred test gap: no mounted ChatSession/network integration or browser E2E coverage of rapid clicks, account changes, and mutation completion. Those paths were implemented but not browser-verified.
- Initial concurrent shell attempts for lint/build encountered transient pwsh access-denied errors; sequential retries succeeded.

## User-requested UI revision
- Removed the separate Start chat screen and `ChatStartView` wrapper. `ChatSession` renders `PolicySelection` and `ChatForm` as siblings, with the form always visible and disabled until ready.
- Conversation hook initializes automatically once per mount with a ref guard for StrictMode effect replay; hook-level mutation callbacks retain choices and survive observer resubscription.
- No backend/API changes. Tests now assert absence of a manual start action and immediate chat-form visibility while resolving policies.
- Render tests isolate the browser Supabase module: no authentication or network is needed for SSR assertions, and the installed SDK requires native WebSocket support absent in Node 20.
- Revision verified: 10 frontend tests, frontend lint/build, targeted Prettier, and 75 backend tests pass. Independent UI revision review found no blocking issues. Live browser/StrictMode mounting remains unverified by automated E2E tests.
