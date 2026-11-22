# Chat Session Context Implementation Plan

**Approved goal:** remove chat-state prop plumbing without creating a controller instance in every child. A provider owns one controller; feature consumers read its scoped context. React Query, tab drafts, backend idempotency and the generic form/history/transcript views retain their responsibilities.

- [x] Add regressions for shared consumer identity/state, missing-provider errors, scope reset on route/account/logout epoch, and context-driven recovery UI. Attempt tests before implementation; report the existing shell blocker if it persists.
- [x] Rename the owner hook to `useChatSessionController`; add a separate typed context consumer and keyed `ChatSessionProvider`. Page context supplies account, route, navigation and draft epoch once.
- [x] Convert status/policy/recovery sections to consumers; add small context adapters for generic form, history and transcript. Make ChatSession a sibling layout without session props.
- [ ] Update D-001/D-002 guidance with the approved scoped-context boundary; preserve existing user edits and API behavior. Verify checks and independent read-only review; do not claim blocked tests passed.

**Constraints:** provider rekeys its controller on account, route or draftEpoch; consumers do not instantiate controllers or duplicate persisted state; no global chat store; missing provider fails explicitly. No dependencies, backend changes, commits or global configuration changes.

## Verification record
- Node test attempts before and after implementation were blocked before execution by the PowerShell harness's `Access is denied (os error 5)`. Tests, lint, typecheck/build and formatting are not claimed passing.
- Vite's already-running development server transformed 12 provider/controller/context/page/adapter/consumer modules with HTTP 200. This establishes transformation only, not runtime or TypeScript correctness.
- Independent read-only review found no evidenced defects in the provider change. Added a provider-level in-flight route-change test after review noted that lifecycle case was covered only by the direct-controller fixture. Five new provider/context tests now cover shared state, route/account/epoch reset, stale-send cancellation, context-driven recovery UI and absent-provider failure; they remain unexecuted.
- D-006, architecture/pattern guides and current README paths are updated. Existing generic views and backend/API/draft/query ownership are unchanged. The previous refactor's pending verification remains a separate limitation.
