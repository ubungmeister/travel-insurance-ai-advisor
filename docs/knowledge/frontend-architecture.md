# Frontend architecture

**Status:** approved project preference: focused responsibilities and composition, inspired by trainerlog. The exact AI Advisor implementation still requires its pending final verification. No new application architecture is introduced by this guide.

## Responsibility boundaries

| Area | Owns | Does not own |
| --- | --- | --- |
| `frontend/src/app/` | Router/provider composition | Feature-specific draft or send logic |
| `frontend/src/pages/` | Route/account context and page composition | A second copy of server or recovery state |
| `frontend/src/components/` | Focused views using props or the feature's scoped context | Independent persistence hidden inside display-only sections |
| `frontend/src/forms/` | Input UI and local input behavior | Server-authoritative ownership or idempotency |
| `frontend/src/hooks/` | Queries, mutations and cohesive feature operations | Every unrelated workflow in a single hook |
| `frontend/src/api/` | Typed HTTP operations using the shared API client | UI rendering or a second auth/token implementation |
| `frontend/src/lib/` | Reusable transport, persistence and pure utilities | A generic workflow framework without a concrete need |
| `frontend/src/store/` | Truly shared client state such as authentication | Mirroring React Query's server cache |

Keep the existing layout; do not reorganize the whole application merely to match another repository's folder names. Split by state ownership and cohesive behavior, not by arbitrary line-count limits. Small wrappers are appropriate for named query operations; a hook that only forwards an unrelated setter is not automatically a useful boundary.

## Composition pattern

Prefer a page/view that composes sibling feature sections and a coordination hook that composes focused hooks. Each state value has one owner. Derived values are computed from that owner, not synchronized into another store with effects.

For chat, the approved division is:
- Policy, history and exact-conversation query hooks own backend reads/cache state.
- The send hook owns mutation status, timeout/abort handling and manual send/retry.
- The draft hook plus storage helpers own editable text, policy choice and immutable recovery payloads.
- `useChatSessionController` connects these results once inside `ChatSessionProvider`; it does not reimplement loading, error or transcript state.
- Policy/status/recovery views sit alongside history, transcript and the controlled composer.

### Shared session context (D-006)

Feature consumers use `useChatSessionContext` to read the provider's result,
instead of receiving every status/callback as a prop. The provider keys its
controller scope by account, route and logout epoch. Calling the controller
hook independently in each child would create separate draft state and send
observers even though their React Query cache is shared.

Keep `ChatForm`, `ConversationHistory`, and `ChatTranscript` reusable with
props. Small `ChatComposer`, `ChatHistory`, and `ChatMessages` adapters connect
those views to context. Context exposes existing owners; it is not a new global
store, a second query cache, or an excuse to remove props from all components.

Useful code locations to inspect (not a claim of verified examples): `frontend/src/hooks/conversation/`, `frontend/src/components/chat/`, `frontend/src/lib/chat-drafts.ts`, `frontend/src/lib/api-client.ts`, and `frontend/tests/chat-recovery.test.mjs`.

## Trainerlog reference

Reviewed on 2026-11-21 at commit **`5d20a656b82a4f252f0bed8e2cd241d84f68bcc4`**. Use these pinned examples to understand the idea, not to copy every implementation choice:

- [useTrainingTableData](https://github.com/ubungmeister/trainerlog/blob/5d20a656b82a4f252f0bed8e2cd241d84f68bcc4/frontend/src/hooks/trainingTable/useTrainingTableData.ts): combines focused data hooks into a feature-facing result.
- [useClientExerciseForm](https://github.com/ubungmeister/trainerlog/blob/5d20a656b82a4f252f0bed8e2cd241d84f68bcc4/frontend/src/hooks/trainingTable/clientExercise/formHandlingHook/useClientExerciseForm.ts): coordinates mutation hooks and pure payload helpers.
- [createNewExercise](https://github.com/ubungmeister/trainerlog/blob/5d20a656b82a4f252f0bed8e2cd241d84f68bcc4/frontend/src/hooks/trainingTable/clientExercise/formHandlingHook/helpers/createNewExercise.ts): keeps payload construction independent of component rendering.
- [TrainingTable page](https://github.com/ubungmeister/trainerlog/blob/5d20a656b82a4f252f0bed8e2cd241d84f68bcc4/frontend/src/pages/trainingTable/TrainingTable.tsx): composes views and modal sections.
- [Table](https://github.com/ubungmeister/trainerlog/blob/5d20a656b82a4f252f0bed8e2cd241d84f68bcc4/frontend/src/components/trainingTable/Table.tsx): separates table header/body/actions/controls and uses a focused date-window hook.

Do not copy trainerlog's direct token reads from localStorage, duplicate fetch/auth code, server-data copies into client stores, or its entire dependency stack. AI Advisor keeps its existing Supabase API client, backend ownership checks and approved recovery rules. Upstream changes do not automatically revise this baseline; review and record any adopted change explicitly.
