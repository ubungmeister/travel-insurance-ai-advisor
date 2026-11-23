# Project guidance

## Consult project knowledge first
- Before planning, implementation, refactoring, debugging or review, use the project-local `project-context` skill and read `docs/knowledge/index.md`, then its relevant topic guides. If the harness cannot load that skill, read those files directly and report the limitation; do not skip the knowledge lookup.
- Use the playbook's status and source fields to distinguish approved preferences from observed code, optional trainerlog references, and proposals. Follow current user/harness instructions first; keep existing architecture approval gates.
- At task wrap-up, apply the learning rules in `docs/knowledge/lessons.md`: maintain reusable preferences/lessons with evidence and verification limits, without secrets or raw transcripts. Do not mark an unverified implementation as a proven example.

## Architecture and diagram requests
When the user explicitly asks to design or revise application architecture, use the project-scoped specialist agents under .codex/agents/ for independent read-only reviews:
- product_architect for goals, scope, user flows, and unknowns
- solution_architect for architecture options and trade-offs
- architecture_reviewer for an independent simplicity, privacy, and insurance-answering risk review
- diagram_architect to express the synthesized proposal as Mermaid diagrams

Keep the lead agent responsible for synthesis and user communication. Ask the specialists to cite repository paths for observed facts and label assumptions separately. Wait for independent reviews before synthesizing. Then have the diagram specialist produce draft diagrams from the synthesis; it must label unresolved choices rather than silently decide them.

For architecture work, do read-only discovery first. Present options, a recommendation, diagrams, risks, and open decisions for the user to correct or approve. Do not edit application code or begin implementation until the user explicitly approves. If the user asks to save a draft, limit changes to architecture documentation and report the exact files.

## Project context (AI Advisor)
- This is an early-stage travel-insurance advisor with a React + TypeScript + Vite frontend (`frontend/`) and a FastAPI backend (`backend/`).
- Current behavior: users authenticate, resume their most recent conversation, reopen history, or start a new conversation with an owned policy (auto-selected for one policy or chosen for multiple). User messages and mock replies are persisted. No-policy accounts see an empty state. Real coverage/LLM/RAG analysis is not implemented.
- Treat `README.md` and `docs/current-database-erd.md` as the current product and data-model references. Keep them aligned when behavior or schema changes.

## Key areas
- Backend: `backend/app/` contains API routers, services, repositories, models, schemas, auth dependencies, configuration, DB setup, and seeds. Alembic config/migrations live in `backend/alembic.ini` and `backend/alembic/` (including `versions/`).
- Frontend: `frontend/src/` contains app routing/providers, auth state and forms, pages, UI components, hooks, API clients, and client state (`store/`).
- Database: SQLAlchemy models in `backend/app/models/` and Alembic migrations in `backend/alembic/versions/` define versioned policies/catalog data, conversations, and messages. `backend/app/db/seed.py` supplies demo/catalog data used by tests.

## Existing behavior and contracts
- Supabase handles browser sign-in/session. The frontend currently signs in/out directly via the Supabase client, while the backend also exposes proxy auth endpoints at `/api/auth/login`, `/api/auth/refresh`, `/api/auth/logout`, and `/api/auth/me`. The frontend API client attaches the Supabase access token, and protected backend routes validate bearer JWTs.
- `GET /api/v1/policies` lists the authenticated user's policies.
- Saved chats use `/chat/:conversationId`; exact URL reads must not fall back to another chat. `/chat/new` is a browser draft and only reads owned policies until Send. History/policy controls and the chat form remain siblings.
- `POST /api/v1/conversations` accepts an optional `policy_id`. Without a choice it returns `no_policies` (200, no save), `ready` (201, one policy auto-selected and saved), or `selection_required` (200, owned choices, no save). An explicit owned choice creates a bound conversation (201); unknown/other-user IDs return the same 404. Never trust a client-supplied policy ID without ownership verification.
- `POST /api/v1/chat` requires `request_id` (UUID), `message`, and exactly one of `policy_id` or `conversation_id`. It verifies ownership and atomically claims the user-scoped receipt and saves the mock turn (plus a conversation on first Send). Matching replays return the original result, changed payloads return 409. Do not hold a database lock during future external inference.
- `GET /api/v1/conversations` lists owned conversations by latest activity descending; `GET /api/v1/conversations/{id}` returns owned detail and messages by ID ascending. Foreign/missing IDs both return 404. Keep drafts and immutable pending requests in account/chat-scoped tab storage, without transcripts or tokens. Manual retry reuses the same payload. Purge on logout or account change, not expiry for the same account.

## Code comments and docstrings
- Compose focused frontend hooks instead of putting request, draft, and UI logic in one hook/component. Chat query hooks own server state through React Query; `useChatDraft` and storage helpers own restorable client state. Keep API functions separate from both.
- Shared chat sections consume `useChatSessionContext` from one account/route/logout-epoch scoped `ChatSessionProvider`. Only the provider instantiates `useChatSessionController`; do not duplicate the controller in children. Generic views keep props behind feature adapters (knowledge decision D-006).
- Chat sends use `networkMode: 'always'`, `retry: false`, and an offline guard for Send and Retry. Account/route-scoped query keys do not replace ownership checks. Logout/account changes invalidate callbacks, abort/cancel work, and clear query AND mutation caches; draft storage and component state must reset separately. History refresh errors must not unconfirm a send.
- When adding or changing a non-obvious hook, standalone function, or stateful component, add or update its documentation: `/** ... */` above the declaration in TypeScript/React or a docstring inside the declaration in Python.
- Explain what it is responsible for, why it is designed that way, and any assumptions or safeguards a future change must preserve (such as lifecycle, ownership, retries, or transaction boundaries). Use enough detail to be useful without narrating the implementation.
- Keep these blocks current in the same change as the behavior they describe. Skip obvious components, wrappers, and helpers; use short inline comments only where the local reason is not clear.

## PR review priorities
- **Authentication and ownership:** check JWT validation and protected-route coverage. Ensure every policy/conversation access is scoped to the authenticated user and cannot cross user boundaries.
- **Contracts and business rules:** verify endpoint status codes, response shapes, validation, policy auto-selection, and no-policy/missing-user handling against schemas, tests, and README behavior.
- **Database integrity:** scrutinize migrations, ORM/docs alignment, version pinning, constraints, indexes, foreign keys, cascades, data transformations, and seed changes. Flag destructive or hard-to-reverse changes.
- **Frontend/backend integration:** check API type/shape alignment, token/session behavior, auth expiry and error handling, and relevant user flows when either side changes.
- **Security and operations:** inspect secret/config/CORS handling, dependency changes, and logging. Avoid exposing tokens or sensitive payloads.
- **Tests:** preserve or update backend coverage in `backend/tests/` for auth, policy/conversation behavior, and schema changes. Frontend rendered-state tests live in `frontend/tests/`; they do not replace browser verification of UI/auth flows.
- Report only actionable bugs, regressions, security risks, or missing tests tied to changed code. Include file and line references; avoid style-only or speculative comments. Do not modify files during a review unless asked to fix findings.
- Before preparing a PR, run `/pr-review [base-branch-or-commit]` for an independent, different-model review of the intended changes and relevant architecture/component patterns. Treat it as advisory: evaluate findings yourself, resolve or explicitly discuss actionable issues, and keep tests/lint/build/browser checks as separate verification gates. For explicit architecture proposals, retain the specialist workflow above.

## Common development commands
- Frontend: `cd frontend; npm install; npm run dev` (also `npm test`, `npm run lint`, `npm run format`, `npm run build`).
- Backend: `cd backend; python -m venv .venv; .venv\Scripts\activate; pip install -r requirements.txt; uvicorn app.main:app --reload`.
- Backend tests: `cd backend; pytest` (requires the backend environment/configuration).
