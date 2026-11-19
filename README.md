# AI Advisor

Full-stack app with a React (Vite) frontend and a Python (FastAPI) backend.

```
├── frontend/
├── backend/
├── .gitignore
├── README.md
└── .env.example
```

## Frontend

React + TypeScript, scaffolded with Vite.

```bash
cd frontend
npm install
npm run dev
```

Runs on [http://localhost:5173](http://localhost:5173).

## Backend

FastAPI served with Uvicorn.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Runs on [http://localhost:8000](http://localhost:8000).

Test it: [http://localhost:8000/health](http://localhost:8000/health) should return:

```json
{
  "status": "ok"
}
```

## Environment variables

Copy `.env.example` to `.env` at the repo root. Fill in the values; `.env` files are gitignored and never committed. Both the backend and the frontend (Vite) read from this single root `.env`.

## Database ERD

See the [implemented database ERD](docs/current-database-erd.md).

## Conversation creation

`POST /api/v1/conversations` requires a Bearer access token. The optional JSON
body contains only `policy_id` (a positive integer). Omitting the body, sending
`{}`, or using `{"policy_id": null}` asks the backend to resolve the user's
policies automatically. The backend uses only the authenticated user's linked
policies; the client never supplies a user ID.

Without an explicit policy choice:

- No policies: HTTP 200, `status: "no_policies"`, null `conversation_id` and
  `selected_policy`, empty `policy_choices`. No conversation is saved.
- One policy: HTTP 201, `status: "ready"`, a saved `conversation_id`, the
  `selected_policy` summary, and empty `policy_choices`.
- Multiple policies: HTTP 200, `status: "selection_required"`, null
  `conversation_id` and `selected_policy`, and owned `policy_choices`. No
  conversation is saved until a choice is submitted.

With `{"policy_id": 123}`, the backend verifies ownership, then returns HTTP 201,
`status: "ready"`, a saved `conversation_id`, the `selected_policy` summary, and
empty `policy_choices`. Unknown and other-user policy IDs both return HTTP 404
with `detail: "Policy not found"` and save nothing. Invalid IDs and unknown
request fields return HTTP 422. `GET /api/v1/policies` remains available for
listing owned policies (including past/future or cancelled policies).

Policy summaries include the policy number, plan, territory, and travel dates.
After login, the chat is visible immediately and policy resolution starts
automatically. A sole policy is selected automatically; multiple policies appear
as choices above the chat with plan/version, territory, travel dates, and status.
No-policy accounts see account/support guidance. Sending is disabled until a
bound conversation is created. Policy controls and the chat form are separate
siblings, not a start-screen wrapper. Refreshing the page resets this UI and
resolves policies again; for a single-policy account this creates a new
conversation, not history.

Creation does not save messages. `/api/v1/chat` remains an authenticated,
stateless mock: it does not consume the conversation ID or analyze the selected
policy. History, persisted messages, RAG, and real coverage advice are out of scope.

## Verification

- Backend (from `backend/`, with dependencies/configuration available): `python -m pytest`.
- Frontend (from `frontend/`): `npm test`, `npm run lint`, `npm run build`.
- Frontend tests use Node's test runner with Vite SSR to check rendered
  start/empty/selection/loading/error/ready states; they are not browser E2E tests.
