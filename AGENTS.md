# Project guidance

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
- Current behavior: users can authenticate, start a conversation with an owned policy (auto-selected for one policy or chosen for multiple), and send mock chat messages. No-policy accounts see an empty state. Chat history APIs, persisted messages, and real coverage/LLM/RAG analysis are not implemented yet.
- Treat `README.md` and `docs/current-database-erd.md` as the current product and data-model references. Keep them aligned when behavior or schema changes.

## Key areas
- Backend: `backend/app/` contains API routers, services, repositories, models, schemas, auth dependencies, configuration, DB setup, and seeds. Alembic config/migrations live in `backend/alembic.ini` and `backend/alembic/` (including `versions/`).
- Frontend: `frontend/src/` contains app routing/providers, auth state and forms, pages, UI components, hooks, API clients, and client state (`store/`).
- Database: SQLAlchemy models in `backend/app/models/` and Alembic migrations in `backend/alembic/versions/` define versioned policies/catalog data, conversations, and messages. `backend/app/db/seed.py` supplies demo/catalog data used by tests.

## Existing behavior and contracts
- Supabase handles browser sign-in/session. The frontend currently signs in/out directly via the Supabase client, while the backend also exposes proxy auth endpoints at `/api/auth/login`, `/api/auth/refresh`, `/api/auth/logout`, and `/api/auth/me`. The frontend API client attaches the Supabase access token, and protected backend routes validate bearer JWTs.
- `GET /api/v1/policies` lists the authenticated user's policies.
- After login, show the chat immediately and resolve policies automatically. Show choices only for multiple policies; keep sending disabled until a bound conversation exists. Policy controls and the chat form are siblings, not a start-screen wrapper.
- `POST /api/v1/conversations` accepts an optional `policy_id`. Without a choice it returns `no_policies` (200, no save), `ready` (201, one policy auto-selected and saved), or `selection_required` (200, owned choices, no save). An explicit owned choice creates a bound conversation (201); unknown/other-user IDs return the same 404. Never trust a client-supplied policy ID without ownership verification.
- `POST /api/v1/chat` is authenticated but currently stateless and returns a mock reply; do not assume conversation/message persistence or real insurance analysis exists.

## PR review priorities
- **Authentication and ownership:** check JWT validation and protected-route coverage. Ensure every policy/conversation access is scoped to the authenticated user and cannot cross user boundaries.
- **Contracts and business rules:** verify endpoint status codes, response shapes, validation, policy auto-selection, and no-policy/missing-user handling against schemas, tests, and README behavior.
- **Database integrity:** scrutinize migrations, ORM/docs alignment, version pinning, constraints, indexes, foreign keys, cascades, data transformations, and seed changes. Flag destructive or hard-to-reverse changes.
- **Frontend/backend integration:** check API type/shape alignment, token/session behavior, auth expiry and error handling, and relevant user flows when either side changes.
- **Security and operations:** inspect secret/config/CORS handling, dependency changes, and logging. Avoid exposing tokens or sensitive payloads.
- **Tests:** preserve or update backend coverage in `backend/tests/` for auth, policy/conversation behavior, and schema changes. Frontend rendered-state tests live in `frontend/tests/`; they do not replace browser verification of UI/auth flows.
- Report only actionable bugs, regressions, security risks, or missing tests tied to changed code. Include file and line references; avoid style-only or speculative comments. Do not modify files during a review unless asked to fix findings.

## Common development commands
- Frontend: `cd frontend; npm install; npm run dev` (also `npm test`, `npm run lint`, `npm run format`, `npm run build`).
- Backend: `cd backend; python -m venv .venv; .venv\Scripts\activate; pip install -r requirements.txt; uvicorn app.main:app --reload`.
- Backend tests: `cd backend; pytest` (requires the backend environment/configuration).
