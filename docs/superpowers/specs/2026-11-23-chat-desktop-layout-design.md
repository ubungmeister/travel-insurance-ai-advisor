# Desktop chat layout — first-draft design

**Status:** Approved by the user on 2026-11-23; amended to use MUI per follow-up. No application code has been changed.

## Intent

Give the existing chat a familiar desktop web layout using MUI: conversation
history in a left sidebar and one main chat column with messages above the
selected-policy panel and composer. Keep this a light presentation refactor,
not a product or backend redesign.

## Approaches considered

1. **Light layout-only refactor (selected):** compose the existing chat sections
   into a desktop sidebar and main column. Render history using existing
   conversation IDs, policy numbers and activity timestamps. Preserve current
   APIs and chat behavior. This matches the requested first-draft scope.
2. **Add conversation titles/previews:** extend the API/backend to provide a
   title or first-message preview for each sidebar row. This is more familiar
   for long histories, but expands the work into data contracts and backend
   behavior, so it is deferred.

## Proposed first-draft behavior

- `ChatHistory` becomes a left-side navigation list with **New chat** and the
  existing conversations. Each row uses a label such as “Conversation #ID ·
  policy · activity date”; selection continues navigating to the exact saved
  conversation URL.
- The main column shows `ChatMessages` as its scrollable upper region. Existing
  persisted user and mocked assistant messages remain the only transcript
  content; no generated sample response, real AI, streaming or coverage advice
  is introduced. An empty chat remains empty until a user sends a message.
- `ChatPolicyPanel` sits directly above `ChatComposer`. It keeps its existing
  behavior: policy selection for a new chat and selected-policy details for a
  saved chat. Its visual treatment is a compact summary/selection block for
  this draft; deeper policy-panel design is deferred.
- Use MUI components and a shared light theme for the chat shell, history,
  message bubbles, policy panel, and composer. Keep the existing app-wide
  authentication route usable under MUI's baseline styles.
- Existing loading/error status and pending-send recovery remain visible in the
  main chat area without changing their state ownership or send/retry behavior.
- Existing page identity, logout and health indicators remain available. Use a
  restrained light desktop style, with no mobile navigation redesign.

## Architecture and safeguards

- Keep `ChatSessionProvider` as the sole owner of the chat controller and keep
  the sections as siblings consuming its context, in line with D-001 and D-006.
- React Query continues to own backend reads and send mutation state; tab-scoped
  draft storage continues to own editable text and immutable recovery payloads
  under D-002. Do not change API contracts, request timing, idempotency, query
  keys, account cleanup or backend behavior.
- Keep generic history, transcript and form views reusable through props; make
  layout/feature changes in the page composition, adapters and chat styles.
- Use MUI Material **9.6.0** with Emotion (`@emotion/react` and
  `@emotion/styled`), following the official installation guidance. Keep
  React/ReactDOM at **18.3.1** and install `react-is` **18.3.1** with a matching
  package override, as MUI documents for React 18. Do not add the separate MUI
  icons package for this first draft.
- Provide one app-level MUI `ThemeProvider` and `CssBaseline`; use the theme and
  MUI `sx`/components for chat styling instead of adding a second CSS system.
  Retain only minimal global sizing/reset styles needed for the app shell.
- MUI Core is MIT-licensed. Keep the existing auth route usable under the
  shared baseline and theme.

## Non-goals

No real AI/RAG, response generation, conversation-title service, pagination,
cross-device live sync, mobile-specific sidebar interactions, policy-detail
redesign, authentication changes or full application shell redesign.

## Verification expectations

Update frontend tests for sidebar history navigation, selected conversation,
new-chat action, and placement/preservation of policy, transcript, composer and
recovery sections. Run the frontend test, lint and build commands. These checks
do not replace browser verification of the desktop layout and chat/auth flows.

The current React Query chat and session-provider verification limits in
`docs/knowledge/index.md` remain in force; this design does not mark them as
verified.
