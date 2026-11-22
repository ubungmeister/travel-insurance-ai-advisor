# Chat React Query Refactor

**Approved design:** React Query owns policies, history, conversation details, and send mutation state. Session storage owns editable drafts and immutable pending recovery; the backend owns idempotency. Use focused hooks and sibling UI sections, inspired by trainerlog's composition pattern, not its token storage.

**Constraints:** preserve exact URL behavior, no first-send database creation before Send, same-ID manual retry only, account/logout reset and same-account expiry recovery, newer typing, rejected restore/discard. Send options: `networkMode: 'always'`, `retry: false`, `gcTime: 0`; guard both Send and Retry offline. Reset settled confirmed mutation state. Flip the identity guard before abort/cancel/clear; logout/account change clears app query and mutation caches and resets drafts separately. History invalidation must never unconfirm a send.

## Tasks (inline execution; no commits or new dependencies)
- [x] Baseline frontend checks; adapt recovery tests to an isolated QueryClient provider. Add failing cache, offline, logout/late-callback, mutation-variable and best-effort refresh regressions.
- [x] Extract `useChatDraft`, account-scoped query hooks/key helpers, mutation/reconciliation logic, and a small `useChatSession` composition hook. Keep all storage writes in the draft hook/helpers.
- [x] Wire the account boundary to auth/logout, preserving cross-tab draftEpoch and expiry behavior. Split policy/recovery/status presentation out of ChatSession. Preserve existing user edits.
- [ ] Update project context/doc blocks. Verify frontend tests/lint/build, backend regression suite, and an independent read-only review. Report unverified browser/DB behavior.

**Review focus:** cached detail must disappear on an exact-ID 404; account keys are not sufficient without cache cleanup; mutation defaults must not offline-queue a send; abort/reset must not repopulate cleared caches or clear recovery; first-turn responses do not contain a full detail model; matching pending cleanup must preserve newer typing.

## Verification record / resume point
- Baseline: 15 frontend tests and lint passed. Mid-refactor: 20 tests passed after adapting React Query's notification scheduler for the mounted test harness; a production build passed before the final UI extraction.
- A later added test used a mutation introspection method that does not exist, leaving its controlled transport unresolved and the test process hanging. Replaced that assertion with mutation-cache `observerRemoved` events and guaranteed mock settlement in test cleanup. A rejected-send warning regression was also reproduced and fixed.
- The user stopped the spawned test process (PID 2612), but the harness still cannot launch PowerShell: `failed to spawn ... WindowsApps\\pwsh.exe: Access is denied (os error 5)`.
- Independent read-only review found two additional issues: no exact-detail refetch after a confirmed replay with an uncached failed detail read, and retained observed mutation variables after rejected-send resolution. Implemented both corrections and regression assertions. Also kept cached new-chat policies out of saved-route view state.
- Latest tests, lint, build, formatting and diff checks MUST be rerun once shell access is restored. Do not treat the intermediate green runs as final verification. No backend edits, migrations, dependencies, commits, or user-change reversions were made.
