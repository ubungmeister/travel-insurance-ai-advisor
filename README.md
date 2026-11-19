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

`POST /api/v1/conversations` requires a Bearer access token and no request body.
The backend uses only the authenticated user's linked policies:

- No policies: HTTP 200, `status: "no_policies"`, null `conversation_id` and
  `selected_policy`, empty `policy_choices`. No conversation is saved.
- One policy: HTTP 201, `status: "ready"`, a saved `conversation_id`, the
  `selected_policy` summary, and empty `policy_choices`.
- Multiple policies: HTTP 201, `status: "selection_required"`, a saved
  `conversation_id`, null `selected_policy`, and owned `policy_choices`.

Policy summaries include the policy number, plan, territory, and travel dates.
Creation does not save messages. Policy selection, history, and persisted chat
endpoints are not implemented yet; `/api/v1/chat` remains a stateless mock.
