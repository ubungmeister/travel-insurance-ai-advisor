# Chat Refresh and Send Recovery Implementation Plan

**Goal:** Restore exact URL chats and recover uncertain sends without duplicate database writes.

**Design:** Keep `/` as resume entry, `/chat/new` as a tab draft, and `/chat/:conversationId` as an exact read. Scope session storage to the account and route; store only draft, policy and immutable pending payload. Keep explicit retry and account-aware authentication. A persisted receipt keyed by local authenticated user and request UUID claims each send atomically; compare a fingerprint of its target and exact input, and reference the committed turn. Preserve legacy conversation creation for existing API callers, not the UI.

**Tasks**
- [x] Phase 1: test route resolution, draft storage and account cleanup. Wire protected routes, login return path, read-only policy selection and controlled composer.
- [x] Phase 2 backend: test validation, replay/conflict, rollback, access denial and concurrent requests; add receipt migration/model and atomic first/existing turn endpoint.
- [x] Phase 2 frontend: test lost response across remount, explicit original-payload retry and matching-only cleanup; connect send and transcript reconciliation.
- [x] Document API/migration/privacy, run backend and frontend checks, and report unverified infrastructure. Preserve existing staged changes; no commit or live database migration.

**Verification:** 98 backend tests and 10 frontend tests passed. Concurrent requests used separate connections to a file-backed SQLite database. Alembic reported one head and rendered PostgreSQL upgrade SQL for the new revision. Frontend lint/build and targeted formatting were checked. Independent source review found no actionable issues. Live PostgreSQL concurrency/migration and authenticated browser E2E were not run.
