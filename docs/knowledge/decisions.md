# Engineering decisions

Decisions describe approved defaults within a scope, not proof that every implementation complies. Cite these IDs in plans/reviews. Record a replacement and mark the old decision superseded rather than leaving conflicting approved rules.

## D-001: Focused frontend responsibilities and composition
- **Status / scope:** approved preference; AI Advisor frontend.
- **Decision:** pages/views compose focused sections; small coordinator hooks compose query, mutation and client-state hooks. Each state value has one owner. Keep API helpers separate and pure transforms outside hooks when they do not need React state/lifecycle.
- **Reason:** the former all-in-one chat hook was hard to navigate and mixed unrelated responsibilities. The user chose trainerlog's composition approach as the reference.
- **Sources:** [frontend architecture](frontend-architecture.md), pinned trainerlog examples, `AGENTS.md`.
- **Verification:** preference approved; latest chat-refactor implementation is not a fully verified example.

## D-002: React Query/server state, tab drafts/client state, backend/idempotency
- **Status / scope:** approved decision; current chat flow.
- **Decision:** focused `useQuery` reads and a `useMutation` send own server request/cache state. Existing draft storage owns editable text, selected policy and immutable pending UUID/payload. Backend receipts enforce duplicate prevention.
- **Reason:** consistent request management without asking a query cache to persist refresh recovery or prevent duplicate database writes.
- **Sources:** [frontend patterns](frontend-patterns.md), `frontend/src/lib/chat-drafts.ts`, `backend/app/models/chat_receipt.py`, `docs/superpowers/plans/2026-11-21-chat-query-refactor.md`.
- **Verification:** design approved; final refactor checks pending. Existing backend/data contracts are described in README/ERD and exercised by tests, with environment-specific limits.

## D-003: Manual retry and coordinated cache cleanup
- **Status / scope:** approved safeguards; chat sends and identity transitions.
- **Decision:** guard Send AND Retry offline; use `networkMode: 'always'` and `retry: false`; retry only the stored unchanged payload. Reset settled mutation state when recovery is resolved; `gcTime: 0` is limited inactive retention. At identity boundaries invalidate callbacks before abort/cancel/cache clear and separately reset tab/component state. History refresh failure cannot unconfirm a send.
- **Reason:** prevent paused/queued POSTs, stale-account callbacks, retained message variables, and duplicate resend after a lost response.
- **Sources:** [frontend patterns](frontend-patterns.md), `frontend/tests/chat-recovery.test.mjs`, refactor plan.
- **Verification:** rules approved; latest implementation verification pending. Clearing/resetting references is not a guarantee of secure memory erasure.

## D-004: Relevant, maintained doc blocks
- **Status / scope:** approved preference; non-obvious hooks/functions/stateful components and backend functions.
- **Decision:** TypeScript `/** ... */` or Python docstrings explain ownership, reasons and safeguards; keep them aligned with the same behavior change. Skip narration of obvious code.
- **Reason:** future edits need to preserve intent, not only understand the current statements.
- **Sources:** `AGENTS.md` and existing chat/auth doc blocks.
- **Verification:** a review obligation; comments do not prove runtime correctness.

## D-005: Trainerlog is a pattern reference, not a dependency mandate
- **Status / scope:** approved knowledge-base scope; project-local frontend guidance.
- **Decision:** pin provenance for trainerlog examples and distinguish current/approved/optional/proposed choices. Do not automatically copy its dependency versions, Java backend, token storage or all UI libraries.
- **Reason:** borrow architectural ideas without importing unrelated requirements or weakening existing auth/recovery safeguards.
- **Sources:** [frontend architecture](frontend-architecture.md), [technologies](technologies.md).
- **Verification:** source snapshot and current package inventory reviewed; optional tools are not adoption approvals.

## D-006: One chat session provider with context consumers
- **Status / scope:** approved preference; the chat feature's shared state access.
- **Decision:** `ChatSessionProvider` instantiates `useChatSessionController` once per account/route/logout-epoch scope. Feature sections consume `useChatSessionContext` without state-prop plumbing; generic form/history/transcript views retain reusable props behind adapters.
- **Reason:** each call to a stateful custom hook creates its own local state and mutation observer. React Query sharing does not make independent draft/controller instances equivalent to one session.
- **Sources:** explicit user approval of the provider/consumer approach; `frontend/src/components/chat/ChatSessionProvider.tsx`, `frontend/src/hooks/chat/use-chat-session-context.ts`, and [frontend architecture](frontend-architecture.md).
- **Verification:** implementation and added regressions await execution because the shell harness remains blocked. This clarifies D-001/D-002's one-owner rule; it does not replace React Query or tab storage.

## D-007: MUI for the first desktop chat layout
- **Status / scope:** approved decision; first-draft desktop chat UI, not a mandate to migrate auth or use MUI for every feature.
- **Decision:** use MUI Material 9.6.0 with Emotion for chat presentation and one shared light theme and `CssBaseline` at the app root. Keep React and ReactDOM at 18.3.1 and align the runtime `react-is` dependency and npm override to 18.3.1. Do not add the MUI icons package for this draft. D-002 and D-006 still govern ownership of chat state.
- **Reason:** share a consistent visual baseline while keeping the existing React version and chat behavior.
- **Sources:** user approval of the desktop chat layout and MUI choice (2026-11-23); `frontend/package.json`, `frontend/src/app/providers.tsx`, and [MUI installation guidance](https://mui.com/material-ui/getting-started/installation/).
- **Verification:** strict-peer clean install and dependency-tree checks under npm 8.19.3 (lockfile v2), the focused light-theme test, and the frontend build passed. Existing Node engine warnings and the build's chunk-size warning are separate from React peer compatibility. Desktop visuals and live browser chat/auth flows were not verified by these checks.

## Recording a new decision

Use: **ID/title; status; scope; choice; reason; sources; verification/limits; supersedes (if any)**. Explicit user choices are approved; new agent-derived preferences are proposed until approved. Keep application contract changes in README/ERD and applicable code/tests as well.
