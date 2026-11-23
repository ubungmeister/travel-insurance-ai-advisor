# Persisted mock chat

User-approved behavior: resume the most recent conversation after login/refresh, with a history selector and New chat action. Keep the existing always-visible chat and sibling policy controls.

- Reuse conversation/message tables; no migration or runtime dependencies. POST `/api/v1/chat` requires a strict positive `conversation_id` and validated `message`. Derive the user from verified auth. Check conversation ownership, reject unbound legacy conversations, and save USER then ASSISTANT in a single transaction. Keep the existing `(mocked)` reply exactly; return `reply` plus the two persisted message records.
- GET `/api/v1/conversations` lists only owned conversations, latest activity first with deterministic ID tie-breaking. GET `/api/v1/conversations/{id}` returns selected policy and messages ordered by ID ascending. Foreign/missing IDs both return 404. Read operations never create conversations.
- Frontend initially loads history, resumes the first entry, or uses the existing policy-selection flow if history is empty. Failed history loads must not create a replacement. Selecting history loads it; New chat explicitly starts policy resolution. The browser stores no transcript. Sending includes the selected conversation ID and displays the saved turn; refresh obtains it from the server. Account-keyed UI prevents prior-account state reuse.
- Serialize concurrent turns by locking the conversation row in PostgreSQL. Do not retry POST automatically: after an ambiguous failure, offer Reload messages rather than silently duplicating the turn.
- Take message timestamps after the row lock (not PostgreSQL transaction-start `now()`), normalize API timestamps to UTC, and retain sub-millisecond ordering on the frontend. A successful explicit reload clears the composer draft to prevent duplicate resend after an ambiguous failure.
- Out of scope: LLM, RAG, streaming, deletion/renaming, message editing, real advice, pagination and cross-device live synchronization.

Approach: extend existing REST routers/services and React hooks. A browser-only transcript would not provide durable ownership-checked history; a separate chat subsystem is unnecessary.
