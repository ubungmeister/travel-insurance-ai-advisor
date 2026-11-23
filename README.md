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
`POST /api/v1/conversations` is retained for existing API clients. The browser
does not call it: **New chat** opens `/chat/new`, where `GET /api/v1/policies`
supplies owned choices and a sole policy is auto-selected. Selecting a policy
or typing a draft does not create a database conversation. No-policy accounts
see account/support guidance.

Saved chats use `/chat/:conversationId`. Refresh loads that exact conversation;
invalid, missing or foreign IDs show an unavailable state, not another chat.
The home route resumes a local new-chat draft if present, otherwise the most
recently active saved chat, or `/chat/new` if history is empty. The history
selector can reopen an older chat. Production hosting must serve the SPA's
`index.html` for `/chat/*` as well as `/`.

## Persisted mock chat

All endpoints below require a Bearer access token and derive ownership from its
verified UUID, not a client-supplied user ID:

- `GET /api/v1/conversations`: owned summaries, latest activity first (latest
  message timestamp, or creation timestamp for empty conversations; ties use
  descending conversation ID). Summaries include `conversation_id`,
  `selected_policy`, `created_at`, and `last_activity_at`.
- `GET /api/v1/conversations/{id}`: `conversation_id`, `selected_policy`,
  `created_at`, and `messages` ordered by ascending message ID. Each message has
  `id`, `role` (`USER` or `ASSISTANT`), `content`, and `created_at`.
- `POST /api/v1/chat` requires a UUID `request_id`, `message`, and exactly one
  positive integer target: `policy_id` for a first turn or `conversation_id` for
  a saved chat. The backend verifies ownership and atomically saves any new
  conversation, user message, and existing `(mocked)` assistant reply. HTTP 200
  returns `conversation_id`, `reply`, and the two saved `messages`. Input is
  limited to 2000 characters and trimmed for display; invalid input is HTTP 422.
- The database reserves `(user_id, request_id)` in the same transaction. An
  exact replay returns the original IDs and turn, including when two requests
  race; a changed target or exact message returns HTTP 409. A new UUID is a
  deliberate new send, even for identical text. A deleted result is not recreated.

Unknown and other-user conversation IDs both return HTTP 404 with
`detail: "Conversation not found"`. Legacy conversations without a selected
policy can be read but reject sends with HTTP 409; use **New chat** to select a
policy. Creation alone still saves no messages.

Tab-scoped `sessionStorage` stores only the editable draft, selected policy,
and the exact pending request for each account and chat. It is not secure
storage; no auth token or server transcript is stored there. Explicit logout
and account changes clear chat data. Explicit logout also clears other tabs for
the same account using an opaque logout marker in `localStorage`; no draft or
message text is shared between tabs. Session expiry preserves recovery data
for the same account after reauthentication.

If the browser cannot confirm a send, **Retry pending message** resends the
original UUID and payload. Refresh never resends, and offline clicks do not
queue sends. Confirmation clears only the matching recovery record and
preserves later typing. First-send confirmation opens the saved URL, and
message IDs prevent duplicate transcript entries on replay. A rejected send
(`404`, `409`, or `422`) can instead be restored for editing or discarded.
Restore is available when the composer is empty, so it cannot overwrite newer
typing. Confirmed sends refresh the history list from the server.

Apply Alembic revision `a31b6d2e90fc` (`alembic upgrade head` from `backend/`)
before deploying the new chat endpoint. Coordinate backend and frontend deploys:
older chat clients do not send the now-required request UUID. PostgreSQL row
locking serializes existing-conversation mock turns. Do not hold this lock
while waiting for a future external inference request.
There is no pagination or live cross-device synchronization in this milestone.
Replies remain mocked: no LLM, RAG, streaming, or real coverage advice is added.

## Verification

### Frontend chat organization

- `frontend/src/hooks/chat/use-chat-session-controller.ts` composes the route,
  policy/history/detail queries, tab draft, and send hook; it does not duplicate
  their request or transcript state. `ChatSessionProvider` creates it once in an
  account/route/logout-epoch scoped boundary; feature sections read that same
  result with `useChatSessionContext` rather than instantiate controllers.
- `use-chat-policies.ts`, `use-conversation-history.ts`, and `use-conversation.ts`
  use React Query with account-scoped keys. `use-send-chat-message.ts` uses a
  mutation with automatic retry disabled and `networkMode: 'always'`; both Send
  and Retry check connectivity rather than silently queueing a message.
- `use-chat-draft.ts` remains responsible for editable and pending data in tab
  storage. `chat-account-boundary.ts` invalidates late callbacks before aborting
  active sends, cancelling queries, and clearing query/mutation caches on identity
  changes. Ordinary navigation does not clear the app-wide client.
- Confirmation updates the matching conversation cache and resets the mutation
  observer; history invalidation is a separate best-effort refresh. Mutation
  `gcTime: 0` limits inactive retention, not secure memory erasure.
- `ChatSession` composes `ChatPolicyPanel`, `ChatSessionStatus`, and
  `PendingSendRecovery` alongside `ChatHistory`, `ChatMessages`, and
  `ChatComposer`. Those adapters keep the generic history/transcript/form views
  reusable with props. Missing chat context throws an explicit provider error.

### Commands

- Backend (from `backend/`, with dependencies/configuration available): `python -m pytest`.
- Frontend (from `frontend/`): `npm test`, `npm run lint`, `npm run build`.
- Frontend tests use Node's test runner, Vite SSR, React test renderer, and
  HTTP-boundary stubs to check exact URL loading, tab drafts and account
  scoping, offline behavior, lost-response recovery and transcript deduplication.
  They are not live browser E2E tests.
