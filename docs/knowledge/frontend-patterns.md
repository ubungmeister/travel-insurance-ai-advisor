# Frontend patterns

**Scope:** AI Advisor's React frontend. These are approved preferences and safeguards; inspect current code and tests before adapting them. Current verification limits remain separate from the design rules.

## Server state and client state

- Use focused React Query `useQuery` hooks for policies, history and conversation details, and `useMutation` for sending/retrying.
- Use the existing API helpers rather than duplicating URLs, headers or Supabase session handling inside views.
- Include the signed-in account and exact resource ID in sensitive query keys: for example `['chat', accountId, 'conversation', id]`.
- Keep editable text, selected policy and pending recovery in the account/chat-scoped tab draft logic. Never store a server transcript or auth token in those draft records.
- Existing authentication state uses Zustand. It is available for genuinely shared client state, not a requirement to introduce a store for every feature. Do not mirror query data into a store merely because a component needs it.

## Send and recovery

Backend idempotency prevents duplicate writes; React Query does not. Save the UUID and exact submitted payload before the request. An uncertain outcome retains them for manual retry; never auto-send on mount or quietly replace the UUID. A deliberate second send gets a new UUID.

Set send mutations to `networkMode: 'always'` and `retry: false`. Check offline status before BOTH a new send and a manual retry so no send is silently paused/queued for reconnection.

Keep pending payloads immutable while the composer remains editable. Confirm only the matching stored request and preserve later typing. A definitive rejection can be restored or discarded; restore must not overwrite a newer draft.

## Confirmation and cache cleanup

Merge confirmed message IDs into the exact full conversation detail cache. A first-turn response alone is not a full detail model; fetch full detail for the returned ID. Invalidate history separately and best-effort: failed history refresh must not turn a confirmed send into an error or recreate recovery state.

`gcTime: 0` only limits inactive mutation retention. Reset settled mutation state after confirmation or resolved rejection when its variables no longer belong to recovery. Neither reset nor cache clear guarantees secure memory erasure.

At logout/account change: invalidate callback guards first, abort sends/cancel queries, clear query AND mutation caches, and reset tab/component draft state separately. Preserve recovery on expiry of the same account. Account-scoped keys are isolation, not proof of authorization. Ordinary navigation must not clear the whole application's cache.

## Effects and hook boundaries

Use effects for actual synchronization or lifecycle work, not to create redundant copies of derived state. Depend on the stable callbacks and primitive values the effect uses. Extract them from a hook result before the effect; do not disable `exhaustive-deps` to hide the problem.

```tsx
const { value, selectPolicy } = useChatDraft(accountId, slot)
const selectedPolicyId = value.policyId

useEffect(() => {
  if (solePolicyId !== undefined && selectedPolicyId !== solePolicyId) {
    selectPolicy(solePolicyId)
  }
}, [solePolicyId, selectedPolicyId, selectPolicy])
```

This example assumes `solePolicyId` comes from a completed, current owned-policy read and `selectPolicy` is stable. It changes a browser draft only; it does not create a conversation or send a request. Prefer deriving `solePolicyId` from current query data over storing another copy.

## Components, forms and comments

- Keep components focused on one view responsibility; compose siblings instead of hiding a whole feature behind a start-screen/form wrapper.
- When several feature sections consume the same session, expose one controller through a feature-scoped provider and a context consumer hook. Do not call a stateful controller separately in every section. Use adapters for generic views rather than binding every form/view to feature context; see D-006.
- Use controlled forms when a parent draft owner must preserve text across refresh, navigation or in-flight sends.
- React Hook Form + Zod are an **optional candidate** for larger validated forms, not an adopted dependency or requirement for a simple message input.
- Add `/** ... */` doc blocks to non-obvious hooks/functions/components, explaining responsibility, reason and safeguards. Keep them current when behavior changes; skip obvious wrappers and render-only helpers.
- Keep pure data transforms separate from React hooks when they have no lifecycle or state dependency. Do not create a new abstraction for every expression.

## Styling

- **Approved preference:** keep small one-off MUI `sx` styles next to JSX; use named constants for larger component-specific styles when that improves readability. Group substantial related chat styles in one feature-level module instead of creating a companion file for every component. Keep page-specific styles in the page. Preserve theme tokens, responsive behavior and MUI props that express semantics or behavior.
- **Source and scope:** user-approved chat styling consolidation (2026-11-23); see [MUI's customization guide](https://mui.com/material-ui/customization/how-to-customize/) and [System overview](https://mui.com/system/getting-started/overview/). `styled()` is appropriate for reusable components and theme overrides for app-wide consistency; neither is required for one-off chat styles. [Trainerlog's pinned `index.css`](https://github.com/ubungmeister/trainerlog/blob/5d20a656b82a4f252f0bed8e2cd241d84f68bcc4/frontend/src/index.css) uses named classes alongside inline Tailwind utilities; do not add another styling framework merely to copy it.
- **Verification:** the 2026-11-23 consolidation passed 41 frontend tests and lint, and built to a separate temporary output directory. The default build output hit a Windows permission error on an existing `dist` asset; browser verification was not performed. The tests emitted React/Emotion renderer warnings and the build reported a large chunk.

## Checks

Preserve integration-level recovery tests while adding focused tests around extracted boundaries. Verify exact URL errors, newer typing, offline retry, rejected recovery, account/logout transitions, late callbacks, cache retention and failed ancillary refreshes. Run the existing frontend test/lint/build commands; a source review or intermediate green run is not final verification.

Relevant records: [D-001 through D-004](decisions.md), [L-001 through L-003](lessons.md).
