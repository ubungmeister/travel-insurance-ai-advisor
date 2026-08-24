# AI Advisor

Full-stack app with a React (Vite) frontend and a Python (FastAPI) backend.

```
├── frontend/
│   └── .env.example
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

Copy `.env.example` to `.env` at the repo root, and copy `frontend/.env.example` to `frontend/.env`. Fill in the values; `.env` files are gitignored and never committed.
