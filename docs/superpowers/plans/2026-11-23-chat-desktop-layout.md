# Chat Desktop Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the existing chat into a light MUI desktop layout with a history sidebar and a main conversation area.

**Architecture:** Keep `ChatSessionProvider` as the single owner and arrange the existing chat sections without changing their query, draft, recovery, or send responsibilities. Use MUI Core with one app-level light theme, replacing the Vite demo styling while keeping authentication usable. Render history from existing API fields; do not extend backend contracts.

**Tech Stack:** React 18.3.1, TypeScript, TanStack React Query 5, MUI Material 9.6.0 with Emotion, `react-is` 18.3.1 override, existing Node test runner and React test renderer. No icon package or other UI dependencies.

**Spec:** `docs/superpowers/specs/2026-11-23-chat-desktop-layout-design.md`

## Global Constraints

- This is a desktop web first draft; no mobile navigation redesign.
- Keep the existing APIs and chat behavior; no backend/data-contract changes.
- Display only persisted user and mocked assistant messages; add no generated sample response, real AI, streaming, or coverage advice.
- `ChatSessionProvider` remains the sole controller owner; chat sections remain siblings reading the shared context.
- React Query continues to own backend reads and send mutation state; tab-scoped draft storage continues to own editable text and immutable recovery payloads.
- Preserve request timing, idempotency, query keys, account cleanup, and send/retry behavior.
- History rows use conversation ID, policy and activity date; do not invent conversation titles or add title/preview API work.
- Use MUI Material 9.6.0 with Emotion; keep React/ReactDOM 18.3.1 and align `react-is` to 18.3.1 with an npm override.
- Keep the existing auth route usable and do not add `@mui/icons-material` or another component library.

## Review Focus

- MUI/React peer compatibility: `react-is` must resolve to 18.3.1 for React 18. Pin in Task 1 with dependency metadata/lockfile checks and run the production build.
- Empty history: **New chat** must remain available, with a clear empty-history state. Pin in Task 2 with an empty-history rendering test.
- Exact saved conversation: only the selected ID is marked active, and selection navigates to that exact `/chat/:conversationId`. Pin in Task 2 with active-row and adapter-navigation tests.
- History with many entries: the sidebar should scroll independently rather than expanding the whole page. Verify in Task 3 at a desktop viewport with an overflowing history list.
- Policy cardinality: zero policies must retain the existing guidance, one policy must remain visibly selected, and multiple policies must remain selectable on a new chat. Pin in Task 2 with a panel rendering test for all three cases and retain the existing no-policy send guard test.
- In-flight/rejected send: recovery actions must remain reachable in the main chat column, and the composer must preserve its existing send guards. Pin in Task 3 by extending the context-driven recovery test after the layout change.

---

### Task 1: Adopt MUI foundation and shared theme

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`
- Modify: `frontend/src/app/providers.tsx`
- Create: `frontend/src/app/theme.ts`
- Modify: `frontend/src/index.css`
- Modify: `frontend/src/App.css`
- Modify: `docs/knowledge/decisions.md`
- Modify: `docs/knowledge/technologies.md`
- Test: `frontend/tests/chat-recovery.test.mjs`

**Interfaces:**
- Export a single `appTheme` from `frontend/src/app/theme.ts` with `palette.mode === 'light'`.
- `Providers` keeps its existing query provider and wraps app content in MUI `ThemeProvider` plus `CssBaseline`.
- Add `@mui/material@9.6.0`, `@emotion/react`, `@emotion/styled`, and runtime `react-is@18.3.1`; set npm `overrides.react-is` to `18.3.1` and preserve the existing React 18 versions and lockfile format.

- [ ] **Step 1: Add a failing theme test** in `frontend/tests/chat-recovery.test.mjs` asserting that the exported app theme uses light mode.
- [ ] **Step 2: Run the focused theme test** with `cd frontend; node --test --test-name-pattern="application theme" tests/chat-recovery.test.mjs` and confirm it fails because the app theme does not yet exist.
- [ ] **Step 3: Install the MUI dependencies** at the specified compatible versions, align `react-is` through npm `overrides`, and confirm `package-lock.json` remains lockfile version 2 under npm 8.19.3.
- [ ] **Step 4: Add the light theme and provider integration** in `frontend/src/app/theme.ts` and `frontend/src/app/providers.tsx`; use `CssBaseline` once at the app root.
- [ ] **Step 5: Remove Vite demo global styles** from `index.css`/`App.css`, retaining only minimal root sizing needed by the app and auth route.
- [ ] **Step 6: Update technology/decision guidance** to record MUI as an approved chat-UI choice (not a blanket library mandate) and record dependency compatibility/verification limits.
- [ ] **Step 7: Rerun the focused theme test and `npm run build`**; confirm the theme test passes and no React peer mismatch/build errors remain.

### Task 2: Build the MUI history sidebar and policy panel

**Files:**
- Modify: `frontend/src/components/chat/ConversationHistory.tsx`
- Modify: `frontend/src/components/chat/ChatHistory.tsx` only if adapter semantics need adjustment; preserve its context-only responsibility.
- Modify: `frontend/src/components/chat/ChatPolicyPanel.tsx`
- Modify: `frontend/src/components/chat/PolicyDetails.tsx`
- Test: `frontend/tests/chat-recovery.test.mjs`

**Interfaces:**
- Keep `ConversationHistoryProps` (`history`, optional `conversationId`, `disabled`, `onSelect`, `onNew`) and the `ChatHistory` context adapter contract.
- Use MUI navigation/list/button/typography components. Render one accessible history list, a **New chat** action, a clear empty state, and an accessible selected row. Each row uses conversation ID, optional policy number, and readable activity date.
- Keep `ChatPolicyPanel`'s current context contract and zero/one/multiple-policy behavior; use MUI surfaces, typography and buttons for its compact summary/selection presentation.

- [ ] **Step 1: Add failing history tests** for an empty list that still exposes **New chat**, multiple entries with exactly one active ID, and selecting a row/New chat invoking their respective callbacks.
- [ ] **Step 2: Run the focused history tests** with `cd frontend; node --test --test-name-pattern="conversation history|chat history adapter" tests/chat-recovery.test.mjs` and confirm the new assertions fail against the current `<select>` UI.
- [ ] **Step 3: Implement the MUI history list** in `ConversationHistory.tsx` with active-row accessibility state, visible ID/policy/date labels, preserved disabled behavior, and no new API state.
- [ ] **Step 4: Add/adjust an adapter test** proving `ChatHistory` routes a selected row to exactly `/chat/{id}` and **New chat** to `/chat/new`; keep the adapter free of data ownership.
- [ ] **Step 5: Add failing `ChatPolicyPanel` tests** for no policies, one selected policy, and multiple selectable policy choices; implement its compact MUI presentation without changing selection logic.
- [ ] **Step 6: Rerun the focused history/policy tests** and confirm they pass.

### Task 3: Compose the MUI desktop chat shell

**Files:**
- Modify: `frontend/src/components/chat/ChatSession.tsx`
- Modify: `frontend/src/pages/chat/ChatPage.tsx`
- Modify: `frontend/src/components/chat/ChatTranscript.tsx`
- Modify: `frontend/src/forms/chat/ChatForm.tsx`
- Test: `frontend/tests/chat-recovery.test.mjs`

**Interfaces:**
- Keep all six feature sections (`ChatHistory`, `ChatMessages`, `ChatComposer`, `ChatPolicyPanel`, `ChatSessionStatus`, `PendingSendRecovery`) consuming the same provider context.
- Compose a labeled MUI `<Box component="aside">` for history and a `<Box component="main">` chat column. The transcript occupies the scrollable upper area; status/recovery remain visible in the main column; the policy panel sits immediately before the composer.
- Keep the existing page title, logout and health indicators available in a restrained header. Use a full-height desktop shell, independently scrollable history/transcript regions, compact MUI message bubbles and composer controls. Keep the auth route usable.

- [ ] **Step 1: Add failing layout assertions** to the existing chat integration test: history is inside the sidebar, transcript precedes the policy/composer region in the main column, and status/recovery still render within that column.
- [ ] **Step 2: Run the focused layout/recovery tests** with `cd frontend; node --test --test-name-pattern="chat layout|context-driven chat sections|empty policy account" tests/chat-recovery.test.mjs` and confirm the layout assertions fail before implementation.
- [ ] **Step 3: Recompose `ChatSession` and `ChatPage`** with MUI layout and header components without changing provider placement or calling the controller from a second component.
- [ ] **Step 4: Update `ChatTranscript` and `ChatForm`** with MUI typography/surfaces and a controlled MUI text input/button. Preserve message escaping/order, 2000-character limit, storage edits, send guards and recovery behavior.
- [ ] **Step 5: Rerun layout, policy and recovery tests**; confirm zero/one/multiple-policy behavior and pending/rejected send recovery remain unchanged.
- [ ] **Step 6: Run complete frontend checks** from `frontend/`: `npm test`, `npm run lint`, and `npm run build`. Record any pre-existing or environment-blocked failures without claiming them as passing.
- [ ] **Step 7: Browser-check the desktop layout** at a normal desktop viewport with empty and populated history, an older selected chat, a new-chat policy selection, and a pending/rejected-send state. Confirm history and transcript scroll independently, policy is directly above the composer, and the auth route still renders. If browser verification is unavailable, report it as pending.

## Execution Notes

- Follow the approved scope in the design spec; do not add conversation-title API work or change mocked backend responses.
- Keep comments/docstrings current for any changed non-obvious hooks or stateful components, per `AGENTS.md` and D-004. This plan expects no hook/state ownership changes.
- No commit or PR action is included.
