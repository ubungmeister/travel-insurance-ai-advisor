# Chat Hook Namespace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the current chat feature hooks and helpers to `frontend/src/hooks/chat/` without changing behavior or API boundaries.

**Architecture:** Keep the existing flat set of focused hooks/helpers and names, but align their feature directory with `pages/chat/`, `components/chat/`, and `forms/chat/`. Preserve the API's separate `api/chat/` and `api/conversation/` domains and the existing state ownership and export surface.

**Tech Stack:** React, TypeScript, Vite, React Query, Node test runner.

**Spec:** `docs/superpowers/specs/2026-11-23-chat-hooks-namespace-design.md`

## Global Constraints

- Move every file from `frontend/src/hooks/conversation/` into `frontend/src/hooks/chat/`; retain file names and flat organization.
- Preserve `useConversation` and `useConversationHistory` names; they still describe the API resources they read.
- Do not change runtime logic, routes, query keys, API modules, persistence, retry/recovery, auth/ownership, or the single-provider/controller rule.
- Keep `frontend/src/hooks/chat/index.ts` limited to `useChatSessionContext`; change the root barrel from `./conversation` to `./chat`.
- Update current source, test, README, and knowledge-guide path references. Do not rewrite historical plans.

## Review Focus

- A component or hook still importing the old source path: verify with a repository search and TypeScript build.
- A Vite SSR test still loading an old module path: verify with the full `npm test` run.
- The root or feature barrel accidentally broadens/changes its exports: inspect both barrel files and run lint/build.
- Current README or knowledge-guide references still point at the old folder: search current docs after migration.
- Accidental behavior/API changes during the move: inspect the diff and run all frontend tests.

---

### Task 1: Move the chat feature hook namespace

**Files:**
- Move all files in `frontend/src/hooks/conversation/` to `frontend/src/hooks/chat/`:
  - `index.ts`
  - `chat-query-keys.ts`
  - `chat-reconciliation.ts`
  - `chat-route.ts`
  - `chat-session-context.ts`
  - `use-chat-draft.ts`
  - `use-chat-policies.ts`
  - `use-chat-session-context.ts`
  - `use-chat-session-controller.ts`
  - `use-chat-transcript-auto-scroll.ts`
  - `use-conversation.ts`
  - `use-conversation-history.ts`
  - `use-send-chat-message.ts`
- Modify source imports in `frontend/src/components/chat/` and the root `frontend/src/hooks/index.ts` barrel.
- Modify Vite SSR module paths in `frontend/tests/chat-recovery.test.mjs`.
- Update current path references in `README.md`, `docs/knowledge/frontend-architecture.md`, `docs/knowledge/decisions.md`, and `docs/knowledge/lessons.md`.

**Interfaces:**
- Consumes: Existing chat-session, API, React Query, storage, and context interfaces.
- Produces: Same exported behavior, now under `frontend/src/hooks/chat/`; `frontend/src/hooks/index.ts` continues exporting auth, chat, and health.

- [ ] **Step 1: Run baseline checks before moving files.**

Run from `frontend/`:

```powershell
npm test
npm run lint
```

Expected: all current tests pass and lint exits successfully. Record any pre-existing warning; do not alter behavior to address unrelated warnings.

- [ ] **Step 2: Move the full folder and update references.**

Move `frontend/src/hooks/conversation/` to `frontend/src/hooks/chat/`. Update only imports and current references that name the old folder. Preserve internal hook/helper code and exports. Keep API modules and endpoint names unchanged.

- [ ] **Step 3: Verify the old path is no longer used in current code/docs.**

Run from repository root:

```powershell
git grep -n "hooks/conversation" -- README.md docs/knowledge frontend/src frontend/tests
```

Expected: no current-path references remain. Historical plan documents are intentionally outside this search and remain unchanged.

- [ ] **Step 4: Run full frontend verification.**

Run from `frontend/`:

```powershell
npm test
npm run lint
npm run build -- --outDir C:/Users/Artem/AppData/Local/Temp/opencode/chat-hooks-namespace-build
```

Expected: tests, lint, TypeScript compilation, and Vite build succeed. Use the temporary output directory to avoid clearing the existing `frontend/dist` directory.

- [ ] **Step 5: Review the final diff.**

Run from repository root:

```powershell
git diff --check
git status --short --branch
git diff --stat
```

Confirm only the approved folder move, reference updates, and this plan/design documentation changed. Leave changes unstaged; do not commit or push.
